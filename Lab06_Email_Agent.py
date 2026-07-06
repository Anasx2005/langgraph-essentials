# Imports
import os
import uuid
from typing import Annotated, Literal, TypedDict
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# LangGraph Imports
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver

# Google Gemini Imports
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load Environment Variables
load_dotenv()

# Define Pydantic Class for structured Gemini Output
class EmailClassificationModel(BaseModel):
    intent: Literal["question", "bug", "billing", "feature", "complex"] = Field(description="The primary intent of the email")
    urgency: Literal["low", "medium", "high", "critical"] = Field(description="The urgency level of the email")
    topic: str = Field(description="Main topic or product mentioned")
    summary: str = Field(description="Brief summary of the email content")

# 2. Define the States
class EmailAgentState(TypedDict):
    email_content: str
    sender_email: str
    email_id: str
    classification: dict | None
    ticket_id: str | None
    search_results: list[str] | None
    customer_history: dict | None
    draft_response: str | None

# Initialize Gemini Model (Using gemini-2.5-flash)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# 3. Define the Nodes
def read_email(state: EmailAgentState) -> EmailAgentState:
    print(f"Reading email {state['email_id']}...")
    return state

def classify_intent(state: EmailAgentState) -> dict:
    print("Classifying email intent using Gemini...")
    # Force Gemini to return the structured dictionary output matching our Pydantic model
    structured_llm = llm.with_structured_output(EmailClassificationModel)
    
    classification_prompt = f"""
    Analyze this customer email and classify it:
    Email: {state['email_content']}
    From: {state['sender_email']}
    """
    
    response = structured_llm.invoke(classification_prompt)
    # Convert Pydantic object to dict for the graph state
    return {"classification": response.model_dump()}

def search_documentation(state: EmailAgentState) -> dict:
    print("Searching knowledge base documentation...")
    classification = state.get('classification', {})
    query = f"{classification.get('intent', '')} {classification.get('topic', '')}"
    
    # Mocking standard documentation lookup results
    search_results = [
        f"Doc Context: Policy regarding {classification.get('topic', 'general issue')}",
        "Doc Context: Standard response protocols."
    ]
    return {"search_results": search_results}

def bug_tracking(state: EmailAgentState) -> dict:
    classification = state.get('classification', {})
    if classification.get('intent') == 'bug':
        print("Generating bug tracking ticket ID...")
        return {"ticket_id": f"BUG_{uuid.uuid4()}"}
    return {"ticket_id": None}

def write_response(state: EmailAgentState) -> Command[Literal["human_review", "send_reply"]]:
    print("Drafting response message...")
    classification = state.get('classification', {})
    context_sections = []

    if state.get('search_results'):
        formatted_docs = "\n".join([f"- {doc}" for doc in state['search_results']])
        context_sections.append(f"Relevant documentation:\n{formatted_docs}")

    context_str = "\n".join(context_sections)

    draft_prompt = f"""
    Draft a brief, professional response to this customer email:
    {state['email_content']}

    Email intent: {classification.get('intent', 'unknown')}
    Urgency level: {classification.get('urgency', 'medium')}

    {context_str}
    """

    response = llm.invoke(draft_prompt)
    
    # Determine routing logic
    needs_review = (
        classification.get('urgency') in ['high', 'critical'] or
        classification.get('intent') == 'complex'
    )

    if needs_review:
        print("Urgent matter detected. Routing to Human Review...")
        goto = "human_review"
    else:
        print("Routine matter. Routing directly to Send Reply...")
        goto = "send_reply"

    return Command(
        update={"draft_response": response.content},
        goto=goto
    )

def human_review(state: EmailAgentState) -> Command[Literal["send_reply", END]]:
    classification = state.get('classification', {})
    
    # Pause graph execution and wait for human response
    human_decision = interrupt({
        "email_id": state['email_id'],
        "original_email": state['email_content'],
        "draft_response": state.get('draft_response', ""),
        "urgency": classification.get('urgency'),
        "intent": classification.get('intent'),
        "action": "Please review and approve/edit this response"
    })

    if human_decision.get("approved"):
        print("Human approved the draft.")
        return Command(
            update={"draft_response": human_decision.get("edited_response", state['draft_response'])},
            goto="send_reply"
        )
    else:
        print("Human rejected the draft. Terminal stop.")
        return Command(update={}, goto=END)

def send_reply(state: EmailAgentState) -> dict:
    print(f"Sending automated reply: {state['draft_response'][:60]}...")
    return {}

# 4. Build and compile the Graph
builder = StateGraph(EmailAgentState)

builder.add_node("read_email", read_email)
builder.add_node("classify_intent", classify_intent)
builder.add_node("search_documentation", search_documentation)
builder.add_node("bug_tracking", bug_tracking)
builder.add_node("write_response", write_response)
builder.add_node("human_review", human_review)
builder.add_node("send_reply", send_reply)

builder.add_edge(START, "read_email")
builder.add_edge("read_email", "classify_intent")
builder.add_edge("classify_intent", "search_documentation")
builder.add_edge("classify_intent", "bug_tracking")
builder.add_edge("search_documentation", "write_response")
builder.add_edge("bug_tracking", "write_response")
builder.add_edge("send_reply", END)

memory = InMemorySaver()
app = builder.compile(checkpointer=memory)

# 5. Save Graph Visualization
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
with open(os.path.join(output_folder, "graph_viz_lab06.png"), "wb") as f:
    f.write(app.get_graph().draw_mermaid_png())
print("Graph image saved to output folder.")

# 6. Test with a batch of diverse customer emails
emails = [
    "I was charged twice for my subscription! This is urgent!",
    "I was wondering if this product is available in blue?",
    "The component won't stay attached to the main dashboard, it looks like a design flaw."
]

print("\n--- Starting Email Agent Processing Loop ---")
for i, content in enumerate(emails):
    print(f"\nProcessing Case {i+1}...")
    
    initial_state = {
        "email_content": content,
        "sender_email": "customer@example.com",
        "email_id": f"email_{i+1}"
    }
    
    thread_id = f"thread_{uuid.uuid4().hex[:6]}"
    config = {"configurable": {"thread_id": thread_id}}
    
    result = app.invoke(initial_state, config)
    
    # Check if the execution stopped at an interrupt (Human in the loop)
    current_state = app.get_state(config)
    if current_state.next and current_state.tasks and current_state.tasks[0].interrupts:
        interrupt_info = current_state.tasks[0].interrupts[0].value
        print(f"\n[INTERRUPT]: Review needed for urgent email regarding '{interrupt_info.get('intent')}'")
        print(f"Generated Draft: {interrupt_info.get('draft_response')}")
        
        # Simulate human approval
        print("Simulating human approval response...")
        resume_command = Command(resume={"approved": True})
        final_result = app.invoke(resume_command, config)
        print("Status: Action completed successfully after human sign-off.")
    else:
        print("Status: Routine case closed automatically.")