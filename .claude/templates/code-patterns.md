# 💻 Code Patterns & Templates
*Reusable Code Structures for Planning Explorer*

## 🏗️ Architecture Patterns

### FastAPI Service Pattern
```python
# services/base_service.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

class BaseService(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def initialize(self):
        """Initialize service dependencies"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check for service"""
        pass

# services/search_service.py
class SearchService(BaseService):
    def __init__(self, es_client, ai_processor):
        super().__init__()
        self.es_client = es_client
        self.ai_processor = ai_processor

    async def initialize(self):
        await self.es_client.connect()
        self.logger.info("Search service initialized")

    async def hybrid_search(self, query: str, filters: Dict) -> Dict:
        """Hybrid keyword + semantic search"""
        try:
            # Generate embeddings for semantic search
            embeddings = await self.ai_processor.generate_embeddings(query)

            # Build Elasticsearch query
            es_query = {
                "query": {
                    "bool": {
                        "must": [
                            {"multi_match": {"query": query, "fields": ["description", "address"]}},
                            {"script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'description_embedding') + 1.0",
                                    "params": {"query_vector": embeddings}
                                }
                            }}
                        ],
                        "filter": self._build_filters(filters)
                    }
                }
            }

            response = await self.es_client.search(index="planning_applications", body=es_query)
            return self._format_response(response)

        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            raise
```

### Repository Pattern
```python
# repositories/base_repository.py
from typing import Optional, List, Dict, Any
from supabase import Client

class BaseRepository:
    def __init__(self, supabase: Client, table_name: str):
        self.supabase = supabase
        self.table_name = table_name

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new record"""
        response = self.supabase.table(self.table_name).insert(data).execute()
        return response.data[0] if response.data else None

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        response = self.supabase.table(self.table_name).select("*").eq("id", id).execute()
        return response.data[0] if response.data else None

    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update record"""
        response = self.supabase.table(self.table_name).update(data).eq("id", id).execute()
        return response.data[0] if response.data else None

    async def delete(self, id: str) -> bool:
        """Delete record"""
        response = self.supabase.table(self.table_name).delete().eq("id", id).execute()
        return len(response.data) > 0

# repositories/user_repository.py
class UserRepository(BaseRepository):
    def __init__(self, supabase: Client):
        super().__init__(supabase, "profiles")

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        response = self.supabase.table(self.table_name).select("*").eq("email", email).execute()
        return response.data[0] if response.data else None

    async def update_subscription(self, user_id: str, tier: str) -> bool:
        """Update user subscription tier"""
        data = {"subscription_tier": tier, "updated_at": "now()"}
        result = await self.update(user_id, data)
        return result is not None
```

### API Endpoint Pattern
```python
# routers/base_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging

class BaseRouter:
    def __init__(self, prefix: str, tags: List[str]):
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.logger = logging.getLogger(f"Router{prefix}")

    def handle_errors(self, func):
        """Decorator for consistent error handling"""
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ValueError as e:
                self.logger.warning(f"Validation error: {e}")
                raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
            except PermissionError as e:
                self.logger.warning(f"Permission denied: {e}")
                raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")
        return wrapper

# routers/search_router.py
class SearchRouter(BaseRouter):
    def __init__(self, search_service: SearchService):
        super().__init__("/api/search", ["search"])
        self.search_service = search_service
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/", response_model=SearchResponse)
        @self.handle_errors
        async def search(
            request: SearchRequest,
            user = Depends(get_current_user)
        ):
            """Perform hybrid search"""
            # Rate limiting check
            await self.check_rate_limit(user)

            # Execute search
            results = await self.search_service.hybrid_search(
                query=request.query,
                filters=request.filters
            )

            # Track usage
            await self.track_usage(user.id, "search")

            return SearchResponse(**results)
```

## 🎨 Frontend Patterns (shadcn/ui Enhanced)

