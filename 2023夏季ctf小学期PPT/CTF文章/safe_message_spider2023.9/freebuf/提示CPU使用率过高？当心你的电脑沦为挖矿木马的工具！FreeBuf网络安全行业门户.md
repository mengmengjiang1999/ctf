## 前言

最近几天不断收到系统的报警信息，提示CPU利用率过高。

主机长时间的高占用一般是由挖矿木马导致的，因此下面就以挖矿木马的方式进行排查系统。

![](https://image.3001.net/images/20211202/1638437452_61a8924ca1caf9ca73ffc.png!small)

## 排查思路

### 查看资源占用情况

    
    
    ps

查看到“ftpuser用户”的一个进程占用了将近90%的CPU资源。

###
![](https://image.3001.net/images/20211203/1638513643_61a9bbeb154d0e07c21f9.png!small)查找进程真实路径

    
    
    ll /proc/2850

由下图所示，可以发现攻击者在目录/home/ftpuse创建了一个隐藏目录

![](https://image.3001.net/images/20211203/1638514512_61a9bf50a8863d4ec2717.png!small)进一步查看文件内容

###
![](https://image.3001.net/images/20211203/1638514748_61a9c03ceb02bcd0d13f3.png!small)分析文件启动进程

由于此处文件太长，就不全部展示了

大致分为两个部分

第一部分：

由Base64编码的恶意代码

![](https://image.3001.net/images/20211203/1638515573_61a9c375cb95bef13e809.png!small)

将这部分的代码进行解码，解码发现这部分数据仍然存在加密情况

![](https://image.3001.net/images/20211203/1638515605_61a9c395e423a907139b9.png!small)

通过构造prel脚本，对文件进行解密

    
    
    perl error.pl 

![](https://image.3001.net/images/20211203/1638515684_61a9c3e4a45a55ec9f843.png!small)

（注:这一部分只需要将eval替换为print，就可以使用prel脚本进行解密了）

由上图所示，可以发现木马真实进程为“PS”

并且攻击者的IP为45.9.148.99，ip真实地址为荷兰![](https://image.3001.net/images/20211203/1638515907_61a9c4c3b07ab6f792cf1.png!small)

通过威胁情报平台查看该IP的标签，至此基本断定本次捕获的为批量挖矿代码植入的攻击

![](https://image.3001.net/images/20211203/1638516543_61a9c73fb8f4cb2e0015e.png!small)第二部分：

攻击者的植入了rsa公钥，方便以后免密登录ssh的后门

![](https://image.3001.net/images/20211203/1638516743_61a9c8070a8f954e6df5e.png!small)

### 挖矿木马文件结构分析

从上面的检查过程中可以发现定时任务一共建有5个任务，下面对文件一一进行查看

文件一：

定时任务：1 1 */2 * * /home/ftpuser/.configrc/a/upd>/dev/null 2>&1

路径：/home/ftpuser/.configrc/a/

![](https://image.3001.net/images/20211203/1638518051_61a9cd23dd5c4041d2f90.png!small)先打开文件upd

含义：如果当前进程存在，就清除进程。然后执行/home/ftpuser/.configrc/a/run

![](https://image.3001.net/images/20211203/1638518189_61a9cdad0decb79a5b11a.png!small)

再打开文件run

含义：先判断cpu类型，本机是x86_64所以执行/home/ftpuser/.configrc/a/cron:

![](https://image.3001.net/images/20211203/1638518287_61a9ce0f5ee0c337a95ef.png!small)

文件二：

定时任务：@reboot /home/ftpuser/.configrc/a/upd>/dev/null 2>&1

与上同，重启时生效

文件三：

定时任务：5 8 * * 1 /home/ftpuser/.configrc/b/sync>/dev/null 2>&1

路径：/home/ftpuser/.configrc/b

文件sync

含义：运行真正shell文件是/home/ela/.bashtemp/b/run

![](https://image.3001.net/images/20211203/1638518456_61a9ceb840573525ba38a.png!small)

文件run

含义：执行恶意代码

![](https://image.3001.net/images/20211203/1638518486_61a9ced64ab0afec9c96a.png!small)

文件四：

定时任务：@reboot /home/ftpuser/.configrc/b/sync>/dev/null 2>&1

与上同，重启的时候生效

文件五：

定时任务：#0 */23 * * * /tmp/.X26-unix/.rsync/c/aptitude >/dev/null 2>&1

路径：/tmp/.X26-unix/.rsync/c

文件：aptitude

![](https://image.3001.net/images/20211203/1638518581_61a9cf35a4be798b0421d.png!small)

文件：run

![](https://image.3001.net/images/20211203/1638518665_61a9cf895f19fe0819bb5.png!small)

这里面调用的shell的是golan

golan内容如下:

![](https://image.3001.net/images/20211203/1638518895_61a9d06f08e1488def2c8.png!small)

并且在/tmp目录下发现了

位于/tmp/.X26-unix/木马压缩包

![](https://image.3001.net/images/20211203/1638519249_61a9d1d18465a6e1ff673.png!small)

位于/tmp/.X19-unix/.rsync/initall下的木马安装脚本

含义：

使用bash执行init和init2 文件，通过调用init和init2生成目录并拷贝木马文件到指定目录

![](https://image.3001.net/images/20211203/1638519300_61a9d20430cec1d8b2888.png!small)

文件：init

路径：/tmp/.X19-unix/.rsync/init

![](https://image.3001.net/images/20211203/1638519338_61a9d22a65e53add72e39.png!small)

文件：init2

路径：/tmp/.X19-unix/.rsync/init2

![](https://image.3001.net/images/20211203/1638519366_61a9d2469f7ffc09fc48b.png!small)

## 挖矿木马清除

删除进程

![](https://image.3001.net/images/20211203/1638517409_61a9caa12b84dd1f773e7.png!small)

删除所有定时任务

    
    
    crontab -l -u ftpuser
    crontab -e -u ftpuser
    

![](https://image.3001.net/images/20211203/1638517466_61a9cadae6938a081177a.png!small)

删除.SSH下的文件

![](https://image.3001.net/images/20211203/1638517508_61a9cb040972dc4708d4e.png!small)

删除用户ftpuser下的木马目录

![](https://image.3001.net/images/20211203/1638517537_61a9cb21f04e26b952e83.png!small)

删除用户root下的木马文件

![](https://image.3001.net/images/20211203/1638517574_61a9cb4679da714185933.png!small)

至此就完成了挖矿木马全部清除，但是正常服务器需要排查日志，查看入侵完整路径并及时修补才能结束。

（注:木马文件名与检查的时候有些不同，思路一致）

# 小结

### 挖矿木马介绍

随着虚拟货币的疯狂炒作，挖矿病毒已经成为不法分子利用最为频繁的攻击方式之一。病毒传播者可以利用个人电脑或
服务器进行挖矿，具体现象为电脑CPU占用率高，可使用空间骤降，电脑温度升高，风扇噪声增大等问题。

### 挖矿木马植入途径

  1. 用户没有及时修补漏洞，目前大部分挖矿木马都会通过漏洞传播
  2. SSH等账户弱口令，爆破进入系统
  3. 下载并运行恶意的邮件附件/软件
  4. 用户访问了植入挖矿脚本的网页，浏览器会解析脚本进行挖矿

### 常见检查方式

  1. CPU使用率：普通人通常对挖矿木马的感知就是通过电脑卡顿开始的，正常使用的情况下，使用率到了100%。
  2. 流量特征分析：通过检索流量中的关键字，以此来发现是否存在挖矿行为。通常可以使用Wireshark进行抓包，并通过威胁情报平台来分析的目的IP的安全性。公司推荐使用设备来直接进行防护。

详细报文特征可查看：https://www.freebuf.com/articles/network/195171.html

  3. 杀毒软件的定期全盘扫描公司推荐使用设备来直接进行防护。

### 预防措施

  1. 主机要需要设定强密码，并定期修改，防止因为密码强度不够而被直接爆破
  2. 及时升级系统以及针对新暴露漏洞添加补丁
  3. 定期检查出口的流量和系统的异常进程 

作者 | 一线卑微安服仔

