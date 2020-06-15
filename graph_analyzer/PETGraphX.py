# This file is part of the DiscoPoP software (http://www.discopop.tu-darmstadt.de)
#
# Copyright (c) 2020, Technische Universitaet Darmstadt, Germany
#
# This software may be modified and distributed under the terms of
# the 3-Clause BSD License.  See the LICENSE file in the package base
# directory for details.

from typing import Dict, List

import matplotlib.pyplot as plt
import networkx as nx
from lxml.objectify import ObjectifiedElement
from networkx import Graph
from enum import IntEnum, Enum

node_props = [
    ('BasicBlockID', 'string', '\'\''),
    ('pipeline', 'float', '0'),
    ('doAll', 'bool', 'False'),
    ('geomDecomp', 'bool', 'False'),
    ('reduction', 'bool', 'False'),
    ('mwType', 'string', '\'FORK\''),
    ('localVars', 'object', '[]'),
    ('globalVars', 'object', '[]'),
    ('args', 'object', '[]'),
    ('recursiveFunctionCalls', 'object', '[]'),
]

edge_props = [
    ('type', 'string'),
    ('source', 'string'),
    ('sink', 'string'),
    ('var', 'string'),
    ('dtype', 'string'),
]


def parse_id(node_id: str) -> (int, int):
    split = node_id.split(':')
    return int(split[0]), int(split[1])


class DepType(Enum):
    CHILD = 0
    SUCCESSOR = 1
    DATA = 2


class CuType(IntEnum):
    CU = 0
    FUNC = 1
    LOOP = 2
    DUMMY = 3


class Dependency:
    type: DepType

    def __init__(self, type: DepType):
        self.type = type


class CuNode:
    id: str
    file_id: int
    node_id: int
    source_file: int
    start_line: int
    end_line: int
    type: CuType
    name: str
    instructions_count: int

    def __init__(self, id: str):
        self.id = id
        self.file_id, self.node_id = parse_id(id)

    def __str__(self):
        return self.id

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.id
        elif isinstance(other, CuNode):
            return other.id == self.id
        else:
            return False

    def __hash__(self):
        return hash(id)


def parse_cu(node: ObjectifiedElement) -> CuNode:
    n = CuNode(node.get("id"))
    n.type = CuType(int(node.get("type")))
    n.source_file, n.start_line = parse_id(node.get("startsAtLine"))
    _, n.end_line = parse_id(node.get("endsAtLine"))
    n.name = node.get("name")
    n.instructions_count = node.get("instructionsCount", 0)
    # TODO func args
    # TODO recursive calls
    # TODO variables
    return n


class PETGraphX(object):
    reduction_vars: List[Dict[str, str]]
    loop_data: Dict[str, int]

    def __init__(self, cu_dict, dependencies_list, loop_data, reduction_vars):
        self.graph = Graph().to_directed()
        self.loop_data = loop_data
        self.reduction_vars = reduction_vars

        for id, node in cu_dict.items():
            self.graph.add_node(id, data=parse_cu(node))

        for node_id, node in cu_dict.items():
            source = node_id
            if 'childrenNodes' in dir(node):
                for child in [n.text for n in node.childrenNodes]:
                    if not self.graph.has_node(child):
                        print(f"WARNING: no child node {child} found")
                    self.graph.add_edge(source, child, data=Dependency(DepType.CHILD))
            if 'successors' in dir(node) and 'CU' in dir(node.successors):
                for successor in [n.text for n in node.successors.CU]:
                    if not self.graph.has_node(successor):
                        print(f"WARNING: no successor node {successor} found")
                    self.graph.add_edge(source, successor, data=Dependency(DepType.SUCCESSOR))

    def show(self):
        print("showing")
        plt.subplot(111)
        # pos = nx.shell_layout(self.graph)
        # pos = nx.fruchterman_reingold_layout(self.graph)
        pos = nx.kamada_kawai_layout(self.graph)

        #nx.draw(self.graph, with_labels=True, font_weight='bold', pos=pos)
        # labels = [str(self.graph.nodes[n]['data']) for n in self.graph.nodes]
        # nx.draw_networkx_labels(self.graph, pos=pos, labels=labels)
        # draw nodes
        nx.draw_networkx_nodes(self.graph, pos=pos, node_color='#2B85FD', node_shape='o',
                               nodelist=[n for n in self.graph.nodes if self.node_at(n).type == CuType.CU])
        nx.draw_networkx_nodes(self.graph, pos=pos, node_color='#ff5151', node_shape='d',
                               nodelist=[n for n in self.graph.nodes if self.node_at(n).type == CuType.LOOP])
        nx.draw_networkx_nodes(self.graph, pos=pos, node_color='grey', node_shape='s',
                               nodelist=[n for n in self.graph.nodes if self.node_at(n).type == CuType.DUMMY])
        nx.draw_networkx_nodes(self.graph, pos=pos, node_color='#cf65ff', node_shape='s',
                               nodelist=[n for n in self.graph.nodes if self.node_at(n).type == CuType.FUNC])
        nx.draw_networkx_nodes(self.graph, pos=pos, node_color='yellow', node_shape='h', node_size=750,
                               nodelist=[n for n in self.graph.nodes if self.node_at(n).name == 'main'])
        # id as label
        labels = {}
        for n in self.graph.nodes:
            labels[n] = str(self.graph.nodes[n]['data'])
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=10)

        nx.draw_networkx_edges(self.graph, pos,
                               edgelist=[e for e in self.graph.edges() if self.edge_at(e).type == DepType.CHILD])
        nx.draw_networkx_edges(self.graph, pos, edge_color='green',
                               edgelist=[e for e in self.graph.edges() if self.edge_at(e).type == DepType.SUCCESSOR])
        plt.show()

    def node_at(self, id: str) -> CuNode:
        return self.graph.nodes[id]['data']

    def edge_at(self, source: str, target: str) -> Dependency:
        return self.graph[source][target]['data']

    def edge_at(self, source: tuple) -> Dependency:
        return self.graph[source[0]][source[1]]['data']

