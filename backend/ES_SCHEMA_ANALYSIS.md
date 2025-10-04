# Elasticsearch Schema Analysis - Ground Truth Report
**Date:** 2025-10-01
**Live ES Endpoint:** https://95.217.117.251:9200/
**Index:** planning_applications
**Total Documents:** 2,326,495 (10,000+ visible)

---

## Executive Summary

This report documents the **ground truth** of the live Elasticsearch schema to identify root causes for test failures. Key findings:

### Critical Issues Identified:

1. **Postcode Filter Failure** - Filter uses wrong field path (missing `.keyword`)
2. **Development Type Filter Failure** - Filter uses model enum values instead of ES actual values
3. **Status Mapping Inconsistencies** - Complex mapping between `app_state` and model `status` enum
4. **Field Mapping Gaps** - Several fields in models don't match ES field names

---

## Part 1: Complete Field Mapping

### Core Fields

| Model Field | ES Field | ES Type | Notes |
|-------------|----------|---------|-------|
| `application_id` | `uid` / `name` / `reference` | text + keyword | Derived from multiple fields |
| `reference` | `reference` | text + keyword | Often null in data |
| `uid` | `uid` | text + keyword | Primary identifier |
| `name` | `name` | text + keyword | Alternative identifier |
| `authority` | `area_name` | text + keyword | ✅ Correct mapping |
| `address` | `address` | text + keyword | ✅ Correct |
| `postcode` | `postcode` | text + keyword | ⚠️ Filter needs `.keyword` |
| `description` | `description` | text + keyword | ✅ Correct |

### Status and Type Fields

| Model Field | ES Field | ES Type | Model Values | ES Actual Values |
|-------------|----------|---------|--------------|------------------|
| `status` | `app_state` | text + keyword | `approved`, `rejected`, `under_consideration`, `submitted`, `withdrawn`, `validated` | `Permitted`, `Undecided`, `Conditions`, `Rejected`, `Withdrawn`, `Unresolved`, `Referred` |
| `development_type` | `app_type` | text + keyword | `residential`, `commercial`, `industrial`, `mixed_use`, `extension`, `change_of_use`, `new_build` | `Full`, `Conditions`, `Trees`, `Outline`, `Amendment`, `Heritage`, `Advertising`, `Other`, `Telecoms` |
| `decision` | `other_fields.decision` | text + keyword | `approved`, `refused`, `withdrawn` | `Application Permitted`, `Granted`, `Approved`, `Refused`, `Withdrawn`, etc. (50+ variations) |

### Date Fields

| Model Field | ES Field | ES Type | Notes |
|-------------|----------|---------|-------|
| `submission_date` | `start_date` | date | ✅ Mapped correctly |
| `decision_date` | `decided_date` | date | ✅ Correct |
| `consultation_end_date` | `other_fields.consultation_end_date` | date | ✅ Nested field |
| `date_received` | `other_fields.date_received` | date | ✅ Nested field |
| `date_validated` | `other_fields.date_validated` | date | ✅ Nested field |

### Nested Fields (other_fields)

| Model Field | ES Path | ES Type | Notes |
|-------------|---------|---------|-------|
| `applicant_name` | `other_fields.applicant_name` | text + keyword | ✅ Correct |
| `agent_name` | `other_fields.agent_name` | text + keyword | ✅ Correct |
| `case_officer` | `other_fields.case_officer` | text + keyword | ✅ Correct |
| `ward_name` | `other_fields.ward_name` | text + keyword | ✅ Correct |

### AI Fields

| Model Field | ES Field | ES Type | Notes |
|-------------|----------|---------|-------|
| `opportunity_score` | `opportunity_score` | integer | ✅ Correct |
| `approval_probability` | `approval_probability` | float | ✅ Correct |
| `ai_summary` | `ai_summary` | text | ✅ Correct |
| `ai_confidence_score` | `ai_confidence_score` | float | ✅ Correct |

---

## Part 2: Actual Data Values Analysis

### 2.1 Status Values (app_state field)

**ES Actual Values** (from 2.3M+ documents):

