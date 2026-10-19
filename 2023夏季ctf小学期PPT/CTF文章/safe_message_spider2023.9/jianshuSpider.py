import os
import sys
import getopt
import requests
import random
import re
import json
import time
import html2text
import argparse
from bs4 import BeautifulSoup

useragents = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    ]
print("------------------\n标准姿势python jianshuSpider.py -s CTF -c 2 -p 1 \n表示查找CTF关键字（必须）+需要2篇文章（默认5）+需要本地图床（默认不需要为0）\n------------------\n")

ap = argparse.ArgumentParser()
#自定义参数（简写，全写，是否必需，说明）
ap.add_argument("-s","--search",required = False, help = "你要搜索的关键字",default='CTF')
ap.add_argument("-c","--count",required = False, help = "你要搜索的文章数目。默认5",default='5')
ap.add_argument("-p","--is_need_pic",required = False, help = "是否需要图床",default=0)
#python demo.py -s CTF -c 2 -p 1
#获取所有的参数
args = vars(ap.parse_args())
print("------------------\n你要爬取的关键字是: "+args['search']+",数目是："+args['count'],end="")
serach_word=args['search']
org_count=int(args['count'])
page_count=int(org_count/10+1)
is_need_pic=int(args['is_need_pic'])
if is_need_pic==0 :
   print(", 而且你不需要本地图床~")
else:
   print(", 而且你需要本地图床~")


def jianshu(url):
    ## 浏览器头部
    headers = {
        'Host': 'www.jianshu.com',
        'Referer': 'https://www.jianshu.com/',
        'User-Agent': random.choice(useragents)
    }
    ## 获取网页主体
    html = requests.get(url,headers=headers).text

    ## bs4
    soup = BeautifulSoup(html,"html.parser")
    try:
        title = soup.find_all("title")[0].get_text()
        #print("title:"+title)
        article = str(soup.find_all("script", id='__NEXT_DATA__')[0].get_text())
        article_json = json.loads(article)
        ## 替图片的src加上https://方便访问
        #print(type(article_json))
        new_article=str(article_json["props"]["initialState"]["note"]["data"]["free_content"])
        new_article = re.sub('(src=")|(data-original-src=")','src="https:',new_article)
        new_article="# "+title+"\n"+new_article
        ## 写入文件
        pwd = os.getcwd() # 获取当前的文件路径
        dirpath = pwd + '/jianshu/'
        title=title.replace('*','?').replace('*','-').replace('|','-').replace('=','-').replace(':','-').replace('\'','-').replace('"','-').replace('：','-').replace('】','-').replace('【','-').replace('/','-').replace('\\','-').replace('[','').replace(']','').replace('<','').replace('>','').replace('!','').replace('_','').replace(' ','').replace('-','')[0:30]
        write2md(dirpath,title,new_article)
    except Exception as e:
        print("error")


def write2md(dirpath,title,article):
    ## 创建转换器
    h2md = html2text.HTML2Text()
    h2md.ignore_links = False
    ## 转换文档
    article = h2md.handle(article)
    ## 写入文件
    if not os.path.exists(dirpath):# 判断目录是否存在，不存在则创建新的目录
        os.makedirs(dirpath)
    # 创建md文件
    with open(dirpath+title+'.md','w',encoding="utf8") as f:
        lines = article.splitlines()
        for line in lines:
            if line.endswith('-'):
                f.write(line)
            else:
                f.write(line+"\n")
    print(title+"下载完成....")


