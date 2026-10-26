#!/usr/bin/env python3

print("Enter a number")
number = int(input())

i = 0
while i <= 9:
    print(f"{i} x {number} = {i * number}")
    i += 1
