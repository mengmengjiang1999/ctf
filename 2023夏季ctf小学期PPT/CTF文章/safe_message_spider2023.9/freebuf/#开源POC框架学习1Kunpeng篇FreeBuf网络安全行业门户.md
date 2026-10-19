# 开源POC框架学习1-Kunpeng篇

  * 开源POC框架学习1-Kunpeng篇
    * 1\. 概述
    * 2\. 编译
    * 3\. 使用方法
    * 4\. 使用例子
    * 5\. 项目的目录结构
    * 6\. web/api.go
    * 7\. plugin部分代码
      * 7.1. 如何实现一个插件
      * 7.2. 插件的调用部分如何实现的
        * 7.2.1. StartWebServer
        * 7.2.2. GetLog
        * 7.2.3. GetVersion
        * 7.2.4. SetConfig
        * 7.2.5. GetPlugins
        * 7.2.6. Check
        * 7.2.7. StartBuffer
        * 7.2.8. ShowLog
    * 8\. example/poc-scanner的实现
    * 9\. 后记
    * 10\. QA
      * 10.1. example例子call_webapi_test.py)报错

## 1\. 概述

> gitee地址: <https://gitee.com/zmf96/KUNPENG_NOTE>

为啥从Kunpeng开始一方面是学习下golang另外一方面是因为它的代码量少(项目的核心代码只有几百行的样子),项目文档及注释比较完善。

    
    
    $ cloc .
         140 text files.
         140 unique files.
          11 files ignored.
    
    github.com/AlDanial/cloc v 1.84  T=0.09 s (1501.2 files/s, 95778.4 lines/s)
    -------------------------------------------------------------------------------    Language                     files          blank        comment           code
    -------------------------------------------------------------------------------    Go                              63            378            137           4613
    Markdown                         5            197              0            886
    JSON                            36              0              0            828
    Python                          12            131             44            426
    HTML                             9             47              2            411
    JavaScript                       3             12             12            109
    C                                1             12              4             39
    Lua                              1              9              9             35
    Java                             1             16             26             23
    Bourne Shell                     1              4              0             12
    -------------------------------------------------------------------------------    SUM:                           132            806            234           7382
    -------------------------------------------------------------------------------    

## 2\. 编译

    
    
    git clone https://github.com/opensec-cn/kunpeng.git
    cd kunpeng
    
    # 静态资源打包进工程的小程序
    git clone  https://github.com/mjibson/esc
    cd esc 
    go build
    # 打包JSON插件到项目代码中
    ./esc/main -include='\.json$' -o plugin/json/JSONPlugin.go -pkg jsonplugin plugin/json/
    
    # 编译c版本所有语言均可使用
    go build -buildmode=c-shared --ldflags="-w -s -X main.VERSION=20191218" -o kunpeng_c.so
    
    # 编译Go专用版本不支持win
    go build -buildmode=plugin --ldflags="-w -s -X main.VERSION=20191218" -o kunpeng_go.so
    
    # 样例测试
    python example/call_so_test.py
    go run example/callsoTest.go
    

