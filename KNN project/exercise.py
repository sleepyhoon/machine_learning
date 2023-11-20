import numpy as np
from sklearn.datasets import load_iris
from dist import get_distance

# 각종 데이터들을 받아온다.
iris = load_iris() # iris data를 가져온다
iris_data = iris.data # 150개의 데이터의 값들 저장 
iris_class = iris.target # 150개 데이터의 class 저장
init_class = iris.target_names # 3개의 target output(setosa,versicolor,virginica) 저장

# test data를 추출하기 위해 제외할 index로 구성된 test_index를 만든다.
# k값도 여기서 설정한다.
iris_length = len(iris_data) # 과제 안에서 default는 140
test_index = list(range(2, 150, 9)) # 4,9,14,,,5의 배수마다 추출하면 에러가 없음 길이는
k=7 # k=7일때 가장 에러가 없는듯하다

# test_data를 iris_data로부터 추출하고 제외한 결과를 iris_data에 반영한다. 이때 iris_class도 수정해줘야 한다.
test_data = iris_data[test_index]
test_class = iris_class[test_index] # test_data[i]의 class는 test_class[i]에 저장되어 있음
iris_data = np.delete(iris_data,test_index,axis=0) # iris_data 수정, 
iris_class = np.delete(iris_class,test_index)  # iris_class 수정

# test data의 class를 계산해보고 이를 실제 class값과 비교해본다.
'''
    distance_class는 1개의 test_data와 140개의 train_data 사이의 거리(의 역수)를 모두 구하고,
    가장 유력한 k개를 추출하여 [distance, train_data의class] pair로 이루어진 원소를 가진 리스트이다.
'''
for i in range(len(test_data)):
    distance_class = get_distance(iris_data,test_data,iris_class,k,i) # test data 한점으로부터 train data까지의 거리 반환
    sum_distance = sum(row[0] for row in distance_class) # 거리의 합을 구한다.
    for j in range(k):
        distance_class[j][0] /= sum_distance # 각각의 거리를 거리 총합으로 나누어 가중치를 반영한다. (이하 가중치를 반영한 거리는 가중치 거리라고 함)
    which_class = [0,0,0] # class별 가중치 거리의 합을 리스트에 저장한다. 예를 들어서 whichc_class의 index 0에 들어가는 값은 class 0의 가중치 거리의 합이다.
    for j in range(k):
        which_class[distance_class[j][1]] += distance_class[j][0] # class별 가중치 거리의 합을 구해본다.
    final_class = which_class.index(max(which_class)) # 가중치 거리의 합이 제일 큰 class를 찾는다.
    print('Test Data Index :',i,'Computed class :',init_class[final_class],'True class :',init_class[test_class[i]])