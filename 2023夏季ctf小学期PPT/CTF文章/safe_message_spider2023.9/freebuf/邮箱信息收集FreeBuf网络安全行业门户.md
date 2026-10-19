寻找目标开放的邮服端口和web邮箱入口

 ** **通过扫描c段找到入口****

  * 拿到目标后，先要先从MX记录域名找到他的真实ip地址（某些目标可能是第三方邮件服务器，这种情况mx记录就没有参考价值了）

![](https://image.3001.net/images/20220630/1656576827_62bd5b3bdb4372c083acc.png!small)

* 然后针对这个ip地址的c段进行扫描（25、109、110、143、465、995、993端口）

 ** **通过子域名的方式找到邮件入口****

Subdomainbrute、ksubdomain、Oneforall、Sublist3r、TeeMO、LangSrcCurise、Layer挖掘机等。

\通过搜索引擎爬取

Google hack 搜索：

site:target.com intitle:”Outlook Web App”

site:target.com intitle:”mail”

site:target.com
intitle:”webmail”![](https://image.3001.net/images/20220630/1656576849_62bd5b51246b96ddce69c.png!small)

同时也可以使用zoomeye搜索等。

<https://www.zoomeye.org/>

![](https://image.3001.net/images/20220630/1656576873_62bd5b6922423160016de.png!small)

\批量收集目标邮箱

  * [https://phonebook.cz/（还可以收集域名、URL）](https://phonebook.cz/%EF%BC%88%E8%BF%98%E5%8F%AF%E4%BB%A5%E6%94%B6%E9%9B%86%E5%9F%9F%E5%90%8D%E3%80%81URL%EF%BC%89)

![](https://image.3001.net/images/20220630/1656576907_62bd5b8b83bd113090e69.png!small)

  * <https://hunter.io/>

![](https://image.3001.net/images/20220630/1656576931_62bd5ba3b2b239f2a1030.png!small)

  * <http://www.skymem.info/>

![](https://image.3001.net/images/20220630/1656576948_62bd5bb473801e2b89680.png!small)

  * <https://www.email-format.com/i/search/>
  * <https://github.com/bit4woo/teemo>
  * <https://github.com/laramies/theHarvester>

\验证邮箱

在收集邮箱之后，我们可以对邮箱进行验证，是否存在目标邮箱被弃用的情况（离职，职位调动等）。

通过mailtester.com可以查询邮箱地址是否存在

https://mailtester.com/testmail.php

\verifyemail这款工具可批量验证邮箱

https://github.com/Tzeross/verifyemail![](https://image.3001.net/images/20220630/1656576991_62bd5bdfc6d9af5c88c6c.png!small)

 ** **\****[ ** **mailtester.py****](http://mailtester.py)

https://github.com/angusluk/MailTester

这款工具可以自动组合邮箱地址再根据组合的结果逐个验证。

脚本的好处在于,它会根据 First / Last Name 中的名字随意拼装组合,然后再对其进行逐个验证。

当我们在对邮箱用户进行枚举的时候，尽量多找一些字典，如中国人姓名拼音、字母缩写top100，1000，10000，此处我们需要更多的鱼叉，多一个邮箱就多一份成功率。

当然可以把搜集到疑似网络管理员、运维人员、安全部门的人员提取出来，这些人单独写邮箱或者不发，因为这些人安全意识相对较高，容易打草惊蛇，我们需要对一些非技术员工安全意识薄弱的人下手，挑软柿子捏。

这里可以配合这个网址 https://www.aies.cn/pinyin.htm 根据收集到的目标信息制定对应人名字典进行组合。

 ** **\****邮箱爆破

这种方式的弱口令爆破只适用于目标企业自己的邮件服务器如owa等 像百度腾讯阿里网易的邮箱不优先考虑。

用到的工具medusa、hydra、SNETCracker、APT34组织 owa爆破工具等。

另外邮箱用户名与密码往往还会使用公司简称+2019，2020等社工口令，多一个字典就多一份成功率。

全部展開回到頂部移至底部

