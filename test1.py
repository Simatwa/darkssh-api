import re

text = (
    "Hello there world "
    "I am from kenya "
    "My name is Caleb "
    "I am aged 21 "
    "I love coding "
    "especially in python "
    "and number 35 9 "
    "my primary email address is "
    "smartwacaleb@gmail.com and secondary one "
    "benycarl23@hotmail.'com "
    "admin@must.edu. "
    "My phone number is +254774304553 "
    "My other one is 0748982989"
)

out = re.findall(r"", text)

print(out)
