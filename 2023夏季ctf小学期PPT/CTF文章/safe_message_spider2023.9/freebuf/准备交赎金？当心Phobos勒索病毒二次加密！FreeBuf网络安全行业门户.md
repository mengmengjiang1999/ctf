## **背景概述**  

**近日，深信服安全团队接到多家企业反馈，服务器遭到勒索病毒攻击，重要数据被加密。经安全团队专家排查，该病毒是近期较为活跃的一款勒索病毒，通常通过RDP暴力破解+人工投放的方式进行攻击，攻击者成功入侵后，通常会关闭系统的安全软件防护功能，运行勒索病毒，加密后会修改文件后缀为[原文件名]+id[随机字符串]+[邮箱地址].phobos，相关的邮箱地址有tylecotebenji@aol.com、tedmundboardus@aol.com、helpyourdata@qq.com等。**

值得关注的是，该勒索病毒 **在运行过程中会进行自复制，并在注册表添加自启动项，** 如果没有清除系统中残留的病毒体，很可能会遭遇二次加密。

##  **勒索特征**

1.勒索信息如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574347_5ce5f50b8c606.png!small)

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574353_5ce5f51117363.png!small)

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574385_5ce5f53150a3d.png!small)

2.勒索病毒加密后的文件后缀名为[原文件名]+id[随机字符串]+[邮箱地址].phobos，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574375_5ce5f52788a5d.png!small)

##  **详细分析**

1.获取进程Token特权信息，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574410_5ce5f54acc775.png!small)

2.获取硬盘信息，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574415_5ce5f54f8c594.png!small)

3.解密出互斥变量名Global\00011A9E993800，创建互斥变量，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574420_5ce5f5548a08b.png!small)

4.提升进程权限，如下所示：

![Snipaste_2019-05-14_11-15-11](https://image.3001.net/images/20190523/1558574458_5ce5f57ae857c.png!small)

5.拷贝自身到C:\Users\panda\AppData\Local目录下，然后设置自启动注册表项，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574463_5ce5f57f8eed4.png!small)

设置的自启动注册表项HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574467_5ce5f583caf2c.png!small)

设置的自启动注册表项

HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574473_5ce5f589c9726.png!small)

拷贝后的文件，如下所示：

![Snipaste_2019-05-14_11-36-40](https://image.3001.net/images/20190523/1558574817_5ce5f6e19e983.png!small)

6.拷贝自身到系统启动项目录，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574821_5ce5f6e5d496c.png!small)

拷贝后的文件，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574825_5ce5f6e9a7f3f.png!small)

7.创建线程，创建管道，然后通过CreateProcess调用cmd命令，删除磁盘卷影和备份操作，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574829_5ce5f6ed3226b.png!small)

调用的相应命令，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574833_5ce5f6f13c6c7.png!small)

8.创建线程，创建管道，然后通过CreateProcess调用cmd命令，关闭防火墙，相应的命令，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574837_5ce5f6f523009.png!small)

相应的命令，如下：

netshadvfirewall set currentprofile state off\nnetsh firewall set opmode
mode=disable

exit

9.解密生成相应加密后缀，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574843_5ce5f6fbb636d.png!small)

10.解密要加密的文件后缀名列表，如下所示：

![Snipaste_2019-05-14_14-56-23](https://image.3001.net/images/20190523/1558574847_5ce5f6ffaf20b.png!small)

11.解密出不加密的文件名列表以及勒索信息超文件本件名info.hta，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574851_5ce5f7032d783.png!small)

不加密的文件名列表，如下所示：

> boot.ini、bootfontbin、ntldr、ntdetect.com、io.sys

12.解密出不加密的文件目录列表，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574855_5ce5f70764470.png!small)

相关的文件目录列表，如下所示：

C:\Windows、Program Files、Program Files(x86)

c:\windows、program files、program files(x86)

13.创建线程，遍历磁盘目录，如下所示：

![Snipaste_2019-05-14_15-57-18](https://image.3001.net/images/20190523/1558574864_5ce5f710d10a8.png!small)

14.创建线程，遍历共享目录，如下所示：

![Snipaste_2019-05-14_15-58-30](https://image.3001.net/images/20190523/1558574868_5ce5f7143000f.png!small)

15.遍历文件，如下所示：

![遍历文件](https://image.3001.net/images/20190523/1558574875_5ce5f71b27032.png!small)

16.设置加密的密钥，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574880_5ce5f720ac444.png!small)

加密文件，加密的后缀名为.id[1A9E9938-0001].[tedmundboardus@aol.com].phobos,如下所示：

![Snipaste_2019-05-14_15-55-51](https://image.3001.net/images/20190523/1558574884_5ce5f724220d7.png!small)

18.在每个磁盘根目录下生成相应的勒索信息文件info.hta和info.txt，如下所示：

![Phobos勒索病毒二次加密](https://image.3001.net/images/20190523/1558574889_5ce5f7296d374.png!small)

##  **解决方案**

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

##  **病毒检测查杀**

深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

64位系统下载链接：

> <http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>

32位系统下载链接：

> <http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

## **病毒防御**

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

> 1、及时给电脑打补丁，修复漏洞。
>
> 2、对重要的数据文件定期进行非本地备份。
>
> 3、不要点击来源不明的邮件附件，不从不明网站下载软件。
>
> 4、尽量关闭不必要的文件共享权限。
>
> 5、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。
>
>
> 6、如果业务上无需使用RDP的，建议关闭RDP。当出现此类事件时，推荐使用深信服防火墙，或者终端检测响应平台（EDR）的微隔离功能对3389等端口进行封堵，防止扩散！

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。推荐使用深信服安全感知+防火墙+EDR，对内网进行感知、查杀和防护。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM。**