## 3\. 使用方法

    
    
    接口调用说明
    
    /*  传入需检测的目标JSON格式为
        {
            "type": "web", //目标类型web或者service
            "netloc": "http://xxx.com", //目标地址web为URLservice格式为123.123.123.123:22
            "target": "wordpress", //目标名称GO插件注册时使用的字符串模糊匹配、JSON插件的target属性模糊匹配、CVE编号例CVE-xx-xxx、KPID(例KP-0013)编号决定使用哪些POC进行检测具体查看 /doc/plguin.md
            "meta":{
                "system": "windows",  //操作系统部分漏洞检测方法不同系统存在差异提供给插件进行判断
                "pathlist":[], //目录路径URL列表部分插件需要此类信息例如列目录漏洞插件
                "filelist":[], //文件路径URL列表部分插件需要此类信息例如struts2漏洞相关插件
                "passlist":[] //自定义密码字典
            } // 非必填
        }
        返回是否存在漏洞和漏洞检测结果
    */
    Check(taskJSON string) string
    
    // 获取插件列表信息
    GetPlugins() string
    
    /*  配置设置传入配置JSON格式为
        {
            "timeout": 15, // 插件连接超时
            "aider": "http://123.123.123.123:8088", // 漏洞辅助验证接口部分漏洞无法通过回显判断是否存在漏洞可通过辅助验证接口进行判断。python -c'import socket,base64;exec(base64.b64decode("aGlzdG9yeSA9IFtdCndlYiA9IHNvY2tldC5zb2NrZXQoc29ja2V0LkFGX0lORVQsc29ja2V0LlNPQ0tfU1RSRUFNKQp3ZWIuYmluZCgoJzAuMC4wLjAnLDgwODgpKQp3ZWIubGlzdGVuKDEwKQp3aGlsZSBUcnVlOgogICAgdHJ5OgogICAgICAgIGNvbm4sYWRkciA9IHdlYi5hY2NlcHQoKQogICAgICAgIGRhdGEgPSBjb25uLnJlY3YoNDA5NikKICAgICAgICByZXFfbGluZSA9IGRhdGEuc3BsaXQoIlxyXG4iKVswXQogICAgICAgIGFjdGlvbiA9IHJlcV9saW5lLnNwbGl0KClbMV0uc3BsaXQoJy8nKVsxXQogICAgICAgIHJhbmtfc3RyID0gcmVxX2xpbmUuc3BsaXQoKVsxXS5zcGxpdCgnLycpWzJdCiAgICAgICAgaHRtbCA9ICJORVcwMCIKICAgICAgICBpZiBhY3Rpb24gPT0gImFkZCI6CiAgICAgICAgICAgIGhpc3RvcnkuYXBwZW5kKHJhbmtfc3RyKQogICAgICAgICAgICBwcmludCAiYWRkIityYW5rX3N0cgogICAgICAgIGVsaWYgYWN0aW9uID09ICJjaGVjayI6CiAgICAgICAgICAgIHByaW50ICJjaGVjayIrcmFua19zdHIKICAgICAgICAgICAgaWYgcmFua19zdHIgaW4gaGlzdG9yeToKICAgICAgICAgICAgICAgIGh0bWw9IlZVTDAwIgogICAgICAgICAgICAgICAgaGlzdG9yeS5yZW1vdmUocmFua19zdHIpCiAgICAgICAgcmF3ID0gIkhUVFAvMS4wIDIwMCBPS1xyXG5Db250ZW50LVR5cGU6IGFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9dXRmLThcclxuQ29udGVudC1MZW5ndGg6ICVkXHJcbkNvbm5lY3Rpb246IGNsb3NlXHJcblxyXG4lcyIgJShsZW4oaHRtbCksaHRtbCkKICAgICAgICBjb25uLnNlbmQocmF3KQogICAgICAgIGNvbm4uY2xvc2UoKQogICAgZXhjZXB0OnBhc3M="))'
    在辅助验证机器上运行以上代码填入http://IP:8088不开启则留空。
            "http_proxy": "http://123.123.123.123:1080", // HTTP代理所有插件http请求流量将通过代理发送需使用内置的http请求函数util.RequestDo
            "pass_list": ["passtest"], // 默认密码字典不定义则使用硬编码在代码里的小字典
            "extra_plugin_path": "/tmp/plugin/" // 除已编译好的插件Go、JSON外可指定额外插件目录仅支持JSON插件指定后程序会周期读取加载插件
        }
    */
    SetConfig(configJSON string)
    
    // 开启web接口开启后可通过web接口进行调用webapi调用格式请查看例子/example/call_webapi_test.py
    StartWebServer(bindAddr string)
    
    // 获取当前版本 例如20190227
    GetVersion() string
    

## 4\. 使用例子

