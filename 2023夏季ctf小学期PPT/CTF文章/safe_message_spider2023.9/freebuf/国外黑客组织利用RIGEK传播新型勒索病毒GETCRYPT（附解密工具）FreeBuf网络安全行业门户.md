***本文作者：熊猫正正，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 一、事件背景

 **国外安全研究员在5月21日在网上爆光了一款利用RIGEK漏洞利用工具包传播的新型勒索病毒。**

如下所示：

![](https://image.3001.net/images/20190522/1558522357_5ce529f5d5a48.png!small)

这款勒索病毒同样修改了桌面的背景，同之前流行的GandCrab和Sodinokibi勒索病毒类似，RIGEK漏洞工具包也经常被利用来传播各种勒索和挖矿病毒，之前已经有不少报道利用RIGEK漏洞工具包传播恶意软件的报告，此次RIGEK被利用传播这款新型的勒索病毒，经过分析这款勒索病毒避开了Russian等地区的主机，笔者分析过大量的勒索病毒样本，不少新型的或流行的勒索病毒都有此操作，猜测：是不是由于前几年杀毒软件的生意不好做，卡巴斯基的安全老毛子们都转搞黑产了？导致近几年做挖矿和勒索的黑产们越来越多，越来越流行，今年针对企业的勒索病毒攻击也是越来越多，之前有报道称在第一季度针对企业的勒索病毒攻击增长了500%，勒索依然是黑产们来钱最快最暴利的手段之一，而且大部分企业中了勒索之后，都选择交钱解决，有些大企业中了勒索，甚至不会公开去找安全公司解决方案，偷偷交钱解密，导致针对企业的勒索攻击越来越频繁，每天都有新的勒索病毒或变种出现......

> 样本下载地址：<https://app.any.run/tasks/701839e5-1a81-47ab-98d2-0dd5ae14ae53/>

有兴趣的朋友可以下载样本进行分析，分析这款勒索病毒还是很有趣的......笔者预测马上这款新型的勒索病毒就会在国内流行......请各大安全厂商以及各大企业做好相应的应对防护措施!

## 二、样本简介

勒索病毒运行之后，如下所示：

![](https://image.3001.net/images/20190522/1558522774_5ce52b966c2f4.png!small)

勒索信息文本文件# DECRYPT MY FILES #.txt，如下所示：

![](https://image.3001.net/images/20190522/1558522808_5ce52bb895eda.png!small)

勒索病毒加密文件，加密文件后缀名为四位大写字母，如下所示：

![](https://image.3001.net/images/20190522/1558522829_5ce52bcdae519.png!small)

## 三、详细分析

1.勒索病毒母体采用了高强度的混淆免杀技术，勒索病毒的核心被一层“厚厚的”外壳保护，(具体的跟踪调试过程我就省略了，有不会的可以私聊我)，解密出勒索病毒核心代码，核心代码，如下所示：

![](https://image.3001.net/images/20190522/1558522901_5ce52c151c25e.png!small)

2.获取操作系统语言版本，如果操作系统版本为419(LANG_RUSSIAN 俄语) 422(LANG_UKRAINIAN 乌克兰)
423(LANG_BELARUSIAN 白俄罗斯) 43F(LANG_KAZAK 哈萨克族)等地区，则不执行相应的勒索加密过程，退出程序，如下所示：

![](https://image.3001.net/images/20190522/1558522917_5ce52c250d0dd.png!small)

3.获取主机的CPUID，如下所示：

4.生成加密文件后的加密后缀，如下所示：

生成的加密后缀为：ELSH，如下所示：

![](https://image.3001.net/images/20190522/1558522972_5ce52c5c89766.png!small)

5.判断操作系统的版本，进程提权，如下所示：

![](https://image.3001.net/images/20190522/1558522994_5ce52c7221289.png!small)

然后创建线程，删除磁盘卷影，如下所示：

![](https://image.3001.net/images/20190522/1558523008_5ce52c80b30e8.png!small)

6.在%APPDATA%目录下生成加密的key文件encrypted_key.bin，如下所示：

![](https://image.3001.net/images/20190522/1558523036_5ce52c9c2fbea.png!small)

生成Key文件的过程，先解密出Base64硬编码的RSA公钥信息，如下所示：

![](https://image.3001.net/images/20190522/1558523063_5ce52cb73117d.png!small)

然后导入RSA公钥，再加密生成的随机密钥，如下所示：

![](https://image.3001.net/images/20190522/1558523078_5ce52cc6d77bd.png!small)

再使用Base64算法进行加密，如下所示：

![](https://image.3001.net/images/20190522/1558523104_5ce52ce071f78.png!small)

再把Base64加密生成的密钥信息，写入到key文件中，如下所示：

![](https://image.3001.net/images/20190522/1558523162_5ce52d1a6265f.png!small)

生成的key文件，如下所示：

![](https://image.3001.net/images/20190522/1558523176_5ce52d28d6c34.png!small)

7.遍历共享目录文件，然后加密文件，如下所示：

![](https://image.3001.net/images/20190522/1558523191_5ce52d3735300.png!small)

8.遍历磁盘文件，然后加密文件，如下所示：

![](https://image.3001.net/images/20190522/1558523205_5ce52d45e0268.png!small)

9.在每个目录下生成勒索信息文本文件# DECRYPT MY FILES #.txt，如下所示：

![](https://image.3001.net/images/20190522/1558523227_5ce52d5bbea6e.png!small)

10.遍历磁盘目录，如果目录中包含，如下字符串目录，则不进行加密，如下所示：

![](https://image.3001.net/images/20190522/1558523243_5ce52d6b51a84.png!small)

相应的目录字符串列表，如下所示：

    
    
    :\\$Recycle.Bin
    
    :\\ProgramData
    
    :\\Users\\All Users
    
    :\\Program Files
    
    :\\Local Settings
    
    :\\Windows
    
    :\\Boot
    
    :\\System Volume Information
    
    :\\Recovery
    
    AppData

如果文件名中包含“加密后的文件后缀”或者包含“# DECRYPT MY FILES #”,则不进行加密，如下所示：

![](https://image.3001.net/images/20190522/1558523267_5ce52d83bf375.png!small)

11.如果遍历到相应的文件符合要求，则加密文件，加密后的文件后缀名为之前生成的后缀名，如下所示：

![](https://image.3001.net/images/20190522/1558523293_5ce52d9dc7524.png!small)

12.生成勒索桌面背景，如下所示：

![](https://image.3001.net/images/20190522/1558523340_5ce52dccaef09.png!small)

修改桌面背景，如下所示：

![](https://image.3001.net/images/20190522/1558523360_5ce52de0513a9.png!small)

然后在TEMP目录下生成勒索信息桌面背景图片desk.bmp，写入相应的数据，如下所示：

![](https://image.3001.net/images/20190522/1558523377_5ce52df16cc59.png!small)

最后退出程序。

## 四、IOC

### MD5：

    
    
    6D21C5C3BCFF6076179BCCD9EA6D1464

(在文章审核期间，Emsisoft竟然在5月23号放出来解密工具，Emsisoft之前也放出了不少的勒索解密工具，真是造福全球，国内用户如果有中此勒索的，可以下载解密)

## 五、解密工具

Emsisoft releases a free decrypter for the GetCrypt Ransomware

下载地址：<https://www.emsisoft.com/decrypter/getcrypt>

经过笔者测试，可以解密，如下所示：

![](https://image.3001.net/images/20190523/1558574239_5ce5f49fbe6e7.png!small)

 ***本文作者：熊猫正正，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

