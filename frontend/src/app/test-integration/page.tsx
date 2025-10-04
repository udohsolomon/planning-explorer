'use client';

import { useState } from 'react';
import { AISearchAnimation } from '@/components/search/animation/AISearchAnimation';
import { SemanticSearchBar } from '@/components/ai/SemanticSearchBar';

export default function TestIntegrationPage() {
  const [showAnimation, setShowAnimation] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');
  const [searchType, setSearchType] = useState<'semantic' | 'keyword' | 'hybrid'>('semantic');
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
    console.log(message);
  };

  const handleSearch = async (query: string, type: 'traditional' | 'semantic' | 'natural_language') => {
    addLog(`🎯 handleSearch called: query="${query}", type="${type}"`);

    // Show animation for AI searches
    if (type === 'semantic' || type === 'natural_language') {
      addLog('✨ Showing animation');
      setShowAnimation(true);
      setCurrentQuery(query);
      setSearchType(type === 'semantic' ? 'semantic' : 'hybrid');

      // Simulate API call
      addLog('📡 Starting simulated API call...');
      await new Promise(resolve => setTimeout(resolve, 3000));
      addLog('✅ Simulated API call complete');
    } else {
      addLog('ℹ️ Skipping animation (traditional search)');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-[#10B981]/5 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-block px-4 py-2 bg-[#10B981]/10 rounded-full mb-4">
            <span className="text-[#043F2E] font-semibold text-sm">INTEGRATION TEST</span>
          </div>
          <h1 className="text-4xl font-bold text-[#043F2E] mb-3">
            Animation Integration Test
          </h1>
          <p className="text-gray-600">Test the SemanticSearchBar + AISearchAnimation integration</p>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <SemanticSearchBar
            placeholder="Try: 'approved housing in Manchester'"
            showSuggestions={false}
            showSearchType={true}
            onSearch={handleSearch}
            className="shadow-xl"
          />
        </div>

        {/* Status */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Current State */}
          <div className="bg-white p-6 rounded-xl shadow-lg border border-[#043F2E]/10">
            <h2 className="font-bold text-[#043F2E] mb-4 flex items-center gap-2">
              <span className="text-2xl">📊</span> Current State
            </h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Animation Visible:</span>
                <span className={`font-bold ${showAnimation ? 'text-green-600' : 'text-gray-400'}`}>
                  {showAnimation ? 'YES ✅' : 'NO'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Query:</span>
                <span className="font-mono text-xs">{currentQuery || '(none)'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Search Type:</span>
                <span className="font-semibold">{searchType}</span>
              </div>
            </div>
          </div>

          {/* Instructions */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100/50 p-6 rounded-xl border border-blue-200/50">
            <h2 className="font-bold text-blue-900 mb-3 flex items-center gap-2">
              <span className="text-2xl">📋</span> Test Steps
            </h2>
            <ol className="text-sm text-blue-800 space-y-2">
              <li className="flex items-start gap-2">
                <span className="font-bold">1.</span>
                <span>Select "Semantic" or "Natural Language"</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold">2.</span>
                <span>Enter any query</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold">3.</span>
                <span>Click Search</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold">4.</span>
                <span>Animation should appear!</span>
              </li>
            </ol>
          </div>
        </div>

        {/* Event Log */}
        <div className="bg-gray-900 p-6 rounded-xl shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-white flex items-center gap-2">
              <span className="text-2xl">🔍</span> Event Log
            </h2>
            <button
              onClick={() => setLogs([])}
              className="px-3 py-1 bg-gray-700 text-white text-sm rounded hover:bg-gray-600"
            >
              Clear
            </button>
          </div>
          <div className="bg-black/50 rounded-lg p-4 h-64 overflow-y-auto font-mono text-xs">
            {logs.length === 0 ? (
              <div className="text-gray-500 italic">No events yet...</div>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="text-green-400 mb-1">
                  {log}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Animation */}
        {showAnimation && (
          <AISearchAnimation
            query={currentQuery}
            searchType={searchType}
            onComplete={() => {
              addLog('🎉 Animation completed');
              setShowAnimation(false);
            }}
            onCancel={() => {
              addLog('❌ Animation cancelled');
              setShowAnimation(false);
            }}
            onError={(error) => {
              addLog(`⚠️ Animation error: ${error.message}`);
              setShowAnimation(false);
            }}
          />
        )}
      </div>
    </div>
  );
}
