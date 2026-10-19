## **一、前言**

WinRAR是一个文件压缩与解压软件，由Eugene Roshal开发，首个公开版本RAR
1.3发布于1993年。CVE-2023-38831是在2023年8月15日被披露的一个高危漏洞，黑客将提前构造的恶意压缩包发给被攻击用户，可使被攻击用户执行任意代码。NVD漏洞评分7.8，级别高危。本文先讲解复现方法，再讲解漏洞原理。

##  **二、漏洞复现**

准备材料：windows虚拟机， winrar版本< 6.23，010editor

2.1 文件准备

打开一个空白目录，新建一个文件夹，命名jidian.txt1

再新建一个文本文件，命名jidian.txt2，内容随便定义

![](https://image.3001.net/images/20230831/1693450385_64f0009146ba3b40d3a95.png!small)

打开jidian.txt1文件夹，新建一个可执行文件，命名jidian.txt .cmd（注意txt后面有个空格），写入内容：start
calc。此文件的作用是打开计算器，用来演示任意命令执行。

![](https://image.3001.net/images/20230831/1693450421_64f000b511d5562c4d855.png!small)

2.2 压缩文件

全选，用winrar压缩文件，选择zip格式

![](https://image.3001.net/images/20230831/1693450530_64f00122a69b0cbd661bc.png!small)![](https://image.3001.net/images/20230831/1693450554_64f0013ac5c69008f8e24.png!small)

2.3 修改文件

将文件用010editor打开，将文件名中的1和2都改成空格，保存。

![](https://image.3001.net/images/20230831/1693450587_64f0015b338d14512a8b1.png!small)

2.4 触发

此时如果我们双击压缩包，可以看到里面包含了jidian.txt和一个同名文件夹。这也是CVE-2023-38831恶意文件最明显的特征：

![](https://image.3001.net/images/20230831/1693450611_64f0017309ea7a5ca606b.png!small)

双击jidian.txt文本文件，此时没有打开记事本，而是打开了计算器：

  

![](https://image.3001.net/images/20230831/1693450637_64f0018d1711fb555533f.png!small)

说明植入的代码被成功执行。

##  **三、漏洞原理**

调试工具：IDA7.7、everything

3.1 文件的落地过程

双击压缩包打开winrar，此时用IDA附加进程

![](https://image.3001.net/images/20230831/1693450666_64f001aac2a2c5977cb53.png!small)

打开import导入表，搜索“WriteFile”函数，查找交叉引用，将所有位置下断点。若用X64dbg可以直接下api断点，原理一样。

![](https://image.3001.net/images/20230831/1693450686_64f001be7295cda474ca7.png!small)

下好断点后F9运行，IDA会等待程序进一步操作，我们双击jidian.txt，IDA会断在WriteFile调用的位置.

![](https://image.3001.net/images/20230831/1693450734_64f001ee0a82c7c1fc947.png!small)

接下来取消无关断点，通过不断的F8调试，来到

7FF7A28EABC0函数

第一个while循环遍历包内所有文件的文件名，并全部解压。

![](https://image.3001.net/images/20230831/1693450764_64f0020c5331a2578ca66.png!small)

正常情况下同一个目录不允许有同名的文件和文件夹。但此恶意文件被强行修改成了同名，所以winrar会都进行解压。解压内容放在临时文件夹下。由于windows不允许文件以空格结尾，所以“jidian.txt
”文件会保存为“jidian.txt”（去掉空格），文件夹里的文件保存为“jidian.txt .cmd”。

![](https://image.3001.net/images/20230831/1693450813_64f0023d2f5eab805ac77.png!small)![](https://image.3001.net/images/20230831/1693450823_64f00247344253a108a02.png!small)

3.2 文件的执行过程

通过动态调试，文件名最终被送入到sub_D84AC函数的ShellExecuteExW函数里。

![](https://image.3001.net/images/20230831/1693450856_64f002689ab3391c13e70.png!small)![](https://image.3001.net/images/20230831/1693450865_64f00271448f8ff8f4ff8.png!small)ShellExecuteExW()非常灵活，会自动识别文件扩展名，并调用系统里该后缀默认的程序打开。当匹配不到已知扩展名时，会将文件当作可执行程序运行。而windows里运行可执行文件是可以省略扩展名的，系统会自动查找目录下符合前缀的可执行文件。所以我们运行”jidian.txt
”时，实际运行的是”jidian.txt .cmd”。

##  **四、修复方案**

目前该漏洞已经修复，受影响用户可升级到RARLAB WinRAR 最新版本（>=6.23）。

