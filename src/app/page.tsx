'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { FormEvent } from 'react';

interface FoodItem {
  name: string;
  serving_size: number;
  serving_unit: string;
  [key: string]: string | number;  // Better typing for additional properties
}

interface NutritionData {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  proteinPercentage: number;
  carbsPercentage: number;
  fatPercentage: number;
  acidity_level?: number;
  image?: string;
  name: string;
  allergens?: Array<{
    name: string;
    definite: boolean;
  }>;
  health_benefits?: string[];
  macronutrient_ratios?: {
    protein: number;
    carbs: number;
    fat: number;
  };
}

// List of keywords that indicate a liquid food
const LIQUID_FOODS = [
  'coffee', 'tea', 'juice', 'milk', 'smoothie', 'shake', 'beverage', 'drink',
  'americano', 'espresso', 'latte', 'cappuccino', 'water', 'soda', 'beer', 'wine',
  'cortado', 'macchiato', 'mocha', 'frappuccino', 'cold brew', 'nitro', 'lungo',
  'ristretto', 'flat white', 'affogato'
];

const isLiquidFood = (foodName: string): boolean => {
  return LIQUID_FOODS.some(keyword => foodName.toLowerCase().includes(keyword));
};

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [foodQuery, setFoodQuery] = useState('');
  const [quantity, setQuantity] = useState('100');
  const [unit, setUnit] = useState('g');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [nutritionData, setNutritionData] = useState<NutritionData | null>(null);
  const [suggestions, setSuggestions] = useState<FoodItem[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (isLiquidFood(foodQuery)) {
      setUnit('ml');
      setQuantity('100');
    } else {
      setUnit('g');
      setQuantity('100');
    }
  }, [foodQuery]);

  useEffect(() => {
    if (showSuggestions && suggestions.length > 0) {
      document.body.classList.add('results-shown');
    } else {
      document.body.classList.remove('results-shown');
    }
  }, [showSuggestions, suggestions.length]);

  const fetchSuggestions = async (searchQuery: string) => {
    if (!searchQuery) {
      setSuggestions([]);
      return;
    }
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/search?query=${encodeURIComponent(searchQuery.toLowerCase())}`
      );
      const data = await response.json();
      // Filter out any entries with size indicators and remove duplicates
      const cleanedData = data
        .map((item: FoodItem) => ({
          ...item,
          name: item.name.replace(/\s*\((Small|Medium|Large)\)/g, '').trim()
        }))
        .filter((item: FoodItem, index: number, self: FoodItem[]) => 
          index === self.findIndex((t) => t.name.toLowerCase() === item.name.toLowerCase())
        );
      setSuggestions(cleanedData);
      setShowSuggestions(true);
    } catch (err) {
      console.error('Failed to fetch suggestions:', err);
    }
  };

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setFoodQuery(value);
    
    // Clear nutrition data when search is empty
    if (!value.trim()) {
      setNutritionData(null);
      setSuggestions([]);
      setShowSuggestions(false);
    } else {
      fetchSuggestions(value);
    }
  };

  const handleSuggestionClick = (suggestion: FoodItem) => {
    setFoodQuery(suggestion.name);
    setShowSuggestions(false);
    setQuantity('100');
    setUnit(isLiquidFood(suggestion.name) ? 'ml' : 'g');
    document.body.classList.remove('results-shown');
  };

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const cleanQuery = foodQuery.replace(/\s*\((Small|Medium|Large)\)/g, '');
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/nutrition?query=${encodeURIComponent(cleanQuery)}&quantity=${quantity}&unit=${unit}`
      );
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch nutrition data');
      }
      
      // Calculate macronutrient percentages
      const totalCaloriesFromMacros = (data.protein * 4) + (data.carbs * 4) + (data.fat * 9);
      const proteinPercentage = Math.round((data.protein * 4 / totalCaloriesFromMacros) * 100);
      const carbsPercentage = Math.round((data.carbs * 4 / totalCaloriesFromMacros) * 100);
      const fatPercentage = Math.round((data.fat * 9 / totalCaloriesFromMacros) * 100);

      // Update the data with calculated percentages
      setNutritionData({
        ...data,
        proteinPercentage,
        carbsPercentage,
        fatPercentage
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
      setShowSuggestions(false);
    }
  };

  if (!mounted) {
    return null;
  }

  return (
    <main className="min-h-screen relative">
      {/* Background Image */}
      <div className="fixed inset-0 z-0">
        <Image
          src="/images/fridge-background.jpg"
          alt="Background"
          fill
          className="object-cover"
          priority
        />
      </div>
      
      {/* Mobile Navigation Bar */}
      <div className="md:hidden fixed top-0 left-0 right-0 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md z-50 shadow-lg">
        <div className="flex justify-between items-center px-4 py-3">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-amber-950 to-amber-700 bg-clip-text text-transparent">
            NutriSmart
          </h1>
        </div>
      </div>
      
      {/* Content Container with backdrop blur */}
      <div className="relative z-10 pt-16 md:pt-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Enhanced Header with backdrop */}
          <div className="text-center mb-8 md:mb-12 animate-fade-in bg-white/95 dark:bg-slate-900/95 backdrop-blur-md rounded-2xl p-6 md:p-8 shadow-xl">
            <h1 className="hidden md:block text-5xl md:text-6xl font-extrabold mb-4 bg-gradient-to-r from-amber-950 via-amber-800 to-amber-700 bg-clip-text text-transparent drop-shadow-[0_2px_2px_rgba(120,53,15,0.3)] tracking-tight font-serif">
              NutriSmart
            </h1>
            <p className="text-lg md:text-xl font-medium tracking-wide bg-gradient-to-r from-slate-800 to-slate-600 dark:from-slate-200 dark:to-slate-300 bg-clip-text text-transparent transition-all duration-300 ease-in-out hover:tracking-wider font-sans">
              Make informed choices with instant nutritional insights
            </p>
          </div>

          {/* Search Section */}
          <div className="space-y-4 sm:space-y-8">
            <form onSubmit={handleSearch} className="search-container mx-0 sm:mx-0 p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-lg bg-white/95 dark:bg-slate-800/95 backdrop-blur-lg">
              <div className="flex flex-col gap-4">
                {/* Search Input */}
                <div className="relative">
                  <input
                    type="text"
                    value={foodQuery}
                    onChange={handleQueryChange}
                    onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                    placeholder="Search for any food..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-lg text-slate-900 dark:text-white bg-white/90 dark:bg-slate-800/90"
                    required
                  />
                  {suggestions.length > 0 && showSuggestions && (
                    <div className="absolute left-0 right-0 mt-1 max-h-60 overflow-auto bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
                      {suggestions.map((suggestion, index) => (
                        <div
                          key={index}
                          className="p-3 hover:bg-gray-100 dark:hover:bg-slate-700 cursor-pointer border-b border-gray-200 dark:border-gray-700 transition-colors"
                          onClick={() => handleSuggestionClick(suggestion)}
                        >
                          <span className="font-medium text-slate-900 dark:text-white">{suggestion.name}</span>
                          <span className="text-sm text-slate-600 dark:text-slate-300 ml-2">
                            (100 {isLiquidFood(suggestion.name) ? 'ml' : 'g'})
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Quantity and Unit Controls - Mobile Optimized */}
                <div className="flex gap-2 flex-col sm:flex-row">
                  <div className="flex-1">
                    <input
                      type="number"
                      value={quantity}
                      onChange={(e) => setQuantity(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-lg text-slate-900 dark:text-white bg-white/90 dark:bg-slate-800/90"
                      min="0"
                      required
                    />
                  </div>
                  <div className="w-full sm:w-24">
                    <select
                      value={unit}
                      onChange={(e) => setUnit(e.target.value)}
                      className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 bg-white/90 dark:bg-slate-800/90 text-lg text-slate-900 dark:text-white"
                      required
                    >
                      <option value={isLiquidFood(foodQuery) ? 'ml' : 'g'}>
                        {isLiquidFood(foodQuery) ? 'ml' : 'g'}
                      </option>
                      <option value="oz">oz</option>
                    </select>
                  </div>
                </div>

                {/* Search Button */}
                <button
                  type="submit"
                  className="w-full px-6 py-3 bg-[#0B4A0B] text-white rounded-lg hover:bg-[#083708] focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors text-lg font-medium shadow-md"
                  disabled={loading}
                >
                  {loading ? 'Searching...' : 'Get Nutrition'}
                </button>
              </div>
            </form>

            {error && (
              <div className="text-error text-sm font-medium px-4 py-2 bg-error/10 rounded-lg">
                {error}
              </div>
            )}

            {/* Results Section */}
            {nutritionData && (
              <div className="mt-8 space-y-4 animate-fade-in-up">
                {/* Main Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="stat-card bg-white/95 dark:bg-slate-800/95 backdrop-blur-md p-6 rounded-2xl shadow-lg transform hover:scale-105 transition-transform duration-200">
                    <div className="stat-value text-2xl font-bold text-amber-700 dark:text-amber-400">{nutritionData.calories}</div>
                    <div className="stat-label text-sm text-slate-900 dark:text-slate-100 mt-2 font-medium">Calories</div>
                  </div>
                  <div className="stat-card bg-white/95 dark:bg-slate-800/95 backdrop-blur-md p-6 rounded-2xl shadow-lg transform hover:scale-105 transition-transform duration-200">
                    <div className="stat-value text-2xl font-bold text-blue-700 dark:text-blue-400">{nutritionData.protein}g</div>
                    <div className="stat-label text-sm text-slate-900 dark:text-slate-100 mt-2 font-medium">Protein</div>
                  </div>
                  <div className="stat-card bg-white/95 dark:bg-slate-800/95 backdrop-blur-md p-6 rounded-2xl shadow-lg transform hover:scale-105 transition-transform duration-200">
                    <div className="stat-value text-2xl font-bold text-yellow-700 dark:text-yellow-400">{nutritionData.carbs}g</div>
                    <div className="stat-label text-sm text-slate-900 dark:text-slate-100 mt-2 font-medium">Carbs</div>
                  </div>
                  <div className="stat-card bg-white/95 dark:bg-slate-800/95 backdrop-blur-md p-6 rounded-2xl shadow-lg transform hover:scale-105 transition-transform duration-200">
                    <div className="stat-value text-2xl font-bold text-red-700 dark:text-red-400">{nutritionData.fat}g</div>
                    <div className="stat-label text-sm text-slate-900 dark:text-slate-100 mt-2 font-medium">Fat</div>
                  </div>
                </div>

                {/* Content Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Left Column */}
                  <div className="space-y-4">
                    {/* Macronutrient Distribution */}
                    <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-md rounded-2xl p-6 shadow-lg">
                      <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">
                        Macronutrient Distribution
                      </h3>
                      <div className="flex items-center justify-between">
                        <div className="macro-ring-container relative w-40 h-40">
                          <svg className="w-full h-full -rotate-90 relative z-10" viewBox="0 0 100 100">
                            {/* Background circle */}
                            <circle
                              cx="50"
                              cy="50"
                              r="45"
                              fill="none"
                              stroke="#e5e7eb"
                              strokeWidth="10"
                              className="dark:stroke-gray-700"
                            />
                            
                            {(() => {
                              const circumference = 2 * Math.PI * 45;
                              const gap = 1; // Small gap between segments
                              
                              // Calculate stroke lengths and positions
                              const proteinLength = (circumference * nutritionData.proteinPercentage / 100) - gap;
                              const carbsLength = (circumference * nutritionData.carbsPercentage / 100) - gap;
                              const fatLength = (circumference * nutritionData.fatPercentage / 100) - gap;
                              
                              // Calculate starting positions
                              const proteinStart = 0;
                              const carbsStart = proteinLength + gap;
                              const fatStart = carbsStart + carbsLength + gap;
                              
                              return (
                                <>
                                  {/* Fat segment (drawn first as it's largest) */}
                                  <circle
                                    cx="50"
                                    cy="50"
                                    r="45"
                                    fill="none"
                                    stroke="#EF4444"
                                    strokeWidth="10"
                                    strokeDasharray={`${fatLength} ${circumference - fatLength}`}
                                    strokeDashoffset={-fatStart}
                                    className="macro-ring"
                                  />
                                  
                                  {/* Carbs segment */}
                                  <circle
                                    cx="50"
                                    cy="50"
                                    r="45"
                                    fill="none"
                                    stroke="#EAB308"
                                    strokeWidth="10"
                                    strokeDasharray={`${carbsLength} ${circumference - carbsLength}`}
                                    strokeDashoffset={-carbsStart}
                                    className="macro-ring"
                                  />
                                  
                                  {/* Protein segment */}
                                  <circle
                                    cx="50"
                                    cy="50"
                                    r="45"
                                    fill="none"
                                    stroke="#3B82F6"
                                    strokeWidth="10"
                                    strokeDasharray={`${proteinLength} ${circumference - proteinLength}`}
                                    strokeDashoffset={-proteinStart}
                                    className="macro-ring"
                                  />
                                </>
                              );
                            })()}
                          </svg>
                          
                          {/* Center text */}
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-gray-800 dark:text-white">
                                {nutritionData.calories}
                              </div>
                              <div className="text-sm text-gray-600 dark:text-gray-300">
                                calories
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex flex-col gap-3 ml-4">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                            <span className="text-sm font-medium">Protein {nutritionData.proteinPercentage}%</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                            <span className="text-sm font-medium">Carbs {nutritionData.carbsPercentage}%</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-red-500"></div>
                            <span className="text-sm font-medium">Fat {nutritionData.fatPercentage}%</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Allergens */}
                    {nutritionData.allergens && nutritionData.allergens.length > 0 && (
                      <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-md rounded-2xl p-6 shadow-lg mt-4">
                        <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200 flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                          Allergen Information
                        </h3>
                        <div className="space-y-3">
                          <div className="flex flex-wrap gap-2">
                            {nutritionData.allergens.map((allergen, index) => (
                              <div
                                key={index}
                                className={`flex items-center ${
                                  allergen.definite 
                                    ? 'bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-100 border-red-200 dark:border-red-800' 
                                    : 'bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-100 border-yellow-200 dark:border-yellow-800'
                                } px-3 py-1.5 rounded-lg border shadow-sm`}
                              >
                                <span className="font-medium text-sm">
                                  {allergen.name}
                                </span>
                              </div>
                            ))}
                          </div>
                          {nutritionData.allergens.some(a => a.definite) && (
                            <div className="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg flex items-start">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              <p>This item contains confirmed allergens. Please exercise caution if you have known allergies or sensitivities to any of the listed ingredients.</p>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Right Column */}
                  <div className="space-y-4">
                    {/* Health Benefits */}
                    {nutritionData.health_benefits && nutritionData.health_benefits.length > 0 && (
                      <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-md rounded-2xl p-6 shadow-lg">
                        <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200 flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Health Benefits
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {nutritionData.health_benefits.map((benefit, index) => (
                            <span
                              key={index}
                              className="px-3 py-1.5 bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-100 rounded-lg text-sm font-medium"
                            >
                              {benefit}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Acidity Level */}
                    {nutritionData.acidity_level && (
                      <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-md rounded-2xl p-6 shadow-lg mt-4">
                        <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200 flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                          </svg>
                          Acidity Level
                        </h3>
                        <div className="flex items-center justify-between">
                          <div className="relative w-32 h-32">
                            <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                              <circle
                                cx="50"
                                cy="50"
                                r="45"
                                fill="none"
                                stroke="#e5e7eb"
                                strokeWidth="10"
                                className="dark:stroke-gray-700"
                              />
                              <circle
                                cx="50"
                                cy="50"
                                r="45"
                                fill="none"
                                stroke={
                                  nutritionData.acidity_level < 4.5 ? '#EF4444' :
                                  nutritionData.acidity_level < 5.5 ? '#F59E0B' : '#10B981'
                                }
                                strokeWidth="10"
                                strokeDasharray={`${2 * Math.PI * 45} ${2 * Math.PI * 45}`}
                                strokeDashoffset={2 * Math.PI * 45 * (1 - nutritionData.acidity_level / 14)}
                                className="transition-all duration-500"
                              />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                              <div className={`text-3xl font-bold ${
                                nutritionData.acidity_level < 4.5 ? 'text-red-500' :
                                nutritionData.acidity_level < 5.5 ? 'text-yellow-500' : 'text-green-500'
                              }`}>
                                {nutritionData.acidity_level.toFixed(1)}
                              </div>
                              <div className="text-sm text-gray-600 dark:text-gray-400">
                                pH
                              </div>
                            </div>
                          </div>
                          <div className="ml-6 flex-1">
                            <div className={`text-lg font-semibold mb-2 ${
                              nutritionData.acidity_level < 4.5 ? 'text-red-500' :
                              nutritionData.acidity_level < 5.5 ? 'text-yellow-500' : 'text-green-500'
                            }`}>
                              {nutritionData.acidity_level < 4.5 ? 'High Acidity' :
                               nutritionData.acidity_level < 5.5 ? 'Medium Acidity' : 'Low Acidity'}
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
                              {nutritionData.acidity_level < 4.5 ? 
                                'May cause digestive sensitivity. Consider consuming in moderation, especially if you have acid reflux or gastric concerns.' :
                               nutritionData.acidity_level < 5.5 ? 
                                'Moderate acidity level that most people can tolerate well. Generally safe for regular consumption.' :
                                'Gentle on the digestive system. Suitable for most dietary preferences and those with acid sensitivity.'}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}