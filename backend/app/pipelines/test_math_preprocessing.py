#!/usr/bin/env python3
"""
Test script to verify math formatting preprocessing functionality.
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from question_ingestion import preprocess_math_formatting, fix_common_sat_math_patterns

# Test cases with common corrupted math patterns
test_cases = [
    # Case 1: Fraction separation (example from the issue)
    {
        "input": "14x = 2 w + 19 7y",
        "expected_pattern": "14x = 2w + 19/7y",
        "description": "Separated fraction repair"
    },
    
    # Case 2: Square root separation
    {
        "input": "The solution is 2 √ ( w + 19 )",
        "expected_pattern": "2√(w + 19)",
        "description": "Square root repair"
    },
    
    # Case 3: Exponent separation
    {
        "input": "If x 2 + 3x = 12, find x",
        "expected_pattern": "x² + 3x",
        "description": "Exponent repair"
    },
    
    # Case 4: Complex equation with multiple issues
    {
        "input": "14x / 7y = 2 √ ( w + 19 )",
        "expected_pattern": "14x/7y = 2√(w + 19)",
        "description": "Complex equation repair"
    },
    
    # Case 5: Function notation
    {
        "input": "sin 30 degrees equals what?",
        "expected_pattern": "sin(30°)",
        "description": "Function notation repair"
    },
    
    # Case 6: Coordinate notation
    {
        "input": "Point A is at ( 3 , 4 )",
        "expected_pattern": "(3, 4)",
        "description": "Coordinate notation repair"
    },
    
    # Case 7: Percentage notation
    {
        "input": "25 percent of 80",
        "expected_pattern": "25%",
        "description": "Percentage notation repair"
    },
    
    # Case 8: Pi notation
    {
        "input": "The circumference is 2 pi r",
        "expected_pattern": "2πr",
        "description": "Pi notation repair"
    },
]

def test_math_preprocessing():
    """Test the math preprocessing functionality."""
    print("Testing Math Formatting Preprocessing")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Input:    '{test_case['input']}'")
        
        # Apply preprocessing
        result = preprocess_math_formatting(test_case['input'])
        print(f"Output:   '{result}'")
        
        # Check if the expected pattern is present in the result
        if test_case['expected_pattern'] in result:
            print("✅ PASSED")
            passed += 1
        else:
            print(f"❌ FAILED - Expected pattern '{test_case['expected_pattern']}' not found")
            failed += 1
        
        print("-" * 40)
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failed} tests failed. The preprocessing may need adjustment.")

def test_realistic_sat_questions():
    """Test with realistic SAT question examples."""
    print("\n\nTesting Realistic SAT Question Examples")
    print("=" * 50)
    
    realistic_examples = [
        {
            "input": """15. If 14x = 2 w + 19 7y , what is the value of x?
A) w + 19 14y
B) 2 w + 19 7y
C) (2w + 19) / (7y × 14)
D) 2w + 19 / 7y × 14""",
            "description": "Realistic SAT algebra question"
        },
        
        {
            "input": """22. The formula for the area of a circle is A = pi r 2. If the radius is 3, what is the area?
A) 9 pi
B) 6 pi
C) 3 pi
D) 12 pi""",
            "description": "Realistic SAT geometry question"
        },
        
        {
            "input": """8. Solve for x: 2x + 3 = √ ( 4x + 1 )
A) x = 2
B) x = 4
C) x = 1
D) x = 3""",
            "description": "Realistic SAT equation with square root"
        }
    ]
    
    for i, example in enumerate(realistic_examples, 1):
        print(f"\nRealistic Example {i}: {example['description']}")
        print(f"Original:\n{example['input']}")
        
        result = preprocess_math_formatting(example['input'])
        print(f"\nProcessed:\n{result}")
        print("-" * 60)

if __name__ == "__main__":
    test_math_preprocessing()
    test_realistic_sat_questions()
