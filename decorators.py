import time

def timeit(arg=None, print_result=False):
    if callable(arg):
        # Decorator used without parentheses
        return timing_wrapper(arg, print_result)
    else:
        # Decorator used with parentheses
        return lambda func: timing_wrapper(func, arg, print_result)

def timing_wrapper(func, custom_name=None, print_result=False):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        if custom_name:
            function_name = custom_name
        else:
            function_name = func.__name__

        if print_result:
            print(f"The function '{function_name}' took {execution_time:.4f} seconds to execute. Result: {result}")
        else:
            print(f"The function '{function_name}' took {execution_time:.4f} seconds to execute.")
        
        return result
    return wrapper

@timeit(print_result=True)
def __testFunction():
    return 1

if __name__ == "__main__":
    __testFunction()