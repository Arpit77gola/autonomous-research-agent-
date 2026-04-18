import os
import sys
import argparse
from dotenv import load_dotenv

load_dotenv()

from graph.state import ResearchState
from graph.graph import research_graph


def run(query: str, email: str = None) -> str:
    """Run the full autonomous research pipeline for a given query."""
    print(f"\n{'='*60}")
    print(f"  AUTONOMOUS RESEARCH AGENT")
    print(f"{'='*60}")
    print(f"  Query: {query}")
    print(f"{'='*60}\n")

    initial_state = ResearchState(query=query)
    result = research_graph.invoke(initial_state, {"recursion_limit": 50})
    report = result.get("final_report", "")

    if report:
        print(f"\n{'='*60}")
        print("  FINAL REPORT")
        print(f"{'='*60}\n")
        print(report)
    else:
        print("\n[Error] No report was generated.")
        return report

    # Send email if requested
    if email:
        output_dir = os.getenv("OUTPUT_DIR", "output")
        safe_name  = "".join(
            c if c.isalnum() or c in " _-" else "_"
            for c in query[:50]
        )
        pdf_path = os.path.join(output_dir, f"{safe_name}.pdf")

        from utils.email_sender import send_report_email
        send_report_email(
            to_email  = email,
            subject   = f"Research Report: {query}",
            report_md = report,
            pdf_path  = pdf_path if os.path.exists(pdf_path) else None,
        )

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous Research Agent — powered by Groq + Tavily + LangGraph"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Research question to investigate",
    )
    parser.add_argument(
        "--email", "-e",
        metavar="EMAIL",
        help="Send the report to this email address after generation",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive loop mode",
    )
    args = parser.parse_args()

    if args.interactive:
        print("\nAutonomous Research Agent (type 'quit' to exit)\n")
        while True:
            try:
                query = input("Research query: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break
            if not query:
                continue
            if query.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            email = input("Send report to email? (press Enter to skip): ").strip() or None
            run(query, email=email)
    elif args.query:
        run(args.query, email=args.email)
    else:
        demo = "What are the latest breakthroughs in quantum computing in 2025?"
        print(f"No query provided. Running demo query:\n  {demo}\n")
        run(demo)


if __name__ == "__main__":
    main()