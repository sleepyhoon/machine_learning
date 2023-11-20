import cv2
import numpy as np
from rembg import remove
from Circle_shape import Circle_shape

image = cv2.imread('PILL project/ttest/exam_image10.png') 
# 새로운 크기 지정 (가로, 세로)
new_size = (200,200)

# 이미지 크기 조절
resized_image = cv2.resize(image, new_size)
image_remove_bg = remove(resized_image)
gray = cv2.cvtColor(image_remove_bg, cv2.COLOR_BGR2GRAY)
gray = cv2.bitwise_not(gray) # 객체보다 배경이 밝은 경우 이미지 반전

# 가우시안 블러 적용 (노이즈 제거)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# 케니 에지 검출
edges = cv2.Canny(blurred, 50, 150)

_, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# 윤곽선 찾기
contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

# 윤곽선을 그린 이미지 생성 (검은 배경)
contour_image = np.zeros_like(image)
contour_image = cv2.resize(contour_image, new_size)

maxIdx = 0
idx = 0
maxArea = 0.0

for cnt in contours:
    area = cv2.contourArea(cnt)
    if maxArea < area:
        maxIdx = idx
        maxArea = area
    idx = idx + 1
# 각 윤곽선을 이미지에 그리기
cv2.drawContours(contour_image, contours, idx-1, (0, 0, 255), 2)  # -1은 모든 윤곽선을 그리라는 의미
# 윤곽선을 그린 이미지를 함께 출력
cv2.imshow('Contour Image', contour_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

shape = ''
for contour in contours:
        
    # 윤곽선 근사화
    epsilon = 0.03 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    # 근사화된 윤곽선의 꼭짓점 개수
    vertices = len(approx)
    
    # 객체의 형태에 따라 분류(장방형이랑 타원형은 같은 모양으로 취급하자)
    if vertices <= 2:
        print(vertices)
        shape = 'fault'
    if vertices == 3:
        shape = "Triangle"
    if vertices == 4:
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = float(w) / h
        shape = "Square" if aspect_ratio >= 0.95 and aspect_ratio <= 1.05 else "Rectangle(=Ellipse)"
    if vertices >= 5:
        print(vertices)
        shape = Circle_shape(contour)
    print(shape)
