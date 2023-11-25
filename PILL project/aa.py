def count_overlapping_substrings(string1, string2):
    count = 0

    # 두 문자열 중 짧은 문자열의 길이를 기준으로 반복
    for i in range(1, min(len(string1), len(string2)) + 1):
        # 각 위치에서의 부분 문자열 비교
        if string1[-i:] == string2[:i]:
            count += 1

    return count

# 예시 사용
string1 = "abc"
string2 = "bbbbabcbbb"
overlap_count = count_overlapping_substrings(string1, string2)
print(f"두 문자열에서 겹치는 부분 문자열의 개수: {overlap_count}")
