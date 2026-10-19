![](https://image.3001.net/images/20191009/1570596022_5d9d64b65d865.png!small)

## B2R2

B2R2是一套针对二进制代码分析的实用算法、函数以及工具集，B2R2采用纯F#（.NET）开发，B2R2原名为B2-R2，其命名引用的是[
_R2-D2_](https://en.%2A%2A%2A%2A%2A%2A%2A%2A%2A.org/wiki/R2-D2)，因为.NET不允许在标识符或命名空间中使用字符“-”，因此我们将该项目名米给B2R2。其中，B代表Binary，B2即二进制代码，R指的是逆向分析Reverse。

### 工具特性

> 1、B2R2是一款采用F#开发的“分析友好型”工具，它可以为研究人员开发彻骨分析工具提供语法上的便利，例如模式匹配和代数数据类型等等。
>
>
> 2、B2R2运行速度非常快，它带有一个快速高效的前端引擎，可用于对二进制代码进行分析，该引擎纯粹以实现功能性为目的进行开发，因此它自然支持二进制代码反编译，提升和并行优化。
>
> 3、B2R2简单易用，并且没有绝对的依赖组件，因为它本身就是一个完全托管的库，我们只需要安装[
> _.NET核心SDK_](https://dotnet.microsoft.com/download)即可。
>
> 4、B2R2与操作系统无关，它只需要.NET核心的支持，即可在Linux、macOS和Windows等操作系统平台上运行。
>
> 5、B2R2可与其他组件协同工作，以为它没有与任何其他语言绑定，我们可以在任何支持[
> _命令行_](https://en.%2A%2A%2A%2A%2A%2A%2A%2A%2A.org/wiki/List_of_CLI_languages)的其他语言环境下使用B2R2。

### 依赖组件

B2R2只依赖于一小部分的外部.NET库，这也符合我们设计的尽量实现最少依赖库的标准。下面给出的是B2R2所需的依赖库列表：

> 1、[
> _System.Reflection.Metadata_](https://www.nuget.org/packages/System.Reflection.Metadata/)
>
> 2、[
> _Microsoft.FSharpLu.Json_](https://www.nuget.org/packages/Microsoft.FSharpLu.Json/)
>
> 3、[ _FParsec_](https://www.nuget.org/packages/FParsec)

### API文档

我们当前使用了docfx来生成B2R2的API文档：【[ _点我获取_](https://b2r2.org/APIDoc/)】。

## B2R2下载

研究人员可使用Git命令直接将项目代码从GitHub库克隆至本地：

    
    
    git clone https://github.com/B2R2-org/B2R2.git 

## 工具使用样例

接下来，我们演示一下如何使用B2R2的API接口。

1、首先，我们需要生成一个名为“DIRNAME”的空目录：

    
    
    mkdir DIRNAME

2、然后，使用dotnet命令在命令行工具中常见一个空的终端项目：

    
    
    $ dotnet new console -lang F#

3、将B2R2.FrontEnd包添加进项目中：

    
    
    $ dotnet add package B2R2.FrontEnd

4、使用我们熟悉的编辑器修改Program.fs文件：

    
    
    open B2R2
    
    open B2R2.FrontEnd
    
    [<EntryPoint>]
    
    let main argv =
    
      let isa = ISA.OfString "amd64"
    
      let bytes = [| 0x65uy; 0xffuy; 0x15uy; 0x10uy; 0x00uy; 0x00uy; 0x00uy |]
    
      let handler = BinHandler.Init (isa, bytes)
    
      let ins = BinHandler.ParseInstr handler 0UL
    
      ins.Translate handler.TranslationContext |> printfn "%A"
    
      0

5、最后，使用下列命令运行B2R2：

    
    
    dotnet run

## 代码构建

构建B2R2项目其实非常简单，我们只需要安装.NET核心SDK 3.0以及上述依赖组件即可。

1、以发布模式构建B2R2，可直接在项目根目录路径下运行下列命令：

    
    
    make release

或

    
    
    dotnet build -c Release

2、以调试模式构建B2R2，可直接在项目根目录路径下运行下列命令：

    
    
    make

或

    
    
    dotnet build

## 项目引用

如果你想要在自己的研究项目中使用B2R2的话，请在[
_项目_](https://softsec.kaist.ac.kr/~sangkilc/papers/jung-bar19.pdf)中添加下列信息：

@INPROCEEDINGS{jung:bar:2019,

    
    
    author = {Minkyu Jung and Soomin Kim and HyungSeok Han and Jaeseung Choi and Sang Kil Cha},
    
    title = {{B2R2}: Building an Efficient Front-End for Binary Analysis},
    
    booktitle = {Proceedings of the NDSS Workshop on Binary Analysis Research},
    
    year = 2019
    
    }

## 项目地址

> B2R2：【[ _GitHub传送门_](https://github.com/B2R2-org/B2R2)】

## 参考资料

> 1、[ _http://fsharp.org/_](http://fsharp.org/)
>
> 2、[ _https://b2r2.org/APIDoc/_](https://b2r2.org/APIDoc/)
>
> 3、[
> _https://github.com/B2R2-org/B2R2/blob/master/CONTRIBUTING.md_](https://github.com/B2R2-org/B2R2/blob/master/CONTRIBUTING.md)
>
> 4、[ _http://csrc.kaist.ac.kr/_](http://csrc.kaist.ac.kr/)

 *** 参考来源：[
_tarnish_](https://github.com/mandatoryprogrammer/tarnish)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

