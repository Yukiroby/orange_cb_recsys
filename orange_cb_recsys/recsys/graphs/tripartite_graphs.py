from typing import List, Tuple, Dict

from orange_cb_recsys.recsys.graphs import TripartiteGraph
import pandas as pd
import networkx as nx


class NXTripartiteGraph(TripartiteGraph):
    def __init__(self, source_frame: pd.DataFrame):
        super().__init__(source_frame)

    def create_graph(self):
        self.__graph = nx.DiGraph()

    def add_node(self, node: object):
        self.__graph.add_node(node)

    def add_edge(self, from_node: object, to_node: object, weight: float, label: str = 'weight',
                 attr: Dict[str, object] = None):
        self.__graph.add_edge(from_node, to_node, weight=weight, label=label, **attr)

    def get_edge_data(self, from_node: object, to_node: object):
        try:
            return self.__graph.get_edge_data(from_node, to_node)
        except ValueError:
            return None

    def get_adj(self, node: object) -> List[Tuple[object, object, float]]:
        return self.__graph.neighbors(node)

    def get_predecessors(self, node: object) -> List[Tuple[object, object, float]]:
        return self.__graph.predecessors(node)

    def get_successors(self, node: object) -> List[Tuple[object, object, float]]:
        return self.__graph.successors(node)
