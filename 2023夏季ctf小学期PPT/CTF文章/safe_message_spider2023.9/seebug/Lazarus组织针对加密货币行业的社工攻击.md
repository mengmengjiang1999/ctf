**作者：深信服千里目安全实验室  
原文链接：<https://mp.weixin.qq.com/s/y-SHoh9f5qwAwqml3uf8vw>**

## 【事件背景】

近期深信服安全团队捕获到了Lazarus组织针对加密货币相关行业的社工攻击活动，该组织在寻找到攻击目标信息后，疑似通过即时通讯软件主动和目标取得联系，并发送修改过的开源PDF软件(Secure
PDF Viewer.exe)和携带加密payload的恶意PDF文件(Android Hardware Wallet.pdf)。单独打开”Secure
PDF Viewer.exe”无恶意行为，”Android Hardware
Wallet.pdf”无法用常规软件打开，所以该组织会利用社工的方式，诱使攻击目标使用exe文件查看pdf文件，最终解密出后台恶意程序执行，达到远控和窃取信息的目的。

对比了2021年初Google披露的Lazarus组织针对安全研究人员的攻击活动，发现本次活动有以下特征：

(1) 对加密货币相关目标发起攻击，符合Lazarus组织的一贯的“搞钱”目标;

(2) 本次出现的组件其执行与加载方式与2021年初披露Lazarus组织组件加载方式一致，都是”rundll32.exe 文件名 函数名 16字节校验数据
4位未知数字”;

(3) C2格式与2021年初披露的C2格式一致, 形如“image/upload/upload.asp”;

攻击流程如下：

![img](https://images.seebug.org/content/images/2021/09/6a32f8a7-c59a-4e76-9ad7-c845ed135793.png-w331s)

## 【详细分析】

诱饵pdf文件Android Hardware Wallet.pdf打开后内容如下，可根据内容和文件名判断为针对加密货币行业的攻击活动

![](https://images.seebug.org/content/images/2021/09/8c2b01b1-29aa-4f50-ac4b-60a8036b6b75.png-w331s)

其社工攻击发送文件如下，其中”Secure PDF Viewer.exe”为为攻击者修改过的PDF开源软件，”Android Hardware
Wallet.pdf” 为恶意PDF文件

![](https://images.seebug.org/content/images/2021/09/76851e4b-46c8-440e-be9f-55d6bb13ae13.png-w331s)

“Secure PDF Viewer.exe”其在文件处理逻辑部分加入了恶意代码，用于解密与执行恶意文档中的第一阶段payload

![img](https://images.seebug.org/content/images/2021/09/641ff1c2-0623-49ba-97d0-e2422117fecf.png-w331s)

首先，创建“C:\Programdata\WindowsUpdate”路径，并且读取打开文档最后4个字节数据是否存在 **标记0x78563412**
，如果存在该标记则该文档为恶意文档

![](https://images.seebug.org/content/images/2021/09/8ff5323c-7204-4e91-ac87-13cda6a45c7d.png-w331s)

读取恶意文档尾部0x208字节数据，并且使用xor解密（xor解密秘钥为0xE4）出相关数据data1

![img](https://images.seebug.org/content/images/2021/09/3933b5e5-8e66-4470-bb3e-2dac88da7697.png-w331s)

解密出的数据data1如下图，解密出的数据为第一阶段payload的相关执行参数，分别为函数名、16字节校验数据以及未知数字

![img](https://images.seebug.org/content/images/2021/09/55c895ae-bedf-4f1e-9703-31c93a57cd35.png-w331s)

该文件读取诱饵pdf文件大小，并解密该诱饵文件释放到“%appdata%”下同名文件

![img](https://images.seebug.org/content/images/2021/09/64d3a6e6-e3aa-4c55-b3b8-752a0dc05b2f.png-w331s)

接着会解密第二阶段payload数据，将第二阶段payload数据写入文件C:\ProgramData\WindowsUpdate\MSCache.cpl并通过rundll32.exe调用执行

![](https://images.seebug.org/content/images/2021/09/894ed5a1-ae5a-4eea-be8d-89714682930d.png-w331s)

其释放的第二阶段payload相关信息如下

描述 | 详细信息  
---|---  
名称 | MSCache.cpl/CAST.dll  
文件大小 | 110080 bytes  
文件类型 | exe  
文件功能 | dropper  
编译时间 | 2021-04-07 00:15:37 (UTC+0)  
开发平台及语言 | win/c++  
Pdb | /  
是否加壳 | 否  
md5 | d33bceb356a04b58ce8cf5baea860239  
  
其原名为CAST.dll最终会调用CAST_encryptW导出函数执行后续动作。

![](https://images.seebug.org/content/images/2021/09/97f68869-ce35-497f-a7a9-7d26edcc6fed.png-w331s)

接着内存加密第三阶段payload数据，并在内存展开并执行

![](https://images.seebug.org/content/images/2021/09/3d5142aa-4cab-4074-b915-5b05f0619be7.png-w331s)

其第三阶段payload相关信息如下

描述 | 详细信息  
---|---  
名称 | Dll.dll  
文件大小 | 460960 bytes  
文件类型 | exe  
文件功能 | downloader  
编译时间 | 2021-04-07 00:15:37 (UTC+0)  
开发平台及语言 | win/c++  
Pdb | /  
是否加壳 | 否  
md5 | 93d04c28e2f1448a273a8e554260bd9d  
  
第三阶段payload为一个下载器，首先会初始化相关网络请求数据

![](https://images.seebug.org/content/images/2021/09/970ca50b-0b57-40c0-8a49-75b2e54347af.png-w331s)

接着尝试向C2下载第四阶段payload并反射执行，目前C2已经无法通信，无法获取第四阶段payload数据

![](https://images.seebug.org/content/images/2021/09/7e0858e5-e917-4657-9d4d-f567421ff244.png-w331s)

## 【溯源关联】

本次出现的组件其执行与加载方式与2021年初披露Lazarus组织组件加载方式一致，都是”rundll32.exe 文件名 函数名 16字节校验数据
4位未知数字”

![](https://images.seebug.org/content/images/2021/09/9bdc0a3d-ce9c-488d-b93c-ed6769df70b2.png-w331s)
其C2格式与2021年初披露的C2格式一致，形如”image/upload/upload.asp”

![](https://images.seebug.org/content/images/2021/09/418e5b66-4b2c-45b3-b91e-9d64088c80a0.png-w331s)

基于攻击目标和技术特征多种关联结果，确定本次攻击事件其相关组织为Lazarus组织。

## 【IOC】

md5 | 1a00ef6c4cc9ae09f3f7d59cd726add1  
---|---  
| 819edb8646bf2f877ab636a8b27caafd  
url | https://www.smartaudpor[.]com/image/upload/upload.asp  
domain | www.smartaudpor[.]com  
  
## 【参考链接】

[【2021年谷歌年初披露的Lazarus报告】](https://blog.google/threat-analysis-group/new-campaign-targeting-security-researchers)  
[【深信服2021年年初披露的Lazarus分析报告】](https://mp.weixin.qq.com/s/8hLNDgrRcbvP3W0ASrwOwQ)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1719/>

