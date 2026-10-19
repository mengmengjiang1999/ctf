# 0x00 前言

  * 没啥师傅带，自闭学web安全，上班摸鱼学学开发的知识，前期在B站根据黑马程序员的java学习路线刷完了基础篇：javaSE、servlet+jsp、spring、springmvc、springboot，尝试通关下webgoat和代码阅读来检验下学习成果

  * 关于webgoat前期安装部署步骤图就略过了。github下载，通过maven导入模块，idea会自动下载所需的jar包，然后运行主配置文件就能跑起来了。没什么需要配置的

  * 上一篇A1写完感觉学习下java web开发对代码阅读帮助挺大的，对于A2 Cryptographic Failures可写的内容不多，主要是一些编码知识，所以就跳过了

  * ![image.png](https://image.3001.net/images/20230506/1683361566_64560f1ed373cf7078a0e.png!small)

  * A3 注入，这都是老生常谈的内容，sql注入、xss、代码注入、命令注入，都是属于注入的范畴，一句话概括就是前端提交的数据包里带有恶意指令，本应该作为参数代入程序执行CRUD操作，却被服务器当成指令执行了

  * 关于java web的前置知识，请参考第一篇笔记

# 一、SQL注入

## 1、基本篇

  * 基本篇都是很简单的字符型、数值型注入和堆叠注入，简单过一下

  * ![image.png](https://image.3001.net/images/20230506/1683362232_645611b8d8733c5abb7a8.png!small)

  * 第2页，开胃小菜，给你一张表，让你输入sql语句获取bob的数据

  * ![image.png](https://image.3001.net/images/20230506/1683363512_645616b85c8fd8d2501d9.png!small)

  * 代码逻辑如下：

  * ![image.png](https://image.3001.net/images/20230506/1683363548_645616dc777b43a5b9510.png!small)

  * 第3页，也是考察sql语句编写，代码逻辑同上，就不水字数了，跳过

  * ![image.png](https://image.3001.net/images/20230506/1683363863_64561817b6488e4ad481f.png!small)

  * 第4页，同上

  * ![image.png](https://image.3001.net/images/20230506/1683364800_64561bc0c03c7f8ef0cdf.png!small)

  * 第5页，同理，跳过，第六七八页主要是讲解sql注入的基本原理和危害以及分布，直接来到第9页，字符型注入，考察基础的sql语句单引号的闭合，逃逸单引号执行指令

  * ![image.png](https://image.3001.net/images/20230506/1683365378_64561e02421edb25e0ea7.png!small)

  * ![image.png](https://image.3001.net/images/20230506/1683365677_64561f2d19ed458fbbf07.png!small)

  * 第10页，数值型注入

  * ![image.png](https://image.3001.net/images/20230506/1683365952_645620402de65541b3012.png!small)

  * 看了下前端的form表单action是跳转到5b这个类，不是10，你可以发现这个表单是两个输入项的，但是他页面也提示了，只有一个参数是可以注入的，看源代码的sql语句就知道第一个参数的值接收位置是用了?问号，也就是预编译的标示符，第二个就是直接拼接，所以注入点是第二个

  * ![image.png](https://image.3001.net/images/20230506/1683366091_645620cb197f3f121fdf0.png!small)

  * ![image.png](https://image.3001.net/images/20230506/1683366135_645620f75cecb59613d9d.png!small)

  * `另外提一嘴，第一篇讲过这个webgoat用的框架是ssj，jpa框架我没用过，但是看到这里可以知道jpa的预编译是用的问号来插值。而国内常用的是ssm，mybatis，用的是#井号和$美元号，其中美元号是可以注入的。对于ssm，一般sql语句要么以注解的形式写在dao或mapper包里的接口中，要么是以配置文件的形式写在resources下的mapper.xml中，如果使用的是mybatis-plus这个库，封装了sql语句成函数化了，就没那么好找了。`

  * 第11页，字符型注入，闭合一下然后留一个半闭合给他就OK了

  * ![image.png](https://image.3001.net/images/20230508/1683510906_6458567a282e2e41f2042.png!small)

  * 代码结构也是一个版式

  * ![image.png](https://image.3001.net/images/20230508/1683511044_64585704262f44d22b11e.png!small)

  * 第12页，考察堆叠注入

  * ![image.png](https://image.3001.net/images/20230508/1683513650_6458613228782bb10df2a.png!small)

  * 第13页，也是堆叠注入

  * ![image.png](https://image.3001.net/images/20230508/1683513794_645861c29b82f85556c66.png!small)

## 2、扩展篇

  * 主要是利用sql语句的一些高级功能进行注入，注释绕过，联合查询等等，关于这些内容可以看mysql必知必会这本书，内容不多

### 2.1 联合查询注入

![image.png](https://image.3001.net/images/20230508/1683516180_64586b14841eb8ffcfa02.png!small)

  * 来到第3页，获取dave的密码，一开始使用union 联合查询是不行的。

  * ![image.png](https://image.3001.net/images/20230508/1683517082_64586e9a76194856ad985.png!small)

  * 前面没细看，以为是过滤了union，其实是提示了union的前后表字段数不一致，不过尝试的注释绕过，试试注释一下union就可以了，这里就不太懂了，一般来说，使用联合查询，一种方式是让后面的表与前面的表字段数一致，一种是让前面的表失效不需要字段数一致，比如经常输入个负数就让前面的表查询失效只生效union后面的表，就只展示了后面的表字段

  * ![image.png](https://image.3001.net/images/20230508/1683517319_64586f87b2b151e2b20f6.png!small)

  * 然而我这里阴差阳错直接使用注释union且后面的表字段数与前面字段数相同，也能查出结果，并且结果只返回后面的表数据，这是否意味着注释的union可以让前面的表失效了？（功力不太行，知识盲区了）

  * 代码逻辑

  * ![image.png](https://image.3001.net/images/20230508/1683527838_6458989e8f37353200a36.png!small)

  * ![image.png](https://image.3001.net/images/20230508/1683527933_645898fd369d123d8beb4.png!small)

### 2.2 盲注

  * 有基于布尔值的盲注和基于时间的盲注

  * ![image.png](https://image.3001.net/images/20230508/1683534651_6458b33b9b86fbdb7b530.png!small)

  * 第5页，需要获得tom的密码以tom身份登录，看到提示说漏洞在注册的表单上

  * ![image.png](https://image.3001.net/images/20230508/1683538563_6458c2834a74ff9608dc5.png!small)

  * 此时想到可以尝试二次注入，也就是注册一个tom'，这样，当我们点击忘记密码修改tom'的密码时，执行的语句直接闭合，变成了修改tom的密码，然后发现这条路是不行的，因为修改密码这个功能是假的。。。。。。

  * ![image.png](https://image.3001.net/images/20230508/1683538710_6458c316d9ca598e22f4a.png!small)

  * 看来只能是通过注册表单来想办法猜出tom的密码了，正好第4页的说明就是介绍盲注，解题关键应该是这个，当使用substring判断password第一个值是否为a时，他直接将这串代码作为账号创建了

  * ![image.png](https://image.3001.net/images/20230509/1683596887_6459a657dc9cc3b28622a.png!small)

  * 当我们判断第一个值为t时，他就显示user已经存在。所以是可以盲注的，两次回显不一样。反过来说，一般注册功能都是将前端传入的用户名进行查询，检查用户名是否已经存在，每一次传入闭合的内容时都会当成指令进行substring的判断，当判断为false时，他就将整个指令作为用户名传入，如果substring结果为true，实际上传入的用户名就是tom了。就回显了用户已存在

  * ![image.png](https://image.3001.net/images/20230509/1683597158_6459a766b4ffe7d4d5a3e.png!small)

  * 于是就先判断密码的长度，得知不大于30且大于20

  * ![image.png](https://image.3001.net/images/20230509/1683597843_6459aa1308d1800c5faa4.png!small)

  * ![image.png](https://image.3001.net/images/20230509/1683597935_6459aa6fc0e756c46e172.png!small)

  * 最后得知是23位的密码

  * ![image.png](https://image.3001.net/images/20230509/1683598050_6459aae2e13ce569e70c4.png!small)

  * 然后发送到burp的枚举模块，枚举一位位的密码值，得知第一位是t

  * ![image.png](https://image.3001.net/images/20230509/1683598188_6459ab6cf3e390e692efd.png!small)

  * 第二位是h

  * ![image.png](https://image.3001.net/images/20230509/1683598695_6459ad67205f58ecd2c49.png!small)

  * ![image.png](https://image.3001.net/images/20230509/1683598923_6459ae4b90cd764fe0e25.png!small)

  * 以此类推，逐个一通枚举后得出密码是thisisasecretfortomonly，login成功，过关

  * ![image.png](https://image.3001.net/images/20230509/1683600615_6459b4e73a48b9472d5c3.png!small)

  * ![image.png](https://image.3001.net/images/20230509/1683600658_6459b51281d6f494e66eb.png!small)

  * 先看login表单，怪不得提示说只能在注册表单里过关，因为login表单做了预编译防护

  * ![image.png](https://image.3001.net/images/20230509/1683600780_6459b58c8e95477698d97.png!small)

  * 看回注册表单

  * ![image.png](https://image.3001.net/images/20230509/1683600966_6459b646d367e38418f9c.png!small)

  * ![image.png](https://image.3001.net/images/20230509/1683601046_6459b696ec9039adff1be.png!small)

  * 第6页是选择题，关于预编译的功能说明

  * ![image.png](https://image.3001.net/images/20230509/1683601351_6459b7c706f3e15e9b68d.png!small)

## 3、防御与绕过篇

  * 这里主要是讲解代码开发安全编写，这些东西就跟黑马的课上学的一模一样了

  * ![image.png](https://image.3001.net/images/20230509/1683602186_6459bb0aa416bb9def0a1.png!small)

  * ![image.png](https://image.3001.net/images/20230509/1683602769_6459bd5112b0895995384.png!small)

  * 第9页，第一次输入，提示不允许空格

  * ![image.png](https://image.3001.net/images/20230509/1683614800_6459ec509680284c8a2f1.png!small)

  * 那么可以使用注释绕过试试

  * ![image.png](https://image.3001.net/images/20230509/1683615245_6459ee0d9144c7fbafed0.png!small)

  * 他只是做了一下参数的空格过滤，然后调用了之前未使用预编译的章节漏洞代码

  * ![image.png](https://image.3001.net/images/20230509/1683615396_6459eea44145e4c7e2e24.png!small)

  * ![image.png](https://image.3001.net/images/20230509/1683615406_6459eeaef201d3954a18c.png!small)

  * 第10页，不允许空格和sql关键字

  * ![image.png](https://image.3001.net/images/20230509/1683615797_6459f03532459cec45f2b.png!small)

  * 使用双写关键字绕过

  * ![image.png](https://image.3001.net/images/20230509/1683615878_6459f0866d249bac59067.png!small)

  * 代码这里使用了touppercase先变成大写参数，然后再使用replace替换掉FROM和SELECT，使用混合的双写就能让他去除掉一个，留下一个关键字照样可以作为语句

  * ![image.png](https://image.3001.net/images/20230509/1683616000_6459f1004ca23494bec8c.png!small)

  * 第11页是一个很重要的知识点，就是预编译不是万能的sql注入防御手段，在使用order by的sql语句中是可以被注入的，因为它无法进行预编译参数化，预编译的占位符的值是会被加入引号的，而order by后一般是接字段名，字段名是不能带引号的，比如 order by username；如果带上引号成了order by ‘username’，那username就是一个字符串不是字段名了，这就产生了语法错误

  * ![image.png](https://image.3001.net/images/20230509/1683616546_6459f322a2c7a2cc93e7f.png!small)

  * 第12页，要求猜解webgoat-prd的IP地址

  * ![image.png](https://image.3001.net/images/20230509/1683617849_6459f8395d73f214a050e.png!small)

  * 通过repeater重放可以得到报错后的语句回显

  * ![image.png](https://image.3001.net/images/20230509/1683617946_6459f89a9cd48cc357c61.png!small)

  * 按照11页的提示使用case做判断来决定排序的字段，这里的意思是但hostname的值匹配相等就使用id作为order by的值即按照id排序，如果匹配不相等就按status

  * ![image.png](https://image.3001.net/images/20230509/1683618454_6459fa96d3ce20186aee7.png!small)

  * 测试一下不相等，确实是按status排序

  * ![image.png](https://image.3001.net/images/20230509/1683618582_6459fb16c2be9ffa61aaa.png!small)

  * 所以我们可以使用substring函数来猜解webgoat-pro的ip地址了，得出ip第一个值是1

  * ![image.png](https://image.3001.net/images/20230509/1683618826_6459fc0ab71f55132d926.png!small)

  * 同理最后得出是104，结合一开始给出的后三部分，就完成了

  * ![image.png](https://image.3001.net/images/20230509/1683618923_6459fc6bd8fe5aefa8704.png!small)

  * 先看展示代码，没有使用预编译的参数化

  * ![image.png](https://image.3001.net/images/20230509/1683620462_645a026e9e1b6d5d0ce44.png!small)

  * 提交答案框就使用了预编译参数化

  * ![image.png](https://image.3001.net/images/20230509/1683620499_645a02930d5d45149b88f.png!small)

# 二、路径遍历

![image.png](https://image.3001.net/images/20230509/1683620594_645a02f2c826282e1c9f8.png!small)

  * 第2页，先正常传个文件过去，显示了保存路径，

  * ![image.png](https://image.3001.net/images/20230509/1683623398_645a0de6d937310c4fee7.png!small)

  * 同时给了提示要篡改存放位置就是当前位置的上一级，所以需要修改一下数据包里的文件名，过关

  * ![image.png](https://image.3001.net/images/20230509/1683622513_645a0a710da3f0c79ac83.png!small)

  * 查看代码

  * ![image.png](https://image.3001.net/images/20230509/1683622817_645a0ba1009e6c846f88f.png!small)

  * 父类文件处理方法的逻辑

  * ![image.png](https://image.3001.net/images/20230509/1683623045_645a0c85ad6345b450636.png!small)

  * ![image.png](https://image.3001.net/images/20230509/1683623215_645a0d2f3b4fdbc0b3216.png!small)

  * 第3页，根据过滤了../，尝试绕过

  * ![image.png](https://image.3001.net/images/20230509/1683623444_645a0e14b29a543e830a0.png!small)

  * 试一下双写，是可以绕过的，过关

  * ![image.png](https://image.3001.net/images/20230509/1683623540_645a0e74ddbd0eff8b6fb.png!small)

  * ![image.png](https://image.3001.net/images/20230509/1683623600_645a0eb0554db3a8b667d.png!small)

  * 第4页，提示fullname字段被加固了

  * ![image.png](https://image.3001.net/images/20230509/1683624044_645a106cd170f8a3a3b2b.png!small)

  * 继续使用双写确实不行

  * ![image.png](https://image.3001.net/images/20230509/1683624073_645a108945685f956aacc.png!small)

  * 尝试在filename里试试，过关

  * ![image.png](https://image.3001.net/images/20230509/1683624109_645a10ad9b565b62b637e.png!small)

  * 代码逻辑，前面的关卡他收集的是fullname，而这里他使用了getOriginalFilename方法获取原始的文件名直接使用，也就是fullname失效的原因。但是这样反而filename那里就可以利用了，

  * ![image.png](https://image.3001.net/images/20230509/1683624228_645a1124a0fc14182782f.png!small)

  * 第5页，提示路径遍历还可以用于访问意料之外的文件

  * ![image.png](https://image.3001.net/images/20230509/1683624885_645a13b5801a494dd56dc.png!small)

  * 当点击随机图片按钮时，会触发JavaScript的事件函数

  * ![image.png](https://image.3001.net/images/20230509/1683625303_645a1557cd620811ea229.png!small)

  * 这个函数会发起一个get请求，路径是PathTraversal/random-picture，并将返回的值修改为图片的src属性值

  * ![image.png](https://image.3001.net/images/20230509/1683625348_645a158464c8656fed417.png!small)

  * 在响应包也可以看到location字段的值是指定了某张jpg

  * ![image.png](https://image.3001.net/images/20230509/1683625525_645a16359dd26d1dcd2f5.png!small)

  * 由于location是重定向功能，所以这里就是当我们没有指定参数时，他会随机重定向到一个url中，当我传入参数id=1.jpg时，返回的重定向值是1.jpg.jpg

  * ![image.png](https://image.3001.net/images/20230509/1683625852_645a177c74f196cdd5c1c.png!small)

  * 只传入id=2时，返回是2.jpg

  * ![image.png](https://image.3001.net/images/20230509/1683625885_645a179d93c42bc851af8.png!small)

  * 直接传入path-traversal-secret，是得不到这张过关图片的，返回了400

  * ![image.png](https://image.3001.net/images/20230509/1683625984_645a1800aa528f0db9a16.png!small)

  * 传入跳到上一级，返回了参数非法，不允许使用../

  * ![image.png](https://image.3001.net/images/20230509/1683626125_645a188d4bc8851bae072.png!small)

  * 将../进行url编码，最后试了两层找到了path-traversal-secret图片信息

  * ![image.png](https://image.3001.net/images/20230510/1683685703_645b01479c5266f79d8d0.png!small)

  * 过关条件是将当前主机的用户名使用sha512加密作为答案

  * ![image.png](https://image.3001.net/images/20230510/1683685900_645b020c5a74d14ae9b59.png!small)

  * 代码逻辑

  * ![image.png](https://image.3001.net/images/20230510/1683687440_645b0810cde69642b0bcc.png!small)

  * ![image.png](https://image.3001.net/images/20230510/1683687495_645b0847ef5c4bc870e36.png!small)

  * ![image.png](https://image.3001.net/images/20230510/1683687897_645b09d945eb06e6c855b.png!small)

  * 第67页，主要是解压保存文件时的路径遍历漏洞，保存文件因为要指定路径，导致文件名带有遍历的话，就会存放到意料之外的位置

  * ![image.png](https://image.3001.net/images/20230510/1683686916_645b060473ad8c33157ac.png!small)

  * ![image.png](https://image.3001.net/images/20230510/1683686945_645b0621449c54ee0b450.png!small)

  * 这一关是存在一些错误的，且只适合在linux系统做，这里略过

  * ![image.png](https://image.3001.net/images/20230510/1683702195_645b41b31bbe245416719.png!small)

# 三、XSS

  * XSS也是老生常谈的漏洞了....

  * ![image.png](https://image.3001.net/images/20230510/1683708895_645b5bdf699f04af5ce0b.png!small)

  * 第2页，简单的在控制台输入alert(document.cookie);过关

  * ![image.png](https://image.3001.net/images/20230510/1683709253_645b5d458d9c58913b622.png!small)

  * 第3456页漏洞说明

  * ![image.png](https://image.3001.net/images/20230510/1683709277_645b5d5dcaeb8f5eb1213.png!small)

  * ![image.png](https://image.3001.net/images/20230510/1683709289_645b5d69ba2c1f6700bdb.png!small)

  * ![image.png](https://image.3001.net/images/20230510/1683709309_645b5d7d3fd41fb0ed83d.png!small)

  * ![image.png](https://image.3001.net/images/20230510/1683709321_645b5d8985a3553e957d8.png!small)

  * 第7页，反射型xss

  * ![image.png](https://image.3001.net/images/20230510/1683709483_645b5e2b921150ca1c276.png!small)

  * 提示有个字段参数存在漏洞，提交一次数据就可以看到信用卡号原封不动返回。直接简单的""即可(好吧这里freebuf过滤了xss语句....)

  * ![image.png](https://image.3001.net/images/20230510/1683709708_645b5f0c3a18051345621.png!small)

  * ![image.png](https://image.3001.net/images/20230510/1683709746_645b5f3283c04b6e8a4ac.png!small)

  * 代码逻辑

  * ![image.png](https://image.3001.net/images/20230510/1683710021_645b6045bd2b5c566f849.png!small)

  * 第10页dom xss，找出访问测试代码的路由

  * ![image.png](https://image.3001.net/images/20230510/1683710907_645b63bb84256e5f3a70b.png!small)

  * ![image.png](https://image.3001.net/images/20230510/1683710214_645b61060d4142e1fb7de.png!small)

  * 根据他的提示，在传过来的js文件中搜索route，找到了一个routes对象，按照他提供的模式填入test过关

  * ![image.png](https://image.3001.net/images/20230510/1683711185_645b64d1b61a50ca595d9.png!small)

  * 第11页，提醒使用上面得到的test路由来执行一个函数拿到一个随机值

  * ![image.png](https://image.3001.net/images/20230510/1683711230_645b64fea045ec75ec93e.png!small)

  * 直接放函数到url发现直接就返回了这个函数，

  * ![image.png](https://image.3001.net/images/20230510/1683711992_645b67f8268004ce276c5.png!small)

  * 也就是说可以直接传xss语句加入script标签包住并url编码再访问一次就拿到了值，过关

  * ![image.png](https://image.3001.net/images/20230510/1683712130_645b68820582a0df5817b.png!small)

  * ![image.png](https://image.3001.net/images/20230510/1683712178_645b68b2a9e8b3cc6b966.png!small)

  * 第12页就是一些知识选择题了，没有存储型xss的实验，略过

# 四、总结

  * 没啥总结的，又水完一篇....

