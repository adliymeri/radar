from enum import Enum
from datetime import datetime


class CarBrand(str, Enum):
    TOYOTA = "Toyota"
    BMW = "BMW"
    MERCEDES = "Mercedes-Benz"
    AUDI = "Audi"


CAR_MODELS = {
    CarBrand.TOYOTA: ["Camry", "Corolla", "RAV4"],
    CarBrand.BMW: ["3 Series", "5 Series", "X5"],
    CarBrand.MERCEDES: ["C-Class", "E-Class", "GLE"],
    CarBrand.AUDI: ["A4", "A6", "Q5"],
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
