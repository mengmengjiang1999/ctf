## 一、概要

**2018年4月，腾讯安全曝光了“寄生推”，揭开了流量黑产的面纱，让大众了解到黑产正逐步隐藏到幕后，通过伪装正规SDK的方式，借助大众开发者触达用户，然后动态下发指令，通过恶意广告和应用推广，赚取广告推广费用，实现灰色牟利。无独有偶，近日，依托腾讯安全大数据，腾讯安全反诈骗实验室追踪到暴风影音、天天看、塔读文学等众多应用中集成的某SDK存在下载恶意子包，通过webview配合js脚本在用户无感知的情况下刷百度广告的恶意操作。**

该恶意SDK通过众多应用开发者所开发的正规应用，途经各中应用分发渠道触达千万级用户；其背后的黑产则通过恶意SDK留下的后门控制千万用户，动态下发刷量代码，大量刷广告曝光量和点击量，赚取大量广告费用，给广告主造成了巨额广告费损失。

根据安全人员详细分析，此恶意SDK主要存在以下特点：

> 1\.
> 该SDK被1000+千应用开发者使用，通过应用开发者的分发渠道抵达用户。主要涉及的应用包括掌通家园、暴风影音、天天看、塔读文学等，潜在可能影响上千万用户；
>
> 2\. 刷量子包通过多次下载并加载，并从服务器获取刷量任务，使用webview加载js脚本实现在用户无感知的情况下自动化的进行刷量任务。

此类流量黑产给传统的广告反作弊带来了极大挑战，传统通过IP、曝光频率、点击率等表象数据形成的反作弊策略难以识别这种控制大量真实设备做’肉鸡’的刷量作弊，使得大量广告费用流入黑产手中，却无法给广告主带来应有的广告效果。

## 二、SDK作恶流程和影响范围

此恶意SDK集成在应用中的那部分代码没有提供实际功能，其在被调用后会定时上报设备相关信息，获取动态子包的下载链接，下载子包并加载调用。然后由子包执行相应的恶意行为。

恶意SDK作恶流程示意图：

