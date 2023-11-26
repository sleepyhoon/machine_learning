import mysql.connector
from mysql.connector import Error
import logging
'''
색,모양,텍스트 순으로 입력받고 먼저 들어오는 것을 신뢰도가 높게 설정한다.

색은 좌우를 나누어서 4개,4개씩 입력받으며(상위 4개의 색),만약 하나의 색이라고 인식하면 4개만 입력받음
색을 a1,a2,a3,a4,b1,b2,b3,b4라고 하면 가중치 = [3,2,1] 로 설정.
가중치는 1순위는 3, 2순위는 2, 3,4순위는 1로 하여 (1순위,1순위) = 3 + 3 = 6, (2순위,3순위) = 2 + 1 = 3 으로 계산한다.

색을 이용해서 입력받고, 필터링한 후 모양도 추정되는 상위 2가지를 입력받고,
마찬가지로 1순위 모양을 가진 알약은 가중치 4,
2순위 모양을 가진 알약은 가중치 1로 설정하였다
(모양의 경우 정확도가 1가지 모양으로만 해도 90프로에 육박하고, 2가지 모양을 썻을때보다 정확도가 
3~4%만 차이나기 때문에 굳이 하지 않아도 될지도 모른다.)

색과 모양으로 예외처리를 하고나서, 마지막으로 텍스트로 필터링을 진행한다. 텍스트는 문자열로 받는다고 생각한다.
입력받은 텍스트와 실제 텍스트를 비교해서 (물론 앞뒤를 구분하여 2가지로 비교해야한다) 유사도가 가장 높은 상위 5개(일단 임의로 설정)를 출력한다.
'''

