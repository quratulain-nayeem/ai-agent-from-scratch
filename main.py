from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.prebuilt import create_react_agent
from tools import search_tool, wiki_tool, save_tool
import json

load_dotenv()

# -----------------------------
# Schema for structured research
# -----------------------------
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]


# -----------------------------
# Models
# -----------------------------
chat_llm = ChatGroq(model="llama-3.3-70b-versatile")
research_llm = ChatGroq(model="llama-3.3-70b-versatile")

parser = PydanticOutputParser(pydantic_object=ResearchResponse)

tools = [search_tool, wiki_tool, save_tool]
research_agent = create_react_agent(research_llm, tools)


# -----------------------------
# Query classifier
# -----------------------------
def is_research_query(query: str) -> bool:
    research_keywords = [
        "research", "analyze", "explain", "compare",
        "history", "impact", "causes", "statistics",
        "data", "sources", "study"
    ]
    return any(word in query.lower() for word in research_keywords)


# -----------------------------
# Conversational Mode
# -----------------------------
def run_chat(query: str):
    response = chat_llm.invoke(query)
    return response.content


# -----------------------------
# Research Mode
# -----------------------------
def run_research(query: str):
    system_prompt = f"""
You are Q.AI, an elite research intelligence system.

If the query requires research:
- Use tools when necessary.
- Respond ONLY in valid JSON.
- Follow this exact schema:
{parser.get_format_instructions()}

Do not include extra text outside JSON.
"""

    raw = research_agent.invoke({
        "messages": [
            ("system", system_prompt),
            ("human", query)
        ]
    })

    # Extract final AI message only
    final_message = None
    for msg in reversed(raw["messages"]):
        if msg.type == "ai":
            final_message = msg.content
            break

    if not final_message:
        return None, "No valid response returned."

    try:
        structured = parser.parse(final_message)
        return structured, None
    except Exception:
        return None, final_message


# -----------------------------
# CLI Loop
# -----------------------------
if __name__ == "__main__":
    query = input("What can I help you with? ")

    if is_research_query(query):
        structured, fallback = run_research(query)

        if structured:
            print("\n--- Structured Research Output ---\n")
            print("Topic:", structured.topic)
            print("\nSummary:", structured.summary)
            print("\nSources:", structured.sources)
            print("\nTools Used:", structured.tools_used)
        else:
            print("\nAgent Response:\n")
            print(fallback)
    else:
        response = run_chat(query)
        print("\nQ.AI:\n")
        print(response)