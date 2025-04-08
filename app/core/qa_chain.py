from typing import Dict, List, TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
# from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

from app.core.llm_provider import llm

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    question: str
    context: str
    answer: str

def create_planner():
    """Create the planning agent."""
    # llm = ChatOpenAI(model="gpt-4", temperature=0)

    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a planning agent that breaks down questions into steps.
        Given a question and context, create a plan to answer it.
        The plan should be a list of steps that will help answer the question.
        Each step should be clear and specific."""),
        ("human", "Question: {question}\nContext: {context}")
    ])
    
    return prompt | llm

def create_executor():
    """Create the execution agent."""
    # llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an execution agent that answers questions based on the given context.
        You must only use information from the provided context.
        If the context doesn't contain enough information to answer the question, say so.
        Be precise and concise in your answers."""),
        ("human", "Question: {question}\nContext: {context}")
    ])
    
    return prompt | llm

def create_qa_chain(context: str):
    """Create the QA chain using LangGraph's Plan & Execute pattern."""
    
    def planner(state: AgentState) -> Dict:
        """Plan the steps to answer the question."""
        planner_chain = create_planner()
        plan = planner_chain.invoke({
            "question": state["question"],
            "context": context
        })
        return {"plan": plan.content}
    
    def executor(state: AgentState) -> Dict:
        """Execute the plan and generate the answer."""
        executor_chain = create_executor()
        answer = executor_chain.invoke({
            "question": state["question"],
            "context": context
        })
        return {"answer": answer.content}
    
    # Create the workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", planner)
    workflow.add_node("executor", executor)
    
    # Add edges
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", END)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Compile
    app = workflow.compile()
    
    return app 