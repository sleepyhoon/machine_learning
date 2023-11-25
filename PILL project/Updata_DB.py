import mysql.connector
from mysql.connector import Error
import logging
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

# decoding 과정에서 사용하는 함수. 값을 이용해서 키를 찾아준다.
def find_key(dictionary, value):
    return next((key for key, val in dictionary.items() if val == value), None)

# color decoding
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

# 입력받은 색깔을 이용해서 db에 가중치 적용
def Update_Weight_Color(input_color,weight,connection):
    cursor = connection.cursor()
    
    try:
        if input_color[2] == '' and input_color[3] == '': # 색이 1가지 인 경우
            query = "UPDATE pill_data SET priority = priority + %s WHERE color_class1 = %s"
            cursor.execute(query, (weight[0],input_color[0],))
            query = "UPDATE pill_data SET priority = priority + %s WHERE color_class1 = %s"
            cursor.execute(query, (weight[0],input_color[1],))
        else: # 색이 2가지인 경우
        # 1순위 색깔들 모임
            query = "UPDATE pill_data SET priority = priority + %s WHERE color_class1 = %s and color_class2 = %s"
            cursor.execute(query, (weight[0],input_color[0], input_color[2],))
            # 1,2순위 색깔들 모임
            query = "UPDATE pill_data SET priority = priority + %s WHERE color_class1 = %s and color_class2 = %s"
            cursor.execute(query, (weight[0],input_color[0], input_color[3],))
            query = "UPDATE pill_data SET priority = priority + %s WHERE color_class1 = %s and color_class2 = %s"
            cursor.execute(query, (weight[0],input_color[1], input_color[2],))
            # 2순위 색깔들 모임
            query = "UPDATE pill_data SET priority = priority + %s WHERE color_class1 = %s and color_class2 = %s"
            cursor.execute(query, (weight[0],input_color[1], input_color[3],))
            
        # 변경사항을 모든 쿼리에 대해 하나의 트랜잭션으로 묶음
        connection.commit()
    
    except mysql.connector.Error as err:
        # 어떠한 예외가 발생하면 롤백
        logging.error(f"MySQL Error: {err}")
        connection.rollback()
    finally:
        cursor.close()

# 입력받은 모양을 이용해서 db에 가중치 적용
def Update_Weight_Shape(input_shape,weight,connection):
    cursor = connection.cursor()
    
    try:
        query = "UPDATE pill_data SET priority = priority + %s WHERE drug_shape = %s"
        cursor.execute(query, (weight[0],input_shape[0],))
        query = "UPDATE pill_data SET priority = priority + %s WHERE drug_shape = %s"
        cursor.execute(query, (weight[0],input_shape[1],))

        # 변경사항을 모든 쿼리에 대해 하나의 트랜잭션으로 묶음
        connection.commit()
    except mysql.connector.Error as err:
        # 어떠한 예외가 발생하면 롤백
        logging.error(f"MySQL Error: {err}")
        connection.rollback()
    finally:
        cursor.close()

# 입력받은 텍스트을 이용해서 db에 가중치 적용
def Update_Weight_Text(input_text,weight,connection):
    cursor = connection.cursor()

    try:
        query = "UPDATE pill_data SET priority = priority + %s WHERE (print_front LIKE %s AND print_back LIKE %s) \
                 OR (print_front LIKE %s AND print_back LIKE %s)"
        cursor.execute(query, (weight[0], input_text[0], input_text[1], input_text[1], input_text[0]))

        # 변경사항을 모든 쿼리에 대해 하나의 트랜잭션으로 묶음
        connection.commit()   
    except mysql.connector.Error as err:
        # 어떠한 예외가 발생하면 롤백
        logging.error(f"MySQL Error: {err}")
        connection.rollback()
    finally:
        cursor.close()

def Choose_Top_5(connection):
    cursor = connection.cursor()
    try:
        query = "select * from pill_data order by priority desc limit 5"
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            print(row)
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    finally:
        cursor.close()

def Initialization(connection):
    try:
        # 시작하기전 모든 가중치를 0으로 설정
        cursor = connection.cursor()
        query = "update pill_data set priority = 0"
        cursor.execute(query)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    finally:
        cursor.close()
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

    # 사진 속 알약의 feature를 입력받음.
    input_color = [0,1,-1,-1] # 하양과 노랑
    input_shape = [0,1] # 원형과 타원형
    input_text = ["G","G"] # 임의의 글씨
    # 일단 임의로 가중치를 설정해놓음
    weight = [4,2,1]
    
    color_class = decoding_to_color(input_color,find_key) 
    label_class = decoding_to_label(input_shape,find_key)
    
    Initialization(connection)
    Update_Weight_Color(color_class,weight,connection)
    Update_Weight_Shape(label_class,weight,connection)
    Update_Weight_Text(input_text,weight,connection)
    Choose_Top_5(connection)
    connection.close()
    
if __name__ == '__main__':
    main()
