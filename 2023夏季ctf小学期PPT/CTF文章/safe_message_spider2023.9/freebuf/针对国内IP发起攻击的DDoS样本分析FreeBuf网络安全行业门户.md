##  **一、前言**

**![图片1.png](https://image.3001.net/images/20190516/1557987815_5cdd01e7c0c09.png!small)**

**近期光通天下团队捕获到名为stianke_trojan.bak的恶意样本，经过样本初步分析确认该病毒类型Linux.Trojan.Generic.DDos。**

样本md5值等信息如下：

    
    
    MD5：43a5c08bfac85e097b1eceeafaeeec40  
    
    
    SHA-1：9e9680e492bfcdf894bdedc92dc25848f0474f1d
    File Type ELF 
    
    Magic： ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), statically linked, for GNU/Linux 2.2.5, not stripped 
    
    TRiD ELF Executable and Linkable format (Linux) (50.1%) 
    
    ELF Executable and Linkable format (generic) (49.8%) 
    
    File Size 1.17 MB

此次捕获到的病毒家族庞大，变种复杂多样，运用了大量的关键字符加密（动态解密过程）。利用linux特性，感染大量系统文件（高效、非临时性）作为自我保护与持续性攻击的手段。

利用Linux系统原理巧妙伪装与隐藏，被感染服务器植入后门，发动DDos网络攻击，如果被木马植入，将会带来极大的危害及不可预估的损失。

##  **二、行为分析**

观察病毒是否加壳进行了免杀处理，通过查壳并未加壳，如下所示：

