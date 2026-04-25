import re
import math
from collections import defaultdict, Counter

print("✅ Script started!")

GENERIC_UTILITY_MOVES = {
    'protect', 'endure', 'rest', 'sleeptalk', 'substitute', 'facade', 'terablast',
    'sunnyday', 'raindance', 'sandstorm', 'snowscape', 'gigaimpact', 'hyperbeam',
    'helpinghand', 'takedown', 'bodyslam', 'swift', 'doubleedge', 'thief', 'taunt',
    'fling', 'curse', 'tackle', 'confide', 'swagger', 'attract', 'round', 'snore',
    'workup', 'toxic', 'return', 'frustration', 'secretpower'
}

IGNORED_METHOD_PREFIXES = {'R'}

METHOD_WEIGHTS = {
    'level': 1.0,
    'tm': 1.9,
    'egg': 1.9,
    'other': 0.9,
}

def choose_primary_method(method_types):
    if 'egg' in method_types:
        return 'egg'
    if 'tm' in method_types:
        return 'tm'
    if 'level' in method_types:
        return 'level'
    return 'other'

def bucket_sort_key(item):
    move, score = item
    return (-score, move)

def classify_method(method_code):
    if not method_code:
        return None
    suffix = method_code[1:]
    if not suffix:
        return None
    if suffix[0] in IGNORED_METHOD_PREFIXES:
        return None
    if suffix.startswith("L"):
        return "level"
    if suffix.startswith(("M", "T", "V", "D")):
        return "tm"
    if suffix.startswith("E"):
        return "egg"
    return "other"

def parse_pokedex(filename):
    print("📦 Parsing pokedex.ts...")
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read()

    pokedex = {}
    start = data.find("{")
    data = data[start:]
    if data.endswith("};"):
        data = data[:-2]

    entries = re.findall(r'([\w-]+):\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)},?', data, re.DOTALL)

    count = 0
    for name, block in entries:
        types_match = re.findall(r'types:\s*\[(.*?)\]', block)
        types = [x.strip().strip('"') for x in types_match[0].split(',')] if types_match else []

        egg_match = re.findall(r'eggGroups:\s*\[(.*?)\]', block)
        egg_groups = [x.strip().strip('"') for x in egg_match[0].split(',')] if egg_match else []

        abilities_block = re.search(r'abilities:\s*{(.*?)}', block, re.DOTALL)
        abilities = re.findall(r':\s*"([^"]+)"', abilities_block.group(1)) if abilities_block else []

        stats_match = re.search(r'baseStats:\s*{(.*?)}', block, re.DOTALL)
        base_stats = {}
        if stats_match:
            for stat_name, stat_value in re.findall(r'(hp|atk|def|spa|spd|spe):\s*(\d+)', stats_match.group(1)):
                base_stats[stat_name] = int(stat_value)

        num_match = re.search(r'num:\s*(-?\d+)', block)
        dex_num = int(num_match.group(1)) if num_match else None

        prevo_match = re.search(r'prevo:\s*"([^"]+)"', block)
        prevo = prevo_match.group(1).lower() if prevo_match else None

        evos_match = re.search(r'evos:\s*\[(.*?)\]', block)
        evos = []
        if evos_match:
            evos = [x.strip().strip('"').lower() for x in evos_match.group(1).split(',') if x.strip()]

        pokedex[name.lower()] = {
            "types": types,
            "eggGroups": egg_groups,
            "abilities": abilities,
            "baseStats": base_stats,
            "num": dex_num,
            "prevo": prevo,
            "evos": evos,
        }

        count += 1
        if count % 100 == 0 or count < 10:
            print(f"  🟢 Processed {count} Pokémon...")

    print(f"✅ Finished parsing pokedex.ts — found {count} Pokémon.")
    return pokedex

def parse_learnsets(filename, target_gen):
    print(f"📦 Parsing learnsets.ts for generation {target_gen} only...")
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read()

    start = data.find("{")
    data = data[start:]
    if data.endswith("};"):
        data = data[:-2]

    entries = re.finditer(r'([\w-]+):\s*{\s*learnset:\s*{(.*?)}\s*(,|})', data, re.DOTALL)

    learnsets = {}
    count = 0
    for match in entries:
        name, moves_block, _ = match.groups()
        move_entries = re.findall(r'(\w+):\s*\[(.*?)\]', moves_block)

        filtered_moves = []
        filtered_move_methods = {}
        move_method_types = {}

        for move_name, method_block in move_entries:
            methods = [m.strip().strip('"') for m in method_block.split(",")]
            gen_methods = [m for m in methods if m.startswith(str(target_gen))]

            usable_methods = []
            method_types = set()
            for m in gen_methods:
                method_type = classify_method(m)
                if method_type is None:
                    continue
                usable_methods.append(m)
                method_types.add(method_type)

            if usable_methods:
                filtered_moves.append(move_name)
                filtered_move_methods[move_name] = usable_methods
                move_method_types[move_name] = method_types

        learnsets[name.lower()] = {
            "moves": filtered_moves,
            "methods": filtered_move_methods,
            "method_types": move_method_types,
        }

        count += 1
        if count % 100 == 0 or count < 10:
            print(f"  🟣 Processed {count} learnsets...")

    print(f"✅ Finished parsing learnsets.ts — found {count} Pokémon.")
    return learnsets

