## 1 内容简介

Nmap是一款流行的网络扫描软件，有着强大的功能，包括主机发现、端口扫描、操作系统识别、服务识别、traceroute、dns解析、漏洞扫描、暴力破解等，这使它成为了安全研究员的必备武器之一，但是许多研究员使用Nmap扫描的速度并不理想，甚至有时可以说是很慢，本文就带你从Nmap的源码出发，并结合实验验证，挖掘Nmap扫描性能方面的内在逻辑，探索提升Nmap性能的路径。  
本文主要涉及主机、端口扫描、操作系统识别、服务版本识别扫描，关于脚本扫描的性能未涉及。

## 2 nmap扫描基本实现简介

在了解Nmap关于扫描性能方面细节之前，我们需要知道一些Nmap如何实现主机、端口、操作系统识别、服务识别的基本技术。懂的都懂，端口扫描常用到半开放式扫描技术，这样可以提升扫描速度和减少IO消耗，比如tcp端口开发扫描常使用syn扫描，而对于服务版本识别这种基于TCP握手的扫描，则只能建立完整TCP握手后再发包，再提取回复中的关键字识别服务的版本。Nmap也是如此。

##### 2.1 无TCP连接的扫描

对于主机发现、端口扫描、操作系统识别nmap使用无TCP连接的扫描（端口可能是udp，和此类似），主机发现使用arp、icmp协议，端口扫描使用tcp的syn、ack、fin等，操作系统识别则是直接从tcp层构造cookie、tcp
id、option等根据回复特征以完成识别，这几个技术都有个共同点就是只需要发一次包收一次包即可完成识别，所以nmap都使用了`send()`来发包，然后pcap设置规则收包。

##### 2.2 TCP连接的扫描

对于tcp
connect扫描和服务版本识别nmap就需要进行完整tcp连接，就要采用其他的提升扫描速度的技术了，因为nmap是单线程扫描，可以说仅使用单线程nmap能把扫描性能做到目前这样已经是很强了。nmap对于tcp
connect扫描使用select设置超时来实现。对于服务版本识别这种基于tcp的应用层扫描，则使用epoll，传入超时时间和执行应用层交互的回调函数来实现。

## 3 nmap中无TCP连接的扫描性能分析

### 3.1 实验

 **实验** : 先看一个实验，我们使用nmap默认参数对256个IP的100个端口进行端口扫描，看下时间：

