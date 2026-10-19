## ****背景**** ** **概述****

近日，深信服终端安全团队捕获了Crylock勒索软件变种。早在2014年，名为Cryakl的勒索软件开始运营，期间进行了多次迭代后在2020年更名为Crylock。根据文件二进制信息，该勒索软件可能由Bad
Black Rabbit团伙开发。

![](https://image.3001.net/images/20210508/1620461881_6096493965ab2873bfa80.png!small)

##  ** **样本**** ** **分析****

使用Borland Dephi 7开发，利用动态函数地址和动态解密字符串做为反杀软手段；

![](https://image.3001.net/images/20210508/1620461893_6096494579718cb28a1a7.png!small)

调用的动态地址函数从数据段解密字符串；

![](https://image.3001.net/images/20210508/1620461904_609649508963a95ecad7b.png!small)

随机命名拷贝勒索病毒至%Temp%目录；

![](https://image.3001.net/images/20210508/1620462447_60964b6fc66e5a0bca88b.png!small)

设置管理员模式重新运行；

![](https://image.3001.net/images/20210508/1620462461_60964b7dac7e8f7c318d6.png!small)

添加开机自启；

![](https://image.3001.net/images/20210508/1620462478_60964b8e92b9f5ba8b5fc.png!small)

加密文件后缀白名单sys、dll、ini、log、bmp、bat；

![](https://image.3001.net/images/20210508/1620462489_60964b996c5a0cfc45988.png!small)

加密文件夹白名单recycle、windows、program files 、program data等；

![](https://image.3001.net/images/20210508/1620462529_60964bc148c7f31df51fe.png!small)

结束进程白名单，除系统进程外还包括远程桌面软件anydesk.exe；

![](https://image.3001.net/images/20210508/1620462541_60964bcda1cd613e5aad2.png!small)

结束进程。![](https://image.3001.net/images/20210508/1620462571_60964beb7523d2ff58b7b.png!small)

执行的CMD命令列表，用于关闭/删除文件备份；

$ vssadmin delete shadows /all /queit  
$ wbadmin DELETE SYSTEMSTATEBACKUP -keepVersions:0  
$ wbadmin DELETE BACKUP -keepVersions:0  
$ wmic SHADOWCOPY DELETE  
$ bcdedit /set {{default}} recoveryenabled No  
$ bcdedit /set {{default}} bootstatuspolicy ignoreallfailures

![](https://image.3001.net/images/20210508/1620463020_60964dacd515684296b54.png!small)

遍历a-z盘，先加密非系统盘，最后加密系统盘；

![](https://image.3001.net/images/20210508/1620463033_60964db9e4279efb7cba9.png!small)![](https://image.3001.net/images/20210508/1620463042_60964dc22704e44484f79.png!small)  

加密函数会根据文件大小和类型选择不同加密方式，以下其中三种加密类别：

类型

|

大小

|

加密方式  
  
---|---|---  
|

< 0x100000

|

（编号15）（默认）加密Filesize/2+1字节  
  
|

> 0x10485760

|

（编号14） 加密0x3D090字节  
  
|

< 0x30000

|

（编号18） 加密补成0x100000大小  
  
加密15（默认）

![](https://image.3001.net/images/20210508/1620463064_60964dd8eee35cef27185.png!small)

在加密结束后，每段程序末尾写入{ENCRYPTSTART}以及加密信息，生成的128位种子被加密写入程序末尾，到最后以{ENCRYPTEND}结束。

![](https://image.3001.net/images/20210508/1620463075_60964de3da905aca7b6ff.png!small)

##  ** **加密流程****

（1）勒索病毒将待加密明文分为512位一组，每生成512位密钥后异或得到密文

在测试中发现，相同密钥种子生成的密钥流相同，不受明文或密文影响

![](https://image.3001.net/images/20210508/1620463091_60964df33d6facb3cc41d.png!small)

（2）512位密钥生成器，由128位种子根据固定数组进行扩散和混淆形成密钥

![](https://image.3001.net/images/20210508/1620463107_60964e03c51c63ab85bd2.png!small)

（3）128位种子生成器，根据randomSeed函数生成

![](https://image.3001.net/images/20210508/1620463120_60964e10605d8d001ca99.png!small)

（4）randomSeed函数，根据32位初始种子生成，每次执行初始种子会以固定算法变化

![](https://image.3001.net/images/20210508/1620463130_60964e1a14f85042b60d5.png!small)

（5）初始种子，使用QueryPerformanceCounter、GetTickCount函数生成

![](https://image.3001.net/images/20210508/1620463139_60964e231c28ded26ab65.png!small)

以上分析结果表明：

  * 相同初始种子生成的512位密钥流相同，不受明文/密文影响
  * 32位初始种子以固定算法变换134775813*initSeed+1
  * 明文以512位分组并异或512位密钥得到密文

##  ** **加固建议****

1.日常生活工作中的重要的数据文件资料设置相应的访问权限，关闭不必要的文件共享功能并且定期进行非本地备份；

2.使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；

3.避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；

4.定期检测系统漏洞并且及时进行补丁修复。

