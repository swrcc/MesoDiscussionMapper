'''
This python script maps the Mesoscale Discussions and Precipitation Discussions from the 
Weather Prediction Center and Storm Prediction Center. It plots the areas outlined in the
discussions over a map of New York and then adds the current radar. 

INSTRUCTIONS: to run this file, create a folder called "MesoDiscussionMapper" on your desktop and save the MesoDiscussionMappery.py script in 
that folder. Then in the MesoDiscussionMapper folder, create a second folder called "MappingElements". Download and save the following files
in the MappingElements folder:
- SWRCC_Logo_Transparent.png
- NYS Shorline.shp
- NYS Interstates.shp
- NYS Interstates.shp
- NYS_cities.csv (this csv can be edited locally to modify the cities that are included as desired)
- NYS Counties.shp
- US StatesCoastlines.shp
- World Countries.shp
'''

#Utilized python modules
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from shapely.geometry import Polygon
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import ast
import requests
from PIL import Image
import numpy as np
from io import BytesIO
import datetime
from datetime import timedelta
import os

###############################
# LOADING THE MAPPING FILES
###############################

# Retrieve the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths to mapping elements
mapping_elements_dir = os.path.join(script_dir, 'MappingElements')
swrcc_logo_path = os.path.join(mapping_elements_dir, 'SWRCC_Logo_Transparent.png')
nys_border_path = os.path.join(mapping_elements_dir, 'NYS Shorline.shp')
nys_interstates_path = os.path.join(mapping_elements_dir, 'NYS Interstates.shp')
nys_cities_path = os.path.join(mapping_elements_dir, 'NYS_cities.csv')
nys_counties_path = os.path.join(mapping_elements_dir, 'NYS Counties.shp')
us_states_path = os.path.join(mapping_elements_dir, 'US StatesCoastlines.shp')
world_countries_path = os.path.join(mapping_elements_dir, 'World Countries.shp')

# Load the mapping elements
SWRCC_logo = Image.open(swrcc_logo_path)
border = gpd.read_file(nys_border_path)
interstates = gpd.read_file(nys_interstates_path)
interstates2 = gpd.read_file(nys_interstates_path)
cities = pd.read_csv(nys_cities_path)
counties = gpd.read_file(nys_counties_path)
states = gpd.read_file(us_states_path)
countries = gpd.read_file(world_countries_path)


###############################
# GET THE DISCUSSION DATA
###############################

while True: 
    source = input('Are you using a direct link? (y or n): ')
    if source == 'n':
        text = input('Paste the raw coordinates (copy/paste them into browser search bar first to remove automatic formatting): ') 
        break
    elif source == 'y': 
        url = input('Enter Meso Discussion Link: ')
        try:
            # Open the URL and extract the text
            html = urlopen(url).read()
            soup = BeautifulSoup(html, features="html.parser")
            text = soup.get_text()  # Get URL text
            break
        except Exception as e:
            print(f"ERROR: {e}. Please enter a valid URL.")
    else:
        print('ERROR: Invalid input. Enter "y" if using a direct link to the Meso/Precip Discussion; enter "n" if not using a direct link.')
        continue

coords = []
coordinates = []

###############################
# LOADING AND PLOTTING THE SHAPEFILES
###############################

# Plot the shapefiles
fig, ax = plt.subplots(figsize=(10, 10))
interstates2.plot(ax=ax, edgecolor='black', facecolor='none', alpha=1, linewidth=2)
interstates.plot(ax=ax, edgecolor='red', facecolor='none', alpha=0.25, linewidth=1)
countries.plot(ax=ax, edgecolor='white', facecolor='black', alpha=1, linewidth=0.25)
states.plot(ax=ax, edgecolor='white', facecolor='none', alpha=0.5, linewidth=0.25)
counties.plot(ax=ax, edgecolor='white', facecolor='black', alpha=0.5, linewidth=0.50)
border.plot(ax=ax, edgecolor='white', facecolor='none', alpha=1, linewidth=1, zorder=9)
gdf_cities = gpd.GeoDataFrame(cities, geometry=gpd.points_from_xy(cities.Longitude, cities.Latitude)) #geodataframe for csv cities

###############################
# RETREIVING AND PLOTTING THE RADAR
###############################

