import numpy as np
import random

class City:
    def __init__(self, x=None, y=None, id=None):
        """
        Initialize a city with coordinates (x,y) and an optional id.
        If coordinates are not provided, they are randomly initialized.
        """
        self.x = x if x is not None else random.randint()
        self.y = y if y is not None else random.randint()
        self.id = id
    
    def distance(self, city):
        """Calculate the Euclidean distance to another city."""
        return np.sqrt((self.x - city.x) ** 2 + (self.y - city.y) ** 2)
    
    def __str__(self):
        """String representation of the city."""
        return f"City(id={self.id}, x={self.x:.2f}, y={self.y:.2f})"