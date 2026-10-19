![](https://image.3001.net/images/20210112/1610457359_5ffda10f2ea462a6fc1a5.png!small)

## 安全审计和静态分析

Aura是一款静态分析框架，为了应对PyPI上恶意软件包和易受攻击的代码日益增加的威胁而开发。

虽然还有其他工具的功能与Aura重叠，如Bandit、dlint、semgrep等，但这些替代工具的重点是不同的，这会影响功能以及如何使用它们。另一方面，Aura报告代码的**行为**、异常和漏洞，并尽可能多地提供信息。Aura报告的许多内容不一定是用户可以操作的，但它们告诉您许多有关代码行为的信息，例如进行网络通信、访问敏感文件或使用与指示可能的恶意代码的混淆相关的机制。通过收集此类数据并将其聚合在一起，Aura可以在功能上与其他安全系统（如防病毒、IDS或防火墙）进行比较，这些系统本质上是在对不同类型的数据（网络通信、运行进程等）进行相同的分析。

## 项目目标

  * 为上传到PyPI的包提供一个自动监控系统，在异常情况下发出警报，这些异常可能表示正在进行的攻击或代码中的漏洞；

  * 使组织能够对源代码进行自动化的安全审核，并实施安全的编码实践，重点是审核第三方代码，如Python依赖包；

  * 允许研究人员大规模扫描代码存储库，创建数据集并执行分析，以进一步推进恶意代码依赖性领域的研究；

## 功能列表

  * 支持在不执行代码得情况下分析恶意软件；

  * 通过重写AST树实现高级反混淆处理机制；

  * 递归扫描自动解包文档并扫描内容；

  * 支持扫描非python文件-插件可以在“原始文件”模式下工作，例如内置的Yara集成；

  * 扫描硬编码的密码和其他敏感信息；

  * 自定义差异引擎-支持比较不同数据源之间的更改，例如将PyPI包与所做的更改进行比较；

  * 适用于x和Python3.x源代码；

  * 高性能，支持扫描整个PyPI存储库；

  * 以多种格式输出，如纯文本、JSON、SQLite、SARIF等；

  * 在超过4TB的压缩Python源代码上进行了测试；

  * Aura能够报告代码行为，如网络通信、文件访问或系统命令执行；

  * 计算“Aura分数”，告诉你源代码/输入数据的可信度；

  * ....

如果你发现你想要的功能上面没有列举出来的话，别担心！Aura是一个基于健壮插件系统的框架，我们完全可以根据自己的需要自定义开发任何东西，，从一组数据分析器、传输协议到定制格式，实现了完全的自定义化。

## 工具安装

    
    
    poetry install --no-dev -E full

或者，也可以直接使用预构建的Docker镜像：

    
    
    sourcecodeai/aura:dev

## Aura运行

    
    
    docker run -ti --rm sourcecodeai/aura:dev scan pypi://requests -v

Aura使用一个所谓的uri来标识要扫描的协议和位置，如果没有使用协议，scan参数将被视为本地系统上文件或目录的路径。

![](https://image.3001.net/images/20210112/1610457449_5ffda169cbd3a4452f035.png!small)

### 数据包比对：

    
    
    docker run -ti --rm sourcecodeai/aura:dev diff pypi://requests pypi://requests2

![](https://image.3001.net/images/20210112/1610457474_5ffda1825c407df7ceb04.png!small)

查找最流行的代码包（您需要先调用“aura update”来[ _下载_ _更新_
_数据集_](https://cdn.sourcecode.ai/pypi_datasets/index/datasets.html)）：

    
    
    aura find-typosquatting --max-distance 2 --limit 10

## 工具演示视频

视频地址：【[点我观看](https://asciinema.org/a/367999)】

## 项目地址

Aura：【[ _GitHub传送门_](https://github.com/SourceCode-AI/aura)】

## 开源许可证协议

本项目的开发与发布遵循GPL v3.0开源许可证协议。

  

