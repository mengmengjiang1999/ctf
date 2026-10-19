**今天给大家介绍的是一款名叫Reko的开源反编译工具，该工具采用C#开发，广大研究人员可利用Reko来对机器码进行反编译处理。**

 **Reko不仅包含核心反编译引擎和后端代码分析模块，而且还提供了用户友好的操作界面。目前，该工具提供了Windows
GUI和ASP.NET后端。反编译引擎需要从前端获取用户的输入，可接受的输入为单独的可执行文件或反编译项目文件。Reko项目文件中还包含了代码文件的额外信息，来为研究人员的反编译操作或格式化输出提供帮助。在整个过程中，负责分析输入代码的主要是反编译引擎。**

![11.png](https://image.3001.net/images/20190328/1553770542_5c9ca82e2e68b.png!small)![22.png](https://image.3001.net/images/20190328/1553770542_5c9ca82e2f6e9.png!small)

Reko的目标就是帮助用户在最小化操作交互的情况下，帮助用户完成对多种处理器架构和可执行文件格式的反编译处理。需要注意的是，很多软件许可证会禁止他人对该软件的机器码进行反编译或逆向分析，所以希望大家不要将本工具用于恶意目的。

## 项目地址

Reko：【[GitHub传送门](https://github.com/uxmal/reko)】

## 工具下载和安装

运行下列命令下载Reko：

    
    
    $ git clone git://github.com/uxmal/reko.git

### Windows用户

在Windows平台上，首先需要安装下列依赖组件：

NETFramework 4.7.2：【[下载地址](https://www.microsoft.com/net/download/dotnet-framework-runtime)】

下载好MSI文件之后，直接运行安装程序即可。

### 非Windows用户

如果你使用的不是Windows系统，那么你首先得安装下列依赖组件：

Monov5.14.0：【[传送门](https://download.mono-project.com/archive/5.14.0/)】

安装好mono之后，你就可以直接从整合构建服务器下载源代码，或直接构建Reko源码来使用工具了。

工具下载好并完成环境配置之后，你就可以使用一款IDE或命令行来构建Reko-decompiler.sln文件了。如果你习惯使用IDE，推荐你Visual
Studio 2017或MonoDevelop v5.10及以上版本。如果你习惯使用命令行，你可以使用下列命令：

    
    
    msbuild Reko-decompiler.sln

## 工具使用

在Windows上，安装完成后会在开始菜单里创建一个“Reko Decompiler”快捷方式，你可以直接点击图标启动Reko客户端。

在非Windows系统上，你需要使用下列命令运行WindowsDecompiler.exe：

    
    
    mono WindowsDecompiler.exe

### 运行命令行客户端

在Windows上，假设你已经把Reko的安装目录写到了PATH环境变量里，那你就可以直接在命令行中输入下列命令来使用工具了：

    
    
    decompile some_binary_file.exe

在非Windows平台上，假设你已经把Reko的安装目录写到了PATH环境变量里，那你就可以直接在命令行中输入下列命令来使用工具了：

    
    
    mono decompile some_binary_file.exe

## 使用Reko进行逆向分析

如果你对编程比较熟的话，你可以直接访问Reko对象模型。比如说，你想输出程序中已知操作进程的名称和地址的话，你可以这样写：

    
    
    using Reko;
    
    using Reko.Core;
    
     
    
    class DumpProcedures {
    
        public static int Main(string [] args) {
    
            var dec = DecompilerDriver.Create();
    
            if (!dec.Load("myfile.exe"))
    
                return -1;
    
            dec.ScanPrograms();
    
            foreach (var program indec.Project.Programs) {
    
                foreach (var entry in program.Procedures){
    
                    Console.Write("Address{0}, procedure name {1}", entry.Key, entry.Value);
    
                }
    
            }
    
        }
    
    }

## 参考资料

> 1、
> SourceForge下载点：【[传送门](https://sourceforge.net/projects/decompiler/files/)】
>
> 2、
> 用户手册从：【[传送门](https://github.com/uxmal/reko/blob/master/doc/guide/reko.md)】
>
> 3、 Reko
> API文档：【[传送门](https://github.com/uxmal/reko/blob/master/doc/guide/api.md)】
>
> 4、
> 命令行操作手册：【[传送门](https://github.com/uxmal/reko/blob/master/doc/guide/cli.md)】

***参考来源：[uxmal](https://github.com/uxmal/reko)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

