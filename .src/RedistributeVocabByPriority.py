import json
import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

INPUT_LEVELS_PATH = "../output/Levels.json"
OUTPUT_LEVELS_PATH = "../output/Levels.rebalanced.json"
JMDICT_PATH = "../.sources/jmdict/JMdict.xml"
TRANSLATIONS_FR_PATH = "./Translations.fr.json"

KANJI_REGEX = re.compile(r"[\u4e00-\u9fff]")


def load_priority_tags(jmdict_path):
    pri_by_reading = defaultdict(set)

    context = ET.iterparse(jmdict_path, events=("end",))
    for _, elem in context:
        if elem.tag != "entry":
            continue

        for k_ele in elem.findall("k_ele"):
            keb = k_ele.findtext("keb")
            if keb:
                for pri in k_ele.findall("ke_pri"):
                    if pri.text:
                        pri_by_reading[keb].add(pri.text)

        for r_ele in elem.findall("r_ele"):
            reb = r_ele.findtext("reb")
            if reb:
                for pri in r_ele.findall("re_pri"):
                    if pri.text:
                        pri_by_reading[reb].add(pri.text)

        elem.clear()

    return pri_by_reading


def load_french_overrides(path):
    if not os.path.exists(path):
        return {}

    data = json.load(open(path, "r", encoding="utf-8"))
    entries = data.get("entries", {})
    normalized = {}
    for entry_key, meanings in entries.items():
        entry_map = {}
        for english, french in meanings.items():
            if isinstance(french, str):
                french_list = [french]
            else:
                french_list = list(french)
            entry_map[english.strip().lower()] = [value.strip() for value in french_list if value.strip()]
        normalized[entry_key] = entry_map
    return normalized


def write_french_overrides(path, entries):
    ordered = {}
    for entry_key in sorted(entries.keys()):
        english_map = entries[entry_key]
        ordered_english = {}
        for english_key in sorted(english_map.keys()):
            ordered_english[english_key] = english_map[english_key]
        ordered[entry_key] = ordered_english

    payload = {"entries": ordered}
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def build_jmdict_french_map(jmdict_path):
    mapping = defaultdict(lambda: defaultdict(list))

    context = ET.iterparse(jmdict_path, events=("end",))
    for _, elem in context:
        if elem.tag != "entry":
            continue

        readings = []
        for k_ele in elem.findall("k_ele"):
            keb = k_ele.findtext("keb")
            if keb:
                readings.append(keb)
        for r_ele in elem.findall("r_ele"):
            reb = r_ele.findtext("reb")
            if reb:
                readings.append(reb)

        if not readings:
            elem.clear()
            continue

        for sense in elem.findall("s"):
            english = []
            french = []
            for gloss in sense.findall("g"):
                lang = gloss.get("l")
                if lang is None or lang == "eng":
                    if gloss.text:
                        english.append(gloss.text)
                elif lang == "fre":
                    if gloss.text:
                        french.append(gloss.text)

            if english and french:
                for eng in english:
                    eng_key = eng.strip().lower()
                    for reading in readings:
                        mapping[reading][eng_key].extend(french)

        elem.clear()

    # Deduplicate per reading/english while preserving order
    for reading, eng_map in mapping.items():
        for eng_key, fr_list in list(eng_map.items()):
            seen = set()
            unique = []
            for fr in fr_list:
                fr_norm = fr.strip().lower()
                if fr_norm and fr_norm not in seen:
                    seen.add(fr_norm)
                    unique.append(fr.strip())
            eng_map[eng_key] = unique

    return mapping


def get_nf_min(pri_set):
    nf_values = []
    for tag in pri_set:
        if tag.startswith("nf") and len(tag) == 4 and tag[2:].isdigit():
            nf_values.append(int(tag[2:]))
    return min(nf_values) if nf_values else None


def priority_key(pri_set):
    if not pri_set:
        return (0, 999)

    if any(tag in pri_set for tag in ("spec1", "news1", "ichi1")):
        return (3, get_nf_min(pri_set) or 999)

    nf_min = get_nf_min(pri_set)
    if nf_min is not None and nf_min <= 30:
        return (3, nf_min)

    if any(tag in pri_set for tag in ("spec2", "news2", "ichi2")):
        return (2, nf_min or 999)

    if nf_min is not None and nf_min <= 48:
        return (2, nf_min)

    return (1, nf_min or 999)


def dedupe_strings(values):
    seen = set()
    unique = []
    for value in values:
        normalized = value.strip().lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(value.strip())
    return unique


def resolve_french_meanings(display, english_meanings, existing_fr, jmdict_map, overrides):
    english_keys = [meaning.strip().lower() for meaning in english_meanings if meaning.strip()]

    override_entry = overrides.get(display, {})
    jmdict_entry = jmdict_map.get(display, {})

    resolved = []
    for english_key in english_keys:
        override = override_entry.get(english_key)
        if override:
            resolved.extend(override)
            continue

        candidates = jmdict_entry.get(english_key, [])
        resolved.extend(candidates)

    resolved = dedupe_strings(resolved)
    if resolved:
        return resolved

    return dedupe_strings(existing_fr)


