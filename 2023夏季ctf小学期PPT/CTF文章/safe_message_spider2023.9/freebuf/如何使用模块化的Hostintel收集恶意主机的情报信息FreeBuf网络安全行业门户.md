**今天给大家介绍的是一款模块化的Python应用程序，广大研究人员可使用这款工具来收集关于恶意主机的情报信息。**

![１.png](https://image.3001.net/images/20190314/1552528221_5c89b35dd8999.png!small)

## Hostintel

这款工具可以用来收集关于目标主机的各种情报信息，Hostintel以模块化的形式进行开发，因此广大用户可以轻松添加新的情报源。

Hostintel通过FQDN主机名、域名或IP地址来进行主机识别。这款工具的当前版本仅支持IPv4。输出数据为CSV格式，发动目的地为STDOUT，因此用户可以直接保存数据或将其转发至其他软件。由于数据的输出格式为CSV格式，所以广大用户还可以根据自己的需要来将数据导入到Excel表格或数据库系统中。

### 工具演示视频

### 帮助信息

    
    
    $python hostintel.py -h
    
    usage:hostintel.py [-h] [-a] [-d] [-v] [-p] [-s] [-c] [-t] [-o] [-i] [-r]
    
                        ConfigurationFile InputFile
    
     
    
    Modular application to look up host intelligence information. Outputs CSV to
    
    STDOUT.This application will not output information until it has finished all
    
    ofthe input.
    
     
    
    positional arguments:
    
      ConfigurationFile     Configuration file
    
      InputFile             Input file, one host per line (IP,domain, or FQDN
    
                            host name)
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -a, --all             Perform All Lookups.
    
      -d, --dns             DNS Lookup.
    
      -v, --virustotal      VirusTotal Lookup.
    
      -p, --passivetotal    PassiveTotal Lookup.
    
      -s, --shodan          Shodan Lookup.
    
      -c, --censys          Censys Lookup.
    
      -t, --threatcrowd     ThreatCrowd Lookup.
    
      -o, --otx             OTX by AlienVault Lookup.
    
      -i, --isc             Internet Storm Center DShieldLookup.
    
      -r, --carriagereturn  Use carriage returns with new lines on csv.

## 工具安装

首先，确保你计算机或安装设备的配置文件是正确的。这里需要在配置文件中添加你的API密钥和用户名。在运行该工具前，你还需要安装Python（该工具采用Python2开发，但理论上支持Python3）和Pip。在工具的使用过程中，我们还需要从GitHub上安装各种模块，因此git命令也是需要配置好的。对于任何一个平台来说，使用Git来安装软件都是非常方便的。接下来，安装Python依赖：

    
    
    $ pip install -r requirements.txt

如果你在macOS上安装遇到问题的话【[参考资料](http://stackoverflow.com/questions/31649390/python-requests-ssl-handshake-failure)】，，你可能还需要使用下列命令安装部分代码库：

    
    
    $ pip install requests[security]

最后，我个人建议大家使用Python的virtualenv，来为该工具搭建自定义的本地Python环境：【[参考资料](http://docs.python-guide.org/en/latest/dev/virtualenvs/)】。

## 工具运行

    
    
    $python hostintel.py myconfigfile.conf myhosts.txt -a > myoutput.csv

该命令的输出文件：myoutput.csv理论上可以直接导入到任意数据库或电子表格中。

注意：如果你的网络连接质量较差的话，工具搜索数据的时间可能会比较长。因此建议用户在这种情况下每次只使用一个模块，并手动进行数据导出。

## 样本数据

我们已经在项目的“sampledata”目录中提供了一些简单的样本数据。其中的IP地址、域名和主机都是随机选取的，不针对特定组织或个人。样本数据的使用方法如下：

### 少量主机列表：

    
    
    $python hostintel.py local/config.conf sampledata/smalllist.txt -a >sampledata/smalllist.csv
    
    ***Processing 8.8.8.8 ***
    
    ***Processing 8.8.4.4 ***
    
    ***Processing 192.168.1.1 ***
    
    ***Processing 10.0.0.1 ***
    
    ***Processing google.com ***
    
    ***Processing 212.227.247.242 ***
    
    ***Writing Output ***

### 大量主机列表：

    
    
    $python hostintel.py local/config.conf sampledata/largerlist.txt -a >sampledata/largerlist.csv
    
    ***Processing 114.34.84.13 ***
    
    ***Processing 116.102.34.212 ***
    
    ***Processing 118.75.180.168 ***
    
    ***Processing 123.195.184.13 ***
    
    ***Processing 14.110.216.236 ***
    
    ***Processing 14.173.147.69 ***
    
    ***Processing 14.181.192.151 ***
    
    ***Processing 146.120.11.66 ***
    
    ***Processing 163.172.149.131 ***
    
     
    
    ...
    
     
    
    ***Processing 54.239.26.180 ***
    
    ***Processing 62.141.39.155 ***
    
    ***Processing 71.6.135.131 ***
    
    ***Processing 72.30.2.74 ***
    
    ***Processing 74.125.34.101 ***
    
    ***Processing 83.31.179.71 ***
    
    ***Processing 85.25.217.155 ***
    
    ***Processing 93.174.93.94 ***
    
    ***Writing Output ***

## 情报资源

大家可以从下列站点获取API密钥，并添加至项目的配置文件中：

> 1、 GeoLite2 (不需要网络I/O)：[http://www.maxmind.com](http://www.maxmind.com/)
>
> 2、 DNS (需要网络I/O)：<https://github.com/rthalley/dnspython>
>
> 3、 VirusTotal
> (需要公共API密钥和网络I/O)：[http://www.virustotal.com](http://www.virustotal.com/)
>
> 4、 PassiveTotal
> (需要API、用户名密钥和网络I/O)：[http://www.passivetotal.com](http://www.passivetotal.com/)
>
> 5、 Shodan (需要API密钥和网络I/O)：[http://www.shodan.io](http://www.shodan.io/)
>
> 6、 Censys (需要API、用户名密钥和网络I/O)：[http://www.censys.io](http://www.censys.io/)
>
> 7、 ThreatCrowd
> (需要网络I/O)：[http://www.threatcrowd.org](http://www.threatcrowd.org/)
>
> 8、 OTX by AlienVault
> (需要API密钥和网络I/O)：[https://otx.alienvault.com](https://otx.alienvault.com/)
>
> 9、 Internet Storm Center
> (需要网络I/O)：[https://isc.sans.edu](https://isc.sans.edu/)

## 代码库资源

1、GeoIP2 Python 库：

<https://github.com/maxmind/GeoIP2-python>

2、The Python DNS 库：

<https://github.com/rthalley/dnspython>

<http://www.iodigitalsec.com/performing-dns-queries-python/>

3、VirusTotal Python 库：

<https://github.com/blacktop/virustotal-api>

4、Shodan Python 库：

<http://shodan.readthedocs.io/en/latest/>

<https://github.com/achillean/shodan-python>

5、Censys Python 库：

<https://github.com/censys/censys-python>

<https://www.censys.io/api>

6、PassiveTotal Python 库：

<https://passivetotal.readthedocs.io/en/latest/>

<https://github.com/passivetotal/python_api>

7、ThreatCrowd Python 库

<https://github.com/threatcrowd/ApiV2>

<https://github.com/jheise/threatcrowd_api>

8、OTX Python 库：

<https://github.com/AlienVault-Labs/OTX-Python-SDK>

<https://otx.alienvault.com/api/>

9、Internet Storm CenterDShield Python 库

<https://github.com/rshipp/python-dshield>

<https://isc.sans.edu/api/>

## 项目地址

Hostintel：【[GitHub传送门](https://github.com/keithjjones/hostintel)】

***参考来源：[hostintel](https://github.com/keithjjones/hostintel)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

