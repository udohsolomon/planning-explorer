# Feature Specification: AI Search Process Animation for Planning Explorer

## Overview
Implement an animated, real-time process visualization that displays on the search results page when users submit natural language queries about UK planning applications. This feature provides transparency into the AI search process and builds user confidence by showing the system's intelligence at work.

**Design Philosophy**: This animation reinforces Planning Explorer's brand identity while delivering a premium, trust-building user experience that differentiates us from traditional planning portals.

## Feature Requirements

### 1. Animation Trigger
- Activate when user submits a natural language search query from the search bar
- Display on the search results page (`/search`) before results are shown
- Duration: 3-5 seconds (or actual processing time if longer)
- Smooth entrance animation: fade-in with subtle scale (0.95 → 1.0)

### 2. Visual Design & Brand Identity

#### Container Design
- **Positioning**: Center-aligned modal overlay with backdrop blur effect
- **Background**: Clean white card (`#ffffff`) with subtle shadow (`0 10px 40px rgba(4, 63, 46, 0.08)`)
- **Border**: 1px solid `rgba(4, 63, 46, 0.1)` for refined definition
- **Padding**: 48px (desktop), 32px (tablet), 24px (mobile)
- **Border Radius**: 16px for modern, approachable feel
- **Max Width**: 680px for optimal readability
- **Backdrop**: Semi-transparent overlay (`rgba(4, 63, 46, 0.02)`) with blur effect

#### Layout Structure
- **Vertical Timeline**: Stepper design with connecting animated lines
- **Stage Spacing**: 32px between stages (24px on mobile)
- **Icon Alignment**: Left-aligned with connecting lines
- **Content Flow**: Icon → Title → Sub-steps (left-to-right flow)
- **Connection Lines**: Dotted/dashed vertical lines (2px, `#E5E7EB`) with animated progress fill

#### Brand Color System
**Planning Explorer Primary Palette:**
- **Primary Green**: `#043F2E` (Brand core color)
- **Secondary Green**: `#065940` (Hover states)
- **Accent Green**: `#087952` (Active highlights)
- **Success Green**: `#10B981` (Completion states)
- **Neutral Gray**: `#6B7280` (Inactive/upcoming states)
- **Light Gray**: `#F3F4F6` (Background accents)
- **Dark Text**: `#1A1A1A` (Primary text)
- **Medium Text**: `#666666` (Secondary text)

