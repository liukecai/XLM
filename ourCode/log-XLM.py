# Code to print figures from training log file.  Written by Liu, Kecai.

'''
pip install argparse

clm ppl:
python .\log-XLM.py --file .\run-20190319-1430-XLM-clm-enfr.log --lang1 en --lang2 fr --lm clm  --ppl True

mlm ppl and acc:
python .\log-XLM.py --file .\run-20190319-1430-XLM-clm-enfr.log --lang1 en --lang2 fr --lm mlm  --ppl True
python log-XLM.py --file enzh_mlm_train.log --lang1 en --lang2 zh --lm mlm  --ppl True
python log-XLM.py --file run-20190423-1553-XLM-mlm-enzh-l8-h8-bs32.log --lang1 en --lang2 zh --lm mlm  --ppl True
python log-XLM.py --file run-20190430-1535-XLM-mlm-enzh-l8-h8-bs32.log --lang1 en --lang2 zh --lm mlm  --ppl True
python log-XLM.py --file mlm-20190425-2353-enfr-l6-h8-bs32.log --lang1 en --lang2 fr --lm mlm  --ppl True
python log-XLM.py --file mlm-20190425-2353-enfr-l6-h8-bs32.log --lang1 en --lang2 fr --lm mlm  --acc True
python log-XLM.py --file mlm-20190504-0034-enzh-l6-h8-bs32.log --lang1 en --lang2 zh --lm mlm  --ppl True
python log-XLM.py --file mlm-20190504-0034-enzh-l6-h8-bs32.log --lang1 en --lang2 zh --lm mlm  --acc True
python log-XLM.py --file mlm-20190504-0034-enzh-l8-h8-bs32.log --lang1 en --lang2 zh --lm mlm  --ppl True
python log-XLM.py --file mlm-20190504-0034-enzh-l8-h8-bs32.log --lang1 en --lang2 zh --lm mlm  --acc True

mt bleu, acc and ppl:
python .\log-XLM.py --file .\run-20190318-2130-XLM-mlm_mlm-unsupervised-enfr.log --lang1 en --lang2 fr --mt True --bleu True
python log-XLM.py --file enfr_UMT_train.log --lang1 en --lang2 fr --mt True --bleu True
python log-XLM.py --file run-20190423-1131-XLM-mlm_mlm-unsupervised-enfr.log --lang1 en --lang2 fr --mt True --bleu True
python log-XLM.py --file run-20190423-1131-XLM-mlm_mlm-unsupervised-enfr.log --lang1 en --lang2 fr --mt True --acc True
python log-XLM.py --file run-20190423-1131-XLM-mlm_mlm-unsupervised-enfr.log --lang1 en --lang2 fr --mt True --ppl True
python log-XLM.py --file run-20190424-1532-XLM-mlm_mlm-unsupervised-enzh.log --lang1 en --lang2 zh --mt True --bleu True
python log-XLM.py --file run-20190424-1532-XLM-mlm_mlm-unsupervised-enzh.log --lang1 en --lang2 zh --mt True --acc True
python log-XLM.py --file run-20190424-1532-XLM-mlm_mlm-unsupervised-enzh.log --lang1 en --lang2 zh --mt True --ppl True
'''

import matplotlib.pyplot as plt
import re
import json
import argparse

LOG = re.compile("(?<= __log__:).+")

FALSY_STRINGS = {'off', 'false', '0'}
TRUTHY_STRINGS = {'on', 'true', '1'}

def bool_flag(s):
    """
    Parse boolean arguments from the command line.
    """
    if s.lower() in FALSY_STRINGS:
        return False
    elif s.lower() in TRUTHY_STRINGS:
        return True
    else:
        raise argparse.ArgumentTypeError("Invalid value for a boolean flag!")

def get_parse():
    parser = argparse.ArgumentParser(description="XLM log analyse")

    parser.add_argument("--file", type=str, help="The log file")
    
    parser.add_argument("--lang1", type=str, default=None, help="The source language")
    parser.add_argument("--lang2", type=str, default=None, help="The target language")

    parser.add_argument("--mt", type=bool_flag, default=False, help="Machine translation is true or language model is false")
    parser.add_argument("--lm", type=str, default="", help="MLM or CLM")

    parser.add_argument("--ppl", type=bool_flag, default=False, help="Show the PPL plot")
    parser.add_argument("--bleu", type=bool_flag, default=False, help="Show the BLEU plot")
    parser.add_argument("--acc", type=bool_flag, default=False, help="Show the acc plot")

    return parser

