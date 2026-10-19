## 样本功能

“XOR.DDoS”木马一款经典的linux
dos木马，该木马能够感染32位和64位的Linux系统，通过安装rootkit来隐藏自身，并可通过DDoS攻击形成僵尸网络，该木马首次曝光是在2014年，时隔这么多年该木马依然盛行。

## 样本信息

样本名称：  
0972688711161e347d08ce1c931eb41904fc6f4e4764548e1f14da132a0d1b5d  
样本类型：  
ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), statically linked,
for GNU/Linux 2.6.9, not stripped  
样本大小：  
662840  
MD5  
7d44757d809641646e02ab76ed93ede8  
SHA1  
332f38022f433a472dc5aa6683c9b9ccccf46e0d  
SHA256  
0972688711161e347d08ce1c931eb41904fc6f4e4764548e1f14da132a0d1b5d  
SSDeep  
12288:RBRO1UmJJ0nHgBL9YfJip2qm+x4h1TonHp6y07l7mtBDvnD/u9hMHDB:RBRpmJ+HyL9AiAqm+x4h1mH6wvnDWXMN

## 动态分析

1、查看该病毒类型  
![](https://image.3001.net/images/20220728/1659016579_62e29583f2797ab757bca.png!small)2、网络连接行为  
运行后，通过netstat执行发现，存在一条 103.115.42.70的请求记录，该ip地址归属地为香港  
![](https://image.3001.net/images/20220728/1659016580_62e29584a3f4ec02e77a0.png!small)3、top查看系统进程，发现该异常异常，但是该名称会随机发生变化，每当执行kill会，会有进程名称启动  
![](https://image.3001.net/images/20220728/1659016581_62e2958539d7b48bf9a21.png!small)

## 3.1样本静态分析

1、通过readlink读取程序的当前路径  
![](https://image.3001.net/images/20220728/1659016581_62e29585beffa0528bed4.png!small)调用readlink函数，在函数中调用传入的filename参数，即/proc/self/exe  
![](https://image.3001.net/images/20220728/1659016582_62e295863e83a83850b18.png!small)

备注：readlink定义函数：ssize_t readlink(const char *path, char *buf, size_t
bufsiz);readlink()会将参数path的
符号链接内容存储到参数buf所指的内存空间,linux系统中有个符号链接：/proc/self/exe
它代表当前程序，所以可以用readlink读取它的源路径就可以获取当前程序的绝对路径。具体用法如下

    
    
    #include <unistd.h>  
    #include <stdio.h>  
      
    int main(int argc , char* argv[])  
    {  
    char buf[1024] = { 0 };  
    int n;  
      
    n = readlink("/proc/self/exe" , buf , sizeof(buf));  
    if( n > 0 && n < sizeof(buf))  
    {  
    printf("%s\n" , buf);  
    }  
    }

2、调用dec_conf函数解密字符串  
对main函数进行进一步分析发现，会调用大量dec_conf函数对字符串进行解密  
![](https://image.3001.net/images/20220728/1659016582_62e29586b33d7f02804fe.png!small)跟进dec_conf函数发现，系统主要是利用encrypt_code函数进行解密  
![](https://image.3001.net/images/20220728/1659016583_62e295874749e907e91da.png!small)![](https://image.3001.net/images/20220728/1659016583_62e29587e92f299ccc659.png!small)获取xorkeys为BB2FA36AAA9541F0  
![](https://image.3001.net/images/20220728/1659016584_62e295886c117f260a48a.png!small)

可利用脚本对加密后的参数进行解密

    
    
    key="BB2FA36AAA9541F0"  
    pwd=["m4S4nAC/nA","m4S4nAC/n2_AD","m.[$nFR$7nLQQGF",">#S' RW   X\x1BFTp\a&#Ah\"\\[{ty","*6F6{"]  
    result=list()  
    #pwd为密文  
    def canshu(aa):  
    result = list()  
    for i in range(len(aa)):  
    result.append(chr(ord(aa[i])^ord(key[i % len(key)])))  
    result=''.join(result)  
    print(result)  
      
    for i in range(len(pwd)):  
    canshu(aa=pwd[i])

3、样本自我复制与删除  
通过分析main函数发现，当传入参数argc为2时，样本会自动进行删除  
![](https://image.3001.net/images/20220728/1659016584_62e29588e838333993ad8.png!small)样本进行自我复制，复制到lib/udev/udev目录下  
![](https://image.3001.net/images/20220728/1659016585_62e29589627dcf8868d7b.png!small)4、设置自启动以及定时任务  
AddService函数设置病毒为系统服务并随系统启动而启动  
![](https://image.3001.net/images/20220728/1659016585_62e29589dbaf03072eabb.png!small)

写入本地crontab，作为定时任务执行，每3分钟执行一次cron.sh

![](https://image.3001.net/images/20220728/1659016586_62e2958a636dd602a75c6.png!small)cron.sh具体内容如下  
![](https://image.3001.net/images/20220728/1659016586_62e2958ae022b90a1a9ef.png!small)5、样本通信  
样本a在ddservice函数实现自启动，在函数decrypt_remotestr解密服务器的ip地址，最后开启两个线程调用tcp_thread实现和服务器的通信，并且自身含有rootkit模块，通过HidePidPort、HideFile对端口、文件进行隐藏  
![](https://image.3001.net/images/20220728/1659016587_62e2958b57d77eabdfa96.png!small)tcp_thread线程会依次获取计算机的内核版本，处理器，cpu核数，时钟频率，key，static  
![](https://image.3001.net/images/20220728/1659016587_62e2958bcf4dd400ee38d.png!small)daemondown函数，设置dns通信地址103.25.9.229，并访问url下载数据包，该数据包中包含的用于控制肉鸡进行ddos指令的命令等，再次调用pthread_create，向目标主机发起dos攻击  
![](https://image.3001.net/images/20220728/1659016588_62e2958c6c011c55abe3b.png!small)

## 加固措施

1、首先利用kill -stop pid 挂起父进程；  
2、删除/lib/udev/ 下的udev 和/lib/libedev.so；  
3、删除/etc/cron.hourly下的cron.sh，删除crontab定时任务  
4、删除etc/init.d下的系统启动项；  
5、杀掉挂起的父进程。

## 参考链接

https://www.cnblogs.com/goabout2/p/4888669.html
https://www.freebuf.com/articles/terminal/204444.html

