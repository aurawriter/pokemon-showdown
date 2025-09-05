import re
from collections import defaultdict, Counter

print("✅ Script started!")

def parse_pokedex(filename):
    print("📦 Parsing pokedex.ts...")
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read()

    pokedex = {}
    start = data.find("{")
    data = data[start:]
    if data.endswith("};"):
        data = data[:-2]

    entries = re.findall(r'(\w+):\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)},?', data, re.DOTALL)

    count = 0
    for name, block in entries:
        types = re.findall(r'types:\s*\[(.*?)\]', block)
        types = [x.strip().strip('"') for x in types[0].split(',')] if types else []

        egg_groups = re.findall(r'eggGroups:\s*\[(.*?)\]', block)
        egg_groups = [x.strip().strip('"') for x in egg_groups[0].split(',')] if egg_groups else []

        abilities_block = re.search(r'abilities:\s*{(.*?)}', block, re.DOTALL)
        abilities = re.findall(r':\s*"([^"]+)"', abilities_block.group(1)) if abilities_block else []

        pokedex[name.lower()] = {
            "types": types,
            "eggGroups": egg_groups,
            "abilities": abilities,
        }

        count += 1
        if count % 10 == 0 or count < 10:
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

    entries = re.finditer(r'(\w+):\s*{\s*learnset:\s*{(.*?)}\s*(,|})', data, re.DOTALL)

    learnsets = {}
    count = 0
    for match in entries:
        name, moves_block, _ = match.groups()

        move_entries = re.findall(r'(\w+):\s*\[(.*?)\]', moves_block)
        filtered_moves = []
        for move_name, method_block in move_entries:
            methods = [m.strip().strip('"') for m in method_block.split(",")]
            if any(m.startswith(str(target_gen)) for m in methods):
                filtered_moves.append(move_name)

        learnsets[name.lower()] = filtered_moves
        count += 1
        if count % 10 == 0 or count < 10:
            print(f"  🟣 Processed {count} learnsets...")

    print(f"✅ Finished parsing learnsets.ts — found {count} Pokémon.")
    return learnsets

def build_move_map(pokedex, learnsets):
    print("🔧 Building move frequency maps...")
    by_type = defaultdict(list)
    by_egg = defaultdict(list)
    by_ability = defaultdict(list)

    for name, info in pokedex.items():
        if name not in learnsets:
            continue
        for t in info['types']:
            by_type[t].append(name)
        for eg in info['eggGroups']:
            by_egg[eg].append(name)
        for ab in info['abilities']:
            by_ability[ab].append(name)

    def count_moves_by_trait(group_map):
        trait_move_counts = {}
        for trait, mon_list in group_map.items():
            trait_move_counts[trait] = Counter()
            for mon in mon_list:
                for move in learnsets.get(mon, []):
                    trait_move_counts[trait][move] += 1
        return trait_move_counts

    return {
        'type': count_moves_by_trait(by_type),
        'egg': count_moves_by_trait(by_egg),
        'ability': count_moves_by_trait(by_ability),
        'pools': {
            'type': by_type,
            'egg': by_egg,
            'ability': by_ability
        }
    }

def parse_grouped_sets_with_threshold(group_string):
    groups = re.findall(r'{(.*?)}', group_string)
    return [[name.strip().lower() for name in group.split(',')] for group in groups if group.strip()]

