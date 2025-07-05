import React, { useEffect, useRef } from 'react';

declare global {
  interface Window {
    MathJax: any;
  }
}

interface MathRendererProps {
  children: string;
  inline?: boolean;
  className?: string;
}

export const MathRenderer: React.FC<MathRendererProps> = ({ 
  children, 
  inline = false, 
  className = '' 
}) => {
  const mathRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Configure MathJax before loading if not already configured
    if (!window.MathJax) {
      // Set up MathJax configuration before loading the script
      window.MathJax = {
        tex: {
          inlineMath: [['$', '$'], ['\\(', '\\)']],
          displayMath: [['$$', '$$'], ['\\[', '\\]']],
          processEscapes: true,
          processEnvironments: true
        },
        options: {
          skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
        },
        startup: {
          ready: () => {
            window.MathJax.startup.defaultReady();
            renderMath();
          }
        }
      };

      // Load MathJax script
      const mathJaxScript = document.createElement('script');
      mathJaxScript.id = 'MathJax-script';
      mathJaxScript.async = true;
      mathJaxScript.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
      document.head.appendChild(mathJaxScript);
    } else {
      // MathJax is already loaded, just render
      setTimeout(renderMath, 100); // Small delay to ensure DOM is ready
    }

    function renderMath() {
      if (window.MathJax && window.MathJax.typesetPromise && mathRef.current) {
        window.MathJax.typesetPromise([mathRef.current]).catch((err: any) => 
          console.log('MathJax typeset failed: ' + err.message)
        );
      } else if (window.MathJax && window.MathJax.Hub) {
        // Fallback for MathJax v2
        window.MathJax.Hub.Queue(['Typeset', window.MathJax.Hub, mathRef.current]);
      }
    }
  }, [children]);

  // Process the text to wrap math expressions in proper delimiters
  const processedText = React.useMemo(() => {
    let text = children;
    
    // Convert function notation
    text = text.replace(/f\s*\(\s*x\s*\)/g, '$f(x)$');
    
    // Convert fractions
    text = text.replace(/(\d+)\s*\/\s*(\d+)/g, '$\\frac{$1}{$2}$');
    
    // Convert exponents
    text = text.replace(/(\w+)\^(\d+)/g, '$$$1^{$2}$$');
    text = text.replace(/(\w+)²/g, '$$$1^2$$');
    text = text.replace(/(\w+)³/g, '$$$1^3$$');
    
    // Convert square roots
    text = text.replace(/√\(([^)]+)\)/g, '$\\sqrt{$1}$');
    text = text.replace(/√(\w+)/g, '$\\sqrt{$1}$');
    
    // Convert mathematical operators
    text = text.replace(/×/g, '$\\times$');
    text = text.replace(/÷/g, '$\\div$');
    text = text.replace(/±/g, '$\\pm$');
    text = text.replace(/≤/g, '$\\leq$');
    text = text.replace(/≥/g, '$\\geq$');
    text = text.replace(/≠/g, '$\\neq$');
    text = text.replace(/∞/g, '$\\infty$');
    text = text.replace(/π/g, '$\\pi$');
    
    // Convert coordinate notation
    text = text.replace(/\(([^,]+),\s*([^)]+)\)/g, '$($$1, $2$$)$');
    
    // Convert angle notation
    text = text.replace(/(\d+)°/g, '$$$1^\\circ$$');
    
    return text;
  }, [children]);

  const Tag = inline ? 'span' : 'div';

  return (
    <Tag 
      ref={mathRef} 
      className={`math-renderer ${className} ${inline ? 'inline-math' : 'block-math'}`}
      dangerouslySetInnerHTML={{ __html: processedText }}
    />
  );
};

// Simple text formatter for when MathJax is not needed
export const formatMathText = (text: string): string => {
  if (!text) return text;
  
  // Basic cleanup without MathJax
  return text
    .replace(/\bf\s*\(\s*x\s*\)/g, 'f(x)')
    .replace(/(\d+)\s*\/\s*(\d+)/g, '$1/$2')
    .replace(/(\d+)\s*\^\s*(\d+)/g, '$1^$2')
    .replace(/\s*=\s*/g, ' = ')
    .replace(/\s*\+\s*/g, ' + ')
    .replace(/\s*\-\s*/g, ' - ')
    .replace(/\s*\*\s*/g, ' × ')
    .replace(/(\d+)\s*x\s*/g, '$1x')
    .replace(/\s+/g, ' ')
    .trim();
};

export default MathRenderer;
