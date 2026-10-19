***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![google68.jpg](https://image.3001.net/images/20190527/1558950861_5cebb3cd84d9b.jpg!small)**
**本文分享的writeup是关于谷歌某生产系统的一个LFI漏洞，作者通过Redirect重定向组合构造方式发现了该漏洞，最终可以远程在目标服务器上实现本地系统命令运行，获取到系统敏感运行信息，最终获得了谷歌官方奖励的$13,337。**

## 第一次尝试

尝试说明：springboard.google.com系统上的身份验证绕过（Auth Bypass）

目标对象/URL：​springboard.google.com/REDACTED_DIR

总结：访问<https://springboard.google.com/>相关目录后，会发生页面重定向跳转，跳转后的页面中会显示一个“OnContent
Debug for”调试窗口。

### 复现：

1.访问<https://springboard.google.com/>，跳转到<https://cloudsearch.google.com/cloudsearch/error?et=6>，页面出现以下信息，提示只有内部工作人员才有权限执行应用服务：

![01.png](https://image.3001.net/images/20190527/1558950643_5cebb2f307ee8.png!small)2.之后，再次访问springboard.google.com下的某个目录-<https://springboard.google.com/REDACTED_DIR>，就会跳出“OnContent Debug for”调试窗口：

![02.png](https://image.3001.net/images/20190527/1558950653_5cebb2fd791aa.png!small)这算是内部信息泄露吗？几经测试没有新的发现，我就向谷歌上报了这个漏洞，但是，3天之后，谷歌给我的回复为：

> 初步看来，你的上报情况不算太严重以致可以分类为某种漏洞，但我们会尽快进行一些分析调查。
>
> At first glance, this might not be severe enough to qualify for a reward,
> though the panel will take a look shortly.

更扯的是：一周之后，谷歌的回复如下：

> 根据我们的漏洞奖励项目来看，你上报的漏洞暂未达到奖励标准。
>
> “As a part of our Vulnerability Reward Program, we decided that it does not
> meet the bar for a financial reward”

## 第二次尝试

由于以上的发现无法达到谷歌的漏洞奖励标准，为此，我决定围绕“身份验证绕过（Auth
Bypass）”再深入对这个漏洞进行一些分析，其中肯定还存在一些隐藏的目录链接。在Web应用暴破工具wfuzz的帮助下，我发现了很多有意思的东西，实现了从身份验证绕过到管理员权限的LFI。

 **尝试说明：** springboard.google.com系统的LFI执行；

目标对象/ URL：

    
    
    springboard.google.com/REDACTED_DIR/ANOTHER_DIR

 **总结：** 实现了从身份验证绕过到名为“gxx-xxxx”管理员权限的LFI执行，springboard.google.com为谷歌的一个生产系统。

### 复现：

1.在<https://springboard.google.com/REDACTED_DIR/ANOTHER_DIR>下，存在某个服务 “Redacted
status main” (FrameworkInfo)的运行状态信息，如下：

![03.png](https://image.3001.net/images/20190527/1558950702_5cebb32e1b20d.png!small)2.如果点击页面状态信息中的最后一个按键选项“Show
REDACTED”
，你就会重定向到<https://springboard.google.com/REDACTED_DIR/ANOTHER_DIR?file=/proc/self/environ>，其中的/proc/self/environ命令就会被加载，/proc/self/environ命令为显示出当前系统中的相关运行环境变量和配置属性，如下：

![04.png](https://image.3001.net/images/20190527/1558950714_5cebb33ad96df.png!small)3.哇哦，这完全就是一个LFI漏洞啊！再来试试/proc/version看看：

![05.png](https://image.3001.net/images/20190527/1558950725_5cebb345cdffc.png!small)此时，我屏住了呼吸，内心却兴奋不已，这是谷歌生产系统中具备管理员权限的LFI漏洞啊！另外，每次刷新/proc/self/environ命令后，得到的都会是不同的系统变量，从这可以看出，该域名下对应了多个服务器系统。

之后，我还努力想从LFI实现RCE，但无奈谷歌的安全防护还不错，我未能成功，另外，也无法从中读取一些类似/proc/*/fd、ssh keys、server
keys等日志密钥信息。

## 漏洞上传的进程

> 2019.3.22 向谷歌上报第一个身份验证绕过漏洞
>
> 2019.3.30 发现LFI漏洞并向谷歌上报
>
> 2019.4.04 谷歌回复称第一个漏洞未达奖励标准
>
> 2019.4.17 我询问谷歌是否两个漏洞都未达到奖励标准
>
> 2019.4.23 谷歌回复称他们搞乱了 正在核定第二个LFI漏洞
>
> 2019.5.21 谷歌奖励了我$13,337美金

 ***参考来源：[omespino](https://omespino.com/write-up-google-bug-bounty-lfi-on-production-servers-in-redacted-google-com-13337-usd/)，clouds编译，转载请注明来自FreeBuf.COM**  

