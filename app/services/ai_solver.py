"""AI-powered math solver using OpenAI API (optional enhancement)."""

import json
import os
import re

import httpx

from app.config import OPENAI_API_KEY


MATH_SYSTEM_PROMPT = """You are an expert mathematics tutor. When given a math problem:

1. Identify the type of problem (algebra, calculus, geometry, statistics, etc.)
2. Provide a detailed step-by-step solution
3. Explain each step clearly
4. Give the final answer

Format your response as JSON with this structure:
{
    "type": "equation|calculus|geometry|algebra|statistics|other",
    "steps": [
        {
            "step": "Step title",
            "explanation": "Detailed explanation of this step",
            "result": "Mathematical result of this step (use LaTeX notation with $$ delimiters)"
        }
    ],
    "final_answer": "The final answer",
    "needs_graph": true/false,
    "graph_type": "function|equation|geometry|none",
    "graph_expression": "expression to plot if applicable",
    "success": true
}

Use LaTeX notation wrapped in $$ for mathematical expressions in results.
Be thorough and educational in your explanations."""


async def solve_with_ai(question: str) -> dict | None:
    """Solve a math problem using OpenAI API."""
    api_key = OPENAI_API_KEY
    if not api_key:
        return None

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": MATH_SYSTEM_PROMPT},
                        {"role": "user", "content": question},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 4000,
                },
            )

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]

                # Try to parse as JSON
                try:
                    # Find JSON in the response
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        result = json.loads(json_match.group())
                        return result
                except (json.JSONDecodeError, AttributeError):
                    pass

                # Fall back to raw text response
                return {
                    "type": "ai_response",
                    "steps": [
                        {
                            "step": "AI Solution",
                            "explanation": content,
                            "result": "",
                        }
                    ],
                    "final_answer": content,
                    "success": True,
                }
            else:
                return None

    except Exception:
        return None


async def solve_question(question: str) -> dict:
    """Solve a question using AI first, then fall back to SymPy."""
    from app.services.math_solver import analyze_question

    # Try AI solver first (if API key is available)
    ai_result = await solve_with_ai(question)
    if ai_result and ai_result.get("success"):
        ai_result["solver"] = "ai"
        return ai_result

    # Fall back to SymPy symbolic solver
    sympy_result = analyze_question(question)
    sympy_result["solver"] = "sympy"
    return sympy_result
