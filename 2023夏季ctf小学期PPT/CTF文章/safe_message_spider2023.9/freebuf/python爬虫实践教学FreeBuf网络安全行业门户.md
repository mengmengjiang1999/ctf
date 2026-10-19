[i春秋作家：Mochazz](https://bbs.ichunqiu.com/thread-40312-1-1.html?from=beef)

## 一、前言

这篇文章之前是给新人培训时用的，大家觉的挺好理解的，所以就分享出来，与大家一起学习。如果你学过一些python，想用它做些什么又没有方向，不妨试试完成下面几个案例。

## 二、环境准备

安装`requests lxml beautifulsoup4` 三个库（下面代码均在python3.5环境下通过测试）

    
    
    pip install requests lxml beautifulsoup4

  
![image.png](https://image.3001.net/images/20180515/15263677258554.png!small)  

## 三、几个爬虫小案例

  * 获取本机公网IP地址
  * 利用百度搜索接口，编写url采集器
  * 自动下载搜狗壁纸
  * 自动填写调查问卷
  * 获取公网代理IP，并判断是否能用、延迟

### 3.1 获取本机公网IP地址

利用公网上查询IP的借口，使用python的requests库，自动获取IP地址。

    
    
    import requests
    r = requests.get("http://2017.ip138.com/ic.asp")
    r.encoding = r.apparent_encoding        #使用requests的字符编码智能分析，避免中文乱码
    print(r.text)
    # 你还可以使用正则匹配re模块提取出IP
    import re
    print(re.findall("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",r.text))

  
![image.png](https://image.3001.net/images/20180515/15263677399123.png!small)  

### 3.2 利用百度搜索接口，编写url采集器

这个案例中，我们要使用requests结合BeautifulSoup库来完成任务。我们要在程序中设置User-Agent头，绕过百度搜索引擎的反爬虫机制（你可以试试不加User-Agent头，看看能不能获取到数据）。注意观察百度搜索结构的URL链接规律，例如第一页的url链接参数pn=0，第二页的url链接参数pn=10....
依次类推。这里，我们使用css选择器路径提取数据。

    
    
    import requests
    from bs4 import BeautifulSoup
    # 设置User-Agent头，绕过百度搜索引擎的反爬虫机制
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    # 注意观察百度搜索结构的URL链接规律，例如第一页pn=0，第二页pn=10.... 依次类推，下面的for循环搜索前10页结果
    for i in range(0,100,10):
            bd_search = "https://www.baidu.com/s?wd=inurl:/dede/login.php?&pn=%s" % str(i)
            r = requests.get(bd_search,headers=headers)
            soup = BeautifulSoup(r.text,"lxml")
        # 下面的select使用了css选择器路径提取数据
            url_list = soup.select(".t > a")
            for url in url_list:
                    real_url = url["href"]
                    r = requests.get(real_url)
                    print(r.url)

编写好程序后，我们使用关键词`inurl:/dede/login.php` 来批量提取织梦cms的后台地址，效果如下：

  
![image.png](https://image.3001.net/images/20180515/15263677541511.png!small)  

### 3.3 自动下载搜狗壁纸

这个例子，我们将通过爬虫来自动下载搜过壁纸，程序中存放图片的路径改成你自己想要存放图片的目录路径即可。还有一点，程序中我们用到了json库，这是因为在观察中，发现搜狗壁纸的地址是以json格式存放，所以我们以json来解析这组数据。

    
    
    import requests
    import json
    #下载图片
    url = "http://pic.sogou.com/pics/channel/getAllRecomPicByTag.jsp?category=%E5%A3%81%E7%BA%B8&tag=%E6%B8%B8%E6%88%8F&start=0&len=15&width=1366&height=768"
    r = requests.get(url)
    data = json.loads(r.text)
    for i in data["all_items"]:
        img_url = i["pic_url"]
        # 下面这行里面的路径改成你自己想要存放图片的目录路径即可
        with open("/home/evilk0/Desktop/img/%s" % img_url[-10:]+".jpg","wb") as f:
            r2 = requests.get(img_url)
            f.write(r2.content)
        print("下载完毕：",img_url)

  
![1.gif](https://image.3001.net/images/20180515/15263677807555.gif!small)

#### 3.4 自动填写调查问卷

目标官网：[https://www.wjx.cn](https://bbs.ichunqiu.com/thread-40312-1-1.html?from=beef)

目标问卷：[https://www.wjx.cn/jq/21581199.aspx](https://bbs.ichunqiu.com/thread-40312-1-1.html?from=beef)

    
    
    import requests
    import random
    
    url = "https://www.wjx.cn/joinnew/processjq.ashx?submittype=1&curID=21581199&t=1521463484600&starttime=2018%2F3%2F19%2020%3A44%3A30&rn=990598061.78751211"
    data = {
        "submitdata" : "1$%s}2$%s}3$%s}4$%s}5$%s}6$%s}7$%s}8$%s}9$%s}10$%s"
    }
    header = {
        "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)",
        "Cookie": ".ASPXANONYMOUS=iBuvxgz20wEkAAAAZGY4MDE1MjctNWU4Ni00MDUwLTgwYjQtMjFhMmZhMDE2MTA3h_bb3gNw4XRPsyh-qPh4XW1mfJ41; spiderregkey=baidu.com%c2%a7%e7%9b%b4%e8%be%be%c2%a71; UM_distinctid=1623e28d4df22d-08d0140291e4d5-102c1709-100200-1623e28d4e1141; _umdata=535523100CBE37C329C8A3EEEEE289B573446F594297CC3BB3C355F09187F5ADCC492EBB07A9CC65CD43AD3E795C914CD57017EE3799E92F0E2762C963EF0912; WjxUser=UserName=17750277425&Type=1; LastCheckUpdateDate=1; LastCheckDesign=1; DeleteQCookie=1; _cnzz_CV4478442=%E7%94%A8%E6%88%B7%E7%89%88%E6%9C%AC%7C%E5%85%8D%E8%B4%B9%E7%89%88%7C1521461468568; jac21581199=78751211; CNZZDATA4478442=cnzz_eid%3D878068609-1521456533-https%253A%252F%252Fwww.baidu.com%252F%26ntime%3D1521461319; Hm_lvt_21be24c80829bd7a683b2c536fcf520b=1521461287,1521463471; Hm_lpvt_21be24c80829bd7a683b2c536fcf520b=1521463471",
    }
    
    for i in range(0,500):
        choice = (
            random.randint(1, 2),
            random.randint(1, 4),
            random.randint(1, 3),
            random.randint(1, 4),
            random.randint(1, 3),
            random.randint(1, 3),
            random.randint(1, 3),
            random.randint(1, 3),
            random.randint(1, 3),
            random.randint(1, 3),
        )
        data["submitdata"] = data["submitdata"] % choice
        r = requests.post(url = url,headers=header,data=data)
        print(r.text)
        data["submitdata"] = "1$%s}2$%s}3$%s}4$%s}5$%s}6$%s}7$%s}8$%s}9$%s}10$%s"

当我们使用同一个IP提交多个问卷时，会触发目标的反爬虫机制，服务器会出现验证码。

  
![image.png](https://image.3001.net/images/20180515/15263678025068.png!small)

  
![image.png](https://image.3001.net/images/20180515/15263678115694.png!small)  

我们可以使用X-Forwarded-For来伪造我们的IP，修改后代码如下：

    
    
    import requests
    import random
    
    url = "https://www.wjx.cn/joinnew/processjq.ashx?submittype=1&curID=21581199&t=1521463484600&starttime=2018%2F3%2F19%2020%3A44%3A30&rn=990598061.78751211"
    data = {
        "submitdata" : "1$%s}2$%s}3$%s}4$%s}5$%s}6$%s}7$%s}8$%s}9$%s}10$%s"
    }
    header = {
        "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)",
        "Cookie": ".ASPXANONYMOUS=iBuvxgz20wEkAAAAZGY4MDE1MjctNWU4Ni00MDUwLTgwYjQtMjFhMmZhMDE2MTA3h_bb3gNw4XRPsyh-qPh4XW1mfJ41; spiderregkey=baidu.com%c2%a7%e7%9b%b4%e8%be%be%c2%a71; UM_distinctid=1623e28d4df22d-08d0140291e4d5-102c1709-100200-1623e28d4e1141; _umdata=535523100CBE37C329C8A3EEEEE289B573446F594297CC3BB3C355F09187F5ADCC492EBB07A9CC65CD43AD3E795C914CD57017EE3799E92F0E2762C963EF0912; WjxUser=UserName=17750277425&Type=1; LastCheckUpdateDate=1; LastCheckDesign=1; DeleteQCookie=1; _cnzz_CV4478442=%E7%94%A8%E6%88%B7%E7%89%88%E6%9C%AC%7C%E5%85%8D%E8%B4%B9%E7%89%88%7C1521461468568; jac21581199=78751211; CNZZDATA4478442=cnzz_eid%3D878068609-1521456533-https%253A%252F%252Fwww.baidu.com%252F%26ntime%3D1521461319; Hm_lvt_21be24c80829bd7a683b2c536fcf520b=1521461287,1521463471; Hm_lpvt_21be24c80829bd7a683b2c536fcf520b=1521463471",
        "X-Forwarded-For" : "%s"
    }
    
    for i in range(0,500):
        choice = (
            random.randint(1, 2),
            random.randint(1, 4),
            random.randint(1, 3),
            random.randint(1, 4),
            random.randint(1, 3),
            random.randint(1, 3),
            random.randint(1, 3),
            random.randint(1, 3),
            random.randint(1, 3),
            random.randint(1, 3),
        )
        data["submitdata"] = data["submitdata"] % choice
        header["X-Forwarded-For"] = (str(random.randint(1,255))+".")+(str(random.randint(1,255))+".")+(str(random.randint(1,255))+".")+str(random.randint(1,255))
        r = requests.post(url = url,headers=header,data=data)
        print(header["X-Forwarded-For"],r.text)
        data["submitdata"] = "1$%s}2$%s}3$%s}4$%s}5$%s}6$%s}7$%s}8$%s}9$%s}10$%s"
        header["X-Forwarded-For"] = "%s"

效果图：

  
![image.png](https://image.3001.net/images/20180515/15263678267778.png!small)

![image.png](https://image.3001.net/images/20180515/1526367832252.png!small)

  
![image.png](https://image.3001.net/images/20180515/15263678478274.png!small)  

  

关于这篇文章，因为之前写过，不赘述，感兴趣直接看：[
【如何通过Python实现自动填写调查问卷】](https://bbs.ichunqiu.com/thread-40312-1-1.html?from=beef)

#### 3.5 获取公网代理IP，并判断是否能用、延迟时间

这一个例子中，我们想爬取[
【西刺代理】](https://bbs.ichunqiu.com/thread-40312-1-1.html?from=beef)上的代理IP，并验证这些代理的存活性以及延迟时间。（你可以将爬取的代理IP添加进proxychain中，然后进行平常的渗透任务。）这里，我直接调用了linux的系统命令`ping
-c 1 " + ip.string + " | awk 'NR==2{print}' -`
，如果你想在Windows中运行这个程序，需要修改倒数第三行`os.popen`中的命令，改成Windows可以执行的即可。

    
    
    from bs4 import BeautifulSoup
    import requests
    import os
    
    url = "http://www.xicidaili.com/nn/1"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
    r = requests.get(url=url,headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    server_address = soup.select(".odd > td:nth-of-type(4)")
    ip_list = soup.select(".odd > td:nth-of-type(2)")
    ports = soup.select(".odd > td:nth-of-type(3)")
    for server,ip in zip(server_address,ip_list):
        if len(server.contents) != 1:
            print(server.a.string.ljust(8),ip.string.ljust(20), end='')
        else:
            print("未知".ljust(8), ip.string.ljust(20), end='')
        delay_time = os.popen("ping -c 1 " + ip.string + " | awk 'NR==2{print}' -")
        delay_time = delay_time.read().split("time=")[-1].strip("\r\n")
        print("time = " + delay_time)

  
![image.png](https://image.3001.net/images/20180515/15263679151873.png!small)![3.gif](https://image.3001.net/images/20180515/15263679533324.gif!small)  

## 四、结语

当然，你还可以用python干很多有趣的事情。如果上面的这些例子你看的不是很懂，那我最后在送上一套python爬虫视频教程：[
【Python网络爬虫与信息提取】
](https://bbs.ichunqiu.com/thread-40312-1-1.html?from=beef)。现在网络上的学习真的很多，希望大家能够好好利用。

有问题大家可以留言哦，也欢迎大家到春秋论坛中来耍一耍
[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)  

