**今天给大家介绍的是一款能够帮助渗透测试人员实时执行DNS重绑定（Rebinding）测试的DNS服务器。**  

![a.png](https://image.3001.net/images/20180402/15226753775994.png!small)  

## Whonow DNS服务器

Whonow是一款能够帮助渗透测试人员实时执行DNS重绑定（Rebinding）的DNS服务器，Whonow允许我们定义DNS响应并通过域名请求来实现规则的动态重绑定。

    
    
    #respond to DNS queries for this domain with 52.23.194.42 the first time
    # itis requested and then 192.168.1.1 every time after that
    A.52.23.194.42.1time.192.168.1.1.forever.rebind.network
    #respond first with 52.23.194.42, then 192.168.1.1 the next five times,
    # andthen start all over again (1, then 5, forever...)
    A.52.23.194.42.1time.192.168.1.1.5times.repeat.rebind.network  
    

动态DNS重绑定规则最棒的一点就在于，你不需要自己搭建一台DNS服务器来利用目标浏览器的[同源策略](https://en.wikipedia.org/wiki/Same-origin_policy)，实际上，任何人都可以共享同样的一台[公共whonow服务器](http://rebind.network/)。

需要注意的是，你需要在每一个发送给whonow服务器的DNS查询请求中用UUID（例如a06a5856-1fff-4415-9aa2-823230b05826）来指定子域名。比如说，指向*.rebind.network的请求应该写成*.a06a5856-1fff-4415-9aa2-823230b05826.rebind.network。

## 子域名=重绑定规则

whonow的优势是你可以通过在域名中使用子域名来定义DNS响应的行为，而且你只需要使用一些简单的关键字（例如A, (n)times,
forever和repeat），就可以定义复杂且强大的DNS行为。

### whonow请求结构剖析

下面给出的是一份whonow请求样本：

A.<ip-address>.<rule>[.<ip-address>.<rule>[.<ip-address>.<rule>]][.uuid/random-string].example.com

1、A：一种DNS请求类型，当前只支持A记录，但随后会添加AAAA记录的支持。

2、<ip-address>：ipv4（ipv6正在添加中）地址，例如192.168.1.1。

3、<rule>：其中的三条规则如下

（1）(n)time[s]：DNS服务器的响应次数，例如1time, 3times或5000times。

（2）forever：使用之前的IP地址响应请求。

（3）repeat：从同开始重复执行整套规则。

4、[uuid/random-string]：一个随机字符串，用于标识DNS重绑定攻击的IP地址。

5、example.com：指向whonow域名服务器的域名，例如公开的rebind.network whonow实例。

如果你需要实现更加复杂的行为，可以同时使用多条规则。

## 演示样本

    
    
    #always respond with 192.168.1.1. This isn't really DNS rebinding
    # butit still works
    A.192.168.1.1.forever.rebind.network
    #alternate between localhost and 10.0.0.1 forever
    A.127.0.0.1.1time.10.0.0.1.1time.repeat.rebind.network
    #first respond with 192.168.1.1 then 192.168.1.2. Now respond 192.168.1.3forever.
    A.192.168.1.1.1time.192.168.1.2.2times.192.168.1.3.forever.rebind.network
    #respond with 52.23.194.42 the first time, then whatever `whonow--default-address`
    # isset to forever after that (default: 127.0.0.1)
    A.52.23.194.42.1time.rebind.network  
    

## 注意事项

### 使用唯一域名

每当whonow服务器中的一个唯一域名被请求之后，它们都会在服务器的RAM中创建一个小型的状态存储程序，每当域名被请求，程序计数器会自增，其状态也可能会改变。每一个唯一域名都有其唯一的程序实例对应，为了防止其他域名程序的状态受到影响，你应该在规则定义之后添加一个UUID子域名，而且这个UUID不能被重复使用。

    
    
    #this
    A.127.0.0.1.1time.10.0.0.1.1time.repeat.8f058b82-4c39-4dfe-91f7-9b07bcd7fbd4.rebind.network
    # notthis
    A.127.0.0.1.1time.10.0.0.1.1time.repeat.rebind.network  
    

## 运行你自己的whonow服务器

为了在云端运行我们自己的whonow服务器，我们需要在域名提供商的管理面板中配置一个指向你VPS的自定义域名服务器。接下来，在VPS中安装whonow，并确保它运行在端口53（默认的DNS端口）上。

安装命令：

    
    
    npm install --cli -g whonow@latest

运行命令：

    
    
    whonow --port 53

  
![b.png](https://image.3001.net/images/20180402/15226755228718.png!small)  

如果你觉得安装过程太麻烦的话，你也可以直接使用运行在[rebind.network](http://rebind.network/)上的开放whonow服务器。

## 工具使用

    
    
    $whonow --help
    usage:whonow [-h] [-v] [-p PORT] [-d DEFAULT_ANSWER] [-b MAX_RAM_DOMAINS]
    Amalicious DNS server for executing DNS Rebinding attacks on the fly.
    Optionalarguments:
    -h, --help            Show this help message and exit.
    -v, --version         Show program's version number andexit.
    -p PORT, --port PORT  What port to run the DNS server on (default:53).
    -d DEFAULT_ANSWER, --default-answerDEFAULT_ANSWER
    The default IP addressto respond with if no rule is
    found (default:"127.0.0.1").
    -b MAX_RAM_DOMAINS, --max-ram-domainsMAX_RAM_DOMAINS
    The number of domainname records to store in RAM at
    once. Once the numberof unique domain names queried
    surpasses this numberdomains will be removed from
    memory in the orderthey were requested. Domains that
    have been removed inthis way will have their program
    state reset the nexttime they are queried (default:
    10000000).  
    

## 测试

如果你想要测试服务器的功能（test.js），你必须要让Whonow服务器运行在localhost:15353：

    
    
    # inone terminal
    whonow -p 15353
    # inanother terminal
    cd path/to/node_modules/whonow
    npmtest  
    

 ***
参考来源：[whonow](https://github.com/brannondorsey/whonow)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

