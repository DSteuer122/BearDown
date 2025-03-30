import random
import string
from datetime import datetime

# Names
# • Address: Including street address, city, county, precinct, and ZIP code done Look at state !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# • Birthdate done
# • Ages over 89: These must be aggregated into a single category of 90 or older.
# • Telephone Numbers done
# • Email Addresses not done
# • Social Security Numbers (SSN) done
# • Medical Record Numbers (MRN) done
# • Account Numbers done

# List of fake first and last names to choose from
first_names = [
    "Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Henry", "Isla", "Jack",
    "Katherine", "Liam", "Mia", "Noah", "Olivia", "Patrick", "Quinn", "Ryan", "Sophia", "Thomas",
    "Ursula", "Victor", "Willow", "Xavier", "Yasmine", "Zachary", "Aaron", "Bella", "Caleb", "Diana",
    "Ethan", "Fiona", "Gabriel", "Hannah", "Isaac", "Julia", "Kevin", "Laura", "Mason", "Natalie",
    "Oscar", "Penelope", "Quentin", "Rebecca", "Samuel", "Tessa", "Ulysses", "Vanessa", "Wyatt", "Xena",
    "Yvette", "Zane", "Amber", "Blake", "Catherine", "Derek", "Eleanor", "Felix", "Georgia", "Harvey",
    "Ivy", "James", "Kylie", "Leo", "Madeline", "Nathan", "Ophelia", "Peter", "Quincy", "Rose",
    "Sebastian", "Tiffany", "Uriel", "Vivian", "Walter", "Xander", "Yvonne", "Zeke", "Asher", "Beatrice",
    "Cole", "Delilah", "Emmanuel", "Faith", "Gideon", "Hope", "Ian", "Jasmine", "Killian", "Lydia",
    "Miles", "Naomi", "Omar", "Paige", "Rafael", "Selena", "Tobias", "Una", "Vance", "Wendy",
    "Xiomara", "Yosef", "Zara", "Adrian", "Brenda", "Cyrus", "Daisy", "Elliot", "Freya", "Gregory",
    "Hazel", "Imogen", "Jared", "Kayla", "Landon", "Melody", "Nolan", "Orion", "Piper", "Riley",
    "Stella", "Tristan", "Umar", "Valerie", "Weston", "Ximena", "Yahir", "Zion", "Ariana", "Brayden",
    "Carmen", "Declan", "Evelyn", "Francis", "Gianna", "Hudson", "Isabelle", "Jonah", "Kendra", "Lillian"
]

last_names = [
    "Johnson", "Williams", "Taylor", "Brown", "Miller", "Davis", "Wilson", "Moore", "Anderson", "Thomas",
    "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez",
    "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez",
    "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter", "Mitchell", "Perez",
    "Roberts", "Campbell", "Edwards", "Stewart", "Flores", "Morris", "Nguyen", "Murphy", "Rivera", "Cook",
    "Rogers", "Morgan", "Peterson", "Cooper", "Reed", "Bailey", "Bell", "Gomez", "Kelly", "Howard",
    "Ward", "Cox", "Diaz", "Richardson", "Wood", "Watson", "Brooks", "Bennett", "Gray", "James",
    "Reyes", "Cruz", "Hughes", "Price", "Myers", "Long", "Foster", "Sanders", "Ross", "Morales",
    "Powell", "Sullivan", "Russell", "Ortiz", "Jenkins", "Gutierrez", "Perry", "Butler", "Barnes", "Fisher",
    "Henderson", "Coleman", "Simmons", "Patterson", "Jordan", "Reynolds", "Hamilton", "Graham", "Kim", "Gonzales",
    "Alexander", "Ramos", "Wallace", "Griffin", "West", "Cole", "Hayes", "Chavez", "Gibson", "Bryant",
    "Ellis", "Stevens", "Murray", "Ford", "Marshall", "Owens", "McDonald", "Harrison", "Ruiz", "Kennedy",
    "Wells", "Alvarez", "Woods", "Mendoza", "Castillo", "Olson", "Webb", "Washington", "Tucker", "Freeman",
    "Burns", "Henry", "Vasquez", "Snyder", "Simpson", "Crawford", "Jimenez", "Porter", "Mason", "Shaw"
]

