from enum import Enum
from datetime import datetime


class CarBrand(str, Enum):
    MERCEDES = "Mercedes-Benz"
    VOLKSWAGEN = "Volkswagen"
    BMW = "BMW"
    AUDI = "Audi"
    TOYOTA = "Toyota"
    FORD = "Ford"
    OPEL = "Opel"
    PEUGEOT = "Peugeot"
    RENAULT = "Renault"
    FIAT = "Fiat"
    HYUNDAI = "Hyundai"
    KIA = "Kia"
    SKODA = "Škoda"
    NISSAN = "Nissan"
    HONDA = "Honda"
    MAZDA = "Mazda"
    CITROEN = "Citroën"
    DACIA = "Dacia"
    LAND_ROVER = "Land Rover"
    VOLVO = "Volvo"
    BYD = "BYD"

CAR_MODELS = {
    CarBrand.MERCEDES: [
        "A-Class", "B-Class", "C-Class", "E-Class", "S-Class", "CLA",
        "GLA", "GLC", "GLE", "ML", "Vito", "Sprinter",
        "EQA", "EQB", "EQC", "EQE", "EQS",
    ],
    CarBrand.VOLKSWAGEN: [
        "Golf 4", "Golf 5", "Golf 6", "Golf 7", "Golf 8", "Passat", "Polo", "Jetta",
        "Tiguan", "Touareg", "Touran", "T-Roc", "e-Golf", "ID.3", "ID.4", "ID.5", "ID.7",
    ],
    CarBrand.BMW: [
        "1 Series", "3 Series", "5 Series", "7 Series", "X1", "X3", "X5", "X6",
        "i3", "i4", "iX", "iX1", "iX3",
    ],
    CarBrand.AUDI: [
        "A1", "A3", "A4", "A5", "A6", "A7", "A8", "Q3", "Q5", "Q7",
        "e-tron", "Q4 e-tron", "Q8 e-tron",
    ],
    CarBrand.TOYOTA: [
        "Yaris", "Auris", "Corolla", "Camry", "Avensis", "C-HR",
        "RAV4", "Land Cruiser", "Hilux", "Prius", "bZ4X",
    ],
    CarBrand.FORD: [
        "Fiesta", "Focus", "Mondeo", "Kuga", "Puma", "EcoSport", "Transit",
        "Mustang Mach-E",
    ],
    CarBrand.OPEL: [
        "Corsa", "Astra", "Insignia", "Mokka", "Grandland", "Zafira",
        "Corsa Electric", "Mokka Electric", "Astra Electric",
    ],
    CarBrand.PEUGEOT: [
        "208", "308", "508", "2008", "3008", "5008",
        "e-208", "e-2008", "e-308", "e-3008",
    ],
    CarBrand.RENAULT: [
        "Clio", "Megane", "Captur", "Kadjar", "Scenic", "Trafic",
        "Zoe", "Megane E-Tech", "Scenic E-Tech",
    ],
    CarBrand.FIAT: [
        "500", "Panda", "Punto", "Tipo", "500X", "Doblò",
        "500e", "600e",
    ],
    CarBrand.HYUNDAI: [
        "i10", "i20", "i30", "Tucson", "Kona", "Santa Fe",
        "Kona Electric", "Ioniq 5", "Ioniq 6",
    ],
    CarBrand.KIA: [
        "Picanto", "Rio", "Ceed", "Sportage", "Sorento", "Stonic",
        "Niro EV", "EV6", "EV9",
    ],
    CarBrand.SKODA: [
        "Fabia", "Octavia", "Superb", "Kodiaq", "Karoq", "Scala",
        "Enyaq",
    ],
    CarBrand.NISSAN: [
        "Micra", "Qashqai", "Juke", "X-Trail", "Navara",
        "Leaf", "Ariya",
    ],
    CarBrand.HONDA: [
        "Civic", "Accord", "CR-V", "HR-V", "Jazz",
        "e",
    ],
    CarBrand.MAZDA: [
        "2", "3", "6", "CX-3", "CX-5", "CX-30",
        "MX-30",
    ],
    CarBrand.CITROEN: [
        "C3", "C4", "C5", "Berlingo",
        "ë-C4",
    ],
    CarBrand.DACIA: [
        "Sandero", "Duster", "Logan", "Lodgy",
        "Spring",
    ],
    CarBrand.LAND_ROVER: [
        "Range Rover", "Range Rover Sport", "Range Rover Evoque",
        "Range Rover Velar", "Discovery", "Discovery Sport", "Defender",
    ],
    CarBrand.VOLVO: [
        "XC40", "XC60", "XC90", "V40", "V60", "S60",
        "XC40 Recharge", "EX30", "EX40", "EC40", "EX90",
    ],
    CarBrand.BYD: [
        "Atto 3", "Dolphin", "Seal", "Sealion 7", "Song Plus", "Yuan Plus", "Seagull",
    ],
}


class Color(str, Enum):
    BLACK = "Black"
    WHITE = "White"
    GRAY = "Gray"
    SILVER = "Silver"
    BLUE = "Blue"
    RED = "Red"


class Transmission(str, Enum):
    AUTOMATIC = "Automatic"
    MANUAL = "Manual"


class FuelType(str, Enum):
    PETROL = "Petrol"
    DIESEL = "Diesel"
    HYBRID = "Hybrid"
    ELECTRIC = "Electric"


class Drivetrain(str, Enum):
    FWD = "FWD (Front Wheel Drive)"
    RWD = "RWD (Rear Wheel Drive)"
    AWD = "AWD (All Wheel Drive)"
    FOUR_WD = "4WD"
    

def get_years():
    current = datetime.now().year
    return list(range(current, 1989, -1))
