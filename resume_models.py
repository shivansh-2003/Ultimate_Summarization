from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime

class BasicInformation(BaseModel):
    """Basic personal information from a resume."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None
    
    model_config = {
        "extra": "allow"  # Allow additional fields not defined in the model
    }

class Skill(BaseModel):
    """Individual skill with optional proficiency level."""
    name: str
    proficiency: Optional[str] = None
    category: Optional[str] = None
    
    @field_validator('proficiency')
    def validate_proficiency(cls, v):
        """Normalize proficiency levels if present."""
        if v:
            # Convert various formats to consistent levels
            v = v.lower().strip()
            if v in ('expert', 'advanced', 'proficient', 'high'):
                return 'Advanced'
            elif v in ('intermediate', 'competent', 'medium'):
                return 'Intermediate'
            elif v in ('beginner', 'basic', 'novice', 'low'):
                return 'Beginner'
        return v

class SkillCategory(BaseModel):
    """Group of skills in a specific category."""
    category: str
    skills: List[str]

class Experience(BaseModel):
    """Work experience entry."""
    company: str
    title: str
    dates: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    current: Optional[bool] = False
    location: Optional[str] = None
    responsibilities: Optional[List[str]] = Field(default_factory=list)
    achievements: Optional[List[str]] = Field(default_factory=list)
    technologies: Optional[List[str]] = Field(default_factory=list)
    
    model_config = {
        "extra": "allow"
    }

class Education(BaseModel):
    """Educational background entry."""
    degree: str
    institution: str
    dates: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    gpa: Optional[str] = None
    major: Optional[str] = None
    minor: Optional[str] = None
    honors: Optional[List[str]] = Field(default_factory=list)
    coursework: Optional[List[str]] = Field(default_factory=list)
    
    class Config:
        extra = "allow"

class Certification(BaseModel):
    """Professional certification entry."""
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    expiration: Optional[str] = None
    id: Optional[str] = None
    
    class Config:
        extra = "allow"

class Project(BaseModel):
    """Project entry from resume."""
    name: str
    description: Optional[str] = None
    role: Optional[str] = None
    technologies: Optional[List[str]] = Field(default_factory=list)
    url: Optional[str] = None
    dates: Optional[str] = None
    
    class Config:
        extra = "allow"

class ResumeData(BaseModel):
    """Structured data extracted from a resume."""
    basic_information: BasicInformation = Field(default_factory=BasicInformation)
    professional_summary: Optional[str] = None
    skills: List[Any] = Field(default_factory=list)  # Can be either Skill or SkillCategory objects
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications_licenses: List[Certification] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    career_highlights: List[str] = Field(default_factory=list)
    languages: Optional[List[Dict[str, str]]] = None
    
    @field_validator('skills', mode='before')
    def validate_skills(cls, v):
        """Handle different skill formats."""
        if isinstance(v, dict):
            # Handle category dict format
            result = []
            for category, skills in v.items():
                result.append(SkillCategory(category=category, skills=skills))
            return result
        return v
    
    class Config:
        extra = "allow"

class KeywordMatch(BaseModel):
    """ATS keyword matching results."""
    present: List[str] = Field(default_factory=list)
    missing: List[str] = Field(default_factory=list)

class ATSAnalysis(BaseModel):
    """ATS compatibility analysis results."""
    score: Optional[float] = None
    keyword_match: Optional[KeywordMatch] = None
    skills_alignment: Optional[str] = None
    experience_relevance: Optional[str] = None
    format_issues: Optional[List[str]] = Field(default_factory=list)
    recommendations: Optional[List[str]] = Field(default_factory=list)
    analysis_text: Optional[str] = None
    
    class Config:
        extra = "allow"

class ResumeSummaryResult(BaseModel):
    """Complete result from resume analysis."""
    structured_data: ResumeData
    narrative_summary: str
    ats_analysis: Optional[ATSAnalysis] = None
    processing_time: float
    processed_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        extra = "allow"