def parse_moves(filename):
    print("📦 Parsing moves.ts...")
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    moves = {}
    current_move = None
    current_block = []
    depth = 0
    in_moves_table = False
    count = 0
    entry_start = re.compile(r'^\s*(?:"([^"]+)"|([\w-]+)):\s*{\s*$')

    for line in lines:
        if not in_moves_table:
            if "export const Moves" in line:
                in_moves_table = True
            continue

        if current_move is None:
            match = entry_start.match(line)
            if match:
                current_move = (match.group(1) or match.group(2)).lower()
                current_block = [line]
                depth = line.count("{") - line.count("}")
            continue

        current_block.append(line)
        depth += line.count("{") - line.count("}")

        if depth <= 0:
            block_text = "".join(current_block)
            type_match = re.search(r'type:\s*"([^"]+)"', block_text)
            category_match = re.search(r'category:\s*"([^"]+)"', block_text)
            if type_match:
                moves[current_move] = {
                    "type": type_match.group(1),
                    "category": category_match.group(1) if category_match else None,
                }
                count += 1
            current_move = None
            current_block = []
            depth = 0

    print(f"✅ Finished parsing moves.ts — found {count} moves.")
    return moves

def is_cap_mon(mon_info):
    num = mon_info.get('num')
    return num is not None and -72 <= num <= -1

def build_family_data(pokedex):
    family_root = {}
    family_members = defaultdict(set)

    def find_root(mon):
        seen = set()
        cur = mon
        while (
            cur in pokedex
            and pokedex[cur].get('prevo')
            and pokedex[cur]['prevo'] not in seen
            and pokedex[cur]['prevo'] in pokedex
        ):
            seen.add(cur)
            cur = pokedex[cur]['prevo']
        return cur

    for mon in pokedex:
        root = find_root(mon)
        family_root[mon] = root
        family_members[root].add(mon)

    family_base = {}
    family_finals = {}
    family_primary_final = {}

    for root, members in family_members.items():
        base = root
        finals = sorted([m for m in members if not pokedex.get(m, {}).get('evos')])
        if not finals:
            finals = [base]
        family_base[root] = base
        family_finals[root] = finals

        def bst(mon):
            if mon not in pokedex:
                return -1
            stats = pokedex[mon].get('baseStats', {})
            return sum(stats.get(s, 0) for s in ('hp', 'atk', 'def', 'spa', 'spd', 'spe'))

        family_primary_final[root] = max(finals, key=bst)

    return {
        'root_of': family_root,
        'members': family_members,
        'base_of_root': family_base,
        'finals_of_root': family_finals,
        'primary_final_of_root': family_primary_final,
    }

def clamp(value, low, high):
    return max(low, min(high, value))

def safe_int(prompt, minimum=1, maximum=None, allow_blank=False):
    while True:
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return None
        if raw.isdigit():
            value = int(raw)
            if value >= minimum and (maximum is None or value <= maximum):
                return value
        if maximum is None:
            print(f"❗ Please enter a number >= {minimum}.")
        else:
            print(f"❗ Please enter a number between {minimum} and {maximum}.")

def parse_csv_input(text):
    return [x.strip() for x in text.split(',') if x.strip()]

def parse_grouped_sets(group_string):
    groups = re.findall(r'{(.*?)}', group_string)
    return [[name.strip().lower() for name in group.split(',')] for group in groups if group.strip()]

def normalize_title_list(values):
    return {v.strip().title() for v in values if v.strip()}

def move_is_allowed(move_name, moves_data, banned_move_types):
    if not banned_move_types:
        return True
    move_info = moves_data.get(move_name.lower())
    if not move_info:
        return True
    return move_info.get("type") not in banned_move_types

def filter_move_list(move_names, moves_data, banned_move_types):
    return [move for move in move_names if move_is_allowed(move, moves_data, banned_move_types)]

def get_role_tags(stats):
    tags = set()
    atk = stats.get('atk', 0)
    spa = stats.get('spa', 0)
    spe = stats.get('spe', 0)
    hp = stats.get('hp', 0)
    defense = stats.get('def', 0)
    spd = stats.get('spd', 0)
    bulk = hp + defense + spd

    if atk >= spa + 20:
        tags.add('physical')
    elif spa >= atk + 20:
        tags.add('special')
    else:
        tags.add('mixed')

    if spe >= 100:
        tags.add('fast')
    elif spe <= 60:
        tags.add('slow')
    else:
        tags.add('mid_speed')

    if bulk >= 260:
        tags.add('bulky')
    elif bulk <= 180:
        tags.add('frail')
    else:
        tags.add('mid_bulk')

    if atk >= 115 or spa >= 115:
        tags.add('offensive')
    if bulk >= 250 and spe <= 80:
        tags.add('tank')

    return tags

