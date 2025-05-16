# Optimized Waste Collection Routing in Cities
A simulation platform to solve the Traveling Salesman Problem (TSP) to collect waste from various cities using various heuristic and metaheuristic optimization techniques, with a focus on Ant Colony Optimization (ACO) and its hybrid variants.
## Project Overview

This project implements many variants of Ant Colony Optimization (ACO) algorithms to solve the Traveling Salesman Problem (TSP). The implementations include:

**Multiple ACO-based algorithms:**
- Basic ACO
- Max-Min ACO
- Distributed ACO

**Hybrid Approaches:**
- ACO + Genetic Algorithm (GA)
- ACO + Simulated Annealing (SA)

all algorithms are evaluated on randomly generated TSP instances, and their performances are compared in terms of solution quality and convergence speed.

## Key Components
1. Graph Representation: The problem is modeled as a graph where:
  - Nodes represent decision points (e.g., cities in TSP or waste collection points in WCRP). 
  - Edges represent possible connections or paths between nodes, often associated with a cost (e.g., distance or time).
2. Artificial Ants: These are agents that explore the graph by constructing solutions (e.g., a route) based on probabilistic decisions influenced by pheromone trails and heuristic information.
3. Pheromone Trails: Each edge in the graph has an associated pheromone value, which represents the desirability of choosing that path. Pheromone levels are updated based on the quality of solutions found by the ants.
![image](https://github.com/user-attachments/assets/4796789c-8c0d-471c-8af3-645b0304e810)

## Algorithms Implemented:
### 1- Basic ACO:
  Simulates the behavior of ants seeking paths between their colony and food sources, adapted for solving TSP.
  ![image](https://github.com/user-attachments/assets/43d33b02-e517-4c75-b04b-928b8cbde052)
  
### 2- Min-Max ACO:
  An enhancement of ACO that restricts pheromone values within upper and lower bounds to improve convergence.
  ![image](https://github.com/user-attachments/assets/a086d41b-a6ab-48cd-8910-5d9253793182)

### 3- Distributed ACO:
  Divides the search effort among multiple colonies that work independently with periodic information exchange to improve solution quality and convergence speed.\
  ![image](https://github.com/user-attachments/assets/c102ddc1-0ad0-413e-840f-409e449477c3) ![image](https://github.com/user-attachments/assets/fb0d6fba-400f-4331-9d6f-48b696ffb66b)

### 4- Hybrid ACO + Genetic Algorithm (GA):
  Periodically applies crossover and mutation to improve the diversity of solutions and avoid local optima.
  ![image](https://github.com/user-attachments/assets/46cc7e22-b180-4bd2-89b0-915011b146f4) ![image](https://github.com/user-attachments/assets/d45a2454-38ac-47d3-aa77-0e0079c54e5a)

### 5 - Hybrid ACO + Simulated Annealing (SA):
  Uses probabilistic acceptance of worse solutions to avoid local optima.
  ![image](https://github.com/user-attachments/assets/10ab72ee-4df1-4819-b1a9-5d5389b3388a)





