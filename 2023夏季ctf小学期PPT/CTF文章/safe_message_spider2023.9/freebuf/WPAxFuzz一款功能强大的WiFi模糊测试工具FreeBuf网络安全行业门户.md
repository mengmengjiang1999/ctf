![](https://image.3001.net/images/20230826/1693045015_64e9d117644584362697a.png!small)  

## 关于WPAxFuzz

WPAxFuzz是一款功能强大的Wi-Fi模糊测试工具，该工具能够对802.11协议或SAE交换相关的管理、控制和数据帧执行模糊测试。对于管理、控制或数据帧，您可以选择“标准”模式，其中传输的所有帧都具有有效的大小值，也可以选择大小值为随机的“随机”模式。其中，SAE模糊测试操作需要一个支持WPA3的AP。

值得一提的是，该工具可以针对任何AP（WPA2或WPA3）执行管理、控制或数据帧模糊测试。而且该工具还实现了测试用的DoS攻击向量。总体而言，WPAxFuzz能够实现下列功能：

> 1、管理帧模糊测试；
>
> 2、SAE交换模糊测试；
>
> 3、控制帧模糊测试；
>
> 4、数据帧模糊测试（实验功能）；
>
> 5、DoS攻击测试模块；

## 工具要求

> Python 3.7
>
> Scapy 2.4.3
>
> Nmap 7.93
>
> Blab 1.0

## 工具配置

安装并配置好该工具所需的依赖组件之后，我们还需要探测本地网络以发现潜在目标：

    
    
    nmap -sP {ip_prefix}.*

Blab工具的配置如下：

    
    
    git clone https://haltp.org/git/blab.git
    
        cd blab/
    
        make
    
        cd {binary directory, where Blab is saved}                    ex. cd /bin/blab/bin
    
        cp blab {fuzzer directory}                                    ex. cp blab /home/kali/Desktop/WPAxFuzz

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/efchatz/WPAxFuzz.git

## 工具使用

首先，我们可以使用目标AP、相关STA MAC地址、AP的SSID和无线接口名称更新好配置文件。

然后将WNIC设置为监控器模式：

    
    
    sudo airmon-ng
    
        sudo airmon-ng check
    
        sudo airmon-ng check kill
    
        sudo airmon-ng start {NAME_OF_ATT_INTER}

将你WNIC的信道设置为目标AP所使用的传输信道：

    
    
    sudo airodump-ng {NAME_OF_ATT_INTER}
    
        sudo iw {NAME_OF_ATT_INTER} set channel {AP_channel} HT20

选择你要执行的操作：

> 1) 管理帧模糊测试
>
> 3) 控制帧模糊测试
>
> 4) 数据帧模糊测试（实验功能）

选择下列其中一个模式：

> 标准
>
> 随机

最后，执行模糊测试操作即可。

## 支持的漏洞

 ** **CVE IDs****

|

 ** **漏洞设备**** ** **/**** ** **芯片****

|

 ** **WPA2/WPA3-SAE****

|

 ** **状态****

|

 ** **评级****  
  
---|---|---|---|---  
  
[CVE-2022-32654](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-32654)

|

mt5221/mt7603/mt7613  
mt7615/mt7622/mt7628  
mt7629/mt7663/mt7668  
mt7682/mt7686/mt7687  
mt7697/mt7902/mt7915  
mt7916/mt7921/mt7933  
mt7981/mt7986/mt8167S  
mt8175/mt8362A/mt8365  
mt8385/mt8518S/mt8532  
mt8695/mt8696/mt8788

|

都支持

|

已发布

|

6.7 (中危)  
  
[CVE-2022-32655](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-32655)

|

mt5221/mt7603/mt7613  
mt7615/mt7622/mt7628  
mt7629/mt7663/mt7668  
mt7682/mt7686/mt7687  
mt7697/mt7902/mt7915  
mt7916/mt7921/mt7933  
mt7981/mt7986/mt8167S  
mt8175/mt8362A/mt8365  
mt8385/mt8518S/mt8532  
mt8695/mt8696/mt8788

|

都支持

|

已发布

|

6.7 (中危)  
  
[CVE-2022-32656](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-32656)

|

mt5221/mt7603/mt7613  
mt7615/mt7622/mt7628  
mt7629/mt7663/mt7668  
mt7682/mt7686/mt7687  
mt7697/mt7902/mt7915  
mt7916/mt7921/mt7933  
mt7981/mt7986/mt8167S  
mt8175/mt8362A/mt8365  
mt8385/mt8518S/mt8532  
mt8695/mt8696/mt8788

|

都支持

|

已发布

|

6.7 (中危)  
  
[CVE-2022-32657](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-32657)

|

mt7603/mt7613/mt7615  
mt7622/mt7628/mt7629  
mt7915/mt7916/mt7981  
mt7986

|

都支持

|

已发布

|

6.7 (中危)  
  
[CVE-2022-32658](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-32658)

|

mt7603/mt7613/mt7615  
mt7622/mt7628/mt7629  
mt7915/mt7916/mt7981  
mt7986

|

都支持

|

已发布

|

6.7 (中危)  
  
[CVE-2022-32659](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-32659)

|

mt7603/mt7613/mt7615  
mt7622/mt7628/mt7629  
mt7915/mt7916/mt7981  
mt7986/mt8518s/mt8532

|

都支持

|

已发布

|

6.7 (中危)  
  
[CVE-2022-46740](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-46740)

|

WS7100-20

|

都支持

|

已发布

|

6.5 (中危)  
  
[CVE-2022-32666](https://cve.mitre.org/cgi-bin/cvename.cgi?name=2022-32666)

|

mt7603/mt7613/mt7615  
mt7622/mt7628mt7629  
mt7915/mt7916/mt7981  
mt7986/mt8365

|

都支持

|

已发布

|

7.5 (高危)  
  
[CVE-2021-37910](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-37910)

|

All ASUS RX-based models

|

WPA3-SAE

|

已发布

|

5.3 (中危)  
  
[CVE-2021-40288](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-40288)

|

AX10v1

|

WPA3-SAE

|

已发布

|

7.5 (高危)  
  
[CVE-2021-41753](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-41753)

|

DIR-x1560/DIR-X6060

|

WPA3-SAE

|

已发布

|

7.5 (高危)  
  
[CVE-2021-41788](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-41788)

|

mt7603E/mt7612/mt7613  
mt7615/mt7622/mt7628  
mt7629/mt7915

|

WPA3-SAE

|

已发布

|

7.5 (高危)  
  
## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/efchatz/WPAxFuzz/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **WPAxFuzz** ：【[ _GitHub传送门_](https://github.com/efchatz/WPAxFuzz)】

## 参考资料

> [ _https://arxiv.org/abs/2302.05899_](https://arxiv.org/abs/2302.05899)
>
> [
> _https://www.sciencedirect.com/science/article/pii/S221421262100243X_](https://www.sciencedirect.com/science/article/pii/S221421262100243X)
>
> [ _https://www.sciencedirect.com/journal/journal-of-information-security-> and-> applications/about/awards_](https://www.sciencedirect.com/journal/journal-> of-information-security-and-applications/about/awards)
>
> [ _https://corp.mediatek.com/product-security-> acknowledgements_](https://corp.mediatek.com/product-security-> acknowledgements)
>
> [ _https://www.huawei.com/en/psirt/security-advisories/2022/huawei-sa-> dosvihswr-8f632df1-en_](https://www.huawei.com/en/psirt/security-> advisories/2022/huawei-sa-dosvihswr-8f632df1-en)

