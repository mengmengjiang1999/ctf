## 0x00 漏洞概述

这是一个ExpressJS
web框架+squirrelly模板组件引发的漏洞，截止到目前为止该漏洞还没有修复。攻击者可以利用这个漏洞远程在服务端执行js代码。

该漏洞是由于squirrelly模板组件的内部配置变量错误的被外部参数覆盖造成的。后续的内容均基于ExpressJS V4.16.1和Squirrelly
V8.0.8。

## 0x01 漏洞成因

要知道漏洞成因首选需要了解ExpressJS和Squirrelly相关的一些特性。首先ExpressJS提供了通过模板和模板参数生成/渲染页面的API——render('XX模板',
{k1:v1,k2:v2,……})，然后由Squirrelly提供从模板根据配置和用户输入生成/渲染页面的功能。该功能大致步骤如下：

1、定义模板：index.squirrelly，包含最简单的内容<html>{{it.title}}</html>

2、当用户发起请求时，在handleCache中首先获取模板文件的内容

3、调用compile传入模板文件内容和用户输入&配置

4、调用compileToString函数生成拼装页面的js代码并组成匿名函数

5、调用compileScope函数生成替换模板中占位符的js代码

6、返回到handleCache函数，返回值为生成/渲染页面的匿名函数的js代码

7、调用匿名函数生成/渲染页面

漏洞的引入位于第5步，代码如下图红线所标：

