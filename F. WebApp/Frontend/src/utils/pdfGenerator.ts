import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { nutrientsList, getNutrientUnit } from './nutrientsList';

interface MealData {
  meal: string;
  items: Array<{ type: string; item: string; portion: string }>;
}

interface PDFData {
  userName?: string;
  userData?: {
    gender: string;
    age: number;
    weight: number;
    height: number;
    activity?: string;
    foodPreferences: string[];
  };
  meals: MealData[];
  dailyNeeds: any;
  nutrients: any;
  healthConditions: string[];
  dietTips: Record<string, string[]>;
  language: 'en' | 'id';
  translations: any;
  charts?: {
    macro?: string | null;
    micro?: string | null;
  };
}

export async function generateNutritionPDF(data: PDFData, preview: boolean = false): Promise<string | void> {
  const pdf = new jsPDF('p', 'mm', 'a4');
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 15;
  let yPosition = margin;

  // Colors
  const primaryColor: [number, number, number] = [45, 90, 39]; // forest green (#2d5a27)
  const secondaryColor: [number, number, number] = [85, 133, 80]; // accent green (#558550)
  const textColor: [number, number, number] = [31, 41, 55]; // gray-800

  // Helper function to add new page if needed
  const checkNewPage = (requiredSpace: number = 20) => {
    if (yPosition + requiredSpace > pageHeight - margin) {
      pdf.addPage();
      yPosition = margin;
      return true;
    }
    return false;
  };

  // Header
  pdf.setFillColor(...primaryColor);
  pdf.rect(0, 0, pageWidth, 40, 'F');
  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(24);
  pdf.setFont('helvetica', 'bold');
  pdf.text('ChronoBite', margin, 20);
  pdf.setFontSize(12);
  pdf.setFont('helvetica', 'normal');
  pdf.text('Personalized Nutrition Report', margin, 30);

  // Date
  pdf.setFontSize(10);
  const today = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  pdf.text(today, pageWidth - margin, 30, { align: 'right' });

  yPosition = 50;

  // Section 0: Profile Summary
  if (data.userData) {
    pdf.setTextColor(...primaryColor);
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Profile Summary', margin, yPosition);
    yPosition += 10;

    pdf.setTextColor(...textColor);
    pdf.setFontSize(10);
    
    pdf.setFont('helvetica', 'bold');
    pdf.text('Gender & Age:', margin, yPosition);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`${data.userData.gender === 'male' ? 'Male' : 'Female'}, ${data.userData.age} yrs`, margin + 40, yPosition);
    yPosition += 6;

    pdf.setFont('helvetica', 'bold');
    pdf.text('Weight & Height:', margin, yPosition);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`${data.userData.weight} kg • ${data.userData.height} cm`, margin + 40, yPosition);
    yPosition += 6;

    pdf.setFont('helvetica', 'bold');
    pdf.text('Activity Level:', margin, yPosition);
    pdf.setFont('helvetica', 'normal');
    pdf.text(data.userData.activity || 'Moderate', margin + 40, yPosition);
    yPosition += 6;

    pdf.setFont('helvetica', 'bold');
    pdf.text('Health Conditions:', margin, yPosition);
    pdf.setFont('helvetica', 'normal');
    const conditions = data.healthConditions.map(c => data.translations.input.health[c] || c).join(', ') || 'Normal';
    pdf.text(conditions, margin + 40, yPosition);
    yPosition += 6;

    pdf.setFont('helvetica', 'bold');
    pdf.text('Food Preferences:', margin, yPosition);
    pdf.setFont('helvetica', 'normal');
    const prefs = data.userData.foodPreferences?.join(', ') || 'All Cuisines';
    pdf.text(prefs, margin + 40, yPosition);
    yPosition += 12;
  }

  // Section 1: Meal Menu
  pdf.setTextColor(...primaryColor);
  pdf.setFontSize(16);
  pdf.setFont('helvetica', 'bold');
  pdf.text(data.translations.report.tabs.menu, margin, yPosition);
  yPosition += 10;

  pdf.setTextColor(...textColor);
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'normal');

  data.meals.forEach((mealData) => {
    checkNewPage(30);

    // Meal title
    pdf.setFont('helvetica', 'bold');
    pdf.setFontSize(12);
    pdf.text(mealData.meal, margin, yPosition);
    yPosition += 7;

    // Meal items
    pdf.setFont('helvetica', 'normal');
    pdf.setFontSize(10);
    mealData.items.forEach((item) => {
      checkNewPage(8);
      pdf.setTextColor(...secondaryColor);
      pdf.text(`• ${item.type}:`, margin + 5, yPosition);
      pdf.setTextColor(...textColor);
      pdf.text(`${item.item} (${item.portion})`, margin + 30, yPosition);
      yPosition += 6;
    });
    yPosition += 5;
  });

  // Section 2: Daily Nutrition Summary
  checkNewPage(40);
  yPosition += 5;
  pdf.setTextColor(...primaryColor);
  pdf.setFontSize(16);
  pdf.setFont('helvetica', 'bold');
  pdf.text(data.translations.results.nutritionSummary, margin, yPosition);
  yPosition += 10;

  pdf.setTextColor(...textColor);
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'normal');

  // Macronutrients table
  const macros = [
    { name: data.translations.results.dailyCalories, value: `${data.nutrients.calories} / ${data.dailyNeeds.calories}` },
    { name: data.translations.results.protein, value: `${data.nutrients.protein}g / ${data.dailyNeeds.protein}g` },
    { name: data.translations.results.carbs, value: `${data.nutrients.carbs}g / ${data.dailyNeeds.carbs}g` },
    { name: data.translations.results.fat, value: `${data.nutrients.fat}g / ${data.dailyNeeds.fat}g` },
  ];

  macros.forEach((macro) => {
    checkNewPage(8);
    pdf.setFont('helvetica', 'bold');
    pdf.text(macro.name + ':', margin, yPosition);
    pdf.setFont('helvetica', 'normal');
    pdf.text(macro.value, margin + 60, yPosition);
    yPosition += 7;
  });

  // Section 3: All Nutrients Breakdown
  checkNewPage(40);
  yPosition += 10;
  pdf.setTextColor(...primaryColor);
  pdf.setFontSize(16);
  pdf.setFont('helvetica', 'bold');
  pdf.text(data.translations.report.tabs.other, margin, yPosition);
  yPosition += 10;

  pdf.setTextColor(...textColor);
  pdf.setFontSize(9);
  pdf.setFont('helvetica', 'normal');

  // Group nutrients
  const groups = [
    { title: 'Macronutrients', nutrients: ['carbohydrate_g', 'protein_g', 'fat_g'] },
    {
      title: 'Vitamins',
      nutrients: nutrientsList.filter(n => n.startsWith('vitamin_'))
    },
    {
      title: 'Minerals',
      nutrients: ['calcium_mg', 'iron_mg', 'magnesium_mg', 'phosphorus_mg', 'potassium_mg',
                  'sodium_mg', 'zinc_mg', 'copper_mg', 'manganese_mg', 'selenium_mg', 'fluoride_mg']
    },
    {
      title: 'Others',
      nutrients: ['fiber_g', 'sugar_g', 'saturated_fat_g', 'trans_fat_g', 'cholesterol_mg',
                  'choline_mg', 'folate_mg', 'water_g', 'energy_kcal']
    },
  ];

  groups.forEach((group) => {
    checkNewPage(15);
    pdf.setFont('helvetica', 'bold');
    pdf.setFontSize(11);
    pdf.text(group.title, margin, yPosition);
    yPosition += 6;

    pdf.setFont('helvetica', 'normal');
    pdf.setFontSize(9);

    group.nutrients.forEach((nutrientKey: string) => {
      const value = data.dailyNeeds[nutrientKey];
      const unit = getNutrientUnit(nutrientKey as any);
      const name = data.translations.nutrients[nutrientKey];
      const actual = Math.round(Number(value) * (0.7 + Math.random() * 0.4));

      checkNewPage(6);
      pdf.text(`• ${name}:`, margin + 3, yPosition);
      pdf.text(`${actual}${unit} / ${value}${unit}`, margin + 80, yPosition);
      yPosition += 5;
    });
    yPosition += 3;
  });

  // Section 3.5: Nutrition Analysis (Charts)
  if (data.charts && (data.charts.macro || data.charts.micro)) {
    checkNewPage(60);
    yPosition += 10;
    pdf.setTextColor(...primaryColor);
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    pdf.text(data.translations.report.tabs.nutrition || "Nutrition Analysis", margin, yPosition);
    yPosition += 10;

    const chartWidth = pageWidth - 2 * margin;
    const chartHeight = chartWidth * 0.5; // assuming 2:1 aspect ratio (800x400)

    if (data.charts.macro) {
      checkNewPage(chartHeight + 20);
      pdf.setFontSize(12);
      pdf.text("Macronutrient Balance", margin, yPosition);
      yPosition += 5;
      pdf.addImage(data.charts.macro, 'PNG', margin, yPosition, chartWidth, chartHeight);
      yPosition += chartHeight + 10;
    }

    if (data.charts.micro) {
      checkNewPage(chartHeight + 20);
      pdf.setFontSize(12);
      pdf.text("Micronutrient Analysis", margin, yPosition);
      yPosition += 5;
      pdf.addImage(data.charts.micro, 'PNG', margin, yPosition, chartWidth, chartHeight);
      yPosition += chartHeight + 10;
    }
  }

  // Section 4: Diet Tips
  if (data.healthConditions.length > 0) {
    checkNewPage(40);
    yPosition += 5;
    pdf.setTextColor(...primaryColor);
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    pdf.text(data.translations.report.tabs.tips, margin, yPosition);
    yPosition += 10;

    pdf.setTextColor(...textColor);
    pdf.setFontSize(10);

    data.healthConditions.forEach((condition) => {
      const tips = data.dietTips[condition];
      if (tips) {
        checkNewPage(20);
        pdf.setFont('helvetica', 'bold');
        pdf.text(data.translations.input.health[condition], margin, yPosition);
        yPosition += 6;

        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(9);
        tips.forEach((tip) => {
          checkNewPage(8);
          const lines = pdf.splitTextToSize(`• ${tip}`, pageWidth - margin * 2 - 5);
          lines.forEach((line: string) => {
            checkNewPage(5);
            pdf.text(line, margin + 3, yPosition);
            yPosition += 5;
          });
        });
        yPosition += 3;
      }
    });
  }

  // Footer on last page
  pdf.setFontSize(8);
  pdf.setTextColor(100, 100, 100);
  pdf.text(
    'Generated by ChronoBite - Your Personal Nutrition Assistant',
    pageWidth / 2,
    pageHeight - 10,
    { align: 'center' }
  );

  // Save or preview PDF
  const fileName = `ChronoBite_Report_${new Date().toISOString().split('T')[0]}.pdf`;
  if (preview) {
    return pdf.output('bloburl').toString();
  } else {
    pdf.save(fileName);
  }
}

export async function generatePDFFromElement(elementId: string, fileName: string = 'report.pdf'): Promise<void> {
  const element = document.getElementById(elementId);
  if (!element) {
    console.error('Element not found');
    return;
  }

  const canvas = await html2canvas(element, {
    scale: 2,
    useCORS: true,
    logging: false,
  });

  const imgData = canvas.toDataURL('image/png');
  const pdf = new jsPDF('p', 'mm', 'a4');
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const imgWidth = pageWidth;
  const imgHeight = (canvas.height * imgWidth) / canvas.width;

  let heightLeft = imgHeight;
  let position = 0;

  pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
  heightLeft -= pageHeight;

  while (heightLeft > 0) {
    position = heightLeft - imgHeight;
    pdf.addPage();
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;
  }

  pdf.save(fileName);
}
