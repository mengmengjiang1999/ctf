*****本文原创作者：kaliking，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

**在安全圈里我们会经常听到或用到一些0day漏洞，在印象里我们都觉的只有真正的大神才能挖掘到这样的漏洞，事实也的确如此。不过也不要被吓到，其实大部分的0day是缓冲区溢出漏洞演化而来，只要我们了解了缓冲区溢出原理，假以时日也可以自己挖掘出0day漏洞。**

由于是本系列的开篇，所以不给大家讲解过多的原理，今天先让大家直观感受一下什么是缓冲区溢出，让各位有一个初步的认识，闲话少叙，让我们开始。

![QQ浏览器截图20190212235703.png](https://image.3001.net/images/20190212/1549987042_5c62ece21d8ff.png!small)

给大家一段c语言编写的代码，大家在DEV中编译执行一下：

    
    
    #include <stdio.h>
    
    #include <string.h>
    
          
    
    
    char name[] = "kalikingkalikingkaliking" ;
    
          
    
    
    int main()
    
    {
    
     char buffer[8];
    
     strcpy(buffer, name);
    
     printf("%s\n",buffer);
    
     getchar();
    
     return 0;
    
    }

在win7中会出现以下报错，如图所示：

![1.png](https://image.3001.net/images/20190212/1549985908_5c62e874ed6cf.png!small)有一点c语言基础的人就不难看出问题所在，在程序中我们要把变量name的值拷贝给变量buffer，但我们分配给变量的空间只有8个字节，而name的长度远远大于8个字节。这就导致系统原本分配的空间不足而占用了本来用于存储程序返回地址的空间，导致程序无法正常运行。

 **今天先不讲原理，先讲讲分析缓冲区溢出必备的几款软件：**

1. **Dev-C ++** 是一个[免费的](https://en.wikipedia.org/wiki/Free_software)全功能[集成开发环境](https://en.wikipedia.org/wiki/Integrated_development_environment)（IDE），分布在[GNU通用公共许可证下，](https://en.wikipedia.org/wiki/GNU_General_Public_License)用于 [C](https://en.wikipedia.org/wiki/C_\(programming_language\))和[C ++编程](https://en.wikipedia.org/wiki/C%2B%2B)。它是用[Delphi](https://en.wikipedia.org/wiki/Delphi_\(programming_language\))编写的。 **![dev.png](https://image.3001.net/images/20190216/1550246839_5c66e3b725888.png!small)**

免费下载地址：://sourceforge.net/projects/orwelldevcpp/files/latest/download  

2. **OllyDbg** （以其作者Oleh Yuschuk命名）是一个强调二进制代码分析的x86调试器。

![111-2.png](https://image.3001.net/images/20190216/1550246861_5c66e3cd5a754.png!small)

免费下载地址：<http://www.ollydbg.de/odbg201.zip>

  

3. **IDA** （Interactive Disassembler）是[反汇编](https://en.wikipedia.org/wiki/Disassembler)为[计算机](https://en.wikipedia.org/wiki/Computer)[软件](https://en.wikipedia.org/wiki/Software)，其生成[汇编语言](https://en.wikipedia.org/wiki/Assembly_language)[源代码](https://en.wikipedia.org/wiki/Source_code)从机器可执行代码。它支持多种[可执行文件格式](https://en.wikipedia.org/wiki/Executable)为不同[的处理器](https://en.wikipedia.org/wiki/Central_processing_unit)和[操作系统](https://en.wikipedia.org/wiki/Operating_system)。它还可以用作Windows PE，[Mac OS X ](https://en.wikipedia.org/wiki/Mac_OS_X)[Mach-O](https://en.wikipedia.org/wiki/Mach-O)和[Linux ](https://en.wikipedia.org/wiki/Linux)[ELF](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format)可执行文件的[调试器](https://en.wikipedia.org/wiki/Debugger)。

![08093505_0f8634b7db.png](https://image.3001.net/images/20190216/1550246920_5c66e40887cd2.png!small)

免费版下载地址：<https://www.hex-rays.com/products/ida/support/download_freeware.shtml>

##  **接下来介绍一下三个软件的基本使用方法：**

 ****在这里只介绍在程序分析过程中常用的方法，其余的详细使用教程请自行Google

### Dev c++的使用方法：

1.新建源代码文件

由于我们编写的源代码，只为了了解缓冲区溢出的原理，所以不必过于复杂，我们只需要新建个源代码文件就可以了，没必要创建项目文件。  
![1.png](https://image.3001.net/images/20190216/1550252293_5c66f90584284.png!small)

把我们上边的示例代码拷贝进去，保存与其他编辑器无异，ctrl+s就ok，我习惯保存成c文件，这个大家随意。  
![2.png](https://image.3001.net/images/20190216/1550252741_5c66fac55f68f.png!small)

2.编译运行：

编译运行就很简单了，点击工具栏最上方的运行，接着在下拉菜单中找到编译和运行，点击：

![4.png](https://image.3001.net/images/20190216/1550252945_5c66fb910f2bb.png!small)

这时候会看到文件夹中多了一个exe文件这就是我们要用来调试的程序：

![5.png](https://image.3001.net/images/20190216/1550253033_5c66fbe9006f7.png!small)

3.调试和查看汇编代码

这个是比较重要的一步，因为在编写shellcode的时候会用到，这里只讲用法，如何提取shellcode以后再讲。

首先设置断点，选择设置断点的行，可以再前面行标出单击也可以按F4，当行标处出现红点说明断点设置成功。

![6.png](https://image.3001.net/images/20190216/1550253417_5c66fd697602a.png!small)

然后开启调试模式，我们点击下方选项卡里的调试，接着点击调试按钮。

![7.png](https://image.3001.net/images/20190216/1550253603_5c66fe23d710c.png!small)

接着点击查看CPU窗口：![8.png](https://image.3001.net/images/20190216/1550253846_5c66ff166285e.png!small)

我们就会看到汇编代码界面：

![9.png](https://image.3001.net/images/20190216/1550253907_5c66ff53216a0.png!small)

dev c++几个重要用法已经说完了，还要跟大家说一下如何解决安装使用过程中经常会出现zlib2.dll文件丢失的问题。

解决办法如下：

> 1.下载zlib1.dll:
>
> <http://www.pc6.com/softview/SoftView_81060.html>
>
> 2.解压后放到系统目录中
>
> 32位系统：放到C:\Windows\System32\\(此处为系统目录)
>
> 64位系统：放到C:\Windows\SysWOW64\

为了不使篇幅过长，其余两个软件使用方法我将在下一篇文章中进行讲解。  

***本文原创作者：kaliking，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

