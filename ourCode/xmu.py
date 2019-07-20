import argparse
import re

def strQ2B(ustring):
    """
    全角字符转半角字符
    
    Unicode中
    半角字符为 0x21-0x7e
    全角字符为 0xff01-0xff5e
    全角 = 半角 + 0xfee0

    空格全角为 0x3000
    空格半角为 0x20
    """
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x20
        elif (inside_code >= 0xFF01 and inside_code <= 0xFF5E):
            inside_code -= 0xFEE0
        elif (inside_code == 0x25A0 or inside_code == 0x25CF):
            '''去除奇奇怪怪的字符'''
            continue
        rstring += chr(inside_code)
    return rstring

def addSpace(string):
    newstr = ""
    i = 0
    numFlag = False
    while i < len(string):
        c = string[i]
        if c == ' ':
            i += 1
            continue
        try:
            if c <= '9' and c >= '0':
                newstr += c
                numFlag = True
            elif numFlag and c == '.' and string[i+1] <= '9' and string[i+1] >= '0':
                newstr += c
                newstr += string[i+1]
                i += 1
                numFlag = True
            else:
                if numFlag:
                    newstr += ' '
                newstr += c
                newstr += ' '
                numFlag = False
        except IndexError:
            break
        
        i += 1

    return newstr


def get_parser():
    parser = argparse.ArgumentParser(description="XMU data process")
    parser.add_argument("--file", type=str, help="The XMU corpus file")
    parser.add_argument("--add_space", type=bool, default=False, help="Add space in every word")
    parser.add_argument("--saved_file", type=str, default=None, help="Save the processed file")
    return parser

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    TEXT = r"<text.*"
    TEXT_END = r"</text>"
    
    SPACE = args.add_space

    xmu = open(args.file, "r", encoding="UTF-8")

    if args.saved_file is None:
        xmu_new = open(args.file + ".processed.txt", "w", encoding="UTF-8")
    else:
        xmu_new = open(args.saved_file, "w", encoding="UTF-8")


    line = xmu.readline()
    i = 0
    while line:
        if re.search(TEXT, line) or re.search(TEXT_END, line):
            pass
        else:
            line = strQ2B(line)
            line = line.strip()
            if len(line) > 2:
                if SPACE:
                    line = addSpace(line)
                else:
                    pass
                xmu_new.write(line.strip())
                xmu_new.write("\n")
        
        if (i % 100000 == 0):
            print("line: %d" % i)
        i += 1
        line = xmu.readline()

    xmu.close()
    xmu_new.close()