def get_page_url(question,page_id):
    global x
    ses = requests.Session()
    headers = {
        'authority': 'www.jianshu.com',
        'accept': 'application/json',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'content-length': '0',
        'cookie': '_ga=GA1.2.822598575.1684336455; __bid_n=1882a46b151898c5fc4207; FPTOKEN=qVjVluR1gPvv2jDCsiZJ+iHuEVzNtEkRj36NIz8IPN+csg87dgVzeqWNLBsyJIbBRQQLJ7FVq8yub3KD0uUoEFo4K/ndhpjsqFPdYpYt2bpD9s90q8L+wPwPYHv9Jtu1uVK2PzzAGy6qE34ibzYUa9I5BfiLYuaA2opIG3wkmZ/SdBCLszjCoGE6yP3JDCRuyNWAbwK8wci/zbgHFBzomFfh27+hDBuXt3HOrNFngaYgVDdgMCVlbZ2znNpDd+el4XsSap+u7p2DNc34uBCMo23+3a4vZUY218EPTMJs+IsD06SkS68g7mQEtLZeV11cmexsyxBs2dPfIrmkM4Bp8ef0iN7MmSD0nt6YCbPz+HF2kF/JzuJxPIl4D0UrIgkOyw1H30mXeqngy+o3JiK2kg==|kO00Mp2huQXoH/2FXMMPgnnn/50s92vA8blki1AnHZg=|10|61e0fec223bdf00744cd0d4bb3da93d3; Hm_lvt_38ea8ed97fbe7c334fcc1878c579e5e0=1684336456,1684600191,1685279168,1685871754; Hm_lvt_c11e70df18184f7263176ce90c8a9cc3=1684336456,1684600191,1685279168,1685871754; locale=zh-CN; Hm_lvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1692699211,1693371948,1694004113,1694661214; _gid=GA1.2.87713102.1694661215; _ga_Y1EKTCT110=GS1.2.1694661215.13.1.1694661411.0.0.0; read_mode=day; default_font=font2; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221882a46ac8a1200-095fbbc0ee5c48-1c525634-1484784-1882a46ac8b21e5%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22%24device_id%22%3A%221882a46ac8a1200-095fbbc0ee5c48-1c525634-1484784-1882a46ac8b21e5%22%7D; signin_redirect=https%3A%2F%2Fwww.jianshu.com%2Fsearch%3Futf8%3D%25E2%259C%2593%26q%3DCTF; _m7e_session_core=6f9a5a38fbddc0ab69efa8d791693d8b; Hm_lpvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1694680712',
        'dnt': '1',
        'origin': 'https://www.jianshu.com',
        'pragma': 'no-cache',
        'referer': 'https://www.jianshu.com/search?utf8=%E2%9C%93&q=CTF',
        'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    #url="https://www.jianshu.com/search/do?q="+question+"&type=note&page="+str(page_id)+"&order_by=default"
    url="https://www.jianshu.com/search/do?q="+question+"&type=note&page="+str(page_id)+"&order_by=default"
    one_text=ses.get("https://www.jianshu.com/search?q="+question+"&page="+str(page_id)+"&type=note",headers=headers, proxies={'http_proxy':'socks5://glm:glm_data@180.184.38.189:27001', 'https_proxy':'socks5://glm:glm_data@180.184.38.189:27001'})
    #print(one_text.text)
    ## 浏览器头部
    s=ses.post(url,headers=headers)
    print(s.text)
    exit()
    text=s.content.decode('utf-8')
    tmp = json.loads(text)
    obj_url=''
    try:
        print("搜索的url:+"+url)
        for i in range(0,10):
            #print(tmp)
            obj_num=tmp['entries'][i]['slug']
            obj_url='https://www.jianshu.com/p/'+obj_num
            print("第"+str(page_id)+"页的"+"第"+str(i+1)+"篇文章的page_url： "+ obj_url)
            #print("------写入文件开始---------")
            f=open("url_list.txt","a+")
            f.write(obj_url+"\n")
            f.close()
            #time.sleep(1)
        x=x+1
    except KeyError as e:
        #raise e
        print('暂时被ban了~继续搜冲就完事了>_<\n')
    except IndexError as e:
        print('索引错误')
    except TypeError as e:
        print('类型错误')
    except ValueError as e:
        print('值的类型错误')
    except Exception as e:
        print('错误')
    return obj_url
def model_picture_download(model_picture_url, file_dir,text,new_pic,pic_url):
    headers = {
        'User-Agent': random.choice(useragents)
    }
    model_picture_downloaded = False
    err_status = 0
    while model_picture_downloaded is False and err_status < 10:
        try:
            html_model_picture = requests.get(
                model_picture_url,headers=headers, timeout=1)
            with open(file_dir, 'wb') as file:
                file.write(html_model_picture.content)
                model_picture_downloaded = True
                text=text.replace(pic_url,"./img/"+new_pic)
                print('下载成功！图片 = ')
                return text
        except Exception as e:
            err_status += 1
            random_int = 4
            time.sleep(random_int)
            print(e)
            print('出现异常！睡眠 ' + str(random_int) + ' 秒')
            return text
        continue
    return text

x=1
def main():
    print("\n-------------------开始爬取链接-------------------")
    f=open("url_list.txt","w")
    f.close()
    global x
    global page_count
    global org_count
    global serach_word
    while x<page_count+1:
        get_page_url(serach_word,x)
        #time.sleep(2)
    print("\n-------------------开始爬取文章内容-------------------")
    file = open("url_list.txt") 
    p_count=0
    for line in file.readlines():
        line=line.strip('\n')
        try:
            #print(line)
            jianshu(line)
            p_count=p_count+1
            if p_count==org_count:
                break
        except Exception as e:
            print("error")
    file.close()
    pro_dir="./jianshu/"
    dirs=os.listdir(pro_dir)
    if is_need_pic==0 :
       print("------------------\n你选择了不需要本地图床哦本次服务到此结束")
    else:
       print("正在更换图床\n")
       img_path="./jianshu/img"
       if(os.path.exists(img_path)):
          print("./jianshu/img文件夹已经存在-请先删除文件夹哦\n")
       else:
          print("./jianshu/img文件夹不存在-新建文件夹中ing\n")
          os.makedirs(img_path)
          print("./jianshu/img文件夹已经存在-正在更换图床\n")
          for file in dirs:
             if file!="img":
                f=open(pro_dir+file,"r+",encoding='utf-8')
                text=f.read()
                f.close()
                print(file)
                #print(text)
                pic_list=re.findall(r"!\[\]\(.+?\)", text) #找到了所有文件
                for pic in pic_list:
                   pic_url=pic[4:].split('\)')[0].replace(")","")
                   #print(pic_url)
                   new_pic=str(hash(pic_url))+'.png'
                   new_pic=new_pic.replace("-","")
                   try:
                      text=model_picture_download(pic_url, pro_dir+'img/'+new_pic,text,new_pic,pic_url)
                      print(pic_url)
                      print(new_pic)
                   except Exception as e:
                      print(e)
                   continue
                   
                f=open(pro_dir+file,"w+",encoding='utf-8')
                f.write(text)
                f.close()
    os.remove("url_list.txt")

if __name__ == "__main__":
    main()