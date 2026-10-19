## 关于SocialPwned

SocialPwned是一款功能强大的OSINT公开资源情报收集工具，该工具可以帮助广大研究人员从Instagram、Linkedin和Twitter等社交网络上收集目标用户相关的电子邮件信息，然后再从PwnDB或Dehashed中查找可能存在的凭证泄漏，最后再通过GHunt来获取目标用户相关的Google账号信息。

该工具的目的不仅是为了保护用户的个人数据及隐私安全，而且也是在保护企业的安全。因为，公司员工在社交网络上发布电子邮件地址或相关信息是很常见的。因此，如果这些电子邮件的凭据被泄露的话，那么泄漏的密码可能已经被网络犯罪分子在目标环境中重新使用了。如果泄漏的凭证没有被不法分子所利用的话，SocialPwned的扫描发现也可以帮助你及时修改账号凭证的密码或创建密码的模式，以保护账号的安全。

## 使用的API

> [ _Instagram API_](https://github.com/LevPasha/Instagram-API-python)
>
> [ _Linkedin API_](https://github.com/tomquirk/linkedin-api)
>
> [ _Twint_](https://github.com/twintproject/twint)
>
> [ _PwnDB_](https://github.com/davidtavarez/pwndb)
>
> [ _GHunt_](https://github.com/mxrch/GHunt)

## 工具安装

### 自动化安装

    
    
    $ service docker start
    
    $ docker pull mrtuxx/socialpwned
    
    $ docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --help

注意：这种方法需要我们在本地设备上安装并配置好Docker服务。

### 手动安装

首先，我们需要在本地系统上安装并配置好Tor依赖组件，下面的命令可以在Debian上完成上述任务：

    
    
    $ sudo apt-get install tor
    
    $ /etc/init.d/tor start

接下来，使用Git命令将该项目源码克隆至本地，并安装相关的依赖组件：

    
    
    $ git clone https://github.com/MrTuxx/SocialPwned.git
    
    $ cd SocialPwned
    
    $ sudo pip3 install --user --upgrade git+https://github.com/twintproject/twint.git@origin/master#egg=twint
    
    $ sudo pip3 install -r requirements.txt
    
    $ sudo python3 socialpwned.py --credentials credentials.json --help

## 工具使用

如需使用Instagram和Linkedin的功能，你则需要在每个社交网络上创建一个帐户。此时，必须在JSON文件中提供对应平台的账号凭据：

    
    
    {
    
        "instagram":{
    
            "username":"username",
    
            "password":"password"
    
        },
    
        "linkedin":{
    
            "email":"email",
    
            "password":"password"
    
        },
    
        "ghunt":{
    
            "SID":"SID",
    
            "SSID":"SSID",
    
            "APISID":"APISID",
    
            "SAPISID":"SAPISID",
    
            "HSID":"HSID"
    
        },
    
        "dehashed":{
    
             "email":"email",
    
             "apikey":"apikey"
    
        }
    
    }

## 工具使用帮助

    
    
    usage: socialpwned.py [-h] --credentials CREDENTIALS [--pwndb] [--tor-proxy PROXY] [--instagram] [--info QUERY]
    
                          [--location LOCATION_ID] [--hashtag-ig QUERY] [--target-ig USERNAME] [--search-users-ig QUERY]
    
                          [--my-followers] [--my-followings] [--followers-ig] [--followings-ig] [--linkedin]
    
                          [--company COMPANY_ID] [--search-companies QUERY] [--employees] [--my-contacts]
    
                          [--user-contacts USER_ID] [--search-users-in QUERY] [--target-in USERNAME] [--add-contacts]
    
                          [--add-a-contact USER_ID] [--twitter] [--limit LIMIT] [--year YEAR] [--since DATE]
    
                          [--until DATE] [--profile-full] [--all-tw] [--target-tw USERNAME] [--hashtag-tw USERNAME]
    
                          [--followers-tw] [--followings-tw] [--ghunt] [--email-gh email@gmail.com] [--dehashed]
    
                          [--email-dh email@gmail.com]

如果你想拉取Docker镜像的话，可以使用下列命令：

    
    
    docker run -v $(pwd)/<YOUR CREDENTIALS JSON FILE>:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json <COMMANDS>

## 工具输出格式

SocialPwned的每一次执行，都会生成如下所示的目录文档结构：

    
    
    output
    
    └── session_year_month_day_time
    
        ├── dehashed
    
        │   ├── raw_dehashed.txt
    
        │   └── socialpwned_dehashed.txt
    
        ├── emails
    
        │   └── socialpwned_emails.txt
    
        ├── instagram
    
        │   └── socialpwned_instagram.txt
    
        ├── linkedin_userames
    
        │   ├── first.last.txt
    
        │   ├── firstl.txt
    
        │   ├── first.txt
    
        │   ├── f.last.txt
    
        │   ├── flast.txt
    
        │   ├── lastf.txt
    
        │   └── rawnames.txt
    
        ├── pwndb
    
        │   ├── passwords_pwndb.txt
    
        │   ├── pwndb.txt
    
        │   └── socialpwned_pwndb.txt
    
        ├── socialpwned.json
    
        └── twitter
    
            └── socialpwned_twitter.txt

## 工具使用演示

### Instagram

![](https://image.3001.net/images/20220226/1645810570_6219138ab8fb9b5f4a927.png!small)![](https://image.3001.net/images/20220226/1645810577_621913916fe49b28c6d6a.png!small)

  

 **操作命令：**

    
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --instagram --info España
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --instagram --location 832578276
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --instagram --hashtag-ig someHashtag --pwndb
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --instagram --target-ig username --pwndb
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --instagram --target-ig username --followers-ig --followings-ig --pwndb

### LinkedIn

![](https://image.3001.net/images/20220226/1645810610_621913b218b4c1ff8de24.png!small)![](https://image.3001.net/images/20220226/1645810618_621913baaaa7fea0461b5.png!small)

![](https://image.3001.net/images/20220226/1645810631_621913c7c6f795b518971.png!small)

 **操作命令：**

    
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --linkedin --search-companies "My Target"
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --linkedin --search-companies "My Target" --employees --pwndb
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --linkedin --company 123456789 --employees --pwndb
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --linkedin --company 123456789 --employees --add-contacts
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --linkedin --user-contacts user-id --pwndb
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --linkedin --user-contacts user-id --add-contacts

### Twitter

![](https://image.3001.net/images/20220226/1645810800_62191470665ee2f7d4610.png!small)

 **操作命令：**

    
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --twitter --hashtag-tw someHashtag --pwndb --limit 200 --dehashed
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --twitter --target-tw username --all-tw --pwndb --dehashed --ghunt
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --twitter --target-tw username --all-tw --followers-tw --followings-tw --pwndb

### 邮件数据收集（GHunt）

![](https://image.3001.net/images/20220226/1645810838_621914963759ffdf01457.png!small)

 **操作命令：**

    
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --ghunt --email-gh "email@example.com"

### 凭证数据收集（哈希）

![](https://image.3001.net/images/20220226/1645810868_621914b4942773fd5d238.png!small)

 **操作命令：**

    
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --dehashed --email-dh "email@example.com"

### 联合查询

    
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --instagram --target-ig username --followers-ig --followings-ig --linkedin --company 123456789 --employees --twitter --target-tw username --all-tw --pwndb --ghunt --dehashed
    
    docker run -v $(pwd)/credentials.json:/socialpwned/credentials.json -v $(pwd)/output:/socialpwned/output -it mrtuxx/socialpwned socialpwned.py --credentials credentials.json --instagram --target-ig username --linkedin --target-in username --twitter --target-tw username --all-tw --pwndb --ghunt --dehashed

## 工具演示视频

 **视频地址：**[
_https://www.you*tube.com/watch?v=ErHzZN5QFHo_](https://www.youtube.com/watch?v=ErHzZN5QFHo)

## 项目地址

 **SocialPwned：** 【[ _GitHub传送门_](https://github.com/MrTuxx/SocialPwned)】

## 参考资料

> [ _https://github.com/mxrch/GHunt#manual-> installation_](https://github.com/mxrch/GHunt#manual-installation)
>
> [ _https://github.com/mxrch/GHunt#where-i-find-> these-5-cookies-_](https://github.com/mxrch/GHunt#where-i-find-> these-5-cookies-)
>
> [ _https://github.com/LevPasha/Instagram-API-> python_](https://github.com/LevPasha/Instagram-API-python)
>
> [ _https://github.com/tomquirk/linkedin-> api_](https://github.com/tomquirk/linkedin-api)
>
> [
> _https://github.com/twintproject/twint_](https://github.com/twintproject/twint)
>
> [
> _https://github.com/davidtavarez/pwndb_](https://github.com/davidtavarez/pwndb)
>
> [ _https://github.com/mxrch/GHunt_](https://github.com/mxrch/GHunt)

