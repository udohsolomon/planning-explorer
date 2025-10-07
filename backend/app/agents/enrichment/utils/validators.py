"""
Data validation and cleaning for enriched applicant/agent data.

This module ensures extracted data is clean, valid, and properly formatted
before being cached and returned to the API.
"""

import re
from typing import Optional


class ApplicantDataValidator:
    """
    Validate and clean applicant/agent data extracted from planning portals.

    This class handles common data quality issues:
    - Whitespace and formatting
    - "Not available" variations
    - Extraction errors (HTML tags, labels)
    - Length validation
    """

    # Common "not available" patterns to detect and convert to None
    NA_PATTERNS = [
        r"^n/?a$",                    # n/a, N/A, n a
        r"^not\s+available$",         # not available, NOT AVAILABLE
        r"^none$",                    # none, NONE
        r"^-+$",                      # -, --, ---
        r"^\s*$",                     # empty or whitespace only
        r"^null$",                    # null
        r"^unknown$",                 # unknown
    ]

    # Patterns that suggest extraction error (extracted wrong content)
    ERROR_PATTERNS = [
        r"applicant\s+name",          # Extracted the label instead of value
        r"agent\s+name",              # Extracted the label instead of value
        r"<.*>",                      # HTML tags
        r"javascript:",               # JavaScript code
        r"onclick=",                  # Event handlers
        r"function\s*\(",             # JavaScript functions
        r"^\s*\{",                    # JSON objects
    ]

    @classmethod
    def clean(cls, value: Optional[str]) -> Optional[str]:
        """
        Clean and validate a single extracted value.

        Args:
            value: Raw extracted text from HTML

        Returns:
            Cleaned value or None if invalid

        Examples:
            >>> ApplicantDataValidator.clean("  John Smith  ")
            'John Smith'

            >>> ApplicantDataValidator.clean("N/A")
            None

            >>> ApplicantDataValidator.clean("<span>Name</span>")
            None
        """
        if not value:
            return None

        # Strip whitespace
        value = value.strip()

        if not value:
            return None

        # Check for "not available" patterns
        for pattern in cls.NA_PATTERNS:
            if re.match(pattern, value, re.IGNORECASE):
                return None

        # Check for extraction errors
        for pattern in cls.ERROR_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return None

        # Length validation (names should be reasonable length)
        if len(value) < 2:  # Too short to be a real name
            return None

        if len(value) > 200:  # Unreasonably long, likely extraction error
            return None

        # Additional validation: check for excessive special characters
        special_char_count = sum(1 for c in value if not c.isalnum() and not c.isspace() and c not in "'-,.()")
        if special_char_count > len(value) * 0.3:  # More than 30% special chars
            return None

        return value

    @classmethod
    def validate_result(cls, applicant_name: Optional[str],
                       agent_name: Optional[str]) -> dict:
        """
        Validate complete extraction result with both applicant and agent.

        Args:
            applicant_name: Raw extracted applicant name
            agent_name: Raw extracted agent name

        Returns:
            Dictionary with:
            - valid: bool (always True, even if both None)
            - applicant_name: str|None (cleaned)
            - agent_name: str|None (cleaned)
            - warnings: list of warning messages

        Examples:
            >>> ApplicantDataValidator.validate_result("John Smith", "ABC Architects")
            {
                'valid': True,
                'applicant_name': 'John Smith',
                'agent_name': 'ABC Architects',
                'warnings': []
            }

            >>> ApplicantDataValidator.validate_result(None, None)
            {
                'valid': True,
                'applicant_name': None,
                'agent_name': None,
                'warnings': ['Both applicant and agent names are unavailable']
            }
        """
        warnings = []

        # Clean both values
        cleaned_applicant = cls.clean(applicant_name)
        cleaned_agent = cls.clean(agent_name)

        # Generate warnings
        if cleaned_applicant is None and cleaned_agent is None:
            warnings.append("Both applicant and agent names are unavailable")
        elif cleaned_applicant is None:
            warnings.append("Applicant name is unavailable")
        elif cleaned_agent is None:
            warnings.append("Agent name is unavailable")

        # Check if values were modified during cleaning
        if applicant_name and not cleaned_applicant:
            warnings.append(f"Applicant name rejected during validation: '{applicant_name[:50]}'")
        if agent_name and not cleaned_agent:
            warnings.append(f"Agent name rejected during validation: '{agent_name[:50]}'")

        return {
            "valid": True,  # Even if both None, it's valid (some apps have no agent)
            "applicant_name": cleaned_applicant,
            "agent_name": cleaned_agent,
            "warnings": warnings
        }

    @classmethod
    def validate_batch(cls, results: list) -> dict:
        """
        Validate a batch of extraction results.

        Args:
            results: List of dicts with 'applicant_name' and 'agent_name'

        Returns:
            Dictionary with:
            - total: int (total results)
            - valid_applicant: int (count with valid applicant)
            - valid_agent: int (count with valid agent)
            - valid_both: int (count with both valid)
            - success_rate: float (percentage with at least one valid)

        Example:
            >>> results = [
            ...     {'applicant_name': 'John', 'agent_name': 'ABC'},
            ...     {'applicant_name': 'Jane', 'agent_name': None},
            ...     {'applicant_name': None, 'agent_name': None}
            ... ]
            >>> ApplicantDataValidator.validate_batch(results)
            {
                'total': 3,
                'valid_applicant': 2,
                'valid_agent': 1,
                'valid_both': 1,
                'success_rate': 0.67
            }
        """
        total = len(results)
        valid_applicant = 0
        valid_agent = 0
        valid_both = 0

        for result in results:
            validated = cls.validate_result(
                result.get('applicant_name'),
                result.get('agent_name')
            )

            if validated['applicant_name']:
                valid_applicant += 1
            if validated['agent_name']:
                valid_agent += 1
            if validated['applicant_name'] and validated['agent_name']:
                valid_both += 1

        success_rate = (valid_applicant + valid_agent) / (total * 2) if total > 0 else 0.0

        return {
            "total": total,
            "valid_applicant": valid_applicant,
            "valid_agent": valid_agent,
            "valid_both": valid_both,
            "success_rate": round(success_rate, 2)
        }

