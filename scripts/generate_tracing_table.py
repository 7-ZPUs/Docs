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
uc_files = ['UC1.tex', 'UC2.tex', 'UC3.tex', 'UC4.tex', 'UC5-8.tex', 'UC10-13.tex', 'UC14-26.tex', 'UC27-42.tex', 'UC-Fix.tex']

# Step 1: Extract all UC definitions in order with their levels
uc_pattern = re.compile(r'\\(usecase|subusecase|subsubusecase|deepusecase|subdeepusecase|subsubdeepusecase|abyssalusecase)\{([^}]+)\}\s*\{([^}]+)\}')

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

# Step 2: Build hierarchy - for each UC, find its descendants
# A UC's descendants are all subsequent UCs at a deeper level until we hit one at the same or shallower level
def get_descendants(ucs, index):
    """Get indices of all descendants of the UC at given index"""
    parent_level = ucs[index][2]
    descendants = []
    for i in range(index + 1, len(ucs)):
        if ucs[i][2] > parent_level:
            descendants.append(i)
        else:
            break
    return descendants

# Step 3: Extract requirement -> UC label mapping from Requisiti.tex
req_file = os.path.join(base_dir, 'Requisiti.tex')
with open(req_file, 'r', encoding='utf-8') as f:
    req_content = f.read()

# Find the Requisiti Funzionali table rows
# Split by \hline to get individual rows
# Map: label -> set of requirements
label_to_reqs = {}
# Map: requirement -> set of labels
req_to_labels = {}

# Split content by \hline and look for rows starting with R-\d+-F-
rows = req_content.split('\\hline')
for row in rows:
    row = row.strip()
    # Match the requirement code in the row (search, not match, to handle first row)
    req_match = re.search(r'(R-\d+-F-(?:Ob|De|Op))\s*&', row)
    if req_match:
        req_code = req_match.group(1)
        # Extract all \ref{label} from the entire row
        refs = re.findall(r'\\ref\{([^}]+)\}', row)
        for ref_label in refs:
            if ref_label not in label_to_reqs:
                label_to_reqs[ref_label] = []
            label_to_reqs[ref_label].append(req_code)
            if req_code not in req_to_labels:
                req_to_labels[req_code] = []
            req_to_labels[req_code].append(ref_label)

# Step 4: For each UC, compute requirements (own + descendants)
def get_all_reqs(ucs, index, label_to_reqs):
    """Get all requirements for a UC including descendants"""
    label = ucs[index][0]
    reqs = set()
    # Own requirements
    if label in label_to_reqs:
        reqs.update(label_to_reqs[label])
    # Descendant requirements
    descendants = get_descendants(ucs, index)
    for desc_idx in descendants:
        desc_label = ucs[desc_idx][0]
        if desc_label in label_to_reqs:
            reqs.update(label_to_reqs[desc_label])
    return reqs

def sort_reqs(reqs):
    """Sort requirements by their numeric ID"""
    def req_sort_key(r):
        m = re.match(r'R-(\d+)-', r)
        return int(m.group(1)) if m else 0
    return sorted(reqs, key=req_sort_key)

# Step 5: Generate the LaTeX table rows
output_lines = []

for i, (label, name, level) in enumerate(all_ucs):
    reqs = get_all_reqs(all_ucs, i, label_to_reqs)
    sorted_reqs = sort_reqs(reqs)
    req_str = ", ".join(sorted_reqs) if sorted_reqs else "---"
    output_lines.append(f"\\ref{{{label}}} & {req_str} \\\\")
    output_lines.append("\\hline")

# Write to file
output_path = os.path.join(os.path.dirname(base_dir), '..', '..', 'scripts', 'tracing_output.tex')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))
print(f"Total UCs found: {len(all_ucs)}")
print(f"Output written to: {output_path}")
print(f"Total rows: {len(output_lines) // 2}")
