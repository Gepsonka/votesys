from scripts import election_simulation


if __name__ == "__main__":
    simulation = election_simulation.ElectionSimulation(51.0)
    simulation.simulate_election()
