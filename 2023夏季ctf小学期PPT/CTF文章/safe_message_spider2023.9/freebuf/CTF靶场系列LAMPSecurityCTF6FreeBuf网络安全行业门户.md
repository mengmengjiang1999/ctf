# 下载地址

    
    
    https://download.vulnhub.com/lampsecurity/ctf6.zip
    

# **实战演练**

使用netdiscover命令查找靶机的IP。

![image.png](https://image.3001.net/images/20190820/1566289284_5d5bad849e4f8.png)  

使用nmap查看靶机开放的端口

  

打开浏览器

![image.png](https://image.3001.net/images/20190820/1566289309_5d5bad9d79e31.png)找到了一个链接，sqlmap走起

![image.png](https://image.3001.net/images/20190820/1566289450_5d5bae2a8a3ad.png)![image.png](https://image.3001.net/images/20190820/1566289481_5d5bae491883d.png)![image.png](https://image.3001.net/images/20190820/1566289514_5d5bae6aee16f.png)找到登录账号和密码

![image.png](https://image.3001.net/images/20190820/1566289594_5d5baeba195df.png)![image.png](https://image.3001.net/images/20190820/1566289609_5d5baec950aab.png)  

  

**这个靶机系统有点问题，登录页面输入正确的账号和密码都不能跳转进去管理后台**

