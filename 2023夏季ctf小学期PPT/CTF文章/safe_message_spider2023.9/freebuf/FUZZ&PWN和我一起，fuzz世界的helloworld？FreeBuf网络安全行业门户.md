## 0x00 背景

本文记录自己的一次探索。作为一个尚未完全入门的pwn手，在漏洞挖掘比赛的推动下，尝试 **fuzz+pwn** 的模式，进行漏洞挖掘。  
Fuzz，又称 **模糊测试** 。

>
> “模糊测试”是一种自动程序生成大量随机输入以测试软件应用程序的稳健性并尝试查找漏洞的技术。目标是使用意外且有时无效的输入“模糊”应用程序，以检测传统测试技术可能无法发现的错误和潜在安全问题。

>
> 模糊测试是发现软件中意外行为的有效方法，可以帮助识别安全漏洞，例如缓冲区溢出、整数溢出和其他与内存相关的错误。它经常用于安全测试，是一种在软件应用程序中查找安全漏洞的流行技术。

有了fuzz，pwn手会不会就不是只能做ctf的题目了呢？

### AFL++

本文用到的fuzz工具是AFL++，网上有很多安装的博客，我就不赘述啦。请各位师傅安装好之后，我们直奔主题！（ps : 本文还需要pwn环境支持）  
我的linux环境，可做参考：

> Linux version 5.10.16.3-microsoft-standard-WSL2 (oe-user@oe-host)  
> (x86_64-msft-linux-gcc (GCC) 9.3.0, GNU ld (GNU Binutils)  
> 2.34.0.20200220)

## 0x01 代码

请将下列代码保存为`vuln.c`

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <string.h>
    #include <signal.h>
    
    int vuln(char *str)
    {
        int len = strlen(str);
        if(str[0] == 'A' && len == 66)
        {
            raise(SIGSEGV);
            //如果输入的字符串的首字符为A并且长度为66，则异常退出
        }
        else if(str[0] == 'F' && len == 6)
        {
            raise(SIGSEGV);
            //如果输入的字符串的首字符为F并且长度为6，则异常退出
        }
        else
        {
            printf("it is good!\n");
        }
        return 0;
    }
    
    int main(int argc, char *argv[])
    {
        char buf[100]={0};
        gets(buf);//存在栈溢出漏洞
        printf(buf);//存在格式化字符串漏洞
        vuln(buf);
    
        return 0;
    }
    

## 0x02 编译

cd到保存的目录下，使用afl-gcc进行插桩编译。

    
    
    afl-gcc -g -o ./vuln ./vuln. c
    

## 0x03 准备

在目录下运行命令创造输入和输出文件夹。

    
    
    mkdir input output
    

cd到input文件夹内，创建以下四个文件分别为input1.txt、input2.txt、input3.txt、input4.txt。不过也可以自己定，想写什么都可以。因为，这些文件是让
**afl++作为数据输入给程序测试的** ，称为 **测试用例** 。

    
    
    a
    
    
    
    FAFL+++
    
    
    
    aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqa
    
    
    
    %x %x %x
    

