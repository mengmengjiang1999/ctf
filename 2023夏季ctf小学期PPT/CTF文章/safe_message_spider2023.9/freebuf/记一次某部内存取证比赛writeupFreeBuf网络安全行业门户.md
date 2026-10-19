#### 前言

刚好前段时间蹭了某部的一个取证比赛，偶遇原题魔改部分内容，分享一下wp，内存取证还是比较有意思的，附上镜像文件分享给大家。

#### volatility安装

 **windows下载地址**

<https://www.volatilityfoundation.org/26>

 **下载之后直接使用**

 **Linux安装volatitly2.6**

>  **mv volatility_2.6_lin64_standalone /usr/local/sbin/volatility**
>
>  **cd /usr/local/sbin**  
>  **echo $PATH**  
>  **volatility -h**

 **安装成功**

 **volatility3下载地址**

    
    
    https://github.com/volatilityfoundation/volatility3/releases/tag/v2.0.1
    

**使用环境python3**

    
    
    python3 setup.py build 
    python3 setup.py install
    pip3 install -r requirements.txt
    

![wKg0C2OFvweAdfqtAADNKgzKfy0475.png](https://image.3001.net/images/20230821/1692607457_64e323e18d89a08dadddf.png!small)

#### 常用命令

    
    
    volatility -f winxp.raw imageinfo                      # 查询镜像基本信息
    volatility -f winxp.raw --profile=WinXPSP3x86 pstree   # 查运行进程进程树
    volatility -f winxp.raw --profile=WinXPSP3x86 pslist   # 查正在运行的进程
    volatility -f winxp.raw --profile=WinXPSP3x86 memdump -p 324 --dump-dir=/home/lyshark    # 将PID=324的进程dump出来
    volatility -f winxp.raw --profile=WinXPSP3x86 procdump -p 324 --dump-dir=/home/lyshark   # 将PID=324进程导出为exe
    volatility -f winxp.raw --profile=WinXPSP3x86 dlldump -p 324 --dump-dir=/home/lyshark    # 将PID=324进程的所有DLL导出volatility -f winxp.raw --profile=WinXPSP3x86 getsids -p 324  # 查询指定进程的SID
    volatility -f winxp.raw --profile=WinXPSP3x86 dlllist -p 324  # 查询指定进程加载过的DLL
    volatility -f winxp.raw --profile=WinXPSP3x86 threads -p 324  # 列出当前进程中活跃的线程
    volatility -f winxp.raw --profile=WinXPSP3x86 drivermodule    # 列出目标中驱动加载情况
    volatility -f winxp.raw --profile=WinXPSP3x86 malfind -p 324 -D /home/lyshark   # 检索内存读写执行页volatility -f winxp.raw --profile=WinXPSP3x86 iehistory # 检索IE浏览器历史记录
    volatility -f winxp.raw --profile=WinXPSP3x86 joblinks  # 检索计划任务
    volatility -f winxp.raw --profile=WinXPSP3x86 cmdscan   # 只能检索命令行历史
    volatility -f winxp.raw --profile=WinXPSP3x86 consoles  # 抓取控制台下执行的命令以及回显数据
    volatility -f winxp.raw --profile=WinXPSP3x86 cmdline   # 列出所有命令行下运行的程序
    volatility -f winxp.raw --profile=WinXPSP3x86 filescan  # 列出文件volatility -f winxp.raw --profile=WinXPSP3x86 connscan    # 检索已经建立的网络链接
    volatility -f winxp.raw --profile=WinXPSP3x86 connections # 检索已经建立的网络链接
    volatility -f winxp.raw --profile=WinXPSP3x86 netscan     # 检索所有网络连接情况
    volatility -f winxp.raw --profile=WinXPSP3x86 sockscan    # TrueCrypt摘要TrueCrypt摘要volatility -f winxp.raw --profile=WinXPSP3x86 timeliner # 尽可能多的发现目标主机痕迹volatility -f winxp.raw --profile=WinXPSP3x86 hivelist                                       # 检索所有注册表蜂巢
    volatility -f winxp.raw --profile=WinXPSP3x86 hivedump -o 0xe144f758                         # 检索SAM注册表键值对
    volatility -f winxp.raw --profile=WinXPSP3x86 printkey -K "SAM\Domains\Account\Users\Names"  # 检索注册表中账号密码
    volatility -f winxp.raw --profile=WinXPSP3x86 hashdump -y system地址 -s SAM地址               # dump目标账号Hash值
    volatility -f winxp.raw --profile=WinXPSP3x86 printkey -K "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"  # 查最后登录的用户
    

#### 题目一

 **题目提示：你能帮助小明提取出内存镜像隐藏的密码吗？**

> volatility_2.6_win64_standalone.exe -f memory.img imagesinfo

![wKg0C2OFv5CAK9oqAACaQOqUk3E386.png](https://image.3001.net/images/20230821/1692607458_64e323e21bb075a3c9e0b.png!small)

> volatility_2.6_win64_standalone.exe -f memory.img -profile=Win2003SP1x86
> pslist //查进程

![wKg0C2OFv66AdXqUAADUMWyL0688.png](https://image.3001.net/images/20230821/1692607458_64e323e298b5716e093ab.png!small)

 **异常进程**`DumpIt.exe`,dump内存

>  **volatility_2.6_win64_standalone.exe -f memory.img --profile=Win2003SP2x86
> cmdscan //查看历史命令**

![wKg0C2OFv8aAE2ISAABGjfHFJNU408.png](https://image.3001.net/images/20230821/1692607459_64e323e320fa83ee92ad1.png!small)

 **历史命令涉及的进程只有两个**

> volatility_2.6_win64_standalone.exe -f memory.img --profile=Win2003SP2x86
> memdump -p 1992 --dump-dir=./ //dump出内存

 **使用foremost提取文件**

![wKg0C2OFvqAU8qRAABFBlNirtk453.png](https://image.3001.net/images/20230821/1692607459_64e323e387410bf76fd6a.png!small)

    
    
    key: Th1s_1s_K3y00000
    iv: 1234567890123456
    
    
    
    jfXvUoypb8p3zvmPks8kJ5Kt0vmEw0xUZyRGOicraY4=
    

**使用在线解密，aes解密，偏移量和key都有了，解密**

![wKg0C2OFvAKTVkAAB4ZgjjGsY943.png](https://image.3001.net/images/20230821/1692607459_64e323e3e79d3a3949b71.png!small)

#### 题目二

 **题目：小明的文件被加密了，你能帮助小明解密吗？**

 **链接：**<https://pan.baidu.com/s/1zTIKWY1k9IsQyRZiZIsoGQ>  
 **提取码：e6nh**

>  **volatility_2.6_win64_standalone.exe -f mem.dump imageinfo //查看Profile**

![wKg0C2OFwDGAUJTYAABGNZji148487.png](https://image.3001.net/images/20230821/1692607460_64e323e459968ee11cd5b.png!small)

>  **volatility_2.6_win64_standalone.exe -f mem.dump --profile=Win7SP1x64
> hivedump //查询所有注册表蜂**

![wKg0C2OFwE6AbiEZAABrDJBqfY530.png](https://image.3001.net/images/20230821/1692607460_64e323e4bd83a7c23bd01.png!small)

 **实际上第二个箭头读取hash值的时候为空**

![wKg0C2OFwG6AY7uBAABEnV7s36E298.png](https://image.3001.net/images/20230821/1692607461_64e323e5231dc3a0c0bd6.png!small)

 **获取到管理员用户的的ntlm值，解密，查询历史命令**

>  **volatility_2.6_win64_standalone.exe -f mem.dump --profile=Win7SP1x64
> cmdscan**

![wKg0C2OFwJqAZRF1AABJuPV2sCo696.png](https://image.3001.net/images/20230821/1692607461_64e323e5828282fa93dc0.png!small)

 **发现提示“flag.ccx_password_is_same_with_Administrator”**

 **首先提取出flag.ccx文件然后解密**

>  **volatility -f mem.dump --profile=Win7SP1x64 filescan |grep "flag.ccx"**

![wKg0C2OFwO6AMVkAAA2vKHKj3A782.png](https://image.3001.net/images/20230821/1692607461_64e323e5e4c46ce420c0c.png!small)

 **windows下无法使用查询命令，linux查询到加密文件，dump出来**

> **volatility -f mem.dump --profile=Win7SP1x64 dumpfiles -Q
> 0x000000003e435890 --dump-dir=./**

![wKg0C2OFwQCAOxZPAAAxiS186dU738.png](https://image.3001.net/images/20230821/1692607462_64e323e6493ad13989f61.png!small)

 **且进程中存在进程"encryto.exe",所以使用该程序解密即可，挂载flag.ccx,使用密码读取文件即可**

![wKg0C2OFwaAHZ8fAABw07prJ2c230.png](https://image.3001.net/images/20230821/1692607462_64e323e6a9a036cd23761.png!small)

#### 题目三

 **题目：最近小明喜欢上了维吉尼亚，小明的磁盘文件被损坏了你能帮他恢复数据，解决谜题吗？**

 **链接：**<https://pan.baidu.com/s/1UjnKWx2KgDBKyvs5s1ld6Q>  
 **提取码：o2oq**

>  **volatility -f easy_dump.img imageinfo**

![wKg0C2OFwUOAADVEAACATFAxsr8702.png](https://image.3001.net/images/20230821/1692607463_64e323e71b7bf9b38999b.png!small)

>  **volatility -f easy_dump.img --profile=Win7SP1x64 pslist //查看进程**

![wKg0C2OFwVWABSVzAADPmQFqhI069.png](https://image.3001.net/images/20230821/1692607463_64e323e785628aae61821.png!small)

 **题目给出了文件损坏，涉及到内存镜像应用，提取内存数据**

> **volatility -f easy_dump.img --profile=Win7SP1x64 memdump -p 2500 --dump-> dir=./**

![wKg0C2OFwbiANvonAABsK6AhIUs947.png](https://image.3001.net/images/20230821/1692607464_64e323e80ff6e546f1a9c.png!small)

 **因为查询是否还存在镜像文件使用命令时发现存在图片，使用foremost分离**

>  **foremost 2500.dmp**

![wKg0C2OFwZyATTjAAA2qTF70K8882.png](https://image.3001.net/images/20230821/1692607464_64e323e870a474c32d911.png!small)

 **分离出的文件夹存在一个txt和压缩包等，压缩包使用binwalk分离，发现存在img文件，挂载的时候发现镜像损坏，需要恢复数据**

![wKg0C2OFwcmAM8vAAAtIVBDlUY073.png](https://image.3001.net/images/20230821/1692607464_64e323e8c9422b0d226c6.png!small)

 **这里我使用磁盘恢复工具DiskGenius无法恢复，kali下自带磁盘恢复工具**`testdisk`

>  **testdisk message.img**

![wKg0C2OFwdAUcNiAACCB5yIim4762.png](https://image.3001.net/images/20230821/1692607465_64e323e92e39f716e20d3.png!small)

`c`恢复文件，q退出可以看到恢复的文件`.message.swp`

![wKg0C2OFwfSASa3dAABGi4N3Iss232.png](https://image.3001.net/images/20230821/1692607465_64e323e999d8e5b876aa2.png!small)

 **hint.txt中的数据类似于坐标，根据脚本还原**

    
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    x = []
    y = []
    with open('hint.txt','r') as f:
       datas = f.readlines()
       for data in datas:
            arr = data.split(' ')
            x.append(int(arr[0]))
            y.append(int(arr[1]))
         
    plt.plot(x,y,'ks',ms=1)
    plt.show()
    

![wKg0C2OFwhiAaqctAAFaFPNNCzs811.png](https://image.3001.net/images/20230821/1692607466_64e323ea0d6bdd5c31513.png!small)

**扫码内容为**

>  **Here is the vigenere key: aeolus, but i deleted the encrypted message**

 **密文就是我们恢复磁盘的内容**

>  **yise!dmsx_tthv_arr_didvi**

 **根据维吉尼亚在线解密，密码为：aeolus**

![wKg0C2OFwiiAGoRjAAA1Fzw27vQ634.png](https://image.3001.net/images/20230821/1692607466_64e323eaae4eefb3ad9ce.png!small)

#### 题目四

 **题目：找到CTF用户的password**

 **下载地址**

 **链接：**<https://pan.baidu.com/s/1axn5C_wwc4B8HwnZaVBptQ>  
 **提取码：7t9p**

>  **volatility_2.6_win64_standalone.exe -f 152050.raw imageinfo
> //查看Profile类型**

![wKg0C2OFwpKADSJ2AABEoHtdIWY502.png](https://image.3001.net/images/20230821/1692607467_64e323eb10ef2b1fa4d7a.png!small)

>  **D:\firefoxdownload\volatility_2.6_win64_standalone
> >volatility_2.6_win64_standalone.exe -f 152050.raw
> --profile=Win7SP1x86_23418 hashdump**

![wKg0C2OFwqOAELAAAAxDs4e4Zk111.png](https://image.3001.net/images/20230821/1692607467_64e323eb6d33904e2a156.png!small)

 **ntlm值解密**

![wKg0C2OFwryAMn2qAABEeZvHVOM249.png](https://image.3001.net/images/20230821/1692607468_64e323ec031a84270dcc8.png!small)

 **读取到CTF的密码了**

#### 题目五

 **题目：小明计算机又被不知名账户登录了？明明在计算机管理中没有这个用户，为什么还会被这个用户登录呢，你能帮忙小明找出匿名登录的用户名和密码是什么吗**

 **链接：**<https://pan.baidu.com/s/1qadNeLWIMHsyO3ocxRBcmw>  
 **提取码：jdme**

> python2 vol.py -f misc.vmem imageinfo

![wKg0C2OFwtKAN9nNAAB8KZ6KBnM001.png](https://image.3001.net/images/20230821/1692607468_64e323ec684509c502f76.png!small)

 **读取进程列表**

> python2 vol.py -f misc.vmem --profile=Win2003SP1x86 pslist

![wKg0C2OFwuAJOM3AADr63eXQRE489.png](https://image.3001.net/images/20230821/1692607468_64e323ecc5bf34174d752.png!small)

 **尝试dump对应的进程**

> volatility -f misc.vmem --profile=Win2003SP1x86 memdump -p 804 --dump-dir=./

![wKg0C2OFwwGADtQAABEj3JbTDw412.png](https://image.3001.net/images/20230821/1692607469_64e323ed56656c8d280db.png!small)

> volatility -f misc.vmem --profile=Win2003SP1x86 hashdump

 **dump所有的用户哈希，但是存在大量的用户名，需要判断哪一个是我们想要的**

![wKg0C2OFwwACNM4AAHNO4xcpZw501.png](https://image.3001.net/images/20230821/1692607469_64e323edb9af90f52896d.png!small)

> volatility -f misc.vmem --profile=Win2003SP1x86 filescan

![wKg0C2OFwyOAS9gpAAFSb6DBuw262.png](https://image.3001.net/images/20230821/1692607470_64e323ee723db114c9db7.png!small)

 **存在大量的文件，无从下手，回头查看dump出的两个exe进程的内存，注册表的话直接查找SAM属性**

> strings -e l -d 804.dmp|grep "SAM" //查询SAM字符串，数据块大小为l进行查找

![wKg0C2OFwzKAT5dAACDorFYULc223.png](https://image.3001.net/images/20230821/1692607471_64e323ef05d5d945f0ff7.png!small)

 **发现注册表内的用户路径，然后检索注册表中的该用户**

> volatility -f misc.vmem --profile=Win2003SP1x86 printkey -K
> "SAM\Domains\Account\Users\00000493" **

![wKg0C2OFw0OADeOQAAEoMh1qSo884.png](https://image.3001.net/images/20230821/1692607471_64e323ef6c543203ff0e4.png!small)

 **知道隐藏的用户名为**`FHREhpe\$`,dump出该用户的hash值即可

> volatility -f misc.vmem --profile=Win2003SP1x86 hashdump|grep "FHREhpe"

![wKg0C2OFw1SALiKyAAAKMxfEXo001.png](https://image.3001.net/images/20230821/1692607471_64e323efe261e4aeecabf.png!small)

 **md5解密即可得到密码**

#### 参考链接

<https://blog.csdn.net/lyshark_csdn/article/details/124939244>

