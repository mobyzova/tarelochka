import tensorflow as tf
from tensorflow.keras import layers, models
import os
import gc

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'


def create_fast_cnn_10_classes():
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(128, 128, 3)),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.2),

        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.3),

        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D(2, 2),
        layers.Dropout(0.4),

        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(10, activation='softmax')
    ])
    return model


train_path = 'E:\\FoodClassificationProject\\data\\processed\\train'
valid_path = 'E:\\FoodClassificationProject\\data\\processed\\validation'

train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1. / 255,
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.9, 1.1],
    fill_mode='nearest'
)

valid_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)

train_batches = train_datagen.flow_from_directory(
    train_path,
    target_size=(128, 128),
    batch_size=64,
    shuffle=True,
    class_mode='categorical',
    classes=['apple_pie', 'caesar_salad', 'dumplings', 'french_fries', 'hamburger',
             'chicken_curry', 'cup_cakes', 'pizza', 'sushi', 'ice_cream']
)

valid_batches = valid_datagen.flow_from_directory(
    valid_path,
    target_size=(128, 128),
    batch_size=64,
    shuffle=False,
    class_mode='categorical',
    classes=['apple_pie', 'caesar_salad', 'dumplings', 'french_fries', 'hamburger',
             'chicken_curry', 'cup_cakes', 'pizza', 'sushi', 'ice_cream']
)

model = create_fast_cnn_10_classes()

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy',
        patience=12,
        restore_best_weights=True,
        verbose=1,
        mode='max'
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-6,
        verbose=1
    ),
    tf.keras.callbacks.ModelCheckpoint(
        'E:\\FoodClassificationProject\\models\\fast_cnn_10_classes.h5',
        monitor='val_accuracy',
        save_best_only=True,
        mode='max'
    )
]

history = model.fit(
    train_batches,
    epochs=50,
    validation_data=valid_batches,
    callbacks=callbacks,
    verbose=1
)

model.save('E:\\FoodClassificationProject\\models\\my_final_fast_cnn_10_classes.h5')

gc.collect()
tf.keras.backend.clear_session()

final_acc = history.history['val_accuracy'][-1]
max_acc = max(history.history['val_accuracy'])
final_train_acc = history.history['accuracy'][-1]

print(f"Точность на обучении: {final_train_acc:.3f}")
print(f"Точность на валидации: {final_acc:.3f}")
print(f"Максимальная точность: {max_acc:.3f}")