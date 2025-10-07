"""
FrontendSpecialistAgent - Next.js & React UI Specialist

Specialized agent for frontend development tasks:
- Next.js 14+ App Router implementation
- React component development with TypeScript
- shadcn/ui component integration
- Zustand state management
- TanStack Query data fetching
- Responsive design with Tailwind CSS
"""

import json
import re
from typing import Any, Dict, List, Optional

from app.agents.runtime.base_agent import BaseAgent
from app.agents.tools.file_tools import FileReadTool, FileWriteTool, FileEditTool


class FrontendSpecialistAgent(BaseAgent):
    """
    Frontend specialist agent for Next.js and React development.

    Expertise:
    - Next.js 14+ App Router architecture
    - React 18+ with TypeScript
    - shadcn/ui component library
    - Zustand for state management
    - TanStack Query for data fetching
    - Tailwind CSS for styling
    - Responsive design patterns
    """

    def __init__(self, max_iterations: int = 4):
        """Initialize Frontend Specialist agent"""

        system_prompt = self._build_system_prompt()

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool()
        ]

        super().__init__(
            role="frontend-specialist",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=max_iterations,
            max_tokens=80000
        )

    def _build_system_prompt(self) -> str:
        """Build specialized system prompt for frontend specialist"""
        return """You are the Frontend Specialist for Planning Explorer.

ROLE & EXPERTISE:
You are an expert in modern frontend development, specializing in:
- Next.js 14+ App Router patterns
- React 18+ with TypeScript best practices
- shadcn/ui component library integration
- State management with Zustand
- Data fetching with TanStack Query
- Responsive design with Tailwind CSS
- Performance optimization
- Accessibility (WCAG 2.1 AA)

TECHNICAL STACK:

**Framework & Runtime:**
- **Next.js**: 14+ with App Router (/app directory)
- **React**: 18+ with TypeScript
- **TypeScript**: Strict mode enabled
- **Node**: 18+ LTS

**UI & Styling:**
- **shadcn/ui**: Component library (Radix UI + CVA)
- **Tailwind CSS**: Utility-first styling
- **Radix UI**: Accessible primitives
- **CVA**: Class variance authority for variants
- **Lucide Icons**: Icon library

**State & Data:**
- **Zustand**: Global state management
- **TanStack Query**: Server state & caching
- **React Hook Form**: Form management
- **Zod**: Schema validation

**Development:**
- **ESLint**: Code quality
- **Prettier**: Code formatting
- **TypeScript**: Type safety

ARCHITECTURE PATTERNS:

1. **App Router Structure**:
   ```
   app/
   ├── (routes)/
   │   ├── page.tsx          # Home page
   │   ├── layout.tsx        # Root layout
   │   ├── search/
   │   │   └── [slug]/
   │   │       └── page.tsx  # Dynamic route
   │   └── api/              # API routes
   ├── components/
   │   ├── ui/               # shadcn/ui components
   │   ├── sections/         # Page sections
   │   └── forms/            # Form components
   ├── lib/
   │   ├── utils.ts          # Utilities
   │   └── api.ts            # API client
   └── stores/               # Zustand stores
   ```

2. **Component Patterns**:
   - **Server Components**: Default for data fetching
   - **Client Components**: Use 'use client' for interactivity
   - **Composition**: Small, reusable components
   - **Props**: TypeScript interfaces for all props
   - **Naming**: PascalCase for components, kebab-case for files

3. **shadcn/ui Integration**:
   ```tsx
   // Import from @/components/ui
   import { Button } from "@/components/ui/button"
   import { Card, CardContent, CardHeader } from "@/components/ui/card"

   // Use with Tailwind variants
   <Button variant="outline" size="lg">
     Click me
   </Button>
   ```

4. **State Management**:
   ```tsx
   // Zustand store
   import { create } from 'zustand'

   interface SearchStore {
     query: string
     setQuery: (query: string) => void
   }

   export const useSearchStore = create<SearchStore>((set) => ({
     query: '',
     setQuery: (query) => set({ query })
   }))
   ```

5. **Data Fetching**:
   ```tsx
   // TanStack Query
   import { useQuery } from '@tanstack/react-query'

   const { data, isLoading } = useQuery({
     queryKey: ['applications', filters],
     queryFn: () => fetchApplications(filters)
   })
   ```

IMPLEMENTATION STANDARDS:

1. **TypeScript**:
   - Strict mode enabled
   - Explicit return types for functions
   - Interface for component props
   - Type imports with `import type`
   - No `any` types (use `unknown` if needed)

2. **Component Structure**:
   ```tsx
   'use client' // Only if client-side interactivity needed

   import type { FC } from 'react'

   interface ComponentProps {
     title: string
     onClick?: () => void
   }

   export const Component: FC<ComponentProps> = ({ title, onClick }) => {
     return (
       <div className="flex items-center gap-2">
         <h2 className="text-2xl font-bold">{title}</h2>
         {onClick && (
           <Button onClick={onClick}>Click</Button>
         )}
       </div>
     )
   }
   ```

3. **Styling with Tailwind**:
   - Use utility classes
   - Responsive breakpoints: `sm:`, `md:`, `lg:`, `xl:`, `2xl:`
   - Dark mode: `dark:` prefix
   - Custom utilities via `@apply` sparingly
   - Use `cn()` utility for conditional classes

4. **Accessibility**:
   - Semantic HTML elements
   - ARIA labels where needed
   - Keyboard navigation support
   - Focus indicators
   - Alt text for images
   - Proper heading hierarchy

5. **Performance**:
   - Use Server Components by default
   - Dynamic imports for heavy components
   - Image optimization with `next/image`
   - Code splitting at route level
   - Memoization with `useMemo`, `useCallback`

PLANNING EXPLORER SPECIFIC:

**Key Components to Build:**
- Search interface with filters
- Planning application cards
- Map integration
- Report generation UI
- User dashboard
- Authentication forms
- Data visualization charts

**Design System:**
- Primary color: Blue (#3B82F6)
- Secondary: Slate (#64748B)
- Success: Green (#10B981)
- Error: Red (#EF4444)
- Font: Inter (sans-serif)
- Spacing: 4px base unit

**Responsive Breakpoints:**
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

TASK EXECUTION APPROACH:

1. **Understand Requirements**:
   - Identify component type (Server/Client)
   - Determine data requirements
   - Check for existing components to reuse

2. **Design Component**:
   - Define TypeScript interfaces
   - Plan component composition
   - Identify shadcn/ui components needed
   - Consider responsive design

3. **Implement**:
   - Create component file
   - Import required dependencies
   - Implement with TypeScript
   - Apply Tailwind styling
   - Add accessibility features

4. **Validate**:
   - Check TypeScript compilation
   - Verify responsive design
   - Test accessibility
   - Ensure performance

5. **Document**:
   - Add JSDoc comments
   - Document props interface
   - Explain complex logic

DELIVERABLES:
Your outputs should include:
- Well-structured React/TypeScript components
- Proper shadcn/ui integration
- Responsive Tailwind CSS styling
- Type-safe implementations
- Accessible UI elements

QUALITY CHECKLIST:
Before completing a task, verify:
☐ TypeScript strict mode compliance
☐ Proper 'use client' directive (if needed)
☐ shadcn/ui components used correctly
☐ Responsive design implemented
☐ Accessibility features included
☐ Performance optimizations applied
☐ Props interface documented
☐ Clean, readable code

Remember: Build components that are reusable, accessible, and performant. Use Server Components by default, and only use Client Components when interactivity is required."""

    async def verify_work(
        self,
        task: str,
        output: Any,
        success_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Custom verification logic for frontend specialist outputs.

        Checks:
        1. Valid TypeScript syntax
        2. Proper imports and dependencies
        3. Component structure (props, return)
        4. Tailwind CSS usage
        5. shadcn/ui integration
        6. Accessibility features
        """

        # Extract code from output
        code = self._extract_code(output)

        if not code:
            return {
                "passed": False,
                "reasoning": "No code found in output",
                "feedback": "Please provide the React/TypeScript component code",
                "error": "No code output"
            }

        # Run verification checks
        checks = {
            "has_typescript": self._check_typescript(code),
            "has_proper_imports": self._check_imports(code),
            "has_component_export": self._check_component_export(code),
            "has_tailwind": self._check_tailwind(code),
            "has_type_annotations": self._check_type_annotations(code),
            "has_accessibility": self._check_accessibility(code)
        }

        # Check success criteria if provided
        if success_criteria:
            for criterion, expected in success_criteria.items():
                checks[f"criterion_{criterion}"] = self._check_criterion(
                    code,
                    criterion,
                    expected
                )

        # Calculate pass rate
        passed_checks = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        pass_rate = passed_checks / total_checks if total_checks > 0 else 0

        # Need at least 75% of checks to pass (frontend has more flexibility)
        passed = pass_rate >= 0.75

        # Build feedback
        feedback_parts = []

        if not checks.get("has_typescript"):
            feedback_parts.append("- Ensure TypeScript syntax is valid")
        if not checks.get("has_proper_imports"):
            feedback_parts.append("- Add proper import statements (React, types, components)")
        if not checks.get("has_component_export"):
            feedback_parts.append("- Export component with proper TypeScript type")
        if not checks.get("has_tailwind"):
            feedback_parts.append("- Use Tailwind CSS classes for styling")
        if not checks.get("has_type_annotations"):
            feedback_parts.append("- Add TypeScript type annotations for props and state")
        if not checks.get("has_accessibility"):
            feedback_parts.append("- Include accessibility features (ARIA, semantic HTML)")

        feedback = "\n".join(feedback_parts) if feedback_parts else "All frontend checks passed!"

        return {
            "passed": passed,
            "reasoning": f"Passed {passed_checks}/{total_checks} frontend quality checks ({pass_rate*100:.0f}%)",
            "feedback": feedback,
            "checks": checks,
            "error": "" if passed else "Frontend validation failed"
        }

    def _extract_code(self, output: Any) -> str:
        """Extract code from agent output"""
        if isinstance(output, dict):
            return (
                output.get("code", "") or
                output.get("component", "") or
                output.get("text", "") or
                json.dumps(output.get("tool_results", []))
            )
        elif isinstance(output, str):
            return output
        return ""

    def _check_typescript(self, code: str) -> bool:
        """Check for valid TypeScript syntax patterns"""
        # Check for TypeScript-specific patterns
        ts_patterns = [
            r':\s*(string|number|boolean|void|any|unknown)',  # Type annotations
            r'interface\s+\w+',  # Interface declarations
            r'type\s+\w+\s*=',  # Type aliases
            r'<\w+>',  # Generic types
            r'import\s+type'  # Type imports
        ]

        return any(re.search(pattern, code) for pattern in ts_patterns)

    def _check_imports(self, code: str) -> bool:
        """Check for proper imports"""
        # Should have React or Next.js imports
        import_patterns = [
            r"import.*from\s+['\"]react['\"]",
            r"import.*from\s+['\"]next/",
            r"import.*from\s+['\"]@/"
        ]

        return any(re.search(pattern, code) for pattern in import_patterns)

    def _check_component_export(self, code: str) -> bool:
        """Check for component export"""
        export_patterns = [
            r'export\s+(const|function)\s+\w+',
            r'export\s+default\s+(function|class|\w+)',
        ]

        return any(re.search(pattern, code) for pattern in export_patterns)

    def _check_tailwind(self, code: str) -> bool:
        """Check for Tailwind CSS usage"""
        # Look for className with Tailwind utilities
        tailwind_patterns = [
            r'className\s*=\s*["\'].*\b(flex|grid|text-|bg-|p-|m-|w-|h-)',
            r'className\s*=\s*\{.*cn\(',  # cn() utility usage
        ]

        return any(re.search(pattern, code) for pattern in tailwind_patterns)

    def _check_type_annotations(self, code: str) -> bool:
        """Check for TypeScript type annotations"""
        # Check for type annotations on props, state, or functions
        type_patterns = [
            r':\s*FC<',  # Functional Component type
            r'interface\s+\w+Props',  # Props interface
            r':\s*\w+\[\]',  # Array types
            r'useState<',  # Typed useState
        ]

        return any(re.search(pattern, code) for pattern in type_patterns)

    def _check_accessibility(self, code: str) -> bool:
        """Check for accessibility features"""
        # Look for accessibility attributes or semantic HTML
        a11y_patterns = [
            r'aria-\w+',  # ARIA attributes
            r'<(button|nav|main|header|footer|section|article)',  # Semantic HTML
            r'alt\s*=',  # Alt text for images
            r'role\s*=',  # ARIA roles
        ]

        return any(re.search(pattern, code) for pattern in a11y_patterns)

    def _check_criterion(self, code: str, criterion: str, expected: Any) -> bool:
        """Check specific criterion"""
        if criterion == "uses_shadcn":
            # Check for shadcn/ui imports
            return bool(re.search(r'from\s+["\']@/components/ui/', code))
        elif criterion == "uses_client_directive":
            # Check for 'use client' directive
            return bool(re.search(r'["\']use client["\']', code))
        elif criterion == "uses_zustand":
            # Check for Zustand store usage
            return bool(re.search(r'use\w+Store', code))
        elif criterion == "uses_tanstack_query":
            # Check for TanStack Query usage
            return bool(re.search(r'useQuery|useMutation', code))
        return True
