![](https://image.3001.net/images/20220325/1648201927_623d90c7cf64937e8ca09.png!small)

## **前言**

Goby 现在在安全圈子内属于人尽皆知的安全产品了，在基于 FOFA
平台累积的丰富的指纹库的基础上，可以快速高效的对目标网络环境进行资产探测。同时它也提供了许多 API 接口让使用者可以根据自己需要开发插件，本文介绍的
Ceye Dnslog 日志接收插件是在 Log4j 漏洞爆发的那段时间发现经常会使用到这个平台，每次登陆网页版进行日志查看又太麻烦，于是就开发了这个插件。

## 0×01 插件效果

![](https://image.3001.net/images/20220325/1648203327_623d963f7c4bc0f82193b.gif!small)

## 0×02 Ceye

Ceye 是一个用来检测带外（Out-of-Band）流量的监控平台，如 DNS 查询和 HTTP 请求。它可以帮助安全研究人员在测试漏洞时收集信息（例如
SSRF / XXE / RFI / RCE）。 **它的使用场景主要是在一些不能直接表明攻击是否成功的漏洞利用的过程中，通过使用 CEYE
平台提供的域名，结合诸如 DNS、HTTP 之类的带外信道来得到我们想要的回显信息，从而达到对漏洞的检测。**

## 0×03 插件配置

总体上插件的使用是十分简单的，在 Goby 的设置 → 插件设置 → CEYE Dnslog Platform 页面，填写你再登录 Ceye.io
后获取到的 APIkey 以及分配的域名并点击确定，如图。

![](https://image.3001.net/images/20220325/1648204089_623d99396b7a0dc9ccfc2.png!small)

Ceye 的 api token 和分配的域名可以通过登陆 ceye 平台后的 profile
页面（http://ceye.io/profile）获取。如图

![](https://image.3001.net/images/20220325/1648204122_623d995ab53577d71b866.png!small)

在配置好这些选项之后点击 Goby 插件工具栏处的 Ceye 插件的 Logo 后，就可以打开日志接收界面，当 apikey
和分配域名填写正确的情况下，在使用域名进行回显后，点击获取按钮就可以看到日志接受结果。

## 0×04 关于代码

1\. 由于新版 Goby
对插件要求默认语言为英语，所以需要在项目中进行国际化操作。在我进行国际化的过程中，由于本人粗心多次出现某个标点或某个特殊字符使用的不是英文语言，从而导致插件上传失败，同时由于在
package.json 当中 language 字段和 readme，changelog
字段的值指向的文件地址错误导致插件无法正确加载。具体的国际化代码与目录结构如下图。

![](https://image.3001.net/images/20220325/1648204308_623d9a14b5fe5345f3acf.png!small)

2\. 在开发初期，由于没有使用最新版本的 Goby 进行开发，导致有部分高版本才拥有的 API 没有办法使用，比如 Goby.getLang()
这个在国际化过程中需要用到的 API. 所以推荐在最新版的 Goby 上进行插件开发。

3\. 关于插件的国际化，这里建议使用 jquery 的 i18next
模块进行。首先使用编写translate.js文件，该文件主要用于读取国际化文件（html.json），并将读取到的内容转换成对象，用于在 html
文件中动态进行渲染，translate.js 以及 html.json 的代码如下。

 **translate.js**

    
    
    const fs = require('fs'),  
    path = require('path'),  
    htmlTranslate = 'html.json';  
    let dirArr = fs.readdirSync(path.join(__dirname,'../translate'));  
    module.exports = dirArr.reduce((total,prev)=>{  
    let fileStat = fs.statSync(path.join(__dirname,'../translate/',prev));  
    if (fileStat.isDirectory() && fs.existsSync(path.join(__dirname,'../translate/',prev,htmlTranslate))) {  
    try {  
    const content = require(path.join(__dirname,'../translate/',prev,htmlTranslate));  
    total[prev] = content;  
    } catch (error) {  
    console.error(error);  
    // goby.showErrorMessage(error);  
    }  
    return total;  
    }else{  
    return total;  
    }  
    },{})

 **html.json**

    
    
    {  
    "Get":"获取",  
    "CreateTime":"创建时间",  
    "Address":"远程地址",  
    "Name":"请求地址",  
    "ID":"ID",  
    "Ceye.io":"Ceye Dnslog"  
    }

然后就是在窗口 html 文件中调用先前编写的 translate 方法并结合 Goby 的语言检测 API 来实现实时修改语言。同时在 html 中使用
jquery 的 i18n 插件，通过 data-i18n 属性来动态变化语言。主要代码如下。

 **extension.js 语言检测**``

> `let goby = parent.goby; // 获取GobyAPi  
> let fs = parent.require('fs');  
> function lang(){  
> //获取当前Languzge  
> let language = goby.getLang();`
>
> ``
>
> `//判断翻译文件是否存在  
> let translateState = fs.existsSync(goby.__dirname + '/assets/translate/' +
> language+'/html.json');`
>
> ``
>
> `//翻译文件存在则使用翻译文件,否则使用默认EN翻译  
> let lang = translateState?language:'EN';`
>
> ``
>
> `let a = $.i18n.init({  
> lng: language, //指定语言  
> useCookie:false,  
> resGetPath: './assets/translate/'+lang+'/html.json',//语言包的路径  
> }, function(err, t) {  
> if(!err){  
> $('[data-i18n]').i18n(); // 通过选择器集体翻译  
> return;  
> }  
> });  
> }`
>
> ``
>
> `lang();`
>
> ``
>
> `//当lang改变时更新页面内容  
> goby.bindEvent('onChangeLang',()=>{  
> lang();  
> })`

``

对于 html 中表格元素的渲染，一是通过 layui 的 table.render
进行自动化填写，这种适用于返回数据量较多的情况。二是对于少量数据。通过遍历得到的元素的循环生成的 html 代码然后再通过 js 渲染进 html
页面当中。本插件由于返回的数据量较小使用的就是第二种方法。代码如下

 **extension.js 表格生成**``

> `const config = goby.getConfiguration();  
> const api_key = config["api_key"].default,  
> identifier = config["identifier"].default,  
> api = "http://api.ceye.io/v1/records";  
> $("#get").on("click",(function (){  
> $("#ip-table tbody").html("");  
> $.ajax({  
> type: 'GET',  
> url: api,  
> contentType: 'application/x-www-form-urlencoded', // 发送的数据类型  
> dataType: 'json', // 接收的数据类型  
> data:Qs.stringify({  
> "token":api_key,  
> "type":"dns",  
> "filter":""  
> }),  
> success : function(res) {  
> let html = "";  
> res.data.forEach(d => {  
> console.log(d)  
> html += `<tr>  
> <td>${d.id}</td>  
> <td>${d.name}</td>  
> <td>${d.remote_addr}</td>  
> <td>${d.created_at}</td>  
> </tr>``
>
> `});  
> $("#ip-table tbody").html(html);  
> }  
> });  
> }))```

## 0×05 小结

有了这个插件，当你在 Goby 中扫描到类似 Log4j 或一些网络环境复杂的 rce 利用时，通过使用 ceye.io
检测漏洞的存在后就可以直接在插件中获取到回显信息，在开发了几个插件之后我发现只要你多去翻一翻 Goby
的开发文档，多多利用搜索引擎，开发一款插件并不是很难的事情，关键是要去发现需求，发现自己需要什么，想要什么。才能更快的着手开发。后期我在工作之余还计划开发一个
tg bot 的通知插件以及更多的漏洞利用插件。为 Goby 社区贡献一份自己的力量，希望 Goby 社区可以变得越来越好。

> 插件开发文档：
>
> https://gobies.org/docs.html

 **关于插件开发在B站都有详细的教学，欢迎大家到弹幕区合影~**

  * https://www.bilibili.com/video/BV1u54y147PF/

> 文章来自Goby社区成员： adeljck，转载请注明出处。  
> 下载Goby内测版，请关注公众号：Gobysec  
> 下载Goby正式版，请访问官网：[http://gobies.org](http://gobies.org/)

