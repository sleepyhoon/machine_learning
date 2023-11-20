from colorthief import ColorThief
from image_processor import ImageProcessor
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import cv2
'''
CODE 설명 주석

1. image = 우리가 테스트할 이미지 파일을 numpy 배열로 변환해서 저장

2. processor = 알맞게 전처리된 이미지(4가지 종류) 지금은 정확도가 가장 높다고 생각되는 cropped.image를 사용

3. 색깔 추출을 하는 Colorthief 함수는 매개변수로 이미지 경로나 ByteIO를 요구하기에 numpy 배열인 image의 형변환
필요하다. 
'''

image = cv2.imread('PILL project\exam_image.jpg') # 주석 1번
processor = ImageProcessor(image) # 주석 2번

processor.display_image() # 전처리된 이미지 4개를 모두 볼 수 있음

processor.cropped_image = cv2.cvtColor\
    (processor.cropped_image, cv2.COLOR_BGR2RGB)# cv2의 BGR 형식에서 RGB 형식으로 변환

# processor.cropped_image가 없을 경우에 대한 확인
if processor.cropped_image is not None:
    
    # processor.cropped_image가 NumPy 배열이므로 PIL로 변환
    cropped_image_pil = Image.fromarray(processor.cropped_image)
    
    # PIL 이미지를 BytesIO 객체에 저장
    image_bytesio = BytesIO()
    cropped_image_pil.save(image_bytesio, format='JPEG')
    
    # 주석 3번. ColorTheif를 이용해서 가장 많이 사용된 색 5개 추출
    ct = ColorThief(image_bytesio)
    palette = ct.get_palette(color_count=5)
    
    plt.imshow([[palette[i] for i in range(5)]])
    # 각 RGB 값 출력
    for i, rgb in enumerate(palette, 1):
        print(f"Color {i} (RGB): {rgb}") # 각 색의 RGB값 출력
    plt.show()
else: # 이미지가 없는 경우 
    print("Error: Cropped image is None.")