# Sample data for each component
street_names = ["Main", "Oak", "Pine", "Maple", "Cedar", "Elm", "Willow", "Sunset", "Ridge", "Lakeview"]
street_types = ["St", "Ave", "Blvd", "Dr", "Ln", "Rd", "Ct"]
cities = ["Springfield", "Riverside", "Fairview", "Madison", "Franklin", "Greenville", "Bristol", "Centerville"]
counties = ["Jefferson", "Washington", "Franklin", "Madison", "Lincoln", "Hamilton", "Monroe", "Jackson"]
precincts = ["North", "South", "East", "West", "Central", "Downtown", "Suburban", "Industrial"]
zip_codes = [f"{random.randint(10000, 99999)}" for _ in range(50)]  # Generate 50 random ZIP codes

# Set to keep track of assigned fake names (ensures uniqueness)
used_fake_names = set()

def generate_unique_fake_name():
    """Generates a non-overlapping fake name"""
    while True:
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        fake_name = fname + " " + lname
        if fake_name not in used_fake_names:
            used_fake_names.add(fake_name)
            return lname, fname



def calculate_age(year, month, day):
    today = datetime.today()
    birth_date = datetime(year, month, day)
    
    age = today.year - birth_date.year
    
    # Adjust if the birthday hasn't happened yet this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age

def generate_fake_birthday(original_birthday):
    """Generates a fake birthday, keep the year"""
    if original_birthday == "":
        return 2000+random.randint(1, 12)+random.randint(1,28)
    year = original_birthday[:4]
    if calculate_age(int(original_birthday[:4]),int(original_birthday[4:6]),int(original_birthday[6:8])) >= 90:
        year = "1935"
    month = random.randint(1, 12)
    day = random.randint(1,28)
    month = f"{month:02}"
    day = f"{day:02}"
    birthday = year+month+day
    return birthday

used_fake_phone_numbers = set()

def generate_phone_number():
    """Generates a non-overlapping fake name"""
    while True:
        fake_number = str(random.randint(100,999))+"-"+str(random.randint(100,999))+"-"+str(random.randint(1000,9999))
        if fake_number not in used_fake_phone_numbers:
            used_fake_names.add(fake_number)
            return fake_number

used_fake_email = set()

def generate_email():
    """Generates a non-overlapping fake name"""
    while True:
        fake_number = str(random.randint(100,999))+"-"+str(random.randint(100,999))+"-"+str(random.randint(1000,9999))
        if fake_number not in used_fake_phone_numbers:
            used_fake_names.add(fake_number)
            return fake_number

def generate_SSN():
    """Generate random SSN"""
    SSN = str(random.randint(100,999))+"-"+str(random.randint(10,99))+"-"+str(random.randint(1000,9999))
    return SSN

def generate_MRN():
    """generate fake MRN"""
    letter = chr(random.randint(65, 90))
    MRN = letter+str(random.randint(1000,9999999))
    return MRN
    
def generate_account_number():
    """generate fake account number"""
    letter = chr(random.randint(65, 90))
    AccountNumber = letter+str(random.randint(100000000,9999999999))
    return AccountNumber

# Function to generate a random address
def generate_random_address(state):
    street_number = random.randint(100, 9999)  # House/building number
    street = f"{random.choice(street_names)} {random.choice(street_types)}"
    city = random.choice(cities)
    county = random.choice(counties) + " County"
    precinct = random.choice(precincts) + " Precinct"
    zip_code = random.choice(zip_codes)

    return f"{street_number} {street}, {city}, {county}, {precinct}, {state} ,{zip_code}"
