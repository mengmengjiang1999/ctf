# 零、免喷符

SOC部门小菜鸟一枚，此乃自闭学安全的笔记记录，行文潦草，随性笔记。

# 一、快速使用

### 1.1 熟悉界面

书接上回，当我们部署完基本环境时，系统趋于稳定运行，正式使用splunk更多的是导入数据，字段解析，编写搜索规则这两件事。应用面板支持安装app，是基于某个厂商日志的知识对象，包括解析规则和仪表板数据模板等。

![1666950455728.jpg](https://image.3001.net/images/20221028/1666950461_635ba53dcb20ef1d0a3b3.jpg!small)

splunk最重要的应用就是这个搜索和报告应用了，提供了搜索，分析，数据集，报表，告警，仪表板功能

![1666950493504.jpg](https://image.3001.net/images/20221028/1666950497_635ba56178ebb0b799e16.jpg!small)

### 1.2 数据组织形式

Splunk 平台接受任意类型的数据。尤其是所有 IT 流和历史数据。数据来源可以是事件日志、Web
日志、实时应用程序日志、网络源、系统指标、变更监视、消息队列、归档文件等等。

转换数据为事件的过程称为编制索引。编制索引期间，将对传入数据进行处理，从而实现快速搜索和分析。处理的结果以事件的形式存储在索引中。

索引是数据的平面文件存储库，这些数据称为数据桶，一个桶代表一段时间的数据目录，每个桶里包含了被压缩存放的原始数据和索引文件，而索引文件里包含了一些元数据指向原始数据

### 1.3 导入splunk官方的demo数据

数据针对 Buttercup Games 在线商店。商店出售游戏和其他相关产品，例如 T 恤。本教程主要搜索 Apache Web
访问日志并将访问日志与供应商销售日志进行关联。

通过导航栏中的设置界面里的添加数据，进入数据添加引导界面，完成数据索引

默认索引是main，可以创建多个索引，往往索引字段(index=***)用于区分不同的分子公司或是不同的地域，对于单机实验而言，这里使用索引区分不同的日志项目，这里使用的索引是splunk_demo

![1666950611732.jpg](https://image.3001.net/images/20221028/1666950615_635ba5d74fc3ba353d2df.jpg!small)

设置好数据源类型、主机、索引名，这三个字段是每个数据集都具备的字段，从而区分不同的数据集以及解析方式，再检查配置没问题即可进行索引

![1666950637647.jpg](https://image.3001.net/images/20221028/1666950640_635ba5f065a9469c75ce2.jpg!small)

![1666950647322.jpg](https://image.3001.net/images/20221028/1666950649_635ba5f9305e762576fa7.jpg!small)

### 1.4 数据解读

当我们使用搜索功能时，可以看到有搜索历史，搜索时间范围，搜索模式（简单模式，智能模式，详细模式）对应数据字段细粒度和搜索速度之间的权衡，以及数据摘要

![1666950685159.jpg](https://image.3001.net/images/20221028/1666950686_635ba61ed05be0ba2abf4.jpg!small)

当我们刚接手splunk时，我们或许不太清楚这个平台有什么数据供我们搜索，可以点击数据摘要，可以看到数据概览，因为前面提到导入每个数据集进行索引都需要设置这三个字段。

host代表这些日志是哪个主机的日志，其中源(source)和源类型(sourcetype)是两个不同的字段，前者代表数据是从哪里来的，比如从TCP端口接收的，或是从文件上传来的，后者代表着使用什么规则来解析日志，比如源类型是pa_log，代表日志是PA防火墙的日志，messages代表的是linux的messages日志

![1666950715104.jpg](https://image.3001.net/images/20221028/1666950719_635ba63f0b2d3bc7122fe.jpg!small)

使用命令：source="tutorlialdata.zip"
index="splunk_demo"来搜索刚才导入的数据，可以看到左边字段导航栏中，默认的三个字段会展示在最上面的选定字段中，感兴趣的字段则是splunk解析数据得出来的字段

值得注意的是对于SPL语句而言，key是区分大小写的，value则忽略大小写，index和Index是不同的字段匹配

![1666950744575.jpg](https://image.3001.net/images/20221028/1666950746_635ba65a28979fc2949e4.jpg!small)

点击source进行透视，可以看到这个数据集zip包有8种数据，1个是销售数据日志，3个主机的http访问日志，4个主机的安全日志，而sourcetype则有3种，刚才导入数据的时候并没有指定sourcetype，这是splunk程序自身识别的效果

![1666950781829.jpg](https://image.3001.net/images/20221028/1666950785_635ba681aa1f47798db69.jpg!small)

# 2、简单搜索教程的数据

### 2.1 搜索商店网站访问错误的事件

指定索引，模糊搜索网站域名的所有事件，使用括号来限定错误事件，与或非的条件关键字需要大写,可以看到，搜索出来427个事件

`index=splunk_demo buttercupgames (error OR fail* OR severe)`

![1666950927274.jpg](https://image.3001.net/images/20221028/1666950933_635ba7154da017bb5e4cb.jpg!small)

从method字段看到这些错误的请求方法都是post，从uri_path可以看到url都跳转到了/cart/error.do，从referer字段就看到了错误跳转前的uri是什么，都是出现在购买页面。从msg字段则看到购买失败的原因

![1666950953134.jpg](https://image.3001.net/images/20221028/1666950956_635ba72c68327e5379a8e.jpg!small)

![1666950966018.jpg](https://image.3001.net/images/20221028/1666950970_635ba73a15d497b865801.jpg!small)

![1666950977978.jpg](https://image.3001.net/images/20221028/1666950981_635ba745382ecb93c6cb2.jpg!small)

![1666950986793.jpg](https://image.3001.net/images/20221028/1666950990_635ba74e5381e886d5038.jpg!small)

### 2.2 统计各个商品的销售情况

主要的统计命令:stats，搜索出源数据后，通过管道符传递给该指令,其实很类似sql 命令的order by，通过什么进行排序，而这里是count
by，通过什么进行汇总

`index=splunk_demo buttercupgames status=200 action=purchase |stats count by
categoryId`

![1666951043307.jpg](https://image.3001.net/images/20221028/1666951045_635ba785c73501b26e628.jpg!small)

或者直接将源数据通过管道符传递给top 命令，他会直接进行统计并排序，并显示百分比，如果是要统计源主机的情况，只需要top clientip即可

`index=splunk_demo buttercupgames status=200 action=purchase |top categoryId`

![1666951082114.jpg](https://image.3001.net/images/20221028/1666951086_635ba7ae16ba70abd2e26.jpg!small)

点击可视化还可以调整聚合数据的各种图表形态，比如柱状图，饼图等

![1666951106625.jpg](https://image.3001.net/images/20221028/1666951113_635ba7c9ee8d717c10dc9.jpg!small)

![1666951126120.jpg](https://image.3001.net/images/20221028/1666951128_635ba7d8a384732042889.jpg!small)

### 2.3 使用子搜索，查找出购买力最强的客户以及他购买的产品

分为两步，先找到源IP，然后通过IP搜索出所有事件对商品去重。  
使用[]大括号可以执行子查询，子查询中使用table命令是使子查询结果只保留ip字段作为新的条件进入主查询  
在最后统计，列出count字段，去重的商品数以及对应的产品ID，其他字段都是单值字段，所以只有1个row，而产品ID有多个，即多值字段，需要使用value命令将字段所有值合并到一个row中，而使用as就跟sql语句一样，字段重命名

    
    
    sourcetype=access_* status=200 action=purchase [search sourcetype=access_* status=200 action=purchase 
    | top limit=1 clientip 
    | table clientip] 
    | stats count AS "Total Purchased", distinct_count(productId) AS "Total Products",
    values(productId) AS "Product IDs" by clientip | rename clientip AS "VIP Customer"
    

![1666951205682.jpg](https://image.3001.net/images/20221028/1666951211_635ba82b2f9b487a47ac3.jpg!small)

### 2.4 字段解析

可以看到secure日志，点击下拉列表可以看到字段并没有正确解析,可以在事件操作里选择提取字段

![1666951243933.jpg](https://image.3001.net/images/20221028/1666951246_635ba84e1e4052a513733.jpg!small)

![1666951252603.jpg](https://image.3001.net/images/20221028/1666951254_635ba856cd45e6d6e725d.jpg!small)

有两种提取方法，一种是分隔符，类似excel分列的形式，有明显且统一的分割符号，一种则是正则表达式，适用于混乱格式，这里sshd登录日志看起来没有明显的分隔符，使用空格拆分也不对，就选择正则表达式

![1666951271610.jpg](https://image.3001.net/images/20221028/1666951274_635ba86ae26ceb769c316.jpg!small)

从原始日志中可以看到ssh登录日志有两种，一种是错误密码for不可用的user，一种是错误密码for存在的user，这里只是选取了来自不可用user的登录事件进行正则提取，不会写正则表达式不要紧，只需要用鼠标划取自己想要的数据，填入字段名即可提取数据，splunk会自动帮你写正则，超级简单

![1666951296430.jpg](https://image.3001.net/images/20221028/1666951298_635ba88299f55e911ee6a.jpg!small)

可以看到已经解析了对于不可用用户的信息和源ip,保存设置，于是这条正则表达式解析规则就保存到这些数据集自带的源类型secure-2中

![1666951578142.jpg](https://image.3001.net/images/20221028/1666951581_635ba99d3296887b95281.jpg!small)

![1666951588289.jpg](https://image.3001.net/images/20221028/1666951590_635ba9a664611f82c0c02.jpg!small)

再次搜索即可看到新解析的两个字段，日志列表也能看到

![1667185823932.jpg](https://image.3001.net/images/20221031/1667185826_635f3ca2f0a105fbfb1f5.jpg!small)

![1667185858492.jpg](https://image.3001.net/images/20221031/1667185861_635f3cc59d3d5bbf66d7e.jpg!small)

我们还要摘取针对错误密码for可用user的日志数据里的用户名和ip进行解析，同理，点击相关事件进行解析，要注意和前面的字段名相同，方便一次性搜索出来，同时保存的解析规则名字要修改一下，此时关于这些日志的ssh两条解析规则都存在了secure-2源类型中，以后再有ssh登录日志拿过来，我们完全可以在导入阶段将日志源类型指定为secure-2，就能直接解析了。

![1667185907443.jpg](https://image.3001.net/images/20221031/1667185909_635f3cf59e53ad2c9d22d.jpg!small)

![1667185918853.jpg](https://image.3001.net/images/20221031/1667185922_635f3d02270458055e63b.jpg!small)

![1667185930488.jpg](https://image.3001.net/images/20221031/1667185933_635f3d0d4c7b6e50a4bf2.jpg!small)

![1667185943308.jpg](https://image.3001.net/images/20221031/1667185945_635f3d199c5d1260f68cd.jpg!small)

搜索验证一下，刚才解析完不可用user时，排在第一的是administrator，现在解析完可用user并入字段，可以看到排在第1的是root

![1667185980153.jpg](https://image.3001.net/images/20221031/1667185983_635f3d3fe4917a5852e09.jpg!small)

### 2.5 ssh暴力破解数据统计

 **2.5.1 重新解析secure日志**

此段为个人暴论，首先我们对暴力破解的定义是什么，在一定时间内，使用不同的账户密码组合进行登录尝试，产生大量请求。

但我们经常会看到这么一种暴力破解的误报，就是有台主机不停地登录尝试，比如mysql的登录爆破，但他实际上不是暴力破解，只是mysql改密码了，而应用程序没有改，一直用旧密码不断发起请求，他确实产生了大量请求，然而他是只用了旧密码，就一个密码

所以可以看到真实的暴力破解是，短时间内大量请求，不同的账号密码组合

而对于成功登录的事件，不管多少次，我们都要关注。所以我们其实还要解析一个字段，就是登录结果，如果一个IP使用了多种账号密码组合，并且还有的事件是成功的，那么他绝对是暴力破解且成功了。为此我们还要拆解一个action字段，代表事件结果，这是重新规划解析规则的结果

![1667186067769.jpg](https://image.3001.net/images/20221031/1667186072_635f3d983e86196975a5e.jpg!small)

可以看到action是有3种，对于已经提取的字段是放在设置里的字段提取项目里

![1667186095907.jpg](https://image.3001.net/images/20221031/1667186098_635f3db253e587c815ca5.jpg!small)

![1667186107108.jpg](https://image.3001.net/images/20221031/1667186109_635f3dbd3c1650e1ef027.jpg!small)

 **2.5.2 找出暴力破解的top 5 IP**

搜索逻辑是查找出登录失败次数最多的IP，可以看到第一个IP 87.194.216.51，共948次事件，使用了大量的账号

`index=splunk_demo sourcetype="secure-2" action!=Accepted |stats
values(account) count by clientip`

![1667186245855.jpg](https://image.3001.net/images/20221031/1667186248_635f3e4875a3f7d0973f2.jpg!small)

取消展示账号字段，更直白看到top 5，对于暴力破解的IP，自然是放到防火墙黑名单算完事，毕竟运营嘛，就是IP添加机器人:)

![1667186270503.jpg](https://image.3001.net/images/20221031/1667186272_635f3e6081d7311c8aa11.jpg!small)

 **2.5.3找出存在破解行为且有成功结果的IP**

搜索逻辑是查找同时存在两种登录结果且使用不同密码组合的IP，这里看到有两种登录结果的都是内部IP，并且都是使用的单一账号，并且不是root，很自然的认为他们只是平时偶尔输错密码罢了

`index=splunk_demo sourcetype="secure-2" |stats values(action) as
action,values(account) as account count by clientip`

此时排序就是不是选择count，而是选择action，重点是将"A"ccepted排在最前面，可以看到未有外部多组合尝试的IP有暴力破解成功

![1667186341142.jpg](https://image.3001.net/images/20221031/1667186345_635f3ea9bc302c4d81742.jpg!small)

### 2.6 使用工作流动作联动微步查询IP

前面处理了销售日志和secure日志，还差一个http的访问日志。说实话对于这种http日志，我们没法像ips一样来写一堆规则来匹配安全事件，因为splunk
三大组件中，enterprise、ueba、soar，只有ueba运用机器学习来处理这些"网络流"日志，对于平常使用的enterprise主要是处理syslog风格的日志

这里以某个IP发起了大量4**状态码的事件来模拟一下目录扫描事件，因为目录扫描用字典匹配肯定有很多网站压根不存在的目录及文件

 **2.6.1 根据上述逻辑查找出扫描IP**

搜索语句使用status模糊匹配，并且将uri_path多值字段合并到一个栏位

`index=splunk_demo sourcetype="access_combined_wcookie" status=4* | stats
values(uri_path) count by clientip`

可以看到最前面的IP，87.194.216.51，前面ssh爆破事件第一个就是这个龟孙.

![1667186568892.jpg](https://image.3001.net/images/20221031/1667186574_635f3f8e01e5e89b64b9e.jpg!small)

 **2.6.2 关于工作流动作**

在日常运营过程中我们经常用到微步来确认IP信息，特别是看告警报文拿捏不准的时候，此时就要复制这个IP放到微步，毕竟运营嘛。既然是IP添加机器人:)，就要避免误杀，还要充当微步查询机器人:)

使用工作流可以为某个字段添加一个额外的跳转功能，这里跳转到微步

![1667186603195.jpg](https://image.3001.net/images/20221031/1667186607_635f3faf746a50e52734c.jpg!small)

搜索这个top 1 IP 87.194.216.51的事件，然后在某个事件里点击事件操作就能看到有一个新的工作流功能

![1667186623341.jpg](https://image.3001.net/images/20221031/1667186626_635f3fc2e80a924d656d7.jpg!small)

直接点击这个按钮就跳转到相关URL，oh！实现半自动查微步自由，全自动就需要soar了:)

![1667186668111.jpg](https://image.3001.net/images/20221031/1667186671_635f3fefe7282c7d2a411.jpg!small)

# 3、 简单告警

### 3.1 关于告警的暴论

对于利用安全日志来写告警，依然是遵循以下几个思路。

告警的丰富程度取决于安全日志的丰富程度，比如一台路由器的日志你也指望不了SOC能写出个啥告警

还是得看菜下饭，客户一般都是将waf、UTM、IPS的日志发过来，可以针对安全产品的不同模块编写不同的安全日志，特别是UTM，比如他有防病毒模块、web攻击检测模块、垃圾邮件模块、C2检测等，都要为他写几条，但直接把安全日志有1条出1条那真是纯憨憨。

流量的流向无非就这几个方向，外对内，内对内，内对外。流量的结果无非就成功和不成功。

由此我们就可以编写以下的规则，外部IP对内部IP的攻击事件，结果为失败的次数达到多少次后，就产生告警。对于外部IP对内部IP的攻击事件，只要是成功的，次数大于0次就产生告警

内对内和内对外的，基本同理

### 3.2 编写外部攻击失败的且但IP次数多的ssh告警

关于外对内的，即外部IP访问过来的，我们需要关注攻击事件次数较多的，以及攻击成功的事件，这就是两条告警，以SSH为例，这里使用使用了子网范围的方式排除了这些内部IP

`index=splunk_demo sourcetype="secure-2" clientip!=127.* clientip!=10.*
clientip!=172.16.0.0/12 clientip!=192.168.0.0/16 |stats count by clientip`

可以看到右上角有一个另存为，可以另存为报表、告警或是仪表板

![1667186816381.jpg](https://image.3001.net/images/20221031/1667186820_635f40846502063e01d3e.jpg!small)

将其存为告警，命名为来自外部的ssh暴力破解，权限那里可以设置为仅自己使用或是共享该告警给其他用户

![1667186835020.jpg](https://image.3001.net/images/20221031/1667186838_635f409675abba4d99ddb.jpg!small)

对于告警类型，详情如下，更多的是使用计划搜索，定期去搜索某个时间范围的日志来出告警，系统预设了几个计划周期，但也可以使用linux crontab的方式（分
时 日 月 周几）来设置

![1667186860252.jpg](https://image.3001.net/images/20221031/1667186863_635f40afcf60712e732ad.jpg!small)

我这里设置的是每15分钟搜索一次结果，搜索的日志时间范围是最近15分钟(*/15 * *
*＊)，就刚好能查到新日志（其实可能会漏掉一些，因为新日志可能到来的没那么快，有点时间差），过期时间为1天，即告警记录有效期

触发条件有很多，更倾向于自定义，因为可以对之前的搜索语句再次筛选，比如这里筛选的是大于100次的，或者一开始就在搜索语句加入这个过滤语句，并将触发告警条件改为按结果数>0，也是同样道理

对于触发选项，我们的搜索语句可能会出现多条记录，是按每条一个告警还是一次性展示整个结果列表记录，一般都是一次性

![1667186932330.jpg](https://image.3001.net/images/20221031/1667186937_635f40f92e163c2c26fc2.jpg!small)

限制选项，因为告警可能会很多，我们可以通过限制来限制他的触发周期，但是对于外部爆破事件，我们还是要实时关注，最多把上面的计划任务执行周期调整得大一些，比如1个小时搜索一次，搜索范围是最近1小时，告警次数也微调。这里就不限制了

触发动作，即告警动作选项，一般用到的是log
event，即记录这个告警到其他的索引，一般soc开一个告警存放的索引，方便统一后期查找，也可以避免过期。也会用到发送电子邮件，和定义告警的等级

![1667186958018.jpg](https://image.3001.net/images/20221031/1667186962_635f411299c4d7083d415.jpg!small)

![1667186972702.jpg](https://image.3001.net/images/20221031/1667186975_635f411ff013b477203f4.jpg!small)

关于告警记录，需要设置记录哪些字段和一般日志一样设置索引等其他字段

![1667186993513.jpg](https://image.3001.net/images/20221031/1667186996_635f41347fe2da9d33fd1.jpg!small)

发送邮件这里就填写收件人和邮件内容和格式，当然前期还需要设置发件人，这是在系统设置里设置的

![1667187016447.jpg](https://image.3001.net/images/20221031/1667187018_635f414a4c6ec1906da27.jpg!small)

![1667187027381.jpg](https://image.3001.net/images/20221031/1667187029_635f41555f5e842d38f33.jpg!small)

最后添加一个告警等级，为中风险，至此，一条检测外部IP的ssh暴力破解的告警就搞定了。

![1667187047703.jpg](https://image.3001.net/images/20221031/1667187049_635f4169c2d6d751624c6.jpg!small)

前面搜索结果存为告警后发现忘了加结果不等于成功的条件，可以在设置页面对告警进行修改

![1667187069913.jpg](https://image.3001.net/images/20221031/1667187072_635f4180d2a36d84d47ae.jpg!small)

![1667187081125.jpg](https://image.3001.net/images/20221031/1667187083_635f418b559e4deebaf0f.jpg!small)

或者验证告警，点击旁边的运行，直接跳转到新页面来搜索该语句，可以看到最近15分钟没有相关事件，但有时担心是不是写错了语句，可以改下时间查一查有没有出现想要的结果

![1667188107278.jpg](https://image.3001.net/images/20221031/1667188111_635f458fd633c9f8c2ae8.jpg!small)

![1667188117585.jpg](https://image.3001.net/images/20221031/1667188120_635f4598bbb014a43274c.jpg!small)

### 3.3 编写外部ssh攻击成功的事件

同理，将action=accept就行,在前面我们知道确实没有外部IP攻击成功，所以没事件

`index=splunk_demo sourcetype="secure-2" clientip!=127.* clientip!=10.*
clientip!=172.16.0.0/12 clientip!=192.168.0.0/16 action=Accept |stats count by
clientip`

![1667188186076.jpg](https://image.3001.net/images/20221031/1667188188_635f45dcb7fce61b47c35.jpg!small)

依然另存为告警，重点是次数大于0，因为accept的事件，只要是成功的都值得注意？哎呀那这样会不会有其他专用的外部IP连进来的，那就开个白名单嘛，加个条件clientip≠x.x.x.x，完美解决

![1667188207133.jpg](https://image.3001.net/images/20221031/1667188208_635f45f0d27e1b7667779.jpg!small)

对于告警动作，我们调整严重性为严重

![1667188225055.jpg](https://image.3001.net/images/20221031/1667188228_635f46044aeb27d68e110.jpg!small)

邮件发送优先级调为高

![1667188243638.jpg](https://image.3001.net/images/20221031/1667188245_635f4615d43bdbee1c656.jpg!small)

此时有两条告警了

![1667188261723.jpg](https://image.3001.net/images/20221031/1667188263_635f4627c7436149012f8.jpg!small)

# 4\. 简单仪表板

这个很简单，仪表板用于展示到大屏上。给领导看个乐子，或是作为月报周报输出给客户还是够看的

### 4.1 ssh暴力破解的TOP10 外部IP

搜索下结果表格

`index=splunk_demo sourcetype="secure-2" clientip!=127.* clientip!=10.*
clientip!=172.16.0.0/12 clientip!=192.168.0.0/16 |top limit=10 clientip`

![1667188333594.jpg](https://image.3001.net/images/20221031/1667188335_635f466f94fd1fff1997a.jpg!small)

另存为仪表板，设置下仪表板标题，权限，这个搜索语句结果的面板标题，使用经典仪表板。经典仪表板构造方便，但是相对简约，dashboard studio就很高端

![1667188358549.jpg](https://image.3001.net/images/20221031/1667188361_635f46894a4df08640643.jpg!small)

展示结果，经典仪表板调色和各种参数还是能玩的花里胡哨的，得花些心思调整数据展示类型，标签，等等

![1667188387562.jpg](https://image.3001.net/images/20221031/1667188389_635f46a571c7d260708d3.jpg!small)

![1667188397523.jpg](https://image.3001.net/images/20221031/1667188399_635f46af2e94629c0de45.jpg!small)

  

