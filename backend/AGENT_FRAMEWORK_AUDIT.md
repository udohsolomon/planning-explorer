# Agent Framework Audit Report
**Date**: October 7, 2025
**Status**: 🔴 **CRITICAL DISCREPANCIES FOUND**

---

## 🚨 Critical Discrepancies Identified

### **1. Embedding Model Mismatch** ✅ FIXED
**Severity**: HIGH
**Status**: RESOLVED

**Issue**:
- Agent tools used `sentence-transformers` library with 384-dimensional embeddings
- Actual project uses `OpenAI text-embedding-3-small` with 1536 dimensions

**Impact**:
- Vector search would fail due to dimension mismatch
- ES schema validation would reject 384-dim vectors

**Resolution**:
- ✅ Fixed `EmbeddingTool` in `ai_tools.py` to use OpenAI API
- ✅ Updated `ElasticsearchArchitectAgent` system prompt to reference 1536 dimensions

---

### **2. Supabase Configuration Mismatch** 🔴 NEW CRITICAL ISSUE
**Severity**: HIGH
**Status**: REQUIRES FIX

**Issue**:
- **Agent tools** reference: `settings.supabase_url` and `settings.supabase_key`
- **Actual config** uses: `settings.supabase_url` and `settings.supabase_service_key` (NOT `supabase_key`)

**Evidence from config.py** (lines 34-37):
```python
# Supabase Configuration (Legacy - will be removed)
supabase_url: Optional[str] = Field(default=None, alias="SUPABASE_URL")
supabase_key: Optional[str] = Field(default=None, alias="SUPABASE_ANON_KEY")
supabase_service_key: Optional[str] = Field(default=None, alias="SUPABASE_SERVICE_ROLE_KEY")
```

**Evidence from actual Supabase client** (line 59):
```python
client = create_client(
    settings.supabase_url,
    settings.supabase_key  # ← This is actually supabase_key from config
)
```

**BUT** - The actual project config shows it's marked as "Legacy - will be removed" and uses `supabase_key` (aliased from `SUPABASE_ANON_KEY`).

**Agent tools incorrectly reference**:
- `backend/app/agents/tools/supabase_tools.py:22`: Uses `settings.SUPABASE_URL` and `settings.SUPABASE_KEY`
- Should use: `settings.supabase_url` and `settings.supabase_key` (lowercase, no direct env var access)

**Impact**:
- Supabase tools will fail to initialize
- Agent operations requiring database access will crash

---

### **3. ES Index Name Hardcoding** 🟡 MODERATE ISSUE
**Severity**: MODERATE
**Status**: REQUIRES FIX

**Issue**:
- **Agent tools** hardcode index name as `"planning_applications"`
- **Actual config** defines: `settings.elasticsearch_index = "planning_applications"` (configurable via settings)

**Files affected**:
- `backend/app/agents/tools/elasticsearch_tools.py` - Hardcoded index names in multiple places

**Best Practice Violation**:
- Should reference `settings.elasticsearch_index` instead of hardcoding
- Breaks configurability for different environments (dev, staging, prod)

**Impact**:
- Cannot use different indices for testing vs production
- Violates DRY principle

---

### **4. Cache Service Missing** 🟡 MODERATE ISSUE
**Severity**: MODERATE
**Status**: INFORMATIONAL

**Issue**:
- **Search service** references `app.services.cache_manager` (lines 54, 125)
- **Agent framework** does NOT have cache integration
- Project explicitly states: "No Redis dependency" and "ES built-in caching"

**Observation**:
- Search service has fallback handling: `except ImportError: pass`
- Agents don't need external caching - ES handles this
- This is actually NOT a bug, just an architectural note

**Recommendation**:
- Document that agents rely on ES built-in caching
- No Redis or external cache service needed for agent operations

---

### **5. Sentence Transformers Import Still Present** 🟡 LOW ISSUE
**Severity**: LOW
**Status**: REQUIRES CLEANUP

**Issue**:
- `backend/app/agents/tools/ai_tools.py:11` still imports `sentence_transformers`
- No longer used after OpenAI migration

**Code** (line 11):
```python
from sentence_transformers import SentenceTransformer
```

**Impact**:
- Unused dependency
- Could cause confusion
- Adds unnecessary import overhead

**Fix**: Remove this import

---

### **6. Async Pattern Inconsistency** 🟢 MINOR ISSUE
**Severity**: LOW
**Status**: INFORMATIONAL

**Issue**:
- **Agent tools** use `async/await` throughout
- **Actual Supabase client** has some sync methods (lines 319-332, 344-353)

**Evidence from supabase.py**:
```python
async def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
    """Get user by JWT token"""
    self.ensure_connection()  # ← NOT awaited (line 319)

    try:
        self.client.auth.set_session(token, None)  # ← Sync call
```