# Using the current time, generate the radar from the previous 5-minute benchmark
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M') #used in the plot timestamp
minute05 = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 0]
minute04 = [4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59]
minute03 = [3, 8, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58]
minute02 = [2, 7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57]
minute01 = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]
for n in minute05: 
    if datetime.datetime.now().minute == n: 
        changedtime = str(datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=5))
    else: 
        continue
for n in minute04: 
    if datetime.datetime.now().minute == n: 
        changedtime = str(datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=4))
    else: 
        continue
for n in minute03: 
    if datetime.datetime.now().minute == n: 
        changedtime = str(datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=3))
    else: 
        continue
for n in minute02: 
    if datetime.datetime.now().minute == n: 
        changedtime = str(datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=2))
    else: 
        continue
for n in minute01: 
    if datetime.datetime.now().minute == n: 
        changedtime = str(datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=1))
    else: 
        continue
year = changedtime[0:4]
month = changedtime[5:7]
day = changedtime[8:10]
hour = changedtime[11:13]
minute = changedtime[14:16]
radar_time = year+'-'+month+'-'+day+' '+hour+':'+minute
png_url = "https://mesonet.agron.iastate.edu/archive/data/" + year + "/" + month + "/" + day + "/GIS/uscomp/n0q_" + year + month + day + hour + minute + ".png"
wld_url = "https://mesonet.agron.iastate.edu/archive/data/" + year + "/" + month + "/" + day + "/GIS/uscomp/n0q_" + year + month + day + hour + minute + ".wld"

# Download the PNG image
png_response = requests.get(png_url)
png_image = Image.open(BytesIO(png_response.content)).convert('RGBA')

# Download and parse the world file
wld_response = requests.get(wld_url)
wld_content = wld_response.text.strip().split()
wld_values = list(map(float, wld_content))

# Extract georeferencing information from the world file
pixel_size_x = wld_values[0]
rotation_y = wld_values[1]
rotation_x = wld_values[2]
pixel_size_y = wld_values[3]
upper_left_x = wld_values[4]
upper_left_y = wld_values[5]

# Compute the extent of the image
width, height = png_image.size
extent = [
    upper_left_x,
    upper_left_x + width * pixel_size_x,
    upper_left_y + height * pixel_size_y,
    upper_left_y]

#Give the radar image a transparent background
data = np.array(png_image)
alpha = np.where((data[:, :, 0] == 0) & (data[:, :, 1] == 0) & (data[:, :, 2] == 0), 0, 255) # Create a mask from RGB pixel values at a threshold (0,0,0 = black)
data[:, :, 3] = alpha
# Create a new image with the transparent background
new_image = Image.fromarray(data, 'RGBA')
# Plot the radar
ax.imshow(np.asarray(new_image), extent=extent, origin='upper', zorder=9, alpha = 0.75)

###############################
# EXTRACT POLYGON COORDINATES AND PLOT POLYGON WITH CITIES
###############################

#extract 8-digit numbers from discussion (lat/lon) 
pattern = r'\b\d{8}\b'
matches = re.findall(pattern, text)
matches_tuple = tuple(matches)

for n in matches:
    coords.append("("+n[0:2]+'.'+n[2:4]+',-'+n[4:6]+'.'+n[6:]+")")
coords.append("("+matches[-1][0:2]+'.'+matches[-1][2:4]+',-'+matches[-1][4:6]+'.'+matches[-1][6:]+")")
for z in coords:
    coordinates.append(ast.literal_eval(z))
    
# Create a Polygon from the Mesoscale Discussion coordinates then Create a GeoDataFrame with the polygon
polygon = Polygon([(lat, lon) for lon, lat in coordinates])
polygon_gdf = gpd.GeoDataFrame(index=[0], geometry=[polygon], crs="EPSG:4326")
polygon_gdf2 = gpd.GeoDataFrame(index=[0], geometry=[polygon], crs="EPSG:4326")

