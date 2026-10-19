**Maze勒索病毒，又称Chacha勒索病毒，是今年5月份由Malwarebytes安全研究员首次发现，此勒索病毒主要使用各种漏洞利用工具包Fallout、Spelevo，伪装成合法加密货币交换应用程序的假冒站点或挂马网站等方式进行分发传播，近日笔者监控到一例通过标题为RSA
SecurID的诱饵文档传播此勒索病毒的最新样本。**  

捕获到的诱饵文档是一个以RSA SecurID为标题的文档，内容如下所示：  

![Snipaste_2019-11-14_16-06-50.png](https://image.3001.net/images/20191116/1573913941_5dd005552b112.png!small)文档里面包含恶意宏代码，诱导受害者双击启动宏代码，恶意宏代码，如下所示：  

![Snipaste_2019-11-14_16-25-42.png](https://image.3001.net/images/20191116/1573913961_5dd00569c6635.png!small)动态调试恶意宏代码，如下所示：  

![Snipaste_2019-11-14_15-14-19.png](https://image.3001.net/images/20191116/1573913976_5dd005788d704.png!small)读取窗体中的数据，然后进行解析，窗体的数据，如下所示：  

![Snipaste_2019-11-14_15-11-10.png](https://image.3001.net/images/20191116/1573913990_5dd005866b345.png!small)宏代码解密窗体中的数据，然后从远程服务器hxxp://149.56.245.196/wordupd.tmp下载恶意程序到C:\Windows\Temp\ered.tmp，然后执行恶意程序，如下所示：  

![Snipaste_2019-11-14_10-33-10.png](https://image.3001.net/images/20191116/1573914004_5dd0059433c04.png!small)下载的ered.tmp就是Maze勒索病毒，外壳程序如下所示：  

![Snipaste_2019-11-14_16-40-22.png](https://image.3001.net/images/20191116/1573914017_5dd005a15179e.png!small)分配相应的内存空间，然后解密出勒索病毒的核心代码，如下所示：  

![Snipaste_2019-11-14_16-42-09.png](https://image.3001.net/images/20191116/1573914034_5dd005b25b134.png!small)再跳转执行勒索病毒核心代码，如下所示：  

![Snipaste_2019-11-14_16-53-06.png](https://image.3001.net/images/20191116/1573914052_5dd005c40282e.png!small)此勒索病毒加密后的文件后缀名为随机文件名，如下所示：  

![Snipaste_2019-11-14_16-55-47.png](https://image.3001.net/images/20191116/1573914065_5dd005d1599a0.png!small)勒索提示信息文件DECRYPT-FILES.txt，内容如下所示：  

![Snipaste_2019-11-14_16-57-26.png](https://image.3001.net/images/20191116/1573914078_5dd005dea29c8.png!small)加密文件之后会修改桌面背景图片，如下所示：  

![Snipaste_2019-11-14_16-58-49.png](https://image.3001.net/images/20191116/1573914097_5dd005f1b0a3d.png!small)该勒索病毒解密网站，如下所示：  

![Snipaste_2019-11-14_17-14-53.png](https://image.3001.net/images/20191116/1573914111_5dd005ffbb8c3.png!small)上传勒索提示信息文件之后，如下所示：  

![Snipaste_2019-11-14_17-17-36.png](https://image.3001.net/images/20191116/1573914126_5dd0060e404c1.png!small)

勒索赎金为:0.13967635
BTC，相当于1200美元，过期翻倍，我去！现在搞勒索都这么黑的，上次还是400美元，这次直接1200美元了，黑客的BTC钱包地址：

    
    
    334yPgzDkqD7vvh2GKMrFSQneWVp2onvUq

文档内容上显示的时间为2019年11月12日，估计是12号制作的诱饵文档,最近一段时间一些流行的勒索病毒家族主要使用漏洞和垃圾邮件两种方式进行传播感染，各企业一定要做好相应的防范措施，大部分流行的勒索病毒暂无公开的解密工具，此勒索病毒之前主要使用漏洞利用工具包，通过假虚网站或垃圾网站挂马的方式进行传播，此次又增加了垃圾邮件文档的方式进行传播，可见勒索病毒黑客团伙不断在更新增加自己的攻击传播方式，以获取最大的利益，未来会不会也会利用无文件的方式传播此勒索病毒呢？

## IOC

### MD5

> a2d631fcb08a6c840c23a8f46f6892dd
>
> a0c5b4adbcd9eb6de9d32537b16c423b

### C&C

> 149.56.245.196
>
> 91.218.114.4
>
> 91.218.114.25
>
> 91.218.114.11
>
> 91.218.114.26
>
> 91.218.114.31

### URL

> hxxp://149.56.245.196/wordupd.tmp
>
> hxxp://91.218.114.4/messages/content/appvsgp.html?kakp=2mj&rkjn=koimf
>
> hxxp://91.218.114.11/forum/hhiwoqn.action
>
>
> hxxp://91.218.114.4/messages/jwt.asp?rgct=dp&gf=m1h&igtu=617lg1ps42&q=0q7r0l6v
>
> hxxp://91.218.114.25/view/check/fvksl.html?dab=a6tud3
>
> hxxp://91.218.114.26/archive/pj.jspx?wi=h1265&hi=e
>
> hxxp://91.218.114.31/support/mkhbm.action?vshw=m627m
>
> hxxp://91.218.114.11/ticket/nsa.jsp?efd=g0xay3bx&mtu=1
>
> hxxp://91.218.114.25/pipkl.cgi?ampf=8613eu&cnp=wc6502gj16&q=5m&ycme=35s4b
>
> hxxp://91.218.114.31/check/s.phtml?uxkv=wjebu46&wmbk=12vc05ja7m
>
>
> hxxp://91.218.114.26/support/uuxyhvhu.do?ic=wjpr4uy&lpap=2&edem=62i22cgi41&p=dj6

 ***本文作者：熊猫正正，转载请注明来自FreeBuf.COM**

