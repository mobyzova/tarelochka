import json
import os

class UserProfile:
    def __init__(self):
        self.profile_file = "user_profile.json"
        self.default_profile = {
            "personal": {
                "пол": "мужской",
                "возраст": 25,
                "рост": 170,
                "вес": 70,
                "уровень_активности": "умеренная",
                "цель": "поддержание",
                "целевой_вес": 70,
                "соотношение_бжу": {"углеводы": 40, "белки": 30, "жиры": 30}
            },
            "ограничения": {
                "тип_питания": "стандартное",
                "медицинские_показания": []
            },
            "предпочтения": {
                "сложность_рецептов": "легкая",
                "доступность_ингредиентов": "обычные"
            },
            "рассчитанные_метрики": {
                "основной_обмен": 0,
                "суточная_потребность": 0,
                "дневные_калории": 0,
                "дневные_белки": 0,
                "дневные_углеводы": 0,
                "дневные_жиры": 0
            }
        }
        self.profile = self.load_profile()
        self.calculate_metrics()

    def load_profile(self):
        try:
            if os.path.exists(self.profile_file):
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    return self.merge_profiles(self.default_profile, profile)
            return self.default_profile.copy()
        except Exception:
            return self.default_profile.copy()

    def merge_profiles(self, default, current):
        merged = default.copy()
        for key, value in current.items():
            if key in merged:
                if isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = self.merge_profiles(merged[key], value)
                else:
                    merged[key] = value
        return merged

    def save_profile(self):
        try:
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(self.profile, f, indent=2, ensure_ascii=False)
            self.calculate_metrics()
            return True
        except Exception as e:
            print(f"Ошибка сохранения профиля: {e}")
            return False

    def calculate_metrics(self):
        personal = self.profile["personal"]

        if personal["пол"] == "мужской":
            bmr = 10 * personal["вес"] + 6.25 * personal["рост"] - 5 * personal["возраст"] + 5
        else:
            bmr = 10 * personal["вес"] + 6.25 * personal["рост"] - 5 * personal["возраст"] - 161

        activity_multipliers = {
            "сидячий": 1.2,
            "легкая": 1.375,
            "умеренная": 1.55,
            "высокая": 1.725,
            "очень высокая": 1.9
        }

        tdee = bmr * activity_multipliers.get(personal["уровень_активности"], 1.55)

        goal_adjustments = {
            "похудение": -500,
            "поддержание": 0,
            "набор массы": 300,
            "здоровое питание": -200
        }

        daily_calories = tdee + goal_adjustments.get(personal["цель"], 0)

        ratio = personal["соотношение_бжу"]
        daily_protein = (daily_calories * ratio["белки"] / 100) / 4
        daily_carbs = (daily_calories * ratio["углеводы"] / 100) / 4
        daily_fat = (daily_calories * ratio["жиры"] / 100) / 9

        self.profile["рассчитанные_метрики"] = {
            "основной_обмен": round(bmr),
            "суточная_потребность": round(tdee),
            "дневные_калории": round(daily_calories),
            "дневные_белки": round(daily_protein),
            "дневные_углеводы": round(daily_carbs),
            "дневные_жиры": round(daily_fat)
        }

    def get_ai_prompt_context(self):
        personal = self.profile["personal"]
        metrics = self.profile["рассчитанные_метрики"]
        restrictions = self.profile["ограничения"]

        context = f"""
ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
- Пол: {personal['пол']}
- Возраст: {personal['возраст']} лет
- Рост: {personal['рост']} см, Вес: {personal['вес']} кг
- Цель: {personal['цель']} (целевой вес: {personal['целевой_вес']} кг)
- Уровень активности: {personal['уровень_активности']}
- Рекомендуемая норма: {metrics['дневные_калории']} ккал/день
- Рекомендуемые БЖУ: {metrics['дневные_белки']}г белка, {metrics['дневные_углеводы']}г углеводов, {metrics['дневные_жиры']}г жиров

ОГРАНИЧЕНИЯ:
- Тип питания: {restrictions['тип_питания']}
- Медицинские показания: {', '.join(restrictions['медицинские_показания']) if restrictions['медицинские_показания'] else 'нет'}
"""
        return context

    def update_personal(self, **kwargs):
        self.profile["personal"].update(kwargs)
        return self.save_profile()

    def update_restrictions(self, **kwargs):
        self.profile["ограничения"].update(kwargs)
        return self.save_profile()

    def update_preferences(self, **kwargs):
        self.profile["предпочтения"].update(kwargs)
        return self.save_profile()