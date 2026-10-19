威纶科技总部位于中国，在全球多个国家设有办事处，包括美国、日本、新加坡等。受影响的产品Kingview是该公司推出的第一款针对中小型项目推出的用于监视与控制自动化设备和过程的SCADA产品，其广泛应用于电力、制造、供水和污水处理、楼宇自动化、采矿、环保、冶金等领域。

## Part1漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 未知  
  
## Part2 漏洞描述

KingView中的KingMess.exe具有显示软件运行信息的功能，并且它会每隔一段时间就将软件运行信息以*.kvl形式保存成文件，当软件打开一个特殊构造的kvl文件，会造成栈溢出。

‍漏洞名称| WellinTech KingView 日志文件解析缓冲区溢出漏洞  
---|---  
CVE编号| CVE-2012-4711  
漏洞类型| 本地缓冲区溢出漏洞  
漏洞等级| 10.0 高危  
受影响产品| KingView 6.52 (kingMess.exe 65.20.2003.10300),KingView 6.53
(kingMess.exe 65.20.2003.10400),KingView 6.55 (kingMess.exe 65.50.2011.18049).  
公开状态| 公开  
时间线| 2012.08.28 – 分配CVE ID2012.12.03 – 漏洞补丁发布  
  
## Part3 漏洞复现

 **1\. 实验环境**

实验主机：win xp sp3

软件版本：KingView 6.53

 **2.涉及工具**

Python 3.9

 **3.复现步骤**

第一步：Python3.9利用攻击脚本生成poc.kvl。

![v2-4d0aace6b5882a3fe55d8057add062b2_720w.jpg](https://image.3001.net/images/20220829/1661758121_630c6aa99a41975c094ca.jpg!small)

第二步：将攻击者通过实验主机中信息窗口打开poc.kvl

![v2-5c51cefc1ecb9ebe1d491ba3fc3e2017_720w.jpg](https://image.3001.net/images/20220829/1661758122_630c6aaa52b66da986e41.jpg!small)

第三步：观察结果，发现此时发生了栈溢出，可成功执行shellcode，弹出计算器，如下图所示：

![v2-eae52ae0fb37fe617bbb5f2911bf7165_720w.jpg](https://image.3001.net/images/20220829/1661758123_630c6aab18747b1e150c9.jpg!small)

## Part4 漏洞分析

OllyDbg加载软件KingMess.exe运行，插件下API断点（因为之前有很多读文件的操作）。

![v2-f43a152f67d48daa054b133cd29bc161_720w.jpg](https://image.3001.net/images/20220829/1661758123_630c6aabea266fbfbd4da.jpg!small)![v2-07771e4b1b2552d185d05c591c66dbd2_720w.jpg](https://image.3001.net/images/20220829/1661758125_630c6aad337cf2dbf9aef.jpg!small)

调试执行到返回，如下图所示：

![v2-4c4ac370aaf7b6529029c3d3a7c1b878_720w.jpg](https://image.3001.net/images/20220829/1661758125_630c6aadcbe27a31bcf76.jpg!small)

读取文件头，如下图所示：

![v2-3d9748e9fb964db59ccddbbf7a9c06ef_720w.jpg](https://image.3001.net/images/20220829/1661758126_630c6aae61f46f288addd.jpg!small)

读取文件内容到栈区，如下图所示：

![v2-e07e24536052df9e9bbf4e9191eadb18_720w.jpg](https://image.3001.net/images/20220829/1661758127_630c6aaf01a3b62bd9dc8.jpg!small)

通过调试发现KingMess.exe会读取两次文件内容到栈区，然后崩溃，第二次读取长文件的时候，执行到返回，在内存地址下内存访问断点，如下图所示：

![v2-d290b4c850f8377f260f46a9b2940c0f_720w.jpg](https://image.3001.net/images/20220829/1661758128_630c6ab08f2f6213123d7.jpg!small)

0x40E467 内部读取文件内容，并复制到堆栈上，导致溢出，如下图所示：

![v2-3c0b2584ae1377d3d052daa817ada5b3_720w.jpg](https://image.3001.net/images/20220829/1661758129_630c6ab12f4f507d2fa30.jpg!small)

然后一路执行到返回，盯紧堆栈，最终返回到 被覆盖的堆栈位置(jmp esp)，如下图所示：

![v2-1c6ada466a6233aab3c10e9c0e989e5c_720w.jpg](https://image.3001.net/images/20220829/1661758129_630c6ab1cfa10cd41b603.jpg!small)

总结：打开kvl文件之后，会把文件内的内容按照一定格式sprintf格式化后输出到UI界面，但是在sprintf执行的时候，没有校验用户输入的长度，导致堆栈溢出。

## Part5 修复建议

安装补丁或升级至6.55以上的版本。

