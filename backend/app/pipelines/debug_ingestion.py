#!/usr/bin/env python3
import os
import json
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_pipeline():
    """Debug version to identify issues"""
    
    # Test 1: Check if JSON file exists
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "public", "digital_sat_full.json")
    print(f"Looking for JSON file at: {json_path}")
    print(f"File exists: {os.path.exists(json_path)}")
    
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            print(f"Successfully loaded JSON with {len(data)} items")
            print(f"First item keys: {list(data[0].keys()) if data else 'No items'}")
            
            # Test 2: Check if we can create a simple record
            if data:
                from question_ingestion import QARecord
                try:
                    record = QARecord(**data[0])
                    print(f"Successfully created QARecord: {record.id}")
                except Exception as e:
                    print(f"Failed to create QARecord: {e}")
                    print(f"Data structure: {data[0]}")
                    
        except Exception as e:
            print(f"Error loading JSON: {e}")
    
    # Test 3: Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"OpenAI API key present: {api_key is not None}")
    if api_key:
        print(f"API key length: {len(api_key)}")
    
    # Test 4: Test the workflow compilation
    try:
        from question_ingestion import workflow
        app = workflow.compile(recursion_limit=5)
        print("Workflow compilation successful")
    except Exception as e:
        print(f"Workflow compilation failed: {e}")

if __name__ == "__main__":
    debug_pipeline()
