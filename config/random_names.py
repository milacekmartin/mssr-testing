import random

SLOVAK_FIRST_NAMES = [
    "Adam", "Alex", "Daniel", "David", "Jakub", 
    "Jan", "Lukas", "Martin", "Matej", "Michal",
    "Oliver", "Peter", "Richard", "Samuel", "Tomas",
    "Viktor", "Sebastian", "Dominik", "Marek", "Tobias"
]

SLOVAK_LAST_NAMES = [
    "Novak", "Svoboda", "Novotny", "Dvorak", "Cerny",
    "Prochazka", "Krejci", "Horak", "Nemec", "Pokorny",
    "Pospisil", "Havel", "Kral", "Blazek", "Rosa",
    "Benes", "Fiala", "Sedlacek", "Dobes", "Zeman"
]

def generate_random_name():
    first = random.choice(SLOVAK_FIRST_NAMES)
    last = random.choice(SLOVAK_LAST_NAMES)
    
    import string
    
    random_word_length = random.randint(4, 8)
    first_letter = random.choice(string.ascii_uppercase)
    remaining_letters = ''.join(random.choices(string.ascii_lowercase, k=random_word_length-1))
    random_word = first_letter + remaining_letters
    
    return f"{first}", f"{last} {random_word}"