下面kuepng_c.so对应的头文件

    
    
    // 查看.so导出函数
    // objdump -tT kunpeng_c.so
    // nm -D kunpeng_C.so
    
    /* Code generated by cmd/cgo; DO NOT EDIT. */
    
    /* package kunpeng */
    
    #line 1 "cgo-builtin-export-prolog"
    
    #include <stddef.h> /* for ptrdiff_t below */
    
    #ifndef GO_CGO_EXPORT_PROLOGUE_H
    #define GO_CGO_EXPORT_PROLOGUE_H
    
    #ifndef GO_CGO_GOSTRING_TYPEDEF
    typedef struct { const char *p; ptrdiff_t n; } _GoString_;
    #endif
    
    #endif
    
    /* Start of preamble from import "C" comments.  */
    
    /* End of preamble from import "C" comments.  */
    
    /* Start of boilerplate cgo prologue.  */
    #line 1 "cgo-gcc-export-header-prolog"
    
    #ifndef GO_CGO_PROLOGUE_H
    #define GO_CGO_PROLOGUE_H
    
    typedef signed char GoInt8;
    typedef unsigned char GoUint8;
    typedef short GoInt16;
    typedef unsigned short GoUint16;
    typedef int GoInt32;
    typedef unsigned int GoUint32;
    typedef long long GoInt64;
    typedef unsigned long long GoUint64;
    typedef GoInt64 GoInt;
    typedef GoUint64 GoUint;
    typedef __SIZE_TYPE__ GoUintptr;
    typedef float GoFloat32;
    typedef double GoFloat64;
    typedef float _Complex GoComplex64;
    typedef double _Complex GoComplex128;
    
    /*
      static assertion to make sure the file is being used on architecture
      at least with matching size of GoInt.
    */
    typedef char _check_for_64_bit_pointer_matching_GoInt[sizeof(void*)==64/8 ? 1:-1];
    
    #ifndef GO_CGO_GOSTRING_TYPEDEF
    typedef _GoString_ GoString;
    #endif
    typedef void *GoMap;
    typedef void *GoChan;
    typedef struct { void *t; void *v; } GoInterface;
    typedef struct { void *data; GoInt len; GoInt cap; } GoSlice;
    
    #endif
    
    /* End of boilerplate cgo prologue.  */
    
    #ifdef __cplusplus
    extern "C" {
    #endif
    
    extern void StartWebServer(char* p0);
    
    extern char* Check(char* p0);
    
    extern char* GetPlugins();
    
    extern void SetConfig(char* p0);
    
    extern void ShowLog();
    
    extern char* GetVersion();
    
    extern void StartBuffer();
    
    extern char* GetLog(char* p0);
    
    #ifdef __cplusplus
    }
    #endif
    
    
    
    #coding:utf-8
    
    import time
    import json
    from ctypes import *
    
    # 加载动态连接库
    kunpeng = cdll.LoadLibrary('./kunpeng_c.so')
    
    # 定义出入参变量类型
    kunpeng.GetPlugins.restype = c_char_p
    kunpeng.Check.argtypes = [c_char_p]
    kunpeng.Check.restype = c_char_p
    kunpeng.SetConfig.argtypes = [c_char_p]
    kunpeng.GetVersion.restype = c_char_p
    
    # 获取插件信息
    out = kunpeng.GetPlugins()
    print(out)
    
    # 修改配置
    config = {
        'timeout': 10,
        # 'aider': 'http://xxxx:8080',
        # 'http_proxy': 'http://xxxxx:1080',
        # 'pass_list':['xtest']
        # 'extra_plugin_path': '/home/test/plugin/',
    }
    kunpeng.SetConfig(json.dumps(config))
    
    # 开启日志打印
    kunpeng.ShowLog()
    
    # 扫描目标
    task = {
        'type': 'web',
        'netloc': 'http://www.google.cn',
        'target': 'web'
    }
    task2 = {
        'type': 'service',
        'netloc': '192.168.0.105:3306',
        'target': 'mysql'
    }
    out = kunpeng.Check(json.dumps(task))
    print(json.loads(out))
    out = kunpeng.Check(json.dumps(task2))
    print(json.loads(out))
    

