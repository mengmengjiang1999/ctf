## 概述

Donot“肚脑虫”（APT-C-35）是疑似具有南亚背景的APT组织，其主要以周边国家的政府机构为目标进行网络攻击活动，通常以窃取敏感信息为目的。该组织具备针对Windows与Android双平台的攻击能力。

近日，奇安信威胁情报中心红雨滴在日常的威胁狩猎发现，Donot
APT组织近期攻击频繁。其利用恶意RTF模板注入以及公式编辑漏洞利用样本对周边国家地区开展了多次攻击活动。根据红雨滴研究人员跟踪分析，Donot此次的攻击活动有如下特点：

>
> 此次攻击活动中，Donot组织开始采用在RTF格式文档中的\\*\template目标控制字加载远程恶意模板文件进行攻击，该利用方式免杀效果好，样本首次上传VT时几乎没有杀软查杀。
>
>
> 捕获的样本以“泰国皇家海军第82指挥和参谋课程”、“OPS检查细节”，“OPS需求”、“国防部副本”等标题作为诱饵文档进行攻击活动。其中OPS疑似是位于泰国的石油天然气公司。根据诱饵标题猜测该组织疑似开始针对泰国开展攻击活动。
>
> 此次活动与我们2月披露的攻击活动中采用手法类似，其Payload均采用多层解密加载且大多存放在该组织服务器的”jack”目录下。
>
>
> 未发现影响国内，基于奇安信威胁情报中心的威胁情报数据的全线产品，包括威胁情报平台（TIP）、天眼高级威胁检测系统、NGSOC、奇安信态势感知等，都已经支持对此APT攻击团伙攻击活动的精准检测。

## 样本信息

此次捕获的样本多以泰国相关信息为诱饵标题，部分样本信息如下表所示：

 **文件名**

|

 **MD5**  
  
---|---  
  
 **OPS_requirements.doc**

|

8cc87eb3667aecc1bd41018f00aca559  
  
 **OPS Clearance Details.doc**

|

b7e07104bc65619b55431f6cbaaaea29  
  
 **Royal Thai Navy 82nd Command and Staff course.doc**

|

d4b45f7a937139e05f386a8ad0aba04e  
  
 **contract copy -11 Feb 21.doc**

|

6275908396d4a55c1ad8a21a82e6ada8  
  
 **MOD_Copy.doc**

|

5fdcbb85733f9e8686d582b2f1459961  
  
样本几乎均采用RTF加载带有公式编辑漏洞利用的方式开展攻击活动，且存放的远程链接采取了混淆处理，如下图所示：

