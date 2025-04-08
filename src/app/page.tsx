'use client';

import { useState, useEffect } from 'react';
import { SearchResult } from '@/types';
import Image from 'next/image';
import { FormEvent } from 'react';

interface FoodItem {
  name: string;
  serving_size: number;
  serving_unit: string;
  [key: string]: any;  // For other properties we might not use
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
  const [searchQuery, setSearchQuery] = useState('');

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

  const fetchSuggestions = async (searchQuery: string) => {
    if (!searchQuery) {
      setSuggestions([]);
      return;
    }
    
    try {
      const response = await fetch(
        `http://localhost:5000/api/search?query=${encodeURIComponent(searchQuery.toLowerCase())}`
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
  };

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // Remove any size indicators from the query
      const cleanQuery = foodQuery.replace(/\s*\((Small|Medium|Large)\)/g, '');
      const response = await fetch(
        `http://localhost:5000/api/nutrition?query=${encodeURIComponent(cleanQuery)}&quantity=${quantity}&unit=${unit}`
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
      
      {/* Content Container with backdrop blur */}
      <div className="relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Enhanced Header with backdrop */}
          <div className="text-center mb-12 animate-fade-in bg-white/95 dark:bg-slate-900/95 backdrop-blur-md rounded-2xl p-8 shadow-xl">
            <h1 className="text-5xl md:text-6xl font-extrabold mb-4 bg-gradient-to-r from-amber-950 via-amber-800 to-amber-700 bg-clip-text text-transparent drop-shadow-[0_2px_2px_rgba(120,53,15,0.3)] tracking-tight font-serif">
              NutriSmart
            </h1>
            <p className="text-lg md:text-xl font-medium tracking-wide bg-gradient-to-r from-slate-800 to-slate-600 dark:from-slate-200 dark:to-slate-300 bg-clip-text text-transparent transition-all duration-300 ease-in-out hover:tracking-wider font-sans">
              Make informed choices with instant nutritional insights
            </p>
          </div>

          {/* Search Section with stronger backdrop */}
          <div className="space-y-8">
            <form onSubmit={handleSearch} className="search-container p-6 rounded-2xl shadow-lg bg-white/95 dark:bg-slate-800/95 backdrop-blur-lg border border-amber-100 dark:border-amber-900/20">
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px] relative">
                  <input
                    type="text"
                    value={foodQuery}
                    onChange={handleQueryChange}
                    onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                    placeholder="Search for any food..."
                    className="input-modern w-full rounded-xl border-amber-200 dark:border-amber-900/30 focus:border-amber-500 dark:focus:border-amber-700 focus:ring-amber-500 dark:focus:ring-amber-700"
                    required
                  />
                  
                  {suggestions.length > 0 && showSuggestions && (
                    <div className="search-results absolute z-20 w-full mt-2 max-h-60 overflow-y-auto rounded-lg shadow-xl">
                      {suggestions.map((suggestion, index) => (
                        <div
                          key={index}
                          className="search-result-item hover:bg-slate-100 dark:hover:bg-slate-700"
                          onClick={() => handleSuggestionClick(suggestion)}
                        >
                          <span className="font-medium text-primary">{suggestion.name}</span>
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            (100 {isLiquidFood(suggestion.name) ? 'ml' : 'g'})
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div className="w-24">
                  <input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    className="quantity-input"
                    min="1"
                    required
                  />
                </div>
                <div className="w-24">
                  <select
                    value={unit}
                    onChange={(e) => setUnit(e.target.value)}
                    className="unit-select"
                  >
                    <option value={isLiquidFood(foodQuery) ? 'ml' : 'g'}>
                      {isLiquidFood(foodQuery) ? 'ml' : 'g'}
                    </option>
                    <option value="oz">ounces</option>
                  </select>
                </div>
              <button
                type="submit"
                className="px-8 py-3 bg-green-800 hover:bg-green-900 text-white font-bold rounded-lg shadow-lg transition-all duration-200 hover:scale-105 focus:ring-4 focus:ring-green-700 focus:ring-opacity-50"
              >
                {loading ? (
                  <div className="w-6 h-6 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto" />
                ) : (
                  'Get Nutrition'
                )}
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
                    <div className="stat-value text-4xl font-bold text-amber-600 dark:text-amber-400">{nutritionData.calories}</div>
                    <div className="stat-label text-base text-gray-600 dark:text-gray-300 mt-2">Calories</div>
                  </div>
                  <div className="stat-card bg-white/95 dark:bg-slate-800/95 backdrop-blur-md p-6 rounded-2xl shadow-lg transform hover:scale-105 transition-transform duration-200">
                    <div className="stat-value text-4xl font-bold text-blue-600 dark:text-blue-400">{nutritionData.protein}g</div>
                    <div className="stat-label text-base text-gray-600 dark:text-gray-300 mt-2">Protein</div>
                  </div>
                  <div className="stat-card bg-white/95 dark:bg-slate-800/95 backdrop-blur-md p-6 rounded-2xl shadow-lg transform hover:scale-105 transition-transform duration-200">
                    <div className="stat-value text-4xl font-bold text-yellow-600 dark:text-yellow-400">{nutritionData.carbs}g</div>
                    <div className="stat-label text-base text-gray-600 dark:text-gray-300 mt-2">Carbs</div>
                  </div>
                  <div className="stat-card bg-white/95 dark:bg-slate-800/95 backdrop-blur-md p-6 rounded-2xl shadow-lg transform hover:scale-105 transition-transform duration-200">
                    <div className="stat-value text-4xl font-bold text-red-600 dark:text-red-400">{nutritionData.fat}g</div>
                    <div className="stat-label text-base text-gray-600 dark:text-gray-300 mt-2">Fat</div>
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

function getDefaultPH(foodName: string): number | null {
  switch(foodName.toLowerCase()) {
    // Burgers
    case 'classic hamburger':
    case 'hamburger':
      return 5.8;  // Hamburger pH 5.7-5.9
    case 'cheeseburger':
      return 5.8;  // Cheeseburger pH 5.7-5.9
    case 'double cheeseburger':
      return 5.8;  // Double cheeseburger pH 5.7-5.9
    case 'chicken burger':
      return 5.9;  // Chicken burger pH 5.8-6.0
    case 'veggie burger':
      return 5.7;  // Veggie burger pH 5.6-5.8

    // Pizza
    case 'margherita pizza':
    case 'pepperoni pizza':
    case 'pizza':
      return 4.5;  // Pizza pH 4.3-4.7 (due to tomato sauce)

    // Beverages
    case 'coffee':
    case 'black coffee':
      return 5.0;  // Black coffee pH 4.8-5.1
    case 'espresso':
      return 5.0;  // Espresso pH 4.8-5.2
    case 'cappuccino':
    case 'latte':
      return 6.2;  // Milk-based coffee pH 6.0-6.4
    case 'green tea':
      return 7.2;  // Green tea pH 7.0-7.4
    case 'black tea':
      return 6.0;  // Black tea pH 5.5-6.5
    case 'oolong tea':
      return 7.0;  // Oolong tea pH 6.8-7.2
    case 'chamomile tea':
      return 7.0;  // Chamomile tea pH 6.8-7.2
    case 'peppermint tea':
      return 7.0;  // Peppermint tea pH 6.8-7.2
    case 'rooibos tea':
      return 6.8;  // Rooibos tea pH 6.6-7.0
    case 'herbal tea':
      return 7.0;  // Most herbal teas pH 6.8-7.2
    case 'americano':
      return 5.0;  // Similar to black coffee
    case 'orange juice':
      return 3.5;  // Orange juice pH 3.3-3.7
    case 'apple juice':
      return 3.8;  // Apple juice pH 3.5-4.0
    case 'milk':
      return 6.7;  // Milk pH 6.5-6.7
    case 'coca cola':
    case 'coke':
    case 'pepsi':
      return 2.5;  // Cola drinks pH 2.3-2.7

    // Indian Dishes
    case 'butter chicken':
    case 'murgh makhani':
      return 4.8;  // Butter chicken pH 4.6-5.0
    case 'chicken tikka masala':
      return 5.8;  // Tikka masala pH 5.5-6.0
    case 'chicken tikka':
      return 5.0;  // Chicken tikka pH 4.8-5.2
    case 'curry':
    case 'indian curry':
      return 5.9;  // Generic curry pH 5.7-6.1
    case 'dal':
    case 'daal':
    case 'lentils':
      return 6.3;  // Cooked lentils pH 6.0-6.5
    case 'masala dosa':
      return 5.2;  // Masala dosa pH 5.0-5.4
    case 'idli':
      return 5.0;  // Idli pH 4.8-5.2
    case 'sambar':
      return 4.8;  // Sambar pH 4.6-5.0
    case 'palak paneer':
      return 5.2;  // Palak paneer pH 5.0-5.4

    // Mexican Dishes
    case 'chicken burrito':
      return 5.5;  // Chicken burrito pH 5.3-5.7
    case 'chicken quesadilla':
      return 5.4;  // Chicken quesadilla pH 5.2-5.6

    // Pasta Dishes
    case 'spaghetti with meat sauce':
      return 5.2;  // Spaghetti with meat sauce pH 5.0-5.4
    case 'fettuccine alfredo':
      return 5.4;  // Fettuccine alfredo pH 5.2-5.6

    // Asian Dishes
    case 'pad thai':
      return 5.0;  // Pad thai pH 4.8-5.2
    case 'chicken fried rice':
      return 5.2;  // Chicken fried rice pH 5.0-5.4

    // Common Foods
    case 'rice':
    case 'white rice':
    case 'brown rice':
      return 6.8;  // Cooked rice pH 6.5-7.0
    case 'chicken':
    case 'cooked chicken':
      return 6.5;  // Cooked chicken pH 6.3-6.7
    case 'yogurt':
      return 4.4;  // Regular yogurt pH 4.2-4.6
    case 'bread':
      return 5.7;  // Bread pH 5.3-5.8
    case 'tomato':
      return 4.3;  // Fresh tomato pH 4.0-4.6
    case 'banana':
      return 4.8;  // Banana pH 4.5-5.2
    case 'apple':
      return 3.5;  // Apple pH 3.3-3.9
    case 'beef':
    case 'cooked beef':
      return 5.8;  // Cooked beef pH 5.7-6.0
    case 'egg':
    case 'boiled egg':
      return 7.6;  // Boiled egg pH 7.4-7.8

    // Dairy Products
    case 'greek yogurt':
    case 'greek yoghurt':
      return 4.3;  // Greek yogurt pH 4.2-4.4 (more acidic due to straining)
    case 'cottage cheese':
      return 5.0;  // Cottage cheese pH 4.8-5.2
    case 'cream cheese':
      return 4.4;  // Cream cheese pH 4.3-4.5
    case 'cheddar cheese':
      return 5.3;  // Cheddar cheese pH 5.2-5.4
    case 'mozzarella':
    case 'mozzarella cheese':
      return 5.2;  // Mozzarella pH 5.1-5.3
    case 'butter':
      return 6.1;  // Butter pH 6.0-6.2
    case 'sour cream':
      return 4.5;  // Sour cream pH 4.4-4.6
    case 'ice cream':
      return 6.3;  // Ice cream pH 6.2-6.4

    // Fruits
    case 'lemon':
      return 2.0;  // Lemon pH 1.8-2.3
    case 'lime':
      return 2.2;  // Lime pH 2.0-2.4
    case 'grapefruit':
      return 3.0;  // Grapefruit pH 2.9-3.3
    case 'orange':
      return 3.5;  // Orange pH 3.3-3.7
    case 'strawberry':
      return 3.0;  // Strawberry pH 2.8-3.2
    case 'blueberry':
      return 3.2;  // Blueberry pH 3.0-3.4
    case 'raspberry':
      return 3.2;  // Raspberry pH 3.0-3.4
    case 'pineapple':
      return 3.5;  // Pineapple pH 3.3-3.7
    case 'mango':
      return 3.4;  // Mango pH 3.2-3.6
    case 'pear':
      return 3.5;  // Pear pH 3.3-3.7

    // Vegetables
    case 'carrot':
      return 5.9;  // Carrot pH 5.7-6.1
    case 'potato':
      return 5.6;  // Potato pH 5.4-5.8
    case 'broccoli':
      return 6.3;  // Broccoli pH 6.1-6.5
    case 'cauliflower':
      return 6.5;  // Cauliflower pH 6.3-6.7
    case 'spinach':
      return 5.5;  // Spinach pH 5.3-5.7
    case 'lettuce':
      return 6.0;  // Lettuce pH 5.8-6.2
    case 'cucumber':
      return 5.1;  // Cucumber pH 4.9-5.3
    case 'bell pepper':
      return 4.8;  // Bell pepper pH 4.6-5.0
    case 'onion':
      return 5.3;  // Onion pH 5.1-5.5
    case 'garlic':
      return 5.8;  // Garlic pH 5.6-6.0

    // Seafood
    case 'salmon':
      return 6.2;  // Salmon pH 6.0-6.4
    case 'tuna':
      return 6.0;  // Tuna pH 5.8-6.2
    case 'shrimp':
      return 6.5;  // Shrimp pH 6.3-6.7
    case 'cod':
      return 6.2;  // Cod pH 6.0-6.4
    case 'tilapia':
      return 6.3;  // Tilapia pH 6.1-6.5

    // Nuts and Seeds
    case 'almond':
      return 5.4;  // Almond pH 5.2-5.6
    case 'walnut':
      return 5.4;  // Walnut pH 5.2-5.6
    case 'cashew':
      return 5.9;  // Cashew pH 5.7-6.1
    case 'peanut':
      return 6.3;  // Peanut pH 6.1-6.5
    case 'sunflower seed':
      return 6.0;  // Sunflower seed pH 5.8-6.2

    // Grains and Cereals
    case 'oatmeal':
      return 5.9;  // Oatmeal pH 5.7-6.1
    case 'quinoa':
      return 6.0;  // Quinoa pH 5.8-6.2
    case 'barley':
      return 5.8;  // Barley pH 5.6-6.0
    case 'wheat':
      return 6.0;  // Wheat pH 5.8-6.2
    case 'corn':
      return 6.0;  // Corn pH 5.8-6.2

    // Legumes
    case 'black bean':
      return 6.0;  // Black bean pH 5.8-6.2
    case 'kidney bean':
      return 6.0;  // Kidney bean pH 5.8-6.2
    case 'chickpea':
      return 6.0;  // Chickpea pH 5.8-6.2
    case 'lentil':
      return 6.3;  // Lentil pH 6.1-6.5
    case 'soybean':
      return 6.5;  // Soybean pH 6.3-6.7

    // Processed Foods
    case 'ketchup':
      return 3.9;  // Ketchup pH 3.7-4.1
    case 'mustard':
      return 3.5;  // Mustard pH 3.3-3.7
    case 'mayonnaise':
      return 4.2;  // Mayonnaise pH 4.0-4.4
    case 'soy sauce':
      return 4.8;  // Soy sauce pH 4.6-5.0
    case 'vinegar':
      return 2.4;  // Vinegar pH 2.2-2.6

    default:
      // For any unknown item, return a reasonable default based on food category
      const lowerName = foodName.toLowerCase();
      
      // Beverages
      if (lowerName.includes('tea')) {
        return 7.0;  // Default tea pH
      }
      if (lowerName.includes('coffee')) {
        return 5.0;  // Default coffee pH
      }
      if (lowerName.includes('juice')) {
        return 3.8;  // Default juice pH
      }
      if (lowerName.includes('soda') || lowerName.includes('soft drink')) {
        return 2.5;  // Default soda pH
      }
      if (lowerName.includes('smoothie')) {
        return 4.5;  // Default smoothie pH
      }
      if (lowerName.includes('milk') || lowerName.includes('shake')) {
        return 6.7;  // Default milk pH
      }

      // Dairy and alternatives
      if (lowerName.includes('yogurt') || lowerName.includes('yoghurt')) {
        return 4.4;  // Default yogurt pH
      }
      if (lowerName.includes('cheese')) {
        return 5.2;  // Default cheese pH
      }
      if (lowerName.includes('cream')) {
        return 6.5;  // Default cream pH
      }
      if (lowerName.includes('butter')) {
        return 6.1;  // Default butter pH
      }

      // Proteins
      if (lowerName.includes('chicken') || lowerName.includes('poultry')) {
        return 6.5;  // Default chicken pH
      }
      if (lowerName.includes('beef') || lowerName.includes('steak')) {
        return 5.8;  // Default beef pH
      }
      if (lowerName.includes('pork')) {
        return 6.0;  // Default pork pH
      }
      if (lowerName.includes('lamb')) {
        return 6.0;  // Default lamb pH
      }
      if (lowerName.includes('fish') || lowerName.includes('seafood')) {
        return 6.2;  // Default seafood pH
      }
      if (lowerName.includes('egg')) {
        return 7.6;  // Default egg pH
      }

      // Vegetables
      if (lowerName.includes('vegetable') || lowerName.includes('veg')) {
        return 5.5;  // Default vegetable pH
      }
      if (lowerName.includes('salad')) {
        return 5.5;  // Default salad pH
      }
      if (lowerName.includes('soup')) {
        return 5.0;  // Default soup pH
      }

      // Fruits
      if (lowerName.includes('fruit')) {
        return 3.5;  // Default fruit pH
      }
      if (lowerName.includes('berry') || lowerName.includes('berries')) {
        return 3.2;  // Default berries pH
      }
      if (lowerName.includes('citrus')) {
        return 2.5;  // Default citrus pH
      }

      // Grains and starches
      if (lowerName.includes('bread') || lowerName.includes('toast')) {
        return 5.7;  // Default bread pH
      }
      if (lowerName.includes('pasta') || lowerName.includes('noodle')) {
        return 5.8;  // Default pasta pH
      }
      if (lowerName.includes('rice')) {
        return 6.8;  // Default rice pH
      }
      if (lowerName.includes('grain') || lowerName.includes('cereal')) {
        return 6.0;  // Default grain pH
      }

      // Legumes and nuts
      if (lowerName.includes('bean') || lowerName.includes('legume')) {
        return 6.0;  // Default beans pH
      }
      if (lowerName.includes('nut') || lowerName.includes('seed')) {
        return 5.8;  // Default nuts/seeds pH
      }

      // Snacks and processed foods
      if (lowerName.includes('chip') || lowerName.includes('crisp')) {
        return 5.5;  // Default chips pH
      }
      if (lowerName.includes('candy') || lowerName.includes('sweet')) {
        return 4.5;  // Default candy pH
      }
      if (lowerName.includes('chocolate')) {
        return 6.0;  // Default chocolate pH
      }
      if (lowerName.includes('sauce')) {
        return 4.5;  // Default sauce pH
      }
      if (lowerName.includes('dressing')) {
        return 4.0;  // Default dressing pH
      }

      // Cuisines
      if (lowerName.includes('pizza')) {
        return 4.5;  // Default pizza pH
      }
      if (lowerName.includes('burger')) {
        return 5.8;  // Default burger pH
      }
      if (lowerName.includes('sandwich')) {
        return 5.5;  // Default sandwich pH
      }
      if (lowerName.includes('curry')) {
        return 5.9;  // Default curry pH
      }
      if (lowerName.includes('sushi') || lowerName.includes('roll')) {
        return 4.8;  // Default sushi pH (due to vinegared rice)
      }

      // If nothing else matches, return a safe moderate pH
      return 6.0;  // Default moderate pH for unknown foods
  }
}