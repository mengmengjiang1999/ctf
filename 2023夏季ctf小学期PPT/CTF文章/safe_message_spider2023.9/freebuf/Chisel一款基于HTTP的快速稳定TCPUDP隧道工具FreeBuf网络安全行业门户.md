**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

![](https://image.3001.net/images/20210329/1616999598_606174aeac113249f3398.png!small)

## 关于Chisel

Chisel是一个快速稳定的TCP/UDP隧道工具，该工具基于HTTP实现其功能，并通过SSH保证通信安全。Chisel是一个可执行文件，其中包含了客户端和服务器端，该工具基于Go（golang）语言开发，因此具备较好的跨平台特性。

Chisel主要可以用于绕过防火墙，但也可以用于向网络中提供安全终端节点。

 **工具的运行机制如下图所示：**

![](https://image.3001.net/images/20210329/1616999610_606174ba979c69ef2f67b.png!small)

## 功能介绍

> 易于使用；
>
> 高性能；
>
> 使用SSH协议对通信连接进行加密（通过crypto/SSH）；
>
> 连接经过身份验证；
>
> 通过用户配置文件进行身份验证的客户端；
>
> 通过用户配置文件进行身份验证的客户端连接；
>
> 通过指纹匹配进行身份验证的服务器连接；
>
> 客户端使用指数回退自动重新连接；
>
> 客户端可以通过一个TCP连接创建多个隧道端点；
>
> 客户端可以选择通过SOCKS或HTTP连接代理；
>
> 反向端口转发；
>
> 服务器反向代理；
>
> 服务器允许SOCKS5连接；
>
> 客户端可以选择允许从反向端口进行SOCKS5连接；
>
> 支持ssh-o ProxyCommand通过HTTP提供SSH加密；

## 工具安装

### 源码安装

广大研究人员可以点击【https://github.com/jpillora/chisel/releases/latest】访问该项目的Releases页面下载并安装该工具的最新版本，或运行下列命令：

    
    
    curl https://i.jpillora.com/chisel! | bash

### Docker安装

    
    
    docker run --rm -it jpillora/chisel --help

### Fedora

该项目包目前由Fedora社区进行维护，如果你遇到了关于RPM使用的问题，可以使用这个问题跟踪工具【https://bugzilla.redhat.com/buglist.cgi?bug_status=NEW&bug_status=ASSIGNED&classification=Fedora&component=chisel&list_id=11614537&product=Fedora&product=Fedora%20EPEL】

    
    
    sudo dnf -y install chisel

### 源安装

    
    
    $ go get -v github.com/jpillora/chisel

## 工具使用

    
    
    $ chisel --help
    
     
    
      Usage: chisel [command] [--help]
    
     
    
      Version: X.Y.Z
    
     
    
      Commands:
    
        server - runs chisel in server mode
    
        client - runs chisel in client mode
    
     
    
      Read more:
    
    https://github.com/jpillora/chisel
    
    
    $ chisel server --help
    
     
    
      Usage: chisel server [options]
    
     
    
      Options:
    
     
    
        --host, Defines the HTTP listening host – the network interface
    
        (defaults the environment variable HOST and falls back to 0.0.0.0).
    
     
    
        --port, -p, Defines the HTTP listening port (defaults to the environment
    
        variable PORT and fallsback to port 8080).
    
     
    
        --key, An optional string to seed the generation of a ECDSA public
    
        and private key pair. All communications will be secured using this
    
        key pair. Share the subsequent fingerprint with clients to enable detection
    
        of man-in-the-middle attacks (defaults to the CHISEL_KEY environment
    
        variable, otherwise a new key is generate each run).
    
     
    
        --authfile, An optional path to a users.json file. This file should
    
        be an object with users defined like:
    
          {
    
            "<user:pass>": ["<addr-regex>","<addr-regex>"]
    
          }
    
        when <user> connects, their <pass> will be verified and then
    
        each of the remote addresses will be compared against the list
    
        of address regular expressions for a match. Addresses will
    
        always come in the form "<remote-host>:<remote-port>" for normal remotes
    
        and "R:<local-interface>:<local-port>" for reverse port forwarding
    
        remotes. This file will be automatically reloaded on change.
    
     
    
        --auth, An optional string representing a single user with full
    
        access, in the form of <user:pass>. It is equivalent to creating an
    
        authfile with {"<user:pass>": [""]}. If unset, it will use the
    
        environment variable AUTH.
    
     
    
        --keepalive, An optional keepalive interval. Since the underlying
    
        transport is HTTP, in many instances we'll be traversing through
    
        proxies, often these proxies will close idle connections. You must
    
        specify a time with a unit, for example '5s' or '2m'. Defaults
    
        to '25s' (set to 0s to disable).
    
     
    
        --backend, Specifies another HTTP server to proxy requests to when
    
        chisel receives a normal HTTP request. Useful for hiding chisel in
    
        plain sight.
    
     
    
        --socks5, Allow clients to access the internal SOCKS5 proxy. See
    
        chisel client --help for more information.
    
     
    
        --reverse, Allow clients to specify reverse port forwarding remotes
    
        in addition to normal remotes.
    
     
    
        --tls-key, Enables TLS and provides optional path to a PEM-encoded
    
        TLS private key. When this flag is set, you must also set --tls-cert,
    
        and you cannot set --tls-domain.
    
     
    
        --tls-cert, Enables TLS and provides optional path to a PEM-encoded
    
        TLS certificate. When this flag is set, you must also set --tls-key,
    
        and you cannot set --tls-domain.
    
     
    
        --tls-domain, Enables TLS and automatically acquires a TLS key and
    
        certificate using LetsEncypt. Setting --tls-domain requires port 443.
    
        You may specify multiple --tls-domain flags to serve multiple domains.
    
        The resulting files are cached in the "$HOME/.cache/chisel" directory.
    
        You can modify this path by setting the CHISEL_LE_CACHE variable,
    
        or disable caching by setting this variable to "-". You can optionally
    
        provide a certificate notification email by setting CHISEL_LE_EMAIL.
    
     
    
        --tls-ca, a path to a PEM encoded CA certificate bundle or a directory
    
        holding multiple PEM encode CA certificate bundle files, which is used to
    
        validate client connections. The provided CA certificates will be used
    
        instead of the system roots. This is commonly used to implement mutual-TLS.
    
     
    
        --pid Generate pid file in current working directory
    
     
    
        -v, Enable verbose logging
    
     
    
        --help, This help text
    
     
    
      Signals:
    
        The chisel process is listening for:
    
          a SIGUSR2 to print process stats, and
    
          a SIGHUP to short-circuit the client reconnect timer
    
     
    
      Version:
    
        X.Y.Z
    
     
    
      Read more:
    
        https://github.com/jpillora/chisel
    
    
    $ chisel client --help
    
     
    
      Usage: chisel client [options] <server> <remote> [remote] [remote] ...
    
     
    
      <server> is the URL to the chisel server.
    
     
    
      <remote>s are remote connections tunneled through the server, each of
    
      which come in the form:
    
     
    
        <local-host>:<local-port>:<remote-host>:<remote-port>/<protocol>
    
     
    
        ■ local-host defaults to 0.0.0.0 (all interfaces).
    
        ■ local-port defaults to remote-port.
    
        ■ remote-port is required*.
    
        ■ remote-host defaults to 0.0.0.0 (server localhost).
    
        ■ protocol defaults to tcp.
    
     
    
      which shares <remote-host>:<remote-port> from the server to the client
    
      as <local-host>:<local-port>, or:
    
     
    
        R:<local-interface>:<local-port>:<remote-host>:<remote-port>/<protocol>
    
     
    
      which does reverse port forwarding, sharing <remote-host>:<remote-port>
    
      from the client to the server's <local-interface>:<local-port>.
    
     
    
        example remotes
    
     
    
          3000
    
          example.com:3000
    
          3000:google.com:80
    
          192.168.0.5:3000:google.com:80
    
          socks
    
          5000:socks
    
          R:2222:localhost:22
    
          R:socks
    
          R:5000:socks
    
          stdio:example.com:22
    
          1.1.1.1:53/udp
    
     
    
        When the chisel server has --socks5 enabled, remotes can
    
        specify "socks" in place of remote-host and remote-port.
    
        The default local host and port for a "socks" remote is
    
        127.0.0.1:1080. Connections to this remote will terminate
    
        at the server's internal SOCKS5 proxy.
    
     
    
        When the chisel server has --reverse enabled, remotes can
    
        be prefixed with R to denote that they are reversed. That
    
        is, the server will listen and accept connections, and they
    
        will be proxied through the client which specified the remote.
    
        Reverse remotes specifying "R:socks" will listen on the server's
    
        default socks port (1080) and terminate the connection at the
    
        client's internal SOCKS5 proxy.
    
     
    
        When stdio is used as local-host, the tunnel will connect standard
    
        input/output of this program with the remote. This is useful when
    
        combined with ssh ProxyCommand. You can use
    
          ssh -o ProxyCommand='chisel client chiselserver stdio:%h:%p' \
    
              user@example.com
    
        to connect to an SSH server through the tunnel.
    
     
    
      Options:
    
     
    
        --fingerprint, A *strongly recommended* fingerprint string
    
        to perform host-key validation against the server's public key.
    
    Fingerprint mismatches will close the connection.
    
    Fingerprints are generated by hashing the ECDSA public key using
    
    SHA256 and encoding the result in base64.
    
    Fingerprints must be 44 characters containing a trailing equals (=).
    
     
    
        --auth, An optional username and password (client authentication)
    
        in the form: "<user>:<pass>". These credentials are compared to
    
        the credentials inside the server's --authfile. defaults to the
    
        AUTH environment variable.
    
     
    
        --keepalive, An optional keepalive interval. Since the underlying
    
        transport is HTTP, in many instances we'll be traversing through
    
        proxies, often these proxies will close idle connections. You must
    
        specify a time with a unit, for example '5s' or '2m'. Defaults
    
        to '25s' (set to 0s to disable).
    
     
    
        --max-retry-count, Maximum number of times to retry before exiting.
    
        Defaults to unlimited.
    
     
    
        --max-retry-interval, Maximum wait time before retrying after a
    
        disconnection. Defaults to 5 minutes.
    
     
    
        --proxy, An optional HTTP CONNECT or SOCKS5 proxy which will be
    
        used to reach the chisel server. Authentication can be specified
    
        inside the URL.
    
        For example, http://admin:password@my-server.com:8081
    
                or: socks://admin:password@my-server.com:1080
    
     
    
        --header, Set a custom header in the form "HeaderName: HeaderContent".
    
        Can be used multiple times. (e.g --header "Foo: Bar" --header "Hello: World")
    
     
    
        --hostname, Optionally set the 'Host' header (defaults to the host
    
        found in the server url).
    
     
    
        --tls-ca, An optional root certificate bundle used to verify the
    
        chisel server. Only valid when connecting to the server with
    
        "https" or "wss". By default, the operating system CAs will be used.
    
     
    
        --tls-skip-verify, Skip server TLS certificate verification of
    
        chain and host name (if TLS is used for transport connections to
    
        server). If set, client accepts any TLS certificate presented by
    
        the server and any host name in that certificate. This only affects
    
        transport https (wss) connection. Chisel server's public key
    
        may be still verified (see --fingerprint) after inner connection
    
        is established.
    
     
    
        --tls-key, a path to a PEM encoded private key used for client
    
        authentication (mutual-TLS).
    
     
    
        --tls-cert, a path to a PEM encoded certificate matching the provided
    
        private key. The certificate must have client authentication
    
        enabled (mutual-TLS).
    
     
    
        --pid Generate pid file in current working directory
    
     
    
        -v, Enable verbose logging
    
     
    
        --help, This help text
    
     
    
      Signals:
    
        The chisel process is listening for:
    
          a SIGUSR2 to print process stats, and
    
          a SIGHUP to short-circuit the client reconnect timer
    
     
    
      Version:
    
        X.Y.Z
    
     
    
      Read more:
    
    https://github.com/jpillora/chisel

## 工具使用Demo

我们提供了一个Demo应用程序（https://chisel-demo.herokuapp.com/），它会运行这个chisel server：

    
    
    $ chisel server --port $PORT --proxy http://example.com
    
    # listens on $PORT, proxy web requests to http://example.com

这个Demo应用程序还会运行一个简单的文件服务器（端口为:3000），由于Heroku防火墙的存在，我们是无法直接访问它的。但是，我们可以通过隧道来实现访问：

    
    
    $ chisel client https://chisel-demo.herokuapp.com 3000
    
    # connects to chisel server at https://chisel-demo.herokuapp.com,
    
    # tunnels your localhost:3000 to the server's localhost:3000

接下来，打开浏览器并访问localhost:3000，此时我们将看到服务器的文件目录。

## 安全性

通信连接始终启用了加密。当你启动Chisel服务器时，它将会在内存中生成一个ECDSA公钥/私钥对。其中的公钥指纹（Base64编码的SHA256）将在服务器启动时显示。服务器可以选择使用
--key选项指定密钥种子，而不是生成随机密钥，该选项将用于为密钥生成种子。当客户端连接时，它们还将显示服务器的公钥指纹。客户端可以使用--fingerprint选项指定特定的指纹。

## 身份验证

使用--authfile选项，服务器可以选择提供用户.json配置文件以创建接受的用户访问列表。然后，客户端使用--auth选项进行身份验证。我们可以查看users.json以获取认证配置文件样例。使用--help查看更多帮助信息。

在内部，这是使用SSH提供的密码验证方法实现的。点击【http://blog.gopheracademy.com/go-and-ssh/﻿】了解更多关于SSH加密的信息。

## Socks5指引

1、开启你的Chisel服务器：

    
    
    docker run \
    
      --name chisel -p 9312:9312 \
    
      -d --restart always \
    
      jpillora/chisel server -p 9312 --socks5 --key supersecret

2、连接你的Chisel客户端（使用服务器的指纹信息）：

    
    
    chisel client --fingerprint 'rHb55mcxf6vSckL2AezFV09rLs7pfPpavVu++MF7AhQ=' <server-address>:9312 socks

3、指向你的Socks5客户端：

    
    
    <client-address>:1080

4、现在你的通信将被加密，并通过HTTP实现已认证的Socks5连接。

## 项目地址

Chisel：https://github.com/jpillora/chisel

