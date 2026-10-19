## Lynis介绍

**Lynis是一款开源安全审计工具，广大系统管理员、安全专家和审计人员都可以利用该工具来对Linux以及类Unix系统进行安全审计。该工具可直接在测试主机上运行，而且跟常规漏洞扫描工具相比，Lynis的安全扫描范围更加广泛。**

近期，研究人员又发布了全新版本的多功能安全审计工具-Lynis。这个版本不仅对Lynis的核心功能进行了重大改进，而且还添加了很多额外的安全审计功能。

![](https://image.3001.net/images/20190413/1555133952_5cb17600a563f.png!small)

## 支持的操作系统

该工具不需要安装格外的依赖组件，因此它可以直接在所有的类Unix系统上直接运行，其中包括：

    
    
    AIX
    
    FreeBSD
    
    HP-UX
    
    Linux
    
    macOS
    
    NetBSD
    
    OpenBSD
    
    Solaris
    
    ….

除此之外，它还可以在树莓派和其他嵌入式设备上运行。

## 安装选项

Lynis是一款轻量级框架，而且使用简单。我们只需要把项目文件拷贝到本地系统目录中，然后使用下列命令即可开启安全扫描：

    
    
    ./lynis audit system

该工具采用Shell脚本开发，遵循GPL开源软件许可证协议。

## 工作机制

Lynis可以执行数百种单独的扫描任务，并根据扫描结果来判断目标系统的安全状态。从初始化程序，到生成最终的审计报告，每一种安全扫描任务都由多个测试阶段组成。

### 审计步骤

1、 判断目标操作系统；

2、 搜索可用工具及实用工具；

3、 检查Lynis更行；

4、 使用已启用的插件进行测试；

5、 按照分类进行安全测试；

6、 生成安全扫描报告；

除了上述数据之外，Lynis还会生成一份详细的技术分析报告，并存储在日志文件中，其中还包括了安全警告、安全建议和收集到的数据。

## 使用样例

由于Lynis的灵活性非常高，研究人员可以将其用于多种用途，下面是Lynis的几种使用场景：

> 安全审计
>
> 兼容性测试(PCI、HIPAA、Sox)
>
> 漏洞检测与扫描
>
> 系统安全增强

## 测试资源

很多工具都会使用相同的数据文件来执行安全测试。由于Lynis不会限制可运行的Linux发行版版本，所以它可执行的标准测试要比一般的测试工具多。

    
    
    Bestpractices
    
    CIS
    
    NIST
    
    NSA
    
    OpenSCAPdata
    
    Debian Gentoo

### Lynis插件

插件功能可以增强Lynis的功能，启用插件功能后，Lynis还可以执行额外的安全测试。

## 工具下载

> Lynis：【[官方网站](https://cisofy.com/downloads/lynis/)】
>
> Lynisv2.7.3：【[点我下载](https://downloads.cisofy.com/lynis/lynis-2.7.3.tar.gz)】

 *** 参考来源：[kitploit](https://www.kitploit.com/2019/03/lynis-273-security-auditing-tool-for.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

