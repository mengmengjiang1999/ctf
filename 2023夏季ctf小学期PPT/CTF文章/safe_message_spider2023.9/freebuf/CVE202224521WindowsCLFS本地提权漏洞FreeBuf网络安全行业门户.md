CLFS是Microsoft在Windows Vista和Windows Server 2003
R2中为实现高性能而引入的日志框架，它为应用程序提供API函数来创建、存储和读取日志数据。利用此漏洞可以在计算机上执行任意代码，绕过安全限制并获得系统管理员权限。

## Part1漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 无| 无| 有  
  
## Part2漏洞描述

‍漏洞名称| Windows CLFS 本地提权漏洞  
---|---  
CVE编号| CVE-2022-24521  
漏洞类型| 本地权限提升  
漏洞等级| 7.8 高危 (High）  
公开状态| 公开  
漏洞描述| 通过精心构造的日志文件，可以触发任意代码执行，进行权限提升。  
时间线| 2022-4-12 Microsoft发布2022-4-15 NVD发布  
影响产品| 未安装相关补丁的:Win7至Win11Windows Server2008至2022  
  
## Part3漏洞复现

###  **1\. 复现环境**

系统版本：Windows 10 版本 1903

###  **2\. 复现步骤**

运行漏洞利用程序后，当前用户变更为system

![1688537164_64a5084c9a631877195d7.png!small](https://image.3001.net/images/20230705/1688537164_64a5084c9a631877195d7.png!small)

## Part4漏洞分析

CClfsBaseFilePersisted::LoadContainerQ函数的第215行判断_CLFS_CONTAINER_CONTEXT结构的cidQueue字段值是否为-1，为-1时则调用CClfsBaseFilePersisted::RemoveContainer函数。

![1688537178_64a5085ac5ce91f4978ba.png!small](https://image.3001.net/images/20230705/1688537178_64a5085ac5ce91f4978ba.png!small)

CClfsBaseFilePersisted::RemoveContainer函数的第56行调用CClfsBaseFilePersisted::FlushImage函数处理文件数据，当结果大于等于0时，取_CLFS_CONTAINER_CONTEXT的pCaontainer字段值，并调用相关函数。

![1688537189_64a5086551a7ce3eaa0d7.png!small](https://image.3001.net/images/20230705/1688537189_64a5086551a7ce3eaa0d7.png!small)

CClfsBaseFilePersisted::FlushImage函数第8行调用了CClfsBaseFilePersisted::WriteMetadataBlock函数。

![1688537199_64a5086f9e1946f9ba146.png!small](https://image.3001.net/images/20230705/1688537199_64a5086f9e1946f9ba146.png!small)

CClfsBaseFilePersisted::WriteMetadataBlock函数调用ClfsEncodeBlock和ClfsDecodeBlockjams函数。

![1688537210_64a5087a0fcd9f91d41ff.png!small](https://image.3001.net/images/20230705/1688537210_64a5087a0fcd9f91d41ff.png!small)

ClfsEncodeBlock调用ClfsEncodeBlockPrivate函数处理数据。

![1688537221_64a5088588acd20099eff.png!small](https://image.3001.net/images/20230705/1688537221_64a5088588acd20099eff.png!small)

ClfsEncodeBlockPrivate函数将扇区最后2字节数据写入到签名缓冲区，然后使用生成的签名替换原有的2字节数据。

![1688537231_64a5088fbe06ce7089b17.png!small](https://image.3001.net/images/20230705/1688537231_64a5088fbe06ce7089b17.png!small)

ClfsDecodeBlockjams调用ClfsDecodeBlockPrivate函数处理数据。

![1688537249_64a508a15cddf4a62f69f.png!small](https://image.3001.net/images/20230705/1688537249_64a508a15cddf4a62f69f.png!small)

ClfsDecodeBlockPrivate函数将签名缓冲区数据写回扇区最后2字节，但缓冲区内的数据并未进行处理。

![1688537259_64a508ab66aa1743a7fe1.png!small](https://image.3001.net/images/20230705/1688537259_64a508ab66aa1743a7fe1.png!small)

漏洞利用过程：

1、构造日志文件，使_CLFS_CONTAINER_CONTEXT结构的cidQueue字段值为-1，pCaontainer字段值为代码地址，签名缓冲区偏移指向pCaontainer所在地址。

2、调用CreateLogFile
API打开已有的日志文件，此时会调用ClfsDecodeBlockPrivate函数，将签名缓冲区数据写回到扇区最后2字节。

3、当_CLFS_CONTAINER_CONTEXT结构的cidQueue字段值为-1时，会调用CClfsBaseFilePersisted::RemoveContainer函数。

4、RemoveContainer函数调用CClfsBaseFilePersisted::FlushImage函数将扇区最后2字节写入到pCaontainer字段。

5、当RemoveContainer函数调用完FlushImage函数后，pCaontainer值被替换为指定的代码地址，随后会将该地址作为虚表指针并调用相关函数。因为pCaontainer是可控的，因此可以执行任意构造的代码，从而实现权限提升。

## Part5修复建议

[https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-24521﻿](https://link.zhihu.com/?target=https%3A//msrc.microsoft.com/update-guide/vulnerability/CVE-2022-24521)

根据系统安装链接内相应补丁。

