#-*-coding:utf-8-*-

from src.utils import language_detect, is_number

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


assert is_number("12030")
assert is_number("0.12030")
assert is_number("4.")
assert is_number("-4.")
assert is_number("4.3e10")
assert is_number("4.3e-10")
assert is_number("4.3e+10")
assert not is_number("0.120.30")
assert not is_number("0.120a30")
assert not is_number(".")