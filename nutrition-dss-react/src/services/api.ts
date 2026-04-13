// API Service Layer
// Handles all backend communication

interface FormData {
  gender: string;
  age: number;
  weight: number;
  height: number;
  activity: string;
  diseases: string[];
  food_preferences: string[];
  algorithm: string;
}

interface AnalysisResult {
  success: boolean;
  energy: {
    bmr: number;
    tdee: number;
  };
  guidelines: Record<string, any>;
  [key: string]: any;
}

interface MenuRequest {
  algorithm: string;
  user_profile: FormData;
  analysis_data: AnalysisResult;
  user_input: AnalysisResult;
}

interface MenuResult {
  success: boolean;
  menu_plan: any;
  [key: string]: any;
}

// Determine API base URL based on environment
const getAPIBase = (): string => {
  if (import.meta.env.DEV) {
    return 'http://localhost:5000';
  }
  // Production: use relative URL or Render backend URL
  return import.meta.env.VITE_API_URL || '';
};

export const api = {
  async analyzeProfile(formData: FormData): Promise<AnalysisResult> {
    const response = await fetch(`${getAPIBase()}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  },

  async generateMenu(menuRequest: MenuRequest): Promise<MenuResult> {
    const response = await fetch(`${getAPIBase()}/api/generate-menu`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(menuRequest),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  },
};
