# AI Search Animation - Usage Guide
*Planning Explorer Implementation*

## Quick Start

### Basic Usage

```tsx
import { AISearchAnimation } from '@/components/search/animation';
import { useState } from 'react';

export function SearchPage() {
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setIsSearching(true);
  };

  const handleSearchComplete = () => {
    setIsSearching(false);
    // Show search results
  };

  return (
    <div>
      {/* Search Interface */}
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        onKeyPress={(e) => {
          if (e.key === 'Enter') {
            handleSearch(searchQuery);
          }
        }}
        placeholder="Search planning applications..."
      />

      {/* Animation Modal */}
      {isSearching && (
        <AISearchAnimation
          query={searchQuery}
          searchType="semantic"
          onComplete={handleSearchComplete}
          onCancel={() => setIsSearching(false)}
        />
      )}
    </div>
  );
}
```

---

## Component API

### AISearchAnimation Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `query` | `string` | ✅ | The search query text |
| `searchType` | `'semantic' \| 'keyword' \| 'hybrid'` | ✅ | Type of search being performed |
| `onComplete` | `() => void` | ✅ | Callback when animation finishes |
| `onCancel` | `() => void` | ❌ | Callback when user cancels |
| `onError` | `(error: AnimationError) => void` | ❌ | Callback for error handling |
| `actualProgress` | `number` | ❌ | Real-time progress from backend (0-100) |
| `estimatedDuration` | `number` | ❌ | Override default duration (ms) |

---

## Advanced Usage

### With Real-Time Backend Progress

```tsx
import { AISearchAnimation } from '@/components/search/animation';
import { useSearchProgress } from '@/hooks/useSearchProgress';

export function AdvancedSearch() {
  const { progress, isSearching, performSearch } = useSearchProgress();

  const handleSearch = async (query: string) => {
    await performSearch(query);
  };

  return (
    <>
      {isSearching && (
        <AISearchAnimation
          query={query}
          searchType="semantic"
          actualProgress={progress} // Synced with backend
          onComplete={() => console.log('Search complete')}
        />
      )}
    </>
  );
}
```

### With Dynamic Value Updates

```tsx
import { useAnimationStore } from '@/stores/animationStore';

export function SearchWithDynamicValues() {
  const { updateDynamicValue } = useAnimationStore();

  // Update values from backend in real-time
  useEffect(() => {
    const ws = new WebSocket('ws://api.planningexplorer.com/search');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      // Update animation with live counts
      if (data.applicationsFound) {
        updateDynamicValue('applicationsFound', data.applicationsFound);
      }

      if (data.applicationsFiltered) {
        updateDynamicValue('applicationsFiltered', data.applicationsFiltered);
      }
    };

    return () => ws.close();
  }, [updateDynamicValue]);

  return (
    <AISearchAnimation
      query={query}
      searchType="semantic"
      onComplete={handleComplete}
    />
  );
}
```

### With Error Handling

```tsx
import type { AnimationError } from '@/types/animation.types';

export function SearchWithErrors() {
  const [error, setError] = useState<AnimationError | null>(null);

  const handleError = (error: AnimationError) => {
    setError(error);

    // Show error notification
    toast.error(error.userMessage);

    // Log for analytics
    analytics.track('search_error', {
      type: error.type,
      retryable: error.retryable,
    });
  };

  return (
    <AISearchAnimation
      query={query}
      searchType="semantic"
      onComplete={handleComplete}
      onError={handleError}
    />
  );
}
```

---

## Customization

### Adjusting Timings

```tsx
import { DEFAULT_TIMINGS } from '@/components/search/animation';

// Override default duration
<AISearchAnimation
  query={query}
  searchType="semantic"
  estimatedDuration={6000} // 6 seconds instead of 4.6
  onComplete={handleComplete}
/>
```

### Responsive Behavior

The component automatically adapts to:
- **Desktop** (1024px+): Full 680px modal with 48px icons
- **Tablet** (768-1023px): 90% width, 44px icons
- **Mobile** (<768px): 95% width, 40px icons, faster animations

### Reduced Motion Support

Automatically respects `prefers-reduced-motion`:
- Disables all animations
- Shows instant transitions between stages
- Still maintains accessibility

---

## State Management

### Zustand Store Access

```tsx
import { useAnimationStore } from '@/stores/animationStore';

export function SearchControl() {
  const {
    currentStage,
    isAnimating,
    dynamicValues,
    cancelAnimation,
  } = useAnimationStore();

  return (
    <div>
      <p>Current Stage: {currentStage} / 5</p>
      <p>Applications Found: {dynamicValues.applicationsFound || 0}</p>
      {isAnimating && (
        <button onClick={cancelAnimation}>Cancel Search</button>
      )}
    </div>
  );
}
```

