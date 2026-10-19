**0x01 简介**

被动收集资产并自动进行SQL注入检测（插件化 自动Bypass）、XSS检测、RCE检测、敏感信息检测

 **0x02 程序介绍**

  * 自动更新Bypass插件

  * XSS漏洞检测

  * Rce漏洞检测

  * 敏感信息检测

  * 主动爬虫+扫描

 **0x03 程序截图**

![](https://image.3001.net/images/20221120/1668928679_6379d4a7a57cdce8e307c.png!small)![](https://image.3001.net/images/20221120/1668928694_6379d4b69e42a62ea5ead.png!small)![](https://image.3001.net/images/20221120/1668928703_6379d4bfe31c5f8156d9a.png!small)![](https://image.3001.net/images/20221120/1668928712_6379d4c8dd46d63540123.png!small)

 **0x04 参数教程**

一定要下载crt并安装证书，否则无法扫描https

    
    
    ./EPScan -h​Usage of /EPScan:-deep   bool   // 选择后开启，默认不开启，不开效率快但是误报微高深入扫描（降低效率提高准确率）-pdelay   string   // 需带有http协议头，看例子流量转发（程序的流量转发到指定端口，例如Burp的8080端口: http://127.0.0.1:8080) -pdir   string  // 加载指定目录下所有的插件，默认不进行Bypass批量加载指定目录下的Bypass插件-plist   string  // 查看插件信息，默认输出 "plus/" 目录下的插件信息查看插件列表和详细信息 (default "plus/")-port   string  // 开启监听端口监听端口配置 (default "8899")-ptest   string  // 测试指定插件效果 会输出原始Payload和处理后的Payload插件测试-run     bool  // 开始被动式扫描，例如：./EPScan -pdir plus/ -port 8899 -run开始被动式扫描

开始被动式扫描

一定要下载crt并安装证书，否则无法扫描https

    
    
    ./EPScan -port 8899 -run

开始被动式扫描并加载Bypass插件目录

    
    
    ./EPScan -pdir plus/ -port 8899 -run

 **0x05 插件编写**

 **SQL注入Bypass插件编写**

 **例：**

 **插件样例**

    
    
    package main //包名必须为 "main"​import ("strings")​var ( // 全局变量必须包含以下三个参数Plus_Author   = "ExpLang"        // 插件作者Plus_Version  = "1.0"            // 插件版本Plus_Describe = "Bypass_SafeDog" // 插件描述)​func Bypass(Value string) string { // 主函数名必须为 "Bypass" 区分大小写，参数为String，返回值为String，思路：传入原始Payload，返回处理后的Payload。​var Value_Bypass stringvar bypass_SafeDog_str = "/*x^x*/"Value_Bypass = strings.Replace(Value, "UNION", bypass_SafeDog_str+"UNION"+bypass_SafeDog_str, -1) // 寻找指定字符串并全部替换Value_Bypass = strings.Replace(Value_Bypass, "SELECT", bypass_SafeDog_str+"SELECT"+bypass_SafeDog_str, -1)​return Value_Bypass // 返回处理后的Payload。}​func INFO() []string {return []string{Plus_Author, Plus_Version, Plus_Describe} //输出插件信息}​

编译为插件：

    
    
    ./EPScan -pluslist+----+---------+---------+-------------------------------+-------------------------------+| ID | AUTHOR  | VERSION |           DESCRIBE            |             PATH              |+----+---------+---------+-------------------------------+-------------------------------+| 1  | ExpLang | 1.0     | Bypass_SafeDog                | plus/bypass_SafeDog.go        || 2  | ExpLang | 1.0     | 替换 "'" 单引号为 "%EF%BC%87"   | plus/bypass_apostrophemask.go || 3  | ExpLang | 1.0     | 测试/演示                | plus/bypass_name.go           |+----+---------+---------+-------------------------------+-------------------------------
测试插件

    
    
    ./EPScan -ptest "plus/bypass_name.go"

 **0x06 程序下载**

https://github.com/ExpLangcn/EPScan