def stat_distance(custom_stats, mon_stats):
    if not mon_stats:
        return None

    stat_weights = {
        'hp': 0.8, 'atk': 1.35, 'def': 1.0,
        'spa': 1.35, 'spd': 1.0, 'spe': 1.25,
    }

    distance = 0.0
    total_weight = 0.0
    for stat, weight in stat_weights.items():
        if stat not in custom_stats or stat not in mon_stats:
            continue
        diff = abs(custom_stats[stat] - mon_stats[stat])
        distance += diff * weight
        total_weight += weight

    if total_weight == 0:
        return None
    return distance / total_weight

def similarity_from_distance(distance):
    if distance is None:
        return 0.0
    return 1.0 / (1.0 + (distance / 18.0))

def is_generic_move(move_name, prevalence_ratio):
    move_key = move_name.lower().replace(' ', '')
    normalized_generic = {m.replace(' ', '') for m in GENERIC_UTILITY_MOVES}
    return move_key in normalized_generic or prevalence_ratio >= 0.72

def get_family_non_egg_moves(rep_mon, learnsets, moves_data, banned_move_types):
    if rep_mon not in learnsets:
        return []
    out = []
    for move in learnsets[rep_mon]['moves']:
        if not move_is_allowed(move, moves_data, banned_move_types):
            continue
        method_types = learnsets[rep_mon]['method_types'].get(move, set())
        if method_types - {'egg'}:
            out.append(move)
    return out

def get_family_egg_moves(base_mon, learnsets, moves_data, banned_move_types):
    if base_mon not in learnsets:
        return []
    out = []
    for move in learnsets[base_mon]['moves']:
        if not move_is_allowed(move, moves_data, banned_move_types):
            continue
        method_types = learnsets[base_mon]['method_types'].get(move, set())
        if 'egg' in method_types:
            out.append(move)
    return out

def get_family_all_moves(root, family_data, learnsets, moves_data, banned_move_types):
    rep_mon = family_data['primary_final_of_root'][root]
    base_mon = family_data['base_of_root'][root]
    moves = set(get_family_non_egg_moves(rep_mon, learnsets, moves_data, banned_move_types))
    moves.update(get_family_egg_moves(base_mon, learnsets, moves_data, banned_move_types))
    return sorted(moves)


def family_has_any_moves(root, family_data, learnsets, moves_data, banned_move_types):
    return bool(get_family_all_moves(root, family_data, learnsets, moves_data, banned_move_types))

def get_coverage_moves(custom_types, coverage_types, pokedex, learnsets, family_data, moves_data, excluded_pokemon, banned_move_types, threshold=0.5):
    coverage_results = {}
    excluded_pokemon = set(excluded_pokemon or [])
    excluded_roots = {family_data['root_of'].get(mon, mon) for mon in excluded_pokemon}

    for coverage_type in coverage_types:
        if coverage_type in banned_move_types:
            coverage_results[coverage_type] = {"total": 0, "moves": [], "blocked": True}
            continue

        supporting_roots = []
        for root, rep_mon in family_data['primary_final_of_root'].items():
            if root in excluded_roots:
                continue
            if rep_mon not in learnsets:
                continue
            rep_info = pokedex.get(rep_mon, {})
            if is_cap_mon(rep_info):
                continue
            if not family_has_any_moves(root, family_data, learnsets, moves_data, banned_move_types):
                continue

            mon_types = set(rep_info.get('types', []))
            if not mon_types.intersection(custom_types):
                continue
            if coverage_type in mon_types:
                continue

            supporting_roots.append(root)

        total = len(supporting_roots)
        if total <= 2:
            coverage_results[coverage_type] = {"total": total, "moves": [], "blocked": False}
            continue

        counter = Counter()
        move_method_counter = defaultdict(Counter)

        for root in supporting_roots:
            rep_mon = family_data['primary_final_of_root'][root]
            base_mon = family_data['base_of_root'][root]

            for move in get_family_non_egg_moves(rep_mon, learnsets, moves_data, banned_move_types):
                move_info = moves_data.get(move.lower())
                if move_info and move_info.get("type") == coverage_type:
                    counter[move] += 1
                    move_method_counter[move]['level_or_tm'] += 1

            for move in get_family_egg_moves(base_mon, learnsets, moves_data, banned_move_types):
                move_info = moves_data.get(move.lower())
                if move_info and move_info.get("type") == coverage_type:
                    counter[move] += 1
                    move_method_counter[move]['egg'] += 1

        moves = []
        for move, count in counter.items():
            ratio = count / total
            if ratio >= threshold:
                primary = move_method_counter[move].most_common(1)[0][0] if move_method_counter[move] else 'other'
                moves.append((move, count, round(ratio * 100), primary))

        coverage_results[coverage_type] = {"total": total, "moves": sorted(moves), "blocked": False}

    return coverage_results

