![](https://image.3001.net/images/20191008/1570545424_5d9c9f108ca7f.jpg!small)

**很多安全研究人员都会面临这样一个问题，那就是如何在不安装代理或软件包的情况下，检查100多个不同的Linux系统是否匹配某些入侵威胁指标IoC。因此，Fenrir就应运而生了。**

##  Fenrir

Fenrir是一款简单但功能强大的IoC扫描器，Fenrir基于Bash脚本开发，可以帮助研究人员扫描Linux、Unix和macOS系统中的下列入侵威胁指标IoC：

###  1、哈希

MD5、SHA1和SHA256，使用md5sum、sha1sum和sha -a 256。

###  2、文件名

检测字符串以及子字符串的完整路径，例如"/var/temp/p.exe"中的"temp/p.exe"。

###  3、字符串

在文件中利用grep实现搜索功能。

###  4、命令控制服务器（C2）

检测C2服务器字符串，并通过 'lsof -i'和'lsof -i -n'输出。

###  5、时间戳

使用不同模式的stat来定义补货文件的最小和最大时间戳（创建时间）。

##  工具基础特性

> Bash脚本
>
> 无需安装，无需代理
>
> 使用常用工具来提取属性，例如md5sum、grep以及不同模式的stat
>
> 可在Linux、Unix和macOS系统平台下运行
>
> 智能排除（根据文件大小、扩展名和某些目录），以加快扫描速度
>
> 不留痕迹

##  工具使用

    
    
    Usage: ./fenrir.sh DIRECTORY

其中的DIRECTORY为递归扫描的起始目录。

**所有的设置都需要在脚本的Header中进行配置：**

![](https://image.3001.net/images/20191008/1570545454_5d9c9f2eddceb.png!small)

##  工具运行流程

Fenrir的运行流程如下：

> 1、读取IoC文件；
>
> 2、获取操作参数，并配置递归扫描的起始路径（目录）；
>
> 3、检查lsof输出中的C2服务器；
>
> 4、检查需排除的目录（可在脚本的Header中配置）；
>
> 5、检查需要扫描的特殊文件扩展名（可在脚本的Header中配置）；
>
> 6、检查IoC文件中的文件名（完整路径）是否匹配；
>
> 7、检查需要排除的文件大小（可在脚本的Header中配置）；
>
> 8、检查文件中的某些字符串（通过grep实现）；
>
> 9、检查给定哈希值；
>
> 10、检查文件更改和创建时间戳；

##  工具运行截图

**扫描执行，匹配不同类型的demo目录：**

![](https://image.3001.net/images/20191008/1570545471_5d9c9f3fa073f.png!small)

**检测C2服务器连接状态：**

![](https://image.3001.net/images/20191008/1570545477_5d9c9f45c1e5a.png!small)

**检测GZIP压缩日志文件中的字符串：**

![](https://image.3001.net/images/20191008/1570545483_5d9c9f4b6960e.png!small)

**工具配置：**

![](https://image.3001.net/images/20191008/1570545491_5d9c9f5388887.png!small)

**Ansible Playbook：**

![](https://image.3001.net/images/20191008/1570545496_5d9c9f584415a.png!small)

**Stat：**

![](https://image.3001.net/images/20191008/1570545505_5d9c9f619e806.png!small)

##  项目地址

> Fenrir：【[GitHub传送门](https://github.com/Neo23x0/Fenrir)】

 ***
参考来源：[Neo23x0](https://github.com/Neo23x0/Fenrir)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

