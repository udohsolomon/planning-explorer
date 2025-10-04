# Elasticsearch Query Patterns - What Works vs What Doesn't

**Purpose:** Quick reference for correct ES query patterns based on live schema investigation
**Date:** 2025-10-01
**Schema Version:** planning_applications (2.3M+ documents)

---

## Pattern 1: Postcode Filtering

### ❌ WRONG - Returns 0 Results
```json
{
  "query": {
    "bool": {
      "filter": [
        {
          "wildcard": {
            "postcode": "BH15*"
          }
        }
      ]
    }
  }
}
```
**Why it fails:** `postcode` is analyzed text field, wildcard needs exact match

### ✅ CORRECT - Returns 892 Results
```json
{
  "query": {
    "bool": {
      "filter": [
        {
          "wildcard": {
            "postcode.keyword": "BH15*"
          }
        }
      ]
    }
  }
}
```
**Why it works:** `postcode.keyword` is exact-match keyword field

**Python Code:**
```python
# WRONG
{"wildcard": {"postcode": f"{postcode}*"}}

# CORRECT
{"wildcard": {"postcode.keyword": f"{postcode.upper()}*"}}
```

---

## Pattern 2: Development Type Filtering

### ❌ WRONG - Returns 0 Results
```json
{
  "query": {
    "bool": {
      "filter": [
        {
          "terms": {
            "app_type.keyword": ["residential", "commercial", "industrial"]
          }
        }
      ]
    }
  }
}
```
**Why it fails:** Model enum values don't exist in ES data

### ✅ CORRECT - Returns 1,047,647 Results
```json
{
  "query": {
    "bool": {
      "filter": [
        {
          "terms": {
            "app_type.keyword": ["Full", "Outline", "Trees"]
          }
        }
      ]
    }
  }
}
```
**Why it works:** Uses actual ES values

**Python Code:**
```python
# WRONG - Model enum values
{"terms": {"app_type.keyword": ["residential", "commercial"]}}

# CORRECT - ES actual values
{"terms": {"app_type.keyword": ["Full", "Outline"]}}

# BEST - Use mapping
DEV_TYPE_MAPPING = {
    'residential': ['Full', 'Outline'],
    'commercial': ['Advertising'],
    'industrial': ['Telecoms']
}
mapped_values = DEV_TYPE_MAPPING.get(dev_type, [])
{"terms": {"app_type.keyword": mapped_values}}
```

---

## Pattern 3: Status Filtering

### ⚠️ INCOMPLETE - Missing 371K Documents
```json
{
  "query": {
    "bool": {
      "filter": [
        {
          "terms": {
            "app_state.keyword": ["Permitted", "Granted", "Decided"]
          }
        }
      ]
    }
  }
}
```
**Why incomplete:** "Decided" doesn't exist, "Conditions" is missing

### ✅ COMPLETE - Includes All Approved Applications
```json
{
  "query": {
    "bool": {
      "filter": [
        {
          "terms": {
            "app_state.keyword": ["Permitted", "Granted", "Conditions"]
          }
        }
      ]
    }
  }
}
```
**Why it works:** Includes "Conditions" (371K docs), removes non-existent "Decided"

**Python Code:**
```python
# WRONG - Missing Conditions, includes non-existent Decided
status_values = ['Permitted', 'Granted', 'Decided']

# CORRECT - Includes Conditions, removes Decided
status_values = ['Permitted', 'Granted', 'Conditions']
```

---

## Pattern 4: Authority Filtering

### ✅ CORRECT - Works as Expected
```json
{
  "query": {
    "bool": {
      "filter": [
        {
          "terms": {
            "area_name.keyword": ["Poole", "Bournemouth", "Christchurch"]
          }
        }
      ]
    }
  }
}
```
**Why it works:** Correct field name and keyword subfield

**Python Code:**
```python
# CORRECT
{"terms": {"area_name.keyword": authorities}}
```

---

## Pattern 5: Date Range Filtering

### ✅ CORRECT - Submission Date
```json
{
  "query": {
    "bool": {
      "filter": [
        {
          "range": {
            "start_date": {
              "gte": "2024-01-01",
              "lte": "2024-12-31"
            }
          }
        }
      ]
    }
  }
}
```
**Why it works:** Uses ES field name `start_date`, not model name `submission_date`

