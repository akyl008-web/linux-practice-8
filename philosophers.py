#!/usr/bin/env python3
"""ПР-8, вариант B, задание 4. Обедающие философы: наивное решение (deadlock) и два исправления:
нумерация вилок (сначала вилка с меньшим номером) и ограничение числа философов за столом
(официант-семафор на N−1 мест). Статистика: сколько раз поел каждый.
Запуск: python3 philosophers.py [секунд на вариант, по умолчанию 5]"""
import random
import sys
import threading
import time

N = 5


def run(mode, duration):
    forks = [threading.Lock() for _ in range(N)]
    waiter = threading.Semaphore(N - 1)  # за столом одновременно не больше N−1 философов
    meals = [0] * N
    stop = threading.Event()

    def philosopher(i):
        left, right = i, (i + 1) % N
        first, second = (min(left, right), max(left, right)) if mode == "numbered" else (left, right)
        while not stop.is_set():
            time.sleep(random.uniform(0, 0.005))  # думает
            if mode == "waiter":
                waiter.acquire()
            with forks[first]:
                time.sleep(0.005)  # пауза между вилками — делает deadlock вероятным
                with forks[second]:
                    meals[i] += 1  # ест
                    time.sleep(0.002)
            if mode == "waiter":
                waiter.release()

    for i in range(N):
        threading.Thread(target=philosopher, args=(i,), daemon=True).start()

    # сторож: если 2 с никто не поел — взаимоблокировка
    start, last, still, deadlock = time.monotonic(), -1, 0.0, False
    while time.monotonic() - start < duration:
        time.sleep(0.5)
        total = sum(meals)
        still = still + 0.5 if total == last else 0.0
        last = total
        if still >= 2:
            deadlock = True
            break
    stop.set()
    return meals[:], deadlock, time.monotonic() - start


def main():
    duration = float(sys.argv[1]) if len(sys.argv) > 1 else 5
    titles = {"naive": "Наивное (левая, потом правая)",
              "numbered": "Нумерация вилок",
              "waiter": f"Официант ({N - 1} места за столом)"}
    for mode, title in titles.items():
        meals, deadlock, elapsed = run(mode, duration)
        status = (f"DEADLOCK — 2 с никто не ест (обнаружено через {elapsed:.1f} с)" if deadlock
                  else f"работало {elapsed:.1f} с без зависаний")
        print(f"{title}: {status}")
        print("  поел: " + "  ".join(f"Ф{i}={m}" for i, m in enumerate(meals))
              + f"   всего {sum(meals)}, min {min(meals)}, max {max(meals)}", flush=True)


if __name__ == "__main__":
    main()