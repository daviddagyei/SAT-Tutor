"""
PDF Processing Pipeline for SAT Questions

This module orchestrates the entire process of converting SAT PDFs to
structured question data and storing them in the database.
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from .extractor import extract_text_from_pdf
from .processor import process_text_to_sections, extract_questions_from_section, SATSection
from .transformer import transform_questions_to_json

logger = logging.getLogger(__name__)


def process_pdf_to_questions(pdf_path: str, output_json_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Process a PDF file into structured question data
    
    Args:
        pdf_path: Path to the PDF file
        output_json_path: Optional path to save JSON output
        
    Returns:
        List of question dictionaries
    """
    logger.info(f"Processing PDF: {pdf_path}")
    
    # Step 1: Extract text from PDF
    extracted_text = extract_text_from_pdf(pdf_path)
    logger.info(f"Extracted text from {len(extracted_text)} pages")
    
    # Step 2: Process text into sections
    sections = process_text_to_sections(extracted_text)
    logger.info(f"Identified {len(sections)} SAT sections")
    
    # Step 3: Extract questions from each section
    all_questions = []
    for section_type, section_contents in sections.items():
        logger.info(f"Processing section: {section_type}")
        
        for content in section_contents:
            section_questions = extract_questions_from_section(content, section_type)
            logger.info(f"Extracted {len(section_questions)} questions from {section_type}")
            all_questions.extend(section_questions)
    
    # Step 4: Transform questions to JSON format
    question_data = transform_questions_to_json(all_questions)
    logger.info(f"Transformed {len(question_data)} questions to JSON format")
    
    # Save to file if output path is provided
    if output_json_path:
        output_dir = os.path.dirname(output_json_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(output_json_path, 'w') as f:
            json.dump(question_data, f, indent=2)
        logger.info(f"Saved question data to {output_json_path}")
    
    return question_data


def process_pdf_and_store_in_db(pdf_path: str, save_json: bool = True) -> Tuple[int, int]:
    """
    Process a PDF and store questions in the database
    
    Args:
        pdf_path: Path to the PDF file
        save_json: Whether to save intermediate JSON output
        
    Returns:
        Tuple of (questions_processed, questions_stored)
    """
    # Process the PDF to extract questions
    output_json = None
    if save_json:
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_json = f"./data/processed/{pdf_name}_questions.json"
    
    questions = process_pdf_to_questions(pdf_path, output_json)
    
    # Import the repository here to avoid circular imports
    from ...repositories.question_repository import QuestionRepository
    
    # Initialize repository
    question_repo = QuestionRepository()
    
    # Store questions in database
    questions_stored = 0
    
    for question_data in questions:
        try:
            # Save question to database
            # This assumes your repository has a create method that accepts a dictionary
            question_repo.create(question_data)
            questions_stored += 1
            
        except Exception as e:
            logger.error(f"Error storing question: {e}")
    
    logger.info(f"Processed {len(questions)} questions, stored {questions_stored} in database")
    
    return len(questions), questions_stored


def batch_process_pdfs(pdf_directory: str, output_directory: Optional[str] = None) -> Dict[str, Tuple[int, int]]:
    """
    Process all PDFs in a directory
    
    Args:
        pdf_directory: Directory containing PDF files
        output_directory: Optional directory to save JSON output files
        
    Returns:
        Dictionary mapping PDF filenames to (questions_processed, questions_stored) tuples
    """
    if not os.path.exists(pdf_directory):
        raise FileNotFoundError(f"PDF directory not found: {pdf_directory}")
    
    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    results = {}
    pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_directory, pdf_file)
        
        try:
            # Process the PDF and store questions
            processed, stored = process_pdf_and_store_in_db(pdf_path)
            results[pdf_file] = (processed, stored)
            
            # Log results
            logger.info(f"Processed {pdf_file}: {processed} questions extracted, {stored} stored in database")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file}: {e}")
            results[pdf_file] = (0, 0)
    
    return results