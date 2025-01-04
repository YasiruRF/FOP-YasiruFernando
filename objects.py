import random
import numpy as np
import matplotlib.pyplot as plt
from math import pi, sin

#Item classes
class Object:
    def __init__(self, pos, colour, size, heat_val = 50):
        self.pos = pos
        self.item_colour = np.array(colour)
        self.colour = self.item_colour.copy()
        self.size = size
        self.heat_val = heat_val
        self.image = np.full((self.size[0], self.size[1], 3), self.colour)  

    def get_coord(self):
        return self.pos

    def get_colour(self):
        return self.colour

    def set_colour(self, colour):
        self.item_colour = np.array(colour)
        self.colour = self.item_colour.copy()
        self.image = np.full((self.size[0], self.size[1], 3), self.colour)  

    def get_image(self):
        return np.full((self.size[0], self.size[1], 3), self.colour)

    def set_image(self, image):
        if image.shape[:2] == (self.size[0], self.size[1]):
            self.image = image
        else:
            raise ValueError(f"Image size {image.shape[:2]} does not match object size {self.size}.")
         
    def get_topleft(self):
        xleft = self.pos[0] - self.size[1] // 2
        ytop = self.pos[1] - self.size[0] // 2
        return (xleft, ytop)

    def get_size(self):
        return self.size

    def set_size(self, size):
        self.size = size
        self.image = np.full((self.size[0], self.size[1], 3), self.colour)  

    def get_heat_val(self):
        return self.heat_val
    
    def set_heat_val(self, heat_val):
        self.heat_val = heat_val

    def day_night(self, factor):
        brightness = np.array([50,30,30])
        self.colour = np.clip(self.item_colour+ brightness*(1-factor), 50, 250).astype(np.uint8)
        self.image = np.full((self.size[0], self.size[1], 3), self.colour)  

    def get_type(self):
        return self.__class__.__name__
    
    def __str__(self):
        return f"{self.__class__.__name__}: {self.pos}, Color: {self.colour}"

class Tree(Object):
    def __init__(self, pos, colour, size):
        super().__init__(pos, colour, (size, size), heat_val = 70)

class House(Object):
    def __init__(self, pos, colour, height, width, boundary):
        super().__init__(pos, colour, (height, width), heat_val = 80)
        self.boundary = boundary

    def boundry_setting(self, x, y):
        house_x, house_y = self.pos
        house_height, house_width = self.size

        left = house_x - self.boundary
        right = house_x + house_width + self.boundary
        top = house_y - self.boundary
        bottom = house_y + house_height + self.boundary

        return left <= x <= right and top <= y <= bottom
    
class Apartment(Object):
    def __init__(self, pos, colour, height, width, boundary):
        super().__init__(pos, colour, (height, width), heat_val = 80)
        self.boundary = boundary

    def boundry_setting(self, x, y):
        apartment_x, apartment_y = self.pos
        apartment_height, apartment_width = self.size

        left = apartment_x - self.boundary
        right = apartment_x + apartment_width + self.boundary
        top = apartment_y - self.boundary
        bottom = apartment_y + apartment_height + self.boundary

        return left <= x <= right and top <= y <= bottom

class Street(Object):
    def __init__(self, pos, height, width, colour=np.array([48,46,46])):
        super().__init__(pos, colour, (height, width), heat_val = 80)

class White_lines(Object):
    def __init__(self, pos, height, width, colour=np.array([255,255,255])):
        super().__init__(pos, colour, (height, width), heat_val = 80)

class Pond(Object):
    def __init__(self, pos, size, colour=np.array([51, 53, 255])):
        super().__init__(pos, colour, (size, size), heat_val = 50)

class Bushes(Object):
    def __init__(self, pos, colour, size):
        super().__init__(pos, colour, (size, size), heat_val = 70)

class MerryGo(Object):
    def __init__(self, pos, colour, size):
        super().__init__(pos, colour, (size, size), heat_val = 90)

    def get_image(self):
        image = np.full((self.size[0], self.size[1], 3), self.colour)
        
        # Creating a circulr shape
        y, x = np.ogrid[:self.size[0], :self.size[1]]
        center = (self.size[0] / 2-0.5, self.size[1] / 2-0.5)
        radius = np.sqrt((x - center[0])**2 + (y - center[1])**2)
        mask = radius <= min(self.size[0], self.size[1]) // 2
        
        #applying to the square.
        image[~mask] = [153, 255, 204]  
        
        return image
    
    def set_image(self, new_image):
        self._image = new_image

class Slide(Object):
    def __init__(self, pos, colour, size):
        super().__init__(pos, colour, (size, size), heat_val = 90)

#block classes
class Blocks:
    def __init__(self, size, topleft, colour=np.array([255, 255, 255]), heat_val = 50):
        self.size = size
        self.topleft = topleft
        self.items = []
        self.bg_colour = np.array(colour)
        self.colour = self.bg_colour.copy()
        self.heat_val = heat_val

    def get_topleft(self):
        return self.topleft

    def add_item(self, item):
        self.items.append(item)

    def set_bg_colour(self, colour):
        self.bg_colour = np.array(colour)
        self.colour = self.bg_colour.copy()

    def generate_image(self):
        grid = np.full((self.size, self.size, 3), self.colour)
        for item in self.items:
            topleft = item.get_topleft()
            img = item.get_image()
            cx_start = topleft[0]
            ry_start = topleft[1]
            cx_stop = cx_start + img.shape[1]
            ry_stop = ry_start + img.shape[0]
            grid[ry_start:ry_stop, cx_start:cx_stop] = img
        return grid

    def get_heat_val(self):
        return self.heat_val
    
    def set_heat_val(self, heat_val):
        self.heat_val = heat_val

    def day_night(self, factor):
        brightness = np.array([50,30,30])
        self.colour = np.clip(self.bg_colour + brightness*(1-factor), 50, 255).astype(np.uint8)
        for item in self.items:
            item.day_night(factor)
    
    def set_image(self, image):
        if image.shape[:2] == (self.size, self.size):
            self.colour = np.mean(image, axis=(0, 1)).astype(np.uint8)

    def get_type(self):
        return self.__class__.__name__

    def __str__(self):
        return f"{self.__class__.__name__}: {self.topleft}, #items = {len(self.items)}"

# Subclasses
class Ground(Blocks):
    def __init__(self, size, topleft, colour=np.array([239, 168, 61])):
        super().__init__(size, topleft, colour, heat_val = 60)

class Park(Blocks):
    def __init__(self, size, topleft,colour=np.array([153, 255, 204])):
        super().__init__(size, topleft, colour, heat_val = 80)

class Forest(Blocks):
    def __init__(self, size, topleft, colour=np.array([120,202,123])):
        super().__init__(size, topleft, colour, heat_val = 50)

class Water(Blocks):
    def __init__(self, size, topleft, colour=np.array([0,119,190])):
        super().__init__(size, topleft, colour, heat_val = 50)

class Road(Blocks):
    def __init__(self, size, topleft, colour=np.array([94, 82, 82])):
        super().__init__(size, topleft, colour, heat_val = 80)


