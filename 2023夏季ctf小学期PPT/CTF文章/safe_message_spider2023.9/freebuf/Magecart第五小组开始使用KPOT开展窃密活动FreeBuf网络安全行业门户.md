## 一、概述

**2019年8月，安天CERT监测到了多起利用KPOT木马进行窃密的事件。我们判定这些窃密事件是由Magecart第五小组发起的，攻击者利用KPOT窃取用户加密货币钱包信息、应用账户信息以及浏览器cookies等多种信息。攻击者主要利用了垃圾邮件以及RIG和Fallout漏洞利用工具包来传播木马。**

Magecart是一个以获取经济利益为主要目的的窃取支付信息的组织，根据公开情报描述，Magecart至少有12个不同的小组，这些小组具有不同的运作方式、技术配置，成员水平也参差不齐。

Magecart的第五小组最早出现于2016年，主要利用供应链进行攻击。攻击者将窃密脚本注入到第三方服务提供商的组件库中，在线零售商在使用第三方服务提供商的服务时，可能会加载攻击者注入的窃密脚本。当用户进行在线支付时，窃密脚本运行并尝试窃取用户的支付信息。在本次发现的窃密事件中，Magecart第五小组的攻击行为和目的都发生了改变，舍弃了以往使用的专用窃密脚本而改用KPOT木马，窃取了更多的用户信息。

经验证，我们的智甲终端防御系统可实现对KPOT木马的有效防御。

## 二、KPOT木马的传播方式

### 2.1 利用垃圾邮件传播KPOT

攻击者通过购买现成的邮件地址库、根据自定义规则自动生成邮件地址、从网络上收集邮件地址等方法获取到大量邮件地址，发送大量带有恶意附件的垃圾邮件。

攻击者将KPOT木马制作成压缩包添加在邮件附件中，使用PowerPoint等正常软件的图标作为KPOT木马的图标，将KPOT木马伪装成PPT等正常文件，若用户未设置“显示文件后缀名”，则不能发现该文件实为EXE文件，当用户双击打开该伪装PPT时，就会运行KPOT木马，被窃取各种信息。

攻击者构造漏洞利用文档，将该文档添加在邮件附件中，在邮件正文中书写诱惑性文字，诱使用户打开附件中的文档。当用户打开文档时，便会触发漏洞利用代码，下载KPOT并执行，致使用户多种信息被窃取。

