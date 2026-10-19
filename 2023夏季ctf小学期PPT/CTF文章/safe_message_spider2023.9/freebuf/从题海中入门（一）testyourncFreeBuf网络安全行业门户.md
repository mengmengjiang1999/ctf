
    以前学过WEB全家桶，但兜兜转转导师还是领我走到了逆向大门前。想入门PWN，有一丢丢基础，又不知道从哪里入手，索性就想在做题中慢慢入门，于是我把BUUCTF中的题目做了一个难度升序，一题一题总结着开始做。
    

# 工具准备

### checksec

    
    
    不知道为何我在linux 18.04.5 64虚拟机中尝试安装checksec总是出现一下情况：
    

![image](https://image.3001.net/images/20220517/1652770262_628345d6ca68c2c6131b9.png!small)  
在不停换源之后仍无法解决我就直接下载github上的包了：  
`git clone https://github.com/slimm609/checksec.sh`

接下来就是切到其目录下将其拷贝到任意全局bin目录下方便使用：  
![image](https://image.3001.net/images/20220517/1652772537_62834eb9ac9042ecf3728.png!small)  
参考的文章说pwntools自带checksec，我就顺便下载了，但是没找到使用的教程就没用。

## IDA pro

IDA pro我是挂VPN在官网下的，没用网上给的网盘资源，所以在这就给个官网地址☞：[IDA pro下载官网](https://www.hex-rays.com/ida-free/#download)

# 实验流程

## 一、打开[BUUCTF](https://buuoj.cn/challenges)申请靶机和审题

![image](https://image.3001.net/images/20220517/1652773207_628351574e1b86aa334ba.png!small)

### 审题思路

1、根据提示，需要使用nc，nc的全名是netcat，其主要用途是建立和监听任意TCP和UDP连接，支持ipv4和ipv6。因此，它可以用来网络调试、端口扫描等等。  
2、给出了test文件，考虑对文件进行例行检查。

## 二、checksec检测文件保护机制

![image](https://image.3001.net/images/20220517/1652773411_62835223e2af5b53efd05.png!small)  
获取到的信息为：

    
    
    Arch: amd64-64-little（程序架构信息，这是一个64位的程序，就是说可拖进64位IDA）
    Relro：Partial Relro（Relocation Read-Only技术部分开启，这是一项针对于GOT表改写攻击的技术）
    Stack：No Canary found（能栈溢出）
    NX： NX enable（Non-Executable Memory，不可执行内存）
    PIE： PIE enable（Address space layout randomization技术，地址空间布局随机化，通过将数据随机放置来防止攻击的技术）
    

## 三、IDA静态分析

1、将test文件拖入IDA pro  
![image](https://image.3001.net/images/20220517/1652777292_6283614c4c7a84c1c5afc.png!small)  
一眼就看到了图形视图中的/bin/sh和system（以图形的形式比较直观的看到各个函数之间的关系,以汇编的形式展现），盲猜是直接进行了一个system(“/bin/sh”）（汇编学得好就不用盲猜了QAQ），接下来去验证一下。

2、按下f5进行反编译（ida的核心功能可以将汇编语言转换为高级语言）  
![image](https://image.3001.net/images/20220517/1652778386_628365927f57a895c37f2.png!small)  
可以看到确实如猜测的一样，那么直接进靶机去试一试就好了。

## 四、nc连接靶机

![image](https://image.3001.net/images/20220517/1652778512_628366101f4cd948ce726.png!small)  
flag就没藏着，ls查看目录就直接出来了

# 总结

#### checksec的使用

其中各项技术开关的利用在本题没有展现，所以就不展开说了，有兴趣可以☞[checksec工具使用-pwn](https://www.jianshu.com/p/755e52d48a77)

#### IDA pro初步使用

1、初步了解了IDA pro的界面  
2、使用了其反汇编的功能（f5）

#### nc的使用

nc 是 Linux下强大的网络命令行工具，主要用于 TCP、UDP、UNIX域套接字相关的操作。它被设计成可以由其他程序灵活驱动可靠的后台工具，拥有
"瑞士军_刀" 的美称，每个系统管理员都应该掌握它

# 参考文章

[BUUCTF PWN-----第1题:test_your_nc](https://blog.csdn.net/bing_Max/article/details/119947896)  
[checksec安装与使用](https://blog.csdn.net/Little_Small_Joze/article/details/114465018)  
[checksec工具使用-pwn](https://www.jianshu.com/p/755e52d48a77)  
[Pwn---test_your_nc（WP）](https://zhuanlan.zhihu.com/p/386134133)  
[ida
pro使用教程（简略）](https://blog.csdn.net/weixin_49764009/article/details/121068655)