def build_move_map(pokedex, learnsets, family_data, moves_data, banned_move_types):
    print("🔧 Building move frequency maps...")
    by_type = defaultdict(list)
    by_egg = defaultdict(list)
    by_ability = defaultdict(list)

    for root, rep_mon in family_data['primary_final_of_root'].items():
        info = pokedex.get(rep_mon)
        if rep_mon not in learnsets or not info or is_cap_mon(info):
            continue
        if not family_has_any_moves(root, family_data, learnsets, moves_data, banned_move_types):
            continue
        for t in info['types']:
            by_type[t].append(root)
        for ab in info['abilities']:
            by_ability[ab].append(root)

    for root, base_mon in family_data['base_of_root'].items():
        info = pokedex.get(base_mon)
        if not info or is_cap_mon(info):
            continue
        if not family_has_any_moves(root, family_data, learnsets, moves_data, banned_move_types):
            continue
        for eg in info['eggGroups']:
            by_egg[eg].append(root)

    def count_moves_by_trait(group_map):
        trait_move_counts = {}
        for trait, root_list in group_map.items():
            trait_move_counts[trait] = Counter()
            for root in root_list:
                for move in get_family_all_moves(root, family_data, learnsets, moves_data, banned_move_types):
                    trait_move_counts[trait][move] += 1
        return trait_move_counts

    return {
        'type': count_moves_by_trait(by_type),
        'egg': count_moves_by_trait(by_egg),
        'ability': count_moves_by_trait(by_ability),
        'pools': {'type': by_type, 'egg': by_egg, 'ability': by_ability},
    }