**Color Application:**
- **Active Stage Icon**: Primary Green (#043F2E) background with white icon
- **Active Stage Title**: Dark text (#1A1A1A) with semi-bold weight
- **Active Sub-steps**: Medium text (#666666) with Accent Green (#087952) bullets
- **Completed Stage Icon**: Success Green (#10B981) with white checkmark
- **Completed Stage Text**: Neutral Gray (#6B7280) with reduced opacity
- **Upcoming Stage Icon**: Light Gray (#F3F4F6) border only, no background
- **Upcoming Stage Text**: Neutral Gray (#6B7280) at 50% opacity
- **Progress Line**: Gradient from Primary Green to Success Green

#### Typography System
**Font Family**: DM Sans (matches Planning Explorer brand)
- **Stage Titles**:
  - Font: DM Sans, Semi-Bold (600)
  - Size: 18px (desktop), 16px (mobile)
  - Color: #1A1A1A
  - Line Height: 1.4

- **Sub-steps**:
  - Font: DM Sans, Regular (400)
  - Size: 15px (desktop), 14px (mobile)
  - Color: #666666
  - Line Height: 1.6
  - Bullet Points: Custom diamond (◆) in Accent Green (#087952)

- **Stage Counter** (optional):
  - Font: DM Sans, Medium (500)
  - Size: 14px
  - Color: #6B7280

- **Dynamic Values** (counts, numbers):
  - Font: DM Sans, Semi-Bold (600)
  - Color: #043F2E (Primary Green for emphasis)

#### Icon Design
- **Size**: 48px × 48px (desktop), 40px × 40px (mobile)
- **Background**: Circular with 50% border-radius
- **Icon Color**: White (`#ffffff`)
- **Icon Set**: Use Lucide React icons for consistency
  - Brain/Lightbulb: Understanding query
  - Database/Search: Database search
  - Filter/Funnel: Filtering
  - BarChart/TrendingUp: Ranking
  - Sparkles/FileCheck: Preparing results
- **Animation**: Gentle pulse effect (scale 1.0 → 1.05 → 1.0) on active stage
- **Transition**: 200ms ease-in-out for smooth state changes

### 3. Process Stages (Adapted for Planning Applications)

#### Stage 1: Understanding Query
- **Icon**: Brain or Message Bubble icon
- **Title**: "Understanding Your Question"
- **Sub-steps**:
  - ◆ Analyzing natural language query...
  - ◆ Extracting key parameters (location, type, status)...
  - ◆ Identifying search intent...

#### Stage 2: AI Semantic Search
- **Icon**: Search or Database icon
- **Title**: "Searching Planning Database"
- **Sub-steps**:
  - ◆ Scanning 336K+ planning applications...
  - ◆ Running AI semantic matching...
  - ◆ [Dynamic] X applications found that match criteria...

#### Stage 3: Filtering Results
- **Icon**: Filter icon
- **Title**: "Filtering Results"
- **Sub-steps**:
  - ◆ Applying location & date filters...
  - ◆ Cross-checking approval status...
  - ◆ [Dynamic] X applications remaining after filters...

#### Stage 4: Ranking Matches
- **Icon**: Chart/Ranking icon
- **Title**: "Ranking Matches"
- **Sub-steps**:
  - ◆ Calculating relevance scores...
  - ◆ Analyzing opportunity ratings...
  - ◆ Sorting by best matches...

#### Stage 5: Preparing Response
- **Icon**: Sparkles or Document icon
- **Title**: "Preparing Results"
- **Sub-steps**:
  - ◆ Generating AI insights...
  - ◆ Formatting display data...
  - ◆ Ready to display results!

### 4. Animation Behavior & Motion Design

#### Sequential Animation Timeline
Stages animate one after another in sequence with carefully choreographed timing:

**Stage Entrance** (Total: 800ms per stage)
1. **Icon Reveal** (300ms): Scale from 0.8 → 1.0 with fade-in, elastic easing
2. **Title Slide-In** (200ms): Fade + translate from left (-10px → 0), ease-out
3. **Sub-steps Cascade** (150ms each, staggered by 80ms): Fade + translate from left
   - First sub-step: delay 0ms
   - Second sub-step: delay 80ms
   - Third sub-step: delay 160ms
4. **Pulse Effect** (continuous): Gentle 2s loop while active (opacity 1.0 → 0.85 → 1.0)
5. **Completion** (250ms): Icon morph to checkmark with bounce, title/steps fade to completed state

**Connection Line Animation**
- Animated stroke-dashoffset for "drawing" effect
- Progress from previous stage to current stage
- Duration: 400ms, ease-in-out
- Color: Gradient from Primary Green → Success Green

#### Visual States (Detailed Specification)

**Active State**:
- **Icon**: Primary Green (#043F2E) background, white icon, pulsing animation
- **Title**: Dark text (#1A1A1A), font-weight 600, fully opaque
- **Sub-steps**: Medium text (#666666), staggered fade-in, Accent Green bullets (◆)
- **Connection Line**: Animated gradient stroke, actively drawing
- **Overall Effect**: Draws user attention without being distracting

**Completed State**:
- **Icon**: Success Green (#10B981) background, white checkmark icon, scale bounce
- **Title**: Neutral Gray (#6B7280), font-weight 600, 80% opacity
- **Sub-steps**: Neutral Gray (#6B7280), 70% opacity, all visible
- **Checkmark Animation**: Scale from 0 → 1.2 → 1.0 with elastic easing (300ms)
- **Connection Line**: Solid Success Green, fully drawn
- **Overall Effect**: Satisfying completion feedback

**Upcoming/Pending State**:
- **Icon**: Light Gray (#F3F4F6) background, Neutral Gray (#6B7280) icon at 40% opacity
- **Title**: Neutral Gray (#6B7280), font-weight 600, 50% opacity
- **Sub-steps**: Hidden (will appear when stage activates)
- **Connection Line**: Dashed Light Gray (#E5E7EB), static
- **Overall Effect**: Clear preview of upcoming work

#### Progress Indicators

**Top Progress Bar** (Optional enhancement):
- **Position**: Top of modal card, 4px height
- **Background**: Light Gray (#F3F4F6)
- **Fill**: Linear gradient (Primary Green → Accent Green)
- **Animation**: Smooth width transition, 400ms ease-out
- **Percentage**: 0% → 100% based on stage completion (20% per stage)

**Stage Counter Badge**:
- **Position**: Top-right corner of modal
- **Text**: "Step 2 of 5"
- **Style**: DM Sans Medium, 14px, Neutral Gray (#6B7280)
- **Background**: Light Gray (#F3F4F6), 6px padding, 8px border-radius
- **Animation**: Fade + scale when updating (200ms)

**Overall Completion Timer** (Alternative approach):
- **Circular Progress**: SVG circle around entire animation area
- **Stroke**: Primary Green (#043F2E), 3px width
- **Duration**: 4-5 seconds full rotation
- **Position**: Subtle overlay at bottom-right

#### Performance Optimizations
- Use `transform` and `opacity` for animations (GPU-accelerated)
- Leverage Framer Motion's `layoutId` for shared element transitions
- Implement `will-change` CSS property on animating elements
- Debounce stage transitions to prevent janky animations
- Use `IntersectionObserver` to pause animations when modal not visible

### 5. Technical Implementation

#### Component Architecture

```typescript
// Main Animation Component
interface AISearchAnimationProps {
  query: string;
  searchType: 'semantic' | 'keyword' | 'hybrid';
  actualProgress?: number; // Real-time progress from backend (0-100)
  estimatedDuration?: number; // Override default duration
  onComplete: () => void;
  onCancel?: () => void;
}

<AISearchAnimation
  query={userQuery}
  searchType={searchType}
  actualProgress={realTimeProgress}
  onComplete={handleSearchComplete}
  onCancel={handleSearchCancel}
/>
```

**Component Hierarchy:**
```
AISearchAnimation (Container)
  ├── AnimationBackdrop (Overlay with blur)
  ├── AnimationCard (Modal container)
  │   ├── ProgressBar (Optional top indicator)
  │   ├── StageCounter (Step X of 5)
  │   ├── SearchStage (x5 instances)
  │   │   ├── StageIcon (with pulse animation)
  │   │   ├── ConnectionLine (animated stroke)
  │   │   ├── StageTitle
  │   │   └── SearchSubStep (x3 per stage)
  │   │       ├── BulletIcon (diamond)
  │   │       └── StepText (with dynamic values)
  │   └── CancelButton (appears after 8s)
```

#### State Management (Zustand/React State)

```typescript
interface AnimationState {
  currentStage: number; // 1-5
  stageStatus: ('pending' | 'active' | 'completed')[]; // Array of 5
  subStepProgress: Record<number, number[]>; // Stage -> [step1, step2, step3]
  dynamicValues: {
    applicationsFound?: number;
    applicationsFiltered?: number;
    relevanceScore?: number;
  };
  isAnimating: boolean;
  isPaused: boolean;
  elapsedTime: number;
}

// Actions
const useAnimationStore = create<AnimationState>((set) => ({
  currentStage: 0,
  stageStatus: ['pending', 'pending', 'pending', 'pending', 'pending'],
  subStepProgress: {},
  dynamicValues: {},
  isAnimating: false,
  isPaused: false,
  elapsedTime: 0,

  startAnimation: () => set({ isAnimating: true, currentStage: 1 }),
  completeStage: (stage: number) => {
    // Update stage status, move to next
  },
  updateDynamicValue: (key: string, value: number) => {
    // Update dynamic values in real-time
  },
  pauseAnimation: () => set({ isPaused: true }),
  cancelAnimation: () => set({ isAnimating: false, currentStage: 0 }),
}));
```

#### Timing & Duration Control

**Default Stage Timings** (Total: 4.6 seconds):
- **Stage 1 - Understanding**: 900ms
  - Icon reveal: 300ms
  - Title slide: 200ms
  - Sub-steps cascade: 400ms (3 × 150ms staggered)
- **Stage 2 - Searching**: 1500ms (longest stage - most important)
  - Icon reveal: 300ms
  - Title slide: 200ms
  - Sub-steps cascade: 600ms
  - Additional dwell time: 400ms (to emphasize database work)
- **Stage 3 - Filtering**: 800ms
- **Stage 4 - Ranking**: 800ms
- **Stage 5 - Preparing**: 600ms
  - Faster completion for smooth transition to results

**Adaptive Timing Logic:**
```typescript
function calculateStageDuration(
  stage: number,
  actualProgress: number,
  defaultDuration: number
): number {
  // If backend provides real progress, sync animation timing
  if (actualProgress > 0) {
    return Math.max(defaultDuration * 0.8, 500); // Min 500ms per stage
  }
  return defaultDuration;
}
```

#### Animation Implementation (Framer Motion)

**Stage Icon Animation:**
```tsx
<motion.div
  initial={{ scale: 0.8, opacity: 0 }}
  animate={{ scale: 1, opacity: 1 }}
  transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }} // Elastic easing
  className="stage-icon"
>
  {/* Icon with continuous pulse when active */}
  <motion.div
    animate={isActive ? { opacity: [1, 0.85, 1] } : {}}
    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
  >
    <IconComponent />
  </motion.div>
</motion.div>
```

**Sub-step Stagger Animation:**
```tsx
<motion.ul
  variants={{
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08, // 80ms stagger
        delayChildren: 0.2, // Wait for title
      }
    }
  }}
  initial="hidden"
  animate="visible"
>
  {subSteps.map((step, index) => (
    <motion.li
      key={index}
      variants={{
        hidden: { opacity: 0, x: -10 },
        visible: { opacity: 1, x: 0 }
      }}
      transition={{ duration: 0.15, ease: "easeOut" }}
    >
      <span className="bullet">◆</span> {step.text}
    </motion.li>
  ))}
</motion.ul>
```

**Checkmark Bounce Animation:**
```tsx
<motion.div
  initial={{ scale: 0 }}
  animate={{ scale: [0, 1.2, 1] }}
  transition={{
    duration: 0.3,
    times: [0, 0.6, 1],
    ease: [0.34, 1.56, 0.64, 1] // Elastic
  }}
  className="checkmark"
>
  <Check className="w-6 h-6" />
</motion.div>
```

**Connection Line Drawing:**
```tsx
<motion.svg className="connection-line">
  <motion.line
    x1="50%" y1="0" x2="50%" y2="100%"
    stroke="url(#gradient)"
    strokeWidth="2"
    strokeDasharray="4 4"
    initial={{ pathLength: 0 }}
    animate={{ pathLength: 1 }}
    transition={{ duration: 0.4, ease: "easeInOut" }}
  />
  <defs>
    <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stopColor="#043F2E" />
      <stop offset="100%" stopColor="#10B981" />
    </linearGradient>
  </defs>
</motion.svg>
```

#### Animation Library Stack
- **Framer Motion** v11+ for complex orchestration
- **Lucide React** for icon library
- **Tailwind CSS** for utility styling
- **Custom CSS** for gradient effects and backdrop blur

### 6. Responsive Design & Adaptive Layouts

#### Desktop (1024px+)
- **Modal Width**: 680px max-width, centered
- **Modal Padding**: 48px all sides
- **Icon Size**: 48px × 48px
- **Stage Spacing**: 32px between stages
- **Typography**: 18px titles, 15px sub-steps
- **Progress Bar**: Full width at top (optional)
- **Cancel Button**: Bottom-right, 40px height
- **Backdrop Blur**: Full effect (8px blur)

#### Tablet (768px - 1023px)
- **Modal Width**: 90% viewport width, max 600px
- **Modal Padding**: 32px all sides
- **Icon Size**: 44px × 44px
- **Stage Spacing**: 28px between stages
- **Typography**: 17px titles, 14px sub-steps
- **Progress Bar**: Condensed to 3px height
- **Cancel Button**: Full-width at bottom
- **Backdrop Blur**: Medium effect (6px blur)

#### Mobile (< 768px)
- **Modal Width**: 95% viewport width, 16px margins
- **Modal Padding**: 24px all sides
- **Icon Size**: 40px × 40px
- **Stage Spacing**: 24px between stages
- **Typography**: 16px titles, 14px sub-steps
- **Connection Lines**: Thinner (1px) or hidden
- **Progress Bar**: Essential - shows at top (3px height)
- **Stage Counter**: Moved to top-center
- **Cancel Button**: Full-width sticky bottom button
- **Sub-step Text**: Condensed, may hide third sub-step
- **Backdrop Blur**: Light effect (4px blur) for performance

#### Touch & Interaction Adjustments
- **Mobile Tap Targets**: Min 44px × 44px for cancel button
- **Swipe to Dismiss**: Optional left/right swipe gesture
- **Reduced Motion**: Respect `prefers-reduced-motion` media query
  - Disable pulse animations
  - Instant transitions instead of staggered
  - Static icons instead of animated
  - Cross-fade between stages only

#### Performance Considerations by Device
**Mobile Optimization:**
```typescript
const isMobile = useMediaQuery('(max-width: 768px)');
const reducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)');

const animationConfig = {
  stageDuration: isMobile ? 600 : 800, // Faster on mobile
  enablePulse: !isMobile && !reducedMotion,
  enableStagger: !reducedMotion,
  enableBlur: !isMobile, // Disable blur on mobile for performance
};
```

### 7. Edge Cases & Error Handling

#### Fast API Response (<2s)
**Challenge**: Results arrive before animation completes
**Solution**:
- Queue results and hold animation to minimum duration
- Minimum display time: 2.5 seconds (preserves user trust)
- Accelerate stages proportionally (all stages 80% speed)
- Skip Stage 5 dwell time, transition immediately
- Smooth fade-out to results (300ms)

**Implementation:**
```typescript
if (apiResponseTime < 2000) {
  const accelerationFactor = 0.8;
  stageDurations = stageDurations.map(d => d * accelerationFactor);
  // Still ensures minimum 2.5s total
}
```

#### Slow API Response (>5s)
**Challenge**: Keeping users engaged during extended wait
**Solution - Progressive Enhancement:**

**At 5 seconds (Stage 2-3 loop):**
- Add rotating messages in Stage 2:
  - "Searching 336,000+ applications..."
  - "Analyzing semantic matches..."
  - "Cross-referencing locations..."
- Subtle message rotation every 2s

**At 8 seconds:**
- Show cancel button with gentle fade-in
- Button style: Outlined, Neutral Gray
- Text: "Cancel Search"
- Position: Bottom-center of modal

**At 10 seconds:**
- Add supplementary message below stages:
  - "🔍 Deep search in progress for best results..."
  - Font: DM Sans, 14px, Neutral Gray (#6B7280)
  - Icon: Animated search icon

**At 15 seconds:**
- Enhanced cancel button (more prominent):
  - Background: Light Gray (#F3F4F6)
  - Border: Primary Green (#043F2E)
  - Hover: Primary Green background
- Additional message:
  - "This is taking longer than usual. You can cancel and try a simpler query."

**Implementation:**
```typescript
useEffect(() => {
  const timers = [
    setTimeout(() => setShowRotatingMessages(true), 5000),
    setTimeout(() => setShowCancelButton(true), 8000),
    setTimeout(() => setShowDeepSearchMessage(true), 10000),
    setTimeout(() => setEnhanceCancelButton(true), 15000),
  ];
  return () => timers.forEach(clearTimeout);
}, []);
```

#### Error States (Stage-Specific Handling)

**Connection Error:**
- **Failed Stage**: Stage 2 (Database Search)
- **Visual**: Icon changes to Alert Triangle (red #EF4444)
- **Animation**: Gentle shake effect (3x left-right 10px)
- **Message**:
  ```
  ⚠️ Connection Error
  Unable to reach planning database
  ```
- **Actions**:
  - Retry Button (Primary): "Try Again"
  - Cancel Button (Secondary): "Go Back"

**Query Parsing Error:**
- **Failed Stage**: Stage 1 (Understanding)
- **Visual**: Icon changes to Help Circle (orange #F59E0B)
- **Message**:
  ```
  🤔 Query Not Understood
  We couldn't parse your search query
  Try: "Approved housing in Manchester"
  ```
- **Actions**:
  - Simplified Search Button: "Use Filters Instead"
  - Edit Query Button: "Rephrase Search"

**No Results Error:**
- **Completed Stage**: All stages complete successfully
- **Final Stage (5) Message Change**:
  ```
  ℹ️ No Matching Applications
  Try broadening your search criteria
  ```
- **Actions**:
  - Broaden Search Button: "Remove Filters"
  - New Search Button: "Start Over"

**Server Error (500):**
- **Failed Stage**: Varies based on where error occurred
- **Visual**: Icon changes to X Circle (red #EF4444)
- **Message**:
  ```
  ❌ Server Error
  Something went wrong on our end
  ```
- **Actions**:
  - Retry Button: "Try Again"
  - Contact Support: "Report Issue" (Enterprise only)

**Rate Limit Error (429):**
- **Failed Stage**: Stage 2
- **Visual**: Icon changes to Clock (orange #F59E0B)
- **Message**:
  ```
  ⏱️ Rate Limit Reached
  You've used your free searches for today
  Upgrade to Professional for unlimited searches
  ```
- **Actions**:
  - Upgrade Button (Primary, Primary Green): "Upgrade Now"
  - Wait Button (Secondary): "Try Later"

#### Network Timeout
- **Timeout Duration**: 30 seconds
- **Behavior**: Same as Slow API Response with automatic cancellation
- **Message**: "Search timed out. Please try again with a simpler query."
- **Actions**:
  - Retry Button
  - Simplify Search Button

#### Accessibility Error Announcements
```tsx
<div role="status" aria-live="polite" className="sr-only">
  {errorMessage && `Error: ${errorMessage}`}
  {currentStage === 5 && isComplete && "Search complete, displaying results"}
</div>
```

### 8. Accessibility & Inclusive Design

#### ARIA Implementation

**Modal Container:**
```tsx
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="search-animation-title"
  aria-describedby="search-animation-description"
  className="animation-modal"
>
  <h2 id="search-animation-title" className="sr-only">
    AI Search in Progress
  </h2>
  <p id="search-animation-description" className="sr-only">
    We're analyzing your search query across 336,000+ planning applications
  </p>
</div>
```

**Stage Announcements:**
```tsx
<div role="status" aria-live="polite" aria-atomic="true" className="sr-only">
  {currentStage === 1 && "Stage 1 of 5: Understanding your question"}
  {currentStage === 2 && "Stage 2 of 5: Searching planning database"}
  {currentStage === 3 && "Stage 3 of 5: Filtering results"}
  {currentStage === 4 && "Stage 4 of 5: Ranking matches"}
  {currentStage === 5 && "Stage 5 of 5: Preparing results"}
  {isComplete && "Search complete. Displaying results."}
</div>
```

**Progress Updates:**
```tsx
<div role="progressbar"
  aria-valuenow={progress}
  aria-valuemin={0}
  aria-valuemax={100}
  aria-label="Search progress"
  className="sr-only"
>
  {progress}% complete
</div>
```

#### Keyboard Navigation

**Focus Management:**
- Auto-focus on cancel button when it appears (after 8s)
- Escape key dismisses modal (if cancellable)
- Tab cycles through interactive elements only
- Focus trap within modal during animation

**Keyboard Shortcuts:**
```typescript
const handleKeyDown = (e: KeyboardEvent) => {
  switch(e.key) {
    case 'Escape':
      if (cancellable) handleCancel();
      break;
    case 'Enter':
      if (canRetry) handleRetry();
      break;
  }
};
```

#### Reduced Motion Support

**CSS Media Query:**
```css
@media (prefers-reduced-motion: reduce) {
  .animation-modal * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }

  .stage-icon {
    /* No pulse animation */
    animation: none;
  }

  .connection-line {
    /* Instant drawing */
    animation: none;
    stroke-dashoffset: 0;
  }
}
```

**Component-Level Adaptation:**
```tsx
const reducedMotion = useReducedMotion(); // Custom hook

<motion.div
  initial={reducedMotion ? { opacity: 1 } : { opacity: 0, scale: 0.8 }}
  animate={reducedMotion ? { opacity: 1 } : { opacity: 1, scale: 1 }}
  transition={reducedMotion ? { duration: 0 } : { duration: 0.3 }}
>
```

**Alternative Static Display:**
- Cross-fade between stages only (200ms)
- No stagger effects on sub-steps
- Static icons (no pulse)
- Instant stage transitions
- Simple opacity changes

#### Screen Reader Optimization

**Contextual Descriptions:**
```tsx
<span className="sr-only">
  {stage === 2 && dynamicValues.applicationsFound &&
    `Found ${dynamicValues.applicationsFound} matching applications`
  }
  {stage === 3 && dynamicValues.applicationsFiltered &&
    `${dynamicValues.applicationsFiltered} applications after filtering`
  }
</span>
```

**Action Announcements:**
```tsx
<div role="alert" aria-live="assertive" className="sr-only">
  {error && `Error occurred: ${error.message}`}
  {showCancelButton && "Cancel button is now available"}
  {isComplete && "Search completed successfully"}
</div>
```

#### Color Contrast (WCAG AA Compliance)

**Text Contrast Ratios:**
- **Dark text on white** (#1A1A1A on #FFFFFF): 15.8:1 ✓ (AAA)
- **Medium text on white** (#666666 on #FFFFFF): 5.7:1 ✓ (AA)
- **Primary green on white** (#043F2E on #FFFFFF): 10.9:1 ✓ (AAA)
- **White on primary green** (#FFFFFF on #043F2E): 10.9:1 ✓ (AAA)
- **Error red on white** (#EF4444 on #FFFFFF): 4.5:1 ✓ (AA)

**Icon Color Modes:**
- Ensure 3:1 contrast for icons
- Provide text labels, not icon-only UI
- Support high contrast mode

#### Focus Indicators
```css
.cancel-button:focus-visible {
  outline: 2px solid #043F2E;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(4, 63, 46, 0.1);
}
```

#### Touch Target Sizes (Mobile)
- Minimum 44px × 44px for all interactive elements
- Adequate spacing between buttons (8px minimum)
- Swipe gesture for dismissal (optional, with fallback)

### 9. File Structure & Organization

```
/src/components/search/animation/
  ├── AISearchAnimation.tsx           # Main orchestrator component
  ├── AnimationBackdrop.tsx           # Modal overlay with blur
  ├── AnimationCard.tsx               # Modal container with styling
  ├── SearchStage.tsx                 # Individual stage component
  ├── StageIcon.tsx                   # Animated icon with pulse effect
  ├── ConnectionLine.tsx              # Animated connecting lines
  ├── SearchSubStep.tsx               # Sub-step item with bullet
  ├── ProgressBar.tsx                 # Top progress indicator
  ├── StageCounter.tsx                # "Step X of 5" badge
  ├── CancelButton.tsx                # Cancellation control
  ├── ErrorDisplay.tsx                # Error state UI
  └── config/
      ├── animationStages.ts          # Stage definitions and timings
      ├── animationTimings.ts         # Duration and easing configs
      └── animationIcons.ts           # Icon mappings per stage

/src/hooks/animation/
  ├── useAnimationController.ts       # Main animation state logic
  ├── useStageTransition.ts           # Stage progression logic
  ├── useAnimationTiming.ts           # Adaptive timing calculations
  ├── useReducedMotion.ts             # Accessibility motion detection
  └── useSearchProgress.ts            # Real-time backend sync

/src/stores/
  └── animationStore.ts               # Zustand store for animation state

/src/types/
  └── animation.types.ts              # TypeScript interfaces

/src/styles/animation/
  ├── searchAnimation.css             # Component-specific styles
  └── animationUtils.css              # Reusable animation utilities
```

**File Responsibilities:**

**AISearchAnimation.tsx** - Main Component
- Receives props (query, searchType, callbacks)
- Orchestrates all child components
- Manages overall animation lifecycle
- Handles keyboard events and focus trap

**AnimationBackdrop.tsx** - Overlay
- Semi-transparent backdrop with blur
- Click-to-dismiss (if enabled)
- Responsive blur levels by device

**AnimationCard.tsx** - Modal Container
- Brand-aligned styling with shadows
- Responsive padding and sizing
- Houses all animation content

**SearchStage.tsx** - Stage Component
- Renders icon, title, sub-steps, connection line
- Manages stage-specific state (pending/active/complete)
- Handles stage transition animations

**useAnimationController.ts** - Core Logic Hook
```typescript
export const useAnimationController = (
  onComplete: () => void,
  estimatedDuration?: number
) => {
  const [currentStage, setCurrentStage] = useState(0);
  const [stageStatuses, setStageStatuses] = useState([...]);
  const [dynamicValues, setDynamicValues] = useState({});

  const startAnimation = useCallback(() => { ... });
  const progressToNextStage = useCallback(() => { ... });
  const handleError = useCallback((error, stage) => { ... });
  const cancelAnimation = useCallback(() => { ... });

  return {
    currentStage,
    stageStatuses,
    dynamicValues,
    startAnimation,
    progressToNextStage,
    handleError,
    cancelAnimation,
  };
};
```

### 10. User Experience Benefits & Business Value

#### User Experience Benefits

**Transparency & Trust Building**
- Users see exactly what's happening during search processing
- Demonstrates AI sophistication and data thoroughness (336K+ applications)
- Builds confidence through visible, intelligent process
- Reduces perceived wait time through engaging visual feedback

**Engagement & Retention**
- Keeps users engaged during 3-5 second wait period
- Prevents abandonment through continuous progress feedback
- Creates anticipation for results through staged reveal
- Transforms passive waiting into active observation

**Education & Value Communication**
- Teaches users about AI search capabilities (semantic matching, filtering, ranking)
- Highlights platform intelligence and technological superiority
- Demonstrates value proposition (automated workflow that would take hours manually)
- Reinforces competitive differentiation from traditional portals

**Delight & Premium Feel**
- Smooth, choreographed animations create polished, professional experience
- Brand-aligned green color palette reinforces Planning Explorer identity
- Microinteractions (pulse, bounce, stagger) add personality
- Overall experience positions product as premium, AI-first solution

**Perceived Performance**
- Animation disguises actual processing time
- Makes 5-second search feel faster than 2-second blank loading screen
- Provides psychological "progress" even during complex operations
- Reduces user anxiety through visible activity

#### Business Value & Strategic Benefits

**Conversion Optimization**
- Increases free-to-paid conversion by showcasing AI capabilities
- Demonstrates value before results appear
- Creates "wow moment" that differentiates from competitors
- Builds trust that justifies premium pricing

**Brand Differentiation**
- Positions Planning Explorer as AI-first, innovative platform
- Contrasts sharply with basic loading spinners on competitor sites
- Creates memorable, shareable user experience
- Reinforces "intelligent" brand positioning

**User Retention**
- Reduces bounce rate during search
- Keeps users engaged long enough to see results
- Creates positive emotional association with product
- Encourages repeat usage through delightful experience

**Educational Marketing**
- Demonstrates AI capabilities without explicit marketing copy
- Shows (not tells) technological sophistication
- Educates users on value proposition passively
- Creates understanding of what justifies subscription cost

**Freemium Conversion Funnel**
- Free users see impressive AI animation, increasing upgrade intent
- Rate limit errors elegantly promote Professional plan
- Animation quality signals premium product worth paying for
- Creates desire for "unlimited" access to impressive technology

#### Success Metrics & KPIs

**User Engagement:**
- Animation completion rate > 95%
- Search session duration increase of 15%
- Reduced search abandonment rate by 30%

**Business Impact:**
- Free-to-paid conversion uplift of 8-12%
- User satisfaction score increase (NPS +10 points)
- Social sharing/word-of-mouth mentions increase

**Technical Performance:**
- Animation performance score > 90/100
- No increase in perceived wait time
- < 5ms impact on search response time

**Brand Perception:**
- "Innovative" brand attribute increase by 20%
- "Trustworthy AI" perception increase by 25%
- Competitive differentiation score improvement

## Example User Flow

1. User types: "Show me approved housing developments in Manchester over £5M"
2. Clicks search → Navigate to `/search?q=...`
3. Animation overlay appears
4. Stage 1 shows "Understanding Your Question" with parameters extracted
5. Stage 2 shows "Searching Planning Database" with live count
6. Stage 3 shows "Filtering Results" with applied filters
7. Stage 4 shows "Ranking Matches" with relevance scoring
8. Stage 5 completes → Animation fades out
9. Search results appear with highlighted matches

## Implementation Roadmap

### Phase 1: Core Animation Foundation (MVP) - Week 1
**Estimated Effort**: 3-4 days | **Priority**: HIGH

**Deliverables:**
- ✅ Basic 5-stage sequential animation with Planning Explorer brand colors
- ✅ Static sub-step messages with diamond bullets (◆)
- ✅ Simple Framer Motion transitions (fade, slide, scale)
- ✅ Desktop-first responsive design (680px modal)
- ✅ Cancel button functionality (appears at 8s)
- ✅ Basic accessibility (ARIA labels, keyboard nav)

**Components to Build:**
- AISearchAnimation.tsx (main orchestrator)
- SearchStage.tsx (stage rendering)
- SearchSubStep.tsx (sub-step items)
- animationStages.ts (configuration)

**Acceptance Criteria:**
- Animation runs smoothly at 60fps on desktop
- Transitions between stages feel natural and brand-aligned
- Cancel button allows graceful exit
- Basic screen reader support functional

---

### Phase 2: Enhanced Animations & Interactivity - Week 2
**Estimated Effort**: 3-4 days | **Priority**: HIGH

**Deliverables:**
- ✅ Dynamic value injection (application counts from backend)
- ✅ Advanced Framer Motion choreography (stagger, pulse, bounce)
- ✅ Connection line drawing animations with gradient
- ✅ Progress bar indicator (optional top bar)
- ✅ Stage counter badge ("Step 2 of 5")
- ✅ Mobile responsive optimization (all breakpoints)
- ✅ Adaptive timing based on actual API response

**New Components:**
- StageIcon.tsx (with pulse animation)
- ConnectionLine.tsx (SVG drawing effect)
- ProgressBar.tsx (top indicator)
- StageCounter.tsx (badge)

**Hooks to Build:**
- useAnimationController.ts (state management)
- useStageTransition.ts (progression logic)
- useAnimationTiming.ts (adaptive timing)

**Acceptance Criteria:**
- Dynamic counts update in real-time from backend
- Pulse and bounce animations enhance feel without distraction
- Mobile experience is optimized for performance
- Timing adapts to fast (<2s) and slow (>5s) responses

---

### Phase 3: Error Handling & Edge Cases - Week 3
**Estimated Effort**: 2-3 days | **Priority**: MEDIUM

**Deliverables:**
- ✅ Comprehensive error state UI for all error types
- ✅ Stage-specific error handling (connection, parsing, timeout)
- ✅ Retry and alternative action buttons
- ✅ Slow response handling (rotating messages, enhanced cancel)
- ✅ Fast response acceleration logic
- ✅ Rate limit error with upgrade CTA

**New Components:**
- ErrorDisplay.tsx (error state UI)
- CancelButton.tsx (standalone component)
- AnimationBackdrop.tsx (with click-to-dismiss)

**Acceptance Criteria:**
- All error types display appropriate UI
- Retry functionality works correctly
- Upgrade CTAs appear for rate limit errors
- Slow searches don't frustrate users
- Fast searches still show minimum animation

---

### Phase 4: Accessibility & Polish - Week 4
**Estimated Effort**: 2-3 days | **Priority**: MEDIUM

**Deliverables:**
- ✅ Full WCAG AA compliance (color contrast, focus indicators)
- ✅ Comprehensive screen reader announcements
- ✅ Reduced motion support (`prefers-reduced-motion`)
- ✅ Focus trap and keyboard navigation refinement
- ✅ Touch gesture support (swipe to dismiss)
- ✅ Performance optimization (GPU acceleration)

**Updates to All Components:**
- Add complete ARIA attributes
- Implement reduced motion alternatives
- Optimize animation performance
- Add comprehensive keyboard controls

**Acceptance Criteria:**
- WCAG AA compliance verified with automated tools
- Screen readers announce all state changes
- Reduced motion users get simplified experience
- Animation performs smoothly on mid-range devices

---

### Phase 5: Analytics & Optimization - Week 5
**Estimated Effort**: 2 days | **Priority**: LOW

**Deliverables:**
- ✅ Event tracking for animation interactions
- ✅ Performance monitoring and reporting
- ✅ A/B testing infrastructure for variations
- ✅ User feedback collection mechanism
- ✅ Analytics dashboard for success metrics

**Implementation:**
- Track animation completion rates
- Monitor stage-by-stage drop-off
- Measure perceived vs actual wait time
- Collect user sentiment data
- A/B test different timing configurations

**Acceptance Criteria:**
- All key metrics tracked and reportable
- A/B testing framework operational
- Performance monitoring alerts configured
- User feedback mechanism integrated

---

## Testing Strategy

### Unit Testing
- Component rendering tests (Jest + React Testing Library)
- Animation state transitions
- Timing calculations
- Error handling logic

### Integration Testing
- Full animation flow from start to completion
- Backend progress synchronization
- Error state transitions
- Accessibility compliance

### E2E Testing (Playwright)
- Complete user journey with animation
- Mobile responsiveness
- Keyboard navigation
- Screen reader compatibility

### Performance Testing
- Animation FPS monitoring
- Memory usage profiling
- Bundle size impact analysis
- Mobile device testing

### Visual Regression Testing
- Screenshot comparison for brand consistency
- Animation frame accuracy
- Responsive layout verification

---

## Technical Dependencies

**Required Libraries:**
- `framer-motion`: ^11.0.0 (animation orchestration)
- `lucide-react`: ^0.400.0 (icon library)
- `zustand`: ^4.5.0 (state management)
- `react-use`: ^17.5.0 (utility hooks)

**Development Dependencies:**
- `@testing-library/react`: ^14.0.0
- `@testing-library/jest-dom`: ^6.1.0
- `playwright`: ^1.40.0

**TypeScript Version**: 5.0+
**React Version**: 18.0+
**Next.js Version**: 14.0+

---

## Rollout Strategy

### Beta Testing (Week 6)
- Enable for 10% of users
- Collect feedback and metrics
- Monitor performance and errors
- Iterate based on feedback

### Gradual Rollout (Week 7-8)
- 25% → 50% → 75% → 100%
- Monitor KPIs at each stage
- Quick rollback capability if issues arise

### Feature Flags
- `ENABLE_SEARCH_ANIMATION`: Master toggle
- `ANIMATION_VARIANT`: A/B testing variants
- `FORCE_REDUCED_MOTION`: Testing flag

---

## Success Metrics & Monitoring

### Week 1 Post-Launch
- Animation completion rate > 90%
- Zero performance degradation
- < 1% error rate

### Month 1 Post-Launch
- Search abandonment reduction by 20%
- User satisfaction score increase (+5 NPS)
- Free-to-paid conversion uplift of 5%

### Quarter 1 Post-Launch
- Sustained engagement metrics
- Brand perception improvement
- Competitive differentiation validated

---

**Status**: ✅ Ready for Implementation
**Owner**: Frontend Team (Lead: TBD)
**Priority**: HIGH - Strategic UX Differentiator
**Total Estimated Effort**: 12-15 development days
**Target Launch**: Q4 2025

---

## Conclusion

This AI Search Animation feature represents a strategic investment in user experience that will:

1. **Differentiate Planning Explorer** as the most innovative, AI-first planning intelligence platform
2. **Build user trust** through transparency and visible intelligence
3. **Drive conversions** by showcasing premium AI capabilities to free users
4. **Enhance brand perception** as cutting-edge and user-focused
5. **Reduce churn** by creating delightful, memorable interactions

The carefully choreographed animation, brand-aligned design, and comprehensive error handling will transform a simple loading state into a powerful marketing and trust-building moment that reinforces Planning Explorer's position as the UK's leading AI-powered planning platform.

**This feature will significantly enhance Planning Explorer's perceived intelligence and provide a delightful, transparent user experience that differentiates it from traditional planning portals while driving measurable business outcomes.**
