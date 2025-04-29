import numpy as np
import matplotlib.pyplot as plt
import time, random

class City:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Ant:
	def __init__(self):
		self.clear()

	def clear(self):
		self.cost= 0.0
		self.tour= []

class HybridACO:
	def __init__(self, cities, objfunc, num_ants=50, init_pheromone=1, evaporation_rate=0.1, Q=100, alpha=1, beta=2, seed=None):
		self.cities=		cities[:]
		self.objfunc=		objfunc #TODO: handle objective function better, what if it doesn't have 2 cities as parameters?
		self.ants=		[Ant() for _ in range(num_ants)]
		self.pheromones=	np.ones((len(cities), len(cities)))*init_pheromone
		self.eva_rate=		evaporation_rate
		self.Q=			Q	#TODO: should this be parameterized?
		self.alpha=		alpha
		self.beta=		beta
		# self._best_ant= None
		if seed:
			random.seed(int(seed))

	def update(self):
		for ant in self.ants:
			ant.clear()
			unvisited= list(range(len(self.cities)))
			prob= [1/len(unvisited) for _ in range(len(unvisited))]
			while unvisited:
				city= random.choices(unvisited, prob)[0]
				# city= np.random.choice(unvisited, p=prob) #TODO find a way to seed this!!!
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
		
		self.pheromones*= (1-self.eva_rate) #TODO: which is better? update pheromones only after all ants have explored vs after each individual ant exploration
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

	def replace_worst(self, children_tours):
		self.ants.sort(key=lambda a: a.cost, reverse=True)
		for i in range(len(children_tours)):
			new_ant= Ant()
			new_ant.tour= children_tours[i]
			new_ant.cost= sum(self.objfunc(self.cities[new_ant.tour[i]], self.cities[new_ant.tour[i+1]]) for i in range(len(new_ant.tour)-1))
			self.ants[-(i+1)]= new_ant

def order_crossover(parent1, parent2):
	size = len(parent1)
	start, end= sorted(random.sample(range(size), 2))

	child= [-1]*size
	child[start:end+1]= parent1[start:end+1]

	ptr= (end+1)%size
	for city in parent2:
		if city not in child:
			child[ptr]= city
			ptr= (ptr+1)%size

def mutate(tour, mutation_rate=0.1):
	tour= tour[:]
	if random.random() < mutation_rate:
		i , j= random.sample(range(len(tour)), 2)
		tour[i], tour[j]= tour[j], tour[i]
	return tour

def generate_children(top_ants, num_children, mutation_rate=0.1):
	children= []

	while len(children)<num_children:
		parent1= random.choice(top_ants).tour
		parent2= random.choice(top_ants).tour

		if parent1!=parent2:
			child_tour= order_crossover(parent1, parent2)
			child_tour= mutate(child_tour, mutation_rate)
			children.append(child_tour)
	return children

def main(seed=None):
	'''Example program that uses HybridACO Algorithm'''
	#Config of Problem   (Application Side)
	random.seed(seed)
	n_cities= 50
	cities=   [City(random.randint(0, 500), random.randint(0, 500)) for _ in range(n_cities)]

	#Config of Algorithm (Passed to Algorithm Class by Application)
	colony= HybridACO(cities, #TODO: it'll probably be better to pass the graph inside the main loop
	        # lambda c1, c2: abs(c1.x-c2.x)+abs(c1.y-c2.y),		#l1_norm - Manhattan Distance
	        lambda c1, c2: np.sqrt((c1.x-c2.x)**2+(c1.y-c2.y)**2),	#l2_norm - Euclidean Distance
	)

	#Main Loop
	ITERATIONS=	10
	ga_interval=	10
	loss= [0.0]*ITERATIONS
	t0= time.time()
	for iteration in range(ITERATIONS):
		colony.update()

		if iteration%ga_interval==0 and iteration!=0:
			children_tours= generate_children(colony.get_best(10), num_children=10, mutation_rate=0.1)
			colony.replace_worst(children_tours)

		best= colony.get_best()[0]
		print(f'Iteration {iteration+1:2d}/{ITERATIONS} - Best Distance: {best.cost}')
		loss[iteration]= best.cost

	dt= time.time()-t0

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

if __name__=='__main__':
	main(seed=42)
