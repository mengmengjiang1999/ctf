burpsuite是一款功能强大的用于攻击web应用程序的集成平台，通常在服务器和客户端之间充当一个双向代理，用于截获通信过程中的数据包，对于截获到的包可以人为的进行修改和重放。
此BurpSuite实战主要包括两个实验：分别是使用burp进行暴力破解和Burpsuite简介及MIME上传绕过实例。
链接：<https://sourl.cn/RCXTic>  

实验一：使用burp进行暴力破解

## 一、实验简介

实验所属系列：web安全 实验对象：本科/专科信息安全专业 相关课程及专业：网络安全，计算机网络 实验类别：实践实验类

## 二、预备知识

1.Burp的工作模式：在没有burp之前，客户端使用浏览器直接与服务器进行通信。有了burp之后，burp在客户端与服务器之间充当代理。这样，浏览器发送给服务器的请求就会被burp进行捕获，而burp和wireshark这种审计类工具相比，其强大之处在于不仅可以做审计工作，更可以对数据包进行修改并发送出去。使用了burp的结构如下图所示。![](https://image.3001.net/images/20201022/1603336609_5f90f9a1b763b5ef68719.png!small)

2.暴力破解：一般使用暴力破解都有两种原因：

  * 对这个漏洞的测试，人是可以完成的，即可穷举。

  * 人可以完成，但是代价太大，或者太浪费时间。

正是出于这样的问题，一些软件的出现帮助人完成了这些测试，这就是暴力破解的真正好处。在业界曾经有这样的一种看法，对于暴力破解的使用都不屑一顾，因为大家觉得技术含量太低。但是，从实际的情况来看，因为用户使用弱口令情况太普遍，导致很多漏洞使用暴力破解都可以轻松拿下。
暴力破解，最有价值的地方是在对字典的构造上，这是一门技术，需要长期的经验积累。

## 三、实验目的

通过该实验掌握burp的配置方法和相关模块的使用方法，对一个虚拟网站使用burp进行暴力破解来使网站建设者从攻击者的角度去分析和避免问题，以此加强网站安全。在此郑重声明，本教程只做教学目的，严禁使用本教程对线上网站进行破坏攻击。

## 四、实验环境

![](https://image.3001.net/images/20201022/1603336619_5f90f9abb0dedefda2c81.png!small)

服务器：windows xp sp3 ip地址：10.1.1.163 测试者：windows xp sp3 ip地址随机

## 五、实验步骤

步骤一：

Burp是个非常强大的web分析工具。burp在浏览器和服务器之间充当了一个双向代理。这样，就可以把用户或者服务器通信过程中产生的数据包给截获下来，让专业人员去分析。（关于Burpsuite的部分简介可以参考实验二）
本次实验，需要完成的任务如下：

  * 配置burp和浏览器代理，使burp能够正常运行；

  * 学会使用burp中的compare模块；

  * 学会使用burp中的repeat模块；

  * 学会使用burp中的intruder模块。

此实验由合天网安实验室平台提供了一个存在暴力破解隐患的网站。
配置burp和设置ie代理：在预备知识中我们了解到，burp在浏览器(客户端)是以代理的方式存在。因此，如果想要我们发送的包被burp截断，就需要双方协商好一个监听端口。
首先，双击打开桌面的burp进入主界面。 1.设置burp监听端口：选择proxy(代理)，进入之后选择options。我们看到在Proxy
listeners处burp为我们默认添加了一个本地8080端口处的监听项。当然，你也可以自拟一个新的监听端口，在左侧点击ADD即可设置。![](https://image.3001.net/images/20201022/1603336632_5f90f9b84600912959d49.png!small)

2.配置浏览器的代理项：这里以系统自带的ie为例（chrome和firefox用户可以使用代理插件进行设置）
使用win+R键打开命令窗口，输入inetcpl.cpl进入ie设置。
在连接选项卡中，选择局域网设置：![](https://image.3001.net/images/20201022/1603336641_5f90f9c17c646312726a5.png!small)

输入我们为burp指定的监听端口号：
![](https://image.3001.net/images/20201022/1603336653_5f90f9cd909f513873f80.png!small)

这时候，我们就建立了基本配置。 3.测试：在burp中打开intercept is
on：![](https://image.3001.net/images/20201022/1603336662_5f90f9d69f399b3dbd555.png!small)

用浏览器访问：10.1.1.163/crack,我们会在burp中看到：![](https://image.3001.net/images/20201022/1603336671_5f90f9dfa8f66095cabcb.png!small)

这表明我们已经成功的截获了来自浏览器的请求。
点击forward就可以把这个请求发送给服务器，服务器会将结果返回给浏览器中，并将响应在burp中记录下来。Drop会将这个包丢掉，即不会发送到服务器端。

步骤二：

熟悉comparer，repeater，intruder模块。1.compare模块：compare模块可以将不同的数据包(无论是请求包还是响应包)进行比较。
首先，我们添加一条请求到compare模块去。 在已经截取的数据包上面右键，选择send to comparer：
![](https://image.3001.net/images/20201022/1603336682_5f90f9ea28f46869a25ab.png!small)

这时候，我们会看到在comparer模块，上下两个界面中同时多出来了一条记录：
![](https://image.3001.net/images/20201022/1603336940_5f90faec074ba370b265f.png!small)

使用同样的方法，我们在为comparer模块添加另外的一条记录：
![](https://image.3001.net/images/20201022/1603336949_5f90faf5f30c35db394da.png!small)

我们打算使用1和2进行对比，在两个视图中选择1和2（顺序无所谓），然后点击右下角的compare
word（bytes是指文件按照字节流来进行比对）：![](https://image.3001.net/images/20201022/1603336961_5f90fb01dbf0e62b05c9c.png!small)

从图中我们可以看到，窗口标题提示了我们两个文件有多少处不同。左下角的图例告诉了我们右侧和左侧相比，哪些是添加的，哪些是修改的，哪些是删除的。非常直观。
2.repeater模块：有时候我们需要向服务器发送多次相同的请求来测试服务器的响应。这里，我们只需要将burp截取到的请求通过右键send to
repeater就可以在repeater中进行操作了。![](https://image.3001.net/images/20201022/1603336973_5f90fb0defc2a2f8aa6b4.png!small)

进入到repeater之后，点击go按钮，右侧就会返回服务器的响应。 Go的次数没有限制，点击多少次go，burp就会把当前的请求页向服务器发送多少次。
使用repeater的目的是进行重放攻击测试，看服务器是否会对重放测试做出反应。![](https://image.3001.net/images/20201022/1603336985_5f90fb19c227adc3d26ae.png!small)

3.intruder模块：这个模块是burp非常强势的地方，也正是我们课中说到的暴力破解主要使用的模块。
（1）同样的，在已经截获的请求页上右键，选择send to intruder。
进入intruder模块。会看到四个选项卡，分别是Target，Positions，Payloads，Options。
Target主要是设置暴力破解访问的host地址和对应的端口号：![](https://image.3001.net/images/20201022/1603336994_5f90fb22e2d3ea31207e4.png!small)

Positions设置是选择我们要暴力破解的位置。在默认情况下，burp会自动将所有的变量都勾选上。实际操作中，我们往往是针对单一点，选择“clear$”，此时所有默认的爆破点都已经消失。
（2）用鼠标选中需要暴力破解的变量的值。然后右侧选择“add$”，这样我们就添加了一个爆破点，这个爆破点的payload位置是在两个“$”之间的部分。![](https://image.3001.net/images/20201022/1603337014_5f90fb36e92b79e6276dd.png!small)

Payloads设置：选择怎样的字典或者payload，是这个模块要做的事情。Payload type下拉列表框为我们提供了常用的payload
类型，视情况选择即可。![](https://image.3001.net/images/20201022/1603337025_5f90fb41548135d6a547c.png!small)

如果你有合适的字典，在选择了payload type为simple list后，接下来你就可以在payload
options中选择你要加载的字典文件，点击load即可。![](https://image.3001.net/images/20201022/1603337125_5f90fba5831699a66f02f.png!small)

有时候我们需对payload进行二次处理，比如md5加密啊，base64加密啊之类的，burp当然也考虑到了这一点。在payload
processing中集成了一些常见的算法。 点击add，在弹出的窗口中就可以根据需要选择了。
![](https://image.3001.net/images/20201022/1603337137_5f90fbb1cd215fd674823.png!small)

Options中有关于其他细节的设置，比如攻击时使用的线程数，关于攻击的一些存储设置之类。这里就不再赘述。

步骤三：

下面尝试对密码的爆破：已知用户名为hetian，密码为50-100之间的某个数。
1.访问http://10.1.1.163/crack/，这是一个登录界面：![](https://image.3001.net/images/20201022/1603337148_5f90fbbcd8b7811e51ab9.png!small)

2.使用hetian登录，密码任意。完成表单后提交。这时候burp会截取我们的请求：
![](https://image.3001.net/images/20201022/1603337161_5f90fbc918c625d11543e.png!small)

3.在该请求页上右键选择send to
repeater，我们来进行重放测试。点击go，右侧返回服务器的响应。多次go之后发现，服务器返回的长度和内容都没有发生变化，都会提示sorry：![](https://image.3001.net/images/20201022/1603337174_5f90fbd6b37589e1b3bfd.png!small)![](https://image.3001.net/images/20201022/1603337188_5f90fbe480d7ccd81a5c1.png!small)

也就是说，服务器对多次测试并没有加以限制，因此我们可以使用暴力破解了。
为了再次验证，我们在登陆界面再次输入一个不同的密码。在我们将两次请求的响应使用comparer去比对一下。（在proxy中选择子选项卡HTTP
History，选择方法为post的两个历史记录，点击每一条post记录，下方会看到不同的post数据时，这应该就是我们的两次不同密码的请求记录，右键选择send
to
comparer(response)）：![](https://image.3001.net/images/20201022/1603339166_5f91039e5ee2d19296aee.png!small)![](https://image.3001.net/images/20201022/1603339185_5f9103b17497cf1d7974c.png!small)

从图中我们可以发现，经过对两次不同的请求返回结果进行对比，burp为我们在左上角标出了2项不同，但都是体现在时间上，其余都相同。所以可以使用暴力破解。
4.进入到intruder之后，先点击Clear$，然后选中我们刚才填写的pas字段值，点击Add$。这样，就确定了爆破点是pas位置。
![](https://image.3001.net/images/20201022/1603339202_5f9103c2d2f0fcc5c7eb3.png!small)![](https://image.3001.net/images/20201022/1603339221_5f9103d5a93a3f9bfda79.png!small)

5.打开payload选项卡，payload
type选择数字：![](https://image.3001.net/images/20201022/1603339235_5f9103e38ffbdb31cfbcf.png!small)

6.选择数字之后，我们填写数字范围。因为是已经暗示了密码范围，所以我们选择50到100.顺序生成，每步加1(step设置)：![](https://image.3001.net/images/20201022/1603339255_5f9103f7338758a06f194.png!small)

7.开始攻击：![](https://image.3001.net/images/20201022/1603339332_5f910444a8a20db3bedac.png!small)

8.这时候我们看到了攻击测试界面。我们重点关注payload和length，这里的length表示的是服务器的响应长度。
从理论上来分析，登陆成功和登陆失败，返回的长度应该不同，这能方便我们找出正确密码。右下角的进度条显示了我们的进度。
9.一段时间过后，测试结束。在length上双击，可以对length排序。![](https://image.3001.net/images/20201022/1603339347_5f910453c43afe9b9631d.png!small)

我们发现，在测试的50个payload中，payload为69的返回值不同与其他payload返回值。我们怀疑69就是答案。我们来观察一下。
在payload为69的request上双击，进入后选择response。浏览response，直到发现：“you got
it.![](https://image.3001.net/images/20201022/1603339362_5f9104627836413c9ed85.png!small)

![](https://image.3001.net/images/20201022/1603339376_5f910470e984b57fe9714.png!small)

Yes，you catch the flag!成功获取密码。

## 六、答题

![](https://image.3001.net/images/20201022/1603339398_5f910486d92ef66fe2893.png!small)注：请在特定的环境下进行实验（如虚拟机）。切记不要对他人的网站进行实验，如造成不利影响或产生违法行为，一切后果自负。

实验二：Burpsuite简介及MIME上传绕过实例

一、实验简介

实验所属系列：web安全 实验对象：本科/专科信息安全专业 相关课程及专业：信息网络安全概论 实验时数（学分）：2学时 实验类别：实践实验类

二、预备知识

1.了解burpsuite：Burp
Suite是用于攻击web应用程序的集成平台。包含了许多工具，并为这些工具设计了许多接口，以促进加快攻击应用程序的过程。所有的工具都共享一个能处理并显示HTTP消息，持久性，认证，代理，日志，警报的可扩展的框架。
在一个工具处理HTTP请求和响应时，它可以选择调用其他任意的 Burp
工具。例如，代理记录的请求可被Intruder用来构造一个自定义的自动攻击的准则，也可被 Repeater 用来手动攻击，也可被 Scanner
用来分析漏洞，或者被 Spider(网络爬虫)用来自动搜索内容。 Burpsuite主要有如下模块/功能：

  * Target，显示目标站点目录结构

  * Proxy，是一个拦截HTTP/S的代理服务器，作为一个在浏览器和目标应用程序之间的中间人，允许你拦截，查看，修改在两个方向上的原始数据流。

  * Spider，是一个应用智能感应的网络爬虫，它能完整的枚举应用程序的内容和功能。

  * Scanner，是一个高级工具，执行后，它能自动地发现web 应用程序的安全漏洞。

  * Intruder，是一个定制的高度可配置的工具，对web应用程序进行自动化攻击，如：枚举标识符，收集有用的数据，以及使用fuzzing 技术探测常规漏洞。

  * Repeater，是一个靠手动操作来触发单独的HTTP 请求，并分析应用程序响应的工具。

  * Sequencer，是一个用来分析那些不可预知的应用程序会话令牌和重要数据项的随机性的工具。

  * Decoder，是一个进行手动执行或对应用程序数据者智能解码编码的工具。

  * Comparer，通常是通过一些相关的请求和响应得到两项数据的一个可视化的“差异”。

  * Extender，可以让你加载Burp Suite的扩展，使用你自己的或第三方代码来扩展Burp Suit的功能。

  * Options，对Burp Suite的一些设置。

2.了解服务端MIME类型检测：服务端MIME检测类型图片上传过程中http包的Content-Type是否为image/jpeg，如果是就可以成功上传。相关源代码：

  

可以看到红色区域中的if语句只对Content-Type和图片的大小做了判断。

三、实验目的

通过本实验了解利用Burpsuite绕过MIME上传检测的过程。

四、实验环境

![](https://image.3001.net/images/20201022/1603339465_5f9104c93eca6225790f3.png!small)

服务器：win2003，IP地址：10.1.1.59:81 测试者：win7，IP地址随机

五、实验步骤

步骤一：

1.使用Burpsuite的代理功能：访问http://10.1.1.59:81，输入用户名：admin，密码：password，打开burpsuite，设置好浏览器代理，点击sql
injection：
![](https://image.3001.net/images/20201022/1603339595_5f91054b71b6c658bc799.png!small)

截获的数据包如下：![](https://image.3001.net/images/20201022/1603339609_5f910559b604242c158c2.png!small)

单击右键，如下图所示：![](https://image.3001.net/images/20201022/1603339621_5f910565b66d75d69ebea.png!small)

Send to XXX分别表示将截获的数据发送到各个模块，然后在各模块下进行下一步操作。 下拉菜单，点击Send to
Spider切换到Spider模块下，burpsuite会自动对网站进行爬行，切换到Control选项卡下可以查看爬行的状态和设置爬行范围，Options选项卡中可以进行爬行的设置等。一段时间后切换到Target模块查看结果：![](https://image.3001.net/images/20201022/1603339635_5f910573b52adf8ae60c6.png!small)

Change request method表示更改请求方式，如之前使用的GET请求，点击Change request method后为变为POST：
![](https://image.3001.net/images/20201022/1603339648_5f910580af1edc94183df.png!small)![](https://image.3001.net/images/20201022/1603339663_5f91058f9dea4385a4c39.png!small)

Don’t intercept requests表示不截获请求，比如我们选择To this host，在Intercept is
on时burp也不对此主机的请求做拦截。我们就可以正常访问该网页了。![](https://image.3001.net/images/20201022/1603339679_5f91059fcb5e8c22f54d4.png!small)

然后切换到Proxy的Options选项卡下，查看Intercept Client
Requests，已增一条记录：![](https://image.3001.net/images/20201022/1603339693_5f9105ad88c35281a29cb.png!small)

Do intercept下Response to this request功能可用于对服务端发送过来的信息做修改来欺骗浏览器。 如果开启URL-encode
as you type表示对你输入的&，=等字符将会被URL编码替换。 2.Target模块：这个模块下有两个选项卡，Site
map主要是将爬行的站点以树形结构显示，Scope主要是用来设置范围进行过滤。 有时当我们对一个目标网址进行测试时，Site
map下会出现许多不相关的网址，我们可以使用Filter来过滤，只留下目标网址：![](https://image.3001.net/images/20201022/1603339707_5f9105bb2f34d042fd524.png!small)

点击Filter，勾选Show only in-scope
items：![](https://image.3001.net/images/20201022/1603339722_5f9105cac9f8a4ef97794.png!small)

此时Site
map下只剩下目标网址了：![](https://image.3001.net/images/20201022/1603339740_5f9105dc629c5d8c66399.png!small)

然后我们随便点击一个目录又会出现许多功能：![](https://image.3001.net/images/20201022/1603339751_5f9105e7c632d4cc2a97e.png!small)

点击Remove from
scope，比如我此时选择css，该目录就会消失，对应的Scope选项卡下便会多出一条记录：![](https://image.3001.net/images/20201022/1603339767_5f9105f71af5899b2b1fa.png!small)

点击Spider this branch，burp就会对该目录进行爬行。 点击Expand
branch来展开分支，其他功能不是很常用，有兴趣可以自行研究哦。 Site
map选项卡右边可以看到一些请求的信息，在Host下可以选择对链接进行高亮显示，comment下可以添加注释，针对单个链接也可进行右键操作。

![](https://image.3001.net/images/20201022/1603339782_5f910606ec6d167f9f62e.png!small)

步骤二：

使用burpsuite上传绕过服务端MIME类型检测：1.首先在桌面上新建一个1.txt，此处我写入“hello_world”。因为目标主机只允许我们上传jpg文件，那么我们下载就要绕过这个限制，上传一个txt文件上去：
![](https://image.3001.net/images/20201022/1603339799_5f9106170b20d6ec069b8.png!small)

2.打开http://10.1.1.59:81，输入用户名：admin
密码：password，点击Upload：![](https://image.3001.net/images/20201022/1603339811_5f910623d6b9fd9310c58.png!small)

3.设置好浏览器代理后，我们选择刚才创建的txt文件进行上传。此时burpsuite已经截获到了数据包，我们右击选择“send to
reprater”：![](https://image.3001.net/images/20201022/1603339824_5f9106305fea65145c0ed.png!small)

4.切换到Repeater中将Content-Type后的text/plain修改为image/jpeg：![](https://image.3001.net/images/20201022/1603339836_5f91063ccc022a286848b.png!small)

5.点击go，从右侧可看到已经上传成功，在右下方输入1.txt进行搜索刚才上传的图片：![](https://image.3001.net/images/20201022/1603339849_5f910649975828a9c05e2.png!small)

6.关闭代理，打开搜索到的路径：![](https://image.3001.net/images/20201022/1603339864_5f910658499f36bbea80e.png!small)

六、答题

![](https://image.3001.net/images/20201022/1603339885_5f91066da2ab8341271c7.png!small)

注：请在特定的环境下进行实验（如虚拟机）。切记不要对他人的网站进行实验，如造成不利影响或产生违法行为，一切后果自负。

  

