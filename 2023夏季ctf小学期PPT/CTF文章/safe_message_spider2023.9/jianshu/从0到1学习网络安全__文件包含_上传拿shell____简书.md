从0到1学习网络安全 【文件包含&上传拿shell】

[_07](https://www.jianshu.com/u/044de43a8ffc)关注赞赏支持

# 从0到1学习网络安全 【文件包含&上传拿shell】

## 文件包含&上传拿shell

> **注：今后继续定期更新---“实战”！**

* * *

###### Step1：环境搭建

###### 环境搭建这部分略过，今后所有的环境我都会放到公网，感兴趣的朋友可以直接玩。

> image.png

* * *

###### Step2：漏洞复现

  * 首先，点击传送门得到`test_1.pcap`

1、打开流量包，第一件事肯定是找网址地址，很明显这里请求了登录界面；

  

image.png

追踪http流得到登录地址

  

image.png

2、进入登录界面，不着急既然登录了肯定有账号密码（这里我设了个坑第一段登录的密码是错误的仔细观察就能发现）：

  

image.png

继续看第二段登录的流量，找到正确的登录密码：

  

image.png

额...皮一下，我们继续按着提示分析流量包：

  

image.png

追踪流得到下一个地址：

  

image.png

3、进入下一个页面，这里是利用文件包含漏洞下载`test_2.pcap`  

image.png

当我们下载1.txt&2.txt文件时注意请求的url：

  

image.png

构造请求url下载`test_2.pcap`

    
    
    http://********/iCTF/control/filedownload/file_download.php?file=template/assets/img/test_2.pcap
    

请求后成功下载`ibug.pcap`，我们继续分析流量包：  

image.png

flag:aHR0cDovL3d3dy5idWcxMDI0LmNuOjEwODg4L2lDVEYvY29udHJvbC91cGxvYWRfZmlsZS91cGxvYWRfZmlsZV8xLnBocA==

base64解密：

  

image.png

4、终于进入上传页面了，文件上传(前端拦截)

前端拦截的上传其实很简单，啥也不需要选直接抓包，点上传：

  

image.png

修改包内容，上传成功：

  

image.png

5、连接蚁剑

  

image.png

###### END

* * *

> 由于小编也在学习中，写的不好各位勿喷。  
>  [从0到1学习网络安全 【目录】](https://www.jianshu.com/p/d62992b1ff2a)

实战靶场环境迁移：

[https://mp.weixin.qq.com/s/5Nat58sq85CmnW-
kWXAOsw](https://links.jianshu.com/go?to=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2F5Nat58sq85CmnW-
kWXAOsw)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [从0到1学习网络安全 【MySql手工注入过狗】](https://www.jianshu.com/p/5e8cf98f50b6)

MySql手工注入过狗 注：今后继续定期更新---“实战”！ Step1：环境搭建 这个环境是在我本机上搭的，其他...

[_07](https://www.jianshu.com/u/044de43a8ffc)阅读 648评论 0赞 2

  * [从0到1学习网络安全 【目录】](https://www.jianshu.com/p/d62992b1ff2a)

文章仅用于供大家学习参考，请勿用于非法测试，否则后果自负！ 攻防相关文章已全部下线删除！ 简介 1.什么是网络安全...

[_07](https://www.jianshu.com/u/044de43a8ffc)阅读 11,237评论 10赞 101

  * [从0到1学习网络安全 【Tomcat put 上传（CVE-2017-12615）拿websh...](https://www.jianshu.com/p/a85dfa9a0e75)

Tomcat put 上传漏洞 注：今后继续定期更新---“实战”！ Step1：环境搭建 环境搭建这部分略过，今...

[_07](https://www.jianshu.com/u/044de43a8ffc)阅读 971评论 0赞 1

  * [从0到1学习网络安全 【Tomcat 弱口令拿webshell】](https://www.jianshu.com/p/899d8fd23f2a)

Tomcat 弱口令 注：今后继续定期更新---“实战”！ Step1：环境搭建 环境搭建这部分略过，今后所有的环...

[_07](https://www.jianshu.com/u/044de43a8ffc)阅读 737评论 0赞 2

  * [从0到1学习网络安全 【Web安全入门篇-文件包含漏洞】](https://www.jianshu.com/p/52b03e911af6)

概述 程序开发人员通常会把可重复使用的函数写到单个文件中，在使用某个函数时，直接调用此文件，无需再次编写，这种调用...

[_07](https://www.jianshu.com/u/044de43a8ffc)阅读 1,070评论 0赞 5

 