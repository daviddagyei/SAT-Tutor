"""
Tests for the PDF text processing functionality
"""
import pytest
from typing import Dict

from backend.app.utils.pdf_processing.processor import (
    process_text_to_sections,
    extract_questions_from_section,
    extract_math_questions,
    extract_reading_writing_questions,
    SATSection
)


class TestPDFProcessor:
    """Test suite for PDF processor module"""
    
    def test_process_text_to_sections_math(self):
        """Test identification of math sections in text"""
        # Sample text with Math section header
        text_by_page = {
            1: "SAT Practice Test\nPage 1",
            2: "MATH TEST - No Calculator\nQuestion 1: What is the area of a circle with radius 5?\nA) 25π\nB) 10π\nC) 5π\nD) 20π"
        }
        
        sections = process_text_to_sections(text_by_page)
        
        assert SATSection.MATH in sections
        assert len(sections[SATSection.MATH]) == 1
        assert "MATH TEST" in sections[SATSection.MATH][0]
        assert "circle with radius 5" in sections[SATSection.MATH][0]
        
    def test_process_text_to_sections_reading_writing(self):
        """Test identification of reading and writing sections in text"""
        # Sample text with Reading and Writing section header
        text_by_page = {
            1: "SAT Practice Test\nPage 1",
            2: "Reading and Writing Section\nPassage 1\nThe following passage discusses climate change...\n\nQuestion 1: According to the passage, what is the main cause of climate change?"
        }
        
        sections = process_text_to_sections(text_by_page)
        
        assert SATSection.READING_WRITING in sections
        assert len(sections[SATSection.READING_WRITING]) == 1
        assert "Reading and Writing Section" in sections[SATSection.READING_WRITING][0]
        assert "passage discusses climate change" in sections[SATSection.READING_WRITING][0]
        
    def test_process_text_with_multiple_sections(self):
        """Test processing text with multiple sections"""
        # Sample text with both Math and Reading/Writing sections
        text_by_page = {
            1: "MATH TEST - Calculator\nQuestion 1: Solve 2x + 3 = 7.",
            2: "Reading Test\nPassage: The history of astronomy is fascinating...\nQuestion 1: What does the author suggest about early astronomers?"
        }
        
        sections = process_text_to_sections(text_by_page)
        
        assert SATSection.MATH in sections
        assert SATSection.READING_WRITING in sections
        assert "Solve 2x + 3 = 7" in sections[SATSection.MATH][0]
        assert "history of astronomy" in sections[SATSection.READING_WRITING][0]
        
    def test_extract_math_questions(self):
        """Test extraction of math questions"""
        math_text = """
        MATH TEST - Calculator
        
        1) If x + 3 = 7, what is the value of x?
        A) 2
        B) 3
        C) 4
        D) 5
        
        2) What is the area of a rectangle with length 8 and width 5?
        A) 13
        B) 26
        C) 40
        D) 80
        
        3. Solve for y: 2y - 4 = 10
        """
        
        questions = extract_math_questions(math_text)
        
        assert len(questions) == 3
        
        # Check first question
        assert questions[0]["question_number"] == "1"
        assert "x + 3 = 7" in questions[0]["text"]
        assert len(questions[0]["options"]) == 4
        assert questions[0]["options"][0]["id"] == "A"
        assert questions[0]["options"][0]["text"] == "2"
        
        # Check third question (grid-in)
        assert questions[2]["question_number"] == "3"
        assert "2y - 4 = 10" in questions[2]["text"]
        assert questions[2]["question_type"] == "grid_in"  # Should be identified as grid-in
        
    def test_extract_reading_writing_questions(self):
        """Test extraction of reading and writing questions"""
        reading_text = """
        Reading and Writing Section
        
        Passage:
        The environmental impact of plastic pollution has become increasingly evident in recent years.
        Marine ecosystems are particularly vulnerable to plastic debris that enters oceans and waterways.
        
        1) According to the passage, which ecosystem is most affected by plastic pollution?
        A) Forests
        B) Deserts
        C) Marine environments
        D) Mountains
        
        2) The author's tone in this passage could best be described as:
        A) critical
        B) informative
        C) enthusiastic
        D) dismissive
        """
        
        questions = extract_reading_writing_questions(reading_text)
        
        assert len(questions) == 2
        
        # Check first question
        assert questions[0]["question_number"] == "1"
        assert "According to the passage" in questions[0]["text"]
        assert questions[0]["question_type"] == "reading_comprehension"
        assert len(questions[0]["options"]) == 4
        
        # Check for context/passage attachment
        assert "context" in questions[0]
        assert "environmental impact" in questions[0]["context"]
        
    def test_extract_questions_from_section(self):
        """Test the section-specific question extraction dispatch"""
        # Math section text
        math_text = "MATH TEST\n1) What is 2+2?\nA) 3\nB) 4\nC) 5\nD) 6"
        
        # Extract questions from math section
        math_questions = extract_questions_from_section(math_text, SATSection.MATH)
        
        assert len(math_questions) == 1
        assert math_questions[0]["section"] == SATSection.MATH
        assert "2+2" in math_questions[0]["text"]
        
        # Reading section text
        reading_text = "Reading Test\nPassage: Science is fascinating.\n1) According to the passage, science is:\nA) boring\nB) fascinating\nC) difficult\nD) unnecessary"
        
        # Extract questions from reading section
        reading_questions = extract_questions_from_section(reading_text, SATSection.READING_WRITING)
        
        assert len(reading_questions) == 1
        assert reading_questions[0]["section"] == SATSection.READING_WRITING
        assert "According to the passage" in reading_questions[0]["text"]