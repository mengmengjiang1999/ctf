# centos7+suricata+redis+ELK

## 架构设计

### 1\. 需求

目前有一个针对网络流量的攻击日志回溯项目，要求部署一套支持全流量解析并快速检索的系统，计划是解析实时流量并将解析后的json日志存储到 ELK中。

  1. 要求包含比较详细的应用层信息，比如 HTTP 的URL、请求头、响应头、请求体和响应体。

  2. 支持实时抓包，并存储成pcap的功能，以供本地使用wireshark回溯分析。

  3. 支持在大流量背景下的全包存储能力，类似于tcpdump的抓包保存pcap功能。

  4. 支持网络流量的威胁检测能力

### 2\. 为什么选择 surcata？

suricata 主要用于企业业务流量的实时分析，是一款非常常用的 IDS 产品，也支持IPS 的功能，通过参数配置即可打开。

suricata 可以完成实时流量的解析，也可以使用离线模式读取pcap。

可以将实时流量抓包存储成pcap，也可以将以下的应用层流量解析成json。

    
    
    http, ftp, tls, smb, dns, dcerpc, ssh, smtp, imap, modbus, dnp3, enip, nfs, ikev2, krb5, ntp, dhcp, rfb, rdp, snmp, tftp, sip, http2
    

通过调研发现，suricata的应用层协议输出并不是全部的数据。比如，针对HTTP协议，suricata
无法识别存储HTTP的请求体和响应体，只能做到URL、请求头和响应头的解析和显示。

对比，同类型的产品 zeek，发现zeek也是默认不支持存储HTTP的请求体和响应体，但zeek的脚本功能可以自定义http的协议输出

