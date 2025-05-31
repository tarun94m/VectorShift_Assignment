from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    id: str

class Edge(BaseModel):
    source: str
    target: str

class Pipeline(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

@app.post("/pipelines/parse")
async def parse_pipeline(pipeline: Pipeline):
    node_ids = {node.id for node in pipeline.nodes}
    graph = {nid: [] for nid in node_ids}

    # Build adjacency list
    for edge in pipeline.edges:
        if edge.source in node_ids and edge.target in node_ids:
            graph[edge.source].append(edge.target)

    # Check for cycles using DFS
    visited = set()
    stack = set()

    def dfs(node):
        if node in stack:
            return False  # cycle found
        if node in visited:
            return True
        stack.add(node)
        for neighbor in graph.get(node, []):
            if not dfs(neighbor):
                return False
        stack.remove(node)
        visited.add(node)
        return True

    is_dag = all(dfs(n) for n in node_ids if n not in visited)

    return {
        "num_nodes": len(pipeline.nodes),
        "num_edges": len(pipeline.edges),
        "is_dag": is_dag
    }

# Run with: uvicorn main:app --reload
