![](https://image.3001.net/images/20201014/1602685302_5f870976088baac1a5b2d.jpeg!small)

## 写在前面的话

2020年9月9日，Palo Alto Networks的研究人员发布了九份安全公告，并修复了PAN-OS操作系统v
8.0及其之前版本中存在的安全漏洞。其中一个漏洞就是CVE-2020-2040，这个漏洞在CVSS v3评分系统中的评分达到了9.8，即一个严重的高危漏洞。

PAN-OS设备一旦启用了Captive
Protal或多因素认证接口的话，则会受漏洞CVE-2020-2040的影响。一旦成功利用，未经认证的攻击者将能够通过向PAN-OS设备发送恶意请求来实现root提权。这个漏洞之所以会被标记为高危漏洞，主要出于两个原因。首先，它不需要任何身份认证；其次，该漏洞将允许攻击者中断系统进程并实现任意代码注入。

根据Shodan的搜索信息，目前网络上有五千多PAN-OS设备处于活跃状态，并且能够直接通过互联网访问。根据Qualys的内部分析报告，这些设备只有4%安装了修复补丁，因此各大组织需要认真对待这个漏洞，尽快修复该问题。

![](https://image.3001.net/images/20201014/1602685309_5f87097dc936a81ae25fd.png!small)

除了CVE-2020-2040之外，Palo Alto Networks还修复了下列漏洞：

![](https://image.3001.net/images/20201014/1602685332_5f8709940fc90170c8995.png!small)

受影响产品：

    
    
    PAN-OS 9.1
    
    PAN-OS 9.0
    
    PAN-OS 8.1
    
    PAN-OS 8.0

如需获取受影响设备的完整列表，请点击【[
_这里_](https://security.paloaltonetworks.com/CVE-2020-2040)】获取安全公告。

## 使用Qualys VMDR识别资产安全

第一步就是要识别资产风险，管理漏洞并降低安全影响，[ _Qualys
VMDR_](https://www.qualys.com/subscriptions/vmdr/?_ga=2.65897256.700746023.1601624982-1674633386.1601624982)可以帮助广大研究人员识别PAN-OS系统的安全性。

![](https://image.3001.net/images/20201014/1602685346_5f8709a2c2084fc4f53d0.png!small)

识别主机之后，Qualys VMDR将会使用一种动态标签来对主机进心分类，并标记“CVE-2020-2040”。

## 发现PAN-OS缓冲区溢出漏洞CVE-2020-2040

识别了PAN-OS主机之后，我们就需要检测这些资产并标记漏洞。而VMDR可以根据漏洞数据库来自动检测类似CVE-2020-2040这样的新型漏洞，我们可以使用下列QQL查询语句来查看被标记了“CVE-2020-2040”的资产：

    
    
    vulnerabilities.vulnerability.qid:13975

上述查询将返回所有受影响主机的列表：

![](https://image.3001.net/images/20201014/1602685359_5f8709af2904f6d5f28a7.png!small)

QID 13975在签名版本VULNSIGS-2.4.986-2及其更高版本中可用，可以使用身份扫描来进行检测。除了QID
13975之外，Qualys还在漏洞知识库中发布了以下QID以帮助识别PAN-OS漏洞：

    
    
    QID 13975: Palo Alto Networks PAN-OS 缓冲区溢出漏洞
    
    QID 13971: Palo Alto Networks PAN-OS 反射型XSS漏洞
    
    QID 13977: Palo Alto Networks PAN-OS 拒绝服务漏洞Denial-Of-Service Vulnerability
    
    QID 13972: Palo Alto Networks PAN-OS 操作系统命令注入漏洞
    
    QID 13973: Palo Alto Networks PAN-OS 操作系统命令注入漏洞
    
    QID 13978: Palo Alto Networks PAN-OS 管理Web接口缓冲区溢出漏洞
    
    QID 13974: Palo Alto Networks PAN-OS 管理Web接口拒绝服务漏洞
    
    QID 13979: Palo Alto Networks PAN-OS 信息泄露漏洞
    
    QID 13980: Palo Alto Networks PAN-OS 信息泄露漏洞

![](https://image.3001.net/images/20201014/1602685395_5f8709d31c3e57899d654.png!small)

在VMDR的帮助下结合下列实时威胁指标，可以将CVE-2020-2040优先处理：

  * 远程代码执行；
  * 拒绝服务；
  * 大数据泄露；
  * 横向渗透；
  * 漏洞利用；

![](https://image.3001.net/images/20201014/1602685417_5f8709e95118c64ead462.png!small)

![](https://image.3001.net/images/20201014/1602685423_5f8709ef5d379c698cde5.png!small)

广大研究人员只需要点击受影响的资产，就可以查看到漏洞以及主机的详细信息了。

## 通过仪表盘追踪漏洞

通过使用VMDR仪表盘，我们可以追踪PAN-OS漏洞以及受影响主机的的状态，并进行实时管理：

![](https://image.3001.net/images/20201014/1602685438_5f8709fe7de5b14d830cd.png!small)

## 解决方案

建议广大用户尽快将PAN-OS升级至PAN-OS v8.1.15、PAN-OS v9.0.9和PAN-OS v9.1.3及其更高版本。

## 快速扫描

广大研究人员可以点击【[
_这里_](https://www.qualys.com/subscriptions/vmdr/?_ga=2.260370315.700746023.1601624982-1674633386.1601624982)】获取Qualys
VMDR，快速开始漏洞的扫描与检测，并修复PAN-OS漏洞CVE-2020-2040。