**Observation**:
- Supabase client mixes async/sync patterns
- `ensure_connection()` is async but called without `await` in some places
- Agent tools assume fully async operations

**Impact**:
- Potential runtime warnings or failures
- Not critical but inconsistent

---

## 📋 Summary of Required Fixes

### **CRITICAL** (Must fix before deployment):

1. ✅ **Embedding model** - FIXED
2. 🔴 **Supabase settings reference** - FIX REQUIRED
   - Change `settings.SUPABASE_URL` → `settings.supabase_url`
   - Change `settings.SUPABASE_KEY` → `settings.supabase_key`

### **MODERATE** (Should fix):

3. 🟡 **ES index hardcoding** - Use `settings.elasticsearch_index`
4. 🟡 **Unused import cleanup** - Remove `sentence_transformers` import

### **INFORMATIONAL** (Document):

5. 🟢 **Cache service** - Document ES built-in caching strategy
6. 🟢 **Async patterns** - Note mixed async/sync in Supabase client

---

## 🔧 Recommended Fixes

### Fix 1: Supabase Settings (CRITICAL)

**File**: `backend/app/agents/tools/supabase_tools.py`

**Lines 21-23** - Change from:
```python
self.supabase_url = settings.SUPABASE_URL
self.supabase_key = settings.SUPABASE_KEY
self.client = create_client(self.supabase_url, self.supabase_key)
```

**To**:
```python
self.supabase_url = settings.supabase_url
self.supabase_key = settings.supabase_key
self.client = create_client(self.supabase_url, self.supabase_key)
```

### Fix 2: ES Index Configuration (MODERATE)

**File**: `backend/app/agents/tools/elasticsearch_tools.py`

**Multiple locations** - Change hardcoded `"planning_applications"` to `settings.elasticsearch_index`

Example (line ~50):
```python
# Before
index = index or "planning_applications"

# After
from app.core.config import settings
index = index or settings.elasticsearch_index
```

### Fix 3: Remove Unused Import (LOW)

**File**: `backend/app/agents/tools/ai_tools.py`

**Line 11** - Remove:
```python
from sentence_transformers import SentenceTransformer
```

---

## ✅ Verification Checklist

Before proceeding with Phase 2 completion:

- [x] Embedding model uses OpenAI (1536 dims) ✅
- [ ] Supabase settings use correct attribute names 🔴
- [ ] ES index name uses settings.elasticsearch_index 🟡
- [ ] Unused imports removed 🟡
- [ ] Cache strategy documented 🟢
- [ ] Async patterns reviewed 🟢

---

## 📊 Impact Assessment

### **If NOT Fixed**:

**Supabase Tools**:
- ❌ AttributeError: 'Settings' object has no attribute 'SUPABASE_URL'
- ❌ All Supabase CRUD, Auth, Storage operations will fail
- ❌ Agent workflow crashes when accessing database

**ES Tools**:
- ⚠️ Works but not configurable
- ⚠️ Cannot use different indices for environments
- ⚠️ Hardcoded values violate best practices

**Overall**:
- 🔴 **HIGH RISK** - Agent framework unusable for Supabase operations
- 🟡 **MODERATE RISK** - ES operations work but not production-ready

---

## 🎯 Action Plan

### Immediate Actions (Before continuing Phase 2):

1. **Fix Supabase settings reference** (5 min)
   - Update `supabase_tools.py` lines 21-23
   - Verify all references to Supabase config

2. **Fix ES index configuration** (10 min)
   - Update all 4 ES tools to use `settings.elasticsearch_index`
   - Add import statement for settings

3. **Remove unused imports** (2 min)
   - Remove `sentence_transformers` from `ai_tools.py`

4. **Run verification tests** (5 min)
   - Test Supabase tool initialization
   - Test ES tool queries
   - Verify no import errors

### Total Time: ~25 minutes

---

## 📝 Notes for Future Development

1. **Settings Pattern**: Always use `settings.attribute_name` (lowercase) not `settings.ATTRIBUTE_NAME`
2. **Configurable Values**: Never hardcode values that are defined in settings
3. **Import Cleanup**: Remove unused imports immediately after refactoring
4. **Async Consistency**: Ensure all async functions are properly awaited
5. **Testing**: Add integration tests for agent tools against actual services

---

## 🚀 Once Fixed

After applying the fixes above, the agent framework will be:
- ✅ **Fully compatible** with actual project configuration
- ✅ **Production-ready** for all database and search operations
- ✅ **Properly configurable** across environments
- ✅ **Clean and maintainable** with no technical debt

**Confidence Level**: 🟢 **VERY HIGH** (after fixes applied)
