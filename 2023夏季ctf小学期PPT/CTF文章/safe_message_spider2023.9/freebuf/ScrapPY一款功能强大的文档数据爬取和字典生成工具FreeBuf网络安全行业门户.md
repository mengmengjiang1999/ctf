![](https://image.3001.net/images/20230810/1691649196_64d484ac783164bbdd7d1.png!small)

## 关于ScrapPY

ScrapPY是一款功能强大的文档数据爬取和字典生成工具，该工具基于Python开发，可以帮助广大研究人员抓取手册、文档和其他敏感PDF，以生成安全工具可以直接使用的有针对性的字典列表来执行暴力破解、强制浏览和字典攻击。

ScrapPY可以执行词频、熵和元数据分析，并可以在全输出模式下运行，为有针对性的攻击创建自定义字典列表。该工具可以通过深入分析，发现潜在密码或隐藏目录的关键字和短语，生成可读的文本文件，并输出到Hydra、Dirb和Nmap等工具。

简而言之，在ScrapPY的帮助下，广大研究人员能够快速实现初始访问、漏洞扫描和横向移动。

## 工具安装

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python
3环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    $ mkdir ScrapPY
    
    $ cd ScrapPY/
    
    $ sudo git clone https://github.com/RoseSecurity/ScrapPY.git

然后切换到项目目录中，使用pip 3命令和项目提供的requirements.txt文件安装该工具所需的其他依赖组件：

    
    
    $ pip3 install -r requirements.txt

## 工具使用

    
    
    usage: ScrapPY.py [-h] [-f FILE] [-m {word-frequency,full,metadata,entropy}] [-o OUTPUT]

输出文档元数据：

    
    
    $ python3 ScrapPY.py -f example.pdf -m metadata

将前100个常用单词输出到名为Top_100_Keywords.txt的文件中：

    
    
    $ python3 ScrapPY.py -f example.pdf -m word-frequency -o Top_100_Keywords.txt

将所有的关键词输出到默认的ScrapPY.txt文件中：

    
    
    $ python3 ScrapPY.py -f example.pdf

将前100个熵最高的单词输出：

    
    
    $ python3 ScrapPY.py -f example.pdf -m entropy

ScrapPY输出结果：

    
    
    # ScrapPY outputs the ScrapPY.txt file or specified name file to the directory in which the tool was ran. To view the first fifty lines of the file, run this command:
    
     
    
    $ head -50 ScrapPY.txt
    
     
    
    # To see how many words were generated, run this command:
    
     
    
    $ wc -l ScrapPY.txt

## 与其他安全工具集成

该工具可以轻松与例如Dirb之类的其他安全工具进行集成，以加快发现隐藏子目录的过程：

    
    
    root@RoseSecurity:~# dirb http://192.168.1.123/ /root/ScrapPY/ScrapPY.txt
    
     
    
    -----------------    
    DIRB v2.21
    
    By The Dark Raver
    
    -----------------    
     
    
    START_TIME: Fri May 16 13:41:45 2014
    
    URL_BASE: http://192.168.1.123/
    
    WORDLIST_FILES: /root/ScrapPY/ScrapPY.txt
    
     
    
    -----------------    
     
    
    GENERATED WORDS: 4592
    
     
    
    ---- Scanning URL: http://192.168.1.123/ ----    
    ==> DIRECTORY: http://192.168.1.123/vi/
    
    + http://192.168.1.123/programming (CODE:200|SIZE:2726)
    
    + http://192.168.1.123/s7-logic/ (CODE:403|SIZE:1122)
    
    ==> DIRECTORY: http://192.168.1.123/config/
    
    ==> DIRECTORY: http://192.168.1.123/docs/
    
    ==> DIRECTORY: http://192.168.1.123/external/

将ScrapPY与Hydra一起使用可以执行高级暴力破解攻击：

    
    
    root@RoseSecurity:~# hydra -l root -P /root/ScrapPY/ScrapPY.txt -t 6 ssh://192.168.1.123
    
    Hydra v7.6 (c)2013 by van Hauser/THC & David Maciejak - for legal purposes only
    
     
    
    Hydra (http://www.thc.org/thc-hydra) starting at 2014-05-19 07:53:33
    
    [DATA] 6 tasks, 1 server, 1003 login tries (l:1/p:1003), ~167 tries per task
    
    [DATA] attacking service ssh on port 22

使用ScrapPY生成的字典与Nmap脚本结合使用：

    
    
    nmap -p445 --script smb-brute.nse --script-args userdb=users.txt,passdb=ScrapPY.txt 192.168.1.123

## 工具使用演示

 **演示视频** ：【[ _点我观看_](https://user-images.githubusercontent.com/72598486/201235531-6b037daf-d1f3-4d33-b256-8411e3a0b3da.mov)】

## 项目地址

 **ScrapPY** ：【[ _GitHub传送门_](https://github.com/RoseSecurity/ScrapPY)】