**Python Code:**
```python
# CORRECT - Use ES field name
{"range": {"start_date": {"gte": date_from, "lte": date_to}}}

# WRONG - Don't use model field name
{"range": {"submission_date": {"gte": date_from, "lte": date_to}}}
```

---

## Pattern 6: Decision Filtering

### ✅ CORRECT - Nested Field Access
```json
{
  "query": {
    "bool": {
      "filter": [
        {
          "terms": {
            "other_fields.decision.keyword": ["Granted", "Approved", "Refused"]
          }
        }
      ]
    }
  }
}
```
**Why it works:** Uses nested field path with `.keyword` subfield

**Python Code:**
```python
# CORRECT
{"terms": {"other_fields.decision.keyword": decision_values}}

# WRONG - Missing other_fields prefix
{"terms": {"decision.keyword": decision_values}}
```

---

## Pattern 7: Hybrid Status + Decision Filtering

### ✅ CORRECT - Combines app_state and decision
```json
{
  "query": {
    "bool": {
      "filter": [
        {
          "bool": {
            "should": [
              {
                "terms": {
                  "app_state.keyword": ["Permitted", "Granted", "Conditions"]
                }
              },
              {
                "terms": {
                  "other_fields.decision.keyword": ["Approved", "Granted"]
                }
              }
            ],
            "minimum_should_match": 1
          }
        }
      ]
    }
  }
}
```
**Why it works:** Checks both status fields with OR logic

**Python Code:**
```python
# CORRECT
status_filter = {
    "bool": {
        "should": [
            {"terms": {"app_state.keyword": status_values}},
            {"terms": {"other_fields.decision.keyword": decision_values}}
        ]
    }
}
```

---

## Pattern 8: Semantic Search with Filters

### ✅ CORRECT - KNN + Filters
```json
{
  "knn": {
    "field": "description_embedding",
    "query_vector": [0.1, 0.2, ...],
    "k": 10,
    "num_candidates": 100,
    "filter": {
      "bool": {
        "must": [
          {"terms": {"app_state.keyword": ["Permitted", "Conditions"]}},
          {"wildcard": {"postcode.keyword": "BH15*"}}
        ]
      }
    }
  },
  "query": {
    "bool": {
      "should": [
        {
          "multi_match": {
            "query": "residential development",
            "fields": ["description^3", "address^2"]
          }
        }
      ],
      "filter": [
        {"terms": {"app_state.keyword": ["Permitted", "Conditions"]}},
        {"wildcard": {"postcode.keyword": "BH15*"}}
      ]
    }
  }
}
```
**Why it works:** Applies same filters to both KNN and keyword queries

**Python Code:**
```python
# CORRECT - Apply filters to both KNN and keyword
filter_clauses = self._build_filter_query(filters)

knn_query = {
    "field": "description_embedding",
    "query_vector": embedding,
    "k": k,
    "num_candidates": num_candidates,
    "filter": {"bool": {"must": filter_clauses}}  # Add to KNN
}

keyword_query = {
    "bool": {
        "should": [...],
        "filter": filter_clauses  # Add to keyword
    }
}
```

---

## Field Reference Quick Lookup

| Model Field | ES Field | Filter Type | Example |
|-------------|----------|-------------|---------|
| `postcode` | `postcode.keyword` | wildcard | `{"wildcard": {"postcode.keyword": "BH15*"}}` |
| `authority` | `area_name.keyword` | terms | `{"terms": {"area_name.keyword": ["Poole"]}}` |
| `status` | `app_state.keyword` | terms | `{"terms": {"app_state.keyword": ["Permitted"]}}` |
| `development_type` | `app_type.keyword` | terms | `{"terms": {"app_type.keyword": ["Full"]}}` |
| `decision` | `other_fields.decision.keyword` | terms | `{"terms": {"other_fields.decision.keyword": ["Granted"]}}` |
| `submission_date` | `start_date` | range | `{"range": {"start_date": {"gte": "2024-01-01"}}}` |
| `decision_date` | `decided_date` | range | `{"range": {"decided_date": {"lte": "2024-12-31"}}}` |
| `applicant_name` | `other_fields.applicant_name.keyword` | term/match | `{"match": {"other_fields.applicant_name": "Smith"}}` |

