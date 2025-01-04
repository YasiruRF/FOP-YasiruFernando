import random
import numpy as np
from objects import *  # Assuming this file contains all the block and item classes
import csv
import os

#reading data from csv file and error handling for it.
def csv_read(filename):
    house_colors = []
    tree_colors = []
    
    if not os.path.exists(filename):
        print(f"CSV file '{filename}' not found. Using default colors.")
        return None, None

    try:
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['type'].lower() == 'house':
                    house_colors.append(np.array([int(row['r']), int(row['g']), int(row['b'])]))
                elif row['type'].lower() == 'tree':
                    tree_colors.append(np.array([int(row['r']), int(row['g']), int(row['b'])]))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None, None

    return house_colors, tree_colors

#Appending blocks
def place_blocks(map_shape, blocksize):
    blocks = []

    # Placing Ground blocks
    for i in range(map_shape[0] - 1):
        for j in range(map_shape[1] - 1):
            blocks.append(Ground(blocksize, (blocksize * j, blocksize * i)))

    # Placing Water blocks
    for i in range(map_shape[0]):
        for j in range(map_shape[1] - 1, map_shape[1]):
            blocks.append(Water(blocksize, (blocksize * j, blocksize * i)))
    for i in range(map_shape[0] - 1, map_shape[0]):
        for j in range(map_shape[1]):
            blocks.append(Water(blocksize, (blocksize * j, blocksize * i)))

    return blocks

#Adding forests and items
def add_forest(blocks, map_shape, blocksize, tree_colors):
    forest = []
    for i in range(2):
        for j in range(2): 
            blocks.append(Forest(blocksize, (blocksize * j, blocksize * i)))
            forest.append(len(blocks) - 1)

    default_tree_color = np.array([40, 200, 23])
    
    for forest_index in forest:
        for _ in range(30):
            tree_color = random.choice(tree_colors) if tree_colors else default_tree_color
            blocks[forest_index].add_item(Tree((random.randint(4, 22), random.randint(4, 22)), tree_color, 5))

    return blocks, forest

#Adding houses and apartments
def add_household(blocks, map_shape, blocksize, house_colors, tree_colors):
    default_house_color = np.array([154, 200, 53])
    default_tree_color = np.array([40, 200, 23])

    for i in range(map_shape[0] - 1):
        if i % 3 == 0:
            for j in range(map_shape[1] - 1):
                block_index = i * (map_shape[1] - 1) + j
                house_color = random.choice(house_colors) if house_colors else default_house_color
                house = House((random.randint(6,19), random.randint(3,22)), house_color, 6, 12, boundary=5)
                blocks[block_index].add_item(house)    
                trees = 0
                attempts = 0
                tree_size = 5
                while trees < 5 and attempts < 50:
                    tree_x = random.randint(3, 22)
                    tree_y = random.randint(3, 22)

                    #Overlay handling for the house
                    if not house.boundry_setting(tree_x, tree_y) and not house.boundry_setting(tree_x + tree_size, tree_y + tree_size):
                        tree_color = random.choice(tree_colors) if tree_colors else default_tree_color
                        success = blocks[block_index].add_item(Tree((tree_x, tree_y), tree_color, tree_size))
                        if success:
                            trees += 1
                    attempts += 1
            
        else:
            for j in range(map_shape[1]-1):
                block_index = i * (map_shape[1]-1)+j
                house_color = random.choice(house_colors) if house_colors else default_house_color
                apartment = Apartment((random.randint(8,17),random.randint(4,21)), house_color, 8, 16, boundary=6)
                blocks[block_index].add_item(apartment)
                bushes = 0
                attempts = 0
                bushes_size = 3
                while bushes < 10 and attempts < 50:
                    bushes_x = random.randint(3,22)
                    bushes_y = random.randint(3, 22)

                    #Overlay handling for the apartment
                    if not apartment.boundry_setting(bushes_x, bushes_y) and not apartment.boundry_setting(bushes_x + bushes_size, bushes_y + bushes_size):
                        tree_color = random.choice(tree_colors) if tree_colors else default_tree_color
                        success = blocks[block_index].add_item(Bushes((bushes_x, bushes_y), tree_color, bushes_size))
                        if success:
                            bushes += 1
                    attempts += 1
    return blocks

#Adding roads and items
def add_roads(blocks, map_shape, blocksize, tree_colors):
    default_tree_color = np.array([40, 200, 23])
    roads = []
    for i in range(map_shape[0] - 1):
        if i % 5 == 4:
            for j in range(map_shape[1]):
                blocks.append(Road(blocksize, (blocksize * j, blocksize * i)))
                roads.append(len(blocks) - 1)

    for road_index in roads:
        blocks[road_index].add_item(Street((int(12.5), int(12.5)), 15, 25))
        blocks[road_index].add_item(White_lines((5, 13), 1, 5))
        tree_color = random.choice(tree_colors) if tree_colors else default_tree_color
        blocks[road_index].add_item(Bushes((6, 22), tree_color, 3))
        blocks[road_index].add_item(Bushes((6, 2), tree_color, 3))

    return blocks, roads

#Adding playgrounds and items
def adding_park(blocks, map_shape, blocksize, tree_colors):
    default_tree_color = np.array([40, 200, 23])
    parks = []
    for i in range(map_shape[0] - 1):
        if i % 5 == 3:
            for j in range(map_shape[1] - 1):
                if j % 7 == 1:
                    blocks.append(Park(blocksize, (blocksize * j, blocksize * i)))
                    parks.append(len(blocks) - 1)

    for parks_index in parks:
        c = 3
        for _ in range(4):
            tree_color = random.choice(tree_colors) if tree_colors else default_tree_color
            blocks[parks_index].add_item(Bushes((c, int(2.5)), tree_color, 3))
            blocks[parks_index].add_item(Bushes((int(2.5), c), tree_color, 3))
            c += 5
        blocks[parks_index].add_item(MerryGo((20, 20), np.array([150, 50, 50]), 8))
        blocks[parks_index].add_item(Slide((10, 20), np.array([150, 50, 150]), 4))
        tree_color = random.choice(tree_colors) if tree_colors else default_tree_color
        blocks[parks_index].add_item(Tree((20, 10), tree_color, 5))
        blocks[parks_index].add_item(Pond((10, 12), 7))

    return blocks, parks

#Setting up the map.
def make_map(blocksize, rows, cols, add_forests, add_parks, csv_filename='colours.csv'):
    house_colors, tree_colors = csv_read(csv_filename)
    map_shape = (rows, cols)
    blocks = place_blocks(map_shape, blocksize)

    if add_forests:
        blocks, forest = add_forest(blocks, map_shape, blocksize, tree_colors)
    else:
        print("Skipping forest")

    blocks = add_household(blocks, map_shape, blocksize, house_colors, tree_colors)
    blocks, roads = add_roads(blocks, map_shape, blocksize, tree_colors)
    
    if add_parks:
        blocks, parks = adding_park(blocks, map_shape, blocksize, tree_colors)
    else:
        print("Skipping Parks")

    return blocks, map_shape
