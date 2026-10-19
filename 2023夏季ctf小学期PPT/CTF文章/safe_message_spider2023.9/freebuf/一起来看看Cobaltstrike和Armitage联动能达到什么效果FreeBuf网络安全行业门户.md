***本文原创作者：fengzihk，本文属FreeBuf原创奖励计划，未经许可禁止转载**

**在使用Cobaltstrike的时候发现他在大型或者比较复杂的内网环境中，作为内网拓展以及红队工具使用时拓展能力有些不足，恰恰armitage可以补充这点，利用metasploit的拓展性能、高性能的内网扫描能力，来进一步的拓展内网，达到最大化的成果输出。**

## 一、环境说明：

> 1\. A Os:Ubuntu18.04 ip:192.168.1.163 Cobaltstrike3.8 teamserver团队服务器
> armitage 团队服务器
>
> 2\. B1 Os:Windows 2008r2x64 ip:192.168.1.62 虚拟目标内网入口 （Symantec企业版14）
>
> 3\. B2 Os:Windwos10x64 ip:192.168.1.56 虚拟目标内网个人PC （无杀软）

## 二、具体流程：

powershell绕过杀软使B1回弹一个beacon，然后通过A的Cobaltstrike spawn
给armitage一个beacon，使用armitage扫描内网、利用漏洞，获取权限，然后再转给Cobaltstrike使团队可以共同协作。

## 三、截图

### 3.1、 powershell脚本制作、回弹beacon

如下图所示,很显然,我们当前拿到的这个webshell,只是个 web 服务器权限。

为了演示效果，这里在本地搭建了一个简单的php站点，使用的webshell链接程序是weevely。

Weevely是一款python编写的webshell管理工具，作为编写语言使用python的一款工具，它最大的优点就在于跨平台，可以在任何安装过python的系统上使用。

![图片1.png](https://image.3001.net/images/20180809/1533800836_5b6bf184ec937.png!small)

使用Cobaltstrike制作powershell脚本回弹beacon

使用Invoke-Obfuscation对ps文件进行混淆，加密操作以及重新编码

地址地址：<https://github.com/fengziHK/Invoke-Obfuscation>

命令：

> 1、 Import-Module.\Invoke-Obfuscation.psd1; Invoke-Obfuscation
>
> 2、set scriptblock “powershell命令” 或者 set path ps1文件
>
> 3、接着选择encoding 进行编码
>
> 4、然后out文件

![图片2.png](https://image.3001.net/images/20180809/1533800864_5b6bf1a0c09fe.png!small)![图片3.png](https://image.3001.net/images/20180809/1533800864_5b6bf1a0af501.png!small)
![图片4.png](https://image.3001.net/images/20180809/1533800864_5b6bf1a0bd318.png!small)

在B1机器中执行加过混淆的ps脚本。

在weevely中执行Powershell ./2.ps1

![图片5.png](https://image.3001.net/images/20180809/1533800885_5b6bf1b5cacce.png!small)![图片6.png](https://image.3001.net/images/20180809/1533800885_5b6bf1b5c2161.png!small)

### 3.2、绕过UAC

使用Cobaltstrik的elevate自动bypassuac功能

一般bypassuac都是脚本注入或者dll劫持来绕过uac，从cs的控制台可以看出这里利用的是dll劫持。

![图片7.png](https://image.3001.net/images/20180809/1533800916_5b6bf1d4cd47e.png!small)

### 3.3、 spawn会话

接下来是重点，打开armitage设置监听，监听的payload要和cs一致，不然接收不到会话。

![图片8.png](https://image.3001.net/images/20180809/1533801011_5b6bf23355c2b.png!small)![图片9.png](https://image.3001.net/images/20180809/1533801011_5b6bf2335933b.png!small)
![图片10.png](https://image.3001.net/images/20180809/1533801011_5b6bf2336056a.png!small)![图片11.png](https://image.3001.net/images/20180809/1533801011_5b6bf23385169.png!small)![图片12.png](https://image.3001.net/images/20180809/1533801011_5b6bf23396d61.png!small)

然后我们到目标会话上右键点击是sapwn,下一步选择armitage所监听的会话以及payload。  
看到这里，由cs的控制台可以看出他已经发出指令给目标机器，要求连接armitage。同时armitage在几秒钟内接收了会话，在实战当中不会这么快，内网转发网络延迟还是很高的。

![图片13.png](https://image.3001.net/images/20180809/1533801051_5b6bf25b7adfa.png!small)

### 3.4、扫描漏洞

这里我们先把armitage添加到对方内网，使用meterpreter的pivoting功能自动添加路由。

![图片14.png](https://image.3001.net/images/20180809/1533801099_5b6bf28b71cae.png!small)![图片15.png](https://image.3001.net/images/20180809/1533801099_5b6bf28b76415.png!small)
![图片16.png](https://image.3001.net/images/20180809/1533801099_5b6bf28b7a9d0.png!small)

并扫描目标内网机器B2

使用armitage的默认扫描功能扫描目标内网机器B2

### 3.5、利用漏洞

![图片16.png](https://image.3001.net/images/20180809/1533801162_5b6bf2caa28c7.png!small)![图片17.png](https://image.3001.net/images/20180809/1533801162_5b6bf2caa70c7.png!small)识别B2的操作系统版本、端口开放情况  

执行armitage 查找漏洞功能，并利用。

Attacks -findattacks- 会自动识别当前端口所包含的漏洞。这里不做过多的演示

### 3.6、获取权限、并转发会话给Cobaltstrike。

![图片17.png](https://image.3001.net/images/20180809/1533801190_5b6bf2e630728.png!small)

看到B2机器已经上线，提取权限并转发会话给Cobaltsrike  

![图片18.png](https://image.3001.net/images/20180809/1533801224_5b6bf30869ec3.png!small)![图片19.png](https://image.3001.net/images/20180809/1533801224_5b6bf3086d69f.png!small)
![图片20.png](https://image.3001.net/images/20180809/1533801224_5b6bf3087251c.png!small)

会话转发成功。

## 四、总结

团队要的比较急、临时赶出来，有不对的地方请大家指正！。

主要就是以armitage和cobaltstrike 互相协作，达到内网最大化利用 。

 ***本文原创作者：fengzihk，本文属FreeBuf原创奖励计划，未经许可禁止转载**