![1622461514_60b4cc4a441fb6ebd9169.png!small?1622461514114](https://image.3001.net/images/20210531/1622461514_60b4cc4a441fb6ebd9169.png!small?1622461514114)

红圈中两个变量都是本地的配置变量，但是却可以通过url中的参数来覆盖这两个变量的值，比如url参数：“/?autoEscape=&defaultFilter=b”可以使env.autoEscape的值变为""，使env.defaultFilter的值变为“b”。在不做任何特殊配置的情况下env.autoEscape的值为：“true”，env.defaultFilter的值为：“false”，因此上述代码运行完成后returnStr的值大致如下："tR+='<html>';tR+=c.l('F','e')(it.Express);tR+='</html>';"。

分析上述代码注入点位于：“content = "c.l('F','" + env.defaultFilter + "')(" + content +
')';”，可以通过设置env.defaultFilter的值来注入希望执行的代码。下图是到达缺陷所在函数的调用栈，最下方的(anonymous)函数即我们编写的处理http-get请求的入口函数：

![1622596352_60b6db00ac73cd4b5a3ed.png!small?1622596352545](https://image.3001.net/images/20210602/1622596352_60b6db00ac73cd4b5a3ed.png!small?1622596352545)

## 0x02 环境搭建

在知道漏洞成因后我们可以通过搭建环境来完成验证这个漏洞，环境使用Win7，主要步骤如下：

1、安装NodeJS和npm：请使用百度指导，NodeJS安装时会同步安装npm注意：NodeJS的V14版本开始不再支持Win7，Win7需要选择历史版本。

2、安装ExpressJS：使用npm install express安装。

3、安装Squirrelly：使用npm install squirrelly安装。

4、使用ExpressJS生成默认的web工程：使用express xxProject生成默认的web工程。

5、安装JS调试工具：下载Chrome插件：NIM(Node.js
调试管理工具)，需要修炼梯云纵方可完成，未修练过也没关系，不影响漏洞复现，仅无法更清楚的观察具体的代码执行过程。

通过上述五步即可完成漏洞复现所需要的环境，搭建完成的xxProject的文件目录结构如下图所示：

![1622536173_60b5efedcbbe9b90a171c.png!small?1622536173165](https://image.3001.net/images/20210601/1622536173_60b5efedcbbe9b90a171c.png!small?1622536173165)

注意：package.json中squirrelly的版本需要是8.0.8

## 0x03 漏洞复现

在实际动手前需要首先修改上一步生成的web工程，使其使用squirrelly模板，具体步骤如下：

1、修改app.js文件中的模板类型，将"jade"修改为"squirrelly"，修改的原始代码如下：

![1622535760_60b5ee501166adf39911d.png!small?1622535758662](https://image.3001.net/images/20210601/1622535760_60b5ee501166adf39911d.png!small?1622535758662)

2、删除jade的模板，jade的模板位于views目录下，如下图所示：

![1622539038_60b5fb1e047e635b1bf29.png!small?1622539037802](https://image.3001.net/images/20210601/1622539038_60b5fb1e047e635b1bf29.png!small?1622539037802)

3、在views目录下新建squirrelly模板，文件名为index.squirrelly，内容如下图所示：

![1622545158_60b6130622677720cc153.png!small?1622545157970](https://image.3001.net/images/20210601/1622545158_60b6130622677720cc153.png!small?1622545157970)

4、由于其它页面都被删除了，因此需要删除app.js对于这些页面的引用，注释后app.js文件中代码如下图所示：

![1622545389_60b613ed1b86b555ffef7.png!small?1622545388648](https://image.3001.net/images/20210601/1622545389_60b613ed1b86b555ffef7.png!small?1622545388648)

5、最后修改响应根路径请求的文件：index.js，具体修改下图中选中的代码：

![1622546709_60b619155ef85d9a1a7cd.png!small?1622546709725](https://image.3001.net/images/20210601/1622546709_60b619155ef85d9a1a7cd.png!small?1622546709725)

6、使用npm
start启动服务，然后构造payload尝试复现漏洞：http://localhost:3000/?Express=aaaa&autoEscape=&defaultFilter=e');console.log('hackme');//。此时compileScope函数中引入缺陷的代码如下：

if (env.defaultFilter) {

content = "c.l('F','" + env.defaultFilter + "')(" + content + ')';  
}

此时env.defaultFilter=

因此context的表达式应该是"c.l('F','" + “e');console.log('hackme');//” + "')(" + content
+ ')';

最终context的值为"c.l('F','e');console.log('hackme');//
')(it.Express)”，并在后续的代码生成中变成匿名函数的函数体：var
tR='';tR+='<html>';tR+=c.l('F','e');console.log('hackme');//')(it.Express);tR+='</html>';if(cb){cb(null,tR)}
return tR

可以看到payload通过"e')"闭合了前面的函数c.l，然后接着注入了需要执行的js代码console.log('hackme')，最后用"//"注释符将后续会引起语法问题的代码注释掉，以此完成了代码的注入。

注意：payload中env.autoEscape设置为“”，是为了不走进如下分支而影响代码运行：

![1622598470_60b6e34682785620dc3cf.png!small?1622598470320](https://image.3001.net/images/20210602/1622598470_60b6e34682785620dc3cf.png!small?1622598470320)

7、继续运行代码返回到tryHandleCache中的handleCache(options)(data, options,
cb);代码时handleCache(options)返回的是一个匿名函数，此时会继续执行anonymous(data,options,cb)，其中匿名函数的函数体为之前生成的代码：

"var
tR='';tR+='<html>';tR+=c.l('F','e');console.log('hackme');//')(it.Express);tR+='</html>';if(cb){cb(null,tR)}
return
tR"，依次执行代码到console.log('hackme');时就会在后台出现一行打印，标志着代码注入成功，如下图，至此整个漏洞的复现完成：

![1622549015_60b622175464dbfa1e0e1.png!small?1622549014791](https://image.3001.net/images/20210601/1622549015_60b622175464dbfa1e0e1.png!small?1622549014791)

注意：此时由于生成的页面不正确，因此在浏览器上是不会显示任何内容的，读者可以尝试构造payload使页面正常显示同时注入命令。

## 0x04 可能受影响的项目

分析github上100星以上的项目，共有380个项目使用了squirrelly组件，其中有42个项目使用了存在漏洞的8.0.8版本，具体的项目清单如下，有使用的TX可以自查一下：

项目名称| 项目url  
---|---  
open-olive/vscode-loop-development-kit| https://github.com/open-olive/vscode-loop-development-kit  
mizchi/uniroll| https://github.com/mizchi/uniroll  
reissmatt/risen-one-mission-platform| https://github.com/reissmatt/risen-one-mission-platform  
rpenco/light-webhook| https://github.com/rpenco/light-webhook  
JuanFdS/scriptBolaMagica| https://github.com/JuanFdS/scriptBolaMagica  
xnite/kittencore| https://github.com/xnite/kittencore  
adamuchi/login-with-demo| https://github.com/adamuchi/login-with-demo  
Berzok/Verena_Codex| https://github.com/Berzok/Verena_Codex  
diamondv5/SE-nonoffical| https://github.com/diamondv5/SE-nonoffical  
sitevision/sitevision-apps| https://github.com/sitevision/sitevision-apps  
abyrvalg/pleh4| https://github.com/abyrvalg/pleh4  
Riscue/drone-tool-settings| https://github.com/Riscue/drone-tool-settings  
reissmatt/risen-one-mission-platform| https://github.com/reissmatt/risen-one-mission-platform  
ZohaibArshad12/muze-beta| https://github.com/ZohaibArshad12/muze-beta  
HieuKma/squirrelly-template-11| https://github.com/HieuKma/squirrelly-template-11  
mcoop320/hls-media-server| https://github.com/mcoop320/hls-media-server  
yummyweb/neuron-js| https://github.com/yummyweb/neuron-js  
donaldskip326/gauzy1| https://github.com/donaldskip326/gauzy1  
HieuKma/squirrelly-template-10| https://github.com/HieuKma/squirrelly-template-10  
shuvalov-mdb/xstate-cpp-generator| https://github.com/shuvalov-mdb/xstate-cpp-generator  
googleapis/google-cloudevents-python| https://github.com/googleapis/google-cloudevents-python  
googleapis/google-cloudevents-python| https://github.com/googleapis/google-cloudevents-python  
NgoDucPhu/squirrelly-template| https://github.com/NgoDucPhu/squirrelly-template  
kimha0/clone-you/*这都敏感词*/tube| https://github.com/kimha0/clone-you/*这都敏感词*/tube  
nervetattoo/simple-thermostat| https://github.com/nervetattoo/simple-thermostat  
adobe/ferrum.doctest| https://github.com/adobe/ferrum.doctest  
donaldskip326/gauzy1| https://github.com/donaldskip326/gauzy1  
donaldskip326/gauzy1| https://github.com/donaldskip326/gauzy1  
ever-co/ever-gauzy| https://github.com/ever-co/ever-gauzy  
nqnghia285/music-app| https://github.com/nqnghia285/music-app  
CandyMan999/lmp-v2| https://github.com/CandyMan999/lmp-v2  
tabarra/txAdmin| https://github.com/tabarra/txAdmin  
ever-co/ever-gauzy| https://github.com/ever-co/ever-gauzy  
ever-co/ever-gauzy| https://github.com/ever-co/ever-gauzy  
recoai/recoai-ts-sdk| https://github.com/recoai/recoai-ts-sdk  
donaldskip326/gauzy1| https://github.com/donaldskip326/gauzy1  
ever-co/ever-gauzy| https://github.com/ever-co/ever-gauzy  
baovit72/Solance| https://github.com/baovit72/Solance  
reissmatt/risen-one-mission-platform| https://github.com/reissmatt/risen-one-mission-platform  
  
**注意：使用squirrelly的8.0.8版本一定存在漏洞，但是不一定存在安全风险！还需要使用组件的开发人员梳理所有使用render这个API的地方，确认是否存在可以从外部控制的注入点。**

## 0x05 漏洞总结

这个漏洞虽然看上去像是squirrelly这个组件由于编码上的疏忽而引入的漏洞，但在我看来这个漏洞是一个尚未被CWE收录的，具有普适性的漏洞类型，它可以抽象成如下模型：

1、采用了代码生成技术；

2、在运行期间生成代码并运行；

3、运行期生成并运行的代码取决于或部分取决于用户外部输入

如果在一个项目中存在上述特征，那么都需要小心该类型漏洞的出现。而对于不得已必须使用这种技术的项目，最好做好防御措施，包括：

1、降低运行该进程的用户的权限

2、限制该进程可以访问的路径

3、对用户输入进行白名单控制

4、对于该进程可以执行的操作系统命令做白名单控制

本质上来说这个漏洞是“数据”和“行为”没有彻底区分导致的，对于白帽可以在低代码/零代码平台上找找有没有类似的漏洞。