| ES Value | Document Count | Model Mapping | Correct? |
|----------|----------------|---------------|----------|
| `Permitted` | 1,171,940 | `approved` | ✅ Yes |
| `Undecided` | 486,395 | `under_consideration` | ✅ Yes |
| `Conditions` | 371,110 | ❌ **No mapping** | ❌ Missing |
| `Rejected` | 184,421 | `rejected` | ✅ Yes |
| `Withdrawn` | 102,854 | `withdrawn` | ✅ Yes |
| `Unresolved` | 7,835 | ❌ **No mapping** | ❌ Missing |
| `Referred` | 1,940 | ❌ **No mapping** | ❌ Missing |

**ISSUE:** `Conditions` (371K docs), `Unresolved` (7.8K docs), and `Referred` (1.9K docs) have **NO MODEL MAPPING**.

### 2.2 Development Type Values (app_type field)

**ES Actual Values** (from 2.3M+ documents):

| ES Value | Document Count | Model Enum Used | Correct? |
|----------|----------------|-----------------|----------|
| `Full` | 1,047,647 | `residential` | ❌ **Wrong** |
| `Conditions` | 331,988 | `change_of_use` | ❌ **Wrong** |
| `Trees` | 317,880 | `extension` | ❌ **Wrong** |
| `Outline` | 249,976 | ❌ **No mapping** | ❌ Missing |
| `Amendment` | 135,732 | ❌ **No mapping** | ❌ Missing |
| `Heritage` | 116,504 | `change_of_use` | ❌ **Wrong** |
| `Advertising` | 44,509 | `commercial` | ❌ **Wrong** |
| `Other` | 27,613 | ❌ **No mapping** | ❌ Missing |
| `Telecoms` | 23,280 | ❌ **No mapping** | ❌ Missing |

**CRITICAL ISSUE:** The model's `development_type` enum values (`residential`, `commercial`, etc.) **DO NOT EXIST IN ES DATA**. The filter is searching for values that don't exist!

### 2.3 Decision Values (other_fields.decision)

**Top ES Actual Values** (from 688K+ documents with decisions):

| ES Value | Document Count | Normalized To |
|----------|----------------|---------------|
| `Application Permitted` | 121,549 | `approved` |
| `Granted` | 109,014 | `approved` |
| `Approved` | 96,775 | `approved` |
| `Refused` | 38,865 | `refused` |
| `Withdrawn` | 38,245 | `withdrawn` |
| `Application Withdrawn` | 26,605 | `withdrawn` |
| `Application Refused` | 18,428 | `refused` |
| **50+ more variations** | 688,000+ total | - |

### 2.4 Postcode Values

**Sample ES Postcodes:**
- `BH15 3PU`
- `BH15 3ND`
- `BH14 9HZ`
- `BH11 9NB`
- `BH12 3EY`

**Field Structure:**
- ES Field: `postcode` (type: text with `.keyword` subfield)
- Format: Standard UK postcode format with space
- **Indexed:** Both as analyzed text AND as exact keyword

---

## Part 3: Filter Query Analysis

### 3.1 Postcode Filter - ROOT CAUSE IDENTIFIED

**Current Code** (`app/services/search.py` line 699):
```python
if filters.postcode:
    filter_clauses.append({
        "wildcard": {"postcode": f"{filters.postcode.upper()}*"}
    })
```

**Problem:** Uses text field instead of keyword field for wildcard matching.

**Test Results:**
- ❌ Query `{"wildcard": {"postcode": "BH15*"}}` → **0 results**
- ✅ Query `{"wildcard": {"postcode.keyword": "BH15*"}}` → **892 results**

**Fix Required:**
```python
if filters.postcode:
    filter_clauses.append({
        "wildcard": {"postcode.keyword": f"{filters.postcode.upper()}*"}  # Add .keyword
    })
```

### 3.2 Development Type Filter - ROOT CAUSE IDENTIFIED

**Current Code** (`app/services/search.py` line 607):
```python
if filters.development_types:
    filter_clauses.append({
        "terms": {"app_type.keyword": [dt.value for dt in filters.development_types]}
    })
```

