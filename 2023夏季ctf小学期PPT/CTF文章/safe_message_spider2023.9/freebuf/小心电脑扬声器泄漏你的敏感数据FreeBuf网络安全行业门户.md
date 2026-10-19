**近期，来自以色列本古里安大学的安全研究人员向外界演示了一种名叫“Mosquito”（蚊子攻击）的攻击技术，而这种攻击技术将允许攻击者通过扬声器或耳机从物理隔离（空气间隙）或联网计算机中提取数据。**

![小心电脑扬声器泄漏你的敏感数据](https://image.3001.net/images/20180326/15219998603318.png!small)  

研究人员在这份标题为《[Mosquito攻击：空气间隙计算机之间的隐蔽通信](https://arxiv.org/pdf/1803.03422.pdf)》的研究报告中解释称，这种攻击方法的隐蔽性非常高，它可以通过扬声器的超声波信号来发送和接收数据。这项技术可以将音频输出插孔转换成输入插孔，然后再将扬声器转换为麦克风。这是现代音频芯片组的一种功能，也可以说是一种特性，并且可以通过软件来实现转换。但是，攻击者也可以通过特殊制作的恶意软件来利用这种功能，然后将目标主机的扬声器或耳机转换成麦克风，并通过超声波信号完成两台计算机设备之间的数据提取（最远距离为9米左右）。

![小心电脑扬声器泄漏你的敏感数据](https://image.3001.net/images/20180326/15219998696744.png!small)  

研究人员Mordechai Guri、Yosef Solwicz、Andrey Daidakulov和Yuval
Elovici还设计出了另一种专门针对空气间隙系统的数据提取技术，其中包括：

> 1\. Odini：利用的是CPU核心所生成的低频磁信号；
>
> 2\. Magneto：利用磁信号将空气间隙系统中的数据提取到附近的智能手机中；
>
> 3\. LED-it-Go：利用发光二极管（LED）从空气间隙网络中提取数据；
>
> 4\. aIR-Jumper：使用红外LED和安全监控摄像头与空气间隙网络进行远程通信；
>
> 5\. BitWhisper：利用目标主机中CPU/GPU的温度变化来与附近的空气间隙系统进行通信；

研究人员解释称，在Mosquito攻击中其实麦克风并不是必备组件之一，因为他们所开发的恶意软件可以利用特定音频芯片组中的功能来将已连接的扬声器（输出设备）转换成麦克风（输入设备）。

TrendLabs针对联网扬声器的安全研究报告请点击【[这里](https://blog.trendmicro.com/trendlabs-security-intelligence/iot-devices-need-better-builtin-security/?_ga=2.248644175.970272830.1521871746-301581273.1521599907)】获取。

### 演示视频：“攻击者如何利用联网扬声器窃取你的数据”

看不到？点[这里](https://v.qq.com/x/page/j0614m3bnrb.html)

目前Mosquito攻击仍处于试验阶段，但是就现在的实验结果来看，当前几乎所有的平台都会受到这种安全风险的影响，尤其是物联网设备，而这种安全漏洞将有可能把个人数据甚至是整个企业的数据进一步暴露在网络威胁之下。除此之外，趋势科技前沿威胁研究团队（FTR）的Stephen
Hilt还对[当前最流行的两款扬声器系统](https://documents.trendmicro.com/assets/pdf/The-Sound-of-a-Targeted-Attack.pdf)进行了分析，并且成功利用Mosquito攻击从目标系统中提取出了数据。这也就意味着，目前很多运行在企业环境中的计算机/网络系统都将会暴露在这种安全风险之中。

实际上，这两项研究结果表明，安全问题不应该是一个“事后”才去思考的事情。就目前的网络安全形势来看，无论是个人用户、企业或在线服务提供商，还是[设备设计商/制造商](https://blog.trendmicro.com/trendlabs-security-intelligence/internet-things-ecosystem-broken-fix/?_ga=2.19345008.970272830.1521871746-301581273.1521599907)，都应该对自己所使用的软件或硬件部署多层安全防护。

 ***
参考来源：[trendmicro](https://www.trendmicro.com/vinfo/us/security/news/vulnerabilities-and-exploits/mosquito-attack-shows-how-malware-can-exfiltrate-data-via-pc-speakers)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