## 5\. 项目的目录结构

    
    
    .
    ├── config
    │   └── config.go　　# 配置文件
    ├── doc
    │   ├── img.png
    │   └── plugin.md   # 漏洞poc列表
    ├── example         # 使用示例包括各种语言的调用示例 C、go、java、js、lua、python
    │   ├── call_so_test.c
    │   ├── callsoTest.go
    │   ├── call_so_test.java
    │   ├── call_so_test.js
    │   ├── call_so_test.lua
    │   ├── call_so_test.py
    │   ├── call_webapi_test.py
    │   ├── nmap_kunpeng        # 先使用nmap扫描开放端口然后在调用kunpeng进行检查
    │   │   ├── nmap_kunpeng.py
    │   │   ├── README.md
    │   │   └── requirements.txt
    │   └── poc-scanner   # 使用kunpeng做的一个扫描器后面会有详细的学习记录
                .....
    ├── go.mod      # go mod文件 
    ├── go.sum
    ├── kunpeng_c.h  # 生成的C语言头文件
    ├── kunpeng_c.so  # go build生成的so文件
    ├── kunpeng_go.so
    ├── LICENSE
    ├── main.go    # 程序入口文件 主要就上面实现的那几个导出函数
    ├── note.md
    ├── plugin
    │   ├── go
    
    │   ├── go.go
    │   ├── json
    .....
    │   │   ├── init.go
    │   │   ├── JSONPlugin.go
    │   │   ├── phpmyadmin_deserialization.json
    .....
    │   ├── json.go
    │   └── plugin.go
    ├── README.md
    ├── util
    │   ├── aider.go
    │   ├── fun.go
    │   ├── log.go
    │   └── net.go
    └── web         # 使用gin框架写的http接口一个get一个post请求比较简单。
        └── api.go
    
    25 directories, 185 files
    

## 6\. web/api.go

该部分比较简单只有三个简单的请求主要就是调用该框架实现的核心函数 GetPlugins()、Scan()、config.Set()

    
    
    // StartServer 启动web服务接口
    func StartServer(bindAddr string) {
        router := gin.Default()     // 创建路由对象
        router.GET("/api/pluginList", func(c *gin.Context) {   // 添加一个get请求
            c.JSON(200, plugin.GetPlugins())     // 该请求以json格式返回插件相关的信息
        })
        router.POST("/api/check", func(c *gin.Context) {  // 添加一个post请求调用插件开始扫描
            var json plugin.Task
            if err := c.ShouldBindJSON(&json); err != nil {
                c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
                return
            }
            result := plugin.Scan(json)    // 开始扫描
            c.JSON(200, result)        /// 返回扫描结果
        })
        router.POST("/api/config", func(c *gin.Context) {  // 添加一个pos请求设置config 
            buf := make([]byte, 2048)
            n, _ := c.Request.Body.Read(buf)
            config.Set(string(buf[0:n]))
            c.JSON(200, map[string]bool{"success": true})
        })
    
        router.Run(bindAddr)  // h监听并在 bindAddr (例如 0.0.0.0:38080 上启动服务
    }
    

对应的python测试代码

    
    
    import time
    from ctypes import *
    import json
    import requests
    
    kunpeng = cdll.LoadLibrary('../kunpeng_c.so')  # 加载so文件
    kunpeng.StartWebServer.argtypes = [c_char_p]  # 说明StartWebServer函数的参数类型
    kunpeng.StartWebServer("0.0.0.0:38080".encode("utf-8"))  # 启动kunpneg的web服务
    time.sleep(5)  # 等待5s
    
    api = 'http://127.0.0.1:38080'
    # 请求接口获取插件信息
    plugin_list = requests.get(api + '/api/pluginList').json() 
    print(plugin_list)
    # 请求接口设置相应配置
    config = {
        'timeout': 10,
        # 'aider': 'http://xxxx:8080',
        # 'http_proxy': 'http://xxxxx:1080',
        'pass_list':['xtest'],
        # 'extra_plugin_path': '/home/test/plugin/',
    }
    requests.post(api + '/api/config',json=config)
    
    task = {
        'type': 'web',
        'netloc': 'http://www.google.cn',
        'target': 'web',
        'meta':{
            'system': '',
            'pathlist':[],
            'filelist':[],
            'passlist':[]
        }
    }
    task2 = {
        'type': 'service',
        'netloc': '192.168.0.105:3306',
        'target': 'mysql',
        'meta':{
            'system': '',
            'pathlist':[],
            'filelist':[],
            'passlist':[]
        }
    }
    result = requests.post(api + '/api/check',json=task).json()  # 开始第一个扫描任务
    print(result)
    result = requests.post(api + '/api/check',json=task2).json()  # 开始第二个扫描任务
    print(result)
    

## 7\. plugin部分代码

### 7.1. 如何实现一个插件

