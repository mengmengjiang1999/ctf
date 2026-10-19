**PVS-Studio支持分析用C，
C++，C#和Java开发的项目。你可以在Windows，Linux和macOS下使用它。本文将为大家简单演示，如何在Linux环境下使用PVS-Studio来分析C和C++代码。**

**![](https://image.3001.net/images/20190911/1568156897_5d782ce1b34a6.png!small)**

## 安装

在Linux下安装PVS-Studio有多种方法，这具体取决于你的发行版类型。最方便和首选的方法是使用存储库，因为它允许在发布新版本时自动更新分析器。另一个选择是使用安装包，你可以[在这里](https://www.viva64.com/en/pvs-studio-download/)找到它。

安装命令也因你使用的Linux发行版而异。例如，这是基于Debian的存储库安装命令：

    
    
    wget -q -O - https://files.viva64.com/etc/pubkey.txt | sudo apt-key add -    sudo wget -O /etc/apt/sources.list.d/viva64.list \
    https://files.viva64.com/etc/viva64.list
    sudo apt update
    sudo apt install pvs-studio

要从可下载的软件包安装PVS-Studio，你可以使用gdebi：

    
    
    sudo gdebi pvs-studio-VERSION.deb

安装过程在“[Linux安装和更新PVS-Studio](https://www.viva64.com/en/m/0039/)”文档部分有更详细的描述。你还可以在那里找到非Debian系统的信息。

安装PVS-Studio后，需要输入数据许可。命令如下：

    
    
    pvs-studio-analyzer credentials NAME KEY [-o LIC-FILE]

NAME和KEY分别是注册用户名和许可证密钥。可选参数-o允许你指定将生成许可证文件的位置。默认情况下，它将被存储在~/.config/PVS-Studio/目录中。

如果你需要试用密钥，可以在“[下载和评估PVS-Studio](https://www.viva64.com/en/pvs-studio-download/)”页面上获取。

##  检查你的项目

安装完成后，就可以开始检查项目了。其主要有两种方法：：

> 1.编译监控。
>
> 2.直接从构建系统运行。

我们先来谈谈第一种方式。要在Linux下启动监视，需要[strace](http://man7.org/linux/man-pages/man1/strace.1.html)程序。PVS-Studio使用它来收集在构建期间启动的进程列表和参数。

使用以下命令启动构建：

    
    
    pvs-studio-analyzer trace -- make

这里使用make，但你正在运行的用以构建项目的任意其他命令都可以在这个位置。如果需要，你还可以用通常的方式将命令行参数传递给它。

构建之后，strace将创建一个文件，然后分析器将使用该文件来检查源代码。启动分析的命令如下。

    
    
    pvs-studio-analyzer analyze -o /path/to/project.log

这将生成一个编码的日志文件，你可以将其转换为受支持的格式。稍后我们将讨论如何处理报告的问题。

除了strace之外，你还可以基于compile_commands.json（JSON编译数据库）文件进行分析。许多构建系统都有导出编译命令的内置方法，或者你可以使用[BEAR](https://github.com/rizsotto/Bear)程序来执行此操作。以下是在这种情况下启动分析的命令：

    
    
    pvs-studio-analyzer analyze –f /path/to/compile_commands.json

请注意，分析器通过其可执行文件名识别构建过程中使用的编译器。如果在尝试分析项目时遇到“No compilation units
found”错误，请尝试通过-compiler或-c命令行键显式指定编译器的名称：

    
    
    pvs-studio-analyzer analyze -c MyCompiler

如果你正在使用交叉编译，或者你的编译器具有非标准可执行文件名，则可能需要此项。

除监控模式外，你还可以将分析器直接集成到构建系统或IDE中。我们的官方[GitHub](https://github.com/viva64)存储库提供了已配置集成的示例项目：

> [pvs-studio-cmake-examples](https://github.com/viva64/pvs-studio-cmake-> examples)
>
> [pvs-studio-qmake-examples](https://github.com/viva64/pvs-studio-qmake-> examples)
>
> [pvs-studio-makefile-examples](https://github.com/viva64/pvs-studio-> makefile-examples)
>
> [pvs-studio-waf-examples](https://github.com/viva64/pvs-studio-waf-examples)
>
> [pvs-studio-eclipse-examples](https://github.com/viva64/pvs-studio-eclipse-> examples)

要了解有关在Linux下运行分析器的更多信息，请参阅[文档](https://www.viva64.com/en/m/0036/)。

##  报告

检查项目后，分析器会创建一份编码报告。要将其转换为受支持的格式，你需要使用PVS-Studio安装附带的plog-converter实用程序。

以下是支持的格式列表：

> xml-一种便于进一步处理分析结果的格式，[SonarQube插件](https://www.viva64.com/en/m/0037/)支持该格式；
>
> csv - 文件以纯文本形式存储表格数据（数字和文本）;
>
> errorfile - gcc和clang的输出格式；
>
> tasklist - 可以在QtCreator中打开的错误格式；
>
> html - html报告，包含分析结果的简短描述；
>
> fullhtml - 报告根据源码中的不同参数和导航对分析结果进行排序。

fullhtml格式是查看报告最方便的格式，因为这种格式支持你直接跳转到你感兴趣的警告相对应的代码行。以下是将你的报告转换为该格式的命令：

    
    
    plog-converter -a GA:1,2 -t fullhtml /path/project.log -o /path/report_dir

当你启动它时，名为/path/report_dir的新创建目录将包含所有报告文件。

注意-a参数。它允许你指定应在结果报告中显示的警告内容。如果你需要过滤分析器的输出，这会非常方便。上面的命令将创建一份报告，其中将仅包含第一和第二确定性级别（高和中）的一般分析消息。

一份示例报告：

![](https://image.3001.net/images/20190911/1568156933_5d782d05cc558.png!small)

通过在消息的位置单元格中单击，你可以跳转到相应的代码行：

![](https://image.3001.net/images/20190911/1568156941_5d782d0dedba9.png!small)

通过单击代码列中的诊断代码，你可以打开有关此诊断的文档。

##  抑制分析警告

使用任何静态分析器检查源代码时，都有出现误报的可能，或者出现一些无关紧要的警告。PVS-Studio具有抑制此类消息的方法。要定位单个警告，你可以使用“[抑制错误警报](https://www.viva64.com/en/m/0017/)”文档中描述的方法。

此外，在检查旧代码时，你可能还希望抑制所有警告。通常，如果你只是想检查添加到现有代码库的新代码，则可能需要此选项。你可以使用pvs-studio-analyzer的suppress参数。

你可以使用以下命令批量抑制报告中的警告：

    
    
    pvs-studio-analyzer suppress /path/to/report.log

有关已抑制警告的信息存储在名为suppress_base.json的文件中。 此类消息不包括在后续检查的报告中。

[这里](https://www.viva64.com/en/m/0032/)详细描述了这种机制。

##  总结

以上就是关于在Linux下使用PVS-Studio的简要说明。我希望它有用并解答一些最常见的问题。如需了解有关本主题的更多内容，请参阅[此处](https://www.viva64.com/en/m/0036/)的文档。

***参考来源：[viva64](https://www.viva64.com/en/b/0652/)，FB小编secist编译，转载请注明来自FreeBuf.COM**

  

