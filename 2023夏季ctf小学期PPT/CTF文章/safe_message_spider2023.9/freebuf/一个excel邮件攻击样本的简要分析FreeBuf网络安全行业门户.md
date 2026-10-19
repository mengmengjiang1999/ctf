## 一、基本情况

六一节，收到攻击邮件，附件包含一个excel文档，诱使用户打开

![1654158767_629875af5655f6d6ba64d.png!small?1654158766567](https://image.3001.net/images/20220602/1654158767_629875af5655f6d6ba64d.png!small?1654158766567)

下载附件后，打开excel文档，显示为1个空文档，如下所示：

![1654158785_629875c14843d6a1b5311.png!small?1654158784415](https://image.3001.net/images/20220602/1654158785_629875c14843d6a1b5311.png!small?1654158784415)

其实，在打开文档的时候，后台已经打开下载连接，下载地址是：http://www.sanbarts.com/sdyy4y.exe

![1654158797_629875cdbd39acc2defa4.png!small?1654158797189](https://image.3001.net/images/20220602/1654158797_629875cdbd39acc2defa4.png!small?1654158797189)

下载保存为本地%appdata%目录下，名为word.exe：

![1654158813_629875dd08953c22dbe56.png!small?1654158812047](https://image.3001.net/images/20220602/1654158813_629875dd08953c22dbe56.png!small?1654158812047)

文件属性如下：

![1654158824_629875e872753ff7aaa36.png!small?1654158823810](https://image.3001.net/images/20220602/1654158824_629875e872753ff7aaa36.png!small?1654158823810)

同时，word.exe运行后，会在%temp%目录下生成lvjudcwop.exe，以及其他两个非exe的文档，如下图所示：

![1654158838_629875f67febe49c72c2e.png!small?1654158837573](https://image.3001.net/images/20220602/1654158838_629875f67febe49c72c2e.png!small?1654158837573)

进程执行顺序如下：excel.exe->EQNEDT32.EXE->word.exe->lvjudowop.exe，如下图所示：

![1654158851_62987603292a034f19c95.png!small?1654158850489](https://image.3001.net/images/20220602/1654158851_62987603292a034f19c95.png!small?1654158850489)

因此，可以大致推断：本次邮件是利用cve-2017-11882(EQNEDT32.EXE公式编辑器漏洞)进行攻击。攻击逻辑：访问下载[http://www.sanbarts.com/sdyy4y.exe，保存为word.exe](http://www.sanbarts.com/sdyy4y.exe%E4%B8%8B%E8%BD%BD%E4%BF%9D%E5%AD%98%E4%B8%BAword.exe)并运行，word.exe运行后又释放lvjudowop.exe运行。

## 二、word.exe简要分析

接下来，我们看看word.exe

删除%temp%目录下nsa20c4.tmp文件

![1654158872_62987618e4744b7f073af.png!small?1654158872249](https://image.3001.net/images/20220602/1654158872_62987618e4744b7f073af.png!small?1654158872249)

到0x841C位置

![1654158883_629876236161ecfe8f7f6.png!small?1654158882602](https://image.3001.net/images/20220602/1654158883_629876236161ecfe8f7f6.png!small?1654158882602)

我们直接静态看： 0x841c，也可以看出word.exe真实的EXE长度其实就到这边了，后续带的都是附加的内容。

![1654158895_6298762f68c3583354bdd.png!small?1654158895169](https://image.3001.net/images/20220602/1654158895_6298762f68c3583354bdd.png!small?1654158895169)

动态调试，可以看到ReadFile读的数据和上面静态内容一致，如下图。

![1654158908_6298763cbe817a1b48231.png!small?1654158909006](https://image.3001.net/images/20220602/1654158908_6298763cbe817a1b48231.png!small?1654158909006)

之后，释放并生成文件：kcblmjjlps、
lvjudcwop.exe、oxq57q9q0cduyzn，之后，调用CreateProcess函数运行lvjudcwop.exe，参数为kcblmjjlps文件，如下图所示：

![1654158921_62987649d6fcf8822e9af.png!small?1654158921338](https://image.3001.net/images/20220602/1654158921_62987649d6fcf8822e9af.png!small?1654158921338)

## 三、lvjudcwop.exe简要分析

首先打开kcblmjjlps文件

![1654158939_6298765bc3c0f6cb8e1bd.png!small?1654158938880](https://image.3001.net/images/20220602/1654158939_6298765bc3c0f6cb8e1bd.png!small?1654158938880)

分配一段缓冲区，并进行初始化赋值

![1654158953_62987669cd54e3b8a4929.png!small?1654158953401](https://image.3001.net/images/20220602/1654158953_62987669cd54e3b8a4929.png!small?1654158953401)

再分配一段内存，大小为0x136c（正是kcblmjjlps文件长度），调用fread读取文件内容到缓冲区0xD00000，如下图所示，读取的正是kcblmjjlps实际内容。

![1654158966_629876761ccbb360d3158.png!small?1654158965679](https://image.3001.net/images/20220602/1654158966_629876761ccbb360d3158.png!small?1654158965679)

对缓冲区0xD00000内容进行解密操作，解密后的内容如下图所示：

![1654158980_6298768489b834404253b.png!small?1654158980251](https://image.3001.net/images/20220602/1654158980_6298768489b834404253b.png!small?1654158980251)

调用EnumSystemCodePagesA函数执行解密内容（作为代码执行）

C++复制

BOOL EnumSystemCodePagesA(

[in] CODEPAGE_ENUMPROCA lpCodePageEnumProc,

[in] DWORD dwFlags

);  
  
---  
  
![1654159009_629876a1ec8a4393e01c0.png!small?1654159009929](https://image.3001.net/images/20220602/1654159009_629876a1ec8a4393e01c0.png!small?1654159009929)

汇编代码如下：

![1654159024_629876b0aef2d48323a66.png!small?1654159024324](https://image.3001.net/images/20220602/1654159024_629876b0aef2d48323a66.png!small?1654159024324)

动态获取GetTempPath、GetModuleFileName、LoadLibary、…等函数的内存地址

![1654159040_629876c06f744715bed4c.png!small?1654159040675](https://image.3001.net/images/20220602/1654159040_629876c06f744715bed4c.png!small?1654159040675)

打开oxq57q9q0cduyzn文件

![1654159052_629876cc3e7d0aa88d28e.png!small?1654159052086](https://image.3001.net/images/20220602/1654159052_629876cc3e7d0aa88d28e.png!small?1654159052086)

读取文件内容：

![1654159064_629876d81f3bfd83dfa5b.png!small?1654159064244](https://image.3001.net/images/20220602/1654159064_629876d81f3bfd83dfa5b.png!small?1654159064244)

对文件内容进行解密操作，解密后该内容其实是PE可执行文件，如下图所示：

![1654159077_629876e5e130b8f9a8aaa.png!small?1654159077623](https://image.3001.net/images/20220602/1654159077_629876e5e130b8f9a8aaa.png!small?1654159077623)

四、小结

CVE-2017-11882漏洞由于稳定、效果好等特点，经久不衰，CVE-2017-11882漏洞变异样本层出不穷。

IOCS：<http://www.sanbarts.com/sdyy4y.exe>

当前解析指向Ip：45.120.185.113

名称

|

大小

|

MD5 HASH  
  
---|---|---  
  
sdyy4y.exe/word.exe

|

253,655

|

4dc515da30da0caad44d16bce0dcf446  
  
kcblmjjlps

|

4,972

|

7af109e383f4d8db9dc950ea56808886  
  
oxq57q9q0cduyzn

|

189,439

|

56922abe546e363280c3bb3502f0c8b0  
  
lvjudcwop.exe

|

57,344

|

bd8822afbce872737ccc6a077bbf98c1

