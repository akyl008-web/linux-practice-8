#!/usr/bin/env python3
"""ПР-8, вариант B, задание 2. Детектор взаимоблокировок для единичных ресурсов.
По журналу событий строит ГРАФ ОЖИДАНИЯ (поток → поток, который держит нужный ему ресурс)
и после каждого события ищет в нём цикл обходом в глубину (DFS).
Формат журнала: «поток acquire|wait|release ресурс», # — комментарий.
Запуск: python3 detector.py журнал.txt"""
import sys


def wait_for_graph(owner, waiting):
    """Рёбра T → U: поток T ждёт ресурс, которым владеет поток U."""
    graph = {}
    for t, res in waiting.items():
        u = owner.get(res)
        if u is not None and u != t:
            graph.setdefault(t, []).append(u)
    return graph


def find_cycle(graph):
    """DFS с раскраской: серая вершина на пути обхода → найден цикл."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color, path = {}, []

    def dfs(v):
        color[v] = GRAY
        path.append(v)
        for u in graph.get(v, []):
            if color.get(u, WHITE) == GRAY:
                return path[path.index(u):]
            if color.get(u, WHITE) == WHITE:
                cycle = dfs(u)
                if cycle:
                    return cycle
        color[v] = BLACK
        path.pop()
        return None

    for v in list(graph):
        if color.get(v, WHITE) == WHITE:
            cycle = dfs(v)
            if cycle:
                return cycle
    return None


def main():
    if len(sys.argv) != 2:
        print("Использование: python3 detector.py журнал.txt", file=sys.stderr)
        sys.exit(1)
    owner, waiting = {}, {}  # ресурс → владелец; поток → ресурс, который он ждёт
    with open(sys.argv[1]) as f:
        for n, line in enumerate(f, 1):
            parts = line.split("#")[0].split()
            if not parts:
                continue
            t, event, res = parts
            print(f"{n:>3}: {t} {event} {res}")
            if event == "acquire":
                if owner.get(res) not in (None, t):
                    print(f"     ошибка журнала: {res} уже занят потоком {owner[res]}")
                    continue
                owner[res] = t
                waiting.pop(t, None)  # если поток ждал этот ресурс — ожидание закончилось
            elif event == "wait":
                waiting[t] = res
            elif event == "release" and owner.get(res) == t:
                del owner[res]
            cycle = find_cycle(wait_for_graph(owner, waiting))
            if cycle:
                print(f"ВЗАИМОБЛОКИРОВКА после строки {n}! Цикл ожидания:")
                for k, a in enumerate(cycle):
                    b = cycle[(k + 1) % len(cycle)]
                    print(f"  {a} ждёт {waiting[a]}, которым владеет {b}")
                print(f"Участники: потоки {', '.join(cycle)}; ресурсы {', '.join(waiting[a] for a in cycle)}")
                return
    print("Взаимоблокировок не обнаружено")


if __name__ == "__main__":
    main()