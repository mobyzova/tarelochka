import os
import shutil
from sklearn.model_selection import train_test_split

# Пути к данным: исходные, для обучения и для проверки
data_dir = 'E:\\FoodClassificationProject\\data\\raw'
train_dir = 'E:\\FoodClassificationProject\\data\\processed\\train'
validation_dir = 'E:\\FoodClassificationProject\\data\\processed\\validation'

# Создаем папки если их нет
os.makedirs(train_dir, exist_ok=True)
os.makedirs(validation_dir, exist_ok=True)

# Находим все классы (папки с названиями еды)
class_names = [d for d in os.listdir(data_dir)
               if os.path.isdir(os.path.join(data_dir, d))]

print(f"Найдено классов: {len(class_names)}")
print(f"Список классов: {class_names}")

# Обрабатываем каждый класс отдельно
for class_name in class_names:
    class_dir = os.path.join(data_dir, class_name)
    train_class_dir = os.path.join(train_dir, class_name)
    validation_class_dir = os.path.join(validation_dir, class_name)

    # Создаем папки для этого класса
    os.makedirs(train_class_dir, exist_ok=True)
    os.makedirs(validation_class_dir, exist_ok=True)

    # Находим все изображения в классе
    image_files = [f for f in os.listdir(class_dir)
                   if f.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'))]

    print(f"Класс '{class_name}': {len(image_files)} изображений")

    # Пропускаем классы с слишком малым количеством изображений
    if len(image_files) < 2:
        print(f"Пропуск класса '{class_name}': слишком мало изображений ({len(image_files)})")
        continue

    # ДЕЛИМ ДАННЫЕ: 80% на обучение, 20% на проверку
    train_files, validation_files = train_test_split(
        image_files,
        test_size=0.2,      # 20% на валидацию
        random_state=42     # Для воспроизводимости результатов
    )

    # Копируем обучающие изображения
    for file in train_files:
        src = os.path.join(class_dir, file)
        dst = os.path.join(train_class_dir, file)
        shutil.copy(src, dst)

    # Копируем проверочные изображения
    for file in validation_files:
        src = os.path.join(class_dir, file)
        dst = os.path.join(validation_class_dir, file)
        shutil.copy(src, dst)

    print(f"'{class_name}': {len(train_files)} train, {len(validation_files)} validation")

print("Разделение данных завершено!")
print(f"Итого: {len(class_names)} классов обработано")