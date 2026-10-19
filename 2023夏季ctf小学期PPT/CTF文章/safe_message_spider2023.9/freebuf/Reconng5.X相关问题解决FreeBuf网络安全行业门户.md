升级kali后，自带的Recon-ng也升级到了5.1.1版本，变化还是很大的，最大的变化就是自带模块的取消，即第一次启动Recon-ng时是没有任何模块的，都要自己install，5.X模块将原来的模块移到了单独管理的‘marketplace’中。

搜索全网，得到的结论是，运行 marketplace install all 这条命令下载所有模块，即可轻松‘解决’所有问题……

然而，第一次尝试就出现了 **[!] Unable to synchronize module index.
(ConnectionError)，等一系列ConnectionError错误**

全网搜索后只发现了几种解决方案

1：关闭防火墙（不起作用）

2：apt-get更新（不起作用）

3：也有说在kali上才会出现问题，尝试换了ubuntu等（不起作用）

 **最后终于找到了一种有效的解决方案：**

 **1：配置本地DNS服务器信息（即不使用本地DNS）：**

    
    
    nameserver 114.114.114.114
    nameserver 8.8.4.4

 **2：将动态IP转换为静态IP**

    
    
    auto lo 
    iface lo inet loopback 
    auto eth0 
    iface eth0 inet static # static IP 
    address #本机IP 
    netmask 255.255.255.0 
    gateway #网关

 **配置完成重新打开recon-ng后即可解决**

![](https://image.3001.net/images/20200813/1597322069.png!small)

留下幸福的泪水。。。。。

附上一份官方5.x的变化说明pdf的链接：

<https://www.blackhillsinfosec.com/wp-content/uploads/2019/11/recon-ng-5.x-cheat-sheet-Sheet1-1.pdf>

以及一份说明

<https://www.blackhillsinfosec.com/whats-changed-in-recon-ng-5x/>

