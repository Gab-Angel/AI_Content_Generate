from typing import Literal, Optional, List
from pydantic import BaseModel


class ResearchResult(BaseModel):
    summary: str
    key_points: List[str]
    sources: Optional[List[str]] = None
    insights: Optional[List[str]] = None

class FinalReport(BaseModel):
    type_post: Literal["carousel", "description", "stories", "video"]
    title: Optional[str] = None 
    texts: List[str]
    caption: Optional[str] = None 
    hashtags: Optional[List[str]] = None
    notes: Optional[str] = None


class State(BaseModel):
    type_post: Literal["carousel", "description", "stories", "video"]
    topic: str
    idea: str
    tone: Literal["professional", "happy", "serious"]
    slides: Optional[int] = None  
    result_research: Optional[ResearchResult] = None

