8月11日，全球IT咨询巨头埃森哲遭受了来自LockBit团伙的攻击。埃森哲事件中LockBit勒索团伙声称窃取了埃森哲超过6TB的数据，要求埃森哲支付5000万美元（约3.2亿人民币）作为赎金。

埃森哲是一家以服务于政府、金融、科技、能源、制造业等多个行业的IT巨头，是全球最大的科技咨询公司之一。在此次事件中，埃森哲表示：已通过安全控制对受影响的相关服务器进行隔离，使用备份文件恢复了受影响的系统，对日常运营和客户系统没有造成影响。

埃森哲虽然在声明中淡化了此次事件对其业务正常运转的影响，但造成的数据泄露也被LockBit作为筹码，他们在延缓数据泄露的同时也表示对这些“专业”数据感兴趣的机构可以联系他们。

那么LockBit勒索团伙又是何方神圣？其实，除埃森哲外，近期已有多个国内外企业和单位遭到LockBit的攻击，深信服终端安全团队、深信服安服应急响应中心最新捕获近期事件中的LockBit
2.0变种，深度剖析LockBit攻击历程。

## 变种历史追溯

其实早在2019年9月LockBit就已经问世，当时安全人员参考了其加密后缀，将其称为“ABCD病毒”。LockBit在过去两年以中国、印度、印度尼西亚、乌克兰、英国、法国、德国等欧洲国家的企业及政府组织作为攻击目标；直至今年2021年6月，LockBit似乎受到其他勒索团伙行动的刺激，攻击活动突然加剧，再次进入大众视野：

![](https://image.3001.net/images/20210818/1629252876_611c6d0c3e7a6f6c1a94a.png!small)

而此次攻击埃森哲的是LockBit勒索团伙于今年6月推出的新型变种：LockBit2.0，该变种与一代相比，攻击手法仍然延续了弱口令猜解；从沙箱分析结果来看，两代lockbit功能行为非常相似，发生变化的是2.0采用了大量的混淆技巧，更难被反病毒引擎检出：

![](https://image.3001.net/images/20210818/1629252901_611c6d2581b08ec18efda.png!small)

## 攻击手法

在进入内网后，LockBit利用了大量的扫描工具和暴力破解工具进行横向渗透，以扩大加密面积，获取更多的赎金：

![](https://image.3001.net/images/20210818/1629252916_611c6d34ace218023d961.png!small)

（窃取Windows终端密码工具Mimikatz）![](https://image.3001.net/images/20210818/1629252928_611c6d4007e5ca1fa183c.png!small)

（第三方应用密码窃取工具，包括无线密码、Web浏览器密码、邮箱密码等）

LockBit启动密码窃取的脚本，写入Result.txt做字典用于后续的口令暴力破解攻击：

![](https://image.3001.net/images/20210818/1629252941_611c6d4dd61fe676d6c24.png!small)

## 勒索软件功能分析

分析人员查看编译时间，2021年7月26号，新鲜度很高：

![](https://image.3001.net/images/20210818/1629252956_611c6d5c4ca15bc915f06.png!small)

前期的加密准备和LockBit1.0并无太大的区别，识别系统语言，为了自身的顺利运转结束相关的防护软件和服务进程。

![](https://image.3001.net/images/20210818/1629252970_611c6d6a1811421ed813b.png!small)

获取盘符信息以及获取磁盘类型，会加密可移动磁盘，本地硬盘，网络共享文件

![](https://image.3001.net/images/20210818/1629252985_611c6d79559b73aa46b99.png!small)

创建注册表启动项实现开机自启![](https://image.3001.net/images/20210818/1629253002_611c6d8aca51c1eeffcf9.png!small)

在C:\Windows\SysWOW64下创建图标文件，并将该文件写入“计算机\HKEY_LOCAL_MACHINE\SOFTWARE\Classes\\.lockbit\DefaultIcon”注册表供加密文件时修改文件使用![](https://image.3001.net/images/20210818/1629253016_611c6d987b4d3896736e4.png!small)

该勒索使用ECC/AES加密，完成了加密会话后，ECC的完整加密会话的公钥会存储在注册表的private与public中

![](https://image.3001.net/images/20210818/1629253030_611c6da6c6f85a7668ab9.png!small)![](https://image.3001.net/images/20210818/1629253039_611c6daf0ed410a148ab8.png!small)

注册.lockbit文件打开方式，使用C:\windows\system32\mshta.exe启动释放的Lockbit-ransomware.hta文件来提示受害者。

![](https://image.3001.net/images/20210818/1629253055_611c6dbf58402849b1ad3.png!small)

并设置桌面背景为勒索提示图片

![](https://image.3001.net/images/20210818/1629253070_611c6dce04cd1dfb15c68.png!small)

### 混淆技巧

####  **技巧1：加密资源**

病毒样本采用了新的加密方法，加密了图片、字符串等资源

![](https://image.3001.net/images/20210818/1629253083_611c6ddbbd70e38981792.png!small)

解密出来的LockBit新图标

![](https://image.3001.net/images/20210818/1629253098_611c6deaa7f37f8b8f3ec.png!small)

解密出来的字符串，这里是进程结束清单

![](https://image.3001.net/images/20210818/1629253110_611c6df6e919518b42ca5.png!small)

####  **技巧2：加载动态链接库**

在需要使用动态链接库函数时，LockBit 2.0会通过以下步骤加载：

![](https://image.3001.net/images/20210818/1629253125_611c6e05d23d8c1872805.png!small)

在查找Kernel32.dll地址时，使用的方法为遍历进程PEB中的模组链，找到并返回Kernel32.dll基址

![](https://image.3001.net/images/20210818/1629253136_611c6e107c4969ef1414e.png!small)

####  **技巧3：动态调用函数**

而对于需要调用的函数，LockBit2.0会在动态链接库中遍历所有的函数并匹配hash值，最后返回所需函数地址

部分调用次数少的函数会优化变成内联函数形式

如以下函数为查找并返回wsprintf地址

![](https://image.3001.net/images/20210818/1629253151_611c6e1fa1dfe550cc075.png!small)

以下都是转化后的函数![](https://image.3001.net/images/20210818/1629253164_611c6e2c598c6db9009e6.png!small)

可以看到相比于LockBit1.0，2.0的导入表内容非常少

![](https://image.3001.net/images/20210818/1629253177_611c6e39945aa424c4904.png!small)

####  **技巧4：绕过UAC验证**

病毒样本利用Autoelevated属性的COM组件ICMALuaUtil执行ShellExe绕过UAC验证

通过互斥码{3E5FC7F9-9A51-4367-9063-A120244FBEC7}找到CMSTPLUA，打开后调用ICMALuaUtil

![](https://image.3001.net/images/20210818/1629253192_611c6e489f6898a86391b.png!small)

通过固定偏移+0x28确认是执行ShellExecuteExW

![](https://image.3001.net/images/20210818/1629253204_611c6e54c31c30de44641.png!small)

### 日常加固

1.日常生活工作中的重要的数据文件资料设置相应的访问权限，关闭不必要的文件共享功能并且定期进行非本地备份；

2.使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；

3.避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；

4.定期检测系统漏洞并且及时进行补丁修复。

