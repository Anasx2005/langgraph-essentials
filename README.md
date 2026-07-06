# 🦜🔗 LangGraph Essentials Course - Portfolio

Welcome to my comprehensive portfolio documenting my journey through the **LangGraph Essentials Course**.

This repository contains production-ready Python implementations of all course labs, converted from the original Jupyter Notebooks into clean, modular Python scripts (`.py`). The implementations primarily use **Google Gemini** as the LLM provider while also demonstrating interoperability with **OpenAI** models through LangChain integrations.

The goal of this repository is not only to complete the course exercises, but also to organize them into a production-style project that demonstrates real-world LangGraph concepts such as state management, routing, memory, human-in-the-loop workflows, and enterprise agent architectures.

---

# 🚀 Technical Highlights & Tech Stack

- **Framework:** LangGraph
  - StateGraph
  - Command Routing
  - Interrupts
  - START / END Nodes
  - InMemorySaver
- **LLM Providers**
  - Google Gemini (`gemini-2.5-flash`)
  - OpenAI (`gpt-4o-mini`)
- **LangChain Integrations**
  - LangChain Google GenAI
  - LangChain OpenAI
- **Data Validation**
  - Pydantic
  - Structured JSON Outputs
- **State Management**
  - TypedDict
  - Reducers
  - `Annotated`
  - `operator.add`
- **Environment**
  - Python
  - python-dotenv
  - Virtual Environments (`venv`)

---

# 📚 Course Curriculum

| Lab | Topic | State Management | Flow Control | Memory |
|------|--------|-----------------|--------------|--------|
| **Lab 01** | States & Nodes Foundations | Overwrite | Linear | ❌ |
| **Lab 02** | Parallel Execution (Fan-out/Fan-in) | Append (`operator.add`) | Parallel | ❌ |
| **Lab 03a** | Conditional Routing | Append | Conditional Edges | ❌ |
| **Lab 03b** | Dynamic Routing using Command | Append | Command Routing | ❌ |
| **Lab 04** | Chatbot Memory | Append | Dynamic Routing | ✅ InMemorySaver |
| **Lab 05** | Human-In-The-Loop | Append | Interrupt & Resume | ✅ InMemorySaver |
| **Lab 06** | Enterprise Email Agent | Custom State | Multi-path + HITL | ✅ Multi-thread |

---

# 🛠️ Lab Breakdown

---

## 📁 Lab 01 — States & Nodes Foundations

### Concepts

- Understanding what a StateGraph is
- Creating a TypedDict state
- Writing graph nodes
- Building a linear graph

### Key Takeaways

A LangGraph application revolves around a shared **state object**.

Every node:

- receives the current state
- performs some computation
- returns only the keys that changed

Example execution:

```
START
   ↓
 Node A
   ↓
 END
```

By default, if a node returns an existing key, the previous value is **overwritten**.

---

## 📁 Lab 02 — Parallel Execution & Reducers

### Concepts

- Parallel execution
- Fan-Out / Fan-In
- Reducers
- operator.add

Instead of overwriting values, reducers allow multiple nodes to safely contribute to the same state.

Example:

```python
class State(TypedDict):
    nlist: Annotated[list[str], operator.add]
```

Now every node appends instead of replacing.

Architecture:

```
         START
            |
         Node A
        /      \
   Node B    Node C
        \      /
        Node D
           |
          END
```

LangGraph automatically waits until all parallel branches complete before moving to the next node.

---

## 📁 Lab 03a — Conditional Routing

### Concepts

- add_conditional_edges()
- External routing functions

Routing decisions are separated from business logic.

Example:

```
Node A
   |
Condition Function
  /        \
 B          C
```

---

## 📁 Lab 03b — Dynamic Routing with Command

Instead of defining routing outside the node, the node itself decides where execution goes.

Example:

```python
def node_a(state: State) -> Command[Literal["b", "c", END]]:

    selection = state["nlist"][-1]

    if selection == "b":
        next_node = "b"
    elif selection == "c":
        next_node = "c"
    else:
        next_node = END

    return Command(
        update={
            "nlist": [selection]
        },
        goto=next_node
    )
```

This combines

- State updates
- Routing
- Business logic

inside one atomic operation.

---

## 📁 Lab 04 — Memory & Checkpointers

Graphs normally forget everything after execution.

Adding an `InMemorySaver()` changes that.

