# encoding=UTF-8

import os
import re
import sys

from collections import Counter
from pythainlp import word_tokenize


def segment_and_vocab(read_file, write_file):
    print("Thai segment read file: %s" % read_file)
    print("Thai segment write file: %s" % write_file)
    sentences = open(read_file, mode="r", encoding="UTF-8")
    sentence_seg = open(write_file, mode="w", encoding="UTF-8")
    # words = open("wiki.vocab.th", mode="w", encoding="UTF-8")

    counter = Counter()
    count = 0
    for sentence in sentences.readlines():
        word_list = word_tokenize(sentence, keep_whitespace=False)
        sentence_seg.write(" ".join(word_list))
        counter.update(word_list)

        count += 1
        if count % 5000 == 0:
            print("process sentences: %d" % count)

    del counter["\n"]
    # words.writelines(["{} {}\n".format(c[0], c[1]) for c in counter.most_common()])

    sentences.close()
    sentence_seg.close()
    # words.close()


DOC_RE = re.compile(r"<\/?doc.*>")

def readfile(filename):
    file = open(filename, mode="r", encoding="UTF-8")
    lines = []
    for line in file.readlines():
        line = line.strip()
        if len(line) == 0:
            continue
        if DOC_RE.match(line):
            continue
        lines.append(line)
    file.close()
    return lines


def merge_all_articles():
    sents = open("wiki.sent.th", mode="w", encoding="UTF-8")

    dir_root = "thwiki-20190601-pages-articles-multistream"
    dirs = os.listdir(dir_root)
    for dir in dirs:
        print("process dirs: %s" % dir)
        files = os.listdir(os.path.join(dir_root, dir))
        for filename in files:
            lines = readfile(os.path.join(dir_root, dir, filename))
            sents.writelines(line + "\n" for line in lines)
    sents.close()


if __name__ == "__main__":
    if sys.argv[1] == "extract":
        merge_all_articles()
        segment_and_vocab("wiki.sent.th", "wiki.sent.seg.th")
    if sys.argv[1] == "segment" and len(sys.argv) == 4:
        segment_and_vocab(sys.argv[2], sys.argv[3])