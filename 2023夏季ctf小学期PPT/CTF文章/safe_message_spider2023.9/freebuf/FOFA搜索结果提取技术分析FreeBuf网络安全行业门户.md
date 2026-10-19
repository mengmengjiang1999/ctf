**前言：脚本和文档都是老早就写好的，这周发现fofa新版出来了，就把旧版的薅羊毛完整脚本分享给大家。文章主要是介绍这种脚本的编写思路，给编程新手提供一个思路参考，比起
**requests+** re 我更推荐大家使用 requests+bs4 获取信息。**

> 脚本语言：python2.7

##  白嫖与付费

付费肯定有更好的服务，但是就是喜欢薅羊毛的快乐。能付费尽量付费吧，如果你付费了这个脚本使用起来更安逸。

##  非api原因

根据网站vip功能介绍，可以看到“注册用户”和“普通会员”使用api都是亏本买卖，如果想用api就开svip才最安逸

![](https://image.3001.net/images/20200528/1590631866_5ecf1dba2c6c5.png!small)

##  Fofa与BeautifulSoup

**Fofa** **的搜索语法**

返回头 header="200"

国家 country="CN"

页面内容 body="phpweb"

网页头 title="公司"

端口 port="443"

网站年份 after="2020-01-01"

**BeautifulSoup** **库**

注：一般搭建好网站不会轻易更改网页标签类型，所以使用标签提取比正则匹配能让脚本“活得更久”

定位网页标签

    
    
             soup.find(name="input", attrs={"id": "total_entries"})
    
    
             soup.find_all(name="div", attrs={"class": "list_mod"})

获取标签值

    
    
             yourdiv.attrs['value']

获取ul内的li值

![](https://image.3001.net/images/20200528/1590631894_5ecf1dd6d7460.png!small)

##  执行搜索操作

打开fofa官网<https://fofa.so/>，搜索热门关键字，可以看到url请求为

<https://fofa.so/result?qbase64=>xxx

![](https://image.3001.net/images/20200528/1590632134_5ecf1ec6e4db4.png!small)

其中qbase64的值就是搜索字符串“base64编码+url编码”的结果，这里需要注意中文问题，需要将中文先gbk解码，再用base64库编码（我本机是gbk编码，所以输入的中文也是gbk编码，如果你的机器是utf-8编码就改为utf-8，没测）

    
    
    code = key.decode()
     code = urllib.quote(base64.b64encode(code))

这里遇到个问题一直没整明白，上面那种方式可以成功，但是下面这种使用方式却失败了，如果有人知道原因请留言或私信给我。

    
    
    code = urllib.quote(base64.b64encode(key.decode('gbk')))

代码

![](https://image.3001.net/images/20200528/1590632164_5ecf1ee4090fd.png!small)

##  获取页面搜索结果

使用浏览器自带调试功能查看html框架，可以看到我们搜索结果都在“<div>”标签下，每一个“<divclass="list_mod">”标签是一条信息

![](https://image.3001.net/images/20200528/1590632182_5ecf1ef683149.png!small)一个list_mod标签包含一个目标的全部信息

![](https://image.3001.net/images/20200528/1590632195_5ecf1f0301b6f.png!small)代码，其中divs就是全部目标列表

![](https://image.3001.net/images/20200528/1590632205_5ecf1f0dd5fc4.png!small)

##  定位单条目标信息

选取单个目标的标签点开分析，可以看到标签有list_mod_t和list_mod_c两个子标签

![](https://image.3001.net/images/20200528/1590632221_5ecf1f1d08fa0.png!small)而元素a就是可以直接跳转的链接，从这里提取到目标的url或者IP

![](https://image.3001.net/images/20200528/1590632236_5ecf1f2c263ed.png!small)![](https://image.3001.net/images/20200528/1590632239_5ecf1f2ff35c2.png!small)而目标下面的介绍其实是一个ul列表，这部分信息也比较重要，所以我也提取了

![](https://image.3001.net/images/20200528/1590632255_5ecf1f3fcf1e0.png!small)![](https://image.3001.net/images/20200528/1590632260_5ecf1f4443787.png!small)

代码

![](https://image.3001.net/images/20200528/1590632286_5ecf1f5e6d781.png!small)其中列表信息没做详细分类提取，也没有把他写入到文件，内存里长这样

![](https://image.3001.net/images/20200528/1590632297_5ecf1f693f560.png!small)

##  关于URL存活状态

在单个目标的右边有他的响应码，我是根据这个来确定的存活，当然你也可以自己请求一下提取的URL来判断存活，如果只需要200的网站就在查询时使用header="200"；代码中获取的是右侧整个字符串，大家根据需要自行修改代码就行

![](https://image.3001.net/images/20200528/1590632359_5ecf1fa7efb98.png!small)代码![](https://image.3001.net/images/20200528/1590632380_5ecf1fbc9c3f5.png!small)

##  翻页问题

我们知道目标总数除以10后加1就是页数，所以要提取目标总数，依旧是根据网页标签定位提取数据

![](https://image.3001.net/images/20200528/1590632393_5ecf1fc994e23.png!small)代码如下

![](https://image.3001.net/images/20200528/1590632402_5ecf1fd272f33.png!small)

知道总页数怎么翻页呢？

通过api规则知道请求中的page参数决定当前页面（或者看网页【下一页】的链接），测试中发现有请求频率限制，做下防封延时就行

![](https://image.3001.net/images/20200528/1590632437_5ecf1ff5bbf1c.png!small)![](https://image.3001.net/images/20200528/1590632442_5ecf1ffa95367.png!small)代码如下

![](https://image.3001.net/images/20200528/1590632454_5ecf20067a1a6.png!small)

##  网站cookie

Fofa现在登陆需要进行验证了，无法直接用户名密码登陆，所以我使用的cookie验证身份。

![](https://image.3001.net/images/20200528/1590632467_5ecf2013494b3.png!small)

##  自定义数据输出

在按页获取函数中修改数据处理方式，解除注册会员限制

![](https://image.3001.net/images/20200528/1590632883_5ecf21b37e616.png!small)脚本中是将链接追加到指定txt文件中，其它信息只是获取了，并没有输出

![](https://image.3001.net/images/20200528/1590632827_5ecf217b71766.png!small)

##  脚本使用

使用命令参数输入关键字和cookie，会输出总数，提示每页有多少条存活，其他信息输出自行修改脚本

**注意titile** **、app** **等使用方法，如果网页搜索栏是这样的**

app="BEA-WebLogic-Server"

**那么命令行这样输入**

"app=\"BEA-WebLogic-Server\""

![](https://image.3001.net/images/20200528/1590632539_5ecf205bd237b.png!small)输出总数和网页搜索总数一致（没有带国家参数）

![](https://image.3001.net/images/20200528/1590632556_5ecf206ca41a5.png!small)Hreffile.txt内容

![](https://image.3001.net/images/20200528/1590632568_5ecf207842912.png!small)

##  完整代码

代码已上传 aHR0cHM6Ly9naXRodWIuY29tL21veXV3YS9mb2ZhLXNlYXJjaC1yZXN1bHQtcmVx

注册会员，通过城市枚举和搜索条件定义，能薅200~400条数据吧，足够大家学习完漏洞后做实践了，相关漏洞差不多能有1/15的存在比例。

其实有想过获取页面左侧的城市信息，但是太麻烦了就无脑枚举了，后续大家可以做做”url去重“和”自定义存活确认（有的url访问过去就是网站自定义404页面）“。

 ***本文作者：难再见，转载请注明来自FreeBuf.COM**

