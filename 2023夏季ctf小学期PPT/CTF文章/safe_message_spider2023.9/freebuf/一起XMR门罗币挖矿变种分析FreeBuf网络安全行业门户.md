**近期观测到，Linux下DDG变种挖矿病毒又在全国范围内大规模爆发，该样本通过SSH爆破进行攻击，执行恶意程序，下
载伪装成图片的门罗币挖矿木马，设置为开机启动并在后台运行，木马在入侵计算机之后，以该计算机本地密钥登录known_hosts文件中的服务器进行横向渗透，攻击局域网中的其他机器并控制这些机器，使得这些无法正常提供业务，对该样本进行深入分析。**

## 0x00 样本介绍

样本基本信息：

**样本** | **MD5** | **内容**  
---|---|---  
xvfxprtb | e637e3252f452226c646079fcb6ac101 | 脚本下载图片样本  
1414297571.jpg | 35adcfb63017158c1f100201f850e8bd | 伪装成图片，包含挖矿程序和配置文件  
mysqlc_i686 | 18576051127ac0cc14664ba96c901dcb | 32位远控木马  
mysqlc_x86_64 | 2b95c896bea354a5a67cfcbd84fbb765 | 64位远控木马  
mysqli_i686 | 0c3dc9a67f879e5cc9849d128b16b866 | 32位挖矿程序  
mysqli_x86_64 | 784374992bddb9cf35aa92f098ec78b2 | 64位挖矿程序  
  
## 0x01 详细分析

xvfxprtb实际上是一个shell脚本，它是经过base64加密后的结果。

