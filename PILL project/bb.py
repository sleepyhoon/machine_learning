'''
대소문자 구분이 안됨
글자수에 따라 거리의 변화가 다름.
2글자인 경우 한글자만 달라져도 50프로가 되고
3글자인 경우 한글자 달라지면 66프로
4글자인 경우 한글자 달라지면 75프로... 원본과 비교했때 다른 글자수의 비율이기 때문.
'''

import Levenshtein

def calculate_similarity(input_string, string_list):
    similarities = []

    for string in string_list:
        distance = Levenshtein.distance(input_string, string)
        similarity = 1 - (distance / max(len(input_string), len(string)))
        similarities.append(similarity)

    return similarities


input_string = "abcd"


string_list = ["abc", "acd", "ab", "d"]


similarities = calculate_similarity(input_string, string_list)


for string, similarity in zip(string_list, similarities):
    print(f"Similarity between '{input_string}' and '{string}': {similarity:.2f}")