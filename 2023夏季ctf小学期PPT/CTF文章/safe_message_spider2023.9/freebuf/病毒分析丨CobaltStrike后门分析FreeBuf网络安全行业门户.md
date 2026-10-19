## 一、概述

Cobalt
Strike是一款非常好用的渗透测试工具，拥有多种协议主机上线方式，集成了提权，凭据导出，端口转发，socket代理，office攻击，文件捆绑，钓鱼等多种功能。同时，Cobalt
Strike还可以调用Mimikatz等其他知名工具，因此广受技术大佬的喜爱，当然在渗透windows主机的过程中，其生成的beacon.exe后门就有相对的使用时机。

![image](https://image.3001.net/images/20221031/1667217621_635fb8d5af8160a58420f.png!small)

## 二、分析

### 2.1 基本信息

  
|  
  
---|---  
文件名| beacon.exe  
文件类型| PE32 executable (GUI) Intel 80386, for MS Windows  
文件大小| 13824 bytes  
SHA1| bc8063d320c9808717003984e01ed76d930eb996  
所属家族| CobaltStrike  
  
### 2.2 程序流程图

![image](https://image.3001.net/images/20221031/1667217760_635fb9602dded487fd14b.png!small)

### 2.3 关键行为分析

#### 2.3.1 创建管道

获取系统时间戳并对0x26AA取余拼接管道名。

![image](https://image.3001.net/images/20221031/1667217855_635fb9bf514629d7520ae.png!small)

创建子线程, 并在线程中创建管道，等待主线程连接管道

![image](https://image.3001.net/images/20221031/1667217862_635fb9c6597d56b3b755f.png!small)

![image](https://image.3001.net/images/20221031/1667217869_635fb9cda7a00ca7839c8.png!small)

#### 2.3.2 主线程解密读取管道中shellcode

主线程睡眠1024毫秒，等待子线程创建完管道，在主线程中用CreateFile函数尝试连接管道。

![image](https://image.3001.net/images/20221031/1667218014_635fba5eec0452493ed00.png!small)

主线程连接管道之后，子线程向管道中写入shellcode，然后退出子线程。

![image](https://image.3001.net/images/20221031/1667218021_635fba65984030525a188.png!small)

主线程读取shellcode, 而后申请内存并解密shellcode，把解密的数据存入刚申请的内存中，并且能够明显看到内存中数据的特征是一个PE文件。

![image](https://image.3001.net/images/20221031/1667218029_635fba6d80ad1e44815d6.png!small)

#### 2.3.3 执行shellcode

样本首先修改shellcode内存属性为可执行。

![image](https://image.3001.net/images/20221031/1667218153_635fbae9611231fa14a60.png!small)

而后创建线程, 在线程中跳转至shellcode。

![image](https://image.3001.net/images/20221031/1667218237_635fbb3d5e319a434bd04.png!small)

#### 2.3.4 与C2服务器通信

获取当前主机各类信息PID及主机名。

![image](https://image.3001.net/images/20221031/1667218437_635fbc054cc917299aca6.png!small)

循环连接C2服务器。

![image](https://image.3001.net/images/20221031/1667218445_635fbc0d2dd2791c9987b.png!small)

第一次连接时向C2服务器发送收集的主机信息，之后向C2服务器发送所下发的指令信息。

![image](https://image.3001.net/images/20221031/1667218491_635fbc3b32b2d42da55d1.png!small)

通过InternetReadFile函数读取服务器指令的hash，并以此来执行不同的指令。

![image](https://image.3001.net/images/20221031/1667218454_635fbc16cd882bef00dc0.png!small)

以下为ls指令的分支，获取当前目录，遍历文件，然后将收集的信息发送给服务器。

![image](https://image.3001.net/images/20221031/1667218504_635fbc48ba86ec8374dd3.png!small)

## 三、总结

Cobalt Strike所生成的后门除了beacon.exe还有很多种类，可以根据场景的不同使用不同的后门，在目前Cobalt
Strike所有的后门都比较活跃，在红蓝对抗中也占据着一席之地，建议提前部署具备高级威胁检测能力的安全产品进行及时监控、防范。

