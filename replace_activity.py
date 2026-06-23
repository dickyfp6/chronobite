import os

target_files = [
    r"F. WebApp\app_integrated.py",
    r"C. System Flow\modules\c_input_handler.py",
    r"E. Evaluation\3_Validasi_Ahli_Gizi\validasi_greedy.py",
    r"E. Evaluation\2_Tuning_Parameter\tune_ga.py",
    r"E. Evaluation\2_Tuning_Parameter\tune_optuna.py",
    r"D. Model\Genetic Algorithm\test_ga_auto.py",
    r"D. Model\Genetic Algorithm\test_ga_batch.py",
    r"F. WebApp\Frontend\src\components\figma\BmiCalculatorModal.tsx",
    r"F. WebApp\Frontend\src\pages\InputWizard.tsx",
    r"F. WebApp\Frontend\src\pages\Results.tsx",
    r"F. WebApp\Frontend\src\pages\ProfileSummary.tsx",
    r"F. WebApp\Frontend\src\App.tsx"
]

replacements = [
    ("1.545", "1.4"),
    ("1.845", "1.7"),
    ("2.2", "2.0")
]

for rel_path in target_files:
    full_path = os.path.join(r"c:\Users\USERR\Documents\0. Mata Kuliah\8 -TA\Code\TugasAkhirDSS", rel_path)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content
        for old_val, new_val in replacements:
            new_content = new_content.replace(old_val, new_val)
            
        if new_content != content:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {rel_path}")
        else:
            print(f"No changes needed for {rel_path}")
    else:
        print(f"File not found: {full_path}")
