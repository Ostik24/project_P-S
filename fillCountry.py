import pandas as pd
from geopy.geocoders import Nominatim
import pycountry_convert as pc

df = pd.read_csv('dataset/earthquake_1995-2023.csv')

# Initialize the geocoder
geolocator = Nominatim(user_agent="geoapi")

# Store previously looked-up coordinates
country_cache = {}

# Function to get the country based on latitude and longitude
def get_country(lat, lon):
    if pd.isnull(lat) or pd.isnull(lon):
        return None
    coord_key = (lat, lon)
    if coord_key in country_cache:
        return country_cache[coord_key]
    
    # Define bounding box offsets
    delta = 0.4
    bounding_box = [
        (lat + delta, lon - delta),  # Top-left
        (lat + delta, lon + delta),  # Top-right
        (lat - delta, lon - delta),  # Bottom-left
        (lat - delta, lon + delta),  # Bottom-right
    ]

    try:
        for point in bounding_box:
            location = geolocator.reverse(point, language='en')
            if location and 'country' in location.raw.get('address', {}):
                country = location.raw['address']['country']
                country_cache[coord_key] = country
                print(country)
                return country

        country_cache[coord_key] = 'ocean'
        return 'ocean'
    except Exception as e:
        print(f"Error at coordinates ({lat}, {lon}): {e}")
        return None

# Fill missing country values (update only if 'country' is NA)
df['country'] = df.apply(
    lambda row: get_country(row['latitude'], row['longitude']) if pd.isnull(row['country']) else row['country'],
    axis=1
)
df.to_csv('./dataset/earthquake_1995-2023-country.csv', index=False)
print("Country column updated successfully!")
continent_cache = {}

# Function to convert country to continent
def get_continent_from_country(country):
    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country)
        continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        return continent_code
    except KeyError:
        return 'Unknown'

# Function to get continent based on latitude and longitude (with square check)
def get_continent(country):
    if pd.isnull(country):
        return None
    if country in continent_cache:
        return continent_cache[country]

    try:
        continent = get_continent_from_country(country)
        return continent
    except Exception as e:
        print(f"Error at coordinates ({country}): {e}")
        return 'ocean'

# Update the continent column
df['continent'] = df.apply(
    lambda row: get_continent(row['country']) if pd.isnull(row['continent']) else row['continent'],
    axis=1
)

# # Save the updated dataset
df.to_csv('./dataset/earthquake_1995-2023-country.csv', index=False)
df = pd.read_csv('./dataset/earthquake_1995-2023-country.csv')
print("Continent column updated successfully!")
# Count the number of NA values in the 'continent' column
na_count_continent = df['country'].isna().sum()

print(f"Number of NA values in the 'continent' column: {na_count_continent}")
