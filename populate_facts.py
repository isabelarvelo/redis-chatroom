import redis


r = redis.Redis(host='my-redis', port=6379, decode_responses=True)

# Random Assortment of facts I find personally interesting or think are important to know (Sources in README)
fun_facts = [
    "Recycling one aluminum can saves enough energy to power a TV for three hours.",
    "The Amazon rainforest produces 20% of the world's oxygen.",
    "Cashew apple is the fruit that grows on the cashew tree, not the nut itself. It has a juicy and fruity taste. The nuts we know and love are simply the seed of the fruit.",
    "The sun weighs 2,000 million million million million tons.",
    "The shiniest living thing on earth is the Pollia Condensata, an African fruit.",
    "Raccoons have four times more sensory cells in their paws than most mammals. This allows them to 'see' with their hands and get images of the object they touch without even looking at them.",
    "Pandas are pigeon-toed.",
    "The fastest bear is the black bear, which can run 35 miles per hour. That's about as fast as a horse or deer.",
    "An adult giant panda weighs about 200-300 pounds.",
    "The average American eats approximately 222 pounds of meat per year. This does not include seafood.",
    "Plants yield 10 times more protein per acre than meat.",
    "Famous vegetarians include Leonardo da Vinci, Henry Ford, Brad Pitt, Albert Einstein, and Ozzy Osborne.",
    "'Federer' can be typed entirely with the left hand.",
    "The longest tennis match in history took an incredible 11 hours and 5 minutes to complete.",
    "More than half of the world's population consider themselves soccer fans.",
    "A cloud weighs around a million tonnes.", 
    "The world’s oldest cat lived to 38 years and three days old.", 
    "Hippos can’t swim.", 
    "About 30-40% of the food produced in the US is wasted.",
    "The longest anyone has held their breath underwater is over 24.5 minutes.", 
    "In the US alone soil can draw down 250 million metric tons of carbon dioxide–equivalent greenhouse gasses every year", 
    "We could sequester more than 100% of current annual CO2 emissions with a switch to widely available and inexpensive organic management practices, which we term 'regenerative organic agriculture.'"
]


# Add facts to Redis set
for fact in fun_facts:
    r.sadd("facts", fact)
