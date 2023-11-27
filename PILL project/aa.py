import mysql.connector
from mysql.connector import Error
from Prediction_DB import Prediction

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
    input_color = [0,1,2,3,0,1,2,3] # 하양,노랑,주황,분홍 // 주황,분홍,갈색,연두
    input_shape = [0,1] # 원형과 타원형
    input_text = ["Y","Y"] # 앞면 일수도 있고, 뒷면 일수도 있음
    Prediction(input_color,input_shape,input_text,connection)
    connection.close()
    
if __name__ == '__main__':
    main()