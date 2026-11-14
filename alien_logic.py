from state import neighbors, shortest_distance, s, alien_names, alien_stunned, trap_at

def route(start, goal, blocked=()):
    queue = [start]
    previous = {start: None}
    for place in queue:
        if place == goal: break
        for tile in neighbors(*place):
            if tile not in previous and tile not in blocked:
                previous[tile] = place
                queue.append(tile)
    if goal not in previous: return []
    path = []
    place = goal
    while place is not None:
        path.append(place)
        place = previous[place]
    return path[::-1]


def ghost_goal(player):
    ghost = tuple(s["aliens"][0])
    stalker = tuple(s["aliens"][1])
    exit_tile = next(((x, y) for y, row in enumerate(s["grid"]) for x, tile in enumerate(row) if tile == ">"), player)

    escape_path = route(player, exit_tile)
    if not escape_path: return ghost

    options = []
    for index, tile in enumerate(escape_path[1:], start=1):
        time_to_block = shortest_distance(ghost, tile)
        if time_to_block == 999: continue
        arrival_penalty = max(0, time_to_block - index + 1) * 12
        future_penalty = abs(index - 4) * 2
        partnership_penalty = max(0, 5 - shortest_distance(stalker, tile)) * 12
        corridor_bonus = (4 - len(neighbors(*tile))) * 3
        exit_penalty = 25 if tile == exit_tile else 0
        score = arrival_penalty + future_penalty + time_to_block * 2 + partnership_penalty + exit_penalty - corridor_bonus
        options.append((score, tile))

    if ghost in escape_path[1:7] and shortest_distance(ghost, stalker) >= 3:
        return ghost
    if options: return min(options)[1]
    return ghost


def hunter_goal(player):
    return player


def alien_turn(protected=False, aggressive=False):
    s["turn"] += 1
    warnings = []
    player = (s["px"], s["py"])

    if not aggressive and s["turn"] <= 8:
        if s["turn"] == 8: return "You hear something moving in the darkness..."
        return ""

    target = hunter_goal(player)
    ghost_target = player if shortest_distance(tuple(s["aliens"][0]), player) <= 1 else ghost_goal(player)

    for i in (0, 1):
        if alien_stunned[i] > 0:
            alien_stunned[i] -= 1
            continue

        here = tuple(s["aliens"][i])
        goal = ghost_target if i == 0 else target
        distance_to_player = shortest_distance(here, player)
        sprint_limit = 4 if i == 0 else 8
        steps = 2 if distance_to_player > sprint_limit else 1

        for step in range(steps):
            here = tuple(s["aliens"][i])
            path = route(here, goal)
            chosen = path[1] if len(path) > 1 else here
            if i == 1 and chosen == here and here == target and step == 0:
                warnings.append("The Hunter is holding your escape route!")

            if protected and chosen == player: break
            s["aliens"][i] = list(chosen)
            if chosen == player: return "A creature caught you. Game Over!"
            trap = trap_at(*chosen)
            if trap:
                s["tl"].remove(trap)
                alien_stunned[i] = 3
                warnings.append(alien_names[i] + " walked into your trap and is stunned!")
                break

    if shortest_distance(tuple(s["aliens"][0]), player) <= 2: warnings.append("The Ghost is right behind you!")
    if shortest_distance(tuple(s["aliens"][1]), player) <= 3: warnings.append("The Hunter is cutting off your path!")
    return " ".join(dict.fromkeys(warnings))