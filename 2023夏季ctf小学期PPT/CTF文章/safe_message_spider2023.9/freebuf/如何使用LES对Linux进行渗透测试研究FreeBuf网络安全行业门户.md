***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

![a.png](https://image.3001.net/images/20190614/1560486483_5d0322531fdf4.png!small)

## 写在前面的话

 **LES安全工具由Z-Labs开发并负责维护，可帮助安全测试人员以及安全分析专家在对Linux设备进行红队测试/渗透测试的过程中寻找关键漏洞。在这篇文章中，我将介绍这款工具的运行机制，并教会大家如何高效地使用LES。**

## 工具介绍

为了完成渗透测试任务并兼容不同Linux发行版系统，LES使用了大量的启发式方法来实现其主要功能，同时为给定的Linux设备生成候选漏洞列表，以最大程度地降低假阳性以及误报率。此外，出于工具实用性以及维护便利性开率，该工具还实现了以下特性：

> 1、子系统标记，针对目前大部分流行的Linux发行版，其中包括Debian、Ubuntu、RHEL/CentOS。
>
> 2、用户空间分析子系统，完全支持基于deb和rpm的发行版系统，部分支持其他发行版。

在LES的早期版本中，LES只会处理内核版本，这种方式完全跳过了发行版版本的问题，大部分主要处理功能都通过Linux_Exploit_Suggester脚本来实现。但是这种方式并不是非常有效，因为容易出现误报的问题，从而产生大量需要手动分析的漏洞。

随着时间的推移，LES也得到了改进，并通过生成候选漏洞列表的方式来解决之前的问题：

> 1、 基于内核版本生成初始漏洞列表；
>
> 2、 检查每个漏洞的“标签”命中率；
>
> 3、 基于“附加检查”舍弃不适用的漏洞利用；
>
> 4、 计算每个候选漏洞的内部度量（“等级”），并根据计算对列表排序。

接下来，我们将一一进行讨论。

### 基于内核版本生成初始漏洞列表

这是减少给定设备候选漏洞攻击数量的第一步。LES会解析uname命令的输出结果，并获取准确的内核版本信息，然后再跟漏洞利用代码中定义的版本信息进行对比。例如：Reqs:
pkg=linux-kernel,ver>=4.4,ver<=4.13,...

### 检测标签匹配

为了降低假阳性，并进一步减少候选漏洞数量，提升目标系统的适用性，LES还引入了“标签”的概念。标签是描述内核版本的简单语句，并标明给定的漏洞可以适用于这些系统版本，语句主要由正则表达式组成。例如：Tags:
RHEL=6,RHEL=7{kernel:3.10.0-514.21.2|3.10.0-514.26.1}。“标签”并不会舍弃候选漏洞列表中的实体数量，而是将更加适用的对象“往前放”。

### 舍弃不适用的漏洞

为了进一步优化候选漏洞列表，LES还引入了额外的参数要求（Reqs域）。在向LES中添加漏洞利用实体时，我们可以定义下列条件：

    
    
    Reqs:pkg=linux-kernel,ver>=3.2,ver<=4.10.6,CONFIG_USER_NS=y, \
    
    sysctl:kernel.unprivileged_userns_clone==1

上述条件表明内核版本必须>3.2并且<=4.10.6，而且内核的用户命名空间功能还必须以CONFIG_USER_NS=y进行编译，并启动该功能(sysctl:kernel.unprivileged_userns_clone==1)。

对于不常用的检测情况，LES还提供了运行任意BASH命令的功能，以便研究人员查看漏洞是否适用于给定系统。例如：

    
    
    Reqs:pkg=linux-kernel,ver>=4.4.0,ver<=4.4.0,cmd:grep -qi ip_tables/proc/modules

在上述场景中，命令“grep -qi ip_tables
/proc/modules”主要用来判断ip_tables模块是否已加载，并根据命令返回值（TRUE或FALSE）来判断漏洞是否适用于该系统。

### 基于排名动态生成的漏洞排序列表

最后，LES会根据动态计算的等级（Rank）结果对列表中的现有漏洞及西宁排序，等级越高则在列表中的位置越靠前，也就是漏洞适用于给定系统的概率会越高。

Rank计算基于下列规则：

1、 针对普通漏洞的初始rank为1。

2、 针对优秀漏洞的初始rank为5，例如dirtycow和eBPF_verifier等等。

3、 针对较差漏洞的初始rank为0，例如不稳定的或不适用的漏洞。

4、 如果待测Linux发行版系统版本匹配其中一个标签，则Rank加2。

5、 如果待测Linux发行版系统版本正则表达式匹配其中一个标签，则Rank加5。

例如，LES针对dirtycow漏洞利用的Rank计算方式如下，运行版本为Ubuntu 16.04，内核版本为4.4.0-21-generic：

    
    
    Inital rank: 5
    
    Distribution version match: +2 to rank
    
    kernel version regex match: +5 to rank
    
    final rank: 12

## 功能介绍

接下来，我们一起看看如何使用LES吧！

基本使用场景下，所有的步骤都会按顺序执行来生成候选漏洞列表：

    
    
    $./les.sh

\--cvelist-file选项可以用来设置完整的CVE列表，如果目标系统受其中漏洞影响的话，LES将会用其进行测试，列表可以通过<https://api-ksplice.oracle.com/api/1/update-list/>生成：

    
    
    $./les.sh --cvelist-file <cve-listing-file>

在红队研究的过程中，我们还可以“间接”运行LES来对目标（例如HIDS）执行更加严格的监控：

    
    
    victim-host$dpkg -l > pkgsListing.txt
    
    pentester-host$./les.sh --uname "<uname-a-from-victim>" --pkglist-filepkgsListing.txt

在对目标设备进行漏洞利用测试之前，我们通常还需要检查目标内核是否使用了其他加固措施：

    
    
    $./les.sh --checksec

### 工具快速下载

    
    
    wget https://raw.githubusercontent.com/mzet-/linux-exploit-suggester/master/linux-exploit-suggester.sh-O les.sh

## 项目地址

LES：【[GitHub传送门](https://github.com/mzet-/linux-exploit-suggester)】

 *** 参考来源：mzet，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

