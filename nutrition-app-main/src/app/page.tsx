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
  proteinPercentage?: number;
  carbsPercentage?: number;
  fatPercentage?: number;
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

  useEffect(() => {
    let isMounted = true;
    let attempts = 0;
    const maxAttempts = 3;

    const verifyAuth = async () => {
      const token = localStorage.getItem('authToken');
      if (!token) {
        if (isMounted) {
          router.replace('/login');
        }
        return;
      }

      try {
        const response = await fetch('http://localhost:5000/api/auth/verify', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });

        const data = await response.json();

        if (response.ok && data.authenticated) {
          if (isMounted) {
            setMounted(true);
            setIsLoading(false);
          }
        } else {
          throw new Error(data.error || 'Not authenticated');
        }
      } catch (error) {
        console.error('Auth error:', error);
        if (attempts < maxAttempts) {
          attempts++;
          await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
          await verifyAuth(); // Retry
        } else {
          localStorage.removeItem('authToken');
          localStorage.removeItem('userEmail');
          if (isMounted) {
            router.replace('/login');
          }
        }
      }
    };

    verifyAuth();

    return () => {
      isMounted = false;
    };
  }, [router]);

  if (!mounted || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-green-800 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  // ... rest of your component code ...
} 