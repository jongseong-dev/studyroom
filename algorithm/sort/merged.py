def merge(li1: list, li2: list):
    idx1 = 0
    idx2 = 0
    result = []
    length1 = len(li1)
    length2 = len(li2)
    while length1 - 1 >= idx1 and length2 - 1 >= idx2:
        el1 = li1[idx1]
        el2 = li2[idx2]
        if el1 > el2:
            result.append(el2)
            idx2 += 1
        else:
            result.append(el1)
            idx1 += 1
    if length1 - 1 >= idx1:
        result.extend(li1[idx1:])
    if length2 - 1 >= idx2:
        result.extend(li2[idx2:])

    return result


def merge_sort(arr: list):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)


if __name__ == "__main__":
    import random

    input_data = random.sample(range(1, 100), 15)
    assert merge_sort(input_data) == sorted(input_data)
