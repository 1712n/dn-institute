'use client';

import React from 'react';

export default function SocialShare({ textToShare }: { textToShare: string }) {
  const handleShare = () => {
    // Dynamically grab the window location origin if it's deployed, or fallback
    const appUrl = typeof window !== 'undefined' ? window.location.origin : 'https://devexcuse-generator.vercel.app';
    const tweetText = encodeURIComponent(`I just used the DevExcuse Generator: "${textToShare}"\n\nGenerate yours here: ${appUrl}`);
    const twitterUrl = `https://twitter.com/intent/tweet?text=${tweetText}`;
    window.open(twitterUrl, '_blank');
  };

  return (
    <button 
      onClick={handleShare}
      className="mt-4 px-4 py-2 bg-black text-white rounded-md hover:bg-gray-800 transition-colors flex items-center gap-2 font-medium"
      aria-label="Share on X"
    >
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.008 5.964H5.078z" />
      </svg>
      Share on X
    </button>
  );
}