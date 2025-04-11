'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      console.log('Attempting login...');
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();
      console.log('Login response:', data);

      if (!response.ok) {
        throw new Error(data.error || 'Login failed');
      }

      if (data.token && data.authenticated) {
        console.log('Login successful, storing token...');
        // Store auth data
        sessionStorage.setItem('authToken', data.token);
        sessionStorage.setItem('userEmail', email);
        
        // Navigate to home page using router
        console.log('Navigating to home page...');
        window.location.replace('http://localhost:3000');
      } else {
        throw new Error('Authentication failed');
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed. Please try again.');
      sessionStorage.removeItem('authToken');
      sessionStorage.removeItem('userEmail');
    } finally {
      setIsLoading(false);
    }
  };

  if (!mounted) {
    return null;
  }

  return (
    <form onSubmit={handleSubmit} className="mt-8 space-y-6">
      <div>
        <label htmlFor="email" className="block text-gray-700">Email</label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="youremail@example.com"
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
          required
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-gray-700">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
          required
          disabled={isLoading}
        />
      </div>

      {error && (
        <div className="text-red-500 text-sm">{error}</div>
      )}

      <div className="text-right">
        <Link href="/forgot-password" className="text-[#8B4513] hover:text-[#5C2D0C]">
          Forgot password?
        </Link>
      </div>

      <button
        type="submit"
        className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-[#0B4A0B] hover:bg-[#083708] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
        disabled={isLoading}
      >
        {isLoading ? 'Signing in...' : 'Sign In'}
      </button>

      <div className="text-center text-gray-600">
        Don't have an account?{' '}
        <Link href="/signup" className="text-[#8B4513] hover:text-[#5C2D0C]">
          Sign up
        </Link>
      </div>
    </form>
  );
}

export default function Login() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F4FFF4] p-4">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F4FFF4] p-4">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-lg">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-[#8B4513] mb-2">NutriSmart</h1>
          <p className="text-gray-600">Make informed choices with instant nutritional insights</p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
} 