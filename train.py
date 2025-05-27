import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
import json

folder_path = r'C:\Users\ADITYA\Desktop\chatbot\Chatbot\img'

if not os.path.exists(folder_path):
    raise FileNotFoundError(f"The directory {folder_path} does not exist. Please check the path.")

train_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train_generator = train_datagen.flow_from_directory(
    folder_path,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='training'
)

validation_generator = train_datagen.flow_from_directory(
    folder_path,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(1024, activation='relu'),
    layers.Dense(len(train_generator.class_indices), activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(
    train_generator,
    epochs=10,
    validation_data=validation_generator
)

model_path = r'C:/Users/ADITYA/Desktop/chatbot/Chatbot/image_classifier_model.h5'
model.save(model_path)
print(f"Model training complete and saved as '{model_path}'.")

class_indices = train_generator.class_indices
class_indices_path = r'C:/Users/ADITYA/Desktop/chatbot/Chatbot/class_indices.json'
with open(class_indices_path, 'w') as f:
    json.dump(class_indices, f)
print(f"Class indices saved as '{class_indices_path}'.")
