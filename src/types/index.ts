export interface MacronutrientRatios {
  protein: number;
  carbs: number;
  fat: number;
}

export interface Allergen {
  name: string;
  definite: boolean;
}

export interface SearchResult {
  name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  acidity_level: number;
  glycemic_index: number;
  serving_size: number;
  serving_unit: string;
  vitamins: {
    vitamin_c: number;
    vitamin_a: number;
    vitamin_b6: number;
  };
  minerals: {
    potassium: number;
    calcium: number;
    iron: number;
  };
  category: string;
  health_benefits: string[];
  allergens: Allergen[];
  macronutrient_ratios?: MacronutrientRatios;
}