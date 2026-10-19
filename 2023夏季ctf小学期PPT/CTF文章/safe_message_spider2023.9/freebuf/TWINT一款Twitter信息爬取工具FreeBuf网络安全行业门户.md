![](https://image.3001.net/images/20190827/1566877610_5d64a7aad0c16.png!small)

![](https://image.3001.net/images/20190827/1566877626_5d64a7bac62b2.png!small)

**Twint是一个用Python写的Twitter抓取工具，允许从Twitter配置文件中抓取推文，不使用Twitter的API。**

 **Twint利用Twitter的搜索语法让您从特定用户那里搜索推文，特定主题，主题标签和相关的推文，或者从推文中挑选敏感信息，如电子邮件和电话号码。**

Twint还对Twitter进行了特殊查询，允许您搜索Twitter用户的关注者，用户喜欢的推文，以及他们在API，Selenium或模拟浏览器的情况下关注的用户。

## 好处

使用Twint和Twitter API的一些好处：

> 1.可以获取几乎 **所有的** 推文（Twitter API限制只能持续3200个推文）;
>
> 2.快速初始设置;
>
> 3.可以匿名使用，无需Twitter注册;
>
> 4. **没有速率限制** 。

##  Twitter的限制

Twitter会限制用户可以浏览的时间线。这意味着通过.Profile或者.Favorites你只可以看到~3200条推文。

##  要求

> 1.Python 3.6;
>
> 2.aiohttp;
>
> 3.aiodns;
>
> 4.beautifulsoup4;
>
> 5.cchardet;
>
> 6.elasticsearch;
>
> 7.pysocks;
>
> 8.pandas （> = 0.23.0）;
>
> 9.aiohttp_socks;
>
> 10.schedule;
>
> 11.geopy;
>
> 12.fake-useragent。

##  安装

###  Git的方法：

    
    
    git clone https://github.com/twintproject/twint.git
    pip3 install -r requirements.txt

###  PIP：

    
    
    pip3 install twint

要么

    
    
    pip3 install --user --upgrade -e git + https//github.com/twintproject/twint.git@origin/master#egg=twint

###  Pipenv：

    
    
    pipenv install -e git + https：//github.com/twintproject/twint.git#egg=twint

##  CLI基本示例和组合

一些简单的例子可以帮助您掌握基础知识：

> 1.twint -u username- 从用户的时间线中删除所有推文。
>
> 2.twint -u username -s pineapple- 从包含pineapple的用户时间线中删除所有推文。
>
> 3.twint -s pineapple- 从每个人的推文收集每个包含pineapple的推文。
>
> 4.twint -u username --year 2014- 收集2014年 **之前发送** 推文的推文。
>
> 5.twint -u username --since 2015-12-20 - 收集自2015-12-20以来推文的推文。
>
> 6.twint -u username -o file.txt - 抓取推文并保存到file.txt。
>
> 7.twint -u username -o file.csv --csv - 抓取推文并保存为csv文件。
>
> 8.twint -u username --email --phone - 显示可能包含电话号码或电子邮件地址的推文。
>
> 9.twint -s "Donald Trump" --verified - 由经过验证的用户显示有关唐纳德特朗普的推文。
>
> 10.twint -g="48.880048,2.385939,1km" -o file.csv --csv -> 在巴黎一个地方绕半径1公里的推文将它们导出到csv文件中。
>
> 11.twint -u username -es localhost:9200 - 输出推文到Elasticsearch数据库中
>
> 12.twint -u username -o file.json --json - 抓取推文并保存为json文件。
>
> 13.twint -u username --database tweets.db - 将推文保存到SQLite数据库。
>
> 14.twint -u username --followers - Twitter用户的粉丝。
>
> 15.twint -u username --following - Twitter用户关注的人。
>
> 16.twint -u username --favorites - 收集用户最喜欢的所有推文（收集~3200推文）。
>
> 17.twint -u username --following --user-full - 收集一个人关注的完整用户信息
>
> 18.twint -u username --profile-full -> 使用缓慢但有效的方法从用户的个人资料中收集推文（收集~3200推文，包括转推）。
>
> 19.twint -u username --retweets - 使用快速方法从用户的个人资料中收集最近的900个推文（包括转推）。
>
> 20.twint -u username --resume resume_file.txt - 从上次保存的scroll-id开始恢复搜索。

有关命令和选项的更多详细信息位于[Wiki中](https://github.com/twintproject/twint/wiki/Commands)

##  模块示例

Twint可以用作模块并支持自定义格式。

    
    
    import twint
    # Configure
    c = twint.Config()
    c.Username = "noneprivacy"
    c.Search = "#osint"
    c.Format = "Tweet id: {id} | Tweet: {tweet}"
    # Run
    twint.run.Search(c)

输出

    
    
    955511208597184512 2018-01-22 18:43:19 GMT <now> pineapples are the best fruit
    import twint
    c = twint.Config()
    c.Username = "noneprivacy"
    c.Custom["tweet"] = ["id"]
    c.Custom["user"] = ["bio"]
    c.Limit = 10
    c.Store_csv = True
    c.Output = "none"
    twint.run.Search(c)

##  存储选项

> 1.写入文件;
>
> 2.CSV;
>
> 3.JSON;
>
> 4.SQLite;
>
> 5.Elasticsearch。

##  Elasticsearch设置

有关使用Twint设置Elasticsearch的详细信息位于[Wiki中](https://github.com/twintproject/twint/wiki/Elasticsearch)。

##  图形可视化

![](https://image.3001.net/images/20190827/1566877705_5d64a809e5a95.png!small)

[图表](https://github.com/twintproject/twint/wiki/Graph)详细信息也位于[wiki中](https://github.com/twintproject/twint/wiki/Graph)。

我们正在开发Twint桌面应用程序。

![](https://image.3001.net/images/20190827/1566877715_5d64a813e277a.png!small)

##  常问问题

我尝试从用户那里抓取推文，我知道它们存在，但我没有得到它们。

Twitter可以禁止影子账户，这意味着他们的推文不会通过搜索获得。要解决此问题，--profile-full请通过CLI使用Twint，如果使用Twint作为模块，则添加config.Profile_full = True。请注意，此过程将非常缓慢。

##  更多例子

仅获取关注者用户名/以下用户名

    
    
    twint -u username --followers
    twint -u username --following

获取关注者/关注用户的用户信息

    
    
    twint -u username --followers --user-full
    twint -u username --following --user-full

###  用户列表

仅获取用户的用户信息

    
    
    twint -u username --user-full

从用户列表中获取用户的用户信息

    
    
    twint --userlist inputlist --user-full

**参考来源：[GitHub](https://github.com/twintproject/twint)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

  

