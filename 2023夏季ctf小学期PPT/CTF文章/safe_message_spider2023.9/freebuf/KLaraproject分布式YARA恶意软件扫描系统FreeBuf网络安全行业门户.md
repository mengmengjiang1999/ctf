****

[](https://youtu.be/ug5ZuezbD3c)

****

**Klara 项目旨在帮助威胁情报研究人员使用[Yara](https://n0where.net/pattern-matching-swiss-knife-yara) 搜索发现新的恶意软件。**

为了有效的匹配出恶意软件，研究人员往往需要搜集大量的样本，并需要对一系列收集/恶意文件启动Yara规则，然后再将结果返回。在某些情况下，Yara规则需要调整。但扫描大量的文件需要花费很长时间。相反，如果能使用自定义的架构，那么扫描10TB大小的文件也仅仅只需要30分钟左右。

Klara是一个用Python编写的分布式系统，它允许研究人员扫描一个或多个带有样本集合的Yara规则，在扫描完成后，研究人员可以通过电子邮件和Web界面获得通知。

##  **特性**

>   * 现代化的web界面，使研究人员可以通过电子邮件/API获取结果
>   * 强大的API，允许自动提交Yara作业，检查它们的状态并获取结果。API文档即将发布。
>   * 分布式系统，在商用硬件上运行
>

##  **架构**

Klara利用Yara的强大功能，使用dispatcher-worker模式分配扫描。每个worker服务器连接到一个dispatcher，以检查是否有新的作业可用。如果有，它将检查是否在自己的文件系统上提供了所需的扫描存储库，如果是，它将使用研究人员提交的规则开始执行Yara扫描

Klara试图解决的主要问题是尽可能的在一个合理的时间范围内，对大量恶意软件样本（>1TB）运行Yara作业。

##  **Klara安装**

### Klara运行依赖

>   * GNU/Linux （推荐使用Ubuntu 16.04 或最新的LTS版）
>   * MySQL / MariaDB DB
>   * Python 2.7
>   * Python virtualenv package
>   * Yara（安装在workers）
>

Klara的安装由以下四部分组成：

>   * 数据库安装
>   * Woker安装
>   * Dispatcher安装
>   * Web界面安装
>

组件间的连接关系图示：

    
    
                                  +----------+          +----------------+
                                  |          |          |                |
                      +---------->+ Database +<--+      |     nginx      |
                      |           |          |   |      |   (optional)   |
                      |           +----------+   |      |                |   
               +------+------+                   |      +-------+--------+   
               |             |                   |              |             
        +----->|  Dispatcher | <---+             |              |            
        |      |             |     |             |              |            
        |      +------+------+     |             |              v            
        |             |            |             |      +-------+--------+
        |             |            |             |      |                |
        |             |            |             |      |                |
    +---+----+   +----+---+   +----+---+         ^------+   Web server   |
    |        |   |        |   |        |                |                |
    | Worker |   | Worker |   | Worker |                |                |
    |        |   |        |   |        |                +----------------+
    +--------+   +--------+   +--------+
    
    

Workers使用简单的HTTP REST
API连接到Dispatcher。Dispatcher和Web服务器使用TCP连接来连接MySQL/MariaDB数据库。因此，组件可以被安装在分离的机器/虚拟机上。唯一的要求是它们之间允许TCP连接。

##  **安装指南**

<https://github.com/KasperskyLab/klara/tree/master/install>

##  **下载**

<https://github.com/KasperskyLab/klara>

*参考来源：[n0where](https://n0where.net/distributed-yara-malware-scanning-system-klara-project)，FB小编 secist 编译，转载请注明来自FreeBuf.COM

