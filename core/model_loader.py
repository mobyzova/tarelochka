from tensorflow.keras.models import load_model
import tensorflow as tf
import os
import numpy as np
from services.volume_estimator import VolumeEstimator


class ModelLoader:
    def __init__(self):
        self.model = None
        self.target_size = (128, 128)
        self.class_names = [
            'apple_pie', 'caesar_salad', 'dumplings', 'french_fries', 'hamburger',
            'chicken_curry', 'cup_cakes', 'pizza', 'sushi', 'ice_cream'
        ]

        self.volume_estimator = VolumeEstimator()
        self._food_info_cache = {}
        self._model_loaded = False

        self.load_model()

    def load_model(self):
        if self._model_loaded:
            return

        try:
            model_path = 'E:\\FoodClassificationProject\\models\\my_final_fast_cnn_10_classes.h5'
            if os.path.exists(model_path):
                self.model = load_model(model_path)
                self._model_loaded = True
            else:
                self.model = None
        except Exception:
            self.model = None

    def custom_preprocess(self, x):
        return x / 255.0

    def get_food_info(self, food_name, image_path=None):
        cache_key = f"{food_name}_{hash(image_path) if image_path else 'default'}"

        if cache_key in self._food_info_cache:
            return self._food_info_cache[cache_key]

        # Получаем информацию ТОЛЬКО из обработки изображения
        if image_path and os.path.exists(image_path):
            volume_based_nutrition = self.estimate_nutrition_from_image(image_path, food_name)

            if volume_based_nutrition:
                result = {
                    'calories': volume_based_nutrition['calories'],
                    'protein': volume_based_nutrition['protein'],
                    'carbs': volume_based_nutrition['carbs'],
                    'fat': volume_based_nutrition['fat'],
                    'health_score': volume_based_nutrition['health_score'],
                    'estimation_method': 'volume_estimation',
                    'estimated_mass': volume_based_nutrition.get('estimated_mass', 0),
                    'estimated_volume': volume_based_nutrition.get('estimated_volume', 0),
                    'confidence_score': volume_based_nutrition.get('confidence_score', 70)
                }
            else:
                # Если обработка не удалась, возвращаем нулевые значения
                result = self.get_fallback_info()
        else:
            # Если нет изображения, возвращаем нулевые значения
            result = self.get_fallback_info()

        self._food_info_cache[cache_key] = result
        return result

    def get_fallback_info(self):
        # Возвращает базовую информацию когда обработка невозможна"""
        return {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'health_score': 5,
            'estimation_method': 'fallback_no_image',
            'estimated_mass': 0,
            'estimated_volume': 0,
            'confidence_score': 0
        }

    def estimate_nutrition_from_image(self, image_path, food_type):
        try:
            volume_result = self.volume_estimator.estimate_food_volume_and_calories(image_path, food_type)

            if volume_result:
                nutrition = self.volume_estimator.get_volume_based_nutrition(food_type, volume_result['volume_cm3'])

                if nutrition:
                    nutrition['health_score'] = self.calculate_enhanced_health_score(nutrition, food_type)
                    nutrition['confidence_score'] = self.calculate_confidence_score(volume_result, nutrition)
                    return nutrition

            return None

        except Exception:
            return None

    def calculate_confidence_score(self, volume_result, nutrition):
        # Рассчитывает оценку уверенности на основе результатов обработки
        try:
            confidence = 70  # Базовая уверенность

            # Увеличиваем уверенность если объем в разумных пределах
            volume = volume_result.get('volume_cm3', 0)
            if 50 <= volume <= 1000:
                confidence += 10
            elif volume > 0:
                confidence += 5

            # Увеличиваем уверенность если калории в разумных пределах
            calories = nutrition.get('calories', 0)
            if 50 <= calories <= 800:
                confidence += 10
            elif calories > 0:
                confidence += 5

            return min(95, confidence)

        except:
            return 70

    def calculate_enhanced_health_score(self, nutrition, food_type):
        # Улучшенная оценка полезности на основе реальных питательных значений
        try:
            base_score = 5

            calories = nutrition['calories']
            protein = nutrition['protein']
            carbs = nutrition['carbs']
            fat = nutrition['fat']

            # Оценка на основе калорий
            if calories > 600:
                base_score -= 3
            elif calories > 400:
                base_score -= 2
            elif calories > 250:
                base_score -= 1
            elif calories < 150:
                base_score += 1

            # Оценка на основе белка
            protein_ratio = protein / max(calories / 10, 1)  # Белок на 100 ккал
            if protein_ratio > 3:
                base_score += 2
            elif protein_ratio > 2:
                base_score += 1
            elif protein_ratio < 0.5:
                base_score -= 1

            # Оценка на основе жиров
            fat_ratio = fat / max(calories / 10, 1)  # Жиры на 100 ккал
            if fat_ratio > 4:
                base_score -= 3
            elif fat_ratio > 3:
                base_score -= 2
            elif fat_ratio > 2:
                base_score -= 1
            elif fat_ratio < 1:
                base_score += 1

            # Оценка на основе углеводов
            carbs_ratio = carbs / max(calories / 10, 1)  # Углеводы на 100 ккал
            if carbs_ratio > 8:
                base_score -= 2
            elif carbs_ratio > 6:
                base_score -= 1

            # Корректировка по типу пищи
            if food_type in ['caesar_salad', 'sushi', 'chicken_curry']:
                base_score += 1
            elif food_type in ['french_fries', 'ice_cream', 'cup_cakes']:
                base_score -= 1

            return max(1, min(10, base_score))

        except:
            return 5