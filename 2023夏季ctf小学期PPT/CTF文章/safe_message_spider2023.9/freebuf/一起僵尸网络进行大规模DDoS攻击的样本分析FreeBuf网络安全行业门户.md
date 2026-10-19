*****本文原创作者：Sampson，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

##  **一、背景**

 **最近突然发现服务器出现流量异常，十分卡顿，通过top命令查看内存使用情况，发现可疑的进程：**

![1.png](https://image.3001.net/images/20190524/1558675244_5ce77f2c3a24b.png!small)

通过kill -9 pid(116218)命令杀掉后又启动新的进程，名字更换了：

![2.png](https://image.3001.net/images/20190524/1558675530_5ce7804adb553.png!small)

查看etc/crontab定时任务发现定时任务*/3 * * * * root etc/cron.hourly/gcc.sh，每3分钟执行一次以下脚本：

![3.png](https://image.3001.net/images/20190524/1558675540_5ce78054045c6.png!small)

查看gcc.sh脚本，可以看到脚本内容，该脚本的功能是打开网卡，然后启动libudev.so，并启动多个进程来监控libudev.so进程是否被查杀，如果被杀掉了，会再次拷贝libudev.so执行，而且每次启动都会更换进程名，给查杀带来了难度。

##  **二、样本介绍**  

样本基本信息：

**样本名称** | libudev.so  
---|---  
**样本类型** | ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV),
statically linked, for GNU/Linux 2.6.9, not stripped  
**样本大小** | 662840  
**MD5** | 7d44757d809641646e02ab76ed93ede8  
**SHA256** | 0972688711161e347d08ce1c931eb41904fc6f4e4764548e1f14da132a0d1b5d  
**传播方式** | SSH爆破，远程下载执行  
**所属家族** | XorDDoS  
  
## **三、详细分析**

i3306m样本运行后，首先通过get_self调用readlink来获取当前样本的运行路径：

![4.png](https://image.3001.net/images/20190524/1558675627_5ce780ab1c404.png!small)

该样本内置了一个XOR加解密算法，对字符串进行解密：

![5.png](https://image.3001.net/images/20190524/1558675637_5ce780b52c0b0.png!small)XOR解密密钥为“B2FA36AAA9541F0”：

![6.png](https://image.3001.net/images/20190524/1558675647_5ce780bf1a151.png!small)

通过IDA动态调试监听参数a1，获取解密字符串：

![7.png](https://image.3001.net/images/20190524/1558675659_5ce780cbbaeca.png!small)

解密的字符串如下，<http://www.s9xk32c.com/config.rar>为配置文件：

![20.png](https://image.3001.net/images/20190524/1558675799_5ce7815728d18.png!small)

解密出来的linux系统命令如下，这些字符串会在后面用于创建文件、拷贝文件盒系统命令等：

![21.png](https://image.3001.net/images/20190524/1558675928_5ce781d8b7ce1.png!small)

DelService()函数的功能是删除病毒自启动服务，并且删除/etc/rc*.d/
的S90*文件都是指向/etc/init.d/里的启动脚本的软链接，从rc1.d一直到rc5.d。

![22.png](https://image.3001.net/images/20190524/1558679898_5ce7915a0b453.png!small)

创建/usr/bin/，/bin/，/tmp/三个目录。

![8.png](https://image.3001.net/images/20190524/1558675944_5ce781e81f5dd.png!small)

在之前解密出的系统路径/usr/bin/，/bin/，/tmp/下复制自身并执行，并通过在尾部添加10个随机字符的方式，使得自身的hash值每次都不同，用于对抗检查hash值这一类的扫描。

![9.png](https://image.3001.net/images/20190524/1558675963_5ce781fb71d1d.png!small)

AddService()函数代码尝试将自身作为服务写入到系统启动目录下，使每次样本都能随着系统自启动。

![10.png](https://image.3001.net/images/20190524/1558675982_5ce7820ee71d8.png!small)

远程服务器上下载的gcc.sh脚本，写入本地crontab，作为定时任务执行，每3分钟检测程序是否运行，如果不存在就继续执行拷贝并运行。

![11.png](https://image.3001.net/images/20190524/1558675997_5ce7821ddaf6e.png!small)

样本自身还携带了一个rootkit模块，通过HidePidPort、HideFile对端口、文件进行隐藏。

![12.png](https://image.3001.net/images/20190524/1558676004_5ce78224cbc8d.png!small)

然后创建3个线程，分别执行不同的任务：

![13.png](https://image.3001.net/images/20190524/1558676010_5ce7822a7f6a3.png!small)

kill_process线程的功能是监听配置文件config.rar是否下载成功，如果下载完成，读取每行的内容，根据判断条件对相应进程进行查杀。

![15.png](https://image.3001.net/images/20190524/1558676025_5ce7823970c39.png!small)tcp_thread线程的功能是获取受控主机的信息，然后发送回来：

![16.png](https://image.3001.net/images/20190524/1558676032_5ce782405ea34.png!small)

daemon_get_kill_process线程的功能是通过http_download_mem()函数下载配置文件kill_cfg，然后解密配置文件，休眠1800s，继续执行该操作：

![14.png](https://image.3001.net/images/20190524/1558676016_5ce7823049937.png!small)

在tcp_thread线程中，有一个exec_packet函数，控制肉鸡向目标主机发起DDoS攻击，更具不同的参数设置，可以控制肉鸡进行各种威胁操作，包括创建多个线程发起DDoS攻击，下载恶意脚本并执行，发送恶意信息到指定服务器等操作。

![18.png](https://image.3001.net/images/20190524/1558676056_5ce782587b83c.png!small)

样本更新：

![19.png](https://image.3001.net/images/20190524/1558676068_5ce782648481d.png!small)

##  **四、处理以及加固措施**

病毒查杀脚本和加固方法如下：

**![24.png](https://image.3001.net/images/20190524/1558684554_5ce7a38ac19c1.png!small)**

 ***本文原创作者：Sampson，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

