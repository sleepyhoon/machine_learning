import cv2
import matplotlib.pyplot as plt
from rembg import remove
import numpy as np

'''
HOW TO USE
from image_processor import ImageProcessor
processor = ImageProcessor([YOUR IMAGE])
processor.load_edged()  -> 윤곽선 이미지파일
processor.load_crop()   -> 알약 확대
processor.load_remove_bg() -> 배경제거
processor.load_blur()   -> blur처리 된 이미지
'''
class ImageProcessor:
    def __init__(self, original_image):
        self.original_image = original_image
        self.process_image()
        
    def rotate_image(self, angle):
        (h, w) = self.original_image.shape[:2]
        (cx, cy) = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
        self.original_image = cv2.warpAffine(self.original_image, M, (w, h))
    

    def preprocess_image(self) :
        self.image_remove_bg = remove(self.original_image)
        self.image_remove_gray = cv2.cvtColor(self.image_remove_bg, cv2.COLOR_BGR2GRAY)
        self.image_blur = cv2.GaussianBlur(self.image_remove_gray, (5,5), sigmaX = 0)
        ret, self.thresh = cv2.threshold(self.image_blur, 127, 255, cv2.THRESH_BINARY)
        self.image_edged = cv2.Canny(self.image_blur, 10, 250)

    
    def draw_binding_box(self):
        contours, _ = cv2.findContours(self.image_edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.all_points = []
        for contour in contours:
            for point in contour:
                self.all_points.extend(point)
        if self.all_points:
                self.all_points = np.array(self.all_points).squeeze()
                rect = cv2.minAreaRect(self.all_points)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(self.image_edged, [box], 0, (255,255,255), 2)
    
    
    def crop_image(self):
        x, y, w, h = cv2.boundingRect(self.all_points)
        self.cropped_image = self.original_image[y:y+h, x:x+w]
    
    def display_image(self):
        cv2.imshow('Image', self.original_image)
        cv2.imshow('Remove Background', self.image_remove_bg)
        cv2.imshow('Edged', self.image_edged)
        cv2.imshow('Cropped Image', self.cropped_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def process_image(self):
        self.preprocess_image()
        self.draw_binding_box()
        self.crop_image()
        
    def load_edged(self):
        return self.image_edged

    def load_cropped(self):
        return self.cropped_image

    def load_remove_bg(self):
        return self.image_remove_bg

    def load_blur(self):
        return self.image_blur