def build_weighted_move_scores(
    pokedex,
    learnsets,
    family_data,
    moves_data,
    banned_move_types,
    custom_types,
    custom_egg_groups,
    custom_abilities,
    custom_stats,
    similar_pokemon,
    custom_groups,
    coverage_types,
    excluded_pokemon,
    top_n=80,
):
    move_scores = defaultdict(float)
    move_reasons = defaultdict(list)
    move_support_counts = Counter()
    move_best_method = {}
    candidate_scores = []
    excluded_pokemon = set(excluded_pokemon or [])
    excluded_roots = {family_data['root_of'].get(mon, mon) for mon in excluded_pokemon}
    custom_role_tags = get_role_tags(custom_stats)
    similar_roots = {family_data['root_of'].get(mon, mon) for mon in similar_pokemon}

    for root, rep_mon in family_data['primary_final_of_root'].items():
        if root in excluded_roots:
            continue
        if rep_mon not in learnsets:
            continue
        mon_info = pokedex.get(rep_mon, {})
        if is_cap_mon(mon_info):
            continue
        if not family_has_any_moves(root, family_data, learnsets, moves_data, banned_move_types):
            continue

        base_mon = family_data['base_of_root'][root]
        base_info = pokedex.get(base_mon, {})

        mon_types = set(mon_info.get('types', []))
        mon_egg_groups = set(base_info.get('eggGroups', []))
        mon_abilities = set(mon_info.get('abilities', []))
        mon_stats = mon_info.get('baseStats', {})
        mon_role_tags = get_role_tags(mon_stats)

        shared_types = len(mon_types.intersection(custom_types))
        shared_eggs = len(mon_egg_groups.intersection(custom_egg_groups))
        shared_abilities = len(mon_abilities.intersection(custom_abilities))
        shared_roles = len(mon_role_tags.intersection(custom_role_tags))

        explicit_similar = root in similar_roots

        # Guardrail: if a family shares neither a type nor an egg group, it is too far off-body-plan
        # to contribute to weighted learnset suggestions.
        if shared_types == 0 and shared_eggs == 0 and not explicit_similar:
            continue

        distance = stat_distance(custom_stats, mon_stats)
        stat_similarity = similarity_from_distance(distance)

        score = 0.0
        reason_bits = []

        if shared_types == 2:
            score += 5.5
            reason_bits.append('shares both types')
        elif shared_types == 1:
            score += 3.5
            reason_bits.append('shares one type')

        score += stat_similarity * 4.0
        if stat_similarity >= 0.75:
            reason_bits.append('very similar statline')
        elif stat_similarity >= 0.55:
            reason_bits.append('similar statline')
        elif stat_similarity >= 0.35:
            reason_bits.append('loosely similar statline')

        if shared_roles:
            score += shared_roles * 0.75
            reason_bits.append(f'shares {shared_roles} role tag(s)')
        if shared_eggs:
            score += shared_eggs * 1.6
            reason_bits.append('shares egg group')
        if shared_abilities:
            score += shared_abilities * 1.2
            reason_bits.append('shares ability')
        if explicit_similar:
            score += 4.0
            reason_bits.append('manually chosen similar family')

        if score <= 0:
            continue

        candidate_scores.append((rep_mon, score, distance, reason_bits))

        for move in get_family_non_egg_moves(rep_mon, learnsets, moves_data, banned_move_types):
            method_types = learnsets[rep_mon]['method_types'].get(move, {'other'})
            primary_method = choose_primary_method(method_types)
            weighted_score = score * METHOD_WEIGHTS[primary_method]
            move_scores[move] += weighted_score
            move_reasons[move].append((rep_mon, weighted_score, reason_bits + ['final evo rep', f'{primary_method} move']))
            move_support_counts[move] += 1
            current_best = move_best_method.get(move)
            if current_best is None or METHOD_WEIGHTS[primary_method] > METHOD_WEIGHTS[current_best]:
                move_best_method[move] = primary_method

        for move in get_family_egg_moves(base_mon, learnsets, moves_data, banned_move_types):
            primary_method = 'egg'
            weighted_score = score * 0.9 * METHOD_WEIGHTS[primary_method]
            move_scores[move] += weighted_score
            move_reasons[move].append((base_mon, weighted_score, reason_bits + ['base evo egg move', 'egg move']))
            move_support_counts[move] += 1
            current_best = move_best_method.get(move)
            if current_best is None or METHOD_WEIGHTS[primary_method] > METHOD_WEIGHTS[current_best]:
                move_best_method[move] = primary_method

    candidate_count = len(candidate_scores)

    for group_index, group in enumerate(custom_groups, start=1):
        valid_roots = []
        seen = set()
        for mon in group:
            if mon in excluded_pokemon or mon not in family_data['root_of']:
                continue
            root = family_data['root_of'][mon]
            rep_mon = family_data['primary_final_of_root'][root]
            if root in seen or rep_mon not in learnsets or is_cap_mon(pokedex.get(rep_mon, {})):
                continue
            if not family_has_any_moves(root, family_data, learnsets, moves_data, banned_move_types):
                continue
            seen.add(root)
            valid_roots.append(root)

        if len(valid_roots) < 2:
            continue

        total = len(valid_roots)
        counter = Counter()
        move_to_methods = defaultdict(set)
        for root in valid_roots:
            rep_mon = family_data['primary_final_of_root'][root]
            base_mon = family_data['base_of_root'][root]

            for move in get_family_non_egg_moves(rep_mon, learnsets, moves_data, banned_move_types):
                counter[move] += 1
                move_to_methods[move].update(learnsets[rep_mon]['method_types'].get(move, {'other'}))

            for move in get_family_egg_moves(base_mon, learnsets, moves_data, banned_move_types):
                counter[move] += 1
                move_to_methods[move].add('egg')

        for move, count in counter.items():
            ratio = count / total
            if total > 2 and ratio >= 0.5:
                primary_method = choose_primary_method(move_to_methods[move])
                bonus = (1.5 + (ratio * 2.5)) * METHOD_WEIGHTS[primary_method]
                move_scores[move] += bonus
                move_reasons[move].append((
                    f'group {group_index}',
                    bonus,
                    [f'shared by {round(ratio * 100)}% of custom families in group {group_index}', f'{primary_method} move']
                ))
                current_best = move_best_method.get(move)
                if current_best is None or METHOD_WEIGHTS[primary_method] > METHOD_WEIGHTS[current_best]:
                    move_best_method[move] = primary_method

    coverage_results = get_coverage_moves(
        custom_types=custom_types,
        coverage_types=coverage_types,
        pokedex=pokedex,
        learnsets=learnsets,
        family_data=family_data,
        moves_data=moves_data,
        excluded_pokemon=excluded_pokemon,
        banned_move_types=banned_move_types,
        threshold=0.35,
    )

    for coverage_type, data in coverage_results.items():
        if data.get("blocked"):
            continue
        for move, _, percent, primary in data['moves']:
            method_bucket = 'egg' if primary == 'egg' else 'tm'
            bonus = (3.0 + (percent / 100.0) * 4.0) * METHOD_WEIGHTS[method_bucket]
            move_scores[move] += bonus
            move_reasons[move].append((
                f'{coverage_type} coverage',
                bonus,
                [f'{percent}% of matching non-{coverage_type} families learn it', f'{method_bucket} move']
            ))
            current_best = move_best_method.get(move)
            if current_best is None or METHOD_WEIGHTS[method_bucket] > METHOD_WEIGHTS[current_best]:
                move_best_method[move] = method_bucket

    method_buckets = {'level': {}, 'tm': {}, 'egg': {}, 'other': {}}
    generic_scores = {}

    for move, score in move_scores.items():
        prevalence_ratio = 0.0 if candidate_count == 0 else move_support_counts[move] / candidate_count
        method_bucket = move_best_method.get(move, 'other')
        adjusted_score = score * (0.55 + min(prevalence_ratio, 0.65))
        if is_generic_move(move, prevalence_ratio):
            generic_scores[move] = adjusted_score
        else:
            method_buckets[method_bucket][move] = adjusted_score

    return {
        'level': sorted(method_buckets['level'].items(), key=bucket_sort_key)[:top_n],
        'tm': sorted(method_buckets['tm'].items(), key=bucket_sort_key)[:top_n],
        'egg': sorted(method_buckets['egg'].items(), key=bucket_sort_key)[:top_n],
        'other': sorted(method_buckets['other'].items(), key=bucket_sort_key)[:top_n],
        'generic': sorted(generic_scores.items(), key=bucket_sort_key)[:top_n],
        'candidates': sorted(candidate_scores, key=lambda x: (-x[1], x[0]))[:20],
        'reasons': move_reasons,
        'coverage': coverage_results,
    }

