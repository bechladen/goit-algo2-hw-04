from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import DefaultDict, Dict, Iterable, List, Tuple


Node = int


@dataclass(frozen=True)
class AugmentStep:
    path: List[Node]
    bottleneck: int


class FlowNetwork:
    def __init__(self, n: int):
        self.n = n
        self.adj: List[List[Node]] = [[] for _ in range(n)]
        self.cap: List[DefaultDict[Node, int]] = [defaultdict(int) for _ in range(n)]
        self.flow: List[DefaultDict[Node, int]] = [defaultdict(int) for _ in range(n)]

    def add_edge(self, u: Node, v: Node, capacity: int) -> None:
        if capacity < 0:
            raise ValueError("Пропускна здатність має бути невід’ємною")
        if v not in self.adj[u]:
            self.adj[u].append(v)
        if u not in self.adj[v]:
            self.adj[v].append(u)  # зворотне ребро для залишкової мережі
        self.cap[u][v] += capacity

    def residual(self, u: Node, v: Node) -> int:
        forward_cap = self.cap[u].get(v, 0)
        if forward_cap > 0:
            return forward_cap - self.flow[u].get(v, 0)
        # Для зворотного ребра залишкова ємність дорівнює поточному потоку на (v -> u).
        return self.flow[v].get(u, 0)

    def edmonds_karp(self, s: Node, t: Node, *, verbose: bool = False) -> Tuple[int, List[AugmentStep]]:
        max_flow = 0
        steps: List[AugmentStep] = []

        while True:
            parent = [-1] * self.n
            parent[s] = s
            q = deque([s])

            while q and parent[t] == -1:
                u = q.popleft()
                for v in self.adj[u]:
                    if parent[v] != -1:
                        continue
                    if self.residual(u, v) <= 0:
                        continue
                    parent[v] = u
                    q.append(v)

            if parent[t] == -1:
                break

            # Відновлюємо знайдений шлях та його «вузьке місце».
            path: List[Node] = []
            bottleneck = 10**18
            v = t
            while v != s:
                u = parent[v]
                bottleneck = min(bottleneck, self.residual(u, v))
                path.append(v)
                v = u
            path.append(s)
            path.reverse()

            b = int(bottleneck)
            v = t
            while v != s:
                u = parent[v]
                if self.cap[u].get(v, 0) > 0:
                    self.flow[u][v] += b
                else:
                    self.flow[v][u] -= b
                v = u

            max_flow += b
            step = AugmentStep(path=path, bottleneck=b)
            steps.append(step)
            if verbose:
                print(f"Збільшення на {b} уздовж шляху {path}")

        return max_flow, steps


def build_logistics_network() -> Tuple[FlowNetwork, Dict[str, Node], Dict[Node, str], Node, Node]:
    """
    Фізичні вершини: 20 (2 термінали + 4 склади + 14 магазинів)
    Технічні вершини: надджерело + надстік (для класичної постановки max-flow)
    """

    labels: List[str] = []

    def add_label(name: str) -> Node:
        labels.append(name)
        return len(labels) - 1

    super_source = add_label("Джерело")
    super_sink = add_label("Сток")

    _terminals = [add_label("Термінал 1"), add_label("Термінал 2")]
    _warehouses = [add_label("Склад 1"), add_label("Склад 2"), add_label("Склад 3"), add_label("Склад 4")]
    stores = [add_label(f"Магазин {i}") for i in range(1, 15)]

    name_to_node = {name: i for i, name in enumerate(labels)}
    node_to_name = {i: name for i, name in enumerate(labels)}

    g = FlowNetwork(n=len(labels))

    # Ребра з надджерела (дорівнюють сумі вихідних ємностей кожного термінала).
    g.add_edge(super_source, name_to_node["Термінал 1"], 60)
    g.add_edge(super_source, name_to_node["Термінал 2"], 55)

    # Термінал -> Склад (порядок додавання впливає на детермінований прогін Едмондса–Карпа).
    g.add_edge(name_to_node["Термінал 1"], name_to_node["Склад 1"], 25)
    g.add_edge(name_to_node["Термінал 1"], name_to_node["Склад 2"], 20)
    g.add_edge(name_to_node["Термінал 1"], name_to_node["Склад 3"], 15)

    g.add_edge(name_to_node["Термінал 2"], name_to_node["Склад 3"], 15)
    g.add_edge(name_to_node["Термінал 2"], name_to_node["Склад 4"], 30)
    g.add_edge(name_to_node["Термінал 2"], name_to_node["Склад 2"], 10)

    # Склад -> Магазин
    g.add_edge(name_to_node["Склад 1"], name_to_node["Магазин 1"], 15)
    g.add_edge(name_to_node["Склад 1"], name_to_node["Магазин 2"], 10)
    g.add_edge(name_to_node["Склад 1"], name_to_node["Магазин 3"], 20)

    g.add_edge(name_to_node["Склад 2"], name_to_node["Магазин 4"], 15)
    g.add_edge(name_to_node["Склад 2"], name_to_node["Магазин 5"], 10)
    g.add_edge(name_to_node["Склад 2"], name_to_node["Магазин 6"], 25)

    g.add_edge(name_to_node["Склад 3"], name_to_node["Магазин 7"], 20)
    g.add_edge(name_to_node["Склад 3"], name_to_node["Магазин 8"], 15)
    g.add_edge(name_to_node["Склад 3"], name_to_node["Магазин 9"], 10)

    g.add_edge(name_to_node["Склад 4"], name_to_node["Магазин 10"], 20)
    g.add_edge(name_to_node["Склад 4"], name_to_node["Магазин 11"], 10)
    g.add_edge(name_to_node["Склад 4"], name_to_node["Магазин 12"], 15)
    g.add_edge(name_to_node["Склад 4"], name_to_node["Магазин 13"], 5)
    g.add_edge(name_to_node["Склад 4"], name_to_node["Магазин 14"], 10)

    # Магазин -> надстік (дуже великі ємності, щоб не обмежувати прийом штучно).
    for st in stores:
        g.add_edge(st, super_sink, 10**9)

    return g, name_to_node, node_to_name, super_source, super_sink


