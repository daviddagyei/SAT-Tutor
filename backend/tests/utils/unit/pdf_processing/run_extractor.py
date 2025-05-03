"""
Script to run the PDF extractor on the sample PDF file
"""
import os
import sys
import json
from pathlib import Path

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.insert(0, project_root)

# Import the PDF extractor
from app.utils.pdf_processing.extractor import extract_text_from_pdf

def main():
    # Path to the PDF file
    pdf_path = os.path.join(os.path.dirname(__file__), "sample_pdfs", "sat-practice-test-4.pdf")
    
    # Check if the file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return
    
    print(f"Processing PDF file: {pdf_path}")
    
    try:
        # Extract text from the PDF
        result = extract_text_from_pdf(pdf_path)
        
        # Print the number of pages extracted
        print(f"Successfully processed {len(result)} pages")
        
        # Print a preview of each page
        for page_num, text in result.items():
            preview = text[:100] + "..." if len(text) > 100 else text
            print(f"\nPage {page_num} preview:")
            print(preview)
        
        # Save the extracted text to a JSON file
        output_path = os.path.join(os.path.dirname(__file__), "output", "extracted_text.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\nFull extracted text saved to: {output_path}")
        
    except Exception as e:
        print(f"Error processing PDF: {e}")

if __name__ == "__main__":
    main()