def print_bucket(bucket_name, moves, move_reasons, top_n):
    print(f"{bucket_name}:")
    if not moves:
        print("  (none found)")
        return
    for move, score in moves[:top_n]:
        reasons = sorted(move_reasons[move], key=lambda x: -x[1])[:3]
        pretty_reasons = []
        for source, source_score, source_bits in reasons:
            if source_bits:
                pretty_reasons.append(f"{source} (+{source_score:.2f}: {', '.join(source_bits)})")
            else:
                pretty_reasons.append(f"{source} (+{source_score:.2f})")
        print(f"  • {move} — weighted score {score:.2f}")
        for line in pretty_reasons:
            print(f"      - {line}")

def print_weighted_results(results, top_n=20, generic_top_n=12):
    ranked_candidates = results['candidates']
    move_reasons = results['reasons']
    coverage_results = results['coverage']

    print("🧠 Top stat-aware similar Pokémon:")
    if not ranked_candidates:
        print("  (none found)")
    else:
        for mon_name, score, distance, reasons in ranked_candidates[:12]:
            distance_text = 'n/a' if distance is None else f'{distance:.1f}'
            joined = ', '.join(reasons[:3]) if reasons else 'no reason'
            print(f"  • {mon_name} — score {score:.2f}, stat distance {distance_text} ({joined})")

    if coverage_results:
        print("🧊 Coverage-type suggestions:")
        for coverage_type, data in coverage_results.items():
            if data.get("blocked"):
                print(f"  • {coverage_type}: skipped because {coverage_type} is blacklisted")
                continue
            total = data['total']
            if total <= 2:
                print(f"  • {coverage_type}: skipped because only {total} non-{coverage_type} supporting families matched")
                continue
            print(f"  • {coverage_type} coverage from {total} matching non-{coverage_type} families:")
            if data['moves']:
                for move, _, percent, primary in data['moves'][:12]:
                    print(f"      - {move} ({percent}%) [{primary}]")
            else:
                print("      - (none found)")

    print_bucket("📘 Top level-up move suggestions", results['level'], move_reasons, top_n)
    print_bucket("🧰 Top TM / tutor move suggestions", results['tm'], move_reasons, top_n)
    print_bucket("🥚 Top egg move suggestions", results['egg'], move_reasons, top_n)
    print_bucket("✨ Other move suggestions", results['other'], move_reasons, top_n)

    print("🧩 Generic utility / universal option moves:")
    if not results['generic']:
        print("  (none found)")
    else:
        for move, score in results['generic'][:generic_top_n]:
            reasons = sorted(move_reasons[move], key=lambda x: -x[1])[:2]
            pretty_sources = ', '.join(source for source, _, _ in reasons)
            print(f"  • {move} — utility score {score:.2f} ({pretty_sources})")

    print("  🧾 Final structured move lists:")
    print("  Level-up:", ', '.join(move for move, _ in results['level'][:top_n]) or '(none)')
    print("  TM/Tutor:", ', '.join(move for move, _ in results['tm'][:top_n]) or '(none)')
    print("  Egg:", ', '.join(move for move, _ in results['egg'][:top_n]) or '(none)')
    print("  Other:", ', '.join(move for move, _ in results['other'][:top_n]) or '(none)')
    print("  Generic utility:", ', '.join(move for move, _ in results['generic'][:generic_top_n]) or '(none)')