### shadcn/ui Component Pattern
```tsx
// components/ui/BaseCard.tsx (shadcn/ui based)
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { VariantProps, cva } from 'class-variance-authority'

const cardVariants = cva(
  'transition-all duration-200 cursor-pointer',
  {
    variants: {
      variant: {
        default: 'hover:shadow-md',
        elevated: 'shadow-md hover:shadow-lg',
        outlined: 'border-2',
      },
      size: {
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
)

interface BaseCardProps extends VariantProps<typeof cardVariants> {
  children: React.ReactNode
  className?: string
  onClick?: () => void
  title?: string
}

export function BaseCard({
  children,
  className,
  onClick,
  title,
  variant,
  size,
}: BaseCardProps) {
  return (
    <Card
      className={cn(cardVariants({ variant, size }), className)}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {title && (
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent className={cn(!title && 'pt-6')}>
        {children}
      </CardContent>
    </Card>
  )
}

// components/application/ApplicationCard.tsx (shadcn/ui enhanced)
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Star, MapPin, Calendar, Building, ExternalLink } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ApplicationCardProps {
  application: Application
  onView?: (id: string) => void
  showAIInsights?: boolean
  className?: string
}

export function ApplicationCard({
  application,
  onView,
  showAIInsights = false,
  className
}: ApplicationCardProps) {
  const statusVariants = {
    approved: 'border-green-500 bg-green-50 text-green-700',
    pending: 'border-orange-500 bg-orange-50 text-orange-700',
    rejected: 'border-red-500 bg-red-50 text-red-700'
  }

  return (
    <Card className={cn('hover:shadow-lg transition-shadow duration-200 cursor-pointer group', className)}>
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start gap-4">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold leading-tight mb-1 group-hover:text-primary transition-colors">
              {application.address}
            </h3>
            <p className="text-sm text-muted-foreground">{application.authority}</p>
          </div>

          {application.opportunityScore && (
            <div className="flex items-center gap-1">
              <Star className="w-4 h-4 fill-current text-yellow-500" />
              <Badge variant="secondary" className="font-medium">
                {application.opportunityScore}
              </Badge>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="flex flex-wrap gap-3 text-sm text-muted-foreground mb-3">
          <div className="flex items-center gap-1">
            <Building className="w-4 h-4" />
            <span className="font-mono text-xs">{application.applicationId}</span>
          </div>
          <div className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            <span>{formatDate(application.submittedDate)}</span>
          </div>
        </div>

        <p className="text-sm leading-relaxed line-clamp-2 mb-4">
          {application.aiSummary || application.description}
        </p>

        <div className="flex justify-between items-center">
          <Badge
            variant="outline"
            className={cn(statusVariants[application.status])}
          >
            {application.status.toUpperCase()}
          </Badge>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => onView?.(application.id)}
            className="text-primary group-hover:bg-primary/10"
          >
            View Details
            <ExternalLink className="w-3 h-3 ml-1" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
```

### shadcn/ui Form Pattern
```tsx
// components/forms/SearchForm.tsx
'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import * as z from 'zod'

import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { toast } from '@/components/ui/use-toast'

const searchFormSchema = z.object({
  query: z
    .string()
    .min(2, 'Search query must be at least 2 characters')
    .max(500, 'Search query must be less than 500 characters'),
  authority: z.string().optional(),
  status: z.enum(['approved', 'pending', 'rejected', 'all']),
  dateFrom: z.string().optional(),
  dateTo: z.string().optional(),
})

type SearchFormValues = z.infer<typeof searchFormSchema>

interface SearchFormProps {
  onSubmit: (values: SearchFormValues) => void
  defaultValues?: Partial<SearchFormValues>
}

export function SearchForm({ onSubmit, defaultValues }: SearchFormProps) {
  const form = useForm<SearchFormValues>({
    resolver: zodResolver(searchFormSchema),
    defaultValues: {
      status: 'all',
      ...defaultValues,
    },
  })

  function handleSubmit(values: SearchFormValues) {
    try {
      onSubmit(values)
      toast({
        title: 'Search submitted',
        description: 'Your search has been executed successfully.',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to execute search. Please try again.',
        variant: 'destructive',
      })
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="query"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Search Query</FormLabel>
              <FormControl>
                <Input
                  placeholder="Enter your search query..."
                  {...field}
                />
              </FormControl>
              <FormDescription>
                Search for planning applications using keywords or natural language.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField
            control={form.control}
            name="authority"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Planning Authority</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select authority" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="manchester">Manchester City Council</SelectItem>
                    <SelectItem value="birmingham">Birmingham City Council</SelectItem>
                    <SelectItem value="liverpool">Liverpool City Council</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="status"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Application Status</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="all">All Statuses</SelectItem>
                    <SelectItem value="approved">Approved</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="rejected">Rejected</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <Button type="submit" className="w-full">
          Search Planning Applications
        </Button>
      </form>
    </Form>
  )
}
```

