# Imports
import operator
import os
from typing import Annotated, Literal, TypedDict
from langgraph.graph import END, START, StateGraph

# 1. Define the State
class State(TypedDict):
    nlist: Annotated[list[str], operator.add]

# 2. Define the Nodes
def node_a(state: State) -> None:
    # This node just passes through, the decision happens in the edge
    print(f"Node A received: {state['nlist']}")
    return

def node_b(state: State) -> dict:
    print(f"Node B received: {state['nlist']}")
    return {"nlist": ["B"]}

def node_c(state: State) -> dict:
    print(f"Node C received: {state['nlist']}")
    return {"nlist": ["C"]}

# 3. Define the Conditional Edge Logic
def conditional_edge(state: State) -> Literal["b", "c", END]:
    select = state["nlist"][-1]
    if select == "b":
        return "b"
    elif select == "c":
        return "c"
    else:
        return END

# 4. Build and compile the Graph
builder = StateGraph(State)

builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)

builder.add_edge(START, "a")
builder.add_edge("b", END)
builder.add_edge("c", END)

# Add conditional routing after node "a"
builder.add_conditional_edges("a", conditional_edge)

graph = builder.compile()

# Save the visualization
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

image_path = os.path.join(output_folder, "graph_viz_lab03a.png")
with open(image_path, "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())
print(f"Graph image successfully saved to: {image_path}")

# 5. Get user input and invoke
user_input = input("Enter 'b' for Node B, 'c' for Node C, or 'q' to quit: ")

initial_state = {"nlist": [user_input]}
print("Starting graph execution...")
final_state = graph.invoke(initial_state)
print("Final state:", final_state)