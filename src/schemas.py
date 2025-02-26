"""Schemas for structured data extraction."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StructuredData(BaseModel):
    """Schema for structured data extracted from user input.
    
    This is a general-purpose schema that can handle various types of information
    extracted from user text. It's flexible enough to represent different kinds
    of data while maintaining a consistent structure.
    """
    data_type: str = Field(
        description="Type of data extracted (e.g., 'reservation', 'info_request', 'contact')"
    )
    primary_entity: str = Field(
        description="Main entity referenced in the input (person, place, concept, etc.)"
    )
    attributes: Dict[str, Any] = Field(
        default_factory=dict,  # Add default empty dictionary
        description="Key attributes of the entity as key-value pairs"
    )
    datetime: Optional[str] = Field(
        None, description="Relevant date/time if applicable (ISO format preferred)"
    )
    priority: Optional[int] = Field(
        None, description="Priority level (1-5) if applicable"
    )
    tags: Optional[List[str]] = Field(
        None, description="Relevant tags for categorization"
    )
    notes: Optional[str] = Field(
        None, description="Additional notes or context"
    )