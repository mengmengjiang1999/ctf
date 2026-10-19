![](https://image.3001.net/images/20220623/1655970051_62b41903bdf82759eb2cf.png!small)  

## 关于Blackbird

Blackbird是一款功能强大的公开资源情报收集工具，该工具可以帮助广大研究人员通过目标用户的用户名来快速搜索多达119个社交媒体网站，并收集相关账户的信息。

Blackbird支持发送异步HTTP请求，因此可以大幅度提升运行效率和工具性能。

## 功能特性

> 1、本地Web服务器
>
> 2、按用户名搜索
>
> 3、元数据提取
>
> 4、JSON数据读取和存储
>
> 5、报告生成
>
> 6、效率高速度快

## 支持的社交媒体网站

当前版本的Blackbird支持下列社交媒体网站：

> Facebook
>
> YouTube
>
> Twitter
>
> Telegram
>
> TikTok
>
> Tinder
>
> Instagram
>
> Pinterest
>
> Snapchat
>
> Reddit
>
> Soundcloud
>
> Github
>
> Steam
>
> Linktree
>
> Xbox Gamertag
>
> Twitter Archived
>
> Xvideos
>
> PornHub
>
> Xhamster
>
> Periscope
>
> Ask FM
>
> Vimeo
>
> Twitch
>
> Pastebin
>
> WordPress Profile
>
> WordPress Site
>
> AllMyLinks
>
> Buzzfeed
>
> JsFiddle
>
> Sourceforge
>
> Kickstarter
>
> Smule
>
> Blogspot
>
> Tradingview
>
> Internet Archive
>
> Alura
>
> Behance
>
> MySpace
>
> Disqus
>
> Slideshare
>
> Rumble
>
> Ebay
>
> RedBubble
>
> Kik
>
> Roblox
>
> Armor Games
>
> Fortnite Tracker
>
> Duolingo
>
> Chess
>
> Shopify
>
> Untappd
>
> Last FM
>
> Cash APP
>
> Imgur
>
> Trello
>
> Minecraft
>
> Patreon
>
> DockerHub
>
> Kongregate
>
> Vine
>
> Gamespot
>
> Shutterstock
>
> Chaturbate
>
> ProtonMail
>
> TripAdvisor
>
> RapidAPI
>
> HackTheBox
>
> Wikipedia
>
> Buymeacoffe
>
> Arduino
>
> League of Legends Tracker
>
> Lego Ideas
>
> Fiverr
>
> Redtube
>
> Dribble
>
> Packet Storm Security
>
> Ello
>
> Medium
>
> Hackaday
>
> Keybase
>
> HackerOne
>
> BugCrowd
>
> OneCompiler
>
> TryHackMe
>
> Lyrics Training
>
> Expo
>
> RAWG
>
> Coroflot
>
> Cloudflare
>
> Wattpad
>
> Mixlr
>
> ImageShack
>
> Freelancer
>
> Dev To
>
> BitBucket
>
> Ko Fi
>
> Flickr
>
> HackerEarth
>
> Spotify
>
> Snapchat Stories
>
> Audio Jungle
>
> Avid Community
>
> Bandlab
>
> Carrd
>
> CastingCallClub
>
> Coderwall
>
> Codewars
>
> F3
>
> Gab
>
> Issuu
>
> Steemit
>
> Venmo
>
> MODDB
>
> COLOURlovers
>
> Scheme Color
>
> Roblox Trade
>
> Aetherhub
>
> BugBounty
>
> Huntr

大家也可以根据自己的需求对项目代码进行修改和扩展，以支持其他的站点。

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/p1ngul1n0/blackbird
    
    cd blackbird

使用cd命令切换到项目目录中，然后使用pip命令并通过requirements.txt文件安装该工具所需的依赖组件：

    
    
    pip install -r requirements.txt

## 工具使用

### 通过用户名搜索

    
    
    python blackbird.py -u username

### 运行WebServer

    
    
    python blackbird.py --web

运行后，可以通过浏览器访问http://127.0.0.1:5000来管理和控制Blackbird的WebServer。

### 读取扫描结果文件

    
    
    python blackbird.py -f username.json

### 查看支持的社交媒体网站

    
    
    python blackbird.py --list-sites

## JSON模版

Blackbird支持使用JSON作为模版来存储和读取数据。

项目中的[ _data_ _._
_json_](https://github.com/p1ngul1n0/blackbird/blob/main/data.json)文件中存储了Blackbird支持验证的所有社交媒体网站。

### 模版参数

> app：站点名称
>
> url：站点地址
>
> valid：一个Python表达式，当用户存在时返回True
>
> id：唯一的数字ID
>
> method：HTTP方法
>
> json：JSON POST Body
>
> {username}：目标用户名
>
> response.status：HTTP响应状态
>
> responseContent：原始请求Body
>
> soup：Beautifulsoup解析的请求Body
>
> jsonData：JSON请求Body

### 参考样例

 **GET：**

    
    
    {
    
          "app": "ExampleAPP1",
    
          "url": "https://www.example.com/{username}",
    
          "valid": "response.status == 200",
    
          "id": 1,
    
          "method": "GET"
    
        }

 **POST JSON：**

    
    
    {
    
          "app": "ExampleAPP2",
    
          "url": "https://www.example.com/user",
    
          "valid": "jsonData['message']['found'] == True",
    
          "json": "{{\"type\": \"username\",\"input\": \"{username}\"}}",
    
          "id": 2,
    
          "method": "POST"
    
        }

## 工具运行截图

![](https://image.3001.net/images/20220623/1655970153_62b41969b9ed14866350e.png!small)![](https://image.3001.net/images/20220623/1655970160_62b41970e4d757ae4045c.png!small)

## 项目地址

 **Blackbird** ：【[ _GitHub传送门_](https://github.com/p1ngul1n0/blackbird)】

## 参考资料

> [
> _https://github.com/p1ngul1n0/blackbird/blob/main/data.json_](https://github.com/p1ngul1n0/blackbird/blob/main/data.json)
>
> [ _https://codebeautify.org/json-escape-> unescape_](https://codebeautify.org/json-escape-unescape)

