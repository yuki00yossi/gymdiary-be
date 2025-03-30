from datetime import date
import json
import os

from weight.models import WeightRecord

# --- 栄養素の単位辞書 ---
nutrient_units = {
    "energy": "kcal",
    "protein": "g",
    "fat": "g",
    "carbohydrate": "g",
    "ビタミンA": "μgRAE", "ビタミンD": "μg", "ビタミンE": "mg", "ビタミンK": "μg",
    "ビタミンB1": "mg", "ビタミンB2": "mg", "ナイアシン": "mgNE", "ビタミンB6": "mg",
    "ビタミンB12": "μg", "葉酸": "μg", "パントテン酸": "mg", "ビオチン": "μg", "ビタミンC": "mg",
    "ナトリウム": "g", "カリウム": "mg", "カルシウム": "mg", "マグネシウム": "mg",
    "リン": "mg", "鉄": "mg", "亜鉛": "mg", "銅": "mg", "マンガン": "mg",
    "ヨウ素": "μg", "セレン": "μg", "クロム": "μg", "モリブデン": "μg",
    "コレステロール": "mg", "食物繊維": "g", "食塩相当量": "g"
}


class NutrientRecommendationCalculator:
    """ 推奨栄養素計算クラス """
    def __init__(self, user):
        self.sex = user.sex
        self.birth_date = user.birth_date
        self.height = user.height
        self.activity_level = user.activity_level
        self.weight = WeightRecord.objects.filter(user=user).order_by('-date').first().weight if user.weight else 0
        self.age = user.calculate_age()
        self.age_group = self._get_age_group()

        # JSONファイルからrecommended_intakeを読み込む
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "recommended_intake_complete.json")
        with open(json_path, "r", encoding="utf-8") as f:
            self.recommended_intake = json.load(f)

    def _get_age_group(self) -> str:
        age = self.age
        if 18 <= age <= 29:
            return "18-29"
        elif 30 <= age <= 49:
            return "30-49"
        elif 50 <= age <= 64:
            return "50-64"
        elif 65 <= age <= 74:
            return "65-74"
        elif age >= 75:
            return "75+"
        else:
            raise ValueError("18歳未満は対象外です")

    def get_basal_metabolism(self) -> float:
        if self.sex == 'male':
            bmr = 0.0481 * self.weight + 0.0234 * self.height - 0.0138 * self.age - 0.4235
        else:
            bmr = 0.0481 * self.weight + 0.0234 * self.height - 0.0138 * self.age - 0.9708
        return round(bmr * 1000, 2)

    def get_total_energy(self) -> int:
        return int(self.get_basal_metabolism() * self.activity_level)

    def get_pfc_targets(self) -> dict:
        energy = self.get_total_energy()
        protein = round(self.weight * 1.0, 1)
        fat = round((energy * 0.25) / 9, 1)
        carbohydrate = round((energy * 0.5) / 4, 1)
        return {
            "energy": energy,
            "protein": protein,
            "fat": fat,
            "carbohydrate": carbohydrate
        }

    def get_micronutrient_targets(self) -> dict:
        return self.recommended_intake[self.sex][self.age_group]

    def get_all_targets(self) -> dict:
        return {
            **self.get_pfc_targets(),
            **self.get_micronutrient_targets()
        }

    def get_all_targets_with_units(self) -> dict:
        raw = self.get_all_targets()
        return {
            key: {
                "value": value,
                "unit": nutrient_units.get(key, "")
            }
            for key, value in raw.items()
        }
