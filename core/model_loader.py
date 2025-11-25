from tensorflow.keras.models import load_model
import os
from tkinter import messagebox

class ModelLoader:
    def __init__(self):
        self.model = None
        self.target_size = (128, 128)
        self.class_names = [
            'apple_pie', 'caesar_salad', 'dumplings', 'french_fries', 'hamburger',
            'chicken_curry', 'cup_cakes', 'pizza', 'sushi', 'ice_cream'
        ]
        self.food_info = {
            'apple_pie': {'calories': 350, 'protein': 4, 'carbs': 45, 'fat': 18, 'health_score': 6, 'description': 'Сладкая выпечка с яблоками'},
            'caesar_salad': {'calories': 180, 'protein': 12, 'carbs': 8, 'fat': 12, 'health_score': 9, 'description': 'Здоровый салат с курицей и соусом'},
            'dumplings': {'calories': 280, 'protein': 15, 'carbs': 35, 'fat': 10, 'health_score': 7, 'description': 'Пельмени/вареники с начинкой'},
            'french_fries': {'calories': 320, 'protein': 4, 'carbs': 35, 'fat': 17, 'health_score': 3, 'description': 'Жареный картофель'},
            'hamburger': {'calories': 450, 'protein': 25, 'carbs': 35, 'fat': 22, 'health_score': 4, 'description': 'Бургер с котлетой и булкой'},
            'chicken_curry': {'calories': 320, 'protein': 25, 'carbs': 15, 'fat': 18, 'health_score': 7, 'description': 'Курица в карри с рисом'},
            'cup_cakes': {'calories': 280, 'protein': 3, 'carbs': 40, 'fat': 12, 'health_score': 5, 'description': 'Небольшие сладкие кексы'},
            'pizza': {'calories': 380, 'protein': 18, 'carbs': 45, 'fat': 15, 'health_score': 5, 'description': 'Итальянская пицца с различными топпингами'},
            'sushi': {'calories': 220, 'protein': 12, 'carbs': 35, 'fat': 5, 'health_score': 8, 'description': 'Японское блюдо с рисом и морепродуктами'},
            'ice_cream': {'calories': 250, 'protein': 4, 'carbs': 30, 'fat': 12, 'health_score': 4, 'description': 'Замороженный сладкий десерт'}
        }
        self.load_model()

    def load_model(self):
        try:
            model_path = 'E:\\FoodClassificationProject\\models\\my_final_fast_cnn_10_classes.h5'
            if os.path.exists(model_path):
                self.model = load_model(model_path)
            else:
                messagebox.showerror("Ошибка", f"Кастомная CNN модель не найдена по пути:\n{model_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить кастомную CNN модель:\n{str(e)}")

    def custom_preprocess(self, x):
        return x / 255.0

    def get_food_info(self, food_name):
        return self.food_info.get(food_name, {})