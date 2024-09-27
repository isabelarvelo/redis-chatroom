import random 
import redis 

r = redis.Redis(host='my-redis', port=6379, db=0)

# List of randomly selected cities to generate weather data for
cities = [
    "new york", "los angeles", "chicago", "milwaukee", "atlanta", "nashville", 
    "houston", "phoenix", "philadelphia","miami", "denver", "boston", 
    "san antonio", "san diego", "dallas", "san jose", "austin", 
    "san francisco", "charlotte", "indianapolis",
    "seattle", "denver", "washington", "boston",
    "las vegas", "portland", "memphis",  "baltimore",
    "minneapolis", "tulsa", "arlington", "tampa", "new orleans", 
    "tokyo", "delhi", "shanghai", "sao paulo", "mexico city", "cairo",
    "mumbai", "beijing", "madrid", "paris", "london", "berlin", "rome", 
    "florence", "venice", "barcelona", "lisbon", "athens", "budapest"
]

# Weather conditions
conditions = ["Sunny", "Humid", "Partly Cloudy", "Cloudy", "Rainy", "Thunderstorms", "Windy", "Foggy", "Clear"]

# Generating random temperatures for synthetic data 
def random_temp():
    return random.randint(40, 80)  

# Storing fake weather data
for city in cities:
    condition = random.choice(conditions)
    temp = random_temp()
    weather = f"{condition}, {temp}°F"
    r.hset("weather", city, weather)
