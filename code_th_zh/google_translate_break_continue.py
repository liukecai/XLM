import requests
from transaction.tests.examples import ResourceManager
from bs4 import BeautifulSoup
  
def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except:
        print("Get HTML Text Failed!")
        exit()
  
def google_translate_EtoC(to_translate, from_language="en", to_language="ch-CN"):
    #根据参数生产提交的网址
    base_url = "https://translate.google.cn/m?hl={}&sl={}&ie=UTF-8&q={}"
    url = base_url.format(to_language, from_language, to_translate)
      
    #获取网页
    html = getHTMLText(url)
    if html:
        soup = BeautifulSoup(html, "html.parser")
      
    #解析网页得到翻译结果   
    try:
        result = soup.find_all("div", {"class":"t0"})[0].text
    except:
        print("Translation Failed!")
        result = ""
        exit()
          
    return result
 
def google_translate_CtoE(to_translate, from_language="ch-CN", to_language="en"):
    #根据参数生产提交的网址
    base_url = "https://translate.google.cn/m?hl={}&sl={}&ie=UTF-8&q={}"
    url = base_url.format(to_language, from_language, to_translate)
      
    #获取网页
    html = getHTMLText(url)
    if html:
        soup = BeautifulSoup(html, "html.parser")
      
    #解析网页得到翻译结果   
    try:
        result = soup.find_all("div", {"class":"t0"})[0].text
    except:
        print("Translation Failed!")
        result = ""
        exit()
          
    return result


def main():
    #count = 0
    length_of_file2 = 0

    file1 = open("Book1_en.txt", mode="r", encoding="UTF-8")
    try:
        file2 = open("ALT.zh.txt", mode="r", encoding="UTF-8")
        lines_of_file2 = file2.readlines()
        length_of_file2 = len(lines_of_file2)
        file2.close()
        file3 = open("locaction_of_breaks.txt", mode="a", encoding="UTF-8")
        file3.write("---%d---\n" % length_of_file2)
        file3.close()
    except FileNotFoundError:
        length_of_file2 = 0
    file2 = open("ALT.zh.txt", mode="a", encoding="UTF-8")

    lines = file1.readlines()
    if length_of_file2 != 0:
        lines1 = lines[length_of_file2:]
    else:
        lines1 = lines

    print("The begin of translation process.")
    rm = ResourceManager()
    t1 = '3'

    for line in lines1:
        result = google_translate_EtoC(line)
        try:
            rm.tpc_begin(t1)
            rm.inc()
            file2.write(result + "\n")
            file2.flush()
            rm.tpc_vote(t1)
            rm.tpc_finish(t1)
        except:
            if (1 == rm.delta):
                print("There is an error with the last line of output file.  Please delete it manually.")
                rm.tpc_abort(t1)
            exit()

        """
        if count % 100000 == 0:
            print("Process lines: %d" % count)
        count += 1
        """
    
    file1.close()
    file2.close()
    print("The end of translation process.")

 
if __name__ == "__main__":
    main()