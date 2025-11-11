import json

# Load your JSON file
with open("assets/data/N4.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Sort by ID just in case
data.sort(key=lambda x: x["id"])

# Get the smallest ID
start_id = data[0]["id"]

# Resequence IDs to make them continuous
for i, item in enumerate(data):
    item["id"] = start_id + i

# Save repaired file
with open("N4_fixed.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Fixed N3.json saved as N3_fixed.json with continuous IDs.")

