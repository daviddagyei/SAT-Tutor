// Test script to check what's happening with "1920"

const formatAdvancedMathText = (text) => {
  if (!text) return text;
  
  let formattedText = text;
  console.log('Original text:', text);
  
  // Function notation improvements - be more specific
  formattedText = formattedText.replace(/\bf\s*\(\s*x\s*\)/gi, '<em>f</em>(<em>x</em>)');
  formattedText = formattedText.replace(/\bg\s*\(\s*x\s*\)/gi, '<em>g</em>(<em>x</em>)');
  formattedText = formattedText.replace(/\bh\s*\(\s*x\s*\)/gi, '<em>h</em>(<em>x</em>)');
  console.log('After function notation:', formattedText);
  
  // Fraction improvements using Unicode and styling - but avoid year ranges and standalone years
  // Only format fractions that have a slash and look like actual fractions
  formattedText = formattedText.replace(/\b(\d{1,3})\s*\/\s*(\d{1,3})\b/g, '<span class="fraction"><sup>$1</sup>⁄<sub>$2</sub></span>');
  console.log('After fractions:', formattedText);
  
  // Exponent formatting with proper superscripts - be more careful
  formattedText = formattedText.replace(/([a-zA-Z])\^(\d+)/g, '$1<sup>$2</sup>');
  formattedText = formattedText.replace(/([a-zA-Z])²/g, '$1<sup>2</sup>');
  formattedText = formattedText.replace(/([a-zA-Z])³/g, '$1<sup>3</sup>');
  formattedText = formattedText.replace(/([a-zA-Z])⁴/g, '$1<sup>4</sup>');
  console.log('After exponents:', formattedText);
  
  // Square root improvements
  formattedText = formattedText.replace(/√\(([^)]+)\)/g, '<span class="sqrt">√<span class="sqrt-content">$1</span></span>');
  formattedText = formattedText.replace(/√([a-zA-Z]+)/g, '<span class="sqrt">√<span class="sqrt-content">$1</span></span>');
  console.log('After square roots:', formattedText);
  
  // Mathematical operators with proper spacing
  formattedText = formattedText.replace(/\s*×\s*/g, ' × ');
  formattedText = formattedText.replace(/\s*÷\s*/g, ' ÷ ');
  formattedText = formattedText.replace(/\s*±\s*/g, ' ± ');
  formattedText = formattedText.replace(/\s*≤\s*/g, ' ≤ ');
  formattedText = formattedText.replace(/\s*≥\s*/g, ' ≥ ');
  formattedText = formattedText.replace(/\s*≠\s*/g, ' ≠ ');
  console.log('After operators:', formattedText);
  
  // Only format equals, plus, minus in clear mathematical contexts
  formattedText = formattedText.replace(/\s*=\s*(?=.*[a-zA-Z])/g, ' = ');
  formattedText = formattedText.replace(/\s*\+\s*(?=.*[a-zA-Z])/g, ' + ');
  formattedText = formattedText.replace(/\s*-\s*(?=.*[a-zA-Z])/g, ' - ');
  console.log('After equation operators:', formattedText);
  
  // Mathematical constants
  formattedText = formattedText.replace(/\bπ\b/g, '<em>π</em>');
  formattedText = formattedText.replace(/\b∞\b/g, '<em>∞</em>');
  console.log('After constants:', formattedText);
  
  // MUCH more conservative variable italicization
  // Only italicize single variables that are clearly in mathematical equations
  // Look for patterns like "x = 5", "2x + 3", "f(x)", etc.
  formattedText = formattedText.replace(/\b([a-z])\s*=\s*(\d+|[a-z])/g, '<em>$1</em> = $2');
  formattedText = formattedText.replace(/(\d+)\s*([a-z])\s*([+\-*/=])/g, '$1<em>$2</em>$3');
  formattedText = formattedText.replace(/([+\-*/=])\s*([a-z])\s*(\d+)/g, '$1<em>$2</em>$3');
  formattedText = formattedText.replace(/([+\-*/=])\s*(\d+)\s*([a-z])\b/g, '$1$2<em>$3</em>');
  console.log('After variable italics:', formattedText);
  
  // Coordinate notation - only for clear coordinate pairs
  formattedText = formattedText.replace(/\((-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)\)/g, '(<em>$1</em>, <em>$2</em>)');
  console.log('After coordinates:', formattedText);
  
  // Clean up extra spaces
  formattedText = formattedText.replace(/\s+/g, ' ').trim();
  console.log('Final result:', formattedText);
  
  return formattedText;
};

// Test cases
console.log('=== Testing "1920" ===');
formatAdvancedMathText('1920');

console.log('\n=== Testing "In 1920, the temperature was" ===');
formatAdvancedMathText('In 1920, the temperature was');

console.log('\n=== Testing "(1920)" ===');
formatAdvancedMathText('(1920)');

console.log('\n=== Testing "from 1920 to 1930" ===');
formatAdvancedMathText('from 1920 to 1930');
