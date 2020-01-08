# fastAlign

document author: Liu Kecai

github: [https://github.com/clab/fast_align](https://github.com/clab/fast_align)

paper: [A Simple, Fast, and Effective Reparameterization of IBM Model 2](https://www.aclweb.org/anthology/N13-1073)

## Require libraries

    OpenMP (include with some compilers, such as GCC)
    libtcmalloc
    libsparsehash

1. libtcmalloc

    github: [https://github.com/gperftools/gperftools](https://github.com/gperftools/gperftools)

    ```shell
    # The glibc built-in stack-unwinder on 64-bit systems has some problems with the perftools libraries.
    # For that reason, if you use a 64-bit system, we strongly recommend you install libunwind before trying to configure or install gperftools.

    # libunwind
    wget http://ftp.yzu.edu.tw/nongnu/libunwind/libunwind-1.1.tar.gz
    tar -zxf libunwind-1.1.tar.gz
    cd libunwind-1.1
    ./configure --prefix=/home/wulin/.local
    make
    make install

    # tcmalloc
    git clone https://github.com/gperftools/gperftools.git
    cd gperftools/
    ./autogen.sh
    ./configure --prefix=/home/wulin/.local
    make
    make install
    ```

2. libsparsehash

    github: [https://github.com/sparsehash/sparsehash](https://github.com/sparsehash/sparsehash)

    ```shell
    git clone https://github.com/sparsehash/sparsehash.git
    cd sparsehash/
    ./configure --prefix=/home/wulin/.local
    make
    make install
    ```

## fast_align

    ```shell
    # install and compile
    git clone https://github.com/clab/fast_align.git
    cd fast_align
    mkdir build
    cd build
    cmake ..
    make

    cd build
    ```

1. English tokenizer and chinese segment

    ```shell
    # tokenizer
    /mnt/disk1/wulin/source/mosesdecoder/scripts/tokenizer/tokenizer.perl -lc < ce-new-ref-1.txt > ce-new-ref-1.tok.txt

    # segment
    # https://nlp.stanford.edu/software/stanford-segmenter-2018-10-16.zip
    segment.sh ctb ce-news-source.txt UTF-8 0 > ce-news-source.seg.txt
    ```

2. Concate parallel sentence

    ```python
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
            f3.write(line1[:-1])
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
    ```

3. align

    ```shell
    ./fast_align -i data/concate-ce-new-ref-1.tok.txt-ce-news-source.seg.txt -d -o -v > data/forward.align

    ./fast_align -i data/concate-ce-new-ref-1.tok.txt-ce-news-source.seg.txt -d -o -v -r > data/reverse.align

    ./atools -i data/forward.align -j data/reverse.align -c grow-diag-final-and > data/final.align
    ```

    ```python
    import sys

    def aligned_word(concate_file, align_file):
        cf = open(concate_file, mode='r', encoding='UTF-8')
        af = open(align_file, mode='r', encoding='UTF-8')

        cflines = cf.readlines()
        aflines = af.readlines()
        assert len(cflines) == len(aflines), "lines not equal: %d-%d" % (len(cflines), len(aflines))

        counter = dict()

        for cfline, afline in zip(cflines, aflines):
            cfline_t = cfline.split(" ||| ")
            cfleft, cfright = cfline_t[0], cfline_t[1]
            cfleft = cfleft.split()
            cfright = cfright.split()

            for a in afline.split():
                x = a.split("-")
                tmp = (cfleft[int(x[0])], cfright[int(x[1])])
                if (tmp in counter.keys()):
                    counter[tmp] += 1
                else:
                    counter[tmp] = 1

        counter_sorted = sorted(counter.items(), key=lambda d:d[1], reverse=True)

        dict_file = open("dict_final.txt", mode='w', encoding="UTF-8")
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
        if (len(sys.argv) != 3):
            usage = """You need two arguments, the first is the corpus file, the second is align file"""
            print(usage)
            exit(0)
        inputfile = sys.argv[1]
        inputalign = sys.argv[2]
        aligned_word(inputfile, inputalign)
    ```