### MCP Server Integration Pattern
```typescript
// lib/hooks/useMCPIntegration.ts
import { useState, useCallback } from 'react'

interface MCPServerConfig {
  server: 'shadcn-ui' | 'playwright'
  command: string
  options?: Record<string, any>
}

export function useMCPIntegration() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const executeMCP = useCallback(async (config: MCPServerConfig) => {
    setIsLoading(true)
    setError(null)

    try {
      // Execute MCP server command
      const response = await fetch('/api/mcp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      })

      if (!response.ok) {
        throw new Error(`MCP server error: ${response.statusText}`)
      }

      const result = await response.json()
      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Specific MCP server helpers
  const generateShadcnComponent = useCallback(async (
    componentName: string,
    options: Record<string, any> = {}
  ) => {
    return executeMCP({
      server: 'shadcn-ui',
      command: 'generate',
      options: {
        component: componentName,
        ...options
      }
    })
  }, [executeMCP])

  const generatePlaywrightTest = useCallback(async (
    testName: string,
    component: string,
    options: Record<string, any> = {}
  ) => {
    return executeMCP({
      server: 'playwright',
      command: 'generate-test',
      options: {
        name: testName,
        component,
        ...options
      }
    })
  }, [executeMCP])

  const runPlaywrightTests = useCallback(async (
    options: Record<string, any> = {}
  ) => {
    return executeMCP({
      server: 'playwright',
      command: 'run-tests',
      options
    })
  }, [executeMCP])

  return {
    isLoading,
    error,
    executeMCP,
    generateShadcnComponent,
    generatePlaywrightTest,
    runPlaywrightTests
  }
}
```

### Custom Hook Pattern
```tsx
// hooks/useSearch.ts
interface UseSearchOptions {
  defaultMode?: SearchMode
  autoSearch?: boolean
  debounceMs?: number
}

export function useSearch(options: UseSearchOptions = {}) {
  const [query, setQuery] = useState('')
  const [searchMode, setSearchMode] = useState(options.defaultMode || 'semantic')
  const [filters, setFilters] = useState<SearchFilters>({})

  const searchMutation = useMutation({
    mutationFn: (params: SearchParams) => searchAPI.search(params),
    onError: (error) => {
      toast.error('Search failed: ' + error.message)
    }
  })

  const debouncedSearch = useDebouncedCallback(
    (searchQuery: string) => {
      if (searchQuery.length > 2) {
        searchMutation.mutate({
          query: searchQuery,
          mode: searchMode,
          filters
        })
      }
    },
    options.debounceMs || 300
  )

  useEffect(() => {
    if (options.autoSearch) {
      debouncedSearch(query)
    }
  }, [query, searchMode, filters])

  return {
    query,
    setQuery,
    searchMode,
    setSearchMode,
    filters,
    setFilters,
    search: searchMutation.mutate,
    results: searchMutation.data,
    isLoading: searchMutation.isPending,
    error: searchMutation.error
  }
}

// hooks/useAuth.ts
export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  const login = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password
    })
    if (error) throw error
  }

  const logout = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  }

  const register = async (email: string, password: string) => {
    const { error } = await supabase.auth.signUp({
      email,
      password
    })
    if (error) throw error
  }

  return {
    user,
    loading,
    login,
    logout,
    register,
    isAuthenticated: !!user
  }
}
```

