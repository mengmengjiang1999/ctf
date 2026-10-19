![](https://image.3001.net/images/20210717/1626453343_60f1b55f3f07cad62cc7c.jpg!small)

## 关于Aggrokatz

Aggrokatz是一款CobaltStrike攻击扩展插件，它能够启用pypykatz实现针对Beacon的远程交互。

当前版本的Aggrokatz允许pypykatz解析LSASS导出文件和注册表项文件，并在无需下载文件或向Beacon上传可疑代码的情况下，从中提取出用户凭证和其他存储的敏感信息。将来，该项目还会提供更多的额外功能来实现更隐蔽的活动，比如说搜索和解密所有的DPAPI密钥等等。

## 工具要求

> 你需要安装并配置好pycobalt；
>
> 你需要安装并配置好pypykatz，版本必须>=0.4.8；
>
> 你需要安装并配置好Cobalt Strike；

## 项目下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/sec-consult/aggrokatz

## 工具安装

> 确保pycobalt的cna文件已配置正确，并且能够识别你Python解释器的路径；
>
> 修改cna文件中的pycobalt_path，令其指向pycobalt.cna；
>
> 在Cobalt Strike中，访问View > Script Console和Cobalt Strike > Script
> Manager，使用Script Manager加载本项目中的cna脚本。

## 工具使用

> 如果cna脚本加载成功，你将会在右键点击一个Beacon时看到一个名为“pypykatz”的新菜单选项；
>
> 在解析过程中，你将会在Script Console窗口中查看到调试信息；
>
> 解析完成之后，结果将会在Script Console窗口和Beacon窗口中查看到解析结果；

### LSASS导出解析菜单参数

> LSASS file：远程主机中lsass.dmp文件的路径位置，你还可以使用UNC路径并通过SMB来访问共享的lsass.dmp文件。

> chunksize：一次读取的最大数据量。

> BOF file：BOF文件（Beacon对象文件），这个文件将在每次进行数据块读取的时候上传并在内存中执行。

> (module)：指定需要解析的模块，默认为：全部（all）。

> Output：指定输出格式。

> Populate Credential tab：成功解析所有获取到的凭证之后，将可以在Cobalt
> Strike的Credential标签页中查看到，该功能目前还在测试中。

> Delete remote file after parsing：成功解析LSASS导出文件后，将会从目标主机中删除。

### 注册表导出解析菜单参数

> SYSTEM file：远程主机中SYSTEM.reg文件的路径位置，你还可以使用UNC路径并通过SMB来访问共享的文件。
>
> SAM file（可选）：远程主机中SAM.reg文件的路径位置，你还可以使用UNC路径并通过SMB来访问共享的文件。
>
> SECURITY file（可选）：远程主机中SECURITY.reg文件的路径位置，你还可以使用UNC路径并通过SMB来访问共享的文件。
>
> SOFTWARE file（可选）：远程主机中SOFTWARE.reg文件的路径位置，你还可以使用UNC路径并通过SMB来访问共享的文件。
>
> chunksize：一次读取的最大数据量。
>
> BOF file：BOF文件（Beacon对象文件），这个文件将在每次进行数据块读取的时候上传并在内存中执行。
>
> Output：指定输出格式。

## 工具限制

文件读取BOF当前仅支持最大的文件大小为4GB，但这个限制可以通过一些修改来扩展，但是到目前为止还没有观察到如此大的文件。

## 项目地址

 **Aggrokatz：** 【[ _GitHub传送门_](https://github.com/sec-consult/aggrokatz)】

## 参考资料

> [ _https://www.cobaltstrike.com/_](https://www.cobaltstrike.com/)
>
> [
> _https://github.com/skelsec/pypykatz_](https://github.com/skelsec/pypykatz)
>
> [ _https://r.sec-consult.com/aggrokatz_](https://r.sec-> consult.com/aggrokatz)
>
> [ _https://github.com/dcsync/pycobalt﻿_](https://github.com/dcsync/pycobalt)

