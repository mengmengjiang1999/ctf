***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

##  **下载地址：**

    
    
    https://github.com/chaitin/xray/releases
    https://github.com/chaitin/xray
    

## **特色**

    
    
    使用 go 语言编写，跨平台、纯异步、无阻塞，并发能力强，扫描速度刚刚的
    提供多种使用方式，调用姿势方便，输入输出非常标准化，极具可集成性
    使用 YAML 配置文件非常方便地定义 POC，可以快速扩展扫描能力
    全程使用无害 POC 进行探测，在确保能发现漏洞的基础上不会给业务带来严重影响，非常适用于企业内部安全建设
    命令行式的免费被动扫描工具，不多见
    自备盲打平台，可检测需要反连才能触发的漏洞，如：存储型 XSS、无回显的 SSRF、XXE、命令注入等
    更新速度快，用着不爽可以在 github 提需求，很快就能解决（我试过了，是真的）
    

## **适用人群**

    
    
    白帽子。挖 SRC 必备，打开浏览器挂上代理，然后上网冲浪等漏洞就对了，还不够的话就把代理给你爸妈、给你妹子、给你家猫都挂上
    甲方安全建设者。工具在手，天下我有，细粒度配置，高精度扫描，可作为定期巡检、常规扫描的辅助神器
    乙方工具开发者。在编写渗透框架或者漏洞扫描框架时，作为扫描探针进行集成，简直是大平台中的小尖刀
    

## **快速使用**

最简单的方式是直接调用，扫描一个指定的站点，如：

./xray webscan --basic-crawler http://example.com/

这可能是最简单最常用的一个功能，就是太长了，体验不太友好，建议常用的同学可以

alias xray="/path/xray webscan --basic-crawler"

###  **指定扫描输出**

不指定输出时，默认输出到控制台的标准输出中，可以做管道处理，也可以选择输出为文件，如：

./xray webscan --url http://example.com/ --json-output report.json

###  **不同参数对应不同的输出方式：**

    
    
    无参数：输出到控制台的标准输出
    --`text-output`：输出到文本文件中
    --`json-output`：输出到 JSON 文件中
    --`html-output`：输出到 HTML 文件中
    

### **基于代理的被动扫描**

xray 可以通过类似 Burp 的方式启动，利用 HTTP 代理来抓包扫描，如：

./xray webscan --listen 127.0.0.1:7777

如果运行没报任何错就可以设置浏览器 HTTP 代理为 127.0.0.1:7777 了

###  **设置浏览器代理**

进入 Burp 后，打开 User options 标签页，然后找到 Upstream Proxy Servers 设置。

