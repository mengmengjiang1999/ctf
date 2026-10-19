## 一、样本简介

**近期，国外某安全论坛公布了一款类似Globelmposter的新型勒索病毒，此勒索病毒的某些行为与Globelmposter类似，因联系邮箱中带有x_mister而被命名为X_Mister勒索病毒，该勒索病毒使用RSA+DES算法加密文件，自身不具备横向感染功能，通常由攻击者对目标进行RDP爆破后手动投放，或通过垃圾邮件传播，且加密完成后会进行自删除。**

深信服安全团队第一时间获取到相应的样本，并对样本进行了详细分析。

## 二、勒索病毒特征

1.勒索信息文本文件HOW TOBACK YOUR FILES.txt，如下所示：

![](https://image.3001.net/images/20190425/1556183750_5cc17ac6410d9.png!small)

2.加密后的文件名，[原文件名]+[Mr-X666]，如下所示：

![](https://image.3001.net/images/20190425/1556183761_5cc17ad1c6457.png!small)

## 三、详细分析

1\. 获取程序执行信息，并在内存中解密相应数据，如下所示：

![](https://image.3001.net/images/20190425/1556183765_5cc17ad581c68.png!small)

2.进行提权操作，设置进行权限为SeBackupPrivilege、SeRestorePrivilege、SeSecurityPrivilege、SeManageVolumePrivilege，如下所示：

![](https://image.3001.net/images/20190425/1556183768_5cc17ad80a9f1.png!small)

3.关闭windows defender的实时防护、行为监控等，如下所示：

![](https://image.3001.net/images/20190425/1556183774_5cc17ade0a57b.png!small)

4.设置为自启动项，实现开机自启动操作，如下所示：

![](https://image.3001.net/images/20190425/1556183776_5cc17ae0d122a.png!small)

5.遍历设定卷标盘符，如下所示：

![](https://image.3001.net/images/20190425/1556183780_5cc17ae4399a0.png!small)

6.遍历网络共享目录文件，如下所示：

![](https://image.3001.net/images/20190425/1556183783_5cc17ae7087b3.png!small)

7.遍历磁盘目录，如下所示：

![](https://image.3001.net/images/20190425/1556183786_5cc17aeabdd2b.png!small)

8.创建线程遍历共享目录和磁盘目录下的文件，然后创建线程进行加密操作，如下所示：

![](https://image.3001.net/images/20190425/1556183790_5cc17aee0ff77.png!small)

9.生成隐藏文件.BFC0E91B00AE8A0620D3，写入相应的勒索相关信息，加密后缀、勒索文本文件名、勒索软件版本号等，如下所示：

![](https://image.3001.net/images/20190425/1556183793_5cc17af108c7c.png!small)

10.生成勒索信息文本文件，如下所示：

![](https://image.3001.net/images/20190425/1556183795_5cc17af3bfd7d.png!small)

11.加密文件操作，加密算法为RSA+DES，如下所示：

![](https://image.3001.net/images/20190425/1556183799_5cc17af75ab03.png!small)

13.加密完成之后，删除自启动注册表项，如下所示：

![](https://image.3001.net/images/20190425/1556183802_5cc17afa80df6.png!small)

14.执行删除磁盘卷影、删除远程桌面连接信息 、删除日志信息等操作，如下所示：

![](https://image.3001.net/images/20190425/1556183809_5cc17b01541d1.png!small)

15.进行自删除操作，如下所示：

![](https://image.3001.net/images/20190425/1556183819_5cc17b0b55977.png!small)

## 四、 解决方案

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

### 病毒检测查杀

1、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

> 64位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>
>
> 32位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

### 病毒防御

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1、及时给电脑打补丁，修复漏洞。

2、对重要的数据文件定期进行非本地备份。

3、不要点击来源不明的邮件附件，不从不明网站下载软件。

4、尽量关闭不必要的文件共享权限。

5、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

6、如果业务上无需使用RDP的，建议关闭RDP。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

