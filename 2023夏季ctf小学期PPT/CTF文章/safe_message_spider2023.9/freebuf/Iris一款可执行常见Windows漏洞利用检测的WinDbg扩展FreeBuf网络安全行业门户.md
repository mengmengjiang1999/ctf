**Iris是一款WinDbg扩展，它可以针对常见的Windows进程缓解进行安全检测，并给研究人员提供详细的检测数据。**

![1.png](https://image.3001.net/images/20190914/1568475834_5d7d0aba7d7e5.png!small)![2.png](https://image.3001.net/images/20190914/1568475834_5d7d0aba7f2ba.png!small)

我们可以从上面给出的截图中看到检测的详细信息，其中包括：

### 针对当前进程：

> -DEP策略
>
> -ASLR策略
>
> -ACG策略
>
> -系统调用策略（禁用Win32k系统调用）
>
> -控制流守护策略
>
> -图像加载签名策略（微软签名、存储签名）
>
> -进程字体策略
>
> -进程镜像加载策略
>
> -缓解选项（SEHOP）

### 针对已加载的模块：

> -DynamicBase
>
> -ASLR
>
> -DEP
>
> -SEH
>
> -SafeSEH
>
> -CFG
>
> -RFG
>
> -GS
>
> -AppContainer

如果你不知道上面这些关键词的意思，那么你需要自己上网搜索了。

## 工具安装

输入下列命令将项目代码拷贝到本地：

    
    
    git clone https://github.com/fdiskyou/iris.git

接下来，将项目目录中的x86\iris.dll或x64\iris.dll文件拷贝到WinDbg的winext目录中（针对系统架构选择对应的x86或x64）。

### WinDbg 10.0.xxxxx

除非你将调试工具安装到了非标准路径，否则你可以直接根据下面路径找到winext目录：

    
    
    C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\winext

如果你使用的是32位系统，那么路径则为：

    
    
    C:\Program Files (x86)\Windows Kits\10\Debuggers\x86\winext

## 加载扩展

完成了上述操作之后，我们就可以使用“.load iris”命令来加载扩展，并运行“!iris.help”命令来查看所有可用的命令了：

    
    
    0:014> .load iris
    
    [+] Iris WinDbg Extension Loaded
    
    0:014> !iris.help
    
     
    
    IRIS WinDbg Extension (rui@deniable.org). Available commands:
    
    	help                  = Shows this help
    
    	modules               = Display process mitigations for all loaded modules.
    
    	mitigations           = Display current process mitigation policy.

### 工具运行

正如文章开头的工具运行截图所示，我们可以直接运行“!iris.modules”（“!modules”）或“!iris.mitigations”（!mitigations）命令来使用Iris了。

## 项目地址

Iris：【[ _GitHub传送门_](https://github.com/fdiskyou/iris)】

 ***参考来源：[
_fdiskyou_](https://github.com/fdiskyou/iris)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

