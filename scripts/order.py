import os
import re
import sys

indexed_contents = {}

for file_name in os.listdir("ft_fun"):
    fd = open(f"ft_fun/{file_name}", 'r')
    content = fd.read()
    fd.close()
    match = re.search(r'//file([0-9]*)', content)
    index = int(match.group(1))
    indexed_contents[index] = re.sub(r'//file[0-9]*', '', content)

ordered_content = [value for _, value in sorted(indexed_contents.items())]

with open("not_fun.c", 'w+') as fd:
    fd.write(''.join(ordered_content))
fd.close()
