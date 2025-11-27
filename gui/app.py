import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import sys
from user_profile.profile_gui import ProfileDialog

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.model_loader import ModelLoader
from core.diet_tracker import DietTracker
from services.ai_service import AIService


class ElegantFoodApp:
    def __init__(self):
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.model_loader = ModelLoader()
        self.diet_tracker = DietTracker()
        self.ai_service = AIService()
        self.user_profile = self.diet_tracker.get_user_profile()
        self.current_food = None
        self.current_confidence = 0

        self.colors = {
            "bg_primary": "#FFF8F8",
            "bg_secondary": "#FFF0F5",
            "surface": "#FFFFFF",
            "surface_light": "#FFFBFB",
            "primary": "#FFB6C1",
            "primary_light": "#FFE4E9",
            "accent": "#FF91A4",
            "accent_dark": "#FF6B8B",
            "text_primary": "#2D3748",
            "text_secondary": "#5A5A5A",
            "border": "#E2E8F0",
            "border_accent": "#FFD1DC"
        }

        self.setup_ui()
        self.check_api_status()

    def setup_ui(self):

        self.app = ctk.CTk()
        self.app.title("Тарелочка • Анализатор питания")
        self.app.geometry("1400x900")
        self.app.minsize(1200, 800)
        self.app.configure(fg_color=self.colors["bg_primary"])


        self.app.grid_columnconfigure(1, weight=1)
        self.app.grid_rowconfigure(0, weight=1)


        self.sidebar = ctk.CTkFrame(
            self.app,
            width=280,
            corner_radius=0,
            fg_color=self.colors["bg_secondary"],
            border_width=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 2), pady=0)
        self.sidebar.grid_rowconfigure(4, weight=1)


        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=25, pady=(35, 25), sticky="ew")

        self.logo_label = ctk.CTkLabel(
            logo_frame,
            text="Тарелочка",
            font=ctk.CTkFont(family="Arial", size=26, weight="bold"),
            text_color=self.colors["accent_dark"]
        )
        self.logo_label.pack()

        self.subtitle_label = ctk.CTkLabel(
            logo_frame,
            text="Ваш персональный диетолог",
            font=ctk.CTkFont(family="Arial", size=13),
            text_color=self.colors["text_primary"]
        )
        self.subtitle_label.pack(pady=(5, 0))

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.nav_analyze = self.create_nav_button(
            nav_frame, "Анализ пищи", self.show_analysis_tab
        )
        self.nav_diet = self.create_nav_button(
            nav_frame, "Мой рацион", self.show_diet_tab
        )
        self.nav_ai = self.create_nav_button(
            nav_frame, "AI Анализ", self.show_ai_tab
        )

        stats_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.colors["surface"],
            corner_radius=20,
            border_width=1,
            border_color=self.colors["border_accent"]
        )
        stats_frame.grid(row=2, column=0, padx=20, pady=25, sticky="ew")

        ctk.CTkLabel(
            stats_frame,
            text="Сегодня",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(pady=(18, 10))

        self.sidebar_stats = ctk.CTkLabel(
            stats_frame,
            text="Добавьте первый\nприем пищи",
            font=ctk.CTkFont(family="Arial", size=13),
            text_color=self.colors["text_primary"],
            justify="center"
        )
        self.sidebar_stats.pack(pady=(0, 18))

        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.grid(row=5, column=0, padx=20, pady=20, sticky="sew")

        self.profile_btn = ctk.CTkButton(
            bottom_frame,
            text="Настройки профиля",
            command=self.show_profile,
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.colors["surface"],
            hover_color=self.colors["primary_light"],
            text_color=self.colors["text_primary"],
            height=42,
            corner_radius=15,
            border_width=1,
            border_color=self.colors["border_accent"]
        )
        self.profile_btn.pack(fill="x", pady=(0, 10))

        self.main_frame = ctk.CTkFrame(
            self.app,
            corner_radius=0,
            fg_color=self.colors["bg_primary"],
            border_width=0
        )
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(
            self.main_frame,
            height=120,
            corner_radius=0,
            fg_color=self.colors["surface"],
            border_width=0
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 2))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)

        self.main_title = ctk.CTkLabel(
            header_frame,
            text="Добро пожаловать в Тарелочка",
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        self.main_title.grid(row=0, column=0, padx=40, pady=(25, 5), sticky="w")

        self.main_subtitle = ctk.CTkLabel(
            header_frame,
            text="Ваш персональный помощник в анализе питания",
            font=ctk.CTkFont(family="Arial", size=16),
            text_color=self.colors["text_primary"]
        )
        self.main_subtitle.grid(row=1, column=0, padx=40, pady=(0, 25), sticky="w")

        self.setup_analysis_tab()
        self.setup_diet_tab()
        self.setup_ai_tab()
        self.show_analysis_tab()

    def create_nav_button(self, parent, text, command):
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=ctk.CTkFont(family="Arial", size=15),
            fg_color="transparent",
            hover_color=self.colors["primary_light"],
            text_color=self.colors["text_primary"],
            anchor="w",
            height=52,
            corner_radius=15,
            border_width=0
        )
        btn.pack(fill="x", pady=4)
        return btn

    def setup_analysis_tab(self):
        self.analysis_tab = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.analysis_tab.grid_columnconfigure(0, weight=1)
        self.analysis_tab.grid_rowconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(self.analysis_tab, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(
            content_frame,
            corner_radius=25,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"]
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=0)
        left_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            left_panel,
            text="Загрузка изображения",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=30, pady=(25, 15), sticky="w")

        image_container = ctk.CTkFrame(
            left_panel,
            corner_radius=20,
            fg_color=self.colors["bg_secondary"]
        )
        image_container.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 20))
        image_container.grid_rowconfigure(0, weight=1)

        self.image_frame = ctk.CTkFrame(
            image_container,
            corner_radius=15,
            fg_color=self.colors["surface_light"]
        )
        self.image_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text="Загрузите изображение еды\nдля анализа",
            font=ctk.CTkFont(family="Arial", size=14),
            text_color=self.colors["text_primary"]
        )
        self.image_label.pack(expand=True, padx=20, pady=20)

        btn_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=25, pady=(0, 25))

        self.load_btn = ctk.CTkButton(
            btn_frame,
            text="Выбрать изображение",
            command=self.classify_image,
            height=50,
            font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_dark"],
            corner_radius=12,
            text_color=self.colors["surface"]
        )
        self.load_btn.pack(fill="x", pady=(0, 10))

        self.add_to_diet_btn = ctk.CTkButton(
            btn_frame,
            text="Добавить в рацион",
            command=self.add_to_diet,
            height=50,
            font=ctk.CTkFont(family="Arial", size=14),
            fg_color=self.colors["primary"],
            hover_color=self.colors["accent"],
            corner_radius=12,
            state="disabled",
            text_color=self.colors["surface"]
        )
        self.add_to_diet_btn.pack(fill="x")

        right_panel = ctk.CTkFrame(
            content_frame,
            corner_radius=25,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"]
        )
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(15, 0), pady=0)
        right_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            right_panel,
            text="Результаты анализа",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=30, pady=(25, 20), sticky="w")

        result_card = ctk.CTkFrame(
            right_panel,
            corner_radius=20,
            fg_color=self.colors["bg_secondary"]
        )
        result_card.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 25))
        result_card.grid_columnconfigure(0, weight=1)

        self.result_title = ctk.CTkLabel(
            result_card,
            text="Ожидание анализа...",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        self.result_title.pack(anchor="w", padx=25, pady=(25, 15))

        self.result_details = ctk.CTkLabel(
            result_card,
            text="Загрузите изображение для начала анализа",
            font=ctk.CTkFont(family="Arial", size=13),
            text_color=self.colors["text_primary"],
            justify="left"
        )
        self.result_details.pack(anchor="w", padx=25, pady=(0, 25))

        progress_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        progress_frame.grid(row=2, column=0, sticky="ew", padx=25, pady=(0, 25))

        self.progress = ctk.CTkProgressBar(
            progress_frame,
            height=8,
            progress_color=self.colors["accent"],
            fg_color=self.colors["border"]
        )
        self.progress.pack(fill="x")
        self.progress.set(0)

    def setup_diet_tab(self):
        self.diet_tab = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.diet_tab.grid_columnconfigure(0, weight=1)
        self.diet_tab.grid_rowconfigure(1, weight=1)

        content_frame = ctk.CTkFrame(self.diet_tab, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        stats_frame = ctk.CTkFrame(
            content_frame,
            corner_radius=25,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"]
        )
        stats_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)  # Добавлено равномерное распределение

        ctk.CTkLabel(
            stats_frame,
            text="Общая статистика",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, columnspan=5, padx=30, pady=(25, 20), sticky="w")

        self.stats_meals = self.create_stat_card(stats_frame, "Приемов пищи", "0", 0, 1)
        self.stats_calories = self.create_stat_card(stats_frame, "Калории", "0", 1, 1)
        self.stats_protein = self.create_stat_card(stats_frame, "Белки", "0г", 2, 1)
        self.stats_carbs = self.create_stat_card(stats_frame, "Углеводы", "0г", 3, 1)
        self.stats_fat = self.create_stat_card(stats_frame, "Жиры", "0г", 4, 1)

        list_frame = ctk.CTkFrame(
            content_frame,
            corner_radius=25,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"]
        )
        list_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            list_frame,
            text="История приемов пищи",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=30, pady=25, sticky="w")

        self.meals_listbox = ctk.CTkScrollableFrame(
            list_frame,
            fg_color=self.colors["bg_secondary"],
            corner_radius=15
        )
        self.meals_listbox.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 25))

        # Кнопка очистки
        ctk.CTkButton(
            list_frame,
            text="Очистить рацион",
            command=self.clear_diet,
            font=ctk.CTkFont(family="Arial", size=14),
            height=45,
            fg_color=self.colors["accent_dark"],
            hover_color="#FF4D7A",
            corner_radius=12,
            text_color=self.colors["surface"]
        ).grid(row=2, column=0, padx=25, pady=25, sticky="ew")

    def setup_ai_tab(self):
        self.ai_tab = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.ai_tab.grid_columnconfigure(0, weight=1)
        self.ai_tab.grid_rowconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(self.ai_tab, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        control_frame = ctk.CTkFrame(
            content_frame,
            corner_radius=25,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"]
        )
        control_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
        control_frame.grid_columnconfigure(1, weight=1)

        top_row = ctk.CTkFrame(control_frame, fg_color="transparent")
        top_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=30, pady=(25, 15))
        top_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            top_row,
            text="AI Анализ рациона",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        self.ai_btn = ctk.CTkButton(
            top_row,
            text="Запустить AI анализ",
            command=self.get_ai_recommendations,
            height=50,
            font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_dark"],
            corner_radius=12,
            text_color=self.colors["surface"]
        )
        self.ai_btn.grid(row=0, column=1, sticky="e")

        self.api_status = ctk.CTkLabel(
            control_frame,
            text="Статус API: Не настроен",
            font=ctk.CTkFont(family="Arial", size=13),
            text_color=self.colors["accent_dark"]
        )
        self.api_status.grid(row=1, column=0, padx=30, pady=(0, 25), sticky="w")

        # Область рекомендаций
        output_frame = ctk.CTkFrame(
            content_frame,
            corner_radius=25,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"]
        )
        output_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            output_frame,
            text="Рекомендации по питанию",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=30, pady=25, sticky="w")

        self.ai_output = ctk.CTkTextbox(
            output_frame,
            font=ctk.CTkFont(family="Arial", size=13),
            wrap="word",
            fg_color=self.colors["bg_secondary"],
            text_color=self.colors["text_primary"],
            border_width=1,
            border_color=self.colors["border"],
            corner_radius=15
        )
        self.ai_output.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 25))
        self.ai_output.insert("1.0",
                              "Тарелочка - ваш персональный помощник в анализе питания\n\n"
                              "Для получения рекомендаций:\n"
                              "1. Добавьте приемы пищи через вкладку 'Анализ пищи'\n"
                              "2. Просмотрите статистику в 'Мой рацион'\n"
                              "3. Запустите AI анализ для детальных рекомендаций\n\n"
                              "Система проанализирует баланс питательных веществ и даст персонализированные советы."
                              )
        self.ai_output.configure(state="disabled")

    def create_stat_card(self, parent, title, value, column, row):
        card = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color=self.colors["bg_secondary"],
            border_width=0
        )
        card.grid(row=row, column=column, sticky="nsew", padx=10, pady=15)

        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family="Arial", size=13),
            text_color=self.colors["text_primary"]
        ).pack(pady=(15, 5))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(family="Arial", size=22, weight="bold"),
            text_color=self.colors["accent_dark"]
        )
        value_label.pack(pady=(0, 15))

        return value_label

    def show_analysis_tab(self):
        self.show_tab(self.analysis_tab, "Анализ питания", "Распознавание пищи по изображению")

    def show_diet_tab(self):
        self.show_tab(self.diet_tab, "Мой рацион", "Статистика и история питания")
        self.update_diet_display()

    def show_ai_tab(self):
        self.show_tab(self.ai_tab, "AI Анализ", "Персональные рекомендации")

    def show_tab(self, tab, title, subtitle):
        for widget in self.main_frame.grid_slaves():
            if widget.grid_info()["row"] == 1:
                widget.grid_remove()

        tab.grid(row=1, column=0, sticky="nsew")
        self.main_title.configure(text=title)
        self.main_subtitle.configure(text=subtitle)

    def show_profile(self):
        ProfileDialog(self, self.diet_tracker)

    def classify_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение еды",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )

        if not file_path:
            return

        self.current_image_path = file_path

        if not self.model_loader.model:
            messagebox.showerror("Ошибка", "Модель анализа не загружена")
            return

        self.progress.start()
        self.load_btn.configure(state="disabled")
        self.add_to_diet_btn.configure(state="disabled")

        try:
            image_pil = Image.open(file_path)
            image_display = image_pil.resize((340, 250), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image_display)

            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo

            from tensorflow.keras.preprocessing import image
            import numpy as np

            test_image = image.load_img(file_path, target_size=self.model_loader.target_size)
            test_image = image.img_to_array(test_image)
            test_image = np.expand_dims(test_image, axis=0)
            test_image = self.model_loader.custom_preprocess(test_image)

            predictions = self.model_loader.model.predict(test_image, verbose=0)
            class_index = np.argmax(predictions)
            self.current_food = self.model_loader.class_names[class_index]
            self.current_confidence = predictions[0][class_index] * 100

            # ОБНОВЛЕННАЯ ЧАСТЬ: Получаем информацию с оценкой по изображению
            food_data = self.model_loader.get_food_info(self.current_food, file_path)

            result_text = f"Распознано: {self.current_food.replace('_', ' ').title()}"
            self.result_title.configure(text=result_text, text_color=self.colors["accent_dark"])

            # Формируем детальную информацию с указанием метода оценки
            detail_text = f"Точность анализа: {self.current_confidence:.1f}%\n\n"

            if food_data.get('estimation_method') == 'volume_based':
                detail_text += "📊 ОЦЕНКА ПО ИЗОБРАЖЕНИЮ:\n"
                detail_text += f"• Объем: {food_data.get('estimated_volume', 0):.1f} см³\n"
                detail_text += f"• Масса: {food_data.get('estimated_mass', food_data.get('estimated_mass_g', 0)):.1f} г\n"  # Исправленный ключ
                detail_text += f"• Калории: {food_data.get('calories', 0):.1f} ккал\n"
                detail_text += f"• Белки: {food_data.get('protein', 0):.1f}г\n"
                detail_text += f"• Углеводы: {food_data.get('carbs', 0):.1f}г\n"
                detail_text += f"• Жиры: {food_data.get('fat', 0):.1f}г\n"
            else:
                detail_text += "📋 БАЗОВЫЕ ДАННЫЕ:\n"
                detail_text += f"• Калории: {food_data.get('calories', 'N/A')} ккал\n"
                detail_text += f"• Белки: {food_data.get('protein', 'N/A')}г\n"
                detail_text += f"• Углеводы: {food_data.get('carbs', 'N/A')}г\n"
                detail_text += f"• Жиры: {food_data.get('fat', 'N/A')}г\n"

            detail_text += f"\n• Оценка питательности: {food_data.get('health_score', 'N/A')}/10"

            self.result_details.configure(text=detail_text)
            self.add_to_diet_btn.configure(state="normal")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обработке изображения:\n{str(e)}")
        finally:
            self.progress.stop()
            self.load_btn.configure(state="normal")


    def add_to_diet(self):
            if not self.current_food:
                messagebox.showwarning("Предупреждение", "Сначала выполните анализ изображения")
                return

            # Получаем актуальные данные (с оценкой по изображению)
            file_path = getattr(self, 'current_image_path', None)
            if file_path and os.path.exists(file_path):
                food_data = self.model_loader.get_food_info(self.current_food, file_path)
            else:
                food_data = self.model_loader.get_food_info(self.current_food)

            if not food_data:
                return
            # Используем данные из food_data
            meal_data = {
                'name': self.current_food,
                'calories': food_data['calories'],
                'protein': food_data['protein'],
                'carbs': food_data['carbs'],
                'fat': food_data['fat'],
                'health_score': food_data['health_score'],
                'confidence': self.current_confidence,
                'estimation_method': food_data.get('estimation_method', 'database')
            }

            # Добавляем дополнительную информацию если есть
            if 'estimated_mass' in food_data:
                meal_data['estimated_mass'] = food_data['estimated_mass']
            if 'estimated_volume' in food_data:
                meal_data['estimated_volume'] = food_data['estimated_volume']

            self.diet_tracker.add_meal(meal_data)
            self.update_diet_display()

            method = food_data.get('estimation_method', 'базовые данные')
            calories_value = meal_data['calories']

            messagebox.showinfo("Успех",
                                f"{self.current_food.replace('_', ' ').title()} добавлен в рацион\n"
                                f"Метод оценки: {method}\n"
                                f"Калории: {calories_value} ккал")

    def clear_diet(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить весь рацион?"):
            self.diet_tracker.clear_diet()
            self.update_diet_display()
            self.ai_output.configure(state="normal")
            self.ai_output.delete("1.0", "end")
            self.ai_output.insert("1.0", "Рацион очищен.\n\nДобавьте приемы пищи для получения анализа.")
            self.ai_output.configure(state="disabled")

    def update_diet_display(self):
        stats = self.diet_tracker.get_diet_stats()
        self.stats_meals.configure(text=str(stats['total_meals']))
        self.stats_calories.configure(text=str(stats['total_calories']))
        self.stats_protein.configure(text=f"{stats['total_protein']}г")
        self.stats_carbs.configure(text=f"{stats['total_carbs']}г")
        self.stats_fat.configure(text=f"{stats['total_fat']}г")

        if stats['total_meals'] > 0:
            sidebar_text = f"{stats['total_meals']} приемов\n{stats['total_calories']} ккал"
        else:
            sidebar_text = "Добавьте\nпервый прием пищи"
        self.sidebar_stats.configure(text=sidebar_text)

        # Очищаем список приемов пищи
        for widget in self.meals_listbox.winfo_children():
            widget.destroy()

        # Добавляем приемы пищи с округленными значениями
        for meal in stats['meals']:
            meal_frame = ctk.CTkFrame(
                self.meals_listbox,
                height=70,
                corner_radius=12,
                fg_color=self.colors["surface"],
                border_width=1,
                border_color=self.colors["border_accent"]
            )
            meal_frame.pack(fill="x", pady=6, padx=5)
            meal_frame.pack_propagate(False)

            meal_frame.grid_columnconfigure(0, weight=1)

            # Округляем значения для отображения
            calories = round(meal['calories'])
            protein = round(meal['protein'])
            carbs = round(meal['carbs'])
            fat = round(meal['fat'])

            ctk.CTkLabel(
                meal_frame,
                text=f"{meal['time']} - {meal['name'].replace('_', ' ').title()}",
                font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
                text_color=self.colors["text_primary"]
            ).grid(row=0, column=0, sticky="w", padx=20, pady=(12, 2))

            ctk.CTkLabel(
                meal_frame,
                text=f"{calories} ккал • Белки: {protein}г • Углеводы: {carbs}г • Жиры: {fat}г",
                font=ctk.CTkFont(family="Arial", size=12),
                text_color=self.colors["text_primary"]
            ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 12))

    def get_ai_recommendations(self):
        stats = self.diet_tracker.get_diet_stats()

        if stats['total_meals'] == 0:
            messagebox.showwarning("Предупреждение", "Добавьте приемы пищи для анализа рациона")
            return

        if not self.ai_service.check_api_status():
            messagebox.showerror("Ошибка API",
                                 "Для работы AI анализа необходимо настроить API ключ.\n\n"
                                 "Откройте файл services/ai_service.py и укажите ваш API ключ от CTutees")
            return

        self.ai_btn.configure(state="disabled", text="Анализ выполняется...")
        self.ai_output.configure(state="normal")
        self.ai_output.delete("1.0", "end")
        self.ai_output.insert("1.0", "Выполняется анализ рациона...\nПожалуйста, подождите.")
        self.app.update()

        try:
            prompt = self.diet_tracker.prepare_ai_analysis()
            recommendations = self.ai_service.get_recommendations(prompt)

            self.ai_output.delete("1.0", "end")
            self.ai_output.insert("1.0", f"РЕЗУЛЬТАТЫ AI АНАЛИЗА:\n\n{recommendations}")

        except Exception as e:
            error_msg = f"Ошибка при выполнении анализа:\n{str(e)}\n\nПроверьте подключение к интернету и настройки API."
            self.ai_output.delete("1.0", "end")
            self.ai_output.insert("1.0", error_msg)
        finally:
            self.ai_output.configure(state="disabled")
            self.ai_btn.configure(state="normal", text="Запустить AI анализ")

    def check_api_status(self):
        if self.ai_service.check_api_status():
            self.api_status.configure(text="Статус API: Подключен", text_color=self.colors["accent_dark"])
        else:
            self.api_status.configure(text="Статус API: Требуется настройка", text_color=self.colors["accent_dark"])

    def run(self):
        self.app.mainloop()


if __name__ == "__main__":
    app = ElegantFoodApp()
    app.run()