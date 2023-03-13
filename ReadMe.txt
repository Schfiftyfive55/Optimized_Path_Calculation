- Site Optimization -
This script calculates the optimized path to visit a set of sites based on driving distance between them. The script uses the OSRM API to obtain driving distance information between each pair of sites and then applies the K-nearest neighbors (KNN) algorithm to find the optimized path.

- Requirements - 
This script requires the following packages to be installed
numpy
pandas
seaborn
matplotlib
itertools
folium
requests
json

Use pip install -r requirements.txt

- Input data -

The script reads a CSV file named CHWsites.csv that contains the latitude and longitude coordinates of each CHW site. The CSV file must contain the following columns:

Latitude: the latitude coordinate of the site
Longitude: the longitude coordinate of the site
Site: a name or identifier for the site
Order: the order in which the site should be visited in the optimized path. 
This column is optional and can be left blank. If it is not provided, the script will assign a default order based on the order in which the sites appear in the CSV file. If it is provided, the script will use the order specified in the column.

If there are any duplicate order values in the CSV file, the script will raise a ValueError and stop execution. 
To avoid this, ensure that each order value is unique and that there are no missing or null values. 
If the order column is not provided or contains missing or null values, the script will assign a default order based on the order in which the sites appear in the CSV file.

Recommendation: It is recommended to always set at least one starting point in the input CSV file by adding a value of 1 to the order column for the site that you want to be the starting point.

- Output data -
The script outputs the following :

A heatmap showing the optimized path matrix
A CSV file named ordered_sites.csv containing the ordered list of sites with their coordinates and order in the optimized path
A folium map showing the optimized path
How to run the script
To run the script, follow these steps

Place the template.csv file in the same directory as the script.
Install the required packages if not already installed.
Open a terminal or command prompt and navigate to the directory where the script and input file are located.
Type python main_KNN.py and press Enter.
The script will then perform the following steps

Read the site information from the CSV file.
Calculate the driving distance between each pair of sites using the OSRM API.
Apply the KNN algorithm to find the optimized path.
Generate a heatmap showing the optimized path matrix.
Generate a CSV file containing the ordered list of sites with their coordinates and order in the optimized path.
Generate a folium map showing the optimized path.

- Additional informations : - 
Note : Depending on the number of sites and the network speed, the API calls may take some time to complete.
For example, if there are 100 sites that need to request data from an API, and each site needs to make 100 requests, then there will be a total of 10,000 requests made. 
However, this can be improved by using another API that allows for bulk requests, which can greatly reduce the number of requests needed. 
Furthermore, it is worth noting that this code has been crafted to ensure ease of use and comes at no cost to the user. 
However, it is advised that the driving distance function be replaced with a paid API in the event of more than 100 sites being used.