def check_params(params):
    assert params.file

    plot_dict = {}
    plot_dict["file"] = params.file

    if (params.mt):
        assert params.mt and params.lang1 and params.lang2
    else:
        assert params.lm.lower() == "mlm" or params.lm.lower() == "clm"

    print(params.ppl)
    print(params.bleu)
    if (params.ppl and params.mt):
        tmp_ppl = []
        tmp_ppl.append("valid_%s-%s_mt_ppl" % (params.lang1, params.lang2))
        tmp_ppl.append("valid_%s-%s_mt_ppl" % (params.lang2, params.lang1))
        tmp_ppl.append("test_%s-%s_mt_ppl" % (params.lang1, params.lang2))
        tmp_ppl.append("test_%s-%s_mt_ppl" % (params.lang2, params.lang1))
        plot_dict["ppl"] = tmp_ppl
    elif (params.ppl and not params.mt):
        tmp_ppl = []
        if (params.lang1):
            tmp_ppl.append("valid_%s_%s_ppl" % (params.lang1, params.lm.lower()))
            tmp_ppl.append("test_%s_%s_ppl" % (params.lang1, params.lm.lower()))
        if (params.lang2):
            tmp_ppl.append("valid_%s_%s_ppl" % (params.lang2, params.lm.lower()))
            tmp_ppl.append("test_%s_%s_ppl" % (params.lang2, params.lm.lower()))
        # tmp_ppl.append("valid_%s_ppl" % params.lm.lower())
        # tmp_ppl.append("test_%s_ppl" % params.lm.lower())
        plot_dict["ppl"] = tmp_ppl

    if (params.acc and params.mt):
        tmp_acc = []
        tmp_acc.append("valid_%s-%s_mt_acc" % (params.lang1, params.lang2))
        tmp_acc.append("valid_%s-%s_mt_acc" % (params.lang2, params.lang1))
        tmp_acc.append("test_%s-%s_mt_acc" % (params.lang1, params.lang2))
        tmp_acc.append("test_%s-%s_mt_acc" % (params.lang2, params.lang1))
        plot_dict["acc"] = tmp_acc
    elif (params.acc and not params.mt):
        tmp_acc = []
        if (params.lang1):
            tmp_acc.append("valid_%s_%s_acc" % (params.lang1, params.lm.lower()))
            tmp_acc.append("test_%s_%s_acc" % (params.lang1, params.lm.lower()))
        if (params.lang2):
            tmp_acc.append("valid_%s_%s_acc" % (params.lang2, params.lm.lower()))
            tmp_acc.append("test_%s_%s_acc" % (params.lang2, params.lm.lower()))
        plot_dict["acc"] = tmp_acc

    if (params.bleu):
        tmp_bleu = []
        tmp_bleu.append("valid_%s-%s_mt_bleu" % (params.lang1, params.lang2))
        tmp_bleu.append("valid_%s-%s_mt_bleu" % (params.lang2, params.lang1))
        tmp_bleu.append("test_%s-%s_mt_bleu" % (params.lang1, params.lang2))
        tmp_bleu.append("test_%s-%s_mt_bleu" % (params.lang2, params.lang1))
        plot_dict["bleu"] = tmp_bleu

    return plot_dict

def read_log(filename):
    file = open(filename, mode="r", encoding="UTF-8")
    line = file.readline()
    data = []
    while line:
        if LOG.search(line):
            line_p = line.split(" - ")
            log = LOG.findall(line)[0]
            tmp = json.loads(log)
            tmp["time"] = line_p[1]
            data.append(tmp)
        line = file.readline()
    return data

def line_chart(data, params, plot_dict):
    epoches = []
    ppls = {}
    bleus = {}
    accs = {}
    if (params.ppl):
        for p in plot_dict["ppl"]:
            ppls[p] = []
    if (params.bleu):
        for b in plot_dict["bleu"]:
            bleus[b] = []
    if (params.acc):
        for a in plot_dict["acc"]:
            accs[a] = []

    for d in data:
        epoches.append(d["epoch"])
        if (params.ppl):
            for p in plot_dict["ppl"]:
                ppls[p].append(d[p])
        if (params.bleu):
            for b in plot_dict["bleu"]:
                bleus[b].append(d[b])
        if (params.acc):
            for a in plot_dict["acc"]:
                accs[a].append(d[a])

    plt.figure(1)

    plt.xlabel("epoch")
    if (params.ppl and params.bleu):
        plt.title("ppl and bleu")
        plt.ylabel("ppl/bleu")
        for p in plot_dict["ppl"]:
            plt.plot(epoches, ppls[p], label=p)
        for b in plot_dict["bleu"]:
            plt.plot(epoches, bleus[b], label=b)
    elif (params.ppl):
        plt.title("ppl")
        plt.ylabel("ppl")
        for p in plot_dict["ppl"]:
            plt.plot(epoches, ppls[p], label=p)
    elif (params.bleu):
        plt.title("bleu")
        plt.ylabel("bleu")
        for b in plot_dict["bleu"]:
            plt.plot(epoches, bleus[b], label=b)
    elif (params.acc):
        plt.title("acc")
        plt.ylabel("acc")
        for a in plot_dict["acc"]:
            plt.plot(epoches, accs[a], label=a)

    plt.legend(loc=0)
    plt.show()


if __name__=="__main__":
    parser = get_parse()
    params = parser.parse_args()
    plot_dict = check_params(params)
    print(plot_dict)
    data = read_log(plot_dict["file"])

    if (params.ppl):
        ppl_keys = data[0].keys()
        for p in plot_dict["ppl"]:
            if p in ppl_keys:
                continue
            else:
                print("ERROR: '%s' not in log, please check parameters" % p)
                exit(1)
    if (params.bleu):
        bleu_keys = data[0].keys()
        for b in plot_dict["bleu"]:
            if b in bleu_keys:
                continue
            else:
                print("ERROR: '%s' not in log, please check parameters" % b)
                exit(1)
    if (params.acc):
        acc_keys = data[0].keys()
        for a in plot_dict["acc"]:
            if a in acc_keys:
                continue
            else:
                print("ERROR: '%s' not in log, please check parameters" % a)
                exit(1)

    line_chart(data, params, plot_dict)