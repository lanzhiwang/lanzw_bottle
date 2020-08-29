import re

regex = re.compile(r':([a-zA-Z_]+)(?P<uniq>[^\w/])(?P<re>.+?)(?P=uniq)')

for route in ['user/(?P<id>[0-9]+)', 'user/:id/:action', 'user/:id#[0-9]+#']:
    print(route)
    match = regex.search(route)
    print(match)
    if match:
        print(match.groups())
        print(match.group(0))
    print()

"""
user/(?P<id>[0-9]+)
None
()

user/:id/:action
None
()

user/:id#[0-9]+#
<_sre.SRE_Match object at 0x7fa8402cfb78>
('id', '#', '[0-9]+')
:id#[0-9]+#
()
"""


route = re.sub(
        r':([a-zA-Z_]+)(?P<uniq>[^\w/])(?P<re>.+?)(?P=uniq)',
        r'(?P<\1>\g<re>)',
        'user/:id#[0-9]+#')

print(route)
# user/(?P<id>[0-9]+)
