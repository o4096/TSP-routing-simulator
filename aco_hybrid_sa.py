import numpy as np
import matplotlib.pyplot as plt
import time, random

class City:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Ant:
	def __init__(self, cost=0.0, tour=None):
		self.cost= cost
		if tour==None: self.tour= []
		else:          self.tour= tour[:]

	def clear(self):
		self.cost= 0.0
		self.tour= []

class HybridACO_SA:
	def __init__(self, cities, objfunc, num_ants=50, init_pheromone=1, evaporation_rate=0.1, Q=100, alpha=1, beta=2 , seed=None):
		self.cities=		cities[:]
		self.objfunc=		objfunc
		self.ants=		[Ant() for _ in range(num_ants)]
		self.pheromones=	np.ones((len(cities), len(cities)))*init_pheromone
		self.eva_rate=		evaporation_rate
		self.Q=			Q
		self.alpha=		alpha
		self.beta=		beta
		random.seed(seed)
		# self._best_ant= None

	def update(self):
		for ant in self.ants:
			ant.clear()
			unvisited= list(range(len(self.cities)))
			prob= [1/len(unvisited) for _ in range(len(unvisited))]
			while unvisited:
				city= random.choices(unvisited, prob)[0]
				ant.tour.append(city)
				unvisited.remove(city)

				prob= []
				for next_city in unvisited:
					tau= self.pheromones[city][next_city]**self.alpha
					eta= (1/self.objfunc(self.cities[city], self.cities[next_city]))**self.beta
					prob.append(tau*eta)
				prob=  np.array(prob)
				prob/= np.sum(prob)
				
			for i in range(len(ant.tour)-1):
				ant.cost+= self.objfunc(self.cities[ant.tour[i]], self.cities[ant.tour[i+1]])
		
		self.pheromones*= (1-self.eva_rate)
		for ant in self.ants:
			for i in range(len(ant.tour)-1):
				src= ant.tour[i]
				dst= ant.tour[i+1]
				self.pheromones[src][dst]+= self.Q/ant.cost
				self.pheromones[dst][src]+= self.Q/ant.cost

		# for ant in self.ants:
		# 	if ant.cost<self.best_cost:
		# 		self._best_ant= ant

	def get_best(self, num=1):
		sorted_ants= sorted(self.ants, key=lambda a: a.cost)
		return sorted_ants[:num]
	
	# def get_best(self):
	# 	return self._best_ant



def simulated_annealing(tour, cities, objfunc, T_start=1000, T_end=1, alpha=0.995, max_iter=100):
	def tour_cost(tour):
		return sum(objfunc(cities[tour[i]], cities[tour[i+1]]) for i in range(len(tour)-1))

	current = tour[:]
	current_cost = tour_cost(current)
	best = current[:]
	best_cost = current_cost
	T = T_start

	while T > T_end:
		i, j = random.sample(range(len(current)), 2)
		neighbor = current[:]
		neighbor[i], neighbor[j] = neighbor[j], neighbor[i]

		neighbor_cost = tour_cost(neighbor)
		delta = neighbor_cost - current_cost

		if delta < 0 or random.random() < np.exp(-delta / T):
			current = neighbor
			current_cost = neighbor_cost
			if current_cost < best_cost:
				best = current
				best_cost = current_cost
		T *= alpha
	return best, best_cost

def main(seed=None):
	'''Example program that uses HybridACO Algorithm'''
	#Config of Problem   (Application Side)
	global_best_cost = float('inf')

	random.seed(seed)
	n_cities= 50
	cities=   [City(random.randint(0, 500), random.randint(0, 500)) for _ in range(n_cities)]

	#Config of Algorithm (Passed to Algorithm Class by Application)
	colony= HybridACO_SA(cities, #TODO: it'll probably be better to pass the graph inside the main loop
			# lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
			lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
	)

	#Main Loop
	ITERATIONS=	30
	loss= [0.0]*ITERATIONS
	t0= time.time()
	best_path= []
	best_cost= float('inf')
	for iteration in range(ITERATIONS):
		colony.update()
		
		for ant in colony.ants:
			if best_cost>ant.cost:
				best_cost=ant.cost
				best_path=ant.tour

		new_path, new_cost = simulated_annealing(best_path, colony.cities, colony.objfunc)
		if best_cost>new_cost:
			best_path= new_path
			best_cost= new_cost

		print(f'Iteration {iteration+1:2d}/{ITERATIONS} - Best Distance: {best_cost}')
		loss[iteration] = best_cost

	dt= time.time()-t0

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

if __name__=='__main__':
	main(seed=42)
