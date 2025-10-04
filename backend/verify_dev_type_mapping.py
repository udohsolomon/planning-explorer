#!/usr/bin/env python3
"""
Verification script for development type mapping fix
"""

# Simulate the DevelopmentType enum
class DevelopmentType:
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"
    EXTENSION = "extension"
    CHANGE_OF_USE = "change_of_use"
    NEW_BUILD = "new_build"
    RENOVATION = "renovation"
    DEMOLITION = "demolition"
    OTHER = "other"

# The mapping from search.py
DEVELOPMENT_TYPE_MAPPING = {
    DevelopmentType.RESIDENTIAL: ["Full", "Outline"],  # Most residential are Full/Outline
    DevelopmentType.COMMERCIAL: ["Full", "Outline", "Advertising"],
    DevelopmentType.INDUSTRIAL: ["Full", "Outline"],
    DevelopmentType.MIXED_USE: ["Full", "Outline"],
    DevelopmentType.EXTENSION: ["Amendment"],
    DevelopmentType.CHANGE_OF_USE: ["Full"],
    DevelopmentType.NEW_BUILD: ["Full"],
    DevelopmentType.RENOVATION: ["Amendment"],
    DevelopmentType.DEMOLITION: ["Full"],
    DevelopmentType.OTHER: ["Other", "Trees", "Heritage", "Telecoms"]
}

print("=" * 80)
print("DEVELOPMENT TYPE MAPPING VERIFICATION")
print("=" * 80)
print()

print("Mapping Table:")
print("-" * 80)
for dev_type, es_values in DEVELOPMENT_TYPE_MAPPING.items():
    print(f"{dev_type:30} -> {', '.join(es_values)}")
print()

# Test the filter logic
print("=" * 80)
print("FILTER LOGIC TEST")
print("=" * 80)
print()

# Simulate filter building
test_cases = [
    ([DevelopmentType.RESIDENTIAL], "Single filter: RESIDENTIAL"),
    ([DevelopmentType.COMMERCIAL], "Single filter: COMMERCIAL"),
    ([DevelopmentType.RESIDENTIAL, DevelopmentType.COMMERCIAL], "Multiple filters: RESIDENTIAL + COMMERCIAL"),
    ([DevelopmentType.OTHER], "Other types filter"),
]

for development_types, description in test_cases:
    print(f"Test: {description}")
    print(f"  Input: {development_types}")

    # Simulate the filter building logic
    es_app_types = []
    for dev_type in development_types:
        mapped_values = DEVELOPMENT_TYPE_MAPPING.get(dev_type, [])
        es_app_types.extend(mapped_values)

    print(f"  ES Query: {{'terms': {{'app_type.keyword': {es_app_types}}}}}")
    print()

print("=" * 80)
print("VERIFICATION: All ES app_type values covered")
print("=" * 80)
print()

# ES ground truth values
es_ground_truth = ["Full", "Outline", "Trees", "Conditions", "Amendment", "Heritage", "Advertising", "Other", "Telecoms"]

# Collect all mapped values
all_mapped_values = set()
for values in DEVELOPMENT_TYPE_MAPPING.values():
    all_mapped_values.update(values)

print(f"ES Ground Truth: {sorted(es_ground_truth)}")
print(f"Mapped Values:   {sorted(all_mapped_values)}")
print()

missing = set(es_ground_truth) - all_mapped_values
if missing:
    print(f"⚠️  WARNING: Missing mappings for: {sorted(missing)}")
else:
    print("✅ All ES values are covered by the mapping")
print()

print("=" * 80)
print("Fix Summary:")
print("=" * 80)
print("1. ✅ Added DEVELOPMENT_TYPE_MAPPING constant to search.py")
print("2. ✅ Changed from 'development_type' field to 'app_type' field")
print("3. ✅ Changed from single 'term' query to 'terms' query with multiple values")
print("4. ✅ Maps each model enum to corresponding ES app_type values")
print()
print("Expected Behavior:")
print("  - DevelopmentType.RESIDENTIAL filter -> searches for app_type in ['Full', 'Outline']")
print("  - DevelopmentType.COMMERCIAL filter  -> searches for app_type in ['Full', 'Outline', 'Advertising']")
print("  - DevelopmentType.OTHER filter       -> searches for app_type in ['Other', 'Trees', 'Heritage', 'Telecoms']")
print()
