![](https://image.3001.net/images/20220411/1649678178_62541762b408cb09e9a2f.jpeg!small)

## 关于socid_extractor

socid_extractor是一款功能强大的OSINT公开资源情报收集工具，在该工具的帮助下，广大研究人员可以轻松从多个不同网站的用户个人页面收集账号信息。值得一提的是，socid_extractor能够通过账号Web页面或API响应来收集用户的相关信息，并将其存储为机器可读的格式。

## 使用的组件

> [ _Maigret_](https://github.com/soxoj/maigret)：强大的名称检查工具，支持从目标账号生成所有可用的信息；
>
> [
> _TheScrapper_](https://github.com/champmq/TheScrapper)：支持从网站爬取电子邮件、手机号码和社交媒体账号；
>
> [ _YaSeeker_](https://github.com/HowToFind-> bot/YaSeeker)：可通过邮件和登录信息收集Yandex账号所有可用的信息；
>
> [ _Marple_](https://github.com/soxoj/marple)：针对给定用户名爬取搜索引擎结果；

## 工具下载

该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/soxoj/socid-extractor.git

除此之外，我们还可以使用pip3命令来安装socid_extractor：

    
    
    $ pip3 install socid-extractor

如果你需要安装该工具的最新开发版本，可以使用下列命令直接从该项目的GitHub库获取：

    
    
    $ pip3 install -U git+https://github.com/soxoj/socid_extractor.git

## 工具测试

    
    
    python3 -m pytest tests/test_e2e.py -n 10  -k 'not cookies' -m 'not github_failed and not rate_limited'

## 工具使用

以命令行工具的形式使用：

    
    
    $ socid_extractor --url https://www.deviantart.com/muse1908
    
    country: France
    
    created_at: 2005-06-16 18:17:41
    
    gender: female
    
    username: Muse1908
    
    website: www.patreon.com/musemercier
    
    links: ['https://www.facebook.com/musemercier', 'https://www.instagram.com/muse.mercier/', 'https://www.patreon.com/musemercier']
    
    tagline: Nothing worth having is easy...

如果没有执行工具的安装脚本，没关系，我们还可以直接使用下列命令来直接运行socid_extractor：

    
    
    $ ./run.py --url https://www.deviantart.com/muse1908

除此之外，我们还可以将该工具以Python库的形式来使用：

    
    
    >>> import socid_extractor, requests
    
    >>> r = requests.get('https://www.patreon.com/annetlovart')
    
    >>> socid_extractor.extract(r.text)
    
    {'patreon_id': '33913189', 'patreon_username': 'annetlovart', 'fullname': 'Annet Lovart', 'links': "['https://www.facebook.com/322598031832479', 'https://www.instagram.com/annet_lovart', 'https://twitter.com/annet_lovart', 'https://you*tube.com/channel/UClDg4ntlOW_1j73zqSJxHHQ']"}

## 支持的网站和方法

该工具针对多种不同的站点和平台提供了[ _超过_ _100_ _种数据收集技术方法_](https://github.com/soxoj/socid-extractor/blob/master/METHODS.md)，其中包括但不限于：

> Google（所有的文档页面和地图点贡献信息），需要Cookie；
>
> Yandex（磁盘、相册、znatoki、音乐、集合等），需要Cookie来防止验证码屏蔽；
>
> Mail.ru（my.mail.ru用户主页、照片、视频、游戏、圈子）
>
> Facebook（用户 & 组页面）
>
> VK.com（用户页面）
>
> OK.ru（用户页面）
>
> Instagram
>
> Reddit
>
> Medium
>
> Flickr
>
> Tumblr
>
> TikTok
>
> GitHub
>
> ...

我们还可以查看该项目提供的【[ _测试文件_](https://github.com/soxoj/socid-extractor/blob/master/tests/test_e2e.py)】来获取数据样例，或查看【[
_scheme文件_](https://github.com/soxoj/socid-extractor/blob/master/socid_extractor/schemes.py)】来了解该工具支持的所有数据收集技术方法。

## 项目地址

 **socid_extractor：** 【[ _GitHub传送门_](https://github.com/soxoj/socid-extractor)】

## 参考资料

> [ _https://github.com/soxoj/maigret_](https://github.com/soxoj/maigret)
>
> [
> _https://github.com/champmq/TheScrapper_](https://github.com/champmq/TheScrapper)
>
> [ _https://github.com/HowToFind-bot/YaSeeker_](https://github.com/HowToFind-> bot/YaSeeker)
>
> [ _https://github.com/soxoj/marple_](https://github.com/soxoj/marple)
>
> [ _https://medium.com/week-in-osint/getting-a-grasp-on-> googleids-77a8ab707e43_](https://medium.com/week-in-osint/getting-a-grasp-> on-googleids-77a8ab707e43)
>
> [ _https://osintcurio.us/2019/10/01/searching-instagram-> part-2/_](https://osintcurio.us/2019/10/01/searching-instagram-part-2/)
>
> [ _https://www.aware-online.com/en/importance-of-user-ids-in-social-media-> investigations/_](https://www.aware-online.com/en/importance-of-user-ids-in-> social-media-investigations/)
>
> [ _https://www.eff.org/wp/behind-the-one-way-> mirror_](https://www.eff.org/wp/behind-the-one-way-mirror)
>
> [ _https://www.nytimes.com/interactive/2019/12/19/opinion/location-tracking-> cell-> phone.html_](https://www.nytimes.com/interactive/2019/12/19/opinion/location-> tracking-cell-phone.html)

