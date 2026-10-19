## 背景概述

 **近日，国外安全研究人员捕获到一款名为Seon的勒索病毒，并且发现攻击者通过Bizarro
Sundown(GreenFlash)漏洞利用工具包进行传播，该漏洞利用工具包常被用于传播各类勒索病毒如GandCrab、Locky、Hermes等。Seon勒索病毒使用AES算法加密文件，修改文件后缀为
.FIXT，加密完成后弹出hta窗口与用户交互索要赎金。**

## 勒索特征

1.加密文件后缀.FIXT：

![](https://image.3001.net/images/20190521/1558422099_5ce3a2538718a.png!small)

2.勒索信息：

![](https://image.3001.net/images/20190521/1558422103_5ce3a2577a490.png!small)

![](https://image.3001.net/images/20190521/1558422107_5ce3a25b04210.png!small)

## 详细分析

1.首先生成AES密钥，存放在注册表HKEY_CURRENT_USER\Software\GNU\Display -> windowData中：

![](https://image.3001.net/images/20190521/1558422111_5ce3a25f685c1.png!small)

![](https://image.3001.net/images/20190521/1558422115_5ce3a263a8219.png!small)

2.通过ASM获取CUP信息：

![](https://image.3001.net/images/20190521/1558422120_5ce3a26840552.png!small)

3.遍历磁盘，在每个目录下释放勒索信息txt文件：

![](https://image.3001.net/images/20190521/1558422124_5ce3a26cbf8ac.png!small)

4.遍历时会判断文件的类型，避开加密包含如下字符或类型的文件：

    
    
    runas,bootsect.bak,ntuser.ini,thumbs.db,your_files_are_encrypted.txt,ntldr,iconcache.db,desktop.ini,ntuser.dat.log,bootfont.bin,ntuser.dat,boot.ini,autorun.inf,system,volume,information,programdata,application,data,$windows.~bt,program,files,tor,browser,windows,mozilla,appdata,windows.old,program,files,(x86),$recycle.bin,google,boot,mod,adv,dll,msstyles,mpa,nomedia,ocx,cmd,ps1,themepack,sys,prf,diagcfg,cab,ldf,diagpkg,icl,386,ico,cur,ics,ani,bat,com,rtp,diagcab,nls,msc,deskthemepack,idx,msp,msu,cpl,bin,shs,wpx,icns,exe,rom,theme,hlp,spl,fixt,lnk,scr,drv

5.不在忽略的类型和文件中，便使用AES算法对文件进行加密：

![](https://image.3001.net/images/20190521/1558422129_5ce3a271d9173.png!small)

6.加密完成后在Temp目录下释放startb.bat并运行，内容经过base64解密后是用于删除磁盘卷影和备份的bat命令，用于防止恢复备份：

![](https://image.3001.net/images/20190521/1558422133_5ce3a275505d7.png!small)

7.在Temp目录下释放readme.hta文件，内容经过base64解密后是勒索信息，通过mshta.exe弹出：

![](https://image.3001.net/images/20190521/1558422137_5ce3a27943663.png!small)

## 解决方案

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

### 病毒检测查杀

1、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

    
    
    64位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>
    
    32位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

[](http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z)

### 病毒防御

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1、及时给电脑打补丁，修复漏洞（包括Internet
Explorer内存损坏漏洞CVE-2016-0189、Flash类型混淆漏洞CVE-2015-7645、Flash越界读取漏洞CVE-2016-4117）。

2、对重要的数据文件定期进行非本地备份。

3、不要点击来源不明的邮件附件，不从不明网站下载软件。

4、尽量关闭不必要的文件共享权限。

5、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

6、如果业务上无需使用RDP的，建议关闭RDP。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

