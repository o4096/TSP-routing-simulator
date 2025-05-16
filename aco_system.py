import numpy as np
import matplotlib.pyplot as plt
import random, time

class City:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def distance(self, other):
		return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
	
class Ant:
	def __init__(self, cost=0.0, tour=None):
		self.cost= cost
		if tour==None: self.tour= []
		else:          self.tour= tour[:]

	def clear(self):
		self.cost= 0.0
		self.tour= []
class SystemACO:
	def __init__(self, cities, objfunc, num_ants=50, init_pheromone=1, evaporation_rate=0.1, Q=100, alpha=1, beta=2, seed=None):
		self.cities = cities[:]
		self.objfunc = objfunc
		self.ants = [Ant() for _ in range(num_ants)]
		self.pheromones = np.ones((len(cities), len(cities))) * init_pheromone
		self.eva_rate = evaporation_rate
		self.Q = Q
		self.alpha = alpha
		self.beta = beta
		random.seed(seed)

	def update(self):
		for ant in self.ants:
			# construct_solution(ant, cities, pheromone, visibility, alpha, beta)
			ant.clear()
			unvisited =  list(range(len(self.cities)))
			prob= [1/len(unvisited) for _ in range(len(unvisited))]
			while unvisited:
				city= random.choices(unvisited, prob)[0]
				ant.tour.append(city)
				unvisited.remove(city)
				prob= []
				for next_city in unvisited:
					tau = self.pheromones[city][next_city]**self.alpha
					eta= (1/self.objfunc(self.cities[city], self.cities[next_city]))**self.beta
					prob.append(tau*eta)
				prob = np.array(prob)
				prob /= np.sum(prob)

			for i in range(len(ant.tour)-1):
				ant.cost += self.objfunc(self.cities[ant.tour[i]], self.cities[ant.tour[i+1]])
		self.pheromones *= (1 - self.eva_rate)
		for ant in self.ants:
			for i in range(len(ant.tour)-1):
				src= ant.tour[i]
				dst= ant.tour[i+1]
				self.pheromones[src][dst]+= self.Q/ant.cost
				self.pheromones[dst][src]+= self.Q/ant.cost

	def get_best(self, num=1):
		sorted_ants= sorted(self.ants, key=lambda a: a.cost)
		return sorted_ants[:num]

# def calculate_visibility(cities):
#     num_cities = len(cities)
#     visibility = np.zeros((num_cities, num_cities))
#     for i in range(num_cities):
#         for j in range(num_cities):
#             if i != j:
#                 visibility[i][j] = 1.0 / cities[i].distance(cities[j])
#     return visibility

# # ACO System Algorithm

# # def select_next_city(current_city, unvisited_cities, pheromone, visibility, alpha, beta):
#     pheromone_values = np.array([pheromone[current_city][i] for i in unvisited_cities])
#     visibility_values = np.array([visibility[current_city][i] for i in unvisited_cities])
	
#     probabilities = (pheromone_values**alpha) * (visibility_values**beta)
#     probabilities /= np.sum(probabilities)
	
#     return np.random.choice(unvisited_cities, p=probabilities)

# def construct_solution(ant:Ant, cities:list[City], pheromone, visibility, alpha, beta):
#     num_cities = len(cities)
#     ant.clear()
#     start_city = np.random.randint(num_cities)
#     ant.tour.append(start_city)
	
#     unvisited_cities = list(range(num_cities))
#     unvisited_cities.remove(start_city)
	
#     current_city = start_city
#     while unvisited_cities:
#         next_city = select_next_city(current_city, unvisited_cities, pheromone, visibility, alpha, beta)
#         ant.tour.append(next_city)
#         ant.total_distance += cities[current_city].distance(cities[next_city])
#         unvisited_cities.remove(next_city)
#         current_city = next_city
	
#     # Return to the starting city
#     ant.total_distance += cities[current_city].distance(cities[start_city])

# def update_pheromone(pheromone, ants, evaporation_rate, Q):
#     num_cities = pheromone.shape[0]
#     # Evaporation
#     pheromone *= (1 - evaporation_rate)
	
#     # Deposit
#     for ant in ants:
#         contribution = Q / ant.total_distance
#         for i in range(len(ant.tour) - 1):
#             from_city = ant.tour[i]
#             to_city = ant.tour[i + 1]
#             pheromone[from_city][to_city] += contribution
#             pheromone[to_city][from_city] += contribution
#         # # Add contribution for the return to the start
#         # start_city = ant.tour[0]
#         # last_city = ant.tour[-1]
#         # pheromone[last_city][start_city] += contribution
#         # pheromone[start_city][last_city] += contribution

# def aco_tsp(cities, num_ants, num_iterations, alpha, beta, evaporation_rate, Q, initial_pheromone):
#     num_cities = len(cities)
#     pheromone = initialize_pheromone(num_cities, initial_pheromone)
#     visibility = calculate_visibility(cities)
	
#     best_distance = float('inf')
#     best_tour = None
	
#     for iteration in range(num_iterations):
#         ants = [Ant(num_cities) for _ in range(num_ants)]
		
#         for ant in ants:
#             construct_solution(ant, cities, pheromone, visibility, alpha, beta)
		
#         # Find the best ant of this iteration
#         iteration_best_ant = min(ants, key=lambda x: x.total_distance)
		
#         if iteration_best_ant.total_distance < best_distance:
#             best_distance = iteration_best_ant.total_distance
#             best_tour = iteration_best_ant.tour
		
