import os
import random
import subprocess
import threading
import time
from collections import defaultdict, deque

from flask import Flask, jsonify, request, send_file

app = Flask(__name__)


class CommandGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.epoch_log = []
        self.current_epoch = -1

    def add_node(self, node_id, command=None):
        if node_id in self.nodes:
            raise ValueError(f"Node ID {node_id} already exists.")
        self.nodes[node_id] = {"command": command, "output": None}

    def add_edge(self, source_id, target_id):
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Both source and target nodes must exist.")
        self.edges.append((source_id, target_id))

    def _topological_sort(self):
        in_degree = defaultdict(int)
        graph = defaultdict(list)
        for src, tgt in self.edges:
            graph[src].append(tgt)
            in_degree[tgt] += 1
            if src not in in_degree:
                in_degree[src] = in_degree[src]

        queue = deque([node for node in self.nodes if in_degree[node] == 0])
        sorted_nodes = []

        while queue:
            node = queue.popleft()
            sorted_nodes.append(node)
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_nodes) != len(self.nodes):
            raise Exception("Cycle detected in graph")
        return sorted_nodes

    def run_node(self, node_id, input_text=None, timeout=10):
        print(f"Running Node {node_id}")
        command = self.nodes[node_id]["command"]
        print(f"Command: {command}")

        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            def stream_output(process, node_id):
                output = ""
                for line in process.stdout:
                    output += line
                    print(f"Node {node_id} Output: {line.strip()}")
                    self.nodes[node_id]["output"] = output
                for line in process.stderr:
                    print(f"Node {node_id} Error: {line.strip()}")
                self.nodes[node_id]["output"] = output

            thread = threading.Thread(target=stream_output, args=(process, node_id))
            thread.start()

            if input_text:
                process.stdin.write(input_text)
                process.stdin.close()

            process.wait(timeout=timeout)
            thread.join()

            if process.poll() is None:
                print(f"Timeout reached for Node {node_id}, killing the process.")
                process.kill()

        except subprocess.TimeoutExpired:
            self.nodes[node_id]["output"] = "Timeout expired"
        except Exception as e:
            self.nodes[node_id]["output"] = str(e)

        print(f"Node {node_id} END")

    def process_epoch(self):
        self.current_epoch += 1
        sorted_nodes = self._topological_sort()

        for node_id in sorted_nodes:
            input_text = ""
            for src, tgt in self.edges:
                if tgt == node_id:
                    input_text += self.nodes[src]["output"] or ""
            self.run_node(node_id, input_text=input_text)

        epoch_data = {
            "epoch": self.current_epoch,
            "node_props": {
                node_id: {
                    "output": self.nodes[node_id]["output"],
                    "color": self._generate_color(node_id),
                    "label": f"Node {node_id}",
                }
                for node_id in self.nodes
            },
            "edge_props": {
                f"{src}_{tgt}": {
                    "edge_data": f"Edge {src} → {tgt}",
                    "color": self._generate_edge_color(src, tgt),
                    "label": f"Edge from {src} to {tgt}",
                }
                for src, tgt in self.edges
            },
        }

        self.epoch_log.append(epoch_data)

    def _generate_color(self, node_id):
        random.seed(node_id)
        return f"rgb({random.randint(100, 255)}, {random.randint(100, 255)}, {random.randint(100, 255)})"

    def _generate_edge_color(self, src, tgt):
        random.seed(f"{src}_{tgt}")
        return f"rgb({random.randint(100, 255)}, {random.randint(100, 255)}, {random.randint(100, 255)})"

    def get_graph_structure(self):
        return {
            "nodes": [
                {"id": node_id, "command": self.nodes[node_id]["command"]}
                for node_id in self.nodes
            ],
            "edges": [{"source": src, "target": tgt} for src, tgt in self.edges],
        }

    def get_graph_epochs(self):
        return self.epoch_log


# Initialize the graph
graph = CommandGraph()


def bootstrap_graph():
    graph.add_node(1, "tcpdump -c 1 -nn -i any")
    graph.add_node(2, "ollama run gemma3:1b")
    graph.add_node(3, "ollama run qwen2.5:1.5b")
    graph.add_node(4, "ollama run llama3.2:1b")
    graph.add_node(5, "ollama run llama3:1b")

    graph.add_edge(1, 2)
    graph.add_edge(1, 3)
    graph.add_edge(1, 4)
    graph.add_edge(2, 5)
    graph.add_edge(3, 5)
    graph.add_edge(4, 5)


bootstrap_graph()


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/graph_structure")
def get_structure():
    return jsonify(graph.get_graph_structure())


@app.route("/graph_epochs")
def get_epochs():
    return jsonify(graph.get_graph_epochs())


@app.route("/process_epoch", methods=["POST"])
def process_epoch():
    graph.process_epoch()
    return jsonify({"status": "epoch processed", "epoch": graph.current_epoch}), 200


@app.route("/add_node", methods=["POST"])
def add_node():
    data = request.json
    try:
        graph.add_node(data["id"], data["command"])
        return jsonify({"status": "success"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/add_edge", methods=["POST"])
def add_edge():
    data = request.json
    try:
        graph.add_edge(data["source"], data["target"])
        return jsonify({"status": "success"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5001)
