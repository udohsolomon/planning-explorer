# Planning Explorer - Component Tree Hierarchy

## Complete Component Structure

```
src/
├── app/
│   ├── layout.tsx                    # Root layout with providers
│   ├── page.tsx                      # Homepage
│   ├── globals.css                   # Global styles and design tokens
│   ├── services/
│   │   └── page.tsx                  # Services page
│   ├── about/
│   │   └── page.tsx                  # About page
│   ├── pricing/
│   │   └── page.tsx                  # Pricing page
│   └── faqs/
│       └── page.tsx                  # FAQs page
├── components/
│   ├── layout/
│   │   ├── Header.tsx                # Main site header
│   │   ├── Navigation.tsx            # Navigation component
│   │   ├── Footer.tsx                # Site footer
│   │   └── MobileMenu.tsx            # Mobile navigation menu
│   ├── ui/
│   │   ├── Button.tsx                # Custom button component
│   │   ├── Container.tsx             # Layout container
│   │   ├── Card.tsx                  # Reusable card component
│   │   ├── Input.tsx                 # Form input component
│   │   ├── Select.tsx                # Dropdown select component
│   │   └── Icon.tsx                  # Icon wrapper component
│   ├── sections/
│   │   ├── HeroSlider.tsx            # Main hero slider component
│   │   ├── ServiceHighlights.tsx     # Services overview section
│   │   ├── PricingPlans.tsx          # Pricing cards section
│   │   ├── Testimonials.tsx          # Customer testimonials
│   │   ├── HowItWorks.tsx            # Step-by-step process
│   │   ├── ContactForm.tsx           # Contact/inquiry form
│   │   └── SearchInterface.tsx       # Planning application search
│   └── providers/
│       ├── QueryProvider.tsx         # TanStack Query provider
│       └── StoreProvider.tsx         # Zustand store provider
├── lib/
│   ├── utils.ts                      # Utility functions
│   ├── api.ts                        # API client configuration
│   └── store.ts                      # Zustand store setup
├── types/
│   ├── planning.ts                   # Planning application types
│   ├── api.ts                        # API response types
│   └── ui.ts                         # UI component prop types
└── styles/
    └── components.css                # Component-specific styles
```

## Component Breakdown by Function

### Layout Components
- **Header**: Logo, navigation menu, user account icons
- **Navigation**: Main menu items (Services, About, FAQs, Pricing)
- **Footer**: Company info, social links, legal pages
- **MobileMenu**: Responsive mobile navigation overlay

### UI Components (shadcn/ui compatible)
- **Button**: Primary, secondary, outline variants matching Planning Insights style
- **Container**: Responsive layout container with max-width constraints
- **Card**: Service cards, pricing cards, testimonial cards
- **Input**: Form inputs with validation states
- **Select**: Dropdown components for filters
- **Icon**: Unified icon system with Lucide React

### Section Components
- **HeroSlider**: Dynamic background slider with overlays
- **ServiceHighlights**: Grid of service offerings
- **PricingPlans**: Pricing tier cards with features
- **Testimonials**: Customer feedback carousel
- **HowItWorks**: Step-by-step process visualization
- **ContactForm**: Service inquiry form with validation
- **SearchInterface**: Planning application search and filters

## Design System Integration

### Color Scheme Implementation
- Planning Primary: `#043F2E` (dark green)
- Planning Accent: `#027554` (medium green)
- Planning Bright: `#2DCC9E` (bright green)
- Planning Highlight: `#01CD52` (vibrant green)
- Planning Button: `#c8f169` (lime green)

### Typography System
- **Headings**: SUSE font family, 600 weight
- **Body Text**: DM Sans font family, 18px base size
- **Responsive Scale**: 80px desktop → 30px mobile for main headings

### Responsive Breakpoints
- Mobile: < 480px
- Tablet: 480px - 768px
- Desktop: 768px - 1024px
- Large Desktop: > 1024px
- Max Container: 1290px

### Animation System
- Hover transitions: 150ms ease-in-out
- Slider animations: Custom timing for layer transitions
- Micro-interactions: Subtle button hover effects
- Page transitions: 250ms ease-in-out

## State Management Structure

### Zustand Store Slices
- **UI State**: Mobile menu, modals, loading states
- **Planning Data**: Search results, filters, cached data
- **User State**: Authentication, preferences, recent searches
- **Form State**: Contact form, search form validation

### TanStack Query Keys
- `['planning-applications', filters]`: Search results
- `['planning-details', id]`: Individual application details
- `['statistics']`: Dashboard statistics
- `['user-preferences']`: User settings

## Integration Points for Backend

### API Endpoints (Prepared for Backend Integration)
- `GET /api/planning-applications` - Search planning applications
- `GET /api/planning-applications/:id` - Get application details
- `POST /api/contact` - Submit contact form
- `GET /api/statistics` - Get dashboard statistics
- `POST /api/ai-insights` - Get AI-powered insights

### Data Flow
1. User interactions trigger store updates
2. Store changes trigger API calls via TanStack Query
3. API responses update both cache and UI state
4. Components reactively update based on state changes

## Performance Optimization

### Code Splitting
- Page-level splitting with Next.js dynamic imports
- Component lazy loading for non-critical sections
- Vendor bundle optimization

### Image Optimization
- Next.js Image component for all images
- WebP format with fallbacks
- Responsive image sizes

### Bundle Analysis
- Tree shaking for unused code
- Component library selective imports
- CSS purging for production builds

This component tree ensures pixel-perfect reproduction of Planning Insights while maintaining scalability for Planning Explorer's enhanced AI features.