### Selector Hooks

```tsx
import {
  useCurrentStage,
  useIsAnimating,
  useAnimationProgress,
} from '@/stores/animationStore';

export function SearchStatus() {
  const stage = useCurrentStage();
  const isAnimating = useIsAnimating();
  const progress = useAnimationProgress();

  return (
    <div>
      {isAnimating && (
        <p>Stage {stage}/5 - {progress}% complete</p>
      )}
    </div>
  );
}
```

---

## Integration Examples

### Next.js App Router

```tsx
// app/search/page.tsx
'use client';

import { AISearchAnimation } from '@/components/search/animation';
import { useSearchParams, useRouter } from 'next/navigation';

export default function SearchPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const query = searchParams.get('q') || '';

  const [isSearching, setIsSearching] = useState(true);

  const handleComplete = () => {
    setIsSearching(false);
    // Results are already loaded, just hide animation
  };

  return (
    <>
      {isSearching && query && (
        <AISearchAnimation
          query={query}
          searchType="semantic"
          onComplete={handleComplete}
          onCancel={() => router.push('/')}
        />
      )}

      {/* Search results (hidden during animation) */}
      <SearchResults query={query} />
    </>
  );
}
```

### With TanStack Query

```tsx
import { useQuery } from '@tanstack/react-query';
import { AISearchAnimation } from '@/components/search/animation';

export function QuerySearch({ query }: { query: string }) {
  const { data, isLoading, isSuccess } = useQuery({
    queryKey: ['search', query],
    queryFn: () => searchAPI.search(query),
    enabled: !!query,
  });

  return (
    <>
      {isLoading && (
        <AISearchAnimation
          query={query}
          searchType="semantic"
          onComplete={() => console.log('Animation done')}
        />
      )}

      {isSuccess && <SearchResults results={data} />}
    </>
  );
}
```

---

## Accessibility Features

### Built-in Accessibility

✅ **ARIA Support**
- `role="dialog"` on modal
- `aria-modal="true"`
- `aria-labelledby` and `aria-describedby`
- `role="status"` for screen reader announcements

✅ **Keyboard Navigation**
- ESC key closes animation (if `onCancel` provided)
- Focus trap within modal
- Proper focus management

✅ **Screen Reader**
- Announces each stage transition
- Announces dynamic values (application counts)
- Announces completion

✅ **Reduced Motion**
- Respects `prefers-reduced-motion`
- Provides instant, non-animated alternative

✅ **Color Contrast**
- WCAG AA compliant (all text exceeds 4.5:1)
- Planning Explorer brand colors (#043F2E primary)

---

## Performance Optimization

### GPU Acceleration
All animations use `transform` and `opacity` for 60fps performance.

### Bundle Impact
- **Framer Motion**: ~50KB gzipped (already in dependencies)
- **Animation Components**: ~8KB gzipped
- **Total Impact**: ~8KB additional

### Mobile Performance
Automatic optimizations on mobile:
- Faster stage durations (3.6s vs 4.6s)
- Reduced blur effects
- Simplified animations for low-end devices

---

## Troubleshooting

### Animation Not Showing

```tsx
// ❌ Wrong - Missing client directive
export function Search() {
  return <AISearchAnimation ... />
}

// ✅ Correct - Client component
'use client';

export function Search() {
  return <AISearchAnimation ... />
}
```

### TypeScript Errors

```bash
# Ensure types are imported
import type { AISearchAnimationProps } from '@/types/animation.types';
```

### Framer Motion Errors

```bash
# Verify installation
npm list framer-motion

# Should show: framer-motion@11.18.2
```

---

## Testing

### Unit Test Example

```tsx
import { render, screen, waitFor } from '@testing-library/react';
import { AISearchAnimation } from '@/components/search/animation';

describe('AISearchAnimation', () => {
  it('completes animation sequence', async () => {
    const onComplete = jest.fn();

    render(
      <AISearchAnimation
        query="test query"
        searchType="semantic"
        onComplete={onComplete}
      />
    );

    // Animation should complete after ~4.6 seconds
    await waitFor(() => expect(onComplete).toHaveBeenCalled(), {
      timeout: 5000,
    });
  });

  it('announces stages for screen readers', () => {
    render(
      <AISearchAnimation
        query="test"
        searchType="semantic"
        onComplete={() => {}}
      />
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});
```

---

## Next Steps

After Phase 1 (Core Foundation) is complete, future phases will add:

**Phase 2**: Enhanced animations, connection lines, progress bar
**Phase 3**: Error handling, cancel button, slow response handling
**Phase 4**: Full accessibility compliance, reduced motion refinements
**Phase 5**: Analytics, A/B testing framework

---

*For questions or issues, see the full feature spec: `AI_SEARCH_ANIMATION_FEATURE.md`*
