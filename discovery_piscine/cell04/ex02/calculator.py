#!/usr/bin/env python3

first_number = int(input("Give me the first number: "))
second_number = int(input("Give me the second number: "))

print("Thank you!")
print(f"{first_number} + {second_number} = {first_number + second_number}")
print(f"{first_number} - {second_number} = {first_number - second_number}")

if second_number != 0:
    print(f"{first_number} / {second_number} = {first_number / second_number:g}")
else:
    print("Cannot divide by zero.")

print(f"{first_number} * {second_number} = {first_number * second_number}")
