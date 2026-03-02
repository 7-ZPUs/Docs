import re
import os

# Define paths
base_dir = r"c:\Users\Utente\Desktop\SWE\7zpus\Docs\Docs\2_RTB\DocumentiEsterni\analisi"

# UC level mapping
level_map = {
    'usecase': 0,
    'subusecase': 1,
    'subsubusecase': 2,
    'deepusecase': 3,
    'subdeepusecase': 4,
    'subsubdeepusecase': 5,
    'abyssalusecase': 6,
}

# Files to process in order
uc_files = ['UC1.tex', 'UC2.tex', 'UC3.tex', 'UC4.tex', 'UC5-8.tex',
            'UC10-13.tex', 'UC14-26.tex', 'UC27-42.tex', 'UC-Fix.tex']

# Step 1: Extract all UC definitions in order with their levels
uc_pattern = re.compile(
    r'\\(usecase|subusecase|subsubusecase|deepusecase|subdeepusecase|subsubdeepusecase|abyssalusecase)'
    r'\{([^}]+)\}\s*\{([^}]+)\}'
)

all_ucs = []  # list of (label, name, level)

for fname in uc_files:
    filepath = os.path.join(base_dir, fname)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    for match in uc_pattern.finditer(content):
        cmd_type = match.group(1)
        label = match.group(2)
        name = match.group(3)
        level = level_map[cmd_type]
        all_ucs.append((label, name, level))

print(f"Total UCs found: {len(all_ucs)}")

# Step 2: Build parent map - for each UC, find its parent(s) up to root
# Walk backwards from each UC to find parent at each level above it
def get_ancestors(ucs, index):
    """Get list of ancestor labels for the UC at given index (from parent to root)."""
    current_level = ucs[index][2]
    ancestors = []
    # Walk backwards looking for each parent level
    target_level = current_level - 1
    i = index - 1
    while i >= 0 and target_level >= 0:
        if ucs[i][2] == target_level:
            ancestors.append(ucs[i][0])  # label
            target_level -= 1
        elif ucs[i][2] < target_level:
            # We skipped a level, adjust
            target_level = ucs[i][2]
            ancestors.append(ucs[i][0])
            target_level -= 1
        i -= 1
    return ancestors

# Step 3: Extract requirement -> direct UC label mapping from Requisiti.tex
req_file = os.path.join(base_dir, 'Requisiti.tex')
with open(req_file, 'r', encoding='utf-8') as f:
    req_content = f.read()

# We need to extract requirements IN ORDER as they appear in the Requisiti Funzionali table
# Each row has: R-xxx-F-Ob/De/Op & description & \ref{label} (or tabular with multiple refs)
# Split by \hline

rows = req_content.split('\\hline')

# Ordered list of (req_code, [direct_labels])
req_order = []
for row in rows:
    row_stripped = row.strip()
    req_match = re.search(r'(R-\d+-F-(?:Ob|De|Op))\s*&', row_stripped)
    if req_match:
        req_code = req_match.group(1)
        # Extract all \ref{label} from this row
        refs = re.findall(r'\\ref\{([^}]+)\}', row_stripped)
        req_order.append((req_code, refs))

print(f"Total functional requirements found: {len(req_order)}")

# Build label -> index map for fast lookup
label_to_idx = {uc[0]: i for i, uc in enumerate(all_ucs)}

# Step 4: For each requirement, compute direct UC + ancestors
output_lines = []

for req_code, direct_labels in req_order:
    # Collect all UC labels: direct sources + their ancestors
    all_labels = []
    seen = set()
    for label in direct_labels:
        if label not in seen:
            all_labels.append(label)
            seen.add(label)
        # Find ancestors
        if label in label_to_idx:
            ancestors = get_ancestors(all_ucs, label_to_idx[label])
            for anc in ancestors:
                if anc not in seen:
                    all_labels.append(anc)
                    seen.add(anc)

    # Sort by order of appearance in the UC files (by index)
    def uc_sort_key(lbl):
        return label_to_idx.get(lbl, 999999)
    all_labels_sorted = sorted(all_labels, key=uc_sort_key)

    # Format as \ref{label1}, \ref{label2}, ...
    if all_labels_sorted:
        refs_str = ", ".join(f"\\ref{{{lbl}}}" for lbl in all_labels_sorted)
    else:
        refs_str = "---"

    output_lines.append(f"{req_code} & {refs_str} \\\\")
    output_lines.append("\\hline")

# Write output
output_path = os.path.join(base_dir, '..', '..', '..', 'scripts', 'inverse_tracing_output.tex')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"Output written to: {output_path}")
print(f"Total rows: {len(output_lines) // 2}")

# Debug: print first few rows
for line in output_lines[:10]:
    print(line)
