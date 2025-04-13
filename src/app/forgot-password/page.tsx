'use client';

import React, { useState } from 'react';
import Link from 'next/link';

interface ApiError {
  message: string;
  status?: number;
}

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState<ApiError | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to send reset email');
      }

      setMessage('If an account exists with this email, you will receive password reset instructions.');
    } catch (err: any) {
      setError({ message: err.message || 'Failed to send reset email. Please try again later.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F4FFF4] p-4">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-lg">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-[#8B4513] mb-2">Reset Password</h1>
          <p className="text-gray-600">Enter your email to receive reset instructions</p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email" className="block text-gray-700">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="youremail@example.com"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
              required
              disabled={isLoading}
              suppressHydrationWarning
            />
          </div>

          {error && (
            <div className="text-red-500 text-sm bg-red-50 p-3 rounded-md">
              {error.message}
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
            {isLoading ? 'Sending...' : 'Send Reset Instructions'}
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