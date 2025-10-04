# AI Search Animation - Deployment Guide

## 📋 Pre-Deployment Checklist

### Environment Configuration
- [ ] Copy `.env.example` to `.env.production`
- [ ] Set `NEXT_PUBLIC_API_URL` to production API endpoint
- [ ] Set `NEXT_PUBLIC_WS_URL` to production WebSocket endpoint
- [ ] Configure analytics provider keys (GA4/Mixpanel/PostHog)
- [ ] Set Supabase production credentials
- [ ] Configure Sentry DSN for error tracking
- [ ] Verify all feature flags are set correctly

### Code Verification
- [ ] Run type checking: `npm run type-check`
- [ ] Run linting: `npm run lint`
- [ ] Run tests: `npm test` (in CI/CD environment)
- [ ] Run E2E tests: `npm run test:e2e`
- [ ] Build production bundle: `npm run build`
- [ ] Verify bundle size < 15KB for animation feature

### API Integration
- [ ] Backend API `/api/search` endpoint ready
- [ ] WebSocket `/ws/search/:requestId` endpoint ready
- [ ] API error codes mapped (400→parsing, 429→rate_limit, etc.)
- [ ] Request/response types match frontend types
- [ ] CORS configured for frontend domain
- [ ] Rate limiting configured on backend

### Performance
- [ ] Bundle size analyzed and optimized
- [ ] ErrorDisplay lazy-loaded
- [ ] Analytics code-split
- [ ] Icons lazy-loaded
- [ ] No memory leaks verified
- [ ] 60fps animation verified

### Security
- [ ] Environment variables secured (not in git)
- [ ] API authentication working
- [ ] HTTPS enforced
- [ ] WebSocket secure (WSS)
- [ ] XSS protection enabled
- [ ] CSRF protection enabled

---

## 🚀 Deployment Steps

### Step 1: Staging Deployment

```bash
# 1. Build for staging
npm run build

# 2. Deploy to staging environment
# (Using your deployment method: Vercel/Netlify/Docker)

# 3. Verify staging deployment
curl https://staging.planningexplorer.com/health
```

### Step 2: Smoke Tests

Run these tests on staging:

```bash
# 1. Test search animation
- Visit /search
- Enter query "approved housing in Manchester"
- Verify animation plays correctly
- Verify results display

# 2. Test error handling
- Simulate rate limit error
- Verify upgrade CTA shows
- Test retry functionality

# 3. Test cancellation
- Start search
- Wait for cancel button (8s)
- Click cancel
- Verify animation stops

# 4. Test keyboard accessibility
- Start search
- Press Tab key
- Verify focus trap works
- Press ESC key
- Verify animation cancels

# 5. Test WebSocket connection
- Open browser DevTools > Network > WS
- Start search
- Verify WebSocket messages received
```

### Step 3: Feature Flag Rollout

**Gradual Rollout Strategy:**

1. **5% of users** (Week 1)
   ```env
   NEXT_PUBLIC_ENABLE_AI_ANIMATION=true
   # Use feature flag service to enable for 5%
   ```

2. **Monitor metrics:**
   - Animation completion rate
   - Error rate
   - Bundle size impact
   - API response times
   - User feedback

3. **25% of users** (Week 2)
   - If metrics look good, increase to 25%

4. **100% rollout** (Week 3)
   - Full production rollout

### Step 4: Production Deployment

```bash
# 1. Merge to main branch
git checkout main
git merge develop
git push origin main

# 2. Tag release
git tag -a v1.0.0-animation -m "AI Search Animation Release"
git push origin v1.0.0-animation

# 3. Deploy to production
# (Automatic via CI/CD or manual deployment)

# 4. Verify production
curl https://api.planningexplorer.com/health
```

### Step 5: Post-Deployment Monitoring

**Monitor these metrics for 48 hours:**

1. **Performance Metrics**
   - Animation FPS (target: 60fps)
   - Bundle size (target: <15KB gzipped)
   - API response time (target: <2s 95th percentile)
   - WebSocket latency (target: <100ms)

