import tensorflow as tf
from tensorflow.keras import layers, models
import os
import gc

# Настройки для тихой работы TensorFlow и эффективного использования GPU
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Убираем лишние сообщения
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Отключаем оптимизации для совместимости
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'  # Экономно используем память GPU


# Создаем архитектуру нейронной сети для распознавания еды
def create_fast_cnn_10_classes():
    model = models.Sequential([
        # Первый блок - ищем простые признаки (края, углы)
        layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(128, 128, 3)),
        layers.BatchNormalization(),  # Стабилизируем обучение
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D(2, 2),  # Уменьшаем размер в 2 раза
        layers.Dropout(0.2),  # Защита от запоминания - выключаем 20% нейронов

        # Второй блок - ищем сложные признаки (формы, текстуры)
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.3),  # Увеличиваем защиту до 30%

        # Третий блок - ищем целые объекты (пицца, гамбургер)
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.4),  # Максимальная защита - 40%

        # Преобразуем карты признаков в вектор для классификации
        layers.GlobalAveragePooling2D(),

        # Полносвязные слои - принимаем окончательное решение
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(10, activation='softmax')  # 10 классов еды - выходные вероятности
    ])
    return model


# Пути к данным - обучающие и проверочные изображения
train_path = 'E:\\FoodClassificationProject\\data\\processed\\train'
valid_path = 'E:\\FoodClassificationProject\\data\\processed\\validation'

# Подготовка данных: для обучения добавляем искажения (аугментация)
train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1. / 255,  # Нормализуем цвета от 0-255 к 0-1
    rotation_range=15,  # Поворачиваем изображения
    width_shift_range=0.1,  # Сдвигаем по ширине
    height_shift_range=0.1,  # Сдвигаем по высоте
    zoom_range=0.2,  # Увеличиваем/уменьшаем
    horizontal_flip=True,  # Отражаем по горизонтали
    brightness_range=[0.9, 1.1],  # Меняем яркость
    fill_mode='nearest'  # Заполняем пустоты ближайшими пикселями
)

# Для проверки только нормализуем - без искажений
valid_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)

# Создаем потоки данных из папок
train_batches = train_datagen.flow_from_directory(
    train_path,
    target_size=(128, 128),  # Приводим все изображения к одному размеру
    batch_size=64,  # Обрабатываем по 64 изображения за раз
    shuffle=True,  # Перемешиваем для лучшего обучения
    class_mode='categorical',  # Многоклассовая классификация
    classes=['apple_pie', 'caesar_salad', 'dumplings', 'french_fries', 'hamburger',
             'chicken_curry', 'cup_cakes', 'pizza', 'sushi', 'ice_cream']  # Наши 10 видов еды
)

# Валидационные данные - без перемешивания
valid_batches = valid_datagen.flow_from_directory(
    valid_path,
    target_size=(128, 128),
    batch_size=64,
    shuffle=False,  # Не перемешиваем для честной оценки
    class_mode='categorical',
    classes=['apple_pie', 'caesar_salad', 'dumplings', 'french_fries', 'hamburger',
             'chicken_curry', 'cup_cakes', 'pizza', 'sushi', 'ice_cream']
)

# Создаем и настраиваем модель
model = create_fast_cnn_10_classes()

# Компилируем модель - настраиваем процесс обучения
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),  # Алгоритм оптимизации
    loss='categorical_crossentropy',  # Функция потерь - измеряем ошибки
    metrics=['accuracy']  # Следим за точностью
)

# Система автоматического управления обучением
callbacks = [
    # Останавливаем обучение, если нет улучшений
    tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy',  # Следим за точностью на проверке
        patience=12,  # Ждем 12 эпох без улучшений
        restore_best_weights=True,  # Возвращаем лучшие веса
        verbose=1,
        mode='max'  # Стремимся максимизировать точность
    ),
    # Автоматически уменьшаем скорость обучения при застое
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',  # Следим за ошибкой
        factor=0.5,  # Уменьшаем скорость обучения в 2 раза
        patience=5,  # Ждем 5 эпох
        min_lr=1e-6,  # Минимальная скорость обучения
        verbose=1
    ),
    # Сохраняем лучшую модель во время обучения
    tf.keras.callbacks.ModelCheckpoint(
        'E:\\FoodClassificationProject\\models\\fast_cnn_10_classes.h5',
        monitor='val_accuracy',
        save_best_only=True,  # Сохраняем только когда есть улучшение
        mode='max'
    )
]

# Запускаем обучение
history = model.fit(
    train_batches,
    epochs=50,  # Максимум 50 проходов по данным
    validation_data=valid_batches,  # Проверяем на отдельной выборке
    callbacks=callbacks,  # Используем наши автоматические помощники
    verbose=1  # Показываем прогресс
)

# Сохраняем окончательную модель
model.save('E:\\FoodClassificationProject\\models\\my_final_fast_cnn_10_classes.h5')

# Очищаем память
gc.collect()
tf.keras.backend.clear_session()

# Анализируем результаты
final_acc = history.history['val_accuracy'][-1]  # Последняя точность на проверке
max_acc = max(history.history['val_accuracy'])  # Лучшая точность за все время
final_train_acc = history.history['accuracy'][-1]  # Последняя точность на обучении

# Выводим итоги
print(f"Точность на обучении: {final_train_acc:.3f}")
print(f"Точность на валидации: {final_acc:.3f}")
print(f"Максимальная точность: {max_acc:.3f}")