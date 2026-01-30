
import subprocess
import re
import json
from typing import List, Dict, Optional, Any

from .llm_client import call_llm
from .rag_engine import add_text, get_context
from .vector_db import load_models

# Check Graphviz availability
GRAPHVIZ_AVAILABLE = False
try:
    result = subprocess.run(['dot', '-V'], capture_output=True, text=True)
    if result.returncode == 0:
        GRAPHVIZ_AVAILABLE = True
except Exception:
    GRAPHVIZ_AVAILABLE = False

# =========================================================
# GENERATORS
# =========================================================

def generate_summary() -> str:
    """Generates a 350-400 word academic summary."""
    ctx = get_context("summary main concepts", 10)
    prompt = f"""
Write a 350–400 word academic summary. Use ONLY this context:

Context:
{ctx}

Summary:
"""
    return call_llm(prompt, 0.5, 600)

def generate_five_mark(topic: str) -> str:
    """Generates a 5-mark academic answer."""
    ctx = get_context(topic, 6)
    prompt = f"""
Write a 5-mark answer (10–11 lines, 120–150 words, academic tone) for:

Topic: {topic}

Context:
{ctx}
"""
    return call_llm(prompt, 0.4, 300)

def generate_twelve_mark(topic: str) -> str:
    """Generates a 12-mark answer with ASCII flowchart."""
    ctx = get_context(topic, 8)
    prompt = f"""
Write a 12-mark answer (250–300 words) AND include this ASCII flowchart:

Start
 |
 v
[Step 1]
 |
 v
{{{{Decision?}}}}
 /   \\
Yes   No
 |     |
 v     v
[Path A]   [Path B]
 |
 v
End

Use ONLY this context:

{ctx}
"""
    return call_llm(prompt, 0.5, 900)

def generate_ascii_mindmap(topic: str) -> str:
    """Generates an ASCII mindmap."""
    ctx = get_context(topic, 5)
    prompt = f"""
Create an ASCII mindmap for topic "{topic}". Use hierarchical structure only.

Context:
{ctx}
"""
    return call_llm(prompt, 0.6, 500)

def generate_visual_mindmap(topic: str) -> Optional[str]:
    """Generates Graphviz DOT code for a mindmap."""
    if not GRAPHVIZ_AVAILABLE:
        return None

    ctx = get_context(topic, 6)
    prompt = f"""
Generate VALID Graphviz DOT code for a mindmap about "{topic}".
Return ONLY DOT code. It must begin with 'digraph' and end with '}}'.

Context:
{ctx}
"""
    dot = call_llm(prompt, 0.3, 800)
    
    # Extract code without markdown
    if "```" in dot:
        dot = re.sub(r"```.*?```", "", dot, flags=re.DOTALL).strip()
    
    if not dot.startswith("digraph"):
        return None
        
    # Fix unbalanced braces if needed
    if dot.count("{") > dot.count("}"):
        dot += "}" * (dot.count("{") - dot.count("}"))
        
    return dot

def generate_flashcards() -> List[Dict[str, str]]:
    """Generates flashcards as a list of dicts."""
    ctx = get_context("key definitions terms", 8)
    prompt = f"""
Create 5-10 flashcards based on the context.
Return raw JSON format: [{{"front": "Term", "back": "Definition"}}, ...]
Do NOT use markdown code blocks. Just the JSON.

Context:
{ctx}
"""
    response = call_llm(prompt, 0.3, 800)
    try:
        # Cleanup potential markdown around JSON
        cleaned = re.sub(r"```.*?```", "", response, flags=re.DOTALL).strip()
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []

def generate_exam_questions() -> List[str]:
    """Generates a list of probable exam questions."""
    ctx = get_context("important exam questions", 8)
    prompt = f"""
Generate 5-7 probable exam questions based on the context.
Return raw JSON string array: ["Question 1?", "Question 2?", ...]
Do NOT use markdown code blocks.

Context:
{ctx}
"""
    response = call_llm(prompt, 0.5, 500)
    try:
        cleaned = re.sub(r"```.*?```", "", response, flags=re.DOTALL).strip()
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []

def extract_formulas() -> List[str]:
    """Extracts scientific or mathematical formulas."""
    ctx = get_context("formulas equations math", 8)
    prompt = f"""
Extract all scientific formulas or mathematical equations from the context.
Return raw JSON string array: ["Formula 1", "Formula 2", ...]
If none, return [].

Context:
{ctx}
"""
    response = call_llm(prompt, 0.3, 500)
    try:
        cleaned = re.sub(r"```.*?```", "", response, flags=re.DOTALL).strip()
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []

# =========================================================
# HELPER: TOPIC EXTRACTION
# =========================================================

def _extract_main_topic() -> str:
    """Internal helper to identify the main topic from the loaded context."""
    # Use a generic query to get a broad sense of the document
    ctx = get_context("introduction title main subject", 5)
    prompt = f"""
Identify the single main topic of the text provided in the context.
Return ONLY the topic name (2-5 words). No extra text.

Context:
{ctx}
"""
    return call_llm(prompt, 0.3, 50).strip('"').strip()

# =========================================================
# MAIN PROCESSOR
# =========================================================

def process_content(text: str, source_type: str) -> Dict[str, Any]:
    """
    Main entry point. Adds text to RAG and runs all generators.
    Returns a unified JSON-ready dictionary.
    """
    # 1. Initialize logic if needed (handled by logic within get_context/add_text usually, but can force load)
    load_models()
        
    # 2. Add content
    add_text(text)
    
    # 3. Determine Topic
    main_topic = _extract_main_topic()
    if not main_topic or "API Error" in main_topic:
        main_topic = "General Content"
        
    # 4. Run Generators
    result = {
        "summary": generate_summary(),
        "five_mark_answer": generate_five_mark(main_topic),
        "twelve_mark_answer": generate_twelve_mark(main_topic),
        "mindmap_ascii": generate_ascii_mindmap(main_topic),
        "mindmap_dot": generate_visual_mindmap(main_topic),
        "flashcards": generate_flashcards(),
        "exam_questions": generate_exam_questions(),
        "formulas": extract_formulas(),
        "rag_context_used": get_context(main_topic, k=3)
    }
    
    # Ensure no None values for string fields (graphviz might return None)
    if result["mindmap_dot"] is None:
        result["mindmap_dot"] = ""

    return result
