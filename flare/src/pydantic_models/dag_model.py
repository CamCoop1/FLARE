from collections import Counter, defaultdict
from graphlib import TopologicalSorter
from typing import Dict, Mapping, Set

from pydantic import RootModel, model_validator


class Dag(RootModel[Dict[str, Set[str]]], Mapping[str, str]):
    # Defining the dundermethods requires for dictionary-like
    # Operations like .items() provided by Mapping
    def __getitem__(self, key: str) -> str:
        """
        By Axiom 3 of FLARE each Task should by definition have at most
        one required Task to be ran before it. Hence we are safe in our action
        to return the single element of the set
        """
        return list(self.root[key])[0]

    def __len__(self) -> int:
        return len(self.root)

    def __iter__(self):
        return iter(self.root)

    # End of definitions
    @model_validator(mode="after")
    @classmethod
    def prepare_dag(cls, model):
        """ "Here we prepare the dag graph and assign the ts to our cls object
        This checks no circular DAG exists"""
        ts = TopologicalSorter(model.dag)
        cls.flattened_dag_ordering = list(ts.static_order())
        cls.ts = ts

    @property
    def dag(self):
        return self.root

    def get_roots_of_dag(self):
        dag_graph = self.dag
        incoming = Counter(node for targets in dag_graph.values() for node in targets)
        return set(dag_graph) - incoming.keys()

    def print_dag(self):
        """
        Pretty-print a DAG defined as:
            node -> set(iterable) of dependencies
        """
        ts = TopologicalSorter(self.dag)
        ts.prepare()
        # Build execution levels
        levels = []
        while ts.is_active():
            ready = sorted(ts.get_ready())
            levels.append(ready)
            ts.done(*ready)

        # Reverse dependency lookup
        children = defaultdict(list)
        for node, deps in self.dag.items():
            for dep in deps:
                children[dep].append(node)

        # Print
        for i, level in enumerate(levels):
            print(f"Level {i}")
            for idx, node in enumerate(level):
                connector = "└──" if idx == len(level) - 1 else "├──"
                print(f"{connector} {node}")

                next_nodes = sorted(children.get(node, []))
                for j, child in enumerate(next_nodes):
                    branch = "│   " if idx != len(level) - 1 else "    "
                    sub = "└──" if j == len(next_nodes) - 1 else "├──"
                    print(f"{branch}{sub} {child}")

            print()
