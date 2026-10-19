![](https://image.3001.net/images/20210120/1611141687_60081237b859e188a03fe.png!small)

## 介绍

在这篇文章中，我们将会详细介绍漏洞CVE-2020-26233。这个漏洞将影响Windows平台下GitHub
CLI工具中Git凭证管理器核心v2.0.280及其之前所有版本的GIT命令行工具（也被称为gh），而且一旦成功利用，攻击者将能够在供应链攻击中使用该漏洞，并攻击全球数百万的软件开发人员。

## 问题描述

在此之前，我们曾讨论过[ _GitHub桌面端的远程代码执行问题_](https://blog.blazeinfosec.com/attack-of-the-clones-github-desktop-remote-code-execution)，但这一次受影响的组件则是Git凭证管理器核心。

默认配置下，当Git克隆带有子模块的代码库时，它首先克隆代码库的顶层（根目录），然后递归地克隆子模块。但是在这样做时，它会从顶级目录中启动一个新的Git进程。

如果一个名为git.exe的恶意程序被存放在了代码库根目录下，那么当程序尝试读取配置信息时，Git凭证管理器核心将调用此二进制文件。克隆过程正常进行，并且没有可见的迹象表明运行了恶意二进制文件而不是原始git可执行文件。

自从我们在2020年11月发布第一份报告以来，Github创建了一个[
_SafeExec库_](https://github.com/cli/safeexec)，以减轻Windows中二进制文件搜索顺序不一致带来的风险。

简要回顾一下，[
_Windows首先检查当前文件夹中是否存在给定的二进制文件_](https://superuser.com/questions/897644/how-does-windows-decide-which-executable-to-run)，只有在找不到该二进制文件时，才会遍历%PATH%环境变量中的目录，直到找到目标可执行文件。

在gh的v1.2.1版本中，引入了一个safeexec.LookPath函数，当通过滥用Windows路径搜索顺序克隆新存储库时，可以阻止远程代码执行。

![](https://image.3001.net/images/20210120/1611141712_60081250cee146aa11eec.png!small)

在仔细研究之后，我们的安全工程师Vitor Fernandes发现了一个绕过方法，这样就可以利用它来实现远程代码执行了。

在漏洞发现过程中，我们发现在fork一个新的私有存储库时，仍然可能出现远程代码执行场景。因为在克隆命令执行之后，并不会通过safeexec.LookPath函数来调用“git.exe
config credential.namespace”。因此，所以Windows将返回到其默认值并搜索git.exe文件当前克隆存储库中的二进制文件：

![](https://image.3001.net/images/20210120/1611141721_600812599600570eae4f3.png!small)

下面给出的是 _src/shared/Microsoft.Git.CredentialManager/CommandContext.cs_中的代码：

![](https://image.3001.net/images/20210120/1611141729_60081261d68363919289e.png!small)

我们可以看到，在第89行代码处，将创建一个新的进程来搜索git.exe，而“Environment.LocateExecutable('git.exe')”将作为目录路径参数传递给GitProcess()函数。

下图显示的是Environment.LocateExecutable()函数代码：

![](https://image.3001.net/images/20210120/1611141737_60081269238c78692db08.png!small)

 _/src/shared/Microsoft.Git.CredentialManager/EnvironmentBase.cs_

函数environment.TryLocateExecutable的代码可以在【 _这里_】找到：

![](https://image.3001.net/images/20210120/1611141745_600812714091f593d4ef9.png!small)

在使用Windows的实用工具where.exe时，它将会返回所有出现的文件或命令，包括%PATH%和当前目录的值。

## 漏洞利用

下面给出的是针对该漏洞的漏洞利用步骤：

> 创建一个新的代码库，或向现有代码库中添加文件；
>
> 向这个代码库中上传一个Windows可执行文件，然后将其重命名为exe；
>
> 等待目标用户fork这个代码库；
>
> 然后成功拿到Shell；

在下面的例子中，我们将calc.exe重命名为了git.exe，并将其上传到目标代码库中：

![](https://image.3001.net/images/20210120/1611141751_6008127776029172644ce.png!small)

Fork代码库并执行“gh repo fork REPOSITORY_NAME --clone”命令之后，目标设备将弹出计算器程序：

![](https://image.3001.net/images/20210120/1611141827_600812c34d1db5241fd4c.png!small)

## 参考资料

> [ _https://github.com/microsoft/Git-Credential-Manager-> Core/security/advisories/GHSA-2gq7-ww4j-3m76_](https://github.com/microsoft/Git-> Credential-Manager-Core/security/advisories/GHSA-2gq7-ww4j-3m76)
>
> [ _https://blog.blazeinfosec.com/attack-of-the-clones-github-desktop-remote-> code-execution_](https://blog.blazeinfosec.com/attack-of-the-clones-github-> desktop-remote-code-execution)
>
> [ _https://superuser.com/questions/897644/how-does-windows-decide-which-> executable-to-run_](https://superuser.com/questions/897644/how-does-windows-> decide-which-executable-to-run)
>
> [ _https://stackoverflow.com/questions/304319/is-there-an-equivalent-of-> which-on-the-windows-command-> line_](https://stackoverflow.com/questions/304319/is-there-an-equivalent-of-> which-on-the-windows-command-line)
>
> [
> _https://nvd.nist.gov/vuln/detail/CVE-2020-26233﻿_](https://nvd.nist.gov/vuln/detail/CVE-2020-26233)

