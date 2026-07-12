import pandas as pd
import os
import sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'c:\Users\USERR\Documents\0. Mata Kuliah\8 -TA\Code\TugasAkhirDSS\E. Evaluation\2_Validasi_Ahli_Gizi\Validasi Ahli Gizi.xlsx'

xl = pd.ExcelFile(file_path)

all_scores = {}
comments = []

for sheet in xl.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet)
    
    # Find "BAGIAN 7 — FORM PENILAIAN AHLI GIZI"
    start_row = None
    for i, row in df.iterrows():
        row_text = ' | '.join([str(x) for x in row if str(x) != 'nan']).upper()
        if 'BAGIAN 7' in row_text and 'PENILAIAN' in row_text:
            start_row = i
            break
            
    if start_row is not None:
        # Extract the scores which are probably a few rows down.
        # Format might be: Kode | Pertanyaan/Indikator | SKOR GA | Interpretasi | SKOR Greedy | Interpretasi
        # We will just grab rows until we hit BAGIAN 8 or empty
        for j in range(start_row + 2, len(df)):
            row = df.iloc[j]
            row_text = ' | '.join([str(x) for x in row if str(x) != 'nan']).upper()
            if 'BAGIAN 8' in row_text or 'RATA-RATA' in row_text:
                break
            
            # The columns are probably:
            # 1: Kode, 2: Indikator, 3: Skor GA, 4: Interpretasi, 5: Skor Greedy, 6: Interpretasi
            # Let's just grab any numeric values found in the row
            vals = []
            for col in row.values:
                if isinstance(col, (int, float)) and not np.isnan(col):
                    vals.append(col)
            
            if len(vals) >= 2: # GA score, Greedy score
                indikator = str(row.iloc[2]) if str(row.iloc[2]) != 'nan' else 'Unknown'
                if indikator not in all_scores:
                    all_scores[indikator] = {'GA': [], 'Greedy': []}
                all_scores[indikator]['GA'].append(vals[0])
                all_scores[indikator]['Greedy'].append(vals[1])
                
    # Extract comments from Bagian 8
    start_row = None
    for i, row in df.iterrows():
        row_text = ' | '.join([str(x) for x in row if str(x) != 'nan']).upper()
        if 'BAGIAN 8' in row_text:
            start_row = i
            break
            
    if start_row is not None:
        sheet_comments = []
        for j in range(start_row + 2, min(start_row + 25, len(df))):
            row_text = ' '.join([str(x) for x in df.iloc[j] if str(x) != 'nan'])
            if row_text.strip():
                sheet_comments.append(row_text.strip())
        comments.append(f"Sheet {sheet}:\n" + "\n".join(sheet_comments))

print("=== AVERAGE SCORES ACROSS 13 CASES ===")
for ind, scores in all_scores.items():
    if scores['GA'] and scores['Greedy']:
        avg_ga = np.mean(scores['GA'])
        avg_greedy = np.mean(scores['Greedy'])
        print(f"{ind[:60]}... -> GA: {avg_ga:.2f}/5, Greedy: {avg_greedy:.2f}/5")

print("\n=== SAMPLE COMMENTS ===")
for c in comments[:3]:
    print(c)
    print("-" * 20)
