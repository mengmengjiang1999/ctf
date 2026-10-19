## **概述**

抗疫大战，我们不仅要抗现实中的病毒，还得同时应对随之而来的网络空间病毒。

在此前奇安信威胁情报中心曝光了一次黑产控制药物研究机构邮箱搞钓鱼的攻击行动后([https://mp.weixin.qq.com/s/T2FuoPMtpnVghX4BXG3yjQ](https://mp.weixin.qq.com/s?__biz=MzI2MDc2MDA4OA==&mid=2247490311&idx=1&sn=f53a621b683b5365df9ff1d4d0af5e8f&scene=21#wechat_redirect))，奇安信病毒响应中心也在日常样本监控中又发现部分勒索软件、国外黑产以及新型监控软件开始利用新冠疫情的热点进行投放攻击。

新发现的主要为以下几例：

• 名为Dharma的勒索病毒开始使用以.nocv为后缀加密文件

• CXK勒索软件在投放过程中使用武汉疫情作为诱饵

• 巴西某黑产在提供相关疫情视频的同时暗地里安装银行木马

• Parallax Rat新型监控软件使用了“CoronaVirus”作为样本名

通过奇安信大数据平台监测，我们发现国内有少部分用户中招，为防止威胁进一步扩散，病毒响应中心负责任地对相关样本进行披露和分析。  

  

##  **样本分析**  

###  **恶意代码1**

MD5| 055d1462f66a350d9886542d4d79bc2b  
---|---  
功能简介| Dharma勒索软件  
  
Dharma在执行过程中会经过一次内存加载，shellcode如下：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014115_5e4b9ea32d6a9.png!small)该shellcode的特征与我们之前分析Ryuk的info_steal模块的shellcode一致。应该为同一分发商进行传播投放。

内存加载后PDB如下：C:\crysis\Release\PDB\payload.pdb，其整体行为与之前版本差别不大，将自身复制到System32目录下实现持久化。

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014135_5e4b9eb7864ad.png!small)删除卷影：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014144_5e4b9ec0604ff.png!small)遍历进程和服务，关闭的进程和服务如下：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014152_5e4b9ec8e0099.png!small)加密的文件后缀如下：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014162_5e4b9ed21f8de.png!small)排除以下文件和目录：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014170_5e4b9edaaf9ca.png!small)加密过程中会以.id-XXXXXXX.[coronavirus@qq.com].ncov的形式添加文件后缀，最后弹出勒索框：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014179_5e4b9ee3424b0.png!small)勒索信内容如下，联系邮箱同样与新管病毒有关：coronavirus@qq.com  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014188_5e4b9eecc3744.png!small)  

###  **恶意代码2**

MD5| f94d84da27bd095fdeaf08ed4f7d8c9a  
---|---  
功能简介| 恶意Zip程序  
  
文件名为2020.1.10-2020.1.23Information onTravelers from Wuhan China to
India.zip（2020.1.10-2020.1.23从中国武汉到印度的旅行者的信息.zip），该文件被存放到蓝奏云上。  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014197_5e4b9ef5a5d57.png!small)ZIP中为可执行文件：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014206_5e4b9efebc444.png!small)经分析为CXK勒索软件，其本质为恶搞程序，加密文件后缀.cxk_nmsl：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014214_5e4b9f06bfa5a.png!small)文件内容被Base64加密，可以使用Base64解密工具恢复即可，加密完成后跳转到指定页面：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014224_5e4b9f102a84e.png!small)内容如下：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014231_5e4b9f17510a3.png!small)生成勒索信，索要B币：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014239_5e4b9f1f198b3.png!small)  

###  **恶意代码3**

MD5| 9e06fe19f47402f7706fc33****8d669  
---|---  
功能简介| 恶意MSI程序  
  
该样本为巴西某黑产组织投放的payload，文件名为“video-china02712.msi”。  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014247_5e4b9f272eabc.png!small)播放的视频如下：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014254_5e4b9f2e7ad7f.png!small)之后从hxxp://13.72.105.98:443/APfunkdrawer.iso下载银行木马，目前服务器已经无法访问。  

  

###  **恶意代码4**

MD5| 342d7aec0e3c67d437066000b53f0d61  
---|---  
功能简介| Parallax Rat  
  
样本名为：“new infected CORONAVIRUS sky03.02.2020.pif”，带有数字签名：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014265_5e4b9f39abef2.png!small)  

Parallax最早出现于2019年12月份，开发者在地下论坛进行出售收费65-175美元不等，界面如下：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014274_5e4b9f42d679a.png!small)  

其主要通过垃圾邮件进行传播：  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014282_5e4b9f4a4b667.png!small)执行过程中会对指定进程进行代码注入，之后从i.imgur.com下载图片并作为loader加载图片中的代码。  

  

##  **总结**

可以预见随着病毒在全世界范围的扩散，会有越来越多的国际黑客团伙和黑产组织开始以疫情为诱饵投放payload，通过奇安信多维度大数据关联分析发现，目前Dharma勒索软件和Parallax
Rat国内中招数量较多。

因此，鉴于国内有用户中招，奇安信病毒响应中心提醒用户，疫情在家远程办公，不要点击打开来源不明的文件，不管是邮件还是即时通信工具来源，同时提高个人的安全意识，减少用户隐私信息被盗取的风险。奇安信病毒响应中心会持续对上述家族进行持续跟踪，目前奇安信勒索病毒搜索引擎（lesuobingdu.qianxin.com）已支持上述勒索样本查询。  

![Clipboard
Image.png](https://image.3001.net/images/20200218/1582014291_5e4b9f53e4310.png!small)  

基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对该家族的精确检测。

