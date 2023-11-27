import Levenshtein

def calculate_similarity(pill_text, string):
        if pill_text is None or string is None:
            return 0  # 또는 다른 적절한 값으로 처리

        distance = Levenshtein.distance(pill_text, string)
        similarity = 1 - distance / max(len(pill_text), len(string))
        return similarity


input_string = "G"


string_list = "G"


similarities = calculate_similarity(input_string, string_list)


print(similarities)