import json
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import ResearchState
from utils.llm import get_llm

SYSTEM = """You are a research planning expert.
Given a research question, produce a JSON object with exactly these keys:
  research_plan: list of 3-5 specific sub-questions to answer
  search_queries: list of precise web search strings (one per sub-question)

Return ONLY valid JSON, no other text."""


def plan_research(state: ResearchState) -> dict:
    print(f"\n[Planner] Planning research for: {state.query}")
    llm = get_llm(temperature=0.2)
    response = llm.invoke([
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"Research question: {state.query}"),
    ])
    try:
        text = response.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        plan = json.loads(text)
        print(f"[Planner] Created {len(plan['research_plan'])} sub-questions")
        return {
            "research_plan": plan["research_plan"],
            "search_queries": plan["search_queries"],
        }
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[Planner] JSON parse failed: {e}, using fallback")
        return {
            "research_plan": [state.query],
            "search_queries": [state.query],
        }