kunpeng支持json插件与go插件参见作者写的README及example目录中的现有插件。

  * golang插件例子1

    
    
    // 包名需定义goplugin
    package goplugin
    
    // 引入plugin
    import (
        "fmt"
        "kunpeng/plugin"
        "github.com/go-redis/redis"
    )
    
    // 定义插件结构inforesult需固定存在
    type redisWeakPass struct {
        info   plugin.Plugin // 插件信息
        result []plugin.Plugin // 漏洞结果集可返回多个
    }
    
    func init() {
        // 注册插件定义插件目标名称
        plugin.Regist("redis", &redisWeakPass{})
    }
    func (d *redisWeakPass) Init() plugin.Plugin{
        d.info = plugin.Plugin{
            Name:    "Redis 未授权访问/弱口令", // 插件名称
            Remarks: "导致敏感信息泄露严重可导致服务器直接被入侵控制。", // 漏洞描述
            Level:   0, // 漏洞等级 {0:"严重"1:"高危"2"中危"3"低危"4"提示"}
            Type:    "WEAKPASS", // 漏洞类型自由定义
            Author:  "wolf", // 插件编写作者
                References: plugin.References{
                URL: "https://www.freebuf.com/vuls/162035.html", // 漏洞相关文章
                CVE: "", // CVE编号没有留空或不申明
                KPID: "KP-0008", // kunpeng的POC编号累加数字
            },
        }
        return d.info
    }
    
    func (d *redisWeakPass) GetResult() []plugin.Plugin {
        var result = d.result
        d.result = []plugin.Plugin{}
        return result
    }
    
    func (d *redisWeakPass) Check(netloc string, meta plugin.TaskMeta) bool {
        for _, pass := range meta.PassList {
            client := redis.NewClient(&redis.Options{
                Addr:     netloc,
                Password: pass,
                DB:       0,
            })
            _, err := client.Ping().Result()
            if err == nil {
                client.Close()
                result := d.info
                result.Request = fmt.Sprintf("redis://%s@%s", pass, netloc)
                if pass == "" {
                    result.Remarks = fmt.Sprintf("未授权访问%s", result.Remarks)
                } else {
                    result.Remarks = fmt.Sprintf("弱口令%s,%s", pass, result.Remarks)
                }
                d.result = append(d.result, result)
                return true
            }
        }
        return false
    }
    

  * JSON插件例子

    
    
    {
        "//": "用 Google 的方式进行注释",
        "//": "插件所属应用名自由定义",
        "target": "wordpress",
        "meta":{
            "//": "插件名称",
            "name": "WordPress example.html jQuery DomXSS",
            "//": "漏洞描述",
            "remarks": "WordPress example.html jQuery 1.7.2 存在DomXSS漏洞",
            "//": "漏洞等级 {0:严重1:高危2中危3低危4提示}",
            "level":   3,
            "//": "漏洞类型自由定义",
            "type":    "XSS",
            "//": "插件编写作者",
            "author":  "wolf",
            "references": {
                "//": "漏洞相关文章",
                "url":"https://www.seebug.org/vuldb/ssvid-89179",
                "//": "CVE编号没有留空",
                "cve":"",
            "//": "kunpeng的POC编号累加数字",
            "kpid":"KP-0003"
            }
        },
        "request":{
            "//": "漏洞请求URL",
            "path": "/wp-content/themes/twentyfifteen/genericons/example.html",
            "//": "请求POST内容留空即为GET",
            "postData": ""
        },
        "verify":{
            "//": "漏洞验证类型 {string字符串判断,regex正则匹配,md5文件md5}",
            "type":  "string",
            "//": "漏洞验证值与type相关联",
            "match": "jquery/1.7.2/jquery.min.js"
        }
    }
    

### 7.2. 插件的调用部分如何实现的

核心代码就以下6个文件看起来比较简单的样子。

    
    
    plugin
    ├── go
    ├── go.go
    ├── json
    │   ├── docker_api.json
    │   ├── init.go
    │   ├── JSONPlugin.go
    ├── json.go
    └── plugin.go
    main.go
    

主要的个导出函数

    
    
    extern void StartWebServer(char* p0);　
    extern char* Check(char* p0);
    extern char* GetPlugins();
    extern void SetConfig(char* p0);
    extern void ShowLog();
    extern char* GetVersion();
    extern void StartBuffer();
    extern char* GetLog(char* p0);
    

