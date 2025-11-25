import datetime
from user_profile.user_profile import UserProfile

class DietTracker:
    def __init__(self):
        self.daily_meals = []
        self.total_calories = 0
        self.total_protein = 0
        self.total_carbs = 0
        self.total_fat = 0
        self.user_profile = UserProfile()

    def add_meal(self, meal_data):
        meal = {
            'name': meal_data['name'],
            'calories': meal_data['calories'],
            'protein': meal_data['protein'],
            'carbs': meal_data['carbs'],
            'fat': meal_data['fat'],
            'health_score': meal_data['health_score'],
            'time': datetime.datetime.now().strftime("%H:%M"),
            'confidence': meal_data.get('confidence', 0)
        }

        self.daily_meals.append(meal)
        self.total_calories += meal_data['calories']
        self.total_protein += meal_data['protein']
        self.total_carbs += meal_data['carbs']
        self.total_fat += meal_data['fat']

    def clear_diet(self):
        self.daily_meals = []
        self.total_calories = 0
        self.total_protein = 0
        self.total_carbs = 0
        self.total_fat = 0

    def get_diet_stats(self):
        metrics = self.user_profile.profile["рассчитанные_метрики"]

        return {
            'total_meals': len(self.daily_meals),
            'total_calories': self.total_calories,
            'total_protein': self.total_protein,
            'total_carbs': self.total_carbs,
            'total_fat': self.total_fat,
            'meals': self.daily_meals,
            'daily_goals': {
                'calories': metrics['дневные_калории'],
                'protein': metrics['дневные_белки'],
                'carbs': metrics['дневные_углеводы'],
                'fat': metrics['дневные_жиры']
            },
            'progress': {
                'calories_percent': min(100, int((self.total_calories / metrics['дневные_калории']) * 100)) if metrics['дневные_калории'] > 0 else 0,
                'protein_percent': min(100, int((self.total_protein / metrics['дневные_белки']) * 100)) if metrics['дневные_белки'] > 0 else 0,
                'carbs_percent': min(100, int((self.total_carbs / metrics['дневные_углеводы']) * 100)) if metrics['дневные_углеводы'] > 0 else 0,
                'fat_percent': min(100, int((self.total_fat / metrics['дневные_жиры']) * 100)) if metrics['дневные_жиры'] > 0 else 0
            }
        }

    def prepare_ai_analysis(self):
        stats = self.get_diet_stats()
        profile_context = self.user_profile.get_ai_prompt_context()

        meals_analysis = []
        for i, meal in enumerate(self.daily_meals, 1):
            meal_analysis = f"""
Прием пищи {i} ({meal['time']}):
• Блюдо: {meal['name'].replace('_', ' ').title()}
• Калории: {meal['calories']} ккал
• Белки: {meal['protein']}г ({meal['protein']*4} ккал, {meal['protein']/stats['daily_goals']['protein']*100:.1f}% от дневной нормы)
• Углеводы: {meal['carbs']}г ({meal['carbs']*4} ккал, {meal['carbs']/stats['daily_goals']['carbs']*100:.1f}% от дневной нормы)
• Жиры: {meal['fat']}г ({meal['fat']*9} ккал, {meal['fat']/stats['daily_goals']['fat']*100:.1f}% от дневной нормы)
• Оценка питательности: {meal['health_score']}/10
• Точность распознавания: {meal.get('confidence', 0):.1f}%
"""
            meals_analysis.append(meal_analysis)

        meals_details = "\n".join(meals_analysis)

        protein_calories = stats['total_protein'] * 4
        carbs_calories = stats['total_carbs'] * 4
        fat_calories = stats['total_fat'] * 9
        total_calories_calculated = protein_calories + carbs_calories + fat_calories

        if total_calories_calculated > 0:
            protein_ratio = (protein_calories / total_calories_calculated) * 100
            carbs_ratio = (carbs_calories / total_calories_calculated) * 100
            fat_ratio = (fat_calories / total_calories_calculated) * 100
        else:
            protein_ratio = carbs_ratio = fat_ratio = 0

        target_ratio = self.user_profile.profile["personal"]["соотношение_бжу"]
        target_protein = target_ratio["белки"]
        target_carbs = target_ratio["углеводы"]
        target_fat = target_ratio["жиры"]

        prompt = f"""
{profile_context}

ДЕТАЛЬНЫЙ АНАЛИЗ ТЕКУЩЕГО РАЦИОНА:

ОБЩАЯ СТАТИСТИКА:
• Всего приемов пищи: {stats['total_meals']}
• Общее потребление калорий: {stats['total_calories']} ккал из {stats['daily_goals']['calories']} запланированных ({stats['progress']['calories_percent']}%)
• Белки: {stats['total_protein']}г из {stats['daily_goals']['protein']}г ({stats['progress']['protein_percent']}%)
• Углеводы: {stats['total_carbs']}г из {stats['daily_goals']['carbs']}г ({stats['progress']['carbs_percent']}%)
• Жиры: {stats['total_fat']}г из {stats['daily_goals']['fat']}г ({stats['progress']['fat_percent']}%)

АНАЛИЗ БАЛАНСА МАКРОНУТРИЕНТОВ:
• Фактическое соотношение БЖУ: Белки {protein_ratio:.1f}% / Углеводы {carbs_ratio:.1f}% / Жиры {fat_ratio:.1f}%
• Целевое соотношение БЖУ: Белки {target_protein}% / Углеводы {target_carbs}% / Жиры {target_fat}%
• Отклонение от цели: Белки {protein_ratio - target_protein:+.1f}% / Углеводы {carbs_ratio - target_carbs:+.1f}% / Жиры {fat_ratio - target_fat:+.1f}%

ДЕТАЛЬНЫЙ РАЗБОР ПРИЕМОВ ПИЩИ:
{meals_details}

ОСТАВШИЕСЯ РЕСУРСЫ НА ДЕНЬ:
• Калории: {max(0, stats['daily_goals']['calories'] - stats['total_calories'])} ккал
• Белки: {max(0, stats['daily_goals']['protein'] - stats['total_protein']):.1f}г
• Углеводы: {max(0, stats['daily_goals']['carbs'] - stats['total_carbs']):.1f}г
• Жиры: {max(0, stats['daily_goals']['fat'] - stats['total_fat']):.1f}г

ЗАПРОС НА АНАЛИТИЧЕСКИЙ ОТЧЕТ:

Пожалуйста, предоставьте развернутый анализ по следующим направлениям:

1. ОЦЕНКА ТЕКУЩЕГО СОСТОЯНИЯ
2. ДЕТАЛЬНЫЙ АНАЛИЗ МАКРОНУТРИЕНТОВ
3. АНАЛИЗ КАЧЕСТВА ПИТАНИЯ
4. КОНКРЕТНЫЕ РЕКОМЕНДАЦИИ
5. ПЕРСПЕКТИВНЫЕ СОВЕТЫ

Предоставьте научно обоснованные, измеримые и выполнимые рекомендации с учетом индивидуальных особенностей профиля пользователя.
"""
        return prompt

    def get_user_profile(self):
        return self.user_profile