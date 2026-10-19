***本文原创作者：fuckgod，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

## 简介

**MuddyWater是疑似来自伊朗的APT组织，主要攻击目标为中东地区政府机构，但在近期的公开报告中显示，18年后，中东以外的地区也陆续出现了Muddywater的活动迹象，比如土耳其，巴基斯坦等地。（详细信息见[上篇文章](https://www.freebuf.com/articles/paper/194310.html)）**

近日，国外安全厂商披露了三个新的MuddyWater攻击样本：

![1.png](https://image.3001.net/images/20190403/1554281358_5ca4738e26c47.png!small)

但并未写相关分析文章，笔者就用以分析学习^_^。

## 样本信息

**样本md5** |  **a066f5b93f4ac85e9adfe5ff3b10bc28**  
---|---  
**作者信息** |  Gladiator  
**样本来源** |  <https://app.any.run/tasks/4c62f53f-268f-4669-aa78-7b01f55fa15e>  
  
## 分析环境

**分析环境** |  **Win7 32** **虚拟机**  
---|---  
**调试工具** |  Powershell ise  
  
## 样本分析

样本似乎采用了模板注入，运行后，即从<http://corplink.com.pk/wp-content/themes/buisson/16433.jpg>下载一个宏样本：

![2.png](https://image.3001.net/images/20190403/1554281370_5ca4739ae51db.png!small)

![3.png](https://image.3001.net/images/20190403/1554281382_5ca473a6147c3.png!small)

此类利用方法可以有效的绕过一些杀软检测，VT59家杀软仅4家报毒：

![4.png](https://image.3001.net/images/20190403/1554281393_5ca473b1581fe.png!small)

之后便是MuddyWater组织一贯的老套路，利用模糊的诱饵性图片诱导用户启用宏：

![5.png](https://image.3001.net/images/20190403/1554281408_5ca473c0a202a.png!small)当受害者启用宏后，恶意宏代码即会执行，部分宏代码隐藏在窗体中：

![20.png](https://image.3001.net/images/20190403/1554281451_5ca473eb7b3c9.png!small)

攻击者很鸡贼的故意弹出错误提示，ofiice版本不对，以误导受害者，emmm...这也是MuddyWater的老套路了。

![6.png](https://image.3001.net/images/20190403/1554281493_5ca47415ad1fc.png!small)

宏代码后续指令写入注册表HKEY_CURRENT_USER\Software\Classes\CLSID\\{*}\Shell\Manage\command，并在启动项下写入该数据，也就是只有当受害者重启或者重新登录后续的恶意行为才会执行，这可能是为了绕过某些沙箱。

![7.png](https://image.3001.net/images/20190403/1554281506_5ca47422637a9.png!small)

之后将配置文件释放到c:\windows\temp\下，其中icon.ico主要用于启动后续powershell指令：

![8.png](https://image.3001.net/images/20190403/1554281522_5ca47432f23e8.png!small)![9.png](https://image.3001.net/images/20190403/1554281529_5ca4743974ebc.png!small)

Powershell命令经base64编码，解码后如下：

![10.png](https://image.3001.net/images/20190403/1554281550_5ca4744eadf62.png!small)

获取配置文件picture.jpg的内容，base64解码后，再经解密后执行，接下的工作就是漫长的去混淆的过程，将iex命令替换为输出等命令，解了23层混淆（想哭，各位大佬有没有快速的方法，谢谢告知），最后解混淆的代码如下：

![11.png](https://image.3001.net/images/20190403/1554281565_5ca4745d0a7b8.png!small)

解密后的文件是muddywater常用的POWERSTATS后门。

首先获取系统基本信息，计算机系统名、计算机名、用户名以及IP，公网IP等信息：

![13.png](https://image.3001.net/images/20190403/1554281614_5ca4748e56523.png!small)

之后以“**”将这些信息格式化成字符串，并使用md5对格式化的字符串进行加密。

![image.png](https://image.3001.net/images/20190403/1554281600_5ca4748040fb6.png!small)

再次获取系统基本信息，加密信息，加密方法如下：

![14.png](https://image.3001.net/images/20190403/1554281635_5ca474a3b0eb1.png!small)

与c2：<http://gladiyator.tk/None>通信，发送通信数据，若返回“done”则继续后续：

![15.png](https://image.3001.net/images/20190403/1554281653_5ca474b517672.png!small)

之后将md5加密的数据发往c2获取功能命令执行：

![16.png](https://image.3001.net/images/20190403/1554281666_5ca474c222923.png!small)

将返回的指令以~~!!~~分割后，进入命令分发，命令分发函数如下：

![17.png](https://image.3001.net/images/20190403/1554281682_5ca474d2aa380.png!small)

命令  |  功能  
---|---  
Upload  |  从给定地址下载文件保存到c:\programdata\  
Cmd  |  利用cmd执行命令，返回结果  
B64  |  利用IEX执行base64解码后的指令，返回结果  
其他  |  直接利用iex执行命令，返回结果  
  
之后将执行结果发往c2。

## 关联溯源

外国大佬都说MuddyWater了，应该就石锤了，就假装关联一下，此次样本利用了MuddyWater常用的手法，模糊图片诱导用户启用宏，只是加了一次模板注入用以绕过杀软，手法更厉害了。后续木马是MuddyWater组织常用的POWERSTATS后门：

![18.png](https://image.3001.net/images/20190403/1554281737_5ca475098928f.png!small)

和之前相同的加密key：

![19.png](https://image.3001.net/images/20190403/1554281748_5ca47514a905b.png!small)

## Ioc

### Md5

    
    
    a066f5b93f4ac85e9adfe5ff3b10bc28
    
    8a004e93d7ee3b26d94156768bc0839d
    
    f12bab5541a7d8ef4bbca81f6fc835a3

### cc

> [http://gladiyator.tk](http://gladiyator.tk/)

## 参考连接

<https://ti.360.net/blog/articles/suspected-muddywater-apt-organization-latest-attack-activity-analysis-against-iraqi-mobile-operator-korek-telecom/>

<https://www.freebuf.com/articles/network/199008.html>

 ***本文原创作者：fuckgod，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

