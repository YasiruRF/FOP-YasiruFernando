import random
import numpy as np
import matplotlib.pyplot as plt
from math import pi, sin
from object_placement import *
import argparse 

#Genertes the image of the map
def generate_image(blocks, blocksize, map_shape, hour, flood_progress, snow_progress):
    
    #Calculate time factor based on hour of the day for day and night simulation
    time_factor = 0.1 - 0.9 * sin((2 * pi / 24) * (hour - 6))
    
    grid = np.zeros((map_shape[0]*blocksize, map_shape[1]*blocksize, 3))
    
    #Defining colours for flood and snow
    flood_colour = np.array([0,119,190])
    snow_colour = np.array([255,255,255])

    for block in blocks:
        #Adjusting block brighness based on the time of the day
        block.day_night(time_factor)
        cx_start, ry_start = block.get_topleft()
        block_image = block.generate_image()
        
        #Handles flooding
        if flood_progress > 0:
            
            #Flooding blocks
            if block.get_type() in ['Ground', 'Water', 'Forest', 'Park'] and flood_progress > 0.2:
                block.set_bg_colour(flood_colour)  
            elif block.get_type() in 'Road' and flood_progress > 0.4:
                block.set_bg_colour(flood_colour)

            #Flooding items
            for item in block.items:
                item_type = item.get_type()
                if item_type in ['Pond'] and flood_progress > 0.2:
                    item.set_colour(flood_colour)
                elif item_type in ['Street', 'White_lines'] and flood_progress > 0.5:
                    item.set_colour(flood_colour)
                elif item_type in ['MerryGo'] and flood_progress > 0.6:
                    item.set_colour(flood_colour)
                elif item_type == 'Bushes' and flood_progress > 0.8:
                    item.set_colour(flood_colour)
                
        #Handles snowing
        if snow_progress > 0:
            # Snow covers blocks
            if block.get_type() in ['Ground', 'Forest', 'Park'] and snow_progress > 0.2:
                block.set_bg_colour(snow_colour)  
            elif block.get_type() == 'Road' and snow_progress > 0.4:
                block.set_bg_colour(snow_colour)

            #snow covers items
            for item in block.items:
                item_type = item.get_type()
                if item_type in ['Street', 'White_lines'] and snow_progress > 0.5:
                    item.set_colour(snow_colour)
                elif item_type in ['MerryGo'] and snow_progress > 0.6:
                    item.set_colour(snow_colour)
                elif item_type == 'Bushes' and snow_progress > 0.8:
                    item.set_colour(snow_colour)

        grid[ry_start:ry_start+blocksize, cx_start:cx_start+blocksize] = block_image
    return grid

#To simulates heat diffusion over time
def heat_diffusion(blocks, diffusion_rate=0.01, iterations=3):
    for _ in range(iterations):
        for block in blocks:
            items = block.items
        
            # Creates a grid to represent temperatures
            grid_size = (block.size, block.size)
            temperature_grid = np.full(grid_size, block.get_heat_val())
            
            # Set initial temperatures for items
            for item in items:
                x, y = item.get_topleft()
                size = item.get_size()
                temperature_grid[y:y+size[0], x:x+size[1]] = item.get_heat_val()
            
            # Applies diffusion
            temp_grid = temperature_grid.copy()
            for i in range(grid_size[0]):
                for j in range(grid_size[1]):
                    neighbors = []
                    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < grid_size[0] and 0 <= nj < grid_size[1]:
                            neighbors.append(temperature_grid[ni, nj])
                    if neighbors:
                        avg_temp = sum(neighbors) / len(neighbors)
                        temp_grid[i, j] += diffusion_rate * (avg_temp - temperature_grid[i, j])
            
            # Update item temperatures
            for item in items:
                x, y = item.get_topleft()
                size = item.get_size()
                new_temp = np.mean(temp_grid[y:y+size[0], x:x+size[1]])
                item.set_heat_val(new_temp)
            
            # Update block temperature
            block.set_heat_val(np.mean(temp_grid))
    
    return blocks

