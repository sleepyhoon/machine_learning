import numpy as np
import mysql.connector
from mysql.connector import Error
import tensorflow as tf
'''
색,모양,텍스트 순으로 입력받고 먼저 들어오는 것을 신뢰도가 높게 설정한다.

색은 좌우를 나누어서 2개,2개씩 입력받으며(상위 2개의 색),만약 하나의 색이라고 인식하면 2개만 입력받음
색을 a1,a2,b1,b2라고 하면 (a,b),(b,a) 모두 검색해서 오른쪽 왼쪽 색을 확인한다. a1,a2의 순서도 바꿔야 하나?
일단 a,b 순서를 바꿔서 진행하도록 하자.
가중치는 a1,b1 으로 구성된 알약은 4,
a2,b2를 하나 가지고 있는 알약은 2,
a2,b2를 모두 가지고 있는 알약은 1로 세팅하였다.

색을 이용해서 입력받고, 필터링한 후 모양도 추정되는 상위 2가지를 입력받고,
마찬가지로 1순위 모양을 가진 알약은 가중치 4,
2순위 모양을 가진 알약은 가중치 1로 설정하였다
(모양의 경우 정확도가 1가지 모양으로만 해도 90프로에 육박하고, 2가지 모양을 썻을때보다 정확도가 
3~4%만 차이나기 때문에 굳이 하지 않아도 될지도 모른다.)

색과 모양으로 예외처리를 하고나서, 마지막으로 텍스트로 필터링을 진행한다. 문자열로 입력받을지, 클래스로 입력받을지 아직 정하지 않음.
그래서 정확한 로직은 나중에 구현할 예정이다.
간단하게 짜보자면 입력받은 텍스트와 실제 텍스트를 비교해서 (물론 앞뒤를 구분하여 따로 비교해야한다) 유사도가 
가장 높은 상위 5개(일단 임의로 설정)를 출력한다.
'''
# 색깔을 정수 class로 변환시켜줌. 필요없는 색은 제거해도됨.
def encode_colors(colors):
    color_mapping = {
        '하양': 0,
        '노랑': 1,
        '주황': 2,
        '분홍': 3,
        '빨강': 4,
        '갈색': 5,
        '연두': 6,
        '초록': 7,
        '청록': 8,
        '파랑': 9,
        '남색': 10,
        '자주': 11,
        '보라': 12,
        '회색': 13,
        '검정': 14,
        '투명': 15, # 투명은 구분하기 어려워 보여서 제외 시켜도 될듯
    }
    return np.array([color_mapping[color] for color in colors])

# 모양을 정수 class로 변환시켜줌
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

    
def text_identify(text):
    # 인식한 텍스트를 전달받는 함수. 아직 어떻게 구현할지 모름
    pass


def WhatIsColor(color_class,weight,cursor):
    color_weight = {} # 각 색깔의 가중치를 기억하는 dict
    # 좌우가 색이 다른 알약
    if(len(color_class)==4):
        '''
        label_class = [a1,a2,b1,b2] 라고 할 때,
        
        case 1 -> (a1,a2) (b1,b2) 으로 선택(좌우)
        1. (a1,b1) or (b1,b2) 의 색을 가진 알약 추출 : 가중치 4
        select * from label_data
        where color1 = a1 and color2 = b1
        2. a2 or b2를 하나만 가지고 있는 알약 추출 : 가중치 2
        select * from label_data
        where a2 or b2 in label_data
        3. a2,b2을 모두 가진 알약 추출 : 가중치 1
        select * from label_data
        where color1 = a2 and color2 = b2
        
        case 2 -> (b1,b2) (a1,a2) 으로 선택(좌우)
        1. ...
        2. ...
        3. ...
        
        '''
    # 좌우의 색이 같은 알약
    elif(len(color_class)==2):
        '''
        약 이름 모양 색 텍스트 가중치만으로 이루어진 테이블. 추가적 필요한것.
        if 색1 = 1순위:
            가중치 + 4
        elif 색1 = 2순위:
            가중치 + 1
        '''
        query = ("select color1,color2,drug_shape,print_front,print_back "
                 "from label_data "
                 "where color1 = %s"
                 )
        cursor.execute(query, (color_class[0],))
        color_weight = cursor.fetchall() # 리스트이고 각 구성원소는 튜플이다. (color1,color2,drug_shape,print_front,print_back) 들어있음.
        for row in color_weight:
            print(row)

def WhatIsShape(label,cursor):
    '''
    if 모양 = 1순위:
        가중치 + 4
    elif 모양 = 2순위:
        가중치 + 2
    else:
        가중치 - 2
    '''

def WhatIsText():
    pass

def main():
    connection = mysql.connector.connect(
        host='182.210.67.8',
        user='user1',
        password='1111',
        database='pilldata'
    )
    try:
        connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return

    # 커서 생성
    cursor = connection.cursor()
    
    # 사진 속 알약의 feature를 입력받음.
    input_color = [0,1] # 하양과 노랑
    input_shape = [0,1] # 원형과 타원형
    input_text = ["",""] # 글씨가 없다고 가정
    
    # 일단 임의로 가중치를 설정해놓음
    weight = [4,2,1]
    
    label_class = encode_labels(input_shape) # 인식한 모양을 encoding
    color_class = encode_colors(input_color) # 인식한 색깔을 encoding
    
    answer_color = WhatIsColor(label_class,weight,cursor)
    
    connection.close()
    
if __name__ == '__main__':
    main()
