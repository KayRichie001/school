from datetime import datetime

def greet_based_on_time():
    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        return "Good Morning"
    elif 12 <= current_hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"

def greet():
    pass

# Example usage
def replace_slash_with_dot(input_string):
    return input_string.replace('/', '.')
def replace_slash_with_slash(input_string):
    return input_string.replace('.', '/')