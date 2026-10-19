## 一、样本简介

**近日，深信服安全团队接到客户反馈，主机被加密勒索，经过跟踪分析，拿到了相应的样本，确认样本为Paradise勒索病毒的变种版本，并对此勒索病毒样本进行深入的分析。Paradise(天堂)勒索病毒最早出现在2018年七月份左右，感染多家企业。此次的变种借用了CrySiS家族的勒索信息，代码结构也跟早期版本有了很大的区别。**

勒索信息弹窗：

![](https://image.3001.net/images/20190321/1553168970_5c937a4aa7a4a.png!small)

勒索信息文件：

![](https://image.3001.net/images/20190321/1553168977_5c937a5103c10.png!small)

加密后的文件名：

    
    
    [原文件名]_[随机字符串]_{immortalsupport@cock.li}.p3rf0rm4

![](https://image.3001.net/images/20190321/1553168980_5c937a54abcce.png!small)

## 二、详细分析

1\. 勒索病毒母体样本，使用UPX加壳，如下所示：

![](https://image.3001.net/images/20190321/1553168986_5c937a5a74754.png!small)

2.获取函数CreateToolhelp32Snapshot、Module32FirstW的地址，如下所示：

![](https://image.3001.net/images/20190321/1553168990_5c937a5e57df5.png!small)

3.在内存解密相关数据，修改该内存属性为可读取执行，如下所示：

![](https://image.3001.net/images/20190321/1553168994_5c937a6203b15.png!small)

4.在内存中对数据进行再次解密，得到相应的代码，如下所示：

![](https://image.3001.net/images/20190321/1553168997_5c937a6505b97.png!small)

5.跳转执行解密出来的代码，如下所示：

![](https://image.3001.net/images/20190321/1553169000_5c937a680197a.png!small)

6.搜索定位GetProcAddress函数地址，如下所示：

![](https://image.3001.net/images/20190321/1553169003_5c937a6b47eda.png!small)

7.通过GetProcAddress函数获取LoadLibraryA函数地址，如下所示：

![](https://image.3001.net/images/20190321/1553169006_5c937a6e516ad.png!small)

8.通过上面获取的LoadLibraryA、GetProcAddress函数得到一系列函数的地址，如下所示：

![](https://image.3001.net/images/20190321/1553169009_5c937a71ab854.png!small)

相关的函数，如下所示：

    
    
    VirtualAlloc、VirtualProtect、VirtualFree、GetVersionExA、TerminateProcess、ExitProcess、SetErrorMode

9.获取操作系统版本信息，如下所示：

![](https://image.3001.net/images/20190321/1553169037_5c937a8ddcefe.png!small)

10.通过VirtualAlloc分配相应的内存，再内存中解密核心Payload的PE文件，如下所示：

![](https://image.3001.net/images/20190321/1553169041_5c937a912c779.png!small)

11.后面通过VirtualProtect修改0x00400000内存地址属性，并将解密的Payload代码复制到0x00400000地址处，如下所示：

![](https://image.3001.net/images/20190321/1553169044_5c937a944e382.png!small)

12.跳转执行到0x00400000内存段中的Payload入口代码处0x00402657，如下所示：

![](https://image.3001.net/images/20190321/1553169048_5c937a9865c31.png!small)

13.通过GetUserDefaultLangID获取操作系统语言ID，如下所示：

![](https://image.3001.net/images/20190321/1553169051_5c937a9b8d2d3.png!small)

如果操作系统语言为:

    
    
    Russian俄国、LANG_KAZAK哈萨克族、LANG_BELARUSIAN白俄罗斯、LANG_TATAR俄罗斯

则执行ping 127.0.0.1命令，并删除自身，如下所示：

![](https://image.3001.net/images/20190321/1553169066_5c937aaa6e7e2.png!small)

14.读取程序资源ID为1的资源数据，如下所示：

![](https://image.3001.net/images/20190321/1553169072_5c937ab09f8fd.png!small)

里面包含相应的RSA密钥以及勒索信息等信息，如下所示：

![](https://image.3001.net/images/20190321/1553169078_5c937ab6e769b.png!small)

15.关闭WindowsDefender安全软件，如下所示：

![](https://image.3001.net/images/20190321/1553169084_5c937abc00bd4.png!small)

16.拷贝自身到相应的目录，进行持久化操作，如下所示：

![](https://image.3001.net/images/20190321/1553169088_5c937ac04335e.png!small)

17.同时生成相应的勒索信息HTA文件，如下所示：

![](https://image.3001.net/images/20190321/1553169111_5c937ad7c32f6.png!small)

18.将自身和勒索信息相关文件拷贝到启动目录下面，文件名为生成随机字符串，如下所示：

![](https://image.3001.net/images/20190321/1553169115_5c937adb12998.png!small)

拷贝之后，生成相应的文件，如下所示：

![](https://image.3001.net/images/20190321/1553169118_5c937ade1c9b1.png!small)

19.通过ShellExecuteW执行runas启动程序，如下所示：

![](https://image.3001.net/images/20190321/1553169121_5c937ae11919f.png!small)

20.删除磁盘卷影操作，如下所示：

![](https://image.3001.net/images/20190321/1553169123_5c937ae3e6f99.png!small)

21.遍历进程，结束相应的进程，如下所示：

![](https://image.3001.net/images/20190321/1553169127_5c937ae7d3c26.png!small)

进程列表，如下所示：

![](https://image.3001.net/images/20190321/1553169131_5c937aeb4caf5.png!small)

22.停止相应的服务，如下所示：

![](https://image.3001.net/images/20190321/1553169134_5c937aee4cc52.png!small)

相应的服务列表，如下所示：

![](https://image.3001.net/images/20190321/1553169137_5c937af1180f0.png!small)

![](https://image.3001.net/images/20190321/1553169141_5c937af55e303.png!small)

23.生成相应的加密密钥，如下所示：

![](https://image.3001.net/images/20190321/1553169147_5c937afb91f29.png!small)

24.遍历磁盘目录，然后创建加密线程，加密文件，如下所示：

![](https://image.3001.net/images/20190321/1553169150_5c937afed76b1.png!small)

25.枚举网络共享文件夹目录，然后创建加密线程，加密文件，如下所示：

![](https://image.3001.net/images/20190321/1553169155_5c937b03a4b7d.png!small)

26.加密线程，遍历磁盘和共享目录，然后加密文件，如下所示：

![](https://image.3001.net/images/20190321/1553169158_5c937b06c7f19.png!small)

如果目录包含为以下目录字符串，则不进行加密，相应的字符串列表，如下所示：

    
    
    Windows、$Recycle.bin、System Volume Information
    
    Program Files、ProgramFiles (x86)

同时每个加密的目录下，生成Instructions with yourfiles.txt的勒索信息文本文件。

27.加密文件的过程，如下所示：

![](https://image.3001.net/images/20190321/1553169163_5c937b0b81ad2.png!small)

28.生成并弹出Instructionswith your files.txt勒索信息文本文件，如下所示：

![](https://image.3001.net/images/20190321/1553169166_5c937b0ed751d.png!small)

29.弹出生成的HTA勒索信息文件，如下所示：

![](https://image.3001.net/images/20190321/1553169169_5c937b1195113.png!small)

30.发送请求连接<https://iplogger.org/1t8zw7>网站，获取收害者IP地址，如下所示：

![](https://image.3001.net/images/20190321/1553169173_5c937b153b859.png!small)

## 三、解决方案

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

### 病毒检测查杀

1、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

64位系统下载链接：

<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>

32位系统下载链接：

<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

### 病毒防御

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1、及时给电脑打补丁，修复漏洞。

2、对重要的数据文件定期进行非本地备份。

3、不要点击来源不明的邮件附件，不从不明网站下载软件。

4、尽量关闭不必要的文件共享权限。

5、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

6、如果业务上无需使用RDP的，建议关闭RDP。当出现此类事件时，推荐使用深信服防火墙，或者终端检测响应平台（EDR）的微隔离功能对3389等端口进行封堵，防止扩散！

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

