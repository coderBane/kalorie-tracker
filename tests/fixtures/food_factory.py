from factory.base import Factory
from factory.faker import Faker

from app.models.food import NutritionContent


class NutritionContentFactory(Factory): # type: ignore[type-arg]
    class Meta: # pyright: ignore
        model = NutritionContent
    
    carb_g = Faker('pyfloat', min_value=0, max_value=500)
    fat_g = Faker('pyfloat', min_value=0, max_value=500)
    fiber_g = Faker('pyfloat', min_value=0, max_value=500)
    protein_g = Faker('pyfloat', min_value=0, max_value=500)
    calcium_mg = Faker('pyfloat', min_value=0, max_value=500)
    sodium_mg = Faker('pyfloat', min_value=0, max_value=500)
    potassium_mg = Faker('pyfloat', min_value=0, max_value=500)
    iron_mg = Faker('pyfloat', min_value=0, max_value=500)
    zinc_mg = Faker('pyfloat', min_value=0, max_value=500)
    