上传漏洞是常见的漏洞之一，利用上传漏洞可以上传木马到服务器，从而达到提权的目的。在进行渗透测试的时候，网站往往会有一些限制，限制你的渗透行为。上传漏洞常见的验证一种就是前端验证，本篇文章主要介绍在进行渗透测试的时候如果绕过前端的验证，做一个总结。

![](https://image.3001.net/images/20211124/1637734579_619dd8b37f79bd8bf954b.jpg!small)

注：本篇文章用的靶场是uploads-labs

首先,我们知道js
是服务器返回给客户端的,并作用在客户端的浏览器。那么我们可以把服务器返回的这个js验证函数让它返回true.那么你上传php等木马文件的时候,就会可以上传,也就能抓到包.这是一种解法.

##  **手法**

既然是前端验证你在选择好木马文件的时候就已经开始验证了，自然你抓发送到服务器的数据包是抓不到的。那要怎么抓?在上传之前抓,抓服务器返回的js。

![](https://image.3001.net/images/20211124/1637734648_619dd8f84843e4cce77e6.png!small)

直接刷新，抓这个第一关的数据包。

![](https://image.3001.net/images/20211124/1637734688_619dd9207d619cab59b11.png!small)

抓到之后抓这个数据包的返回包。

![](https://image.3001.net/images/20211124/1637734744_619dd958b0e725a1853bf.png!small)![](https://image.3001.net/images/20211124/1637734764_619dd96c2550aa2329d83.png!small)

可以看到这个js验证号函数，只要返回的是true 就会绕过验证，那么我们直接修改这个函数让它为true。

![1637734789_619dd985247fd301a039a.png!small](https://image.3001.net/images/20211124/1637734789_619dd985247fd301a039a.png!small)

然后我们上传木马，

![1637734808_619dd99841e47764c022e.png!small](https://image.3001.net/images/20211124/1637734808_619dd99841e47764c022e.png!small)

![1637734821_619dd9a5aecaa826f895a.png!small](https://image.3001.net/images/20211124/1637734821_619dd9a5aecaa826f895a.png!small)

可以看到上传成功了。然后复制图片链接用菜刀连接就好了。

那么有没有其他的解法呢?

当然是有的。既然是前段验证,那么我们是不是直接在浏览器改变这个js验证呢?

我们在前端找到这个调用checkFile函数的地方。

![1637734845_619dd9bdbb6baa0727e67.png!small](https://image.3001.net/images/20211124/1637734845_619dd9bdbb6baa0727e67.png!small)

  

既然函数返回true 就会绕过验证,那么我们直接把这个调用改为1不就行了。

![1637734861_619dd9cd706a9f0407773.png!small](https://image.3001.net/images/20211124/1637734861_619dd9cd706a9f0407773.png!small)

上传试一试。

![1637734871_619dd9d7bf65de2713438.png!small](https://image.3001.net/images/20211124/1637734871_619dd9d7bf65de2713438.png!small)

![1637734877_619dd9dd08a811f4841f3.png!small](https://image.3001.net/images/20211124/1637734877_619dd9dd08a811f4841f3.png!small)

也是成功了。

  

另一种思路,当我们在上传的页面把这个js函数不会被加载,是不是就会被绕过了，浏览器都有一些禁用js的插件。

  

![1637734895_619dd9efa3b88a309fc06.png!small](https://image.3001.net/images/20211124/1637734895_619dd9efa3b88a309fc06.png!small)

禁用之后我们再上传。

![1637734908_619dd9fc833fea5b1ac4f.png!small](https://image.3001.net/images/20211124/1637734908_619dd9fc833fea5b1ac4f.png!small)

同样也是绕过了，所以只要是你掌握了精髓,完全可以灵活的运用。![1637734929_619dda111ee5c8db0f38b.png!small](https://image.3001.net/images/20211124/1637734929_619dda111ee5c8db0f38b.png!small)

这也告诉我们在学习的时候要发现学习，多思考。

  

  

