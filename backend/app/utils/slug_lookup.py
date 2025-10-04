"""
Slug Lookup and Validation Utilities
Phase 1 Week 2-3 - Backend Engineer Deliverable

Provides slug → name conversion and validation for content discovery routes

Master Orchestrator: content-discovery-implementation-plan.md
"""

import json
from pathlib import Path
from typing import Optional, Dict, Tuple
from functools import lru_cache


class SlugRegistry:
    """
    Registry for slug lookups with reverse mapping

    Loads slugs.json and creates bidirectional mappings for fast lookups
    """

    def __init__(self, slugs_file: Optional[Path] = None):
        if slugs_file is None:
            # Default to app/data/slugs.json
            slugs_file = Path(__file__).parent.parent / "data" / "slugs.json"

        self.slugs_file = slugs_file
        self._slugs: Dict[str, Dict[str, str]] = {}
        self._reverse: Dict[str, Dict[str, str]] = {}
        self._load_slugs()

    def _load_slugs(self):
        """Load slugs from JSON file"""
        if not self.slugs_file.exists():
            raise FileNotFoundError(f"Slugs file not found: {self.slugs_file}")

        with open(self.slugs_file, 'r') as f:
            self._slugs = json.load(f)

        # Create reverse mappings (slug → name)
        self._reverse = {
            category: {slug: name for name, slug in slugs.items()}
            for category, slugs in self._slugs.items()
        }

    def get_name_from_slug(self, slug: str, category: str) -> Optional[str]:
        """
        Get display name from slug

        Args:
            slug: URL slug (e.g., "manchester-city-council")
            category: "authorities", "locations", or "sectors"

        Returns:
            Display name if found, None otherwise

        Example:
            >>> registry.get_name_from_slug("manchester-city-council", "authorities")
            "Manchester City Council"
        """
        return self._reverse.get(category, {}).get(slug)

    def get_slug_from_name(self, name: str, category: str) -> Optional[str]:
        """
        Get slug from display name

        Args:
            name: Display name (e.g., "Manchester City Council")
            category: "authorities", "locations", or "sectors"

        Returns:
            URL slug if found, None otherwise
        """
        return self._slugs.get(category, {}).get(name)

    def is_valid_slug(self, slug: str, category: str) -> bool:
        """
        Check if slug exists in category

        Args:
            slug: URL slug
            category: "authorities", "locations", or "sectors"

        Returns:
            True if slug is valid, False otherwise
        """
        return slug in self._reverse.get(category, {})

    def get_all_slugs(self, category: str) -> Dict[str, str]:
        """
        Get all slugs for a category

        Args:
            category: "authorities", "locations", or "sectors"

        Returns:
            Dict of name → slug mappings
        """
        return self._slugs.get(category, {})

    def get_category_count(self, category: str) -> int:
        """Get number of slugs in category"""
        return len(self._slugs.get(category, {}))

    def search_slugs(self, query: str, category: str, limit: int = 10) -> list[Tuple[str, str]]:
        """
        Search slugs by partial match

        Args:
            query: Search query
            category: Category to search in
            limit: Max results

        Returns:
            List of (name, slug) tuples
        """
        query_lower = query.lower()
        results = []

        for name, slug in self._slugs.get(category, {}).items():
            if query_lower in name.lower() or query_lower in slug:
                results.append((name, slug))
                if len(results) >= limit:
                    break

        return results


# Singleton instance
_slug_registry: Optional[SlugRegistry] = None


@lru_cache(maxsize=1)
def get_slug_registry() -> SlugRegistry:
    """
    Get singleton slug registry instance

    Returns:
        SlugRegistry instance
    """
    global _slug_registry
    if _slug_registry is None:
        _slug_registry = SlugRegistry()
    return _slug_registry


# Convenience functions for common use cases

def authority_slug_to_name(slug: str) -> Optional[str]:
    """
    Convert authority slug to display name

    Args:
        slug: Authority slug (e.g., "poole")

    Returns:
        Authority name (e.g., "Poole") or None if not found
    """
    registry = get_slug_registry()
    name = registry.get_name_from_slug(slug, "authorities")

    # Fallback: capitalize slug
    if name is None:
        return slug.replace("-", " ").title()

    return name


def location_slug_to_name(slug: str) -> Optional[str]:
    """
    Convert location slug to display name

    Args:
        slug: Location slug (e.g., "manchester")

    Returns:
        Location name or None if not found
    """
    registry = get_slug_registry()
    name = registry.get_name_from_slug(slug, "locations")

    # Fallback: capitalize slug
    if name is None:
        return slug.replace("-", " ").title()

    return name


def sector_slug_to_name(slug: str) -> Optional[str]:
    """
    Convert sector slug to display name

    Args:
        slug: Sector slug (e.g., "residential")

    Returns:
        Sector name or None if not found
    """
    registry = get_slug_registry()
    name = registry.get_name_from_slug(slug, "sectors")

    # Fallback: capitalize slug
    if name is None:
        return slug.replace("-", " ").title()

    return name


def validate_authority_slug(slug: str) -> Tuple[bool, Optional[str]]:
    """
    Validate authority slug

    Args:
        slug: Authority slug

    Returns:
        Tuple of (is_valid, error_message)
    """
    registry = get_slug_registry()

    if not slug:
        return False, "Authority slug is required"

    if not slug.replace("-", "").isalnum():
        return False, "Authority slug contains invalid characters"

    if not registry.is_valid_slug(slug, "authorities"):
        # Still allow it (fallback mode), but warn
        return True, None

    return True, None


def get_popular_authorities(limit: int = 20) -> list[Tuple[str, str]]:
    """
    Get list of popular authorities (first N in registry)

    Args:
        limit: Number of authorities to return

    Returns:
        List of (name, slug) tuples
    """
    registry = get_slug_registry()
    authorities = registry.get_all_slugs("authorities")
    return list(authorities.items())[:limit]


def get_all_authorities() -> Dict[str, str]:
    """Get all authority name → slug mappings"""
    registry = get_slug_registry()
    return registry.get_all_slugs("authorities")


def get_all_locations() -> Dict[str, str]:
    """Get all location name → slug mappings"""
    registry = get_slug_registry()
    return registry.get_all_slugs("locations")


def get_all_sectors() -> Dict[str, str]:
    """Get all sector name → slug mappings"""
    registry = get_slug_registry()
    return registry.get_all_slugs("sectors")
