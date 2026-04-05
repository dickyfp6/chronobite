"""
GUI Application untuk Nutrition Calculation System
Built with tkinter untuk local application
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.input_handler import validate_user_input
from modules.calculations import calculate_user_nutrition_needs
from modules.guidelines import process_user_guidelines
from modules.output_formatter import OutputFormatter


class NutritionCalculatorGUI:
    """GUI Application Class"""
    
    def __init__(self, root):
        """Initialize GUI"""
        self.root = root
        self.root.title("Nutrition Calculation System")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # Set minimum window size
        self.root.minsize(900, 600)
        
        # Result storage
        self.user_data = None
        self.nutrition_results = None
        self.guidelines_result = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container dengan 2 kolom: Input & Result
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ========== LEFT PANEL: INPUT ==========
        left_panel = ttk.LabelFrame(container, text="Input Data", padding=15)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Title
        title_label = ttk.Label(
            left_panel,
            text="Nutrition Calculator",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Input fields
        self._create_input_fields(left_panel)
        
        # Action buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=10)
        
        calculate_btn = ttk.Button(
            button_frame,
            text="Calculate",
            command=self._on_calculate
        )
        calculate_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = ttk.Button(
            button_frame,
            text="Reset",
            command=self._on_reset
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # ========== RIGHT PANEL: RESULT ==========
        right_panel = ttk.LabelFrame(container, text="Results", padding=15)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Result display
        self.result_text = scrolledtext.ScrolledText(
            right_panel,
            height=30,
            width=40,
            font=("Courier", 9),
            bg="white",
            highlightthickness=1,
            highlightbackground="#ccc"
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self._display_welcome_message()
    
    def _create_input_fields(self, parent):
        """Create input fields"""
        
        # Gender
        gender_frame = ttk.Frame(parent)
        gender_frame.pack(fill=tk.X, pady=8)
        ttk.Label(gender_frame, text="Jenis Kelamin:", width=15).pack(side=tk.LEFT)
        self.gender_var = tk.StringVar(value="M")
        gender_combo = ttk.Combobox(
            gender_frame,
            textvariable=self.gender_var,
            values=["M (Laki-laki)", "F (Perempuan)"],
            state="readonly",
            width=20
        )
        gender_combo.pack(side=tk.LEFT, padx=5)
        
        # Age
        age_frame = ttk.Frame(parent)
        age_frame.pack(fill=tk.X, pady=8)
        ttk.Label(age_frame, text="Usia (tahun):", width=15).pack(side=tk.LEFT)
        self.age_var = tk.StringVar(value="25")
        age_spin = ttk.Spinbox(
            age_frame,
            from_=14,
            to=100,
            textvariable=self.age_var,
            width=23
        )
        age_spin.pack(side=tk.LEFT, padx=5)
        
        # Weight
        weight_frame = ttk.Frame(parent)
        weight_frame.pack(fill=tk.X, pady=8)
        ttk.Label(weight_frame, text="Berat Badan (kg):", width=15).pack(side=tk.LEFT)
        self.weight_var = tk.StringVar(value="70")
        weight_entry = ttk.Entry(weight_frame, textvariable=self.weight_var, width=25)
        weight_entry.pack(side=tk.LEFT, padx=5)
        
        # Height
        height_frame = ttk.Frame(parent)
        height_frame.pack(fill=tk.X, pady=8)
        ttk.Label(height_frame, text="Tinggi Badan (cm):", width=15).pack(side=tk.LEFT)
        self.height_var = tk.StringVar(value="170")
        height_entry = ttk.Entry(height_frame, textvariable=self.height_var, width=25)
        height_entry.pack(side=tk.LEFT, padx=5)
        
        # Activity Factor
        activity_frame = ttk.LabelFrame(parent, text="Tingkat Aktivitas", padding=8)
        activity_frame.pack(fill=tk.X, pady=10)
        
        self.activity_var = tk.StringVar(value="1.375")
        
        activities = [
            ("Sedentary (jarang)", "1.2"),
            ("Light (1-3x/minggu)", "1.375"),
            ("Moderate (3-5x/minggu)", "1.55"),
            ("Very Active (6-7x/minggu)", "1.725"),
            ("Extremely Active", "1.9")
        ]
        
        for label, value in activities:
            ttk.Radiobutton(
                activity_frame,
                text=label,
                variable=self.activity_var,
                value=value
            ).pack(anchor=tk.W, pady=2)
        
        # Disease
        disease_frame = ttk.LabelFrame(parent, text="Kondisi Kesehatan", padding=8)
        disease_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(disease_frame, text="Pilih Kondisi:").pack(anchor=tk.W, pady=(0, 5))
        
        self.disease_var = tk.StringVar(value="normal")
        diseases = [
            ("Normal", "normal"),
            ("Diabetes Tipe 2 (DM2)", "dm2"),
            ("Hipertensi", "hypertension"),
            ("Penyakit Kardiovaskular (CVD)", "cvd"),
            ("Kolesterol Tinggi", "cholesterol"),
            ("Penyakit Ginjal Kronis (CKD)", "ckd")
        ]
        
        for label, value in diseases:
            ttk.Radiobutton(
                disease_frame,
                text=label,
                variable=self.disease_var,
                value=value
            ).pack(anchor=tk.W, pady=2)
        
        # Food Preferences
        pref_frame = ttk.Frame(parent)
        pref_frame.pack(fill=tk.X, pady=8)
        ttk.Label(pref_frame, text="Preferensi Makanan:", width=15).pack(side=tk.LEFT)
        self.pref_var = tk.StringVar()
        pref_entry = ttk.Entry(pref_frame, textvariable=self.pref_var, width=25)
        pref_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(pref_frame, text="(Western, Asian, Other)").pack(side=tk.LEFT, padx=5)
    
    def _on_calculate(self):
        """Handle Calculate button click"""
        
        try:
            # Prepare user data
            gender = self.gender_var.get()[0]  # Get first char (M/F)
            age = int(self.age_var.get())
            weight = float(self.weight_var.get())
            height = float(self.height_var.get())
            activity_factor = float(self.activity_var.get())
            disease = self.disease_var.get()
            
            # Parse food preferences
            pref_text = self.pref_var.get().strip()
            food_preferences = [p.strip() for p in pref_text.split(',')] if pref_text else []
            
            self.user_data = {
                'gender': gender,
                'age': age,
                'weight': weight,
                'height': height,
                'activity_factor': activity_factor,
                'disease': disease,
                'food_preferences': food_preferences
            }
            
            # Validate
            if not validate_user_input(self.user_data):
                messagebox.showerror("Error", "Input tidak valid!")
                return
            
            # Calculate nutrition needs
            self.nutrition_results = calculate_user_nutrition_needs(self.user_data)
            
            # Process guidelines
            guidelines_data = process_user_guidelines(self.user_data, self.nutrition_results)
            self.guidelines_result = guidelines_data['guidelines']
            
            # Display results
            self._display_results()
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Input tidak valid: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
    
    def _on_reset(self):
        """Handle Reset button click"""
        self.gender_var.set("M")
        self.age_var.set("25")
        self.weight_var.set("70")
        self.height_var.set("170")
        self.activity_var.set("1.375")
        self.disease_var.set("normal")
        self.pref_var.set("")
        
        self.user_data = None
        self.nutrition_results = None
        self.guidelines_result = None
        
        self._display_welcome_message()
    
    def _display_welcome_message(self):
        """Display welcome message"""
        self.result_text.delete(1.0, tk.END)
        
        welcome_text = """