点击 Add 添加上游代理以及作用域，Destination host处可以使用*匹配多个任意字符串，?匹配单一任意字符串，而上游代理的地址则填写 xray
的监听地址。  
![图片.png](https://image.3001.net/images/20210714/1626240533_60ee7615b8622661323bc.png!small)  
接下来，在浏览器端使用 Burp 的代理地址  
![图片.png](https://image.3001.net/images/20210714/1626240552_60ee76281f41862108f6d.png!small)

此时网页流量便通过了brup转发到了xray  
![图片.png](https://image.3001.net/images/20210714/1626240565_60ee7635a9c7406d378f7.png!small)

代理设置 OK 以后就可以启动代理扫描了，这时候我们打来浏览器尽情冲浪吧，理论上我们的鼠标点到哪 xray 就能扫到哪。

需要注意一下的是，很多时候还会扫到 HTTPS 站点，可能会因为有代理而导致无法访问，或者需要手动确认安全风险。这时候需要我们导入 xray
运行目录下的ca.crt证书

### 生成证书

在浏览器使用 https 协议通信的情况下，必须要得到客户端的信任，才能建立与客户端的通信。

这里的突破口就是 ca 证书。只要自定义的 ca 证书得到了客户端的信任，xray 就能用该 ca 证书签发各种伪造的服务器证书，从而获取到通信内容。

powershell运行 .\xray_windows_amd64.exe genca  
![图片.png](https://image.3001.net/images/20210714/1626240655_60ee768fd2c056f14ddb8.png!small)  
运行命令之后，将在当前文件夹生成 ca.crt 和 ca.key 两个文件。

本命令只需要第一次使用的时候运行即可，如果文件已经存在再次运行会报错，需要先删除本地的 ca.crt 和 ca.key 文件。

### 安装证书

按照导入brup抓https证书的方式导入该证书

浏览器访问http://burp/  
保存证书到桌面  
![图片.png](https://image.3001.net/images/20210714/1626240768_60ee770022b1d56c9a868.png!small)  
![图片.png](https://image.3001.net/images/20210714/1626240708_60ee76c4be5c1ecdd4f3c.png!small)  
重启浏览器，然后就可以抓到https包了。

###  **高级姿势**  
指定扫描插件

使用 --plugins 参数可以选择仅启用部分扫描插件，多个插件之间可使用逗号分隔，如：

./xray webscan --plugins cmd_injection --url http://example.com/

目前提供的插件列表如下：

    
    
    SQL 注入检测 (key: sqldet)：   支持报错注入、布尔注入和时间盲注等
    XSS 检测（key: xss）：         支持扫描反射型、存储型 XSS
    命令/代码注入检测 (key: cmd_injection)：     支持 shell 命令注入、PHP 代码执行、模板注入等
    目录枚举 (key: dirscan)：    检测备份文件、临时文件、debug 页面、配置文件等10余类敏感路径和文件
    路径穿越检测 (key: path_traversal)：     支持常见平台和编码
    XML 实体注入检测 (key: xxe)：    支持有回显和反连平台检测
    POC 管理 (key: phantasm)：    默认内置部分常用的 POC，用户可以根据需要自行构建 POC 并运行。可参考：POC 编写文档（https://chaitin.github.io/xray/#/guide/poc）
    文件上传检测 (key: upload)：    支持检测常见的后端服务器语言的上传漏洞
    弱口令检测 (key: brute_force)：    支持检测 HTTP 基础认证和简易表单弱口令，内置常见用户名和密码字典
    JSONP 检测 (key: jsonp)：    检测包含敏感信息可以被跨域读取的 jsonp 接口
    SSRF 检测 (key: ssrf)：    ssrf 检测模块，支持常见的绕过技术和反连平台检测
    基线检查 (key: baseline)：    检测低 SSL 版本、缺失的或错误添加的 http 头等
    任意跳转检测 (key: redirect)：    支持 HTML meta 跳转、30x 跳转等
    CRLF 注入 (key: crlf_injection)：    检测 HTTP 头注入，支持 query、body 等位置的参数
    …
    

只扫描一个 URL

xray 还提供了方便的只扫描一个 URL 的方式，如：

./xray webscan --url http://example.com/ --json-output out.json

###  **配置文件**

xray 还提供了友好配置文件，可以方便地将常用的命令行参数写到配置文件中，避免了每次都要输入一大串参数的痛苦。

xray 默认会读取运行目录下的 config.yaml 文件作为配置危机，也可以使用 —config 参数指定其他配置文件。

关于命令行的详细配置可以参考 xray 官方文档（(https://chaitin.github.io/xray/#/guide/config)。

###  **反连平台**

xray 在运行时会自动启动反连平台来辅助盲打扫描，可以在配置文件中修改反连平台的配置。目前支持 http 和 dns 两种反连机制，当服务端触发
payload 时 xray 会根据反连平台的状态判断漏洞是否存在。

dns 反连需要启用 root 权限监听 53 端口，并且将域名的 ns 记录指向反连平台的监听地址  
自定义 POC

xray 支持用户使用 YAML 编写 POC。YAML 是 JSON 的超集，也就是说我们甚至可以用 JSON 编写 POC，但这里还是建议大家使用
YAML 来编写，原因如下：

    
    
    YAML 格式的 “值” 无需使用双引号包裹，特殊字符无需转义
    YAML 格式使内容更加可读
    YAML 中可以使用注释
    

我们可以编写以下的 yaml 来测试 tomcat put 上传任意文件漏洞：

    
    
    name: poc-yaml-tomcat_put
    rules:
    - method: PUT
    path: /hello.jsp
    body: world
    - method: GET
    path: /hello.jsp
    search: world
    

这里还要感谢 phith0n 贡献的 xray PoC 生成器 (https://phith0n.github.io/xray-poc-generation/) ，虽然丑陋，但不失文雅。

将 POC 保存到 YAML 文件后使用 --poc参数可以方便地调用，如：

./xray webscan --plugins phantasm --poc /home/test/poc.yaml --url
http://example.com/

###  **xray 与 awvs 爬虫联动**

awvs 的爬虫很好用，支持表单分析和单页应用的爬取，xray 的扫描能力比较强，速度也更快。awvs 和 xray 搭配使用则是如虎添翼。这里演示的是扫描
awvs 的在线靶站  
http://testphp.vulnweb.com/

首先启动 xray 的被动代理，下面的命令将启动一个监听在所有网卡 7001 端口的 HTTP 代理, 并将扫描结果保存在 awvs.html 内。

xray_windows_386.exe webscan --listen 0.0.0.0:7001 --html-output awvs.html

以 awvs 13 web 版为例，登入管理页后，点击 Targets, 然后点击 Add Target 添加扫描目标:  
![图片.png](https://image.3001.net/images/20210714/1626240895_60ee777f0209de95c0443.png!small)  
然后切换到 HTTP 的部分，填写 xray 的 HTTP 代理。  
![图片.png](https://image.3001.net/images/20210714/1626240912_60ee7790eb7c312e91fae.png!small)  
地址需要根据实际情况填写，需要填写为 awvs 所在机器（容器）内能够访问到 xray 代理的地址。如果 xray 在外网，则填写为外网主机的 IP
地址。端口填写为上面启动时设置的端口号。

其他项可以按需调整或保持默认，然后点击 scan 按钮，按图示选择 Crawl Only 即仅使用爬虫，然后点击 Create Scan 就可以开始扫描了。  
![图片.png](https://image.3001.net/images/20210714/1626240927_60ee779f17381a25306c6.png!small)  
检查 xray 的界面有没有在扫描，如果有类似下图的结果说明工作正常，等待扫描完成即可。  
![图片.png](https://image.3001.net/images/20210714/1626240946_60ee77b29fe0290142032.png!small)扫描完成后可以查看
avws.html 查看漏洞详情。

 **学习社群qq：3542167150**

