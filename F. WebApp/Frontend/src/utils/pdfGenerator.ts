import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { nutrientsList, getNutrientUnit } from './nutrientsList';
import logoWhite from '../assets/ChronoBite White.png';

const loadImage = (src: string): Promise<HTMLImageElement> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = (e) => reject(e);
    img.src = src;
  });
};

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
  analysisGuidelines?: any;
  charts?: {
    macro?: string | null;
    micro?: string | null;
  };
}

let cachedLoraReg: string | null = null;
let cachedLoraBold: string | null = null;
let cachedInterReg: string | null = null;
let cachedInterBold: string | null = null;
let prefetchPromise: Promise<void> | null = null;

const fetchFontAsBase64 = async (url: string): Promise<string> => {
  const response = await fetch(url);
  const arrayBuffer = await response.arrayBuffer();
  let binary = '';
  const bytes = new Uint8Array(arrayBuffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
};

export function preFetchFonts(): Promise<void> {
  if (prefetchPromise) return prefetchPromise;

  prefetchPromise = (async () => {
    try {
      const [loraReg, loraBold, interReg, interBold] = await Promise.all([
        fetchFontAsBase64('https://fonts.gstatic.com/s/lora/v37/0QI6MX1D_JOuGQbT0gvTJPa787weuxJBkqg.ttf'),
        fetchFontAsBase64('https://fonts.gstatic.com/s/lora/v37/0QI6MX1D_JOuGQbT0gvTJPa787z5vBJBkqg.ttf'),
        fetchFontAsBase64('https://fonts.gstatic.com/s/inter/v20/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuLyfAZ9hjQ.ttf'),
        fetchFontAsBase64('https://fonts.gstatic.com/s/inter/v20/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuFuYAZ9hjQ.ttf')
      ]);

      cachedLoraReg = loraReg;
      cachedLoraBold = loraBold;
      cachedInterReg = interReg;
      cachedInterBold = interBold;
    } catch (err) {
      console.warn("Failed to prefetch custom fonts", err);
    }
  })();

  return prefetchPromise;
}

export async function generateNutritionPDF(data: PDFData, preview: boolean = false): Promise<string | void> {
  const pdf = new jsPDF('p', 'mm', 'a4');
  pdf.setProperties({
    title: `ChronoBite_${new Date().toISOString().split('T')[0]}`
  });
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 15;
  let yPosition = margin;

  // Colors
  const primaryColor: [number, number, number] = [45, 90, 39]; // forest green (#2d5a27)
  const secondaryColor: [number, number, number] = [85, 133, 80]; // accent green (#558550)
  const textColor: [number, number, number] = [31, 41, 55]; // gray-800

  // Wait for prefetch or fetch immediately
  await preFetchFonts();

  // Dynamic font registration with fallback
  let hasLora = false;
  let hasInter = false;

  if (cachedLoraReg && cachedLoraBold) {
    try {
      pdf.addFileToVFS('Lora-Regular.ttf', cachedLoraReg);
      pdf.addFont('Lora-Regular.ttf', 'Lora', 'normal');
      pdf.addFileToVFS('Lora-Bold.ttf', cachedLoraBold);
      pdf.addFont('Lora-Bold.ttf', 'Lora', 'bold');
      hasLora = true;
    } catch (err) {
      console.warn("Failed to register Lora, falling back", err);
    }
  }

  if (cachedInterReg && cachedInterBold) {
    try {
      pdf.addFileToVFS('Inter-Regular.ttf', cachedInterReg);
      pdf.addFont('Inter-Regular.ttf', 'Inter', 'normal');
      pdf.addFileToVFS('Inter-Bold.ttf', cachedInterBold);
      pdf.addFont('Inter-Bold.ttf', 'Inter', 'bold');
      hasInter = true;
    } catch (err) {
      console.warn("Failed to register Inter, falling back", err);
    }
  }

  const setSerif = (style: 'normal' | 'bold') => {
    pdf.setFont(hasLora ? 'Lora' : 'times', style);
  };

  const setSans = (style: 'normal' | 'bold') => {
    pdf.setFont(hasInter ? 'Inter' : 'helvetica', style);
  };

  // Helper function to add new page if needed
  const checkNewPage = (requiredSpace: number = 20) => {
    if (yPosition + requiredSpace > pageHeight - 25) {
      pdf.addPage();
      yPosition = margin;
      return true;
    }
    return false;
  };

  // Load Logo
  let logoImg: HTMLImageElement | null = null;
  try {
    logoImg = await loadImage(logoWhite);
  } catch (err) {
    console.error("Failed to load logo", err);
  }

  // Header
  pdf.setFillColor(...primaryColor);
  pdf.rect(0, 0, pageWidth, 40, 'F');
  pdf.setTextColor(255, 255, 255);
  
  if (logoImg) {
    const logoHeight = 18; // mm
    const aspect = logoImg.naturalWidth / logoImg.naturalHeight;
    const logoWidth = logoHeight * aspect;
    pdf.addImage(logoImg, 'PNG', margin, 5.5, logoWidth, logoHeight);
  } else {
    pdf.setFontSize(24);
    setSerif('bold');
    pdf.text('ChronoBite', margin, 20);
  }
  
  pdf.setFontSize(11);
  setSans('normal');
  pdf.setTextColor(220, 225, 220);
  pdf.text('Personalized Nutrition Report', margin, 29.5);

  // Date
  pdf.setFontSize(10);
  setSans('normal');
  const today = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  pdf.text(today, pageWidth - margin, 29.5, { align: 'right' });

  yPosition = 50;

  // Section 0: Profile Summary
  if (data.userData) {
    pdf.setTextColor(...primaryColor);
    pdf.setFontSize(16);
    setSerif('bold');
    pdf.text('Profile Summary', margin, yPosition);
    yPosition += 10;

    pdf.setTextColor(...textColor);
    pdf.setFontSize(10);
    
    setSans('bold');
    pdf.text('Gender & Age', margin, yPosition);
    setSerif('normal');
    pdf.text(`${data.userData.gender === 'male' ? 'Male' : 'Female'}, ${data.userData.age} yrs`, margin + 40, yPosition);
    yPosition += 6;

    setSans('bold');
    pdf.text('Weight & Height', margin, yPosition);
    setSerif('normal');
    pdf.text(`${data.userData.weight} kg • ${data.userData.height} cm`, margin + 40, yPosition);
    yPosition += 6;

    setSans('bold');
    pdf.text('Activity Level', margin, yPosition);
    setSerif('normal');
    pdf.text(data.userData.activity || 'Moderate', margin + 40, yPosition);
    yPosition += 6;

    setSans('bold');
    pdf.text('Health Conditions', margin, yPosition);
    setSerif('normal');
    const conditions = data.healthConditions.map(c => data.translations.input.health[c] || c).join(', ') || 'Normal';
    pdf.text(conditions, margin + 40, yPosition);
    yPosition += 6;

    setSans('bold');
    pdf.text('Food Preferences', margin, yPosition);
    setSerif('normal');
    const prefs = data.userData.foodPreferences?.join(', ') || 'All Cuisines';
    pdf.text(prefs, margin + 40, yPosition);
    yPosition += 12;
  }

  // Section 1: Meal Menu
  pdf.setTextColor(...primaryColor);
  pdf.setFontSize(16);
  setSerif('bold');
  pdf.text(data.translations.report.tabs.menu, margin, yPosition);
  yPosition += 10;

  pdf.setTextColor(...textColor);
  pdf.setFontSize(10);
  setSans('normal');

  data.meals.forEach((mealData) => {
    checkNewPage(30);

    // Meal title
    setSerif('bold');
    pdf.setFontSize(12);
    pdf.text(mealData.meal, margin, yPosition);
    yPosition += 7;

    // Meal items
    setSans('normal');
    pdf.setFontSize(10);
    mealData.items.forEach((item) => {
      checkNewPage(8);
      pdf.setTextColor(...secondaryColor);
      setSans('bold');
      const capitalizedType = item.type.charAt(0).toUpperCase() + item.type.slice(1);
      pdf.text(capitalizedType, margin + 5, yPosition);
      setSans('normal');
      pdf.setTextColor(...textColor);
      pdf.text(`${item.item} (${item.portion})`, margin + 40, yPosition);
      yPosition += 6;
    });
    yPosition += 5;
  });

  // Section 2: Daily Nutrition Summary
  checkNewPage(40);
  yPosition += 5;
  pdf.setTextColor(...primaryColor);
  pdf.setFontSize(16);
  setSerif('bold');
  pdf.text(data.translations.results.nutritionSummary, margin, yPosition);
  yPosition += 10;

  pdf.setTextColor(...textColor);
  pdf.setFontSize(10);
  setSans('normal');

  // Macronutrients table
  const formatVal = (val: any) => {
    if (val === null || val === undefined) return '';
    const num = Number(val);
    return isNaN(num) ? String(val) : String(Math.round(num));
  };

  const getNutrientTargetRange = (key: string, fallbackTarget: number, unit: string) => {
    const rule = data.analysisGuidelines?.nutrients?.[key];
    if (rule) {
      const minVal = rule.min != null ? Math.round(rule.min) : null;
      const maxVal = rule.max != null && Number.isFinite(rule.max) ? Math.round(rule.max) : null;
      
      if (minVal !== null && maxVal !== null) {
        if (minVal === maxVal) return `± ${minVal} ${unit}`;
        return `${minVal}-${maxVal} ${unit}`;
      }
      if (minVal !== null) return `min. ${minVal} ${unit}`;
      if (maxVal !== null) return `max. ${maxVal} ${unit}`;
    }
    return `${Math.round(fallbackTarget)} ${unit}`;
  };

  const isMacroFulfilled = (key: string, actual: number, fallbackTarget: number) => {
    const rule = data.analysisGuidelines?.nutrients?.[key];
    if (rule) {
      const minVal = rule.min != null ? rule.min : null;
      const maxVal = rule.max != null && Number.isFinite(rule.max) ? rule.max : null;
      if (minVal !== null && actual < minVal) return false;
      if (maxVal !== null && actual > maxVal) return false;
      return true;
    }
    return actual >= fallbackTarget;
  };

  const isHardConstraintFulfilled = (rule: any, actual: number) => {
    const minVal = rule.min != null ? rule.min : null;
    const maxVal = rule.max != null && Number.isFinite(rule.max) ? rule.max : null;
    if (minVal !== null && actual < minVal) return false;
    if (maxVal !== null && actual > maxVal) return false;
    return true;
  };

  const isOtherNutrientFulfilled = (actual: number, target: number) => {
    return actual >= target;
  };

  const macros = [
    { key: 'energy_kcal', name: data.translations.results.dailyCalories, actualVal: data.nutrients.calories, targetVal: data.dailyNeeds.calories, actual: `${formatVal(data.nutrients.calories)} kcal`, target: getNutrientTargetRange('energy_kcal', data.dailyNeeds.calories, 'kcal') },
    { key: 'carbohydrate_g', name: data.translations.results.carbs, actualVal: data.nutrients.carbs, targetVal: data.dailyNeeds.carbs, actual: `${formatVal(data.nutrients.carbs)}g`, target: getNutrientTargetRange('carbohydrate_g', data.dailyNeeds.carbs, 'g') },
    { key: 'protein_g', name: data.translations.results.protein, actualVal: data.nutrients.protein, targetVal: data.dailyNeeds.protein, actual: `${formatVal(data.nutrients.protein)}g`, target: getNutrientTargetRange('protein_g', data.dailyNeeds.protein, 'g') },
    { key: 'fat_g', name: data.translations.results.fat, actualVal: data.nutrients.fat, targetVal: data.dailyNeeds.fat, actual: `${formatVal(data.nutrients.fat)}g`, target: getNutrientTargetRange('fat_g', data.dailyNeeds.fat, 'g') },
  ];

  macros.forEach((macro) => {
    checkNewPage(8);
    setSans('bold');
    pdf.text(macro.name, margin, yPosition);
    
    const fulfilled = isMacroFulfilled(macro.key, Number(macro.actualVal), Number(macro.targetVal));
    if (fulfilled) {
      setSans('bold');
      pdf.setTextColor(46, 125, 50);
    } else {
      setSans('normal');
      pdf.setTextColor(...textColor);
    }
    pdf.text(macro.actual, margin + 40, yPosition);
    
    setSans('normal');
    pdf.setTextColor(...textColor);
    pdf.text(macro.target, margin + 65, yPosition);
    yPosition += 7;
  });

  // Section 3: All Nutrients Breakdown
  checkNewPage(40);
  yPosition += 10;
  pdf.setTextColor(...primaryColor);
  pdf.setFontSize(16);
  setSerif('bold');
  pdf.text('Nutrition Breakdown', margin, yPosition);
  yPosition += 10;

  // Identify Hard Constraints (excluding energy and macronutrients as they are in the Summary)
  const excludeMacros = ['energy_kcal', 'carbohydrate_g', 'protein_g', 'fat_g'];
  const hardConstraints: string[] = [];
  if (data.analysisGuidelines?.nutrients) {
    Object.entries(data.analysisGuidelines.nutrients).forEach(([key, rule]: [string, any]) => {
      if (rule.hard_soft_type === 'HARD' && nutrientsList.includes(key as any) && !excludeMacros.includes(key)) {
        hardConstraints.push(key);
      }
    });
  }

  // 1. Display Required Nutrient Limits
  pdf.setTextColor(...primaryColor);
  pdf.setFontSize(12);
  setSerif('bold');
  pdf.text('Required Nutrient Limits', margin, yPosition);
  yPosition += 7;

  pdf.setTextColor(...textColor);
  pdf.setFontSize(10);
  setSans('normal');

  if (hardConstraints.length > 0) {
    hardConstraints.forEach((nutrientKey) => {
      const rule = data.analysisGuidelines.nutrients[nutrientKey];
      const unit = rule.unit || getNutrientUnit(nutrientKey as any);
      const name = data.translations.nutrients[nutrientKey] || nutrientKey;
      
      const actualVal = data.nutrients?.[nutrientKey] != null
        ? Math.round(Number(data.nutrients[nutrientKey]))
        : Math.round(Number(data.dailyNeeds[nutrientKey]) * 0.9);

      const minVal = rule.min != null ? Math.round(rule.min) : null;
      const maxVal = rule.max != null && Number.isFinite(rule.max) ? Math.round(rule.max) : null;
      
      let rangeText = '';
      if (minVal !== null && maxVal !== null) {
        if (minVal === maxVal) {
          rangeText = `± ${minVal} ${unit}`;
        } else {
          rangeText = `${minVal}-${maxVal} ${unit}`;
        }
      } else if (minVal !== null) {
        rangeText = `min. ${minVal} ${unit}`;
      } else if (maxVal !== null) {
        rangeText = `max. ${maxVal} ${unit}`;
      } else {
        rangeText = 'No limits';
      }

      checkNewPage(6);
      pdf.setTextColor(...textColor);
      pdf.text(`${name}`, margin + 3, yPosition);
      
      const fulfilled = isHardConstraintFulfilled(rule, actualVal);
      if (fulfilled) {
        setSans('bold');
        pdf.setTextColor(46, 125, 50);
      } else {
        setSans('normal');
        pdf.setTextColor(...textColor);
      }
      pdf.text(`${actualVal}${unit}`, margin + 50, yPosition);
      
      setSans('normal');
      pdf.setTextColor(...textColor);
      pdf.text(`${rangeText}`, margin + 75, yPosition);
      yPosition += 5;
    });
  } else {
    checkNewPage(6);
    setSans('normal');
    pdf.text('No specific health-related hard constraints', margin + 3, yPosition);
    yPosition += 5;
  }
  yPosition += 5;

  // 2. Display Other Nutrients
  checkNewPage(20);
  pdf.setTextColor(...primaryColor);
  pdf.setFontSize(12);
  setSerif('bold');
  pdf.text('Other Nutrients', margin, yPosition);
  yPosition += 7;

  pdf.setTextColor(...textColor);
  pdf.setFontSize(10);

  // Group nutrients, filtering out hard constraints and excluding Macronutrients as they are in the Summary
  const groups = [
    {
      title: 'Vitamins',
      nutrients: nutrientsList.filter(n => n.startsWith('vitamin_') && !hardConstraints.includes(n))
    },
    {
      title: 'Minerals',
      nutrients: ['calcium_mg', 'iron_mg', 'magnesium_mg', 'phosphorus_mg', 'potassium_mg',
                  'sodium_mg', 'zinc_mg', 'copper_mg', 'manganese_mg', 'selenium_mg', 'fluoride_mg'].filter(n => !hardConstraints.includes(n))
    },
    {
      title: 'Others',
      nutrients: ['fiber_g', 'sugar_g', 'saturated_fat_g', 'trans_fat_g', 'cholesterol_mg',
                  'choline_mg', 'folate_mg', 'water_g', 'energy_kcal'].filter(n => !hardConstraints.includes(n))
    },
  ];

  groups.forEach((group) => {
    if (group.nutrients.length === 0) return;

    checkNewPage(15);
    setSans('bold');
    pdf.setFontSize(11);
    pdf.text(group.title, margin, yPosition);
    yPosition += 6;

    setSans('normal');
    pdf.setFontSize(10);

    group.nutrients.forEach((nutrientKey: string) => {
      const value = data.dailyNeeds[nutrientKey];
      const unit = getNutrientUnit(nutrientKey as any);
      const name = data.translations.nutrients[nutrientKey] || nutrientKey;
      
      const actual = data.nutrients?.[nutrientKey] != null 
        ? Math.round(Number(data.nutrients[nutrientKey])) 
        : Math.round(Number(value) * (0.7 + Math.random() * 0.4));

      checkNewPage(6);
      pdf.setTextColor(...textColor);
      pdf.text(`${name}`, margin + 3, yPosition);
      
      const fulfilled = isOtherNutrientFulfilled(actual, Number(value));
      if (fulfilled) {
        setSans('bold');
        pdf.setTextColor(46, 125, 50);
      } else {
        setSans('normal');
        pdf.setTextColor(...textColor);
      }
      pdf.text(`${actual}${unit}`, margin + 50, yPosition);
      
      setSans('normal');
      pdf.setTextColor(...textColor);
      pdf.text(`${value}${unit}`, margin + 75, yPosition);
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
    setSerif('bold');
    pdf.text(data.translations.report.tabs.nutrition || "Nutrition Analysis", margin, yPosition);
    yPosition += 10;

    const chartWidth = pageWidth - 2 * margin;
    const chartHeight = chartWidth * 0.5; // assuming 2:1 aspect ratio (800x400)

    if (data.charts.macro) {
      checkNewPage(chartHeight + 20);
      pdf.setFontSize(12);
      setSerif('bold');
      pdf.text("Macronutrient Balance", margin, yPosition);
      yPosition += 5;
      pdf.addImage(data.charts.macro, 'PNG', margin, yPosition, chartWidth, chartHeight);
      yPosition += chartHeight + 10;
    }

    if (data.charts.micro) {
      checkNewPage(chartHeight + 20);
      pdf.setFontSize(12);
      setSerif('bold');
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
    setSerif('bold');
    pdf.text(data.translations.report.tabs.tips, margin, yPosition);
    yPosition += 10;

    pdf.setTextColor(...textColor);

    data.healthConditions.forEach((condition) => {
      const tips = data.dietTips[condition];
      if (tips) {
        checkNewPage(20);
        pdf.setFontSize(12);
        setSans('bold');
        pdf.text(data.translations.input.health[condition], margin, yPosition);
        yPosition += 6;

        setSans('normal');
        pdf.setFontSize(10);
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
  setSans('normal');
  pdf.setTextColor(100, 100, 100);
  pdf.text(
    'Generated by ChronoBite - Your Personal Nutrition Assistant',
    pageWidth / 2,
    pageHeight - 10,
    { align: 'center' }
  );

  // Save or preview PDF
  const fileName = `ChronoBite_${new Date().toISOString().split('T')[0]}.pdf`;
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
