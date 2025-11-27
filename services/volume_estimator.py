import cv2
import numpy as np
from PIL import Image
from services.depth_estimator import DepthEstimator
from services.food_segmantator import FoodSegmentator

class VolumeEstimator:
    def __init__(self):
        # Сервисы для оценки глубины и сегментации
        self.depth_estimator = DepthEstimator()
        self.segmentator = FoodSegmentator()

        # Кэш для ускорения повторных вычислений
        self._cache = {}
        self._cache_size = 100

        # Плотность продуктов (г/см³)
        self.food_density_db = {
            'apple_pie': 0.35, 'caesar_salad': 0.25, 'dumplings': 0.45,
            'french_fries': 0.25, 'hamburger': 0.40, 'chicken_curry': 0.35,
            'cup_cakes': 0.30, 'pizza': 0.35, 'sushi': 0.45, 'ice_cream': 0.50
        }

        # Калорийность (ккал/г)
        self.calorie_density_db = {
            'apple_pie': 2.8, 'caesar_salad': 1.1, 'dumplings': 1.6,
            'french_fries': 2.8, 'hamburger': 2.5, 'chicken_curry': 1.4,
            'cup_cakes': 3.8, 'pizza': 2.4, 'sushi': 1.2, 'ice_cream': 2.2
        }

        # Параметры для разных типов еды
        self.food_params = {
            'apple_pie': {'typical_size': 20, 'max_depth': 5, 'volume_factor': 0.8, 'limits': (100, 800)},
            'caesar_salad': {'typical_size': 25, 'max_depth': 8, 'volume_factor': 0.6, 'limits': (200, 1200)},
            'dumplings': {'typical_size': 15, 'max_depth': 4, 'volume_factor': 0.9, 'limits': (150, 600)},
            'french_fries': {'typical_size': 15, 'max_depth': 3, 'volume_factor': 0.4, 'limits': (100, 500)},
            'hamburger': {'typical_size': 12, 'max_depth': 6, 'volume_factor': 1.0, 'limits': (200, 900)},
            'chicken_curry': {'typical_size': 20, 'max_depth': 6, 'volume_factor': 0.8, 'limits': (300, 1000)},
            'cup_cakes': {'typical_size': 8, 'max_depth': 5, 'volume_factor': 0.7, 'limits': (50, 300)},
            'pizza': {'typical_size': 30, 'max_depth': 2, 'volume_factor': 0.5, 'limits': (400, 1500)},
            'sushi': {'typical_size': 10, 'max_depth': 4, 'volume_factor': 0.9, 'limits': (100, 500)},
            'ice_cream': {'typical_size': 10, 'max_depth': 6, 'volume_factor': 0.6, 'limits': (50, 400)}
        }

        # Соотношения питательных веществ для разных продуктов
        self.nutrition_ratios = {
            'apple_pie': {'protein': 0.03, 'carbs': 0.50, 'fat': 0.22},
            'caesar_salad': {'protein': 0.18, 'carbs': 0.08, 'fat': 0.10},
            'dumplings': {'protein': 0.10, 'carbs': 0.20, 'fat': 0.08},
            'french_fries': {'protein': 0.03, 'carbs': 0.40, 'fat': 0.18},
            'hamburger': {'protein': 0.20, 'carbs': 0.25, 'fat': 0.18},
            'chicken_curry': {'protein': 0.16, 'carbs': 0.10, 'fat': 0.12},
            'cup_cakes': {'protein': 0.04, 'carbs': 0.50, 'fat': 0.20},
            'pizza': {'protein': 0.14, 'carbs': 0.35, 'fat': 0.15},
            'sushi': {'protein': 0.10, 'carbs': 0.30, 'fat': 0.03},
            'ice_cream': {'protein': 0.05, 'carbs': 0.25, 'fat': 0.15}
        }

    def _get_cache_key(self, image_path, food_type):
        # Создает уникальный ключ для кэша
        return f"{hash(image_path)}_{food_type}"

    def _update_cache(self, key, value):
        #Обновляет кэш, удаляя старые записи при переполнении"""
        if len(self._cache) >= self._cache_size:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = value

    def calculate_3d_volume(self, mask, depth_map, food_type):
        # Вычисляет объем еды на основе маски и карты глубины
        try:
            # Проверяем что маска имеет разумный размер
            pixel_area = np.count_nonzero(mask)
            total_pixels = mask.shape[0] * mask.shape[1]

            if pixel_area < 500 or pixel_area > total_pixels * 0.9:
                return 0.0

            # Находим основной контур еды
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return 0.0

            main_contour = max(contours, key=cv2.contourArea)

            # Создаем чистую маску только основного объекта
            object_mask = np.zeros_like(mask)
            cv2.drawContours(object_mask, [main_contour], 0, 255, -1)

            # Анализируем глубину в области еды
            depth_values = depth_map[object_mask == 255]
            if len(depth_values) == 0:
                return 0.0

            # Нормализуем среднюю глубину
            avg_depth_normalized = np.mean(depth_values) / 255.0

            # Получаем параметры для конкретного типа еды
            params = self.food_params.get(food_type, self.food_params['apple_pie'])

            # Вычисляем масштаб (пикселей на сантиметр)
            x, y, w, h = cv2.boundingRect(main_contour)
            pixels_per_cm = max(w, h) / params['typical_size']

            # Вычисляем объем: площадь × глубина × поправочный коэффициент
            area_cm2 = pixel_area / (pixels_per_cm ** 2)
            depth_cm = avg_depth_normalized * params['max_depth']
            volume_cm3 = area_cm2 * depth_cm * params['volume_factor']

            # Ограничиваем объем разумными пределами
            min_vol, max_vol = params['limits']
            return float(np.clip(volume_cm3, min_vol, max_vol))

        except Exception:
            return 0.0

    def estimate_calories_from_volume(self, volume_cm3, food_type):
        # Оценивает калорийность на основе объема и типа еды"""
        density = self.food_density_db.get(food_type, 0.35)
        calorie_density = self.calorie_density_db.get(food_type, 2.0)

        # Вычисляем массу и калории
        mass_grams = volume_cm3 * density
        calories = mass_grams * calorie_density
        calories = min(calories, 1500.0)  # Ограничиваем максимум

        return {
            'volume_cm3': volume_cm3,
            'mass_grams': mass_grams,
            'calories': calories,
            'density': density,
            'calorie_density': calorie_density
        }

    def estimate_food_volume_and_calories(self, image_path, food_type):
        #Основной метод: оценивает объем и калорийность по изображению"""
        # Проверяем кэш перед вычислениями
        cache_key = self._get_cache_key(image_path, food_type)
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            # Загружаем и проверяем изображение
            with Image.open(image_path) as img:
                image_array = np.array(img, dtype=np.uint8)

            if image_array.shape[0] < 50 or image_array.shape[1] < 50:
                return None

            # Сегментируем еду и оцениваем глубину
            mask = self.segmentator.segment_food(image_array)
            depth_map = self.depth_estimator.estimate_depth(image_array)

            # Вычисляем объем и калории
            volume = self.calculate_3d_volume(mask, depth_map, food_type)

            if volume > 0:
                result = self.estimate_calories_from_volume(volume, food_type)
                self._update_cache(cache_key, result)
                return result

            return None

        except Exception:
            return None

    def get_volume_based_nutrition(self, food_type, volume_cm3):
        #Вычисляет полную пищевую ценность на основе объема"""
        if volume_cm3 <= 0:
            return None

        # Получаем базовую информацию о калориях и массе
        calorie_info = self.estimate_calories_from_volume(volume_cm3, food_type)
        if not calorie_info:
            return None

        # Вычисляем белки, жиры и углеводы по соотношениям
        ratios = self.nutrition_ratios.get(food_type, self.nutrition_ratios['apple_pie'])
        mass_g = calorie_info['mass_grams']

        nutrition = {
            'calories': round(calorie_info['calories']),
            'protein': round(mass_g * ratios['protein']),
            'carbs': round(mass_g * ratios['carbs']),
            'fat': round(mass_g * ratios['fat']),
            'estimated_mass': round(mass_g),
            'estimated_volume': round(calorie_info['volume_cm3'])
        }

        return nutrition