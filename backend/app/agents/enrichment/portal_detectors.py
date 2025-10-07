"""
Portal type detection for UK planning authority websites.

This module detects the type of planning portal based on URL patterns,
enabling the enrichment agent to select the appropriate extraction strategy.

Supported Portal Types:
- Idox Public Access (~60% of UK authorities)
- Custom portals (Liverpool, etc.) (~20% of UK authorities)
- Unknown/Adaptive portals (~20% of UK authorities)
"""

from urllib.parse import urlparse
from typing import Literal
import re

PortalType = Literal["idox_public_access", "liverpool_custom", "unknown"]


class PortalDetector:
    """
    Detect portal type from planning application URL.

    This class uses regex patterns and domain mapping to identify
    the type of planning portal, which determines the extraction strategy.
    """

    # Idox Public Access pattern (~60% of UK local authorities)
    # Example: https://publicaccess.dover.gov.uk/online-applications/...
    IDOX_PATTERN = r"publicaccess\..*\.gov\.uk/online-applications"

    # Liverpool portal pattern (example of custom portal)
    LIVERPOOL_PATTERN = r"lar\.liverpool\.gov\.uk/planning"

    # Known custom portals - extend as new portals are discovered
    # Key: domain, Value: portal type identifier
    KNOWN_CUSTOM_PORTALS = {
        "lar.liverpool.gov.uk": "liverpool_custom",
        "planning.manchester.gov.uk": "manchester_custom",
        # Add more custom portals as they're discovered and patterns learned
    }

    @classmethod
    def detect(cls, url: str) -> PortalType:
        """
        Detect portal type from URL.

        Args:
            url: Planning application URL

        Returns:
            Portal type identifier:
            - "idox_public_access" for Idox portals
            - "liverpool_custom" (or similar) for known custom portals
            - "unknown" for unrecognized portals

        Examples:
            >>> PortalDetector.detect("https://publicaccess.dover.gov.uk/...")
            'idox_public_access'

            >>> PortalDetector.detect("https://lar.liverpool.gov.uk/planning/...")
            'liverpool_custom'

            >>> PortalDetector.detect("https://example.com/planning/12345")
            'unknown'
        """
        if not url:
            return "unknown"

        # Check for Idox Public Access pattern
        if re.search(cls.IDOX_PATTERN, url):
            return "idox_public_access"

        # Check for known custom portals
        domain = urlparse(url).netloc
        if domain in cls.KNOWN_CUSTOM_PORTALS:
            return cls.KNOWN_CUSTOM_PORTALS[domain]

        # Unknown portal - will use adaptive extraction
        return "unknown"

    @classmethod
    def is_idox(cls, url: str) -> bool:
        """
        Check if URL is an Idox Public Access portal.

        Args:
            url: Planning application URL

        Returns:
            True if Idox portal, False otherwise

        Example:
            >>> PortalDetector.is_idox("https://publicaccess.dover.gov.uk/...")
            True
        """
        return cls.detect(url) == "idox_public_access"

    @classmethod
    def is_known_custom(cls, url: str) -> bool:
        """
        Check if URL is a known custom portal.

        Args:
            url: Planning application URL

        Returns:
            True if known custom portal, False otherwise

        Example:
            >>> PortalDetector.is_known_custom("https://lar.liverpool.gov.uk/...")
            True
        """
        portal_type = cls.detect(url)
        return portal_type != "unknown" and portal_type != "idox_public_access"

    @classmethod
    def get_portal_info(cls, url: str) -> dict:
        """
        Get detailed information about the portal type.

        Args:
            url: Planning application URL

        Returns:
            Dictionary with portal metadata:
            - type: Portal type identifier
            - category: Portal category (idox, custom, unknown)
            - extraction_strategy: Recommended extraction method
            - expected_speed: Expected extraction time

        Example:
            >>> PortalDetector.get_portal_info("https://publicaccess.dover.gov.uk/...")
            {
                'type': 'idox_public_access',
                'category': 'idox',
                'extraction_strategy': 'firecrawl_table',
                'expected_speed_ms': 2000
            }
        """
        portal_type = cls.detect(url)

        if portal_type == "idox_public_access":
            return {
                "type": portal_type,
                "category": "idox",
                "extraction_strategy": "firecrawl_table",
                "expected_speed_ms": 2000,
                "confidence": "high"
            }
        elif cls.is_known_custom(url):
            return {
                "type": portal_type,
                "category": "custom",
                "extraction_strategy": "firecrawl_labeled",
                "expected_speed_ms": 2500,
                "confidence": "high"
            }
        else:
            return {
                "type": "unknown",
                "category": "unknown",
                "extraction_strategy": "playwright_context7",
                "expected_speed_ms": 6000,
                "confidence": "medium"
            }

    @classmethod
    def add_custom_portal(cls, domain: str, portal_type: str) -> None:
        """
        Add a new custom portal to the known portals registry.

        This allows the system to learn new portal types over time.

        Args:
            domain: Portal domain (e.g., "planning.example.gov.uk")
            portal_type: Portal type identifier (e.g., "example_custom")

        Example:
            >>> PortalDetector.add_custom_portal("planning.bristol.gov.uk", "bristol_custom")
        """
        cls.KNOWN_CUSTOM_PORTALS[domain] = portal_type


# Example usage and testing
if __name__ == "__main__":
    # Test with different portal types
    test_urls = [
        "https://publicaccess.dover.gov.uk/online-applications/applicationDetails.do?activeTab=summary&keyVal=S4S7QCFZH0F00",
        "https://lar.liverpool.gov.uk/planning/index.html?fa=getApplication&id=175224",
        "https://example.com/planning/12345"
    ]

    for url in test_urls:
        portal_type = PortalDetector.detect(url)
        portal_info = PortalDetector.get_portal_info(url)
        print(f"URL: {url[:60]}...")
        print(f"Type: {portal_type}")
        print(f"Info: {portal_info}")
        print()
