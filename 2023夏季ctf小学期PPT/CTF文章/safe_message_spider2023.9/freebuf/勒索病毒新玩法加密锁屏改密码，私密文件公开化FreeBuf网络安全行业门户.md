**近期，深信服安全团队通过对海外第三方数据样本的监测，捕获到勒索病毒Megacortex新型变种。该家族样本最早出现在今年1月份，并对国外多个行业发起勒索攻击行为。**

该变种相对以往所遇到的勒索病毒，在勒索手法上更为激进：不但加密用户文件，还会进一步修改Windwos登录密码，并在加密完毕后进行锁屏，更进一步还会威胁受害者，若不缴纳赎金则将主机上的文件公开。

##  一、Megacortex家族

Megacortex勒索病毒是国外较活跃的勒索家族，最初于今年1月份在VirusTotal平台上被安全研究员发现，并不断对国外多个行业进行加密勒索攻击，包括有美国、加拿大、法国和荷兰等。下图是Megacortex勒索病毒演进的时间轴：

![图1.png](https://image.3001.net/images/20191107/15730937855441.png!small)

##  二、Megacortex变种行为分析

该变种携带澳大利亚“MURSA PTY
LTD”公司的数字签名，运行后会在C:\Windows\Temp路径下释放qibfmqkeM5-0.cmd、qibfmqkeM5-1.cmd、qibfmqkeM5-2.cmd、M5-990831122.dll和M5-685889264.dll文件。

lqibfmqkeM5-0.cmd，用于删除释放到C:\Windows\Temp路径的文件。

![图2.png](https://image.3001.net/images/20191107/15730938215102.png!small)

lqibfmqkeM5-2.cmd，用于删除磁盘卷影

![图3.png](https://image.3001.net/images/20191107/15730938292543.png!small)

lM5-990831122.dll，用于遍历磁盘文件

lM5-685889264.dll，用于加密磁盘文件，加密后缀名为.m3g4c0rtx

在加密完后进行锁屏，并且修改了用户登录密码：

    
    
    lcmdline:'net user win oo/yUfojOGfTN2Kh'
    
     lcmdline:'C:\Windows\system32\net1 user Administrator oo/yUfojOGfTN2Kh'

![图4.png](https://image.3001.net/images/20191107/15730938538823.png!small)

生成勒索信息文本!-!_README_!-!.rtf，并以“若不缴纳赎金则公开文件”的形式来威胁受害者，如下图所示：

![图5.png](https://image.3001.net/images/20191107/15730938637092.png!small)

##  三、安全建议

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

### 1、病毒检测查杀

可下载如下工具，进行检测查杀

> 64位系统下载链接：
>
> <http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>
>
> 32位系统下载链接：
>
> <http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

### 2、 病毒防御

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

> 1.及时给电脑打补丁，修复漏洞。
>
> 2.对重要的数据文件定期进行非本地备份。
>
> 3.不要点击来源不明的邮件附件，不从不明网站下载软件。
>
> 4.尽量关闭不必要的文件共享权限。
>
> 5.更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。
>
> 6.如果业务上无需使用RDP的，建议关闭RDP。
>
> 7.建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。推荐使用深信服安全感知+防火墙+EDR，对内网进行感知、查杀和防护。

 ***本文作者： 深信服千里目安全实验室，转载请注明来自FreeBuf.COM**  

