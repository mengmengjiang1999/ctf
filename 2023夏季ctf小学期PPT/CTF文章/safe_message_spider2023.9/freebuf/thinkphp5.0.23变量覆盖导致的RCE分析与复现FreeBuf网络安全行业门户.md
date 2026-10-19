# thinkphp5.0.23变量覆盖导致的RCE分析与复现

## 复现

payload  
http://tptest.cc/?XDEBUG_SESSION_START=17774&s=captcha  
POST：_method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=whoami  
![](https://image.3001.net/images/20211206/1638768927_61ada11f397d2f1a9ec43.png)

## 漏洞分析

根据上一篇 invokefunction 的复现，了解了thinkphp加载module，controller,action的过程了  
先看看是如何解析s=captcha的  
还是在App.php的run方法中，routeCheck这里加断点，发现已经将captcha解析了（注意到，这次的type是method，上一篇
invokefunction 的复现中，type是module）  
![](https://image.3001.net/images/20211206/1638768928_61ada120e3f6c57c6799f.png)

继续跟进routeCheck  
最后跟进了Route.php  
路由是个全局静态变量  
![](https://image.3001.net/images/20211206/1638768929_61ada121e809c7e348096.png)  
调试跟进来的时候captcha的路由已经存在了，应该是之前加载配置文件，读取路由配置的时候加载的  
![](https://image.3001.net/images/20211206/1638768931_61ada1232ff84e89bf663.png)  
全局搜索CaptchaController，找到了，在/vendor/topthink/think-captcha/src/helper.php里注册了路由  
![](https://image.3001.net/images/20211206/1638768932_61ada1248f8d143cb8638.png)  
好吧，现在知道了captcha路由的解析过程

现在看下\think\captcha\CaptchaController的index方法  
![](https://image.3001.net/images/20211206/1638768933_61ada12584ac474a80174.png)  
加断点，断不到，说明命令执行和这个函数无关  
调试发现这里出现了异常  
![](https://image.3001.net/images/20211206/1638768934_61ada126b61a884065ce4.png)  
第三句Log抛出异常，而且这个rce看起来和header无关，所以重点看param方法  
![](https://image.3001.net/images/20211206/1638768935_61ada127c7a1641701e40.png)

调试时发现REQUEST_METHOD已经被改了，正常应该是get或post  
![](https://image.3001.net/images/20211206/1638768936_61ada128ef7811cec641e.png)  
再重新来一遍，发现了问题，  
![](https://image.3001.net/images/20211206/1638768938_61ada12a61b11a4bc8b28.png)  
![](https://image.3001.net/images/20211206/1638768939_61ada12b58a080637e4e4.png)  
如果传入_method参数，就会调用把_method当做函数执行，POST参数作为函数参数  
payload传入的是_method=__construct  
看一下__construct是怎么命令执行的  
![](https://image.3001.net/images/20211206/1638768940_61ada12c62d4ba064c77a.png)

看这个foreach，，，做了一波变量覆盖  
一波操作后，  
filter = ['system'],method='get',server['REQUEST_METHOD']=whoami  
![](https://image.3001.net/images/20211206/1638768941_61ada12d5ddc63ce3cb25.png)  
Request.php中搜索REQUEST_METHOD，  
发现这个函数会导致命令执行  
![](https://image.3001.net/images/20211206/1638768942_61ada12e74265eda5e993.png)  
接着跟进server->input  
这里getFilter拿到的是假过滤器system  
![](https://image.3001.net/images/20211206/1638768943_61ada12f944b55365161f.png)  
接着跟进filterValue，豁然开朗  
![](https://image.3001.net/images/20211206/1638768944_61ada130c15b1a13cd5f6.png)

## 总结

解析路由时一定会调用method方法，就一定可以造成变量覆盖  
命令执行需要调用server方法，调用server方法前提是调用method(true)  
而使用method(true)的只有param方法，  
所以总结，只要可以调用param方法就可以构造命令执行payload

## 思考

为什么要这样构造payload?  
get请求的s=captcha，，去掉后同样可以执行，有回显，，，不知道网上的payload为什么要加s=captcha

为什么_method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=whoami  
_method是为了调用__construct函数  
对filter进行变量覆盖，而server[REQUEST_METHOD]是filter的参数，（猜测thinkphp本意是用_method参数设置一个自定义的请求类型，通过REQUEST_METHOD对请求类型过滤）  
那method=get有什么用呢，  
去掉试一下，  
实践证明method=get没用

这个漏洞使用有什么限制吗？  
调试时发现漏洞在这里触发，所以需要开启debug？  
![](https://image.3001.net/images/20211206/1638768945_61ada131ef8fcc5ef6f4e.png)  
关闭debug试一下  
果然，关闭debug复现失败，为什么？理论上只要调用了Request的param方法就可以实现rce啊

所以全局搜索一下param函数，搜索到4个，一个在debug中，两个在exec函数中，另一个在jsonp  
看下exec函数  
可惜$dispatch['type']值为module,  
![](https://image.3001.net/images/20211206/1638768947_61ada13329fec1cede17e.png)  
为了证明猜想，加上一句  
![](https://image.3001.net/images/20211206/1638768948_61ada1347e9d514098205.png)  
RCE成功，看来推理正确

controller和method都用了Request::instance()->param()，只要想办法触发，就可以实现rce  
突然想起来，之前调试时，captcha解析时的类型好像是method，，现在是module，，不会是因为我去掉了那俩参数吧，，，，  
这个类型由什么控制？  
在parseRule中发现  
![](https://image.3001.net/images/20211206/1638768949_61ada135b0d4507e62d76.png)  
如图：如果$route有\，类型就为method，有@就是controller

解析时，result有两条路，第二条路是写死的module类型，只能走第一条路，才有希望到达上图的parseRule函数  
![](https://image.3001.net/images/20211206/1638768950_61ada136ec5b42732ecd3.png)  
而走第一条路，需要匹配到一条路由，，但是thinkphp默认只有两条如图  
![](https://image.3001.net/images/20211206/1638768968_61ada14821d9826b029e9.png)  
传参s=captcha试一下  
![](https://image.3001.net/images/20211206/1638768969_61ada1495168eaaa7f152.png)  
![](https://image.3001.net/images/20211206/1638768970_61ada14a45b18ba89da7f.png)  
可以看见路由规则需要根据method筛选，由于我们需要post传参，实现变量覆盖，而captcha/[:id]又是get类型路由，所以匹配不到  
但是！注意看，根据method筛选路由语句的上面，调用了method，，，回一下上面的总结"解析路由时一定会调用method方法，就一定可以造成变量覆盖"，  
所以post参数加个method=get  
就可以完美匹配captcha路由了，也就可以调用param方法，造成rce了

所以：这里另一条利用链，不需要开启debug

还有一个jsonp的，有rce希望，，，太累了，明天再看

## 再总结

通过变量覆盖实现rce有两种方法

  1. 需要开启debug模式  
直接post下面这条  
_method=__construct&filter[]=system&server[REQUEST_METHOD]=whoami

  2. 不需要开启debug模式，但是需要完整版，  
http://tptest.cc?s=captcha  
[POST]  
_method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=whoami

thinkphp5系列大概就这两个rce了，在这两个基础上，知道了原理，可以用一些绕过方法，进一步攻击利用等

## 感悟

调试完debug模式rce后，，还很不解captcha，method=get，，多此一举？  
是我矮了，目光狭隘了

## 如何修复

看5.0.24如何修复  
![](https://image.3001.net/images/20211206/1638768971_61ada14b48d527b10556e.png)  
和5.0.23不同的是，这里routeCheck返回的type是module  
想一下之前的总结，命令执行<-调用server<-调用method(true)<-调用param()，而调用param条件有:1. 开启debug 2.
type是method或controller 3. jsonp  
之前我们通过captcha路由，构造出了payload使type为method，满足第二个条件，但5.0.24中使用相同payload，type还是module

调试一下看问题出在哪了  
再回一下之前的总结  
漏洞利用第一步，method函数导致变量覆盖，第二步，调用param导致命令执行  
先看下method函数有没有变动

果然，，method这里做了白名单过滤，这就没法绕了  
![](https://image.3001.net/images/20211206/1638768972_61ada14c5c2189959fd78.png)