def find_common_moves(move_maps, traits, learnsets, similar_pokemon=None, restrict_shared=None, custom_groups=None, threshold=0.5):
    print("\n📊 Finding moves that >50% of Pokémon share for each trait...\n")
    all_suggested = set()

    for category, values in traits.items():
        print(f"🔹 Trait category: {category.capitalize()}")
        for val in values:
            move_counter = move_maps[category].get(val)
            pool = move_maps["pools"][category].get(val)

            if not move_counter or not pool:
                print(f"  ❌ No data for: {val}")
                continue

            total = len(pool)
            min_count = max(1, int(total * threshold))

            print(f"  📘 {val} (in {total} Pokémon): moves in >{min_count} Pokémon")

            common_moves = [(move, count) for move, count in move_counter.items() if count > min_count]
            if common_moves:
                for move, count in sorted(common_moves):
                    percent = round(100 * count / total)
                    print(f"    • {move} ({percent}%)")
                    all_suggested.add(move)
            else:
                print("    (none found)")
        print()

    if similar_pokemon:
        print("🧬 Adding moves from similar Pokémon:")
        for mon in similar_pokemon:
            mon = mon.lower()
            if mon in learnsets:
                moves = learnsets[mon]
                if moves:
                    print(f"  • {mon.capitalize()}: {len(moves)} moves")
                    all_suggested.update(moves)
                else:
                    print(f"  • {mon.capitalize()}: (no moves found)")
            else:
                print(f"  • {mon.capitalize()}: ❌ not found")
        print()

    if custom_groups:
        print("🧪 Group-based shared move analysis:")
        for idx, group in enumerate(custom_groups):
            valid = [m for m in group if m in learnsets]
            if len(valid) < 2:
                print(f"  Group {idx+1}: ⚠️ Need at least 2 valid Pokémon")
                continue
            pool = [learnsets[m] for m in valid]
            total = len(pool)
            counter = Counter()
            for moves in pool:
                counter.update(set(moves))
            shared = [(move, count) for move, count in counter.items() if count / total >= threshold]
            if shared:
                print(f"  Group {idx+1} ({', '.join(valid)}):")
                for move, count in sorted(shared):
                    percent = round(100 * count / total)
                    print(f"    • {move} ({percent}%)")
                    all_suggested.add(move)
            else:
                print(f"  Group {idx+1}: (no common moves found)")
        print()

    if restrict_shared:
        print("🔒 Restricting to moves shared by:")
        valid = [mon.lower() for mon in restrict_shared if mon.lower() in learnsets]
        if len(valid) >= 2:
            sets = [set(learnsets[m]) for m in valid]
            shared = set.intersection(*sets)
            print(f"  ✅ {len(shared)} moves shared by {', '.join(valid)}")
            all_suggested &= shared
        elif len(valid) == 1:
            print("  ℹ️ Only one valid mon provided — skipping restriction")
        else:
            print("  ⚠️ No valid mons — skipping restriction")

    if all_suggested:
        print("\n🧾 Final suggested moves (no repeats):")
        print(", ".join(sorted(all_suggested)))
    else:
        print("⚠️ No suggested moves found after applying all filters.")

try:
    pokedex = parse_pokedex("pokedex.ts")
except FileNotFoundError as e:
    print("❌ File not found:", e)
    exit()

if len(pokedex) == 0:
    print("⚠️ No Pokémon were parsed from pokedex.ts — check the format or file path.")
    exit()

while True:
    while True:
        gen_input = input("Enter target generation (1–9): ").strip()
        if gen_input.isdigit() and 1 <= int(gen_input) <= 9:
            gen = int(gen_input)
            break
        print("❗ Please enter a number between 1 and 9.")

    try:
        learnsets = parse_learnsets("learnsets.ts", gen)
    except FileNotFoundError as e:
        print("❌ File not found:", e)
        exit()

    if len(learnsets) == 0:
        print("⚠️ No Pokémon were parsed from learnsets.ts — check the format or file path.")
        exit()

    move_maps = build_move_map(pokedex, learnsets)

    types = input("Enter types (comma separated, e.g. Fairy, Fire): ").strip().split(",")
    egg_groups = input("Enter egg groups (comma separated, e.g. Field, Fairy): ").strip().split(",")
    abilities = input("Enter abilities (comma separated, e.g. Intimidate, Chlorophyll): ").strip().split(",")

    custom_traits = {
        "type": [x.strip() for x in types],
        "egg": [x.strip() for x in egg_groups],
        "ability": [x.strip() for x in abilities],
    }

    similar_input = input("Enter specific Pokémon to base this off (comma separated), or leave blank: ").strip()
    similar_pokemon = [x.strip() for x in similar_input.split(",") if x.strip()] if similar_input else []

    shared_input = input("Enter Pokémon to restrict to shared moves only (comma separated), or leave blank: ").strip()
    restrict_shared = [x.strip() for x in shared_input.split(",") if x.strip()] if shared_input else []

    group_input = input("Enter Pokémon groups using braces (e.g. {A,B,C}, {X,Y}), or leave blank: ").strip()
    grouped_sets = parse_grouped_sets_with_threshold(group_input) if group_input else []

    threshold_input = input("What minimum percentage should a move appear in a group to count? (default 50): ").strip()
    try:
        threshold_value = float(threshold_input) / 100 if threshold_input else 0.5
    except ValueError:
        threshold_value = 0.5

    find_common_moves(
        move_maps,
        custom_traits,
        learnsets,
        similar_pokemon=similar_pokemon,
        restrict_shared=restrict_shared,
        custom_groups=grouped_sets,
        threshold=threshold_value
    )

    again = input("\n🔁 Do you want to analyze another Pokémon or list? (y/n): ").strip().lower()
    if again != "y":
        print("👋 Done!")
        break
