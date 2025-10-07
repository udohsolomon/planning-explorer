# Debug Session - Planning Applications Route 500 Errors
**Session ID:** debug-planning-applications-route
**Started:** 2025-10-05 15:52
**Orchestrator:** Master Orchestrator
**Phase:** Debugging & Resolution

---

## 🎯 Problem Statement

After migrating `/authorities/[slug]` and `/locations/[slug]` to `/planning-applications/[slug]`, the entire frontend is returning HTTP 500 errors.

**Symptoms:**
- `/planning-applications/aberdeen` → 500
- `/authorities` → 500
- `/` (homepage) → 500
- Backend API works perfectly ✅

---

## 🔍 Root Cause Analysis

### Issues Found and Fixed:
1. ✅ Invalid metadata `keywords` format (array → string)
2. ✅ Invalid `columns` prop on `StatsCardGrid`
3. ✅ Invalid `variant` prop on `StatsCard`
4. ✅ Invalid `showMapLink` prop

### Issues Remaining:
- ❌ Frontend still returns 500 after fixes
- ❌ Entire site broken (including unmodified pages)

### Hypothesis:
The 500 errors on **ALL routes** (including homepage) suggest:
1. **Build cache corruption** - Stale .next directory
2. **Global import error** - Broken shared component
3. **TypeScript compilation failure** - Blocking entire build

---

## 📋 Debug Plan

### Phase 1: Isolate the Issue
**Goal:** Determine if the issue is specific to the new route or global

**Tasks:**
1. Kill and restart frontend dev server with clean cache
2. Check if homepage loads without errors
3. If homepage works → issue is in new route only
4. If homepage fails → issue is in shared components

### Phase 2: Minimal Reproduction
**Goal:** Create simplest possible version that works

**Tasks:**
1. Create minimal page.tsx with just static text
2. Test if it loads
3. Gradually add back complexity until error appears

### Phase 3: Component-by-Component Verification
**Goal:** Identify which specific component is broken

**Tasks:**
1. Comment out all imports except essential ones
2. Test route
3. Uncomment imports one by one
4. Identify failing import

### Phase 4: Fix and Validate
**Goal:** Apply permanent fix and verify

**Tasks:**
1. Fix identified issue
2. Test all routes
3. Run full test suite
4. Sign off

---

## 🛠️ Execution Strategy

### Immediate Actions:

**Action 1: Clean Restart**
```bash
# Kill frontend
pkill -f "next dev"

# Clean all caches
cd frontend
rm -rf .next node_modules/.cache

# Restart
npm run dev
```

**Action 2: Test Minimal Route**
Create `/planning-applications/test/page.tsx`:
```tsx
export default function TestPage() {
  return <div>Test Page Works</div>
}
```

Test: `curl http://localhost:3000/planning-applications/test`

**Action 3: Bisect the Component**
If minimal works, gradually add back:
1. Just imports
2. Basic structure
3. State hooks
4. API calls
5. Full component

---

## 🎯 Success Criteria

- ✅ Homepage loads without errors
- ✅ `/planning-applications/aberdeen` returns 200
- ✅ Page renders all sections
- ✅ No console errors
- ✅ Backend API integration works

---

## 📊 Status

**Current Phase:** Phase 1 - Isolation
**Blocked:** No
**Next Steps:** Clean restart and minimal reproduction

---

*Session managed by Master Orchestrator*
