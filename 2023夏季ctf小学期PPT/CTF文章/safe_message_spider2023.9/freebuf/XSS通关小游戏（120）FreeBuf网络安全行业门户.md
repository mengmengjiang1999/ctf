## 第一关：

没有任何的过滤方式，直接构造： <script>alert(1)</script>方法不限

![](https://image.3001.net/images/20211030/1635562459_617cb3dba9fd8207431fe.png!small)![](https://image.3001.net/images/20211030/1635562473_617cb3e90813e147639ca.png!small)

## 第二关：

源码分析：![](https://image.3001.net/images/20211030/1635562514_617cb4120b3b115f9cd94.png!small)

那么这题可以采用不带特殊字符进行绕过，如：

onclick=alert() 当鼠标点击触发

onmousemove=alert() 当鼠标移动触发

onload=alert() 当页面加载完触发

onerror=alert() 当出错触发

![](https://image.3001.net/images/20211030/1635562544_617cb4305872cec9fecfc.png!small)

## 第三关：

源码分析：![](https://image.3001.net/images/20211030/1635562571_617cb44b19b7fcde91456.png!small)

<input name=keyword value='".htmlspecialchars($str).'">//这里也被进行了特殊字符转换

但是htmlspecialchars默认配置是不过滤单引号。只有设置了：quotestyle，才可以

那么可以用单引号闭合并且不能包含<>则就可以用 'onclick='alert(1)

![](https://image.3001.net/images/20211030/1635562681_617cb4b9f2d25cae7d4cc.png!small)

## 第四关：

源码分析：![](https://image.3001.net/images/20211030/1635562705_617cb4d10c989c98bf062.png!small)

其他事件都可以，把闭合方式闭合成功即可![](https://image.3001.net/images/20211030/1635562720_617cb4e0759bdeb8725e0.png!small)

## 第五关：

源码分析：![](https://image.3001.net/images/20211030/1635562742_617cb4f62122709781b98.png!small)

这里进行事件不能通过，都包含on 所以我们可以进行<a
href="javascript:alert(1)">tets</a>标签伪协议![](https://image.3001.net/images/20211030/1635562801_617cb5318eca509b9a70d.png!small)![](https://image.3001.net/images/20211030/1635562812_617cb53cb52479c99b821.png!small)

## 第六关：

源码分析：![](https://image.3001.net/images/20211030/1635562829_617cb54d3bce4cddc7cf9.png!small)

方法很多，主要这关没有置换小写strtolower()函数，大小写绕过等![](https://image.3001.net/images/20211030/1635562847_617cb55f5947a46b08635.png!small)

## 第七关：

分析源码：![](https://image.3001.net/images/20211030/1635562868_617cb5748c14b584c8b96.png!small)

这关大小写不行了，有了置换小写函数，但替换都成了空，因此可以用双写进行绕过，方法很多![](https://image.3001.net/images/20211030/1635562889_617cb5893848f2583a38a.png!small)

## 第八关：

源码分析：![](https://image.3001.net/images/20211030/1635562917_617cb5a537a1c8344d4b6.png!small)

置换为小写，关键字替换，加上输入框特殊字符转换HTML实体，所以只能采用a标签的伪协议javascript:alert(1)
,但因为script被替换了,所以可以采用单个字符串转换为十六进制最后绕过javascript:alert(1) 绕过成功

HTML实体字符转换：[https://www.qqxiuzi.cn/bianma/zifushiti.php](https://www.qqxiuzi.cn/bianma/zifushiti.php)![](https://image.3001.net/images/20211030/1635562935_617cb5b7b7c319a266803.png!small)![](https://image.3001.net/images/20211030/1635562945_617cb5c1bf4234cc3dc30.png!small)

## 第九关：

分析源码：![](https://image.3001.net/images/20211030/1635562965_617cb5d5b90ced1155b7e.png!small)

这题多了一个url检测，必须要带上http:// 但又会影响代码执行，所以把http://注释，构造函数为：

javascript:alert(1) /*http:// */

javascript:alert(1)
//http://![](https://image.3001.net/images/20211030/1635562983_617cb5e7ede5c681c9c47.png!small)

## 第十关：

分析源码：![](https://image.3001.net/images/20211030/1635563002_617cb5fa68b2ad8471c81.png!small)

这题首先有两个参数，可以从分析结果看，真正传的参数是t_sort，但又是隐藏域，在页面不显示，所以我们需要调用这参数，再闭合，后改属性为文本显示出来，构造payload：t_sort="onclick="alert(1)"
type="text![](https://image.3001.net/images/20211030/1635563021_617cb60d64d9a34cf453f.png!small)![](https://image.3001.net/images/20211030/1635563030_617cb6169079811155554.png!small)

## 十一关：

源码分析：![](https://image.3001.net/images/20211030/1635563050_617cb62ab03fd53e3c398.png!small)

关键在于最后输入框传递的变量，顺着变量的方向寻找，找到过滤方式，最后也带入了Referer，所以这道题是从Referer绕过，再上是隐藏域，所以先闭合，再显示出文本框，最后加个事件。这里我用了火狐插件hackbar，也可以用burpsuite工具。构造：11"
type="text"
onclick="alert(1)"![](https://image.3001.net/images/20211030/1635563067_617cb63bdf254055b4e49.png!small)![](https://image.3001.net/images/20211030/1635563080_617cb6486820dc5acb3ad.png!small)

## 十二关：

分析源码：![](https://image.3001.net/images/20211030/1635563099_617cb65b282cca9deca70.png!small)

跟上题同上，只不过换另一只提交方式UA，构造：" type="text" onclick="alert(1)
这构造跟上道题有两点不同，前面少加了数字和最后少加了双引号闭合，可以看图下，这样子是一个完全闭合语句，也是没有问题的。![](https://image.3001.net/images/20211030/1635563121_617cb671b89640b498a31.png!small)![](https://image.3001.net/images/20211030/1635563134_617cb67ee288f85cc177c.png!small)

## 第十三关：

分析源码：![](https://image.3001.net/images/20211030/1635563151_617cb68fea43713434b09.png!small)

还是跟前两关一样，只是修改了提交方式，这道题是cookie，这里我使用了burpsuite工具抓包，从cookie构造：" type="text"
onclick="alert(1)![](https://image.3001.net/images/20211030/1635563167_617cb69fef6104a18c338.png!small)![](https://image.3001.net/images/20211030/1635563177_617cb6a98fc09db522c60.png!small)

## 第十四关：

据说是一个图片中的exif信息，但是网址已失效

## 第十五关：

AngularJS ng-include指令
（AngularJS前端三大框架之一，没学过）![](https://image.3001.net/images/20211030/1635563208_617cb6c820910234d37c0.png!small)

## 第十六关：

源码分析：![](https://image.3001.net/images/20211030/1635563226_617cb6da259b9ef0f46ff.png!small)

首先GET传参肯定是在url输入，其次传递的值置换为小写，再者把script、/、空格替换了，这题空格可以用%0a或者%0d进行绕过，其他标签属性没替换可以用，构造：<img%0asrc=x%0aonerror=alert(1)>![](https://image.3001.net/images/20211030/1635563242_617cb6ea739b3af59dbfb.png!small)

## 第十七关：

这张图片是从其他网站上看到的，也试过，发现还是没有用，还觉得移动事件写错了，也尝试了正确的移动事件onmousemove,结果还是没有用![](https://image.3001.net/images/20211030/1635563262_617cb6fe516a359ca466e.png!small)

## 第十八关：

代码和第十七关一样，同上

## 第十九关：

flash xss

## 第二十关：

flash xss

  

