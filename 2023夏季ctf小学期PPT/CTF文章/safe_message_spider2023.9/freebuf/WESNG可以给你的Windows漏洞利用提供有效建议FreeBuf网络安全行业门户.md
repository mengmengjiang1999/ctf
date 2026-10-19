![](https://image.3001.net/images/20190723/1563893770_5d37200a7bc8f.jpg!small)

## WES-NG

 **WES-NG，全称为Windows ExploitSuggester - Next Generation，该工具的运行基于Windows
systeminfo实用工具的输出，可以给用户提供目标操作系统可能存在的漏洞列表，并针对这些漏洞给出漏洞利用实施建议。该工具的适用系统范围从Windows
XP到Windows 10，还包括Windows Server等服务器/工作站版本。**

## 工具使用

1、 执行下列命令获取最新的漏洞数据库：

    
    
    wes.py --update

2、 使用Windows内置的systeminfo.exe工具来获取本地系统的系统信息，或使用systeminfo.exe/S
MyRemoteHost来远程获取目标主机信息，并将所有信息重定向到一个文件中：systeminfo> systeminfo.txt。

3、 将systeminfo.txt输出文件作为输入参数来执行WES-NG。接下来，WES-NG会使用数据库信息来判断目标系统适配哪一个补丁，以及存在哪些可被利用的漏洞。

4、
由于微软提供的信息存在不完整性和假阳性，因此我们还需要参考其他的[数据来源](https://github.com/bitsadmin/wesng/wiki/Eliminating-false-positives)。

## 工具演示

### Collector

这个GitHub代码库会定期更新漏洞数据库，我们也可以使用下列命令来手动更新：

    
    
    wes.py --update

如果工具要求提供带有hotfix信息的.csv文件，我们可以直接使用/collector目录下的脚本来编译数据库。每一个脚本开头都提供了脚本注释，在使用之前大家可以仔细阅读。这些脚本运行之后，将会生成CVEs.csv文件。下面给出的是WES-NG collector的信息收集来源：

1、 微软安全公告数据：KBs（旧系统）。

2、 MSRC：微软安全响应中心（MSRC）的微软安全更新API，提供了微软系统更新的标准原始信息。

3、 NIST国家漏洞数据库（NVD）：利用Exploit-DB链接来补充信息，随后将漏洞信息合并到一个.csv文件中，然后压缩托管在GitHub代码库上。

## 漏洞提交

请直接通过本项目的Issues页面提交WES-NG漏洞问题。

如果分析结果存在假阳性，请阅读这篇【[文章](https://github.com/bitsadmin/wesng/wiki/Eliminating-false-positives)】。

## 参考资料

> [1]、<https://www.microsoft.com/download/details.aspx?id=36982>
>
> [2]、<https://portal.msrc.microsoft.com/en-us/developer>
>
> [3]、<https://nvd.nist.gov/vuln/data-feeds>

## 项目地址

WES-NG：【[GitHub传送门](https://github.com/bitsadmin/wesng)】

 ***
参考来源：[bitsadmin](https://github.com/bitsadmin/wesng)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

