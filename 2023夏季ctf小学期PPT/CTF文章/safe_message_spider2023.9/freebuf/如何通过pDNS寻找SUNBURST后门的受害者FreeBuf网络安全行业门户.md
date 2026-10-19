![](https://image.3001.net/images/20210106/1609920884_5ff57174be0aca0c18d98.jpg!small)  

## 概述

我们的[
_SunburstDomainDecoder_](https://www.netresec.com/?page=Blog&month=2020-12&post=Reassembling-Victim-Domain-Fragments-from-SUNBURST-DNS)工具现在已经可以识别SUNBURST后门的受影响用户了，我们只需要给该工具提供针对avsvmcloud.com子域名的被动DNS（pDNS）数据，即可识别用户是否受到了攻击者的SUNBURST感染。

如果公司和组织的计算机设备安装了包含SUBURST后门的SolarWinds
Orion更新，那么设备将会向avsvmcloud.com子域名发送看似随机的DNS查询请求。其中的某些DNS请求将会包含目标设备的内部AD域，并会将其编码至子域名中。

## SUBURST后门的三个操作阶段

大多数SUBURST后门的受害者其实都是幸运的，因为攻击者并没有对他们展开实际性的攻击。这也就意味着，大多数的SUBURST后门永远都没有执行通过感染过程的第一个阶段。尽管如此，攻击者还是会对某些目标用户执行到感染的第二个阶段。在这个阶段中，攻击者会使用“C2协调器”，并通过响应一个指向下列IP地址范围的DNS
A记录来进行下一个阶段的感染和攻击：

    
    
    18.130.0.0/16
    
    99.79.0.0/16
    
    184.72.0.0/15

已经进入第二个感染阶段的SUNBURST后门将允许DNS响应中的CNAME记录用作新的C2域。

![](https://image.3001.net/images/20210106/1609920903_5ff571874163d90e54239.png!small)

我们通过研究发现，SUNBURST后门实际上使用了查询avsvmcloud.com网站子域请求中的一个位来标记它已进入感染的第二个阶段，并正在接受CNAME记录中的新C2域。该位在恶意SUNBURST植入后门中被称为
_flag_、 _ext_或 _dnssec_，这些数据可以从带有已编码时间戳的DNS查询中提取，比如说那些指示安装了哪些安全产品的查询。

## 检测感染第二阶段的DNS请求

我们的[
_SunburstDomainDecoder_](https://netresec.com/?b=20C0f71)工具现在已经更新，并在输出中引入了一个“STAGE2”标签来标记包含这个第二阶段的flag的DNS查询。这也就意味着，像CERTs这种专门执行安全事件响应协调和客户通知的国家性质的组织，现在就可以使用SunburstDomainDecoder来识别和通知已经进入第二阶段感染的目标SUNBURST受害者。

在下面的样例中，我们使用Bambenek的[ _uniq-hostnames.txt_](https://github.com/bambenek/research/blob/main/sunburst/uniq-hostnames.txt)被动DNS数据来运行SunburstDomainDecoder，并只会显示包含了“STAGE2”的相关内容：

    
    
    SunburstDomainDecoder.exe < uniq-hostnames.txt | findstr STAGE2
    
    22334A7227544B1E 2020-09-29T04:00:00.0000000Z,STAGE2 5qbtj04rcbp3tiq8bo6t
    
    FC07EB59E028D3EE 2020-06-13T09:00:00.0000000Z,STAGE2 6a57jk2ba1d9keg15cbg
    
    1D71011E992C3D68 2020-06-11T22:30:00.0000000Z,STAGE2 7sbvaemscs0mc925tb99
    
    F90BDDB47E495629 2020-06-13T08:30:00.0000000Z,STAGE2 gq1h856599gqh538acqn
    
    DB7DE5B93573A3F7 2020-06-20T02:30:00.0000000Z,STAGE2 ihvpgv9psvq02ffo77et
    
    3C327147876E6EA4 2020-07-22T17:00:00.0000000Z,STAGE2 k5kcubuassl3alrf7gm3
    
    3C327147876E6EA4 2020-07-23T18:30:00.0000000Z,STAGE2 mhdosoksaccf9sni9icp
    
    1D71011E992C3D68 central.pima.gov,STAGE2
    
    DB7DE5B93573A3F7 coxnet.cox.com,STAGE2,WindowsDefender
    
    F90BDDB47E495629 central.pima.gov,STAGE2

上述绝大多数的子域名都已经记录在了FireEye提供的[
_Indicator_Release_NBIs.csv_](https://github.com/fireeye/sunburst_countermeasures/blob/5ef085b175b8f7c70b1956fd310b05855a9098f6/indicator_release/Indicator_Release_NBIs.csv)文件中，其中包含了指向其他SUNBURST
C2域名的CNAME指针，比如说freescanonline[.]com、deftsecurity[.]com和thedoccloud[.]com等等，但第一个域名（GUID
22334A7227544B1E）其实并不属于FireEye的入侵威胁指标数据。

通过分析[ _其他被动DNS资源_](https://pastebin.com/6EDgCKxd)（例如[ _Rohit
Bansal_](https://twitter.com/0xrb)在pastebin上的被动DNS转储），我们将可以找到更多的STAGE2域和GUID值。

    
    
    curl -s https://pastebin.com/raw/6EDgCKxd | SunburstDomainDecoder.exe | findstr STAGE2
    
    E258332529826721 2020-07-18T05:00:00.0000000Z,STAGE2 1dbecfd99ku6fi2e5fjb
    
    2039AFE13E5307A1 2020-05-30T14:30:00.0000000Z,STAGE2 4n4vte5gmor7j9lpegsf
    
    22334A7227544B1E 2020-09-29T04:00:00.0000000Z,STAGE2 5qbtj04rcbp3tiq8bo6t
    
    FC07EB59E028D3EE 2020-06-13T09:00:00.0000000Z,STAGE2 6a57jk2ba1d9keg15cbg
    
    1D71011E992C3D68 2020-06-11T22:30:00.0000000Z,STAGE2 7sbvaemscs0mc925tb99
    
    1D71011E992C3D68 2020-06-11T22:30:00.0000000Z,STAGE2 7sbvaemscs0mc925tb99
    
    F90BDDB47E495629 2020-06-13T08:30:00.0000000Z,STAGE2 gq1h856599gqh538acqn
    
    F90BDDB47E495629 2020-06-13T08:30:00.0000000Z,STAGE2 gq1h856599gqh538acqn
    
    DB7DE5B93573A3F7 2020-06-20T02:30:00.0000000Z,STAGE2 ihvpgv9psvq02ffo77et
    
    DB7DE5B93573A3F7 2020-06-20T02:30:00.0000000Z,STAGE2 ihvpgv9psvq02ffo77et
    
    3C327147876E6EA4 2020-07-23T18:30:00.0000000Z,STAGE2 mhdosoksaccf9sni9icp

在删除FireEye的IoC文件中已经存在的域和几个伪造的域之后，我们得到了SUNBURST后门在STAGE2中请求的以下FQDN：

    
    
    1dbecfd99ku6fi2e5fjb.appsync-api.us-east-1.avsvmcloud.com
    
    4n4vte5gmor7j9lpegsf.appsync-api.eu-west-1.avsvmcloud.com
    
    5qbtj04rcbp3tiq8bo6t.appsync-api.us-east-1.avsvmcloud.com

能够访问更多被动DNS资源的公司和组织将有望使用SunburstDomainDecoder来识别更多已发展到第二阶段的目标SUNBURST受害者。

## 下载SunburstDomainDecoder

广大用户可以点击【[
_这里_](https://www.netresec.com/files/SunburstDomainDecoder.zip)】下载和使用SunburstDomainDecoder。

