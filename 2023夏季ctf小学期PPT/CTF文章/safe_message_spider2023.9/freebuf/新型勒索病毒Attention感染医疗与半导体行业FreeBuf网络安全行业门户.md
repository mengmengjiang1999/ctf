## **背景概述**

**近日，深信服安全团队检测到一种新的勒索病毒正在活跃，攻击者针对制造行业、医疗行业等目标，通过社会工程、RDP远程爆破等方式手动投放勒索病毒，且进行加密后会人工删除勒索病毒体和入侵日志。**

该勒索病毒加密后会修改文件 **后缀为大写的随机** **[10-12]** **个英文字母**
，使用RAS+AES算法加密文件，并释放勒索信息文件，运行后会进行 **自复制**
，但通常情况下复制体会被攻击者手动删除。深信服安全团队将该勒索病毒命名为Attention勒索病毒，并进行了详细的分析。

##  **勒索特征**

1.勒索信息文件YOUR FILES ARE ENCRYPTED.TXT，如下所示：

![](https://image.3001.net/images/20190528/1559025221_5cecd6458aaf7.png!small)

2.加密后的文件后缀为大写字母的随机[10-12]个英文字母，前三个字母相同，如下所示：

![](https://image.3001.net/images/20190528/1559025226_5cecd64a262ad.png!small)

 **详细分析**

1.在%temp%目录下生成随机的文件B3A9A362.ghost，然后将00写入到文件中，如下所示：

![](https://image.3001.net/images/20190528/1559025230_5cecd64ebe7e4.png!small)

2.然后查找并删除B3A9A362.ghost，如下所示：

![](https://image.3001.net/images/20190528/1559025235_5cecd65371d16.png!small)

3.拷贝自身到%AppData%\Microsoft\Windows目录下ctfmon.exe，如下所示：

![](https://image.3001.net/images/20190528/1559025240_5cecd6581bfdd.png!small)

4.然后通过ShellExecute调用拷贝的ctfmon.exe程序，执行勒索加密操作，如下所示：

![](https://image.3001.net/images/20190528/1559025247_5cecd65f04397.png!small)

5.自删除原文件，如下所示：

![](https://image.3001.net/images/20190528/1559025260_5cecd66c160c6.png!small)

调用的参数，如下所示：

    
    
    "/cfor /l %x in (1,1,666) do ( ping -n 3 127.1 & del"C:\Users\panda\Desktop\Ransomware1.exe" & if not exist"C:\Users\panda\Desktop\Ransomware1.exe" exit )"

6.生成勒索密钥相关信息，如下所示：

![](https://image.3001.net/images/20190528/1559025268_5cecd67445336.png!small)

然后将密钥信息保存到注册表HKEY_CURRENT_USER\Software\Ghost\Service中，如下所示：

![](https://image.3001.net/images/20190528/1559025347_5cecd6c360370.png!small)

7.遍历网络共享目录，如下所示：

![](https://image.3001.net/images/20190528/1559025352_5cecd6c8e6e01.png!small)

8.遍历磁盘目录，如下所示：

![](https://image.3001.net/images/20190528/1559025357_5cecd6cd08bb2.png!small)

9.在内存中解密出勒索信息文本文件，如下所示：

![](https://image.3001.net/images/20190528/1559025363_5cecd6d32e5c4.png!small)

10.在内存中解密出不加密的文件目录，如下所示：

![](https://image.3001.net/images/20190528/1559025367_5cecd6d75a612.png!small)

不加密的文件目录列表，如下所示：

    
    
    ALLUSERPROFILE、APPDATA、WINDIR等

11.内存解密出各种不加密的文件目录，以及文件名或相关的后缀名，如下所示：

![](https://image.3001.net/images/20190528/1559025373_5cecd6dd5bd06.png!small)

不加密的文件名列表，如下所示：

    
    
    boot.ini;bootfont.bin;bootsect.bak;desktop.ini;defender.exe;iconcache.db;master.exe;master.dat;ntdetect.com;ntldr;ntuser.dat;ntuser.data.log;ntuser.ini;temp.txt;thumbs.db;unlock.exe;unlocker.exe;YOURFILES ARE ENCRYPTED.TXT;

不加密的文件目录，包含如下字符串列表，如下所示：

    
    
    .rome\;\MozillaFirefox\;\Mozilla\;\Opera Software\;\Opera\;\Tor Browser\;
    
    \CommonFiles\;\Internet Explorer\;\Windows Defender\;\Window Mail\;
    
    \WindowsMedia Player\;\Windows Multimedia Platform\;Windows NT\;
    
    \WindowsPhoto Viewer\;\Windows Security\;\Embedded Lockdown Manger\;
    
    \WindowsJournal\;\MSBuild\;\Reference Assemblies\;\Windows Sidebar\;
    
    \WindowsDefender Advanced Threat Protection\;\Microsoft\;\Package Cache\;\MicrosoftHelp\;

不加密的文件后缀名列表，如下所示：

    
    
    .bat;.cmd;.com;.cpl;.dll;.lnk;.msc;.msp;.pif;.scr;.sys;.ghost;

12.遍历目录文件，如下所示：

![](https://image.3001.net/images/20190528/1559025411_5cecd70326abd.png!small)

13.加密符合条件的文件，如下所示：

![](https://image.3001.net/images/20190528/1559025502_5cecd75e7422a.png!small)

先读取文件内容，然后进行加密操作，如下所示：

![](https://image.3001.net/images/20190528/1559025506_5cecd76211a13.png!small)

加密后的文件后缀名为随机的[10-12]个英文字母，如下所示：

![](https://image.3001.net/images/20190528/1559025509_5cecd76587a92.png!small)

##  **解决方案**

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

> 64位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>
>
> 32位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

###  ******病毒防御**

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1、及时给电脑打补丁，修复漏洞。

2、对重要的数据文件定期进行非本地备份。

3、不要点击来源不明的邮件附件，不从不明网站下载软件。

4、尽量关闭不必要的文件共享权限。

5、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

6、如果业务上无需使用RDP的，建议关闭RDP

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

