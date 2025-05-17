import numpy as np
import matplotlib.pyplot as plt
import random, time

class City:
	def __init__(self, x, y):
		self.x= x
		self.y= y

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

if __name__ == "__main__":
	#Config of Problem (Application Side)
	n_cities = 50
	cities = [City(random.randint(0, 500), random.randint(0, 500)) for _ in range(n_cities)]
	colony = SystemACO(cities, lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance)
	)

	#Main Loop
	ITERATIONS = 100
	loss=[0.0]*ITERATIONS
	t0 = time.time()
	best_cost= float('inf')
	best_path= []

	for iteration in range(ITERATIONS):
		colony.update()
		
		for ant in colony.ants:
			if best_cost>ant.cost:
				best_cost=ant.cost
				best_path=ant.tour

		print(f'Iteration {iteration+1:2d}/{ITERATIONS} - Best Distance: {best_cost}')
		loss[iteration]= best_cost
	dt = time.time() - t0

	best= colony.get_best()[0]
	print(f'Best Tour: {[int(city) for city in best_path]}')
	print(f'Best Distance: {best_cost} km')
	print(f'Algorithm Time Taken: {dt} seconds')

	x= [cities[i].x for i in best_path]+[cities[best_path[0]].x]
	y= [cities[i].y for i in best_path]+[cities[best_path[0]].y]
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
