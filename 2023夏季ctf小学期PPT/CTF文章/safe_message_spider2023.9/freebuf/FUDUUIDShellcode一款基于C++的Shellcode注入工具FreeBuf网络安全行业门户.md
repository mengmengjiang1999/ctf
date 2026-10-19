## 关于FUD-UUID-Shellcode

FUD-UUID-Shellcode是一款功能强大的Shellcode注入工具，该工具基于C++语言开发，并使用了异或XOR加密技术UUID字符串混淆来尝试绕过Windows
Defender。广大研究人员可以使用该工具测试目标系统的安全性，或研究Windows Defender相关的安全问题。

## 工作机制

### Shellcode生成

首先，该工具会以二进制源码的形式生成一个Payload（使用CobaltStrike或msfvenom），以msfvenom举例，我们可以通过下列方式生成一个Payload：

    
    
    msfvenom -p windows/messagebox  -f raw -o shellcode.bin

然后工具会使用提供的Python 3脚本（bin_to_uuid.py）将Shellcode转换为UUID字符串格式：

    
    
    ./bin_to_uuid.py -p shellcode.bin > uuid.txt

接下来，工具会使用另一个Python 3脚本（xor_encryptor.py）对uuid.txt中的UUID字符串进行异或XOR加密：

    
    
    ./xor_encryptor.py uuid.txt > xor_crypted_out.txt

最后，拷贝输出文件（xor_crypted_out.txt）中的C-style数组到C++文件中（以unsigned char形式，比如说unsigned
char payload[]{your_output_from_xor_crypted_out.txt}）。

### Shellcode注入执行

该工具实现的Shellcode注入技术由以下几个步骤序列组成：

> 1、使用VirtualAlloc给Payload的执行和持久化分配虚拟内存；
>
> 2、使用xor键值对Payload进行异或解密；
>
>
> 3、使用UuidFromStringA将UUID字符串恢复为代码形式，并将其存储在之前（第一步）分配的内存中。这样可以避免使用类似WriteProcessMemory或memcpy这样的可疑API；
>
> 4、使用EnumChildWindows执行之前（第一步）加载在内存中的Payload；

## 工具注意事项

> 1、我们可以自行修改异或加密使用的密钥，直接修改./xor_encryptor.py中的KEY变量即可；
>
> 2、可以修改修改./xor_encryptor.py中的“excutable filename”值来修改默认的文件名；
>
> 3、在编译项目代码时，也可以使用mingw；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Bl4ckM1rror/FUD-UUID-Shellcode.git

### 工具编译

打开终端窗口，然后切换到项目目录中，并运行make命令编译项目代码即可：

    
    
    make

## AV扫描结果

### 概念验证PoC

![](https://image.3001.net/images/20221017/1665940923_634c3dbb1dd399532f36a.png!small)

### 代码静态分析结果

![](https://image.3001.net/images/20221017/1665940932_634c3dc4c1296deab9ab0.png!small)

### 反病毒产品扫描结果

工具代码在[ _antiscan_
_.me_](https://antiscan.me/scan/new/result?id=3IYj6CtMq6h8)上的扫描结果如下（2022年01月08日）：

![](https://image.3001.net/images/20221017/1665940946_634c3dd290df25e92a3d4.png!small)

## 项目地址

 **FUD-UUID-Shellcode** ：【[ _GitHub传送门_](https://github.com/Bl4ckM1rror/FUD-UUID-Shellcode)】

## 参考资料

> [ _https://research.nccgroup.com/2021/01/23/rift-analysing-a-lazarus-> shellcode-execution-method/_](https://research.nccgroup.com/2021/01/23/rift-> analysing-a-lazarus-shellcode-execution-method/)
>
> [
> _https://antiscan.me/scan/new/result?id=3IYj6CtMq6h8﻿_](https://antiscan.me/scan/new/result?id=3IYj6CtMq6h8)

