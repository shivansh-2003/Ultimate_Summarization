import os
import time
import argparse
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from datetime import datetime

# Import specialized summarizers
from normal import GeneralDocumentSummarizer, SummarySettings
from resume import ResumeSummarizer
from legal import LegalDocumentSummarizer

# Load environment variables
load_dotenv()

class UniversalDocumentSummarizer:
    """
    A universal document summarizer that can handle different document types
    by using specialized summarizers based on the document type.
    """
    
    def __init__(self):
        """Initialize the universal document summarizer with specialized summarizers."""
        # Initialize specialized summarizers
        self.general_summarizer = GeneralDocumentSummarizer()
        self.resume_summarizer = ResumeSummarizer()
        self.legal_summarizer = LegalDocumentSummarizer()
    
    def summarize_document(self, 
                          file_path: str, 
                          mode: str,
                          settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Summarize a document using the appropriate summarizer based on document type or specified mode.
        
        Args:
            file_path: Path to the document file
            mode: Specific summarization mode ('general', 'resume', 'legal')
            settings: Additional settings for the summarizer
        
        Returns:
            Dictionary containing the summary and additional information
        """
        start_time = time.time()
        
        # Default settings if none provided
        if settings is None:
            settings = {}
        
        print(f"Processing document as: {mode}")
        
        # Process document based on type
        if mode == "resume":
            # Get job description from settings if available
            job_description = settings.get("job_description")
            result = self.resume_summarizer.process_resume_file(file_path, job_description)
            
            # Format result for consistent output
            summary_result = {
                "document_type": "resume",
                "executive_summary": result.narrative_summary,
                "structured_data": result.structured_data.model_dump(),
                "ats_analysis": result.ats_analysis.model_dump() if result.ats_analysis else None,
                "processing_time": result.processing_time
            }
            
        elif mode == "legal":
            # Get custom question from settings if available
            custom_question = settings.get("custom_question")
            result = self.legal_summarizer.generate_summary(file_path, custom_question)
            
            # Legal summarizer returns dictionary with "summary" key
            # Add an executive_summary key for consistent interface
            result["executive_summary"] = result.get("summary", "")
            summary_result = result
            
        else:  # General document
            # Prepare settings for general summarizer
            general_settings = settings
            result = self.general_summarizer.summarize_document(file_path, general_settings)
            
            # Format result for consistent output
            summary_result = {
                "document_type": "general",
                "executive_summary": result.executive_summary,
                "detailed_summary": result.detailed_summary,
                "topics": [topic.model_dump() for topic in result.topics],
                "key_points": [point.model_dump() for point in result.key_points],
                "statistics": result.statistics.model_dump() if result.statistics else None,
                "processing_time": result.processing_time
            }
        
        # Add processing metadata
        summary_result["processed_at"] = datetime.now().isoformat()
        if "processing_time" not in summary_result:
            summary_result["processing_time"] = time.time() - start_time
            
        return summary_result

def get_user_input(prompt: str, options: List[str], default: Optional[str] = None) -> str:
    """
    Get user input from a list of options.
    
    Args:
        prompt: The prompt to display to the user
        options: List of valid options
        default: The default option if user just presses Enter
        
    Returns:
        The selected option
    """
    # Display options with numbers
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    default_text = f" (default: {default})" if default else ""
    
    while True:
        choice = input(f"\nEnter your choice (1-{len(options)}){default_text}: ").strip()
        
        # Handle default
        if not choice and default:
            return default
        
        # Handle numeric input
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(options):
                return options[choice_index]
        except ValueError:
            # Handle direct text input
            if choice.lower() in [option.lower() for option in options]:
                return next(option for option in options if option.lower() == choice.lower())
        
        print(f"Invalid choice. Please enter a number between 1 and {len(options)} or the option text.")

def main():
    """Main function to run the interactive summarizer."""
    print("=" * 60)
    print("Universal Document Summarizer")
    print("=" * 60)
    
    # Get document file path
    while True:
        file_path = input("\nEnter the path to your document file: ").strip()
        if os.path.isfile(file_path):
            break
        print(f"File not found: {file_path}")
    
    # Get document mode
    mode = get_user_input(
        "Which type of document are you summarizing?",
        ["General Document", "Resume", "Legal Document"],
        "General Document"
    )
    
    # Convert UI selection to internal mode
    mode_map = {
        "General Document": "general",
        "Resume": "resume",
        "Legal Document": "legal"
    }
    selected_mode = mode_map[mode]
    
    # Initialize settings
    settings = {}
    
    # Get mode-specific settings
    if selected_mode == "general":
        # Get conciseness level for general documents directly - don't ask about other settings
        conciseness = get_user_input(
            "Select the conciseness level for the summary:",
            ["very_concise", "balanced", "detailed"],
            "balanced"
        )
        
        # Apply default settings without asking for each one individually
        settings.update({
            "conciseness": conciseness,
            "extract_topics": True,
            "extract_key_points": True,
            "include_statistics": False  # As per your requirements
        })
        
        # Optional focus areas
        focus_areas = input("\nEnter focus areas (comma separated, or leave empty): ").strip()
        if focus_areas:
            settings["focus_areas"] = [area.strip() for area in focus_areas.split(",")]
    
    elif selected_mode == "resume":
        # For resume, just get the job description in a single step
        print("\nEnter the job description for ATS analysis (or leave empty for none):")
        job_description = input().strip()
        if job_description:
            settings["job_description"] = job_description
    
    elif selected_mode == "legal":
        # For legal documents, simpler question input
        custom_q = input("\nDo you want to ask a specific question about this legal document? (y/n): ").strip().lower()
        if custom_q == "y":
            question = input("Enter your question: ").strip()
            if question:
                settings["custom_question"] = question
    
    # Initialize the summarizer
    summarizer = UniversalDocumentSummarizer()
    
    # Process the document
    print("\nProcessing document... This may take a few moments.")
    try:
        result = summarizer.summarize_document(file_path, selected_mode, settings)
        
        # Display processing info
        print(f"\nDocument processed in {result['processing_time']:.2f} seconds")
        
        # Display the summary
        print("\n" + "="*60)
        print(f"DOCUMENT TYPE: {result['document_type'].upper()}")
        print("="*60)
        
        print("\nEXECUTIVE SUMMARY:")
        print(result['executive_summary'])
        
        if 'detailed_summary' in result and result['detailed_summary']:
            print("\nDETAILED SUMMARY:")
            print(result['detailed_summary'])
        
        if 'topics' in result and result['topics']:
            print("\nMAIN TOPICS:")
            for topic in result['topics']:
                print(f"- {topic['name']}")
        
        if 'key_points' in result and result['key_points']:
            print("\nKEY POINTS:")
            for point in result['key_points']:
                print(f"- {point['point']}")
        
        if 'statistics' in result and result['statistics'] and result.get('include_statistics', False):
            print("\nDOCUMENT STATISTICS:")
            stats = result['statistics']
            print(f"Word count: {stats['word_count']}")
            print(f"Reading time: {stats['estimated_reading_time_minutes']:.1f} minutes")
        
        # Save output option
        save_option = input("\nDo you want to save this summary to a file? (y/n): ").strip().lower()
        if save_option == "y":
            output_path = input("Enter the output file path: ").strip()
            import json
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Summary saved to {output_path}")
        
    except Exception as e:
        print(f"\nError processing document: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()