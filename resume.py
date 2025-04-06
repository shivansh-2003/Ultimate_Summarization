import os
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import json
from datetime import datetime
from resume_models import (
    ResumeData, ATSAnalysis, ResumeSummaryResult, 
    KeywordMatch, BasicInformation, Experience, Education,
    Certification, Project, Skill, SkillCategory
)

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ResumeSummarizer:
    """
    A specialized summarizer for extracting structured information from resumes
    using LangChain, OpenAI, and Pydantic for structured output.
    """
    
    def __init__(self, model_name="gpt-4o-mini", temperature=0.0):
        """Initialize the resume summarizer with necessary components."""
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Text splitter tuned for resumes
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""],
            length_function=len
        )
        
        # Resume analysis prompt template with structured Pydantic output format
        self.resume_analysis_prompt = PromptTemplate(
            input_variables=["resume_text"],
            template="""
            You are an expert resume analyzer and HR professional. Extract and structure information from 
            the provided resume. Focus on presenting the most relevant information in a clear, organized manner.
            
            RESUME TEXT:
            {resume_text}
            
            Analyze this resume and provide a structured JSON response that conforms to the following Pydantic model structure:
            
            ```python
            class BasicInformation:
                name: Optional[str]
                email: Optional[str]
                phone: Optional[str]
                location: Optional[str]
                linkedin: Optional[str]
                website: Optional[str]
            
            class Skill:
                name: str
                proficiency: Optional[str]  # e.g., "Beginner", "Intermediate", "Advanced"
                category: Optional[str]  # e.g., "Technical", "Soft Skills", "Languages"
            
            class Experience:
                company: str
                title: str
                dates: Optional[str]  # e.g., "Jan 2020 - Present"
                start_date: Optional[str]
                end_date: Optional[str]
                current: Optional[bool]
                location: Optional[str]
                responsibilities: List[str]
                achievements: List[str]
                technologies: List[str]
            
            class Education:
                degree: str
                institution: str
                dates: Optional[str]
                start_date: Optional[str]
                end_date: Optional[str]
                location: Optional[str]
                gpa: Optional[str]
                major: Optional[str]
                minor: Optional[str]
                honors: List[str]
                coursework: List[str]
            
            class Certification:
                name: str
                issuer: Optional[str]
                date: Optional[str]
                expiration: Optional[str]
                id: Optional[str]
            
            class Project:
                name: str
                description: Optional[str]
                role: Optional[str]
                technologies: List[str]
                url: Optional[str]
                dates: Optional[str]
            
            class ResumeData:
                basic_information: BasicInformation
                professional_summary: Optional[str]
                skills: List[Union[Skill, Dict[str, List[str]]]]  # Can be list of skills or dict of categories
                experience: List[Experience]
                education: List[Education]
                certifications_licenses: List[Certification]
                projects: List[Project]
                career_highlights: List[str]
                languages: Optional[List[Dict[str, str]]]
            ```
            
            The response should be in valid JSON format only, matching the Pydantic model structure above.
            Include empty arrays or objects for sections where no information is provided in the resume.
            For skills, you can either provide a list of Skill objects or a dictionary with categories as keys
            and lists of skill names as values, depending on which format better represents the resume's content.
            """
        )
        
        # Resume summary prompt template
        self.resume_summary_prompt = PromptTemplate(
            input_variables=["resume_json"],
            template="""
            You are an expert resume writer and career coach. Based on the structured resume information provided,
            create a concise and comprehensive summary of the candidate's profile.
            
            RESUME INFORMATION:
            {resume_json}
            
            Create a professional summary that includes:
            
            1. A brief professional overview (2-3 sentences)
            2. Key skills and competencies (including technical and soft skills)
            3. Career progression highlights
            4. Educational background relevance
            5. Notable achievements and their impact
            6. Potential fit for roles based on their background
            
            Keep the summary concise but comprehensive, highlighting the most impressive and relevant aspects
            of the candidate's background. Use professional, engaging language.
            """
        )
        
        # ATS compatibility prompt with Pydantic output format
        self.ats_compatibility_prompt = PromptTemplate(
            input_variables=["resume_json", "job_description"],
            template="""
            You are an ATS (Applicant Tracking System) expert. Given a resume and a job description,
            analyze how well the resume would perform in an ATS screening.
            
            RESUME INFORMATION:
            {resume_json}
            
            JOB DESCRIPTION:
            {job_description}
            
            Provide an analysis that conforms to the following Pydantic model structure:
            
            ```python
            class KeywordMatch:
                present: List[str]  # Keywords found in the resume
                missing: List[str]  # Important keywords missing from the resume
            
            class ATSAnalysis:
                score: float  # ATS Compatibility Score (0-100)
                keyword_match: KeywordMatch
                skills_alignment: str  # Description of skills alignment
                experience_relevance: str  # Description of experience relevance
                format_issues: List[str]  # Format/structure issues that might affect ATS scanning
                recommendations: List[str]  # Recommendations to improve ATS compatibility
            ```
            
            The response should be in valid JSON format only, matching the Pydantic model structure above.
            Base your analysis on current ATS best practices. Focus on actionable recommendations that
            would help the candidate improve their resume for this specific role.
            """
        )
    
    def load_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF resume."""
        print(f"Loading PDF from {pdf_path}...")
        
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        
        print(f"Extracted {len(text)} characters from PDF.")
        return text
    
    def process_resume(self, resume_text: str) -> ResumeData:
        """Process resume text into structured information using Pydantic models."""
        print("Processing resume text into structured information...")
        
        # For resumes, we often don't need chunking as they're typically short,
        # but we'll check length just in case
        if len(resume_text) > 10000:
            chunks = self.text_splitter.split_text(resume_text)
            print(f"Resume is long, split into {len(chunks)} chunks.")
            # Combine chunks as we need the whole context for complete analysis
            resume_text = " ".join(chunks)
        
        prompt = self.resume_analysis_prompt.format(resume_text=resume_text)
        structured_data_str = self.llm.invoke(prompt).content
        
        # Parse the JSON response
        try:
            # Extract JSON if it's embedded in other text
            json_start = structured_data_str.find('{')
            json_end = structured_data_str.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                structured_data_str = structured_data_str[json_start:json_end]
            
            # Parse into dictionary
            structured_dict = json.loads(structured_data_str)
            
            # Convert to Pydantic model
            structured_data = ResumeData.model_validate(structured_dict)
            print("Successfully extracted structured information from resume.")
            return structured_data
            
        except Exception as e:
            print(f"Error parsing response: {e}")
            # Return a minimal structure if parsing fails
            return ResumeData()
    
    def generate_summary(self, resume_data: ResumeData) -> str:
        """Generate a narrative summary from structured resume data."""
        print("Generating narrative summary from structured resume data...")
        
        resume_json = resume_data.model_dump_json(indent=2)
        prompt = self.resume_summary_prompt.format(resume_json=resume_json)
        summary = self.llm.invoke(prompt).content
        
        print("Resume summary generated successfully.")
        return summary
    
    def analyze_ats_compatibility(self, resume_data: ResumeData, job_description: str) -> ATSAnalysis:
        """Analyze how well the resume would perform in an ATS for a specific job."""
        print("Analyzing ATS compatibility...")
        
        resume_json = resume_data.model_dump_json(indent=2)
        prompt = self.ats_compatibility_prompt.format(
            resume_json=resume_json,
            job_description=job_description
        )
        analysis_str = self.llm.invoke(prompt).content
        
        # Try to parse as JSON if possible
        try:
            # Extract JSON if it's embedded in other text
            json_start = analysis_str.find('{')
            json_end = analysis_str.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                analysis_str = analysis_str[json_start:json_end]
            
            # Parse into dictionary
            analysis_dict = json.loads(analysis_str)
            
            # Convert to Pydantic model
            analysis = ATSAnalysis.model_validate(analysis_dict)
            print("ATS analysis completed as structured data.")
            return analysis
            
        except Exception as e:
            print(f"Error parsing ATS analysis: {e}")
            # If parsing fails, store the raw text
            return ATSAnalysis(analysis_text=analysis_str)
    
    def process_resume_file(self, pdf_path: str, job_description: Optional[str] = None) -> ResumeSummaryResult:
        """Process a resume PDF file and generate analysis/summary with Pydantic models."""
        start_time = datetime.now()
        
        # Load and process resume
        resume_text = self.load_pdf(pdf_path)
        resume_data = self.process_resume(resume_text)
        
        # Generate narrative summary
        summary = self.generate_summary(resume_data)
        
        # Analyze ATS compatibility if job description provided
        ats_analysis = None
        if job_description:
            ats_analysis = self.analyze_ats_compatibility(resume_data, job_description)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Create the final result using Pydantic model
        result = ResumeSummaryResult(
            structured_data=resume_data,
            narrative_summary=summary,
            ats_analysis=ats_analysis,
            processing_time=processing_time
        )
        
        return result


if __name__ == "__main__":
    # Example usage
    summarizer = ResumeSummarizer()
    
    # Process a single resume
    result = summarizer.process_resume_file("/Users/shivanshmahajan/Desktop/Ultimate_Summarization/file/best.pdf")
    
    print("\n" + "="*50)
    print("RESUME SUMMARY")
    print("="*50)
    print(result.narrative_summary)
    
    print("\n" + "="*50)
    print("STRUCTURED DATA")
    print("="*50)
    print(result.structured_data.model_dump_json(indent=2))
    
    print("\n" + "="*50)
    print(f"Processing time: {result.processing_time:.2f} seconds")