def find_common_moves(move_maps, traits, learnsets, family_data, moves_data, banned_move_types, similar_pokemon=None, restrict_shared=None, custom_groups=None, coverage_results=None, threshold=0.5, excluded_pokemon=None):
    print(f"\n📊 Finding moves that appear in at least {round(threshold * 100)}% of matching Pokémon families...\n")
    all_suggested = set()
    excluded_pokemon = set(excluded_pokemon or [])
    excluded_roots = {family_data['root_of'].get(mon, mon) for mon in excluded_pokemon}

    for category, values in traits.items():
        print(f"🔹 Trait category: {category.capitalize()}")
        for val in values:
            pool = move_maps['pools'][category].get(val)
            if not pool:
                print(f"  ❌ No data for: {val}")
                continue

            filtered_pool = [root for root in pool if root not in excluded_roots]
            total = len(filtered_pool)
            if total <= 2:
                print(f"  ⚠️ {val}: skipped because only {total} usable families matched after exclusions")
                continue

            filtered_counter = Counter()
            for root in filtered_pool:
                for move in get_family_all_moves(root, family_data, learnsets, moves_data, banned_move_types):
                    filtered_counter[move] += 1

            minimum_needed = math.ceil(total * threshold)
            print(f"  📘 {val} (in {total} usable families): moves in at least {minimum_needed} families")

            common_moves = [(move, count) for move, count in filtered_counter.items() if (count / total) >= threshold]
            if common_moves:
                for move, count in sorted(common_moves):
                    percent = round(100 * count / total)
                    print(f"    • {move} ({percent}%)")
                    all_suggested.add(move)
            else:
                print("    (none found)")
        print()

    if similar_pokemon:
        print("🧬 Adding moves from similar Pokémon families:")
        seen = set()
        for mon in similar_pokemon:
            root = family_data['root_of'].get(mon.lower())
            if not root or root in seen:
                continue
            seen.add(root)
            if root in excluded_roots:
                print(f"  • {mon.capitalize()}: skipped because its family is excluded")
            elif not family_has_any_moves(root, family_data, learnsets, moves_data, banned_move_types):
                print(f"  • {mon.capitalize()}: skipped because its family has no moves in this generation")
            else:
                moves = get_family_all_moves(root, family_data, learnsets, moves_data, banned_move_types)
                rep_mon = family_data['primary_final_of_root'][root]
                if moves:
                    print(f"  • {rep_mon.capitalize()} family: {len(moves)} moves")
                    all_suggested.update(moves)
                else:
                    print(f"  • {rep_mon.capitalize()} family: (no moves found)")
        print()

    if custom_groups:
        print("🧪 Group-based shared move analysis:")
        for idx, group in enumerate(custom_groups, start=1):
            valid_roots = []
            seen = set()
            for mon in group:
                if mon not in family_data['root_of']:
                    continue
                root = family_data['root_of'][mon]
                if root in excluded_roots or root in seen:
                    continue
                if not family_has_any_moves(root, family_data, learnsets, moves_data, banned_move_types):
                    continue
                seen.add(root)
                valid_roots.append(root)

            if len(valid_roots) < 2:
                print(f"  Group {idx}: ⚠️ Need at least 2 valid families")
                continue

            total = len(valid_roots)
            counter = Counter()
            for root in valid_roots:
                counter.update(set(get_family_all_moves(root, family_data, learnsets, moves_data, banned_move_types)))

            shared = [(move, count) for move, count in counter.items() if (count / total) >= threshold]
            if shared:
                names = [family_data['primary_final_of_root'][root] for root in valid_roots]
                print(f"  Group {idx} ({', '.join(names)}):")
                for move, count in sorted(shared):
                    percent = round(100 * count / total)
                    print(f"    • {move} ({percent}%)")
                    all_suggested.add(move)
            else:
                print(f"  Group {idx}: (no common moves found)")
        print()

    if coverage_results:
        print("🧊 Coverage-type suggestions:")
        for coverage_type, data in coverage_results.items():
            if data.get("blocked"):
                print(f"  • {coverage_type}: skipped because {coverage_type} is blacklisted")
                continue
            total = data['total']
            if total <= 2:
                print(f"  • {coverage_type}: skipped because only {total} non-{coverage_type} supporting families matched")
                continue
            print(f"  • {coverage_type} coverage from {total} matching non-{coverage_type} families:")
            if data['moves']:
                for move, _, percent, primary in data['moves']:
                    print(f"      - {move} ({percent}%) [{primary}]")
                    all_suggested.add(move)
            else:
                print("      - (none found)")
        print()

    if restrict_shared:
        print("🔒 Restricting to moves shared by:")
        valid_roots = []
        seen = set()
        for mon in restrict_shared:
            root = family_data['root_of'].get(mon.lower())
            if not root or root in excluded_roots or root in seen:
                continue
            if not family_has_any_moves(root, family_data, learnsets, moves_data, banned_move_types):
                continue
            seen.add(root)
            valid_roots.append(root)
        if len(valid_roots) >= 2:
            sets = [set(get_family_all_moves(root, family_data, learnsets, moves_data, banned_move_types)) for root in valid_roots]
            shared = set.intersection(*sets)
            names = [family_data['primary_final_of_root'][root] for root in valid_roots]
            print(f"  ✅ {len(shared)} moves shared by {', '.join(names)} families")
            all_suggested &= shared
        elif len(valid_roots) == 1:
            print("  ℹ️ Only one valid family provided — skipping restriction")
        else:
            print("  ⚠️ No valid families — skipping restriction")

    if all_suggested:
        print("\n🧾 Final percentage-based move list (no repeats):")
        print(', '.join(sorted(all_suggested)))
    else:
        print("⚠️ No suggested moves found after applying all filters.")

