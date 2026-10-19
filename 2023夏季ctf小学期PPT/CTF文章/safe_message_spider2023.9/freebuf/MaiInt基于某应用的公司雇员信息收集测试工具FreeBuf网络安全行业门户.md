**![MaiInt：基于脉脉应用的中国公司雇员信息收集工具](https://image.3001.net/images/20180719/15319880503241.jpg!small)**

**严正声明：本文仅限于技术探讨，严禁用于其他用途。**

 **本文将介绍一款由埃森哲安全实验室Vincent
Yiu开发的，针对中国[某职场社交应用](http://maimai.cn/)的开源信息自动化收集测试工具-MaiInt（[Github下载](https://github.com/vysec/MaiInt)）。MaiInt
能基于这款应用平台，执行公开资源情报（OSINT）操作，收集该应用注册用户信息，进一步分类，可实现对中国各大公司在该应用平台注册雇员姓名和可能的电子邮箱收集，最终收集结果会以HTML和CSV报告格式呈现。作者在本文讲述了自己开发MaiInt的一些相关过程和延伸利用。**

看不到？点[这里](https://v.qq.com/x/page/b0731tps43p.html)

## 开发MaiInt的起因

目前，针对中国职场社交平台，好像还没有一款好用的公司雇员信息收集工具，而在美英等国，安全研究人员或恶意攻击者可以围绕LinkedIn来进行一些公司雇员收集，且类似的OSINT工具有很多，像[LinkedInt](https://github.com/DisK0nn3cT/linkedin-gatherer)就是其中之一。LinkedInt早期只是开发者小范围的内部使用，直到2017年才正式开源下载。利用LinkedInt可以指定公司名称和公司域名后缀，来收集特定公司的雇员姓名和邮箱信息，这种类似工具可以方便攻击者对某些公司雇员发起有针对性的钓鱼欺骗、撞库和密码暴力破解等恶意攻击。

在2017年12月举办的京东安全大会上，由于各种原因，我发现很难找到中国公司员工的准确信息。虽然
LinkedIn在中国没被禁用，但貌似又不是主流的社交应用。在和朋友
[3gstudent](https://twitter.com/3gstudent?lang=en)
的交流中，他告诉我，在中国，有一款职场社交应用可能比LinkedIn更为活跃。

## 着手开发MaiInt

基于以上难于发现中国公司员工准确信息的问题，由此我开发了MaiInt。开发过程中有几个地方需要克服，特别是由于我不了解中国汉字的URL转码问题，其它的问题在下文略有介绍，也藉此可以启发有兴趣的研究人员对其它OSINT工具的开发。

### 从了解该应用的 iOS APP 开始

我从iPhone应用商店中下载了这款应用的 iOS
APP，之后，我就用我自己的手机号码进行了账号注册。在这款APP中，手机号可以代替用户名，因此，在开发MaiInt之初，需要用到你个人的手机号和该应用的登录验证密码。之后，完成相关注册登录，就能进行特定组织机构的雇员信息收集了。

接下来，就是在Burp中观察网络流量行为了。这一步，需要进行一些设置更改，首先，需要更改iPhone上的无线设置，把手动代理修改为HTTP方式。而且需要确保接入的无线网络没有主机隔离限制，之后，就是设置好你的代理IP，并确保手机防火墙处于关闭状态，能让手机连接到你的代理上去。

通过网络流量抓包分析，可以看到该应用的API接口和各种可用的HTTP方法，我发现利用GET、POST、Cookie参数方式可以很方便地就创建出一个简单的GET请求，并能收到JSON数据格式的响应。

以下为一个执行search请求的示例：

    
    
    GET /search/contacts?query=%E9%A5%BF%E4%BA%86%E4%B9%88&dist=3&searchTokens=%5B%22%E9%A5%BF%E4%BA%86%E4%B9%88%22%5D&me=1&highlight=true&frm=webview%23%2Fsearch%2Fcontacts&appid=4&vc=11.2.1&push_permit=1&version=4.18.8&channel=AppStore&net=wifi&jsononly=1&imei=<censor IMEI>&open=icon&density=2&u=<censor user ID>&device=iPhone10%2C4&access_token=<censor access token>&ts=<censor ts>HTTP/1.1
    Host: maimai.cn
    Accept: */*
    Cookie: access_token=<censor access token>; channel=AppStore; u=<censor user ID>; version=4.18.8; session=<censor session cookie>; session.sig=<censor session signature>
    User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobile/15C153/{iPhone10,4} [iOS 11.2.1]/MaiMai 4.18.8(4.18.8.9)
    Accept-Language: en-GB;q=1, zh-Hant-GB;q=0.9, zh-Hans-GB;q=0.8
    Accept-Encoding: gzip, deflate
    Connection: close

在以上请求中可以发现，多个区域字段都值得深入研究。在身份验证部分的验证请求过程中，所需的就是一个认证访问token和用户ID，这点的更多部分以下还会更多涉及。

另外有意思的部分就是query 和 searchTokens 参数，我使用了在线工具<https://www.url-encode-decode.com/>
对其中涉及的数值作了转码。其中，query参数值%E9%A5%BF%E4%BA%86%E4%B9%88转码后的信息为我要收集的公司 ‘饿了么’：

![MaiInt：基于脉脉应用的中国公司雇员信息收集工具](https://image.3001.net/images/20180719/15319861542903.png!small)而searchToken参数值
%5B%22%E9%A5%BF%E4%BA%86%E4%B9%88%22%5D 转码后则为
[“饿了么”]，比上一个query参数值多了一对括号和引号：![MaiInt：基于脉脉应用的中国公司雇员信息收集工具](https://image.3001.net/images/20180719/15319861736847.png!small)最后请求的输出数据为JSON格式，你可以指定需要收集的记录数量，但是不能超过25,000条，否则就会出现崩溃不响应。

### 自动验证

为了获取有效的访问认证token，我们需要执行身份验证步骤，并从响应消息中获取访问认证token。因此，我退出应用并再次登录进入，并用Burp对该过程进行网络流量抓包。和搜索功能类似，这个应用的登录功能一样可用GET、POST和Cookie参数方式来交互运行，所以也很容易在URL链接中添加各部分所需的请求参数。不尽如人意的是，我没有通过web代理来运行该过程，其中涉及到了一些<https://maimai.cn>的TLS连接，而且登录账号也仅只是为了测试MaiInt之用。

以下为POST请求网络包内容：

    
    
    POST /maimai/user/v3/login?account=<censored account phone number>&appid=4&vc=11.2.1&push_permit=1&version=4.18.8&channel=AppStore&net=wifi&imei=<censored IMEI>&open=icon&density=2&u=&device=iPhone10%2C4&access_token= HTTP/1.1
    Host: open.taou.com
    Content-Type: application/x-www-form-urlencoded
    Connection: close
    Accept: */*
    User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobile/15C153/{iPhone10,4} [iOS 11.2.1]/MaiMai 4.18.8(4.18.8.9)
    Accept-Language: en-GB;q=1, zh-Hant-GB;q=0.9, zh-Hans-GB;q=0.8
    Accept-Encoding: gzip, deflate
    Content-Length: 128
    account=<censored URL encoded phone number>&appid=4&cnt=1&dev_type=4&dname=<censored device name>&new_fr=1&password=<censored password>&stage=complete_uinfo

以上POST包可以通过移动变换URL链接中的参数来变形成为类似以下的GET请求：

    
    
    GET /maimai/user/v3/login?account=<censored&account=<censored+URL+encoded+phone+number>&appid=4&cnt=1&dev_type=4&dname=<censored+device+name>&new_fr=1&password=<censored+password>&stage=complete_uinfo account
    Host: open.taou.com
    Connection: close
    Accept: */*
    User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobile/15C153/{iPhone10,4} [iOS 11.2.1]/MaiMai 4.18.8(4.18.8.9)
    Accept-Language: en-GB;q=1, zh-Hant-GB;q=0.9, zh-Hans-GB;q=0.8
    Accept-Encoding: gzip, deflate

以上请求发出后，得到的响应内容如下：

    
    
    HTTP/1.1 200 OK
    Server: nginx
    Date: Mon, 01 Jan 2018 09:38:33 GMT
    Content-Type: application/json; charset="utf-8"
    Connection: close
    Vary: Accept-Encoding
    Content-Length: 4223
    {"has_weibo": 0, "token": "<censored token>", "has_password": 1, "user": {"meeting_partake_count": 0,
    <...snip for brevity...>
    "education": [], "id": <censored ID>, "ht_city": null, "job_count": 0, "cshow_url": "[http](https://maimai.cn/show?webuid=TsJ6oBCd&srcu=TsJ6oBCd&profession=0&src=app&ampregfr=cshow&abtype=0&turl=http%3A//taou.cn/d/7lnZp)
    <...snip for brevity...>

在上述响应内容中，我们得到了用来作身份验证的token和用户账号ID，还可用这些信息来作search搜索请求。

### 把中文转码为URL编码

以下在Stack
Overflow论坛中给出的发贴展示了如何插入中文字符，并以%格式输出URL编码字符。大家可以点[此](https://stackoverflow.com/questions/38600436/how-to-url-encode-chinese-characters)看看。

### 在Windows系统中设置中文输入

现在，有了把中文字符转化为URL编码的方法，唯一剩下的问题就是需要在Windows系统中设置中文输入。找了找我发现只要设置系统语言环境即可，从控制面板 -区域 - 管理 - 更改系统区域设置，选择中文（简体，中国）。

![MaiInt：基于脉脉应用的中国公司雇员信息收集工具](https://image.3001.net/images/20180719/15319864616120.png!small)![MaiInt：基于脉脉应用的中国公司雇员信息收集工具](https://image.3001.net/images/20180719/15319864748985.png!small)设置之后重启系统，就可以在输入框中添加进入拼音的中文键盘输入。

### 中文姓名 VS 电子邮箱格式

在西方， 英文姓名有first name、middle name 和 last name， last name
也就是我们说的姓氏，通常是英文姓名中的最后一个字段。但是，中文姓名与英文姓名相反，姓氏都是姓名中的第一个字。因此，从英文姓名到电子邮件格式的转换相对简单，但是，从中文姓名到电子邮件格式的转换却是反过来的，有所不同。

例如，英文姓名到邮箱的格式转化是这样的：

> Jane Doe -> jane.doe@company.com

但中文却是这样的：

> 王雪娇 -> wang xue jiao -> xuejiao.wang@company.com / wangxuejiao@company.com

我们需要把中文转化为拼音字符然后再把它组合为邮箱格式，但是，由于中文同音字的原因，很难准确把真实的中文姓名转化为拼音字符，例如，在 ni
的拼音输入法中，存在好多同音字：你,尼,泥,妮,拟,倪,腻,逆,昵,昵......，输入法中的 ni 的第1个选项代表“你”，第2个选项代表
“尼”，以此类推。但好在JSON输出中存在一个貌似是拼音的py属性。

### 加入邮箱发现神器 Hunter 功能

至此，我们熟悉了中文语法相关的姓名和邮箱结构格式，可以用邮箱发现神器 Hunter
来尝试看看大致的一些中文姓名邮箱。Hunter官网[Hunter.io](https://hunter.io/)就能搜索出一些相关结果，它可以通过公司网站域名来匹配互联网上公开的邮箱，最后会把匹配搜索邮箱分类为通用格式。另外，Hunter还具备邮箱有效性验证、批量导入域名获取邮箱、批量查询以及Chrome浏览器插件等实用功能，非常方便邮箱发现识别。以下为Hunter.io对饿了么公司（
ele.me）的邮箱识别：

![MaiInt：基于脉脉应用的中国公司雇员信息收集工具](https://image.3001.net/images/20180719/15319866665381.png!small)Hunter.io对邮箱识别的首要模式是first.last姓在前名在后，但也有一些名在前姓在后（last.first）的识别发现，如其中的一个可能发现为，姓名拼音结构为ZhuPengfei，邮箱格式为Pengfei
Zhu@ele.me。Hunter确实很牛，像LinkedInt中也加入了其识别功能，在我开发的MaiInt中，如果使用者不喜欢Hunter的首要识别模式，我会给出其它选择模式。  

## MaiInt Github 项目  

MaiInt 项目地址为 <https://github.com/vysec/MaiInt>
，运行后的显示界面为：![MaiInt：基于脉脉应用的中国公司雇员信息收集工具](https://image.3001.net/images/20180719/15319872123719.png!small)以下为HTML和CSV的报告结果实例：
![MaiInt：基于脉脉应用的中国公司雇员信息收集工具](https://image.3001.net/images/20180719/15319872618298.png!small)![MaiInt：基于脉脉应用的中国公司雇员信息收集工具](https://image.3001.net/images/20180719/15319872728691.png!small)

## 延伸利用-密码喷洒-自动化密码验证

密码喷洒（Password
spraying），某种程度上也可叫暴力破解登录，它是通过入侵某个资产设备实现对组织机构进行渗透的常见方式之一。与外国不同，在中国，Microsoft
Outlook 和
Exchange不是常用的在线邮箱应用，受众率较高的是腾讯QQ旗下的Exmail企业邮箱服务，各大公司通过该购买该邮箱服务配置成为自身企业服务。

有了以上MaiInt的数据收集应用，综合暴力破解登录就有点意思了。通过分析我发现，腾讯的Exmail企业邮箱服务在登录界面没有部署有即时的多因子身份认证机制（MFA），所以，我首先想到的就是用Burpsuite来抓包分析。之后我发现在登录请求消息中并未包含有密码信息，但却在p参数处存在一个
base64 十六进制编码的二进制大对象（blob)。

我查看了Exmail登录界面的源码，在提交处发现了以下的JavaScript验证格式信息：

    
    
    <form name="form1" method="post" action="/cgi-bin/login" onsubmit="return checkInput();">

这里，我们可以看到，方法checkInput()被调用，后来我在登录界面的源码中发现了checkInput()方法的具体源码：

    
    
    function checkInput() {
        window.org_pass = S("pp").value;
        if (!window.RSAKey) {
            document.getElementById("downError").style.display = "block";
            document.getElementById("returnMsg").style.display = "none";
            return false;
        }
        if (!checkCookie()) {
            return false;
        }
    var inputUin = document.form1.qquin.value.toLowerCase();
        if (inputUin == "") {
            showMsg("emptyUserName");
            document.form1.qquin.focus();
            return false;
        }
    var re = /^\d+$/;
    if (inputUin.indexOf("[@qq](http://twitter.com/qq).com") > 0 || inputUin.indexOf("[@vip](http://twitter.com/vip).qq.com") > 0 || inputUin.indexOf("[@foxmail](http://twitter.com/foxmail).com") > 0) {
            showMsg("errorLoginWithQQAccount");
            return false;
        } else if (inputUin.indexOf("@") > -1) {
            showMsg("errorUserName");
            return false;
        } else {
            document.form1.uin.value = document.form1.qquin.value + "[@mogujie](http://twitter.com/mogujie).com";
        }
        if (document.form1.pp.value == "") {
            showMsg("emptyPassword");
            document.form1.pp.focus();
            return false;
        }
    if (document.form1.pp.value.length >= 100) {
            showMsg("errorPassowrdTooLong");
            document.form1.pp.focus();
            return false;
        }
    if (S("VerifyArea").style.display != "none") {
            if (document.form1.verifycode.value == "验证码") {
                document.form1.verifycode.value = "";
            }
            if (document.form1.verifycode.value == "") {
                showMsg("emptyVerifyCode");
                document.form1.verifycode.focus();
                return false;
            }
        } else {
            document.form1.verifycode.value = "";
        }
    var PublicKey = "CF87D7B4C864F4842F1D337491A48FFF54B73A17300E8E42FA365420393AC0346AE55D8AFAD975DFA175FAF0106CBA81AF1DDE4ACEC284DAC6ED9A0D8FEB1CC070733C58213EFFED46529C54CEA06D774E3CC7E073346AEBD6C66FC973F299EB74738E400B22B1E7CDC54E71AED059D228DFEB5B29C530FF341502AE56DDCFE9";
        var RSA = new RSAKey();
        RSA.setPublic(PublicKey, "10001");
        var PublicTs = "<censored random ts value>";
    var Res = RSA.encrypt(document.form1.pp.value + '\n' + document.form1.ts.value + '\n');
        if (Res) {
            if (document.form1.chg.value == 1) {
                document.form1.p.value = hex2b64(Res);
            } else {
                if (document.form1.ppp.value != "") {
                    document.form1.p.value = document.form1.ppp.value;
                } else {
                    document.form1.p.value = hex2b64(Res);
                }
            }
        }
        var MaskValue = "";
        for (var Loop = 0; Loop < document.form1.pp.value.length; Loop++, MaskValue += "0");
        document.form1.pp.value = MaskValue;
    setCookieAlias(document.form1.uin.value, document.form1.domain.value);
    return true;
    }

以上脚本用S("pp").valu获取 pp
的值，并执行其它各种检查以确保存在RSA密钥和相应的用户cookie，之后对邮箱地址进行校验确保其为有效的Exmail企业账户，而且也会对登录密码长度作出验证，不能超过100个字符。

当所有校验验证完成之后，脚本会调用密码信息并附加上随机生成的PublicTs值，然后利用RSA公钥加密密码，并把加密内容转化成一个base64编码的二进制大对象（blob)，该blod会在之后的
p 参数请求中用到。当该应用的服务器收到这个编码的blob值，会在服务端执行解码和验证操作。

这种加密机制是为了防止恶意攻击者抓包分析流量从而还原出用户密码，是一种很好的用户信息保护机制。也就是说，如果Burpsuite的Intruder模块中存在RSA加密密码，且不创建新插件时，我是看不到实际密码的。为此，我在和朋友
**@evi1cg**
交流过程中，他向我推荐了一篇[《腾讯企业邮箱登陆爆破》](http://www.cnnetarmy.com/%E8%85%BE%E8%AE%AF%E4%BC%81%E4%B8%9A%E9%82%AE%E7%AE%B1%E7%99%BB%E9%99%86%E7%88%86%E7%A0%B4/)的文章。

从该文中可以看到，中国国内安全研究者早在2017年2月，就已经编写好了一个可以暴力破解登录腾讯企业邮箱Exmail的Python脚本。但是，由于中文和英文环境下密码复杂度和弱口令构成的不同，在我的密码破解登录测试中，并不算有效成功。但需要注意的是，很多大公司都对用户密码构成具备了一些不错的要求，在中国国内，数字如生日手机号等个人相关的密码用的较多，所以在我的利用中，这种密码猜解比通常的密码猜解要难一些。

## 结语

感谢阅读，希望大家都能有所收获。我们可以看到，虽然各个地区的技术类似，但不同领域采取的方式不一样，可能造成使用的工具和所获得的开源信息都会有所不同。基于互联网行业在中国的快速发展，中国国内有着更多自己的应用生态系统，而像俄罗斯和中东等其他地区都没有本国的相关应用，用的较多的职场社交应用也是LinkedIn。LinkedIn在中国虽没被禁用，但好像中国职场人士大多都喜欢用另一款
APP。因此，希望我的 MaiInt
你能喜欢。最后我还要推荐一个邮箱验证在线服务<https://trumail.io/>，它可以为开发类似MaiInt的OSINT工具提供更多帮助。

 ***参考来源：[VincentYiu](https://vincentyiu.co.uk/maiint-profiling-china-based-employees/)，clouds 编译，转载请注明来自 FreeBuf.COM**  

