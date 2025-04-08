from typing import Dict, List, TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
# from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from app.core.logger import get_logger
from app.core.llm_provider import llm_provider

load_dotenv()
logger = get_logger(__name__)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    question: str
    context: str
    answer: str

class QAChain:
    """A class to handle the QA chain functionality using LangGraph's Plan & Execute pattern."""
    
    def __init__(self, context: str):
        """Initialize the QA chain with the given context."""
        self.context = context
        self.workflow = None
        self.llm = llm_provider.get_llm()
        logger.debug("QAChain initialized with context")
    
    def create_planner(self):
        """Create the planning agent."""
        logger.debug("Creating planning agent")
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a planning agent that breaks down questions into steps.
            Given a question and context, create a plan to answer it.
            The plan should be a list of steps that will help answer the question.
            Each step should be clear and specific."""),
            ("human", "Question: {question}\nContext: {context}")
        ])
        return prompt | self.llm
    
    def create_executor(self):
        """Create the execution agent."""
        logger.debug("Creating execution agent")
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an execution agent that answers questions based on the given context.
            You must only use information from the provided context.
            If the context doesn't contain enough information to answer the question, say so.
            Be precise and concise in your answers."""),
            ("human", "Question: {question}\nContext: {context}")
        ])
        return prompt | self.llm
    
    def planner(self, state: AgentState) -> Dict:
        """Plan the steps to answer the question."""
        logger.debug("Planning steps for question")
        planner_chain = self.create_planner()
        plan = planner_chain.invoke({
            "question": state["question"],
            "context": self.context
        })
        return {"plan": plan.content}
    
    def executor(self, state: AgentState) -> Dict:
        """Execute the plan and generate the answer."""
        logger.debug("Executing plan and generating answer")
        executor_chain = self.create_executor()
        answer = executor_chain.invoke({
            "question": state["question"],
            "context": self.context
        })
        return {"answer": answer.content}
    
    def create_workflow(self):
        """Create and compile the workflow."""
        logger.debug("Creating workflow")
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("planner", self.planner)
        workflow.add_node("executor", self.executor)
        
        # Add edges
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", END)
        
        # Set entry point
        workflow.set_entry_point("planner")
        
        # Compile
        self.workflow = workflow.compile()
        logger.debug("Workflow created and compiled")
    
    def get_answer(self, question: str) -> Dict:
        """Get an answer for the given question."""
        if not self.workflow:
            self.create_workflow()
        
        logger.info(f"Getting answer for question: {question}")
        response = self.workflow.invoke({
            "messages": [],
            "question": question,
            "context": self.context,
            "answer": ""
        })
        
        logger.debug("Answer generated successfully")
        return response

def create_qa_chain(context: str) -> QAChain:
    """Factory function to create a QAChain instance."""
    return QAChain(context) 