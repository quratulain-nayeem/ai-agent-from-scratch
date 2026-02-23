from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.prebuilt import create_react_agent
from tools import search_tool, wiki_tool, save_tool

load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

llm = ChatGroq(model="llama-3.1-8b-instant")
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

tools = [search_tool, wiki_tool, save_tool]
agent = create_react_agent(llm, tools)

query = input("What can I help you research? ")
raw_response = agent.invoke({"messages": [("human", query)]})

try:
    last_message = raw_response["messages"][-1].content
    structured_response = parser.parse(last_message)
    print(structured_response)
except Exception as e:
    last_message = raw_response["messages"][-1].content
    print("Agent Response:", last_message)