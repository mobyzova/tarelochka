import cv2
import numpy as np

class DepthEstimator:
    def __init__(self):
        pass

    def estimate_depth(self, image_array):
        return self.simple_fallback_depth_estimation(image_array)

    def simple_fallback_depth_estimation(self, image_array):
        try:
            # Переводим в черно-белое для анализа яркости
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY).astype(np.float32)

            # Сильно размываем изображение - убираем мелкие детали
            blurred = cv2.GaussianBlur(gray, (15, 15), 0)

            # Находим разницу: области с большой разницей = много деталей = ближе к камере
            detail_map = np.abs(gray - blurred)

            # Приводим значения к стандартному диапазону 0-255
            depth_map = cv2.normalize(detail_map, None, 0, 255, cv2.NORM_MINMAX)

            # Инвертируем: больше деталей = ближе = темнее на карте глубины
            depth_map = (255 - depth_map).astype(np.uint8)

            return depth_map

        except Exception:
            # Если что-то пошло не так - возвращаем серую карту (средняя глубина)
            return np.ones(image_array.shape[:2], dtype=np.uint8) * 128