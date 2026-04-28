#!/usr/bin/env python3
"""
Suggest level-up learn levels and TM flags for custom Pokemon learnsets.

What this script does
---------------------
Given a Pokemon species name, it reads local `learnsets.ts` and `moves.ts`
from the same folder as this script and tries to:

1. Find moves currently marked as `9L1` for that species.
2. Suggest better level-up levels for those moves.
3. Suggest which moves look like they should be TMs instead of, or in
   addition to, level-up moves.

This is designed for Pokemon Showdown-style data files, especially custom
projects where a lot of placeholder learn methods were coded as `9L1`.

How it works
------------
The script uses heuristics rather than pretending it knows the exact intended
answer:

- It parses `learnsets.ts` to collect how *other* Pokemon learn each move.
- It uses non-suspicious existing level-up learn data to estimate a typical
  level for each move.
- It uses `moves.ts` to inspect move properties such as category, base power,
  accuracy, PP, priority, target, flags, and type.
- It scores moves into rough buckets like early / mid / late and then refines
  with observed learnset data if available.
- It also scores whether a move feels TM-like based on distribution and move
  traits.

This script intentionally avoids directly editing your files. It prints
suggestions first so you can review them.

Usage
-----
python pokemon_learnset_cleanup.py Pikachu
python pokemon_learnset_cleanup.py "MyCustomMon"
python pokemon_learnset_cleanup.py MyCustomMon --include-all
python pokemon_learnset_cleanup.py MyCustomMon --json

Optional flags
--------------
--include-all   Analyze all level-up moves for the species, not just `9L1`.
--json          Print machine-readable JSON instead of a text report.
--min-samples N Require at least N external level-up samples to trust observed
                data strongly. Default: 3

Assumptions / limitations
-------------------------
- The parser is built for common Showdown-style TS object syntax, not arbitrary
  TypeScript.
- It ignores very suspicious `L1` data from other mons when estimating levels,
  because those placeholders can pollute results.
- TM detection is heuristic because custom formats vary a lot.
- If your files diverge heavily from Showdown structure, you may need to tweak
  the regexes near the parser section.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


# -----------------------------------------------------------------------------
# Data models
# -----------------------------------------------------------------------------

@dataclass
class MoveInfo:
    move_id: str
    name: str
    type: Optional[str] = None
    category: Optional[str] = None
    base_power: Optional[int] = None
    accuracy: Optional[Any] = None
    pp: Optional[int] = None
    priority: Optional[int] = None
    target: Optional[str] = None
    flags: Dict[str, Any] = field(default_factory=dict)
    secondary: bool = False
    self_boost: bool = False
    boosts: bool = False
    status: Optional[str] = None
    volatile_status: Optional[str] = None
    side_condition: Optional[str] = None
    weather: Optional[str] = None
    terrain: Optional[str] = None
    pseudo_weather: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None
    multihit: Optional[Any] = None
    recoil: Optional[Any] = None
    drain: Optional[Any] = None
    heal: Optional[Any] = None
    ohko: Optional[bool] = None
    will_crit: Optional[bool] = None
    stalling_move: bool = False
    protect_like: bool = False
    pivot_move: bool = False
    hazard_move: bool = False
    removal_move: bool = False
    recovery_move: bool = False
    setup_move: bool = False


@dataclass
class LearnMethod:
    raw: str
    generation: Optional[int]
    method: str
    level: Optional[int] = None


@dataclass
class SpeciesLearnset:
    species_id: str
    species_name: str
    moves: Dict[str, List[LearnMethod]] = field(default_factory=dict)


@dataclass
class MoveLevelStats:
    samples: List[int] = field(default_factory=list)
    source_species: List[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.samples)

    @property
    def mean(self) -> Optional[float]:
        return statistics.mean(self.samples) if self.samples else None

    @property
    def median(self) -> Optional[float]:
        return statistics.median(self.samples) if self.samples else None


@dataclass
class Suggestion:
    move_id: str
    move_name: str
    current_methods: List[str]
    suggested_level: Optional[int]
    level_bucket: str
    level_confidence: str
    tm_recommendation: str
    tm_confidence: str
    rationale: List[str]
    observed_level_samples: List[int]
    suggested_methods: List[str]


# -----------------------------------------------------------------------------
# Utility helpers
# -----------------------------------------------------------------------------

def to_id(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def normalize_species_name(species_id: str) -> str:
    # Best-effort display formatting.
    if not species_id:
        return species_id
    words = re.findall(r"[a-z]+|[0-9]+", species_id.lower())
    return " ".join(w.capitalize() for w in words)


def split_top_level_items(body: str) -> List[str]:
    items: List[str] = []
    current: List[str] = []
    depth_brace = depth_bracket = depth_paren = 0
    in_string: Optional[str] = None
    escape = False

    for ch in body:
        current.append(ch)
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_string:
                in_string = None
            continue

        if ch in ('"', "'", "`"):
            in_string = ch
        elif ch == '{':
            depth_brace += 1
        elif ch == '}':
            depth_brace -= 1
        elif ch == '[':
            depth_bracket += 1
        elif ch == ']':
            depth_bracket -= 1
        elif ch == '(':
            depth_paren += 1
        elif ch == ')':
            depth_paren -= 1
        elif ch == ',' and depth_brace == 0 and depth_bracket == 0 and depth_paren == 0:
            items.append("".join(current[:-1]).strip())
            current = []

    tail = "".join(current).strip()
    if tail:
        items.append(tail)
    return items


def extract_balanced_braces(text: str, start_index: int) -> Tuple[str, int]:
    if start_index < 0 or start_index >= len(text) or text[start_index] != '{':
        raise ValueError("extract_balanced_braces must start at a '{' character")

    depth = 0
    in_string: Optional[str] = None
    escape = False

    for i in range(start_index, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_string:
                in_string = None
            continue

        if ch in ('"', "'", "`"):
            in_string = ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return text[start_index:i + 1], i + 1

    raise ValueError("Unbalanced braces while parsing file")


def parse_js_scalar(value: str) -> Any:
    value = value.strip()
    if value in ("true", "false"):
        return value == "true"
    if value == "null":
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def parse_simple_object(obj_text: str) -> Dict[str, Any]:
    obj_text = obj_text.strip()
    if obj_text.startswith('{') and obj_text.endswith('}'):
        obj_text = obj_text[1:-1]
    result: Dict[str, Any] = {}
    for item in split_top_level_items(obj_text):
        if not item or ':' not in item:
            continue
        key, value = item.split(':', 1)
        key = key.strip().strip("'\"")
        value = value.strip()
        if value.startswith('{') and value.endswith('}'):
            result[key] = parse_simple_object(value)
        elif value.startswith('[') and value.endswith(']'):
            inner = value[1:-1].strip()
            result[key] = [parse_js_scalar(x) for x in split_top_level_items(inner)] if inner else []
        else:
            result[key] = parse_js_scalar(value)
    return result


# -----------------------------------------------------------------------------
# Parsing learnsets.ts
# -----------------------------------------------------------------------------

def parse_learn_method(method_str: str) -> LearnMethod:
    raw = method_str.strip().strip("'\"")
    match = re.fullmatch(r"(\d+)([A-Za-z]+)(\d+)?", raw)
    if not match:
        return LearnMethod(raw=raw, generation=None, method=raw, level=None)
    generation = int(match.group(1))
    method = match.group(2)
    level = int(match.group(3)) if match.group(3) is not None else None
    return LearnMethod(raw=raw, generation=generation, method=method, level=level)


def parse_learnsets(learnsets_text: str) -> Dict[str, SpeciesLearnset]:
    export_match = re.search(r"export\s+const\s+Learnsets\s*:\s*\{[^=]*=\s*\{", learnsets_text)
    if export_match:
        start = learnsets_text.find('{', export_match.end() - 1)
    else:
        fallback = learnsets_text.find('{')
        if fallback == -1:
            raise ValueError("Could not locate Learnsets export object")
        start = fallback

    outer_text, _ = extract_balanced_braces(learnsets_text, start)
    outer_body = outer_text[1:-1]

    species_map: Dict[str, SpeciesLearnset] = {}
    pos = 0
    while pos < len(outer_body):
        m = re.search(r"([A-Za-z0-9_]+)\s*:\s*\{", outer_body[pos:])
        if not m:
            break
        species_id = m.group(1)
        obj_start = pos + m.end() - 1
        species_obj_text, obj_end = extract_balanced_braces(outer_body, obj_start)
        pos = obj_end

        learnset_match = re.search(r"learnset\s*:\s*\{", species_obj_text)
        if not learnset_match:
            continue
        ls_start = species_obj_text.find('{', learnset_match.end() - 1)
        learnset_text, _ = extract_balanced_braces(species_obj_text, ls_start)
        learnset_body = learnset_text[1:-1]

        species = SpeciesLearnset(
            species_id=species_id,
            species_name=normalize_species_name(species_id),
            moves={},
        )

        for entry in split_top_level_items(learnset_body):
            if ':' not in entry:
                continue
            move_id_raw, methods_raw = entry.split(':', 1)
            move_id = move_id_raw.strip().strip("'\"")
            methods_raw = methods_raw.strip()
            if not methods_raw.startswith('['):
                continue
            end_idx = methods_raw.rfind(']')
            if end_idx == -1:
                continue
            methods_body = methods_raw[1:end_idx]
            methods = [parse_learn_method(x) for x in split_top_level_items(methods_body) if x.strip()]
            species.moves[move_id] = methods

        species_map[species_id] = species

    return species_map


# -----------------------------------------------------------------------------
# Parsing moves.ts
# -----------------------------------------------------------------------------


def parse_moves(moves_text: str) -> Dict[str, MoveInfo]:
    # Simpler parser modeled after the working project script style.
    lines = moves_text.splitlines()
    moves: Dict[str, MoveInfo] = {}
    current_move: Optional[str] = None
    current_block: List[str] = []
    depth = 0
    in_moves_table = False
    entry_start = re.compile(r'^\s*(?:"([^"]+)"|([\w-]+)):\s*{\s*$')

    for line in lines:
        if not in_moves_table:
            if "export const Moves" in line:
                in_moves_table = True
            continue

        if current_move is None:
            match = entry_start.match(line)
            if match:
                current_move = to_id(match.group(1) or match.group(2))
                current_block = [line]
                depth = line.count("{") - line.count("}")
            continue

        current_block.append(line)
        depth += line.count("{") - line.count("}")

        if depth <= 0:
            block_text = "\n".join(current_block)
            name_match = re.search(r'name\s*:\s*"([^"]+)"', block_text)
            type_match = re.search(r'type\s*:\s*"([^"]+)"', block_text)
            category_match = re.search(r'category\s*:\s*"([^"]+)"', block_text)
            power_match = re.search(r'basePower\s*:\s*(\d+|true|false)', block_text)
            accuracy_match = re.search(r'accuracy\s*:\s*(\d+|true|false)', block_text)
            pp_match = re.search(r'pp\s*:\s*(\d+)', block_text)
            priority_match = re.search(r'priority\s*:\s*(-?\d+)', block_text)
            target_match = re.search(r'target\s*:\s*"([^"]+)"', block_text)
            status_match = re.search(r'status\s*:\s*"([^"]+)"', block_text)
            weather_match = re.search(r'weather\s*:\s*"([^"]+)"', block_text)
            terrain_match = re.search(r'terrain\s*:\s*"([^"]+)"', block_text)
            side_condition_match = re.search(r'sideCondition\s*:\s*"([^"]+)"', block_text)

            flags = {}
            flags_match = re.search(r'flags\s*:\s*{([^}]*)}', block_text, re.DOTALL)
            if flags_match:
                for k, v in re.findall(r'([A-Za-z][\w-]*)\s*:\s*(\d+|true|false)', flags_match.group(1)):
                    flags[k] = True if v == "true" else False if v == "false" else int(v)

            boosts = {}
            boosts_match = re.search(r'boosts\s*:\s*{([^}]*)}', block_text, re.DOTALL)
            if boosts_match:
                for k, v in re.findall(r'([A-Za-z][\w-]*)\s*:\s*(-?\d+)', boosts_match.group(1)):
                    boosts[k] = int(v)

            self_boost = False
            self_match = re.search(r'self\s*:\s*{([^}]*)}', block_text, re.DOTALL)
            if self_match and 'boosts' in self_match.group(1):
                self_boost = True

            bp = power_match.group(1) if power_match else None
            if bp == "true":
                bp_val = 0
            elif bp == "false":
                bp_val = 0
            elif bp is not None:
                bp_val = int(bp)
            else:
                bp_val = None

            acc = accuracy_match.group(1) if accuracy_match else None
            if acc == "true":
                acc_val = 101
            elif acc == "false":
                acc_val = None
            elif acc is not None:
                acc_val = int(acc)
            else:
                acc_val = None

            move = MoveInfo(
                move_id=current_move,
                name=name_match.group(1) if name_match else normalize_species_name(current_move),
                type=type_match.group(1) if type_match else None,
                category=category_match.group(1) if category_match else None,
                base_power=bp_val,
                accuracy=acc_val,
                pp=int(pp_match.group(1)) if pp_match else None,
                priority=int(priority_match.group(1)) if priority_match else None,
                target=target_match.group(1) if target_match else None,
                flags=flags,
                secondary='secondary' in block_text and 'secondary: null' not in block_text,
                self_boost=self_boost,
                boosts=bool(boosts),
                status=status_match.group(1) if status_match else None,
                volatile_status=None,
                side_condition=side_condition_match.group(1) if side_condition_match else None,
                weather=weather_match.group(1) if weather_match else None,
                terrain=terrain_match.group(1) if terrain_match else None,
                pseudo_weather=None,
                condition={},
                multihit=None,
                recoil=None,
                drain=None,
                heal=None,
                ohko=('ohko' in block_text),
                will_crit=('willCrit' in block_text),
                stalling_move=('stallingMove' in block_text and 'stallingMove: true' in block_text),
                protect_like=bool(flags.get('protect')) or current_move in {"protect", "detect", "endure", "spikyshield", "kingsshield", "banefulbunker", "silktrap", "burningbulwark"},
                pivot_move=current_move in {"uturn", "voltswitch", "flipturn", "partingshot", "teleport", "chillyreception"},
                hazard_move=(side_condition_match.group(1) if side_condition_match else None) in {"spikes", "stealthrock", "toxicspikes", "stickyweb"},
                removal_move=current_move in {"rapidspin", "defog", "mortalspin", "tidyup"},
                recovery_move=current_move in {"recover", "softboiled", "roost", "slackoff", "milkdrink", "shoreup", "moonlight", "morningsun", "synthesis", "healorder", "rest"},
                setup_move=bool(boosts) or self_boost or current_move in {"swordsdance", "nastyplot", "dragondance", "quiverdance", "bulkup", "calmmind", "agility", "rockpolish", "tailglow", "shellsmash", "curse", "growth", "coil", "honeclaws"},
            )
            moves[current_move] = move

            current_move = None
            current_block = []
            depth = 0

    return moves

def parse_move_object(move_id: str, obj_text: str) -> MoveInfo:
    fields: Dict[str, Any] = {}

    def capture_scalar(key: str) -> None:
        m = re.search(rf"\b{re.escape(key)}\s*:\s*([^,\n}}]+)", obj_text)
        if m:
            fields[key] = parse_js_scalar(m.group(1).strip())

    for key in [
        "name", "type", "category", "basePower", "accuracy", "pp", "priority",
        "target", "status", "volatileStatus", "sideCondition", "weather",
        "terrain", "pseudoWeather", "multihit", "recoil", "drain", "heal",
        "ohko", "willCrit",
    ]:
        capture_scalar(key)

    for key in ["flags", "condition", "boosts", "secondary", "self"]:
        m = re.search(rf"\b{re.escape(key)}\s*:\s*(\{{)", obj_text)
        if m:
            sub_text, _ = extract_balanced_braces(obj_text, m.start(1))
            fields[key] = parse_simple_object(sub_text)

    for key in ["stallingMove"]:
        capture_scalar(key)

    flags = fields.get("flags") or {}
    condition = fields.get("condition") or {}
    self_obj = fields.get("self") or {}
    boosts = fields.get("boosts") or {}
    secondary = bool(fields.get("secondary"))
    self_boost = bool(self_obj.get("boosts")) if isinstance(self_obj, dict) else False

    move = MoveInfo(
        move_id=move_id,
        name=fields.get("name") or normalize_species_name(move_id),
        type=fields.get("type"),
        category=fields.get("category"),
        base_power=fields.get("basePower") if isinstance(fields.get("basePower"), int) else None,
        accuracy=fields.get("accuracy"),
        pp=fields.get("pp") if isinstance(fields.get("pp"), int) else None,
        priority=fields.get("priority") if isinstance(fields.get("priority"), int) else None,
        target=fields.get("target"),
        flags=flags if isinstance(flags, dict) else {},
        secondary=secondary,
        self_boost=self_boost,
        boosts=bool(boosts),
        status=fields.get("status"),
        volatile_status=fields.get("volatileStatus"),
        side_condition=fields.get("sideCondition"),
        weather=fields.get("weather"),
        terrain=fields.get("terrain"),
        pseudo_weather=fields.get("pseudoWeather"),
        condition=condition if isinstance(condition, dict) else {},
        multihit=fields.get("multihit"),
        recoil=fields.get("recoil"),
        drain=fields.get("drain"),
        heal=fields.get("heal"),
        ohko=bool(fields.get("ohko")) if fields.get("ohko") is not None else None,
        will_crit=bool(fields.get("willCrit")) if fields.get("willCrit") is not None else None,
        stalling_move=bool(fields.get("stallingMove")),
        protect_like=bool(flags.get("protect")) or move_id in {"protect", "detect", "endure", "spikyshield", "kingsshield", "banefulbunker", "silktrap", "burningbulwark"},
        pivot_move=move_id in {"uturn", "voltswitch", "flipturn", "partingshot", "teleport", "chillyreception"},
        hazard_move=fields.get("sideCondition") in {"spikes", "stealthrock", "toxicspikes", "stickyweb"},
        removal_move=move_id in {"rapidspin", "defog", "mortalspin", "tidyup"},
        recovery_move=(fields.get("heal") is not None) or move_id in {"recover", "softboiled", "roost", "slackoff", "milkdrink", "shoreup", "moonlight", "morningsun", "synthesis", "healorder", "rest"},
        setup_move=bool(boosts) or self_boost or move_id in {"swordsdance", "nastyplot", "dragondance", "quiverdance", "bulkup", "calmmind", "agility", "rockpolish", "tailglow", "shellsmash", "curse", "growth", "coil", "honeclaws"},
    )
    return move


# -----------------------------------------------------------------------------
# Statistical analysis
# -----------------------------------------------------------------------------

def is_suspicious_level_one(methods: List[LearnMethod]) -> bool:
    level_methods = [m for m in methods if m.method == 'L' and m.level is not None]
    if not level_methods:
        return False
    unique_levels = {m.level for m in level_methods}
    return unique_levels == {1} and len(level_methods) >= 3


def collect_move_level_stats(learnsets: Dict[str, SpeciesLearnset]) -> Dict[str, MoveLevelStats]:
    stats: Dict[str, MoveLevelStats] = defaultdict(MoveLevelStats)

    for species_id, species in learnsets.items():
        for move_id, methods in species.moves.items():
            if is_suspicious_level_one(methods):
                continue

            levels = sorted({m.level for m in methods if m.method == 'L' and m.level is not None})
            if not levels:
                continue

            # Use the first non-trivial learn level as the signal. Skip pure L1 unless it is the
            # only observed level and the species does not look suspicious.
            picked: Optional[int] = None
            non_l1 = [lv for lv in levels if lv > 1]
            if non_l1:
                picked = non_l1[0]
            elif len(levels) == 1 and levels[0] == 1:
                picked = 1

            if picked is not None:
                stats[move_id].samples.append(picked)
                stats[move_id].source_species.append(species_id)

    return stats


def collect_tm_distribution(learnsets: Dict[str, SpeciesLearnset]) -> Dict[str, Counter]:
    dist: Dict[str, Counter] = defaultdict(Counter)
    for species in learnsets.values():
        for move_id, methods in species.moves.items():
            method_names = {m.method for m in methods}
            if 'M' in method_names:
                dist[move_id]['tm_species'] += 1
            if 'L' in method_names:
                dist[move_id]['level_species'] += 1
            dist[move_id]['total_species'] += 1
    return dist


# -----------------------------------------------------------------------------
# Heuristics
# -----------------------------------------------------------------------------

def bucket_for_level(level: int) -> str:
    if level <= 15:
        return "early game"
    if level <= 34:
        return "mid game"
    return "late game"


def clamp_level(level: int) -> int:
    return max(1, min(100, level))


def round_to_design_level(level: float) -> int:
    # Nice round-ish learn levels for RPG feel.
    if level <= 10:
        return int(round(level))
    candidates = [
        12, 14, 15, 16, 18, 20, 22, 24, 25, 26, 28, 30, 32, 34, 35, 36,
        38, 40, 42, 44, 45, 48, 50, 52, 55, 60, 65, 70, 75, 80
    ]
    return min(candidates, key=lambda x: abs(x - level))


def infer_level_from_move_traits(move: Optional[MoveInfo]) -> Tuple[int, List[str]]:
    if move is None:
        return 24, ["No move data found in moves.ts, so defaulted to a mid-game estimate."]

    score = 20.0
    reasons: List[str] = []

    category = move.category or ""
    base_power = move.base_power if move.base_power is not None else 0

    if category == "Status":
        score -= 2
        reasons.append("Status moves often appear earlier than strong damaging moves.")
    else:
        if base_power <= 40:
            score -= 8
            reasons.append("Very low base power suggests an early learn level.")
        elif base_power <= 60:
            score -= 3
            reasons.append("Moderate-low base power leans earlier.")
        elif base_power <= 80:
            reasons.append("Midrange power fits a mid-game move.")
        elif base_power <= 100:
            score += 8
            reasons.append("High base power suggests a later learn level.")
        else:
            score += 16
            reasons.append("Very high base power suggests a late learn level.")

    if move.priority and move.priority > 0:
        score += 2
        reasons.append("Priority often gets delayed slightly because of utility.")
    if move.secondary:
        score += 2
        reasons.append("Secondary effects add value, nudging the move later.")
    if move.status in {"slp", "frz"}:
        score += 10
        reasons.append("Strong status effects like sleep/freeze are usually learned later.")
    elif move.status in {"brn", "par", "psn", "tox"}:
        score += 4
        reasons.append("Reliable status infliction pushes the move a bit later.")
    if move.setup_move:
        score += 8
        reasons.append("Setup moves are usually not extremely early.")
    if move.recovery_move:
        score += 8
        reasons.append("Reliable recovery is often mid-to-late progression.")
    if move.hazard_move or move.removal_move:
        score += 10
        reasons.append("Field control moves are often held for later progression.")
    if move.pivot_move:
        score += 8
        reasons.append("Pivot utility tends to be learned mid/late rather than at the start.")
    if move.protect_like:
        score += 2
        reasons.append("Protect-style utility is often not a very first move.")
    if move.ohko:
        score += 25
        reasons.append("OHKO properties strongly imply a very late learn level.")
    if move.weather or move.terrain or move.pseudo_weather:
        score += 8
        reasons.append("Field-setting utility often arrives later.")
    if move.stalling_move:
        score += 4
        reasons.append("Stalling-focused tools tend to skew later.")
    if move.will_crit:
        score += 3
        reasons.append("Always-crit style moves are usually not super early.")
    if move.multihit is not None:
        score += 1
        reasons.append("Multi-hit utility nudges the move slightly later.")
    if move.drain is not None:
        score += 2
        reasons.append("Drain utility adds extra value.")
    if move.recoil is not None and category != "Status":
        score += 2
        reasons.append("Strong recoil moves are often learned after basic attacks.")
    if move.accuracy is not None and isinstance(move.accuracy, int) and move.accuracy < 85:
        score += 2
        reasons.append("Lower accuracy can correspond with higher-risk later moves.")

    inferred = clamp_level(round_to_design_level(score))
    return inferred, reasons


def infer_tm_likelihood(move_id: str, move: Optional[MoveInfo], tm_dist: Counter, level_stats: Optional[MoveLevelStats]) -> Tuple[str, str, List[str]]:
    reasons: List[str] = []
    score = 0.0

    total_species = tm_dist.get('total_species', 0)
    tm_species = tm_dist.get('tm_species', 0)
    level_species = tm_dist.get('level_species', 0)
    tm_ratio = (tm_species / total_species) if total_species else 0.0

    if total_species >= 5:
        if tm_ratio >= 0.6:
            score += 3
            reasons.append("This move is frequently learned by TM on other species.")
        elif tm_ratio >= 0.3:
            score += 1.5
            reasons.append("This move has meaningful TM precedent on other species.")
        elif tm_ratio <= 0.1 and level_species > 0:
            score -= 1.5
            reasons.append("This move is rarely seen as a TM compared with level-up learnsets.")

    if move is not None:
        if move.hazard_move or move.removal_move:
            score += 2
            reasons.append("Hazard setting/removal is commonly TM-like utility.")
        if move.recovery_move:
            score += 1
            reasons.append("Recovery sometimes appears as shared utility/TM access.")
        if move.protect_like:
            score += 2
            reasons.append("Protect-style utility is very TM-like.")
        if move.pivot_move:
            score += 2
            reasons.append("Pivot moves are often distributed broadly.")
        if move.setup_move:
            score += 1
            reasons.append("Setup moves are often candidates for technical distribution.")
        if move.category == "Status":
            score += 1
            reasons.append("Status and utility moves are more likely to be TM-like than signature attacks.")
        if move.base_power is not None and move.base_power >= 100:
            score -= 1
            reasons.append("Very strong attacks are a bit less likely to be broadly distributed by TM.")
        if move.ohko:
            score -= 3
            reasons.append("OHKO moves are poor TM candidates.")

    shared_distribution = (level_stats.count if level_stats else 0)
    if shared_distribution >= 15:
        score += 2
        reasons.append("This move has wide species distribution, which favors TM treatment.")
    elif shared_distribution >= 6:
        score += 1
        reasons.append("This move appears on several species, which mildly favors TM treatment.")
    elif shared_distribution <= 1:
        score -= 1
        reasons.append("This move has very narrow distribution, which leans away from TM treatment.")

    if score >= 4:
        return "TM recommended", "high", reasons
    if score >= 2:
        return "TM possible", "medium", reasons
    if score >= 0:
        return "Level-up preferred, TM optional", "medium", reasons
    return "Level-up preferred", "high", reasons


def combine_observed_and_inferred_level(
    move_id: str,
    move: Optional[MoveInfo],
    stats: Optional[MoveLevelStats],
    min_samples: int,
) -> Tuple[int, str, List[str], List[int]]:
    inferred_level, inferred_reasons = infer_level_from_move_traits(move)
    reasons = list(inferred_reasons)
    samples = list(stats.samples) if stats else []

    if stats and stats.count:
        median = stats.median if stats.median is not None else inferred_level
        mean = stats.mean if stats.mean is not None else inferred_level
        observed = (median * 0.7) + (mean * 0.3)

        if stats.count >= min_samples:
            blended = (observed * 0.8) + (inferred_level * 0.2)
            reasons.insert(0, f"Observed learn levels on {stats.count} other species provide a strong anchor.")
            confidence = "high" if stats.count >= 8 else "medium"
        else:
            blended = (observed * 0.45) + (inferred_level * 0.55)
            reasons.insert(0, f"Only {stats.count} external learnset sample(s) were found, so move traits still matter a lot.")
            confidence = "medium"
    else:
        blended = inferred_level
        reasons.insert(0, "No external level-up data was found for this move, so the estimate is trait-based.")
        confidence = "low"

    suggested_level = clamp_level(round_to_design_level(blended))

    # Small cleanup rule: avoid obviously weird late placement for baby-tier moves.
    if move is not None and move.category != "Status" and (move.base_power or 0) <= 40 and suggested_level > 25:
        suggested_level = 20
        reasons.append("The result was capped downward because a weak attack probably should not be that late.")

    return suggested_level, confidence, reasons, samples


# -----------------------------------------------------------------------------
# Main suggestion pipeline
# -----------------------------------------------------------------------------

def build_suggestions(
    species_name: str,
    learnsets: Dict[str, SpeciesLearnset],
    moves: Dict[str, MoveInfo],
    include_all: bool,
    min_samples: int,
) -> Dict[str, Any]:
    species_id = to_id(species_name)
    if species_id not in learnsets:
        close = sorted(learnsets.keys(), key=lambda s: levenshtein_like(species_id, s))[:10]
        raise KeyError(
            f"Species '{species_name}' not found. Closest matches: {', '.join(close) if close else 'none'}"
        )

    target = learnsets[species_id]
    move_level_stats = collect_move_level_stats(learnsets)
    tm_distribution = collect_tm_distribution(learnsets)

    suggestions: List[Suggestion] = []

    for move_id, methods in sorted(target.moves.items()):
        current_raw = [m.raw for m in methods]
        if not include_all:
            if not any(m.method == 'L' and m.level == 1 and (m.generation == 9 or m.generation is None) for m in methods):
                continue

        move_info = moves.get(move_id)
        stats = move_level_stats.get(move_id)
        suggested_level, level_confidence, level_reasons, observed_samples = combine_observed_and_inferred_level(
            move_id=move_id,
            move=move_info,
            stats=stats,
            min_samples=min_samples,
        )

        tm_label, tm_confidence, tm_reasons = infer_tm_likelihood(
            move_id=move_id,
            move=move_info,
            tm_dist=tm_distribution.get(move_id, Counter()),
            level_stats=stats,
        )

        rationale = level_reasons + tm_reasons
        level_bucket = bucket_for_level(suggested_level)

        existing_non_placeholder = []
        if any(m.method == 'M' for m in methods):
            existing_non_placeholder.append('9M')

        suggested_methods = [f"9L{suggested_level}"]
        if tm_label in {"TM recommended", "TM possible", "Level-up preferred, TM optional"}:
            suggested_methods.append("9M")

        # Remove duplicates while preserving order.
        seen = set()
        suggested_methods = [x for x in suggested_methods if not (x in seen or seen.add(x))]

        suggestions.append(
            Suggestion(
                move_id=move_id,
                move_name=move_info.name if move_info else normalize_species_name(move_id),
                current_methods=current_raw,
                suggested_level=suggested_level,
                level_bucket=level_bucket,
                level_confidence=level_confidence,
                tm_recommendation=tm_label,
                tm_confidence=tm_confidence,
                rationale=rationale,
                observed_level_samples=observed_samples,
                suggested_methods=suggested_methods,
            )
        )

    return {
        "species_id": target.species_id,
        "species_name": target.species_name,
        "suggestions": suggestions,
    }


def levenshtein_like(a: str, b: str) -> int:
    # Tiny cheap distance for close-match hints.
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    dp = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev = dp[0]
        dp[0] = i
        for j, cb in enumerate(b, 1):
            old = dp[j]
            cost = 0 if ca == cb else 1
            dp[j] = min(dp[j] + 1, dp[j - 1] + 1, prev + cost)
            prev = old
    return dp[-1]


# -----------------------------------------------------------------------------
# Output formatting
# -----------------------------------------------------------------------------

def format_text_report(report: Dict[str, Any]) -> str:
    def sort_learnset_key(item):
        move_id, methods = item
        def first_level(methods_list):
            levels = []
            for m in methods_list:
                if m.startswith("9L"):
                    try:
                        levels.append(int(m[2:]))
                    except ValueError:
                        pass
            return min(levels) if levels else 999
        return (first_level(methods), move_id)

    out: List[str] = []
    out.append(f"Learnset cleanup suggestions for {report['species_name']} ({report['species_id']})")
    out.append("=" * 72)

    suggestions: List[Suggestion] = report["suggestions"]
    if not suggestions:
        out.append("No matching moves found. By default, this script only analyzes moves that include 9L1.")
        out.append("Try again with --include-all if you want every level-up move reviewed.")
        return "\n".join(out)

    for s in suggestions:
        out.append("")
        out.append(f"{s.move_name} [{s.move_id}]")
        out.append(f"  Current methods: {', '.join(s.current_methods)}")
        out.append(f"  Suggested level: {s.suggested_level} ({s.level_bucket}, confidence: {s.level_confidence})")
        out.append(f"  TM call: {s.tm_recommendation} (confidence: {s.tm_confidence})")
        out.append(f"  Suggested methods: {', '.join(s.suggested_methods)}")
        if s.observed_level_samples:
            sample_preview = ", ".join(map(str, s.observed_level_samples[:12]))
            suffix = " ..." if len(s.observed_level_samples) > 12 else ""
            out.append(f"  Observed external levels: {sample_preview}{suffix}")
        out.append("  Rationale:")
        for reason in s.rationale[:8]:
            out.append(f"    - {reason}")

    out.append("")
    out.append("Copy-paste learnset block")
    out.append("-" * 72)
    out.append(f"{report['species_id']}: {{")
    out.append("\tlearnset: {")
    sorted_suggestions = sorted(
        [s for s in suggestions if s.suggested_methods],
        key=lambda s: sort_learnset_key((s.move_id, s.suggested_methods))
    )
    for s in sorted_suggestions:
        methods = ", ".join(f'"{m}"' for m in s.suggested_methods)
        out.append(f'\t\t{s.move_id}: [{methods}],')
    out.append("\t},")
    out.append("},")

    out.append("")
    out.append("Suggested patch snippets")
    out.append("-" * 72)
    for s in suggestions:
        out.append(f"'{s.move_id}': {json.dumps(s.suggested_methods)},")

    return "\n".join(out)


def format_json_report(report: Dict[str, Any]) -> str:
    payload = {
        "species_id": report["species_id"],
        "species_name": report["species_name"],
        "suggestions": [asdict(s) for s in report["suggestions"]],
    }
    return json.dumps(payload, indent=2)




# -----------------------------------------------------------------------------
# Auto-similar-mon selection (based on the weighted similarity logic from plt.py)
# -----------------------------------------------------------------------------

@dataclass
class SpeciesInfo:
    species_id: str
    types: List[str] = field(default_factory=list)
    egg_groups: List[str] = field(default_factory=list)
    abilities: List[str] = field(default_factory=list)
    base_stats: Dict[str, int] = field(default_factory=dict)
    bodyshape: Optional[str] = None
    num: Optional[int] = None


def parse_pokedex(pokedex_text: str) -> Dict[str, SpeciesInfo]:
    # Use a simpler, plt.py-style parser because it is already known to work well
    # on this project's pokedex.ts formatting.
    start = pokedex_text.find("{")
    if start == -1:
        raise ValueError("Could not locate Pokedex object")

    data = pokedex_text[start:]
    if data.endswith("};"):
        data = data[:-2]

    entries = re.findall(r'([\w-]+):\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)},?', data, re.DOTALL)

    species_map: Dict[str, SpeciesInfo] = {}
    for species_id, block in entries:
        types_match = re.findall(r'types:\s*\[(.*?)\]', block)
        types = [x.strip().strip('"').strip("'") for x in types_match[0].split(',')] if types_match else []

        egg_match = re.findall(r'eggGroups:\s*\[(.*?)\]', block)
        egg_groups = [x.strip().strip('"').strip("'") for x in egg_match[0].split(',')] if egg_match else []

        abilities_block = re.search(r'abilities:\s*{(.*?)}', block, re.DOTALL)
        abilities = re.findall(r':\s*"([^"]+)"', abilities_block.group(1)) if abilities_block else []

        stats_match = re.search(r'baseStats:\s*{(.*?)}', block, re.DOTALL)
        base_stats: Dict[str, int] = {}
        if stats_match:
            for stat_name, stat_value in re.findall(r'(hp|atk|def|spa|spd|spe):\s*(\d+)', stats_match.group(1)):
                base_stats[stat_name] = int(stat_value)

        bodyshape_match = re.search(r'body[Ss]hape:\s*"([^"]+)"', block)
        num_match = re.search(r'num:\s*(-?\d+)', block)

        species_map[species_id.lower()] = SpeciesInfo(
            species_id=species_id.lower(),
            types=types,
            egg_groups=egg_groups,
            abilities=abilities,
            base_stats=base_stats,
            bodyshape=bodyshape_match.group(1) if bodyshape_match else None,
            num=int(num_match.group(1)) if num_match else None,
        )

    return species_map


def is_cap_mon(num: Optional[int]) -> bool:
    return num is not None and -72 <= num <= -1


def get_role_tags(stats: Dict[str, int]) -> set[str]:
    tags: set[str] = set()
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


def stat_distance(custom_stats: Dict[str, int], mon_stats: Dict[str, int]) -> Optional[float]:
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


def similarity_from_distance(distance: Optional[float]) -> float:
    if distance is None:
        return 0.0
    return 1.0 / (1.0 + (distance / 18.0))


def compute_body_plan_tier(shared_eggs: int, same_bodyshape: bool) -> str:
    if same_bodyshape and shared_eggs >= 1:
        return "strong"
    if same_bodyshape:
        return "shape_only"
    if shared_eggs >= 2:
        return "egg_strong"
    if shared_eggs == 1:
        return "egg_only"
    return "none"


def auto_pick_similar_species(
    target_species_id: str,
    pokedex: Dict[str, SpeciesInfo],
    learnsets: Dict[str, SpeciesLearnset],
    top_n: int = 15,
) -> List[Tuple[str, float, List[str]]]:
    if target_species_id not in pokedex:
        return []

    target = pokedex[target_species_id]
    target_types = set(target.types)
    target_eggs = set(target.egg_groups)
    target_abilities = set(target.abilities)
    target_bodyshape = target.bodyshape
    target_stats = target.base_stats
    target_role_tags = get_role_tags(target_stats)

    candidates: List[Tuple[str, float, List[str]]] = []

    for species_id, info in pokedex.items():
        if species_id == target_species_id:
            continue
        if species_id not in learnsets:
            continue
        if is_cap_mon(info.num):
            continue

        shared_types = len(set(info.types).intersection(target_types))
        shared_eggs = len(set(info.egg_groups).intersection(target_eggs))
        shared_abilities = len(set(info.abilities).intersection(target_abilities))
        shared_roles = len(get_role_tags(info.base_stats).intersection(target_role_tags))
        same_bodyshape = bool(target_bodyshape and info.bodyshape == target_bodyshape)
        body_plan_tier = compute_body_plan_tier(shared_eggs, same_bodyshape)

        # Same guardrail idea as the modern plt.py: need some body-plan or type overlap.
        if body_plan_tier == "none" and shared_types == 0:
            continue

        distance = stat_distance(target_stats, info.base_stats)
        stat_similarity = similarity_from_distance(distance)

        score = 0.0
        reasons: List[str] = []

        if shared_types == 2:
            score += 4.0
            reasons.append("shares both types")
        elif shared_types == 1:
            score += 2.2
            reasons.append("shares one type")

        if body_plan_tier == "strong":
            score += 6.5
            reasons.append("strong body plan match")
        elif body_plan_tier == "shape_only":
            score += 4.8
            reasons.append("shares body shape")
        elif body_plan_tier == "egg_strong":
            score += 3.8
            reasons.append("shares multiple egg groups")
        elif body_plan_tier == "egg_only":
            score += 2.2
            reasons.append("shares egg group")

        score += stat_similarity * 4.0
        if stat_similarity >= 0.75:
            reasons.append("very similar statline")
        elif stat_similarity >= 0.55:
            reasons.append("similar statline")
        elif stat_similarity >= 0.35:
            reasons.append("loosely similar statline")

        if shared_roles:
            score += shared_roles * 0.75
            reasons.append(f"shares {shared_roles} role tag(s)")
        if shared_abilities:
            score += shared_abilities * 1.2
            reasons.append("shares ability")

        if score > 0:
            candidates.append((species_id, score, reasons))

    candidates.sort(key=lambda x: (-x[1], x[0]))
    return candidates[:top_n]


def collect_move_stats_from_species(
    species_ids: List[str],
    learnsets: Dict[str, SpeciesLearnset],
) -> Tuple[Dict[str, MoveLevelStats], Dict[str, Counter], Dict[str, Counter]]:
    level_stats: Dict[str, MoveLevelStats] = defaultdict(MoveLevelStats)
    tm_dist: Dict[str, Counter] = defaultdict(Counter)
    method_dist: Dict[str, Counter] = defaultdict(Counter)

    for species_id in species_ids:
        species = learnsets.get(species_id)
        if not species:
            continue

        for move_id, methods in species.moves.items():
            method_names = {m.method for m in methods}

            if 'M' in method_names:
                tm_dist[move_id]['tm_species'] += 1
                method_dist[move_id]['tm'] += 1
            if 'E' in method_names:
                method_dist[move_id]['egg'] += 1
            if 'L' in method_names:
                tm_dist[move_id]['level_species'] += 1
                method_dist[move_id]['level'] += 1
            tm_dist[move_id]['total_species'] += 1
            method_dist[move_id]['total'] += 1

            if is_suspicious_level_one(methods):
                continue

            levels = sorted({m.level for m in methods if m.method == 'L' and m.level is not None})
            if not levels:
                continue

            non_l1 = [lv for lv in levels if lv > 1]
            if non_l1:
                picked = non_l1[0]
            elif len(levels) == 1 and levels[0] == 1:
                picked = 1
            else:
                picked = None

            if picked is not None:
                level_stats[move_id].samples.append(picked)
                level_stats[move_id].source_species.append(species_id)

    return level_stats, tm_dist, method_dist


def recommend_methods_from_analogs(method_dist: Counter) -> Tuple[List[str], List[str]]:
    total = method_dist.get('total', 0)
    reasons: List[str] = []
    if total == 0:
        return ["9L24"], ["No analogous species with this move were found, so it defaulted to a basic level-up guess."]

    level_count = method_dist.get('level', 0)
    tm_count = method_dist.get('tm', 0)
    egg_count = method_dist.get('egg', 0)

    level_ratio = level_count / total
    tm_ratio = tm_count / total
    egg_ratio = egg_count / total

    methods: List[str] = []

    if level_ratio >= 0.25 or (level_count > 0 and tm_count == 0 and egg_count == 0):
        methods.append("level")
        reasons.append(f"{level_count}/{total} analog species learn this by level-up.")
    if tm_ratio >= 0.25:
        methods.append("tm")
        reasons.append(f"{tm_count}/{total} analog species learn this by TM.")
    if egg_ratio >= 0.20:
        methods.append("egg")
        reasons.append(f"{egg_count}/{total} analog species pass this as an egg move.")

    if not methods:
        # Fallback preference order from analog prevalence.
        best = max(
            [("level", level_count), ("tm", tm_count), ("egg", egg_count)],
            key=lambda x: x[1]
        )[0]
        methods.append(best)
        reasons.append("No method cleared the usual threshold, so the most common analog method was used.")

    out = []
    if "level" in methods:
        out.append("LEVEL")
    if "tm" in methods:
        out.append("TM")
    if "egg" in methods:
        out.append("EGG")
    return out, reasons


def trim_mean(values: List[int], trim_frac: float = 0.15) -> float:
    if not values:
        return 0.0
    vals = sorted(values)
    if len(vals) < 5:
        return sum(vals) / len(vals)
    trim = int(len(vals) * trim_frac)
    if trim * 2 >= len(vals):
        return sum(vals) / len(vals)
    vals = vals[trim:len(vals)-trim]
    return sum(vals) / len(vals)


def collect_species_method_counts(species_ids: List[str], learnsets: Dict[str, SpeciesLearnset]) -> Tuple[List[int], List[int], List[int]]:
    level_counts: List[int] = []
    tm_counts: List[int] = []
    egg_counts: List[int] = []

    for species_id in species_ids:
        species = learnsets.get(species_id)
        if not species:
            continue
        level_moves = set()
        tm_moves = set()
        egg_moves = set()
        for move_id, methods in species.moves.items():
            for m in methods:
                if m.method == 'L':
                    level_moves.add(move_id)
                elif m.method == 'M':
                    tm_moves.add(move_id)
                elif m.method == 'E':
                    egg_moves.add(move_id)
        if level_moves:
            level_counts.append(len(level_moves))
        if tm_moves:
            tm_counts.append(len(tm_moves))
        if egg_moves:
            egg_counts.append(len(egg_moves))

    return level_counts, tm_counts, egg_counts


def estimate_target_counts_from_analogs(target_species_id: str, analog_ids: List[str], learnsets: Dict[str, SpeciesLearnset]) -> Tuple[int, int, int]:
    level_counts, tm_counts, egg_counts = collect_species_method_counts(analog_ids, learnsets)
    seed = 0
    for ch in target_species_id:
        seed = (seed * 131 + ord(ch)) % (2**32)
    import random
    rng = random.Random(seed)

    avg_level = trim_mean(level_counts) if level_counts else 17
    avg_tm = trim_mean(tm_counts) if tm_counts else 32
    avg_egg = trim_mean(egg_counts) if egg_counts else 8

    target_level = round(avg_level + rng.choice([-2, -1, 0, 1, 2]))
    target_tm = round(avg_tm + rng.choice([-3, -2, -1, 0, 1, 2, 3]))
    target_egg = round(avg_egg + rng.choice([-2, -1, 0, 1, 2]))

    target_level = max(10, min(26, target_level))
    target_tm = max(18, min(45, target_tm))
    target_egg = max(0, min(20, target_egg))
    return target_level, target_tm, target_egg


def choose_methods_with_targets(
    target_species_id: str,
    analog_ids: List[str],
    learnsets: Dict[str, SpeciesLearnset],
    moves: Dict[str, MoveInfo],
    candidate_moves: Dict[str, List[MoveMethod]],
) -> Tuple[Dict[str, List[str]], Dict[str, Dict[str, Any]], int, int, int]:
    level_stats, tm_dist, method_dist = collect_move_stats_from_species(analog_ids, learnsets)
    target_level, target_tm, target_egg = estimate_target_counts_from_analogs(target_species_id, analog_ids, learnsets)

    generic_tm_ids = {to_id(x) for x in [
        'protect', 'endure', 'rest', 'sleeptalk', 'substitute', 'facade',
        'sunnyday', 'raindance', 'sandstorm', 'snowscape', 'gigaimpact', 'hyperbeam',
        'helpinghand', 'takedown', 'bodyslam', 'swift', 'doubleedge', 'thief', 'taunt',
        'fling', 'curse', 'tackle'
    ]}

    per_move: Dict[str, Dict[str, Any]] = {}

    for move_id, methods in candidate_moves.items():
        move_info = moves.get(move_id)
        stats = level_stats.get(move_id)
        suggested_level, level_confidence, level_reasons, observed_samples = combine_observed_and_inferred_level(
            move_id=move_id,
            move=move_info,
            stats=stats,
            min_samples=3,
        )

        dist = method_dist.get(move_id, Counter())
        total = dist.get('total', 0)
        level_count = dist.get('level', 0)
        tm_count = dist.get('tm', 0)
        egg_count = dist.get('egg', 0)

        level_ratio = (level_count / total) if total else 0.0
        tm_ratio = (tm_count / total) if total else 0.0
        egg_ratio = (egg_count / total) if total else 0.0

        level_score = level_ratio * 100.0
        tm_score = tm_ratio * 100.0
        egg_score = egg_ratio * 100.0

        if observed_samples:
            level_score += min(20.0, len(observed_samples) * 3.0)

        if observed_samples and all(x == 1 for x in observed_samples):
            level_score -= 20.0

        if move_id in {'outrage', 'dracometeor', 'hyperbeam', 'gigaimpact', 'leafstorm', 'overheat', 'closecombat'}:
            if not observed_samples:
                suggested_level = max(suggested_level, 42)
            elif len(observed_samples) <= 2:
                suggested_level = max(suggested_level, 36)

        if tm_ratio >= 0.75:
            tm_score += 25.0
            level_score -= 8.0

        if level_ratio >= 0.5 and tm_ratio <= 0.25:
            level_score += 15.0

        if egg_ratio >= 0.25:
            egg_score += 10.0

        if move_id in generic_tm_ids:
            tm_score += 18.0
            level_score -= 10.0

        per_move[move_id] = {
            "methods": methods,
            "move_info": move_info,
            "suggested_level": suggested_level,
            "level_confidence": level_confidence,
            "observed_samples": observed_samples,
            "level_reasons": level_reasons,
            "level_score": level_score,
            "tm_score": tm_score,
            "egg_score": egg_score,
            "dist": dist,
        }

    level_rank = sorted(per_move.items(), key=lambda kv: (-kv[1]["level_score"], kv[0]))
    tm_rank = sorted(per_move.items(), key=lambda kv: (-kv[1]["tm_score"], kv[0]))
    egg_rank = sorted(per_move.items(), key=lambda kv: (-kv[1]["egg_score"], kv[0]))

    chosen_level = {move_id for move_id, info in level_rank[:target_level] if info["level_score"] > 0}

    generic_tm = [move_id for move_id, info in tm_rank if move_id in generic_tm_ids][:12]
    chosen_tm_list = list(generic_tm)
    for move_id, info in tm_rank:
        if move_id in chosen_tm_list:
            continue
        if len(chosen_tm_list) >= target_tm:
            break
        if info["tm_score"] > 0:
            chosen_tm_list.append(move_id)
    chosen_tm = set(chosen_tm_list)

    chosen_egg = {move_id for move_id, info in egg_rank[:target_egg] if info["egg_score"] >= 15.0}

    suggested_methods: Dict[str, List[str]] = {}
    for move_id, info in per_move.items():
        out = []
        if move_id in chosen_level:
            out.append(f"9L{info['suggested_level']}")
        if move_id in chosen_tm:
            out.append("9M")
        if move_id in chosen_egg:
            out.append("9E")
        if not out:
            if info["tm_score"] >= info["level_score"] and info["tm_score"] > 0:
                out = ["9M"]
            else:
                out = [f"9L{info['suggested_level']}"]
        if move_id == "terablast":
            out = []
        suggested_methods[move_id] = out

    return suggested_methods, per_move, target_level, target_tm, target_egg


# -----------------------------------------------------------------------------
# Main suggestion pipeline (auto-analog version)
# -----------------------------------------------------------------------------


def build_suggestions_auto(
    species_name: str,
    learnsets: Dict[str, SpeciesLearnset],
    moves: Dict[str, MoveInfo],
    pokedex: Dict[str, SpeciesInfo],
    include_all: bool,
    min_samples: int,
    top_analogs: int,
) -> Dict[str, Any]:
    species_id = to_id(species_name)
    if species_id not in learnsets:
        close = sorted(learnsets.keys(), key=lambda s: levenshtein_like(species_id, s))[:10]
        raise KeyError(
            f"Species '{species_name}' not found. Closest matches: {', '.join(close) if close else 'none'}"
        )

    target = learnsets[species_id]
    auto_analogs = auto_pick_similar_species(species_id, pokedex, learnsets, top_n=top_analogs)
    analog_ids = [sp for sp, _, _ in auto_analogs]

    candidate_moves: Dict[str, List[MoveMethod]] = {}
    for move_id, methods in sorted(target.moves.items()):
        if not include_all:
            if not any(m.method == 'L' and m.level == 1 and (m.generation == 9 or m.generation is None) for m in methods):
                continue
        candidate_moves[move_id] = methods

    suggested_method_map, per_move_info, target_level, target_tm, target_egg = choose_methods_with_targets(
        target_species_id=species_id,
        analog_ids=analog_ids,
        learnsets=learnsets,
        moves=moves,
        candidate_moves=candidate_moves,
    )

    suggestions: List[Suggestion] = []
    for move_id, methods in candidate_moves.items():
        info = per_move_info[move_id]
        current_raw = [m.raw for m in methods]
        suggested_methods = suggested_method_map.get(move_id, [])

        tm_label = "TM possible" if "9M" in suggested_methods else "Level-up preferred"
        if suggested_methods == ["9M"]:
            tm_label = "TM recommended"
        elif any(x.startswith("9L") for x in suggested_methods) and "9M" in suggested_methods:
            tm_label = "Level-up preferred, TM optional"

        dist = info["dist"]
        total = dist.get("total", 0)
        level_count = dist.get("level", 0)
        tm_count = dist.get("tm", 0)
        egg_count = dist.get("egg", 0)

        rationale = list(info["level_reasons"])
        if total:
            if level_count:
                rationale.append(f"{level_count}/{total} analog species learn this by level-up.")
            if tm_count:
                rationale.append(f"{tm_count}/{total} analog species learn this by TM.")
            if egg_count:
                rationale.append(f"{egg_count}/{total} analog species pass this as an egg move.")
        else:
            rationale.append("No analogous species with this move were found, so it relied on fallback move heuristics.")
        if move_id == "terablast":
            rationale.append("Terablast is banned in this custom format, so it is omitted.")

        suggestions.append(
            Suggestion(
                move_id=move_id,
                move_name=info["move_info"].name if info["move_info"] else normalize_species_name(move_id),
                current_methods=current_raw,
                suggested_level=info["suggested_level"],
                level_bucket=bucket_for_level(info["suggested_level"]),
                level_confidence=info["level_confidence"],
                tm_recommendation=tm_label,
                tm_confidence="high" if "9M" in suggested_methods else "medium",
                rationale=rationale,
                observed_level_samples=info["observed_samples"],
                suggested_methods=suggested_methods,
            )
        )

    return {
        "species_id": target.species_id,
        "species_name": target.species_name,
        "suggestions": suggestions,
        "auto_analogs": auto_analogs,
        "target_level": target_level,
        "target_tm": target_tm,
        "target_egg": target_egg,
    }

def format_text_report_auto(report: Dict[str, Any]) -> str:
    def first_level(methods_list: List[str]) -> int:
        levels = []
        for m in methods_list:
            if m.startswith("9L"):
                try:
                    levels.append(int(m[2:]))
                except ValueError:
                    pass
        return min(levels) if levels else 999

    out: List[str] = []
    out.append(f"Auto-analog learnset cleanup suggestions for {report['species_name']} ({report['species_id']})")
    out.append("=" * 72)

    auto_analogs = report.get("auto_analogs", [])
    out.append(f"Target learnset shape: ~{report.get('target_level', 0)} level-up, ~{report.get('target_tm', 0)} TM, ~{report.get('target_egg', 0)} egg")
    out.append("")
    if auto_analogs:
        out.append("Picked similar species automatically:")
        for species_id, score, reasons in auto_analogs:
            out.append(f"  - {species_id} (score {score:.2f}; {', '.join(reasons[:3])})")
        out.append("")
    else:
        out.append("No suitable analogs were auto-picked, so it fell back to global move heuristics.")
        out.append("")

    suggestions: List[Suggestion] = report["suggestions"]
    if not suggestions:
        out.append("No matching moves found. By default, this script only analyzes moves that include 9L1.")
        out.append("Try again with --include-all if you want every level-up move reviewed.")
        return "\n".join(out)

    for s in suggestions:
        out.append("")
        out.append(f"{s.move_name} [{s.move_id}]")
        out.append(f"  Current methods: {', '.join(s.current_methods)}")
        out.append(f"  Suggested level: {s.suggested_level} ({s.level_bucket}, confidence: {s.level_confidence})")
        out.append(f"  TM call: {s.tm_recommendation} (confidence: {s.tm_confidence})")
        out.append(f"  Suggested methods: {', '.join(s.suggested_methods)}")
        if s.observed_level_samples:
            sample_preview = ", ".join(map(str, s.observed_level_samples[:12]))
            suffix = " ..." if len(s.observed_level_samples) > 12 else ""
            out.append(f"  Observed analogous levels: {sample_preview}{suffix}")
        out.append("  Rationale:")
        for reason in s.rationale[:8]:
            out.append(f"    - {reason}")

    out.append("")
    out.append("Copy-paste learnset block")
    out.append("-" * 72)
    out.append(f"{report['species_id']}: {{")
    out.append("\tlearnset: {")
    filtered = [s for s in suggestions if s.suggested_methods]
    filtered.sort(key=lambda s: (first_level(s.suggested_methods), s.move_id))
    for s in filtered:
        methods = ", ".join(f'"{m}"' for m in s.suggested_methods)
        out.append(f"\t\t{s.move_id}: [{methods}],")
    out.append("\t},")
    out.append("},")

    out.append("")
    out.append("Suggested patch snippets")
    out.append("-" * 72)
    for s in suggestions:
        out.append(f"'{s.move_id}': {json.dumps(s.suggested_methods)},")

    return "\n".join(out)


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Suggest better learn levels and TM/egg flags for custom Pokemon learnsets using auto-picked similar mons.")
    parser.add_argument("species", help="Pokemon species name or ID as it appears in learnsets.ts / pokedex.ts")
    parser.add_argument("--include-all", action="store_true", help="Analyze all moves, not only moves that currently include 9L1")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of text")
    parser.add_argument("--min-samples", type=int, default=3, help="Minimum number of analogous level-up samples before observed data is trusted strongly")
    parser.add_argument("--analog-count", type=int, default=15, help="How many similar species to auto-pick from pokedex.ts")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    learnsets_path = base_dir / "learnsets.ts"
    moves_path = base_dir / "moves.ts"
    pokedex_path = base_dir / "pokedex.ts"

    if not learnsets_path.exists():
        print(f"Error: {learnsets_path} not found", file=sys.stderr)
        return 1
    if not moves_path.exists():
        print(f"Error: {moves_path} not found", file=sys.stderr)
        return 1
    if not pokedex_path.exists():
        print(f"Error: {pokedex_path} not found", file=sys.stderr)
        return 1

    try:
        learnsets_text = learnsets_path.read_text(encoding="utf-8")
        moves_text = moves_path.read_text(encoding="utf-8")
        pokedex_text = pokedex_path.read_text(encoding="utf-8")

        learnsets = parse_learnsets(learnsets_text)
        moves = parse_moves(moves_text)
        pokedex = parse_pokedex(pokedex_text)

        report = build_suggestions_auto(
            species_name=args.species,
            learnsets=learnsets,
            moves=moves,
            pokedex=pokedex,
            include_all=args.include_all,
            min_samples=max(1, args.min_samples),
            top_analogs=max(3, args.analog_count),
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        payload = {
            "species_id": report["species_id"],
            "species_name": report["species_name"],
            "auto_analogs": report.get("auto_analogs", []),
            "suggestions": [asdict(s) for s in report["suggestions"]],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(format_text_report_auto(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