#         update_pheromone(pheromone, ants, evaporation_rate, Q)
	
#     return best_tour, best_distance

# def plot_tour(cities, tour):
#     x = [cities[i].x for i in tour] + [cities[tour[0]].x]
#     y = [cities[i].y for i in tour] + [cities[tour[0]].y]
#     plt.plot(x, y, 'ro-')
#     plt.title('Best Tour Found by ACO')
#     plt.xlabel('X')
#     plt.ylabel('Y')
#     plt.show()


if __name__ == "__main__":
	#Config of Problem (Application Side)
	n_cities = 50
	cities = [City(random.randint(0, 500), random.randint(0, 500)) for _ in range(n_cities)]
	colony = SystemACO(cities,
					   lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance)
	)

	#Main Loop
	ITERATIONS = 100
	loss=[0.0]*ITERATIONS
	t0 = time.time()
	for iteration in range(ITERATIONS):
		colony.update()
		best= colony.get_best()[0]
		print(f'Iteration {iteration+1:2d}/{ITERATIONS} - Best Distance: {best.cost}')
		loss[iteration]= best.cost
	dt = time.time() - t0

	best= colony.get_best()[0]
	print(f'Best Tour: {[int(city) for city in best.tour]}')
	print(f'Best Distance: {best.cost} km')
	print(f'Algorithm Time Taken: {dt} seconds')

	x= [cities[i].x for i in best.tour]+[cities[best.tour[0]].x]
	y= [cities[i].y for i in best.tour]+[cities[best.tour[0]].y]
	plt.figure(figsize=(12, 6))
	plt.subplot(1, 2, 1)
	plt.plot(x, y, 'ro-')
	plt.title('Best Tour Found by ACO')
	plt.xlabel('X')
	plt.ylabel('Y')

	plt.subplot(1, 2, 2)
	plt.plot(range(ITERATIONS), loss, 'b-')
	plt.title('Total Distance Over Iterations')
	plt.xlabel('Iteration')
	plt.ylabel('Total Distance')
	plt.tight_layout()
	plt.show()

	

# if __name__ == "__main__":
#     np.random.seed(42)
#     num_cities = 10
#     cities = [City(np.random.uniform(0, 100), np.random.uniform(0, 100)) for _ in range(num_cities)]
	
#     num_ants = 18
#     num_iterations = 100
#     alpha = 1
#     beta = 2
#     evaporation_rate = 0.1
#     Q = 100
#     initial_pheromone = 1.0
	
#     best_tour, best_distance = aco_tsp(cities, num_ants, num_iterations, alpha, beta, evaporation_rate, Q, initial_pheromone)
#     print(f"Best tour: {best_tour}")
#     print(f"Best distance: {best_distance}")
	
#     plot_tour(cities, best_tour)


#  if __name__ == "__main__":
#     np.random.seed(42)
#     num_cities = 10
#     cities = [City(np.random.uniform(0, 100), np.random.uniform(0, 100)) for _ in range(num_cities)]
	
#     num_ants = 10
#     num_iterations = 100
#     alpha = 1
#     beta = 2
#     evaporation_rate = 0.1
#     Q = 100
#     initial_pheromone = 1.0
	
#     # Initialize pheromone and visibility
#     pheromone = initialize_pheromone(num_cities, initial_pheromone)
#     visibility = calculate_visibility(cities)
	
#     best_distance = float('inf')
#     best_tour = None
	
#     # Run ACO for the specified number of iterations
#     for iteration in range(num_iterations):
#         ants = [Ant(num_cities) for _ in range(num_ants)]
		
#         for ant in ants:
#             construct_solution(ant, cities, pheromone, visibility, alpha, beta)
		
#         # Find the best ant of this iteration
#         iteration_best_ant = min(ants, key=lambda x: x.total_distance)
		
#         if iteration_best_ant.total_distance < best_distance:
#             best_distance = iteration_best_ant.total_distance
#             best_tour = iteration_best_ant.tour
		
#         update_pheromone(pheromone, ants, evaporation_rate, Q)
	
#     # Print each ant's tour distance
#     for i, ant in enumerate(ants):
#         print(f"Ant {i+1} Tour Distance: {ant.total_distance}")
	
#     # Plotting the best tour
#     plt.figure(figsize=(10, 10))
#     x_best = [cities[i].x for i in best_tour] + [cities[best_tour[0]].x]
#     y_best = [cities[i].y for i in best_tour] + [cities[best_tour[0]].y]
#     plt.plot(x_best, y_best, 'ro-', label='Best Tour')
	
#     # Plotting each ant's tour
#     for i, ant in enumerate(ants):
#         x_ant = [cities[j].x for j in ant.tour] + [cities[ant.tour[0]].x]
#         y_ant = [cities[j].y for j in ant.tour] + [cities[ant.tour[0]].y]
#         plt.plot(x_ant, y_ant, '-', label=f'Ant {i+1} Tour', alpha=0.5)
	
#     # Plotting the cities
#     city_x = [city.x for city in cities]
#     city_y = [city.y for city in cities]
#     plt.scatter(city_x, city_y, color='blue', s=50, zorder=5)
	
#     plt.title('Tours of 10 Ants and Best Tour')
#     plt.xlabel('X')
#     plt.ylabel('Y')
#     plt.legend(loc='upper right')
#     plt.grid(True)
#     plt.show()
	
#     print(f"Best tour: {best_tour}")
#     print(f"Best distance: {best_distance}")