***本文作者：艾登——皮尔斯，本文属FreeBuf 原创奖励计划，未经许可禁止转载。**  

 **PS：本文仅用作技术讨论及分享，严禁用于非法用途，违者后果自负。**

## 前言

 **这篇文章将会教你如何用 QRLJacking 去获取别人 Whatsapp
帐号的权限，这种攻击是交互式，需要受害者去扫描你搭建好的钓鱼网站里面的恶意二维码，或者你通过钓鱼邮件等社会工程学手段让诱导受害者去扫描你的恶意二维码。**

Freebuf 之前有关于 QRLJacking 相关报道，传送门如下：

> [QRLJacking：如何劫持快速登陆时使用的二维码
> ](http://www.freebuf.com/articles/web/110510.html)  
> ****
>
> [微信Netting-QRLJacking分析利用-> 扫我二维码获取你的账号权限](http://www.freebuf.com/column/144276.html)

##  **工具：**

Kali Linux 64 Bit 2018.1

![通过QRLJacking获取Whatsapp帐号权限](https://image.3001.net/images/20180325/15219272616774.png!small)

  
QRLJacking

![通过QRLJacking获取Whatsapp帐号权限](https://image.3001.net/images/20180325/15219272768676.png!small)  

## **教程开始:**

1.安装libncurses5-dev

    
    
    apt-get install libncurses5-dev

![通过QRLJacking获取Whatsapp帐号权限](https://image.3001.net/images/20180325/15219273166302.png!small)

2.下载QRLJacking  

    
    
    git clone https://github.com/OWASP/QRLJacking  
    

![通过QRLJacking获取Whatsapp帐号权限](https://image.3001.net/images/20180325/152192738071.png!small)

3.切换到QRLJacking/QrlJacking-Framework目录

    
    
    cd QRLJacking/QrlJacking-Framework

![通过QRLJacking获取Whatsapp帐号权限](https://image.3001.net/images/20180325/15219274306185.png!small)

4.安装requirements.txt文件

    
    
    pip install -r requirements.txt

![通过QRLJacking获取Whatsapp帐号权限](https://image.3001.net/images/20180325/15219274693096.png!small)

5.运行QRLJacking

    
    
    python QRLJacker.py

![通过QRLJacking获取Whatsapp帐号权限](https://image.3001.net/images/20180325/15219276004432.png!small)

6.选择Chat Applications-->WhatsApp-->8000(端口可以任意)然后回车

![通过QRLJacking获取Whatsapp帐号权限](https://image.3001.net/images/20180325/15219276339934.png!small)  

![通过QRLJacking获取Whatsapp帐号权限](https://image.3001.net/images/20180325/15219276391860.png!small)  

7.这个时候在浏览器打开IP:8000，我这里的是<http://192.168.221.128:8000/>

![通过QRLJacking获取Whatsapp帐号权限](https://image.3001.net/images/20180325/15219277013784.png!small)  

8.攻击者只需要修改一下右侧的网页（模仿成其他的网站登录页面类似于钓鱼网站）再诱导受害者扫描攻击者钓鱼网站上面的二维码，当受害者没有仔细辨认就进行扫描二维码登录，攻击者就可以马上获取到受害者的Whatsapp帐号的管理权限

![通过QRLJacking获取Whatsapp帐号权限](https://image.3001.net/images/20180325/15219277443241.png!small)

 **QRLJacking演示视频(提取码e3d5)：**<https://pan.baidu.com/s/1dbj2Ovnuw6PL_-W7NUwcdQ>  

## 小结：

虽然相比于Whatsapp国内的QQ微信支付宝等即时通讯工具通过二维码扫描登录的都会弹出一个登录确认会比较安全，但是我们还是需要提高个人的网络安全意识做到防范于未然，不要乱扫来历不明的二维码，谨防自己相关帐号被控制造成信息泄漏。  

***本文作者：艾登——皮尔斯，本文属FreeBuf 原创奖励计划，未经许可禁止转载。**