参考
[流量分析的瑞士军刀：Zeek：https://www.cnblogs.com/cscshi/p/16582940.html](https://www.cnblogs.com/cscshi/p/16582940.html)

与此同时，suricata的
lua脚本功能也可以配置输出HTTP的请求体和响应体，但是还有一个更简单的方式，suricata的规则告警输出的http报文默认包含
HTTP请求体和响应体，通过修改配置文件即可在告警日志中出现 Base64 编码的请求体和响应体。

    
    
    types:
        - alert:
            http-body: yes           # Requires metadata; enable dumping of HTTP body in Base64
            # http-body-printable: yes # Requires metadata; enable dumping of HTTP body in printable format
    

使用的配置规则：

    
    
    alert http any any -> any any (msg:"HTTP protocol"; http.protocol; content:"HTTP/"; sid:3;)
    

另外一个关键点是，在大流量背景下，zeek是通过各种不同的脚本配置输出日志的， 会比较早的遇到性能瓶颈，毕竟所有流量都会挨个经过所有的脚本。

suricata如果启用 lua 脚本支持的话，也会遇到大流量的性能瓶颈，但在不启用lua脚本且规则数量较少的情况下，可以轻松应对3G/s

规模的实时流量，当然了，这跟机器的配置也有关系。

### 3\. 为什么选择redis作为消息队列？

suricata 支持将日志输出到文件、redis、syslog，但不支持输出到 kafka，但可以使用 reids 的 channel 模式，替代
kafka 的 topic 功能。

根据suricata支持的输出功能，通过网上搜索调研和阅读官方文档，统计有在五种比较好用的方式。

 **方式一：**

使用suricata将日志输出到 `eve.json`文件，然后使用logstash加载 eve.json 文件，并写入到
elasticsearch中。这个也是最常用的方式，网上的教程大多数都是这个方式。

特点：不会造成数据丢失，但 json 文件过多的话会严重占用磁盘空间，需要手动定期删除。

 **方式二：**

使用suricata将日志输出到 `suricata的kafka插件`，然后使用 kafka 写入到 elasticsearch中。

特点：kafka插件是python写的， 我没测试，有需要的话可以自己配置。

 **方式三：**

改写suricata的输出功能的源码，配置支持将日志输出到 `kafka`，然后使用 kafka 写入到 elasticsearch中。

[suricata
支持Kafka输出：https://www.jianshu.com/p/7877bed3684c](https://www.jianshu.com/p/7877bed3684c)

特点：改写源码，俺也不会啊，github有一个已经改写支持的kafka的suricata项目，但使用的是suricata4.0项目，
我没有测试。[kafka-feature-3105-v5](https://github.com/CosmosSun/suricata/tree/kafka-feature-3105-v5)

 **方式四：**

使用suricata将日志输出到`syslog`，然后使用logstash读取 syslog 数据，并写入到 elasticsearch中。

特点：syslog属于UDP协议的输出传输，会出现丢包情况，syslog没有消息队列的功能，如果后面的logstash或者elasticsearch服务异常的话，会导致数据丢失。

 **方式五：**

使用suricata将日志输出到`redis的 channel 模式`，然后使用logstash读取 redis 的 channel数据，并写入到
elasticsearch中。

特点：替代kafka的消息队列，使用redis的channel模式。消息队列的好处是如果后面的服务异常，但是数据没有消费的话，将一直在缓存中等待消费。

对比参考连接
[深入探究Kafka与Redis的对比https://www.dbs724.com/65282.html](https://www.dbs724.com/65282.html)

考虑到大流量的解析和入库问题，磁盘存储问题，搭建的方便性问题，最终决定采用`方式五`。

## 一、依赖环境

    
    
    系统环境：使用最小化安装的 centos7.8
    suricata：源码安装 suricata-6.0.10.tar.gz
    ELK：
        elasticsearch-8.7.0-x86_64.rpm
        kibana-8.7.0-x86_64.rpm
        logstash-8.7.0-x86_64.rpm
    需要依赖：
    	htp-0.5.17.tar.gz
    	LuaJIT-2.0.5.tar.gz
    

## 二、安装 suricata

### 1\. 安装依赖文件

这里采用源码安装的方式进行，便于自定义目录及组件

    
    
    yum install -y http://rpms.famillecollet.com/enterprise/remi-release-7.rpm
    yum install -y python3-pip git redis net-tools gcc libpcap-devel pcre-devel libyaml-devel file-devel zlib-devel jansson-devel nss-devel libcap-ng-devel libnet-devel tar make libnetfilter_queue-devel lua-devel PyYAML cargo libevent-devel libffi-devel libmaxminddb-devel lz4-devel openssl-devel python3-devel rustc unzip hiredis-devel kernel-devel -y
    

### 2\. 安装LuaJIT

用于替换suricata原生带有的 lua，效率更高，参考链接：
[lua与luaJit简介](https://blog.csdn.net/liao392781/article/details/97132095)

    
    
    wget http://luajit.org/download/LuaJIT-2.0.5.tar.gz
    tar -zxf LuaJIT-2.0.5.tar.gz
    cd LuaJIT-2.0.5/
    make && make install
    
    # 配置链接库
    echo "/usr/local/lib" >> /etc/ld.so.conf
    ldconfig
    

### 3\. 安装HTP库

LibHTP是HTTP协议和相关位的安全感知解析器，总的来说，是suricata的必要组件

    
    
    wget https://github.com/OISF/libhtp/releases/download/0.5.17/htp-0.5.17.tar.gz
    tar -xzvf htp-0.5.17.tar.gz
    cd htp-0.5.17
    ./configure
    make && make install
    

### 4\. 安装 suricata

Suricata是一个高性能的网络IDS、IPS和网络安全监控引擎。

Suricata安装在/usr/bin/下，相关配置在/etc/suricata/，日志输出在/var/log/suricata/下。

    
    
    # 编译
    tar zxvf suricata-6.0.10.tar.gz
    cd suricata-6.0.10/
    ./configure \
    --prefix=/usr \
    --sysconfdir=/etc \
    --localstatedir=/var \
    --enable-nfqueue \
    --enable-luajit \
    --with-libluajit-includes=/usr/local/include/luajit-2.0/ \
    --with-libluajit-libraries=/usr/local/lib/ \
    --enable-redis \
    --enable-hiredis \
    --enable-profiling \
    --enable-geoip \
    --enable-rust
    
    #--enable-lua \ #  liblua and luajit 不能共存
    #--enable-nfqueue #为内联IDP(启用NFQueue支持)启用NFQueue支持，一般开启Suricata的IPS模式时使用
    #--enable-profiling #启用性能分析
    

其他组件的支持，仅供参考

    
    
    # 加入PF_RING支持
    --enable-pfring #启用本机Pf_Ring的支持
    --with-libpfring-includes #libpfring的目录
    --with-libpfring-libraries #libpfring的库目录
    
    #Lua主要用来编写规则
    --enable-luajit #启用Luajit(C语言编写的Lua代码解析器)支持
    --with-libluajit-includes #libluajit的目录
    --with-libluajit-libraries #libluajit的库目录
    
    #使用scan(一个高性能的多重正则表达式匹配库)时，所需的库
    --with-libhs-includes #libhs的目录
    --with-libhs-libraries #libhs的库目录
    
    --with-libnss-libraries #libnss的目录
    --with-libnss-includes #libnss的库目录
    
    --with-libnspr-libraries #libnspr的目录
    --with-libnspr-includes #libnspr的库目录
    
    # 安装编译时用到的依赖组件
    yum -y install liblua5.1-dev #配置支持lua, --enable-lua
    yum -y install libgeoip-dev  #配置支持GeoIP, --enable-geoip
    yum -y install rustc cargo   #配置支持Rust, --enable-rust
    

安装

    
    
    make
    make install
    
    # 生成配置文件，会在/etc/suricata/下面生成新的配置文件
    make install-conf
    
    # 生成规则规则
    make install-rules
    
    # 全部生成
    make install-full
    

验证

    
    
    # 查看编译信息
    suricata --build-info
    
    # 启用测试 
    suricata -T
    

后台启动

    
    
    # 监听模式
    suricata -i ens33 -c /etc/suricata/suricata_multi.yaml -v -k none --runmode autofp -D
    
    # 离线读包模式
    suricata -i ens33 -r pcap_source_data/ -v -k none --runmode autofp
    
    -i ens33 # 指定网卡 
    -c /etc/suricata/suricata_multi.yaml # 指定配置文件
    --runmode autofp # 运行模式
    -D 后台运行
    

## 三、配置规则

在调试配置之前先编写一个规则文件，实现的功能很简单，就是将HTTP的协议全部输出成告警事件。

    
    
    mkdir /etc/suricata/rules/
    cd /etc/suricata/rules/
    
    vim suricata.rules
    alert http any any -> any any (msg:"HTTP protocol"; http.protocol; content:"HTTP/"; sid:3;)
    

在前面步骤中`make install-conf`，可以`/etc/suricata/`目录生成suricata的配置文件 `suricata.yaml`

修改配置文件，删除其他的规则，加载`suricata.rules`

    
    
    default-rule-path: /etc/suricata/rules
    
    rule-files:
      - suricata.rules
    

测试启动suricata，查看是否出现报错

    
    
    suricata -i ens33 -c /etc/suricata/suricata.yaml -T
    

没有报错的话就可以正式启动，修改配置文件，查看输出的文件。

    
    
    suricata -i ens33 -c /etc/suricata/suricata.yaml -v -k none --runmode autofp
    

## 四、配置 suricata输出

### 1\. 修改日志格式为json

默认输出位置在 `/etc/suricata`目录，修改文件 /etc/suricata/suricata.yaml。

    
    
    vim /etc/suricata/suricata.yaml
    
    # Define your logging outputs.  If none are defined, or they are all
      # disabled you will get the default: console output.
      outputs:
      - console:
          enabled: yes
          type: json
      - file:
          enabled: yes
          level: info
          filename: suricata.log
          type: json
      - syslog:
          enabled: no
          facility: local5
          format: "[%i] <%d> -- "
          type: json
    

### 2\. 开启pcap输出功能

    
    
    vim /etc/suricata/suricata.yaml
    
      - pcap-log:
          enabled: yes
          filename: listen.pcap
          limit: 1000mb
          max-files: 100    # 每个1G，100个是100G
          compression: none
          mode: sguil # normal, multi or sguil.
          dir: /data/suricata/pcaps/
          use-stream-depth: no # "no" logs all packets
          honor-pass-rules: no # If set to "yes", flows in which a pass rule matched will stop being logged.
    

### 3\. 启用所有协议的日志输出

参考官网： <https://suricata.readthedocs.io/en/suricata-6.0.10/output/eve/eve-json-format.html>

### 4\. 输出到 eve.json文件（本次不采用此模式）

输出到 eve.json 文件，可以很方便的调试配置文件的输出，可以通过文件的大小

在此用于解释多文件输出的用法，以方便理解后面的两个通道输出到 redis的过程。

参考官网：

[EVE JSON输出：https://www.osgeo.cn/suricata/output/eve/eve-json-output.html#output-types](https://www.osgeo.cn/suricata/output/eve/eve-json-output.html#output-types)

[文件权限：https://www.osgeo.cn/suricata/output/eve/eve-json-output.html#file-permissions](https://www.osgeo.cn/suricata/output/eve/eve-json-output.html#file-permissions)

[JSON标志：https://www.osgeo.cn/suricata/output/eve/eve-json-output.html#json-flags](https://www.osgeo.cn/suricata/output/eve/eve-json-output.html#json-flags)

suricata支持在日志输出的位置配置不同的输出器，这里先配置输出到json文件，后续输出到ELK中时需要改成输出到 redis 的 channel
模式。

可选配置文件的rotate，如设置每60分钟创建新文件，防止单个文件过大。

可选配置多进程输出到文件，文件名会以进程ID命名。

需要提前创建好日志输出`/data/suricata/protocol/`目录，否则会启动失败。

    
    
    vim /etc/suricata/suricata.yaml
    
    outputs:
      - eve-log:
          enabled: yes
          filetype: regular 	# 可选regular|syslog|unix_dgram|unix_stream|redis
          filename: /data/suricata/protocol/alert-%Y-%m-%d-%H:%M:%S.json
          filemode: 644
          json:
            preserve-order: yes
            compact: yes
            ensure-ascii: yes
            escape-slash: yes
          rotate-interval: 60m  # 60 minutes
          threaded: false
    

### 5\. 输出多个 eve.json 文件（用于理解多通道输出）

[多个记录器实例：https://www.osgeo.cn/suricata/output/eve/eve-json-output.html#multiple-logger-instances](https://www.osgeo.cn/suricata/output/eve/eve-json-output.html#multiple-logger-instances)

官方支持将不同的协议日志输出到不同的文件中，在output中配置同级的 eve-log 即可，但是官方并建议使用很多个独立的日志文件输出。

官方示例如下：

    
    
    outputs:
      - eve-log:
          enabled: yes
          filetype: regular 	# 可选regular|syslog|unix_dgram|unix_stream|redis
          filename: eve-ips.json
          types:
            - alert
            - drop
    
      - eve-log:
          enabled: yes
          filetype: regular 	# 可选regular|syslog|unix_dgram|unix_stream|redis
          filename: eve-nsm.json
          types:
            - http
            - dns
            - tls
    

实现思路很简单，就是将 `- eve-log: `并列多写几个，然后指定不同的输出即可。

复制配置文件到 suricata_multi.yaml，修改配置

    
    
    vim /etc/suricata/suricata_multi.yaml
    
    # 输出alert告警日志到 /data/suricata/protocol/alert-m-%d-%H:%M:%S.json，告警日志级别选择 Alert
      - eve-log:
          enabled: yes
          filetype: regular #regular|syslog|unix_dgram|unix_stream|redis
          filename: /data/suricata/protocol/alert-%Y-%m-%d-%H:%M:%S.json
          filemode: 644
          json:
            preserve-order: yes
            compact: yes
            ensure-ascii: yes
            escape-slash: yes
    
          rotate-interval: 60m  # 60 minutes
          threaded: false
          identity: "suricata"
          facility: local5
          level: Alert
    
          metadata: yes
          pcap-file: true
          community-id: true
          community-id-seed: 0
          xff:
            enabled: yes
            mode: extra-data
            deployment: reverse
            header: X-Forwarded-For
    
          types:
            - alert:
                payload: no
                packet: no
                metadata: yes
                http-body: yes
                tagged-packets: yes
                metadata:
                    app-layer: true
                    flow: false
                    rule:
                        metadata: false
                        raw: false
                xff:
                  enabled: yes
                  mode: extra-data
                  deployment: reverse
                  header: X-Forwarded-For
    # 输出协议日志到 /data/suricata/protocol/protocol-%Y-%m-%d-%H:%M:%S.json 文件，告警日志级别选择 Info
      - eve-log:
          enabled: yes
          filetype: regular #regular|syslog|unix_dgram|unix_stream|redis
          filename: /data/suricata/protocol/protocol-%Y-%m-%d-%H:%M:%S.json
          filemode: 644
          json:
            preserve-order: yes
            compact: yes
            ensure-ascii: yes
            escape-slash: yes
    
          rotate-interval: 60m  # 60 minutes
          threaded: false
          identity: "suricata"
          facility: local5
          level: Info
          ethernet: yes
          metadata: yes
          pcap-file: true
          community-id: true
          community-id-seed: 0
          xff:
            enabled: yes
            mode: extra-data
            deployment: reverse
            header: X-Forwarded-For
    
          types:
            - http:
                extended: yes
                dump-all-headers: both
            - dns:
                version: 2
                enabled: yes
                requests: yes
                responses: yes
                formats: [detailed, grouped]
                types: [a, ns, md, mf, cname, soa, mb, mg, mr, null, wks, ptr, hinfo, minfo, mx, txt, rp, afsdb, x25, isdn, rt, nsap, nsapptr, sig, key, px, gpos, aaaa, loc, nxt, srv, atma, naptr, kx, cert, a6, dname, opt, apl, ds, sshfp, ipseckey, rrsig, nsec, dnskey, dhcid, nsec3, nsec3param, tlsa, hip, cds, cdnskey, spf, tkey, tsig, maila, any, uri]
            - tls:
                extended: yes
                session-resumption: yes
                custom: [subject, issuer, session_resumed, serial, fingerprint, sni, version, not_before, not_after, certificate, chain, ja3, ja3s]
    

测试启动

    
    
    suricata -i ens33 -c /etc/suricata/suricata_multi.yaml -v -k none --runmode autofp
    

查看启动日志输出，存在 `All AFP capture threads are running.`即说明启动成功。

配置文件中的目录已经要先创建好，否则会启动失败。

在 `/data/suricata/protocol`可以看到输出的日志文件。

    
    
    [root@NTA protocol]# cd /data/suricata/protocol/
    [root@NTA protocol]# ls -l
    total 22785064
    -rw-r--r--. 1 root root           0 Apr 20 10:30 alert-2023-04-20-10:30:19.json
    -rw-r--r--. 1 root root           0 Apr 20 10:33 alert-2023-04-20-10:33:17.json
    -rw-r--r--. 1 root root        3865 Apr 20 10:33 protocol-2023-04-20-10:30:19.json
    -rw-r--r--. 1 root root        3859 Apr 20 10:34 protocol-2023-04-20-10:33:17.json
    

通过分析结果可以看到，确实是已经输出了新的文件，文件内容就是json数据。

    
    
    [root@NTA protocol]# tail protocol-2023-04-20-10:30:19.json -n1 | jq
    {
      "timestamp": "2023-04-20T10:33:15.336837+0800",
      "flow_id": 1817757461430226,
      "in_iface": "ens33",
      "event_type": "flow",
      "src_ip": "10.10.10.1",
      "src_port": 61063,
      "dest_ip": "10.10.10.135",
      "dest_port": 22,
      "proto": "TCP",
      "flow": {
        "pkts_toserver": 3,
        "pkts_toclient": 3,
        "bytes_toserver": 270,
        "bytes_toclient": 162,
        "start": "2023-04-20T10:30:30.835538+0800",
        "end": "2023-04-20T10:32:30.831269+0800",
        "age": 120,
        "state": "new",
        "reason": "shutdown",
        "alerted": false
      },
      "ether": {
        "dest_macs": [
          "00:0c:29:4f:81:53"
        ],
        "src_macs": [
          "00:50:56:c0:00:08"
        ]
      },
      "community_id": "1:z05uY2pXcMpfBOoYDWsPvPs4hdk=",
      "tcp": {
        "tcp_flags": "00",
        "tcp_flags_ts": "00",
        "tcp_flags_tc": "00"
      },
      "host": "suricata_sensor"
    }
    

到此，就说明整体的流程配置好了，既然有了json文件的输出，就可以使用logstash读取文件然后入库到 elasticsearch。

下一步，考虑到日志文件的存储会消耗磁盘空间，我们使用 redis 的订阅模式输出日志事件到logstash。

### 6\. 将数据输出到 redis 的订阅模式（推荐使用）

复制配置文件为`/etc/suricata/suricata_redis.yaml`，修改配置文件输出到 redis的`channel`模式

redis 的输出 频道为 `suricata_alert`和`suricata_protocol`

    
    
    vim /etc/suricata/suricata_redis.yaml
    
    # Configure the type of alert (and other) logging you would like.
    outputs:
      - eve-log:
          enabled: yes
          filetype: 			redis #regular|syslog|unix_dgram|unix_stream|redis
          identity: "suricata"
          facility: local5
          level: Alert 			## possible levels: Emergency, Alert, Critical, Error, Warning, Notice, Info, Debug
          ethernet: yes  		# log ethernet header in events when available
          redis:
            server: 127.0.0.1
            port: 6379
            async: true 		## if redis replies are read asynchronously
            mode: channel 		## possible values: list|lpush (default), rpush, channel|publish
                       			## lpush and rpush are using a Redis list. "list" is an alias for lpush
                       			## publish is using a Redis channel. "channel" is an alias for publish
            key: suricata_alert
            pipelining:
              enabled: yes
              batch-size: 10
    
          metadata: yes
          pcap-file: true
          community-id: true
          community-id-seed: 0
          xff:
            enabled: yes
            mode: extra-data
            deployment: reverse
            header: X-Forwarded-For
    
          types:
            - alert:
                payload: no
                packet: no              # enable dumping of packet (without stream segments)
                metadata: yes             # enable inclusion of app layer metadata with alert. Default yes
                http-body: yes           # Requires metadata; enable dumping of HTTP body in Base64
                tagged-packets: yes
                metadata:
                    app-layer: true
                    flow: false
                    rule:
                        metadata: false
                        raw: false
                xff:
                  enabled: yes
                  mode: extra-data
                  deployment: reverse
                  header: X-Forwarded-For
    
    
      # Extensible Event Format (nicknamed EVE) event log in JSON format
      - eve-log:
          enabled: yes
          filetype: redis 	#regular|syslog|unix_dgram|unix_stream|redis
          identity: "suricata"
          facility: local5
          level: Info 		## possible levels: Emergency, Alert, Critical, ## Error, Warning, Notice, Info, Debug
          ethernet: yes  	# log ethernet header in events when available
          redis:
            server: 127.0.0.1
            port: 6379
            async: true
            mode: channel 	## possible values: list|lpush (default), rpush, channel|publish
                       		## lpush and rpush are using a Redis list. "list" is an alias for lpush
                       		## publish is using a Redis channel. "channel" is an alias for publish
            key: suricata_protocol ## key or channel to use (default to suricata)
            pipelining:
              enabled: yes
              batch-size: 10
          metadata: yes
          pcap-file: true
          community-id: true
          community-id-seed: 0
    
          xff:
            enabled: yes
            mode: extra-data
            deployment: reverse
            header: X-Forwarded-For
    
          types:
            - http:
                extended: yes
                dump-all-headers: both
    
            - dns:
                version: 2
                enabled: yes
                requests: yes
                responses: yes
                formats: [detailed, grouped]
                types: [a, ns, md, mf, cname, soa, mb, mg, mr, null, wks, ptr, hinfo, minfo, mx, txt, rp, afsdb, x25, isdn, rt, nsap, nsapptr, sig, key, px, gpos, aaaa, loc, nxt, srv, atma, naptr, kx, cert, a6, dname, opt, apl, ds, sshfp, ipseckey, rrsig, nsec, dnskey, dhcid, nsec3, nsec3param, tlsa, hip, cds, cdnskey, spf, tkey, tsig, maila, any, uri]
    
            - tls:
                extended: yesd
                session-resumption: yes
                custom: [subject, issuer, session_resumed, serial, fingerprint, sni, version, not_before, not_after, certificate, chain, ja3, ja3s]
    

测试启动

    
    
    suricata -i ens33 -c /etc/suricata/suricata_redis.yaml -v -k none --runmode autofp
    

查看启动日志输出，存在 `All AFP capture threads are running.`即说明启动成功。

配置文件中的目录已经要先创建好，否则会启动失败。

在redis启动消费消息队列，监听suricata的输出 频道为 `suricata_alert`

    
    
    [root@NTA data]# redis-cli 
    127.0.0.1:6379> SUBSCRIBE suricata_alert
    Reading messages... (press Ctrl-C to quit)
    1) "subscribe"
    2) "suricata_alert"
    3) (integer) 1
    

虚拟机搭建的话可以使用科来的数据包播放器给虚拟机的网卡发包。

下载安装
[科来网络分析系统：https://www.colasoft.com.cn/download/capsa.php](https://www.colasoft.com.cn/download/capsa.php)

发包之后可以看到 redis 消费到了新的数据

    
    
    1) "message"
    2) "suricata_alert"
    3) "{\"timestamp\":\"2023-04-20T10:58:20.279310+0800\",\"flow_id\":1915493846657675,\"in_iface\":\"ens33\",\"event_type\":\"alert\",\"src_ip\":\"10.0.88.40\",\"src_port\":64452,\"dest_ip\":\"45.32.125.185\",\"dest_port\":80,\"proto\":\"TCP\",\"ether\":{\"src_mac\":\"f4:5c:89:b1:1d:bd\",\"dest_mac\":\"60:da:83:36:bb:e9\"},\"community_id\":\"1:CtewaAnze05BxdS8vTRNBawnYwI=\",\"tx_id\":0,\"alert\":{\"action\":\"allowed\",\"gid\":1,\"signature_id\":3,\"rev\":0,\"signature\":\"HTTP protocol\",\"category\":\"\",\"severity\":3},\"http\":{\"hostname\":\"45.32.125.185\",\"url\":\"/\",\"http_user_agent\":\"python-requests/2.6.2 CPython/2.7.10 Darwin/18.0.0\",\"http_content_type\":\"text/html\",\"http_method\":\"GET\",\"protocol\":\"HTTP/1.1\",\"status\":401,\"length\":459,\"http_response_body\":\"PCFET0NUWVBFIEhUTUwgUFVCTElDICItLy9JRVRGLy9EVEQgSFRNTCAyLjAvL0VOIj4KPGh0bWw+PGhlYWQ+Cjx0aXRsZT40MDEgVW5hdXRob3JpemVkPC90aXRsZT4KPC9oZWFkPjxib2R5Pgo8aDE+VW5hdXRob3JpemVkPC9oMT4KPHA+VGhpcyBzZXJ2ZXIgY291bGQgbm90IHZlcmlmeSB0aGF0IHlvdQphcmUgYXV0aG9yaXplZCB0byBhY2Nlc3MgdGhlIGRvY3VtZW50CnJlcXVlc3RlZC4gIEVpdGhlciB5b3Ugc3VwcGxpZWQgdGhlIHdyb25nCmNyZWRlbnRpYWxzIChlLmcuLCBiYWQgcGFzc3dvcmQpLCBvciB5b3VyCmJyb3dzZXIgZG9lc24ndCB1bmRlcnN0YW5kIGhvdyB0byBzdXBwbHkKdGhlIGNyZWRlbnRpYWxzIHJlcXVpcmVkLjwvcD4KPGhyPgo8YWRkcmVzcz5BcGFjaGUvMi40LjcgKFVidW50dSkgU2VydmVyIGF0IDQ1LjMyLjEyNS4xODUgUG9ydCA4MDwvYWRkcmVzcz4KPC9ib2R5PjwvaHRtbD4K\"},\"app_proto\":\"http\",\"host\":\"suricata_sensor\"}"
    

### 7\. logstash 订阅redis数据，并输出到 elasticsearch

ELK 的安装见上一章。[流量分析工具（一）：centos7安装ELK 8.7
并配置密码](https://www.freebuf.com/write/364192.html)

在此使用的elasticsearch已配置密码，需要在logstash里面配置。

由于是有两个频道输出日志，可以启用logstash 的
`pipelines`模式，配置文件`/usr/share/logstash/config/pipelines.yml`

    
    
    # /usr/share/logstash/config/pipelines.yml
    
    ##唯一id(标识用的)
    #- pipeline.id: logstash_test
    ##开启线程数量
    #  pipeline.workers: 10
    ##指定对应conf文件
    #  path.config: "/etc/logstash/conf.d/logstash_test.conf"
    - pipeline.id: suricata_alert
      pipeline.workers: 10
      queue.type: persisted
      path.config: "/etc/logstash/conf.d/logstash_alert.conf"
    
    - pipeline.id: suricata_protocol
      pipeline.workers: 10
      queue.type: persisted
      path.config: "/etc/logstash/conf.d/logstash_protocol.conf"
    

依据piplines读取的配置文件，编辑文件：

    
    
    # /etc/logstash/conf.d/logstash_alert.conf
    
    # 从redis读取
    input {
    	redis {
    		data_type => "pattern_channel"
    		key => "suricata_alert"
    		host => "127.0.0.1"
    		port => 6379
    		threads => 10
    	}
    }
    
    # 从文件读取
    # input
    # {
    #     file
    #     {
    #             path => ["/data/suricata/protocol/alert-*.json"]
    #             codec =>  "json"
    #             # sincedb_path => "NULL" 		# windows 的选择
    #             sincedb_path => "/dev/null"	# linux 的选择
    #             start_position => "beginning"
    #     }
    # }
    
    filter{
    	# 矫正 @timestamp 用于生成索引名的时间
    	ruby{
    	   code => "event.set('n_logstashStamp', (event.get('@timestamp').time.localtime + 8*60*60).strftime('%Y-%m-%d %H:%M:%S'))"
    	}
    	date {
    		 match => [ "n_logstashStamp", "yyyy-MM-dd HH:mm:ss" ]
    		 target => "@timestamp"
    	}
    	mutate  {
    		#将不需要的JSON字段过滤
    		remove_field => ["n_logstashStamp", "@version", "event", "log"]
    	}
    }
    
    # 输出elasticsearch，配置用户名和密码
    output {
        elasticsearch {
            hosts => ["http://127.0.0.1:9200"]
            index => "alert_%{+YYYYMMdd}"
    		user => elastic
    		password => "elastic_023"
    		timeout => 300
        }
    
    
    
    # /etc/logstash/conf.d/logstash_protocol.conf
    
    # 从redis读取
    input {
    	redis {
    		data_type => "pattern_channel"
    		key => "suricata_protocol"
    		host => "127.0.0.1"
    		port => 6379
    		threads => 10
    	}
    }
    
    # 从文件读取
    # input
    # {
    #     file
    #     {
    #             path => ["/data/suricata/protocol/protocol-*.json"]
    #             codec =>  "json"
    #             # sincedb_path => "NULL" 		# windows 的选择
    #             sincedb_path => "/dev/null"	# linux 的选择
    #             start_position => "beginning"
    #     }
    # }
    
    	filter{
    		# 矫正 @timestamp 用于生成索引名的时间
    	    ruby{
    		   code => "event.set('n_logstashStamp', (event.get('@timestamp').time.localtime + 8*60*60).strftime('%Y-%m-%d %H:%M:%S'))"
    		}
    		date {
    			 match => [ "n_logstashStamp", "yyyy-MM-dd HH:mm:ss" ]
    			 target => "@timestamp"
    		}
    		mutate  {
    			#将不需要的JSON字段过滤
    			remove_field => ["n_logstashStamp", "@version", "event", "log"]
    		}
    	}
    	
    # 输出elasticsearch，配置用户名和密码
    output {
        elasticsearch {
            hosts => ["http://127.0.0.1:9200"]
            index => "protocol_%{+YYYYMMdd}"
    		user => elastic
    		password => "elastic_023"
    		timeout => 300
        }
    

启用logstash，执行 /usr/share/logstash/bin/logstash ，启动程序

    
    
    [root@NTA config]# /usr/share/logstash/bin/logstash
    Using bundled JDK: /usr/share/logstash/jdk
    .......
    .......
    .......
    

遇到redis 的消息之后，logstash会自动入库，可以在kibana中查看索引和日志数据。

    
    
    # kibana的开发控制台中：
    
    GET _cat/indices
    
    yellow open protocol_20230419 h6kk5wMnThGfY96XXCcUnw 1 1 221962 0  46.8mb  46.8mb
    yellow open alert_20230420    I4Ev2UCxRDuY6SHW3i6IAg 1 1    710 0   3.7mb   3.7mb
    yellow open alert_20230419    9LlRi5yYQpy4kco2EbRenA 1 1   3130 0 805.7kb 805.7kb
    yellow open protocol_20230420 AqKtF6DBTQ-u3iyjZxPjfQ 1 1     60 0 177.1kb 177.1kb
    

至此已经搭建完成。

### 8\. suricata 全文配置文件

    
    
    %YAML 1.1
    ---    vars:
      address-groups:
        HOME_NET: "[192.168.0.0/16,10.0.0.0/8,172.16.0.0/12]"
        EXTERNAL_NET: "!$HOME_NET"
        HTTP_SERVERS: "$HOME_NET"
        SMTP_SERVERS: "$HOME_NET"
        SQL_SERVERS: "$HOME_NET"
        DNS_SERVERS: "$HOME_NET"
        TELNET_SERVERS: "$HOME_NET"
        AIM_SERVERS: "$EXTERNAL_NET"
        DC_SERVERS: "$HOME_NET"
        DNP3_SERVER: "$HOME_NET"
        DNP3_CLIENT: "$HOME_NET"
        MODBUS_CLIENT: "$HOME_NET"
        MODBUS_SERVER: "$HOME_NET"
        ENIP_CLIENT: "$HOME_NET"
        ENIP_SERVER: "$HOME_NET"
      port-groups:
        HTTP_PORTS: "80"
        SHELLCODE_PORTS: "!80"
        ORACLE_PORTS: 1521
        SSH_PORTS: 22
        DNP3_PORTS: 20000
        MODBUS_PORTS: 502
        FILE_DATA_PORTS: "[$HTTP_PORTS,110,143]"
        FTP_PORTS: 21
        GENEVE_PORTS: 6081
        VXLAN_PORTS: 4789
        TEREDO_PORTS: 3544
    	
    default-log-dir: /etc/suricata/log/
    stats:
      enabled: yes
      interval: 8
    
    outputs:
      - fast:
          enabled: no
          filename: fast.log
          append: yes
      - eve-log:
          enabled: yes
          filetype: redis #regular|syslog|unix_dgram|unix_stream|redis
    
    
          identity: "suricata"
          facility: local5
          level: Alert ## possible levels: Emergency, Alert, Critical, Error, Warning, Notice, Info, Debug
          ethernet: yes  # log ethernet header in events when available
          redis:
            server: 127.0.0.1
            port: 6379
            async: true ## if redis replies are read asynchronously
            mode: channel ## possible values: list|lpush (default), rpush, channel|publish
            key: suricata_alert ## key or channel to use (default to suricata)
    
            pipelining:
              enabled: yes ## set enable to yes to enable query pipelining
              batch-size: 10 ## number of entries to keep in buffer
          metadata: yes
          pcap-file: true
          community-id: true
          community-id-seed: 0
          xff:
            enabled: yes
            mode: extra-data
            deployment: reverse
            header: X-Forwarded-For
          types:
            - alert:
                payload: no             # enable dumping payload in Base64
                packet: no              # enable dumping of packet (without stream segments)
                metadata: yes             # enable inclusion of app layer metadata with alert. Default yes
                http-body: yes           # Requires metadata; enable dumping of HTTP body in Base64
                tagged-packets: yes
                metadata:
    
                    app-layer: true
    
                    flow: false
                    rule:
                        metadata: false
                        raw: false
    
                xff:
                  enabled: yes
                  mode: extra-data
                  deployment: reverse
                  header: X-Forwarded-For
    
      - eve-log:
          enabled: yes
          filetype: redis #regular|syslog|unix_dgram|unix_stream|redis
    
          identity: "suricata"
          facility: local5
          level: Info ## possible levels: Emergency, Alert, Critical,
          ethernet: yes  # log ethernet header in events when available
          redis:
            server: 127.0.0.1
            port: 6379
            async: true ## if redis replies are read asynchronously
            mode: channel ## possible values: list|lpush (default), rpush, channel|publish
            key: suricata_protocol ## key or channel to use (default to suricata)
    
            pipelining:
              enabled: yes ## set enable to yes to enable query pipelining
              batch-size: 10 ## number of entries to keep in buffer
    		
          metadata: yes
          pcap-file: true
          community-id: true
          community-id-seed: 0
          xff:
            enabled: yes
            mode: extra-data
            deployment: reverse
            header: X-Forwarded-For
          types:
            - anomaly:
                enabled: no
                types:
                  decode: yes
                  stream: yes
                  applayer: yes
                packethdr: yes
    
            - http:
                extended: yes     # enable this for extended logging information
                dump-all-headers: both
    
            - dns:
                version: 2
                enabled: yes
                requests: yes
                responses: yes
                formats: [detailed, grouped]
                types: [a, ns, md, mf, cname, soa, mb, mg, mr, null, wks, ptr, hinfo, minfo, mx, txt, rp, afsdb, x25, isdn, rt, nsap, nsapptr, sig, key, px, gpos, aaaa, loc, nxt, srv, atma, naptr, kx, cert, a6, dname, opt, apl, ds, sshfp, ipseckey, rrsig, nsec, dnskey, dhcid, nsec3, nsec3param, tlsa, hip, cds, cdnskey, spf, tkey, tsig, maila, any, uri]
    
            - tls:
                extended: yes     # enable this for extended logging information
                session-resumption: yes
                custom: [subject, issuer, session_resumed, serial, fingerprint, sni, version, not_before, not_after, certificate, chain, ja3, ja3s]
    
    
    
            - smtp:
                extended: yes # enable this for extended logging information
                custom: [received, x-mailer, x-originating-ip, relays, reply-to, bcc]
            - ftp
            - rdp
            - nfs
            - smb
            - tftp
            - ikev2
            - dcerpc
            - krb5
            - snmp
            - dhcp:
                enabled: yes
                extended: yes
            - ssh
            - mqtt:
                passwords: yes           # enable output of passwords
    
            - http2
            - flow
            - metadata
      - http-log:
          enabled: no
          filename: http.log
          append: yes
          extended: yes     # enable this for extended logging information
          custom: yes       # enable the custom logging format (defined by customformat)
          customformat: "%{%D-%H:%M:%S}t.%z %{X-Forwarded-For}i %H %m %h %u %s %B %a:%p -> %A:%P"
          filetype: regular # 'regular', 'unix_stream' or 'unix_dgram'
      - tls-log:
          enabled: no  # Log TLS connections.
          filename: tls.log # File to store TLS logs.
          append: yes
          extended: yes     # Log extended information like fingerprint
          custom: yes       # enabled the custom logging format (defined by customformat)
          customformat: "%{%D-%H:%M:%S}t.%z %a:%p -> %A:%P %v %n %d %D"
          filetype: regular # 'regular', 'unix_stream' or 'unix_dgram'
          session-resumption: yes
      - tls-store:
          enabled: no
          certs-log-dir: certs # directory to store the certificates files
      - pcap-log:
          enabled: yes
          filename: listen.pcap
          limit: 1000mb
          max-files: 100    # 100G
          compression: none
          mode: sguil # normal, multi or sguil.
          dir: /data/suricata/pcaps/
    
          use-stream-depth: no #If set to "yes" packets seen after reaching stream inspection depth are ignored. "no" logs all packets
          honor-pass-rules: no # If set to "yes", flows in which a pass rule matched will stop being logged.
      - alert-debug:
          enabled: no
          filename: alert-debug.log
          append: yes
      - alert-prelude:
          enabled: no
          profile: suricata
          log-packet-content: no
          log-packet-header: yes
      - stats:
          enabled: yes
          filename: stats.log
          append: yes       # append to file (yes) or overwrite it (no)
          totals: yes       # stats for all threads merged together
          threads: no       # per thread stats
      - syslog:
          enabled: no
          facility: local5
      - file-store:
          version: 2
          enabled: no
          dir: /data/suricata/filestore
          write-fileinfo: yes
          force-filestore: yes
          force-hash: [sha1, md5]
          xff:
            enabled: yes
            mode: extra-data
            deployment: reverse
            header: X-Forwarded-For
      - tcp-data:
          enabled: no
          type: both
          filename: tcp-data.log
      - http-body-data:
          enabled: no
          type: both
          filename: http-data.log
      - lua:
          enabled: no
          scripts:
    logging:
      default-log-level: notice
      default-output-filter:
      outputs:
      - console:
          enabled: yes
          type: json
      - file:
          enabled: yes
          level: info
          filename: suricata.log
          type: json
      - syslog:
          enabled: no
          facility: local5
          format: "[%i] <%d> -- "
          type: json
    af-packet:
      - interface: ens33
        threads: auto
        cluster-id: 99
        cluster-type: cluster_flow
        defrag: yes
      - interface: default
    pcap:
      - interface: ens33
      - interface: default
    pcap-file:
      checksum-checks: auto
    app-layer:
      protocols:
        rfb:
          enabled: yes
          detection-ports:
            dp: 5900, 5901, 5902, 5903, 5904, 5905, 5906, 5907, 5908, 5909
        mqtt:
          enabled: yes
        krb5:
          enabled: yes
        snmp:
          enabled: yes
        ikev2:
          enabled: yes
        tls:
          enabled: yes
          detection-ports:
            dp: 443
          ja3-fingerprints: yes
          encryption-handling: bypass
        dcerpc:
          enabled: yes
        ftp:
          enabled: yes
        rdp:
          enabled: yes
        ssh:
          enabled: yes
        http2:
          enabled: yes
          http1-rules: no
        smtp:
          enabled: yes
          raw-extraction: no
          mime:
            decode-mime: yes
            decode-base64: yes
            decode-quoted-printable: yes
            header-value-depth: 2000
            extract-urls: yes
            body-md5: no
          inspected-tracker:
            content-limit: 100000
            content-inspect-min-size: 32768
            content-inspect-window: 4096
        imap:
          enabled: detection-only
        smb:
          enabled: yes
          detection-ports:
            dp: 139, 445
        nfs:
          enabled: yes
        tftp:
          enabled: yes
        dns:
          tcp:
            enabled: yes
            detection-ports:
              dp: 53
          udp:
            enabled: yes
            detection-ports:
              dp: 53
        http:
          enabled: yes
          libhtp:
             default-config:
               personality: IDS
               request-body-limit: 100kb
               response-body-limit: 100kb
               request-body-minimal-inspect-size: 32kb
               request-body-inspect-window: 4kb
               response-body-minimal-inspect-size: 40kb
               response-body-inspect-window: 16kb
               response-body-decompress-layer-limit: 2
               http-body-inline: auto
               swf-decompression:
                 enabled: yes
                 type: both
                 compress-depth: 100kb
                 decompress-depth: 100kb
               double-decode-path: no
               double-decode-query: no
             server-config:
        modbus:
          enabled: no
          detection-ports:
            dp: 502
          stream-depth: 0
        dnp3:
          enabled: no
          detection-ports:
            dp: 20000
        enip:
          enabled: no
          detection-ports:
            dp: 44818
            sp: 44818
        ntp:
          enabled: yes
        dhcp:
          enabled: yes
        sip:
          enabled: yes
    asn1-max-frames: 256
    sensor-name: suricata_sensor
    pid-file: /etc/suricata/suricata.pid
    coredump:
      max-dump: unlimited
    host-mode: sniffer-only
    runmode: autofp
    default-packet-size: 1510
    unix-command:
      enabled: auto
    geoip-database: /etc/suricata/GeoLite2-Country.mmdb
    legacy:
      uricontent: enabled
    engine-analysis:
      rules-fast-pattern: yes
      rules: yes
    pcre:
      match-limit: 3500
      match-limit-recursion: 1500
    host-os-policy:
      windows: [0.0.0.0/0]
      bsd: []
      bsd-right: []
      old-linux: []
      linux: []
      old-solaris: []
      solaris: []
      hpux10: []
      hpux11: []
      irix: []
      macos: []
      vista: []
      windows2k3: []
    defrag:
      memcap: 32mb
      hash-size: 65536
      trackers: 65535 # number of defragmented flows to follow
      max-frags: 65535 # number of fragments to keep (higher than trackers)
      prealloc: yes
      timeout: 60
    flow:
      memcap: 128mb
      hash-size: 65536
      prealloc: 10000
      emergency-recovery: 30
    vlan:
      use-for-tracking: true
    flow-timeouts:
      default:
        new: 30
        established: 300
        closed: 0
        bypassed: 100
        emergency-new: 10
        emergency-established: 100
        emergency-closed: 0
        emergency-bypassed: 50
      tcp:
        new: 60
        established: 600
        closed: 60
        bypassed: 100
        emergency-new: 5
        emergency-established: 100
        emergency-closed: 10
        emergency-bypassed: 50
      udp:
        new: 30
        established: 300
        bypassed: 100
        emergency-new: 10
        emergency-established: 100
        emergency-bypassed: 50
      icmp:
        new: 30
        established: 300
        bypassed: 100
        emergency-new: 10
        emergency-established: 100
        emergency-bypassed: 50
    stream:
      memcap: 64mb
      checksum-validation: yes      # reject incorrect csums
      inline: auto                  # auto will use inline mode in IPS mode, yes or no set it statically
      reassembly:
        memcap: 256mb
        depth: 1mb                  # reassemble 1mb into a stream
        toserver-chunk-size: 2560
        toclient-chunk-size: 2560
        randomize-chunk-size: yes
    host:
      hash-size: 4096
      prealloc: 1000
      memcap: 32mb
    decoder:
      teredo:
        enabled: true
        ports: $TEREDO_PORTS # syntax: '[3544, 1234]' or '3533' or 'any'.
      vxlan:
        enabled: true
        ports: $VXLAN_PORTS # syntax: '[8472, 4789]' or '4789'.
      vntag:
        enabled: false
      geneve:
        enabled: true
        ports: $GENEVE_PORTS # syntax: '[6081, 1234]' or '6081'.
    detect:
      profile: medium
      custom-values:
        toclient-groups: 3
        toserver-groups: 25
      sgh-mpm-context: auto
      inspection-recursion-limit: 3000
      prefilter:
        default: mpm
      grouping:
      profiling:
        grouping:
          dump-to-disk: false
          include-rules: false      # very verbose
          include-mpm-stats: false
    mpm-algo: auto
    spm-algo: auto
    threading:
      set-cpu-affinity: no
      cpu-affinity:
        - management-cpu-set:
            cpu: [ 0 ]  # include only these CPUs in affinity settings
        - receive-cpu-set:
            cpu: [ 0 ]  # include only these CPUs in affinity settings
        - worker-cpu-set:
            cpu: [ "all" ]
            mode: "exclusive"
            prio:
              low: [ 0 ]
              medium: [ "1-2" ]
              high: [ 3 ]
              default: "medium"
      detect-thread-ratio: 1.0
    luajit:
      states: 128
    profiling:
      rules:
        enabled: no
        filename: rule_perf.log
        append: yes
        limit: 10
        json: yes
      keywords:
        enabled: no
        filename: keyword_perf.log
        append: yes
      prefilter:
        enabled: yes
        filename: prefilter_perf.log
        append: yes
      rulegroups:
        enabled: no
        filename: rule_group_perf.log
        append: yes
      packets:
        enabled: no
        filename: packet_stats.log
        append: yes
        csv:
          enabled: no
          filename: packet_stats.csv
      locks:
        enabled: no
        filename: lock_stats.log
        append: yes
      pcap-log:
        enabled: no
        filename: pcaplog_stats.log
        append: yes
    nfq:
    nflog:
      - group: 2
        buffer-size: 18432
      - group: default
        qthreshold: 1
        qtimeout: 100
        max-size: 20000
    capture:
    netmap:
     - interface: eth2
     - interface: default
    pfring:
      - interface: ens33
        threads: auto
        cluster-id: 99
        cluster-type: cluster_flow
      - interface: default
    ipfw:
    napatech:
        streams: ["0-3"]
        enable-stream-stats: no
        auto-config: yes
        hardware-bypass: yes
        inline: no
        ports: [0-1,2-3]
        hashmode: hash5tuplesorted
    default-rule-path: /etc/suricata/rules
    rule-files:
      - suricata.rules
    classification-file: /etc/suricata/classification.config
    reference-config-file: /etc/suricata/reference.config
    threshold-file: /etc/suricata/threshold.config
    

