**今天给大家介绍的是一款名叫BlobRunner的安全分析工具，广大研究人员可以在恶意软件的分析过程中使用BlobRunner快速提取和调试恶意软件中的shellcode。**

![83910830198309128.png](https://image.3001.net/images/20181107/1541588807_5be2c747e60a9.png!small)

BlobRunner能够直接在内存中定位目标文件，并跳转到内存地址（可设置偏移量或基地址）。这样一来，研究人员就能够以最简单最快速的方法去对提取出的恶意代码进行调试和分析了。

为了使用BlobRunner，你可以直接从该项目的GitHub主页下载和编译项目源码。

## 代码构建

整个项目代码构建的过程非常简单，大家不必担心…

## 依赖组件

下载并安装Microsoft Visual C++ Build Tools或Visual Studio。

### 构建步骤

1.打开Visual Studio的命令行窗口；

2.切换到BlobRunner所在的目录路径；

3.然后运行下列命令完成代码构建：

    
    
    cl blobrunner.c

### 构建BlobRunner x64

实际上，构建64位版本的方法跟上面的差不多，只不过需要使用对应的64位工具：

1.打开64位版本的Visual Studio命令行窗口；

2.切换到BlobRunner所在的目录路径；

3.然后运行下列命令完成代码构建：

    
    
    cl /Feblobrunner64.exe /Foblobrunner64.out blobrunner.c

## 工具使用

恶意代码调试步骤：

1.在你熟悉的调试器中运行BlobRunner；

2.将需要调试的Shellcode文件以参数的形式传递进去；

3.在代码跳转到Shellcode之前添加一个断点；

4.跳转到Shellcode；

    
    
    BlobRunner.exe shellcode.bin

设置偏移量：

    
    
    BlobRunner.exe shellcode.bin --offset 0x0100

在跳转之前不设置暂停运行，请确保已设置了断点：

    
    
    BlobRunner.exe shellcode.bin –nopause

## 调试x64 Shellcode

x64编译器默认是不支持这个功能的，所以为了调试x64Shellcode，我们需要用加载器创建一个挂起的线程，这样我们就可以在线程恢复运行之前设置断点了。

## 远程调试Shell Bolb（IDAPro）

整个过程基本上跟大家在本地调试Shellcode差不多，不过在远程调试时你需要将Shellcode文件拷贝到远程系统中。如果拷贝路径跟win32_remote.exe的运行路径相同，那么你只需要将文件名以参数的形式传递进去就可以了。否则，你就得在[远程系统](https://www.kitploit.com/search/label/Remote)中指定Shellcode文件的路径了。

### Shellcode样本

大家可以使用[Metasploit](https://www.kitploit.com/search/label/Metasploit)的[msfvenom](https://github.com/rapid7/metasploit-framework/wiki/How-to-use-msfvenom)来快速生成Shellcode样本，下面的代码会创建一个简单的[Windows](https://www.kitploit.com/search/label/Windows)
exec Payload：

    
    
    msfvenom -a x86 --platform windows -p windows/execcmd=calc.exe -o test2.bin

***参考来源：[BlobRunner](https://github.com/OALabs/BlobRunner)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

