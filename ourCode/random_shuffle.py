import linecache
import random
import sys

if __name__ == "__main__":
    assert len(sys.argv) == 3


    fileName1 = sys.argv[1]
    fileName2 = sys.argv[2]

    nLine = 0
    f = open(fileName1,"rb")
    for i in f:
        nLine += 1
    print("dataset 1 lines: %s" % nLine)
    f.close()

    nLine2 = 0
    f = open(fileName2,"rb")
    for i in f:
        nLine2 += 1
    print("dataset 2 lines: %s" % nLine2)
    f.close()

    if nLine != nLine2:
        print("These two file lines different (%s-%s), exit" % (nLine, nLine2))
        exit()

    b = [0 for i in range(nLine)]
    for i in range(nLine):
        b[i]=i+1
    random.shuffle(b)
    print("first")

    f = open(fileName1 + ".shuffle", "w", encoding='UTF-8')
    e = open(fileName2 + ".shuffle", "w", encoding='UTF-8')
    for i in range(nLine):
        a=b[i]
        cf=linecache.getline(fileName1,a) 
        f.write(cf)
        en=linecache.getline(fileName2,a)
        e.write(en)
    print("second")
    f.close()
    e.close()