#Equation to calculate block and item heat changing over time
def thermal_equation(heat_val, hour, flood_level=0, snow_level=0):
    heat = heat_val + 15 * np.sin((2 * np.pi / 24) * (hour - 7))  
    cooldown = 10 * np.sin((2 * np.pi / 24) * (hour - 19))  
    temperature = heat - cooldown
    
    #Applying a cooling affect for flooding
    flood_cooling = 20 * flood_level  
    return max(0, temperature - flood_cooling)  

#Generates the thermal image of the map.
def generate_thermal_image(blocks, blocksize, map_shape, hour, flood_level=0, snow_level = 0):

    thermal_grid = np.zeros((map_shape[0]*blocksize, map_shape[1]*blocksize))
    
    #Dictionaries to store item and block heat over time
    block_temperatures = {'Ground': [], 'Water': [], 'Forest': [], 'Road': [], 'Park': []}
    item_temperatures = {'Tree': [], 'House': [], 'Bushes': [], 'Street': [], 'MerryGo': [], 'Slide': [], 'Pond': [], 'White_lines' : [], 'Apartment': []}

    for block in blocks:
        cx_start, ry_start = block.get_topleft()
        block_heat = thermal_equation(block.get_heat_val(), hour, flood_level, snow_level)
        thermal_grid[ry_start:ry_start+blocksize, cx_start:cx_start+blocksize] = block_heat
        block_temperatures[block.get_type()].append(block_heat)
        
        for item in block.items:
            item_heat = thermal_equation(item.get_heat_val(), hour, flood_level, snow_level)
            x, y = item.get_topleft()
            size = item.get_size()
            thermal_grid[ry_start + y:ry_start + y + size[0], cx_start + x:cx_start + x + size[1]] = item_heat
            item_temperatures[item.get_type()].append(item_heat)
    
    return thermal_grid, block_temperatures, item_temperatures

import random

#To get user inputs
def user_inputs():
    blocksize = 25
    rows = cols = 0
    flood = False
    snow = False
    stop_rain = 0

    #Error Handling for selecting map type
    print("=" * 30)
    print(" Please select a map option:")
    print("-" * 30)
    print(" 1. Normal Map")
    print(" 2. Snow Map")
    print(" 3. Rain Map")
    print("=" * 30)
    map_type = input("I select map: ")
    if map_type not in ['1','2','3']:
        print("Error: Invalid input. Selecting random map")
        maps = ['1','2','3']
        map_type = random.choice(maps)
    print("=" * 30)

    if map_type == '3':
        flood = True
        print("Rain map selected")
        try:
            stop_rain = int(input("For how many hours will the rain stop?: "))
            if stop_rain < 0:
                raise ValueError
        except ValueError:
            print("Invalid input. Setting the rain stopping time to 0 by default")
            stop_rain = 0

    elif map_type == '2':
        snow = True
        print("Snow map selected")

    else:
        print("Normal map selected")

    #Error handling for no. of columns and rows
    while rows*cols < 12:
        try:
            print("The minimum Block requirement is 12 blocks")
            rows = int(input("Please Input No. of Rows: "))
            cols = int(input("Please Input No. of Columns: "))
            if rows <= 0 or cols <= 0:
                raise ValueError
        except ValueError:
            print("Error: Invalid input, setting Rows and Columns to 10.")
            rows, cols = 10, 10

        if rows*cols < 12:
            print("Below the minimum Block requirement, Please try again")
            repeatrow = input("Do you want to change number of Rows? Y/N? ").lower()
            if repeatrow not in ['y','n']:
                print(f"Error: Invalid input, submit new values")
            elif repeatrow == 'y':
                continue
            elif repeatrow == 'n':
                try:
                    cols = int(input("Please Re-Enter No. of Columns: "))
                    if cols <= 0:
                        raise ValueError
                except ValueError:
                    print("Error: Invalid input, setting Columns to 10")
                    cols = 10

    #Error handling for setting number of days to run the simulation
    try:
        num_days = int(input("How many days should the simulation showcase?: "))
        if num_days <= 0:
            raise ValueError
    except ValueError:
        print("Invalid input. Number of days set to 3")
        num_days = 3

    #Error handling to addd forests
    forest = input("Do you want to add a forest? (Y/N) ").lower()
    add_forests = forest == 'y'
    if forest not in ['y','n']:
        print("Error: Invalid input. Setting up forest by default")
        add_forests = True

    #Error handling to add parks
    park = input("Do you want to add a park? (Y/N) ").lower()
    add_parks = park == 'y'
    if park not in ['y','n']:
        print("Error: Invalid input. Setting up park by default")
        add_parks = True

    return blocksize, rows, cols, num_days, add_forests, add_parks, flood, stop_rain, snow

