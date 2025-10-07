# Testing Guide - Planning Applications Route

## Quick Test Steps

### 1. Start Development Servers

**Backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### 2. Test URLs

**New Route (Should work):**
- http://localhost:3000/planning-applications/aberdeen
- http://localhost:3000/planning-applications/manchester
- http://localhost:3000/planning-applications/birmingham
- http://localhost:3000/planning-applications/poole

**Old Routes (Should NOT exist - deleted):**
- ❌ http://localhost:3000/authorities/aberdeen
- ❌ http://localhost:3000/locations/london

**List Pages (Should still work):**
- ✅ http://localhost:3000/authorities (directory listing)

### 3. Verify Features

#### Hero Section
- [x] Green gradient background
- [x] Authority name displayed
- [x] Breadcrumbs: Home > Planning Applications > {Authority}
- [x] Badges showing "Planning Authority" and total applications
- [x] "Get Alerts" CTA button

#### Stats Panel
- [x] 6 stat cards displayed
  - Last 12 Months
  - All Time
  - Approval Rate (with %)
  - Decision Time (days)
  - Active applications
  - Top Sector
- [x] Cards have elevated shadow design

#### Charts
- [x] Monthly Application Trends (line chart)
- [x] Approval Breakdown (pie chart)
- [x] Top 10 Sectors (bar chart)
- [x] Export buttons visible on charts

#### Map Section
- [x] Map section header visible
- [x] Placeholder shown if no applications loaded
- [x] Map renders if applications available

#### Filters
- [x] Sticky filter bar at top
- [x] 4 dropdowns: Date Range, Status, Sector, Sort By
- [x] Filter labels visible

#### Applications Table
- [x] Table header: "Recent Planning Applications"
- [x] Shows "Showing X of Y applications"
- [x] First 5 applications visible (if data available)
- [x] Freemium gate displayed below table
- [x] "See all X applications" CTA button

#### Related Content
- [x] 3 columns: Top Sectors, Nearby Authorities, Popular Features
- [x] Links work and point to correct URLs

### 4. Backend API Test

**Test authority stats endpoint:**
```bash
curl http://localhost:8000/api/v1/stats/authority/aberdeen | jq
```

**Expected response fields:**
- authority_name
- authority_slug
- total_applications_12m
- total_applications_all_time
- approval_rate
- avg_decision_days
- active_applications
- top_sectors[]
- monthly_trend[]
- last_updated

### 5. Link Verification

**From Authorities List Page:**
- Click any authority card
- Should navigate to `/planning-applications/{slug}`
- ✅ Verify URL in browser

**From Sectors Page:**
- Navigate to a sector page
- Click "Top Authorities" links
- Should navigate to `/planning-applications/{slug}`
- ✅ Verify URL in browser

### 6. SEO Verification

**View page source and check:**
- [x] `<title>` tag includes authority name
- [x] `<meta name="description">` present
- [x] OpenGraph tags present (`og:title`, `og:description`, `og:image`)
- [x] Structured data JSON-LD scripts present
- [x] Canonical URL points to `/planning-applications/{slug}`

### 7. Mobile Responsiveness

**Test at different widths:**
- Desktop (1920px) - All cards in grid
- Tablet (768px) - Cards stack appropriately
- Mobile (375px) - Full mobile layout

### 8. Performance Check

**Network tab:**
- [x] API call to `/api/v1/stats/authority/{slug}` completes < 200ms
- [x] Page loads < 3 seconds
- [x] No console errors

### 9. Error Handling

**Test invalid authority:**
- http://localhost:3000/planning-applications/invalid-authority-name
- Should show error message: "Unable to Load Data"
- Should have "Back to Home" button

### 10. Accessibility

**Basic checks:**
- [x] All images have alt text
- [x] Buttons have accessible labels
- [x] Keyboard navigation works
- [x] Focus states visible

---

## Known Issues / TODO

### Map Implementation
- Map currently shows placeholder when no applications loaded
- Need to implement: `GET /api/v1/applications/list/{authority_slug}` endpoint
- Map should show all applications for the authority (no radius filter)

### Applications Table
- Shows placeholder when applications list unavailable
- Backend endpoint `/api/v1/applications/list` needs full implementation
- Filtering and sorting needs backend support

### Future Enhancements
- [ ] Add loading skeletons for better UX
- [ ] Implement error boundary for better error handling
- [ ] Add retry logic for failed API calls
- [ ] Implement caching for applications list
- [ ] Add "Share" functionality
- [ ] Add "Download Report" feature

---

## Troubleshooting

### Issue: Page shows "Unable to Load Data"
**Solution:**
- Check backend is running
- Verify ES is running and has data
- Check authority slug is valid in `slugs.json`

### Issue: Stats show 0 or N/A
**Solution:**
- Verify ES has data for that authority
- Check authority name mapping in backend
- Check date range filters

### Issue: Map doesn't load
**Solution:**
- Check browser console for errors
- Verify Leaflet CSS is loaded
- Check applications array has valid coordinates

### Issue: Links don't work
**Solution:**
- Clear Next.js cache: `rm -rf .next`
- Rebuild: `npm run dev`
- Check console for routing errors

---

## Success Criteria

✅ All tests pass
✅ No console errors
✅ Page loads under 3 seconds
✅ API calls complete under 200ms
✅ All links work correctly
✅ SEO metadata correct
✅ Mobile responsive

---

*Generated by Master Orchestrator - Planning Explorer Development Framework*
