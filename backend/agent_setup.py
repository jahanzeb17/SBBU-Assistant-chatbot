
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from database.chroma_utils import vectorstore
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, END, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage
# from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os
# from IPython.display import Image, display
from dotenv import load_dotenv

load_dotenv()

# conn = sqlite3.connect("history.db", check_same_thread=False)
# memory = SqliteSaver(conn)


retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

@tool
def web_search_tool(query: str) -> str:
    """Up-to-date web info via Tavily"""
    tavily = TavilySearch(max_results=3, topic="general")

    try:
        result = tavily.invoke({"query": query})

        # Extract and format the results from Tavily response
        if isinstance(result, dict) and 'results' in result:
            formatted_results = []
            for item in result['results']:
                title = item.get('title', 'No title')
                content = item.get('content', 'No content')
                url = item.get('url', '')
                formatted_results.append(f"Title: {title}\nContent: {content}\nURL: {url}")

            return "\n\n".join(formatted_results) if formatted_results else "No results found"
        else:
            return str(result)
    except Exception as e:
        return f"WEB_ERROR::{e}"

@tool
def rag_search_tool(query: str) -> str:
    """Top-3 chunks from KB (empty string if none)"""
    try:
        docs = retriever.invoke(query)
        return "\n\n".join(d.page_content for d in docs) if docs else ""
    except Exception as e:
        return f"RAG_ERROR::{e}"


llm = ChatGroq(model="llama-3.3-70b-versatile",temperature=0)

llm_with_tools = llm.bind_tools([rag_search_tool, web_search_tool])

sys_msg = """You are a polite and conversational university assistant also be the conversational with users. 
You can handle greetings, small talk, and general queries in a friendly manner. 
If the user greets you (e.g., "hi", "hello"), respond warmly and conversationally before deciding on routing. 
Always give first priority to the university database for any query related to university data (e.g., syllabus, courses, exam schedules, facilities, teacher profiles, handbooks, academic PDFs). 
If the query is not related to the university, only then route it to web_search for current or global knowledge. 
Never send university-related queries to web_search.
Always answer to the point not long answer.
"""

def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([SystemMessage(content=sys_msg)] + state["messages"])]}


builder = StateGraph(MessagesState)

builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode([rag_search_tool, web_search_tool]))

builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges(
    "tool_calling_llm",
    tools_condition
)
builder.add_edge("tools", "tool_calling_llm")
# builder.add_edge("tools", END)


# agent = builder.compile(checkpointer=memory)
agent = builder.compile()


# if __name__=="__main__":

#     config = {"configurable": {"thread_id": "12"}}
#     while True:

#         user_input = input('Enter query here: ')
#         if user_input == "q":
#             break
#         else:
#             response = agent.invoke({"messages": {"role": "user", "content": user_input}}, config)
#             print(response["messages"][-1].content)