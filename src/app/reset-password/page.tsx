'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';

export default function ResetPassword() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Get token and email from URL parameters
  const token = searchParams?.get('token');
  const email = searchParams?.get('email');

  useEffect(() => {
    if (!token || !email) {
      setError('Invalid reset link. Please request a new password reset.');
    }
  }, [token, email]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setIsLoading(true);

    // Validate inputs
    if (!token || !email) {
      setError('Invalid reset link. Please request a new password reset.');
      setIsLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          email,
          password
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to reset password');
      }

      // Store authentication token if provided
      if (data.token) {
        sessionStorage.setItem('authToken', data.token);
        sessionStorage.setItem('userEmail', email);
      }

      setMessage('Password has been reset successfully. Redirecting to home page...');
      
      // Redirect after successful reset
      setTimeout(() => {
        router.push('/');
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset password');
    } finally {
      setIsLoading(false);
    }
  };

  if (!token || !email) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F4FFF4] p-4">
        <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-lg">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-[#8B4513] mb-2">Invalid Reset Link</h1>
            <p className="text-gray-600">Please request a new password reset.</p>
            <div className="mt-4">
              <Link href="/forgot-password" className="text-[#0B4A0B] hover:text-[#083708]">
                Go to Forgot Password
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F4FFF4] p-4">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-lg">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-[#8B4513] mb-2">Reset Password</h1>
          <p className="text-gray-600">Enter your new password</p>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <div>
            <label htmlFor="password" className="block text-gray-700">New Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
              required
              disabled={isLoading}
              minLength={6}
              suppressHydrationWarning
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-gray-700">Confirm New Password</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
              required
              disabled={isLoading}
              minLength={6}
              suppressHydrationWarning
            />
          </div>

          {error && (
            <div className="text-red-500 text-sm bg-red-50 p-3 rounded-md">
              {error}
            </div>
          )}

          {message && (
            <div className="text-green-500 text-sm bg-green-50 p-3 rounded-md">
              {message}
            </div>
          )}

          <button
            type="submit"
            className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-[#0B4A0B] hover:bg-[#083708] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
            disabled={isLoading}
            suppressHydrationWarning
          >
            {isLoading ? 'Resetting Password...' : 'Reset Password'}
          </button>

          <div className="text-center text-gray-600">
            Remember your password?{' '}
            <Link href="/login" className="text-[#8B4513] hover:text-[#5C2D0C]">
              Sign in
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
} 