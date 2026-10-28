#!/usr/bin/env python3
"""ПР-8, вариант B, задание 3. Классическая взаимоблокировка: два потока захватывают
lock_a и lock_b в разном порядке.
  python3 deadlock.py plain    — обычный threading.Lock: программа ЗАВИСАЕТ; через 3 с faulthandler
                                 печатает, где ждёт каждый поток, и завершает процесс
  python3 deadlock.py tracked  — TrackedLock: вместо зависания — исключение DeadlockError
  python3 deadlock.py ordered  — исправление: оба потока захватывают блокировки в одном порядке"""
import faulthandler
import sys
import threading
import time

from tracked_lock import DeadlockError, TrackedLock


def log(msg):
    print(msg, flush=True)


def worker(name, first, second, first_name, second_name):
    try:
        with first:
            log(f"{name}: захватил {first_name}, жду {second_name}")
            time.sleep(0.1)  # даём второму потоку захватить свою блокировку
            with second:
                log(f"{name}: захватил обе блокировки — работа выполнена")
    except DeadlockError as e:
        log(f"{name}: DeadlockError — {e}. Отпускаю {first_name}")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "plain"
    if mode == "tracked":
        a, b = TrackedLock("lock_a"), TrackedLock("lock_b")
    else:
        a, b = threading.Lock(), threading.Lock()
    if mode == "plain":
        faulthandler.dump_traceback_later(3, exit=True)  # «как убедиться, что зависла»
    log(f"Режим: {mode}")
    t1 = threading.Thread(target=worker, name="T1", args=("T1", a, b, "lock_a", "lock_b"))
    if mode == "ordered":  # тот же порядок: сначала lock_a, потом lock_b
        t2 = threading.Thread(target=worker, name="T2", args=("T2", a, b, "lock_a", "lock_b"))
    else:                  # обратный порядок → циклическое ожидание
        t2 = threading.Thread(target=worker, name="T2", args=("T2", b, a, "lock_b", "lock_a"))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    log("Программа завершилась нормально")


if __name__ == "__main__":
    main()