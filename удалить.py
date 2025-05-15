from typing import Callable, List

def new_f(func: Callable[[int], List[int]]) -> Callable[[int], List[int]]:
    def wrapper(n: int) -> List[int]:
        return [-x for x in func(n)]
    return wrapper

@new_f
def f(n: int) -> List[int]:
    if n>=0:
        return [x for x in range(0, n+1, 2)]
    else:
        return [x for x in range(0, n-1, -2)]
     
print(f(10))
print(f(-10))