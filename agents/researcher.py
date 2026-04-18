from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import ResearchState, Source
from tools.search import web_search
from utils.llm import get_llm

SYSTEM = """You are a research analyst.
Given web search results, extract the most important facts, statistics,
and insights as concise bullet points. Focus on substance, not fluff.
Include specific numbers, dates, and names where available."""


def run_research(state: ResearchState) -> dict:
    print(f"\n[Researcher] Running {len(state.search_queries)} searches...")
    all_sources: list[Source] = []
    all_findings: list[str] = []
    llm = get_llm(temperature=0.1)

    for i, query in enumerate(state.search_queries):
        print(f"  [{i+1}/{len(state.search_queries)}] Searching: {query}")
        sources = web_search(query)
        if not sources:
            continue
        all_sources.extend(sources)

        context = "\n\n".join(
            f"Source: {s.title}\nURL: {s.url}\nContent: {s.snippet[:300]}"
            for s in sources
        )[:2000]  # hard cap on total context
        response = llm.invoke([
            SystemMessage(content=SYSTEM),
            HumanMessage(content=(
                f"Sub-question: {query}\n\n"
                f"Search results:\n{context}"
            )),
        ])
        all_findings.append(f"## Sub-question: {query}\n{response.content}")

    print(f"[Researcher] Collected {len(all_sources)} sources")
    return {"sources": all_sources, "raw_findings": all_findings}