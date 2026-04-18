import json
import os
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import ResearchState
from utils.llm import get_llm

SYSTEM = """You are a critical research reviewer.
Evaluate the research findings and return a JSON object with these keys:
  score: integer 0-10 (10 = complete, comprehensive, no gaps)
  gaps: list of strings (missing information that would improve the research)
  is_sufficient: boolean (true if score >= 7 and gaps are minor)
  reasoning: string (one sentence explaining your score)

Return ONLY valid JSON, no other text."""


def evaluate_research(state: ResearchState) -> dict:
    max_iter = int(os.getenv("MAX_ITERATIONS", "6"))
    print(f"\n[Critic] Evaluating research (iteration {state.iteration + 1}/{max_iter})")

    if state.iteration >= max_iter:
        print("[Critic] Max iterations reached, proceeding to writer")
        return {"is_sufficient": True, "knowledge_gaps": [], "iteration": state.iteration + 1}

    findings_text = "\n\n".join(state.raw_findings[-10:])
    llm = get_llm(temperature=0.1)
    response = llm.invoke([
        SystemMessage(content=SYSTEM),
        HumanMessage(content=(
            f"Original question: {state.query}\n\n"
            f"Research findings so far:\n{findings_text}"
        )),
    ])
    try:
        text = response.content.strip().replace("```json", "").replace("```", "")
        result = json.loads(text)
        score = result.get("score", 0)
        print(f"[Critic] Score: {score}/10 — {result.get('reasoning', '')}")
        if not result.get("is_sufficient", False) and result.get("gaps"):
            return {
                "is_sufficient": False,
                "knowledge_gaps": result["gaps"],
                "search_queries": result["gaps"][:3],
                "iteration": state.iteration + 1,
            }
        return {"is_sufficient": True, "knowledge_gaps": [], "iteration": state.iteration + 1}
    except (json.JSONDecodeError, KeyError):
        return {"is_sufficient": True, "knowledge_gaps": [], "iteration": state.iteration + 1}