#### 7.2.1. StartWebServer

启动web api

    
    
    //export StartWebServer
    func StartWebServer(bindAddr *C.char) {
        go web.StartServer(C.GoString(bindAddr))
    }
    

#### 7.2.2. GetLog

获取log待补充

#### 7.2.3. GetVersion

获取Version没啥好说的

#### 7.2.4. SetConfig

待补充

#### 7.2.5. GetPlugins

循环GoPlugins与JSONPlugins两个map将插件的信息放到plugins,方便其他部分用。

    
    
    // GetPlugins 获取插件信息
    func GetPlugins() (plugins []map[string]interface{}) {
        for name, pluginList := range GoPlugins {
            for _, plugin := range pluginList {
                info := plugin.Init()
                pluginMap := util.Struct2Map(info)
                delete(pluginMap, "request")
                delete(pluginMap, "response")
                pluginMap["target"] = name
                plugins = append(plugins, pluginMap)
            }
        }
        for name, pluginList := range JSONPlugins {
            for _, plugin := range pluginList {
                pluginMap := util.Struct2Map(plugin.Meta)
                delete(pluginMap, "request")
                delete(pluginMap, "response")
                pluginMap["target"] = name
                plugins = append(plugins, pluginMap)
            }
        }
        sort.Stable(pluginsSlice(plugins))
        return plugins
    }
    

#### 7.2.6. Check

待补充

大概调用流程Check() -> plugin.Scan() -> plugin.Run()/jsonCheck()

    
    
    //export Check
    func Check(task *C.char) *C.char {
        util.Logger.Info(C.GoString(task))
        var m plugin.Task  // 插件任务m
        err := json.Unmarshal([]byte(C.GoString(task)), &m)
        if err != nil {
            util.Logger.Error(err.Error())
            return C.CString("[]")
        }
        util.Logger.Info(m) // 打印log
        result := plugin.Scan(m)  // 开始扫描
        if len(result) == 0 {
            return C.CString("[]")
        }
        b, err := json.Marshal(result)
        if err != nil {
            util.Logger.Error(err.Error())
            return C.CString("[]")
        }
        return C.CString(string(b)) // 返回扫描结果
    }
    

#### 7.2.7. StartBuffer

待补充

#### 7.2.8. ShowLog

待补充

## 8\. example/poc-scanner的实现

目录结构如下

    
    
    ├── app.py   # 程序入口
    ├── config.py
    ├── extra
    │   └── ugj_59eeb735187efa73c0c4e94dcada4570.json
    ├── poc_server.conf
    ├── README.md
    ├── requirements.txt
    ├── static  # 静态资源文件
    │   └── js
    │       ├── formating.js
    │       └── md5.min.js
    ├── templates  # 静态模板文件
    │   ├── edit.html
    │   ├── login.html
    │   ├── message.html
    │   ├── navbar.html
    │   ├── panel_header.html
    │   ├── pluginList.html
    │   ├── register.html
    │   ├── result.html
    │   └── scan.html
    ├── tools
    │   ├── basetornado.py
    │   ├── command.py  # 程序启动代码
    │   ├── handlers
    │   │   ├── Index.py  # 插件列表、自行添加的json插件的修改删除、 用户登录退出
    │   │   ├── __init__.py
    │   │   ├── Message.py   
    │   │   ├── Register.py  # 添加新json插件
    │   │   └── Scan.py     # 执行扫描任务的部分
    │   ├── __init__.py
    │   └── so_proxy.py  # 对kunpeng_c.co的封装
    └── upso.sh
    

核心就是对Kunpeng_c.so的封装其余部分是一个tornado写的网站。

## 9\. 后记

年前就开始写了然后... 有些关键的地方没写清楚有时间在补充

水平有限大佬多多指教

感谢opensec-cn的开源

## 10\. QA

### 10.1. example例子call_webapi_test.py)报错

    
    
    Traceback (most recent call last):
      File "call_webapi_test.py", line 8, in <module>
        kunpeng.StartWebServer("0.0.0.0:38080")
    ctypes.ArgumentError: argument 1: <class 'TypeError'>: wrong type
    

修改第8行为`kunpeng.StartWebServer("0.0.0.0:38080".encode("utf-8"))`,问题解决

