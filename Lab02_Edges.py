# Imports 
import operator
import os
from typing import Annotated, Literal, TypedDict
from langgraph.graph import END, START, StateGraph

# 1. Define the State with a Reducer (operator.add) to append items instead of overwriting
class State(TypedDict):
    nlist: Annotated[list[str], operator.add ]    

# 2. Define the Nodes
def node_a(state: State) -> State:
    print(f"Node A is receiving: {state['nlist']}")
    return {"nlist": ["A"]}

def node_b(state: State) -> State:
    print(f"Node B is receiving: {state['nlist']}")
    return {"nlist": ["B"]}

def node_c(state: State) -> State:
    print(f"Node C is receiving: {state['nlist']}")
    return {"nlist": ["C"]}

def node_bb(state: State) -> State:
    print(f"Node BB is receiving: {state['nlist']}")
    return {"nlist": ["BB"]}

def node_cc(state: State) -> State:
    print(f"Node CC is receiving: {state['nlist']}")
    return {"nlist": ["CC"]}

def node_d(state: State) -> State:
    print(f"Node D is receiving: {state['nlist']}")
    return {"nlist": ["D"]}

# 3. Build and compile the Graph
builder = StateGraph(State)
# Add nodes
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)
builder.add_node("bb", node_bb)
builder.add_node("cc", node_cc)
builder.add_node("d", node_d)
# Add edges (Notice the parallel branching from 'a' to 'b' and 'c')
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "bb")
builder.add_edge("c", "cc")
builder.add_edge("bb", "d")
builder.add_edge("cc", "d")
builder.add_edge("d", END)
graph = builder.compile()


# Save the graph visualization as a PNG image in output folder
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

image_path = os.path.join(output_folder, "graph_viz_lab02.png")
image_bytes = graph.get_graph().draw_mermaid_png()
with open(image_path, "wb") as f:
    f.write(image_bytes)
print(f"Graph image successfully saved to: {image_path}")


# 4. Initialize state and invoke the graph
initial_state = {"nlist": ["Initial String:"]}
print("Starting the graph execution with initial state:", initial_state)
final_state = graph.invoke(initial_state)
print("Final state:", final_state)