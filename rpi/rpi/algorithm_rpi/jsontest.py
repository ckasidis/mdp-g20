
array_string="[[17,18,'S',1],[3,17,'S',2],[11,9,'W',3]]"

import ast

# Example string representation of an array of nested arrays
# array_string = '[[1, 2], [3, 4, 5], [6, 7, 8, 9]]'

# Use ast.literal_eval() to convert the string to a Python array
array = ast.literal_eval(array_string)

print(array)
print(type(array))
# Output: [[1, 2], [3, 4, 5], [6, 7, 8, 9]]