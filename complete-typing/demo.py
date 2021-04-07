from typing import List

def greet(name: str) -> None:
    print("Hello", name)

def get(arr: List[str], idx: int) -> str:
    return arr[idx]

arr = ["World"]
greet(get(arr, 1))
