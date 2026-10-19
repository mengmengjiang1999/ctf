## 前言

UEditor是由百度web前端研发部开发的所见即所得富文本web编辑器，具有轻量，可定制，注重用户体验等特点。UEditor存在一个XSS漏洞，编辑器在定义过滤规则的时候不严和读取内容的时候的绕过导致了该漏洞，此漏洞已经上报，由于技术略菜，有分析不到位的还请多多见谅。

## 漏洞成因分析

漏洞文件产生在前端配置文件ueditor.config.js：

以下为纯文本粘贴为true时的过滤规则，对一些危险的标签没有做过滤，怪不得好多二次开发的。

    
    
    //纯文本粘贴模式下的过滤规则
        //'filterTxtRules' : function(){
        //    function transP(node){
        //        node.tagName = 'p';
        //        node.setStyle();
        //    }
        //    return {
        //        //直接删除及其字节点内容
        //        '-' : 'script style object iframe embed input select',
        //        'p': {$:{}},
        //        'br':{$:{}},
        //        'div':{'$':{}},
        //        'li':{'$':{}},
        //        'caption':transP,
        //        'th':transP,
        //        'tr':transP,
        //        'h1':transP,'h2':transP,'h3':transP,'h4':transP,'h5':transP,'h6':transP,
        //        'td':function(node){
        //            //没有内容的td直接删掉
        //            var txt = !!node.innerText();
        //            if(txt){
        //                node.parentNode.insertAfter(UE.uNode.createText(' &ampnbsp &ampnbsp'),node);
        //            }
        //            node.parentNode.removeChild(node,node.innerText())
        //        }
        //    }
        //}()
    

如下图，在官方文档里也进行了说明，通过getContent和setContent方法用<p>标签读取编辑器内容

![1617005619_60618c3350cbbf52665b5.png!small?1617005619486](https://image.3001.net/images/20210329/1617005619_60618c3350cbbf52665b5.png!small?1617005619486)

    
    
    #通getContent和setContent方法可以设置和读取编辑器的内容
    var ue = UE.getEditor();//对编辑器的操作最好在编辑器ready之后再做ue.ready(function(){
        //设置编辑器的内容
        ue.setContent('hello');
        //获取html内容，返回: <p>hello</p>
        var html = ue.getContent();
        //获取纯文本内容，返回: hello
        var txt = ue.getContentTxt();});

HTML中的p标签为段落标签，目前所有主流浏览器都支持<p>标签。

从编辑器里的左上角显示html可以看出，是带有<p>标签的，所以在标签内写入payload是不被执行的

![1617005741_60618cad57418d4fa5d14.png!small?1617005741335](https://image.3001.net/images/20210329/1617005741_60618cad57418d4fa5d14.png!small?1617005741335)

![1617005787_60618cdb55a481ca94b07.png!small?1617005787723](https://image.3001.net/images/20210329/1617005787_60618cdb55a481ca94b07.png!small?1617005787723)

![1617005749_60618cb5abaaefdb62d5a.png!small?1617005749735](https://image.3001.net/images/20210329/1617005749_60618cb5abaaefdb62d5a.png!small?1617005749735)

如下图，在删除掉<p>标签后写入payload可触发XSS漏洞

![1617005826_60618d020e509237a2884.png!small?1617005826019](https://image.3001.net/images/20210329/1617005826_60618d020e509237a2884.png!small?1617005826019)

![1617005840_60618d10d6d6b15edb3f9.png!small?1617005840843](https://image.3001.net/images/20210329/1617005840_60618d10d6d6b15edb3f9.png!small?1617005840843)

如果没有提交或者保存的功能，那么无法与数据库交互形成存储XSS，但是依然可多次点击左上角html按钮触发xss

![1617006008_60618db845b43ac326228.png!small?1617006008695](https://image.3001.net/images/20210329/1617006008_60618db845b43ac326228.png!small?1617006008695)

## 漏洞利用

首先安装部署环境：https://github.com/fex-team/ueditor/releases/tag/v1.4.3.3

存储型XSS需要写入后端数据库，这里要把编辑器部署到一个可与数据库交互的环境中。

首先我们打开编辑器输入正常的文本：

![1617006369_60618f21778f46d9f3e6e.png!small?1617006369503](https://image.3001.net/images/20210329/1617006369_60618f21778f46d9f3e6e.png!small?1617006369503)

![1617006404_60618f44963b9894db568.png!small?1617006404641](https://image.3001.net/images/20210329/1617006404_60618f44963b9894db568.png!small?1617006404641)

抓包并将<p>标签以及原本的文本删除

![1617006439_60618f6743357de1b6253.png!small?1617006439339](https://image.3001.net/images/20210329/1617006439_60618f6743357de1b6253.png!small?1617006439339)

插入payload：

    
    
    %3Cp%3E1111111"><ImG sRc=1 OnErRoR=prompt(1)>%3Cbr%2F%3E%3C%2Fp%3E

![1617006474_60618f8a7495ed8da15a6.png!small?1617006474352](https://image.3001.net/images/20210329/1617006474_60618f8a7495ed8da15a6.png!small?1617006474352)

成功触发存储型XSS漏洞

![1617006515_60618fb3439e3d17ccab9.png!small?1617006515419](https://image.3001.net/images/20210329/1617006515_60618fb3439e3d17ccab9.png!small?1617006515419)

![1617006641_60619031caf0d7311cafd.png!small?1617006642187](https://image.3001.net/images/20210329/1617006641_60619031caf0d7311cafd.png!small?1617006642187)

经笔者调查在互联网上存在着许多ueditor编辑器在线展示的网站，这些大都存在没有与后端交互的反射型XSS，但是如果存在与后端数据库交互的功能譬如一些写作平台即可形成存储型XSS漏洞，结合一些xss平台，或者再和其他漏洞配合形成组合拳，威力也不容小藐。

## 防御措施

1、修改 xss过滤白名单 配置文件ueditor.config.js，增加白名单过滤，比如对一些非法的参数和标签，像
<>、,",'，img标签的onerror属性，script标签等进行自动转义，或者是强制的拦截并提示。

2、对输入的数据也进行html转义，使其不会识别为可执行脚本。

