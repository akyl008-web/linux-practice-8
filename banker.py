#!/usr/bin/env python3
"""ПР-8, вариант B, задание 1. Алгоритм банкира: проверка безопасности и обработка запросов
request(pid, vector) с откатом, если состояние после выделения небезопасно.
Запуск:
  python3 banker.py bank1.txt < requests.txt           # запросы из stdin: «процесс a b c»
  python3 banker.py bank1.txt --check P1,P3,P4,P2,P0   # проверить заданную последовательность
Формат файла: «available a b c», затем строки «Pk  allocation...  max...»; # — комментарий."""
import sys


def read_state(path):
    available, names, alloc, maxm = None, [], [], []
    with open(path) as f:
        for line in f:
            parts = line.split("#")[0].split()
            if not parts:
                continue
            if parts[0] == "available":
                available = [int(x) for x in parts[1:]]
                continue
            m = len(available)
            values = [int(x) for x in parts[1:]]
            if len(values) != 2 * m:
                raise ValueError(f"строка {line.strip()!r}: нужно {2 * m} чисел")
            names.append(parts[0])
            alloc.append(values[:m])
            maxm.append(values[m:])
    return available, names, alloc, maxm


def leq(a, b):
    return all(x <= y for x, y in zip(a, b))


def add(a, b):
    return [x + y for x, y in zip(a, b)]


def sub(a, b):
    return [x - y for x, y in zip(a, b)]


def vec(v):
    return "(" + ", ".join(map(str, v)) + ")"


def safety(available, alloc, need):
    """Проверка безопасности. Возвращает безопасную последовательность (индексы) или None."""
    work = available[:]
    finish = [False] * len(alloc)
    seq = []
    progress = True
    while progress:
        progress = False
        for i in range(len(alloc)):
            if not finish[i] and leq(need[i], work):
                work = add(work, alloc[i])  # процесс завершился и вернул всё, что держал
                finish[i] = True
                seq.append(i)
                progress = True
    return seq if all(finish) else None


def check_sequence(available, alloc, need, seq):
    """Проверяет, что заданная последовательность процессов безопасна."""
    work = available[:]
    for i in seq:
        if not leq(need[i], work):
            return False, i
        work = add(work, alloc[i])
    return True, None


def request(available, alloc, need, i, req):
    if not leq(req, need[i]):
        return "ОШИБКА: запрос превышает оставшуюся потребность Need"
    if not leq(req, available):
        return "ЖДАТЬ: свободных ресурсов недостаточно"
    # пробное выделение
    available[:] = sub(available, req)
    alloc[i] = add(alloc[i], req)
    need[i] = sub(need[i], req)
    seq = safety(available, alloc, need)
    if seq is None:
        # откат
        available[:] = add(available, req)
        alloc[i] = sub(alloc[i], req)
        need[i] = add(need[i], req)
        return "ОТКАЗ: после выделения состояние небезопасно — выполнен откат"
    return f"ВЫДЕЛЕНО: состояние безопасно, последовательность {seq}"


def main():
    if len(sys.argv) < 2:
        print("Использование: python3 banker.py файл [--check P1,P3,...] [< запросы]", file=sys.stderr)
        sys.exit(1)
    available, names, alloc, maxm = read_state(sys.argv[1])
    need = [sub(mx, al) for mx, al in zip(maxm, alloc)]  # Need = Max − Allocation
    index = {name: i for i, name in enumerate(names)}

    def names_of(seq):
        return ", ".join(names[i] for i in seq)

    print(f"Файл: {sys.argv[1]}")
    print(f"{'':<4}{'Allocation':<14}{'Max':<14}{'Need':<14}")
    for i, name in enumerate(names):
        print(f"{name:<4}{vec(alloc[i]):<14}{vec(maxm[i]):<14}{vec(need[i]):<14}")
    print(f"Available = {vec(available)}")
    seq = safety(available, alloc, need)
    print(f"Проверка безопасности: SAFE, последовательность {names_of(seq)}" if seq is not None
          else "Проверка безопасности: UNSAFE — безопасной последовательности нет")

    if "--check" in sys.argv:
        order = sys.argv[sys.argv.index("--check") + 1].split(",")
        ok, bad = check_sequence(available, alloc, need, [index[p] for p in order])
        print(f"Проверка последовательности {', '.join(order)}: "
              + ("безопасна" if ok else f"НЕ безопасна (не хватает ресурсов для {names[bad]})"))

    if sys.stdin.isatty():
        print("Введите запросы «процесс a b c» (Ctrl+D — конец):")
    for line in sys.stdin:
        parts = line.split("#")[0].split()
        if not parts:
            continue
        pid, req = parts[0], [int(x) for x in parts[1:]]
        result = request(available, alloc, need, index[pid], req)
        print(f"Запрос {pid} {vec(req)}: {result.replace(str(safety(available, alloc, need)), names_of(safety(available, alloc, need) or []))}")
        print(f"  Available = {vec(available)}")


if __name__ == "__main__":
    main()