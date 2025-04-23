# tokenbender

<img width="770" alt="Screenshot of tokenbender UI showing a graph" src="https://github.com/user-attachments/assets/c83b8a30-bbc4-4a67-82b1-3fcf1fa0bc6b" />

A web-based visual interface for defining and running sequences of commands as a directed acyclic graph (DAG). The output of one command node can be piped as the input to subsequent nodes. Made it to experiment with small model workflows locally while having a visual aspect to it.

The state of the graph (including command outputs) is captured after each full execution cycle ("epoch"), allowing you to step back and forth through the history using a slider to observe how data flows and changes.

## Prerequisites

*   **Python 3.x**
*   **Flask:** (`pip install Flask`)
*   **(Optional) `uv`:** A fast Python package installer and resolver (for the suggested run command).
*   **(For Demo)** `ollama`: If you want to run the default demo graph, you need Ollama installed and running with the specified models (`gemma3:1b`, `qwen2.5:1.5b`, `llama3.2:1b`, `llama3:1b`). See [ollama.com](https://ollama.com/).
*   **(For Demo)** `tcpdump`: The demo uses `tcpdump`. This usually requires **root privileges** (`sudo`).

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

3.  **Trigger Graph Execution (Epochs):**
    *   The graph execution doesn't run automatically. You need to trigger each "epoch" (a full run through the topologically sorted nodes) via an API call.
    *   Open a separate terminal and run the following command to trigger one epoch:
        ```bash
        curl -X POST http://127.0.0.1:5001/process_epoch
        ```
    *   To automatically trigger epochs repeatedly (e.g., every 5 seconds), you can use `watch`:
        ```bash
        watch -n 5 curl -X POST http://127.0.0.1:5001/process_epoch
        ```
    *   **Important:** If using the default `tcpdump` command, you might need to run the `python app.py` or `uv run ...` command with `sudo` for `tcpdump` to have the necessary permissions.
        ```bash
        sudo python app.py
        # or potentially: sudo uv run ... app.py
        ```

4.  **Explore Epochs:**
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

## API Endpoints

*   `GET /`: Serves the main HTML page.
*   `GET /graph_structure`: Returns the static structure of the graph (nodes and edges).
*   `GET /graph_epochs`: Returns the history of all processed epochs, including node/edge properties and outputs for each epoch.
*   `POST /process_epoch`: Triggers the execution of the next epoch in the graph.
*   `POST /add_node`: (API only) Adds a new node. Requires JSON payload: `{"id": "new_node_id", "command": "echo 'new'"}`.
*   `POST /add_edge`: (API only) Adds a new edge. Requires JSON payload: `{"source": "source_id", "target": "target_id"}`.
