**近日，亚信安全截获新型迷宫（Maze）勒索病毒变种文件，该病毒与众不同的是，其完成加密数据后会循环播放文件被加密的录音，多种渠道通知受害者已经感染勒索病毒。亚信安全将其命名为
Ransom.Win32.MAZE.E。**

迷宫（Maze）勒索病毒，别名ChaCha勒索，最早出现于2019年5月，由于其始终保持活跃状态，亚信安全持续追踪该勒索病毒动态，我们发现其在本月异常活跃，更新较为频繁。该病毒在早期主要使用漏洞利用工具包Fallout、Spelevo等通过网页挂马方式传播，或者伪装成合法加密货币交换应用程序的假冒站点传播。

此次我们截获的最新在野样本，其是通过标题为RSA
SecurID的诱饵文档传播（亚信安全将其命名为Trojan.W97M.DEDEX.S），该文档里面包含恶意宏代码，诱导受害者运行文件，启动宏代码。宏代码会读取窗体中的数据，然后进行解析，其主要功能是下载迷宫勒索病毒主体文件，对于不同的变种文件，其勒索主体文件下载地址和文件名称会发生变化。运行下载的迷宫勒索病毒后，其会加密系统中的数据。完成加密后，该病毒不会删除自身，而是循环播放文件被加密的录音，通知受害人已经感染勒索病毒。

##  **病毒详细分析**

###  **标题为** **RSA SecurID** **的诱饵文档分析**

![](https://image.3001.net/images/20191129/1575017669_5de0dcc5839d5.png!small)

【标题为RSA SecurID的诱饵文档】

读取窗体中的数据，下载并执行迷宫勒索病毒主体文件：

![](https://image.3001.net/images/20191129/1575017757_5de0dd1d9f6bd.png!small)

窗体的数据如下：

![](https://image.3001.net/images/20191129/1575017766_5de0dd26e6b0b.png!small)

通过调试，宏代码解密窗体中的数据，然后从远程服务器hxxp://192.xxx.210.xxx/officeupd.fft下载恶意程序到C:\Windows\Temp\jbz.exe，然后执行恶意程序，如下所示：

![](https://image.3001.net/images/20191129/1575017784_5de0dd383e15c.bmp!small)

###  **样本对比分析**

标题为RSA SecurID的不同变种的诱饵文档，其文档内容不同：

![](https://image.3001.net/images/20191129/1575017847_5de0dd77b5fa6.bmp!small)

勒索主体文件的下载地址和名称也发生了变化：

![](https://image.3001.net/images/20191129/1575017893_5de0dda5df6a7.png!small)

文档中恶意的宏代码也有所变化，但是大致的程序流程还是一样的：

![](https://image.3001.net/images/20191129/1575017907_5de0ddb356f9d.png!small)

###  **勒索主体文件** **officeupd.fft** **分析**

该勒索主体文件通过外壳程序在内存中解密执行真正的勒索Payload：

![](https://image.3001.net/images/20191129/1575017920_5de0ddc03171a.png!small)![](https://image.3001.net/images/20191129/1575017926_5de0ddc613443.png!small)

然后跳转到入口点执行核心代码：

![](https://image.3001.net/images/20191129/1575017937_5de0ddd1db13d.png!small)

文件加密完成后同样会删除系统卷影信息：

![](https://image.3001.net/images/20191129/1575017953_5de0dde10860d.png!small)

此勒索病毒加密后的文件后缀名为随机文件名：

![](https://image.3001.net/images/20191129/1575017962_5de0ddea686c0.png!small)

加密文件之后会修改桌面背景图片：

![](https://image.3001.net/images/20191129/1575017971_5de0ddf3c2e94.png!small)![](https://image.3001.net/images/20191129/1575017977_5de0ddf99019f.png!small)![](https://image.3001.net/images/20191129/1575017982_5de0ddfebe761.png!small)

勒索提示信息文件DECRYPT-FILES.txt，内容如下所示：

![](https://image.3001.net/images/20191129/1575017996_5de0de0c5a874.png!small)

###  **解决方案**

> 不要点击来源不明的邮件以及附件；
>
> 不要点击来源不明的邮件中包含的链接；
>
> 请到正规网站下载应用程序；
>
> 浏览网页时，不随意下载和安装应用程序；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 打全系统及应用程序补丁；
>
> 尽量关闭不必要的文件共享；
>
> 请注意备份重要文档。备份的最佳做法是采取3-2-1规则，即至少做三个副本，用两种不同格式保存，并将副本放在异地存储。

##  **IOC**

**文件** **sha-1** |  **文件名称** |  **亚信安全检测名**  
---|---|---  
37facdc5167a2de80a4d328920579e31  |  VERDI.doc  |  Trojan.W97M.DEDEX.S  
e3648731a36105980f5fae6b4afe614b  |  officeupd.fft  |  Ransom.Win32.MAZE.E  
  
***本文作者：亚信安全，转载请注明来自FreeBuf.COM**

