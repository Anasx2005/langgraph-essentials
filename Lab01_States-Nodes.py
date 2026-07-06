# Imports 
import operator
import os
from typing import Annotated, Literal, TypedDict
from langgraph.graph import END, START, StateGraph

# 1. Define the State
class State(TypedDict):
    nlist: list[str]

# 2. Define the Node
def node_a(state:State) -> State:
    print(f"Node A is receiving: {state['nlist']}")
    msg = "Hello world from node a"
    return {"nlist": [msg]}

# 3. Build and compile the Graph
builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_edge(START,"a")
builder.add_edge("a",END)
graph = builder.compile()

# Save the graph visualization as a PNG image in output folder
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

image_path = os.path.join(output_folder, "graph_viz_lab01.png")
image_bytes = graph.get_graph().draw_mermaid_png()
with open(image_path, "wb") as f:
    f.write(image_bytes)
print(f"Graph image successfully saved to: {image_path}")


# 4. Initialize state and invoke the graph
initial_state = {"nlist":["Hello node a ,how are you ?"]}
print("Starting the graph execution with initial state:", initial_state )
final_state = graph.invoke(initial_state)
print("Final state:", final_state)







    
