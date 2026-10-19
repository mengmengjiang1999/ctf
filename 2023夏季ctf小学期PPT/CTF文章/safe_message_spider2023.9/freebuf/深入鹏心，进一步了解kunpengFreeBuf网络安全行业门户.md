# kunpeng 是什么？

kunpeng 是一个GOLANG 开源的POC 框架。

使用方法及其简单，通过源码编译生成一个so文件，或者从github 下载编译好的so文件，和现有程序结合即可。

跨语言调用，各个语言调用的demo 代码都在github里有。另外，python 还封装了一个简陋的基于web 的扫描器 poc_scanner 。

开源社区维护，包含常见的POC，并不断丰富中，(读完此文，希望你掌握提交POC 的方法，大家一起努力，愿鲲鹏早日长成一条大鱼)

# 剖析鲲鹏 ？

### 0\. 先聊编译方法：

1). 需要基本的golang 环境，这个自己配吧，~^~

2). 安装esc 用来把json 文件定义的插件编译成单个的golang 文件 :

    
    
    go install github.com/mjibson/esc

3). 编译成so :

    
    
    go build -buildmode=c-shared --ldflags="-w -s -X main.VERSION=20190226" -o kunpeng_c.so 

main.VERSION 会传递到编译的宏里，作为编译的SO的版本号。

buildmode 一定为c-shared 这样才能编译出so 文件.

### 1\. 从main.go 说起:

1) 编译主文件 main.go 为整个程序的入口。

函数导出与参数转换:

通过如下的方式导出函数

    
    
    //export StartWebServer
    func StartWebServer(bindAddr *C.char) {
    	go web.StartServer(C.GoString(bindAddr))
    }

函数参数为 cgo 中的 c 语言类型。kunpeng 主要通过字符串和调用语言进行交互，所以，传递参数，调用参数基本上都是 * C.char 。

* C.char 和 Golang 语言之间的String 类型互转：
    
    
    C.GoString(charMessage)

2)主要导出如下的几个函数 :

StartWebServer

关联代码 web/api.go 启动一个 简陋的 webserver 用来接收api 请求，是个检测的测试api 请求的办法。

主要实现几个web 接口:

> /api/pluginList 获取插件列表,
>
> /api/check 传递检测对象获取检测结果，
>
> /api/config 间接调用SetConfig 方法，修改全局的配置对象。

Check

为检测POC 的主要函数，检测步骤如下:

> a. C.GoString 转换数据类型 ---> json.Unmarshal 转为JSON 对象
>
> b. 调用plugin.Scan 方法 (重要方法，接下来细聊)
>
> c. 将结果使用 C.CString(string(b)) 包装结果返回给调用语言。

GetPlugins

获取插件列表，包括json 插件和golang 编写的插件。

SetConfig

设置运行选项，传入一个JSON 字符串，可以设置的几个选项如下:

    
    
    {
            "timeout": 15, // 插件连接超时
            "aider": "http://123.123.123.123:8088", // 漏洞辅助验证接口，部分漏洞无法通过回显判断是否存在漏洞，可通过辅助验证接口进行判断。python -c'import socket,base64;exec(base64.b64decode("aGlzdG9yeSA9IFtdCndlYiA9IHNvY2tldC5zb2NrZXQoc29ja2V0LkFGX0lORVQsc29ja2V0LlNPQ0tfU1RSRUFNKQp3ZWIuYmluZCgoJzAuMx4wLjAnLDgwODgpKQp3ZWIubGlzdGVuKDEwKQp3aGlsZSBUcnVlOgogICAgdHJ5OgogICAgICAgIGNvbm4sYWRkciA9IHdlYi5hY2NlcHQoKQogICAgICAgIGRhdGEgPSBjb25uLnJlY3YoNDA5NikKICAgICAgICByZXFfbGluZSA9IGRhdGEuc3BsaXQoIlxyXG4iKVswXQogICAgICAgIGFjdGlvbiA9IHJlcV9saW5lLnNwbGl0KClbMV0uc3BsaXQoJy8nKVsxXQogICAgICAgIHJhbmtfc3RyID0gcmVxX2xpbmUuc3BsaXQoKVsxXS5zcGxpdCgnLycpWzJdCiAgICAgICAgaHRtbCA9ICJORVcwMCIKICAgICAgICBpZiBhY3Rpb24gPT0gImFkZCI6CiAgICAgICAgICAgIGhpc3RvcnkuYXBwZW5kKHJhbmtfc3RyKQogICAgICAgICAgICBwcmludCAiYWRkIityYW5rX3N0cgogICAgICAgIGVsaWYgYWN0aW9uID09ICJjaGVjayI6CiAgICAgICAgICAgIHByaW50ICJjaGVjayIrcmFua19zdHIKICAgICAgICAgICAgaWYgcmFua19zdHIgaW4gaGlzdG9yeToKICAgICAgICAgICAgICAgIGh0bWw9IlZVTDAwIgogICAgICAgICAgICAgICAgaGlzdG9yeS5yZW1vdmUocmFua19zdHIpCiAgICAgICAgcmF3ID0gIkhUVFAvMS4wIDIwMCBPS1xyXG5Db250ZW50LVR5cGU6IGFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcclxuQ29udGVudC1MZW5ndGg6ICVkXHJcbkNvbm5lY3Rpb246IGNsb3NlXHJcblxyXG4lcyIgJShsZW4oaHRtbCksaHRtbCkKICAgICAgICBjb25uLnNlbmQocmF3KQogICAgICAgIGNvbm4uY2xvc2UoKQogICAgZXhjZXB0OnBhc3M="))'
    在辅助验证机器上运行以上代码，填入http://IP:8088，不开启则留空。
            "http_proxy": "http://123.123.123.123:1080", // HTTP代理，所有插件http请求流量将通过代理发送（需使用内置的http请求函数util.RequestDo）
            "pass_list": ["passtest"], // 默认密码字典，不定义则使用硬编码在代码里的小字典
            "extra_plugin_path": "/tmp/plugin/" // 除已编译好的插件（Go、JSON）外，可指定额外插件目录（仅支持JSON插件），指定后程序会周期读取加载插件
        }

