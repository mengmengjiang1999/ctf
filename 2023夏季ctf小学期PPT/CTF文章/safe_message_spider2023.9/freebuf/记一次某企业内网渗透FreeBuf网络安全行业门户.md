首先还是老规矩，此文章只做技术分享，另外此漏洞已交漏洞平台，如有他人恶意利用、恶意转载抹黑与本作者无关

渗透千万条，安全第一条，请大家不要去触碰红线！文章不喜勿喷谢谢！

## 一、内网渗透介绍

好注意事项说完后正题正式开始，首先呢想打内网的话我们就得知道什么是内网，这里我就说一些简单的例子吧，例如172.16.xx.xx、192.168.xx.xx、
10.0.xx.xx类似的ip地址归属于内网IP地址，在者就是内网IP外网是无法进行访问的

## 二、外网打点

通过fofa呢找到目标站点，很轻松的通过弱口令进入后台如下：

成果1：网站控制权限

弱口令：

admin/admin

![1638756647_61ad7127eb0f2fce00371.png!small](https://image.3001.net/images/20211206/1638756647_61ad7127eb0f2fce00371.png!small)

接着找到上传点，系统设置-系统参数-上传文件，上传即可

首先上传图片马，因为前断有过滤，抓包改为jsp就getshell了

![1638756659_61ad71335deb7e9d05e53.png!small](https://image.3001.net/images/20211206/1638756659_61ad71335deb7e9d05e53.png!small)

通过弱口令-文件上传拿到webshell

![1638756669_61ad713d90e6a66e54edb.png!small](https://image.3001.net/images/20211206/1638756669_61ad713d90e6a66e54edb.png!small)

通过哥斯拉上线msf

![1638756678_61ad7146da696588e9499.png!small](https://image.3001.net/images/20211206/1638756678_61ad7146da696588e9499.png!small)![1638756689_61ad715154d0d54e871f6.png!small](https://image.3001.net/images/20211206/1638756689_61ad715154d0d54e871f6.png!small)添加路由，然后在将shell移交给cs

![1638756716_61ad716c91c38ae4fb883.png!small](https://image.3001.net/images/20211206/1638756716_61ad716c91c38ae4fb883.png!small)![1638756765_61ad719d2430d8a4dcad3.png!small](https://image.3001.net/images/20211206/1638756765_61ad719d2430d8a4dcad3.png!small)

上线之后进行权限维持

## 三、内网渗透

成果2：获取服务器权限

![1638756782_61ad71aedef262e9d5a61.png!small](https://image.3001.net/images/20211206/1638756782_61ad71aedef262e9d5a61.png!small)查看端口开放情况，发现3389开启，进行密码抓取

![1638756804_61ad71c45b56666dd76e5.png!small](https://image.3001.net/images/20211206/1638756804_61ad71c45b56666dd76e5.png!small)

成功抓到明文密码，做socks代理进行内网渗透

![1638756818_61ad71d2377c1bc62bbd2.png!small](https://image.3001.net/images/20211206/1638756818_61ad71d2377c1bc62bbd2.png!small)Administrator/aiyuyuan![1638756848_61ad71f057ce836aa96e3.png!small](https://image.3001.net/images/20211206/1638756848_61ad71f057ce836aa96e3.png!small)成果3：获取花生壳控制权限

192.168.1.239

![1638756875_61ad720b852d25c552526.png!small](https://image.3001.net/images/20211206/1638756875_61ad720b852d25c552526.png!small)

成果4：获取向日葵控制权限

![1638756884_61ad721473db3b3430509.png!small](https://image.3001.net/images/20211206/1638756884_61ad721473db3b3430509.png!small)成果5：获取数据库权限

192.168.1.238mssql数据库

![1638756899_61ad722374d2a26a48d9d.png!small](https://image.3001.net/images/20211206/1638756899_61ad722374d2a26a48d9d.png!small)成果6：获取ups权限

![1638756914_61ad72324214a8aa1226f.png!small](https://image.3001.net/images/20211206/1638756914_61ad72324214a8aa1226f.png!small)

成果7：获取打印机权限

![1638756922_61ad723adb7f5843f9221.png!small](https://image.3001.net/images/20211206/1638756922_61ad723adb7f5843f9221.png!small)

成果:8：获取ftp权限

192.168.1.235

![1638756936_61ad7248dd0d0e004ef66.png!small](https://image.3001.net/images/20211206/1638756936_61ad7248dd0d0e004ef66.png!small)![1638756945_61ad72511121b7b112c8c.png!small](https://image.3001.net/images/20211206/1638756945_61ad72511121b7b112c8c.png!small)成果9：第二台服务器权限

利用获取的密码进行登录成果拿到权限

Administrator/aiyuyuan

192.168.1.236

![1638756963_61ad72639e1653e63617b.png!small](https://image.3001.net/images/20211206/1638756963_61ad72639e1653e63617b.png!small)成果10：获取向日葵控制权限

由于装有向日葵所以直接打开获取连接的识别码

192.168.1.236

![1638756977_61ad7271054af889d6c4e.png!small](https://image.3001.net/images/20211206/1638756977_61ad7271054af889d6c4e.png!small)

成果11：获取ups控制权限

![1638756992_61ad72804a2c82a5b5247.png!small](https://image.3001.net/images/20211206/1638756992_61ad72804a2c82a5b5247.png!small)成果12：获取文件共享权限

获取HU共享文件权限，可下载和上传文件

![1638757018_61ad729a6928d389c797e.png!small](https://image.3001.net/images/20211206/1638757018_61ad729a6928d389c797e.png!small)成果13：获取百度网盘控制权限

![1638757013_61ad729538d4cc2242cbc.png!small](https://image.3001.net/images/20211206/1638757013_61ad729538d4cc2242cbc.png!small)成果14：获取第三台服务器权限

利用获取的密码进行横向，成果登录成果拿到权限

Administrator/aiyuyuan

![1638757028_61ad72a4b609d732a08f5.png!small](https://image.3001.net/images/20211206/1638757028_61ad72a4b609d732a08f5.png!small)

成果15：获取花生壳控制权限

192.168.1.237

![1638757037_61ad72adc064c4790cd3c.png!small](https://image.3001.net/images/20211206/1638757037_61ad72adc064c4790cd3c.png!small)

成果16：获取向日葵控制权限

192.168.1.127

![1638757042_61ad72b2c39756129be6c.png!small](https://image.3001.net/images/20211206/1638757042_61ad72b2c39756129be6c.png!small)

成果17：获取打印机权限

http://192.168.1.233/

![1638757054_61ad72beeb8eb4ae675b3.png!small](https://image.3001.net/images/20211206/1638757054_61ad72beeb8eb4ae675b3.png!small)成果18：获取宝利通远程会议系统权限

存在未授权访问

![1638757075_61ad72d31f9389cc8cac5.png!small](https://image.3001.net/images/20211206/1638757075_61ad72d31f9389cc8cac5.png!small)由于扫了b段没有发现存活内网渗透到此结束

