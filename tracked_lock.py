#!/usr/bin/env python3
"""ПР-8, вариант B, задание 3. TrackedLock — обёртка над threading.Lock, которая ведёт граф ожидания
в реальном времени и при появлении цикла бросает DeadlockError вместо зависания."""
import threading


class DeadlockError(RuntimeError):
    pass


_graph_lock = threading.Lock()  # защищает сам граф ожидания
_waiting = {}                   # поток → TrackedLock, которую он ждёт


class TrackedLock:
    def __init__(self, name):
        self.name = name
        self._lock = threading.Lock()
        self.owner = None  # поток-владелец

    def acquire(self):
        me = threading.current_thread()
        with _graph_lock:
            if self._lock.acquire(blocking=False):
                self.owner = me
                return True
            _waiting[me] = self  # новое ребро графа ожидания: me → владелец этой блокировки
            cycle = _find_cycle(me)
            if cycle:
                del _waiting[me]
                raise DeadlockError("цикл ожидания: " + "; ".join(cycle))
        self._lock.acquire()  # блокирующее ожидание — вне _graph_lock
        with _graph_lock:
            del _waiting[me]
            self.owner = me
        return True

    def release(self):
        with _graph_lock:
            self.owner = None
            self._lock.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *exc):
        self.release()


def _find_cycle(start):
    """Идёт по рёбрам «поток → владелец ожидаемой блокировки». Поток ждёт не больше одной
    блокировки, поэтому из вершины выходит не больше одного ребра, и обход в глубину
    сводится к проходу по цепочке. Возвращает описание цикла через start или None."""
    path, seen, t = [], {start}, start
    while t in _waiting:
        lock = _waiting[t]
        owner = lock.owner
        if owner is None:
            return None
        path.append(f"{t.name} ждёт {lock.name}, её держит {owner.name}")
        if owner is start:
            return path
        if owner in seen:
            return None
        seen.add(owner)
        t = owner
    return None