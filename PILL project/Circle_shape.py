import cv2
import numpy as np
from image_processor import ImageProcessor

def Circle_shape(contour):
    # 윤곽선 근사화
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    # 타원으로 근사화
    ellipse = cv2.fitEllipse(approx)
    
    # 타원의 가로, 세로 길이와 각도
    (major_axis, minor_axis), angle = ellipse[1], ellipse[2]
    
    # 타원의 형태를 분석하여 타원과 원을 구분
    if abs(major_axis - minor_axis) < 10:
        return "Circle"
    else:
        return "Ellipse"
