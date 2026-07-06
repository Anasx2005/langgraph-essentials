# Imports 
import operator
import os
from typing import Annotated, Literal, TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver

# 1. Setup Memory and Config
memory = InMemorySaver()
config = {"configurable": {"thread_id": "session_05"}}

# 2. Define the State
class State(TypedDict):
    nlist: Annotated[list[str], operator.add]

# 3. Define Nodes (Node A uses interrupt for unexpected inputs)
def node_a(state: State) -> Command[Literal["b", "c", END]]:
    print("Entered 'a' node")
    select = state["nlist"][-1]
    
    if select == "b":
        next_node = "b"
    elif select == "c":
        next_node = "c"
    elif select == "q":
        next_node = END
    else:
        # If input is unexpected, pause the graph and wait for human decision
        admin = interrupt(f"Unexpected input '{select}'")
        print(f"Human decision received in node: {admin}")
        
        if admin == "continue":
            next_node = "b"
        else:
            next_node = END
            select = "q"
            
    return Command(
        update={"nlist": [select]},
        goto=next_node
    )

def node_b(state: State) -> dict:
    print(f"Node B received: {state['nlist']}")
    return {"nlist": ["B"]}

def node_c(state: State) -> dict:
    print(f"Node C received: {state['nlist']}")
    return {"nlist": ["C"]}

# 4. Build and compile the Graph with memory
builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)

builder.add_edge(START, "a")
builder.add_edge("b", END)
builder.add_edge("c", END)

graph = builder.compile(checkpointer=memory) 

# Save the visualization
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

image_path = os.path.join(output_folder, "graph_viz_lab05.png")
with open(image_path, "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())
print(f"Graph image successfully saved to: {image_path}")

# 5. Interactive Loop handling Interrupts
while True:
    user_input = input("\nEnter 'b', 'c', or 'q' to quit (or anything else to trigger interrupt): ")
    input_state = {"nlist": [user_input]}
    
    result = graph.invoke(input_state, config)

    # Check if the graph paused because of an interrupt
    # In newer versions of LangGraph, we can check for state keys or handle via loop
    if isinstance(result, dict) and 'nlist' in result and result['nlist'][-1] == "q":
        print("Quitting program.")
        break
    
    # Check the state to see if it is currently interrupted
    current_state = graph.get_state(config)
    if current_state.next and current_state.tasks and current_state.tasks[0].interrupts:
        # Get the interrupt message
        interrupt_msg = current_state.tasks[0].interrupts[0].value
        print(f"\n[INTERRUPT TRIGGERED]: {interrupt_msg}")
        
        human_decision = input("Type 'continue' to route to Node B, or anything else to quit: ")
        
        # Resume the graph by passing a Command with the human response
        resume_command = Command(resume=human_decision)
        result = graph.invoke(resume_command, config)
        print("Result after resume:", result)
        
        if result['nlist'][-1] == "q":
            print("Quitting program after interrupt choice.")
            break
        