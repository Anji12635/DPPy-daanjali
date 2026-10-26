#!/usr/bin/env python3

original_array = [2, 8, 9, 48, 8, 22, -12, 2]
new_array = set()

for number in original_array:
    if number > 5:
        new_array.add(number + 2)

print(original_array)
print(new_array)
