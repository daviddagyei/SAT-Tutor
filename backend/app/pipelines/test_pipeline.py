#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from question_ingestion import load_pdf, split_pages

def test_pipeline():
    """Test the pipeline step by step"""
    print("=" * 50)
    print("TESTING SAT QUESTION INGESTION PIPELINE")
    print("=" * 50)
    
    # Test 1: Check PDF files
    current_dir = os.path.dirname(__file__)
    questions_pdf = os.path.join(current_dir, "sat-questions.pdf")
    answers_pdf = os.path.join(current_dir, "sat_answers.pdf")
    
    print(f"1. PDF File Check:")
    print(f"   Questions PDF: {os.path.exists(questions_pdf)} ({questions_pdf})")
    print(f"   Answers PDF: {os.path.exists(answers_pdf)} ({answers_pdf})")
    
    # Test 2: Load PDFs
    print(f"\n2. Loading PDFs...")
    state = {
        'raw_pages': [],
        'chunks': [],
        'parsed': [],
        'errors': [],
        'current_chunk_index': 0,
        'parsing_status': ''
    }
    
    try:
        result = load_pdf(state)
        print(f"   Pages loaded: {len(result.get('raw_pages', []))}")
        print(f"   Errors: {result.get('errors', [])}")
        
        if result.get('raw_pages'):
            print(f"   First page preview: {result['raw_pages'][0].page_content[:200]}...")
            
            # Test 3: Split pages
            print(f"\n3. Splitting pages...")
            split_result = split_pages(result)
            print(f"   Chunks created: {len(split_result.get('chunks', []))}")
            print(f"   Split errors: {split_result.get('errors', [])}")
            
            if split_result.get('chunks'):
                print(f"   First chunk preview: {split_result['chunks'][0][:200]}...")
        
    except Exception as e:
        print(f"   Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_pipeline()