def build_translation_entries(levels, jmdict_map, overrides):
    valid_displays = set()
    for level_key, items in levels.items():
        if not level_key.isdigit():
            continue
        for item in items:
            item_type = item.get("type")
            if item_type == "vocab":
                if item.get("id") == item.get("sharedid"):
                    valid_displays.add(item.get("display", ""))
            elif item_type == "vocab_kana":
                meanings = item.get("meanings", []) or []
                if meanings and item.get("id") == item.get("sharedid"):
                    valid_displays.add(item.get("display", ""))

    translations = {key: dict(value) for key, value in overrides.items() if key in valid_displays}

    for level_key, items in levels.items():
        if not level_key.isdigit():
            continue
        for item in items:
            if item.get("type") not in ("vocab", "vocab_kana"):
                continue
            if item.get("type") == "vocab" and item.get("id") != item.get("sharedid"):
                continue
            if item.get("type") == "vocab_kana":
                meanings = item.get("meanings", []) or []
                if not meanings or item.get("id") != item.get("sharedid"):
                    continue

            display = item.get("display", "")
            if not display:
                continue

            english_meanings = item.get("meanings", []) or []
            existing_fr = item.get("meanings_fr", []) or []
            english_keys = [meaning.strip().lower() for meaning in english_meanings if meaning.strip()]

            if display not in translations:
                translations[display] = {}

            entry_map = translations[display]
            jmdict_entry = jmdict_map.get(display, {})

            for english_key in english_keys:
                if english_key in entry_map:
                    continue

                candidates = jmdict_entry.get(english_key, [])
                if candidates:
                    entry_map[english_key] = dedupe_strings(candidates)
                    continue

                if existing_fr:
                    entry_map[english_key] = dedupe_strings(existing_fr)
                else:
                    entry_map[english_key] = []

    return translations


def apply_french_meanings(items, jmdict_map, overrides):
    for item in items:
        if item.get("type") in ("vocab", "vocab_kana"):
            english_meanings = item.get("meanings", []) or []
            existing_fr = item.get("meanings_fr", []) or []
            item["meanings_fr"] = resolve_french_meanings(
                item.get("display", ""),
                english_meanings,
                existing_fr,
                jmdict_map,
                overrides,
            )


def main():
    if not os.path.exists(INPUT_LEVELS_PATH):
        raise FileNotFoundError(f"Levels file not found: {INPUT_LEVELS_PATH}")

    if not os.path.exists(JMDICT_PATH):
        raise FileNotFoundError(f"JMdict file not found: {JMDICT_PATH}")

    levels = json.load(open(INPUT_LEVELS_PATH, "r", encoding="utf-8"))
    pri_by_reading = load_priority_tags(JMDICT_PATH)
    fr_overrides = load_french_overrides(TRANSLATIONS_FR_PATH)
    jmdict_fr_map = build_jmdict_french_map(JMDICT_PATH)
    translations = build_translation_entries(levels, jmdict_fr_map, fr_overrides)
    write_french_overrides(TRANSLATIONS_FR_PATH, translations)
    fr_overrides = load_french_overrides(TRANSLATIONS_FR_PATH)

    kanji_level = {}
    for level in range(1, 101):
        level_key = str(level)
        if level_key not in levels:
            continue
        for item in levels[level_key]:
            if item.get("type") == "kanji":
                kanji_level[item.get("display", "")] = level

    vocab_items = []
    capacity = {}
    non_vocab_by_level = defaultdict(list)

    for level in range(1, 101):
        level_key = str(level)
        if level_key not in levels:
            continue

        items = levels[level_key]
        capacity[level] = sum(1 for item in items if item.get("type") == "vocab")

        for index, item in enumerate(items):
            item_type = item.get("type")
            if item_type != "vocab":
                non_vocab_by_level[level].append((index, item))
                continue

            display = item.get("display", "")
            min_level = 1
            kanji_in_display = KANJI_REGEX.findall(display)
            if kanji_in_display:
                for char in kanji_in_display:
                    if char in kanji_level:
                        min_level = max(min_level, kanji_level[char])
                    else:
                        # Unknown kanji, keep it from moving earlier than its current level.
                        min_level = max(min_level, level)

            pri_set = pri_by_reading.get(display, set())
            vocab_items.append(
                {
                    "item": item,
                    "min_level": min_level,
                    "priority": priority_key(pri_set),
                    "original_level": level,
                    "original_index": index,
                }
            )

    vocab_items.sort(
        key=lambda row: (
            -row["priority"][0],
            row["priority"][1],
            row["min_level"],
            row["original_level"],
            row["original_index"],
        )
    )

    assigned = defaultdict(list)
    remaining = dict(capacity)

    for entry in vocab_items:
        target_level = None
        for level in range(entry["min_level"], 101):
            if remaining.get(level, 0) > 0:
                target_level = level
                break
        if target_level is None:
            # Fallback to the original level if no capacity is found.
            target_level = entry["original_level"]

        assigned[target_level].append(entry)
        remaining[target_level] = remaining.get(target_level, 0) - 1

    output = {}
    for level in range(1, 101):
        level_key = str(level)
        if level_key not in levels:
            continue

        output_items = []

        # Preserve non-vocab order as in the original level.
        non_vocab = sorted(non_vocab_by_level[level], key=lambda row: row[0])
        output_items.extend(item for _, item in non_vocab)

        # Preserve original ordering among vocab assigned to this level.
        vocab_for_level = sorted(
            assigned[level],
            key=lambda row: (row["original_level"], row["original_index"]),
        )
        output_items.extend(row["item"] for row in vocab_for_level)

        apply_french_meanings(output_items, jmdict_fr_map, fr_overrides)

        output[level_key] = output_items

    # Carry over any non-numeric keys untouched (e.g., "special").
    for key, value in levels.items():
        if not key.isdigit():
            apply_french_meanings(value, jmdict_fr_map, fr_overrides)
            output[key] = value

    json.dump(output, open(OUTPUT_LEVELS_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Done. Output: {OUTPUT_LEVELS_PATH}")


if __name__ == "__main__":
    main()