![](https://image.3001.net/images/20190618/1560822491_5d0842dbe61a4.png!small)

解密后得到shell脚本，该脚本的功能是下载1414297571.jpg样本，并将该图片样本重命名为mysqli.tar.gz，解压挖矿程序和程序的配置脚本，执行in脚本开始挖矿。

![](https://image.3001.net/images/20190618/1560822500_5d0842e44be4e.png!small)

解压mysqli.tar.gz后目录结构：

![](https://image.3001.net/images/20190618/1560822507_5d0842eb5b7b5.png!small)

执行in脚本，定时下载挖矿木马任务，每 15 分钟从 pastebin 上下载经过 base64 编码的脚本自身并执行，并设置成开机启动 。

![](https://image.3001.net/images/20190618/1560822512_5d0842f0c624c.png!small)

还包含了kill_sus_proc()函数，清理自身挖矿进程 ，并杀掉CPU大于30%的进程。

![](https://image.3001.net/images/20190618/1560822518_5d0842f6aed06.png!small)

该病毒通过识别内核版本，执行对应版本的病毒。

![](https://image.3001.net/images/20190618/1560822523_5d0842fb787a0.png!small)

判断挖矿程序的配置是否存在。

![](https://image.3001.net/images/20190618/1560822531_5d0843030799e.png!small)

读取.ssh目录下known_hosts中的服务器地址，尝试使用密钥登录后横向传播，攻击局域网中的其他机器并控制这些机器。

![](https://image.3001.net/images/20190618/1560822537_5d084309888a5.png!small)

查杀Stratum矿池协议的挖矿进程，使得自己独占CPU资源。

![](https://image.3001.net/images/20190618/1560822543_5d08430f96587.png!small)

清除历史命令、除日志、邮件和服务器登陆行为。

![](https://image.3001.net/images/20190618/1560822552_5d08431812b22.png!small)

矿机配置文件config.json如下：

    
    
    {
        "algo": "cryptonight",
        "api": {
            "port": 0,
            "access-token": null,
            "id": null,
            "worker-id": null,
            "ipv6": false,
            "restricted": true
        },
        "autosave": true,
        "av": 0,
        "background": true,
        "colors": false,
        "cpu-affinity": null,
        "cpu-priority": null,
        "donate-level": 1,
        "huge-pages": true,
        "hw-aes": null,
        "log-file": null,
        "max-cpu-usage": 75,
        "pools": [
            {
                "url":"xmr.pool.minergate.com:45700",
                "user":"nidaye222@protonmail.com",
                "pass": "x",
                "rig-id": null,
                "nicehash": false,
                "keepalive": false,
                "variant": -1,
                "enabled": true,
                "tls": false,
                "tls-fingerprint": null
            },
            {
                "url":"xmr-eu1.nanopool.org:14444",
                "user":"489N5AAY5igKmcD7gfYxmg6GrGJEXy46HbX23XRTHe1JYiSg4yo9iwBW9XcoCKaJ9xXbwBVSndKerbMvZdwoHMb23QyAFtz",
                "pass": "x",
                "rig-id": null,
                "nicehash": false,
                "keepalive": true,
                "variant": -1,
                "enabled": true,
                "tls": false,
                "tls-fingerprint": null
            },
            {
                "url":"xmr-asia1.nanopool.org:14444",
                "user":"489N5AAY5igKmcD7gfYxmg6GrGJEXy46HbX23XRTHe1JYiSg4yo9iwBW9XcoCKaJ9xXbwBVSndKerbMvZdwoHMb23QyAFtz",
                "pass": "x",
                "rig-id": null,
                "nicehash": false,
                "keepalive": true,
                "variant": -1,
                "enabled": true,
                "tls": false,
                "tls-fingerprint": null
            }
        ],
        "print-time": 60,
        "retries": 11,
        "retry-pause": 5,
        "safe": false,
        "threads": [
            {
                "low_power_mode": 1,
                "affine_to_cpu": false
            },
            {
                "low_power_mode": 1,
                "affine_to_cpu": false
            },
            {
                "low_power_mode": 1,
                "affine_to_cpu": false
            }
        ],
        "user-agent": null,
        "syslog": false,
        "watch": true
    }

矿池地址：xmr.pool.minergate.com:45700  

用户名：[nidaye222@protonmail.com](mailto:nidaye222@protonmail.com)

密码：x

矿池地址：xmr-eu1.nanopool.org:14444

用户名：

489N5AAY5igKmcD7gfYxmg6GrGJEXy46HbX23XRTHe1JYiSg4yo9iwBW9XcoCKaJ9xXbwBVSndKerbMvZdwoHMb23QyAFtz

密码：x

矿池地址：xmr-asia1.nanopool.org:14444

用户名：

489N5AAY5igKmcD7gfYxmg6GrGJEXy46HbX23XRTHe1JYiSg4yo9iwBW9XcoCKaJ9xXbwBVSndKerbMvZdwoHMb23QyAFtz

密码：x

通过挖矿钱包地址发现Pool: nanopoolPaid: 0 XMR，目前挖的门罗币为0。

![](https://image.3001.net/images/20190618/1560822683_5d08439bf1159.png!small)

## 0x02 解决方案

1、手动清除挖矿木马，删除病毒体rm-rf /tmp/.mysqli/,rm /tmp/mysqli.tar.gz

2、清理定时任务/var/spool/cron/crontabs

3、查杀挖矿进程，psauxf|grep -v grep|grep "mysqli"|awk '{print $2}'|xargs kill -9，ps
auxf|grep -v grep|grep " mysqlc"|awk'{print $2}'|xargs kill -9

4、清除开启自启动服务chkconfig--del in

5、采用高强度的密码，定期更换服务器密码。

## 0x03 相关IOC

### MD5

    
    
    e637e3252f452226c646079fcb6ac101
    35adcfb63017158c1f100201f850e8bd
    18576051127ac0cc14664ba96c901dcb
    2b95c896bea354a5a67cfcbd84fbb765
    0c3dc9a67f879e5cc9849d128b16b866
    784374992bddb9cf35aa92f098ec78b2

### C2

    
    
    122.114.196.38:43100

### URLs

    
    
    https://pastebin.com/raw/xvfxprtb http://m.jianlistore.com/images/qrcode/1414297571.jpg

*本文作者：Sampson，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。

