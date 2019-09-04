#-*-coding:utf-8-*-

from src.utils import language_detect

vocab_path = r"data/processed/en-zh/vocab.en-zh"
detect_path = vocab_path + ".lang.detect"

with open(vocab_path, encoding='UTF-8') as vocab:
    with open(detect_path, mode="w", encoding="UTF-8") as detect:
        for line in vocab.readlines():
            line = line.split()
            if language_detect(line[0], 'en'):
                line.append("en")
            if language_detect(line[0], 'zh'):
                line.append('zh')

            detect.write(" ".join(line))
            detect.write("\n")
