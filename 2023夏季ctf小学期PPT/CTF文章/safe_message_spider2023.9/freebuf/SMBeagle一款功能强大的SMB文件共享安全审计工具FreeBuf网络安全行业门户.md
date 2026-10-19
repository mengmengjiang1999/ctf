![](https://image.3001.net/images/20220105/1641369494_61d54f960df45f97d0bde.png!small)

## 关于SMBeagle

SMBeagle是一款针对SMB文件共享安全的审计工具，该工具可以帮助广大研究人员迅速查看网络中所有的可视文件，并判断目标文件是否可读或可写入。该工具所有的扫描发现数据都将存储至一个CSV文件中，或直接推送至Elasticsearch主机。

注意：SMBeagle会尝试利用Win32 API来实现运行速度的最优化。

## 主要使用场景

### 研究重点在弱共享权限上

各种规模的企业通常都有文件共享，但文件权限安全性很差。

大型企业在文件服务器上的共享空间越来越大，发现权限配置错误的敏感数据并不少见。

小型企业通常在办公室的角落里有一个小型NAS，且没有任何权限限制！

SMBeagle将帮助研究人员获取这些共享并列出它可以读取和写入的所有文件。当然了，如果SMBeagle能读/写，那么勒索软件也可以读/写。

### 横向渗透和权限提升

SMBeagle可以为渗透测试人员提供比较隐蔽的权限提升和横线渗透路径。

通过直接将数据输出至Elasticsearch主机，测试人员可以快速找到可读脚本和可写可执行的文件。

在SMBeagle的帮助下，寻找水坑攻击和未受保护的密码从未如此容易。

## 工具架构

该工具基于模块化构建，并使用了松散的耦合结构进行模块之间的相互切换：

![](https://image.3001.net/images/20220105/1641369514_61d54faad668d2d3b9e79.png!small)

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/punk-security/SMBeagle

## 工具使用

该工具执行唯一必需的参数就是设置输出格式，也就是需要指定数据输出至一个CSV文件中，或是设置Elasticsearch主机的IP地址。

建议广大研究人员启动快速模式，并将数据输出至CSV文件中，但这个CSV文件可能会非常大：

    
    
    SMBeagle -c out.csv -f

## 工具完整使用

    
    
    USAGE:
    
    Output to a CSV file:
    
      SMBeagle -c out.csv
    
    Output to elasticsearch (Preffered):
    
      SMBeagle -e 127.0.0.1
    
    Disable network discovery and provide manual networks:
    
      SMBeagle -D -e 127.0.0.1 -n 192.168.12.0/23 192.168.15.0/24
    
    Scan local filesystem too (SLOW):
    
      SMBeagle -e 127.0.0.1 -l
    
    Do not enumerate ACLs (FASTER):
    
      SMBeagle -A -e 127.0.0.1
    
     
    
      -c, --csv-file                     提供CSV文件路径，将输出结果保存至CSV
    
      -e, --elasticsearch-host         提供Elasticsearch主机名，将输出结果保存至Elasticsearch
    
      -f, --fast                         每个目录枚举一个文件权限
    
      -l, --scan-local-drives             扫描设备的本地驱动器
    
      -L, --exclude-local-shares         不扫描设备的本地驱动器machine
    
      -D, --disable-network-discovery    禁用网络发现
    
      -n, --network                   手动添加网络扫描
    
      -N, --exclude-network             扫描中排除某个网络
    
      -h, --host                        手动添加主机扫描
    
      -H, --exclude-host                 扫描中排除某个主机
    
      -q, --quiet                       禁用不必要的输出
    
      -v, --verbose                     提供详细输出
    
      -m, --max-network-cidr-size        (默认: 20) 扫描目标SMB主机网络大小的最大值
    
                                         
    
      -A, --dont-enumerate-acls          (默认: false) 跳过枚举文件ACL
    
      --help                           显示帮助信息
    
      --version                         显示版本信息

## 项目地址

 **SMBeagle：** 【[ _GitHub传送门_](https://github.com/punk-security/SMBeagle)】

## 参考资料

> [ _https://github.com/punk-> security/SMBeagle/blob/main/kibana/README.md_](https://github.com/punk-> security/SMBeagle/blob/main/kibana/README.md)

