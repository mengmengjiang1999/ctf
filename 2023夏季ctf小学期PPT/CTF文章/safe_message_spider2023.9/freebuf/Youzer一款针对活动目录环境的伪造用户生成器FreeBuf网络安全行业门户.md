***本工具仅供技术分享、交流讨论，严禁用于非法用途**

![a.png](https://image.3001.net/images/20190722/1563810854_5d35dc2679725.png!small)

## Youzer介绍

**Youzer是一款针对活动目录环境的伪造用户生成器，Youzer的目标就是创建一个包含大量信息的活动目录环境，该工具使用了Python3代码库“faker”来生成随机账号。**

    
    
    pip3 install faker

你可以提供一个字典文件，或预生成的密码。生成选项可以用来测试Hashcat规则等等，字典选项在提供特定的密码列表时也非常有用，我们可以用它来实现字典攻击。

输出数据为一个CSV文件和一个PowerShell脚本，它们会被拷贝到目标设备中。在执行过程中，PowerShell脚本会绑定LDAP，所以它不依赖于新的活动目录模块。

### RoadMap

> 1、 生成多个部门（OU）；
>
> 2、 生成组架构并随机分配；
>
> 3、 实现额外的Faker对象属性来填充LDAP域，例如地址和区域等等；
>
> 4、 从创建嵌套分组结构的组织结构图；

## 工具使用样例

Youzer可以在30秒内创建十万个伪造的用户账号，并在大约3分钟内创建一百万个随机用户账号：

    
    
    [-]Domain Name set to : example
    
    [*]Writing to output file : sales_example.csv
    
    [!]Generating 100000 users in password generate mode
    
    [!]Creating Powershell script for import : sales_example.ps1
    
    python3 youzer.py --generate --generate_length 20 --ou --domain example      20.35s user0.11s system 95% cpu 21.354 total

## 工具演示视频

视频地址：<https://www.youtube.com/watch?v=DIdFxF814AA>

### 使用随机生成的字符密码创建1000个用户账号：

    
    
    python3 youzer.py --generate --generate_length 20 --ou"ou=sales,dc=example,dc=domain" --domain example --users 1000--output sales_example.csv
    
    ?88   d8P d8888b ?88   d8Pd88888P  d8888b 88bd88b
    
    d88   88 d8P' ?88d88   88    d8P' d8b_,dP  88P'  `
    
    ?8(  d88 88b  d88?8(  d88 d8P'   88b     d88
    
    `?88P'?8b`?8888P'`?88P'?8bd88888P'`?888P'd88'
    
           )88
    
          ,d8P                            version : 0.1
    
       `?888P'
    
    author  : @lorentzenman
    
    team    : SpiderLabs
    
    [-]Domain Name set to : example
    
    [*]Writing to output file : sales_example.csv
    
    [!]Generating 1000 users in password generate mode
    
    [!]Creating Powershell script for import : sales_example.ps1

### CSV文件样本输出：

    
    
    Name,GivenName,sn,ou,password,address,description
    
    DennisShaw,Dennis,Shaw,"ou=sales,dc=example,dc=domain",VwVeloi09FaECRdNbbXD,
    
    SamFrancis,Sam,Francis,"ou=sales,dc=example,dc=domain",qhitxgjDW4gZFuraLJbB,
    
    EllieFreeman,Ellie,Freeman,"ou=sales,dc=example,dc=domain",7qbLcknqlPtpkOzdLyw3,
    
    TerenceArnold,Terence,Arnold,"ou=sales,dc=example,dc=domain",lumPMbDk1YomypRj26by,
    
    AnneMurphy,Anne,Murphy,"ou=sales,dc=example,dc=domain",6r42EGGoEJYe9PydHRTV,
    
    WendySmith,Wendy,Smith,"ou=sales,dc=example,dc=domain",tKI2zFUOU8XdK4ZTUJas,
    
    JayLyons,Jay,Lyons,"ou=sales,dc=example,dc=domain",wxEIbw18tW9uFYXtMI9H,
    
    JonathanWhite,Jonathan,White,"ou=sales,dc=example,dc=domain",caoHcm2Y90lIH7zskJYr,
    
    AdamRoberts,Adam,Roberts,"ou=sales,dc=example,dc=domain",Qu0y7mlb2haQQddxYrcN,
    
    GeorginaJones,Georgina,Jones,"ou=sales,dc=example,dc=domain",rYBjxs4tpj9Qza7HcKYI,
    
    LeeNewton,Lee,Newton,"ou=sales,dc=example,dc=domain",6CVlBvEutc3Ahco2UI5q,
    
    AaronSmith,Aaron,Smith,"ou=sales,dc=example,dc=domain",hmSSoKILfvrHuHbPTDIQ,
    
    MaxHall,Max,Hall,"ou=sales,dc=example,dc=domain",11Ys9Zdk2M8J1JAScBkP,
    
    KimberleyDouglas,Kimberley,Douglas,"ou=sales,dc=example,dc=domain",WQ9285gSHv2MXkwoLYlg,
    
    DeniseFisher,Denise,Fisher,"ou=sales,dc=example,dc=domain",CT1pbfAnCoezuyrJbQX9,

### 根据源字典列表创建1000个用户账户：

    
    
    python3 youzer.py --wordlist~/tools/pw/Probable-Wordlists/Real-Passwords/Top12Thousand-probable-v2.txt --ou"ou=IT,dc=example,dc=domain" --domain example --users 1000 --outputIT_example.csv
    
    ?88   d8P d8888b ?88   d8Pd88888P  d8888b 88bd88b
    
    d88   88 d8P' ?88d88   88    d8P' d8b_,dP  88P'  `
    
    ?8(  d88 88b  d88?8(  d88 d8P'   88b     d88
    
    `?88P'?8b`?8888P'`?88P'?8bd88888P'`?888P'd88'
    
           )88
    
          ,d8P                            version : 0.1
    
       `?888P'
    
    author  : @lorentzenman
    
    team    : SpiderLabs
    
    [-]Domain Name set to : example
    
    [*]Writing to output file : IT_example.csv
    
    [!]Generating 1000 users in wordlist mode
    
    [!]Creating Powershell script for import : IT_example.ps1

### 上述字典选项的CSV输出文件内容：

    
    
    Name,GivenName,sn,ou,password,address,description
    
    RhysParker,Rhys,Parker,"ou=IT,dc=example,dc=domain",houston,
    
    GeoffreyHarris,Geoffrey,Harris,"ou=IT,dc=example,dc=domain",clothing,
    
    GeorgiaDavis,Georgia,Davis,"ou=IT,dc=example,dc=domain",spotty,
    
    GemmaNorris,Gemma,Norris,"ou=IT,dc=example,dc=domain",brendan1,
    
    DanielMarsh,Daniel,Marsh,"ou=IT,dc=example,dc=domain",pauline,
    
    DominicHarvey,Dominic,Harvey,"ou=IT,dc=example,dc=domain",devin,
    
    TeresaStokes,Teresa,Stokes,"ou=IT,dc=example,dc=domain",snapple,
    
    JoannaMorgan,Joanna,Morgan,"ou=IT,dc=example,dc=domain",volcom,
    
    OliverMiddleton,Oliver,Middleton,"ou=IT,dc=example,dc=domain",master,

## 项目地址

> Youzer：【[GitHub传送门](https://github.com/SpiderLabs/youzer)】

 ***
参考来源：[SpiderLabs](https://github.com/SpiderLabs/youzer)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