```python
memory = InMemorySaver()

graph.compile(
    checkpointer=memory
)
```

Using

```python
config = {
    "configurable": {
        "thread_id": "user1"
    }
}
```

allows the graph to restore previous conversations.

The same `thread_id` continues the previous session automatically.

---

## 📁 Lab 05 — Human-In-The-Loop

One of LangGraph's most powerful features.

Execution intentionally pauses using:

```python
interrupt()
```

The graph:

- Saves its current state
- Stops execution
- Waits for human approval

Later it resumes with

```python
Command(
    resume="Approved"
)
```

without restarting the workflow.

This enables production-safe AI systems.

---

## 📁 Lab 06 — Enterprise Email Agent

A complete production-style agent.

Pipeline:

```
Incoming Email
        │
        ▼
 Structured Extraction
        │
        ▼
Intent Classification
        │
        ▼
Parallel Operations
 ├───────────────┐
 │               │
 ▼               ▼
Database      Ticket System
Lookup         Creation
 │               │
 └──────┬────────┘
        ▼
 Draft Response
        │
        ▼
 Urgency Check
        │
   Critical?
      │
 ┌────┴────┐
 │         │
 ▼         ▼
Human     Send
Review    Email
```

Features:

- Structured Output with Pydantic
- Gemini Integration
- Context Retrieval
- Parallel Processing
- Dynamic Routing
- Human Approval
- Session Memory

If:

- urgency == `critical`

or

- intent == `complex`

the graph automatically routes into a Human Review checkpoint before responding.

---

# 🖼️ Output Graph Visualizations

Every lab automatically exports a Mermaid-generated graph visualization.

```
output/
│
├── graph_viz_lab01.png
├── graph_viz_lab02.png
├── graph_viz_lab03a.png
├── graph_viz_lab03b.png
├── graph_viz_lab05.png
└── graph_viz_lab06.png
```

These images provide a visual representation of each workflow's execution graph.

---

# 📂 Project Structure

```
langgraph-essentials-course/
│
├── Lab01_States.py
├── Lab02_Parallel.py
├── Lab03a_Conditional.py
├── Lab03b_Command.py
├── Lab04_Memory.py
├── Lab05_HITL.py
├── Lab06_Email_Agent.py
│
├── output/
│   ├── graph_viz_lab01.png
│   ├── graph_viz_lab02.png
│   ├── graph_viz_lab03a.png
│   ├── graph_viz_lab03b.png
│   ├── graph_viz_lab05.png
│   └── graph_viz_lab06.png
│
├── requirements.txt
├── .env
└── README.md
```

---

# ⚙️ Local Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/langgraph-essentials-course.git

cd langgraph-essentials-course
```

Create a virtual environment

```bash
python -m venv venv
```

Windows

```bash
.\venv\Scripts\activate
```

Mac / Linux

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file

```text
GOOGLE_API_KEY=AIzaSyYourGeminiStudioKeyHere

OPENAI_API_KEY=sk-proj-YourOpenAIKeyHere
```

---

# ▶️ Run Any Lab

Example:

```bash
python Lab01_States.py
```

or

```bash
python Lab02_Parallel.py
```

or

```bash
python Lab03a_Conditional.py
```

or

```bash
python Lab03b_Command.py
```

or

```bash
python Lab04_Memory.py
```

or

```bash
python Lab05_HITL.py
```

or

```bash
python Lab06_Email_Agent.py
```

---

# 🎯 What This Repository Demonstrates

By completing this course, I gained hands-on experience with:

- LangGraph architecture
- StateGraph fundamentals
- TypedDict state design
- Reducers
- Parallel execution
- Fan-Out / Fan-In workflows
- Conditional routing
- Dynamic Command routing
- Conversation memory
- Checkpointers
- Human-In-The-Loop systems
- Interrupt & Resume execution
- Structured Outputs using Pydantic
- Google Gemini integration
- OpenAI integration
- Enterprise agent workflows
- Multi-step orchestration
- Production-ready graph architectures

---

# 📖 Summary

This repository represents a complete implementation of the **LangGraph Essentials Course**, with every lab rewritten into clean, production-style Python scripts.

Beyond reproducing the course material, the project emphasizes maintainable code structure, modern LangGraph patterns, practical LLM integrations, and real-world AI agent design principles. It serves as both a learning portfolio and a reference implementation for building stateful, reliable, and production-ready AI workflows using LangGraph.