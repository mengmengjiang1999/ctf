## 一、背景

 **近期截获一例利用最新公布WinRAR漏洞（CVE-2018-20250）的攻击样本，文件名为Meeting
summary.rar。该恶意ACE压缩文件内含一个名为Meeting summary的Office Word文档，诱使受害者直接解压释放该文件。**

用WinRAR打开后该压缩档包含内容如下所示。

![1.png](https://image.3001.net/images/20190321/1553137393_5c92fef1c47ba.png!small)

在winrar内一直点击进入目录可看到startups.exe的具体信息，如下图所示。

![2.png](https://image.3001.net/images/20190321/1553137248_5c92fe60e9d7a.png!small)当受害者通过WinRAR直接解压该文件便会触发该漏洞，从而释放内置的恶意程序（startups.exe）到用户windows系统的启动目录内，从而使得下次重启系统的时候该恶意程序能自动启动运行。![3.png](https://image.3001.net/images/20190321/1553137249_5c92fe61083c6.png!small)

## 二、startups.exe程序分析

文件名  |  startups.exe  
---|---  
MD5  |  7706640ac741740d1e5521ed671e8904  
SHA1  |  59773b72caefa9f882a8602a19d9210fa9ad1f65  
  
startups.exe程序执行后首先会删除以前生成的文件。在临时目录下查找以.ocra-delete-me结尾的文件并删除之。

![4.png](https://image.3001.net/images/20190321/1553137644_5c92ffec4fe09.png!small)

通过GetModuleFileName获取可执行文件全路径文件名。

然后获取exe所在的目录名称。

![5.png](https://image.3001.net/images/20190321/1553137658_5c92fffa10fc2.png!small)

设置环境变量OCRA_EXECUTABLE。

![6.png](https://image.3001.net/images/20190321/1553137670_5c9300069a79d.png!small)

打开exe文件并映射到内存。

![7.png](https://image.3001.net/images/20190321/1553137678_5c93000e37ee9.png!small)

判断文件标志0x41B6BA4E，EXE文件是否是以该四个字节为结尾。

  
![8.png](https://image.3001.net/images/20190321/1553137688_5c9300188e5f7.png!small)

利用winhex打开startups.exe，可以看到startups.exe确实以该4个字节结束。

![9.png](https://image.3001.net/images/20190321/1553137699_5c93002309fb4.png!small)

读取操作标志号所在的位置（文件尾部倒数第8个位置开始的四个字节），从上图我们可以看到标志号所在的位置是0x00009600，也就是从exe文件偏移0x0000960处取值，startups.exe中取值是0x00000004。

![10.png](https://image.3001.net/images/20190321/1553137708_5c93002c619ea.png!small)

执行0x00000004操作号相应操作，该操作是利用LZMA算法进行文件解压缩。

![11.png](https://image.3001.net/images/20190321/1553137719_5c930037744bd.png!small)

在解压缩函数004032c0操作后，解压后的内存部分数据如下所示。

![12.png](https://image.3001.net/images/20190321/1553137736_5c930048ecf72.png!small)

在解压缩数据中读取操作标志号，如上图中开始的4个字节为0x00000001，该操作是创建目录。上图中可以看到创建的目录是src目录。然后是操作标识号为0x00000002，表示的是创建文件，上图中紧跟其后的文件名为src\buby.rb。

如此一来，就把解压数据中包含的所有目录和文件创建到系统临时目录下相应的位置。  
![13.png](https://image.3001.net/images/20190321/1553137747_5c9300533b6f3.png!small)

![14.png](https://image.3001.net/images/20190321/1553137839_5c9300af3e520.png!small)

随后，通过操作标识号0x00000006进行进程创建动作。创建启动的进程是bin目录下的rubyw.exe（ruby程序），参数是src\ruby.rb。

![15.png](https://image.3001.net/images/20190321/1553137852_5c9300bcb8dca.png!small)

IDA代码如下：

![16.png](https://image.3001.net/images/20190321/1553137862_5c9300c64bc9f.png!small)

ruby.rb的内容如下：

上面代码的利用https访问[https://66.42.33.59:443/#WEZf](https://66.42.33.59/#WEZf)的内容，然后通过RtlMoveMemory、CreateThread创建并启动线程。

遗憾的是，该URL目前已经无法连接，因此无法分析进一步的恶意负载。

此外，通过网络搜索，发现上述分析中经常发现的OCRA字符串其实是一个开源项目。OCRA(OneClick Ruby Application
Builder)是一个将.rb文件打包为可执行文件的gem，生成的EXE可脱离Ruby环境运行。其原理是将Ruby程序运行所需的解释器、gems等全部打包“带走”。  
常用参数如下：

> \--windows 不显示控制台(rubyw.exe)
>
> \--console 显示控制台 (默认，ruby.exe)
>
> \--dll dllname 包含Ruby的bin目录中指定的DLL
>
> \--no-lzma 打包时禁用LZMA压缩
>
> \--quiet 不显示打包进度
>
> \--help 查看ocra帮助
>
> \--no-autoload 不包含脚本中autoload的项目
>
> \--icon 用自定义的ico替换掉默认的红宝石图标

由此，startups.exe其实就是一个由OCRA转换过来的exe文件。

## 三、结束语

> 1、利用winrar（CVE-2018-20250）漏洞；
>
> 2、利用OCRA将RB代码转换成EXE程序；
>
> 3、后续的恶意代码也是利用RB语言。

可以预期，利用WinRAR漏洞（CVE-2018-20250）传播恶意程序的攻击行为将愈发红火。此外，利用开源框架（本文OCRA）实现恶意代码加载可能成为一种趋势。

用户要对后缀名为rar的压缩文档加强警惕，建议未升级winrar补丁的用户立马更新winarar新版本或者删除UNACEV2.DLL文件使其无法支持ACE格式。此外，建议修改winrar使用习惯，不要在未明的情况下直接右键解压释放。建议双击打开后，看清楚压缩包的具体信息后在解压。

 ***本文作者：cgf99，转载请注明来自FreeBuf.COM**