#Generates rain
def generate_rain(shape, intensity):
    return np.random.random(shape) < intensity

#Applies rain
def apply_rain(image, rain):
    rain_color = np.array([93, 226, 231])  
    return np.where(rain[:,:,np.newaxis], rain_color, image)

#Generates snow
def generate_snow(shape, intensity):
    return np.random.random(shape) < intensity

#Applies snow
def apply_snow(image, snow):
    snow_color = np.array([255, 255, 255]) 
    return np.where(snow[:,:,np.newaxis], snow_color, image)


def simulate_snow(blocks, snow_intensity, temperature_drop = 30):
    for block in blocks:
        # Decrease outdoor temperature
        new_temp = max(block.get_heat_val() - temperature_drop, -5)  
        block.set_heat_val(new_temp)
        
        for item in block.items:
            #Decreases temperature of items that are not house or apartment
            if item.get_type() not in ['House', 'Apartment']:
                item_new_temp = max(item.get_heat_val() - temperature_drop, -5)
                item.set_heat_val(item_new_temp)
                
            else:
                # Increases the temperature for houses and apartments
                item_new_temp = min(item.get_heat_val() + 15, 25)  # Max indoor temp of 25°C
                item.set_heat_val(item_new_temp)
    
#Runs the simulation according to set configurations
def run_simulation(blocks, map_shape, num_days, flood, stop_rain, snow):
    blocksize = 25
    real_temperatures = []
    depicted_temperatures = []
    block_temp_history = {'Ground': [], 'Water': [], 'Forest': [], 'Road': [], 'Park': []}
    item_temp_history = {'Tree': [], 'House': [], 'Bushes': [], 'Street': [], 'MerryGo': [], 'Slide': [], 'Pond': [], 'White_lines' : [], 'Apartment': []}

    plt.figure(figsize=(10, 5))
    
    #Total no. of hours of the simulation
    total_hours = num_days * 24
    
    #Durations of snow and flooding
    flood_start = 3
    flood_end = total_hours - 6
    flood_duration = flood_end - flood_start

    snow_start = 3
    snow_end = total_hours-6
    snow_duration = snow_end - snow_start

    for hour in range(total_hours):
        day = hour // 24
        hour_of_day = hour % 24

        #Applying heat diffusion to blocks
        blocks = heat_diffusion(blocks)
        snow_progress = 0
        flood_progress = 0
      
        #Snows if snow = True
        if snow:    
            snow_progress = 0
            snow_intensity = 0

            #Caluculates snow progress and intensity
            if snow_start <= hour < snow_end:
                snow_progress = (hour - snow_start) / snow_duration
                snow_intensity = min(0.1, snow_progress * 0.2)  
            elif hour >= snow_end:
                snow_progress = 1
                snow_intensity = 0.3

            #Temperature drop as snow progresses
            temperature_drop = 5 * snow_progress  
            simulate_snow(blocks, snow_intensity, temperature_drop)

            #Apply snow effects
            canopy_map = generate_image(blocks, blocksize, map_shape, hour_of_day, flood_progress, snow_progress)
            snowing = generate_snow(canopy_map.shape[:2], snow_intensity)
            canop_snow = apply_snow(canopy_map, snowing)
            thermal_map, block_temperatures, item_temperatures = generate_thermal_image(blocks, blocksize, map_shape, hour_of_day, 0, snow_progress)
            plt.clf()
            plt.subplot(1, 2, 1)
            plt.imshow(canop_snow.astype(np.uint8))
            plt.title(f"Canopy Map - Day:{day+1:02d}, Time: {hour_of_day:02d}:00")
            plt.axis("off")

        elif flood:
            flood_progress = 0
            rain_intensity = 0

            #Calculates flood progress and intensity
            if flood and flood_start <= hour+stop_rain < flood_end:
                flood_progress = (hour - flood_start) / flood_duration
                rain_intensity = min(0.1, flood_progress * 0.2) 
            elif flood and hour >= flood_end:
                flood_progress = 1
                rain_intensity = 0.1  # Maximum rain intensity

            #Apply rain effects
            canopy_map = generate_image(blocks, blocksize, map_shape, hour_of_day, flood_progress, snow_progress)
            rain = generate_rain(canopy_map.shape[:2], rain_intensity)
            canopy_rain = apply_rain(canopy_map, rain)
            thermal_map, block_temperatures, item_temperatures = generate_thermal_image(blocks, blocksize, map_shape, hour_of_day, flood_progress)
            plt.clf()
            plt.subplot(1, 2, 1)
            plt.imshow(canopy_rain.astype(np.uint8))
            plt.title(f"Canopy Map - Day:{day+1:02d}, Time: {hour_of_day:02d}:00")
            plt.axis("off")

        else:
            #Generates normal map
            thermal_map, block_temperatures, item_temperatures = generate_thermal_image(blocks, blocksize, map_shape, hour_of_day)
            canopy_map = generate_image(blocks, blocksize, map_shape, hour_of_day, flood_progress, snow_progress)

            plt.clf()
            plt.subplot(1, 2, 1)
            plt.imshow(canopy_map.astype(np.uint8))
            plt.title(f"Canopy Map - Day:{day+1:02d}, Time: {hour_of_day:02d}:00")
            plt.axis("off")

        #Subplotting the thermal map
        plt.subplot(1, 2, 2)
        plt.imshow(thermal_map, cmap="jet", vmin=0, vmax=100)
        plt.title(f"Thermal Map - Day:{day+1:02d}, Time: {hour_of_day:02d}:00")
        plt.colorbar(label="Temperature (°C)")
        plt.axis("off")

        plt.pause(0.1)
        print(f"Timestep {hour_of_day:02d}:00, {'Snow' if snow else 'Flood'} Progress: {snow_progress if snow else flood_progress:.2f}")

        #Calculating the real temperature based on the time of the day
        real_temp = 30 + 10 * sin((2 * pi / 24) * (hour_of_day - 6))  # base real temp
        flood_cooling = 10 * flood_progress
        snow_cooling = 50 * snow_progress

        #Adjusting real temperature based on flooding and snowing
        if snow:
            real_temp -= snow_cooling
            temperature_drop = 30 * snow_progress  # Adjust temperature drop based on snow progress
            simulate_snow(blocks, snow_intensity, temperature_drop)
        elif flood:
            real_temp -= flood_cooling

        #Calculating the average given temperature and storing real and given temperatures
        depicted_temp = np.mean(thermal_map)
        real_temperatures.append(real_temp)
        depicted_temperatures.append(depicted_temp)
        print(f"Timestep {hour_of_day:02d}:00, Real Temp: {real_temp:.2f}, Depicted Temp: {depicted_temp:.2f}")
        
        #Storing temperature history of blocks
        for block_type, temps in block_temperatures.items():
            block_temp_history[block_type].append(np.mean(temps))

        #Storing temperature history of items
        for item_type, temps in item_temperatures.items():
            item_temp_history[item_type].append(np.mean(temps))
    
    plt.close()
    return real_temperatures, depicted_temperatures, block_temp_history, item_temp_history

