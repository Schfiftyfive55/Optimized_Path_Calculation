import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import requests
import json



# A dictionary to store cached distance values
distance_cache = {}

def driving_distance(lat1, lon1, lat2, lon2):
    # Check if the distance value has already been cached
    if (lat1, lon1, lat2, lon2) in distance_cache:
        return distance_cache[(lat1, lon1, lat2, lon2)]
    elif (lat2, lon2, lat1, lon1) in distance_cache:
        return distance_cache[(lat2, lon2, lat1, lon1)]

    # If the distance value is not in the cache, make an API call to get it
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    response = requests.get(url)
    data = json.loads(response.text)

    if data["code"] == "Ok":
        distance = data["routes"][0]["distance"] / 1000  # convert meters to kilometers
        print("Ongoing")
        # Add the distance value to the cache
        distance_cache[(lat1, lon1, lat2, lon2)] = distance
        return distance
    else:
        return None

# Read the site information from a CSV file
sites_df = pd.read_csv("template.csv", usecols=['latitude', 'longitude', 'site','order'])



# Filter out rows with null order values
non_null_order = sites_df[sites_df['order'].notnull()]
# Check for duplicate order values in non-null entries
if non_null_order['order'].duplicated().any():
    raise ValueError('Multiple non-null sites have the same order value in the CSV file.')



# Create arrays of latitude and longitude values
latitudes = sites_df['latitude'].values
longitudes = sites_df['longitude'].values

# Use meshgrid to create arrays of all pairs of latitude and longitude values
lat1, lat2 = np.meshgrid(latitudes, latitudes)
lon1, lon2 = np.meshgrid(longitudes, longitudes)

# Use the driving_distance function to calculate all distances at once
distances = np.vectorize(driving_distance)(lat1, lon1, lat2, lon2)

# Convert the distance matrix to a DataFrame and add site names as column and index labels
distances_df = pd.DataFrame(distances, columns=sites_df['site'], index=sites_df['site'])
print(distances_df)


def knn(distances, sites_df):
    # Number of cities
    n = len(distances)
    
    # Find the starting city index
    if 'starting_point' in sites_df.columns:
        start_city_index = sites_df[sites_df['starting_point'] == 1].index[0]
    elif 'order' in sites_df.columns:
        start_city_index = sites_df.sort_values(by='order').index[0]
    else:
        # Choose a random starting city index if none is provided
        print('No Starting_Point specified, choosing random starting point')
        start_city_index = np.random.randint(0, n)
    
    # Initialize list of visited cities with starting city
    visited_cities = [start_city_index]
    
    # Initialize total distance traveled
    total_distance = 0
    
    # Determine the order in which to visit the sites
    if 'order' in sites_df.columns:
        ordered_sites = sites_df.sort_values(by='order')
        ordered_sites = ordered_sites[ordered_sites.index != start_city_index]
        ordered_sites = list(ordered_sites.index)
    else:
        ordered_sites = []
    
    # Repeat until all cities have been visited
    while len(visited_cities) < n:
        # Index of the last visited city
        current_city = visited_cities[-1]
        
        # Calculate distances from current city to all other cities that haven't been visited
        distances_to_unvisited_cities = [distances[current_city][i] for i in range(n) if i not in visited_cities]
        
        # Find the indices of the three nearest neighbors among unvisited cities
        nearest_neighbors = np.argsort(distances_to_unvisited_cities)[:3]
        
        # If there are still ordered sites to visit, choose the first ordered site among the three nearest neighbors
        if ordered_sites:
            next_city = ordered_sites[0]
        else:
            # Choose the first unvisited city among the three nearest neighbors
            next_city = [i for i in range(n) if i not in visited_cities][nearest_neighbors[0]]
        
        # Add the next city to the list of visited cities
        visited_cities.append(next_city)
        if next_city in ordered_sites:
            ordered_sites.remove(next_city)
        
        # Add the distance from the current city to the next city to the total distance
        total_distance += distances[current_city][next_city]
    
    # Add the distance from the last visited city back to the starting city to the total distance
    total_distance += distances[visited_cities[-1]][visited_cities[0]]
    
    return visited_cities, total_distance


# Find the optimized path
best_path, best_distance = knn(distances, sites_df)
    
best_distance = sum(distances_df.iloc[best_path[i], best_path[i+1]] for i in range(len(best_path)-1))
print(best_path)
# Create a new DataFrame with the sites ordered by the optimized path
ordered_sites = pd.DataFrame([sites_df.iloc[site_id] for site_id in best_path])
ordered_sites["order"] = range(1, len(ordered_sites) + 1)

# Sort the ordered_sites dataframe by the order column
ordered_sites = ordered_sites.sort_values(by="order")

# Reset the index to start from 1
ordered_sites = ordered_sites.reset_index(drop=True)
ordered_sites.index += 1

n = len(ordered_sites)
ordered_sites.loc[:, "order"] = range(1, n+1)
ordered_sites = ordered_sites.set_index("order")

# Visualize the optimized path matrix
sns.heatmap(distances_df.loc[ordered_sites["site"], ordered_sites["site"]], cmap="coolwarm", annot=True, fmt=".1f")
#plt.show()

# Print the ordered list of sites and the total distance
print("Optimized path:")
print(ordered_sites)
print("Total distance:", best_distance)
ordered_sites.to_csv('ordered_sites.csv', index=True)

# Define map center as the first site in ordered_sites dataframe
map_center = (ordered_sites.iloc[0]['latitude'], ordered_sites.iloc[0]['longitude'])

# Create map object
my_map = folium.Map(location=map_center, zoom_start=10)

# Define a function to get the route coordinates from OSRM API
def get_route(start, end):
    coords_str = f"{start[1]},{start[0]};{end[1]},{end[0]}"
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?steps=false&geometries=geojson"
    response = requests.get(url)
    route_data = json.loads(response.content)
    return route_data['routes'][0]['geometry']['coordinates']

# Get the optimized path coordinates from OSRM API and add them to the map
route_coords = []
for i in range(len(ordered_sites) - 1):
    start = (ordered_sites.iloc[i]['latitude'], ordered_sites.iloc[i]['longitude'])
    end = (ordered_sites.iloc[i+1]['latitude'], ordered_sites.iloc[i+1]['longitude'])
    route_coords.extend(get_route(start, end))
   
    
route_coords = [[coord[1], coord[0]] for coord in route_coords]

# Add markers for each site
for i, site in ordered_sites.iterrows(): 
    folium.Marker(location=[site['latitude'], site['longitude']], tooltip=site['site']).add_to(my_map)
    
folium.PolyLine(locations=route_coords, color='red').add_to(my_map)

# display map
my_map.save('optimized_path.html')
