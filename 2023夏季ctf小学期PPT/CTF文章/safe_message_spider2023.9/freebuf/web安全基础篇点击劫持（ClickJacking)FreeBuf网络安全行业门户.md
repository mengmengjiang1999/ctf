## 前言

此文章学习总结与《白帽子讲WEB安全》及借鉴了各路大神的文章，欢迎讨论与指正。

2008年，发现了一种Click
Jacking（点击劫持）的攻击，这类攻击方式影响了几乎所有的桌面平台，包括IE、firefox、opera、flash等。

## 一、什么是点击劫持

点击劫持是一种视觉上的欺骗手段。攻击者使用一个透明的、不可见的ifiame，翻盖在一个网页上，然后诱使用户在该网页上进行操作，此时用户将在不知情的情况下，点击透明的iframe页面。通过调整iframe页面的位置，可以诱使用户恰好点击在iframe的一些功能性按钮上。

比如目前网页上的一些广告弹窗有一部分使用这种攻击方式。

点击劫持与CSRF攻击有异曲同工之妙，都是在用户不知情的情况下诱使用户完成一些动作。但是在CSRF攻击过程中如果出现用户交互的页面，则攻击者可能无法顺利完成，与之相反的是，点击劫持没有这个问题，他利用的就是与用户产生交互的页面。

例子如下

    
    
    <!DOCTYPE html>
    <html>
    <head>
    	 <meta charset="UTF-8">
         <title>点击劫持</title>
    <style>
    	iframe {
    		/*窗口的大小*/
    		width: 2500px;
    		height: 1600px;
    		
    	
    		/*定位绝对位置*/
    		position: absolute;
    		top: -195px;
    		left: -740px;
    		z-index: 2;
    		
    		/* 从视图上隐藏 */
    		-moz-opacity: 0.5;
    		opacity: 0.5;
    		filter: alpha(opacity=0.5);
    		
    		}
    		
    		/*按钮的位置*/
    		button{
    			position: absolute;
    			top: 100px;
    			left: 32px;
    			z-index: 1;
    			width: 120px;
    	}
    </style>
    </head>
    
         <body>
              <button>test</button>
              <iframe src="https://www.freebuf.com/vuls/334263.html"></iframe>
         </body>
    </html>
    

html中有一个button按钮，如果iframe完成透明时，那么用户看到的就是，（opacity: 0.5参数调整为0)

