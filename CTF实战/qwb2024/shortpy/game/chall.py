import sys

blacklist = [
    "eval",
    "exec", 
    "._module",
    "builtins",
    "breakpoint",
    "import"
]

user_input = open(sys.argv[1]).read()

del sys

def check(code):
    for b in blacklist:
        if b in code:
            return False

    return all(ord(c) < 128 for c in code)

if check(user_input):
    eval(user_input, {}, {})