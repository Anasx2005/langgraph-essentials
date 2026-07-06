# Imports 
import operator
import os
from typing import Annotated, Literal, TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

# 1. Define the State
class State(TypedDict):
    nlist: Annotated[list[str], operator.add]

# 2. Define Nodes (Node A now controls the routing dynamically)
# command return 2 things the updated state and the next node to go to
def node_a(state: State) -> Command[Literal["b", "c", END]]: 
    select = state["nlist"][-1]
    print(f"Node A processing input: {select}")
    
    if select == "b":
        next_node = "b"
    elif select == "c":
        next_node = "c"
    else:
        next_node = END

    # Command updates the state and forces the graph to move to the 'goto' node
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

# 3. Build and compile the Graph (No conditional edges needed here!)
builder = StateGraph(State)

builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)

builder.add_edge(START, "a")
builder.add_edge("b", END)
builder.add_edge("c", END)

graph = builder.compile()

# Save the visualization
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

image_path = os.path.join(output_folder, "graph_viz_lab03b.png")
with open(image_path, "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())
print(f"Graph image successfully saved to: {image_path}")

# 4. Interactive Loop
while True:
    user_input = input("Enter 'b', 'c', or 'q' to quit: ")
    if user_input == "q":
        print("Quitting program.")
        break
        
    initial_state = {"nlist": [user_input]}
    result = graph.invoke(initial_state)
    print("Execution result:", result)
    print("-" * 40)