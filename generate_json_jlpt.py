"""
generate_jlpt_json.py
Generate JSON files per JLPT level (n5.json ... n1.json)
Requires: pip install jamdict tqdm

Notes:
- Jamdict uses JMdict/kanjidic data; many entries include JLPT tags but coverage may vary.
- The script will try to use entry.jlpt_tags or entry.misc for JLPT-level hints.
- If JLPT tags are missing for many words, consider using an external JLPT wordlist mapping (not included).
"""

import json
import os
from jamdict import Jamdict
from tqdm import tqdm

# Output folder for JSONs
OUT_DIR = "jlpt_json"
os.makedirs(OUT_DIR, exist_ok=True)

# Initialize jamdict (requires jamdict data installed; see notes below)
jam = Jamdict()

# JLPT levels we want (map tag forms to canonical)
JLPT_LEVELS = ["N5", "N4", "N3", "N2", "N1"]

# Collector: level -> list of dict entries
collector = {lvl: [] for lvl in JLPT_LEVELS}
collector["UNKNOWN"] = []  # fallback bucket

def extract_meaning_from_entry(entry):
    # entry.senses holds meanings (english glosses often at sense.gloss with lang='eng')
    glosses = []
    for sense in entry.senses:
        for g in sense.gloss:
            # jamdict's Gloss objects often have .text and .lang
            try:
                if getattr(g, "lang", None) in (None, "eng", "en"):
                    glosses.append(g.text if hasattr(g, "text") else str(g))
            except Exception:
                # fallback
                glosses.append(str(g))
    return "; ".join(glosses) if glosses else ""

def detect_jlpt_from_entry(entry):
    """
    Try multiple ways to get JLPT tag from jamdict entry.
    Returns list of JLPT tags found (like ['N5']) or [].
    """
    tags = set()
    # Some entries have attribute 'jlpt' or 'misc' including 'jlpt-N5' etc.
    # jamdict Entry has .misc (list) and sometimes .jlpt_tags
    try:
        # try common attribute names
        if hasattr(entry, "jlpt_tags"):
            for t in entry.jlpt_tags:
                tags.add(t.upper())
    except Exception:
        pass

    try:
        for m in getattr(entry, "misc", []) or []:
            mm = str(m).upper()
            # variants: 'jlpt-n5', 'jlpt', 'N5' etc.
            if mm.startswith("JLPT"):
                # extract N5..N1
                if "N5" in mm:
                    tags.add("N5")
                elif "N4" in mm:
                    tags.add("N4")
                elif "N3" in mm:
                    tags.add("N3")
                elif "N2" in mm:
                    tags.add("N2")
                elif "N1" in mm:
                    tags.add("N1")
    except Exception:
        pass

    # Some sense-level misc may include JLPT hints; try senses
    try:
        for sense in entry.senses:
            for misc in getattr(sense, "misc", []) or []:
                mm = str(misc).upper()
                if mm.startswith("JLPT"):
                    if "N5" in mm: tags.add("N5")
                    elif "N4" in mm: tags.add("N4")
                    elif "N3" in mm: tags.add("N3")
                    elif "N2" in mm: tags.add("N2")
                    elif "N1" in mm: tags.add("N1")
    except Exception:
        pass

    return sorted(list(tags))

def choose_kana_for_entry(entry):
    """
    Return a primary kana reading (hiragana/katakana) for the entry.
    Prefer 'ja_kana' forms or first kana_form.
    """
    # jamdict Entry has .kana_forms (list) and .kanji_forms
    try:
        if entry.kana_forms:
            # return first kana_form text
            return entry.kana_forms[0].text
    except Exception:
        pass
    # fallback: try kanji_forms' reading if available
    try:
        if entry.kanji_forms:
            kf = entry.kanji_forms[0]
            # kanji form may have reading info in its .reading_list
            if hasattr(kf, "reading_list") and kf.reading_list:
                return kf.reading_list[0].text
    except Exception:
        pass
    return ""

# Iterate over JAMDICT entries (this may be large; use tqdm)
print("Iterating JMdict entries (this may take time)...")
count = 0
for res in tqdm(jam.search("") ):  # jam.search("") yields all entries
    # jamdict returns SearchResult; access .entries list
    try:
        for entry in res.entries:
            count += 1
            # Primary kanji: use first kanji literal if exists, else kana form
            kanji_text = ""
            if entry.kanji_forms:
                kanji_text = entry.kanji_forms[0].literal
            else:
                # if no kanji forms, use kana form as representation
                if entry.kana_forms:
                    kanji_text = entry.kana_forms[0].text

            reading = choose_kana_for_entry(entry) or ""
            meaning = extract_meaning_from_entry(entry) or ""

            jlpt_tags = detect_jlpt_from_entry(entry)

            if jlpt_tags:
                # If multiple tags, assign to lowest (easiest) level? We'll keep all
                for tag in jlpt_tags:
                    tag = tag.upper()
                    if tag in collector:
                        collector[tag].append({
                            "kanji": kanji_text,
                            "reading": reading,
                            "meaning": meaning,
                            "level": tag
                        })
                    else:
                        collector["UNKNOWN"].append({
                            "kanji": kanji_text,
                            "reading": reading,
                            "meaning": meaning,
                            "level": tag
                        })
            else:
                # no JLPT tag found
                collector["UNKNOWN"].append({
                    "kanji": kanji_text,
                    "reading": reading,
                    "meaning": meaning,
                    "level": ""
                })

    except Exception as e:
        # ignore single-entry errors but print occasionally
        print("Entry iteration error:", e)
        continue

print(f"Total entries processed (approx): {count}")

# Save JSON files per level
for lvl in JLPT_LEVELS:
    out = os.path.join(OUT_DIR, f"{lvl.lower()}.json")
    print(f"Saving {lvl}: {len(collector[lvl])} entries -> {out}")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(collector[lvl], f, ensure_ascii=False, indent=2)

# Save unknowns
out_unknown = os.path.join(OUT_DIR, "unknown.json")
print(f"Saving UNKNOWN: {len(collector['UNKNOWN'])} entries -> {out_unknown}")
with open(out_unknown, "w", encoding="utf-8") as f:
    json.dump(collector["UNKNOWN"], f, ensure_ascii=False, indent=2)

print("Done. Check the 'jlpt_json' folder.")
