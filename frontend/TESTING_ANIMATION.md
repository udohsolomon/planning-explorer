# Testing AI Search Animation Locally

## Quick Setup Guide

### Step 1: Create a Test Page

Since the animation isn't integrated into the main search yet, create a test page:

**Create: `frontend/src/app/test-animation/page.tsx`**

```tsx
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
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-[#043F2E] mb-8">
          AI Search Animation Test
        </h1>

        <div className="bg-white p-6 rounded-lg shadow-lg mb-8">
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
            className="px-6 py-3 bg-[#043F2E] text-white rounded-lg hover:bg-[#065940] disabled:opacity-50"
          >
            {isSearching ? 'Animation Running...' : 'Start Animation'}
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

        <div className="bg-blue-50 p-4 rounded-lg">
          <h2 className="font-semibold text-blue-900 mb-2">Instructions:</h2>
          <ol className="text-sm text-blue-800 space-y-1">
            <li>1. Enter a search query above</li>
            <li>2. Click "Start Animation"</li>
            <li>3. Watch the 5-stage animation play</li>
            <li>4. Try pressing ESC to cancel</li>
            <li>5. After 8 seconds, a cancel button appears</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
```

### Step 2: Visit the Test Page

```bash
# Make sure dev server is running
npm run dev

# Open browser to:
http://localhost:3000/test-animation
```

### Step 3: What You Should See

1. **Initial State**: Input field and "Start Animation" button
2. **Animation Plays**: Full-screen modal with 5 stages
3. **Stage Progression**:
   - Stage 1: Understanding Your Question (0.9s)
   - Stage 2: Searching Database (1.5s)
   - Stage 3: Filtering Results (0.8s)
   - Stage 4: Ranking Matches (0.8s)
   - Stage 5: Preparing Results (0.6s)
4. **Total Duration**: ~4.6 seconds
5. **Cancel Button**: Appears after 8 seconds (for slow searches)
6. **Completion**: Alert shows "Animation complete!"

### Step 4: Test Features

#### Test Cancellation
- Click "Start Animation"
- Press **ESC key** to cancel
- OR wait 8 seconds and click "Cancel Search" button

#### Test Error Simulation
To test error states, you'll need to trigger an error. Create another test page:

**Create: `frontend/src/app/test-animation-error/page.tsx`**

```tsx
'use client';

import { useState } from 'react';
import { AISearchAnimation } from '@/components/search/animation/AISearchAnimation';
import { useAnimationStore } from '@/stores/animationStore';
import type { AnimationError } from '@/types/animation.types';

export default function TestAnimationErrorPage() {
  const [isSearching, setIsSearching] = useState(false);
  const [errorType, setErrorType] = useState<'connection' | 'rate_limit' | 'timeout' | 'server'>('connection');
  const { setError } = useAnimationStore();

  const handleStartWithError = () => {
    setIsSearching(true);

    // Simulate error after 2 seconds
    setTimeout(() => {
      const error: AnimationError = {
        type: errorType,
        message: getErrorMessage(errorType),
        userMessage: getUserMessage(errorType),
        retryable: errorType !== 'rate_limit',
      };
      setError(error);
    }, 2000);
  };

  const getErrorMessage = (type: string) => {
    switch (type) {
      case 'connection': return 'Unable to reach planning database';
      case 'rate_limit': return "You've used your free searches for today";
      case 'timeout': return 'Search took too long to complete';
      case 'server': return 'Our servers are experiencing issues';
      default: return 'An error occurred';
    }
  };

  const getUserMessage = (type: string) => {
    switch (type) {
      case 'connection': return 'Connection Error';
      case 'rate_limit': return 'Rate Limit Reached';
      case 'timeout': return 'Timeout Error';
      case 'server': return 'Server Error';
      default: return 'Error';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-[#043F2E] mb-8">
          Test Error States
        </h1>

        <div className="bg-white p-6 rounded-lg shadow-lg mb-8">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Error Type to Test
          </label>
          <select
            value={errorType}
            onChange={(e) => setErrorType(e.target.value as any)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4"
          >
            <option value="connection">Connection Error</option>
            <option value="rate_limit">Rate Limit (shows upgrade CTA)</option>
            <option value="timeout">Timeout Error</option>
            <option value="server">Server Error</option>
          </select>

          <button
            onClick={handleStartWithError}
            disabled={isSearching}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            Trigger Error After 2 Seconds
          </button>
        </div>

        {isSearching && (
          <AISearchAnimation
            query="test query"
            searchType="semantic"
            onComplete={() => setIsSearching(false)}
            onCancel={() => setIsSearching(false)}
            onError={(error) => console.error('Error:', error)}
          />
        )}
      </div>
    </div>
  );
}
```

Visit: `http://localhost:3000/test-animation-error`

---

## Integration with Real Search (Optional)

To integrate with your actual search, update `SearchInterface.tsx`:

```tsx
// Add this import at the top
import { AISearchAnimation } from '@/components/search/animation/AISearchAnimation';

// Add state for animation
const [showAnimation, setShowAnimation] = useState(false);

// Update performSearch function to show animation:
const performSearch = async (query: string, type: 'traditional' | 'semantic' | 'natural_language') => {
  // Show animation for semantic/NL searches
  if (type === 'semantic' || type === 'natural_language') {
    setShowAnimation(true);
  }

  // ... existing search code ...

  // Hide animation when done
  setShowAnimation(false);
}

// Add animation component before closing </section>:
{showAnimation && (
  <AISearchAnimation
    query={filters.query}
    searchType={searchType === 'semantic' ? 'semantic' : 'hybrid'}
    onComplete={() => setShowAnimation(false)}
    onCancel={() => {
      setShowAnimation(false);
      setIsSearching(false);
    }}
  />
)}
```

---

## Troubleshooting

### Animation Doesn't Show
1. **Check console** for errors
2. **Verify imports** are correct
3. **Check** that `isSearching` state is true
4. **Ensure** framer-motion is installed: `npm install framer-motion --legacy-peer-deps`

### Animation Closes Immediately
- Make sure `onComplete` doesn't set `isSearching` to false too quickly
- The animation should play for ~4.6 seconds before completing

### Styling Issues
- Verify Tailwind CSS is configured
- Check that Planning Explorer brand colors are in `tailwind.config.ts`:
  ```js
  colors: {
    'planning-primary': '#043F2E',
    'planning-bright': '#10B981',
  }
  ```

### Cancel Button Not Showing
- The cancel button appears after **8 seconds** for slow searches
- To test immediately, modify `useSlowResponseHandler.ts` timing

---

## Next Steps

Once you've tested the animation:

1. **Integrate** with actual search API
2. **Add** real-time progress updates from backend
3. **Configure** analytics tracking
4. **Deploy** to staging for user testing

See `DEPLOYMENT.md` for full production deployment guide.
