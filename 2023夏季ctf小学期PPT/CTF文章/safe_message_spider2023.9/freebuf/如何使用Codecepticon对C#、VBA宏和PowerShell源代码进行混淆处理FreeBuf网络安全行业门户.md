![](https://image.3001.net/images/20221222/1671712405_63a44e9513870f4d87fcb.png!small)

## 关于Codecepticon

Codecepticon是一款功能强大的代码混淆处理工具，该工具专为红队和紫队渗透测试安全活动而开发，在该工具的帮助下，广大研究人员可以轻松对C#、VBA5/VBA6（宏）和PowerShell源代码进行混淆处理。Codecepticon与其他代码混淆处理工具的区别在于，该工具主要针对的是源代码，而不是编译后的可执行文件，并且能够绕过AV或EDR产品的检测。

除了代码混淆功能之外，Codecepticon还允许我们重写代码，也提供了相关的命令行功能选项。

## 工具要求

### Visual Studio Pro/Community 2022

![](https://image.3001.net/images/20221222/1671712421_63a44ea571978f2d20fc9.png!small)

### Roslyn编译器

![](https://image.3001.net/images/20221222/1671712428_63a44eac3f28905eac2e0.png!small)

### 打开和编译

打开Codecepticon，等待所有的NuGet包下载完成后，就可以构建工具解决方案了。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Accenture/Codecepticon.git

## 工具使用

该工具支持高度自定义配置，并且Codecepticon提供了两种使用方法，要么将所有参数放在命令行中。我们可以使用CommandLineGenerator.html快速生成工具命令：

![](https://image.3001.net/images/20221222/1671712442_63a44eba8d0713f04a120.png!small)

命令行生成器的输出格式为命令行输出或XML，具体可以自行选择，终端命令可以通过下列方式执行：

    
    
    Codecepticon.exe --action obfuscate --module csharp --verbose ...etc

如果使用了XML配置文件，则命令如下：

    
    
    Codecepticon.exe --config C:\Your\Path\To\The\File.xml

### C#

运行工具后，直接选择对应的解决方案，即可对C#项目进行混淆处理。在尝试对目标项目运行Codecepticon之前，请确保该项目可以被独立编译，并做好备份。

### VBA/VBA6

VBA混淆针对的是宏文件源代码本身，而非Microsoft
Office文档。这也就意味着，我们无法向Codecepticon传递一个doc(x)或xls(x)文件，因此需要传递模块本身源代码。（按Alt+F11或直接将源码拷贝进去）

### PowerShell

由于由于PowerShell脚本的复杂性，以及它在编写脚本方面提供的自由度，要覆盖所有边缘情况并确保混淆的结果完全正常运行是一项挑战。虽然Codecepcon可以很好地处理简单的脚本/函数，但在PowerView等复杂脚本/功能上运行它是行不通的，不过开发人员目前正在解决这个问题。

### 命令行参数（混淆）

在对一个应用程序或脚本进行混淆处理之后，相关的命令行参数很有可能会发生变化。下面的例子中，我们使用了HTML映射文件来寻找新的参数名称。比如说，我们尝试转换下列命令：

    
    
    SharpHound.exe --CollectionMethods DCOnly --OutputDirectory C:\temp\

通过搜索HTML映射文件中的每一个参数，我们将会获取到下列信息：

![](https://image.3001.net/images/20221222/1671712490_63a44eea04077e16691b1.png!small)

![](https://image.3001.net/images/20221222/1671712497_63a44ef11fd72fb9bc82f.png!small)

![](https://image.3001.net/images/20221222/1671712503_63a44ef7b8967657d6e3b.png!small)

替换所有的字符串后，结果如下：

    
    
    ObfuscatedSharpHound.exe --AphylesPiansAsp TurthsTance --AnineWondon C:\temp\

但是，某些值可能存在于多个分类：

![](https://image.3001.net/images/20221222/1671712515_63a44f034f14c3c1f2cc0.png!small)

因此，我们要养成在本地环境先进行测试的习惯。

## 项目地址

 **Codecepticon** ：【[ _项目地址_](https://github.com/Accenture/Codecepticon)】

## 参考资料

> [ _https://blog.xpnsec.com/building-modifying-packing-> devops/_](https://blog.xpnsec.com/building-modifying-packing-devops/)
>
> [
> _https://twitter.com/EmericNasi/status/1460640760928296966_](https://twitter.com/EmericNasi/status/1460640760928296966)
>
> [
> _https://github.com/MagicMau/ProceduralNameGenerator_](https://github.com/MagicMau/ProceduralNameGenerator)
>
> [ _https://github.com/uwol/proleap-> vb6-parser_](https://github.com/uwol/proleap-vb6-parser)
>
> [ _https://github.com/dwyl/english-words_](https://github.com/dwyl/english-> words)

