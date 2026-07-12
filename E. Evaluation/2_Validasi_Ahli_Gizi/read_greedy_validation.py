import pandas as pd
import os
import sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'c:\Users\USERR\Documents\0. Mata Kuliah\8 -TA\Code\TugasAkhirDSS\E. Evaluation\2_Validasi_Ahli_Gizi\Validasi Ahli Gizi.xlsx'
xl = pd.ExcelFile(file_path)

greedy_scores = {}
greedy_comments = []

for sheet in xl.sheet_names:
    if 'Case' not in sheet:
        continue
    df = pd.read_excel(file_path, sheet_name=sheet)
    
    # 1. FIND SCORES
    start_row = None
    for i, row in df.iterrows():
        row_text = ' | '.join([str(x) for x in row if str(x) != 'nan']).upper()
        if 'BAGIAN 7' in row_text and 'PENILAIAN' in row_text:
            start_row = i
            break
            
    if start_row is not None:
        for j in range(start_row + 2, len(df)):
            row_text = ' | '.join([str(x) for x in df.iloc[j] if str(x) != 'nan']).upper()
            if 'BAGIAN 8' in row_text or 'RATA-RATA' in row_text:
                break
            
            # Extract numeric values
            vals = []
            for col in df.iloc[j].values:
                if isinstance(col, (int, float)) and not np.isnan(col):
                    vals.append(col)
            
            # The second numeric value is Greedy (first is GA)
            if len(vals) >= 2:
                indikator = str(df.iloc[j, 1]) if str(df.iloc[j, 1]) != 'nan' else 'Unknown'
                # Clean indikator text
                indikator = indikator.split('\n')[0].strip()
                if indikator not in greedy_scores:
                    greedy_scores[indikator] = []
                greedy_scores[indikator].append(vals[1])
                
    # 2. FIND COMMENTS
    start_row = None
    for i, row in df.iterrows():
        row_text = ' | '.join([str(x) for x in row if str(x) != 'nan']).upper()
        if 'BAGIAN 8' in row_text:
            start_row = i
            break
            
    if start_row is not None:
        # Columns: usually col 0/1 is question, col 2 is GA, col 3/4 is Greedy
        # Let's search for "Greedy" in the header of this section
        header_row = start_row + 1
        greedy_col_idx = -1
        for col_idx, val in enumerate(df.iloc[header_row]):
            if 'GREEDY' in str(val).upper():
                greedy_col_idx = col_idx
                break
                
        if greedy_col_idx != -1:
            sheet_comments = []
            for j in range(header_row + 1, min(header_row + 25, len(df))):
                question = str(df.iloc[j, 1]) if len(df.columns) > 1 else ""
                if question.strip() and question != 'nan':
                    comment = str(df.iloc[j, greedy_col_idx])
                    if comment.strip() and comment != 'nan':
                        sheet_comments.append(f"Q: {question}\nA: {comment}\n")
            
            if sheet_comments:
                greedy_comments.append(f"--- {sheet} ---")
                greedy_comments.extend(sheet_comments)

print("=== GREEDY AVERAGE SCORES ===")
for ind, scores in greedy_scores.items():
    if scores:
        avg = np.mean(scores)
        print(f"{ind}: {avg:.2f}/5")

print("\n=== GREEDY COMMENTS ===")
for c in greedy_comments:
    print(c)