def main():
    try:
        pokedex = parse_pokedex('pokedex.ts')
        moves_data = parse_moves('moves.ts')
    except FileNotFoundError as e:
        print('❌ File not found:', e)
        raise SystemExit

    if len(pokedex) == 0:
        print('⚠️ No Pokémon were parsed from pokedex.ts — check the format or file path.')
        raise SystemExit

    family_data = build_family_data(pokedex)

    while True:
        gen = safe_int('Enter target generation (1–9): ', minimum=1, maximum=9)

        try:
            learnsets = parse_learnsets('learnsets.ts', gen)
        except FileNotFoundError as e:
            print('❌ File not found:', e)
            raise SystemExit

        if len(learnsets) == 0:
            print('⚠️ No Pokémon were parsed from learnsets.ts — check the format or file path.')
            raise SystemExit

        print("🔧 Building move frequency maps...")
        move_maps = build_move_map(pokedex, learnsets, family_data, moves_data, set())

        print("\n🧪 Enter your custom Pokémon info.")
        types = parse_csv_input(input('Enter types (comma separated, e.g. Fairy, Fire): ').strip())
        egg_groups = parse_csv_input(input('Enter egg groups (comma separated): ').strip())
        abilities = parse_csv_input(input('Enter abilities (comma separated): ').strip())

        print("\n📈 Enter base stats for the custom Pokémon.")
        custom_stats = {
            'hp': safe_int('HP: ', minimum=1, maximum=255),
            'atk': safe_int('Attack: ', minimum=1, maximum=255),
            'def': safe_int('Defense: ', minimum=1, maximum=255),
            'spa': safe_int('Sp. Atk: ', minimum=1, maximum=255),
            'spd': safe_int('Sp. Def: ', minimum=1, maximum=255),
            'spe': safe_int('Speed: ', minimum=1, maximum=255),
        }

        custom_traits = {'type': types, 'egg': egg_groups, 'ability': abilities}

        similar_input = input('Enter specific Pokémon to base this off (comma separated), or leave blank: ').strip()
        similar_pokemon = [x.strip().lower() for x in similar_input.split(',') if x.strip()] if similar_input else []

        exclude_input = input('Enter Pokémon to exclude entirely (comma separated), or leave blank: ').strip()
        excluded_pokemon = [x.strip().lower() for x in exclude_input.split(',') if x.strip()] if exclude_input else []

        shared_input = input('Enter Pokémon to restrict to shared moves only (comma separated), or leave blank: ').strip()
        restrict_shared = [x.strip().lower() for x in shared_input.split(',') if x.strip()] if shared_input else []

        group_input = input('Enter Pokémon groups using braces (e.g. {A,B,C}, {X,Y}), or leave blank: ').strip()
        grouped_sets = parse_grouped_sets(group_input) if group_input else []

        coverage_input = input('Enter desired coverage move types (comma separated, e.g. Ice, Ground), or leave blank: ').strip()
        coverage_types = normalize_title_list(parse_csv_input(coverage_input))

        banned_types_input = input('Enter move types to blacklist (comma separated, e.g. Rock, Water), or leave blank: ').strip()
        banned_move_types = normalize_title_list(parse_csv_input(banned_types_input))

        threshold_input = input('What minimum percentage should a move appear in a group/trait to count? (default 50): ').strip()
        try:
            threshold_value = float(threshold_input) / 100 if threshold_input else 0.5
        except ValueError:
            threshold_value = 0.5
        threshold_value = clamp(threshold_value, 0.01, 1.0)

        print("\nChoose output mode:")
        print('  1. Percentage-based suggestions (family-aware)')
        print('  2. Stat-aware weighted suggestions (family-aware)')
        print('  3. Both')
        mode = input('Enter 1, 2, or 3: ').strip()
        if mode not in {'1', '2', '3'}:
            mode = '3'

        coverage_results = get_coverage_moves(
            custom_types=set(types),
            coverage_types=coverage_types,
            pokedex=pokedex,
            learnsets=learnsets,
            family_data=family_data,
            moves_data=moves_data,
            excluded_pokemon=excluded_pokemon,
            banned_move_types=banned_move_types,
            threshold=threshold_value,
        ) if coverage_types else {}

        if mode in {'1', '3'}:
            move_maps = build_move_map(pokedex, learnsets, family_data, moves_data, banned_move_types)
            find_common_moves(
                move_maps,
                custom_traits,
                learnsets,
                family_data,
                moves_data,
                banned_move_types,
                similar_pokemon=similar_pokemon,
                restrict_shared=restrict_shared,
                custom_groups=grouped_sets,
                coverage_results=coverage_results,
                threshold=threshold_value,
                excluded_pokemon=excluded_pokemon,
            )

        if mode in {'2', '3'}:
            weighted_results = build_weighted_move_scores(
                pokedex=pokedex,
                learnsets=learnsets,
                family_data=family_data,
                moves_data=moves_data,
                banned_move_types=banned_move_types,
                custom_types=set(types),
                custom_egg_groups=set(egg_groups),
                custom_abilities=set(abilities),
                custom_stats=custom_stats,
                similar_pokemon=set(similar_pokemon),
                custom_groups=grouped_sets,
                coverage_types=coverage_types,
                excluded_pokemon=excluded_pokemon,
                top_n=100,
            )

            if restrict_shared:
                valid_roots = []
                seen = set()
                excluded_roots = {family_data['root_of'].get(mon, mon) for mon in excluded_pokemon}
                for mon in restrict_shared:
                    root = family_data['root_of'].get(mon.lower())
                    if not root or root in seen or root in excluded_roots:
                        continue
                    if not family_has_any_moves(root, family_data, learnsets, moves_data, banned_move_types):
                        continue
                    seen.add(root)
                    valid_roots.append(root)
                if len(valid_roots) >= 2:
                    shared = set.intersection(*(set(get_family_all_moves(root, family_data, learnsets, moves_data, banned_move_types)) for root in valid_roots))
                    for bucket in ('level', 'tm', 'egg', 'other', 'generic'):
                        weighted_results[bucket] = [(move, score) for move, score in weighted_results[bucket] if move in shared]

            print_weighted_results(weighted_results, top_n=20, generic_top_n=12)

        again = input("\n🔁 Do you want to analyze another Pokémon or list? (y/n): ").strip().lower()
        if again != 'y':
            print('👋 Done!')
            break

if __name__ == '__main__':
    main()
