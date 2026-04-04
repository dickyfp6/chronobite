import pandas as pd

label_mak = pd.read_csv('A. Data/Data Raw/label_makanan.csv', sep=';')
label_cui = pd.read_csv('A. Data/Data Raw/label_cuisine.csv')

overlap = len(set(label_mak['fdc_id']) & set(label_cui['fdc_id']))
unique_mak = len(set(label_mak['fdc_id']) - set(label_cui['fdc_id']))
unique_cui = len(set(label_cui['fdc_id']) - set(label_mak['fdc_id']))

print(f'label_makanan rows: {len(label_mak)}')
print(f'label_cuisine rows: {len(label_cui)}')
print(f'Overlap (fdc_id): {overlap}')
print(f'Unique in label_makanan: {unique_mak}')
print(f'Unique in label_cuisine: {unique_cui}')
