![](https://image.3001.net/images/20220626/1656249955_62b85e63a10201de59bcf.jpeg!small)

## 关于MITM_Intercept

MITM_Intercept是一款功能强大的数据包编辑工具，MITM_Intercept可以通过Burp或其他具备SSL和TLS拦截功能的工具来拦截和修改非HTTP协议的数据包。该工具基于[
_mitm_relay_](https://github.com/jrmdev/mitm_relay)项目的理念实现，适用于客户端安全评估领域的渗透测试人员和安全研究专家。

## 工具运行机制

首先，我们需要配置侦听器的地址和端口。对于每个侦听器，还需要配置一个目标（地址和端口）。从侦听器接收到的每个数据都将打包到HTTP
POST请求的Body中，其中的URL将包含“CLIENT_REQUEST”。从目标接收到的每个数据都将打包到HTTP
POST请求的Body中，其中的URL将包含“SERVER_RESPONSE”。随后，这些请求都将被发送到本地HTTP拦截服务器。

我们可以选择配置HTTP代理，使用[ _Burp
Suite_](https://portswigger.net/burp)等工具作为HTTP拦截工具，并在那里查看消息。这样一来，我们就可以使用Burp的各种扩展来手动修改数据包消息了。

修改数据包的另一种方法就是使用一个Python脚本，HTTP拦截服务器在接收消息时将运行该脚本。

发送到HTTP拦截服务器的消息Body将打印到shell。如果给出修改脚本，修改后将打印消息。在所有修改操作完成之后，拦截服务器还将作为HTTP响应Body进行回显。

如需解密SSL/TLS通信，则需要向MITM_Intercept提供一个证书和一个密钥，客户端在启动与侦听器的握手时将使用该证书和密钥。如果目标服务器需要特定的证书进行握手，则可以选择提供指定的证书和密钥。

 **下图显示的是该工具的工作流程** ：

![](https://image.3001.net/images/20220626/1656249970_62b85e728fb30eb94cb58.jpeg!small)

## 工具要求

> 1、Python 3.9
>
> 2、[ _requests库_](https://docs.python-requests.org/en/latest/)：$ python -m
> pip install requests

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/cyberark/MITM_Intercept.git

## 工具使用

    
    
    usage: mitm_intercept.py [-h] [-m] -l [u|t:]<interface>:<port> [[u|t:]<interface>:<port> ...] -t
    
                             [u|t:]<addr>:<port> [[u|t:]<addr>:<port> ...] [-lc <cert_path>]
    
                             [-lk <key_path>] [-tc <cert_path>] [-tk <key_path>] [-w <interface>:<port>]
    
                             [-p <addr>:<port>] [-s <script_path>] [--sni <server_name>]
    
                             [-tv <defualt|tls12|tls11|ssl3|tls1|ssl2>] [-ci <ciphers>]
    
     
    
    mitm_intercept version 1.6
    
     
    
    options:
    
      -h, --help            show this help message and exit
    
      -m, --mix-connection  Perform TCP relay without SSL handshake. If one of the relay sides starts an
    
                            SSL handshake, wrap the connection with SSL, and intercept the
    
                            communication. A listener certificate and private key must be provided.
    
      -l [u|t:]<interface>:<port> [[u|t:]<interface>:<port> ...], --listen [u|t:]<interface>:<port> [[u|t:]<interface>:<port> ...]
    
                            Creates SSLInterceptServer listener that listens on the specified interface
    
                            and port. Can create multiple listeners with a space between the parameters.
    
                            Adding "u:" before the address will make the listener listen in UDP
    
                            protocol. TCP protocol is the default but adding "t:" for cleanliness is
    
                            possible. The number of listeners must match the number of targets. The i-th
    
                            listener will relay to the i-th target.
    
      -t [u|t:]<addr>:<port> [[u|t:]<addr>:<port> ...], --target [u|t:]<addr>:<port> [[u|t:]<addr>:<port> ...]
    
                            Directs each SSLInterceptServer listener to forward the communication to a
    
                            target address and port. Can create multiple targets with a space between
    
                            the parameters. Adding "u:" before the address will make the target
    
                            communicate in UDP protocol.TCP protocol is the default but adding "t:" for
    
                            cleanliness is possible. The number of listeners must match the number of
    
                            targets. The i-th listener will relay to the i-th target.
    
      -lc <cert_path>, --listener-cert <cert_path>
    
                            The certificate that the listener uses when a client contacts him. Can be a
    
                            self-sign certificate if the client will accept it.
    
      -lk <key_path>, --listener-key <key_path>
    
                            The private key path for the listener certificate.
    
      -tc <cert_path>, --target-cert <cert_path>
    
                            The certificate that used to create a connection with the target. Can be a
    
                            self-sign certificate if the target will accept it. Doesn't necessary if the
    
                            target doesn't require a specific certificate.
    
      -tk <key_path>, --target-key <key_path>
    
                            The private key path for the target certificate.
    
      -w <interface>:<port>, --webserver <interface>:<port>
    
                            Specifies the interface and the port the InterceptionServer webserver will
    
                            listens on. If omitted the default is 127.0.0.1:49999
    
      -p <addr>:<port>, --proxy <addr>:<port>
    
                            Specifies the address and the port of a proxy between the InterceptionServer
    
                            webserver and the SSLInterceptServer. Can be configured so the communication
    
                            will go through a local proxy like Burp. If omitted, the communication will
    
                            be printed in the shell only.
    
      -s <script_path>, --script <script_path>
    
                            A path to a script that the InterceptionServer webserver executes. Must
    
                            contain the function handle_request(message) that will run before sending it
    
                            to the target or handle_response(message) after receiving a message from the
    
                            target. Can be omitted if doesn't necessary.
    
      --sni <server_name>   If there is a need to change the server name in the SSL handshake with the
    
                            target. If omitted, it will be the server name from the handshake with the
    
                            listener.
    
      -tv <defualt|tls12|tls11|ssl3|tls1|ssl2>, --tls-version <defualt|tls12|tls11|ssl3|tls1|ssl2>
    
                            If needed can be specified a specific TLS version.
    
      -ci <ciphers>, --ciphers <ciphers>
    
                            Sets different ciphers than the python defaults for the TLS handshake. It
    
                            should be a string in the OpenSSL cipher list format
    
                            (https://www.openssl.org/docs/manmaster/man1/ciphers.html).
    
     
    
    For dumping SSL (pre-)master secrets to a file, set the environment variable SSLKEYLOGFILE with a
    
    file path. Useful for Wireshark.

通信数据需要被定向到侦听器，以便拦截任意协议。这样做的方式取决于客户机的操作方式。有时它使用DNS地址，更改主机文件就足以解析侦听器地址。如果地址是硬编码的，则需要应用更具创造性的方法，通常涉及到对路由表进行一些修改。

## 修改脚本

我们可以通过-s选项来染HTTP拦截服务器运行一个Python脚本，但服务器接收到HTTP请求的时候便会运行这个脚本，脚本运行完成后HTTP拦截服务器便会回传响应信息。

配置代理时（如Burp），请求的修改将在脚本运行之前进行，响应的修改将在脚本运行之后进行。

脚本中必须包含handle_request(message)和handle_response(message)这两个函数，当消息从客户端发送到服务器时，HTTP拦截服务器将调用handle_request(message)，当消息从服务器发送到客户端时，HTTP拦截服务器将调用handle_response(message)。

下面的样例脚本中，我们将会在消息的结尾添加一个空字节：

    
    
    def handle_request(message):
    
        return message + b"\x00"
    
     
    
    def handle_response(message):
    
        # Both functions must return a message.
    
    return message

## 证书

该工具需要一个服务器证书和一个私钥来实现SSL拦截。关于如何生成自签名证书或Burp证书，可以参考这篇【 _文档_】。

## 工具使用演示一-拦截MSSQL连接

### 演示视频

 **视频地址** ：【[ _点我观看_](https://user-images.githubusercontent.com/28649672/162933166-21c1f37d-ee6c-4162-8c00-2bc724cc10a7.mp4)】

### 脚本示例

下面给出的两个脚本支持拦截TLS协议消息：

 **demo_script.py**

    
    
    from time import time
    
    from struct import pack
    
    from pathlib import Path
    
     
    
     
    
    def handle_request(message):
    
     
    
        if message.startswith(b"\x17\x03"):
    
            return message
    
     
    
        with open("msg_req" + str(time()), "wb") as f:
    
            f.write(message[:8])
    
     
    
        return message[8:]
    
     
    
     
    
    def handle_response(message):
    
     
    
        if message.startswith(b"\x17\x03"):
    
            return message
    
     
    
        path = Path(".")
    
        try:
    
            msg_res = min(i for i in path.iterdir() if i.name.startswith("msg_res"))
    
            data = msg_res.read_bytes()
    
            msg_res.unlink()
    
        except ValueError:
    
            data = b'\x12\x01\x00\x00\x00\x00\x01\x00'
    
     
    
        return data[:2] + pack(">h", len(message)+8) + data[4:] + message

 **demo_script2.py**

    
    
    from time import time
    
    from struct import pack
    
    from pathlib import Path
    
     
    
    def handle_request(message):
    
     
    
        if message.startswith(b"\x17\x03"):
    
            return message
    
     
    
        path = Path(".")
    
        try:
    
            msg_req = min(i for i in path.iterdir() if i.name.startswith("msg_req"))
    
            data = msg_req.read_bytes()
    
            msg_req.unlink()
    
        except ValueError:
    
            data = b'\x12\x01\x00\x00\x00\x00\x01\x00'
    
     
    
     
    
        return data[:2] + pack(">h", len(message)+8) + data[4:] + message
    
     
    
     
    
    def handle_response(message):
    
     
    
        if message.startswith(b"\x17\x03"):
    
            return message
    
     
    
        with open("msg_res" + str(time()), "wb") as f:
    
            f.write(message[:8])
    
     
    
    return message[8:]

## 工具使用演示二-拦截MSSQL连接（TLS）

### 演示视频

 **视频地址** ：【[ _点我观看_](https://user-images.githubusercontent.com/28649672/162976250-75f2e3c5-f328-4bcc-ad49-a9561d493cb1.mp4)】

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/cyberark/MITM_Intercept/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **MITM_Intercept：** 【[
_GitHub传送门_](https://github.com/cyberark/MITM_Intercept)】

## 参考资料

> [
> _https://github.com/jrmdev/mitm_relay_](https://github.com/jrmdev/mitm_relay)
>
> [
> _https://portswigger.net/bappstore/12e84399d46a408dbe970f181391f781﻿_](https://portswigger.net/bappstore/12e84399d46a408dbe970f181391f781)
>
> [ _https://portswigger.net/burp_](https://portswigger.net/burp)
>
> [
> _https://en.wiki*pedia.org/wiki/Server_Name_Indication_](https://en.wikipedia.org/wiki/Server_Name_Indication)
>
> [
> _https://docs.python.org/3/library/socketserver.html_](https://docs.python.org/3/library/socketserver.html)
>
> [
> _https://docs.python.org/3/library/http.server.html#http.server.ThreadingHTTPServer_](https://docs.python.org/3/library/http.server.html#http.server.ThreadingHTTPServer)
>
> [
> _https://www.openssl.org/docs/manmaster/man1/ciphers.html_](https://www.openssl.org/docs/manmaster/man1/ciphers.html)
>
> [ _https://docs.python-requests.org/en/latest/_](https://docs.python-> requests.org/en/latest/)
>
> [ _https://github.com/jrmdev/mitm_relay#host-> configuration_](https://github.com/jrmdev/mitm_relay#host-configuration)
>
> [
> _https://github.com/jrmdev/mitm_relay#certificates_](https://github.com/jrmdev/mitm_relay#certificates)
>
> [ _https://github.com/srini0x00/dvta_](https://github.com/srini0x00/dvta)
>
> [
> _https://en.wik*ipedia.org/wiki/Tabular_Data_Stream_](https://en.wikipedia.org/wiki/Tabular_Data_Stream)

