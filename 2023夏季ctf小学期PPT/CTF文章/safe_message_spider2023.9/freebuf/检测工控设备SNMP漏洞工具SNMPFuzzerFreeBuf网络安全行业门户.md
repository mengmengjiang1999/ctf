## 什么是snmp fuzzer

 **snmpfuzzer是一款用于对目标设备snmp可写oid节点数据进行fuzz测试的小工具。**

## 为什么要用snmp fuzzer

现如今工控环境中，存在大量的工控设备默认开启了snmp服务并支持snmp写操作，且设备使用了默认的snmp
community值，由于工控环境的特殊性，设备参数设定后会长时间不会修改，导致开启snmp服务的工控设备存在数据被篡改、覆盖、以及被大量可写数据攻击致瘫痪的风险。而snmpfuzzer灵活且自动化能够对开放了snmp写权限的工控设备进行检测，从而评估设备的安全性。

## 工控设备开启snmp的危害

在以往的测试过程中，通过snmp
fuzzer发现过一些工控设备的漏洞，这些漏洞主要集中在对snmp写操作的数据没有进行有效的校验。例如某设备支持通过snmp写操作来修改设备网卡的mac地址，但是没有对mac地址的长度进行校验，只要传入过长或者过短的mac地址都会造成设备瘫痪。还有些设备的网卡可以通过snmp写操作来开启和禁用，这样直接就会造成设备的网络中断影响业务。此外通常厂商还会有其自定义的私有oid节点，这些节点也很可能会存在一些安全问题，导致设备出现各种预期外的异常。

## snmp fuzzer检测流程

![](https://image.3001.net/images/20190620/1560996279_5d0ae9b7a70cb.png!small)

snmp fuzz测试机通过发送可写oid的snmp set-request请求去改变工控设备可写oid控制的数据，通过发送get request、get-next-request请求, 来接收工控设备返回的get-response报文，如果测试机没有收到get-response的回复报文，则利用socket通信，来监测工控设备是否崩溃。

## snmp fuzzer安装

在Ubuntu环境下安装与使用snmp fuzzer。

1\. 通过git命令，下载snmp fuzzer 代码。

    
    
    git clone <https://github.com/dark-lbp/snmp_fuzzer>

[](https://github.com/dark-lbp/snmp_fuzzer)

2\. snmp fuzzer运行依赖scrapy，如果没有安装scrapy，需要安装。

运行pip install scrapy命令，安装scrapy。

## Snmp fuzzer使用与分析

1\. 编写扫描目标设备可写oid的测试py脚本。

a. 创建一个test_scan_oid.py的文件。

b. 打开test_scan_oid.py文件，输入以下内容。

如下图所示：

![](https://image.3001.net/images/20190620/1560996479_5d0aea7ff33e4.png!small)

    
    
    target：设置目标机的IP地址。
    
    port：检查目标机是否崩溃的通信端口。
    
    count：fuzz snmp oid可写报文的次数。
    
    nic：目标机的默认路由。
    
    Target：创建一个snmpTarget类。
    
    SnmpTrarget参数说明：
    
    name：测试fuzz的名字，测试人员可以自定义。
    
    monitor_port：目标机是否存活监控端口。
    
    community：具备oid可写权限v2c用户，通常设备设置的v2c用户为：public或者private。
    
    oid：开始扫描oid结点。
    
    version：snmp用户版本，目前snmp fuzzer只支持snmp v1、v2c。
    
    Target.oid_scan()：开启扫描目标机可写oid的功能。
    
    Target.save_scan_result()：保存可写oid到pcap文件。

c. 运行test_scan_oid.py文件，开始扫描目标机可写的oid。

执行python test_scan_oid.py命令，执行完后在snmp_fuzzer/output目录下会有一个

Ip+_snmp_set_packet_list.pcap的文件，如：

![](https://image.3001.net/images/20190620/1560996605_5d0aeafdba0b0.png!small)

该文件存储的是目标设备可写的oid报文，用于fuzz测试。

2.编写fuzz测试脚本，进行fuzz测试。

1）创建一个test_snmp_fuzz.py文件。

2）打开test_snmp_fuzz.py文件，输入以下内容，如下图所示：

![](https://image.3001.net/images/20190620/1560996692_5d0aeb54e5cd1.png!small)

Target.read_test_case_from_pcap用于从可写的oid报文中读取oid。

Traget.fuzz()用于开始fuzz测试，通过不断发送snmp set-request请求，去设置snmp fuzz自己造的可写数据。如下图所示：

![](https://image.3001.net/images/20190620/1560996724_5d0aeb74086f5.png!small)

3\. 运行test_snmp_fuzz.py文件，开始fuzz测试。

    
    
    pythontest_snmp_fuzz.py

当目标设备对某个写请求不进行反馈或反馈异常时，会通过socket connect 对目标设备的存活进行检测，具体检测原理如下图所示：

![](https://image.3001.net/images/20190620/1560996745_5d0aeb89cde82.png!small)

当出现如下图log信息时代表目标机已经崩溃。

![](https://image.3001.net/images/20190620/1560996758_5d0aeb96e51e2.png!small)

## 如何避免开启snmp的危害

开启snmp服务的设备采用snmp v3用户，因为snmp v3支持用户认证与加密，安全性更好、更可靠。

 ***本文作者：zoucl123，转载请注明来自FreeBuf.COM**

