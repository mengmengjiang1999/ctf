**Galileo是一款针对Web应用程序的开源渗透测试工具，可帮助开发和渗透测试人员识别并利用其Web应用程序中的漏洞。**

## 截图

**![screen.png](https://image.3001.net/images/20180529/15275511062265.png!small)**

##  **安装**

    
    
    $ git clone https://github.com/m4ll0k/Galileo.git galileo
    $ cd galileo

 **安装依赖**

    
    
    $ pip install -r requirements.txt

或

    
    
    $ apt-get install python-pysocks

 **windows**

    
    
    $ python -m pip install pysocks

 **运行**

    
    
    $ python galileo.py

##  **使用**

设置全局选项：

    
    
    galileo #> set
      Set A Context-Specific Variable To A Value
      ------------------------------------------      - Usage: set <option> <value>
      - Usage: set COOKIE phpsess=hacker_test
    
    
      Name        Current Value                            Required  Description
      ----------  -------------                            --------  -----------      PAUTH                                                no        Proxy auth credentials (user:pass)
      PROXY                                                no        Set proxy (host:port)
      REDIRECT    True                                     no        Set redirect
      THREADS     5                                        no        Number of threads
      TIMEOUT     5                                        no        Set timeout
      USER-AGENT  Mozilla/5.0 (X11; Ubuntu; Linux x86_64)  yes       Set user-agent
      VERBOSITY   1                                        yes       Verbosity level (0 = minimal,1 = verbose)

搜索模块：

    
    
    galileo #> search disclosure
    [+] Searching for 'disclosure'...
    
      Disclosure
      ----------        disclosure/code
        disclosure/creditcard
        disclosure/email
        disclosure/privateip
    

显示模块：

    
    
    galileo #> show modules
    
      Bruteforce
      ----------        bruteforce/auth_brute
        bruteforce/backup_brute
        bruteforce/file_dir_brute
    
      Disclosure
      ----------        disclosure/code
        disclosure/creditcard
        disclosure/email
        disclosure/privateip
    
      Exploits
      --------        exploits/shellshock
    
      Fingerprint
      -----------        fingerprint/cms
        fingerprint/framework
        fingerprint/server
    
      Injection
      ---------        injection/os_command_injection
        injection/sql_injection
    
      Scanner
      -------        scanner/asp_trace
    
      Tools
      -----        tools/socket

使用模块：

    
    
    galileo #> use bruteforce/backup_brute
    galileo bruteforce(backup_brute) #> 

设置模块选项

    
    
    galileo bruteforce(backup_brute) #> show options
    
      Name      Current Value  Required  Description
      --------  -------------  --------  -----------      EXTS                     no        Set backup extensions
      HOST                     yes       The target address
      METHOD    GET            no        HTTP method
      PORT      80             no        The target port
      URL_PATH  /              no        The target URL path
      WORDLIST                 yes       Common directory wordlist
    
    galileo bruteforce(backup_brute) #> set HOST www.xxxxxxx.com
    HOST => www.xxxxxxx.com
    galileo bruteforce(backup_brute) #> set WORDLIST /home/m4ll0k/Desktop/all.txt
    WORDLIST => /home/m4ll0k/Desktop/all.txt

运行：

    
    
    galileo bruteforce(backup_brute) #> run

![screen2.png](https://image.3001.net/images/20180529/15275511293135.png!small)

 ***参考来源：[github](https://github.com/m4ll0k/Galileo)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**  