**Problem:** Uses model enum values that **DON'T EXIST IN ES**.

**Test Results:**
- ❌ Query `{"terms": {"app_type.keyword": ["residential", "commercial"]}}` → **0 results**
- ✅ Query `{"terms": {"app_type.keyword": ["Full", "Outline"]}}` → **1,297,623 results**

**Fix Required:**
The `development_type` filter is **fundamentally misaligned**. There are two options:

**Option A:** Map model enum values to ES values
```python
# Map development_type enum to app_type ES values
DEV_TYPE_TO_APP_TYPE = {
    'residential': ['Full', 'Outline'],  # Most Full/Outline are residential
    'commercial': ['Advertising'],
    'extension': ['Trees'],  # Trees often involve extensions
    'change_of_use': ['Conditions', 'Amendment', 'Heritage'],
    'other': ['Other', 'Telecoms']
}

if filters.development_types:
    app_type_values = []
    for dt in filters.development_types:
        app_type_values.extend(DEV_TYPE_TO_APP_TYPE.get(dt.value, []))

    if app_type_values:
        filter_clauses.append({
            "terms": {"app_type.keyword": app_type_values}
        })
```

**Option B:** Stop using development_type filter entirely and use app_type directly
- Update model to expose `app_type` field directly
- Remove `development_type` enum or make it AI-derived field

**Recommendation:** Use Option A short-term, migrate to Option B long-term with AI classification.

### 3.3 Status Filter - PARTIALLY WORKING

**Current Code** (`app/services/search.py` lines 568-604):
```python
if filters.statuses:
    status_values = []
    decision_values = []

    for status in filters.statuses:
        if status.value == 'rejected':
            status_values.extend(['Rejected', 'Refused'])
            decision_values.extend(['Refused', 'Rejected'])
        elif status.value == 'approved':
            status_values.extend(['Permitted', 'Granted', 'Decided'])
            decision_values.extend(['Approved', 'Granted'])
        # ... etc
```

**Issues:**
1. Missing mapping for `Conditions` (371K documents)
2. Missing mapping for `Unresolved` (7.8K documents)
3. Missing mapping for `Referred` (1.9K documents)
4. `Decided` value in approved mapping doesn't exist in app_state

**Fix Required:**
```python
for status in filters.statuses:
    if status.value == 'rejected':
        status_values.extend(['Rejected', 'Refused'])
        decision_values.extend(['Refused', 'Rejected'])
    elif status.value == 'approved':
        status_values.extend(['Permitted', 'Granted'])  # Remove 'Decided'
        decision_values.extend(['Approved', 'Granted'])
    elif status.value == 'under_consideration':
        status_values.extend(['Undecided', 'Unresolved', 'Referred'])  # Add missing
    # ... etc
```

---

## Part 4: Sample Documents

### Document 1: Undecided Full Application
```json
{
    "_id": "4ChuRpEB6zk0AeBPgXUO",
    "app_state": "Undecided",
    "app_type": "Full",
    "area_name": "Poole",
    "postcode": "BH15 3ND",
    "address": "103 Foxholes Road, Poole, BH15 3ND",
    "description": "Single-storey side and rear extensions...",
    "start_date": "2024-06-12",
    "other_fields": {
        "application_type": "Householder",
        "status": "Registered",
        "applicant_name": "See source",
        "agent_company": "Roger Wilkinson Architectural...",
        "date_validated": "2024-06-18"
    }
}
```

**Field Analysis:**
- `app_state`: `Undecided` → Model maps to `under_consideration` ✅
- `app_type`: `Full` → Model incorrectly maps to `residential` ❌
- `postcode`: Has value, filter needs `.keyword` ❌
- `other_fields.application_type`: `Householder` (different from `app_type`)

