![](https://image.3001.net/images/20200824/1598235153.jpg!small)

## 1.目标

将 kali 安装到 Tinkpad E480

遇到问题： 无法安装无线网卡驱动

## 2\. 操作过程

 **注意： 下面的操作都是在root权限下操作的。**

环境介绍：

    
    
    # 笔记本型号
    Tinkpad E480
    # 当前 Kali 版本
    Linux kali 5.5.17-kali2-amd64
    # 无线网卡介绍
    Realtek Semiconductor Co., Ltd. RTL8821CE 802.11ac PCIe Wireless Network Adapter

### 2.1 换源

  * 修改源,为安装依赖软件包做准备

    
    
    vim /etc/apt/sources.list 
    
        ### 将下面的数据追加到末尾
    
        #deb http://http.kali.org/kali kali-rolling main non-free contrib
    
        #阿里云
    
        deb http://mirrors.aliyun.com/kali kali-rolling main non-free contrib
    
        deb-src http://mirrors.aliyun.com/kali kali-rolling main non-free contrib

  * 更新

    
    
    apt-get update && apt-get upgrade
    #删除已经下载的包 
    apt-get clean

### 2.2 启用 ssh 服务

    
    
    /etc/init.d/ssh start
    ##添加开机自启动   
    update-rc.d ssh enable
    ## 关闭则为：
    update-rc.d ssh disabled

开启了之后，就可以用自己熟悉的管理终端进行操作了。

### 2.3 驱动 RTL8821CE

  * 安装依赖

    
    
    sudo apt install bc module-assistant build-essential dkms

下载驱动代码

    
    
    git clone https://github.com/tomaspinho/rtl8821ce

  * 根据实际环境进行编译测试

    
    
    cd rtl8821ce
    
    ## uname -r 查询到软件包不存在，但是下面的已经默认安装
    ls /lib/modules/5.7.0-kali1-amd64/
    
    ## 原来的思路是想通过，修改 Makefile 里面的 
    ## KVER  := 5.7.0-kali1-amd64
    ## 后来觉得下面的这个方法更好 创建软链接
    cd /lib/modules/
    ln -s  5.7.0-kali1-amd64/ 5.5.0-kali2-amd64
    
    # make 
    sudo ./dkms-install.sh
    
    # 编译后，发现 8821ce.ko 文件
    insmod 8821ce.ko 
    insmod: ERROR: could not insert module 8821ce.ko: Invalid module format
    
    # 安装失败，重头再来。。。
    # 直接升级内核
    apt install linux-image-5.7.0-kali1-amd64
    
    ## 重启，发现无线网卡已经可用 
    reboot

## 3.小结

  * 思路回顾

发现问题后，先 lspci查了下无线网卡型号，然后就用 把网卡型号和 Kali 作为关键字，google了一下，获取了下面的参考文档的链接。

总结了下面两个参考链接的教程，大体思路是到 github上下载驱动，编译安装。

当时我跟着教程操作的时候，总也说无法安装linux-headers-xxxxxx,然后就有了 第二章节的一通操作。

总体来说，虽然开始的时候，大概猜测到了问题，但是由于对驱动和内核知识的欠缺，导致了这次翻车。这个文件就用于记录我第一使用
kali遇到的小问题，根本原因待分析。

  * 参考文档

    
    
    https://medium.com/@kimiyukiyukawa/installing-rtl8821ce-network-controller-on-ubuntu-335d8ccb8a92
    
    https://tutorialforlinux.com/2020/01/12/step-by-step-kali-linux-realtek-rtl8821ce-driver-installation-guide/

  * 引申

写下这篇文章后，我也没有彻底了解，是更新了内核，然后驱动就撞上了呢？

还是我之前编译好了驱动，然后更新内核，内核和驱动匹配，导致最后网卡驱动成功？

  * 其他

不知道这个操作是不是可以作为 TinkPad E480笔记本安装 debain系列系统，驱动 RTL8821CE无线网卡的通用解决思路。

驱动成功后，就不想再折腾了，先体验体验 Kali。欢迎大哥们提提自己的思路。

