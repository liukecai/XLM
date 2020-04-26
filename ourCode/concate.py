import sys

def concate(file1, file2, newfile=None):
    f1 = open(file1, mode='r', encoding="UTF-8")
    f2 = open(file2, mode='r', encoding="UTF-8")
    if newfile:
        f3 = open(newfile, mode='w', encoding="UTF-8")
    else:
        f1_name = file1.split(r"/")[-1]
        f2_name = file2.split(r"/")[-1]
        f3 = open("concate-%s-%s"%(f1_name, f2_name), mode='w', encoding="UTF-8")
    
    lines1 = f1.readlines()
    lines2 = f2.readlines()
    assert len(lines1) == len(lines2), "lines not equal: %d-%d" % (len(lines1), len(lines2))

    for line1, line2 in zip(lines1, lines2):
        if len(line1.strip()) == 0 or len(line2.strip()) == 0:
            continue
        f3.write(line1.strip())
        f3.write(" ||| ")
        f3.write(line2)
    
    f1.close()
    f2.close()
    f3.close()

if __name__ == "__main__":
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    if (len(sys.argv) == 4):
        file3 = sys.argv[3]
    else:
        file3 = None
    
    concate(file1, file2, file3)