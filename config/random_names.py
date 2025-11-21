import random

# Bez diakritiky pre testovanie
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
    """
    Generuje náhodné slovenské meno + priezvisko bez diakritiky
    s jedinečným sufixom.
    """
    first = random.choice(SLOVAK_FIRST_NAMES)
    last = random.choice(SLOVAK_LAST_NAMES)
    
    # Jedinečný 4-znakový suffix
    import string
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    return f"{first}-{suffix}", f"{last}-{suffix}"