![图片2.png](https://image.3001.net/images/20190516/1557987893_5cdd023576d0b.png!small)
图片一：查壳

病毒拖入虚拟机或沙箱进行运行，动态观察病毒对系统恶意行为，如修改配置、网络操作等，对病毒行为结果做到心中有数，如下所示：

![图片3.png](https://image.3001.net/images/20190516/1557987929_5cdd02593cffd.png!small)
![图片4.png](https://image.3001.net/images/20190516/1557988068_5cdd02e40a48c.png!small)图片二：行为监控

##  **三、样本详细分析**

### **（1）样本执行流程分析**

拖入IDA中观察样本的复杂程度如下所示：

![图片5.png](https://image.3001.net/images/20190516/1557988093_5cdd02fdd5379.png!small)图片三：IDA
VIEW

利用字符串交叉引用提取有效的字符串信息，其中提取大量的DDos所攻击的ip（高达300以上），ip源基本都是中国境内的，如下所示：

![图片6.png](https://image.3001.net/images/20190516/1557988113_5cdd0311c4317.png!small)
**** 图片四：目标ip源

定位到病毒入口点，经样本动态调试，执行流程大体如下：

![图片7.png](https://image.3001.net/images/20190516/1557988162_5cdd03421c238.png!small)![图片8.png](https://image.3001.net/images/20190516/1557988162_5cdd03426b1c1.png!small)
![图片9.png](https://image.3001.net/images/20190516/1557988162_5cdd03426f2bf.png!small)
图片五：病毒执行流程

### **（2）动态解密字符串模块**

解密数据赋值给全局变量：

![图片10.png](https://image.3001.net/images/20190516/1557988254_5cdd039eb6cda.png!small)![图片11.png](https://image.3001.net/images/20190516/1557988254_5cdd039eba6da.png!small)
图片六：动态解密数据  

通过字符串动态解密，最后解密出正确的ip域名端口等数据：

![图片12.png](https://image.3001.net/images/20190516/1557988295_5cdd03c77b148.png!small)
图片七：ip/域名/port

最终整理全局变量被赋值的数据，如下所示：

![13.png](https://image.3001.net/images/20190516/1557988379_5cdd041b87217.png!small)![图片13.png](https://image.3001.net/images/20190516/1557988403_5cdd04333ea0b.png!small)
图片八：域名解析

### **（3）MainBeikong模块**

观察执行流程会发现，当病毒第一次执行的时候，g_iGatesType被赋值为1，则必然会进入到该函数，函数分析如下：

![图片14.png](https://image.3001.net/images/20190516/1557988432_5cdd0450303c5.png!small)
图片九：MainBeikong

执行恶意代码，会先killPid与删除“/tmp/bill.lock”，，在启动目录下存在bash，然后还会判断一些文件且删除，保证唯一性（后面还会在创建该文件）。

这时候就用到了前面的全局变量g_strSN(DbSecuritySpt)伪装在init.d与rc目录下，通过查看写入文件数据，是病毒源文件绝对路径。

![图片15.png](https://image.3001.net/images/20190516/1557988474_5cdd047ad77d4.png!small)
图片十：伪装启动源

使用自己封装的函数MkdirPid，创建文件且写入线程文件，我们通过sysdig或者动态执行代码后，追踪恶意行为，这时候创建以全局变量g_strGL(lod)后缀的文件记录Pid如下所示：

![图片16.png](https://image.3001.net/images/20190516/1557988499_5cdd0493221be.png!small)
**** **** 图片十一：写入Pid

MainBeikong函数进入了结尾，函数清理了环境（因为每执行一个函数就会fork()创建新进程，退出当前进程），把自己加入系统服务中，为下一步执行MainBackdoovr做预热准备，如下所示：

![图片17.png](https://image.3001.net/images/20190516/1557988552_5cdd04c8384a5.png!small)
图片十二：MainBeikong

（注：windows使用OD等工具可以在新线程创建回调进行附加下断，也可以在Thread 运行回调时候可以下断，Linux
fork或者processthread配合exit就很难下断新进程，提供思路，使用IDC写脚本修改二进制机器码与汇编指令，达到实现完整的动态调试效果。）

###  **（4）MainBackdoorv模块**

MainBackdoorv函数是病毒中尤为重要一个环节，这里是恶意攻击的执行点，也是重点分析的函数，如下所示：

![图片18.png](https://image.3001.net/images/20190516/1557988618_5cdd050a2b5f2.png!small)
图片十三：MainBackdoorv

该函数会判断是否已存在getty.lock.ak，g_strBDG（selinux）全局变量解密的数据创建的文件，如果不存在则创建该文件且获取全局变量g_strBDSN，selinux针对getty文件，如下所示：  

![图片19.png](https://image.3001.net/images/20190516/1557988643_5cdd0523ed2a6.png!small)
图片十四：selinux伪装

###  **（5）MainProcess模块**

MainProcess包含了C&C通信，自己也构建了服务端，创建了大量的线程（多线程方式），有着良好的线程锁与线程池来控制攻击线程。不同的操作使用了不同封装类来调用对象执行，用this作为参数，而this作为回调函数列表，以指针偏移方式去寻址调用恶意代码，是一个非常复杂的函数，重点分析如下：

![图片20.png](https://image.3001.net/images/20190516/1557988696_5cdd0558537e1.png!small)
图片十五：MainProcess执行流程  

MainProcess先是利用了谷歌公开的服务器更新了域名，网络抓包如图八，这个比较有意思，如下所示：

![图片21.png](https://image.3001.net/images/20190516/1557988728_5cdd057857dde.png!small)
图片十六：InitDnsCache

接着初始化了大量的攻击ip，如图四所示，感染了/usr/lib/libamplify.so动态链接模块，而且初始化了ATK（攻击）模块及this偏移，如下所示：

![图片22.png](https://image.3001.net/images/20190516/1557988763_5cdd059b8cdaa.png!small)图片十七：ATK模块  

动态调试过程中还发现了函数感染了大量的文件，并拥有755的权限，提取被感染的文件名称，如下所示：

![23.png](https://image.3001.net/images/20190516/1557988812_5cdd05cca921b.png!small)**![图片23.png](https://image.3001.net/images/20190516/1557988842_5cdd05ea6aa92.png!small)
** 图片十八：被感染文件 **  
**

线程创建及类Manager调用，使用Socket创建了服务端，用来接收客户端（ip组中返回的数据），Send发送大量的数据如下所示：

![图片24.png](https://image.3001.net/images/20190516/1557988890_5cdd061a55d92.png!small)![图片25.png](https://image.3001.net/images/20190516/1557988890_5cdd061a59eec.png!small)
![图片26.png](https://image.3001.net/images/20190516/1557988890_5cdd061aa0829.png!small)
图片十九：SocketDDos

这个样本比较独特的地方，维护了很多对象，对this指针进行调用列表赋值，作为创建新线程参数传入。在构造函数里进行了初始化，在析构释放执行了部分操作，如下所示：

![图片27.png](https://image.3001.net/images/20190516/1557988936_5cdd0648ce62b.png!small)![图片28.png](https://image.3001.net/images/20190516/1557988936_5cdd0648d0526.png!small)
![图片29.png](https://image.3001.net/images/20190516/1557988936_5cdd0648d7d54.png!small)
图片二十：ObjectRef

最后找到了关键攻击函数ProssMain，封装了各类型的DDoS攻击，如下所示：

![图片30.png](https://image.3001.net/images/20190516/1557988965_5cdd066566db0.png!small)
图片二十一：DDos攻击封装

（Ps：附上一张DDoS攻击状态图（模拟），直观的感受DDoS对服务器带来的性能影响与危害。）

![图片31.png](https://image.3001.net/images/20190516/1557989058_5cdd06c2177c6.png!small)****
图片二十二：DDos攻击感官图

##  **四、恶意域名,IP及被攻击IP整理**

###  **恶意域名:**

Lea.f3322.org 103.73.160.25（中国香港）

###
![微信图片_20190516144529.png](https://image.3001.net/images/20190516/1557989149_5cdd071dd6326.png!small)
**控制端-恶意IP：**

    
    
    130.73.160.25:2500 (德国柏林州柏林)

###  **被攻击IP（331 个,大部分在中国）：**

    
    
     61.132.163.68
    
    202.102.192.68
    
    202.102.213.68
    
    ...
    
    221.7.92.86
    
    221.7.92.98

##  **五、病毒处理及加固措施**

根据病毒的行为与样本分析定性，清理被感染的文件及尝试恢感染的数据，对服务器进行加固，编写伪脚本如下（需要配合实际情况）：

![图片32.png](https://image.3001.net/images/20190516/1557989184_5cdd0740c67cd.png!small)
图片二十三：病毒处理及数据恢复脚本

## **六、总结**

经过病毒的全面分析，入侵系统以后，执行了大量的恶意代码，感染文件、加载内核模块、伪装隐藏等恶意行为，目的发动各种形式的DDos攻击。

单纯的观察行为是很难排查与定位，无法捕获到病毒执行过程与文件数据感染的具体情况。管理人员应该加强安全防范意识，有良好的网络监控服务（如DDos监控）日志审计等，第一时间掌控服务器健康状态，从而及时发现、排查、追踪、定位、分析、处理，将病毒造成的损害降至最低点。

 ***本文作者：光通天下，转载请注明来自FreeBuf.COM**