# Plot the polygon on top of the shapefiles and radar
polygon_gdf.plot(ax=ax, edgecolor='yellow', facecolor='yellow', alpha=0.25, linewidth=2, zorder=10)
polygon_gdf2.plot(ax=ax, edgecolor='yellow', facecolor='none', alpha=1, linewidth=3, zorder=10)
# Plot cities and annotate city names
gdf_cities.plot(ax=ax, color='white', edgecolor="black", markersize=30, zorder=10)
for x, y, label in zip(gdf_cities.geometry.x, gdf_cities.geometry.y, gdf_cities['City']):
    text = ax.text(x, y-0.15, label, color='white', fontsize=8, fontweight="normal", horizontalalignment='center', verticalalignment ="center", rotation=0, zorder=10)
    # Apply buffer color path effects
    text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


###############################
# SWRCC LOGO
###############################

#overlay the SWRCC logo
logo = SWRCC_logo.resize((300, 300))
logo_width, logo_height = logo.size
# Define the position to overlay the logo (bottom-right corner)
map_width, map_height = plt.gcf().get_size_inches()*plt.gcf().dpi
x_pos = 250  # 10 pixels from the right edge
y_pos = 1160  # 10 pixels from the bottom edge
# Convert the logo image to an array and overlay it on the map
logo_array = np.array(logo)
# Add the logo to the plot
plt.figimage(logo_array, x_pos, y_pos, zorder=10)

###############################
# GENERATE INFO BOXES
###############################

# Get the current time
current_time = datetime.datetime.now().strftime("%I:%M %p %B %d,%Y")

# Add a text box with the timestamp
ax.text(
    x=0.01, y=0.02,  # Position (relative coordinates, adjusted for margins)
    s=f'Map generated at: {current_time}',  
    fontsize=8,  alpha=0.7, color="white",
    bbox=dict(facecolor='black', alpha=0.5, edgecolor='black'),  # Bounding box properties
    transform=ax.transAxes,  # Use axes coordinate system
    zorder=10
)

###############################
# EXTRACT THE VALID TIME TO PLOT ON MAP
###############################

if source == 'y':
    # Find all occurrences of the valid time using a regular expression
    pattern = re.findall(r'\d{6}Z', soup.get_text())

    # Finding the <pre> section in the HTML
    pre_section = soup.find('pre')
    if pre_section:
        # Extracting the text from the <pre> section
        pre_text = pre_section.get_text()
        # Splitting the text into lines
        lines = pre_text.split('\n')
        # Removing blank lines
        non_blank_lines = [line for line in lines if line.strip()]

        # Extracting the fourth line
        if len(non_blank_lines) >= 4:
            third_line = non_blank_lines[2]
            date = third_line[-11:]

            # Converting the date string to a datetime object
            new_date = datetime.datetime.strptime(date, '%b %d %Y')
            
            timestamp = []
            for valid_time in pattern:
                try:
                    # Extracting day, hour, and minute from valid_time
                    day = int(valid_time[:2])
                    hour = int(valid_time[2:4])
                    minute = int(valid_time[4:6])
                    # Creating a datetime object
                    datetime_object = datetime.datetime(new_date.year, new_date.month, day, hour, minute) - timedelta(hours=4)
                    timestamp.append(datetime_object.strftime("%I:%M %p %B %d"))
                    
                except ValueError as e:
                    print(f"Error parsing valid_time '{valid_time}': {e}")
        else:
            print("Not enough lines in the <pre> section to extract the fourth line.")
    else:
        print("No <pre> section found in the HTML.")
    #print('Graphic valid from:', timestamp[0], 'to', timestamp[1])
    s=f'Valid from {timestamp[0]} to {timestamp[1]}'
else: 
    s='VALID TIME NOT ACCESSIBLE - Please use direct link'
    
ax.text(
    x = 0.24, y = 0.96, # Position (relative coordinates, adjusted for margins)
    s=s, 
    fontsize=12,  alpha=1, color="white",
    bbox=dict(facecolor='black', alpha=0.7, edgecolor='black'),  # Bounding box properties
    transform=ax.transAxes,  # Use axes coordinate system
    zorder=10,
)
    
###############################
# CREATE THE PLOT
###############################

# Customize the plot
ax.set_facecolor('#001177')
plt.title("Discussion Focus Area", fontsize=20)
ax.set_xticks([])
ax.set_yticks([])
#Entire State
plt.xlim(-80.3,-71.8)
plt.ylim(40.3,45.4)
#New York City
#plt.xlim(-75,-72)
#plt.ylim(40,42)
# Show the plot
plt.show()
