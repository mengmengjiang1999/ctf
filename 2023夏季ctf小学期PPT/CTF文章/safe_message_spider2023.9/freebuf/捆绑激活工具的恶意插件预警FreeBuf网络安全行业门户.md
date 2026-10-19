**近日，亚信安全截获一款恶意插件的安装包程序，该安装包程序通常与激活工具、绿色软件等捆绑在一起，一旦用户运行这些捆绑恶意插件的激活工具或者绿色软件，这些恶意的插件在用户不知情的情况下安装在浏览器中，劫持用户的浏览器。虽然目前没有发现通过此方法传播勒索病毒和挖矿病毒，但只要修改源代码，就可以轻易传播任意恶意软件。亚信安全将此类恶意插件命名为PUA.Win32.BangMai.AC。**

## 攻击流程

##
![](https://image.3001.net/images/20190613/1560419475_5d021c93b0c50.png!small)

## 详细分析

恶意插件安装包文件运行后，会在C:\Windows\Help\IBM目录释放恶意插件文件，其中包括“天馨气象”和“星驰天气助手”等插件。通过修改注册表键值的方式关闭UAC（User
Account Control）和设置自启动项。

![](https://image.3001.net/images/20190613/1560419492_5d021ca427efd.png!small)

![](https://image.3001.net/images/20190613/1560419504_5d021cb0d4656.png!small)

![](https://image.3001.net/images/20190613/1560419514_5d021cba2a4b8.png!small)

其中XCExtent.exe和TxExtent.exe分别对应“星驰天气助手”和“天馨气象”插件，他们会安装到Chrome浏览器的扩展程序中。

![](https://image.3001.net/images/20190613/1560419534_5d021cce56a89.png!small)

![](https://image.3001.net/images/20190613/1560419544_5d021cd866c8d.png!small)

通过逆向我们看到这个病毒在自己的工程里称为“流氓镜像快马”。恶意程序PDB路径，如下图所示：

![](https://image.3001.net/images/20190613/1560419564_5d021cec42c4c.png!small)

此病毒也同样会劫持IE浏览器，为其安装BHO插件：

![](https://image.3001.net/images/20190613/1560419578_5d021cfadad37.png!small)

![](https://image.3001.net/images/20190613/1560419588_5d021d0493776.png!small)

## Chrome插件分析

根据插件配置信息，该插件逻辑分为3个部分，包括config.js、backgroud.js和l.js脚本文件。其中config.js是该插件的配置信息，包括C&C服务器地址和channelID，通过我们不同的测试，该channelID是变化的，可能会根据其ID进行不同的恶意行为：

![](https://image.3001.net/images/20190613/1560419618_5d021d2217181.png!small)

Config.js代码内容

l.js是Content_Scripts脚本，Content_Scripts是谷歌浏览器Chrome扩展程序开发中常用到功能，该恶意插件可以通过此脚本截获所有的网络请求，在每个响应后添加远程恶意JS脚本：

![](https://image.3001.net/images/20190613/1560419647_5d021d3fad676.png!small)

![](https://image.3001.net/images/20190613/1560419657_5d021d4973596.png!small)

l.js代码内容

## IE插件分析

此恶意软件也会劫持IE浏览器，其中存放在C:\Windows\Help\IBM文件夹下的txweather_x64.dll和txweather_x86.dll是用于劫持IE浏览器的BHO插件。BHO插件是IE浏览器辅助插件,可对IE浏览器的界面和访问内容进行修改操作。

![](https://image.3001.net/images/20190613/1560419705_5d021d79538b7.png!small)

只要安装上此插件，所有使用IE访问的页面都会被插入恶意的JS脚本，通过访问[www[.]xxfqxxx.com/xxxx](http://www.591fq.com/xxxx)实现，目前该域名已经无法访问。

![](https://image.3001.net/images/20190613/1560419728_5d021d9022c67.png!small)

IE访问页面插入的恶意脚本内容

## 风险分析

通过安装恶意的插件劫持浏览器，可能会存在如下风险：

> 安装恶意软件，如勒索病毒，挖矿病毒等（风险性较高）；
>
> 进行恶意推广；
>
> 在访问的网页中插入悬浮广告；
>
> 在浏览器上安装软件时可能会被替换成插件提供的安装包。

## 解决方案

> 安装正版软件，不使用激活工具等程序；
>
> 从正规网站下载软件；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 打开系统自动更新，并检测更新进行安装。

 ***本文作者：亚信安全，转载请注明来自FreeBuf.COM**

