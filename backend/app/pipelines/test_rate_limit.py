#!/usr/bin/env python3
"""
Test script to verify rate limiting works correctly.
This will process just the first 3 chunks to test the rate limiting mechanism.
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv

# Add the pipeline directory to the path
sys.path.append(os.path.dirname(__file__))

# Load environment variables
load_dotenv()

# Import the pipeline components
from question_ingestion import (
    GraphState, load_pdf, split_pages, parse_answer_key, 
    llm_extract, RATE_LIMIT_DELAY
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_rate_limiting():
    """Test the rate limiting with just a few chunks"""
    
    logging.info("Starting rate limit test...")
    
    # Initialize state
    state = {
        "raw_pages": [],
        "chunks": [],
        "parsed": [],
        "errors": [],
        "current_chunk_index": 0,
        "parsing_status": "",
        "answer_key": {}
    }
    
    # Load PDFs
    logging.info("Loading PDFs...")
    state = load_pdf(state)
    
    if state["errors"]:
        logging.error(f"Errors loading PDFs: {state['errors']}")
        return
    
    # Split pages
    logging.info("Splitting pages...")
    state = split_pages(state)
    
    if not state["chunks"]:
        logging.error("No chunks created")
        return
    
    # Parse answer key
    logging.info("Parsing answer key...")
    state = parse_answer_key(state)
    
    # Process only first 3 chunks to test rate limiting
    max_chunks = min(3, len(state["chunks"]))
    logging.info(f"Testing rate limiting with {max_chunks} chunks...")
    
    start_time = time.time()
    
    for i in range(max_chunks):
        state["current_chunk_index"] = i
        
        chunk_start_time = time.time()
        state = llm_extract(state)
        chunk_end_time = time.time()
        
        chunk_duration = chunk_end_time - chunk_start_time
        logging.info(f"Chunk {i+1} completed in {chunk_duration:.2f} seconds")
        
        if state["parsing_status"] == "success":
            logging.info(f"Successfully parsed chunk {i+1}")
        else:
            logging.warning(f"Failed to parse chunk {i+1}")
    
    total_time = time.time() - start_time
    logging.info(f"Total test time: {total_time:.2f} seconds")
    logging.info(f"Successfully parsed: {len(state['parsed'])} chunks")
    logging.info(f"Errors: {len(state['errors'])}")
    
    # Show some results
    for i, record in enumerate(state["parsed"][:2]):  # Show first 2 records
        if hasattr(record, 'model_dump'):
            data = record.model_dump()
        elif hasattr(record, 'dict'):
            data = record.dict()
        else:
            data = record
        logging.info(f"Record {i+1}: ID={data.get('id', 'N/A')}, Question={data.get('question_number', 'N/A')}")

if __name__ == "__main__":
    test_rate_limiting()
