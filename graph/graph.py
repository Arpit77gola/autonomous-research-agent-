from langgraph.graph import StateGraph, END

from graph.state import ResearchState
from agents.planner import plan_research
from agents.researcher import run_research
from agents.critic import evaluate_research
from agents.writer import write_report


def should_continue(state: ResearchState) -> str:
    """Route after critic: loop back to researcher or proceed to writer."""
    if state.is_sufficient:
        return "write"
    return "research"


def build_graph() -> StateGraph:
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("planner", plan_research)
    graph.add_node("researcher", run_research)
    graph.add_node("critic", evaluate_research)
    graph.add_node("writer", write_report)

    # Entry point
    graph.set_entry_point("planner")

    # Edges
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "critic")

    # Conditional: critic decides whether to loop or finish
    graph.add_conditional_edges(
        "critic",
        should_continue,
        {
            "research": "researcher",   # gap found → research more
            "write": "writer",          # sufficient → write report
        },
    )

    graph.add_edge("writer", END)

    return graph.compile()


# Singleton compiled graph
research_graph = build_graph()
