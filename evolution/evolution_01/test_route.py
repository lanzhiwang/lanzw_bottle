import re

regex = re.compile(r':([a-zA-Z_]+)(?P<uniq>[^\w/])(?P<re>.+?)(?P=uniq)')

for route in ['user/(?P<id>[0-9]+)', 'user/:id/:action', 'user/:id#[0-9]+#']:
    print(route)
    match = regex.match(route)
    print(match)
    if match:
        print('  ', match.groups())
    print()
