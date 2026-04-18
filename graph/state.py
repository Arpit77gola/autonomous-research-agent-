from __future__ import annotations

from typing import Annotated
from pydantic import BaseModel, Field
import operator


class Source(BaseModel):
    url: str
    title: str
    snippet: str
    relevance_score: float = 1.0


class ResearchState(BaseModel):
    # Input
    query: str = ""

    # Planner fills these
    research_plan: list[str] = Field(default_factory=list)
    search_queries: list[str] = Field(default_factory=list)

    # Researcher fills these
    sources: Annotated[list[Source], operator.add] = Field(default_factory=list)
    raw_findings: Annotated[list[str], operator.add] = Field(default_factory=list)

    # Critic fills these
    knowledge_gaps: list[str] = Field(default_factory=list)
    is_sufficient: bool = False
    iteration: int = 0

    # Writer fills this
    final_report: str = ""

    # Error tracking
    error: str = ""