![](https://image.3001.net/images/20230810/1691652418_64d491427ec2528dffab6.jpeg!small)

## 关于Bropper

Bropper是一款功能强大的自动化Blind ROP利用工具，所谓Blind
ROP，简称BROP，指的是没有对应应用程序的源代码或者二进制文件下，对程序进行攻击，劫持程序的执行流。

大多数服务器（如nginx、Apache、MySQL）都会与客户端进行通信。这意味着即使有ASLR和PIE，Canary和地址也会保持不变。因此，我们就可以使用暴力破解之类的方法来获取泄漏的敏感信息，或利用某些有效漏洞。

## 漏洞利用执行流

> 1、找到缓冲区溢出偏移量；
>
> 2、找到Canary；
>
> 3、找到保存的寄存器（RBP/RIP）；
>
> 4、找到stop gadgets；
>
> 5、找到brop gadgets；
>
> 6、找到一个写入函数（write/dprintf/puts/...）；
>
> 7、泄漏代码；

## 工具下载

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python
3环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Hakumarachi/Bropper.git

然后切换到项目目录中，使用pip 3命令和项目提供的requirements.txt文件安装该工具所需的其他依赖组件：

    
    
    cd Bropper/
    
    pip3 install -r requirements.txt

## 工具使用

工具基础使用：

    
    
    python3 -m pip install -r requirements.txt
    
    python3 bropper.py -t 127.0.0.1 -p 1337 --wait "Password :" --expected Bad --expected-stop Welcome -o dump

工具使用帮助：

    
    
    $ python3 bropper.py -h
    
    usage: bropper.py [-h] -t TARGET -p PORT --expected-stop EXPECTED_STOP --expected EXPECTED --wait WAIT -o OUTPUT [--offset OFFSET] [--canary CANARY] [--no-canary] [--rbp RBP] [--rip RIP] [--stop STOP]
    
                      [--brop BROP] [--plt PLT] [--strcmp STRCMP] [--elf ELF]
    
     
    
    Description message
    
     
    
    options:
    
      -h, --help             显示工具帮助信息和退出
    
      -t TARGET, --target TARGET
    
                            设置目标URL
    
      -p PORT, --port PORT  设置目标端口target port
    
      --expected-stop EXPECTED_STOP
    
                            设置期望的stop gadget响应
    
      --expected EXPECTED   期望的正常响应
    
      --wait WAIT             发送Payload之前需要等待的时间
    
      -o OUTPUT, --output OUTPUT
    
                             转储远程代码时要写入的文件
    
      --offset OFFSET        设置一个偏移量值
    
      --canary CANARY       设置一个Canary值
    
      --no-canary            如果没有Canary栈保护，则可以使用该参数选项
    
      --rbp RBP             设置RBP地址
    
      --rip RIP             设置RIP地址
    
      --stop STOP           设置stop gadget地址
    
      --brop BROP           设置brop gadget地址
    
      --plt PLT               设置PLT地址
    
      --strcmp STRCMP       设置strcmp入口值
    
      --elf ELF              设置ELF地址

## 工具使用演示

Bropper代码库提供了三个自定义漏洞样例，我们可以直接运行或构建Dockerfile：

![](https://image.3001.net/images/20230810/1691652503_64d49197cc33ae576ae3f.png!small)

接下来，Bropper将会直接转储二进制代码：

![](https://image.3001.net/images/20230810/1691652510_64d4919ed18f688d87067.png!small)

最后，我们就可以使用ROPgadget从转储的二进制代码中提取出所有的ROP gadget了：

    
    
    $ ROPgadget --binary dump
    
    Gadgets information
    
    ============================================================
    
    0x0000000000001177 : adc al, 0 ; add byte ptr [rax], al ; jmp 0x1020
    
    0x0000000000001157 : adc al, byte ptr [rax] ; add byte ptr [rax], al ; jmp 0x1020
    
    0x0000000000001137 : adc byte ptr [rax], al ; add byte ptr [rax], al ; jmp 0x1020
    
    ...
    
    ...
    
    ...
    
    0x0000000000001192 : xor ch, byte ptr [rdi] ; add byte ptr [rax], al ; push 0x16 ; jmp 0x1020
    
    0x000000000000182e : xor eax, 0x891 ; mov rdi, rax ; call rcx
    
    0x0000000000001861 : xor eax, 0xffffff22 ; mov rdi, rax ; call rcx
    
     
    
    Unique gadgets found: 235

## 项目地址

 **Bropper** ：【[ _GitHub传送门_](https://github.com/Hakumarachi/Bropper)】

## 参考资料

> [ _https://www.scs.stanford.edu/brop/bittau-> brop.pdf_](https://www.scs.stanford.edu/brop/bittau-brop.pdf)
>
> [ _https://www.scs.stanford.edu/brop/bittau-brop-> slides.pdf_](https://www.scs.stanford.edu/brop/bittau-brop-slides.pdf)

