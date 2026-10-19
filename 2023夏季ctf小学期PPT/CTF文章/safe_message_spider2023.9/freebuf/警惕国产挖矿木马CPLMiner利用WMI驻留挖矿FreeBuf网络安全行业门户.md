## 背景概述

近日，深信服安全团队捕获到一款国产挖矿木马，该挖矿木马 **使用恶意WMI在系统中进行驻留** ，不断下载恶意挖矿cpl文件；cpl文件又叫控制面板项，文件
**本质是Windows可执行性文件** ，但不属于可以直接独立运行的文件，类似于dll文件需要通过可执行文件调用。

## 情报分析

攻击者使用的域名统一以1eaba4fdae.com为二级域名，三级域名为随机的数字，目前为止发现相关的C&C地址有：

 **C &C地址**

|

 **对应功能**

|

 **域名注册时间**  
  
---|---|---  
  
2340.1eaba4fdae.com/wmi.txt

|

downloader脚本

|

2020年8月  
  
2340.1eaba4fdae.com/32.txt

|

32位挖矿程序  
  
2340.1eaba4fdae.com/64.txt

|

64位挖矿程序  
  
4318.1eaba4fdae.com/cpl32.txt

|

32位挖矿程序（base64）  
  
4318.1eaba4fdae.com/cpl64.txt

|

64位挖矿程序（base64）  
  
该二级域名约在2020年8月左右注册，解密的VBS脚本变量能够识别出很多拼音单词：

![](https://image.3001.net/images/20201124/1606218123_5fbcf18b0a75b9cb2d28e.png!small)

查询攻击者的钱包地址收益，目前约超过六千元：

![](https://image.3001.net/images/20201124/1606218131_5fbcf19329cd55df41b87.png!small)

## 技术分析

恶意WMI项是经过混淆的VBS代码，使用异或过的十六进制存储：

![](https://image.3001.net/images/20201124/1606218147_5fbcf1a34e7140bf98d84.png!small)

将解码后的代码进行格式化，能够看出脚本通过拼接的地址下载一段代码进行执行，下载地址为2340.1eaba4fdae.com/wmi.txt：

![](https://image.3001.net/images/20201124/1606218163_5fbcf1b30090f44398e7b.png!small)

WMI也是一段经过多层混淆的VBS代码，而第一段VBS中的函数a则是对其进行解码操作，解码后得到的VBS中也包含部分混淆，具体表现为使用十六进制代替关键字符串，并使用随机的变量或函数名：

![](https://image.3001.net/images/20201124/1606218172_5fbcf1bc49cfb7fd1ffb7.png!small)

通过编写脚本对其进行还原，能够看出大概功能为通过地址2340.1eaba4fdae.com/32.txt下载恶意的cpl文件释放在temp下根据时间创建的目录，通过正常的系统程序control.exe对其进行加载,
同时下载x.txt到同目录，下载mum.txt到temp目录：

![](https://image.3001.net/images/20201124/1606218182_5fbcf1c61e0ea0f1ca02f.png!small)

通过control.exe调用cpl文件原理跟调用dll文件类似，其中会通过rundll32.exe最终调用文件，而cpl文件与dll文件不同的是，入口函数不是dllmain，而是CPLApplet函数；程序中使用if/else花指令来干扰调试，每个关键操作之前都会有大段的无效代码：

![](https://image.3001.net/images/20201124/1606218191_5fbcf1cf14dc3dc3747d5.png!small)

读取x.txt到内存中，对其进行两次解密，得到一个PE文件：

![](https://image.3001.net/images/20201124/1606218199_5fbcf1d7afa6f560fcd24.png!small)

将PE文件在内存中展开，该PE文件是由开源代码编译的挖矿程序：

![](https://image.3001.net/images/20201124/1606218209_5fbcf1e1d430099fae9f3.png!small)

查找并通过call调用执行其导出函数“a”：

![](https://image.3001.net/images/20201124/1606218221_5fbcf1edae278f91802f5.png!small)

连接矿池进行挖矿，数据内容经过base64编码：

![](https://image.3001.net/images/20201124/1606218252_5fbcf20c2ac1b7c973702.png!small)

解码后得到挖矿信息：

![](https://image.3001.net/images/20201124/1606218278_5fbcf226cd5bad96f57ba.png!small)

## 加固建议

1.日常生活工作中的重要的数据文件资料设置相应的访问权限，关闭不必要的文件共享功能并且定期进行非本地备份；

2.使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；

3.避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；

4.定期检测系统漏洞并且及时进行补丁修复。