![1615431240_6049864817a1966b8b07c.png!small?1615431240389](https://image.3001.net/images/20210311/1615431240_6049864817a1966b8b07c.png!small?1615431240389)

该利用方式免杀效果极好，当样本首次上传VT时，几乎没有杀软查杀：![1615431252_60498654127a0f47d8ec5.png!small](https://image.3001.net/images/20210311/1615431252_60498654127a0f47d8ec5.png!small)

当样本运行后，将尝试从远程模板获取文件加载执行，当带有公式编辑器漏洞的远程模板加载利用成功后，将经过多层解密下载执行恶意载荷。整体执行流程如下图所示：

![1615431349_604986b51dd2de7d38974.png!small](https://image.3001.net/images/20210311/1615431349_604986b51dd2de7d38974.png!small)

## 详细分析

以5fdcbb85733f9e8686d582b2f1459961样本为例，该样本信息如下：

 **文件名**

|

 **MOD_Copy.doc**  
  
---|---  
  
 **MD5**

|

5fdcbb85733f9e8686d582b2f1459961  
  
 **文件格式**

|

RTF  
  
 **远程模板文件地址**

|

http[:]//worldoption.xyz/jack/6Tuni6MNu5EMiSHjVywGxKsA1KnRi8Se.do  
  
文件使用\\*\template目标控制符，参数为url混淆后的unicode字符串。

![1615431595_604987ab22955dd1b7812.png!small](https://image.3001.net/images/20210311/1615431595_604987ab22955dd1b7812.png!small)

RTF格式中使用\uN?表示一个unciode字符。\u后跟一个带符号的16位十进制整数值接一个占位符，用？表示。N大于32767的话，则表示为负数。解混淆示例如下：

L"h" == 0x0068 == -(-0x0068) == -(0xFFFF+1-0x68) == -65432。

样本运行后，可明显看到尝试加载远程模板文件。

![1615431418_604986fa687a703f463d2.png!small](https://image.3001.net/images/20210311/1615431418_604986fa687a703f463d2.png!small)

存放远程模板文件的服务器是个开放目录，其中存放着多个恶意文件，如下所示：

![1615431433_6049870944ad517011173.png!small](https://image.3001.net/images/20210311/1615431433_6049870944ad517011173.png!small)

加载的远程模板文件是带有公式编辑漏洞利用的样本，基本信息如下：

 **文件名**

|

 **6Tuni6MNu5EMiSHjVywGxKsA1KnRi8Se.dot**  
  
---|---  
  
 **MD5**

|

87f2ff9f2cb1cc3be9cc6d2adbc9efcd  
  
 **漏洞利用**

|

CVE-2017-11882  
  
漏洞成功利用后将跳转到shellcode执行，首先进行异或解密：

![1615431660_604987ecdee297c56b4c8.png!small](https://image.3001.net/images/20210311/1615431660_604987ecdee297c56b4c8.png!small)

解密后将通过URLDownloadToCacheFileA从"http[:]//worldoption.xyz/jack/6Tuni6MNu5EMiSHjVywGxKsA1KnRi8Se"下载文件。该文件为加密的shellcode数据

![1615431732_60498834c9435d92a579f.png!small](https://image.3001.net/images/20210311/1615431732_60498834c9435d92a579f.png!small)

下载成功后，对其进行解密操作，解密算法为取反并异或0x64，，直到匹配到0xDEE89A75，并头部是否为0x90，若等于0x90则进入下一步。

![1615432122_604989bae6d7f74e648c7.png!small](https://image.3001.net/images/20210311/1615432122_604989bae6d7f74e648c7.png!small)

异或AB再次解密

![1615432142_604989cef266df942867a.png!small](https://image.3001.net/images/20210311/1615432142_604989cef266df942867a.png!small)

之后通过卡巴斯基，avast，nod32，MacFree，360杀毒软件的驱动文件检测是否存在杀软。

![1615432156_604989dcb3db1390b3d75.png!small](https://image.3001.net/images/20210311/1615432156_604989dcb3db1390b3d75.png!small)

检测再次与0xFE异或解密后0xD29字节shellcode，然后异或0xCE再解密0x100个字节

![1615432178_604989f2948a6ffee3d8a.png!small](https://image.3001.net/images/20210311/1615432178_604989f2948a6ffee3d8a.png!small)

解密成功后，进入第二段shellcode执行，并通过URLDownloadToFileA从http://worldoption.xyz/jack/6Tuni6MNu5EMiSHjVywGxKsA1KnRi8Se.dat下载文件到%Appdata%\\\wingui.dll并修复DOS头

![1615432196_60498a0478425f01886c7.png!small](https://image.3001.net/images/20210311/1615432196_60498a0478425f01886c7.png!small)

![1615432244_60498a340156bf9843342.png!small](https://image.3001.net/images/20210311/1615432244_60498a340156bf9843342.png!small)

再通过URLDownloadToFileA从http://worldoption.xyz/jack/6Tuni6MNu5EMiSHjVywGxKsA1KnRi8Se.doc
下载文件到%Temp%\\\doucument.doc用以迷惑受害者。

![1615432280_60498a588f0d35e9f3ded.png!small](https://image.3001.net/images/20210311/1615432280_60498a588f0d35e9f3ded.png!small)

下载成功后，创建计划任务每三分钟运行一次wingui.dll并调用其导出函数HPMG。

![1615432291_60498a63d1dea4b15dfcc.png!small](https://image.3001.net/images/20210311/1615432291_60498a63d1dea4b15dfcc.png!small)

创建的计划任务如下图所示：

![1615432310_60498a76462d92d2eba66.png!small](https://image.3001.net/images/20210311/1615432310_60498a76462d92d2eba66.png!small)

释放的wingui.dll是Donot组织常用的恶意代码，信息如下：

 **文件名**

|

6Tuni6MNu5EMiSHjVywGxKsA1KnRi8Se.dat  
  
---|---  
  
 **MD5**

|

17d0da6f523a7463c3e9db424f95ab42  
  
 **时间戳**

|

星期一, 01.03.2021 07:16:50 UTC  
  
 **导出DLL** **名**

|

Mvcupdte.dll  
  
通过计划任务加载成功后，将调用其导出函数HPMG首先通过两次time64的差与参数进行判断进行延时。

![1615432346_60498a9a5dc2b4d6d756e.png!small](https://image.3001.net/images/20210311/1615432346_60498a9a5dc2b4d6d756e.png!small)

创建“WinMsCompany”的互斥变量，保证只有一个实例运行。

![1615432391_60498ac787fc8f0e6b98a.png!small](https://image.3001.net/images/20210311/1615432391_60498ac787fc8f0e6b98a.png!small)

使用wmic检测Vmware虚拟机环境。

![1615432404_60498ad45405969747f77.png!small](https://image.3001.net/images/20210311/1615432404_60498ad45405969747f77.png!small)获取用户名，计算机名，使用WQL语句查询系统属性，查询CPU信息，查询硬件信息

![1615432430_60498aeec0fd9aaa42153.png!small](https://image.3001.net/images/20210311/1615432430_60498aeec0fd9aaa42153.png!small)![1615432536_60498b5864fcf413afdda.png!small](https://image.3001.net/images/20210311/1615432536_60498b5864fcf413afdda.png!small)![1615432543_60498b5f4904977e77a6b.png!small](https://image.3001.net/images/20210311/1615432543_60498b5f4904977e77a6b.png!small)![1615432549_60498b659ee739ff69ff3.png!small](https://image.3001.net/images/20210311/1615432549_60498b659ee739ff69ff3.png!small)

查询系统盘下的"\\\Program Files" "\\\Program Files (x86)")文件信息

![1615432581_60498b854abd31743b7b8.png!small](https://image.3001.net/images/20210311/1615432581_60498b854abd31743b7b8.png!small)

拼接格式化获取到的系统信息

![1615432598_60498b9691f75edf86d08.png!small](https://image.3001.net/images/20210311/1615432598_60498b9691f75edf86d08.png!small)数据编码与data字段拼接

![1615432631_60498bb7f372bd08319a0.png!small](https://image.3001.net/images/20210311/1615432631_60498bb7f372bd08319a0.png!small)

会先去请求wiki两次，再POST请求saltpodium.xyz
/vocha/ogo，并下载数据到C:\ProgramData\MJuego\JacaPM.dll。

![1615432657_60498bd1780fc88ecf4fe.png!small](https://image.3001.net/images/20210311/1615432657_60498bd1780fc88ecf4fe.png!small)使用rundll32运行JacaPM.dll的导出函数HWG，并创建计划任务。

![1615432672_60498be0057d6f646828b.png!small](https://image.3001.net/images/20210311/1615432672_60498be0057d6f646828b.png!small)

在temp目录写入windows.bat 传入参数并运行，卸载任务计划，删除自身

![1615432688_60498bf0a30f70438cac9.png!small](https://image.3001.net/images/20210311/1615432688_60498bf0a30f70438cac9.png!small)

![1615432981_60498d154a00431c17070.png!small](https://image.3001.net/images/20210311/1615432981_60498d154a00431c17070.png!small)

同时在相同主域名的queen目录下也存放了多个恶意文件，分析发现其是64为版本的恶意代码，功能代码与32位程序一致。

![1615432708_60498c047e57928ce867e.png!small](https://image.3001.net/images/20210311/1615432708_60498c047e57928ce867e.png!small)

## 溯源关联

 **奇安信威胁情报中心红雨滴团队**
结合威胁情报中心ALPHA[ti.qianxin.com](https://ti.qianxin.com/blog/ti/.qianxin/.com)平台，对此次攻击活动的手法，恶意代码等方面关联分析发现，此次攻击活动与donot存在高度相似性。在《2021年1月南亚地区APT组织攻击活动总结分析》中的肚脑虫样本c92901f2ef13374f4afd950d840e02c1，存在功能和payload执行流程的一致性，且在此次攻击活动中DLL文件添加隐藏功能函数，替换了虚拟机沙箱检测手段，说明肚脑虫组织在不断更新自身的攻击武器。

![1615432721_60498c11c3324c39673bc.png!small](https://image.3001.net/images/20210311/1615432721_60498c11c3324c39673bc.png!small)

根据样本d4b45f7a937139e05f386a8ad0aba04e的请求域名cachepage.icu可以关联到新的样本7a6559ff13f2aecd89c64c1704a68588，该样本通过线程注入shellcode下载后续payload。

![1615432736_60498c201453331de6da2.png!small](https://image.3001.net/images/20210311/1615432736_60498c201453331de6da2.png!small)

下载地址为：http[:]//cachepage.icu/queen/PLK5uovTqDpkBkGHn364mqgVAF950dhN.ico

## 总结

Donot是一个长期活跃的APT组织，同时具有Windows与Andorid双平台攻击能力，且持续更新其武器库，此次更是首次采用了RTF加载远程模板文件的方式进行免杀，且效果极好。奇安信威胁情报中心将持续追踪该组织攻击活动。

奇安信威胁情报中心再次提醒各企业用户，加强员工的安全意识培训是企业信息安全建设中最重要的一环，如有需要，企业用户可以建设态势感知，完善资产管理及持续监控能力，并积极引入威胁情报，以尽可能防御此类攻击。

目前，基于奇安信威胁情报中心的威胁情报数据的全线产品，包括威胁情报平台（TIP）、天眼高级威胁检测系统、NGSOC、奇安信态势感知等，都已经支持对此APT攻击团伙攻击活动的精准检测。

![1615432762_60498c3a38d7680288dff.png!small](https://image.3001.net/images/20210311/1615432762_60498c3a38d7680288dff.png!small)

## IOCS

 **MD5:**

b7e07104bc65619b55431f6cbaaaea29

d4b45f7a937139e05f386a8ad0aba04e

6275908396d4a55c1ad8a21a82e6ada8

5fdcbb85733f9e8686d582b2f1459961

8cc87eb3667aecc1bd41018f00aca559

C03B67720F11529F76DBD81AE9DEF650

883D668A9CAD0C68885EA8A96155C6D9

695774E0748701DDF713140C675003FE

DBDD51BF9A351F3FC5C65A66FAB21E2F

17D0DA6F523A7463C3E9DB424F95AB42

695774E0748701DDF713140C675003FE

87F2FF9F2CB1CC3BE9CC6D2ADBC9EFCD

81f83e54e60d9c99f79e77af10cb8f21

7a6559ff13f2aecd89c64c1704a68588

c7535faaf1e5f779241a77aa9065bfde

0105b9f0042f3f9974a33da060da216b

 **URL:**

requireplugin.xyz

worxbox.xyz

findingdocs.xyz

cachepage.icu

cookieslog.xyz

worldoption.xyz

saltpodium.xyz

srtreg.xyz

staticscr.xyz

## 参考链接

https://ti.qianxin.com/blog/articles/Summary-and-analysis-of-APT-attack-activities-in-South-Asia-in-January-2021/

