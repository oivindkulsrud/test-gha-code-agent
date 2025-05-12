"""
bubble_sort.py

A simple implementation of the bubble sort algorithm in Python.
"""

def bubble_sort(arr):
    """
    Sorts a list of comparable items using bubble sort algorithm.
    Returns a new sorted list.

    Args:
        arr (list): A list of elements that can be compared using >.

    Returns:
        list: A new list containing the sorted elements.

    Example:
        >>> bubble_sort([3, 1, 4, 1, 5, 9, 2])
        [1, 1, 2, 3, 4, 5, 9]
    """
    n = len(arr)
    result = arr.copy()
    for i in range(n):
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Sort a list of numbers using bubble sort."
    )
    parser.add_argument(
        "numbers", metavar="N", type=float, nargs=+, help="numbers to sort"
    )
    args = parser.parse_args()
    sorted_list = bubble_sort(args.numbers)
    print(sorted_list)