![](https://image.3001.net/images/20190423/1555990018_5cbe8602108ae.png!small)

受恶意SDK影响的主要应用列表：

![](https://image.3001.net/images/20190423/1556001333_5cbeb23575b75.png!small)

![](https://image.3001.net/images/20190423/1556001373_5cbeb25d334e9.png!small)

## 三、恶意SDK作恶行为详细分析

此恶意SDK被众多的中小应用开发者集成，我们以应用塔读文学为例，对其恶意行为进行详细分析。

![](https://image.3001.net/images/20190423/1556001429_5cbeb295b9074.png!small)

恶意SDK代码结构：

![](https://image.3001.net/images/20190423/1555991123_5cbe8a53652bf.png!small)

此sdk代码较少，没有什么实际的功能。其在被加载调用后，会设置定时任务，每隔3600秒（1小时）启动GatherService，上报设备相关信息，获取动态子包__gather_impl.jar的下载链接。

![](https://image.3001.net/images/20190423/1555991237_5cbe8ac5e356e.png!small)

GatherService链接服务器，获取__gather_impl.jar的下载链接。

![](https://image.3001.net/images/20190423/1555991264_5cbe8ae0c49ba.png!small)

请求链接：<http://gather.andr>****.com:5080/gupdate/v1。

请求数据：包括uid、应用包名、设备id、应用版本、手机厂商、型号、系统版本、imei、sdk版本等内容。

![](https://image.3001.net/images/20190423/1555991423_5cbe8b7f2a870.png!small)

返回内容：包括子包的版本、下载url、文件md5。

![](https://image.3001.net/images/20190423/1555991471_5cbe8baf27e0c.png!small)

动态加载下载的__gather_impl.jar。

![](https://image.3001.net/images/20190423/1555991526_5cbe8be6f2879.png!small)

子包__gather_impl.jar代码结构，此子包的主要功能有：1、上传用户设备信息，2、下载并动态加载子包stat-impl.jar。

![](https://image.3001.net/images/20190423/1555991586_5cbe8c221ebbc.png!small)

1）链接服务器，上传用户设备信息

![](https://image.3001.net/images/20190423/1555991635_5cbe8c532e536.png!small)

服务器链接：<http://userdata.andr>****.com/userdata/userdata.php （此url在分析时已失效，无法链接）。

上报内容：包括位置信息（经纬度），用户安装列表（软件名、包名），设备信息（厂商、型号、fingerprint，是否root），deviceid、手机号、运营商、imei、mac等。

![](https://image.3001.net/images/20190423/1555991698_5cbe8c926600d.png!small)

2）再次请求服务器，获取stat-impl.jar的下载链接。

![](https://image.3001.net/images/20190423/1555991745_5cbe8cc105894.png!small)

请求链接：<http://iupd.andr>****.com:6880/wupdate/v1。

请求数据：包括uid、imei、sdk版本、手机厂商、型号、系统版本、应用包名、设备id、设备指令集等内容。

![](https://image.3001.net/images/20190423/1555991808_5cbe8d00b2547.png!small)

返回内容：包括子包的版本、下载url、文件md5。

![](https://image.3001.net/images/20190423/1555991908_5cbe8d64d91f5.png!small)

子包下载完成后，调用native方法动态加载此子包。

![](https://image.3001.net/images/20190423/1555992082_5cbe8e12c01b7.png!small)

![](https://image.3001.net/images/20190423/1555992088_5cbe8e18c83af.png!small)

![](https://image.3001.net/images/20190423/1555992382_5cbe8f3e1169f.png!small)

stat-impl.jar的代码结构：

![](https://image.3001.net/images/20190423/1555992421_5cbe8f6517139.png!small)

stat-impl.jar子包被加载后，线程com.drudge.rmt.g会被启动，其作用主要是用来联网获取刷量任务，并调度任务的执行。

主要的刷量任务包括：1、刷百度搜索的关键字，2、使用js脚本实现自动点击、滑动来刷百度广告和亿量广告的点击，3、使用webview刷网页访问。

1\. 刷百度关键字搜索

此任务会根据获取json字符串，进行相应的操作，包括设置BAIDUID、更新配置、添加任务、设置剪切板和使用关键字刷百度搜索。

设置关键字，使用webview加载对应的url：

![](https://image.3001.net/images/20190423/1555992630_5cbe9036a2003.png!small)

捕获到的刷百度关键字的webview加载请求：

![](https://image.3001.net/images/20190423/1555992644_5cbe9044bb1e7.png!small)

链接服务器<http://tw.andr>****.com:6080/wtask/v1获取相关任务,并将任务内容存入[package]/cache/volley目录下：

![](https://image.3001.net/images/20190423/1555992729_5cbe909920266.png!small)

![](https://image.3001.net/images/20190423/1555992746_5cbe90aa8d26f.png!small)

2\. 使用js脚本刷百度广告

使用webview加载<http://mobads.baidu.com/ads/index.htm>，并在加载完成后执行js脚本实现自动滑动、点击、保存等操作来自动刷广告。

![](https://image.3001.net/images/20190423/1555992816_5cbe90f0096cc.png!small)

相关的js脚本。

1）js函数定义滑动、点击、保存等操作。

![](https://image.3001.net/images/20190423/1555992988_5cbe919cf2581.png!small)

Java层解析并实现js层传递过来的操作命令。

![](https://image.3001.net/images/20190423/1555993052_5cbe91dc82764.png!small)

2）js函数判断并获取页面元素。

![](https://image.3001.net/images/20190423/1555993133_5cbe922d5dcaf.png!small)

...

![](https://image.3001.net/images/20190423/1555993161_5cbe9249d0812.png!small)

3）js函数计算页面元素相对位置，并进行滑动、点击操作。

![](https://image.3001.net/images/20190423/1555993206_5cbe92760f3f7.png!small)

...

捕获到的刷百度广告的webview加载请求：

![](https://image.3001.net/images/20190423/1555993238_5cbe92963dd8b.png!small)

3、使用webview刷网页访问

此任务向服务器请求需要访问的url链接，在获取到相应的网页url后，使用webview加载进行访问。

请求需要访问的url链接

![](https://image.3001.net/images/20190423/1555993286_5cbe92c60e2e0.png!small)

    
    
    请求链接
    
    [http://us.yiqimeng.men:8080/geturls?k=beike-xinshiye&c=5](http://us.yiqimeng.men:8080/geturls?k=beike-xinshiye&c=5)
    
    返回内容
    
    ["<http://m.xinshiye.cc/cars/17/10/21/707989.html?content_id=707989u0026key=x2HAJuZaaa9YWpVa8EXTqOmHHUxhSnj75xhhAS7f6tveQsphsCm3jc9xrhV4RZbRzgm%2FQqzCVcw2dvukMqw25Q%3D%3Du0026_t=1511190410>",
    
    "<http://m.xinshiye.cc/cars/17/10/11/234818.html?content_id=234818u0026key=NzLZyHQXsCdpS6bkAWab2LSzd2XApbGOJYUuN%2Bm4PFsoWk1l%2FnZSD8M1yp1cuhz%2FdL0uoNG93TVt8ai6zEU%2BQw%3D%3Du0026_t=1511190560>",
    
    "<http://m.xinshiye.cc/cars/17/11/26/1769446.html?content_id=1769446u0026key=8KLxL1fm2gwNDxqT6nsSAbQ07kcEZRHBrekhzNSJcNaAg1nZmbW49pQ3EaEYJfMUeMlwSX4KzdliXJ3O37fs9g%3D%3Du0026_t=1513046929>",
    
    "<http://m.xinshiye.cc/cars/17/10/31/1444661.html?content_id=1444661u0026key=mODVhDy0zyzBGH1G6sTwDYXqiy3D7pDfymsirda6s5%2BW8tarfIDPjuhT3mkqeMMDKzKr%2BFVC2Py2gzsNkMniHw%3D%3Du0026_t=1509589907>",
    
    "<http://m.xinshiye.cc/cars/17/12/09/1921549.html?content_id=1921549u0026key=0XFxkCX0Bn4k%2Fw5%2FqvlSIOCREqEWoJ5jimqn%2BZAeJIwksQzydyT0AZFAVZJAritm3hpGza4TFNlONZDtoY%2BfTA%3D%3Du0026_t=1513045278>"]

使用webview访问获取url：

![](https://image.3001.net/images/20190423/1555993342_5cbe92fe0a7c0.png!small)

捕获到的刷求医不如健身网的webview加载请求：

![](https://image.3001.net/images/20190423/1555993368_5cbe9318dc047.png!small)

## 四、相关URL整理

![](https://image.3001.net/images/20190423/1556001650_5cbeb37229524.png!small)

## 五、结语

从近期Android端恶意应用的作恶手法来看，恶意开发者更多地从直接开发App应用转向开发SDK，向Android应用供应链的上游转移。通过提供恶意的SDK给应用开发者，恶意开发者可以复用这些应用的分发渠道，十分有效的扩大影响用户的范围。而在恶意SDK的类别方面，黑产从业者主要把精力放在用户无感知的广告刷量和网站刷量等方向，通过使用代码分离和动态代码加载技术，可以完全从云端下发实际执行的代码，控制用户设备作为“肉鸡”进行广告、网站刷量等黑产行为，具有很强的隐蔽性。

这类流量型黑产逐渐增多，不仅对手机用户造成了危害，同时也给移动端广告反作弊带来了很大的挑战，传统基于IP、曝光频率、点击率等表象数据形成的反作弊策略难以识别这种控制大量真实设备做’肉鸡’的刷量作弊，难以保障应用开发者和广告主的正当权益。

 ***本文作者：腾讯手机管家，转载请注明来自FreeBuf.COM**

