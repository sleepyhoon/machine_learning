'''
대소문자 구분이 안됨
글자수에 따라 거리의 변화가 다름.
2글자인 경우 한글자만 달라져도 50프로가 되고
3글자인 경우 한글자 달라지면 66프로
4글자인 경우 한글자 달라지면 75프로... 원본과 비교했때 다른 글자수의 비율이기 때문.
'''

import Levenshtein

word1 = "kitten"
word2 = "sitting"

distance = Levenshtein.distance(word1, word2)
print(f"Levenshtein distance between '{word1}' and '{word2}': {distance}")