### Document 2: Withdrawn Application
```json
{
    "_id": "4ihuRpEB6zk0AeBPgXUO",
    "app_state": "Withdrawn",
    "app_type": "Full",
    "area_name": "Poole",
    "postcode": "BH11 9NB",
    "description": "Erection of 324 dwellings...",
    "decided_date": "2024-06-28",
    "other_fields": {
        "decision": "Withdrawn",
        "status": "Decided",
        "n_dwellings": 324
    }
}
```

**Field Analysis:**
- `app_state`: `Withdrawn` → Model maps correctly ✅
- `other_fields.decision`: `Withdrawn` → Model maps correctly ✅
- `other_fields.status`: `Decided` (different from `app_state`)

### Document 3: Rejected Amendment
```json
{
    "_id": "5yhuRpEB6zk0AeBPgXUO",
    "app_state": "Rejected",
    "app_type": "Amendment",
    "area_name": "Poole",
    "postcode": "BH12 2LY",
    "decided_date": "2024-07-09",
    "other_fields": {
        "decision": "Refuse",
        "status": "Decided"
    }
}
```

**Field Analysis:**
- `app_state`: `Rejected` → Model maps correctly ✅
- `app_type`: `Amendment` → Model has NO MAPPING ❌
- `other_fields.decision`: `Refuse` → Model maps to `refused` ✅

### Document 4: Conditions Application
```json
{
    "_id": "8ShuRpEB6zk0AeBPgXUO",
    "app_state": "Conditions",
    "app_type": "Full",
    "area_name": "Poole",
    "postcode": "BH15 1HP",
    "other_fields": {
        "decision": "Grant with Conditions"
    }
}
```

**Field Analysis:**
- `app_state`: `Conditions` → Model has NO MAPPING ❌
- This represents **371,110 documents** (15.9% of total data)
- Likely should map to `approved` status

---

## Part 5: Root Cause Summary

### Priority 1: CRITICAL (Blocking Filters)

#### Issue 1.1: Postcode Filter Uses Wrong Field Path
- **Location:** `app/services/search.py:699`
- **Current:** `{"wildcard": {"postcode": "BH15*"}}`
- **Required:** `{"wildcard": {"postcode.keyword": "BH15*"}}`
- **Impact:** 100% of postcode filters return 0 results
- **Fix Effort:** 1 line change

#### Issue 1.2: Development Type Filter Uses Non-Existent Values
- **Location:** `app/services/search.py:607`
- **Current:** Filters for `["residential", "commercial", "industrial"]`
- **Actual ES Values:** `["Full", "Outline", "Trees", "Conditions", "Amendment", "Heritage", "Advertising", "Other", "Telecoms"]`
- **Impact:** 100% of development_type filters return 0 results
- **Fix Effort:** Medium - requires mapping table or model redesign

### Priority 2: HIGH (Missing Mappings)

#### Issue 2.1: Status "Conditions" Not Mapped
- **ES Value:** `Conditions` (371,110 documents - 15.9% of data)
- **Current Mapping:** None
- **Impact:** 371K documents excluded from status filters
- **Recommended Mapping:** `approved` (conditional approval)

#### Issue 2.2: Status "Unresolved" Not Mapped
- **ES Value:** `Unresolved` (7,835 documents)
- **Current Mapping:** None
- **Recommended Mapping:** `under_consideration`

#### Issue 2.3: Status "Referred" Not Mapped
- **ES Value:** `Referred` (1,940 documents)
- **Current Mapping:** None
- **Recommended Mapping:** `under_consideration`

### Priority 3: MEDIUM (Incorrect Mappings)

#### Issue 3.1: "Decided" Status Value Doesn't Exist
- **Location:** `app/services/search.py:577`
- **Current Code:** `status_values.extend(['Permitted', 'Granted', 'Decided'])`
- **Problem:** `Decided` does NOT exist in `app_state` field
- **Impact:** No matches for this term
- **Fix:** Remove `'Decided'` from mapping

---

## Part 6: Recommended Fixes

### Fix 1: Postcode Filter (CRITICAL - 1 minute)

**File:** `app/services/search.py`
**Line:** 699

**Before:**
```python
if filters.postcode:
    filter_clauses.append({
        "wildcard": {"postcode": f"{filters.postcode.upper()}*"}
    })
```