![](https://www.antiy.cn/images/20190926/201909262-1.jpg)

图 2-1 传播KPOT木马的钓鱼邮件

### 2.2利用RIG和Fallout漏洞利用工具包传播KPOT

攻击者攻击某网站并在网页中嵌入网页重定向代码，用户访问被攻陷的网站后，经过多次重定向，获得漏洞利用工具的着陆页（引导页），触发漏洞利用代码，从服务器下载KPOT木马到用户主机上并运行该木马，窃取用户多种信息。

![](https://www.antiy.cn/images/20190926/201909262-2.jpg)

图 2 2 漏洞利用工具包作业过程

### 2.3可能利用钓鱼网站传播KPOT

攻击者为一款名为G-Cleaner的Windows垃圾清理工具构建了官网。G-Cleaner是一个伪装成Windows垃圾清理工具的Azorult木马。当用户在搜索引擎上搜索清理工具时，有可能搜索G-Cleaner并下载该工具，在进行垃圾清理时运行该木马，导致信息被窃取。

虽然目前还未出现利用钓鱼网站传播KPOT的事件，但是从近期出现的构建虚假G-Cleaner官网和BleachBit官网传播Azorult木马的事件来看，利用这种方法传播KPOT是极有可能发生的。【1】

![](https://www.antiy.cn/images/20190926/201909262-3.jpg)

图 2-3 构建虚假G(arbage)Cleaner传播Azorult木马

![](https://www.antiy.cn/images/20190926/201909262-4.jpg)

图 2-4 构建虚假BleachBit官网传播Azorult木马

## 三、KPOT域名与Magecart第五小组联系密切

分析人员通过KPOT木马的回传数据所使用的域名关联到了多个公开的Magecart第五小组域名，如下图所示。在关联过程中发现的脚本文件init.js，经对比也与Magecart第五小组使用的窃密脚本一致。

![](https://www.antiy.cn/images/20190926/201909263-1.png)

图 3-1 通过域名关联到Magecart第五小组

关联到的脚本的结构与Magecart第五小组使用的窃密脚本结构一致。脚本的功能是为页面中所有的表单和可单击元素设置监听器，确保用户提交支付信息之前可以调用CLK函数，从表单和输入字段中提取支付信息，提取信息成功后，使用Base64算法将信息进行编码，通过HTTP
POST方式将支付信息、主机名和用户ID发送到C2服务器。功能也与Magecart第五小组的一致。

![](https://www.antiy.cn/images/20190926/201909263-2.jpg)

图 3-2 Magecart第五小组脚本和关联脚本的对比

## 四、Magecart——多个窃取支付信息的组织**

Magecart是一个以获取经济利益为主要目的的窃取支付信息的组织**，根据公开情报描述，Magecart至少有12个不同的小组，这些小组具有不同的运作方式、技术配置，成员水平也参差不齐。【2】组织信息如下表所示（暂无第十小组的相关信息）。

表 4-1 第一小组（第二小组）

名称 | 第一小组（第二小组）  
---|---  
首次发现时间 | 2015年  
目标 | 电子商务网站，无针对性。  
攻击过程 | 使用自动化工具来攻击目标网站，在网站中嵌入窃密脚本，当用户在表单中输入信息后，拷贝表单并将数据传送回服务器。  
脚本特点 | 设置计时器，超时脚本重新运行；根据URL关键字检测支付页，检查特定支付表单字段是否输入信息；HTTP POST回传数据。  
获利方式 | 使用盗窃的***信息购买商品，将商品转运欧洲进行贩卖获利。  
  
表 4-2 第三小组

名称 | 第三小组  
---|---  
首次发现时间 | 2016年  
目标 | 主要目标为活跃在南美洲的大众化在线商店和支付处理商  
攻击过程 | 攻击目标网站，在网站中嵌入窃密脚本，窃取支付信息。  
脚本特点 | 脚本中定义表单字段（包含“账单”，“货品清单”以及支付相关字段等），通过匹配表单关键字检测支付页；HTTP
POST方式回传数据，数据为JSON格式。  
  
表 4-3 第四小组

名称 | 第四小组  
---|---  
首次发现时间 | 2017年  
目标 | 电子商务网站，无针对性。  
攻击过程 | 攻击目标网站，在网站中嵌入窃密脚本，窃取支付信息。  
脚本特点 |
通过匹配关键字验证URL有效性；劫持点击事件，验证所有的支付信息输入；检查受害网站使用的协议（HTTPS或HTTP）生成不同的数据回传路径；使用预置表单替换活动表单，标准化数据；窃取的数据包含受害站点IP地址；记录脚本访问者，识别是否被分析人员分析。  
规避手段 |
伪装成正常流量（注册与广告商，解析服务提供商以及目标站点相似的域名；将脚本的JS扩展名更改为图片的扩展名，伪装成图片）；请求由受害站点发出并且包含有效的user-agent字段，才会返回窃密JS脚本，否则将会返回403 Forbidden页面或正常的脚本；窃密脚本中包含成千上万行正常代码，用于隐藏核心窃密代码。  
  
表4-4 第五小组

名称 | 第五小组  
---|---  
首次发现时间 | 2016年  
目标 | 第三方服务提供商  
攻击过程 |
供应链攻击。在线商店通常采用许多第三方服务（支付服务，web框架，校验服务，解析服务等），攻击者通过攻击这些第三方服务提供商，将恶意脚本注入其组件中，当在线商店调用这些服务完成支付时，将会运行窃密脚本，导致用户支付信息被窃取，达到攻击一个第三方服务提供商，窃取成千上万个网站上支付信息的效果。  
脚本特点 | 窃取的数据中包含用户主机名及用户唯一ID。  
规避手段 | 使用javascriptobfuscator.com提供的混淆服务混淆窃密脚本；  
  
表 4-5 第六小组

名称 | 第六小组  
---|---  
首次发现时间 | 2018年  
目标 | 针对处理大量日常付款的顶级目标（如英国航空公司British Airways和Newegg (技术组件、计算机和硬件领域最大的在线零售商之一)）  
攻击过程 | 攻击目标网站，在网站中嵌入窃密脚本，窃取交易信息。  
脚本特点 | 将恶意脚本嵌入可点击元素标签中(按钮标签、超链接标签 )，监控鼠标和触控板，在用户填写完表单信息点击提交按钮时，将窃取到的数据发送给服务器。  
获利方式 | 出售窃取到的支付卡信息  
  
表4-6 第七小组

名称 | 第七小组  
---|---  
首次发现时间 | 2018年  
目标 | 电子商务网站，无针对性  
攻击过程 | 攻击目标网站，直接在网站中嵌入窃密脚本，窃取支付信息。  
脚本特点 |
使用受害站点作为代理接收窃取到的数据；将窃取到的数据串成一个长字符串，每个数据项用“|”分割，使用Base64编码；向受害站点发起图片请求，将窃取到的数据追加到GET请求中。  
  
表 4-7 第八小组

名称 | 第八小组  
---|---  
首次发现时间 | 2018年  
目标 | 热门购物网站  
攻击过程 |
攻击者攻击了多个热门购物网站，劫持了多个购物网站的流量，当用户访问这些购物网站时时会被重定向到一个嵌入了窃密脚本的特定购物网站，当用户在该购物网站结账时，支付信息会被窃取。  
脚本特点 | 代码包含检测调试工具（如Firebug）的功能，阻止分析人员分析脚本  
  
表 4-8 第九小组

名称 | 第九小组  
---|---  
首次发现时间 | 2018年  
目标 | 主要目标为活跃在南美洲的大众化在线商店和支付处理商  
攻击过程 | 攻击目标网站，在网站中嵌入窃密脚本，窃取支付信息。  
脚本特点 |
通过域名信息检测是否存在第三小组木马的活动痕迹，将第三小组获取到的***或***账号最后一位用0-9的数字替换，破坏数据可靠性，影响第三小组贩卖支付信息。  
  
表 4-9 第十一小组

名称 | 第十一小组  
---|---  
首次发现时间 | 2016年  
目标 | 意大利、西班牙、爱尔兰 、法国 、比利时、荷兰和英国的在线零售平台  
攻击过程 | 攻击目标网站，直接在网站中嵌入窃密脚本，窃取支付信息。  
脚本特点 |
检测后台管理页面，添加“admin”、“account”、“login”和“password”关键字，不仅窃取支付信息，还窃取网站管理员的账户口令。  
  
表 4-10 第十二小组

名称 | 第十二小组  
---|---  
首次发现时间 | 2019年  
目标 | 电子商务网站  
攻击过程 |
供应链攻击。攻击者攻击第三方广告商，将窃密脚本注入到广告商的JavaScript库中，电子商务网站便会在展示广告时载入窃密脚本，导致用户在结账时支付信息被窃取。  
脚本特点 |
包含两个混淆脚本，一个用来阻止分析人员分析脚本，另一个用来进行窃密；完整性检查，用于检测脚本是否被修改；检查浏览器调试器是否打开；通过检查浏览器用户代理确认浏览器会话是否来自实际的使用者；生成一个随机数来指定个别的受害者，并使用密钥名称E-tag将其保存到LocalStorage中。  
规避手段 | 清理浏览器调试器控制台消息防止被检测和分析。  
  
## 五、KPOT木马分析

表 5-1 KPOT木马

病毒名称 | Trojan/Win32.Wacatac  
---|---  
原始文件名 | kewalohaxevirucehep.exe  
MD5 | 875A03560F534F08789485836AEF35D9  
文件大小 | 422 KB (432128 字节)  
文件格式 | BinExecute/Microsoft.EXE[:X86]  
时间戳 | 2018-09-14 03:26:48  
编译语言 | Microsoft Visual C++  
VT首次上传时间 | 2019-08-10  
VT检测结果 | 50/70  
  
### 5.1 KPOT运行流程

KPOT运行后会从C2服务器获取控制指令，根据控制指令窃取指定信息，将信息加密后回传到C2服务器。KPOT会获取系统语言版本并判断当前语言所对应的国家是否为“独立国家联合体”成员国（详见5.5小节），若是则不进行窃密操作。

![](https://www.antiy.cn/images/20190926/201909265-1.jpg)

图 5-1 KPOT流程图

### 5.2 规避反病毒程序检测

5.2.1 在内存中释放两段shellcode躲避检测

样本运行后会通过两段shellcode来执行窃密程序。

表 5-2 shellcode功能

阶段 | 功能  
---|---  
shellcode1 | 内存中释放并执行shellcode2  
shellcode2 | 进程替换，用PE文件覆盖样本主体，跳转到程序入口点，执行该PE文件  
  
![](https://www.antiy.cn/images/20190926/201909265-2.jpg)

图 5-2 通过两段shellcode执行窃密程序

5.2.2 异或加密字符串

样本为了规避反病毒程序检测，将重要字符串进行了异或加密，每个字符串对应不同的密钥。

表 5-3 字符串解密举例

异或密钥 | 字符串长度 | 密文 | 解密后结果  
---|---|---|---  
0x5C | 0x12 | 4((,fss8o:hr?31r47 | [http://d3f4.com.hk](http://d3f4.com.hk/)  
0x1E | 0x11 | 1QxT-oZrHqY\LYtGU | /OfJ3qDlVoGBRGjYK  
  
![](https://www.antiy.cn/images/20190926/201909265-3.jpg)

图 5-3 EXE文件中加密的字符串

### 5.3 创建互斥量，保证只有一个实例运行

窃密程序会根据磁盘序列号生成互斥量名称，并创建互斥量，若创建失败，则退出程序。

![](https://www.antiy.cn/images/20190926/201909265-4.jpg)

图 5-4 互斥量生成算法

### 5.4 连接C2获取控制指令5.4.1 控制指令解密算法

样本会连接C2服务器获取控制指令，通过Base64解码和XOR解密后得到控制指令。

![](https://www.antiy.cn/images/20190926/201909265-5.jpg)

图 5-5 数据解密流程

表 5-4 解密模块的异或算法伪代码

key和Data计算得到新密钥 | 新密钥与密文异或得到明文控制指令  
---|---  
key="LfB9zNRyztyNDcgN"Data=0x0~0xFFmiddle,V,i,j=0x0k=0x100do{
middle=key[i]+Data[j] V=middle+V Data[V]=Data[j] Data[j]=V j++ i++ if(i==0x10)
i=0 k--}while(k) | i,j,V1,V2,middle=0do{ i++ V1=Data[i]+V1 middle=Data[i]
Data[i]=Data[V1] Data[V1]=middle V2=Data[i]+middle+0xFF plaintext[j]=Data[V2]
XOR ciphertext[j] j++}  
  
5.4.2 控制指令格式和功能

由于C2服务器已失活，不能得到具体的控制指令，但是KPOT是一个在地下论坛中公开售卖的信息窃取恶意软件，因此可以通过其他事件中所暴露的控制指令格式来分析本样本功能。

    
    
    1111111111111110__DELIMM__IP地址__DELIMM__appdata__GRABBER__*.log,*.txt,__GRABBER__%appdata%__GRABBER__0__GRABBER__1024__DELIMM__desktop_txt__GRABBER__*.txt,__GRABBER__%userprofile%\Desktop__GRABBER__0__GRABBER__150__DELIMM____DELIMM____DELIMM__

控制指令之间通过“__DELIMM__”进行分割。【3】上述代码中共包含了4组信息。

表 5-5 控制指令格式举例码

第一组 | 第二组 | 第三组 | 第四组  
---|---|---|---  
开启或关闭相应功能 | IP地址 | GRABBER规则 | GRABBER规则  
1111111111111110 | A.B.C.D | ['appdata', '*.log,*.txt,', '%appdata%', '0',
'1024'] | ['desktop_txt', '*.txt,', '%userprofile%', '0', '150']  
  
GRABBER规则指定要搜索和窃取的文件。

表 5-6 GRABBER规则说明

第一个字段 | 第二个字段 | 第三个字段 | 第四个字段 | 第五个字段  
---|---|---|---|---  
规则名称 | 要窃取的文件 | 路径 | 最小文件大小（字节） | 最大文件大小（字节）  
desktop_txt' | *.txt | %userprofile% | 0 | 150  
  
> 1.窃取账户和浏览器cookies信息

第一组数据是一个16字节大小的字符串，“1111111111111110”，每个字节都对应一个功能的开启和关闭，1代表开启，0代表关闭。

表 5-7 16字节字符串代表的功能

功能名称 | 功能解释  
---|---  
chromium | 窃取Chrome的cookies、口令和自动填充数据  
mozilla | 窃取Firefox的cookies、口令和自动填充数据  
wininetCookies | 窃取Internet Explorer的cookies数据  
crypto | 窃取多种加密货币文件  
skype | 窃取skype账户信息  
telegram | 窃取telegram账户信息  
discord | 窃取discord账户信息  
battlenet | 窃取battle.net账户信息  
iexplore | 窃取Internet Explorer口令信息  
steam | 窃取Steam账户信息  
screenshot | 获取屏幕截图  
ftp | 窃取多种FTP客户端账户信息  
credentials | 窃取多种windows凭据信息  
jabber | 窃取多种Jabber客户端账户信息  
exeDelete | 删除exe文件  
dllDelete | 删除dll文件  
  
除了控制指令中声明的信息外，该样本还会窃取Microsoft
Outlook账户信息、VPN账户信息以及从“default.rdp”文件中获取rdp配置信息。

![](https://www.antiy.cn/images/20190926/201909265-6.jpg)

图 5-6 窃取Microsoft Outlook账户信息

> 2.第二组数据是C2服务器的IP地址。
>
> 3.GRABBER规则：['appdata', '*.log,*.txt,', '%appdata%', '0', '1024']
>
>
> 在“C:\Users\用户名\AppData\Roaming\”文件夹中搜索文件大小在0到1024字节之间，后缀名为“.log”和“.txt”的文件，窃取软件的日志信息。
>
> 4.GRABBER规则：['desktop_txt', '*.txt,', '%userprofile%', '0', '150']
>
>
> 在“C:\Users\用户名\”文件夹中搜索文件大小在0到150字节之间，后缀名为“.txt”的文件。用户可能会将一些账户口令信息保存在该目录下，攻击者可以通过在这些目录下搜索txt文件窃取账户口令信息。

### 5.5 收集系统信息回传到C2服务器

样本会收集系统信息，并以HTTP
POST方式回传到C2服务器。回传的数据经过了异或加密，加密密钥和控制指令的解密密钥相同，都为“LfB9zNRyztyNDcgN”，但异或方法不同，控制指令异或方法详见表3-4，数据加密是直接使用该密钥进行异或。样本发送给服务器的数据详见表2-9。这些数据以SYSINFORMATION或_CRED_DATA_FFFILEE为起始分隔符，以_SYSINFORMATION_CRED_DATA_或_FFFILEE_为结束分隔符。

![](https://www.antiy.cn/images/20190926/201909265-7.jpg)

图 5-7 以POST方式回传数据

表 5-8 回传到服务器的数据

前62字节结构 | 进程权限是否提升  
---|---  
进程完整性级别  
Windows版本  
语言环境  
Bot ID  
收集的系统信息  | Windows版本  
Machine GUID  
外网IP  
CPU  
RAM  
屏幕分辨率  
主机名  
用户名  
本地时间  
GPU  
键盘布局  
安装的软件  
命令执行后的输出内容 |  
  
窃取的文件内容 |  
  
  
![](https://www.antiy.cn/images/20190926/201909265-8.jpg)

图 5-8 起始分隔符和结束分隔符

### 5.6 删除自身

> 1.若样本获取控制指令失败，则退出程序，删除自身。
>
> 2.控制指令中包含是否删除自身的选项，若该选项设置为1，则删除自身。

![](https://www.antiy.cn/images/20190926/201909265-9.jpg)

图 5-9 控制指令中指定是否删除自身

## 六、总结

Magecart第五小组使用木马KPOT开展窃密活动，该木马一直都在地下论坛售卖，木马作者也一直持续进行更新。在之前的窃密活动中，Magecart第五小组一直在窃取支付信息，并未出现窃取其他信息的行为，并且一直专用窃密脚本进行窃密操作，然而在此次窃密活动中，Magecart第五小组不仅使用KPOT木马完成窃密活动，还窃取了用户多种类型的信息，攻击形式和目的都发生了改变。

### 附录一：IoCs

HASH |
FB01F0B120B61A87306B94C5FCB3DE4DF7219A040364923C858070EBAAAF1EA0E55ADC77DA695DF375AB985469B5E5E40E65C933F2E53ECEE4C677BAD5F848999D2C60CAD96E3C1C6E6FAE0FACA55CB0FCEAC5474B5F4DB3508AA2B008E90930852B3467F3A79E805B91D0CAC01BD328  
---|---  
URL |
3eueu[.]com/set.exe3prokladkaeu[.]com/set.exek0j8h7f6d5s4[.]com/set.exej5h4f9b6[.]com/set.exe3pubss[.]com/set.exe1stpubs[.]com/set.exeqposhgames[.]com/set.exe2ndpub[.]com/set.exekaiwachis[.]ug/NShnObEA4XwtlDCC/gate.phpicherryls[.]com/exec.exesetseta[.]com/set.exeinewsmvo[.]com/set.exe3prokladkaeu[.]com/taskis.exe3prokladkaeu[.]com/set.exemaper[.]info/XGu4835.246.189[.]253/gate/log.phpd3f4[.]com.hk/OfJ3qDlVoGBRGjYK/conf.phpcommbank.detailsconfirm[.]in/204/js/main2.js  
IP |
188.241.39.10188.241.39.220192.162.244.25209.99.16.11962.133.58.60162.251.80.2788.99.66.31216.58.206.23893.184.221.24035.246.189.25347.254.175.211  
  
### 附录二：参考资料

> [1]攻击者通过虚假BleachBit官网分发AZORult恶意软件
>
>
> [https://bbs.antiy.cn/forum.php?mod=viewthread&tid=83509&extra=page%3D1](https://bbs.antiy.cn/forum.php?mod=viewthread&tid=83509&extra=page%3D1)
>
> [2]RiskIQ-Flashpoint Inside Magecart Report
>
> <https://cdn.riskiq.com/wp-content/uploads/2018/11/RiskIQ-Flashpoint-Inside-> MageCart-Report.pdf>
>
> [3]New KPOT v2.0 stealer brings zero persistence and in-memory features to
> silently steal credentials
>
> <https://www.proofpoint.com/us/threat-insight/post/new-kpot-v20-stealer-> brings-zero-persistence-and-memory-features-silently-steal>
>
> [4]Ar3s Avoids Lengthy Prison Term After Cooperating With Authorities
>
> <https://www.recordedfuture.com/ar3s-prison-release/>

***本文作者：antiylab，转载请注明来自FreeBuf.COM**

