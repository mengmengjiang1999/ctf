  

## 1、影响范围

Yii2 < 2.0.38

## 2、环境搭建

影响范围：Yii2 < 2.0.38

所以我们下载2.0.37即可

https://github.com/yiisoft/yii2/releases/tag/2.0.37

之后直接在根目录下执行php yii
serve开启服务，然后修改下配置文件config/web.php；给cookieValidationKey修改一个任意值，不然会报错。

![](https://image.3001.net/images/20210109/1610177582_5ff95c2eb09fd0f265cab.png!small)

## 3、PHP（反）序列化有关的魔法函数

环境搭建好了，就先了解下魔法函数，方便后面利用链的理解。

> __construct()：当对象创建(new)时会自动调用。但在unserialize()时是不会自动调用的。
>
> __destruct()：当对象被销毁时会自动调用。
>
> __call()：是在对象上下文中调用不可访问的方法时触发
>
> __callStatic()：是在静态上下文中调用不可访问的方法时触发。
>
> __get()：用于从不可访问的属性读取数据。
>
> __set()：用于将数据写入不可访问的属性。
>
> __isset()：在不可访问的属性上调用isset()或empty()触发。
>
> __unset()：在不可访问的属性上使用unset()时触发。
>
> __sleep():在执行序列化函数serialize()时执行。
>
> __wakeup():在执行反序列化函数unserialize()时执行。
>
> __toString():允许一个类决定如何处理像一个字符串时它将如何反应。
>
> __invoke():脚本尝试将对象调用为函数时，调用__invoke()方法。

常用魔法函数图示，更加直观理解：

![](https://image.3001.net/images/20210109/1610177252_5ff95ae4148cbc3fc3bdd.png!small)

## 4、漏洞分析与复现

### 分析:

从大佬们的EXP入手分析

![](https://image.3001.net/images/20210109/1610177290_5ff95b0acdd9d54a4ee8f.png!small)

如图所示，EXP执行顺序为①②③最后RCE

> ①：new了一个BatchQueryResult对象，导致执行了BatchQueryResult类下的__construct函数
>
> ②：new了一个Generator对象，导致执行了Generator类下的__construct函数
>
> ③：new了一个CreateAction对象，导致执行了CreateAction类下的__construct
>
> 最后因为CreateAction类中run()方法中的checkAccess和id的值是可控的，导致了RCE。

根据EXP中的类，我们跟进每个文件去分析。

先new的BatchQueryResult，所以BatchQueryResult.php就是整个POP链的起点。

![](https://image.3001.net/images/20210109/1610177352_5ff95b4895e7380ffe434.png!small)

1、BatchQueryResult类中__destruct调了reset()方法，然后可以看到reset()方法中的$this->dataReader是可控的，这里的$this->dataReader->close()可以利用魔法函数__call（前面说了，如果执行不存在的方法就会调用call方法），这就说明在EXP的第二个类Generator存在可利用的__call方法，继续跟进Generator.php。

![](https://image.3001.net/images/20210109/1610177366_5ff95b567da7c34102c05.png!small)

![](https://image.3001.net/images/20210109/1610177373_5ff95b5de6b28a5abd119.png!small)

2、Generator类中看到__call调用了format方法,format又调用了call_user_func_array,但是$formatter和arguments都是不可控的；继续往下走，$formatter传入了$this->getFormatter,在这个方法中，$this->formatters是我们可控的，也就是说getFormatter方法的返回值是可控的,call_user_func_array这个函数的第一个参数可控，第二个参数为空;那么EXP中的下一步代入了一个无参数的方法去RCE；我们去查看下EXP的最后一步，CreateActiion类中的run()方法，跟进CreateAction.php文件。

![](https://image.3001.net/images/20210109/1610177387_5ff95b6b2338f44a4bec2.png!small)

3、CreateAction类中，run()很明显可以看到$this->checkAccess以及$this->id都可控，利用链就出来了

> yii\db\BatchQueryResult::__destruct() -> Faker\Generator::__call() ->
> yii\rest\CreateAction.php::run()

### 复现:

复现的第一步，先自己添加一个反序列化的入口，在controllers目录下新建一个存在反序列化的Action，TestController.php

![](https://image.3001.net/images/20210109/1610177413_5ff95b854ceaff647513f.png!small)

![](https://image.3001.net/images/20210109/1610177423_5ff95b8f8b8b46116a20d.png!small)

入口建立成功后就可以去执行EXP了，执行EXP后会得到Base64编码后的序列化字符

![](https://image.3001.net/images/20210109/1610177438_5ff95b9ea4ae33efc4e65.png!small)

将攻击代码代入URL即可成功RCE

![](https://image.3001.net/images/20210109/1610177447_5ff95ba7a694e22817857.png!small)

## 5、修复建议

升级到2.0.38之后的版本即可成功修复此漏洞。

![](https://image.3001.net/images/20210109/1610177460_5ff95bb4cbafe15018457.png!small)

## 6、参考链接

https://xz.aliyun.com/t/8307

https://www.anquanke.com/post/id/86452