2. **User Metrics**
   - Animation completion rate (target: >90%)
   - Cancellation rate (target: <10%)
   - Error rate (target: <1%)
   - Upgrade conversion from rate limit CTA

3. **Business Metrics**
   - Search engagement increase
   - User satisfaction scores
   - Support ticket volume
   - Feature adoption rate

---

## 📊 Monitoring Setup

### Analytics Events

The following events are tracked automatically:

**Animation Lifecycle:**
- `animation_started`
- `animation_stage_reached`
- `animation_completed`
- `animation_cancelled`

**Error Tracking:**
- `animation_error`
- `animation_retry`

**User Interactions:**
- `cancel_button_clicked`
- `error_action_clicked`
- `upgrade_cta_clicked`

**Performance:**
- `animation_performance`

### Error Tracking (Sentry)

Configure Sentry error boundaries:

```tsx
import * as Sentry from '@sentry/nextjs';

// In _app.tsx or layout.tsx
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
});
```

### Performance Monitoring

```tsx
// Track Web Vitals
export function reportWebVitals(metric) {
  if (process.env.NEXT_PUBLIC_ENABLE_WEB_VITALS === 'true') {
    analytics.track({
      name: 'web_vitals',
      properties: {
        name: metric.name,
        value: metric.value,
        label: metric.label,
      },
    });
  }
}
```

---

## 🔄 Rollback Procedures

### If Critical Issues Occur:

**Option 1: Feature Flag Disable**
```env
NEXT_PUBLIC_ENABLE_AI_ANIMATION=false
```
- Redeploy or update feature flag service
- Animation will be disabled immediately
- Users see fallback search experience

**Option 2: Git Revert**
```bash
# 1. Identify problematic commit
git log --oneline

# 2. Revert to previous version
git revert <commit-hash>

# 3. Deploy reverted version
git push origin main
```

**Option 3: Rollback to Previous Release**
```bash
# 1. Checkout previous tag
git checkout v0.9.0

# 2. Create rollback branch
git checkout -b rollback/v0.9.0

# 3. Deploy rollback
git push origin rollback/v0.9.0
```

### Rollback Triggers:

Immediate rollback if:
- Error rate >5%
- Animation causes page crashes
- Critical security vulnerability
- API overload/DDoS
- Bundle size impact >50KB

Gradual rollback if:
- Animation completion rate <70%
- High cancellation rate (>30%)
- Negative user feedback spike
- Performance degradation

---

## 🛠️ Troubleshooting

### Common Issues

**1. Animation not showing**
- Check `NEXT_PUBLIC_ENABLE_AI_ANIMATION` is true
- Verify API endpoint is reachable
- Check browser console for errors

**2. WebSocket connection fails**
- Verify WSS URL is correct
- Check CORS configuration
- Verify SSL certificate valid
- Fallback to polling should work

**3. High error rate**
- Check API error mapping
- Verify backend returns correct status codes
- Check network connectivity
- Review Sentry error logs

**4. Performance issues**
- Check bundle size: `npm run build`
- Verify lazy loading works
- Check FPS in DevTools Performance tab
- Review memory leaks

**5. Analytics not tracking**
- Verify analytics keys configured
- Check browser ad blockers
- Review analytics initialization
- Check network requests

---

## 📞 Support Contacts

**During Deployment:**
- DevOps Lead: [contact]
- Backend Team: [contact]
- Frontend Team: [contact]

**Post-Deployment:**
- On-call Engineer: [contact]
- Product Manager: [contact]

---

## ✅ Deployment Complete

After successful deployment:

1. **Update documentation**
   - Mark feature as production-ready
   - Update changelog
   - Create release notes

2. **Team communication**
   - Notify support team
   - Update customer success
   - Announce to users

3. **Archive deployment artifacts**
   - Save deployment logs
   - Archive test results
   - Document any issues

---

*Deployment guide for AI Search Animation feature*
*Planning Explorer v1.0*
