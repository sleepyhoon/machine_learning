import numpy as np

def get_distance(iris_data,test_data,iris_class,k,i): # distance_class 배열을 return 하는 함수이다.
    distance_class = [] # test data ~ train data 까지의 유클리드 거리, 그리고 train data의 class를 담은 리스트
    for j in range(len(iris_data)):
        distance = np.linalg.norm(test_data[i]-iris_data[j]) # 유클리드 거리를 구한다.
        if distance == 0:
            # 거리가 0인 경우를 처리 (0으로 나누는 것을 피하기 위해 아주 작은 양수 값을 사용)
            distance = np.finfo(float).eps  # 아주 작은 양수 값
        distance = 1/distance # 거리의 역수를 취한다.
        distance_class.append([distance,iris_class[j]])
    distance_class.sort(reverse=True,key=lambda x:x[0]) # 내림차순으로 정렬해야 한다. 가중치 거리 상위 k개를 뽑아내기 때문이다
    distance_class = distance_class[:k] # 상위 k개 만큼만 분리
    return distance_class