### State Management Pattern
```tsx
// stores/searchStore.ts
interface SearchState {
  query: string
  searchMode: SearchMode
  filters: SearchFilters
  results: SearchResult[]
  totalResults: number
  isLoading: boolean
  error: string | null

  // Actions
  setQuery: (query: string) => void
  setSearchMode: (mode: SearchMode) => void
  setFilters: (filters: SearchFilters) => void
  search: () => Promise<void>
  clearResults: () => void
}

export const useSearchStore = create<SearchState>()(
  devtools(
    persist(
      (set, get) => ({
        query: '',
        searchMode: 'semantic',
        filters: {},
        results: [],
        totalResults: 0,
        isLoading: false,
        error: null,

        setQuery: (query) => set({ query }),
        setSearchMode: (searchMode) => set({ searchMode }),
        setFilters: (filters) => set({ filters }),

        search: async () => {
          const { query, searchMode, filters } = get()
          set({ isLoading: true, error: null })

          try {
            const response = await searchAPI.search({
              query,
              mode: searchMode,
              filters
            })

            set({
              results: response.applications,
              totalResults: response.total,
              isLoading: false
            })
          } catch (error) {
            set({
              error: error.message,
              isLoading: false
            })
          }
        },

        clearResults: () => set({
          results: [],
          totalResults: 0,
          error: null
        })
      }),
      {
        name: 'search-store',
        partialize: (state) => ({
          query: state.query,
          searchMode: state.searchMode,
          filters: state.filters
        })
      }
    )
  )
)
```

## 🤖 AI Integration Patterns

### AI Service Pattern
```python
# services/ai_service.py
class AIService:
    def __init__(self):
        self.openai = AsyncOpenAI()
        self.cache = CacheService()
        self.metrics = MetricsCollector()

    async def process_with_cache(
        self,
        operation: str,
        input_data: Any,
        cache_ttl: int = 3600
    ) -> Any:
        """Generic cached AI operation"""
        cache_key = f"ai:{operation}:{hash(str(input_data))}"

        # Check cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            await self.metrics.track("cache_hit", operation)
            return cached_result

        # Execute AI operation
        start_time = time.time()
        try:
            result = await self._execute_operation(operation, input_data)

            # Cache result
            await self.cache.set(cache_key, result, cache_ttl)

            # Track metrics
            await self.metrics.track("ai_operation", {
                "operation": operation,
                "duration": time.time() - start_time,
                "tokens": result.get("usage", {}).get("total_tokens", 0)
            })

            return result

        except Exception as e:
            await self.metrics.track("ai_error", {"operation": operation, "error": str(e)})
            raise

    async def _execute_operation(self, operation: str, input_data: Any) -> Any:
        """Execute specific AI operation"""
        if operation == "summarize":
            return await self._summarize(input_data)
        elif operation == "score":
            return await self._score_opportunity(input_data)
        elif operation == "embeddings":
            return await self._generate_embeddings(input_data)
        else:
            raise ValueError(f"Unknown operation: {operation}")
```

### Prompt Engineering Pattern
```python
# prompts/templates.py
class PromptTemplate:
    def __init__(self, template: str, variables: List[str]):
        self.template = template
        self.variables = variables

    def format(self, **kwargs) -> str:
        """Format template with variables"""
        missing = set(self.variables) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing variables: {missing}")

        return self.template.format(**kwargs)

# Opportunity scoring prompt
OPPORTUNITY_SCORING = PromptTemplate(
    template=\"\"\"
    Analyze this UK planning application and provide opportunity scoring:

    Application Details:
    - ID: {application_id}
    - Address: {address}
    - Description: {description}
    - Authority: {authority}
    - Type: {application_type}

    Analyze across four dimensions (0-100 scale):

    1. Approval Probability:
       - Authority track record: {authority_approval_rate}%
       - Application type success rate
       - Policy compliance indicators
       - Community impact assessment

    2. Market Potential:
       - Location desirability
       - Market demand indicators
       - Competition analysis
       - Growth potential

    3. Project Viability:
       - Technical feasibility
       - Scale appropriateness
       - Timeline realism
       - Resource requirements

    4. Strategic Fit:
       - Market trends alignment
       - Innovation opportunity
       - Risk/reward balance
       - Future growth potential

    Provide:
    - Score for each dimension (0-100)
    - Overall weighted score
    - Key rationale points (2-3 per dimension)
    - Risk factors identified
    - Opportunity highlights
    \"\"\",
    variables=[
        "application_id", "address", "description",
        "authority", "application_type", "authority_approval_rate"
    ]
)
```

