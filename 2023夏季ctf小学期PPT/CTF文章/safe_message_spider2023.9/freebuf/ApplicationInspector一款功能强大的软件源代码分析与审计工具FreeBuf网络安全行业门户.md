![](https://image.3001.net/images/20200205/1580845498_5e39c9ba52bb0.jpg!small)

**ApplicationInspector是一款功能强大的软件源代码分析与审计工具，它可以帮助研究人员识别和发现目标应用程序中的公众周知的功能以及源代码中有意思的特性，并清楚目标应用的本质特征以及实现的功能。**

ApplicationInspector跟传统静态分析工具不同的是，它不会尝试去识别目标应用模式的好与坏，它只会报告它所检测到的应用程序模式，而且它会使用超过400种规则来完成检测，其中包含可能会影响应用程序安全性的一些模式，例如所使用的加密算法等等。ApplicationInspector会直接检查目标应用程序的源代码，而不是选择信任已有文档或安全建议，这对于分析开源项目或其他组件来说，能够提升准确率。

ApplicationInspector支持扫描各种编程语言，其中包括C、C++、C、Java、JavaScript、HTML、Python、Objective-C、GO、Ruby以及PowerShell[
_等等_](https://github.com/microsoft/ApplicationInspector/wiki/2.1-Field:-applies_to-\(languages-support\))，并且还支持扫描混合语言的文件。除此之外，ApplicationInspector还支持HTML、JSON和text等输出格式，默认输出报告格式为HTML。

值得一提的是，ApplicationInspector提供了一个可过滤的指示器，以此来提供最小化的误报率，并帮助研究人员自定义默认规则以及条件匹配逻辑。

## ApplicationInspector的功能如下图所示：

![](https://image.3001.net/images/20200205/1580845508_5e39c9c423942.png!small)

## 工具下载

广大研究人员可以使用下列命令将项目源 码克隆至本地：

    
    
    git clone https://github.com/microsoft/ApplicationInspector.git

## 项目构建

项目的源码构建需要安装.NET Core 3.0，并使用标准的dotnet构建命令直接在项目根目录运行。

### 框架依赖：

    
    
    dotnet build -c Release

### 目标平台构建：

    
    
    dotnet publish -c Release -r win-x86
    
    dotnet publish -c Release -r linux-x64
    
    dotnet publish -c Release -r osx-x64

## 工具使用

如需使用ApplicationInspector，可以直接下载对应的ApplicationInspector版本。如果你是用的是.NET
Core版本，你还需要安装.NET Core v3.0或更高版本。

ApplicationInspector是一款基于命令行的工具，因此我们可以直接在Windows、Linux或macOS平台上通过命令行终端来运行该工具：

    
    
    > dotnet AppInspector.dll or on *Windows* simply AppInspector.exe <command> <options>
    
    Microsoft Application Inspector 1.0.25
    ApplicationInspector 1.0.25
    
    (c) Microsoft Corporation. All rights reserved
    
    ERROR(S):
      No verb selected.
    
      analyze        Inspect source directory/file/compressed file (.tgz|zip) against defined characteristics
      tagdiff        Compares unique tag values between two source paths
      tagtest        Test presence of smaller set or custom tags in source (compare or verify modes)
      exporttags     Export default unique rule tags to view what features may be detected
      verifyrules    Verify rules syntax is valid
      help           Display more information on a specific command
      version        Display version information

使用样例

命令行帮助信息：

    
    
      Usage: dotnet AppInspector.dll [arguments] [options]
    
      dotnet AppInspector.dll -description of available commands
      dotnet AppInspector.dll <command> -options description for a given command

### 分析命令：

    
    
     Usage: dotnet AppInspector.dll analyze [arguments] [options]
    
      Arguments:
      -s, --source-path             Required. Path to source code to inspect (required)
      -o, --output-file-path        Path to output file.  Ignored with -f html option which auto creates output.html
      -f, --output-file-format      Output format [html|json|text]. Default = html
      -e, --text-format             Match text format specifiers 
      -r, --custom-rules-path       Custom rules path
      -t, --tag-output-only         Output only contains identified tags. Default = false
      -i, --ignore-default-rules    Ignore default rules bundled with application. Default = false
      -d, --allow-dup-tags          Output only non-unique tag matches. Default = false
      -c, --confidence-filters      Output only matches with confidence [high|medium|low].  Default = high,medium
      -k, --file-path-exclusions    Exclude source files [none|<list>]. Default = sample,example,test,docs,.vs,.git
      -x, --console-verbosity       Console verbosity [high|medium|low|none].  Default = medium
      -l, --log-file-path           Log file path.  Default is <application path>/log.txt
      -v, --log-file-level          Log file level [Debug|Info|Warn|Error|Fatal|Off].  Default = Error

### 扫描一个项目目录，不需要输出“output.html”文件（默认）：

    
    
    dotnet AppInspector.dll analyze -s /home/user/myproject 

### 添加自定义扫描规则：

    
    
    dotnet AppInspector.dll analyze -s /home/user/myproject -r /my/rules/directory -r /my/other/rules

### JSON格式输出：

    
    
    dotnet AppInspector.dll analyze -s /home/user/myproject -f json

## Tagdiff命令

如果你需要使用不同的标签（功能）来分析、比对和报告两个不同的项目，比如说两个不同版本的项目，你可以使用tagdiff命令：

    
    
     Usage: dotnet AppInspector.dll tagdiff [arguments] [options]
    
      Arguments:
      --src1                        Required. Source 1 to compare (required)
      --src2                        Required. Source 2 to compare (required
      -t, --test-type               Type of test to run [equality|inequality].  Default = equality
      -r, --custom-rules-path       Custom rules path
      -i, --ignore-default-rules    Ignore default rules bundled with application.  Default = false
      -o, --output-file-path        Path to output file
      -x, --console-verbosity       Console verbosity [high|medium|low].  Default = medium
      -l, --log-file-path           Log file path
      -v, --log-file-level          Log file level [error|trace|debug|info].  Default = error

### 查看不同项目对比结果的命令如下：

    
    
    dotnet AppInspector.dll tagdiff --src1 /home/user/project1 --src2 /home/user/project2

### 基本使用1：

    
    
    dotnet AppInspector.dll tagdiff --src1 /home/user/project1 --src2 /home/user/project2 -t equality

### 基本使用2：

    
    
    dotnet AppInspector.dll tagdiff --src1 /home/user/project1 --src2 /home/user/project2 -t inequality

## TagTest命令

该命令用于识别目标项目中是否存在指定的一系列规则，比如说，你想知道目标应用中是否使用了某个加密算法，就可以使用该命令了。

### 命令参数如下：

    
    
     Usage: dotnet AppInspector.dll tagtest [arguments] [options
    
      Arguments:
      -s, --source-path             Required. Source to test (required)
      -t, --test-type               Test to perform [rulespresent|rulesnotpresent].  Default = rulespresent
      -r, --custom-rules-path       Custom rules path 
      -i, --ignore-default-rules    Ignore default rules bundled with application.  Default = true
      -o, --output-file-path        Path to output file
      -x, --console-verbosity       Console verbosity [high|medium|low].  Default = medium
      -l, --log-file-path           Log file path
      -v, --log-file-level          Log file level

### 使用下列命令即可查看目标项目中是否存在某规则集：

    
    
    dotnet AppInspector.dll tagtest -s /home/user/project1 -r /home/user/myrules.json

### 基本使用1：

    
    
    dotnet AppInspector.dll tagtest -s /home/user/project1 -r /home/user/myrules.json -t rulespresent

### 基本使用2：

    
    
    dotnet AppInspector.dll tagtest -s /home/user/project1 -r /home/user/myrules.json -t rulesnotpresent

## ExportTags命令

### 该命令可以输出指定标签的规则集模式：

    
    
      Usage: dotnet AppInspector.dll exporttags [arguments] [options]
    
      Arguments:
      -r, --custom-rules-path       Custom rules path
      -i, --ignore-default-rules    Ignore default rules bundled with application.  Default = false
      -o, --output-file-path        Path to output file
      -x, --console-verbosity       Console verbosity [high|medium|low].  Default = medium

### 输出默认规则标签至终端：

    
    
    dotnet AppInspector.dll exporttags

### 使用输出文件：

    
    
    dotnet AppInspector.dll exporttags -o /home/user/myproject/exportags.txt

### 使用自定义规则以及输出文件：

`dotnet AppInspector.dll exporttags -r /home/user/myproject/customrules -o
/hom/user/myproject/exportags.txt`

## Verify命令

### 该命令可以验证规则集是否兼容，并保证导入和分析时不会发生错误：

    
    
      Usage: dotnet AppInspector.dll verifyrules [arguments]
    
      Arguments:
      -r, --custom-rules-path       Custom rules path
      -i, --ignore-default-rules    Ignore default rules bundled with application.  Default = false
      -o, --output-file-path        Path to output file
      -x, --console-verbosity       Console verbosity [high|medium|low].  Default = medium.

### 验证默认规则：

    
    
    dotnet AppInspector.dll verifyrules

### 使用自定义规则：

    
    
    dotnet AppInspector.dll verifyrules -r /home/user/myproject/customrules -i

## 项目地址

> ApplicationInspector：【[
> _GitHub传送门_](https://github.com/microsoft/ApplicationInspector)】

## 参考资料

> 1、[
> _https://github.com/Microsoft/ApplicationInspector/wiki_](https://github.com/Microsoft/ApplicationInspector/wiki)

 *** 参考来源：[
_microsoft_](https://github.com/microsoft/ApplicationInspector)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

