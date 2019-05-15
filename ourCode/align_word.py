import sys

def aligned_word(concate_file, align_file, dict_filename=None):
    cf = open(concate_file, mode='r', encoding='UTF-8')
    af = open(align_file, mode='r', encoding='UTF-8')
    
    cflines = cf.readlines()
    aflines = af.readlines()
    assert len(cflines) == len(aflines), "lines not equal: %d-%d" % (len(cflines), len(aflines))

    counter = dict()
    count = 0

    for cfline, afline in zip(cflines, aflines):
        cfline_t = cfline.split(" ||| ")
        cfleft, cfright = cfline_t[0], cfline_t[1]
        cfleft = cfleft.split()
        cfright = cfright.split()

        try:
            for a in afline.split():
                x = a.split("-")
                tmp = (cfleft[int(x[0])], cfright[int(x[1])])
                if (tmp in counter.keys()):
                    counter[tmp] += 1
                else:
                    counter[tmp] = 1
        except IndexError as e:
            print("Error lines: %d " % count, e)
            print("Raw line: %s" % cfline)
            print("Align line: %s" % afline)
            count += 1
            continue

        count += 1
        if count % 5000000 == 0:
            print("Process line %d" % count)

    counter_sorted = sorted(counter.items(), key=lambda d:d[1], reverse=True)
    
    if dict_filename is None:
        dict_file = open("dict.en-zh", mode='w', encoding="UTF-8")
    else:
        dict_file = open(dict_filename, mode="w", encoding="UTF-8")
    for i in counter_sorted:
        dict_file.write(str(i[0][0]))
        dict_file.write("\t\t")
        dict_file.write(str(i[0][1]))
        dict_file.write("\t")
        dict_file.write(str(i[1]))
        dict_file.write("\n")

    cf.close()
    af.close()
    dict_file.close()

if __name__ == "__main__":
    if (len(sys.argv) < 3):
        usage = """You need two arguments, the first is the corpus file, the second is align file"""
        print(usage)
        exit(0)
    inputfile = sys.argv[1]
    inputalign = sys.argv[2]
    if len(sys.argv) == 4:
        out = sys.argv[3]
    else:
        out = None
    aligned_word(inputfile, inputalign, out)