'''
How To Use?

from Prediction_DB import Prediction 을 맨위에 적어준다.
Prediction(input_color,input_shape,input_text,connection)
-----------------------입력--------------------------
매개변수는 순서대로 아래와 같이 색깔,모양,텍스트를 리스트 형태로 입력해야함.
input_color = [0,1,2,3,2,6,4,5] # 하양,노랑...
input_shape = [0,1] # 원형과 타원형
input_text = ["",""] # 임의의 글씨
connection 은 밑에 코드를 의미함. 본문에서 아마 맨 처음에 이미 선언 했을 것.
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
----------------------------------------------------
----------------------출력--------------------------
입력받은 색깔,모양,텍스트를 바탕으로 가장 유력한 5개의 알약의 정보를 모두 출력함.
----------------------------------------------------
'''
class Prediction:

    def __init__(self, input_color, input_shape, input_text, connection):
        self.input_color = input_color
        self.input_shape = input_shape
        self.input_text = input_text
        self.connection = connection
        self.predict()

    # decoding 과정에서 사용하는 함수. 값을 이용해서 키를 찾아준다.
    def find_key(self, dictionary, value):
        return next((key for key, val in dictionary.items() if val == value), None)

    # color decoding
    def decoding_to_color(self, input_color, find_key):
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
            '투명': 15,
            '':-1
        }
        mapped_colors = [find_key(color_mapping, index) for index in input_color]
        return mapped_colors

    # label decoding
    def decoding_to_shape(self, input_shape, find_key):
        shape_mapping = {
            '원형': 0,
            '타원형': 1,
            '장방형': 2,
            '팔각형': 3,
            '육각형': 4,
            '오각형': 5,
            '마름모형': 6,
            '사각형' : 7
        }
        mapped_shape = [find_key(shape_mapping,index) for index in input_shape]
        return mapped_shape

    def Decoding(self):
        input_color = self.decoding_to_color(self.input_color,self.find_key)
        input_shape = self.decoding_to_shape(self.input_shape,self.find_key)
        return input_color, input_shape
    
    # 입력받은 색깔을 이용해서 db에 가중치 적용
    def Update_Weight_Color(self):
        cursor = self.connection.cursor()
        weight = [3,2,1]
        print(self.input_color)
        try:
            # 색이 1가지 인 경우
            if self.input_color[4] == '' and self.input_color[5] == '' and self.input_color[6] == '' and self.input_color[7] == '':
                # 1순위 색
                query = "UPDATE pill_data SET priority = priority + %s WHERE color_class1 = %s" 
                cursor.execute(query, (weight[0],self.input_color[0],))
                # 2순위 색
                query = "UPDATE pill_data SET priority = priority + %s WHERE color_class1 = %s"
                cursor.execute(query, (weight[1],self.input_color[1],))
                # 3,4순위 색
                query = "UPDATE pill_data SET priority = priority + %s WHERE color_class1 = %s OR color_class1 = %s"
                cursor.execute(query, (weight[2],self.input_color[2],self.input_color[3],))

            # 색이 2가지인 경우
            else:
                # 1,1순위 색깔들 모임 = 가중치 6
                query = "UPDATE pill_data SET priority = priority + %s WHERE (color_class1 = %s and color_class2 = %s)"
                cursor.execute(query, (weight[0]+weight[0], self.input_color[0], self.input_color[4],))

                # 1,2순위 색깔들 모임 = 가중치 5
                query = ("UPDATE pill_data SET priority = priority + %s WHERE (color_class1 = %s and color_class2 = %s) OR "
                        "(color_class1 = %s and color_class2 = %s)")
                cursor.execute(query, (weight[0]+weight[1], self.input_color[0], self.input_color[5], self.input_color[1], self.input_color[4],))

                # 1,3순위나 1,4순위, 2,2순위 색깔들 모임 = 가중치 4
                query = ("UPDATE pill_data SET priority = priority + %s WHERE (color_class1 = %s and color_class2 = %s) OR "
                        "(color_class1 = %s and color_class2 = %s) OR (color_class1 = %s and color_class2 = %s) OR "
                        "(color_class1 = %s and color_class2 = %s) OR (color_class1 = %s and color_class2 = %s)")
                cursor.execute(query, (weight[0]+weight[2], self.input_color[0], self.input_color[6], self.input_color[0], self.input_color[7],
                                    self.input_color[2], self.input_color[4], self.input_color[3], self.input_color[4], self.input_color[1], self.input_color[5],))

                # 2,3순위, 2,4순위 색깔들 모임 = 가중치 3
                query = ("UPDATE pill_data SET priority = priority + %s WHERE (color_class1 = %s and color_class2 = %s) OR "
                        "(color_class1 = %s and color_class2 = %s) OR (color_class1 = %s and color_class2 = %s) OR "
                        "(color_class1 = %s and color_class2 = %s)")
                cursor.execute(query, (weight[1]+weight[2], self.input_color[1], self.input_color[6], self.input_color[1], self.input_color[7],
                                    self.input_color[2], self.input_color[5], self.input_color[3], self.input_color[5],))

                # 3,4순위 색깔들 모임 = 가중치 2
                query = ("UPDATE pill_data SET priority = priority + %s WHERE (color_class1 = %s and color_class2 = %s) OR "
                        "(color_class1 = %s and color_class2 = %s)")
                cursor.execute(query, (weight[2]+weight[2], self.input_color[2], self.input_color[7], self.input_color[3], self.input_color[6],))

            # 변경사항을 모든 쿼리에 대해 하나의 트랜잭션으로 묶음
            self.connection.commit()
        
        except mysql.connector.Error as err:
            # 어떠한 예외가 발생하면 롤백
            logging.error(f"MySQL Error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    # 입력받은 모양을 이용해서 db에 가중치 적용
    def Update_Weight_Shape(self):
        cursor = self.connection.cursor()
        weight = [3,2,1]
        try:
            query = "UPDATE pill_data SET priority = priority + %s WHERE drug_shape = %s"
            cursor.execute(query, (weight[0],self.input_shape[0],))
            query = "UPDATE pill_data SET priority = priority + %s WHERE drug_shape = %s"
            cursor.execute(query, (weight[0],self.input_shape[1],))
            # 변경사항을 모든 쿼리에 대해 하나의 트랜잭션으로 묶음
            self.connection.commit()
        except mysql.connector.Error as err:
            # 어떠한 예외가 발생하면 롤백
            logging.error(f"MySQL Error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    # 입력받은 텍스트을 이용해서 db에 가중치 적용
    def Update_Weight_Text(self):
        cursor = self.connection.cursor()
        weight = [3,2,1]
        try:
            query = "UPDATE pill_data SET priority = priority + %s WHERE (print_front LIKE %s AND print_back LIKE %s) \
                    OR (print_front LIKE %s AND print_back LIKE %s)"
            cursor.execute(query, (weight[0], self.input_text[0], self.input_text[1], self.input_text[1], self.input_text[0],))

            # 변경사항을 모든 쿼리에 대해 하나의 트랜잭션으로 묶음
            self.connection.commit()   
        except mysql.connector.Error as err:
            # 어떠한 예외가 발생하면 롤백
            logging.error(f"MySQL Error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()
    # 유력한 상위 5개 알약 정보들 출력하기.
    def Choose_Top_5(self):
        cursor = self.connection.cursor()
        try:
            query = "select * from pill_data order by priority desc limit 10"
            cursor.execute(query)
            result = cursor.fetchall()
            for row in result:
                print(row)
        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")
        finally:
            cursor.close()

    # 시작하기전 모든 가중치를 0으로 설정
    def Initialization(self):
        try:
            cursor = self.connection.cursor()
            query = "update pill_data set priority = 0"
            cursor.execute(query)
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")
        finally:
            cursor.close()

    def predict(self):
        self.Initialization()
        self.input_color, self.input_shape = self.Decoding()
        self.Update_Weight_Color()
        self.Update_Weight_Shape()
        self.Update_Weight_Text()
        self.Choose_Top_5()
