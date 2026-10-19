## 一.前言

最近精力比较充沛，也很久没有跟新了，近期在和大佬一起学习二进制安全，在这里分享一下近期成果。后续会针对海莲花的样本进行一些分享，欢迎各位大佬骚扰、指正。

## 二.分析情况

### 2.1 互斥量

样本MD5: 3C0533706F1F2F9CE1D46658BBC2AA16

创建互斥量：d10a8197-fbc8-4146-80de-ba931f23f05c

![1626227338_60ee428aeb96eac1d676f.png!small?1626227340894](https://image.3001.net/images/20210714/1626227338_60ee428aeb96eac1d676f.png!small?1626227340894)

### 2.2 virtualAlloc函数

利用virtualAlloc函数创建了可执行空间，并利用memmove函数将shellcode复制到开辟的空间当中。

![1626227357_60ee429d4af3be12985ab.png!small?1626227357963](https://image.3001.net/images/20210714/1626227357_60ee429d4af3be12985ab.png!small?1626227357963)

### 2.3 动态调试

拷贝到内存中的shellcode。

![1626227438_60ee42ee1aa6074dd6a5f.png!small?1626227439567](https://image.3001.net/images/20210714/1626227438_60ee42ee1aa6074dd6a5f.png!small?1626227439567)

拷贝完成后，程序将动态写入一个call指令指向shellcode位置，写入地址为：004014A5。

![1626227457_60ee430137fb5a2541d05.png!small?1626227458388](https://image.3001.net/images/20210714/1626227457_60ee430137fb5a2541d05.png!small?1626227458388)

![1626227478_60ee43168ba8822998da2.png!small?1626227480219](https://image.3001.net/images/20210714/1626227478_60ee43168ba8822998da2.png!small?1626227480219)

### 2.4 ExitProcess函数

写入完成后程序调用ExitProcess函数，多次退出后到达修改后的位置，通过第一个call跳转到shellcode当中。

![1626227494_60ee4326a66463ca17639.png!small?1626227495339](https://image.3001.net/images/20210714/1626227494_60ee4326a66463ca17639.png!small?1626227495339)

![1626227506_60ee4332adf1487c43232.png!small?1626227507424](https://image.3001.net/images/20210714/1626227506_60ee4332adf1487c43232.png!small?1626227507424)

该shellcode仅做了一个动作，则是动态的加载dll程序自身。

![1626227524_60ee43442abcf18ded441.png!small?1626227525494](https://image.3001.net/images/20210714/1626227524_60ee43442abcf18ded441.png!small?1626227525494)

完成后再次利用之前写入call指令的位置跳转入dll程序的下一个模块。

![1626227542_60ee43561289c1aba9d25.png!small?1626227542269](https://image.3001.net/images/20210714/1626227542_60ee43561289c1aba9d25.png!small?1626227542269)

该模块主要作用为读取资源块中的shellcode内容，并将内容读取到可执行的内存空间当中。

![1626227557_60ee4365b31dbc7623fc9.png!small?1626227559170](https://image.3001.net/images/20210714/1626227557_60ee4365b31dbc7623fc9.png!small?1626227559170)

![1626227574_60ee4376d80cfe622e47b.png!small?1626227576531](https://image.3001.net/images/20210714/1626227574_60ee4376d80cfe622e47b.png!small?1626227576531)

跳转入shellcode当中。

![1626227587_60ee4383b71a14b863931.png!small?1626227588420](https://image.3001.net/images/20210714/1626227587_60ee4383b71a14b863931.png!small?1626227588420)

### 2.5 LoadLibrary以及GerProcAddress函数

多次利用LoadLibrary以及GerProcAddress函数动态获取需要用到的API函数地址。

![1626227603_60ee4393b14b1901d1b5a.png!small?1626227604638](https://image.3001.net/images/20210714/1626227603_60ee4393b14b1901d1b5a.png!small?1626227604638)

### 2.6 创建svchost.exe进程

获取svchost存放的位置：

![1626227617_60ee43a1923a506863b8c.png!small?1626227618116](https://image.3001.net/images/20210714/1626227617_60ee43a1923a506863b8c.png!small?1626227618116)

创建svchost进程并获取进程id，获取完毕后利用VirualAllocEx函数svchost进程中开辟内存空间并利用WriteProcessMemory向进程注入shellcode。

![1626227634_60ee43b2eb4e0484f1a7e.png!small?1626227636428](https://image.3001.net/images/20210714/1626227634_60ee43b2eb4e0484f1a7e.png!small?1626227636428)

进程PID为0x2384，十六进制转换后进程PID为9092

![1626227655_60ee43c7a4c413bdee760.png!small?1626227656554](https://image.3001.net/images/20210714/1626227655_60ee43c7a4c413bdee760.png!small?1626227656554)

通过信息我们得知，开辟的内存空间地址为0x800000。

![1626227669_60ee43d59aa4d4b29e382.png!small?1626227671204](https://image.3001.net/images/20210714/1626227669_60ee43d59aa4d4b29e382.png!small?1626227671204)

### 2.7 内存列表获取

我们可以通过火绒剑对该进程进行内存列表获取，发现shellcode已注入成功。

![1626227685_60ee43e5d77531c0bbe0c.png!small?1626227686308](https://image.3001.net/images/20210714/1626227685_60ee43e5d77531c0bbe0c.png!small?1626227686308)

跳转到注入的shellcode当中，经过多次循环解密。

![1626227703_60ee43f75eaaab9630cc9.png!small?1626227704285](https://image.3001.net/images/20210714/1626227703_60ee43f75eaaab9630cc9.png!small?1626227704285)

### 2.8 CS连接

最终跳到了CobaltStrike控制，上线模块当中。

![1626227716_60ee4404baa734659d50e.png!small?1626227717193](https://image.3001.net/images/20210714/1626227716_60ee4404baa734659d50e.png!small?1626227717193)

### 2.9 外联地址获取

海莲花C2地址为：185.225.19.22。

![1626227734_60ee44165b36c86fc987f.png!small?1626227734711](https://image.3001.net/images/20210714/1626227734_60ee44165b36c86fc987f.png!small?1626227734711)

![1626227746_60ee4422b09c70f0e35bb.png!small?1626227747256](https://image.3001.net/images/20210714/1626227746_60ee4422b09c70f0e35bb.png!small?1626227747256)

## 三.小结

这里主要针对样本做了简单分析，了解样本存在的行为，后续会陆续更新，欢迎各位大佬骚扰。