---

## Status Mapping Reference

| Model Status | ES app_state Values | ES decision Values |
|--------------|---------------------|-------------------|
| `approved` | `Permitted`, `Granted`, `Conditions` | `Approved`, `Granted`, `Application Permitted` |
| `rejected` | `Rejected`, `Refused` | `Refused`, `Rejected`, `Application Refused` |
| `under_consideration` | `Undecided`, `Unresolved`, `Referred` | - |
| `submitted` | `Pending`, `Registered` | - |
| `withdrawn` | `Withdrawn` | `Withdrawn`, `Application Withdrawn` |

---

## Development Type Mapping Reference

| Model Development Type | ES app_type Values |
|------------------------|-------------------|
| `residential` | `Full`, `Outline` |
| `commercial` | `Advertising` |
| `industrial` | `Telecoms` |
| `extension` | `Trees` |
| `change_of_use` | `Conditions`, `Amendment`, `Heritage` |
| `new_build` | `Full` |
| `other` | `Other` |

---

## Common Mistakes

### Mistake 1: Using Text Field for Exact Match
```python
# ❌ WRONG
{"term": {"postcode": "BH15 3PU"}}

# ✅ CORRECT
{"term": {"postcode.keyword": "BH15 3PU"}}
```

### Mistake 2: Using Model Field Names
```python
# ❌ WRONG
{"range": {"submission_date": {"gte": "2024-01-01"}}}

# ✅ CORRECT
{"range": {"start_date": {"gte": "2024-01-01"}}}
```

### Mistake 3: Using Model Enum Values
```python
# ❌ WRONG
{"terms": {"app_type.keyword": ["residential", "commercial"]}}

# ✅ CORRECT
{"terms": {"app_type.keyword": ["Full", "Outline", "Advertising"]}}
```

### Mistake 4: Forgetting Nested Field Prefix
```python
# ❌ WRONG
{"terms": {"decision.keyword": ["Approved"]}}

# ✅ CORRECT
{"terms": {"other_fields.decision.keyword": ["Approved"]}}
```

### Mistake 5: Case Sensitivity
```python
# ❌ WRONG - ES values are case-sensitive
{"terms": {"app_state.keyword": ["permitted", "granted"]}}

# ✅ CORRECT - Match ES case exactly
{"terms": {"app_state.keyword": ["Permitted", "Granted"]}}
```

---

## Testing Queries

### Test 1: Verify Postcode Filter Works
```bash
curl -u "elastic:PASSWORD" -k "https://95.217.117.251:9200/planning_applications/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "size": 0,
    "query": {
      "bool": {
        "filter": [{"wildcard": {"postcode.keyword": "BH15*"}}]
      }
    }
  }'

# Expected: {"hits": {"total": {"value": 892}}}
```

### Test 2: Verify Development Type Filter Works
```bash
curl -u "elastic:PASSWORD" -k "https://95.217.117.251:9200/planning_applications/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "size": 0,
    "query": {
      "bool": {
        "filter": [{"terms": {"app_type.keyword": ["Full", "Outline"]}}]
      }
    }
  }'

# Expected: {"hits": {"total": {"value": 1297623}}}
```

### Test 3: Verify Status Filter Includes Conditions
```bash
curl -u "elastic:PASSWORD" -k "https://95.217.117.251:9200/planning_applications/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "size": 0,
    "query": {
      "bool": {
        "filter": [{"terms": {"app_state.keyword": ["Permitted", "Granted", "Conditions"]}}]
      }
    }
  }'

# Expected: {"hits": {"total": {"value": 1543050}}}  (includes 371K Conditions)
```

---

## Quick Reference Card

**Remember:**
1. Always use `.keyword` for exact match filters (term, terms, wildcard, prefix)
2. Use ES field names, not model field names
3. Use ES actual values, not model enum values
4. Check nested fields use `other_fields.` prefix
5. ES values are case-sensitive - match exactly

**When in doubt:**
- Check ES_SCHEMA_ANALYSIS.md for field mappings
- Run aggregation to see actual values
- Test query against live ES first
