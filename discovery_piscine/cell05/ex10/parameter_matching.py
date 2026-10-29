#!/usr/bin/env python3

import sys

if len(sys.argv) != 2:
    print("none")
else:
    word = input("What was the parameter? ")
    if word == sys.argv[1]:
        print("Good job!")
    else:
        print("Nope, sorry...")
