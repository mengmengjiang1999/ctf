## 关于Judge-Jury-and-Executable

Judge-Jury-and-Executable是一款文件系统取证分析扫描和威胁捕捉工具。该工具能够在MFT和操作系统级别上进行文件系统扫描，并且还可以扫描存储在SQL、SQLite或CSV中的数据。除此之外，Judge-Jury-and-Executable还可以利用SQL的强大功能和语法来探测威胁和数据。

## 功能介绍

> 立即扫描已安装的文件系统以查找威胁。
>
> 或者在事件发生前收集系统基线，以获得额外的威胁搜寻能力，可在事件发生之前、期间或之后使用。
>
> 一对多工作站。
>
> 扫描MFT，绕过文件权限、文件锁定或操作系统文件保护/隐藏。
>
> 为每个文件收集多达51个不同的属性。
>
> 扫描结果进入SQL表，以便以后进行搜索，在许多扫描和/或许多机器上聚合结果，并进行历史或回顾性分析。
>
> 利用SQL的强大功能来搜索文件系统、查询文件属性、回答复杂或高级问题，以及寻找威胁或危害迹象。

## 工具要求

> .NET Framework v4.8
>
> 带有读取/写入/创建访问权的本地或远程SQL数据库
>
> Visual Studio
>
> 接入网络
>
> SQL基础知识

## 高级数据分析

在MFT和取证级别的数据得到保护之后，将收集每个文件的操作系统级别属性、可用数据和元数据，并扩充MFT条目所创建的每个条目。因此，即使由于文件权限（ACL）、文件锁定（正在使用）、磁盘损坏、零字节长度文件或任何其他原因而无法访问操作系统API，工具仍将记录和跟踪该文件的存在。但是，条目将不包含操作系统无法访问的信息。每个文件最多可收集51个不同的数据点。

