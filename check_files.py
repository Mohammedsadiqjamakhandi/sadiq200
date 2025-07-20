import csv
import json

# Show some EQ symbols
print("🔍 Preview: nse_eq_symbols.csv")
with open("nse_eq_symbols.csv") as f:
    for i, line in enumerate(f):
        print(f"{i+1:>2}: {line.strip()}")
        if i >= 9: break

# Show some master data entries
print("\n🔍 Preview: ScripMaster.json")
with open("ScripMaster.json") as f:
    master_data = json.load(f)
    for i, row in enumerate(master_data):
        print(f"{i+1:>2}: symbol={row.get('symbol')}, exch_seg={row.get('exch_seg')}, token={row.get('token')}")
        if i >= 9: break
