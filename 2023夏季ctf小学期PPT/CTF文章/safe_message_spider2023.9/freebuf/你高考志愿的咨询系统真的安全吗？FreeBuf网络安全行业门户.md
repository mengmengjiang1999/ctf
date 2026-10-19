原创： EEE 合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

![v2-b6ac4acb391e97c8ef3bf1f3f5fe9a62_hd.w](https://pic4.zhimg.com/80/v2-b6ac4acb391e97c8ef3bf1f3f5fe9a62_hd.webp)

背景随着各省高考的结束，亲戚家表弟表妹也都开始陆续准备填报志愿，志愿咨询系统倒是有很多，但由考试院主办的这种官方性质的就比较少了。正好之前的一点存货拿出来分享一下（声明：文中所涉及的所有漏洞已全部修复解决完毕，并已加强了安全策略。笔者初衷于分享与普及网络知识，提供安全防御思路。若读者因此而作出任何危害网络安全行为后果自负，与合天智汇及原作者无关）

![v2-a17f39b0263ccd7b5082f9456ca34bcd_hd.w](https://pic4.zhimg.com/80/v2-a17f39b0263ccd7b5082f9456ca34bcd_hd.webp)

误打误撞的信息泄露

首先映入眼帘的是其官网首页。

这里建议一下大家，渗透在开始阶段不要直接上来拿扫描器一通乱打，尤其这种可能存在防火墙设备的单位，搞不好可能会直接ban掉ip，后续继续渗透可能还要挂代理这样就会麻烦很多。

![v2-73b9546038cdbc4ffcd17e912697ea63_hd.w](https://pic3.zhimg.com/80/v2-73b9546038cdbc4ffcd17e912697ea63_hd.webp)

常见的源码泄露问题，一般都存在于网站根目录中由于开发过程不规范，上线前未做安全检查，导致出现例如svn泄露，.git泄露。

而这种验证方法也很简单。访问url即可。

（.git泄露）http://[ip]/.git/HEAD

![v2-b0c04a8c7c603841670c8529a2465a6d_hd.w](https://pic3.zhimg.com/80/v2-b0c04a8c7c603841670c8529a2465a6d_hd.webp)

类似的还比如.svn泄露 格式如下：http://[ip]/.svn/entriesp

其结果最终会导致网站全部源码及关键信息全部泄露，攻击者可直接通过读取源码中的数据库密码，或通过代码分析出新的漏洞，达到进一步侵入服务器的恶意利用行为。

这种问题可以在某云镜像中的漏洞库中可以看到，问题是个小问题，但是影响就非常大了。

![v2-9615ff4a5a9d5465e9c1b6c846e8a48d_hd.w](https://pic1.zhimg.com/80/v2-9615ff4a5a9d5465e9c1b6c846e8a48d_hd.webp)

但在本系统中虽然没发现在服务器配置层面出现的源码泄露问题，但误打误撞发现了目录结构泄露的问题，目录结构泄露的问题，这种问题基本上一发现，整个网站都有这种问题。测试方法和简单，在网站路径后输入目录名称即可，当然后续中AWVS扫描器结果也发现了该问题。

![v2-2d3e6a744998f3fc16e4586ced40c058_hd.w](https://pic3.zhimg.com/80/v2-2d3e6a744998f3fc16e4586ced40c058_hd.webp)

目录索引结构所泄露的问题，其实就非常明显了，即使我们无法直接获取后台的源码，但是也可以通过索引结构，暴露出一些后台地址，上传点等敏感业务功能，或者看见其他攻击者上传的木马，直接盗马利用。增加了攻击线索。就比如下面暴露的这些目录，就为接下来的渗透埋下了伏笔。

![v2-46ccf7634de52b52dd04bcc228e65873_hd.w](https://pic4.zhimg.com/80/v2-46ccf7634de52b52dd04bcc228e65873_hd.webp)

![v2-bf4dd73df11d94303ce4193bd4b64177_hd.w](https://pic2.zhimg.com/80/v2-bf4dd73df11d94303ce4193bd4b64177_hd.webp)

遍地的XSS

存储性XSS都常见于个人信息，留言功能或在线聊天的会话功能处。虽然本网站没有提供在线的咨询服务，但恰好提供了各个院校的咨询留言，并会展示到网站首页。

![v2-646c7e11009c86f099f23553098f5d4f_hd.w](https://pic2.zhimg.com/80/v2-646c7e11009c86f099f23553098f5d4f_hd.webp)

比较尴尬的是...所有功能点中尝试的XSS攻击基本上全部都生效了...网站并没有提供任何的防护。

分享一些流传比较多的XSS语句

这些攻击语句基本上都是大家做XSS中常用的，可以收藏起来需要的时候直接无脑使用。

><script>alert(document.cookie)</script>
='><script>alert(document.cookie)</script>
"><script>alert(document.cookie)</script>
<script>alert(document.cookie)</script> <script>alert(vulnerable)</script>
%3Cscript%3Ealert('XSS')%3C/script%3E <script>alert('XSS')</script>
<imgsrc="javascript:alert('XSS')"> <imgsrc="http://xxx.com/yyy.png"
onerror="alert('XSS')"> <divstyle="height:expression(alert('XSS'),1)"
/>（这个仅限IE 有效）

![v2-7664f027cf873439450948cf8aedb4ce_hd.w](https://pic2.zhimg.com/80/v2-7664f027cf873439450948cf8aedb4ce_hd.webp)

![v2-cd451eb884577699c3c71462d825ed25_hd.w](https://pic3.zhimg.com/80/v2-cd451eb884577699c3c71462d825ed25_hd.webp)

![v2-8eca10306f15d37895c9e4a1e29a2feb_hd.w](https://pic3.zhimg.com/80/v2-8eca10306f15d37895c9e4a1e29a2feb_hd.webp)

缺一点权限

发现了这么一堆XSS和信息泄露，总感觉都不痛不痒，这啥玩意权限都没有，所以接下来的渗透重心就放在了权限上。

![v2-a69250abe700f0b2e421d13c75caa369_hd.w](https://pic2.zhimg.com/80/v2-a69250abe700f0b2e421d13c75caa369_hd.webp)

在这里发现了一个小问题，没有验证码...这就意味着可以直接爆破，其次高校管理员的登陆口也暴露出来。（利用之前索引目录泄露也可以暴露这个问题）

然后进入登录口，第一条就告诉我，初始密码是院校代码.....

![v2-5bb931d9f0f5e0dcbf4de78e5810841a_hd.w](https://pic3.zhimg.com/80/v2-5bb931d9f0f5e0dcbf4de78e5810841a_hd.webp)

由此判断，大批量的院校代码密码也都是一样的。

所以就傻傻的找全国高校代码去了，发现验证码也是可以直接被爆破的，遂进行爆破

![v2-8300b955e6ad98972d7ae88dc0015ec6_hd.w](https://pic1.zhimg.com/80/v2-8300b955e6ad98972d7ae88dc0015ec6_hd.webp)

302跳转的全部都是存在弱口令的，其实在之前的索引泄露中，也泄露的这一批文件夹，就是各个院校的文件夹，95%的管理员都没有改密码，涉及400多管理员账户。

![v2-46ccf7634de52b52dd04bcc228e65873_hd.w](https://pic2.zhimg.com/80/v2-46ccf7634de52b52dd04bcc228e65873_hd.webp)

随便拿一个账户登录：

![v2-6c536d14bc42cefb8661f8e2eea0cd27_hd.w](https://pic3.zhimg.com/80/v2-6c536d14bc42cefb8661f8e2eea0cd27_hd.webp)

![v2-bf6d294526f12eab48e6dc3b64acae96_hd.w](https://pic2.zhimg.com/80/v2-bf6d294526f12eab48e6dc3b64acae96_hd.webp)

总结

至此，本次发现了信息泄露，XSS，验证码绕过，后台管理员弱密码等问题，该网站为某教育考试院属下的志愿咨询系统。注册量用户多，考生也会集中在这两个月登录。XSS甚至都可以打全站用户。

信息泄露其实本身作用并不大，但如果一旦泄露了重要的攻击信息，那就很比较大了。

问题比较严重，第一时间上报领导了，大概已经过了一个多月了，问题也全部修复了，给各位小伙伴们提供了思路，分享交流渗透过程。若读者因此而作出任何危害网络安全行为后果自负，与合天智汇及原作者无关。

![v2-a79f3ccfcdcddcfccf8d8e039e539803_hd.w](https://pic4.zhimg.com/80/v2-a79f3ccfcdcddcfccf8d8e039e539803_hd.webp)

相关实验

个人密码安全：网络大爆炸的现代，几乎可以通过一个点，将一个人所有的资料都挖掘出来，可以说没有了隐私。而在这样的大环境下，网络上的个人密码设置安全就显得尤为重要。

点击“[实验:个人密码安全(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECIDee9320adea6e062017112014260100001)”，可预览学习（PC端操作最佳哟）![image.png](https://image.3001.net/images/20190726/1564109518_5d3a6ace6719c.png!small)  