========================================
NUTRITION CALCULATION SYSTEM
========================================

Selamat datang!

Aplikasi ini akan membantu Anda menghitung:
1. Body Mass Index (BMI)
2. Berat Badan Ideal (BBI)
3. Basal Metabolic Rate (BMR)
4. Total Daily Energy Expenditure (TDEE)
5. Kebutuhan Nutrisi

Cara penggunaan:
1. Isi semua data pada form di sebelah kiri
2. Klik tombol "Calculate"
3. Hasil akan ditampilkan di sini

Silakan mulai dengan mengisi data Anda!
========================================
"""
        self.result_text.insert(1.0, welcome_text)
    
    def _display_results(self):
        """Display calculation results"""
        self.result_text.delete(1.0, tk.END)
        
        result_text = ""
        
        # Header
        result_text += "=" * 45 + "\n"
        result_text += "HASIL PERHITUNGAN\n"
        result_text += "=" * 45 + "\n\n"
        
        # User data
        result_text += "DATA USER:\n"
        result_text += "-" * 45 + "\n"
        gender_text = "Laki-laki" if self.user_data['gender'] == 'M' else "Perempuan"
        result_text += f"Jenis Kelamin: {gender_text}\n"
        result_text += f"Usia: {self.user_data['age']} tahun\n"
        result_text += f"Berat Badan: {self.user_data['weight']} kg\n"
        result_text += f"Tinggi Badan: {self.user_data['height']} cm\n"
        result_text += f"Kondisi: {self.user_data['disease'].upper()}\n\n"
        
        # Anthropometric results
        result_text += "HASIL ANTROPOMETRI:\n"
        result_text += "-" * 45 + "\n"
        result_text += f"BMI: {self.nutrition_results['bmi']} "
        result_text += f"({self.nutrition_results['bmi_category']})\n"
        result_text += f"BBI: {self.nutrition_results['bbi']} kg\n"
        result_text += f"BMR: {self.nutrition_results['bmr']} kcal/hari\n"
        result_text += f"TDEE: {self.nutrition_results['tdee']} kcal/hari\n\n"
        
        # Guidelines
        if self.guidelines_result and self.guidelines_result['guidelines']:
            result_text += "KEBUTUHAN NUTRISI:\n"
            result_text += "-" * 45 + "\n"
            
            # Separate by source
            guideline_nutrients = {}
            dri_nutrients = {}
            
            for nutrient, constraint in self.guidelines_result['guidelines'].items():
                source = constraint.get('source', 'guideline')
                if source == 'DRI fallback':
                    dri_nutrients[nutrient] = constraint
                else:
                    guideline_nutrients[nutrient] = constraint
            
            # Display guideline nutrients
            if guideline_nutrients:
                result_text += f"\nDari Disease Guideline ({len(guideline_nutrients)}):\n"
                for nutrient, constraint in list(guideline_nutrients.items())[:8]:
                    min_val = constraint['min']
                    max_val = constraint['max']
                    unit = constraint.get('unit', '')
                    result_text += f"  {nutrient}: {min_val:.2f} - {max_val:.2f} {unit}\n"
            
            # Display DRI fallback nutrients
            if dri_nutrients:
                result_text += f"\nDari DRI Micronutrient ({len(dri_nutrients)}):\n"
                for nutrient, constraint in list(dri_nutrients.items())[:8]:
                    value = constraint['min']
                    unit = constraint.get('unit', '')
                    result_text += f"  {nutrient}: {value:.2f} {unit}\n"
        
        result_text += "\n" + "=" * 45
        
        self.result_text.insert(1.0, result_text)


def run_gui():
    """Run GUI application"""
    root = tk.Tk()
    app = NutritionCalculatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
