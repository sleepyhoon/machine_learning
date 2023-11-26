import Levenshtein

word1 = "kitten"
word2 = "sitting"

distance = Levenshtein.distance(word1, word2)
print(f"Levenshtein distance between '{word1}' and '{word2}': {distance}")
