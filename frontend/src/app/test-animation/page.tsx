'use client';

import { useState } from 'react';
import { AISearchAnimation } from '@/components/search/animation/AISearchAnimation';

export default function TestAnimationPage() {
  const [isSearching, setIsSearching] = useState(false);
  const [query, setQuery] = useState('approved housing in Manchester');

  const handleStartAnimation = () => {
    setIsSearching(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-[#10B981]/5 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 text-center">
          <div className="inline-block px-4 py-2 bg-[#10B981]/10 rounded-full mb-4">
            <span className="text-[#043F2E] font-semibold text-sm">ENHANCED UI/UX</span>
          </div>
          <h1 className="text-4xl font-bold text-[#043F2E] mb-3">
            AI Search Animation Test
          </h1>
          <p className="text-gray-600">Experience the modern, sleek animation design</p>
        </div>

        <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-xl border border-[#043F2E]/10 mb-8">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Test Query
          </label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4"
            placeholder="Enter search query..."
          />

          <button
            onClick={handleStartAnimation}
            disabled={isSearching}
            className="px-8 py-4 bg-gradient-to-r from-[#043F2E] to-[#065940] text-white rounded-xl hover:from-[#065940] hover:to-[#087952] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 font-semibold shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
          >
            {isSearching ? '✨ Animation Running...' : '🚀 Start Animation'}
          </button>
        </div>

        {/* Animation */}
        {isSearching && (
          <AISearchAnimation
            query={query}
            searchType="semantic"
            onComplete={() => {
              console.log('Animation complete!');
              setIsSearching(false);
              alert('Animation complete! Check console for details.');
            }}
            onCancel={() => {
              console.log('Animation cancelled');
              setIsSearching(false);
            }}
            onError={(error) => {
              console.error('Animation error:', error);
              alert(`Error: ${error.message}`);
            }}
          />
        )}

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100/50 p-6 rounded-xl border border-blue-200/50">
            <h2 className="font-bold text-blue-900 mb-3 flex items-center gap-2">
              <span className="text-2xl">📋</span> Instructions
            </h2>
            <ol className="text-sm text-blue-800 space-y-2">
              <li className="flex items-start gap-2">
                <span className="font-bold">1.</span>
                <span>Enter a search query above</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold">2.</span>
                <span>Click "Start Animation"</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold">3.</span>
                <span>Watch the enhanced 5-stage animation</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold">4.</span>
                <span>Try pressing <kbd className="px-2 py-1 bg-white rounded text-xs">ESC</kbd> to cancel</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold">5.</span>
                <span>Wait 8+ seconds for enhanced cancel button</span>
              </li>
            </ol>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100/50 p-6 rounded-xl border border-green-200/50">
            <h2 className="font-bold text-green-900 mb-3 flex items-center gap-2">
              <span className="text-2xl">✨</span> Enhanced Features
            </h2>
            <ul className="text-sm text-green-800 space-y-2">
              <li className="flex items-center gap-2">
                <span className="text-green-600">●</span>
                <span>Glassmorphism backdrop with blur</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-600">●</span>
                <span>Spring animations & smooth transitions</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-600">●</span>
                <span>Shimmer progress bar effect</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-600">●</span>
                <span>Modern gradient buttons</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-600">●</span>
                <span>Premium shadows & lighting</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-600">●</span>
                <span>Micro-interactions on hover/tap</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
