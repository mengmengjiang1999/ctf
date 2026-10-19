## 前言

前一段时间ciscn线下赛半决赛一个go的题目，给了二进制程序，给了源码，但是因为go需要联网下包才能编译，不然是不行的，考虑patch二进制程序，当时没ida啥也没，程序也跑不起来没法本地调试
我直接 ****** 最后还是用了队友的windows去给题目解了的，然后我也一直在找arm下跑x86的方案，也就总结了一下，整理发出来

## 环境

mac os 版本为13.4.1

utm版本为4.2.5

![](./img/3262351405227759333.png)

安装utm的环境就不在多说了，直接跳过，由于网上都是装desktop版本的，然后再去卸载桌面的那种方式，我队友告诉我会很卡装了很久，我就寻思找了个server
的镜像

## 下载镜像

笔者这里下载是2210，其他版本应该也一样 osboxes 封装了很多现成的环境，直接拉就行了而且还写了密码

    
    
    Username: osboxes
    Password: osboxes.org
    Open VM Tools: Not Installed
    Keyboard Layout: US (Qwerty)
    VMware Compatibility: Version 10+
    
    https://www.osboxes.org/ubuntu-server/#ubuntu-server-20-04-4-info
    

![](./img/3328052602192411596.png)

下载完成后解压得到vmdk

![](./img/2842111362470043710.png)

然后配合qemu给他转换为qcow2

    
    
    qemu-img convert -f vmdk -O qcow2 Ubuntu\ Server\ 22.10\ \(64bit\).vmdk Ubuntu2210.qcow2
    

选择模拟 选其他  
![](./img/8072930962195898113.png)

![](./img/4112127672700123819.png)

默认

![](./img/8294362338800714252.png)

名字自定义

![](./img/7125720398226625991.png)

点击编辑

![](./img/7741620564138445003.png)

点击新建磁盘 导入qcow2就行了

![](./img/1070897640114625033.png)

到这基础的配置就完事了，登录进去，给个dhcp就有ip了这里可以自己去配置什么什么的都ok，然后直接ssh链接进去

![](./img/6310202937345614298.png)

apt install proxychains -y 安装下工具 ，这里是我存粹懒的换源了  
然后clash开启下允许局域网连接

![](./img/7002654969820664202.png)

## 部署环境

先去安装

    
    
    proxychains apt update
    proxychains apt install python3-pip  python3-dev -y
    proxychains pip3 install -U pip 
    proxychains pip3 install pwntools
    proxychains apt install gdb
    proxychains git clone https://github.com/pwndbg/pwndbg
    proxychains ./setup.sh
    

这里给pwndbg也安装上去了

![](./img/5299752357362197145.png)

然后随意拉一个pwn的程序就行了，这里我拉的是

<https://buuoj.cn/challenges#rip>

gdb成功运行起来，然后我们测试下poc

![](./img/8708717036853669909.png)

    
    
    from pwn import *
    p=remote("node4.buuoj.cn",xxx)
    payload='A'*15+'B'*8+p64(0x401186+1).decode("iso-8859-1")
    p.sendline(payload)
    p.interactive()
    

![](./img/554571442133482402.png)

## 安装zsh

    
    
    proxychains apt install zsh -y
    proxychains wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh
    proxychains sh install.sh
    

![](./img/579908252736564078.png)

到这就配置完成了

## tips

### 配置ssh 免密码登录

![](./img/4712129238578607585.png)  
给我们本地的key直接写到ubuntu

![](./img/4104656723376944671.png)

    
    
    vim ~/.ssh/config
    
    Host pwn
        HostName 192.168.64.4
        User root

![](./img/847613184557316170.png)

### ida8 for mac

都放到百度网盘了

链接: <https://pan.baidu.com/s/1f1Tzwh5CximErgaLRCkToQ?pwd=wdg7> 提取码: wdg7  
\--来自百度网盘超级会员v5的分享

