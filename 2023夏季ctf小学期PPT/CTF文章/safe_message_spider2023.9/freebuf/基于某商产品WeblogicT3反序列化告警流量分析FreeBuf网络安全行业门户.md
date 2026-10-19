# 前言

攻防演练时会遇到的针对weblogic等中间件漏洞利用以及漏洞扫描的很多，但是我看到某态势的流量的时候发现态势的探针的监测不单单是基于披露的poc或者exp来产生的告警。

![image-20220701125938689.png](https://image.3001.net/images/20220712/1657608994_62cd1b22af3564cb0c928.png!small)

这里一万多条告警。

# 环境搭建

这里我使vulhub复现几个cve来分析流量，这里的目的主要是对比wireshark、科*分析软件和某商安全设备的全流量的数据包告警分析。

![image-20220531120159178.png](https://image.3001.net/images/20220712/1657608995_62cd1b23a4379e42f8a82.png!small)

    
    
    cd CVE-2020-14882  
    docker-compose up -d

![image-20220531120406415.png](https://image.3001.net/images/20220712/1657608996_62cd1b24804d6c596bcd3.png!small)

    
    
    docker ps

![image-20220531144101546.png](https://image.3001.net/images/20220712/1657608997_62cd1b255f039fd4b3238.png!small)

> <http://192.168.166.130:7001/console/login/LoginForm.jsp>

![image-20220531150735334.png](https://image.3001.net/images/20220712/1657608998_62cd1b263aed90809414e.png!small)

# 分析

直接使用wireshark抓包是无法抓取不到数据包的，原因是nat模式下不走网卡，所以这里涉及到了tips就是添加路由

> route add 192.168.166.130 mask 255.255.255.255 192.168.0.1

![image-20220531172841700.png](https://image.3001.net/images/20220712/1657608999_62cd1b273d484d1c7c13a.png!small)

![image-20220531172821422.png](https://image.3001.net/images/20220712/1657609000_62cd1b2804d3e1e4fbd19.png!small)

用完删除

> route delete 192.168.166.130 mask 255.255.255.255 192.168.0.1

![image-20220531172908980.png](https://image.3001.net/images/20220712/1657609000_62cd1b28dfb0e3b1cc3fc.png!small)

但是此时似乎是没有用的，因为我们在进行漏洞利用的时候走的是http协议，传输层走的是tcp但是依旧是无法看到详细的流量数据。

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

设置虚拟机为桥接模式，再次尝试获取流量

![image-20220601100226184-16540489468111.png](https://image.3001.net/images/20220712/1657609001_62cd1b29b0a9210fd4b1a.png!small)

已成功获取到数据流量。使用命令查看对目标攻击的所有流量

> ip.addr==192.168.0.120

![image-20220601101920990.png](https://image.3001.net/images/20220712/1657609002_62cd1b2ab4e30a95f175e.png!small)

追踪一下tcp流

![image-20220601103810275.png](https://image.3001.net/images/20220712/1657609003_62cd1b2bc00343fe6e62e.png!small)

直接追踪`t3`流量，因为weblogic使用的协议为T3,当然态势内的漏洞监测也是基于`t3`协议来告警触发的。

上面两部分的内容是客户端和服务端的信息

    
    
    t3 7.0.0.0  
    AS:10  
    HL:19  
    ​  
    HELO:12.2.1.3.false  
    AS:2048  
    HL:19  
    MS:10000000  
    PN:DOMAIN

在使用paylaod的时候会给服务端发送请求，正常情况下我们能够找到的poc或者说exp的工作原理大部分都是基于版本来校验的

![image-20220601104955322.png](https://image.3001.net/images/20220712/1657609004_62cd1b2c8944a241351cf.png!small)

当然这里的环境版本为`12.2.1.3.0`

![image-20220601105126325.png](https://image.3001.net/images/20220712/1657609005_62cd1b2d52e085f51bcad.png!small)

这里根据不通的流可以看出来。这一点儿的话其实可以根据python脚本的内容也能看出来校验机制，这一点儿跟很多厂商的漏扫的原理应该是一致的。

这里我执行了几条命令，来查看一下流量特征

> `whoami`

![image-20220601110141273.png](https://image.3001.net/images/20220712/1657609006_62cd1b2e31c9ae3468398.png!small)

![image-20220601110344150.png](https://image.3001.net/images/20220712/1657609007_62cd1b2f01649bb71f942.png!small)

> `ls`

![image-20220601110253110.png](https://image.3001.net/images/20220712/1657609007_62cd1b2fba1780573e543.png!small)

![image-20220601110429921.png](https://image.3001.net/images/20220712/1657609008_62cd1b30e9943982ba515.png!small)

> `pwd`

![image-20220601130505217.png](https://image.3001.net/images/20220712/1657609009_62cd1b31c1382ccb81f38.png!small)

![image-20220601105733656.png](https://image.3001.net/images/20220712/1657609010_62cd1b32aab184a8f1dfd.png!small)

上传的shell.jsp文件做编码

![image-20220601130633592.png](https://image.3001.net/images/20220712/1657609011_62cd1b338270502e7a4f5.png!small)

序列化的部分就是在这一部分完成的

![image-20220601143017004.png](https://image.3001.net/images/20220712/1657609012_62cd1b34a09c494da0118.png!small)

回头看一下某报警日志的流量

![image-20220601145337314.png](https://image.3001.net/images/20220712/1657609013_62cd1b3568a52e66bf7ba.png!small)

这里触发规则库的内容是由于探针监测到流量中存在序列化的操作就直接触发了，所以这个时候正常的日志也是会触发漏洞预警。

可能使用wireshark对tcp的交互看着不太清晰，使用`科*网络分析`

![image-20220601110730949.png](https://image.3001.net/images/20220712/1657609014_62cd1b36934a5cb9bb9a1.png!small)

重新抓包

![image-20220601143349351.png](https://image.3001.net/images/20220712/1657609015_62cd1b37b528afdd37b02.png!small)

这是所有的攻击日志

![image-20220601112830027.png](https://image.3001.net/images/20220712/1657609016_62cd1b38b3dc7936cf4ec.png!small)

可以看到tcp流中数据交互的流量包。

![image-20220601120935730.png](https://image.3001.net/images/20220712/1657609017_62cd1b39a6262e1999b19.png!small)

因为这里只显示数据块部分的数据,那么这里可以看到，同样文件上传的时候内容是分块传输的

![image-20220601142652762.png](https://image.3001.net/images/20220712/1657609018_62cd1b3a9b30ccc9a07f3.png!small)

![image-20220601142728999.png](https://image.3001.net/images/20220712/1657609019_62cd1b3bd7b34cdf1cc51.png!small)

分作了四个数据块进行传输。

# 安全设备的告警

![image-20220704174713987.png](https://image.3001.net/images/20220712/1657609021_62cd1b3d7940417d59b89.png!small)

上面是tcp部分流量

![image-20220701130125910.png](https://image.3001.net/images/20220712/1657609022_62cd1b3eedb5782f45c66.png!small)

请求体内容

![image-20220701130155133.png](https://image.3001.net/images/20220712/1657609024_62cd1b40445065ecac16b.png!small)

那么告警行为的触发已经不是基于weblogic正常利用时的流量了，此时只是在tcp的传输阶段就已经拒绝连接了。

# 思考

安全设备流量监控下的预警以及触发条件是基于全流量还是部分流量以及规则条件产生的，规则库基于POC以及EXP,但是可能不会考虑到是否有完整的利用链，所以用户的体验感就比较难受了。

