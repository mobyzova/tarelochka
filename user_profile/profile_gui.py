import customtkinter as ctk
from tkinter import messagebox

class ProfileDialog:
    def __init__(self, parent, diet_tracker):
        self.parent = parent
        self.diet_tracker = diet_tracker
        self.profile = diet_tracker.get_user_profile()
        self.colors = parent.colors
        self.setup_dialog()

    def setup_dialog(self):
        self.dialog = ctk.CTkToplevel(self.parent.app)
        self.dialog.title("Настройки профиля")
        self.dialog.geometry("1000x800")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent.app)
        self.dialog.grab_set()
        self.dialog.configure(fg_color=self.colors["bg_primary"])

        header_frame = ctk.CTkFrame(
            self.dialog,
            height=120,
            corner_radius=0,
            fg_color=self.colors["surface"],
            border_width=0
        )
        header_frame.pack(fill="x", padx=0, pady=(0, 2))
        header_frame.pack_propagate(False)

        ctk.CTkLabel(
            header_frame,
            text="Настройки профиля",
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=40, pady=(25, 5), sticky="w")

        ctk.CTkLabel(
            header_frame,
            text="Персонализируйте ваши цели и предпочтения",
            font=ctk.CTkFont(family="Arial", size=16),
            text_color=self.colors["text_primary"]
        ).grid(row=1, column=0, padx=40, pady=(0, 25), sticky="w")

        main_container = ctk.CTkFrame(self.dialog, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=20)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(main_container)
        self.tabview.grid(row=0, column=0, sticky="nsew")

        self.tabview.configure(
            fg_color=self.colors["bg_primary"],
            segmented_button_fg_color=self.colors["primary_light"],
            segmented_button_selected_color=self.colors["accent"],
            segmented_button_selected_hover_color=self.colors["accent_dark"],
            segmented_button_unselected_color=self.colors["primary_light"],
            segmented_button_unselected_hover_color=self.colors["primary"],
            text_color=self.colors["text_primary"],
            text_color_disabled=self.colors["text_secondary"]
        )

        self.tab_personal = self.tabview.add("  Личные данные  ")
        self.tab_goals = self.tabview.add("  Цели  ")
        self.tab_preferences = self.tabview.add("  Предпочтения  ")

        for tab in [self.tab_personal, self.tab_goals, self.tab_preferences]:
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)

        self.setup_personal_tab()
        self.setup_goals_tab()
        self.setup_preferences_tab()

        self.setup_action_buttons()

    def setup_personal_tab(self):
        personal = self.profile.profile["personal"]

        container = ctk.CTkScrollableFrame(
            self.tab_personal,
            fg_color="transparent"
        )
        container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        container.grid_columnconfigure(0, weight=1)

        basic_card = ctk.CTkFrame(
            container,
            corner_radius=25,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"]
        )
        basic_card.grid(row=0, column=0, sticky="ew", padx=0, pady=10)
        basic_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            basic_card,
            text="Основная информация",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=30, pady=(25, 20))

        ctk.CTkLabel(
            basic_card,
            text="Пол:",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=1, column=0, sticky="w", padx=30, pady=10)

        self.gender_var = ctk.StringVar(value=personal["пол"])
        gender_frame = ctk.CTkFrame(basic_card, fg_color="transparent")
        gender_frame.grid(row=1, column=1, sticky="w", padx=30, pady=10)

        ctk.CTkRadioButton(
            gender_frame,
            text="Мужской",
            variable=self.gender_var,
            value="мужской",
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_dark"],
            text_color=self.colors["text_primary"]
        ).pack(side="left", padx=(0, 20))

        ctk.CTkRadioButton(
            gender_frame,
            text="Женский",
            variable=self.gender_var,
            value="женский",
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_dark"],
            text_color=self.colors["text_primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            basic_card,
            text="Возраст (лет):",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=2, column=0, sticky="w", padx=30, pady=10)

        self.age_entry = ctk.CTkEntry(
            basic_card,
            width=250,
            height=45,
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.colors["surface_light"],
            border_color=self.colors["border"],
            text_color=self.colors["text_primary"]
        )
        self.age_entry.insert(0, str(personal["возраст"]))
        self.age_entry.grid(row=2, column=1, sticky="w", padx=30, pady=10)

        ctk.CTkLabel(
            basic_card,
            text="Рост (см):",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=3, column=0, sticky="w", padx=30, pady=10)

        self.height_entry = ctk.CTkEntry(
            basic_card,
            width=250,
            height=45,
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.colors["surface_light"],
            border_color=self.colors["border"],
            text_color=self.colors["text_primary"]
        )
        self.height_entry.insert(0, str(personal["рост"]))
        self.height_entry.grid(row=3, column=1, sticky="w", padx=30, pady=10)

        ctk.CTkLabel(
            basic_card,
            text="Вес (кг):",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=4, column=0, sticky="w", padx=30, pady=10)

        self.weight_entry = ctk.CTkEntry(
            basic_card,
            width=250,
            height=45,
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.colors["surface_light"],
            border_color=self.colors["border"],
            text_color=self.colors["text_primary"]
        )
        self.weight_entry.insert(0, str(personal["вес"]))
        self.weight_entry.grid(row=4, column=1, sticky="w", padx=30, pady=10)

        ctk.CTkLabel(
            basic_card,
            text="Уровень активности:",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=5, column=0, sticky="w", padx=30, pady=10)

        self.activity_var = ctk.StringVar(value=personal["уровень_активности"])
        activity_menu = ctk.CTkOptionMenu(
            basic_card,
            values=["сидячий", "легкая", "умеренная", "высокая", "очень высокая"],
            variable=self.activity_var,
            width=250,
            height=45,
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.colors["surface_light"],
            button_color=self.colors["accent"],
            button_hover_color=self.colors["accent_dark"],
            text_color=self.colors["text_primary"],
            dropdown_font=ctk.CTkFont(family="Arial", size=13),
            dropdown_text_color=self.colors["text_primary"],
            dropdown_fg_color=self.colors["surface"],
            dropdown_hover_color=self.colors["primary_light"]
        )
        activity_menu.grid(row=5, column=1, sticky="w", padx=30, pady=10)

    def setup_goals_tab(self):
        personal = self.profile.profile["personal"]

        container = ctk.CTkScrollableFrame(
            self.tab_goals,
            fg_color="transparent"
        )
        container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        container.grid_columnconfigure(0, weight=1)

        goals_card = ctk.CTkFrame(
            container,
            corner_radius=25,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"]
        )
        goals_card.grid(row=0, column=0, sticky="ew", padx=0, pady=10)
        goals_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            goals_card,
            text="Цели питания",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=30, pady=(25, 20))

        ctk.CTkLabel(
            goals_card,
            text="Основная цель:",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=1, column=0, sticky="w", padx=30, pady=10)

        self.goal_var = ctk.StringVar(value=personal["цель"])
        goal_menu = ctk.CTkOptionMenu(
            goals_card,
            values=["похудение", "поддержание", "набор массы", "здоровое питание"],
            variable=self.goal_var,
            width=250,
            height=45,
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.colors["surface_light"],
            button_color=self.colors["accent"],
            button_hover_color=self.colors["accent_dark"],
            text_color=self.colors["text_primary"],
            dropdown_font=ctk.CTkFont(family="Arial", size=13),
            dropdown_text_color=self.colors["text_primary"],
            dropdown_fg_color=self.colors["surface"],
            dropdown_hover_color=self.colors["primary_light"]
        )
        goal_menu.grid(row=1, column=1, sticky="w", padx=30, pady=10)

        ctk.CTkLabel(
            goals_card,
            text="Целевой вес (кг):",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=2, column=0, sticky="w", padx=30, pady=10)

        self.target_weight_entry = ctk.CTkEntry(
            goals_card,
            width=250,
            height=45,
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.colors["surface_light"],
            border_color=self.colors["border"],
            text_color=self.colors["text_primary"]
        )
        self.target_weight_entry.insert(0, str(personal["целевой_вес"]))
        self.target_weight_entry.grid(row=2, column=1, sticky="w", padx=30, pady=10)

    def setup_preferences_tab(self):
        restrictions = self.profile.profile["ограничения"]
        preferences = self.profile.profile["предпочтения"]

        container = ctk.CTkScrollableFrame(
            self.tab_preferences,
            fg_color="transparent"
        )
        container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        container.grid_columnconfigure(0, weight=1)

        diet_card = ctk.CTkFrame(
            container,
            corner_radius=25,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"]
        )
        diet_card.grid(row=0, column=0, sticky="ew", padx=0, pady=10)
        diet_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            diet_card,
            text="Тип питания",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=30, pady=(25, 20))

        ctk.CTkLabel(
            diet_card,
            text="Тип питания:",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=1, column=0, sticky="w", padx=30, pady=10)

        self.diet_type_var = ctk.StringVar(value=restrictions["тип_питания"])
        diet_menu = ctk.CTkOptionMenu(
            diet_card,
            values=["стандартное", "вегетарианское", "веганское", "кето", "палео", "средиземноморское"],
            variable=self.diet_type_var,
            width=250,
            height=45,
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.colors["surface_light"],
            button_color=self.colors["accent"],
            button_hover_color=self.colors["accent_dark"],
            text_color=self.colors["text_primary"],
            dropdown_font=ctk.CTkFont(family="Arial", size=13),
            dropdown_text_color=self.colors["text_primary"],
            dropdown_fg_color=self.colors["surface"],
            dropdown_hover_color=self.colors["primary_light"]
        )
        diet_menu.grid(row=1, column=1, sticky="w", padx=30, pady=10)

        recipes_card = ctk.CTkFrame(
            container,
            corner_radius=25,
            fg_color=self.colors["surface"],
            border_width=1,
            border_color=self.colors["border"]
        )
        recipes_card.grid(row=1, column=0, sticky="ew", padx=0, pady=10)
        recipes_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            recipes_card,
            text="Предпочтения рецептов",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=30, pady=(25, 20))

        ctk.CTkLabel(
            recipes_card,
            text="Сложность рецептов:",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=1, column=0, sticky="w", padx=30, pady=10)

        self.difficulty_var = ctk.StringVar(value=preferences["сложность_рецептов"])
        difficulty_menu = ctk.CTkOptionMenu(
            recipes_card,
            values=["легкая", "средняя", "сложная"],
            variable=self.difficulty_var,
            width=250,
            height=45,
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.colors["surface_light"],
            button_color=self.colors["accent"],
            button_hover_color=self.colors["accent_dark"],
            text_color=self.colors["text_primary"],
            dropdown_font=ctk.CTkFont(family="Arial", size=13),
            dropdown_text_color=self.colors["text_primary"],
            dropdown_fg_color=self.colors["surface"],
            dropdown_hover_color=self.colors["primary_light"]
        )
        difficulty_menu.grid(row=1, column=1, sticky="w", padx=30, pady=10)

        ctk.CTkLabel(
            recipes_card,
            text="Доступность ингредиентов:",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=2, column=0, sticky="w", padx=30, pady=10)

        self.availability_var = ctk.StringVar(value=preferences["доступность_ингредиентов"])
        availability_menu = ctk.CTkOptionMenu(
            recipes_card,
            values=["обычные", "сезонные", "экзотические"],
            variable=self.availability_var,
            width=250,
            height=45,
            font=ctk.CTkFont(family="Arial", size=13),
            fg_color=self.colors["surface_light"],
            button_color=self.colors["accent"],
            button_hover_color=self.colors["accent_dark"],
            text_color=self.colors["text_primary"],
            dropdown_font=ctk.CTkFont(family="Arial", size=13),
            dropdown_text_color=self.colors["text_primary"],
            dropdown_fg_color=self.colors["surface"],
            dropdown_hover_color=self.colors["primary_light"]
        )
        availability_menu.grid(row=2, column=1, sticky="w", padx=30, pady=10)

    def setup_action_buttons(self):
        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Сохранить настройки",
            command=self.save_profile,
            height=50,
            font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_dark"],
            corner_radius=12,
            text_color=self.colors["surface"]
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=self.dialog.destroy,
            height=50,
            font=ctk.CTkFont(family="Arial", size=14),
            fg_color=self.colors["surface"],
            hover_color=self.colors["primary_light"],
            text_color=self.colors["text_primary"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border_accent"]
        ).pack(side="right")

    def save_profile(self):
        try:
            personal_updates = {
                "пол": self.gender_var.get(),
                "возраст": int(self.age_entry.get()),
                "рост": int(self.height_entry.get()),
                "вес": int(self.weight_entry.get()),
                "уровень_активности": self.activity_var.get(),
                "цель": self.goal_var.get(),
                "целевой_вес": int(self.target_weight_entry.get())
            }

            restrictions_updates = {
                "тип_питания": self.diet_type_var.get()
            }

            preferences_updates = {
                "сложность_рецептов": self.difficulty_var.get(),
                "доступность_ингредиентов": self.availability_var.get()
            }

            self.profile.update_personal(**personal_updates)
            self.profile.update_restrictions(**restrictions_updates)
            self.profile.update_preferences(**preferences_updates)

            messagebox.showinfo("Успех", "Настройки профиля успешно сохранены!")
            self.dialog.destroy()

        except ValueError as e:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных числовых значений")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении профиля: {str(e)}")