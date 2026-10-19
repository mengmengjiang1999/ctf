## **家族背景以及现状介绍**  

XorDDoS僵尸网络家族从2014年一直存活至今，因其解密方法大量使用Xor而被命名为XorDDoS，该僵尸网络家族目前活跃程度仍旧较高，主要是攻击者对其C2一直持续进行更新，下图是深信服云脑中对XorDDoS网络请求趋势分析，从访问情况来看较为稳定。  

![图片1.png](https://image.3001.net/images/20191024/1571878890_5db0f7ea2ce7f.png!small)下图为该僵尸网络家族在国内的感染分布图，可以看到主要存在广东以及江浙一带。  

##
![图片2.png](https://image.3001.net/images/20191024/1571878908_5db0f7fc98a4b.png!small)
**防护原理分析**  

深信服安全团队对XorDDos家族的防护原理进行详细分析，并对其做清除处理。主要进程的执行流程如下：  

![图片3.png](https://image.3001.net/images/20191024/1571878965_5db0f83559696.png!small)  

cron.hourly下的bash文件,其中包含了其比较明显的特征名称，曾经出现过以下几种(可能还有更多)

  * /etc/cron.hourly/udev.sh => cp /lib/libgcc4.so /lib/libgcc4.4.so

  * /etc/cron.hourly/gcc.sh => cp /lib/libudev.so /lib/libudev.so.6

  * /etc/cron.hourly/gcc4.sh => cp /lib/libudev4.so /lib/libudev4.so.6

  * /etc/cron.hourly/cron.sh => cp /lib/udev/dev /lib/udev/debug (rootkit 版本, /proc/rs_dev)

  

解密daemonname子串，解密部分其他文章已经做了很详细的分析，解密字符串如下：  

![图片4.png](https://image.3001.net/images/20191024/1571879050_5db0f88a07c50.png!small)![图片5.png](https://image.3001.net/images/20191024/1571879058_5db0f892dc8b3.png!small)然后会执行daemon(1,0)创建守护进程，守护进程的描述如下：  

![图片6.png](https://image.3001.net/images/20191024/1571879079_5db0f8a74a067.png!small)

接下来它会对进程的参数数量做检查，主要包括对2个和3个参数的处理。

如果只有一个参数，会对当前运行文件的路径与/usr/bin/、/bin、/tmp目录做对比，如果不在上述任意一个目录，会进行创建/usr/bin、/bin、/tmp、/lib、/var/run目录，拷贝文件到/lib/libudev4.so(这只是其中一个变种)，然后拷贝自身到/usr/bin、/bin、/tmp下面任意一个目录(名称为10个小写字母随机名，一个成功就不会拷贝到其他目录)，并且变换md5,执行该文件。

![图片7.png](https://image.3001.net/images/20191024/1571879105_5db0f8c1138c0.png!small)![图片8.png](https://image.3001.net/images/20191024/1571879121_5db0f8d10f018.png!small)![图片9.png](https://image.3001.net/images/20191024/1571879129_5db0f8d9a6eeb.png!small)![图片10.png](https://image.3001.net/images/20191024/1571879137_5db0f8e15961f.png!small)这里的LinuxExec实际是dobulefork来创建子进程，然后再次调用execvp来创建一个新进程(2个参数）。  

![图片11.png](https://image.3001.net/images/20191024/1571879161_5db0f8f9b92d7.png!small)![图片12.png](https://image.3001.net/images/20191024/1571879167_5db0f8ff813d8.png!small)

接下来就会删除当前运行的进程的自身文件。

当进程是运行在/usr/bin、/bin、/tmp任意一个目录下的，则会先获取共享内存，获取共享内存成功当前的进程pid写入共享内存。

![图片13.png](https://image.3001.net/images/20191024/1571879207_5db0f9272a48f.png!small)![图片14.png](https://image.3001.net/images/20191024/1571879247_5db0f94f351a2.png!small)![图片15.png](https://image.3001.net/images/20191024/1571879254_5db0f956c14ce.png!small)![图片16.png](https://image.3001.net/images/20191024/1571879263_5db0f95f87362.png!small)然后转到添加服务，这里就是各种启动项以及定时任务。  

![图片17.png](https://image.3001.net/images/20191024/1571879284_5db0f974b9439.png!small)生成一个随机ID，从之前的daemonname中随机挑选一个，然后将这个daemonname放到进程环境变量argv中，就会在系统中将本进程的名称改变，达到迷惑的作用。  

![图片18.png](https://image.3001.net/images/20191024/1571879317_5db0f99554772.png!small)![图片19.png](https://image.3001.net/images/20191024/1571879334_5db0f9a65be2d.png!small)![图片20.png](https://image.3001.net/images/20191024/1571879340_5db0f9acdd9a6.png!small)![图片21.png](https://image.3001.net/images/20191024/1571879348_5db0f9b48f15e.png!small)接下来创建一个daemon_process线程，该线程会检测/var/run/xxx.pid文件；/lib目录下的母体文件，没有检测到母体文件就重新拷贝一份；检测当前进程的文件是否还存在，不存在则将当前进程杀死(这里是一个bug点，后续对清除有很大作用)。  

![图片22.png](https://image.3001.net/images/20191024/1571879392_5db0f9e064b57.png!small)daemon_process进程详细如下：  

![图片23.png](https://image.3001.net/images/20191024/1571879422_5db0f9fe550b7.png!small)继续删除自身文件，重新创建文件和进程，这就是XorDDos进程终止后会被重新拉起的原因。  

![图片24.png](https://image.3001.net/images/20191024/1571879443_5db0fa1398baf.png!small)

>  **rootkit版本**  
>
>
>
> XorDDoS的rootkit模块来源于https://github.com/mncoppola/suterusu项目，但在实际环境中，该模块的安装函数并没有执行，因此未能成功安装。  
>

##  **清除原理**

从分析中知道，会有一个daemon_process线程对文件状态进行检测，文件不存在就将进程杀死，所以在将恶意启动项、定时任务等清除以后，使用chattr对xorddos涉及到的几个目录加锁，然后病毒进程就会自动终止，之后再将被加锁的文件夹恢复。

深信服为广大用户免费提供查杀脚本：

>  **https://edr.sangfor.com.cn/api/download/chk_cln_xorddos.zip**

## 防护建议

 **病毒检测查杀**

深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

>  **https://edr.sangfor.com.cn/api/download/chk_cln_xorddos.zip**

  
**病毒防御**

1、使用深信服安全产品，接入安全云脑，使用云查服务可以即时检测防御新威胁；

2、深信服推出安全运营服务，通过以“人机共智”的服务模式帮助用户快速扩展安全能力，针对此类威胁安全运营服务提供设备安全设备策略检查、安全威胁检查、相关漏洞检查等服务，确保第一时间检测风险以及更新策略，防范此类威胁。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。推荐使用深信服安全感知+防火墙+EDR，对内网进行感知、查杀和防护。

  

