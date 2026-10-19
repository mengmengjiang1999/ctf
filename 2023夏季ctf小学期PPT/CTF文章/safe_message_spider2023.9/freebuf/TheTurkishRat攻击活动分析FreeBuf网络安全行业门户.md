**近期Check Point研究人员发现大规模恶意邮件攻击活动，其主要针对80多家土耳其公司。恶意软件使用了不同的方法来绕过目标安防机制。**

初始攻击媒介是含有Office文件的钓鱼邮件，该文件采用BIFF格式，普通的Office工具无法解析该文件。
运行后下载恶意Jar文件，该文件被高度混淆，使用了多种规避技术，避免自身被安全产品检测。Jar文件会在目标中植入多平台恶意软件Adwind
RAT，窃取目标敏感信息，并将结果发送到攻击者的C＆C服务器上，同时攻击者可获得对目标计算机的访问权。

目前这些文件在“Virus Total”中的检测率都很低，很可能是因为文件被高度混淆。

## 传播方式

> 1、攻击者向受害者发送恶意电子邮件。
>
> 2、受害者运行恶意文件。
>
> 3、恶意文件从GitHub下载恶意RAT。
>
> 4、恶意软件与C＆C服务器建立连接。

##
![image.png](https://image.3001.net/images/20200414/1586825566_5e95095e6311c.png!small)恶意JAR文件下载

### 恶意邮件

###
![image.png](https://image.3001.net/images/20200414/1586825620_5e950994935b6.png!small)附件内容

###
![image.png](https://image.3001.net/images/20200414/1586825646_5e9509aeac14b.png!small)下载器

最初的恶意文档是XLS或CSV文件。 XLS文件有外部引用，可触发下载恶意JAR文件：  

![image.png](https://image.3001.net/images/20200414/1586825741_5e950a0dd6767.png!small)`cmd
/c powershell –executionpolicy bypass –W Hidden
–command`命令用来下载名为‘zpmqwjs.docx’的JAR文件。Externsheet
Injection技术并不常见，因此可以规避部分安全产品的检测。  

![image.png](https://image.3001.net/images/20200414/1586825942_5e950ad62bfb0.png!small)攻击者在单元格内容中添加了许多垃圾字符和特殊字符，并使用了20年前的BIFF版本，因此检测工具无法解析该文件。
BiffView分析工具返回错误：  

![image.png](https://image.3001.net/images/20200414/1586826008_5e950b18ad1a9.png!small)

## Github托管

攻击者使用GitHub Pages服务创建网站，利用网站传播托管在其存储库中的恶意软件。  

![image.png](https://image.3001.net/images/20200414/1586826136_5e950b9857e1f.png!small)

名为“ 5308682”的用户与该github存储库有关， 该帐户还与18个不同的存储库有关。
攻击者托管的文件基本上都是同一个恶意JAR文件的变体，使用了不同的文件名：“ wucgy3jecwgpv.svg”，“
6da7uj4b4oi2a.pdf”，“ zpmqwjs.docx”等。

## 攻击活动分析

[Talos](https://www.openoffice.org/sc/excelfileformat.pdf)和[Sophos](https://news.sophos.com/en-us/2019/07/11/oto-gonderici-excel-formula-injections-target-turkish-victims/)报告了攻击活动的早期阶段。随着攻击活动的不断深入，攻击者正在不断改进其规避检测技术。  

##
![image.png](https://image.3001.net/images/20200414/1586826335_5e950c5fe8edd.png!small)Payload植入

植入器和payload文件都被混淆，只有少部分安全产品可检测到。

![image.png](https://image.3001.net/images/20200414/1586826436_5e950cc4f301a.png!small)![image.png](https://image.3001.net/images/20200414/1586826452_5e950cd4b0a94.png!small)

图9为Dropper的反编译代码。恶意软件使用了几种新的规避技术：

> 1、 检查JVM的默认语言环境是否为土耳其语。  
>
>
> 2、检查机器语言是否为土耳其语。
>
> 3、检查计算机名称是否为土耳其语。
>
>
> 4、恶意软件连接到checkip.amazonaws.com查询IP，通过ipinfo.io/public_ip/country来查看IP所属国家/地区是否是土耳其。

如果不满足上述任何条件，恶意软件不会执行。然后，payload通过WMIC.exe搜索反病毒软件，并将信息发送到C&C服务器。

> `WMIC /Node:localhost /Namespace:\\\root\SecurityCenter2 Path
> AntiVirusProduct Get displayName /Format:List`  
>

攻击者利用Attrib.exe将payload设置为隐藏文件。恶意软件寻找不会引起怀疑的图标和名称，用户双击恶意软件将启动控制面板（如图11）来误导受害者。实际上，双击图标不会启动恶意文件，使用Java启动程序后恶意软件才会开始窃取信息。

![image.png](https://image.3001.net/images/20200414/1586827069_5e950f3d9bed8.png!small)  

![image.png](https://image.3001.net/images/20200414/1586827078_5e950f46f32c0.png!small)  

写入注册表‘HKEY_CURRENT_USER \ Software \ Microsoft \ Windows \ CurrentVersion \
Run’，确保计算机重启后自动运行恶意软件。恶意软件会尝试连接21736.xyz的1505端口：

![image.png](https://image.3001.net/images/20200414/1586827198_5e950fbe95aa0.png!small)  

上图为Adwind 3.0标准版操作界面，提供以下功能：

> 1、截屏  
>
>
> 2、拍摄照片，录制视频或声音
>
> 3、窃取文件，缓存密码和Web数据
>
> 4、收集键盘记录
>
> 5、收集VPN证书
>
> 6、控制Android设备的SMS
>
> 7、目标网络横向移动

## IOCs

### C&C

> 15438[.]xyz  
>
>
> 12724[.]xyz
>
> 21736[.]xyz

### Documents  

> c71663808fcbab56682602c9e97de8c3a761f4ed
>
> 5749253092cad3e8f7ddf50ce04beda666005c06
>
> aeb56403f3d3950a530663dca5ecb7530d7fec3d
>
> b3281798cc961738f9c7e6b269492c0f9bb47f08
>
> b4a8dfe2eebaf436c021458e515baf39ed812740
>
> dd0e3c99d3a62e4b45008ffb2f9f046399dc9603
>
> 72bd643d71cd725ac59e6fc76a4617180e652ddf
>
> 0914962f88e854527d9b4822fa6d2ff31abc88d4
>
> 099a4689f83e9136877f707f853bd906e47abb28
>
> 57045445bb365d711c411f3d61dcc71c416a29b1
>
> 81dd7442049535b1e1c5f2904a1e02a6a67ce3ad
>
> 867226868146118784a1caad4509653524560008
>
> 1ad020f084ee146c4bff08e94c6c162c2cdc45b7
>
> 20043296337725ad3dc6e304642d1f932c781f48
>
> 43922917c4cbedc248808d592e3a2eec3671639b
>
> 5d87e1fdba078f591bee4cde00daf59d83e38129
>
> 884bf4ae3b1ecaea6c058f19fce92fbe09214ecf
>
> 8ca09bebe64bc1f8a2b5e50d4883f81d58a9f9fc
>
> 9c2360e8b2256cc7e839e215b5b1892d997378c7
>
> 20413ca7b6b034be9e492a949b92dad96171b96a
>
> 29f03c2651f1f555ec55d0cbee0d937c859c47af
>
> 2c71a5896716b12742be84f11a2b6644cb1d08d5
>
> 350618e55e6c7c2c572f7ba22319991881c956c9
>
> 40050a73fdb3dee718a77c2b300ca7d1c1a62b96
>
> 7c179f13f2e16bb77df0ef0105368be66477cb56
>
> 7d6c9f8b025cf5dcf2a214b3f407e46d2174d4d5
>
> 7ee216ddb55b31f6657d5ef2f4b383ca5205ca11
>
> b3e8a2cfa3c711b4cca896e586fc2c0dd1a64576
>
> ca6bb68098d965fc6d22e236d7147905a8a5b313
>
> db7b06a0b551892ec93fe06fa3df4da07b3b407c
>
> e13bcdcf48575579f1b6ec923cf0a61c6c9be1d0
>
> efec9d9d8234ac7bee2482601cb44f295d72bf47

### JAR dropper

> 8ca09bebe64bc1f8a2b5e50d4883f81d58a9f9fc
>
> 981c98fa370ee934a2754a457a830bcf1e381fbe
>
> ce0b09339b565a6613***5a372f83f4003a81190

### JAR payloads

> 1a5aefbf734564b499f2c0f7269da4b6ed1d95f6
>
> 7f3f31249c0390846df9ffdcb246ae49bc9fa1a4

 ***参考来源：[checkpoint](https://research.checkpoint.com/2020/the-turkish-rat-distributes-evolved-adwind-in-a-massive-ongoing-phishing-campaign/)，由Kriston编译，转载请注明来自FreeBuf.COM **  

