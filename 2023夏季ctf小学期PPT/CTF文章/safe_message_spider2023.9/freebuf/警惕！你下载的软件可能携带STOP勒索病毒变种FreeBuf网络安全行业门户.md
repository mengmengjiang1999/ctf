## 前言

**近日，深信服EDR安全团队捕获到一起通过捆绑软件运行勒索病毒的事件。勒索病毒与正常的应用软件捆绑在一起运行，捆绑的勒索病毒为STOP勒索病毒的变种，加密后缀为.djvu。**

## 一、勒索病毒母体携带者

cexplorer.exe是被捆绑了恶意软件的安装包，使用Resource Hacker查看其资源，可以发现其中夹藏着两个PE文件。

![](https://image.3001.net/images/20181216/1544924934_5c15af0682c19.png!small)

cexplorer.exe运行会将两个PE文件释放，如下图所示：

![](https://image.3001.net/images/20181216/1544924943_5c15af0f5cf3b.png!small)

![](https://image.3001.net/images/20181216/1544924961_5c15af2194f74.png!small)

随后运行两个PE文件，如下图所示：

![](https://image.3001.net/images/20181216/1544924972_5c15af2c66fb8.png!small)

C:\Users\weizhou\AppData\Roaming\cexplorer.exe运行，原来是个Chameleon Explorer的安装包。

![](https://image.3001.net/images/20181216/1544924981_5c15af3557cb1.png!small)

安装成功后，就能使用了，该软件是个文件系统管理软件。

![](https://image.3001.net/images/20181216/1544924990_5c15af3eaf8a4.png!small)

C:\Users\weizhou\AppData\Roaming\update.exe，就是勒索病毒体，运行后完成勒索。如下图：

![](https://image.3001.net/images/20181216/1544925007_5c15af4f114fb.png!small)

## 二、勒索病毒母体

1\. 勒索病毒母体是一个Loader加载器，如下所示：

![](https://image.3001.net/images/20181216/1544925070_5c15af8e7e437.png!small)

2\. 通过调试，在内存中解密出PE，如下所示：

![](https://image.3001.net/images/20181216/1544925081_5c15af997d79b.png!small)

3\. 然后加载到00400000内存的位置，然后执行相应的PE代码，如下图所示：

![](https://image.3001.net/images/20181216/1544925091_5c15afa38df58.png!small)

4\. 从内存中DUMP出完整的PE文件，是勒索病毒的主体模块，获取主机的地理位置，如下所示：

![](https://image.3001.net/images/20181216/1544925104_5c15afb0eaea8.png!small)

通过访问相应的网站，如果返回包含RU、BY、UA、AZ、AM、TJ、KZ、KG、UZ等国家代码的，则进行自删除操作，如下所示：

![](https://image.3001.net/images/20181216/1544925116_5c15afbcacf5f.png!small)

5\. 拷贝相应的程序到appdata\local目录下的随机目录，如下所示：

![](https://image.3001.net/images/20181216/1544925160_5c15afe85fd2e.png!small)

然后创建定时触发任务计划，如下所示：

![](https://image.3001.net/images/20181216/1544925170_5c15aff25d439.png!small)

相应的触发时间，如下所示：

![](https://image.3001.net/images/20181216/1544925181_5c15affd64594.png!small)

相应的计划任务，如下所示：

![](https://image.3001.net/images/20181216/1544925191_5c15b0070f8f9.png!small)

6\. 查询自启动注册表项，如下所示：

![](https://image.3001.net/images/20181216/1544925201_5c15b011bab9c.png!small)

然后设置相应的自启动项注册表项，如下所示：

![](https://image.3001.net/images/20181216/1544925213_5c15b01d4ae71.png!small)

7\. 获取进程运行的参数，如下所示：

![](https://image.3001.net/images/20181216/1544925224_5c15b02825c21.png!small)

然后设置相应的启动参数，启动进程，如下所示：

![](https://image.3001.net/images/20181216/1544925234_5c15b032b8d66.png!small)

相应的代码，如下所示：

![](https://image.3001.net/images/20181216/1544925245_5c15b03deed87.png!small)

执行之后，再次判断程序运行的参数，通过相应的判断，调用参数，启动程序，进行勒索加密的过程，如下所示：

![](https://image.3001.net/images/20181216/1544925258_5c15b04a732f5.png!small)

8\. 如果进程是按上面相应的参数运行的，父进程参数，如下所示：

![](https://image.3001.net/images/20181216/1544925273_5c15b0592897c.png!small)

则从内存中解密出相应的下载服务器地址列表，如下所示：

![](https://image.3001.net/images/20181216/1544925286_5c15b06652b14.png!small)

相应的恶意下载链接如下所示：

> <http://bana911.ru/1.exe>$run
>
> <http://bana911.ru/2.exe>$run
>
> <http://bana911.ru/updatewin.exe>$run
>
> <http://bana911.ru/3.exe>$run

分隔$run符号，得到相应的恶意程序下载地址，如下所示：

![](https://image.3001.net/images/20181216/1544925319_5c15b08774e12.png!small)

然后下载执行恶意程序，如下所示：

![](https://image.3001.net/images/20181216/1544925331_5c15b09333951.png!small)

9.获取相应的MAC地址，如下所示：

![](https://image.3001.net/images/20181216/1544925342_5c15b09e1e6b8.png!small)

然后生成MD5值，如下所示：

![](https://image.3001.net/images/20181216/1544925360_5c15b0b03121f.png!small)

然后追加PID=HASH值方式上传MAC信息，返回相应的数据，如下所示：

![](https://image.3001.net/images/20181216/1544925373_5c15b0bdeb41b.png!small)

相应的远程服务器网站如下：

> <http://bana911.ru/323232/get.php?pid=B0ED0332ED2154CB43506063A03AECD3>

10\. 循环遍历磁盘目录，避开以下目录，如下所示：

![](https://image.3001.net/images/20181216/1544925387_5c15b0cbef7c9.png!small)

相应的目录，如下所示：

    
    
    C:\\Windows\\
    
    C:\\Program Files (x86)\\MozillaFirefox\\
    
    C:\\Program Files (x86)\\InternetExplorer\\
    
    C:\\Program Files (x86)\\Google\\
    
    C:\\Program Files\\Mozilla Firefox\\
    
    C:\\Program Files\\Internet Explorer\\
    
    C:\\Program Files\\Google\\
    
    D:\\Windows\\
    
    D:\\Program Files (x86)\\MozillaFirefox\\
    
    D:\\Program Files (x86)\\InternetExplorer\\
    
    D:\\Program Files (x86)\\Google\\
    
    D:\\Program Files\\Mozilla Firefox\\
    
    D:\\Program Files\\Internet Explorer\\
    
    D:\\Program Files\\Google\\

遍历相应的目录文件，如下所示：

![](https://image.3001.net/images/20181216/1544925401_5c15b0d9124c9.png!small)

然后进行加密操作，如下所示：

![](https://image.3001.net/images/20181216/1544925979_5c15b31bc0b25.png!small)

整个加密过程，如下所示：

![](https://image.3001.net/images/20181216/1544926020_5c15b344189bb.png!small)

加密文件函数过程，如下所示：

![](https://image.3001.net/images/20181216/1544926044_5c15b35c5d331.png!small)

11\. 加密后的文件，如下所示：

![](https://image.3001.net/images/20181216/1544925469_5c15b11d1adc7.png!small)

同时在相应的目录下生成_openme.txt的勒索信息文本文件，如下所示：

![](https://image.3001.net/images/20181216/1544925487_5c15b12fd9d5b.png!small)

## 三、1.exe

该模块通过禁用Windows Defender和任务管理器实现自保护和隐藏。

禁用Windows Defender：

![](https://image.3001.net/images/20181216/1544925506_5c15b142be59d.jpg!small)

禁用任务管理器：

![](https://image.3001.net/images/20181216/1544925519_5c15b14fc7be3.jpg!small)

## 四、2.exe

2\. exe是一个hosts文件修改器，是为了将windows的各种更新站点，各种安全网站的站点的域名重定向127.0.0.1(localhost)

![](https://image.3001.net/images/20181216/1544925555_5c15b1737532d.png!small)

![](https://image.3001.net/images/20181216/1544925534_5c15b15ea8fe6.png!small)

![](https://image.3001.net/images/20181216/1544925568_5c15b180d1af5.png!small)

被修改之前的hosts文件：

![](https://image.3001.net/images/20181216/1544925584_5c15b190cca72.png!small)

![](https://image.3001.net/images/20181216/1544925598_5c15b19ed94df.png!small)

## 五、3.exe

3.exe其实是一个压缩包，包含被修改的TeamViewer。修改后的TeamViewer运行无界面，攻击者可通过它控制受害者主机。

![](https://image.3001.net/images/20181216/1544925612_5c15b1acc30f8.jpg!small)

## 六、updatewin.exe

为了防止加密过程中受害者发现异常并重启系统，该模块伪装成Windowsupdate的界面，制造正在进行系统升级的假象，以迷惑受害者。

![](https://image.3001.net/images/20181216/1544925625_5c15b1b90df22.jpg!small)

## 病毒检测查杀

1、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

> <http://edr.sangfor.com.cn/tool/SfabAntiBot.zip>

## 病毒防御

> 1、及时给电脑打补丁，修复漏洞。
>
> 2、对重要的数据文件定期进行非本地备份。
>
> 3、不要点击来源不明的邮件附件，不从不明网站下载软件。
>
> 4、尽量关闭不必要的文件共享权限。
>
> 5、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

