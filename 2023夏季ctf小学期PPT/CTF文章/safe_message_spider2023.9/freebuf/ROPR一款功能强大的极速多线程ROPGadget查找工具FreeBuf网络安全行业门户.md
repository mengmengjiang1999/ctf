![](https://image.3001.net/images/20220913/1663036781_631fed6db0b6c07fe7f7d.jpg!small)  

## 关于ROPR

ROPR是一款速度极快且功能强大的ROPGadget查找工具，该工具支持多线程运行，可以帮助广大研究人员快速寻找和定位目标ROPGadget。

ROP（Return Oriented
Programming），即返回导向编程，而ROPGadget是一些包含汇编指令的代码段，通常以ret指令结尾，这些指令已经作为可执行代码存在于每个源码文件或代码库中，而这些小工具可用于二进制攻击，并破坏易受攻击的可执行文件。

当许多ROPGadget的地址写入缓冲区时，就形成了ROP链。如果攻击者可以将堆栈指针移动到此ROP链中，则控制权将会完全转移给攻击者。

大多数可执行文件包含足够的小工具来编写ROP链一旦我们知道了地址，就可以使用包含在同一地址空间（如libc）中的动态库。

而使用ROPGadget的好处在于，无需在任何地方编写新的可执行代码，攻击者可以仅使用程序中已经存在的代码来实现其目标。

## 工具要求

工具需要使用cargo（Rust构建系统）来构建和使用ROPR。

## 工具下载

### 源码安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并构建项目代码：

    
    
    git clone https://github.com/Ben-Lichtman/ropr
    
    cd ropr
    
    cargo build --release

此时，应用程序将会安装到target/release/ropr路径下。

或者，下列命令同样可以安装ROPR：

    
    
    git clone https://github.com/Ben-Lichtman/ropr
    
    cd ropr
    
    cargo install --path .

此时，应用程序将会安装到~/.cargo/bin路径下。

### Cargo安装

    
    
    cargo install ropr

此时，应用程序将会安装到~/.cargo/bin路径下。

## 工具使用

    
    
    USAGE:
    
        ropr [OPTIONS] <BINARY>
    
     
    
    ARGS:
    
        <BINARY>    待检查的文件路径
    
     
    
    OPTIONS:
    
        -b, --base-pivot               用于更改基指针的ROPGadget过滤器
    
        -c, --colour <COLOUR>       开启输出颜色高亮和明文显示
    
        -h, --help                     打印工具帮助信息
    
        -j, --nojop                    移除"JOP Gadgets"
    
        -m, --max-instr <MAX_INSTR>    一个小工具中的最大指令数量[默认: 6]
    
        -n, --noisy                    包含潜在的低质量小工具
    
        -p, --stack-pivot               过滤堆栈指针后的小工具
    
        -r, --norop                    移除普通的"ROP Gadgets"
    
        -R, --regex <REGEX>          执行正则表达式搜索
    
            --range <RANGE>         搜索地址范围（十六进制），例如 `0x1234-0x4567`
    
            --raw <RAW>             将输入文件当作代码段
    
        -s, --nosys                    移除系统调用和其他中断
    
        -V, --version                  打印工具版本信息

## 工具使用演示

比如说，如果我们想要使用其他注册表键值来填充rax，我们就可以使用正则表达式“^mov eax, ...;”来选择过滤器：

    
    
    ❯ ropr /usr/lib/libc.so.6 -R "^mov eax, ...;" > /dev/null
    
     
    
    ==> Found 197 gadgets in 0.118 seconds

现在，我们就可以在命令行添加某些过滤器来获取高质量的处理结果了：

    
    
    ❯ ropr /usr/lib/libc.so.6 -m 2 -j -s -R "^mov eax, ...;"
    
    0x000353e7: mov eax, eax; ret;
    
    0x000788c8: mov eax, ecx; ret;
    
    0x00052252: mov eax, edi; ret;
    
    0x0003ae43: mov eax, edx; ret;
    
    0x000353e6: mov eax, r8d; ret;
    
    0x000788c7: mov eax, r9d; ret;
    
     
    
    ==> Found 6 gadgets in 0.046 seconds

接下来，我们可以查看到mov小工具的地址为0x00052252。

## 项目地址

 **ROPR** ：【[ _GitHub传送门_](https://github.com/Ben-Lichtman/ropr)】

