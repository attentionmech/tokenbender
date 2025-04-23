# tokenbender

<img width="770" alt="Screenshot of tokenbender UI showing a graph" src="https://github.com/user-attachments/assets/c83b8a30-bbc4-4a67-82b1-3fcf1fa0bc6b" />

An EXPERIMENTAL(read not finished yet) visual interface for running commands as a directed acyclic graph (DAG). The output of one command node can be piped as the input to subsequent nodes. Made it to experiment with small model workflows locally while having a visual aspect to it.

The state of the graph (including command outputs) is captured after each full execution cycle ("epoch"), allowing you to step back and forth through the history using a slider to observe how data flows and changes.

## UI

<img width=600 src="https://github.com/user-attachments/assets/bdf75618-578c-44df-8cb5-300313894ca8" />


## Prerequisites

*   **Python 3.x**
*   **Flask:** (`pip install Flask`)
*   **(Optional) `uv`:** A fast Python package installer and resolver (for the suggested run command).
*   **(For Demo)** `ollama`: If you want to run the default demo graph, you need Ollama installed and running with the specified models (`gemma3:1b`, `qwen2.5:1.5b`, `llama3.2:1b`, `llama3:1b`). See [ollama.com](https://ollama.com/).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd tokenbender
    ```
2.  **Install dependencies:**
    *   Using `uv` (recommended):
        ```bash
        # Nothing extra to install if using 'uv run' directly
        ```
    *   Using `pip`:
        ```bash
        pip install Flask
        ```

## Running the Application

1.  **Start the Flask Server:**
    *   Using `uv`:
        ```bash
        uv run --with flask app.py
        ```
        *(Note: The `--with flask` might be specific to how you've set up `uv` or project files. If `app.py` directly imports Flask, `uv run app.py` might suffice after `uv pip install Flask`)*
        **OR** If you just want to run the script directly after installing Flask:
        ```bash
        # Ensure Flask is installed: pip install Flask
        python app.py
        ```
    *   This will start the server, typically on `http://127.0.0.1:5001`.

2.  **Access the UI:**
    *   Open your web browser and navigate to `http://127.0.0.1:5001`. You should see the initial graph structure.


3.  **Explore Epochs:**
    *   As epochs are processed, the slider at the bottom of the web UI will update.
    *   Move the slider to view the state of the graph (node outputs displayed on edges, node colors) at different points in the execution history.

## Quick usage

To define your own workflow:

1.  Edit the `app.py` file.
2.  Modify the `bootstrap_graph()` function.
    *   Use `graph.add_node(<node_id>, "<your shell command>")` to add command nodes. Node IDs can be strings or numbers.
    *   Use `graph.add_edge(<source_node_id>, <target_node_id>)` to define the data flow dependencies.
3.  Restart the Flask server.

**Example: Simple Echo Workflow**

```python
def bootstrap_graph():
    graph.add_node("A", "echo 'Hello from A'")
    graph.add_node("B", "echo 'Input was:' - ; cat - ; echo 'End of B'") # Reads stdin
    graph.add_node("C", "echo 'Input was:' - ; cat - ; echo 'End of C'") # Reads stdin
    graph.add_node("D", "wc -c") # Reads stdin from B and C

    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("B", "D")
    graph.add_edge("C", "D")
```
