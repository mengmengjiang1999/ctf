![](https://image.3001.net/images/20221120/1668944651_637a130b130061fdf25c0.png!small)

## 关于Perfetch Hash Cracker

Perfetch Hash Cracker是一款基于Rust开发的强大暴力破解工具，该工具可以帮助广大研究人员通过爆破的形式破解prefetch哈希。

在针对Windows操作系统的信息安全取证活动中，我们可能会找到一些已删除的prefetch文件，并查看到文件名称。虽然这些文件的内容可能无法恢复，但文件名本身通常就足够允许我们找到创建prefetch文件的可执行文件完整路径。

## 工具运行机制

提供的Bodyfile主要用于获取目标卷宗上每个文件夹的路径，该工具会将提供的可执行文件名称附加到这些路径的结尾处，以创建可执行文件的可能完整路径列表。然后使用提供的哈希函数对每个可能的完整路径进行哈希处理。如果检测到有一个可能的完整路径，其结果与提供的哈希匹配，则输出该路径。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/harelsegev/prefetch-hash-cracker.git

## 工具使用

在使用该工具时，我们必须提供下列内容：

> 1、可执行文件名称：包括扩展名，这部分内容将会嵌入到prefetch文件名称中；
>
> 2、Prefetch哈希：prefetch文件名结尾的最后8个十六进制数字值，在.pf后缀的前面；
>
> 3、Hash函数；
>
> 4、Bodyfile；
>
> 5、挂载点；

### Hash函数

下面给出的是三个已知的prefetch哈希函数：

> SCCA XP：主要用于Windows XP操作系统中；
>
> SCCA Vista：主要用于Windows Vista和Windows 10操作系统中；
>
> SCCA 2008：主要用于Windows 7、Windows 8和Windows 8.1操作系统中；

### Bodyfile

可执行文件执行所在卷宗的Bodyfile。

Bodyfile格式并不受到严格的限制，因此可能某些格式变体并不一定支持，但使用fls和MFTECmd创建的Bodyfile应该是可以正常工作的。

### 挂载点

Bodyfile的挂载点如下所示：

    
    
    0|C:/Users/Peter/Desktop ($FILE_NAME)|62694-48-2|d/d-wx-wx-wx|...

## 29个字符的限制

如果可执行文件的名称超过了29个字符（包括后缀名在内），它将会在frefetch文件名中被截断。比如说，执行下列文件：

    
    
    This is a very long file nameSo this part will be truncated.exe

在Windows 10设备上的C:\Temp目录中运行该工具，则会创建下列prefetch文件：

    
    
    THIS IS A VERY LONG FILE NAME-D0B882CC.pf

此时，就无法从prefetch文件名中派生出可执行文件名，因此无法将其提供给工具。

## 工具运行截图

![](https://image.3001.net/images/20221120/1668944641_637a13011f438e0bf8cb7.jpeg!small)

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/harelsegev/prefetch-hash-cracker/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Perfetch Hash Cracker** ：【[
_GitHubc传送门_](https://github.com/harelsegev/prefetch-hash-cracker)】

## 参考资料

> [ _https://github.com/harelsegev/prefetch-hash-cracker#The-29-character-> limit﻿_](https://github.com/harelsegev/prefetch-hash-> cracker#The-29-character-limit)

