**pepe是一个基于python的用于从Pastebin收集有关泄露电子邮件地址信息的脚本工具。**

**![pepe.png](https://image.3001.net/images/20190428/1556405431_5cc4dcb7efc57.png!small)**

它会解析Pastebin
email:password转储并收集有关每个电子邮件地址的信息。pepe目前支持Google，Trumail，Pipl，FullContact和HaveIBeenPwned。此外，它还允许你向人发送有关其泄露密码的信息邮件，最后每个信息都会在Elasticsearch中进行进一步的探索。

它只支持一种格式 - email:password。

目前，通知（notification）仅在FullContact上找到匹配时才会工作，然后会向你发送电子邮件地址和关联的社交媒体帐户。

## 安装条件

> Python 3
>
> FullContact API <https://www.fullcontact.com/developer/>
>
> Google
>
> Pipl API <https://pipl.com/api/>
>
> HaveIBeenPwned
>
> SafePush (通知 - 可选 - 正在进行中) <https://www.pushsafer.com/>
>
> Trumail <https://trumail.io/>
>
> Gmail account (发送电子邮件)
>
> Elasticsearch (可选)
    
    
    pip install -r requirements

## Config

    
    
    {"domains": 
      { #domains to whitelist or blacklist
      "whitelist": [""],
      "blacklist": ["yahoo.com"]
    },
    "keys": 
      { #API KEYS
      "pushsafer": "API_KEY",
      "fullcontact": "API_KEY",
      "pipl": "API_KEY"
    },
    "gmail": 
      { #GMAIL credentials and informational message that will be send
      "username": "your_username@gmail.com",
      "password": "password",
      "message": "Hey,\n\nI am a security researcher and I want to inform you that your password !PASSWORD! has been leaked and you should change it immediately.\nThis email is part of the research, you can find more about it on https://medium.com/@wojciech\n\nStay safe!"},
    "elasticsearch":
      { #ElasticSearch connection info
      "host": "127.0.0.1",
      "port": 9200}
    }

## 使用

    
    
    root@kali:~/PycharmProjects/pepe# python pepe.py -h
    usage: pepe.py [-h] [--file FILE] [--stream] [--interactive]
                     [--modules MODULES [MODULES ...]] [--elasticsearch]
                     [--whitelist] [--blacklist]
    
                                ,=.
                  ,=''''==.__.="  o".___
            ,=.=="                  ___/
      ,==.,"    ,          , \,===""
     <     ,==)  "'"=._.==)    `==''    `"           `
    
      clover/snark^
      http://ascii.co.uk/art/platypus
      
      Post Exploitation Pastebin Emails
      github.com/woj-ciech
      medium.com/@woj_ciech
      
      Example:
      python pepe.py --file <dump.txt> --interactive --whitelist
      python pepe.py --file <dump.txt> --modules hibp google trumail --elasticsearch --blacklist
    
    optional arguments:
      -h, --help            显示帮助信息并退出
      --file FILE           加载文件
      --stream              Stream Pastebin
      --interactive         交互模式
      --modules MODULES [MODULES ...]
                            用于检查非交互模式的模块
      --elasticsearch       输出到ElasticSearch
      --whitelist           白名单列表
      --blacklist           黑名单列表

## 示例

交互模式，单独检查每个电子邮件并执行特定模块。

    
    
    root@kali:~/PycharmProjects/pepe# python pepe.py --file paste.txt --interactive --blacklist
    
    -----------------------Found email [REDACTED]@hotmail.com with password [REDACTED]-----------------------    [A] Add domain hotmail.com to blacklist
    [T] Test
    [G] Google search
    [H] HaveIBeenPwned
    [P] Pipl
    [F] FullContact
    [I] Inform
    [N] Next
    > G
    ---Google Search---    http://[REDACTED]
    http://[REDACTED]
    http://[REDACTED]
    
    [A] Add domain gmail.com to blacklist
    [T] Test
    [G] Google search
    [H] HaveIBeenPwned
    [P] Pipl
    [F] FullContact
    [I] Inform
    [N] Next
    > N
    -----------------------Found email [REDACTED].[REDACTED]@gmail.com with password [REDACTED]-----------------------    [A] Add domain gmail.com to blacklist
    [T] Test
    [G] Google search
    [H] HaveIBeenPwned
    [P] Pipl
    [F] FullContact
    [I] Inform
    [N] Next
    > F
    ---FullContact---    [REDACTED] [REDACTED]
    https://twitter.com/[REDACTED]
    https://facebook.com/[REDACTED]
    https:/linkedin.com/[REDACTED]
    [A] Add domain gmail.com to blacklist
    [T] Test
    [G] Google search
    [H] HaveIBeenPwned
    [P] Pipl
    [F] FullContact
    [I] Inform
    [N] Next
    > P
    ---Pipl---    Name: [REDACTED]
    [REDACTED] years old
    Jobs:
    Quality Control [REDACTED] (since 2018)
    [REDACTED] Review [REDACTED] (2017-2018)
    [REDACTED] Attorney [REDACTED] (2017-2018)
    [REDACTED] Attorney at [REDACTED] (2017-2017)
    ...
    [REDACTED] (2012-2012)
    [REDACTED] Assistant at [REDACTED] (2012-2012)
    Author/Founder at [REDACTED] (2009-2011)
    https://www.linkedin.com/in/[REDACTED]
    http://www.facebook.com/people/[REDACTED]
    http://twitter.com/[REDACTED]
    http://pinterest.com/[REDACTED]
    https://plus.google.com/[REDACTED]
    
    ...
    [REDACTED]

非交互模式，仅针对电子邮件地址执行所选模块。

    
    
    root@kali:~/PycharmProjects/# python pepe.py --file pastetest.txt --blacklist --modules hibp google fullcontact trumail --elasticsearch
    -----------------------Found email [REDACTED]@hotmail.com with password [REDACTED]-----------------------    ---Google Search---    https://pastebin.com/[REDACTED]
    ---Have I Been Pwned---    LinkedIn
    ---FullContact---    No results
    ---Trumail---    Email test passed
    -----------------------Found email charlie.[REDACTED]@live.com with password [REDACTED]-----------------------    ---Google Search---    https://justpaste.it/[REDACTED]
    https://pastebin.com/[REDACTED]
    ---Have I Been Pwned---    MyHeritage
    RiverCityMedia
    Tumblr
    YouveBeenScraped
    ---FullContact---    Charlie [REDACTED]
    https://twitter.com/[REDACTED]
    [REDACTED]
    ---Trumail---    Email test passed
    -----------------------Found email [REDACTED].[REDACTED]@gmail.com with password [REDACTED]-----------------------    ---Google Search---    http://[REDACTED]
    http://[REDACTED]
    http://[REDACTED]
    https://pastebin.com/[REDACTED]
    ---Have I Been Pwned---    BTSec
    Exactis
    HauteLook
    Houzz
    LinkedIn
    ---FullContact---    [REDACTED] [REDACTED]
    https://www.facebook.com/[REDACTED]
    [REDACTED]
    ---Trumail---    Email test passed
    -----------------------Found email [REDACTED].[REDACTED]@gmail.com with password [REDACTED]-----------------------    ---Google Search---    https://[REDACTED]
    https://[REDACTED]
    https://[REDACTED]
    https://pastebin.com/[REDACTED]
    ---Have I Been Pwned---    Lastfm
    LinkedIn
    MySpace
    Trillian
    Tumblr
    ---FullContact---    [REDACTED] [REDACTED] [REDACTED].
    https://www.facebook.com/[REDACTED]
    https://plus.google.com/[REDACTED]
    https://www.linkedin.com/in/[REDACTED]
    http://www.pinterest.com/[REDACTED]
    https://twitter.com/[REDACTED]
    https://youtube.com/user/[REDACTED]
    [REDACTED]

## 相关截图

![pipl.jpg](https://image.3001.net/images/20190428/1556405509_5cc4dd051d1d6.jpg!small)![kibana.jpg](https://image.3001.net/images/20190428/1556405522_5cc4dd1272225.jpg!small)![email.jpg](https://image.3001.net/images/20190428/1556405534_5cc4dd1ecb825.jpg!small)

 ***参考来源：[GitHub](https://github.com/woj-ciech/pepe)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

