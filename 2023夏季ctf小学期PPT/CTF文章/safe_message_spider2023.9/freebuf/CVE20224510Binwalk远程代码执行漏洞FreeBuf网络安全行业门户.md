Binwalk 是用于搜索给定二进制镜像文件以获取嵌入的文件和代码的工具。

具体来说，Binwalk是一个固件的分析工具，旨在协助研究人员对固件非分析，提取及逆向工程用处。简单易用，完全自动化脚本，并通过自定义签名，提取规则和插件模块，还重要一点的是可以轻松地扩展。

## Part1漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 无  
  
Part2漏洞描述

‍漏洞名称| Binwalk 远程代码执行漏洞  
---|---  
CVE编号| CVE-2022-4510  
漏洞类型| 远程代码执行  
漏洞等级| 7.8 高危 (High）  
公开状态| 公开  
漏洞描述| 从 2.1.2b 到 2.3.3 版本的 ReFirm Labs binwalk 中发现了一个路径遍历漏洞。通过制作恶意 PFS文件系统文件，当
binwalk 在提取模式（-e 选项）下运行时，攻击者可以让 binwalk 的 PFS 提取器在任意位置提取文件。远程代码执行可以通过构建一个 PFS
文件系统来实现，该文件系统在提取时会将恶意的 binwalk 模块提取到文件夹 .config/binwalk/plugins
中从而执行代码。该漏洞与程序文件src/binwalk/plugins/unpfs.py相关。此问题会影响从 2.1.2b 到 2.3.3
的binwalk。  
时间线| 2022-10-26 漏洞提交2022-12-15 分配cve编号  
影响产品| Binwalk v2.1.2b-2.3.3  
  
##  **分析环境:**

Kalix64

Binwalk v2.3.3

## Part3漏洞复现

### 1\. 创建一个.pfs 文件头如下,然后打包成exp.zip

![1688537542_64a509c616abf4c35597a.png!small](https://image.3001.net/images/20230705/1688537542_64a509c616abf4c35597a.png!small)

2\. 正常binwalk执行之后输出

![1688537553_64a509d139fba25ce1504.png!small](https://image.3001.net/images/20230705/1688537553_64a509d139fba25ce1504.png!small)

3\. 在kali中用binwalk解析exp.zip binwalk -M -e exp.zip，并查看结果

![1688537572_64a509e493e9c73b8178b.png!small](https://image.3001.net/images/20230705/1688537572_64a509e493e9c73b8178b.png!small)

![1688537605_64a50a054396c50f849bd.png!small](https://image.3001.net/images/20230705/1688537605_64a50a054396c50f849bd.png!small)

4\. 看到在kali桌面生成了一个_exp.zip.extracted 的文件夹。文件夹下面pfs-root目录下看到123.py
是我们pfs文件头写的文件名。

5\. 构造验证pfs 并打包成exp.zip.

6\. 构造的pfs文件头如下

![1688537619_64a50a130d60b4ec92fb4.png!small](https://image.3001.net/images/20230705/1688537619_64a50a130d60b4ec92fb4.png!small)

7\. 再次在kali中用binwalk解析 exp.zip

![1688537628_64a50a1c3e4a3cbc821d9.png!small](https://image.3001.net/images/20230705/1688537628_64a50a1c3e4a3cbc821d9.png!small)

8.可以看到binwalk在正常输出之后又输出rce... 字段。证明复现成功！

Part4漏洞分析

什么是PFS文件

PFS文件是由PhotoFiltre
Studio（图像修饰程序）创建的选择文件。它包含图像编辑器的多边形选择工具使用的坐标，以便在给定坐标之间绘制线。PFS文件以纯文本格式存储。

漏洞源代码

![1688537643_64a50a2b84a35364a1dea.png!small](https://image.3001.net/images/20230705/1688537643_64a50a2b84a35364a1dea.png!small)

问题出现在红框内部的代码

在解析pfs文件头的时候，会把pfs文件头内部的文件命和out_dir 拼接。拼接之后默认走else代码分支，并且对特殊符号没有校验导致可以使用../
符号路径穿越。再利用binwalk的plugins功能。就可以释放py文件到binwalk的plugins目录下，从而代码执行。

## Part5修复建议

1\. Binwalk软件升级到最新的2.3.4版本。

2\. 代码要检测特殊符号，防止路径穿越。

