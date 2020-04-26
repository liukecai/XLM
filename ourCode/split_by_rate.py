# Split dataset into smaller size.  Written by Liu, Kecai.

import sys

if __name__ == "__main__":
    file1name = sys.argv[1]
    file2name = sys.argv[2]

    file1 = open(file1name, mode='r', encoding='UTF-8')
    file2 = open(file2name, mode='r', encoding='UTF-8')

    lines1 = file1.readlines()
    lines2 = file2.readlines()

    len1 = len(lines1)
    len2 = len(lines2)

    assert len1 == len2, "Two files need to the same lines, but get %d-%d" % (len1, len2)

    rates = [0.1, 0.5, 1, 5, 10, 25, 50, 75]

    for rate in rates:
        length = len1 * rate * 0.01
        count = 0

        print("Process rate %.2f" % rate)

        new_file1 = open(file1name + str(rate), mode='w', encoding='UTF-8')
        new_file2 = open(file2name + str(rate), mode='w', encoding='UTF-8')
        for line1, line2 in zip(lines1, lines2):
            new_file1.write(line1)
            new_file2.write(line2)
            count += 1
            if count >= length:
                break
        new_file1.close()
        new_file2.close()
    
    file1.close()
    file2.close()
