![](https://image.3001.net/images/20200324/1585011456_5e795b007350e.png!small)

## 前言

 **本文介绍了笔者通过python程序实现某OA系统自动考勤打卡功能及相关逻辑原理的解析。**

> Github:<https://github.com/cahi1l1yn/eChecker>

 **声明：本程序仅供Python语言的学习交流用途，笔者不提倡利用程序自动考勤的做法，笔者不对滥用本程序导致的任何后果负责。**

## 需求分析

疫情期间，笔者所在公司使用某OA系统的考勤功能代替原来的刷脸考勤，结果导致很多人经常忘记打卡，于是笔者寻思着能不能写个程序实现自动考勤，希望实现的主要功能是：指定用户名密码登录和指定时间签到签退，扩展功能是：自定义签到和签退的IP或定位地址。

## 系统逻辑分析

为了通过python实现上述功能，首先需要人工访问系统进行相关的操作，并抓包分析请求和返回数据，弄清逻辑原理，下面介绍分析过程：

### 登录

访问OA系统登录页面，点击输入登录信息后截取登录数据包，分析发现登录接口除了验证用户名和密码外，还会验证下图红框所示的cookie和token参数。因此我们需要找到这两个参数值从哪里获取。

![](https://image.3001.net/images/20200323/1584952460_5e78748cb45a2.png!small)

重新访问登录页面并抓取返回包，首先从返回包头部看到了JSESSIONID参数，而另一个lt参数则在返回页面的源码中。

![](https://image.3001.net/images/20200323/1584953348_5e7878043d75c.png!small)

![](https://image.3001.net/images/20200323/1584953417_5e787849d580c.png!small)

弄清楚这两个参数的来源后，我们重新回到登录页面提交登录请求，获取并记录下会话cookie。

### 考勤

登录账号后，进入考勤模块进行打工并截取数据包，可以看出程序是通过向考勤接口提交参数值为CHECKIN和CHECKOUT的json字符串以实现签到和签退。

![](https://image.3001.net/images/20200323/1584953912_5e787a380cf09.png!small)

另外可以看到请求包中携带了好几个cookie参数，经过不断的测试排除后，最终确定WEBID、JSESSIONID和ETEAMSID这三个为关键cookie，其余几个都可以忽略。

### 自定义考勤地址

上述测试过程是PC端的，由于其中并没有涉及到地址的参数，因此转到APP端进行测试。截取APP端的考勤请求包，可以看到checkaddress参数就是考勤定位地址。

![](https://image.3001.net/images/20200325/1585113958_5e7aeb667e28d.png!small)

笔者尝试在PC端的考勤请求参数中插入checkaddress，从响应包中可以看出已经成功使用该参数自定义考勤地址进行考勤，同时这里如果再加入经纬度参数的话，即可高度模拟定位考勤。

![](https://image.3001.net/images/20200325/1585114240_5e7aec80b3489.png!small)

值得关注的是，笔者分析发现当考勤请求携带了PC端UA时，服务端会将客户端识别为PC端，此时不会处理checkaddress参数，签到地址就是客户端的真实IP地址。当考勤请求携带移动端UA或者pythonUA时，服务端会将客户端识别为移动端且处理checkaddress参数，此时就可以实现自定义考勤地址，包括IP地址和地理位置。

## 逻辑梳理

通过上述操作后，笔者已经了解到登录接口和考勤接口的逻辑和请求形式，下面简单梳理相关流程，这个流程也就是后续编写程序主要的逻辑依据：

    
    
    1.【用户访问登录页面】
           ||
           \/
    2.【登录页面返回一个cookie(JSESSIONID)和token(lt)】
           ||
           \/
    3.【用户携带cookie像登录接口提交token、用户名和密码】
           ||
           \/
    4.【登录接口验证成功后返回会话cookie(ETEAMSID\JSESSIONID\)】
           ||
           \/
    5.【用户携带会话cookie向考勤接口提交签到/签退请求】

## 功能实现

这里先回顾一下本程序实现需求是：指定用户名密码登录和指定时间签到签退。通过上述逻辑梳理，已经可以实现指定用户和密码登录已经签到签退，另外还需要实现的就是指定时间，下面我们加入指定时间相关的功能再次梳理python程序的主要功能逻辑：

    
    
    1.【输入用户名、密码、签到签退时间运行程序】
           ||
           \/
    2.【登录系统获取会话cookie】
           ||
           \/
    3.【程序获取本地时间】
           ||
           \/
    4.【程序比对本地时间和用户设定时间】
           ||
           \/
    5.【在指定时间携带会话cookie进行考勤】
    

## 程序结构

梳理出程序主要功能逻辑后，开始定义函数分别实现上述主要功能，下面列出程序的主要函数结构：

    
    
    def get_cookie(user,passwd):登录系统，获取会话cookie，该函数实现了[逻辑梳理]中的第2-4步
    
    def keep_session():维持会话cookie有效性，因cookie长期不活跃会失效，因此通过此函数访问系统以维持cookie，如果cookie已经失效，则会调用get_cookie函数重新登录获取cookie
    
    def check_in():签到模块，携带cookie向考勤接口提交CHECKIN
    
    def check_out():签退模块，携带cookie向考勤接口提交CHECKOUT
    
    def get_position():定位模块，根据用户输入的地理位置获取经纬度
    
    def check_time():获取本地时间并于用户设定时间作比对，触发考勤模块和会话维持模块
    
    def main():程序入口函数，获取用户输入
    

## 代码解析

通过上面的介绍，我们已经大概了解整个程序的运行逻辑，下面对部分关键代码进行解析（部分常规代码有省略）：

    
    
    def get_cookie(user,passwd):
        ...........
        token = re.search(r'LT\S+cn',html).group()
        #urllib访问登录页面后，从页面中获取lt参数值，即token
        pcookie = re.search(r'JSESSIONID=\S+',str(pres.info().headers)).group()
        #访问登录页面后，从返回包头部中获取cookie，后续提交登录请求时需要携带该cookie
        data ='lt='+token+'&execution=e1.2&j_pcClient=&_eventId=submit&isApplyed=false&ampregisterSourceUrl=&ampregisterSource=&ampregisterDataSource=&username='+user+'&password='+passwd
        #组合token和用户输入的登录信息，用于组成登录请求
        req = urllib2.Request(lurl)
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        #通过cookiejar记录登录成功后页面返回的会话cookie
        opener.addheaders = [('Cookie',pcookie)]
        #在登录请求包头中加入一开始获取到的cookie
        try:
            res = opener.open(lurl,data=data,timeout=10)
        except urllib2.URLError:
            print '[ERROR]Urlllib error, retry later'
        try:
            cookie = re.search(r'ETEAMSID=\w+',str(cj)).group()+';'+re.search(r'JSESSIONID=\w+',str(cj)).group()+';'+re.search(r'WEBID=\w+',str(cj)).group()
        #到这一步已经登录成功，cookiejar已经记录了会话cookie，记录形式是这样的：
        <CookieJar[<Cookie BIDUPSID=B681378758CB3586029EBFFFF16FBDE2 for .baidu.com/>, <Cookie PSTM=1532404690 for .baidu.com/>, <Cookie BD_NOT_HTTPS=1 for www.baidu.com/>]>
        因此这里利用正则匹配出我们所需要的3个cookie值
            print '[INFO]Login succeed, your cookie is:'+cookie
        ...........
    
    
    
    def check_in():
        ............
        req = urllib2.Request(curl)
        req.add_header("Cookie",cookie)
        req.add_header("Content-Type","application/json")
        if stat == '0':
            data = json.dumps({"type":"CHECKOUT","checkAddress":addr,"longitude":longi,'latitude':lati})
        #当用户自定义了考勤地址时，且成功获取到经纬度信息时，提交的请求中加入了地理位置和经纬度参数，服务端默认将urllib的UA识别为移动端，故会记录用户提交的地理信息，完美模拟定位考勤效果
        elif stat == '1':
            data = json.dumps({"type":"CHECKOUT","checkAddress":addr})
        #当用户自定义了考勤地址时，但未成功获取到经纬度信息时，提交的请求中只加入地理位
        elif stat =='2':
            req.add_header('User-Agent',ua)
            data = json.dumps({"type":"CHECKOUT"})
        #当用户未自定义考勤地址时，提交的请求按PC端原始格式，且此处需要加入自定义的PC端UA，否则服务端会将签到地址记录为空值
        try:
            res = urllib2.urlopen(req,data=data,timeout=5).read()
            smsg = res.find('签到成功')
            fmsg = res.find('签到失败')
            if smsg > -1:
                print '[INFO]'+time.strftime('%Y-%m-%d_%H:%M',time.localtime())+' Checkin succeed'
            elif fmsg > -1:
                print '[WARNING]'+time.strftime('%Y-%m-%d_%H:%M',time.localtime())+' Checkin fail:'+res
        #以上代码通过在返回报文中查找成功和失败的字符，作为考勤是否成功的判断依据，并输出到终端提示用户
        ..........  
    
    
    
    def check_time():
        while True:
            ltime = time.strftime('%H:%M',time.localtime()).lstrip('0')
            day = time.strftime('%a',time.localtime())
            #获取当前的时间，lstrip去0是为了时针为0-9的个位数时进行格式统一
            ..........
            if ltime == '4:30':
                keep_session()
                time.sleep(60)
            #由于会话cookie在一定时间后（貌似是十几个小时）会失效，因此设定在凌晨调用keepsession()维持cookie
            elif ltime == intime.lstrip('0') and day not in ('Sat','Sun'):
            #比对本地时间与用户输入时间，且判断是否周末
                keep_session()
            #进行考勤前，再次检验cookie是否有效
                rnd = random.randint(0,600)
                print '[INFO]Checkin after ' + str(int(rnd)/60) + ' Min ' + str(int(rnd)%60) + ' Sec'
                time.sleep(int(rnd))
                check_in()
            #为了避免用户设定一个时间后，程序每天都在同一时间点考勤，这里结合sleep和random实现在用户设定时间上正向浮动随机时间进行考勤
                time.sleep(60)
            ........
            ........
            check_time()  
    
    
    
    def get_position(addr):
        global longi
        global lati
        url = 'http://api.map.baidu.com/geocoding/v3/?address='+addr+'&output=json&ak='+api_key+'&callback=showLocation'
        html = urllib2.urlopen(url.encode('utf-8')).read()
        longi = re.search(r'lng":\d+.\d+',html).group().lstrip('lng":')
        lati = re.search(r'lat":\d+.\d+',html).group().lstrip('lat":')
        #调用百度地图API获取经纬度信息，使用encode('utf-8')处理url可以避免中文乱码问题(需要注册APIKEY)

## 运行效果

![](https://image.3001.net/images/20200330/1585528596_5e813f14af6e1.png!small)

![](https://image.3001.net/images/20200325/1585123686_5e7b11662eadf.png!small)

![](https://image.3001.net/images/20200401/1585702023_5e83e4878b827.png!small)

## 总结

本文分享了笔者利用python编写某OA系统自动考勤程序的过程，包括对系统逻辑的分析、程序结构的介绍和关键代码的解析等内容。

程序最终实现了用户自定义考勤时间、地址，并自动根据地址获取经纬度(如地址为IP地址则不获取)，每天在指定时间以上述自定义信息进行考勤。

欢迎各位大佬提出本程序的不足之处。

> 注：考勤地址可自定义的漏洞已经上报。

 ***本文作者：biubiugo，转载请注明来自FreeBuf.COM**