**After:**
```python
if filters.postcode:
    filter_clauses.append({
        "wildcard": {"postcode.keyword": f"{filters.postcode.upper()}*"}
    })
```

### Fix 2: Development Type Filter (CRITICAL - 30 minutes)

**File:** `app/services/search.py`
**Line:** 607

**Before:**
```python
if filters.development_types:
    filter_clauses.append({
        "terms": {"app_type.keyword": [dt.value for dt in filters.development_types]}
    })
```

**After:**
```python
# Add mapping constant at top of file
DEV_TYPE_TO_APP_TYPE_MAPPING = {
    'residential': ['Full', 'Outline'],
    'commercial': ['Advertising'],
    'industrial': ['Telecoms'],
    'extension': ['Trees'],
    'change_of_use': ['Conditions', 'Amendment', 'Heritage'],
    'mixed_use': ['Full', 'Outline'],  # Can't distinguish
    'new_build': ['Full'],
    'other': ['Other']
}

# Update filter logic
if filters.development_types:
    app_type_values = []
    for dt in filters.development_types:
        mapped_values = DEV_TYPE_TO_APP_TYPE_MAPPING.get(dt.value, [])
        app_type_values.extend(mapped_values)

    if app_type_values:
        # Remove duplicates
        app_type_values = list(set(app_type_values))
        filter_clauses.append({
            "terms": {"app_type.keyword": app_type_values}
        })
```

### Fix 3: Status Mappings (HIGH - 15 minutes)

**File:** `app/services/search.py`
**Lines:** 568-604

**Changes:**
1. Remove `'Decided'` from approved mapping (line 577)
2. Add `'Conditions'` to approved mapping
3. Add `'Unresolved'` and `'Referred'` to under_consideration mapping

**Updated Code:**
```python
for status in filters.statuses:
    if status.value == 'rejected':
        status_values.extend(['Rejected', 'Refused'])
        decision_values.extend(['Refused', 'Rejected'])
    elif status.value == 'approved':
        status_values.extend(['Permitted', 'Granted', 'Conditions'])  # Add Conditions, remove Decided
        decision_values.extend(['Approved', 'Granted'])
    elif status.value == 'under_consideration':
        status_values.extend(['Undecided', 'Unresolved', 'Referred'])  # Add Unresolved, Referred
    elif status.value == 'submitted':
        status_values.extend(['Pending', 'Registered'])
    elif status.value == 'withdrawn':
        status_values.append('Withdrawn')
        decision_values.append('Withdrawn')
```

---

## Part 7: Testing Validation

### Test Queries to Verify Fixes

#### Postcode Filter Test
```bash
# Should return ~892 results
curl -u "elastic:***" -k "https://95.217.117.251:9200/planning_applications/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "size": 0,
    "query": {
      "bool": {
        "filter": [
          {"wildcard": {"postcode.keyword": "BH15*"}}
        ]
      }
    }
  }'
```

#### Development Type Filter Test
```bash
# Should return 1M+ results for Full + Outline
curl -u "elastic:***" -k "https://95.217.117.251:9200/planning_applications/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "size": 0,
    "query": {
      "bool": {
        "filter": [
          {"terms": {"app_type.keyword": ["Full", "Outline"]}}
        ]
      }
    }
  }'
```

#### Status Filter Test
```bash
# Should return 1.5M+ results (Permitted + Granted + Conditions)
curl -u "elastic:***" -k "https://95.217.117.251:9200/planning_applications/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "size": 0,
    "query": {
      "bool": {
        "filter": [
          {
            "bool": {
              "should": [
                {"terms": {"app_state.keyword": ["Permitted", "Granted", "Conditions"]}}
              ]
            }
          }
        ]
      }
    }
  }'
```

---

## Part 8: Long-Term Recommendations

### Recommendation 1: Restructure Development Type Classification

**Problem:** `app_type` field contains UK planning application types (Full, Outline, etc.), NOT development types (residential, commercial).

