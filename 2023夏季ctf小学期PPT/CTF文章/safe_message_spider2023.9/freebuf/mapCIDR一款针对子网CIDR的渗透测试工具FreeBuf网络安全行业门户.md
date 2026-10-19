![](https://image.3001.net/images/20201026/1603701433_5f968ab95205913acd44a.png!small)

## mapCIDR

mapCIDR是一款功能强大的小型实用工具，该工具能够帮助广大研究人员针对给定的子网或CIDR地址范围来进行各种类型的渗透测试操作。该工具进行了专门的设计以便进行大规模扫描操作，并且能够以功能代码库或独立命令行接口工具的形式来使用。

## 特性介绍

> 基于简单且模块化的代码库实现，方便分发代码；
>
> 支持基于CIDR的分布式扫描；
>
> 支持Stdin和Stdout，方便整合进工作流中；

## 工具安装

### 源码安装：

    
    
    ▶ GO111MODULE=auto go get -u github.com/projectdiscovery/mapcidr/cmd/mapcidr

### GitHub代码库克隆：

    
    
    ▶ git clone https://github.com/projectdiscovery/mapcidr.git; cd mapcidr/cmd/mapcidr; go build .; cp mapcidr /usr/local/bin

## 工具使用

    
    
    ▶ mapcidr –h

上面这条命令将显示该工具的帮助信息，下面给出的是该工具所有支持的操作选项：

![](https://image.3001.net/images/20201026/1603701570_5f968b42379893abb2081.png!small)

## 工具运行

为了获取给定CIDR对应的IP地址列表，我们可以使用下列命令：

    
    
    ▶ mapcidr -cidr 173.0.84.0/24
    
    ▶ echo 173.0.84.0/24 | mapcidr

命令运行结果如下图所示：

![](https://image.3001.net/images/20201026/1603701504_5f968b00759d3b655f557.png!small)

### CIDR地址切割

如需使用CIDR计数来对给定的CIDR或CIDR列表进行地址切割，或者将目标CIDR地址分割成多个相等大小的小型子网，可以使用下列命令：

    
    
    ▶ mapcidr -cidr 173.0.84.0/24 -sbc 10 -silent
    
    ▶ echo 173.0.84.0/24 | mapcidr -sbc 10 -silent

命令运行结果如下：

    
    
    173.0.84.0/27
    
    173.0.84.32/27
    
    173.0.84.64/27
    
    173.0.84.96/27
    
    173.0.84.128/27
    
    173.0.84.160/27
    
    173.0.84.208/28
    
    173.0.84.192/28
    
    173.0.84.240/28
    
    173.0.84.224/28

### 主机地址切割

如需将给定的CIDR地址切割成相等数量的主机，可以直接使用下列命令：

    
    
    ▶ mapcidr -cidr 173.0.84.0/16 -sbh 20000 -silent
    
    ▶ echo 173.0.84.0/16 | mapcidr -sbh 20000 -silent

命令运行结果如下：

    
    
    173.0.0.0/18
    
    173.0.64.0/18
    
    173.0.128.0/18
    
    173.0.192.0/18

注意：只有当每个子网所需的地址或主机数量是2的幂次方时，才有可能获得完美的地址分割。否则，该工具将尝试自动找到最佳分割策略以获得所需的结果。

## 以代码库的形式使用mapCIDR

广大研究人员还可以直接在自己的Go程序中使用这个代码库，下面的代码片段概述了如何将CIDR划分为子网，以及如何将CIDR划分为包含一定数量主机的子网：

    
    
    package main
    
     
    
    import (
    
             "fmt"
    
     
    
             "github.com/projectdiscovery/mapcidr"
    
    )
    
     
    
    func main() {
    
             // Divide the CIDR into two subnets
    
             subnets1 := mapcidr.SplitN("192.168.1.0/24", 2)
    
             for _, subnet := range subnets1 {
    
                       fmt.Println(subnet)
    
             }
    
             // Divide the CIDR into two subnets containing 128 hosts each
    
             subnets2 := mapcidr.SplitByNumber("192.168.1.0/24", 128)
    
             for _, subnet := range subnets2 {
    
                       fmt.Println(subnet)
    
             }
    
     
    
             // List all ips in the CIDR
    
             ips, _ := mapcidr.Ips("192.168.1.0/24")
    
             for _, ip := range ips {
    
                       fmt.Println(ip)
    
             }
    
    }

## 工具运行截图

![](https://image.3001.net/images/20201026/1603701550_5f968b2ee9026cf96ae6d.png!small)

## 项目地址

mapCIDR：【[GitHub传送门](https://github.com/projectdiscovery/mapcidr)】

