import os
import sys

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Need four arguments: data path, save path, src lang and tgt lang ('en', 'fr', 'zh'...)")
        exit(1)

    DATA_PATH = sys.argv[1]
    SAVE_PATH = sys.argv[2]
    SRC = sys.argv[3]
    TGT = sys.argv[4]

    filelist = os.listdir(DATA_PATH)
    print("Porcess file list: %s" % filelist)
    srclist = [x for x in filelist if SRC in x]
    srclist = sorted(srclist)
    tgtlist = [x for x in filelist if TGT in x]
    tgtlist = sorted(tgtlist)
    print("Porcess file list for source language: %s" % srclist)
    print("Porcess file list for target language: %s" % tgtlist)

    all_src = open(os.path.join(SAVE_PATH, "all.%s" % SRC), mode="w", encoding="UTF-8")
    all_tgt = open(os.path.join(SAVE_PATH, "all.%s" % TGT), mode="w", encoding="UTF-8")

    srclines = 0
    tgtlines = 0

    for srcfilename, tgtfilename in zip(srclist, tgtlist):
        if srcfilename[:-7] == tgtfilename[:-7]:
            print("Processing %s - %s" % (srcfilename, tgtfilename))

            srcfile = open(os.path.join(DATA_PATH, srcfilename), mode="r", encoding="UTF-8")
            tgtfile = open(os.path.join(DATA_PATH, tgtfilename), mode="r", encoding="UTF-8")

            srcline = srcfile.readlines()
            tgtline = tgtfile.readlines()

            if len(srcline) != len(tgtline):
                print("\tEN lines and ZH lines not equal: %d-%d" % (len(srcline), len(tgtline)))
                srcfile.close()
                tgtfile.close()
                continue

            srclines += len(srcline)
            tgtlines += len(tgtline)

            all_src.writelines(srcline)
            all_tgt.writelines(tgtline)

            srcfile.close()
            tgtfile.close()
    
    all_src.close()
    all_tgt.close()

    if srclines == tgtlines:
        print("Processing %d lines. End." % srclines)
    else:
        print("Process error, enlines and zhlines not equal: %d-%d" % (srclines, tgtlines))        
            