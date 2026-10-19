# 起初

在做银行项目的时候，发现流量包被进行了加密

    
    
    POST /mstep/mstep.do?act=business HTTP/1.1
    Host: xxx
    Cookie: JSESSIONID=0000Nyz0Y5yeXY7-SfoX_sArd2N:1eo58lj2m; Path=/; HttpOnly
    Mobileoa_design_type: 1
    Content-Type: application/json; charset=utf-8
    Content-Length: 731
    Accept-Encoding: gzip, deflate
    User-Agent: okhttp/3.12.0
    Connection: close
    
    {"pkgFlag":0,"errCode":0,"errMsg":"","dataPackage":{"encryptFlag":1,"hashFlag":1,"signatureFlag":0,"encryptionType":"2","app_code":"Y2hlcnJ5X05hdGl2ZQ==","hash":"UUJvC9ap+2uO6UfmJxWx7Q==","business":"\/Al7pDY8YXxtEiD2PDG5btt0y5IlyQp0Zff92hl1RJbvZxp4HeBaoz5nqvQVd34hA75XMZYNPQZulMXcFtfBL9Vmwx+sd3HNpXtgmIF26dMjwT3oO1C0HPCruJI+nyk+h4X9dUb6lTUwdKMB+WBc9O7y9mfjy1RBQLLDpuBf+lxXxFXwINvAeM\/hXhT\/nD\/7eBASEW6tR+rbzamwnrISt5A9j7IGzvKc+D7e+ldJ6D1z1kXsQhmlFSPaB8VJeBxE+M3iaxTOMiA4UBkY7FogK9ssL4xaofZkgh3amYZbe0RHeIFeFsUj5uVrPLFrMBlHDTut2s9XrN\/gWmX1+Ru4RZpt7xsb0RFyU+I2OX834MVEapOQXSxqOxxY0macompDLPGkApYDTf7yHp\/JjN4gWonNOSNVTDj2Gjb9xqqb7TS8dGz0ap7NLOGQhB02daFfeCHnTmOE+Sf5Gq03q5Fz+v7NXmy0DORanVoG6K\/HxyxM0QmR\/1OkEkeYUjXbvng8"},"crc":0}
    

# 模块

对代码脱壳分析，发现在这个目录下加解密

![](./img/6737887083297167323.png)

于是乎百度该模块的作用，发现是一个app开发第三方平台，即[cherryx官网](https://www.icitic.net/#/)

![](./img/1559779813664541901.png)

# 解密&流程

在ios中进行抓包

    
    
    POST /inf/api/md_getDownloadPath HTTP/1.1
    Host: xxx
    Cookie: SESSION_MSTEP_COOKIE=8324167242539638784; 
    Content-Type: application/json;charset=utf-8
    Accept: */*
    User-Agent: CIBWbg/2.4.3 (iPhone; iOS 14.2; Scale/2.00)
    Accept-Language: zh-Hans-CN;q=1
    Accept-Encoding: gzip, deflate
    Content-Length: 402
    Connection: close
    
    {"pkgFlag":"0","errMsg":"","dataPackage":{"encryptFlag":"1","hashFlag":"1","signatureFlag":"0","business":"maETrFenZI44wvQ1I5HVQlszHnWtXqZYtz+h7dLfzZCXYYcSnjS59JXeKniHAvXS4b7qrWgn7qcvBwjNiVUiOOY98N19OKFfE9HL1wYo71yGalZ9h\/GZEN54BpCkmfXOnAnkLa18bvI02K6W+zj\/hQ==","hash":"c809a3ed1b5ff3d5546e51ea98f63a8f5e349babdae5f6a3003a61d4d4278db5","app_code":"Mzg2NzMxMjE3X0lPU19hbGxfMi4xLjBfNDQ5"},"errCode":"0"}

明显business的值被加密。

对app进行脱壳跟踪函数，在com.icitic.mobile.cherry.http.SecurityParams.decryptBusiness的返回值得到明文

![](./img/327174898927768153.png)

而返回包也存在的一样的加密，即：

    
    
    HTTP/1.1 200 OK
    Server: nginx
    Date: Wed, 15 Mar 2023 02:50:12 GMT
    Content-Type: application/json;charset=UTF-8
    Content-Length: 543
    Connection: close
    X-RateLimit-Remaining: -1
    X-RateLimit-Burst-Capacity: 1
    X-RateLimit-Replenish-Rate: 0
    X-Frame-Options: SAMEORIGIN
    Strict-Transport-Security: max-age=63072000; includeSubdomains; preload
    Referer-Policy: origin
    Content-Security-Policy: frame-ancestors 'self'
    X-Permitted-Cross-Domain-Policies: master-only
    X-XSS-Protection: 1; mode=block
    X-Download-Options: SAMEORIGIN
    X-Content-Type-Options: nosniff
    
    {"pkgFlag":0,"errCode":null,"errMsg":null,"dataPackage":{"encryptFlag":1,"hashFlag":1,"hash":"D2CAD246070CCDA1033D47AB1CD9227B1CF555422F782E503165CB7309547016","app_code":null,"business":"DuUx3Su+Yw9keZ1523gCQDsFvAX3hl/niqggId8uirPjVT4l93axsjxLlKjaJ5Tc18hz0BpJcZhPgy/MA5E3VaB+veeSzJvZjWRQHTrwkmHWQ3tmX6lXIyvviBIt2W2FEEj5rVddnghut+JJHdVwTxctE51z21oi0OOeYrgopexttNrSmEx+vjVgXF4YAVBWYXFeWQ83Z4ktCQoFY98xaMc4chV2MmrDpO5HyqFCS2I/IA+iapROqdfKsPpNrp4SzenmOVUE+9fCZAwJ+qAogMLm/rbh9G/m8g+J2EmFnqksxWZYLZUX2IT9cEUs9SSv5jHPI1IEGmPGz0bZXG+oPg=="},"crc":0}

在包中的com.icitic.mobile.cherry.http.SecurityParams.decryptResponse函数返回值得到明文

![](./img/6533298180286790254.png)

### 流程分析

通过抓到的加密包，捕捉到关键字并全局搜索  
在com.icitic.mobile.cherry.http.SecurityParams的class下

![](./img/5642069424040633289.png)

跟踪encryptBusiness函数

![](./img/6566727892807238359.png)

即

![](./img/8889838364546412685.png)

原明文来到这里进行了加密的分析处理  
第一条路是3des加密  
第二条路是rsa加密  
主要的判断因素在于encryptFlag的值

![](./img/1128719765423092583.png)

其不同的值会进行不同的加密，在抓包中看到最多的是3des加密。  
对生成key进行跟踪，即跟踪函数getENSRKey、getCRKey、getSessionkey

![](./img/4974474956985054074.png)

均跳转到com.icitic.mobile.cherry.http.SessionManager的class

![](./img/4387650567849866283.png)

![](./img/8833168175620462918.png)

![](./img/923417859088522992.png)

对其进行hook

![](./img/6072000027207004138.png)

每次登陆都会进行更换（随机key）

# 总结

该平台下的开发基本思路都是由encryptFlag的值来判断，大都是以sm4来加密，可以以案例来做参考去hook

