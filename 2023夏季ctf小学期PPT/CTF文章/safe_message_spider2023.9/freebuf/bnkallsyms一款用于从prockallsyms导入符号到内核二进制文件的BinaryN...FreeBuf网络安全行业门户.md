**今天给大家介绍一款名叫kallsyms的工具，它其实是一个Binary
Ninja插件，它可以从/proc/kallsyms导入符号到内核二进制代码中。**

## 工具介绍

bn-kallsyms允许用户直接打开Binary Ninjia中包含内核符号的文件，并向其中导入符号信息等等。

加载内核符号之前：

![1.png](https://image.3001.net/images/20180703/15306163638132.png!small)

加载内核符号之后：

![2.png](https://image.3001.net/images/20180703/15306163674186.png!small)

## 工具要求

这款插件要求的最低版本Binary Ninjia如下：

    
    
    release- 1.1.1142
    dev -1.1.1228-dev  
    

## 工具使用

### 生成kallsyms文件

运行下列命令即可生成kallsyms文件

    
    
    sudo sh -c "echo 0  >/proc/sys/kernel/kptr_restrict" && sudo cat /proc/kallsyms >kallsyms.txt

### 加载kallsyms

使用该工具时，你首先要从boot镜像中提取出压缩的内核镜像，可使用binwalk实现：

    
    
    $binwalk -e vmlinuz-4.13.0-43-generic

该命令会创建一个包含已解压内核镜像的子目录：

    
    
    $file ~/_vmlinuz-4.13.0-43-generic.extracted/47B4 
    /home/joe/_vmlinuz-4.13.0-43-generic.extracted/47B4:ELF
     64-bit LSB executable, x86-64, version 1 (SYSV), statically 
    linked,BuildID[sha1]=3e0dc1c8b93e2f3f522a596cfc4b482065469041, stripped  
    

将内核ELF文件加载进Binary Ninja，然后点击Tools->"kallsyms: Apply kernel
symbols"，接下来你需要选择/proc/kallsyms输出文件。选择之后，点击“Open”，插件将对kallsyms文件进行解析，并创建相关函数，然后将符号名导入进数据库中。

## 许可证

本项目遵循[MIT](https://github.com/zznop/bn-kallsyms/blob/master/LICENSE)许可证协议。

 *** 参考来源：[bn-kallsyms](https://github.com/zznop/bn-kallsyms)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

