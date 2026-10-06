from collections import defaultdict, deque

from backend.app.engine.exceptions import CyclicGraphError
from backend.app.models.flow import EdgeModel, FlowModel, NodeModel


class DAGBuilder:
    def __init__(self, flow: FlowModel):
        self.flow = flow
        self.nodes_by_id: dict[str, NodeModel] = {n.id: n for n in flow.nodes}
        self.adjacency: dict[str, list[str]] = defaultdict(list)
        self.in_degree: dict[str, int] = {n.id: 0 for n in flow.nodes}
        self.incoming_edges: dict[str, list[EdgeModel]] = defaultdict(list)
        self.outgoing_edges: dict[str, list[EdgeModel]] = defaultdict(list)

        self._build_graph()

    def _build_graph(self) -> None:
        for edge in self.flow.edges:
            # Ensure both source and target exist in flow
            if edge.source in self.nodes_by_id and edge.target in self.nodes_by_id:
                self.adjacency[edge.source].append(edge.target)
                self.in_degree[edge.target] += 1
                self.incoming_edges[edge.target].append(edge)
                self.outgoing_edges[edge.source].append(edge)

    def get_topological_order(self) -> list[str]:
        """Calculates topological ordering using Kahn's algorithm.

        Raises CyclicGraphError if any cycle is present.
        """
        in_deg = dict(self.in_degree)
        queue = deque([node_id for node_id, deg in in_deg.items() if deg == 0])
        order: list[str] = []

        while queue:
            curr = queue.popleft()
            order.append(curr)

            for neighbor in self.adjacency[curr]:
                in_deg[neighbor] -= 1
                if in_deg[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.nodes_by_id):
            unprocessed = set(self.nodes_by_id.keys()) - set(order)
            raise CyclicGraphError(
                f"Cycle detected in workflow graph involving nodes: {', '.join(unprocessed)}"
            )

        return order

    def get_incoming_edges(self, node_id: str) -> list[EdgeModel]:
        return self.incoming_edges.get(node_id, [])

    def get_node(self, node_id: str) -> NodeModel | None:
        return self.nodes_by_id.get(node_id)
