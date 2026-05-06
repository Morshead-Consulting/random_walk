import sys
from src.simulations import (
    simulation_1,
    simulation_2,
    simulation_3,
    simulation_4,
    simulation_5,
    simulation_6,
)

SIMULATIONS = [
    (1, "Simulation 1",          simulation_1),
    (2, "Simulation 2",          simulation_2),
    (3, "Coin Toss Random Walk", simulation_3),
    (4, "Simulation 4",          simulation_4),
    (5, "Simulation 5",          simulation_5),
    (6, "Simulation 6",          simulation_6),
]


def run_menu():
    while True:
        print("\n" + "=" * 40)
        print("      Random Walk Simulations")
        print("=" * 40)
        for num, name, _ in SIMULATIONS:
            print(f"  {num}.  {name}")
        print("  0.  Quit")
        print("=" * 40)

        choice = input("Select a simulation: ").strip()

        if choice == "0":
            print("Goodbye!")
            sys.exit(0)

        matched = False
        for num, name, module in SIMULATIONS:
            if choice == str(num):
                print(f"\nRunning {name} — close the window to return to the menu.\n")
                module.run()
                matched = True
                break

        if not matched:
            print("Invalid choice, please try again.")
