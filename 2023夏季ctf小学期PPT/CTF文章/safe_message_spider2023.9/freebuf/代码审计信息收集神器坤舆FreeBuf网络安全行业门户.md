## 前言

本文是作者从github上下载下来对”坤舆”进行分析，有不足的地方欢迎大家在评论区交流。坤舆集成了Seebug漏洞库和ZoomEye的搜索功能。

## 下载地址

> 项目地址：<https://github.com/knownsec/Kunyu>  
> 百度网盘：  
> 链接：<https://pan.baidu.com/s/1mRGTatOOeq3VkVU-MubfKA>  
> 提取码：4fng

## 工具介绍

Kunyu (坤舆)，名字取自 <坤舆万国全图>
，测绘实际上是一个地理信息相关的专业学科，针对海里的、陆地的、天上的地理信息进行盘点。同样应用于网络空间，发现未知、脆弱的资产也是如此，更像是一张网络空间地图，用来全面描述和展示网络空间资产、网络空间各要素及要素之间关系，以及网络空间和现实空间的映射关系。所以我认为“坤舆”还是比较贴合这个概念的。  
Kunyu(坤舆)，旨在让企业资产收集更高效，使更多安全相关从业者了解、使用网络空间测绘技术

## 工具分析

当你在使用工具的时候大致会执行以下步骤：

当前文件：kunyu/console.py  
如果没有zoomeye的apikey和login的token值，那么就会出现报错，如果有就会执行  
KunyuInterpreter里的main函数，可以从导包中看到，KunyuInterpreter模块在kunyu.core.console包中

![](https://image.3001.net/images/20210903/1630629236_61316d740a18567a91505.png!small)

当前文件：kunyu/core/console.py  
虽然图一指向的是main函数，但是会先执行 **init** 这个魔方函数  
super是为了子类继承父类之后为了调用父类方法

![](https://image.3001.net/images/20210903/1630629261_61316d8db853b02919d70.png!small)

当前文件：kunyu/core/console.py  
找到父类，可以看到父类的 **init**
魔方函数，会用eval去执行ZoomEye，调用里面的Command_info参数值来赋值给complet，setup函数里的意思是执行自动补齐，创建目录……等函数

![](https://image.3001.net/images/20210903/1630629291_61316dab3820444cd3706.png!small)![](https://image.3001.net/images/20210903/1630629299_61316db39b7b208632318.png!small)

当前文件：kunyu/core/console.py  
将ZoomEye的help参数内容打印出来，附上help内容

![](https://image.3001.net/images/20210903/1630629330_61316dd29abb2ed1d1ef9.png!small)

![](https://image.3001.net/images/20210903/1630629343_61316ddfae5966f40a794.png!small)当前文件：kunyu/core/console.py  
执行父类start函数，赋值参数，利用auxiliary函数判断输入命令的信息或者有无命令情况就跳出循环，如果有第二张图命令的话就会去执行相对应的函数，分别对应清楚、设置、导出的功能。那如果输入的不是这些，就会去执行get_command_handler函数

![](https://image.3001.net/images/20210903/1630629418_61316e2a14271ef44b867.png!small)![](https://image.3001.net/images/20210903/1630629425_61316e31be332a7048cfe.png!small)当前文件：kunyu/core/console.py  
去执行ZoomEye里的函数，这里的getattr函数只是简单定义了一下使用方法，最终还是到ZoomEye里去，如果没有识别到对应函数，就会报错。

![](https://image.3001.net/images/20210903/1630629449_61316e49404676430167f.png!small)当前文件：kunyu/core/zoomeye.py  
这边就拿searchhost来举例子，按第六步来讲拼接后到ZoomEye中对应的函数是command_searchhost，发现会去调用
__command_search函数，这边对应的search就是输入的命令

![](https://image.3001.net/images/20210903/1630629475_61316e63862f3e86d51bd.png!small)当前文件：kunyu/core/zoomeye.py  
一开始设置的是对表格的初始化，在接下来，就是判断输入的东西，当然你搜索host的时候，会接着执行下一步command_search，它把command_search的默认type值设为host，所以这边return过去就没有带上第二个参数

![](https://image.3001.net/images/20210903/1630629501_61316e7d81c35da7cd1dc.png!small)当前文件：kunyu/core/zoomeye.py  
可以看到会先到_dork_search函数去执行

![](https://image.3001.net/images/20210903/1630629540_61316ea45bfd0226b707b.png!small)这个dorksearch函数是在ZoomeyeSearch父类下的，这个父类下有很多魔方函数，会先执行
**init** 、__call，其中__call这个函数会跳到__request函数去，也是在同个父类下

![](https://image.3001.net/images/20210903/1630629568_61316ec0ae482b0ac0465.png!small)可以看到用if语句去尝试用get、post带参请求网站

![](https://image.3001.net/images/20210903/1630629664_61316f2080380c89ffa33.png!small)回到_dork_search函数中，可以看到，执行完成后，会将数据保存到excel表中，对应的是以下函数，从导入模块中可以看到，这个函数是从kunyu.lib.export中的函数

![](https://image.3001.net/images/20210903/1630629694_61316f3e30353ec89fd67.png!small)![](https://image.3001.net/images/20210903/1630629701_61316f45d2bbbcc6afc94.png!small)当前文件：kunyu/lib/export.py  
最后利用file_name = excel.save(os.path.join(setting.OUTPUT_PATH,
__time))保存到对应的路径。这边的path路径对应的是第一张图上的批注，至此，完整的一个使用分析就结束了。

![](https://image.3001.net/images/20210903/1630629722_61316f5ac970db150b023.png!small)有的人就会问了，一开始说好的seebug哪去了  
当前文件：kunyu/core/zoomeye.py  
把要搜索的东西放到Seebug的search函数去执行，可以看到seebug是从kunyu.core.seebug中导入的

![](https://image.3001.net/images/20210903/1630629751_61316f77da1195f6159a0.png!small)![](https://image.3001.net/images/20210903/1630629760_61316f80a918b2255b70d.png!small)当前文件：kunyu/core/seebug.py  
初始化执行__get_login函数，如果有登陆的话，就会获得token，往headers字典中，添加token信息，然后就去seebug漏洞库中搜索想搜索的东西。

![](https://image.3001.net/images/20210903/1630629784_61316f98a286a21d924e2.png!small)

## 使用演示

输入命令kunyu console 进入kunyu图形化界面

![](https://image.3001.net/images/20210903/1630629917_6131701d3d5af451645e8.png!small)接下来就能看到命令提示栏，还有个立体化的log，这个命令提示栏帮助我们更好的输入想执行的命令

![](https://image.3001.net/images/20210903/1630629939_61317033e5d01172e307f.png!small)

以searchhost命令演示，上面分析讲到可以输入web网址、host、domain；以www.baidu.com 为例进行演示

![](https://image.3001.net/images/20210903/1630629997_6131706d13d21cf1902e7.png!small)一页最多可以展示20个信息，可以用show命令查看常规设置,可以用命令set
page = xx 来设置想要获得数据的页数

![](https://image.3001.net/images/20210903/1630630047_6131709ff3f6957c94123.png!small)分析中谈到，可以生成excel表，是的，它会自动生成在目录下，可以利用Exportpath来查询保存的路径

![](https://image.3001.net/images/20210903/1630630074_613170bad0b9985cc5b65.png!small)

## 总结

对坤舆分析了一波后，对我日后的工具开发和审计有蛮大帮(信)助(心)，我可不想做个脚本小子，不过能白嫖还是白嫖好一点。  
工具的实用性和展示性效果感觉很nice，各位师傅快去下来玩一玩呀！

