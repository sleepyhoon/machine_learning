import tensorflow as tf
from keras import layers, models
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
import os

# 데이터셋 경로 설정
dataset_path = "PILL project"
train_path = os.path.join(dataset_path, "train")
test_path = os.path.join(dataset_path, "ttest")

# CNN 모델 정의
model = models.Sequential()
model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Flatten())
model.add(layers.Dense(128, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

# 모델 컴파일
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 이미지 데이터 증강을 위한 ImageDataGenerator 설정
train_datagen = ImageDataGenerator(rescale=1./255,
                                   shear_range=0.2,
                                   zoom_range=0.2,
                                   horizontal_flip=True)

test_datagen = ImageDataGenerator(rescale=1./255)

# 데이터 로딩 및 증강
train_generator = train_datagen.flow_from_directory(train_path, target_size=(64, 64), batch_size=32, class_mode='binary')
test_generator = test_datagen.flow_from_directory(test_path, target_size=(64, 64), batch_size=32, class_mode='binary')

# 모델 학습
model.fit(train_generator, epochs=10, validation_data=test_generator)

# 테스트 이미지로 모델 테스트
img = image.load_img(test_path, target_size=(64, 64))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
img_array /= 255.0

prediction = model.predict(img_array)
if prediction[0] > 0.5:
    print("이 알약은 A 형태입니다.")
else:
    print("이 알약은 B 형태입니다.")