![image](https://image.3001.net/images/20221209/1670583841_63931621aefad7936cc51.png!small)  
![image](https://image.3001.net/images/20221209/1670583850_6393162a0a2fee3da08d9.png!small)

可以看到花了11秒。显然这个时间是比较长的，如果使用自己写的扫描器，我们每秒发包可以超过30000个，把所有端口进行一次发包总共时间为100*256/30000=0.85，设置1秒的等待（内网中等待一秒远远足够，nmap使用等待比这个低很多），然后重试一次，那么总共时间不超过（0.85+1）*2
=3.7秒。

通过wireshark抓包看下nmap发包速率怎样：

![image](https://image.3001.net/images/20221212/1670814043_6396995bda4dc85a06c2d.png!small)  
![image](https://image.3001.net/images/20221212/1670814056_6396996829e0a7d6023fb.png!small)

看到nmap只向目标网段发送了七千多个包，而不是预计的100*256个包，这是因为nmap在端口扫描前会先进行主机发现探测，如果发现这个主机不在线那么就不会发起端口扫描：

![image](https://image.3001.net/images/20221212/1670814082_639699827144f4c49e114.png!small)

比如上图筛选的这个IP就没有发起端口扫描（80、443是主机发现的策略）（当然这样会带来一个问题，如果一个主机禁了ICMP并且没有开启80和443，但开启了其他端口，那么就会被漏掉）。就如这样比较节省流量的扫描方式依然耗时11秒，nmap这中间经历了什么是让人好奇的。

### 3.2 源码分析

就如我们所知，端口扫描技术的性能，无非就在于发包速度、发包间隔、收包超时、收包处理速度、重试次数、网卡带宽、网络拥塞度等，这些因素在nmap源码中都有体现，而且体现的可以说有些智能。

定位nmap主机发现、端口扫描分组循环处代码，位于`nmap_main()`->`ultra_scan()`:

    
    
    ......
      while (!USI.incompleteHostsEmpty()) {
        doAnyPings(&USI);
        doAnyOutstandingRetransmits(&USI); // Retransmits from probes_outstanding
        /* Retransmits from retry_stack -- goes after OutstandingRetransmits for
           memory consumption reasons */
        doAnyRetryStackRetransmits(&USI);
        doAnyNewProbes(&USI);
        gettimeofday(&USI.now, NULL);
        // printf("TRACE: Finished doAnyNewProbes() at %.4fs\n", o.TimeSinceStartMS(&USI.now) / 1000.0);
        printAnyStats(&USI);
        waitForResponses(&USI);
        gettimeofday(&USI.now, NULL);
        // printf("TRACE: Finished waitForResponses() at %.4fs\n", o.TimeSinceStartMS(&USI.now) / 1000.0);
        processData(&USI);
    
        ......
      }
      ......
    

从函数名称就可以看出它的大致过程：一个分组USI对象，先ping，如果有会尝试重传，再发起探测发包，然后等待收包，最后处理本次更新的数据。当所有端口都扫完，就退出切换下一个分组。

其中`doAnyNewProbes()`就是进行端口扫描的函数，以此举例分析，主机发现的ICMP发包是在`doAnyPings(&USI)`中，所有无TCP连接扫描的性能逻辑大致一致。

    
    
    static void doAnyNewProbes(UltraScanInfo *USI) {
      HostScanStats *hss, *unableToSend;
      gettimeofday(&USI->now, NULL);
      unableToSend = NULL;
      hss = USI->nextIncompleteHost();
      while (hss != NULL && hss != unableToSend && USI->gstats->sendOK(NULL)) {
        if (hss->freshPortsLeft() && hss->sendOK(NULL)) {
          ultrascan_host_timeout_init(USI, hss);
          sendNextScanProbe(USI, hss);
          unableToSend = NULL;
        } else if (unableToSend == NULL) {
          unableToSend = hss;
        }
        hss = USI->nextIncompleteHost();
      }
    }
    

在这可以看到，每个主机对象hss在进行`sendNextScanProbe`发包前会进行一次判断，主要是`sendOK()`和`freshPortsLeft()`，后者显然就是判断是否还存在待发包的端口，而两个`sendOK()`里面有什么，经过我的实验在端口扫描阶段`hss->sendOK()`非常频繁的返回了
false。

    
    
    bool HostScanStats::sendOK(struct timeval *when) {
      ......
      //判断当前主机是否超时
      if (target->timedOut(&USI->now) || completed()) {
        ......
      }
      ......
    
      //是否达到最小发包速率
      if (o.min_packet_send_rate != 0.0) {
        ......
      }
    
      //是否通过速度现在检测
      if (rld.rld_waiting) {
        ......
      }
    
      //是否满足发包延迟要求
      if (sdn.delayms) {
        ......
      }
    
      //主要判断是否发生TCP拥塞避免
      getTiming(&tmng);
      if (tmng.cwnd >= num_probes_active + .5 &&
          (freshPortsLeft() || num_probes_waiting_retransmit || !retry_stack.empty())) {
        ......
      }
    
      if (!when)
        return ...
    
      TIMEVAL_MSEC_ADD(earliest_to, USI->now, 10000);
      return ...
    }
    

这是`HostScanStats::sendOK()`简略代码，可以看到每次发一个包前nmap都会作这些判断，其实就是这些判断决定了nmap发包速度。经过分析，这些函数所判断的条件主要就是：判断当前主机是否超时、是否达到最小发包速率、是否通过速度限制检测、是否满足发包延迟要求、是否拥塞。

接下来我们依次来看看这些判断条件的值究竟是从哪里来的，代表着怎样的实际含义，能不能通过nmap扫描参数设置来影响它们，影响它们会带来什么变化。

#### 3.2.1 主机超时

`target->timedOut`看声明注释：

    
    
    /* Returns whether the host is timedout.  If the timeoutclock is
         running, counts elapsed time for that.  Pass NULL if you don't have the
         current time handy.  You might as well also pass NULL if the
         clock is not running, as the func won't need the time. */
    bool Target::timedOut(const struct timeval *now) {
      unsigned long used = htn.msecs_used;
      struct timeval tv;
    
      if (!o.host_timeout) return false;
      if (htn.toclock_running) {
        if (now) tv = *now;
        else gettimeofday(&tv, NULL);
        used += TIMEVAL_MSEC_SUBTRACT(tv, htn.toclock_start);
      }
    
      return (used > o.host_timeout);
    }
    

它就是字面意思，一台主机超时时间。也就是说，如果 nmap
花在这台主机上的时间超过`host_timeout`全局变量中的值就会终止对它的后续扫描。没错，nmap 扫描的性能参数中有一个`--host-timeout`的参数，我们如果指定它为1秒，那么一秒后这台主机无论能扫出什么数据都会不再继续，包括进行服务版本探测。可以说这是比较暴力的，特别是对于进行完整TCP连接的服务版本探测。

 **实验** ：

![image](https://image.3001.net/images/20221212/1670814425_63969ad9423c36d484979.png!small)  
![image](https://image.3001.net/images/20221212/1670814433_63969ae1656a147186901.png!small)

指定进行服务版本探测，最多时间3秒钟，然后三秒之后就立即停止了，并且甚至连前面的端口扫描都没有完成，除了发现了主机在线，没有输出任何后续扫描结果。

用户没设置时默认为0，也就不构成影响。

#### 3.2.2 最小/最大发包速率

    
    
    /* The requested minimum packet sending rate, or 0.0 if unset. */
      float min_packet_send_rate;
    

全局变量 min_packet_send_rate，也没错，它和nmap扫描参数`--min-rate`对应，还有一个`--max-rate`,分别表示用户要求的发包最小最大速度，这是两个强硬指标参数。

  * 对于最小发包速率，不管网卡带宽，网卡拥塞程度，nmap会按照自己的计时不顾其他条件（比如设置的发包延迟）来满足这个要求，除非`--min-rate`设置太大，cpu和IO跟不上无法满足。

  * 对于最大发包速率，可以理解为nmap直接按计时来控制发包速度不超过这个值，在上面函数中没有这个条件判断，但其实它在`doAnyNewProbes`的另一个发包判断条件中：`USI->gstats->sendOK(NULL)`，在这不贴出函数源码，和`hss->sendOK(NULL)`不一样的是，前者针对于一个分组（里面可能有多个主机），后者针对单个主机。在`doAnyNewProbes`中先判断一个分组发包是否满足发包要求，再判断单个主机发包是否满足要求。

这是用户指定参数，没设置时默认为0，也就不构成影响。

##### 3.2.2.1 最小发包速率实验

我们就拿前面的例子做对比实验，对前面实验的256个IP的100个端口进行扫描：

![image](https://image.3001.net/images/20221212/1670814493_63969b1d96605c12599aa.png!small)

![image](https://image.3001.net/images/20221212/1670814504_63969b28c5b420882dc5b.png!small)  
一秒钟完成了7000多个包的扫描。设置为50000时这个时间又缩短了点，但再往后变大，这个时间就不变了，因为已经达到了IO最大限度：

![image](https://image.3001.net/images/20221212/1670814518_63969b36e1f9a254d0138.png!small)

![image](https://image.3001.net/images/20221212/1670814538_63969b4a3f77e6386dac8.png!small)

##### 3.2.2.2 最大发包速率实验

再试试最大发包速率，设置为500

![image](https://image.3001.net/images/20221212/1670814578_63969b72c6b14566b406b.png!small)

![image](https://image.3001.net/images/20221212/1670814588_63969b7cae032277f246e.png!small)

前面需要11秒，现在是14秒这两个时间是很稳定的，可见最大发包速率拖延了整体扫描进度。

#### 3.2.3 速率限制检测

条件`rld.rld_waiting`，查看声明：

    
    
    /* To test for rate limiting, there is a delay in sending the first packet
       of a certain retransmission number.  These values help track that. */
    struct rate_limit_detection_nfo {
      unsigned int max_tryno_sent; /* What is the max tryno we have sent so far (starts at 0) */
      bool rld_waiting; /* Are we currently waiting due to RLD? */
      struct timeval rld_waittime; /* if RLD waiting, when can we send? */
    };
    

看这里我没有太理解它的意思，再看看`rld_waittime`的值来源，在`doAnyOutstandingRetransmits()`中：

    
    
    do {
            probeI--;
            probe = *probeI;
            if (probe->timedout && !probe->retransmitted &&
                maxtries > probe->tryno && !probe->isPing()) {
              /* For rate limit detection, we delay the first time a new tryno
                 is seen, as long as we are scanning at least 2 ports */
              if (probe->tryno + 1 > (int) host->rld.max_tryno_sent &&
                  USI->gstats->numprobes > 1) {
                host->rld.max_tryno_sent = probe->tryno + 1;
                host->rld.rld_waiting = true;
                TIMEVAL_MSEC_ADD(host->rld.rld_waittime, USI->now, 1000);
              } else {
                host->rld.rld_waiting = false;
                retransmitProbe(USI, host, probe);
                retrans++;
              }
              break; /* I only do one probe per host for now to spread load */
            }
          } while (probeI != host->probes_outstanding.begin());
    

最后理解了，它就是当探测一个单位（一个ip的一个端口就为一个探测单位）未响应而进入重传时，就会等待1秒再发起，可能就是为了避开未响应时的网络拥塞。我们抓包完全可以看出来：

 **实验** ：

![image](https://image.3001.net/images/20221212/1670814616_63969b9891c5792ed899b.png!small)

![image](https://image.3001.net/images/20221212/1670814626_63969ba25f7e49f943c59.png!small)

![image](https://image.3001.net/images/20221212/1670814646_63969bb6a425c7d3b261b.png!small)

![image](https://image.3001.net/images/20221212/1670814664_63969bc85b256a3c405bd.png!small)

#### 3.2.4 发包延迟

`sdn.delayms`这个条件就是对两个探测包`send()`间隔时间，即发包延迟。查看声明：

    
    
    struct send_delay_nfo {
      unsigned int delayms; /* Milliseconds to delay between probes */
      ......
    };
    

注释也说明了它的含义，我们还原下`HostScanStats::sendOK()`中判断`sdn.delayms`处的原始代码：

    
    
    bool HostScanStats::sendOK(struct timeval *when) {
      struct ultra_timing_vals tmng;
      std::list<UltraProbe *>::iterator probeI;
      struct timeval probe_to, earliest_to, sendTime;
      long tdiff;
    
      ......
      if (sdn.delayms) {
        if (TIMEVAL_MSEC_SUBTRACT(USI->now, lastprobe_sent) < (int) sdn.delayms) {
          if (when) {
            TIMEVAL_MSEC_ADD(*when, lastprobe_sent, sdn.delayms);
          }
          return false;
        }
      }
      ......
      return false;
    }
    

可以看到这里做了时间判断只有当`sdn.delayms`达到要求时间是才会返回true允许探测包发送，我经过加入日志方式验证了确实如此当`sdn.delayms`被设置为1秒时，会多次重上面判断处返回false，并且抓包记录中看到探测包之间间隔时间大致就是一秒。

这个发包延迟的值是从何而来，跟踪代码可以看到`sdn.delayms`是被初始化为全局变量`o.scan_delay`的，而`o.scan_delay`就是nmap扫描参数`--scan-delay`所设置的。

这个值在默认下为0也就说说探测包之间默认不等待。但是发包延迟完全有可能在扫描过程中在一定条件下变成有发包延迟值了：

当收到新数据包时`ultrascan_port_probe_update`一定会被数据处理循环调用以更新端口数据，如果这个探测回复包带来了最大重传成功次数变化
（下面会讲到），并且这个次数大于3或者4（当用户使用`-T4`参数时是4，`T3`参数时是3） ，就会调用`void
HostScanStats::boostScanDelay()`，这个函数改变了发包延迟，可以大致理解为一个端口竟然需要三四次重传才能得到有效回复，所以nmap认为应该降低下发包速度了。

    
    
    void HostScanStats::boostScanDelay() {
      unsigned int maxAllowed = USI->tcp_scan ? o.maxTCPScanDelay() :
                                USI->udp_scan ? o.maxUDPScanDelay() :
                                o.maxSCTPScanDelay();
      if (sdn.delayms == 0)
        sdn.delayms = (USI->udp_scan) ? 50 : 5; // In many cases, a pcap wait takes a minimum of 80ms, so this matters little :(
      else sdn.delayms = MIN(sdn.delayms * 2, MAX(sdn.delayms, 1000));
      sdn.delayms = MIN(sdn.delayms, maxAllowed);
      sdn.last_boost = USI->now;
      sdn.droppedRespSinceDelayChanged = 0;
      sdn.goodRespSinceDelayChanged = 0;
    }
    

还要先提下另一个扫描参数`--max-scan-delay`，这个参数其实就是分别将全局`o.max_tcp_scan_delay`、`o.max_udp_scan_delay`、`o.max_sctp_scan_delay`设置为参数值，如果不使用`--max-scan-delay`设置那么这三个全局变量的值都默认为1秒，然后如上面代码所示，函数开头根据当前端口协议确定`maxAllowed`然后和发包延迟一起计算新的发包延迟，可以大致理解下这个计算的意思就是，会把发包延迟从0调整为5、50、500以上的某个值。

#### 3.2.5 拥塞窗口

##### 3.2.5.1 拥塞窗口机制和计算

发包延迟后面的源码是如下判断：

    
    
    struct ultra_timing_vals tmng;
    getTiming(&tmng);
    if (tmng.cwnd >= num_probes_active + .5 &&
          (freshPortsLeft() || num_probes_waiting_retransmit || !retry_stack.empty())) {
        if (when)
          *when = USI->now;
        return true;
    }
    

从`getTiming()`中取一个计时对象，判断里面的cwnd和当前正在活动的探测包数量`num_probes_active`作比较，并且判断当前该主机是否存在待发送的探测包。先看看它的声明和注释：

    
    
    /* Based on TCP congestion control techniques from RFC2581. */
    struct ultra_timing_vals {
      ......
      double cwnd; /* Congestion window - in probes */
      ......
    };
    

留意到结构体的注释 RFC2581，这里介绍一个TCP拥塞控制理论，沿用百度的解释：

 **Congestion window** （拥塞窗口），它是卫星通信在因特网中防止通信拥塞的一种措施，它是在发端采用了一种 **Congestion
avoidance** （拥塞避免）算法和 **Slow start**
（慢速启动）算法相结合的机制。“拥塞窗口”就是“拥塞避免”的窗口，它是一个装在发送端的可滑动窗口，窗口的大小是不超过接收端确认通知的窗口。“慢速启动”是在连接建立后，每收到一个来自收端的确认，就控制窗口增加一个段值大小，当窗口值达到“慢速启动”的限值后，慢速启动便停止工作，避免了网络发生拥塞。

如果对这个机制不了解的可以自己去查查，简单的说就是，TCP一开始不发送大量的数据，先探测一下网络的拥塞程度，然后由小到大逐渐增加拥塞窗口的大小，为了方便后面有时会把拥塞窗口简写为`cwnd`，接下来我们看看nmap怎么在发包中体现拥塞窗口思想的。

 **实验** :

先做一个实验，看看这个拥塞窗口对发包到底有多大影响，我们在拥塞窗口判断前日志输出拥塞窗口大小和活动探测包数量，再将函数`sendOK()`返回值打出来:

![image](https://image.3001.net/images/20221212/1670814788_63969c44000eab8806589.png!small)

![image](https://image.3001.net/images/20221212/1670814816_63969c6078c4bc284205f.png!small)

为了展示拥塞窗口对发包的影响，我找了一个主机存活但端口均被防火墙过滤掉了的主机，扫1000个默认端口：

![image](https://image.3001.net/images/20221212/1670814832_63969c705d74e1d1172a7.png!small)

![image](https://image.3001.net/images/20221212/1670814843_63969c7b3c7ddb62a7000.png!small)

结果扫了21秒，如果我们找一个有部分端口开放的主机，仅仅用了5秒钟。

![image](https://image.3001.net/images/20221212/1670814914_63969cc2bb04086d81f0d.png!small)

来看看增加的输出的日志：

![image](https://image.3001.net/images/20221212/1670814928_63969cd043f4b74c01703.png!small)

第一个循环，当 num_probes_active 将超出 cwnd 时就`sendOK()`就返回
false了,而一旦`sendOK()`返回false，那么外层`doAnyNewProbes()`就会放弃对这个主机的扫描而等待下个大循环才再进入，我又观察了后面的日志发现一直到扫描结束
num_probes_active
都被cwnd限制为10以下：![image](https://image.3001.net/images/20221212/1670814944_63969ce0624ebea0461b5.png!small)

也就是说
nmap发包循环从分组中取出我们目标主机后，本来有上千个探测包要一次性发送，但仅仅发了不到10个然后就进入了收包等待，这肯定是非常影响效率的，我们从抓包中也可以看到1000个端口正好2000个包，用时20多秒：

![image](https://image.3001.net/images/20221212/1670814958_63969cee3848518897b79.png!small)

而另外一个有部分端口开发的主机就不一样了，它的cwnd从开始的10慢慢增加到了75，并且每次循环中明显发包数量明显成倍的多了：

![image](https://image.3001.net/images/20221212/1670814973_63969cfd6efffdc3db917.png!small)

所以从实验现象上可以初步推测：主机的响应程度可能会影响拥塞窗口，进而影响了发包速度。

现在继续回到源码，进入`getTiming(&tmng)`看下nmap如何来计算这个cwnd的 ：

    
    
    void HostScanStats::getTiming(struct ultra_timing_vals *tmng) {
      assert(tmng);
    
      /* Use the per-host value if a pingport has been found or very few probes
         have been sent */
      if (target->pingprobe.type != PS_NONE || numprobes_sent < 80) {
        *tmng = timing;
        return;
      }
    
      /* Otherwise, use the global cwnd stats if it has sufficient responses */
      if (USI->gstats->timing.num_updates > 1) {
        *tmng = USI->gstats->timing;
        return;
      }
    
      /* Last resort is to use canned values */
      tmng->cwnd = USI->perf.host_initial_cwnd;
      tmng->ssthresh = USI->perf.initial_ssthresh;
      tmng->num_updates = 0;
      return;
    }
    

大致解读下它的意思，当扫描类型不为ping并且向主机发送探测包低于80个时，使用该主机数据中的timing对象，否则当分组中收到至少一个有效包就使用分组中的timing对象，否则使用分组中全局初始化值。

我们先看看主机对象初始化和分组对象初始化时timing对象都初始化为了什么，从 timing.cc: 336行找到了它的初始化值：

    
    
    /* Do initialization after the global NmapOps table has been filled in. */
    void scan_performance_vars::init() {
      low_cwnd = o.min_parallelism ? o.min_parallelism : 1;
      max_cwnd = MAX(low_cwnd, o.max_parallelism ? o.max_parallelism : 300);
      group_initial_cwnd = box(low_cwnd, max_cwnd, 10);
      host_initial_cwnd = group_initial_cwnd;
       slow_incr = 1;
      /* The congestion window grows faster with more aggressive timing. */
      if (o.timing_level < 4)
        ca_incr = 1;
      else
        ca_incr = 2;
      cc_scale_max = 50;
      initial_ssthresh = 75;
      ......
    }
    

扫描并行度`o.min_parallelism`和`o.max_parallelism`是可以通过 nmap参数`--min-parallelism`和`--max-parallelism`来设置的，如果都没有设置那么通过上面盒子计算出来的`group_initial_cwnd`就应该是10，然后在scan_engine.cc:1334的`init_ultra_timing_vals()`函数中初始化给了主机或者分组的`timing->cwnd`：

    
    
    timing->cwnd = (utt == TIMING_HOST) ? perf->host_initial_cwnd : perf->group_initial_cwnd;
    

这也就是上面看到的日志中，两个主机的cwnd一开始都是10的来源了。那么既然实验中第二台主机被扫时cwnd增加到了75又是怎么增加上去的呢？追踪代码我们找到了：scan_engine.cc:1649

    
    
    /* Adjust host and group congestion control variables (struct ultra_timing_vals)
       and host send delay (struct send_delay_nfo) based on a received packet. Use
       rcvdtime == NULL to indicate that you have given up on a probe and want to
       count this as a DROPPED PACKET. */
    static void ultrascan_adjust_timing(UltraScanInfo *USI, HostScanStats *hss,
                                        UltraProbe *probe,
                                        struct timeval *rcvdtime) {
      ......
    
      /* Increase the window for a positive reply. This can overlap with case (1)
         above. */
      if (rcvdtime != NULL) {
        USI->gstats->timing.ack(&USI->perf, ping_magnifier);
        hss->timing.ack(&USI->perf, ping_magnifier);
      }
      ......
    }
    

这里同时更新了分组和主机的timing对象：

    
    
    /* Update congestion variables for the receipt of a reply. */
    void ultra_timing_vals::ack(const struct scan_performance_vars *perf, double scale) {
      num_replies_received++;
    
      if (cwnd < ssthresh) {
        /* In slow start mode. "During slow start, a TCP increments cwnd by at most
           SMSS bytes for each ACK received that acknowledges new data." */
        cwnd += perf->slow_incr * cc_scale(perf) * scale;
        if (cwnd > ssthresh)
          cwnd = ssthresh;
      } else {
        /* Congestion avoidance mode. "During congestion avoidance, cwnd is
           incremented by 1 full-sized segment per round-trip time (RTT). The
           equation
             cwnd += SMSS*SMSS/cwnd
           provides an acceptable approximation to the underlying principle of
           increasing cwnd by 1 full-sized segment per RTT." */
        cwnd += perf->ca_incr / cwnd * cc_scale(perf) * scale;
      }
      if (cwnd > perf->max_cwnd)
        cwnd = perf->max_cwnd;
    }
    

注意这里有一个`ssthresh`变量对应两个处理规则，查看声明：

    
    
    int ssthresh; /* The threshold above which mode is changed from slow start
                       to congestion avoidance */
    

这就是前面说到的拥塞窗口机制从慢启动到拥塞避免模式的阀值了，在`scan_performance_vars::init()`中被设置为75了，最后还有一个最大值。两个分支下的拥塞窗口分别是怎么计算的：

  * 慢启动模式下。`perf->slow_incr`也就是前面`scan_performance_vars::init()`中初始化的为1，`cc_scale(perf)`：

    
    
    /* Returns the scaling factor to use when incrementing the congestion
       window. */
    double ultra_timing_vals::cc_scale(const struct scan_performance_vars *perf) {
      double ratio;
      assert(num_replies_received > 0);
      ratio = (double) num_replies_expected / num_replies_received;
      return MIN(ratio, perf->cc_scale_max);
    }
    

也就是说`cc_scale`计算的是 （待收包总量/已收包总量）和50的较小值。`scale`的值在非ping扫描时是初始化的1。  
这三者的乘积表达的意思大概就可以理解为，所发探测包中，收到回复越稀少，那么单个收包带来的拥塞窗口增长值就越大，但不是完全没有响应因为这样是进入拥塞窗口调整的条件需要是收到有效数据包。

  * 拥塞避免模式下。一开始时默认都是10的cwnd也就是慢启动模式，随着扫描推进cwnd就会慢慢变大，达到阀值75后就会进入拥塞避免模式。此时拥塞窗口的递增规则会发生变化：  
拥塞模式下使用`ca_incr`，它在`scan_performance_vars::init()`中初始化为1，除非在
-T4和-T5模板配置下为2，另外三者乘积的结果还要除以当前cwnd，可以理解为在拥塞避免模式下cwnd增长速度相比慢启动模式慢很多，并且增长的越来越慢。

  * 最大值。当cwnd超过默认值300时，就会停止增长，但也可以使用`--max-parallelism`来指定更大的。

现在基本知道nmap是如何计算拥塞窗口的了，但还有三点需要补充：

##### 3.2.5.2 拥塞窗口值降低

另外我们看到的实验中cwnd都在增长，实际从代码中看cwnd也可能会降低，`ultrascan_adjust_timing`中还会调用`ultra_timing_vals::drop()`里面会降低：

    
    
    /* Update congestion variables for a detected drop. */
    void ultra_timing_vals::drop(unsigned in_flight,
      const struct scan_performance_vars *perf, const struct timeval *now) {
      /* "When a TCP sender detects segment loss using the retransmission timer, the
         value of ssthresh MUST be set to no more than the value
           ssthresh = max (FlightSize / 2, 2*SMSS)
         Furthermore, upon a timeout cwnd MUST be set to no more than the loss
         window, LW, which equals 1 full-sized segment (regardless of the value of
         IW)." */
      cwnd = perf->low_cwnd;
      ssthresh = (int) MAX(in_flight / perf->host_drop_ssthresh_divisor, 2);
      last_drop = *now;
    }
    

条件是：

    
    
    static void ultrascan_adjust_timing(UltraScanInfo *USI, HostScanStats *hss,
                                        UltraProbe *probe,
                                        struct timeval *rcvdtime) {
      ......
      /* Notice a drop if
         1) We get a response to a retransmitted probe (meaning the first reply was
            dropped), or
         2) We got no response to a timing ping. */
      if ((probe->tryno > 0 && rcvdtime != NULL)
          || (probe->isPing() && rcvdtime == NULL)) {
    
        // Drops often come in big batches, but we only want one decrease per batch.
        if (TIMEVAL_AFTER(probe->sent, hss->timing.last_drop))
          hss->timing.drop(hss->num_probes_active, &USI->perf, &USI->now);
        if (TIMEVAL_AFTER(probe->sent, USI->gstats->timing.last_drop))
          USI->gstats->timing.drop_group(USI->gstats->num_probes_active, &USI->perf, &USI->now);
      }
      ......
    }
    

这个drop指的是什么我没太弄清楚，实际测试中我没有遇到过cwnd下降的情况，但应该知道有这样的事实。

##### 3.2.5.3 拥塞窗口的计算对象

无论从`scan_performance_vars::init()`初始化还是从`ultrascan_adjust_timing()`调整拥塞窗口大小的源码中都可以发现，拥塞窗口的计算对于分组和单个主机是独立进行的，也就是说一个主机对象中的拥塞窗口值取决于该主机历史目前为止发包收包的表现，一个分组对象中的拥塞窗口值则取决于这个分组中所有主机目前为止发包收包表现。

##### 3.2.5.4 拥塞窗口的作用对象

回到`HostScanStats::sendOK()`代码中，`getTiming()`获得的拥塞窗口值是会影响函数返回值决定当前探测包是否发送的，也直接影响到发包速度的。不仅如此，我们知道在`doAnyNewProbes()`中决定一个探测包是否发出前有两个`sendOK()`的判断第二个`sendOK()`：`HostScanStats::sendOK()`外，还有第一个`sendOK()`也就是`GroupScanStats::sendOK()`，它里面也会判断cwnd，但是判断的是分组的cwnd：

    
    
    /* Returns true if the GLOBAL system says that sending is OK.*/
    bool GroupScanStats::sendOK(struct timeval *when) {
    
      ......
      if (timing.cwnd >= num_probes_active + 0.5) {
        if (when)
          *when = USI->now;
        return true;
      }
      ......
      return false;
    }
    

可见分组的cwnd大小也会直接影响分组发包的判断和速度。

而主机的cwnd却并不是影响主机发包的唯一因素，从`HostScanStats::getTiming()`能发现，一个主机在拥有自己的拥塞窗口值的情况下，实际执行发包时的参考标准却有可能是分组的拥塞窗口或者是自己的，取决于所这个发包是否ping包或者发包数量是否低于80。这里我们再做个实验，猜测如果一个主机需要扫描的端口比较少，那么就算分组的cwnd较大，这个主机也只会使用默认的cwnd值10或者增长一点。为此我们在`getTiming()`获取到返回值输出日志后，增加了输出分组中cwnd值。

 **实验** ：

对一个C段主机的四个端口（部分端口开放，能促使cwnd的增长）进行扫描：

![image](https://image.3001.net/images/20221212/1670815023_63969d2f04fc4b6617711.png!small)

看到在最开始的发包循环中，主机使用的cwnd和分组使用的cwnd (`USI->gstats->timing`) 都是初始化值10。

![image](https://image.3001.net/images/20221212/1670815036_63969d3c7fb76c702d5cd.png!small)

经过多次发包后，分组中的cwnd由于部分开放的端口被探测出来甚至飞涨到了拥塞避免阀值75，但当前主机使用的cwnd仍然是默认的10：

![image](https://image.3001.net/images/20221212/1670815051_63969d4bb4ed127edffd5.png!small)

也有分组没有增长到阀值，但主机的cwnd发生了一点调整：

![image](https://image.3001.net/images/20221212/1670815067_63969d5be471b3f833e6b.png!small)

和我们预想的表现差不多。

##### 3.2.5.5 用户指定拥塞窗口

从拥塞窗口初始化代码可以看出来，我们可以通过设置`--min-parallelism`来设置初始的拥塞窗口，这样可以带来发包速度的提升，也可以设置`--max-parallelism`来控制拥塞窗口的最大值如果你懂得如何控制恰当。可以做个实验验证`--min-parallelism`带来的速度提升：

 **实验** :

以前面实验中我们测试的那个扫1000个端口用了21秒的主机，现在加上`--min-parallelism`：

![image](https://image.3001.net/images/20221212/1670815083_63969d6bd4ba32ca6f60a.png!small)

只用了5秒：

![image](https://image.3001.net/images/20221212/1670815095_63969d77f40ee0ed843de.png!small)

##### 3.2.5.6 总结

最后我们来总结下nmap下的拥塞窗口机制：

  * 拥塞窗口是一种将拥塞避免算法和慢启动算法相结合的TCP拥塞控制机制，基本思想就是在一开始发包较慢，根据回包情况决定是否加快发包，当快到一个阀值，就加快的很慢了。

  * nmap也实现了这个机制，并且针对主机和分组的收发包表现分别计算两个拥塞窗口值，他们的初始化值一样，阀值一样。

  * 拥塞窗口随着发包持续进行和端口被探测出来会上升，也在某些场景会下降。

  * 对一个主机发起探测包时，会参考分组的拥塞窗口大小和视探测包类型参考主机拥塞窗口大小，参考结果会影响发包速度。

#### 3.2.6 并行度

上一节提到并行度参数 min/max parallelism影响了初始的拥塞窗口，跟踪这个参数的使用我发现它还影响了
lua扫描（不在本文讨论范围内）、idle scan扫描（一种端口扫描模式，通常不用）以及服务版本识别。接下来我们看看它如何影响服务版本识别的：

在service_scan.cc:1980中`ServiceGroup::ServiceGroup`构造函数中使用`o.min_parallelism`、`o.max_parallelism`来初始化了`ideal_parallelism`：

    
    
    ServiceGroup::ServiceGroup(std::vector<Target *> &Targets, AllProbes *AP) {
      ......
      desired_par = 1;
      if (o.timing_level == 3) desired_par = 20;
      if (o.timing_level == 4) desired_par = 30;
      if (o.timing_level >= 5) desired_par = 40;
      // TODO: Come up with better ways to determine ideal_parallelism
      int min_par, max_par;
      min_par = o.min_parallelism;
      max_par = MAX(min_par, o.max_parallelism ? o.max_parallelism : 100);
      ideal_parallelism = box(min_par, max_par, desired_par);
    }
    

如果没有设置parallelism参数值，依这个盒子在默认-T3模版配置下计算出来ideal_parallelism默认值就是20，`ideal_parallelism`是服务版本扫描的并行度，简单的说就是目前nmap正在探测的目标端口个数，会在判断是否向下一个端口发起服务探测时有影响，service_scan.cc:2317行：

    
    
    static int launchSomeServiceProbes(nsock_pool nsp, ServiceGroup *SG) {
      ......
      while (SG->services_in_progress.size() < SG->ideal_parallelism &&
             !SG->services_remaining.empty()) {
        ......
        nextprobe = svc->nextProbe(true);
    	......
      }
      return 0;
    }
    

nmap对服务探测发包和处理是使用epoll技术来完成的，`launchSomeServiceProbes`会在收包回调函数中被调用，如果当前正在探测的服务端口数量大于`ideal_parallelism`就会等待正在探测的端口的完成，否则继续添加下一个端口。

为此可以做个实验，我们给超过10个有效端口进行服务探测，但设置`--max-parallelism`为10，看下是否出现了并行度限制的情况

 **实验** ：

在`launchSomeServiceProbes()`中加入并行度和当前探测中端口的输出：

![image](https://image.3001.net/images/20221212/1670815869_6396a07d614ae01f97aa1.png!small)

执行命令对30台主机的4个端口就行扫描：

![image](https://image.3001.net/images/20221212/1670815881_6396a0892faf21fe9d177.png!small)

![image](https://image.3001.net/images/20221212/1670815889_6396a091dbc73687fdd7a.png!small)

可以看到总共发现需要进行服务探测的端口有17个，但`ideal_parallelism`只有10个，当到达这个限制后，队列中剩下了7个等待下一次进行并行探测，理论上这是会影响探测速度的，我们可以在试下如果并行度没有被限制速度会不会不同。但是目前不能简单的通过对比实验比较出并行度对于服务版本识别的速度的影响，因为并行度不仅影响服务探测还很大程度影响在服务探测之前进行的端口扫描的速度，于是我们需要在代码中增加服务探测函数执行时间的日志：

service_scan开头处：

![image](https://image.3001.net/images/20221212/1670815902_6396a09e11476949ae61d.png!small)

结束处：

![image](https://image.3001.net/images/20221212/1670815910_6396a0a6b68590a21e702.png!small)

现在我们观察下限制并行度时的时间：

![image](https://image.3001.net/images/20221212/1670815922_6396a0b28776efcc4374c.png!small)

![image](https://image.3001.net/images/20221212/1670815932_6396a0bc2cf4abb6c5dcd.png!small)

约用了58秒，再看并行度没有被限制时的时间，取消`--max-parallelism`参数：

![image](https://image.3001.net/images/20221212/1670815942_6396a0c65a7b2c0cf879b.png!small)

![image](https://image.3001.net/images/20221212/1670815955_6396a0d38a477e6f0214c.png!small)

![image](https://image.3001.net/images/20221212/1670815963_6396a0dbdef6dcba3128a.png!small)

这次计划进行服务探测的端口共17个，但并行度为20，也就没有产生限制，但时间却为约59秒。从结果上看，甚至时间变慢了，我又作了几次实验，发现两者时间确实差不多。

然而，影响nmap服务探测速度的是另外一个重要的并行度概念：同一端口探测策略的并行度。当出现一个比较奇特的端口，nmap并不能通过一两个探测包就识别出它的服务版本出来而是先后尝试了很多条策略（对一个端口发起一个会话请求，根据后续交互内容从中提取服务端指纹的过程，就是叫一条策略），最后才识别或者甚至没有识别出来。这些策略就存在一个并行度问题。遗憾的是，nmap同一端口探测策略的并行度值为1，也就是说nmap在同一时间只对一个端口尝试一个策略。

为了说明这个结论，我们先做一个实验，通过抓包观察nmap对于同一端口探测策略发包情况：

 **实验**

我们接着上一个实验的结果，上面的探测目标中，主机172.16.x.y的80和8000
这两个端口就是奇特的端口，它不能被nmap所有策略识别出来，我们将它从目标中排除掉，看下这批端口使用时间：

![image](https://image.3001.net/images/20221212/1670815986_6396a0f2d992950d66417.png!small)

![image](https://image.3001.net/images/20221212/1670815999_6396a0ffc8b38fb8236a7.png!small)

![image](https://image.3001.net/images/20221212/1670816008_6396a1086fbb1d64be263.png!small)

仅用了6秒就完成了。我们从日志中看到，排除 172.16.x.y
这个主机后，计划进行服务探测的目标端口从17个变为了14个，因为排除的主机中有三个是开放的端口。

为什么仅少了3个端口，服务探测时间就从58秒变为了6秒速度提升了近90%？我们可以从抓包中看到一些原因。

探测14个端口的抓包（下面的）：

![image](https://image.3001.net/images/20221212/1670816019_6396a113b0caffa922181.png!small)

nmap在极短时间内完成了对14个端口的14个应用层发包。

探测17个端口（含奇特端口）的抓包：

![image](https://image.3001.net/images/20221212/1670816033_6396a121d68e5dec1f045.png!small)

![image](https://image.3001.net/images/20221212/1670816044_6396a12c308503924b324.png!small)

![image](https://image.3001.net/images/20221212/1670816054_6396a136642ca618b68f7.png!small)

（说明：第一个图中隐藏的目标主机ip包含多个主机，因为处于开始阶段，多个主机需要扫描，后面两个图中隐藏的ip就仅剩下了 172.1.x.y
这台目标主机了，下面讲述为什么它拖延了时间）

一共发出了74个应用层发包，发包时间先后从16秒到63秒持续了57秒之久。其中几个时间点之间间隔的5秒是下一节要讲的tcp连接超时时间，也是一个`epoll_wait()`（epoll模型的使用请自行了解）的io最长等待时间（当一批io描述符在epoll中没有响应，`epoll_wait()`就会等到超时才会返回），这些时间点16、21、26...63就是nmap每一轮发生超时后的集中发包时间点，可以看出除了第一轮发包时间点发包达到了默认并行度20，剩下的时间点发包数为从2到14个不等，这些发包都是对172.16.x.y
的80和8000端口发出的，它们因为无法被识别，nmap先后尝试了数十个策略。

我们的问题是，如果对于比如80端口的所有策略是并行发包的，那么为什么有数十个策略要尝试却发包这么慢，所以我们现在怀疑这些策略并不是并行发包，来分析抓包数据：

先看下第一轮之后最多发包数的第33秒时的流量（下图隐藏的ip仅包含本机ip和172.16.x.y的ip）：

![image](https://image.3001.net/images/20221212/1670816068_6396a14465f2351c05d17.png!small)

可以发现，在引擎先使用44132端口向目标80端口发起一次tcp握手后，随后经过发起http请求，获得http
400的回复然后结束会话，如图中红色标识过程。 接着，引擎又打开新的tcp连接使用44134端口，再向80端口发起http请求，然后也获得了http
400的回复。由此可推测，引擎是在一次探测的结束后才发起新的探测的，我又按照这个思路分析了剩下的流量，现象都是如此。

因此我们可以基本确定nmap对于同一端口探测策略是没有并行进行的，而我们看到每个时间点对同一端口发出的多个探测包，只是nmap对该端口短时间内连续尝试了多个策略并且端口有持续响应的结果，但并不是同时发起。

为了确认这个结论，我们还是分析下代码，nmap进行服务版本探测就是调用`service_scan()`函数：

    
    
    int service_scan(std::vector<Target *> &Targets) 
    {
      ......
      // Lets create a nsock pool for managing all the concurrent probes
      // Store the servicegroup in there for availability in callbacks
      if ((nsp = nsock_pool_new(SG)) == NULL) {
        ......
      }
      ......
      launchSomeServiceProbes(nsp, SG);
      ......
    
      // OK!  Lets start our main loop!
      looprc = nsock_loop(nsp, timeout);
    }
    

里面先`nsock_pool_new`生成`nsock_pool`对象
nsp，它是一个nmap定义的专门用来管理io事件和io描述符的对象，然后调用`launchSomeServiceProbes()`：

    
    
    static int launchSomeServiceProbes(nsock_pool nsp, ServiceGroup *SG) {
      ......
      //从service_scan中进来后，这里就会一次将不超过并行度范围的端口全部放入处理中，只有后面xxx_handler（）函数的执行完后进来时，才会找不到新端口，因为可能端口第一次已经处理完了。
      //在构造好一个探测单元后，就使用nsock_connect_tcp将connect_handler作为回调发起一个连接。
    
      //遍历所有待扫端口，判断并行度限制
      while (SG->services_in_progress.size() < SG->ideal_parallelism &&
             !SG->services_remaining.empty()) {
        // Start executing a probe from the new list and move it to in_progress
        svc = SG->services_remaining.front();
        ......
    
        //获取探测单元
        nextprobe = svc->nextProbe(true);
        ......
    
    	//创建套接字
        if ((svc->niod = nsock_iod_new(nsp, svc)) == NULL) {
          fatal("Failed to allocate Nsock I/O descriptor in %s()", __func__);
        }
    
        //发起tcp/udp的连接，传入连接成功后的回调函数 “servicescan_connect_handler”
        if (svc->proto == IPPROTO_TCP)
          nsock_connect_tcp(nsp, svc->niod, servicescan_connect_handler,
                            DEFAULT_CONNECT_TIMEOUT, svc,
                            (struct sockaddr *)&ss, ss_len,
                            svc->portno);
        else {
          assert(svc->proto == IPPROTO_UDP);
          nsock_connect_udp(nsp, svc->niod, servicescan_connect_handler,
                            svc, (struct sockaddr *) &ss, ss_len,
                            svc->portno);
        }
    
    	//添加到 “探测处理中” 链表
        if (!SG->services_remaining.empty() && SG->services_remaining.front() == svc) {
          SG->services_remaining.pop_front();
          SG->services_in_progress.push_back(svc);
        }
      }
    
      return 0;
    }
    

大致流程就是，在while循环中将不超过并行度范围的端口全部拿出来，创建探测对象，发起tcp/udp的连接，标记为探测中，传入回调`servicescan_connect_handler()`，在连接成功后后续流程就交给回调区处理。我们从日志中可以看出来，这时就达到了发包最大并行度，因为这时都是首次探测尝试。

在这个函数执行完成后，nsp
中就有了所有探测中的端口的io描述符和数据处理的回调函数，现在回到`service_scan()`接下来调用`nsock_loop()`，跟踪发现它就是
engine_epoll.c 中的`epoll_loop()`, 完全可以预见，后续所有的端口探测发起和数据处理指纹匹配这些工作，都是在这个循环函数中完成：

    
    
    int epoll_loop(struct npool *nsp, int msec_timeout) {
    
      struct epoll_engine_info *einfo = (struct epoll_engine_info *)nsp->engine_data;
      ......
      do {
    	  ......
          results_left = epoll_wait(einfo->epfd, einfo->events, einfo->evlen, combined_msecs);
          ......
      } while (results_left == -1 && sock_err == EINTR); /* repeat only if signal occurred */
      ......
      iterate_through_event_lists(nsp, results_left);
    }
    

进入循环后，nmap会根据传入的超时时间`combined_msecs`，使用`epoll_wait`等待上一步中传入的io描述符的响应事件，传入`iterate_through_event_lists()`处理：

    
    
    void iterate_through_event_lists(struct npool *nsp, int evcount) {
      struct epoll_engine_info *einfo = (struct epoll_engine_info *)nsp->engine_data;
      ......
      for (n = 0; n < evcount; n++) {
        struct niod *nsi = (struct niod *)einfo->events[n].data.ptr;
    
        /* process all the pending events for this IOD */
        process_iod_events(nsp, nsi, get_evmask(einfo, n));
       ......
      }
      ......
    }
    

在`process_iod_events()`调用`process_event()`最后调用回调`servicescan_connect_handler()`处理端口连接成功后的下一步动作：

    
    
    static void servicescan_connect_handler(nsock_pool nsp, nsock_event nse, void *mydata) {
    
      ......
      } else if (status == NSE_STATUS_SUCCESS) 
      {
       ......
        // Yeah!  Connection made to the port.  Send the appropriate probe
        send_probe_text(nsp, nsi, svc, probe);
        // Now let us read any results
        nsock_read(nsp, nsi, servicescan_read_handler, svc->probe_timemsleft(probe, nsock_gettimeofday()), svc);
      }
      else {
        ......
        }
      }
      // We may have room for more probes!
      launchSomeServiceProbes(nsp, SG);
      return;
    }
    

简要含义就是，调用`send_probe_text()`发送一个探测payload（比如http，SSL
握手，Portmap等），然后调用`nsock_read()`做一次读取，为了获得比如ftp、ssh协议的banner，并将`servicescan_read_handler()`设置为回调处理这些获取的内容，可以预见里面肯定会作指纹匹配这样的操作。先看下`send_probe_text()`：

    
    
    static int send_probe_text(nsock_pool nsp, nsock_iod nsi, ServiceNFO *svc,
                                 ServiceProbe *probe) {
        ......
        probestring = probe->getProbeString(&probestringlen);
    
        nsock_write(nsp, nsi, servicescan_write_handler, svc->probe_timemsleft(probe), svc,
                    (const char *) probestring, probestringlen);
        return 0;
      }
    

很简单，就是使用`nsock_write()`发包。看下`servicescan_read_handler()`：

    
    
    static void servicescan_read_handler(nsock_pool nsp, nsock_event nse, void *mydata) {
    
      ......
    
      } else if (status == NSE_STATUS_SUCCESS) {
    
        //读取内容
        readstr = (u8 *) nse_readbuf(nse, &readstrlen);
    
        //遍历指纹库做对比匹配
        for (MD = NULL; probe->fallbacks[fallbackDepth] != NULL; fallbackDepth++) {
          MD = (probe->fallbacks[fallbackDepth])->testMatch(readstr, readstrlen);
          if (MD && MD->serviceName) break; // Found one!
        }
    
    	//匹配成功
        if (MD && MD->serviceName) {
          // WOO HOO!!!!!!  MATCHED!  But might be soft
          ......
        }
    
    	//匹配失败
        if (!MD || !MD->serviceName || MD->isSoft)
        {
         	if (......) 
          	{
       			startNextProbe(nsp, nsi, SG, svc, false);
     		} 
     		else if (......) 
     		{
          		end_svcprobe(nsp, PROBESTATE_FINISHED_TCPWRAPPED, SG, svc, nsi);
        	} 
        	else 
        	......
       }
    
      //重新进入launchSomeServiceProbes()，为了让前面一开始因为并行度限制而尚未开始探测的端口进入探测状态。
      // We may have room for more probes!
      launchSomeServiceProbes(nsp, SG);
    
    }
    

这里我比较多的简化了代码，梗概就是：读取收到的上层内容，遍历指纹库做对比匹配，匹配成功后会提取相应的产品、版本、主机名、操作系统等信息，失败后就判断是继续发起下一次探测`startNextProbe()`还是结束探测。

经过上面的实验现象和源码分析我们可以确定了，nmap对于同一端口的探测策略是依次执行的而并不存在并行度。现在我们终于可以解释为什么出现奇特端口时 nmap
服务探测如此之慢了：当出现一些奇特的端口时，会增大很多nmap的策略尝试消耗，并且同一端口的探测策略不并行执行的更加剧了耗时。

#### 3.2.7 服务探测的连接超时

上节说到并行度会影响服务探测的效率，虽然实测不明显，但我在经过一些源码研究后发现，其实影响服务探测速度的有一个重要的参数，就是服务连接超时。在
service_scan.h 中有以下宏定义：

    
    
    /**********************  DEFINES/ENUMS ***********************************/
    #define DEFAULT_SERVICEWAITMS 5000
    #define DEFAULT_TCPWRAPPEDMS 2000   // connections closed after this timeout are not considered "tcpwrapped"
    #define DEFAULT_CONNECT_TIMEOUT 5000
    #define DEFAULT_CONNECT_SSL_TIMEOUT 8000  // includes connect() + ssl negotiation
    #define SERVICEMATCH_REGEX 1
    #define MAXFALLBACKS 20 /* How many comma separated fallbacks are allowed in the service-probes file? */
    

其中`DEFAULT_SERVICEWAITMS`、`DEFAULT_CONNECT_TIMEOUT
`、`DEFAULT_CONNECT_SSL_TIMEOUT`分别表示发起单个服务探测到探测结束总共消耗时间、TCP端口的connect超时时间、SSL端口的握手超时时间。如果把这三个时间改为2000（也就是两秒）、2000、5000，那么整体探测速度会有将近一半的速度提升。但这没有办法从参数中设置，只能修改宏来编译使用。可以实验演示：

 **实验** ：

我们探测30个ip中四个的端口，它们部分开启：

![image](https://image.3001.net/images/20221212/1670816117_6396a1754af9c28065ff4.png!small)

花了一分钟。

![image](https://image.3001.net/images/20221212/1670816134_6396a186b04e5f51a5cf0.png!small)

再更改宏定义后重编译执行：

![image](https://image.3001.net/images/20221212/1670816145_6396a1912c8db3ff9ea46.png!small)

![image](https://image.3001.net/images/20221212/1670816157_6396a19d50f6dc7feb249.png!small)  
时间降到了34秒，我又对比了两次探测的抓包，发现第一次扫描时，nmap向目标端口发起应用层协议请求包时，每个批量之间间隔了5秒以上，而第二次扫描时，多数间隔都是2秒以上，这里我就不贴出抓包详情了有兴趣你可验证。

从源码上看，这个超时时间将会被直接传入service scan模块中的epoll_wait函数中，位于

![image](https://image.3001.net/images/20221212/1670816170_6396a1aa31b1f8167ffa9.png!small)

在日志中可以看到，在没改动之前，传入的等待时间是5000ms：

![image](https://image.3001.net/images/20221212/1670816182_6396a1b681ef52ce28fcd.png!small)

改动之后是2000ms：

![image](https://image.3001.net/images/20221212/1670816195_6396a1c3caacf7ccfc2a7.png!small)

nmap在这个模块中没有像其他模块那样采用动态学习机制来调整这几个超时时间，而这个方法的确是可以加快服务版本探测的速度的，但是同样的在互联网环境中可能会带来准确性问题，并且改动后需要编译，不太灵活。

#### 3.2.8 重传次数

`sendOK()`中的判断发包是否允许的条件目前我们讨论完了，但是nmap中还有其他两个影响性能的参数：retry（重传）和 rtt-timeout（往返超时）。

在`ultra_scan()`的分组发包大循环中，除了通过`doAnyPings()`和`doAnyNewProbes()`来发送ping包和端口探测包，还使用了`doAnyOutstandingRetransmits(&USI)`和`doAnyRetryStackRetransmits(&USI)`来对未响应的探测包进行重传，这里有两个重要的概念：允许重传次数和最大重传次数。允许重传次数比较好理解，就是一个端口未发生响应那么就继续发包直到响应所允许的次数。而最大重传次数就牵涉到nmap的学习思想：如果向一个端口发送探测包达到既定允许重传次数后，依然没有响应，那么就把它视为超时，如果在最后一次发包后得到了有效的回复，那么就认为当前主机具有一定”潜力“，就把后续所有端口的允许重传次数增加1次，以此来提高网络容错度。这个最大重传次数就是，如果一个主机总是能提升自己允许重传次数，就给它一个最大值，因为无限增加允许重传次数是不合理的也可能是恶意的。

在主机对象中允许重传次数由`HostScanStats::allowedTryno()`成员函数返回：

    
    
    unsigned int HostScanStats::allowedTryno(bool *capped, bool *mayincrease) {
    
      ......
      /* TODO: This should perhaps differ by scan type. */
      maxval = MAX(1, max_successful_tryno + 1);
      if (maxval > USI->perf.tryno_cap) {
        if (capped)
          *capped = true;
        maxval = USI->perf.tryno_cap;
        tryno_mayincrease = false; /* It never exceeds the cap */
      } else if (capped) *capped = false;
      ......
    
      return maxval;
    }
    

在`HostScanStats`对象构造函数中`max_successful_tryno`被初始化为0，所以一开始`allowedTryno()`返回的允许重传次数都是`max_successful_tryno`+1=1次，这也能解释，我们在平常抓包时一般看到nmap只会对一个未响应的包重传一次。

    
    
    maxval = USI->perf.tryno_cap;
    

`USI->perf.tryno_cap`就是用户设置的最大重传次数，使用`--max-retries`参数就能设置它的值，默认下为10。

在`ultrascan_port_probe_update()`中收到一个端口有效的探测回包后，如果此时的重试次数刚好是允许重传次数的最后一次，那么就会把`max_successful_tryno`增加为允许重传次数，当然根据`allowedTryno()`的计算后续允许重传次数就会加1：

    
    
    void ultrascan_port_probe_update(UltraScanInfo *USI, HostScanStats *hss,
                                     std::list<UltraProbe *>::iterator probeI,
                                     int newstate, struct timeval *rcvdtime,
                                     bool adjust_timing_hint) {
      ......
      if (adjust_timing) {
        ultrascan_adjust_timing(USI, hss, probe, rcvdtime);
    
        if (rcvdtime != NULL && probe->tryno > hss->max_successful_tryno) {
          /* We got a positive response to a higher tryno than we've seen so far. */
          hss->max_successful_tryno = probe->tryno;
          ......
        }
      }
      ......
    }
    

用户不能设置初始化的允许重传次数，nmap默认为1次，但可以设置最大重传次数，这在网络不稳定的环境中是有用的。

### 3.2.9 报文往返超时

在 nmap 基础扫描中，只有两个超时概念：一个是host timeout，一个是rtt
timeout，前者就是一个主机上消耗的时间，很死，超时就直接终止该主机，后者叫报文往返超时，先解释下 rtt
时间，nmap对一个探测单位发出第一个报文后会记录一个时间，后续会重传，如果最后收到了一个有效的响应包，那么收包时间和第一个发包时间差值就是rtt，rtt
timeout的含义也就是，如果等待了rtt时间后依然没有一个响应包，那么就视为超时并终止重传放入完成列表。

在构造一个探测单位尝试第一次发包时，nmap将发包时间记录下来了，可以在`sendIPScanProbe()`函数中看到如下代码：

    
    
    if (decoy == o.decoyturn) {
              probe->setIP(packet, packetlen, pspec);
              probe->sent = USI->now;
            }
    

在`ultra_scan()`分组发包循环中，使用`doAnyNewProbes()`发包和`waitForResponses()`完成收包后，有`processData()`用来处理主机列表中的数据，里面就会判断：如果一个探测单位发包达到了允许重传次数，并且当前时间达到了rtt
timeout（由`host->probeTimeout()`来返回），那么会将它标记为完成不再扫描：

    
    
    if (!probe->timedout && TIMEVAL_SUBTRACT(USI->now, probe->sent) >
              (long) host->probeTimeout()) {
            host->markProbeTimedout(probeI);
            continue;
          }
    

rtt timeout 默认值为1000ms，但后续的 rtt timeout 和重传次数、拥塞窗口一样，有个学习的过程：timing.cc:168行:

    
    
    /* Same as adjust_timeouts(), except this one allows you to specify
     the receive time too (which could be because it was received a while
     back or it could be for efficiency because the caller already knows
     the current time */
    void adjust_timeouts2(const struct timeval *sent,
                          const struct timeval *received,
                          struct timeout_info *to) {
    
      delta = TIMEVAL_SUBTRACT(*received, *sent);
    
      if (to->srtt == -1 && to->rttvar == -1) {
        ......
      } 
      //这里学习rtt timeout, 计算新的rtt timeout		// A
      else {
        long rttdelta;
        rttdelta = delta - to->srtt;
        //过滤掉 rtt 变化太突兀的包
        if (rttdelta > 1500000 && rttdelta > 3 * to->srtt + 2 * to->rttvar) {
          if (o.debugging) {
            log_write(LOG_STDOUT, "Bogus rttdelta: %ld (srtt %d) ... ignoring\n", rttdelta, to->srtt);
          }
          return;
        }
        to->srtt += rttdelta >> 3;
        to->rttvar += (ABS(rttdelta) - to->rttvar) >> 2;
        to->timeout = to->srtt + (to->rttvar << 2);
      }
      ......
    
      //学习调整后的rtt时间，不能超过设定的范围   		//B
      to->timeout = box(o.minRttTimeout() * 1000, o.maxRttTimeout() * 1000,
                        to->timeout);
    
      //如果存在发包延迟，那么rtt时间只允许要比发包延迟更高 //C
      if (o.scan_delay)
        to->timeout = MAX((unsigned) to->timeout, o.scan_delay * 1000);
      ......
    
    }
    

从上面我加了的中文注释A、B、C的对应代码含义可见，nmap在收到一个有效包后，会计算收包和发包的时间差即 rtt 来比对当前的 rtt
timeout值，过滤掉那些明显不正常的包，然后来更新后续探测的 rtt timeout 时间，计算规则如A注释处分支所示，可以理解为，rtt
变长后，后续的探测的rtt timeout 就会变长，rtt缩短后，rtt
timeout也会缩短。但是变化也有一个长短范围，如B处所示，`o.minRttTimeout()`和`o.maxRttTimeout()`是用户在
nmap 参数`--min-rtt-timeout`和`--max-rtt-timeout`中设置的，当然rtt timeout
也有初始化值，由`--initial-rtt-timeout`来设置。

 **实验**

在初始时我们可以看到上面代码中参数to（结构体timeout_info）的各成员的初始化值，下面日志中“to”是to->timeout的值，显示是1秒：

![image](https://image.3001.net/images/20221212/1670816227_6396a1e3bc3a31b3925f2.png!small)

因为我测试的网络很稳定，rtt很低，在第二轮收发包循环中，rtt很快被调整为了最低值100ms：

![image](https://image.3001.net/images/20221212/1670816242_6396a1f27bf5e15ff0e94.png!small)

需要指出的是，主机的 rtt 高和不响应有区别，不响应的话，rtt timeout 不会调整。

另外单个主机和分组有分别有 rtt timeout 时间，在发生rtt
变化时都会作调整，在`ultrascan_adjust_timeouts`中可以体现：

    
    
    static void ultrascan_adjust_timeouts(UltraScanInfo *USI, HostScanStats *hss,
                                          UltraProbe *probe,
                                          struct timeval *rcvdtime) {
      if (rcvdtime == NULL)
        return;
    
      adjust_timeouts2(&(probe->sent), rcvdtime, &(hss->target->to));
      adjust_timeouts2(&(probe->sent), rcvdtime, &(USI->gstats->to));
    
      USI->gstats->lastrcvd = hss->lastrcvd = *rcvdtime;
    }
    

### 3.3 小节

上面我们分析了nmap源码中9个性能概念：

 **主机超时、最小/最大发包速率、速率限制检测、发包延迟、拥塞窗口、并行度、重传次数、报文往返超时、服务探测连接超时**

可以总结为：

描述超时的有：主机超时、报文往返超时、服务探测连接超时

涉及发包速度的有：最小/最大发包速率、速率限制检测、发包延迟、拥塞窗口、并行度、服务探测连接超时

涉及扫描准确度的有：主机超时、最小/最大发包速率、速率限制检测、发包延迟、拥塞窗口、并行度、重传次数、报文往返超时、服务探测连接超时

可以用户设置参数的有：主机超时、最小/最大发包速率、发包延迟、拥塞窗口、并行度、重传次数、报文往返超时

nmap动态学习的有：拥塞窗口、重传次数、报文往返超时

用户可以设置参数来提升/降低扫描速度的有：最小/最大发包速率、发包延迟、并行度

用户改动并重新编译来提升/降低扫描速度的有：服务探测连接超时

## 4 使用指引

从上节讨论的nmap源码中几个性能概念和提到的用户参数，可以总结下使用nmap来提升扫描准确性和速度的几个方法，当然准确性和速度永远都是两个相互制衡的概念，不可兼得。

#### 4.1 提升速度

a. 设置`--min-rate`参数，无理由强制发包效率，脱离了nmap的学习机制，影响准确性。

b. 设置`--min-parallelism`参数，增大初始拥塞窗口，针对于完全无响应主机，可以避免因默认拥塞窗口值太低而导致发包进度太慢,
带来的速度收益较好。

c. 设置`--rtt-timeout`参数，缩小探测单位超时时间，这样对于无任何响应的主机，将更快将它放入完成列表，但这个参数实际上带来速度提升不大，nmap速度的瓶颈在于发包环节，不在于数据处理环节。

d. 更改服务探测连接超时宏定义时间，这可以较大幅度减少服务探测时间，并且nmap没有提供可以有效减少服务探测时间的参数，这是个可选方法。

#### 4.2 提升准确度

a. 设置`--scan-delay`参数，强制发包延迟，会和nmap的学习机制结合确定发包速度，但收益可能不明显，因为nmap的学习机制就已经基于RFC2581已较为科学。

b. 设置`--max-parallelism`参数，将默认的最大拥塞窗口值300缩小，不过建议使用nmap默认值。

c. 设置`--initial-rtt-timeout`参数，将初始的报文往返超时加大，这可以在一定程度上提高网络延迟的包容度。