ShowLog

设置运行选项，是否展示日志. 与后边的 StartBuffer GetLog 无关。

GetVersion

获得当前SO 的版本，编译的时候通过 -X main.VERSION=20190226 覆盖传递

StartBufferGetLog

三个函数完成一个日志记录功能, 扫描开始前调用StartBuffer 开启日志记录，扫描结束后调用GetLog 返回调用的Log .
可以用来返回给调用者，了解扫描过程的细节。

### 2\. 插件的加载机制:

插件的代码主要集中在 plugin/plugins.go 中 。

其中定义了两种类型 : JSONPlugins 和 GoPlugins 用来标识两种不同的插件类型。

 **1) JSONPlugins**

JSONPlugins 为一组 json 文件中定义的一组检测规则，初始化为 plugin/json/中的所有json 文件.
这种插件一般执行过程为，向host,port 指定的地址执行一个http 请求，请求一个指定的URL 接口然后对 接口返回的结果进行简单的判断。

JSONPlugin 的加载代码在 plugin/json/init.go 中。 鲲鹏的可灵活扩展性很大一部分原因也是因为这个模块。

鲲鹏 本身可以定义一个 ExtraPluginPath 的目录，用来标识外部扩展 JSON 文件的路径，只需要在该路径中编写符合规则的JSON
文件，该检测方法，会自动的加载到鲲鹏的检测库中。 **无需重新编译SO。** 使用的协程异步加载 20秒钟同步一次。

一个JSON 插件的定义规则如下 ：

    
    
    {
        "target":"discuz",
        "meta":{
            "name":    "Discuz! 7.2 admincp.php XSS",
            "remarks": "Discuz! 7.2 admincp.php 存在反射型XSS漏洞",
            "level":   3,
            "type":    "XSS",
            "author":   "wolf",
            "references": {
                "url":"",
                "cve":"",
                "kpid":"KP-0042"
            }
        },
        "request":{
            "path":     "/admincp.php?infloat=yes&handlekey=123);test(700);//",
            "postData": ""
        },
        "verify":{
            "type":  "string",
            "match": "if($('return_123);test(700);//"
        }
    }

meta 部分用来标识这个插件的主要用途。关键部分是request 和 verify 两个模块。

request 为定义请求部分，path 为请求的地址，默认为GET 请求。如果 request 中的postData 不为空，则为发起post 请求。

verify 为结果匹配部分，type 分为三种 string , regex , md5 。

具体的包装实现模块在 plugin/json.go 中。

2 **） GoPlugins**

GoPlugin为Golang 实现的系统插件。封装了一组实现了 GoPlugin 接口的对象。

目前包含的插件列表在plugin/go/目录下，通过golang 的代码实现更为丰富的检测。

每个插件文件为一个独立的go 文件，其中 init 方法会被模块加载的时候执行，一般内部会通过 plugin.Regist 注册为系统插件。

plugin.Regist 传递一个 名称，一个对象，该对象必须实现GoPlugin 的几个接口。

GoPlugin 接口定义在 plugin/go.go 中

接口定义 Init Check GetResult 三个方法，分别用来标识该插件的 初始化，检测，获取结果三个阶段。

GoPlugin对象的References 中可以定义 CVE , KPID 用来标识指定CVE 或者 KPID 的插件。

扫描过程会依次执行 Init , Check, GetResult 三步。

###  **3\. POC 检测流程**

poc 检测的入口函数为plugin.Scan 方法。

扫描过程分为两步， GoPlugin 和 JSONPlugin 。

 **1) GoPlugin 扫描**

通过传递对象的Target 参数来识别， 如果以 cve- 开头那么就执行对应的插件，如果已kp- 那么扫描执行KPID 的插件。标识为all
会做所有的插件检测。

 **2) JSONPlugin 扫描**

JSON 检测方法和GoPlugin 类似，同样和 cve- kp- all 来标识三种不同的分类。

执行完所有插件的的扫描方法，结果会附加到一个数组对象中，最后将数组返回给调用方。

> \-- -- -- -- -- --- -- --- - - - -- - - - - - -- - - - - - -- - - -- - -- -> -- - -- - -- - - -- - - -- - - -
#  **扩展鲲鹏？**

1). 写POC 插件

同上插件分为JSON插件和GOPlugin 根据不同的需求来完成相应插件的编写。

2). 优化整个流程

你可以修改Check 的整个执行流程让他更符合你自己的应用环境。

（如果觉得不错，记得提交PR 奥）

注：如果文章看明白了，那么请来kunpeng的地址来提交PR吧 ， ^_^

<https://github.com/opensec-cn/kunpeng>

