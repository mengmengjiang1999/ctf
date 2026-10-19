> [本文作者：青衫磊落](https://bbs.ichunqiu.com/space-uid-208328.html)  
>

最近看到个特别全面源码分享网站，刚好有个项目是一直想做但是没有头绪的，就想下载学习一下。注册账号后，发现还需要若干金币。后来发现可以通过每隔一定时间发心情状态来获得金币，就打算写一个自动发心情状态的
**[python脚本](https://bbs.ichunqiu.com/thread-35308-1-1.html?from=beef)**
来收割金币。

### 思路分析

使用burp抓取一下提交的包，如下图所示：  

![图片.png](https://image.3001.net/images/20180307/15204170043912.png!small)  

因此我们的目的是写一个自动提交心情的python脚本，提交包中需要包含必要的cookie信息，隐藏的radom字符串，心情文本内容，和文件，经测试发现文件可为空。表单中只包含前两项就可以成功增加金币，这就更加省事了。  
文末附有完整python代码，接下来我们看一下是怎么一步步写出来的。

### 具体实现

#### 第一步

首先先写读取页面的功能！这个之前也写过很多，都是搜索出一段代码来直接使用。然而这次找了几段代码代码应为python及库的版本问题都不太好调试。  
就直接看requests库官方文档，官方文档才是最好的资料。  
版本1代码

    
    
    #coding:utf-8  
    import requests
    url_home = "http://www.home.com/"
    r = requests.get(url_home)
    print(r.text)

  
![图片.png](https://image.3001.net/images/20180307/15204170168597.png!small)  

此时获得的页面是未曾登陆的无法发表心情状态。

### 第二步

  
![图片.png](https://image.3001.net/images/20180307/15204170242314.png!small)  

版本2代码：

    
    
    #coding:utf-8  
    import requests
    cookies = dict(zdmid="93EB84AE485E7B7E365C4F87691F8A9D")
    url_home = "http://www.home.com/"
    r = requests.get(url_home，cookies=cookies)
    print(r.text)

![图片.png](https://image.3001.net/images/20180307/15204170318335.png!small)  

### 第三步

接下来我们提取需要提交表单的隐藏input随机字符串，同时选择当前首页的其他人的心情状态作为我们的文本内容。  
解析html，当然是神库
**[beautifulSoup4](https://bbs.ichunqiu.com/thread-35308-1-1.html?from=beef)**
了，别无他想。分析需要提取的值在html页面的具体位置，查看官方文档选择合适的api方法，然后编写代码实现。

  
![图片.png](https://image.3001.net/images/20180307/1520417038683.png!small)  

    
    
    #coding:utf-8  
    import requests
    from bs4 import BeautifulSoup
    
    cookies = dict(zdmid="451178ECCF2145D24F94DE0A1DF7D658")
    url_home = "http://www.home.com/"
    r = requests.get(url_home, cookies=cookies)
    soup = BeautifulSoup(r.text, 'html.parser')
    random = soup.form.input.attrs["value"] 
    content = soup.select_one(".content").contents[0]
    
    print(random)
    print(content)

  
![图片.png](https://image.3001.net/images/20180307/15204170447500.png!small)  

### 第四步骤

接下来我们来实现提交心情状态功能。  
只需要将上一步骤提取的内容构造post提交就可以了。

版本4代码

    
    
    #coding:utf-8  
    import requests
    from bs4 import BeautifulSoup
    
    cookies = dict(zdmid="451178ECCF2145D24F94DE0A1DF7D658")
    url_home = "http://www.home.com/"
    r = requests.get(url_home, cookies=cookies)
    soup = BeautifulSoup(r.text, 'html.parser')
    random = soup.form.input.attrs["value"] 
    content = soup.select_one(".content").contents[0]
    
    mood_create = 'http://www.mood/create.htm'
    payload = {'radom': radom, 'content': content}
    requests.post(mood_create, cookies=cookies, data=payload)

### 第五步

  
![图片.png](https://image.3001.net/images/20180307/15204170523883.png!small)  

因此可以使用[session](https://bbs.ichunqiu.com/thread-35308-1-1.html?from=beef)来改造代码，[requests](https://bbs.ichunqiu.com/thread-35308-1-1.html?from=beef)中的[session](https://bbs.ichunqiu.com/thread-35308-1-1.html?from=beef)将会自动保存相关的cookie信息，如此每次运行就可以自动使用账号及密码登陆。  
版本5代码

    
    
       #coding:utf-8  
        import requests
        from bs4 import BeautifulSoup
    
        s = requests.Session()
        url_home = "http://www.home.com/"
        s.get(url_home)
    
        url_login = "http://www.login.htm"
        data_login = {'account':'username','password':'passwd','rememberme':'on'}
        text = s.post(url_login,data=data_login)
    
        r = s.get(url_home)
        soup = BeautifulSoup(r.text, 'html.parser')
        random = soup.form.input.attrs["value"] 
        content = soup.select_one(".content").contents[0]
    
        mood_create = 'http://www.moodcreate.htm'
        payload = {'radom': radom, 'content': content}
        s.post(mood_create, cookies=cookies, data=payload)

### 第六步

上面的步骤完成后，我们可以执行一次自动提交心情状态的代码。我们想要做的每隔一定的时间间隔提交一条状态。因此还要添加上一个定时器，来自动执行这个过程。  
最终完整代码如下，[justForFun](https://bbs.ichunqiu.com/thread-35308-1-1.html?from=beef)。

    
    
        #coding:utf-8
        import threading
        import requests
        import random
        from bs4 import BeautifulSoup
        url_login = "http://www.login.htm"
        url_home = "http://www.home.com/"
        mood_create = "http://www.mood/create.htm"
    
        s = requests.Session()
    
        def create():
            global timer
            global s
            s.get(url_home)
            data_login = {'account':'username','password':'passwd','rememberme':'on'}
            text = s.post(url_login,data=data_login)
            res = s.get(url_home)
            soup = BeautifulSoup(r.text, 'html.parser')
            random = soup.form.input.attrs["value"] 
            content = soup.select_one(".content").contents[0]
            payload = {'radom': random, 'content': content}
            s.post(mood_create, cookies=cookies, data=payload)
    
            timer = threading.Timer(5*60*60, create) 
            timer.start()
    
        timer = threading.Timer(1, create)    
        timer.start()

  

  

 **> >>>>> [黑客入门必备技能](https://www.ichunqiu.com/zhihu?from=beef)
**带你入坑和逗比表哥们一起聊聊黑客的事儿，他们说高精尖的技术比农药都好玩~  

  

  

