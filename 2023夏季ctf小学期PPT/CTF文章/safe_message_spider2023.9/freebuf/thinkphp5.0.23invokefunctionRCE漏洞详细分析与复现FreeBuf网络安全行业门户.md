本文为thinkphp5.0.23 invokefunction 漏洞 RCE 详细分析与复现。

## 复现

去官网下载thinkphp5.0.23

漏洞payload
?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=whoami  
本地搭建环境实测  
![](https://image.3001.net/images/20211107/1636246699_618724ab97b1cb65a797f.png!small)XDEBUG_SESSION_START是调试用的，不用管  
s参数是thinkphp的一种路由形式  
http://xxx.com/index.php?s=/module/controller/func/args/value
(func也叫action，就是类里的方法名)

举个小例子  
例如s=index/index/getname/name/z3  
![](https://image.3001.net/images/20211107/1636246700_618724ac7cbec0f056986.png!small)![](https://image.3001.net/images/20211107/1636246701_618724ad2277b2551cf3f.png!small)

## 漏洞分析

现在来分析下payload中的s参数  
s=index/think\app/invokefunction  
module 是 index，对应的是index文件夹  
controller 是 think\app，对应的是？？？  
func 是 invokefunction，对应的是 think\app的invokefunction方法

上面例子中s=index/index/getname/name/z3，是application/index/controller/Index.php文件中的getname方法，但是think\app是什么，controller文件夹下找不到

那只能调试一下，看thinkphp是如何解析路由的  
从index.php开始看

    
    
    index.php->/../thinkphp/start.php->/base.php
    

然后执行了App::run()->send();

先看App::run()方法  
![](https://image.3001.net/images/20211107/1636246701_618724ada81d3d85f98fc.png!small)看注释是一些框架初始化的操作，继续往下看  
![](https://image.3001.net/images/20211107/1636246702_618724ae3407b39f325b9.png!small)是处理路由的操作  
![](https://image.3001.net/images/20211107/1636246702_618724aea1d9c42c108c9.png!small)调试可以看出，routeCheck将路由解析了  
进去看一下  
![](https://image.3001.net/images/20211107/1636246703_618724af644fa1526c691.png!small)跟进parseUrl  
调用了parseUrlPath方法，使用trim，根据/ 进行分割，得到数组  
![](https://image.3001.net/images/20211107/1636246703_618724afefc6feb26650e.png!small)

然后就是对路由的解析了  
![](https://image.3001.net/images/20211107/1636246704_618724b082915ecb34dfa.png!small)path的第一个元素定义为module  
![](https://image.3001.net/images/20211107/1636246705_618724b15784a1ea9eec7.png!small)第二第三元素定义为controller和action,然后返回  
又回到了App.php的run方法，知道了controller就是think\php，但还不知道怎么调用的think\php  
继续看  
![](https://image.3001.net/images/20211107/1636246706_618724b231a671ca2555f.png!small)调用了exec  
![](https://image.3001.net/images/20211107/1636246708_618724b4acb450f4c046a.png!small)module方法执行了命令，跟进  
![](https://image.3001.net/images/20211107/1636246709_618724b54b5ae40f2b0e2.png!small)创建了request对象  
![](https://image.3001.net/images/20211107/1636246709_618724b5c8290e70fb7f5.png!small)设置request的module  
![](https://image.3001.net/images/20211107/1636246710_618724b65f63ce59f065d.png!small)设置moduel路径

下面重点又来了，解析controller ：think\app  
![](https://image.3001.net/images/20211107/1636246710_618724b6e94a6ad63166f.png!small)

一番操作后，controller还是think\app，

Loader::controller成功解析了think\php  
注意看$instance是think\App类型对象  
![](https://image.3001.net/images/20211107/1636246711_618724b7acd2796cc33fd.png!small)

App.php里果然有invokeFunction方法，所以继续调试，应该就是通过反射，获取到call_user_func_array方法的反射对象，传参调用

再看下payload:

    
    
    &function=call_user_func_array
    &vars[0]=system
    &vars[1][]=whoami
    

这里传入的函数是call_user_func_array  
参数是[system,[whoami]]  
即$reflect->invokeArgs([system,[whoami]])  
注意这里$reflect->invokeArgs方法参数是一个数组，而call_user_func_array第一个参数是函数名，第二个参数也是数组，这就可以理解为什么要这样构造了&vars[0]=system，&vars[1][]=whoami  
![](https://image.3001.net/images/20211107/1636246712_618724b86b2fb337c3c73.png!small)

还有个问题没解决Loader::controller怎么解析的think\php  
跟进Loader::controller方法  
![](https://image.3001.net/images/20211107/1636246713_618724b94b87edd6c4fe1.png!small)跟进ReflectionClass  
通过ReflectionClass方法创建了think\App对象  
![](https://image.3001.net/images/20211107/1636246713_618724b9c27ee32164085.png!small)

试一下正常调用

    
    
    s=index/index/getname/name/z3
    

![](https://image.3001.net/images/20211107/1636246714_618724ba6be0e8e498cf5.png!small)controller
应该是index，被解析为了app\index\controller\Index  
那为什么think\app没有被解析为app\index\controller\think\app呢？

再重新调一遍，在Loader::controller中，index被解析为了app\index\controller\Index  
![](https://image.3001.net/images/20211107/1636246715_618724bb118fefc805299.png!small)

继续跟进getModuleAndClass方法  
![](https://image.3001.net/images/20211107/1636246715_618724bb8cb846b2f30a1.png!small)问题就在这里，如果匹配到了\，$class就原封不动，还是think\app。如果没匹配到\，进入parseClass方法  
将class的路径补全为app\index\controller\Index

![](https://image.3001.net/images/20211107/1636246716_618724bc1f9d05604e282.png!small)

## 总结

所以现在知道了 **thinkphp5.0.23 invokeFunction漏洞的原理**

>
> thinkphp在解析controller时，如果有\字符，就原封不动的用它来创建对象，所以将controller设置为think\php，就会创建App对象
>
> 而App对象里有invokefunction方法，所以action设置为invokefunction
>
> invokefunction参数是调用的函数名和参数，所以可以执行任意方法了

本质就是可以根据项目代码中的class创建对象，并调用对象的方法，并且可控参数。

## 思考

实战中遇到的几个问题。例如module名不确定，可能是index、admin、home等等  
如果module名不对，就会报错  
![](https://image.3001.net/images/20211107/1636246717_618724bda8982645ba392.png!small)原因是module初始化时，会检查application文件夹下有没有module的文件名，如果不存在，就会抛出异常  
![](https://image.3001.net/images/20211107/1636246718_618724be15a4b16e37591.png!small)解决办法

> 暴力尝试
>
>
> 在thinkphp5.0之前版本可以使用?m=index&c=index&a=index方式指定module,controller,action，那么?c=index&a=index，不指定m，就会使用默认module

## 如何修复

看5.0.24  
![](https://image.3001.net/images/20211107/1636246718_618724be885efaa14adf0.png!small)修复方法很直截了当，用正则做了个过滤，不会绕。