def plot_results(real_temperatures, depicted_temperatures, block_temp_history, item_temp_history):

    # Plot real vs depicted temperature
    plt.figure()
    plt.plot(real_temperatures, label="Real Temperature", color="blue")
    plt.plot(depicted_temperatures, label="Depicted Temperature", color="red", linestyle="--")
    plt.title("Real vs Depicted Temperature Over Time")
    plt.xlabel("Time (hours)")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Plot block temperatures
    plt.figure()
    for block_type, temps in block_temp_history.items():
        plt.plot(temps, label=f"{block_type} Temperature")
    plt.title("Block Types Temperature Over Time")
    plt.xlabel("Time (hours)")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Plot item temperatures
    plt.figure()
    for item_type, temps in item_temp_history.items():
        plt.plot(temps, label=f"{item_type} Temperature")
    plt.title("Item Types Temperature Over Time")
    plt.xlabel("Time (hours)")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Plot average temperatures bar chart
    avg_block_temps = {block_type: np.mean(temps) for block_type, temps in block_temp_history.items()}
    avg_item_temps = {item_type: np.mean(temps) for item_type, temps in item_temp_history.items()}
    all_temps = {**avg_block_temps, **avg_item_temps}
    sorted_temps = sorted(all_temps.items(), key=lambda x: x[1])
    names, temperatures = zip(*sorted_temps)
    colors = plt.cm.coolwarm(np.linspace(0, 1, len(names)))
    plt.figure(figsize=(12, 6))
    plt.bar(names, temperatures, color=colors)
    plt.title("Average Temperature of Blocks and Items")
    plt.xlabel("Block/Item Type")
    plt.ylabel("Temperature (°C)")
    plt.ylim(min(temperatures) - 5, max(temperatures) + 5)
    plt.tight_layout()
    plt.show()

