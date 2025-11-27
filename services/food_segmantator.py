import cv2
import numpy as np

class FoodSegmentator:
    def __init__(self):
        pass

    def segment_food(self, image_array):
        # Основной метод для сегментации еды на изображении
        try:
            # Пытаемся улучшенную сегментацию, если не вышло - используем маску по центру
            mask = self.enhanced_fallback_segmentation(image_array)
            return mask if self.validate_segmentation(mask) else self.create_centered_mask(image_array.shape)
        except Exception:
            # Если все сломалось - возвращаем маску по центру
            return self.create_centered_mask(image_array.shape)

    def validate_segmentation(self, mask):
        # Проверяет, что маска имеет разумный размер и форму
        try:
            mask_area = np.count_nonzero(mask)
            total_area = mask.shape[0] * mask.shape[1]
            coverage_ratio = mask_area / total_area

            # Отсеиваем слишком маленькие или слишком большие маски
            if coverage_ratio < 0.03 or coverage_ratio > 0.9:
                return False

            # Ищем контуры и проверяем, что есть хотя бы один
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return False

            # Проверяем, что основной контур занимает большую часть маски
            main_contour = max(contours, key=cv2.contourArea)
            contour_area = cv2.contourArea(main_contour)

            return contour_area / mask_area > 0.6

        except Exception:
            return False

    def enhanced_fallback_segmentation(self, image_array):
        # Улучшенная сегментация через цветовые диапазоны и текстуру
        try:
            # Переводим в разные цветовые пространства для лучшего анализа
            hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
            lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)

            # Диапазоны цветов, характерных для еды
            color_ranges = [
                ([10, 40, 40], [25, 255, 255]),  # Оранжевые/коричневые
                ([0, 40, 40], [10, 255, 255]),   # Красные
                ([170, 40, 40], [180, 255, 255]), # Красные (доп диапазон)
                ([35, 40, 40], [85, 255, 255]),  # Зеленые
                ([20, 40, 40], [35, 255, 255]),  # Желтые
            ]

            # Объединяем маски по всем цветовым диапазонам
            combined_mask = np.zeros(image_array.shape[:2], dtype=np.uint8)
            for lower, upper in color_ranges:
                mask_hsv = cv2.inRange(hsv, np.array(lower), np.array(upper))
                combined_mask = cv2.bitwise_or(combined_mask, mask_hsv)

            # Анализ текстуры через яркость - исключаем слишком темные и светлые области
            L, A, B = cv2.split(lab)
            _, bright_mask = cv2.threshold(L, 45, 255, cv2.THRESH_BINARY)    # Не слишком темно
            _, dark_mask = cv2.threshold(L, 220, 255, cv2.THRESH_BINARY_INV) # Не слишком светло
            texture_mask = cv2.bitwise_and(bright_mask, dark_mask)

            # Объединяем цветовую и текстурную сегментацию
            combined_mask = cv2.bitwise_or(combined_mask, texture_mask)

            # Очищаем маску от шума и заполняем дыры
            kernel = np.ones((7, 7), np.uint8)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)  # Заполняем дыры
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)   # Убираем шум

            # Находим основной объект
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                main_contour = max(contours, key=cv2.contourArea)
                main_area = cv2.contourArea(main_contour)
                total_area = image_array.shape[0] * image_array.shape[1]

                # Если объект слишком большой - вероятно выделили фон
                if main_area > total_area * 0.75:
                    # Ограничиваем поиск центральной областью
                    h, w = image_array.shape[:2]
                    center_mask = np.zeros((h, w), dtype=np.uint8)
                    center_x, center_y = w // 2, h // 2
                    axis_x, axis_y = int(w * 0.35), int(h * 0.35)
                    cv2.ellipse(center_mask, (center_x, center_y), (axis_x, axis_y), 0, 0, 360, 255, -1)
                    combined_mask = cv2.bitwise_and(combined_mask, center_mask)
                else:
                    # Используем только основной контур
                    clean_mask = np.zeros_like(combined_mask)
                    cv2.drawContours(clean_mask, [main_contour], 0, 255, -1)
                    combined_mask = clean_mask

            # Финальная проверка размера
            final_area = np.count_nonzero(combined_mask)
            total_area = combined_mask.shape[0] * combined_mask.shape[1]

            # Если маска все еще слишком большая - используем запасной вариант
            if final_area > total_area * 0.85:
                return self.create_centered_mask(image_array.shape)

            return combined_mask

        except Exception:
            return self.create_centered_mask(image_array.shape)

    def create_centered_mask(self, image_shape):
        # Создает эллиптическую маску в центре изображения как запасной вариант
        h, w = image_shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        center_x, center_y = w // 2, h // 2
        axis_x, axis_y = int(w * 0.25), int(h * 0.25)
        cv2.ellipse(mask, (center_x, center_y), (axis_x, axis_y), 0, 0, 360, 255, -1)
        return mask