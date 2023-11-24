import os
import mysql.connector
from mysql.connector import Error
import numpy as np
import tensorflow as tf
from image_processor import ImageProcessor
import cv2
import random
from tqdm import tqdm
import matplotlib.pyplot as plt

def fetch_image(image_name, connection):
    try:
        cursor = connection.cursor()
        query = "SELECT image FROM image_data WHERE file_name = %s"
        cursor.execute(query, (image_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"Error fetching image: {e}")
        return None
    
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
    
def load_data_and_labels(connection, max_images=15000, pixel_threshold=30):
    data = []
    labels = []
    image_count = 0
    # 데이터베이스에서 image_data 테이블의 file_name을 가져옵니다.
    try:
        cursor = connection.cursor()
        query = "SELECT file_name FROM image_data"
        cursor.execute(query)
        all_files = [item[0] for item in cursor.fetchall()]
    except Error as e:
        print(f"Error fetching file names from image_data: {e}")
        return None, None

    # tqdm 인스턴스 생성
    total_files_tqdm = tqdm(desc="Total Images Processed", total=len(all_files), position=0)
    saved_images_tqdm = tqdm(desc="Images Saved", total=max_images, position=1)
    for file_name in all_files:
        total_files_tqdm.update(1)
        if image_count >= max_images:
            break
        # 데이터베이스에서 이미지와 레이블 검색
        image_blob = fetch_image(file_name, connection)
        label = fetch_label(file_name, connection)
        if image_blob is not None and label is not None:
            # 이미지 데이터를 NumPy 배열로 변환
            nparr = np.frombuffer(image_blob, np.uint8)
            original_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if original_image is not None:
                processor = ImageProcessor(original_image)
                processed_image = processor.load_edged()
                if processed_image is not None:
                    # 흰색 픽셀의 수 계산
                    white_pixels = np.sum(processed_image == 255)
                    # 설정한 임계값보다 흰색 픽셀의 수가 적은 경우, 이미지를 건너뜀
                    if white_pixels < pixel_threshold:
                        continue
                    # 이미지 크기 조정
                    resized_image = cv2.resize(processed_image, (784, 784))
                    # 이미지 차원 확인 및 조정
                    if len(resized_image.shape) == 2:
                        resized_image = resized_image.reshape((784, 784, 1))
                    data.append(resized_image)
                    labels.append(label)
                    image_count += 1
                    saved_images_tqdm.update(1)
    total_files_tqdm.close()
    saved_images_tqdm.close()
    print("Number of images and labels loaded:", image_count)
    # 데이터 배열을 NumPy 배열로 변환
    data = np.array(data, dtype='float32') / 255.0
    labels = np.array(labels)
    # 데이터와 레이블을 무작위로 섞음
    indices = np.arange(len(data))
    np.random.shuffle(indices)
    data = data[indices]
    labels = labels[indices]
    print("Number of images and labels loaded:", image_count)
    print("Data shape:", data.shape)
    print("Labels shape:", labels.shape)
    return data, labels

def encode_labels(labels):
    label_mapping = {
        '원형': 0,
        '타원형': 1,
        '장방형': 2,
        '팔각형': 3,
        '육각형': 4,
        '오각형': 5,
        '마름모형': 6,
        '사각형' : 7
    }
    return np.array([label_mapping[label] for label in labels])

def evaluate_top_2_accuracy(model, val_data, val_labels):
    predictions = model.predict(val_data)
    top_2_predictions = np.argsort(predictions, axis=1)[:, -2:]
    correct_count = 0
    for i in range(len(val_labels)):
        if val_labels[i] in top_2_predictions[i]:
            correct_count += 1
    top_2_accuracy = correct_count / len(val_labels)
    return top_2_accuracy

def train_model(data, labels, validation_split=0.2):
    encoded_labels = encode_labels(labels)
    # 데이터셋 분리: 학습 데이터, 검증 데이터, 테스트 데이터
    train_split_index = int(len(data) * 0.6)
    test_val_split_index = int(len(data) * 0.8)
    train_data, test_val_data = data[:train_split_index], data[train_split_index:]
    train_labels, test_val_labels = encoded_labels[:train_split_index], encoded_labels[train_split_index:]
    val_split_index = int(len(test_val_data) * 0.5)
    val_data, test_data = test_val_data[:val_split_index], test_val_data[val_split_index:]
    val_labels, test_labels = test_val_labels[:val_split_index], test_val_labels[val_split_index:]
    # 모델 구조 정의
    input_shape = (784, 784, 1)  # 리사이즈된 이미지의 크기 및 채널 차원 추가
    num_classes = 8  # 알약 모양의 클래스
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=input_shape),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.BatchNormalization(),  # 배치 정규화 추가
        tf.keras.layers.Dropout(0.509),  # 드롭아웃 추가, 비율은 조정 가능
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    # 모델 컴파일
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.0004)  # 학습률 설정
    model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    # 모델 학습 (검증 데이터 추가)
    history = model.fit(train_data, train_labels, epochs=100, batch_size=32, validation_data=(val_data, val_labels))
    top_2_accuracy = evaluate_top_2_accuracy(model, val_data, val_labels)
    print(f"Top 2 Accuracy on Validation Data: {top_2_accuracy * 100:.2f}%")
    # Epochs의 범위를 설정
    epochs_range = range(1, len(history.history['loss']) + 1)
    # Loss와 Accuracy 그래프 생성
    plt.figure(figsize=(12, 4))
    # Loss 그래프
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, history.history['loss'], label='Training Loss')
    plt.plot(epochs_range, history.history['val_loss'], label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    # Accuracy 그래프
    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, history.history['accuracy'], label='Training Accuracy')
    plt.plot(epochs_range, history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.legend()
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    # 그래프 표시
    plt.show()
    return model, test_data, test_labels

def evaluate_accuracy(model, test_data, test_labels):
    print(test_data.shape)
    predictions = model.predict(test_data)
    # 상위 1개 예측 정확도
    top_1_predictions = np.argmax(predictions, axis=1)
    top_1_accuracy = np.sum(top_1_predictions == test_labels) / len(test_labels)
    # 상위 2개 예측 정확도
    top_2_predictions = np.argsort(predictions, axis=1)[:, -2:]
    top_2_correct_count = 0
    for i in range(len(test_labels)):
        if test_labels[i] in top_2_predictions[i]:
            top_2_correct_count += 1
    top_2_accuracy = top_2_correct_count / len(test_labels)
    return top_1_accuracy, top_2_accuracy
def main():
    image_directory = 'D:\\data_of_ml\\dataset\\training_set\\data'
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
    # 데이터와 레이블을 로드하는 함수 호출
    data, labels = load_data_and_labels(connection)
    model, test_data, test_labels = train_model(data, labels)
    top_1_accuracy, top_2_accuracy = evaluate_accuracy(model, test_data, test_labels)
    print(f"Top 1 Accuracy on Test Data: {top_1_accuracy * 100:.2f}%")
    print(f"Top 2 Accuracy on Test Data: {top_2_accuracy * 100:.2f}%")
    # 사용자에게 모델 저장 여부를 묻는 부분
    save_model = input("Do you want to save model (yes/no): ")
    if save_model.lower() == 'yes':
        model.save('D:\\data_of_ml\\dataset\\softmax_modelv2.h5')  # 모델 저장
    connection.close()
if __name__ == '__main__':
    main()