![image.png](https://image.3001.net/images/20220527/1653585266_628fb57241c6931729a88.png!small)

当iframe半透明时，可以看到，上面的按钮其实覆盖在另一个网页上

![image.png](https://image.3001.net/images/20220527/1653585275_628fb57b4ea852b769e70.png!small)

其中起到关键作用的代码就是

    
    
    iframe {
    		width: 2500px;
    		height: 1600px;
    		
    	
    		/*定位绝对位置*/
    		position: absolute;
    		top: -195px;
    		left: -740px;
    		z-index: 2;
    		
    		/* 从视图上隐藏 */
    		-moz-opacity: 0.5;
    		opacity: 0.5;
    		filter: alpha(opacity=0.5);
    		
    		}
    

通过控制iframe的width（宽度）、height（长度）以及调试top、left的位置，可以把iframe页面内的任意部分覆盖到任何地方。同时设置iframe的position（位置）的absolute（绝对值），z-index设置为最大让iframe窗口在页面的最上层，在通过设置opacity在控制页面的透明程度，0为不可见iframe中的内容。

## 二、图片覆盖攻击

点击劫持本质上是一种视觉欺骗，我们可以顺着这个思路发掘一些攻击，如果图片覆盖。

一名叫sven.vetsch的安全研究者最先提出这种Cross Site Image
Overlaying攻击，简称XSIO。是通过调整图片的style使得图片能够覆盖在他指定的任意位置

    
    
    <a href="http://192.168.163.131/DVWA">
    <img src="http://192.168.163.131/2.png" style="position:absolute;right:100px;top:90px;" >
    </a>
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
         <meta charset="UTF-8">
         <title>图片覆盖</title>
    </head>
    <body>
         <a href="https://www.freebuf.com/vuls/334263.html">
              <img src="http://192.168.163.132/1.png" style="position:absolute;top:90px;left:320px;" />
         </a>
    </body>
    </html>
    

页面被一张图片覆盖并指向 https://www.freebuf.com/vuls/334263.html
这个地址，如果用户点击了这个图片，那就会直接跳转到该网站，如果这个是恶意网站，用户点击后，会出现危害。

XSIO是因为没有限制图片的 position属性为 absolute，导致可以控制一张图片出现在网页的任意位置，形成点击劫持。

图片还可以伪装的像一个正常链接、按钮。或者在图片中构造一些文字，覆盖在关键位置，就可以达到欺骗的目的。

比如利用XSIO修改页面中的联系电话，可能很多人会上当。

由于img标签在很多系统中是对用户开放的，因此现实中很多站点可能存在XSIO。在防御XISO时候，需要检查用户提交的HTML代码中，img标签的style属性是否可能导致复现。

## 三、拖拽劫持与数据窃取

2010年，名为Paul Stone的安全专家提出浏览器拖拽事件导致的安全问题。

目前很多浏览器都开始支持Drag&Drop的API。对于用户来说，拖拽使他们的操作更加简单。浏览器中的对象可以是链接，文字或者窗口，因此拖拽不受同源策略的限制。

拖拽劫持的思路是诱使用户从隐藏的不可见iframe中拖拽出攻击者希望得到的数据，然后放到攻击者能控制的另一个页面中，进行窃取数据。

在JavaScript或者java
API的支持下，这个攻击过程会变得非常隐蔽。因此它突破了传统点击劫持得先天局限，所以这种新型得拖拽劫持能够导致更大得危害。

## 四、点击劫持3.0：触屏劫持

2010年9月，安全专家公布智能手机上的触屏劫持攻击。

一次触屏操作，可能会对应以下几个事件：

    
    
    touchstart 手指触摸屏幕时发生
    touchend 手指离开屏幕时发生
    touchmove 手指滑动时发生
    touchcancel 系统可取消touch事件
    

通过讲一个不可见的iframe覆盖到当前网页上，可以劫持用户的触屏操作。

而且手机上的屏幕空间有限，手机浏览器为了节约空间，甚至隐藏了地址栏，因此手机的视觉欺骗可能会更加容易实行。

电脑打开网页

![image.png](https://image.3001.net/images/20220527/1653585293_628fb58dcaf7d380205b5.png!small)

手机打开网页

![image.png](https://image.3001.net/images/20220527/1653585301_628fb5954e2cd9ea6e110.png!small)

下面手机端打开网页时不显示url的，所以手机端的视觉欺骗更加难以识别。

## 五、防御点击劫持攻击

点击劫持是一种视觉上的欺骗，针对传统的点击攻击，一般时通过禁止跨域的iframe来规范的。

### 5.1 frame busting

我们可以利用JavaScript，禁止iframe嵌套

    
    
    if (top.location != location) {
    	top.location = self.location;
    }
    

但是这种frame busting也存在一些缺陷。由于他是用于JavaScript写的，控制能力不是特别强，是有办法绕过的。

斯坦福大学总结了一篇关于"攻击frame busting"，详细讲述了各种绕过frame busting的方法

    
    
    http://seclab.stanford.edu/websec/framebusting/
    

### 5.2 X-Frame-Options

因为frame busting是可以绕过的，所以我们需要寻找其他的解决方案。使用HTTP头中的X-Frame-Options。

X-FRAME-OPTIONS是微软提出的一个http头，专门用来防御利用iframe嵌套的点击劫持攻击。并且在IE8、Firefox3.6、Chrome4以上的版本均能很好的支持。

他又三个可选值：

    
    
    DENY	拒绝任何域加载
    SAMEORIGIN	允许同源域下加载
    ALLOW-FROM origin	可以定义允许frame加载的页面地址
    

当值为DENY，浏览器会拒绝当前页面加载任何frame页面；值为SAMEORIGIN，则frame页面的地址只能加载同源下的页面；值为ALLOW-FROM，则可以定义允许frame加载的页面地址。

在PHP中可以这样配置：

    
    
    header('X-Frame-Options:Deny');
    

在 Firefox浏览器中，使用 NoScript 扩展能够在一定程度上检测和阻止点击劫持攻击。利用 NoScript 中 ClearClick
组件能够检测和警告潜在的点击劫持攻击，自动检测页面中可能不安全的页面。

## 六、总结

点击劫持相对于XSS与CSRF来说，因为需要诱使用户与页面产生交互行为，因此实施攻击的成本较高，但攻击者讲此漏洞利用在钓鱼、欺诈和流氓广告等方面。

点击劫持结合CRSF：通常的CRSF攻击由于同源策略、token等的原因，会攻击失败，但是点击劫持本就是在iframe中调用原网页，服务器会认为是用户在正确的页面做出了这些操作，可以通过点击劫持，去控制用户做那些csrf做不了的操作。

点击劫持结合XSS:
反射性xss漏洞触发时会在页面url中存在恶意xss代码，目前谷歌浏览器等都会进行拦截或警告，但是如果利用点击劫持，控制用户做出点击触发js代码的操作，就不会触发浏览器的安全策略，将一个原本可能无关紧要的漏洞变的具备威胁。

