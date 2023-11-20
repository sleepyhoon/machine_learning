import os
import mysql.connector
from mysql.connector import Error
import numpy as np
import tensorflow as tf
from image_processor import ImageProcessor  # 가정: ImageProcessor가 이 파일에 정의되어 있음\
import cv2

def fetch_label(image_name, connection):
    try:
        cursor = connection.cursor()
        query = "SELECT drug_shape FROM label_data WHERE file_name = %s"
        cursor.execute(query, (image_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"Error fetching label: {e}")
        return None

def load_data_and_labels(image_directory, connection):
    processor = ImageProcessor()
    data = []
    labels = []

    for subdir, _, files in os.walk(image_directory):
        for file in files:
            if file.endswith('.png'):
                image_path = os.path.join(subdir, file)
                processed_image = processor.load_edged(image_path)
                label = fetch_label(file, connection)

                if processed_image is not None and label is not None:
                    data.append(processed_image)
                    labels.append(label)

    return np.array(data), np.array(labels)
def encode_labels(labels):
    label_mapping = {
        '원형': 0,
        '타원형': 1,
        '장방형': 2,  # 원형과 동일하게 취급한다고 했으므로 0을 할당할 수도 있음
        '팔각형': 3,
        '육각형': 4,
        '오각형': 5,
        '마름모형': 6
    }
    return np.array([label_mapping[label] for label in labels])

def train_model(data, labels):
    # 레이블 인코딩
    encoded_labels = encode_labels(labels)
    input_shape = (28, 28)  # 리사이즈된 이미지의 크기
    num_classes = 7  # 알약 모양의 클래스 
    # 모델 구조 정의
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=input_shape),  # 이미지를 1D 배열로 변환
        tf.keras.layers.Dense(num_classes, activation='softmax')  # num_classes는 분류하려는 클래스의 수
    ])

    # 모델 컴파일
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # 모델 학습
    model.fit(data, encoded_labels, epochs=10)

    return model


def main():
    image_directory = 'PILL project\train'
    db_config = {
        'host': '182.210.67.8',
        'user': 'user1',
        'password': '1111',
        'database': 'pilldata'
    }

    try:
        connection = mysql.connector.connect(**db_config)
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return

    data, labels = load_data_and_labels(image_directory, connection)
    model = train_model(data, labels)

    connection.close()

if __name__ == '__main__':
    main()