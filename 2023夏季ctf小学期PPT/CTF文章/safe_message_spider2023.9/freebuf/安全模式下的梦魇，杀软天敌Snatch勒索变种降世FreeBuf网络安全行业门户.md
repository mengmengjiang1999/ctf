# **概述** ****

近日，奇安信病毒响应中心在日常样本监控过程中发现Snatch勒索家族新变种开始肆虐，其在执行过程中会创建服务，并使服务器重启进入保护模式，在安全模式下删除卷影，启动服务进行加密，由于在保护模式下大部分的杀软都无法正常运行，如果杀软没有在服务器重启之前除掉该勒索软件，那么一旦进入保护模式，勒索软件将会无可匹敌。目前已经检测到国内有用户中招，由于新变种暂无解密工具，我们提醒政企用户多加防范。

Snatch勒索最早出现于2018年末，加密文件时添加的后缀为.
Snatch,该后缀名起源于2000年上映的《Snatch》电影，在其早期勒索信的邮箱地址中(imBoristheBlade@protonmail.com)也同样来源于剧中角色，武器经销商“the
Blade”Boris Yurinov。可见，作者应该非常喜欢这部电影中的俄语系角色。

# 简要分析

Snatch勒索在2019年非常活跃，有数次版本更新，加密后缀有.FileSlack,.jupstb,.cekisan,.icp,.jimm,.hceem等，有趣的是在今年8月份时，疑似该团伙成员在地下论坛中发布寻找手中有网站权限的合作伙伴的帖子被公布在了社交网络上。

![图片.png](https://image.3001.net/images/20191212/1576125358_5df1c3ae094b5.png!small)  

其声称需要有RDP、VNC、TeamView、WebShell和Sql注入漏洞的网站权限。而且其明确拒绝了和英语系用户之间的合作。

![图片.png](https://image.3001.net/images/20191212/1576125364_5df1c3b4ede70.png!small)  

其论坛中的id:“BulletToothTony”同样也出自于《Snatch》电影中的角色，赏金猎人Bullet-Tooth
Tony。8月份之后Snatch勒索就没有了频繁的更新，攻击者应该在设计新版本的勒索程序和规划大规模的攻击。

在最近的11月份和12月份中我们发现了Snatch勒索的新变种，可能出于免杀考虑，和旧版本的勒索一样，新一批的Snatch勒索依然采用Go语言编写，通过弱口令爆破的方式远程登陆服务器，并开始信息收集和横向移动，最后将勒索软件下载到目标服务器上。

通过奇安信多维度大数据平台，我们找到了Snatch勒索最新的变种，并进行了简要的分析，样本运行后会先注册名为SuperBackupMan的服务。

![图片.png](https://image.3001.net/images/20191212/1576125392_5df1c3d04d141.png!small)![图片.png](https://image.3001.net/images/20191212/1576125398_5df1c3d6136b2.png!small)  

之后Snatch勒索软件在：

HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SafeBoot\Minimal注册表下添加SuperBackupMan和VSS两项，以便勒索加密服务和卷影服务在安全模式下能够正常运行。

![图片.png](https://image.3001.net/images/20191212/1576125408_5df1c3e0a4797.png!small)![图片.png](https://image.3001.net/images/20191212/1576125415_5df1c3e7d90a0.png!small)  

调用bcdedit.exe将操作系统设置为以安全模式启动：

![图片.png](https://image.3001.net/images/20191212/1576125424_5df1c3f0aa362.png!small)  

调用shutdown.exe重启计算机：

![图片.png](https://image.3001.net/images/20191212/1576125430_5df1c3f66c6b2.png!small)  

重启之后系统将进入安全模式，并启动SuperBackupMan服务，在安全模式下大部分的杀软的服务处于停止状态，故可以绕过杀软的检测执行加密逻辑。该服务在执行过程中不可停止、挂起和结束。

![图片.png](https://image.3001.net/images/20191212/1576125463_5df1c417e7443.png!small)  

服务启动后，会调用net命令停止当前服务，接着调用vssadmin删除卷影：

![图片.png](https://image.3001.net/images/20191212/1576125470_5df1c41e330b8.png!small)  

之后开始遍历文件进行加密，加密后缀为五位随机字母，加密过程中排除特定目录下的文件：

![图片.png](https://image.3001.net/images/20191212/1576125475_5df1c423b4bc0.png!small)![图片.png](https://image.3001.net/images/20191212/1576125480_5df1c4287be5e.png!small)  

在桌面释放以RESTORE_加密后缀_FILE的勒索信：

![图片.png](https://image.3001.net/images/20191212/1576125485_5df1c42dcc51b.png!small)  

勒索信内容如下：

![图片.png](https://image.3001.net/images/20191212/1576125492_5df1c434b1f7e.png!small)  

# 结论

 ****
通过使系统进入保护模式，并在保护模式下规避杀软、加密文件的勒索病毒很不常见，这意味着越来越多的勒索团伙在孜孜不倦的思考并编写具有“创造性”的勒索软件。勒索软件经过这几年的发展，“创新”的趋势一直没有减弱的痕迹，可以预见的是，未来几年勒索仍是政企安全的心头之患。同时这种利用思路很容易被其他勒索家族借鉴，再次提醒广大政企用户年末加强防范，提高安全意识，顺利迎接即将到来的2020年。

目前奇安信集团全线产品，包括天擎、天眼、SOC、态势感知、威胁情报平台，支持对涉及相关攻击活动的检测和相关勒索病毒的查杀。

# 安全建议

我们建议政企用户参考以下建议加强防范：

1、 对重要数据和文件按时进行备份。

2、 及时给电脑打补丁，修复漏洞。

3、 不要点击来源不明的邮件，不要从不明网站下载软件，推荐使用奇安信企业软件管家。

4、
关闭不必要的文件共享以及相关端口，如445，135，139等，如果业务没有需要的话尽量关闭3389端口或者给3389端口设置白名单配置，推荐开启天擎的防远程爆破功能。

5、 采用高强度的密码，不要使用弱口令，保证每台服务器的密码都不相同，每隔一段时间更换密码。

# 参考链接

[1]<https://threatpost.com/snatch-team-infiltrates-steals-data-ransomware/150974/>

