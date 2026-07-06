# Imports 
import operator
import os
from typing import Annotated, Literal, TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from langgraph.checkpoint.memory import InMemorySaver

# 1. Define State and Nodes (Same logic as Lab 3b)
class State(TypedDict):
    nlist: Annotated[list[str], operator.add]

def node_a(state: State) -> Command[Literal["b", "c", END]]:
    select = state["nlist"][-1]
    print(f"Node A processing input: {select}")
    
    if select == "b":
        next_node = "b"
    elif select == "c":
        next_node = "c"
    else:
        next_node = END

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

# 2. Build the Graph
builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)
builder.add_edge(START, "a")
builder.add_edge("b", END)
builder.add_edge("c", END)

# 3. Add Memory Checkpointer
memory = InMemorySaver()
# Compile the graph with checkpointer enabled
graph = builder.compile(checkpointer=memory)
# Configuration with a unique thread_id to identify this session
config = {"configurable": {"thread_id": "session_01"}}


# 4. Interactive Loop with Memory Persistence
while True:
    user_input = input("With Memory - Enter 'b', 'c', or 'q' to quit: ")
    if user_input == "q":
        print("Quitting program.")
        break
        
    initial_state = {"nlist": [user_input]}
    
    # Notice we pass the 'config' here so LangGraph loads the existing memory state
    result = graph.invoke(initial_state, config)
    print("Persistent state result:", result)
    print("-" * 40)