#Gives configuration for each scenerio 
def get_scenario_config(scenario):
    if scenario == 'snow':
        return {
            'blocksize': 25,
            'rows': 10,
            'cols': 10,
            'num_days': 2,
            'add_forests': True,
            'add_parks': True,
            'flood': False,
            'stop_rain': 0,
            'snow': True
        }
    elif scenario == 'rain':
        return {
            'blocksize': 25,
            'rows': 10,
            'cols': 10,
            'num_days': 2,
            'add_forests': True,
            'add_parks': True,
            'flood': True,
            'stop_rain': 0,
            'snow': False
        }
    elif scenario == 'normal':
        return {
            'blocksize': 25,
            'rows': 10,
            'cols': 10,
            'num_days': 2,
            'add_forests': True,
            'add_parks': True,
            'flood': False,
            'stop_rain':0,
            'snow': False
        }
        
def main():
    
    #Run map with different scenerios called from command line inputs
    parser = argparse.ArgumentParser(description="Run map simulation with different scenarios.")
    parser.add_argument('scenario', nargs='?', choices=['snow', 'rain', 'normal'], help="Specify a scenario (snow or rain or normal map)") 
    args = parser.parse_args()

    #Checks if the scenerio is specified
    if args.scenario:
        config = get_scenario_config(args.scenario)
        if config:
            print(f"Running {args.scenario} scenario with preset configuration.")
            blocksize = config['blocksize']
            rows = config['rows']
            cols = config['cols']
            num_days = config['num_days']
            add_forests = config['add_forests']
            add_parks = config['add_parks']
            flood = config['flood']
            stop_rain = config['stop_rain']
            snow = config['snow']
        else:
            print(f"Unknown scenario: {args.scenario}")
            return
    else:
        #Gets user inputs to run the simulation
        print("Running simulation with user input.")
        blocksize, rows, cols, num_days, add_forests, add_parks, flood, stop_rain, snow = user_inputs()

    #Creates the map with specific parameters
    blocks, map_shape = make_map(blocksize, rows, cols, add_forests, add_parks)
    
    # Runs the simulation
    real_temperatures, depicted_temperatures, block_temp_history, item_temp_history = run_simulation(blocks, map_shape, num_days, flood, stop_rain, snow)

    # Plots the results
    plot_results(real_temperatures, depicted_temperatures, block_temp_history, item_temp_history)

    # Prints a summary table of the item and block given temperature vs real temperature 
    print("\n\nItem Temperatures Table (Real vs Depicted)")
    print(f"{'Hour':<10}{'Type':<20}{'Depicted Temp (°C)':<25}{'Real Temp (°C)':<20}")
    print("-" * 75)
    for hour in range(24):
        #Calculates the real temperature
        real_temp = 30 + 10 * sin((2 * pi / 24) * (hour - 6))
        
        for block_type, temps in block_temp_history.items():
            depicted_temp = temps[hour % len(temps)]
            print(f"{hour:02d}:00      {block_type:<20}{depicted_temp:<25.2f}{real_temp:<20.2f}")
        for item_type, temps in item_temp_history.items():
            depicted_temp = temps[hour % len(temps)]
            print(f"{hour:02d}:00      {item_type:<20}{depicted_temp:<25.2f}{real_temp:<20.2f}")

if __name__ == "__main__":
    main()