**Solution:**
1. **Rename Model Field:** `development_type` → `application_type`
2. **Update Enum Values:** Match ES values exactly (`Full`, `Outline`, `Trees`, etc.)
3. **Add AI-Derived Field:** `ai_development_classification` with values like `residential`, `commercial`
4. **Use AI Processing:** Classify applications based on description + context

### Recommendation 2: Normalize Status Values at Index Time

**Problem:** Too many status variations cause complex mapping logic.

**Solution:**
1. Add `normalized_status` field to ES during indexing
2. Map all app_state variations to standard enum during indexing
3. Simplify filter logic in search service

### Recommendation 3: Add Postcode Validation

**Problem:** Postcode filter currently uses uppercase + wildcard without validation.

**Solution:**
1. Validate UK postcode format before querying
2. Extract outward code (first part) for broader searches
3. Support both partial and full postcode searches

### Recommendation 4: Create Field Mapping Documentation

**Problem:** Disconnect between model fields and ES fields causes confusion.

**Solution:**
1. Generate automatic mapping documentation from code
2. Add comments in model classes showing ES field names
3. Create validation tests that verify mappings against live ES

---

## Appendix A: ES Field Type Reference

### Text vs Keyword Fields

Elasticsearch creates dual mappings for most text fields:

- **text**: Analyzed for full-text search (lowercase, tokenized, stemmed)
- **keyword**: Exact match for filtering, aggregations, sorting

**Example:**
```json
"postcode": {
    "type": "text",              // For search: "find BH15"
    "fields": {
        "keyword": {
            "type": "keyword"    // For filter: "exactly BH15 3PU"
        }
    }
}
```

**Usage Rules:**
- Use **text field** for: `match`, `multi_match`, `query_string` queries
- Use **keyword field** for: `term`, `terms`, `wildcard`, `prefix`, sorting, aggregations

### Nested vs Object Fields

- **Object fields** (`other_fields`): Flattened at index time, fields accessible via dot notation
- **Nested fields**: Maintain array structure, require nested queries

In this schema, `other_fields` is an **object**, so access via:
- `other_fields.decision.keyword`
- `other_fields.applicant_name.keyword`

---

## Appendix B: Complete app_state Distribution

| app_state Value | Document Count | Percentage | Model Mapping | Status |
|----------------|----------------|------------|---------------|--------|
| Permitted | 1,171,940 | 50.4% | approved | ✅ OK |
| Undecided | 486,395 | 20.9% | under_consideration | ✅ OK |
| Conditions | 371,110 | 15.9% | ❌ **NONE** | ❌ FIX |
| Rejected | 184,421 | 7.9% | rejected | ✅ OK |
| Withdrawn | 102,854 | 4.4% | withdrawn | ✅ OK |
| Unresolved | 7,835 | 0.3% | ❌ **NONE** | ❌ FIX |
| Referred | 1,940 | 0.1% | ❌ **NONE** | ❌ FIX |
| **Total** | **2,326,495** | **100%** | - | - |

**Missing Mappings Impact:** 380,885 documents (16.4%) have no status mapping!

---

## Appendix C: Complete app_type Distribution

| app_type Value | Document Count | Percentage | Description |
|---------------|----------------|------------|-------------|
| Full | 1,047,647 | 45.0% | Full planning permission |
| Conditions | 331,988 | 14.3% | Discharge of conditions |
| Trees | 317,880 | 13.7% | Tree works |
| Outline | 249,976 | 10.7% | Outline planning permission |
| Amendment | 135,732 | 5.8% | Non-material amendments |
| Heritage | 116,504 | 5.0% | Listed building consent |
| Advertising | 44,509 | 1.9% | Advertisement consent |
| Other | 27,613 | 1.2% | Other application types |
| Telecoms | 23,280 | 1.0% | Telecoms/prior approval |
| **Total** | **2,295,129** | **98.6%** | (Some docs missing app_type) |

---

## Report End

**Author:** Elasticsearch Architect (AI Specialist)
**Reviewed:** Search Service Implementation
**Next Steps:** Apply recommended fixes in priority order