def decompose_terminal_to_store_flows(
    g: FlowNetwork, name_to_node: Dict[str, Node], *, terminal_order: Iterable[str], store_order: Iterable[str]
) -> Dict[Tuple[str, str], int]:
    """
    Атрибутуємо доставку в магазини до терміналів через декомпозицію на кожному складі:
    - Запас: потік (Термінал -> Склад)
    - Попит: потік (Склад -> Магазин)
    Жадібно (детерміновано): термінали в terminal_order; магазини в store_order.
    """

    terminals = list(terminal_order)
    stores = list(store_order)
    warehouses = ["Склад 1", "Склад 2", "Склад 3", "Склад 4"]

    result: Dict[Tuple[str, str], int] = {(t, s): 0 for t in terminals for s in stores}

    for w_name in warehouses:
        w = name_to_node[w_name]
        supply = {t: g.flow[name_to_node[t]].get(w, 0) for t in terminals}
        demand = {s: g.flow[w].get(name_to_node[s], 0) for s in stores}

        for t in terminals:
            rem = supply[t]
            if rem <= 0:
                continue
            for s in stores:
                need = demand[s]
                if need <= 0:
                    continue
                x = min(rem, need)
                if x <= 0:
                    continue
                result[(t, s)] += x
                rem -= x
                demand[s] -= x
                if rem == 0:
                    break

    return result


def print_summary(
    g: FlowNetwork,
    name_to_node: Dict[str, Node],
    node_to_name: Dict[Node, str],
    steps: List[AugmentStep],
    max_flow: int,
) -> None:
    print("Максимальний потік:", max_flow)
    print()
    print("Кроки Едмондса–Карпа (шляхи та вузьке місце):")
    total = 0
    for i, st in enumerate(steps, 1):
        total += st.bottleneck
        path_str = " -> ".join(node_to_name[n] for n in st.path)
        print(f"{i:02d}. +{st.bottleneck:>3} | {path_str} | разом={total}")

    print()
    terminals = ["Термінал 1", "Термінал 2"]
    stores = [f"Магазин {i}" for i in range(1, 15)]
    table = decompose_terminal_to_store_flows(g, name_to_node, terminal_order=terminals, store_order=stores)

    print("Таблиця: Термінал -> Магазин -> Фактичний Потік")
    for term in terminals:
        for store in stores:
            print(f"{term}\t{store}\t{table[(term, store)]}")

    print()
    totals_by_terminal = {term: sum(table[(term, store)] for store in stores) for term in terminals}
    totals_by_store = {store: sum(table[(term, store)] for term in terminals) for store in stores}

    print("Підсумок по терміналах:")
    for term in terminals:
        print(f"- {term}: {totals_by_terminal[term]}")

    print("Підсумок по магазинах:")
    for store in stores:
        print(f"- {store}: {totals_by_store[store]}")


def main() -> None:
    g, name_to_node, node_to_name, s, t = build_logistics_network()
    max_flow, steps = g.edmonds_karp(s, t, verbose=False)
    print_summary(g, name_to_node, node_to_name, steps, max_flow)


if __name__ == "__main__":
    main()

