## 一、样本简介

**深信服EDR安全团队，最近捕获到一款新型勒索病毒家族样本Vendetta。Vendetta是一款使用.NET框架开发的勒索病毒样本，会加密主机系统中大部分文件后缀名的文件，加密后缀为.vendetta，同时其具有Telegram通信功能，通过Telegram发送相应的主机进程信息以及加密信息，最后进行自删除。**

勒索信息内容如下所示：

![1545903250\(1\).png](https://image.3001.net/images/20181227/1545904163_5c24a023da7a0.png!small)

## 二、详细分析

1.样本使用.NET框架开发，无加壳，如下所示：

![1.png](https://image.3001.net/images/20181227/1545904172_5c24a02c06564.png!small)

2.判断程序是否已经运行，如果已经运行，则退出，如下所示：

![2.png](https://image.3001.net/images/20181227/1545904178_5c24a0320c001.png!small)

3.生成日志文件log.html，如下所示：

![3.png](https://image.3001.net/images/20181227/1545904184_5c24a03894476.png!small)

4.判断系统所在区域，如果为以下国家区域，则退出，如下所示：

![4.png](https://image.3001.net/images/20181227/1545904192_5c24a0400ff76.png!small)

相应的国家区域列表，如下所示：

> Russian、Russian (Belarus)、Russian (Kyrgyzstan)、Russian (Kazakhstan)、
>
> Russian(Moldova)、Russian (Russia)、Russian (Ukraine)、Bashkir (Russia)、
>
> Chechen(Russia)、Church Slavic (Russia)、Ossetic (Russia)、Sakha (Russia)、
>
>
> Tatar(Russia)、Ukrainian、Ukrainian(Ukraine)、Azerbaijani、Azerbaijani(Cyrillic)、Azerbaijani
> (Cyrillic, Azerbaijan)、Azerbaijani (Latin)
>
> Azerbaijani(Latin, Azerbaijan)、Armenian、Armenian(Armenia)、
>
> Belarusian、Belarusian (Belarus)、Kazakh (Kazakhstan)、Kyrgyz、
>
> Kyrgyz(Kyrgyzstan)、Kazakh、Romanian(Moldova)、Tajik、
>
> Tajik(Cyrillic)、Tajik (Cyrillic, Tajikistan)、Uzbek、
>
> Uzbek(Perso-Arabic)、Uzbek (Perso-Arabic, Afghanistan)、Uzbek (Cyrillic)、
>
> Uzbek(Cyrillic, Uzbekistan)、Uzbek (Latin)、Uzbek (Latin, Uzbekistan)、
>
> Turkmen、Turkmen (Turkmenistan)

5.枚举进程信息，然后生成进程信息文件processes.csv，并写入进程信息，如下所示：

![5.png](https://image.3001.net/images/20181227/1545904202_5c24a04a913f4.png!small)

6.枚举进程，结束掉相应的进程列表中的进程，如下所示：

![6.png](https://image.3001.net/images/20181227/1545904210_5c24a052e3ba1.png!small)

相应的进程列表，如下所示：

    
    
    notepad、devenv、msbuild、taskmgr、spoolsv、skypebackgroundhost、skypeapp、
    
    searchui、samsungrapidsvc、redis-server、postgres、perfwatson2、open server x64、
    
    openserver x32、open server x86、open server、nginx、named、mysqld、mongod、
    
    memcached、jenkins、java、httpd、googleupdate、ftp、chrome、calculator、
    
    firefox、winword、microsoftedge、microsoftedgecp、cmsserver、zf、dsq、
    
    sqlsrvr、qqeimguard、企业QQ、qqeimplatform、tv_x64、teamviewer 13、wpscloudsvr、
    
    WPS服务程序、提供账号登录、云存储等服务、teamviewer_service、igfxtray、igfxhk、
    
    igfxem、igfxcuiservice、tv_w32、ss_privoxy、privoxy、userclient、qqprotect、
    
    mqsvc、gnaupdaemon、mysqld-nt

7.随机生成password，如下所示：

![7.png](https://image.3001.net/images/20181227/1545904221_5c24a05d24437.png!small)

使用RSA的公钥加密相应的password，并生password文件，如下所示：

![8.png](https://image.3001.net/images/20181227/1545904230_5c24a066b2541.png!small)

RSA的公钥从公钥配置文件public.xml中读取，如下所示：

![9.png](https://image.3001.net/images/20181227/1545904239_5c24a06f59258.png!small)

8.获取要加密的文件后缀名列表，一共三千多个，如下所示：

![10.png](https://image.3001.net/images/20181227/1545904250_5c24a07a098c4.png!small)

9.创建文件加密线程，如下所示：

![11.png](https://image.3001.net/images/20181227/1545904259_5c24a0836842d.png!small)

遍历磁盘文件，如下所示：

![12.png](https://image.3001.net/images/20181227/1545904268_5c24a08c94447.png!small)

如果文件存放在以下目录，则不进行加密，如下所示：

![13.png](https://image.3001.net/images/20181227/1545904277_5c24a095dad1a.png!small)

相应的目录列表，如下所示：

    
    
    %ApplicationData%
    
    %AllUsersProfile%
    
    %ProgramData%
    
    %ProgramFiles%
    
    C:\Intel
    
    C:\Nvidia
    
    C:\intel
    
    C:\nvidia
    
    C:\Users\AllUsers
    
    C:\Users\Allusers
    
    C:\Users\allusers
    
    C:\Users\Public
    
    C:\Users\public
    
    C:\Users\acdgq\Desktop
    
    C:\Windows
    
    C:\ProgramFiles
    
    C:\ProgramFiles\Common Files
    
    C:\ProgramFiles\Common Files\Microsoft\Exchange Server
    
    C:\ProgramFiles\Common Files\Microsoft SQL Server
    
    C:\ProgramFiles\Microsoft\Exchange Server
    
    C:\ProgramFiles (x86)\Microsoft\Exchange Server
    
    C:\ProgramFiles\Microsoft SQL Server
    
    C:\ProgramFiles (x86)\Microsoft SQL Server

对遍历到的目录或文件进行相关处理，如下所示：

![14.png](https://image.3001.net/images/20181227/1545904288_5c24a0a0173f8.png!small)

并保存相应的加密文件和非加密文件的文件信息encFiles.json、nonEncFiles.json，如下所示：

![15.png](https://image.3001.net/images/20181227/1545904298_5c24a0aa54a0d.png!small)

加密文件内容，如下所示：

![16.png](https://image.3001.net/images/20181227/1545904307_5c24a0b36bd11.png!small)

10.加密文件的过程，如下所示：

![17.png](https://image.3001.net/images/20181227/1545904319_5c24a0bf5a3aa.png!small)

根据文件的大小，执行不同的加密程序，相应的加密程序如下所示：

![18.png](https://image.3001.net/images/20181227/1545904329_5c24a0c90e681.png!small)

加密后的文件为[加密后的原文件名]+vendetta，如果生成的加密后的文件名大于等于248，则使用[原文件名]+vendetta2为加密后的文件名，如下所示：

![19.png](https://image.3001.net/images/20181227/1545904340_5c24a0d420da8.png!small)

加密后的文件，如下所示：

![20.png](https://image.3001.net/images/20181227/1545904350_5c24a0de04047.png!small)

11.获取主机的相关ID，创建Telegram通讯连接，将之前生成的加密密钥以及进程列表信息通过Telegram发送，如下所示：

![21.png](https://image.3001.net/images/20181227/1545904359_5c24a0e767521.png!small)

12.加密完成之后，通过Telegram发送相应的信息以及生成的配置文件等，如下所示：

![22.png](https://image.3001.net/images/20181227/1545904368_5c24a0f0e4985.png!small)

13.生成相应的勒索信息超文本文件How to decrypt files.html，如下所示：

![23.png](https://image.3001.net/images/20181227/1545904378_5c24a0fa8c72c.png!small)

并设置为自启动项，如下所示：

![24.png](https://image.3001.net/images/20181227/1545904387_5c24a103638f5.png!small)

14.最后进行自删除操作，如下所示：

![25.png](https://image.3001.net/images/20181227/1545904396_5c24a10c902e0.png!small)

## 三、解决方案

深信服EDR产品能有效检测及防御此类勒索病毒家族样本及其变种，如下所示：

![26.png](https://image.3001.net/images/20181227/1545904405_5c24a1156f8ef.png!small)

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1.不要点击来源不明的邮件附件，不从不明网站下载软件；

2.及时给主机打补丁(永恒之蓝漏洞补丁)，修复相应的高危漏洞；

3.对重要的数据文件定期进行非本地备份；

4.尽量关闭不必要的文件共享权限以及关闭不必要的端口，如：445,135,139,3389等；

5.RDP远程服务器等连接尽量使用强密码，不要使用弱密码；

6.安装专业的终端安全防护软件，为主机提供端点防护和病毒检测清理功能。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

