## 关于Melody

Melody是一款功能强大的透明互联网传感器，该工具专为威胁情报而设计，支持自定义标记规则，并且可以模拟存在安全漏洞的应用程序。该工具基于一款检测规则框架实现其功能，并允许广大研究人员标记感兴趣的数据包，以便对其进行进一步的威胁分析和监控。

## 功能介绍

下面列出的是Melody支持的一些核心功能：

> 1、数据捕捉
>
> 2、支持编写检测规则并标记特定的数据包，以进行大规模分析；
>
> 3、使用内置HTTP/S服务器模拟易受攻击的网站；
>
> 4、支持IPv4和IPv6上的主要互联网协议；
>
> 5、支持在最低配置的V*PS上持久运行；
>
> 6、无需进行大量配置即可使用；
>
> 7、独立模式：仅使用命令行接口配置Melody；
>
> 8、灵活性强，易于扩展功能；
>
> 9、静态编译的二进制文件；
>
> 10、Docker镜像持续更新；

## 工具使用场景

### 互联网传感器

> 1、从互联网噪声中提取趋势和模式；
>
> 2、索引恶意活动、攻击尝试和目标扫描器；
>
> 3、监控新出现的威胁；
>
> 4、密切关注特定的威胁；

### 数据流分析

> 1、建立一个背景噪声数据文档；
>
> 2、捕捉、标记和重放可疑数据流中的恶意数据包；

## 工具下载

### 源码安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并进行代码构建：

    
    
    git clone https://github.com/bonjourmalware/melody /opt/melody
    
    cd /opt/melody
    
    make build

### 获取最新发布版本

我们还可以直接访问该项目的【[
_Releases页面_](https://github.com/bonjourmalware/melody/releases)】下载该工具最新的预构建版本。下载完成后，我们需要执行下列命令进行工具的配置和使用：

    
    
    make install               # Set default outfacing interface
    
    make cap                   # Set network capabilities to start Melody without elevated privileges
    
    make certs                 # Make self signed certs for the HTTPS fileserver
    
    make enable_all_rules      # Enable the default rules
    
    make service               # Create a systemd service to restart the program automatically and launch it at startup
    
     
    
    sudo systemctl stop melody  # Stop the service while we're configuring it

可以使用下列命令更新filter.bpf文件来过滤不需要的数据包：

    
    
    sudo systemctl start melody     # Start Melody
    
    sudo systemctl status melody    # Check that Melody is running    

日志文件将会存储在“/opt/melody/logs/melody.ndjson”路径中：

    
    
    tail -f /opt/melody/logs/melody.ndjson # | jq

### Docker使用

    
    
    make certs                           # Make self signed certs for the HTTPS fileserver
    
    make enable_all_rules                # Enable the default rules
    
    mkdir -p /opt/melody/logs
    
    cd /opt/melody/
    
     
    
    docker pull bonjourmalware/melody:latest
    
     
    
    MELODY_CLI="" # Put your CLI options here. Example : export MELODY_CLI="-s -i 'lo' -F 'dst port 5555' -o 'server.http.port: 5555'"
    
     
    
    docker run \
    
        --net=host \
    
        -e "MELODY_CLI=$MELODY_CLI" \
    
        --mount type=bind,source="$(pwd)/filter.bpf",target=/app/filter.bpf,readonly \
    
        --mount type=bind,source="$(pwd)/config.yml",target=/app/config.yml,readonly \
    
        --mount type=bind,source="$(pwd)/var",target=/app/var,readonly \
    
        --mount type=bind,source="$(pwd)/rules",target=/app/rules,readonly \
    
        --mount type=bind,source="$(pwd)/logs",target=/app/logs/ \
    
        bonjourmalware/melody

## 规则配置

参考样例如下：

    
    
    CVE-2020-14882 Oracle Weblogic Server RCE:
    
      layer: http
    
      meta:
    
        id: 3e1d86d8-fba6-4e15-8c74-941c3375fd3e
    
        version: 1.0
    
        author: BonjourMalware
    
        status: stable
    
        created: 2020/11/07
    
        modified: 2020/20/07
    
        description: "Checking or trying to exploit CVE-2020-14882"
    
        references:
    
          - "https://nvd.nist.gov/vuln/detail/CVE-2020-14882"
    
      match:
    
        http.uri:
    
          startswith|any|nocase:
    
            - "/console/css/"
    
            - "/console/images"
    
          contains|any|nocase:
    
            - "console.portal"
    
            - "consolejndi.portal?test_handle="
    
      tags:
    
        cve: "cve-2020-14882"
    
        vendor: "oracle"
    
        product: "weblogic"
    
    impact: "rce"

## 系统日志

下面给出的日志样例。是一个通过IPv4发送的Netcat TCP数据包，内容如下：

    
    
    {
    
      "tcp": {
    
        "window": 512,
    
        "seq": 1906765553,
    
        "ack": 2514263732,
    
        "data_offset": 8,
    
        "flags": "PA",
    
        "urgent": 0,
    
        "payload": {
    
          "content": "I made a discovery today. I found a computer.\n",
    
          "base64": "SSBtYWRlIGEgZGlzY292ZXJ5IHRvZGF5LiAgSSBmb3VuZCBhIGNvbXB1dGVyLgo=",
    
          "truncated": false
    
        }
    
      },
    
      "ip": {
    
        "version": 4,
    
        "ihl": 5,
    
        "tos": 0,
    
        "length": 99,
    
        "id": 39114,
    
        "fragbits": "DF",
    
        "frag_offset": 0,
    
        "ttl": 64,
    
        "protocol": 6
    
      },
    
      "timestamp": "2020-11-16T15:50:01.277828+01:00",
    
      "session": "bup9368o4skolf20rt8g",
    
      "type": "tcp",
    
      "src_ip": "127.0.0.1",
    
      "dst_port": 1234,
    
      "matches": {},
    
      "inline_matches": [],
    
      "embedded": {}
    
    }

## 工具运行截图

![](https://image.3001.net/images/20220423/1650707062_6263ca765ecc63ae30045.png!small)

## 工具使用演示

![](https://image.3001.net/images/20220423/1650707082_6263ca8a38362bc4bf683.gif)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/bonjourmalware/melody/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Melody：** 【[ _GitHub传送门_](https://github.com/bonjourmalware/melody)】

## 参考资料

> [
> _https://bonjourmalware.github.io/melody/quickstart/﻿_](https://bonjourmalware.github.io/melody/quickstart/)

