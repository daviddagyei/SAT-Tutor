"""
Command-line interface for the PDF processing pipeline

This module provides a command-line interface to run the PDF processing pipeline,
which converts SAT PDFs to structured question data and stores them in the database.

Example usage:
    # Process a single PDF file
    python -m app.utils.pdf_processing.cli --pdf-path /path/to/sat_exam.pdf
    
    # Process all PDFs in a directory
    python -m app.utils.pdf_processing.cli --pdf-dir /path/to/pdf_folder
    
    # Process a PDF and save JSON output without database import
    python -m app.utils.pdf_processing.cli --pdf-path /path/to/sat_exam.pdf --json-only
"""
import os
import sys
import argparse
import logging
from pathlib import Path

from .pipeline import process_pdf_to_questions, process_pdf_and_store_in_db, batch_process_pdfs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("pdf_processing_cli")

def main():
    """Main entry point for the PDF processing command-line interface"""
    parser = argparse.ArgumentParser(
        description="Process SAT PDF files into structured question data and store in database"
    )
    
    # Define command-line arguments
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--pdf-path", help="Path to a single PDF file")
    input_group.add_argument("--pdf-dir", help="Path to directory containing PDF files")
    
    parser.add_argument("--output-dir", help="Directory to save JSON output files")
    parser.add_argument("--json-only", action="store_true", 
                        help="Only generate JSON data, don't store in database")
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        if args.pdf_path:
            # Process a single PDF file
            pdf_path = os.path.abspath(args.pdf_path)
            
            if not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                return 1
                
            if args.json_only:
                # Generate JSON only
                output_json = None
                if args.output_dir:
                    os.makedirs(args.output_dir, exist_ok=True)
                    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
                    output_json = os.path.join(args.output_dir, f"{pdf_name}_questions.json")
                else:
                    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
                    output_json = f"{pdf_name}_questions.json"
                
                questions = process_pdf_to_questions(pdf_path, output_json)
                logger.info(f"Processed {len(questions)} questions from {pdf_path}")
                logger.info(f"JSON output saved to {output_json}")
                
            else:
                # Process and store in database
                processed, stored = process_pdf_and_store_in_db(pdf_path)
                logger.info(f"Processed {processed} questions, stored {stored} in database")
                
        elif args.pdf_dir:
            # Process all PDFs in a directory
            pdf_dir = os.path.abspath(args.pdf_dir)
            
            if not os.path.exists(pdf_dir):
                logger.error(f"PDF directory not found: {pdf_dir}")
                return 1
                
            output_dir = args.output_dir if args.output_dir else os.path.join(pdf_dir, "processed")
            
            if args.json_only:
                # Generate JSON files without database import
                results = {}
                pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
                
                for pdf_file in pdf_files:
                    pdf_path = os.path.join(pdf_dir, pdf_file)
                    pdf_name = os.path.splitext(pdf_file)[0]
                    output_json = os.path.join(output_dir, f"{pdf_name}_questions.json")
                    
                    try:
                        questions = process_pdf_to_questions(pdf_path, output_json)
                        results[pdf_file] = len(questions)
                        logger.info(f"Processed {len(questions)} questions from {pdf_file}")
                    except Exception as e:
                        logger.error(f"Error processing {pdf_file}: {e}")
                        results[pdf_file] = 0
                
                total_processed = sum(results.values())
                logger.info(f"Total questions processed: {total_processed}")
                logger.info(f"JSON outputs saved to {output_dir}")
                
            else:
                # Process and store in database
                results = batch_process_pdfs(pdf_dir, output_dir)
                
                total_processed = sum(processed for processed, _ in results.values())
                total_stored = sum(stored for _, stored in results.values())
                
                logger.info(f"Total questions processed: {total_processed}")
                logger.info(f"Total questions stored in database: {total_stored}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())