## 🔐 Security Patterns

### Authentication Middleware
```python
# middleware/auth_middleware.py
class AuthMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, request: Request, call_next):
        # Skip auth for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)

        # Extract and validate token
        token = self._extract_token(request)
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )

        try:
            # Verify token
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            # Check expiration
            if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token expired"}
                )

            # Add user to request state
            request.state.user = payload

        except JWTError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )

        return await call_next(request)

    def _is_public_endpoint(self, path: str) -> bool:
        public_paths = ["/", "/health", "/docs", "/auth/login", "/auth/register"]
        return any(path.startswith(p) for p in public_paths)

    def _extract_token(self, request: Request) -> Optional[str]:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]
        return None
```

### Input Validation Pattern
```python
# models/validators.py
from pydantic import BaseModel, validator, Field
from typing import Optional, List

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    search_mode: SearchMode = SearchMode.SEMANTIC
    size: int = Field(20, ge=1, le=100)
    from_: int = Field(0, ge=0, alias="from")
    filters: Optional[SearchFilters] = None

    @validator('query')
    def validate_query(cls, v):
        # Prevent SQL injection
        dangerous_patterns = ['--', ';', 'DROP', 'DELETE', 'UPDATE']
        if any(pattern.lower() in v.lower() for pattern in dangerous_patterns):
            raise ValueError('Invalid characters in query')
        return v.strip()

    @validator('search_mode')
    def validate_search_mode(cls, v):
        if v not in ['keyword', 'semantic', 'ai']:
            raise ValueError('Invalid search mode')
        return v

class CreateAlertRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    search_params: dict
    notification_channels: List[str] = Field(default=['email'])
    frequency: str = Field('daily', regex='^(daily|weekly|monthly)$')

    @validator('notification_channels')
    def validate_channels(cls, v):
        valid_channels = ['email', 'slack', 'webhook']
        for channel in v:
            if channel not in valid_channels:
                raise ValueError(f'Invalid notification channel: {channel}')
        return v
```

## 📊 Testing Patterns

### Test Base Classes
```python
# tests/base.py
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

class BaseAPITest:
    @pytest.fixture
    async def client(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test-token"}

    @pytest.fixture
    def mock_user(self):
        return {
            "id": "test-user-id",
            "email": "test@example.com",
            "subscription_tier": "professional"
        }

class BaseServiceTest:
    @pytest.fixture
    def mock_es_client(self):
        return AsyncMock()

    @pytest.fixture
    def mock_supabase(self):
        return AsyncMock()

    @pytest.fixture
    def mock_ai_service(self):
        mock = AsyncMock()
        mock.generate_embeddings.return_value = [0.1] * 1536
        mock.calculate_opportunity_score.return_value = {
            "score": 85,
            "breakdown": {"approval_probability": 0.9}
        }
        return mock

# tests/test_search_api.py
class TestSearchAPI(BaseAPITest):
    @pytest.mark.asyncio
    async def test_search_success(self, client, auth_headers, mock_es_client):
        with patch('services.elasticsearch.client', mock_es_client):
            mock_es_client.search.return_value = {
                "hits": {"total": {"value": 10}, "hits": []},
                "aggregations": {}
            }

            response = await client.post(
                "/api/search",
                json={"query": "solar panels", "search_mode": "semantic"},
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert "applications" in data
            assert "total" in data
```

---

*These code patterns provide consistent, maintainable, and scalable implementation templates for the Planning Explorer platform.*