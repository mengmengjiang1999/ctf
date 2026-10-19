### 背景：

最近总是能听到同事说在GitHub上搜到某个敏感信息，然后利用该信息成功的检测并发现某个漏洞，最后提交到对应的SRC（安全应急响应中心）换点money。顿时心里那个羡慕啊，然后就心说自己也要学会使用GitHub这个宝藏。

### 开始：

众所周知，作为安全人员，学会使用google hack是最基本的一项技能。那么什么是google hack呢？google
hack其实就是一系列的命令语法，这些命令语法可以用来快速的搜索敏感网站，关键字等信息。比如使用:inurl:XXXX；intext:XXXX；等等。看到这里估计很多人会思考，那GitHub有没有相关的语法命令呢？其实在学习之前，我也不清楚是否存在，但是在研究以后，我发现原来GitHub也有属于自己的命令语法可以用来快速方便的搜索敏感信息。接下来就带大家一起学习一下相关的命令语法。

1.q+关键字

我们通常情况下在GitHub上搜索是这样的形式，例如在搜索处输入hundsun，可以成功的搜索出一些项目信息，如图1所示。观察一下可以看到这里的url是这样的：

[https://github.com/search?utf8=%E2%9C%93&q=aliyuncs&type=；q对应的正是要搜索的关键字。type指定搜索结果展示的类型，分为Repositories，Code，Commits，Issues，Marketplace，Topics，Wikis，Users。默认搜索结果是以项目名的形式展示，从图1中可以看到。如果需要其他模式可以自己选择](https://github.com/search?utf8=%E2%9C%93&q=aliyuncs&type=%EF%BC%9Bq%E5%AF%B9%E5%BA%94%E7%9A%84%E6%AD%A3%E6%98%AF%E8%A6%81%E6%90%9C%E7%B4%A2%E7%9A%84%E5%85%B3%E9%94%AE%E5%AD%97%E3%80%82type%E6%8C%87%E5%AE%9A%E6%90%9C%E7%B4%A2%E7%BB%93%E6%9E%9C%E5%B1%95%E7%A4%BA%E7%9A%84%E7%B1%BB%E5%9E%8B%EF%BC%8C%E5%88%86%E4%B8%BARepositories%EF%BC%8CCode%EF%BC%8CCommits%EF%BC%8CIssues%EF%BC%8CMarketplace%EF%BC%8CTopics%EF%BC%8CWikis%EF%BC%8CUsers%E3%80%82%E9%BB%98%E8%AE%A4%E6%90%9C%E7%B4%A2%E7%BB%93%E6%9E%9C%E6%98%AF%E4%BB%A5%E9%A1%B9%E7%9B%AE%E5%90%8D%E7%9A%84%E5%BD%A2%E5%BC%8F%E5%B1%95%E7%A4%BA%EF%BC%8C%E4%BB%8E%E5%9B%BE1%E4%B8%AD%E5%8F%AF%E4%BB%A5%E7%9C%8B%E5%88%B0%E3%80%82%E5%A6%82%E6%9E%9C%E9%9C%80%E8%A6%81%E5%85%B6%E4%BB%96%E6%A8%A1%E5%BC%8F%E5%8F%AF%E4%BB%A5%E8%87%AA%E5%B7%B1%E9%80%89%E6%8B%A9)。

![image.png](https://image.3001.net/images/20181221/1545371638_5c1c7ff681f76.png!small)

####  

#### `2.in:file,path`

上边是最常见的搜索方式，可是有时候我们希望在文件名和路径中搜索包含关键字信息，那么这时候该如何搜索呢？此时可以使用如下url链接：

[https://github.com/search?o=desc&p=1&q=aliyuncs+in:file,path&ref=searchresults&s=indexed&type=Code&utf8=%E2%9C%93](https://github.com/search?o=desc&p=1&q=aliyuncs+in:file,path&ref=searchresults&s=indexed&type=Code&utf8=%E2%9C%93)
。

![image.png](https://image.3001.net/images/20181221/1545371654_5c1c800693192.png!small)

#### 3.repo:项目名

有时候大家可能会遇到一种情况，需要在指定项目中搜索包含敏感信息的文件，那么这时候该如何进行搜索呢？此时，可以使用如下url：

![image.png](https://image.3001.net/images/20181221/1545371694_5c1c802e23d21.png!small)

#### 4.-repo:项目名

对应的使用如下链接可以搜索除了指定项目以外的包含敏感信息的文件：

[https://github.com/search?o=desc&p=1&q=hundsun](https://github.com/search?o=desc&p=1&q=hundsun)
in:file,path -repo:XXXXX &ref=searchresult s
&s=indexed&type=Code&utf8=%E2%9C%93。这里q参数多了-repo:xxxxx。这个用来指定排除哪些项目。

#### 5.搜索兴趣推荐项目

  

Github还提供了一种方式可以基于用户的搜索兴趣进行推荐，使用如下url：<https://github.com/explore>  

![image.png](https://image.3001.net/images/20181221/1545371708_5c1c803c4fe3c.png!small)

#### 6.stars:条件

在有些情况下，我们需要对搜索结果进行筛选，使用星数搜索进行搜索是一个较好的方式。使用该语法，程序会展示星数大于要求的项目。这样带来的好处是可以快速找到好的项目。这里面的条件可以是简单的>或者..。1..10表示搜索项目星数介于1到10之间的。

#### 7.高级搜索

高级搜索可以指定多个搜索选项，例如项目名，项目创建者，创建时间，星数等等。其链接如下：<https://github.com/search/advanced>  

![image.png](https://image.3001.net/images/20181221/1545371749_5c1c806569f58.png!small)

看到这里可能很多人还没意识到有什么用，其实这里面的作用是很大的。因为你完全可以根据个人的需求去开发一些独特的搜索脚本。比如开发一个搜索数据库信息的python程序。例如：在正常情况下，输入关键字:jdbc
3306可以快速搜索出很多包含数据库的信息，利用前边学到的知识，可以加上对搜索结果进行筛选提取出外网的可用的数据库信息。

最后说点搜索技巧一类的，Github是一个大的宝库，知道搜索语法还需要了解如何去搜。尤其是搜索关键字该如何去寻找。可以根据特征去搜索，比如：对于oracle的，可以搜索jdbc
1502，因为mysql默认端口是1502。对于其他的可以搜索1433，3389一类的端口。如图所示。除此之外还可以这样搜索:关键字 username
passwd、ftp等等。

![image.png](https://image.3001.net/images/20181221/1545371780_5c1c8084af948.png!small)

最后附带我在网上搜集了几个敏感信息收集工具，这里都列出来方便自己也方便他人。这些工具在文件末尾备注。这里对GitPrey重点说明一下，其是使用python开发的用于收集企业敏感信息的脚本工具。我下载以后尝试输入包含各种关键字的命令运行，但是返回的结果都为空。后来经过查看代码发现在进行信息提取的时候，有个正则匹配地方，匹配的标签出问题了。因此这个如果要使用是需要进行简单改造的，其他工具都可以拿来使用。当然，如果感兴趣的可以利用前边介绍的知识自己构建一个专属的敏感信息收集工具。  

GitPrey(<https://github.com/repoog/GitPrey>)、

Nuggest(<https://github.com/az0ne/Github_Nuggests>)

theHarvester(<https://github.com/laramies/theHarvester>)

GISL(<https://github.com/FeeiCN/GSIL>)

###  

