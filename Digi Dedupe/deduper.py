import pandas as pd
from rapidfuzz import fuzz
from tqdm.auto import tqdm

# === File Paths ===
save_path = r"C:\Users\OwenKinney\OneDrive - Cobalt Service Partners\Cobalt Service Partners (CSP) - The One Site\Cobalt HQ Team Hubs\Operations\OPS - Working Documents\Kinney Working Docs\outputvf512.xlsx"
file_path = r"/Digi - Master Catalog - CW 4-14-2025 - Excel.xlsx"

# === Load Data ===
df = pd.read_excel(file_path, sheet_name="Digi - Master Catalog - CW 4-14")
df['Description'] = df['Description'].fillna('').astype(str).str.strip()

# === Settings ===
length_threshold_pct = 0.2
similarity_threshold = 95

# === Prepare for Grouping ===
grouped_rows = []
used_ids = set()
group_number = 1

# === Set up Global Progress Bar ===
total_rows = df.shape[0]
pbar = tqdm(total=total_rows, desc="Processing rows", position=0)

# === Process Each Subcategory ===
for subcategory in df['Subcategory'].dropna().unique():
    subcategory_df = df[df['Subcategory'] == subcategory].reset_index(drop=True)

    for idx, row in subcategory_df.iterrows():
        row_id = row['IV_Item_RecID']
        if row_id in used_ids:
            pbar.update(1)
            continue

        current_group = [(row_id, row['Description'])]
        used_ids.add(row_id)

        current_description = row['Description']
        current_length = len(current_description)

        for idx2, row2 in subcategory_df.iterrows():
            row2_id = row2['IV_Item_RecID']
            if row2_id in used_ids or row_id == row2_id:
                continue

            comp_description = row2['Description']
            comp_length = len(comp_description)

            if current_length == 0 or comp_length == 0:
                continue

            length_difference = abs(current_length - comp_length) / max(current_length, comp_length)
            if length_difference > length_threshold_pct:
                continue

            similarity = fuzz.ratio(current_description, comp_description)
            if similarity >= similarity_threshold:
                current_group.append((row2_id, comp_description))
                used_ids.add(row2_id)

        # Only save groups with more than 1 item
        if len(current_group) > 1:
            for rec_id, desc in current_group:
                grouped_rows.append({
                    'Group Number': group_number,
                    'Subcategory': subcategory,
                    'IV_Item_RecID': rec_id,
                    'Customer Description': desc
                })
            group_number += 1

        pbar.update(1)  # Always update for each row, used or grouped

pbar.close()

# === Create Output DataFrame ===
output_df = pd.DataFrame(grouped_rows)

# === Save Output ===
with pd.ExcelWriter(save_path, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Original Data', index=False)
    output_df.to_excel(writer, sheet_name='Fuzzy Duplicates', index=False)

print("Fuzzy duplicates exported successfully!")