![](https://image.3001.net/images/20210508/1620447442_609610d2649a7a434ada4.png!small)

## 每份文件收集的信息

> SHA256哈希
>
> MD5哈希
>
> 导入表哈希
>
> MFT号&序列号
>
> MFT创建/修改/访问的数据
>
> 操作系统创建/修改/访问的数据
>
> 所有的标准操作系统文件属性：位置、大小、日期时间戳、属性、元数据
>
> 是否是PE或DLL或驱动器
>
> 认证代码是否已签名
>
> 是否验证了509证书链
>
> 自定义YARA规则
>
> 文件熵

## 样本数据行

 ** **MFTNumber****

|

18010  
  
---|---  
  
 ** **SequenceNumber****

|

0  
  
 ** **SHA256****

|

C67BE7D3F54D44AC264A18E33909482F1F8CA7B7FBAAF5659EF71ED9F8092C34  
  
 ** **FullPath****

|

C:\Windows\WinSxS\amd64_windows-defender-service-cloudclean_31bf3856ad364e35_6.3.9600.18603_none_73d12e8145b3841b\SymSrv.dll  
  
 ** **Length****

|

149264  
  
 ** **FileOwner****

|

TrustedInstaller  
  
 ** **Attributes****

|

A  
  
 ** **IsExe****

|

1  
  
 ** **IsDll****

|

1  
  
 ** **IsDriver****

|

0  
  
 ** **BinaryType****

|

16  
  
 ** **IsSigned****

|

1  
  
 ** **IsSignatureValid****

|

1  
  
 ** **IsValidCertChain****

|

0  
  
 ** **IsTrusted****

|

1  
  
 ** **ImpHash****

|

5D54F5D721E301667338323AC07578E3  
  
 ** **MD5****

|

65FB3391EB26F5AC647FC*40501D8E21D  
  
 ** **SHA1****

|

4B46DB2A99A47FF6A6EE376F4D79F5298BFF28A2  
  
 ** **CompileDate****

|

15:48.0  
  
 ** **MimeType****

|

application/x-msdownload  
  
 ** **InternalName****

|

symsrv.dll  
  
 ** **ProductName****

|

Debugging Tools for Windows(R)  
  
 ** **OriginalFileName****

|

symsrv.dll  
  
 ** **FileVersion****

|

6.12.2.633  
  
 ** **FileDescription****

|

Symbol Server  
  
 ** **Copyright****

|

© Microsoft Corporation. All rights reserved.  
  
 ** **Company****

|

Microsoft Corporation  
  
 ** **Language****

|

English (United States)  
  
 ** **Trademarks****

|

  
  
  
 ** **Project****

|

  
  
  
 ** **ApplicationName****

|

  
  
  
 ** **Comment****

|

  
  
  
 ** **Title****

|

  
  
  
 ** **Link****

|

  
  
  
 ** **ProviderItemID****

|

  
  
  
 ** **ComputerName****

|

L  
  
 ** **DriveLetter****

|

C  
  
 ** **DirectoryLocation****

|

C:\Windows\WinSxS\amd64_windows-defender-service-cloudclean_31bf3856ad364e35_6.3.9600.18603_none_73d12e8145b3841b  
  
 ** **Filename****

|

SymSrv.dll  
  
 ** **Extension****

|

.dll  
  
 ** **CertSubject****

|

CN=Microsoft Corporation, OU=MOPR, O=Microsoft Corporation, L=Redmond,
S=Washington, C=US  
  
 ** **CertIssuer****

|

CN=Microsoft Code Signing PCA, O=Microsoft Corporation, L=Redmond,
S=Washington, C=US  
  
 ** **CertSerialNumber****

|

6105F71E000000000032  
  
 ** **CertThumbprint****

|

D468FAEB5190BF9DECD9827AF470F799C*41A769C  
  
 ** **CertNotBefore****

|

7/13/2009 5:00:18 PM  
  
 ** **CertNotAfter****

|

10/13/2010 5:10:18 PM  
  
 ** **PrevalenceCount****

|

1  
  
 ** **Entropy****

|

0  
  
 ** **YaraRulesMatched****

|

NULL  
  
 ** **DateSeen****

|

17:12.0  
  
 ** **MftTimeAccessed****

|

43:52.6  
  
 ** **MftTimeCreation****

|

56:50.9  
  
 ** **MftTimeModified****

|

56:50.9  
  
 ** **MftTimeMftModified****

|

13:49.2  
  
 ** **CreationTime****

|

56:50.9  
  
 ** **LastAccessTime****

|

56:50.9  
  
 ** **LastWriteTime****

|

43:52.6  
  
## 固定查询样例

    
    
    /*
    
    IDEA: All files in the directory C:\Windows\System32\ should be 'owned' by TrustedInstaller.
    
    If a file in the System32 directory is owned by a different user, this indicates an anomaly,
    
    and that user is likely the user that created that file.
    
    Malware likes to masquerade around as valid Windows system files.
    
    Executables that are placed in the System32 directory not only look more official, as it is a common path for
    
    system files, but an explicit path to that executable does not need to be supplied to execute it from the
    
    command line, windows 'Run' dialog box of the start menu, or the win32 API call ShellExecute.
    
    */
    
     
    
    SELECT
    
    TOP 1000 *
    
    FROM  [FileProperties]
    
    WHERE
    
            [FileOwner] <> 'TrustedInstaller'
    
        AND [DirectoryLocation] = ':\Windows\System32'
    
        AND IsSigned = 0
    
    ORDER BY [PrevalenceCount] DESC
    
     
    
     
    
    /*
    
    IDEA: The MFT creation timestamp and the OS creation timestamp should match.
    
    If the MFT creation timestamp occurs after the creation time reported by the OS meta-data,
    
    this indicates an anomaly.
    
    Timestomp is a tool that is part of the Metasploit Framework that allows a user to backdate a file
    
    to an arbitrary time of their choosing. There really isn't a good legitimate reason for doing this
    
    (let me know if you can think of one), and is considered an anti-forensics technique.
    
    */
    
     
    
    SELECT
    
    TOP 1000 *
    
    FROM  [FileProperties]
    
    WHERE
    
    ([MftTimeAccessed] <> [LastAccessTime]) OR
    
    ([MftTimeCreation] <> [CreationTime]) OR
    
    ([MftTimeMftModified] <> [LastWriteTime])
    
    ORDER BY [DateSeen] DESC
    
     
    
    /*
    
    IDEA: The 'CompileDate' property of any executable or dll should always come before the creation timestamp for that file.
    
    Similar logic applies as for the MFT creation timestamp occuring after the creation timestamp. How could a program have been
    
    compiled AFTER the file that holds it was created? This anomaly indicates backdating or timestomping has occurred.
    
    */
    
     
    
     
    
    SELECT
    
    TOP 1000 *
    
    FROM  [FileProperties]
    
    WHERE
    
    ([MftTimeCreation] < [CompileDate]) OR
    
    ([CreationTime] < [CompileDate])
    
    ORDER BY [DateSeen] DESC

## 项目地址

Judge-Jury-and-Executable：【[
_GitHub传送门_](https://github.com/AdamWhiteHat/Judge-Jury-and-Executable)】

