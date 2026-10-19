**Spray是一款能够从活动目录凭证中提取密码的强大工具，该工具目前由[Jacob
Wilkin](https://github.com/Greenwolf/Spray)（Greenwolf）负责开发和维护。**![1591222191_5ed81faf8448d.png!small](https://image.3001.net/images/20200604/1591222191_5ed81faf8448d.png!small)工具依赖

目前，Spray工具所有的依赖组建都已经默认在Kali Linux系统中预安装好了，如果你想要在macOS或其他系统上使用Spray的话，可以使用apt-get或brew来安装curl和rpcclient(smb)：

> rpcclient
>
> curl

## 工具下载

广大研究人员可以使用下列命令将项目源码克隆至本地：

> git clone <https://github.com/Greenwolf/Spray.git>

## 工具使用

这个脚本将能够在一段时间内把活动目录凭证中的密码喷射到目标中，这里要求使用密码策略作为输入参数，这样才能保证账号不被锁定。

除了脚本代码之外，Spray还提供了大量定制化的的多语言密码文件，这些密码是由各种语言中最常见的活动目录密码组合精心编制而成，并且都符合一个大写字母、一个小写字母和一个数字这样的复杂密码组合类别。

### SMB

如果需要针对SMB作为目标来进行密码喷射，则必须要提供用户列表、密码列表、在锁定周期内的每次尝试次数、锁定周期长度以及域名信息：

    
    
    

`Useage: spray.sh -smb <targetIP> <usernameList> <passwordList>
<AttemptsPerLockoutPeriod> <LockoutPeriodInMinutes> <DOMAIN>`

` `

` Example: spray.sh -smb 192.168.0.1 users.txt passwords.txt 1 35 SPIDERLABS`

` `

` Optionally Skip Username%Username Spray: spray.sh -smb 192.168.0.1 users.txt
passwords.txt 1 35 SPIDERLABS skipuu`

` `

### OWA

如需针对OWA作为目标来进行密码喷射，则必须创建一个包含了POST请求信息的文件，其中需要写入Username:
[sprayuser@domain.com](mailto:sprayuser@domain.com)以及Password: spraypassword：

    
    
    

`Useage: spray.sh -owa <targetIP> <usernameList> <passwordList>
<AttemptsPerLockoutPeriod> <LockoutPeriodInMinutes> <RequestsFile>`

` `

` Example: spray.sh -owa 192.168.0.1 users.txt passwords.txt 1 35 post-request.txt`

` `

### Lync

如需针对一个lync服务作为目标来进行密码喷射，则必须提供lync自动发现URL或能够返回www认证Header的URL，同时还需携带一个电子邮件地址列表：

    
    
    

`Useage: spray.sh -lync <targetIP> <usernameList> <passwordList>
<AttemptsPerLockoutPeriod> <LockoutPeriodInMinutes>`

` `

` Example: spray.sh -lync <https://lyncdiscover.spiderlabs.com/> users.txt
passwords.txt 1 35`

` `

` Example: spray.sh -lync
<https://lyncweb.spiderlabs.com/Autodiscover/AutodiscoverService.svc/root/oauth/user>
users.txt passwords.txt 1 35`

` `

### 思科Web VPN

如果需要针对思科Web VPN服务作为目标来进行密码喷射，则需要提供目标端口以及目标服务托管的端口信息：

    
    
    

`Useage: spray.sh -cisco <targetURL> <usernameList> <passwordList>
<AttemptsPerLockoutPeriod> <LockoutPeriodInMinutes>`

` `

` Example: spray.sh -ciso 192.168.0.1 usernames.txt passwords.txt 1 35`

` `

### 密码列表更新

我们可以根据当前年份来更新我们的密码列表，比如说（2016/2017）：

    
    
    

`Useage: spray.sh -passupdate <passwordList>`

` `

` Example: spray.sh -passupdate passwords.txt`

` `

当然了，我们还可以将目标企业或组织名称作为可选参数添加至密码列表中：

    
    
    

`Useage: spray.sh -passupdate <passwordList> <CompanyName>`

` `

` Example: spray.sh -passupdate passwords.txt Spiderlabs`

` `

### 用户名生成

我们还可以根据一系列常用名称来生成我们的用户名列表：

    
    
    

`Useage: spray.sh -genusers <firstnames> <lastnames> "<<fi><li><fn><ln>>"`

` `

` Example: spray.sh -genusers english-first-1000.txt english-last-1000.txt
"<fi><ln>"`

` `

` Example: spray.sh -genusers english-first-1000.txt english-last-1000.txt
"<fn>.<ln>"`

` `

### 许可证协议

Spray项目的开发和发布遵循GNU General Public开源许可证协议。

## 项目地址

> Spray：【[GitHub传送门](https://github.com/Greenwolf/Spray)】

## 参考来源

> [Greenwolf](https://github.com/Greenwolf/Spray)

