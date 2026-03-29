'use client';

import { useState } from 'react';
import SocialShare from '../components/SocialShare';

export default function Home() {
  const [issue, setIssue] = useState('');
  const [excuse, setExcuse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateExcuse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!issue.trim()) return;

    setLoading(true);
    setExcuse('');
    setError('');

    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ issue }),
      });

      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.error || 'Failed to generate excuse');
      }
      
      if (data.result) {
        setExcuse(data.result);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Our servers are currently compiling the ultimate excuse. Please try again in a minute.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-2xl mx-auto p-8 font-sans min-h-screen flex flex-col justify-center">
      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
        <h1 className="text-4xl font-extrabold mb-3 text-gray-900 tracking-tight">DevExcuse Generator</h1>
        <p className="mb-8 text-lg text-gray-500">What broke? Let AI generate a highly technical excuse for your PM.</p>

        <form onSubmit={generateExcuse} className="flex flex-col gap-5">
          <div>
            <label htmlFor="issue" className="block text-sm font-medium text-gray-700 mb-1">The Bug / Issue</label>
            <input 
              id="issue"
              type="text" 
              value={issue}
              onChange={(e) => setIssue(e.target.value)}
              placeholder="e.g., The login button doesn't work"
              className="border border-gray-300 p-3 rounded-lg w-full focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none"
              required
            />
          </div>
          <button 
            type="submit" 
            disabled={loading || !issue.trim()}
            className="bg-blue-600 text-white p-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Generating...' : 'Generate Excuse'}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 bg-red-50 text-red-700 border border-red-200 rounded-lg">
            {error}
          </div>
        )}

        {excuse && !error && (
          <div className="mt-8 p-6 bg-gray-50 border border-gray-200 rounded-lg">
            <h2 className="text-sm uppercase tracking-wider font-semibold text-gray-500 mb-3">Your Excuse:</h2>
            <p className="text-xl font-medium text-gray-900 leading-relaxed">"{excuse}"</p>
            <div className="mt-4 border-t border-gray-200 pt-4">
              <SocialShare textToShare={excuse} />
            </div>
          </div>
        )}
      </div>
    </main>
  );
}