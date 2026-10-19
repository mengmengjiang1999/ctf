## 前言

 **今天给大家介绍的是一款名叫HackerTarget
ToolKit的工具，这款工具实际上是一款网络情报工具，它可以帮助组织快速地发现自家网络系统中存在的攻击面。**

![HackerTarget
ToolKit](https://image.3001.net/images/20181114/1542202137_5bec23197a566.png!small)

## HackerTarget

HackerTarget这款开源网络情报工具可以帮助组织有效识别攻击面，并及时发现安全漏洞。在没有网络情报/数据的情况下，想要快速找出网络系统中的安全漏洞几乎是一件不可能完成的任务。通过将全世界最好的开源安全扫描工具与开源情报相结合，我们就可以实现攻击面的快速识别了。

随着网络技术的不断发展，我们可以在几秒钟之内部署大量的互联网设备，但随之而来的就是攻击面的动态增加，这也使得映射外部网络拓扑变得更加困难。因此，为了解决这样的问题，我们的工具会从域名和IP地址数据开始，然后通过开源扫描工具来映射网络结构。

注：本工具采用Python编程语言开发，并使用了HacKerTarget.com的API。

## 工具安装和运行

    
    
    git clone <https://github.com/ismailtasdelen/hackertarget.git>
    
    cd hackertarget/
    
    python hackertarget.py

## 工具主界面

![工具主界面](https://image.3001.net/images/20181114/1542202187_5bec234be54c6.png!small)  

### 菜单详情

    
    
    [1] 跟踪路径
    
    [2]Ping测试
    
    [3]DNS查询
    
    [4] 反向DNS
    
    [5] 查找DNS主机
    
    [6] 查找共享DNS
    
    [7] 区域传送
    
    [8] Whois查询
    
    [9] IP地址查询
    
    [10] 反向IP查询
    
    [11] TCP端口扫描
    
    [12] 子网查询
    
    [13] HTTP头检测
    
    [14] 提取页面链接
    
    [15] 退出

### 克隆现有代码库（通过HTTPS克隆）：

    
    
    root@ismailtasdelen:~#git clone https://github.com/ismailtasdelen/hackertarget.git

### 克隆现有代码库（通过SSH克隆）：

    
    
    root@ismailtasdelen:~#git clone git@github.com:ismailtasdelen/hackertarget.git

## 项目地址

> HackerTarget：【[GitHub传送门](https://github.com/ismailtasdelen/hackertarget)】

## 参考资料

> <https://hackertarget.com/>

***参考来源：[hackertarget](https://github.com/ismailtasdelen/hackertarget)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

