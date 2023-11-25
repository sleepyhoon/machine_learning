import mysql.connector
from mysql.connector import Error

'''
색,모양,텍스트 순으로 입력받고 먼저 들어오는 것을 신뢰도가 높게 설정한다.

색은 좌우를 나누어서 2개,2개씩 입력받으며(상위 2개의 색),만약 하나의 색이라고 인식하면 2개만 입력받음
색을 a1,a2,b1,b2라고 하면 
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


def find_key(dictionary, value):
    return next((key for key, val in dictionary.items() if val == value), None)

# color decoding 해주기
def decoding_to_color(input_color,find_key):
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
        '':-1
    }
    mapped_colors = [find_key(color_mapping, index) for index in input_color]
    return mapped_colors

# label decoding
def decoding_to_label(input_shape,find_key):
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
    mapped_label = [find_key(label_mapping,index) for index in input_shape]
    return mapped_label

# 색은 무조건 왼쪽 1순위 색, 왼쪽 2순위 색, 오른쪽 1순위 색, 오른쪽 2순위 색으로 받고 색이 1개인 알약은 오른쪽 1,2번째는 -1로 반환
def WhatIsColor(color_class,weight,cursor):
    color_weight = {} # 각 색깔의 가중치를 기억하는 dict
    
    query = ("select color_class1,color_class2,drug_shape,print_front,print_back,priority "
            "from pill_data "
            )
    cursor.execute(query)
    color_weight = cursor.fetchall() # 리스트이고 각 구성원소는 튜플이다.

    # 튜플의 리스트로 변환
    color_weight_list = [list(row) for row in color_weight]
    
    if color_class[2] == -1 and color_class[3] == -1: # 색이 1가지 인 경우
        for i in range(len(color_weight_list)):
            if color_weight_list[i][0] == color_class[0]:
                color_weight_list[i][5] += weight[0] # +4
            elif color_weight_list[i][0] == color_class[1]:
                color_weight_list[i][5] += weight[1] # +1
    else: # 색이 2가지인 경우
        for i in range(len(color_weight_list)):
            if color_weight_list[i][0] == color_class[0] and color_weight_list[i][1] == color_class[2]: # 1순위들 모임
                color_weight_list[i][5] += weight[0]
            elif color_weight_list[i][0] == color_class[1] and color_weight_list[i][1] == color_class[3]: # 2순위들 모임
                color_weight_list[i][5] += weight[2]
            else: # 1,2순위 색깔들 모임
                color_weight_list[i][5] += weight[1]
    return color_weight_list
# 모양은 1순위와 2순위를 입력받음.
def WhatIsShape(list,shape_class,weight):
    for i in range(len(list)):
        if list[i][2] == shape_class[0]: # 1순위 모양
            list[i][5] += weight[0]
        elif list[i][2] == shape_class[1]: # 2순위 모양
            list[i][5] += weight[2]
        else: # 그외의 모양
            list[i][5] -= 2
    # priority를 기준으로 정렬
    sorted_color_weight = sorted(list, key=lambda x: x[5],reverse=True)

    # 상위 5개만 추출
    top_5_color_weight = sorted_color_weight[:5]

    # 결과 확인
    for row in top_5_color_weight:
        print(row)

def WhatIsText(input_text,cursor):
    # 인식한 텍스트를 전달받는 함수. 문자열로 입력받는다고 생각하자. ['a','b'] 뭐가 앞뒤인지 모르기 때문에 둘다 해봐야할듯
    query = "SELECT print_front, print_back, priority FROM pill_data WHERE (print_front LIKE %s AND print_back LIKE %s) \
        OR (print_front LIKE %s AND print_back LIKE %s)"
    cursor.execute(query, (input_text[0], input_text[1], input_text[1], input_text[0]))

    text = cursor.fetchall()
    # 튜플의 리스트로 변환
    text_weight_list = [list(row) for row in text]
    for i in range(len(text_weight_list)):
        text_weight_list[i][2] += 4
    for row in text_weight_list:
        print(row)

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
    input_color = [0,1,-1,-1] # 하양과 노랑
    input_shape = [0,1] # 원형과 타원형
    input_text = ["","YH"] # 글씨가 없다고 가정
    
    # 일단 임의로 가중치를 설정해놓음
    weight = [4,2,1]
    
    color_class = decoding_to_color(input_color,find_key) 
    label_class = decoding_to_label(input_shape,find_key)
    list = WhatIsColor(color_class,weight,cursor)
    WhatIsShape(list,label_class,weight)
    WhatIsText(input_text,cursor)
    connection.close()
    
if __name__ == '__main__':
    main()
