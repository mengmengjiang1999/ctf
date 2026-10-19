本篇是”手上有啥就搞啥“系列的第二篇，研究对象是 **猫盘普通版** ，侧重点是 **固件刷机** 、 **挖矿程序逆向** 和 **挖矿木马检测与防范**
。

相较于上篇的手环，猫盘可算个复杂的设备，可玩性也更强。 **网上的教程主要侧重救砖** 、
**NAS构建(刷黑群晖)等开发相关的内容。本文也会简单涉及，原因是(我的一个朋友)猫盘变砖，刷机也是部分任务，但又不想拾人牙慧，故侧重探究猫盘所谓挖矿的技术实现**
、并借此荒腔走板地讨论 **挖矿木马的检测与防范** 。

 **往期回顾** ：[ **手上有啥就搞啥(一) — 小米手环3**](../articles/endpoint/344640.html)

## 0x00 基础知识

### 0x00 - 00 猫盘简介

猫盘是ARM平台的私有云服务器，官网出来这个可以用来挖矿的，由于硬件通用性高，很多固件可适配到猫盘上，现在主要适配猫盘的系统有：onespace（X3P）、synology（群晖）、openwrt(路由），可以利用猫盘做下载器或轻度备份文件服务器。

![](https://image.3001.net/images/20221011/1665489282_63455982c57f39a8ea0ca.png!small)

### 0x00 - 01 啥叫挖矿

 **首先，最重要的是，目前在国内挖矿行为是被禁止的！！！本文研究挖矿行为特征目的是更好的实施挖矿木马的检测与防范。**

BTC概念：

简单来说，区块链就是(因为各种原因，笔者现在比较反感去中心化一词，所以改用分布式)分布式数据库，或者分布式账本(当然web3日新月异，此处按下不表，只针对比特币)。每个人手上都有本账，抗打击能力强，摔不坏，丢不了，但是账不会白记，回报就是比特币。借用[
**混子曰漫画**](https://www.sohu.com/a/158701989_163524)如下：

![](https://image.3001.net/images/20221011/1665489330_634559b2d5000ca9fb7c0.png!small)

IPFS概念：

计算机专业的可能并不以为然，不就是分布式，普及玩儿烂的技术。最熟悉的当然是 **分布式存储** 。

星际文件系统 **IPFS** （InterPlanetary File
System）是一个面向全球的、点对点的分布式版本文件系统，目标是为了补充目前统治互联网的超文本传输协议，将所有具有相同文件系统的计算设备连接在一起。

![](https://image.3001.net/images/20221011/1665489360_634559d01e094699e7efc.png!small)原理用基于内容的地址替代基于域名的地址，也就是用户寻找的不是某个地址而是储存在某个地方的内容，不需要验证发送者的身份，而只需要验证内容的哈希，通过这样可以让网页的速度更快、更安全、更健壮、更持久。IPFS是基于区块链技术的去中心化存储网。

## 0x01 站在巨人肩上

### 0x01 - 00 硬件拆解

猫盘也算个高端设备，拆解十分简单，刷机和调试除了网口主要用到 **UART** 和 **USB** 两个接口。

因为万用表被借走，就选用了另一种高效的引脚识别方法——上网搜~

![](https://image.3001.net/images/20221011/1665489398_634559f62b895ebf46e8f.png!small)

上图已标明UART和USB对应引脚，注意到刷机(调试)时VCC不要接，USB接口需要ttl转USB母头转接线才能插U盘-.-。

### 0x01- 01 固件及资源

没啥好说的，直接放链接：

  * [ **flash-image**](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fhanwckf%2Fbl-armada-3720%2Freleases%2Flatest)

  *  **[Linux img 镜像](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fhanwckf%2Fbuild-catdrive%2Freleases%2Flatest)**

  * <https://github.com/hanwckf/build-catdrive>

  * [ **原厂资料备份**](https://links.jianshu.com/go?to=https%3A%2F%2Fpan.baidu.com%2Fs%2F1yikyr60_VpbHhOgpH8crgw)，提取码: qc7c

  *  **[APK下载](https://www.maopan.com/h5/)**

## 0x02 自己动手做

![](https://image.3001.net/images/20221011/1665489511_63455a67d3d1566aa1416.png!small)

### 0x02 - 00 左手刷机

 **拆机**

一个螺丝刀就可以搞定。

![](https://image.3001.net/images/20221011/1665489575_63455aa71eb2bb6a55b30.jpg!small)连接UART接口，
**再次强调不要接VCC！**

![](https://image.3001.net/images/20221011/1665489610_63455aca5127a206f24ee.png!small)
波特率 **115200** ， **UART** 输出error，系统 **panic** :

![](https://image.3001.net/images/20221011/1665489686_63455b16ec50c15aedd51.png!small)

所以第一步是救砖。

 **救砖**

首先U盘格式化为mbr的 **ext4或fat32** 分区，将 **flash-image.bin**
复制到其根目录下，然后插到猫盘上，斥2.8元巨资购买了转接头。( **Uboot** 还可以用，可以直接刷 **all.bin** )

![](https://image.3001.net/images/20221011/1665489746_63455b52b90b2c185535c.png!small)

在uboot控制台依次输入以下命令：

    
    
    setenv bootargs "console=ttyMV0,115200 root=/dev/mmcblk0p1 rootwait rw init=/bin/sh"
    ext4load mmc 0:1 0x1000000 boot/armada-3720-customer0.dtb
    ext4load mmc 0:1 0x2000000 boot/Image
    booti 0x2000000 - 0x1000000
    

把 **flash-image.bin** 复制到 **mmcblk0p2** 上：

    
    
    mount -t proc /proc
    mount /dev/mmcblk0p2 /media
    mount /dev/sda1 /mnt
    cp -f /mnt/flash-image.bin /media
    umount /media
    umount /mnt
    

在 **uboot** 控制台依次输入以下命令：

    
    
    ext4load mmc 0:2 0x1000000 flash-image.bin
    sf probe
    sf erase 0x0 0x200000
    sf write 0x1000000 0x0 0x200000
    

输入 **reset** 复位，然后进入新uboot刷入 **mac**

    
    
    env default -a
    setenv ethaddr "mac_addr"
    saveenv
    

重启刷入 **all.bin** ：

    
    
    bubt full.bin spi usb
    

![](https://image.3001.net/images/20221011/1665489896_63455be87f3ae8e13911c.png!small)

启动后就可以装硬盘网线刷想要的NAS系统，网上许多教程，这里不再赘述。

### 0x02 - 01 右手逆向

 **原地踏步**

由于看到二进制就想打开看一看，对于 **flash-image.bin** 上来就是 **IDA** ，一顿操作恢复了函数和字符串：

![](https://image.3001.net/images/20221011/1665490063_63455c8f072a42f899f9c.png!small)

在想办法解决符号时，发现是开源 **U-boot** ，有源代码 -.-，所以分析工作还是 **三思而后行** 吧。

 **挖矿过程逆向**

以下截图来自[
**开箱测评**](https://t.cj.sina.com.cn/articles/view/6414330982/17e52ec6600100arse)：

![](https://image.3001.net/images/20221011/1665490090_63455caa1f1bd84a80b8a.png!small)
**猫盘的挖矿过程与矿机相同吗？通过硬件配(jia)置(ge)就可以大概猜到~**

![](https://image.3001.net/images/20221011/1665490121_63455cc9311b2a3b996f4.gif!small)

简单搜索一下，猫盘挖矿的原理描述就是，
**共享猫盘的闲置存储空间和利用家庭网络的闲置上行带宽资源，形成一个区块链存储服务平台，输出给内容、视频、游戏、区块链等公司，获得这些公司支付的各种数字货币。然后兑换成BTC返还奖励给用户。技术细节基本没资料~.~**

简单来讲就是拿你的猫盘作 **资源节点** ，再简单点就是 **P2P共享经济** 。 **那具体实现是什么** ？ **IPFS** ？ **FIL**
？

可以有两条思路，一是通过 **进程列表** 、 **端口信息** 定位什么程序在起作用；二是 **静态分析固件** ，定位可执行文件位置。

由于挖矿服务已经扑街，猫盘又是刷机恢复回来的，所以勉为其难选静态分析。

固件结构很简单， **binwalk** 解析部分结果如下：

    
    
    DECIMAL       HEXADECIMAL     DESCRIPTION
    --------------------------------------------------------------------------------    8192          0x2000          Linux EXT filesystem, blocks count: 500024, image size: 512024576, rev 1.0, ext4 filesystem data, UUID=81f53685-f951-4b38-bac7-fc009baa9baa
    512032768     0x1E850000      Linux EXT filesystem, blocks count: 500032, image size: 512032768, rev 1.0, ext4 filesystem data, UUID=bdf85562-5165-4ec4-8a93-1c6379a479a4
    1024065536    0x3D0A0000      Linux EXT filesystem, blocks count: 1658720, image size: 1698529280, rev 1.0, ext4 filesystem data, UUID=a6ce57aa-5432-4047-bf6e-7d5b24142414
    ......
    

解开后部分目录：

    
    
    # tree -d -L 2
    .
    ├── ext-root
    ├── ext-root-0
    │   ├── local
    │   ├── opt
    │   └── root
    └── ext-root-1
        ├── bin
        ├── boot
        ├── dev
        ├── etc
        ├── lib
        ├── lib32
        ├── libexec
        ├── opt
        ├── root
        ├── sbin
        ├── usr
        └── var
    

还是老办法，先学习正向实现，再逆向分析。先了解了 IPFS搭建、Fil搭建等等，然后去固件里搜索，基本都是些偏离的信息：

    
    
    # grep -r ipfs
    Binary file ext-root-1/usr/lib/python2.7/site-packages/pygments/lexers/igor.pyc matches
    Binary file ext-root-1/usr/lib/python2.7/site-packages/pygments/lexers/_mapping.pyc matches
    ext-root-1/usr/share/nmap/nmap-service-probes:match ipfs m|^\\0\\0\\0\\x04\\0\\0(..)\\0\\0\\1\\n\\x10................\\x12.*\\x1a.(?:P-\\d+,?)+".[\\w.,_-]+\\*.[\\w.,_-]+$|s p/InterPlanetary File System peer/
    ext-root-1/usr/share/nmap/nmap-service-probes:match ipfs m|^\\0\\0..\\n\\x10................\\x12.*\\x1a.(?:P-\\d+,?)+".[\\w.,_-]+\\*.[\\w.,_-]+$|s p/InterPlanetary File System peer/
    

由于文件过多，逐一看太费时，毕竟还要搬砖。一般此时都是从Web接口出发回溯，但这里用到一条命令偶然打开了局面：

    
    
    # grep -r -P '[\\p{Han}]' # 搜索中文字符串
    

![](https://image.3001.net/images/20221011/1665490241_63455d417a41f5d573eec.png!small)不得不表扬开发人员的认真负责，如果那些恶意软件作者也这么良心，逆向分析就简单多了。可以看到和挖矿相关的代码在
**/opt/bin**
目录下。猜测python作为胶水语言，应该是坐配置和判断，最后调用一个ELF实现功能。有个名字带miner的程序可能就是主功能程序，从中文注释来看，
**yf** 是 **云帆** 的意思~.~。

![](https://image.3001.net/images/20221011/1665490370_63455dc25f8c82fef2352.png!small)

下简单分析一下流程。

首先是 **sys_y.py** ，注意到多次出现 **speedDaemon** 、 **yfminer** 、和 **fungeeker**
三个进程调用，为功能进程。

    
    
    def killalls():
        try:
            os.system("kill -9 `ps -ef|grep speedDaemon |grep -v grep|awk '{print $2}'`")
            os.system("kill -9 `ps -ef|grep yfminer |grep -v grep|awk '{print $2}'`")
            os.system("kill -9 `ps -ef|grep fungeeker |grep -v grep|awk '{print $2}'`")
    

函数逻辑十分简单，流程图如下：

![](https://image.3001.net/images/20221011/1665490395_63455ddb9a4990ffda2f4.png!small)

 **main** 函数循环调用 **PrepareStart**

    
    
    def main():
        signal.signal(signal.SIGINT, quit)
        signal.signal(signal.SIGTERM, quit)
    
        if((datetime.datetime.now()).strftime('%Y') == "1970"):
            sys.exit(0)
    
        while True:
            LOG("NOTICE", "MAIN", "\\n****************************\\n********** START! **********\\n****************************")
            try:
                PrepareStart()
            except:
                pass
            time.sleep(3600)
    

**PrepareStart** 收集信息和判断是否是挖矿版后调用 **SysStart** 开始主功能，在 **MultiMng**
函数中开线程最终启动之前提及 **speedDaemon** 、 **yfminer** 、和 **fungeeker** 三个进程。部分关键代码如下：

    
    
    def PrepareStart():
    				...
            try:
                LineIp = GetIp()
            MacAddr = GetMacAddr()
    				...
            try:
                MacAddr = MacAddr.replace(':', '')
    				...
            SPACE = get_space()
    				...
            while(0 == YDig):
                PrNode = prove_sncode() #验证猫盘是否为挖矿版
                if(PrNode == 0):
    	                YDig = 1
    	                continue
                elif(PrNode == -1):
                    killalls()     
                else:#((PrNode == -3) or (PrNode == -2))
                    YDig = 2
                    continue
            SysStart()
    
    def SysStart():
    				...
            MultiMng()
            while True:
                if(1 != YDig):
                    if(dignum > 480):
                        PrNode = prove_sncode() #验证猫盘是否为挖矿版
                        if(0 == PrNode):
                            YDig = 1
                        dignum = 0
                    dignum += 1
    
    def MultiMng():
        for i in range(MUL_NUB):
            thds.append(work_thd_mng(MAGE_QUE))
    				...
    
    class work_thd_mng (threading.Thread):
    		...
                    Execute()
                    EchSys2()
                    del_logfiles()
    
    #看是否启动程序
    def Execute():
    		...
        try:
            if((SpeedCode == 2) and (Opened == 1)):   #0:speedtest 1:yunfan 2:fengxing
                FX_GetMsg()
            if((SpeedCode == 1) and (Opened == 1)):   #0:speedtest 1:yunfan 2:fengxing
                #YF_GetMsg()
                YF_GetMsg2()
    		...
            sys_fx = commands.getoutput('ps -ef|grep fungeeker|grep -v grep | wc -l')
            sys_yf = commands.getoutput('ps -ef|grep yfminer|grep -v grep | wc -l')
            sys_sp = commands.getoutput('ps -ef|grep speedDaemon.sh|grep -v grep | wc -l')
    

下面分析关键的三个进程，通过分析得知 **speedDaemon** 和 **fungeeker** 只是辅助，都为脚本，篇幅有限不作赘述，核心程序还是
**yfminer** 。

    
    
    # file yfminer
    yfminer: ELF 64-bit LSB executable, ARM aarch64, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux-aarch64.so.1, for GNU/Linux 3.7.0, BuildID[sha1]=3415dd67a0e45f0f3286001f43406b9abff3b912, stripped
    

这个ARM64程序打开还是很丝滑的，基本自动识别：

![](https://image.3001.net/images/20221011/1665490443_63455e0bcd92f6f14ddb8.png!small)找到main函数，![](https://image.3001.net/images/20221011/1665490454_63455e1616cad9fa96f8a.png!small)

大致分析其流程：

    
    
    __int64 __fastcall main(int a1, char **a2, char **a3)
    {
      __int64 v3; // x0
      _DWORD *v5; // x19
      __int64 v6; // x0
      __pid_t v7; // w0
    
      if ( htonl(0x12345678u) == 305419896 )  // 判断字节序
        byte_747143 = 1;
      v3 = puts("yfminer begin"); // 程序开始
      if ( !(unsigned int)sub_52E268(v3) ) // 关键函数
      {
        while ( 1 ) // 死循环, 针对时间满足条件
        {
          sleep(1u);
          if ( qword_747180 && sub_4F9A48() - qword_747180 > 120000 ) // clock_gettime 检测
          {
            v5 = (_DWORD *)operator new(0x60uLL);
            sub_492160(v5);
            v5[4] = 29;
            v5[22] = 1;
            v5[23] = dword_7473D0;
            v6 = sub_437BBC();
            if ( (unsigned __int8)sub_4380B4(v6, v5, 0LL) != 1 )
              sub_42CEE0(v5);
            sub_4F2394(4LL, "Msgpool common thread is dead,line = %d,exit process\\n", (unsigned int)dword_7473D0); //sprintf
            sub_4F9A10(3000LL);  // usleep 1000 * 3000LL
            sub_47B918(103LL, 0LL, 0LL);
            v7 = getpid();  // 获取当前 pid
            kill(v7, 15); // kill pid
            sleep(0xAu);
            exit(0);
          }
        }
      }
      puts("start p2p fail");  // 程序启动失败
      return 0LL;
    }
    

**main** 函数十分简洁，给人以程序逻辑很简单的假象，毕竟是个 **p2p node** 程序，逻辑并没有那么简单；只管看来 **while**
循环是主功能，实际 **sub_52E268** 才是关键函数。

![](https://image.3001.net/images/20221011/1665490499_63455e431ae9962c237bd.png!small)上图为
**sub_52E268** 伪代码，红框部分为检测与配置。

![](https://image.3001.net/images/20221011/1665490533_63455e6568c42d84b8375.png!small)

然后通过 **signal** 信号实现通信， **sub_52E6FC** 为处理函数，用到的信号解释如下：

    
    
    SIGHUP 1 Term 终端的挂断或进程死亡
    SIGINT 2 Term 来自键盘的中断信号
    SIGQUIT 3 Core 来自键盘的离开信号
    SIGFPE 8 Core 浮点例外
    SIGKILL 9 Term 杀死
    SIGPIPE 13 Term 管道损坏：向一个没有读进程的管道写数据
    SIGTERM 15 Term 终止
    

由于后续程序过程较复杂，下主要分析 **sub_4FDBD4** 函数一条主线回溯( **被调用** → **调用** )：

 **sub_513100** → **sub_512FF8** → **sub_4FFF78** → **sub_4FDBD4**

在 **sub_4FDBD4** 函数中值得注意的是各类实例的初始化：

![](https://image.3001.net/images/20221011/1665490572_63455e8c476f025230b43.png!small)
**vtable** 结构如下，红框内为成员函数列表：

![](https://image.3001.net/images/20221011/1665490582_63455e9604473f726ce09.png!small)略过
**sub_512FF8** 、 **sub_4FFF78** 直接看复杂的 **sub_513100** 函数：

![](https://image.3001.net/images/20221011/1665490617_63455eb9a65f59385efdf.png!small)是
**p2p node** 的一些功能具体实现:

![](https://image.3001.net/images/20221011/1665490626_63455ec2d62ef117a2507.png!small)

猜测激励机制是根据绑定账号具体贡献在云端计算反馈，由于已经失(pao)效(lu)这里就不作分析。

  *  **挖矿木马的检测与防范**

猫盘所谓的挖矿与想象的并不相同，但仍借此荒腔走板聊一聊挖矿木马的检测防范。

由于虚拟货币(价格)兴起，挖矿木马、勒索软件也随之流行，成为网络安全重要威胁之一。挖矿木马主要分有以下几种 **形式** ：

 **可执行文件** ：存储在机器上的典型恶意程序，通常通过设置计划任务或修改注册表项实现持久化。

 **基于浏览器** ：使用JavaScript（或类似技术）的挖矿木马是在浏览器中执行。

 **无文件挖矿木马** ：利用如PowerShell等合法工具在机器的内存中执行挖矿作业，具有不落地、难检测等特点。

挖矿木马的 **主要特征** 有：

 **异常网络连接** ：连接挖矿相关的网站或 IP 地址。

 **专用协议流量特征** ：通信过程采用专门的通信协议，因此存在一定的网络通信特征。

 **极大的CPU或GPU资源占用** ：服务器响应速度慢、崩溃或频繁重启，设备温度过高。

从特征出发，可结合威胁情报检测网络连接，比如一些矿池地址检测：

比特币： **mine.btcguid.com:8332** 、 **pit.deepbit.net:8332** …

门罗币： **xmr-us-east1.nanopool.org:14444** 、 **pool.supportxmr.com:7777** 、
**pool.minexmr.com:5555** …

检测协议关键字：

 **id** 、 **method** 、 **jsonrpc** 、 **params** 、 **result** 、 **login** 、
**pass** 、 **agent** 、 **job_id** 、 **seed_hashblob** 、 **target** 、 **rigid**
…

![](https://image.3001.net/images/20221011/1665490667_63455eebc135715618fd9.png!small)检测主机资源：

![](https://image.3001.net/images/20221011/1665490677_63455ef51879543513131.png!small)防范措施也是老生成谈的一些点：
**补漏洞** ； **强密码** ； **重防护** ； **慎上网** 等。可惜这也很难。

## 0x03 做个总结

本篇针对猫盘作了固件刷机和挖矿程序逆向研究。设备较为高端，硬件和固件都比较规范，逆向研究的难度和价值都不高，作开发更合适。在挖矿过程研究方面，并没有使用猜测的IPFS方式实现，而是利用设备作了传统p2p
node，再将收益折算BTC回馈用户。在文末很突兀的提及了挖矿木马的检测与防范。每次提及Web3都是希望与唏嘘并存，最后笑一笑吧，下个设(po)备(lan)再见。

![](https://image.3001.net/images/20221011/1665490734_63455f2ea3c7dde0b87f7.png!small)

## 0x04 参考资料

[超详细的猫盘Docker应用解惑](https://post.smzdm.com/p/ar6rpn6g/)

[混子曰|一分钟了解比特币&区块链](https://www.sohu.com/a/158701989_163524)

[什么是IPFS?](https://zhuanlan.zhihu.com/p/32615963)

[猫盘--区块链技术落地，挖矿版开箱评测](https://t.cj.sina.com.cn/articles/view/6414330982/17e52ec6600100arse)

<https://github.com/hanwckf/build-catdrive>

[猫盘（挖矿版）- 能赚比特币的区块链硬盘](http://maopan.io/parameter.html)

[猫盘推出挖矿版应用分布式存储技术](https://cloud.tencent.com/developer/news/276042)

[linux - signal 信号列表](https://zhuanlan.zhihu.com/p/61882365)

[Android下恶意代码隐藏的一种方式 ](https://www.antiy.com/response/20211015.html)

