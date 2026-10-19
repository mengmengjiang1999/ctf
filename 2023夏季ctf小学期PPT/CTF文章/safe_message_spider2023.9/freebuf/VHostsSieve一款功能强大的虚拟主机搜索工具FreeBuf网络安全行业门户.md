![1593001676_5ef346cc4dccc.jpg!small](https://image.3001.net/images/20200624/1593001676_5ef346cc4dccc.jpg!small)

## VHosts-Sieve

VHosts-Sieve是一款能够在不可解析域中搜索出虚拟主机的强大工具。

## 工具下载&安装

广大用户可以使用下列命令下载和安装VHosts-Sieve，并配置相应的依赖组件：

``git clone <https://github.com/dariusztytko/vhosts-sieve.git>``

``

````

``

``pip3 install -r vhosts-sieve/requirements.txt``

``

## 工具使用

获取子域名列表（比如说，使用[ _Amass_](https://github.com/OWASP/Amass)）：

    
    
    $ amass enum -v -passive -o domains.txt -d example.com -d example-related.com

使用vhosts-sieve.py查询虚拟主机：

``$ python3 vhosts-sieve.py -d domains.txt -o vhosts.txt``

``

````

``

``Logs dir: None``

``

````

``

``Max domains to resolve: -1``

``

````

``

``Max IPs to scan: -1``

``

````

``

``Max vhost candidates to check: -1``

``

````

``

``Ports to scan: [80, 443, 8000, 8008, 8080, 8443]``

``

````

``

``SNI enabled: False``

``

````

``

``Threads number: 16``

``

````

``

``Timeout HTTP: 5.0s``

``

````

``

``Timeout TCP: 3.0s``

``

````

``

``Verbose: False``

``

````

``

``User agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0)
Gecko/20100101 Firefox/68.0``

``

````

``

``Resolving 12 domains...``

``

````

``

``Scanning 1 IPs...``

``

````

``

``Finding vhosts (active IPs: 1, vhost candidates: 7)...``

``

````

``

``Saved results (4 vhosts)``

``

输出文件中将包含工具成功发现的虚拟主机，数据存储格式如下：

``165.22.264.81 80 http False zxcv.example.com 301``

``

````

``

``165.22.264.81 443 https False zxcv.example.com 200 dev.example.com 200
admin.example.com 401``

``

### 其中的每一行将包含下列信息：

> 1、IP地址
>
> 2、端口号
>
> 3、检测到的协议（HTTP或HTTPS）
>
> 4、“Stopped”标签（ _参考文档_）
>
> 5、成功发现的虚拟主机列表（包含响应状态码）

## 日志记录

已成功发现的虚拟主机返回的响应信息将会被记录在日志中，可通过-l或`--logs-dir`选项进行配置。

## 工作机制

为了扫描并发现虚拟主机，工具将会执行下列操作：

1、输入文件中的域名将需要被解析为IPv4地址。

2、根据解析结果，域名将会被划分成下列两个类：

> (1)已解析域名
>
> (2)未解析域名（虚拟主机候选者）

3、对已解析域名对应的IP地址进行扫描，并扫描Web端口，默认为80、443、8000、8008、8080、8433。

4、针对每一个开放端口，对虚拟主机候选者进行验证。

### 虚拟主机候选者验证

虚拟主机候选者的验证机制如下：

1、发送随机虚拟主机（无效的主机Header）请求；

2、存储响应数据作为参考；

3、使用虚拟主机候选者返回的响应与参考相应做对比：

> (1)如果响应类似，则跳过虚拟主机候选者；
>
> (2)否则，将虚拟主机候选者标记为有效的虚拟主机；

4、为了增加正功率，可以额外添加发送下列Header：

> (1)X-Forwarded-For: 127.0.0.1
>
> (2)X-Originating-IP: [127.0.0.1]
>
> (3)X-Remote-IP: 127.0.0.1
>
> (4)X-Remote-Addr: 127.0.0.1

5、除此之外，如果发现了过多有效的虚拟主机，则会停止验证，并将结果标记为“Stopped”；

请注意，整个过程中无需将响应状态码考虑在内，即便是4xx或5xx响应，因为其他内容才是值得详细分析的。

### SNI

针对HTTPS协议，可能需要通过主机Header和SNI（TLS扩展）来发送虚拟主机候选者验证请求，这样可以遍历到一些存在弱安全配置的SNI代理，用户可以使用
--enable-sni选项来启用SNI模式。

## 性能优化

针对包含上千子域名的大型网络，可能需要好几个小时才能完成虚拟主机候选者的验证，此时就可以使用下列选项来提升处理速度：

> 1、限制默认扫描的端口：`80, 443, 8000, 8008, 8080, 8443`，仅开启443端口扫描（`-p, --ports-to-> scan`）；
>
> 2、增加扫描线程数（`-t, --threads-number`）；
>
> 3、限制需要解析的域名数量（`-max domains`）；
>
> 4、限制要扫描的IP地址数量（`-max ips`）；
>
> 5、限制要检查的虚拟主机候选数量（`--max-vhost-candidates`）；
>
> 6、减少超时时间（`--timeout tcp`，`--timeout http`）；

除此之外，我们还建议用户使用`-v`（verbosity）选项来持续查看处理结果。

## 项目地址

> VHosts-Sieve：【[ _GitHub传送门_](https://github.com/dariusztytko/vhosts-sieve)】

## 参考来源

>  _[dariusztytko](https://github.com/dariusztytko/vhosts-sieve)_

