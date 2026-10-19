***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **近期，兰云科技银河实验室近期通过“兰眼下一代威胁感知系统”发现一大批通过恶意邮件进行传播的PasswordStealer木马，木马采用.net
编写，传播初期可以绕开绝大多数传统杀毒软件的检测，危害极大。该木马可以窃取包括浏览器、邮件客户端、FTP等软件的密码，传播多采用CVE-2017-11882和宏进行传播，最终将窃取的密码上传到指定的邮箱中。**![兰眼下一代威胁感知系统界面截图.png](https://image.3001.net/images/20180830/1535600317_5b8766bd4eb55.png!small)

兰眼下一代威胁感知系统界面截图

##  **1.传播分析**

通过一段时间的监控发现，该木马通过大规模投放恶意邮件进行传播，邮件中的附件带有CVE-2017-11882或者带有宏的恶意文档，并会结合社会工程学诱导人打开。

### 1.1 通过CVE-2017-11882进行传播

该rtf(MD5:
5b9e9269784eb277fce3caa8bfbb8cd3)文件使用的漏洞为CVE-2017-11882，其漏洞原理为：模块EQNEDT32.exe，在读入包含MathType的ole数据时，在拷贝公式字体名称时没有对名称长度进行校验，从而可执行任意代码。

![图片2.png](https://image.3001.net/images/20180830/1535600341_5b8766d59b33d.png!small)

通过分析最后会发现通过网络下载到临时文件并执行：

###
![图片3.png](https://image.3001.net/images/20180830/1535600351_5b8766df18488.png!small)1.2
**通过宏进行传播**

该宏样本（MD5：474886c09cb42e49ecc475cec46b4681）会通过社会工程学进行诱导点击，点击后会通过powershell脚本下载木马进行执行：

![图片4.png](https://image.3001.net/images/20180830/1535600360_5b8766e8701f7.png!small)

提取出的powershell样本，可以看到最后会通过网络进行下载木马并执行：

![图片5.png](https://image.3001.net/images/20180830/1535600369_5b8766f1e7880.png!small)

该窃密木马（MD5：453b51215acfe98b238f3d9116c203c2）使用.NET进行通过编写会通过注入的方式将关键窃密软件注入到带有有效数字签名的msbuild.exe中，最终会窃取包括浏览器、邮件客户端、FTP等多款软件的密码。

##  **2.** **dropper** **分析**

通过分析发现会发现加的壳为 SmartAssembly 6.9.0.114 版本：

![图片6.png](https://image.3001.net/images/20180830/1535600379_5b8766fb2d98c.png!small)

脱壳后，进行调试发现很多变量进行混淆，通过解密算法进行去混淆：

![图片7.png](https://image.3001.net/images/20180830/1535600388_5b876704e7813.png!small)

混淆方法是进行AES的加密然后进行进行base64编码：

![图片8.png](https://image.3001.net/images/20180830/1535600436_5b876734a5c5b.png!small)

样本会拷贝msbuild.exe
文件到临时文件夹重命名为svhost.exe，并为注入做准备。微软官方程序msbuild.exe拥有完整的数字签名，这样会在一定程度上躲避杀软查杀。

![图片9.png](https://image.3001.net/images/20180830/1535600448_5b876740a7198.png!small)

然后开始获取注入关键API的地址

![图片10.png](https://image.3001.net/images/20180830/1535600459_5b87674b45aba.png!small)

解密后

![图片11.png](https://image.3001.net/images/20180830/1535600468_5b876754d0108.png!small)

最后通过注入把从资源文件中获取并解密的主窃密木马注入到svhost.exe中

![图片12.png](https://image.3001.net/images/20180830/1535600478_5b87675ea21d5.png!small)

通过将资源文件下载并写解密程序来获取主窃密木马

![图片13.png](https://image.3001.net/images/20180830/1535600507_5b87677b185a1.png!small)![图片14.png](https://image.3001.net/images/20180830/1535600514_5b876782a8ec2.png!small)

###  **2.1** **主窃密木马**

此木马（MD5：b938ce3f4d054841f1f2d9137af7bd2f），仍然使用.NET程序进行编写，仍然使用了加密关键字符串的技术，加密算法如下，通过解密后，可以看到关键的流程：

![图片15.png](https://image.3001.net/images/20180830/1535600548_5b8767a4e1c23.png!small)

样本会先sleep一会，然后通过获取系统名称来跟下面的的几个名字进行判断，如果有下面的名字则退出程序：

![图片16.png](https://image.3001.net/images/20180830/1535600559_5b8767afafbcb.png!small)

通过分析发现窃密的数据有Chrom、firefox、Opera
Software、YandexBrowser、IE、keychain.plist（ios）、seamonkey、Comodo、MapleStudio、Chromium、orch
Browser、UCBrowser、Outlook、hunderbird、Opera
Mail、FoxmailPreview、Pocomail、Eudora、postbox、FileZilla、WS_FTP、Martin
Prikryl、CoreFTP、Paltalk、FlashFXP、SmartFTPClient 2.0等等。

![图片17.png](https://image.3001.net/images/20180830/1535600569_5b8767b973d35.png!small)

最后将窃取的数据通过SMTP协议发送到指定邮箱中：

![图片18.png](https://image.3001.net/images/20180830/1535600583_5b8767c70b9da.png!small)

此木马还有一些其他的功能，但在此次中并没有在配置文件中配置。

关闭UAC：

![图片19.png](https://image.3001.net/images/20180830/1535600595_5b8767d31db61.png!small)

设置开机自启动：

![图片20.png](https://image.3001.net/images/20180830/1535600606_5b8767de222e5.png!small)

机器重启：

![图片21.png](https://image.3001.net/images/20180830/1535600616_5b8767e8d90a4.png!small)

关闭指定进程：

![图片22.png](https://image.3001.net/images/20180830/1535600630_5b8767f6eb4a3.png!small)

关闭一些如cmd、注册表等排查工具：

![图片23.png](https://image.3001.net/images/20180830/1535600642_5b8768020481a.png!small)

下载文件并执行：

![图片24.png](https://image.3001.net/images/20180830/1535600652_5b87680c69ce9.png!small)

屏幕截图：

![图片25.png](https://image.3001.net/images/20180830/1535600665_5b876819a6302.png!small)

## 3.建议

此类木马通过大规模发放窃密软件，对客户主机中密码进行窃取，危害极大。建议提前部署具备高级威胁检测能力的安全产品进行及时监控、防范。

##  **4.** **IOC**

MD5：

    
    
    5b9e9269784eb277fce3caa8bfbb8cd3 
    
    474886c09cb42e49ecc475cec46b4681
    
    453b51215acfe98b238f3d9116c203c2
    
    b938ce3f4d054841f1f2d9137af7bd2f

URL：

[](http://wjp-com.tk/flowqqqqqqq.exe)

<http://wjp-com.tk/flowqqqqqqq.exe>

<http://ptpjm.co.id/updd/hux.exe>

***本文作者：兰云科技银河实验室，转载请注明来自FreeBuf.COM**

