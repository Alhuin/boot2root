import os.path
import re
import glob

def main():
    if os.path.exists('./ft_fun'):
        path = './ft_fun/*'
        files = glob.glob(path)
        a = [None] * 760
        for file in files:
            try :
                with open(file) as f:
                    content = f.read()
                    code = content.split('\n')[0]
                    fileNum = re.search('(\d+)', content.split('\n')[2])
                    if fileNum:
                        fileNum = int(fileNum.group(1)) - 1
                        a[fileNum] = code + '\n'
            except IOError as exc:
                if exc.errno != errno.EISDIR:
                    raise
        w = open('ordered_fun.c', 'w')
        st = ""
    if os.path
    for e in a:
        st = st + e
    w.write(st)
main()