最后效果如图：  
![image](https://image.3001.net/images/20230421/1682071308_64425f0c9243eb2a4a691.png!small)

## 0x04 fuzz you!

运行命令进行fuzz。

    
    
    afl-fuzz -m 300 -i input/ -o output/ ./vuln -f
    

命令具有以下参数：

> -m 300：指定目标二进制文件的内存限制为300m（以 MB 为单位）。  
> -i input/：指定包含输入测试用例（也就是刚才我们创建的那些文件）的目录，用作模糊器的初始种子输入。  
> -o output/：指定模糊器将写入其结果的输出目录。  
> ./vuln：指定要进行模糊测试的目标二进制文件的路径。  
> -f：指示 afl-fuzz 以 fork 服务器模式运行目标二进制文件，从而提高性能并减少内存使用。

运行以后会出现如下界面：

![image](https://image.3001.net/images/20230421/1682071513_64425fd930b37c329450c.jpg!small)  
大家看不懂的话，可以看看chat哥的翻译对照一下，不过两张图的数据不太一样，大家稍微注意一下：

![image](https://image.3001.net/images/20230421/1682071689_644260895e925138510dd.png!small)

## 0x05 分析的准备

在fuzz完了之后，我们就会在目录`/output/default/crashes`下看到四个crashes。

![image](https://image.3001.net/images/20230421/1682071852_6442612c89af2cd463363.png!small)  
我们会用到xxd命令，所以运行命令进行安装：

    
    
    sudo apt-get install xxd
    

我们先xxd看一个试试：  
![image](https://image.3001.net/images/20230421/1682071932_6442617cea57bae917935.png!small)  
在此，我们可以看到它的内容。我在这里走了很多弯路，想用xxd来提取数据然后输入调试，后来发现了一个更方便的方法，直接
**用python进行读取转为十六进制输入** ， **用pwn的方式进行调试** ！

#### 把你的pwntools与fuzz结合！

我们用mv xxxxx id1命令，将那些很长的名字改成id1、id2等等，方便后面操作。  
![image](https://image.3001.net/images/20230421/1682075676_6442701cd5602964555d0.png!small)  
修改后的效果如下。  
![image](https://image.3001.net/images/20230421/1682075277_64426e8d430f33c61c5c0.png!small)

接下来是本文的重磅代码，也是我最得意的部分！在`get_crash()`的括号内输入crash的路径，运行该代码即可开始调试！

    
    
    from pwn import *
    import binascii
    
    p = process('./vuln')
    
    def get_crash(file):
        with open(file, 'rb') as f:
            binary_data = f.read()
            hex_data = binascii.hexlify(binary_data)
            bytes_str = binascii.unhexlify(hex_data)
            print(bytes_str)
            return bytes_str
    
    payload = get_crash('/mnt/c/sevn/fuzz/test/output/default/crashes/id0')
    gdb.attach(p)
    pause()
    p.sendline(payload)
    
    p.interactive()
    

## 0x06 调试你的crash！

我们在这里简单调试一两个crash作为示范。

### id2

运行python代码：

    
    
    from pwn import *
    import binascii
    
    p = process('./vuln')
    
    def get_crash(file):
        with open(file, 'rb') as f:
            binary_data = f.read()
            hex_data = binascii.hexlify(binary_data)
            bytes_str = binascii.unhexlify(hex_data)
            print(bytes_str)
            return bytes_str
    #在get_crash中写上你的crash文件所在
    payload = get_crash('/mnt/c/sevn/fuzz/test/output/default/crashes/id2')
    gdb.attach(p)
    pause()
    p.sendline(payload)
    
    p.interactive()
    

运行出来后输入c，可以看到调试id2的效果。我们可以在程序的最后输入`bt`，然后看到调试器显示了当前程序的回溯（backtrace），也称为调用栈（call
stack），它包含了函数调用链的信息。这是一个非常有用的信息，因为它告诉我们 **在程序崩溃时正在执行哪个函数，并且在该函数内部执行的函数调用** 。  
在这个例子中，pwndbg给出了一个完整的调用栈，以及在程序崩溃时正在执行的函数。具体来说，回溯显示了以下信息：

> #0：指出崩溃时正在执行的函数是printf_positional，它是一个库函数，可以在 stdio-common/vfprintf-process-> arg.c 中找到它的实现代码。  
> #1: 指出在printf_positional内部调用的函数是__vfprintf_internal，也是一个库函数，可以在 stdio-> common/vfprintf-internal.c 中找到它的实现代码。  
> #2: 指出在__vfprintf_internal内部调用的函数是__printf，也是一个库函数，可以在 stdio-common/printf.c
> 中找到它的实现代码。  
> #3: 指出在main函数中调用的函数是__printf，这就是我们要查找的漏洞。

![image](https://image.3001.net/images/20230421/1682075875_644270e39a9f5ab27780e.png!small)

通过调用栈信息，我们可以知道崩溃时正在执行的函数是 __printf，因此我们需要查看在main函数中调用
__printf时的参数。我们还可以在main函数中设置一个断点，然后通过调试器单步执行程序，以查看在崩溃发生之前程序的状态和行为。  
有printf可以基本推断，这是一个 **格式化字符串漏洞** 。

### id3

运行python代码：

    
    
    from pwn import *
    import binascii
    
    p = process('./vuln')
    
    def get_crash(file):
        with open(file, 'rb') as f:
            binary_data = f.read()
            hex_data = binascii.hexlify(binary_data)
            bytes_str = binascii.unhexlify(hex_data)
            print(bytes_str)
            return bytes_str
    #在get_crash中写上你的crash文件所在
    payload = get_crash('/mnt/c/sevn/fuzz/test/output/default/crashes/id3')
    gdb.attach(p)
    pause()
    p.sendline(payload)
    
    p.interactive()
    

我们单步调试观察到栈，由汇编代码发现，在pop rbx后就会进行ret，则必然会返回到我们的输入数据：  
![image](https://image.3001.net/images/20230421/1682076538_6442737ad5356b9c126d0.png!small)  
我们可以看到返回到了一个错误地址，这就是 **栈溢出漏洞** 的体现了。

![image](https://image.3001.net/images/20230421/1682076375_644272d720804d3d1e4a4.png!small)

## 0x07 尾声

这篇文章的分享就到这里，有什么问题和不对的地方欢迎指出和一起讨论！谢谢~这是第一次fuzz，希望不是最后一次（划掉）。

