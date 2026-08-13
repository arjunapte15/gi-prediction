"""Fetch nutrient data from USDA FoodData Central for the American foods in
data/raw/gi_gl_raw.csv and write data/raw/american_nutrients.csv (plus
data/raw/american_nutrients_unmatched.txt for foods with no confident match).

The food_name -> fdc_id mapping below was curated by hand: FDC's search API
was queried for each food (preferring Foundation/SR Legacy/FNDDS over
Branded, per Phase 3 rules) and results were reviewed for the best match,
then checked for complete macro data before being locked in here.
"""
import csv
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ["FDC_API_KEY"]
ROOT = Path(__file__).resolve().parents[2]

FOOD_MATCHES = {
    "White bread": 2707598,
    "Burger Buns, 100% Whole wheat": 2707751,
    "Doughnut": 2708062,
    "Rye bread, Pumpernickel": 174918,
    "Multigrain bread, gluten-free": 2707797,
    "Multigrain batch bread": 2707777,
    "White sourdough bread, gluten free": 174100,
    "Oat bran concentrate bread": 172676,
    "Fruit and Muesli bread (Bürgen)": 2440339,
    "Muesli bread (packet mix)": 2440339,
    "Oats, rolled, uncooked": 173904,
    "Weet-Bix breakfast biscuit": 173910,
    "Rice Bubbles (Kellogg's)": 2708455,
    "Cornflakes": 2708453,
    "Bran Flakes (Kellogg's)": 2708456,
    "Chocolate cake (Betty Crocker)": 2707867,
    "Danish Pastry, Apple and Peach": 2708060,
    "Apple Blueberry muffin": 172765,
    "Banana, oat and honey muffin": 2707830,
    "Cranberry Raisin muffin": 2707830,
    "Pizza base, oven-baked (Boboli)": 560943,
    "French Fries, baked (OreIda)": 2709460,
    "Cheddar Cheese Crackers (Combos)": 2672832,
    "Cheddar Cheese Pretzels (Combos)": 2499998,
    "Soft pretzel, wheat": 169064,
    "Microwave popcorn, butter flavor": 2708227,
    "Cheese Puffs, rice and corn (Pirate's Booty)": 1892305,
    "Ice cream, premium chocolate, 15% fat": 2705632,
    "Milk, reduced fat": 2705386,
    "Yoghurt, Greek style, honey topped": 2008886,
    "Yoghurt, black cherry": 2069963,
    "Yoghurt, bourbon vanilla": 170888,
    "Yoghurt, natural, no added sugar": 171284,
    "Custard apple, raw": 173953,
    "Pineapple, raw": 2346398,
    "Grapes, Crimson seedless": 174683,
    "Grapes, green, Menidee, seedless": 174683,
    "Watermelon, raw": 167765,
    "Orange juice": 169099,
    "Sweet corn, cooked in microwave": 169999,
    "Carrots, unpeeled, boiled": 170394,
    "Carrots, diced, frozen": 169984,
    "Peas, plain and frozen": 170017,
    "Hommus dip": 174289,
    "Baked Beans in Cheesy Tomato sauce (Heinz)": 1624816,
    "Baked Beans in Barbecue sauce (Heinz)": 2246973,
    "Baked Beans in Tomato sauce (Heinz)": 1624816,
    "Manuka honey MGO 440+": 169640,
    "Capilano Premium Honey": 169640,
    "Mixed Grain bread roll (Bürgen)": 2707782,
    "Brown rice, instant (Uncle Ben's)": 2108264,
    "Peanut Butter Granola bars (Kudos)": 173133,
    "Chocolate covered almonds (Cocoavia)": 170670,
    "Raisins": 2709212,
    "Strawberries, fresh, raw": 167762,
    "Apricot, coconut and honey muffin": 2707830,
    "Fruit Salad, canned (peach/pear/apricot/pineapple/cherry)": 173028,
    "Maple syrup, pure Canadian": 170276,
    "Apricot fruit spread, no added sugar": 2439868,
    "Apricot fruit spread (Cottees)": 170645,
    "Apple juice, unsweetened": 173933,
    "Tomato soup, condensed, prepared with water (Campbell's)": 2709757,
    "Chunky Roast Chicken and Vegetable soup (Campbell's)": 2773605,
}

UNMATCHED = {
    "Mango dessert, prepared (Nestlé)": "No confident FDC match: searches for the branded Nestle mango dessert "
    "and generic mango pudding/dessert terms returned only unrelated puddings "
    "(banana, bread, rice, noodle) with no mango-based dessert in Foundation/SR "
    "Legacy/FNDDS/Branded data.",
}

NUTRIENT_MAP = {
    "203": "protein_g",
    "204": "fat_g",
    "205": "carbs_g",
    "291": "fiber_g",
    "293": "fiber_g",
    "269": "sugar_g",
    "269.3": "sugar_g",
}

unique_ids = sorted(set(FOOD_MATCHES.values()))
nutrients_by_id = {}
CHUNK = 20
for i in range(0, len(unique_ids), CHUNK):
    chunk_ids = unique_ids[i : i + CHUNK]
    r = requests.post(
        "https://api.nal.usda.gov/fdc/v1/foods",
        params={"api_key": API_KEY},
        json={"fdcIds": chunk_ids},
        timeout=60,
    )
    r.raise_for_status()
    for food in r.json():
        fid = food["fdcId"]
        vals = {}
        for n in food["foodNutrients"]:
            num = n.get("nutrient", {}).get("number")
            if num in NUTRIENT_MAP and n.get("amount") is not None:
                vals.setdefault(NUTRIENT_MAP[num], n["amount"])
        nutrients_by_id[fid] = vals

rows = []
for food_name, fdc_id in FOOD_MATCHES.items():
    vals = nutrients_by_id[fdc_id]
    missing = {"fiber_g", "fat_g", "protein_g", "carbs_g", "sugar_g"} - set(vals.keys())
    if missing:
        raise SystemExit(f"{food_name} (fdc_id {fdc_id}) still missing {missing}")
    rows.append(
        {
            "food_name": food_name,
            "fdc_id": fdc_id,
            "fiber_g": round(vals["fiber_g"], 2),
            "fat_g": round(vals["fat_g"], 2),
            "protein_g": round(vals["protein_g"], 2),
            "carbs_g": round(vals["carbs_g"], 2),
            "sugar_g": round(vals["sugar_g"], 2),
        }
    )

out_csv = ROOT / "data" / "raw" / "american_nutrients.csv"
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["food_name", "fdc_id", "fiber_g", "fat_g", "protein_g", "carbs_g", "sugar_g"])
    writer.writeheader()
    writer.writerows(rows)

out_unmatched = ROOT / "data" / "raw" / "american_nutrients_unmatched.txt"
with open(out_unmatched, "w", encoding="utf-8") as f:
    for name, reason in UNMATCHED.items():
        f.write(f"{name}: {reason}\n")

print(f"Wrote {len(rows)} rows to {out_csv}")
print(f"Wrote {len(UNMATCHED)} unmatched entries to {out_unmatched}")
