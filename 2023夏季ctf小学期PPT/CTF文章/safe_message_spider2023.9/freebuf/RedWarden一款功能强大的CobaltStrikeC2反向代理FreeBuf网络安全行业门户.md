![](https://image.3001.net/images/20210616/1623844671_60c9e73f281d8a1dff716.png!small)

## 关于RedWarden

RedWarden是一款功能强大的Cobalt Strike
C2反向代理，可以帮助广大研究人员通过数据包审查和CobaltStrike的Malleable配置关联分析实现针对蓝队、反病毒产品、终端安全响应系统（EDR）以及扫描器的抵御和对抗。

红队研究人员一直都在研究如何对抗事件响应工具的误导，尤其是涉及到C2重定向网络的时候。那么RedWarden将这些想法整合到了一个轻量级实用程序中，并能够模仿Apache2作为简单HTTP（s）反向代理。

## RedWarden运行机制

![](https://image.3001.net/images/20210616/1623844682_60c9e74ac0576767b59ce.png!small)

## 工具概述

RedWarden可以充当HTTP/HTTPS反向代理，并对入站C2
HTTP请求施加若干限制，选择将哪些数据包定向到Teamserver以及需要丢弃哪些数据包，类似于Apache2的mod_rewrite中强制执行的.htaccess文件限制。

RedWarden的创建是为了解决C2重定向器层上的IR/AV/EDRs/沙盒规避问题，它的目的是取代经典的Apache2+mod_rewrite设置。

根据以下三种策略，无效数据包可能会被错误路由：

  * 重定向：将节点重定向至其他网站；
  * 重置：直接中断TCP连接；
  * 代理：从其他网站获取响应，尽可能模仿被克隆/劫持的网站。

上述配置已在配置文件中设置好：

    
    
    #
    
    # What to do with the request originating not conforming to Beacon, whitelisting or
    
    # ProxyPass inclusive statements:
    
    #   - 'redirect' it to another host with (HTTP 301),
    
    #   - 'reset' a TCP connection with connecting client
    
    #   - 'proxy' the request, acting as a reverse-proxy against specified action_url
    
    #       (may be dangerous if client fetches something it shouldn't supposed to see!)
    
    #
    
    # Valid values: 'reset', 'redirect', 'proxy'.
    
    #
    
    # Default: redirect
    
    #
    
    drop_action: redirect

下面的样例中显示了将一个节点重定向至https://googole.com的输出结果：

![](https://image.3001.net/images/20210616/1623844703_60c9e75fce65057e68d17.png!small)

## 工具要求

该程序的当前版本仅支持在Linux系统上运行，并且支持多进程执行。

需要安装openssl系统命令，用于生成SSL证书。

最后，使用Python3 的pip命令安装所需的依赖组件：

    
    
    bash $ sudo pip3 install -r requirements.txt

## 工具使用

最精简版本的RedWarden配置文件config.yaml包含下列内容：

    
    
    port:
    
      - 80/http
    
      - 443/https
    
     
    
    profile: jquery-c2.3.14.profile
    
     
    
    ssl_cacert: /etc/letsencrypt/live/attacker.com/fullchain.pem
    
    ssl_cakey: /etc/letsencrypt/live/attacker.com/privkey.pem
    
     
    
    teamserver_url:
    
      - 1.2.3.4:8080
    
     
    
    drop_action: reset

接下来，需要在程序运行时提供配置文件的路径：

    
    
    bash$ sudo python3 RedWarden.py -c config.yaml
    
     
    
      [INFO] 19:21:42: Loading 1 plugin...
    
      [INFO] 19:21:42: Plugin "malleable_redirector" has been installed.
    
      [INFO] 19:21:42: Preparing SSL certificates and keys for https traffic interception...
    
      [INFO] 19:21:42: Using provided CA key file: ca-cert/ca.key
    
      [INFO] 19:21:42: Using provided CA certificate file: ca-cert/ca.crt
    
      [INFO] 19:21:42: Using provided Certificate key: ca-cert/cert.key
    
      [INFO] 19:21:42: Serving http proxy on: 0.0.0.0, port: 80...
    
      [INFO] 19:21:42: Serving https proxy on: 0.0.0.0, port: 443...
    
      [INFO] 19:21:42: [REQUEST] GET /jquery-3.3.1.min.js
    
      [INFO] 19:21:42: == Valid malleable http-get request inbound.
    
      [INFO] 19:21:42: Plugin redirected request from [code.jquery.com] to [1.2.3.4:8080]
    
      [INFO] 19:21:42: [RESPONSE] HTTP 200 OK, length: 5543
    
      [INFO] 19:21:45: [REQUEST] GET /jquery-3.3.1.min.js
    
      [INFO] 19:21:45: == Valid malleable http-get request inbound.
    
      [INFO] 19:21:45: Plugin redirected request from [code.jquery.com] to [1.2.3.4:8080]
    
      [INFO] 19:21:45: [RESPONSE] HTTP 200 OK, length: 5543
    
      [INFO] 19:21:46: [REQUEST] GET /
    
      [...]
    
      [ERROR] 19:24:46: [DROP, reason:1] inbound User-Agent differs from the one defined in C2 profile.
    
      [...]
    
      [INFO] 19:24:46: [RESPONSE] HTTP 301 Moved Permanently, length: 212
    
      [INFO] 19:24:48: [REQUEST] GET /jquery-3.3.1.min.js
    
      [INFO] 19:24:48: == Valid malleable http-get request inbound.
    
      [INFO] 19:24:48: Plugin redirected request from [code.jquery.com] to [1.2.3.4:8080]
    
      [...]

上面的输出中包含一行指向未授权、不兼容C2配置的入站请求，它会被丢弃：

    
    
    [...]
    
      [DROP, reason:1] inbound User-Agent differs from the one defined in C2 profile.
    
      [...]

## 工具运行截图

![](https://image.3001.net/images/20210616/1623844743_60c9e787a326ca98ae792.png!small)

## 项目地址

 **RedWarden：** 【[ _GitHub传送门_](https://github.com/mgeeky/RedWarden)】

