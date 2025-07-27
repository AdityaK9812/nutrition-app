'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

interface NutritionData {
  name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  proteinPercentage: number;
  carbsPercentage: number;
  fatPercentage: number;
  acidity_level: number;
  health_benefits: string[];
  allergens: Array<{
    name: string;
    definite: boolean;
  }>;
}

interface FoodItem {
  name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
}

export default function Home() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [foodQuery, setFoodQuery] = useState('');
  const [quantity, setQuantity] = useState('100');
  const [unit, setUnit] = useState('g');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [nutritionData, setNutritionData] = useState<NutritionData | null>(null);
  const [suggestions, setSuggestions] = useState<FoodItem[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const checkAuth = async () => {
      const token = sessionStorage.getItem('authToken');
      if (!token) {
        router.push('/login');
        return;
      }

      try {
        // Verify token with backend
        const response = await fetch('http://localhost:5000/api/auth/verify', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Invalid token');
        }

        setIsAuthenticated(true);
        setIsLoading(false);
      } catch (error) {
        console.error('Auth verification failed:', error);
        sessionStorage.removeItem('authToken');
        sessionStorage.removeItem('userEmail');
        router.push('/login');
      }
    };

    checkAuth();
  }, [router]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const token = sessionStorage.getItem('authToken');
      if (!token) {
        throw new Error('Not authenticated');
      }

      const cleanQuery = foodQuery.trim();
      console.log('[Search] Starting search for:', cleanQuery);
      console.log('[Search] Parameters:', { quantity, unit });
      
      const url = `http://localhost:5000/api/nutrition?query=${encodeURIComponent(cleanQuery)}&quantity=${quantity}&unit=${unit}`;
      console.log('[Search] Request URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('[Search] Response status:', response.status);
      const data = await response.json();
      console.log('[Search] Raw response data:', data);

      if (!response.ok) {
        if (response.status === 401) {
          console.log('[Search] Authentication error - redirecting to login');
          sessionStorage.removeItem('authToken');
          router.push('/login');
          throw new Error('Session expired. Please login again.');
        }
        throw new Error(data.error || 'Failed to fetch nutrition data');
      }

      console.log('[Search] Processing response data...');
      console.log('[Search] Health Benefits:', data.health_benefits);
      console.log('[Search] Allergens:', data.allergens);
      console.log('[Search] Acidity Level:', data.acidity_level);

      // Calculate macronutrient percentages if not provided
      const totalCaloriesFromMacros = (data.protein * 4) + (data.carbs * 4) + (data.fat * 9);
      const proteinPercentage = Math.round((data.protein * 4 / totalCaloriesFromMacros) * 100);
      const carbsPercentage = Math.round((data.carbs * 4 / totalCaloriesFromMacros) * 100);
      const fatPercentage = Math.round((data.fat * 9 / totalCaloriesFromMacros) * 100);

      console.log('[Search] Calculated percentages:', { proteinPercentage, carbsPercentage, fatPercentage });

      // Ensure all required fields are present with proper defaults
      const processedData: NutritionData = {
        ...data,
        proteinPercentage,
        carbsPercentage,
        fatPercentage,
        health_benefits: Array.isArray(data.health_benefits) ? data.health_benefits : [],
        allergens: Array.isArray(data.allergens) ? data.allergens : [],
        acidity_level: typeof data.acidity_level === 'number' ? data.acidity_level : 7.0
      };

      console.log('[Search] Final processed data:', processedData);
      console.log('[Search] Setting nutrition data in state...');

      setNutritionData(processedData);
      console.log('[Search] State updated with new data');
    } catch (err) {
      console.error('[Search] Error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
      if (err instanceof Error && err.message === 'Not authenticated') {
        router.push('/login');
      }
    } finally {
      setLoading(false);
      setShowSuggestions(false);
      console.log('[Search] Search operation completed');
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem('authToken');
    sessionStorage.removeItem('userEmail');
    router.replace('/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
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
      
      {/* Logout Button */}
      <div className="absolute top-4 right-4 z-50">
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Logout
        </button>
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

          {/* Search Section */}
          <div className="space-y-4 sm:space-y-8">
            <form onSubmit={handleSearch} className="search-container mx-2 sm:mx-0 p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-lg bg-white/95 dark:bg-slate-800/95 backdrop-blur-lg">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1 min-w-0">
                  <input
                    type="text"
                    value={foodQuery}
                    onChange={(e) => setFoodQuery(e.target.value)}
                    placeholder="Search for any food..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    required
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    min="0"
                    required
                  />
                  <select
                    value={unit}
                    onChange={(e) => setUnit(e.target.value)}
                    className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
                    required
                  >
                    <option value="g">g</option>
                    <option value="ml">ml</option>
                  </select>
                  <button
                    type="submit"
                    className="px-6 py-2 bg-[#0B4A0B] text-white rounded-md hover:bg-[#083708] focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors"
                    disabled={loading}
                  >
                    {loading ? 'Searching...' : 'Get Nutrition'}
                  </button>
                </div>
              </div>
            </form>

            {error && (
              <div className="text-red-600 dark:text-red-400 text-sm font-medium px-4 py-2 bg-red-100 dark:bg-red-900/20 rounded-lg">
                {error}
              </div>
            )}

            {/* Results Section */}
            {nutritionData && (
              <div className="mt-8 space-y-6 animate-fade-in-up">
                {/* Food Name */}
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                    {nutritionData.name}
                  </h2>
                </div>

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
                          <div className="absolute inset-0">
                            <div className="w-full h-full rounded-full overflow-hidden">
                              <div 
                                className="absolute top-0 left-0 w-full h-full border-8 border-blue-500"
                                style={{
                                  clipPath: `polygon(50% 50%, -50% -50%, ${50 + 50 * Math.cos(-Math.PI/2 + 2*Math.PI*nutritionData.proteinPercentage/100)}% ${50 + 50 * Math.sin(-Math.PI/2 + 2*Math.PI*nutritionData.proteinPercentage/100)}%)`
                                }}
                              />
                              <div 
                                className="absolute top-0 left-0 w-full h-full border-8 border-yellow-500"
                                style={{
                                  clipPath: `polygon(50% 50%, ${50 + 50 * Math.cos(-Math.PI/2 + 2*Math.PI*nutritionData.proteinPercentage/100)}% ${50 + 50 * Math.sin(-Math.PI/2 + 2*Math.PI*nutritionData.proteinPercentage/100)}%, ${50 + 50 * Math.cos(-Math.PI/2 + 2*Math.PI*(nutritionData.proteinPercentage + nutritionData.carbsPercentage)/100)}% ${50 + 50 * Math.sin(-Math.PI/2 + 2*Math.PI*(nutritionData.proteinPercentage + nutritionData.carbsPercentage)/100)}%)`
                                }}
                              />
                              <div 
                                className="absolute top-0 left-0 w-full h-full border-8 border-red-500"
                                style={{
                                  clipPath: `polygon(50% 50%, ${50 + 50 * Math.cos(-Math.PI/2 + 2*Math.PI*(nutritionData.proteinPercentage + nutritionData.carbsPercentage)/100)}% ${50 + 50 * Math.sin(-Math.PI/2 + 2*Math.PI*(nutritionData.proteinPercentage + nutritionData.carbsPercentage)/100)}%, ${50 + 50 * Math.cos(-Math.PI/2 + 2*Math.PI)}% ${50 + 50 * Math.sin(-Math.PI/2 + 2*Math.PI)}%)`
                                }}
                              />
                            </div>
                            <div className="absolute inset-0 flex items-center justify-center">
                              <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                                {nutritionData.calories}
                                <div className="text-sm font-normal">calories</div>
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
                      <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-md rounded-2xl p-6 shadow-lg">
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
                    {nutritionData.acidity_level !== undefined && (
                      <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-md rounded-2xl p-6 shadow-lg">
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