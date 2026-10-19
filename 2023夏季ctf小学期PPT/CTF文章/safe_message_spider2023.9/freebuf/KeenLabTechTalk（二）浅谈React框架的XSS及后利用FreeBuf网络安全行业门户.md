## KeenLab Tech Talk系列

首期：[《虚拟化入门》](https://www.bilibili.com/video/BV1w64y1r7D2/?spm_id_from=333.788.b_636f6d6d656e74.12)

第三期：[《Android Auto
中一个普通的堆漏洞》](https://www.bilibili.com/video/BV1p34y1d746?spm_id_from=333.999.0.0)

## 前言

随着前端技术的高速发展，前后端分离的开发模式已经深入人心。由于后端不再直接输出页面，转以API接口的方式提供服务，导致XSS在这类新项目中不再常见。不过安全永远是一个动态的过程，新的开发技术会带来新的攻击面。现今前端最常用的主要是三个框架：React、Vuejs和Angular，本文将具体介绍基于React框架开发的前端应用的攻击面。其他框架也可依此类推。

##  **React应用长什么样？**

可以使用[ **Create React App**](https://create-react-app.dev/)(来快速生成并运行一个React应用。安装了 **[React Developer
Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)**
并访问一个网站后，若浏览器DevTool会亮起“Component”等标签，则代表这个网站使用了React框架开发。安全从业者往往会需要对一个网站的JavaScript代码进行审计。由于几乎所有的React开发的项目都使用了JSX，因此React框架通常会配合Webpack（parcel
/ rollup）、babel（tsc）等前端编译流程工具使用，如果没有Sourcemap就很难从被编译的源码还原出原始React代码。

##  **什么是JSX？**

JSX是一种JavaScript的语法扩展，通常和React配合使用。Vuejs也支持JSX。JSX允许开发者直接在JavaScript内部编写XML语法，不需要经过各种字符串的中转。由于没有浏览器支持JSX，导致React应用的的开发环境通常需要一个编译器负责将JSX编译为浏览器可以识别的JS代码。编译器（通常是babel）会将以下JSX代码：

> const element = ( <h1 className="greeting"> Hello, world! </h1>);

编译成以下能在浏览器中执行的JavaScript代码（结构有做简化）

    
    
    const element = {  type: 'h1',  props: {    className: 'greeting',  children: 'Hello, world!'  }};

就像代码展示的那样，没有什么DOM结构了，有的只有一个个Object。  
我们注意这里的 Hello, world! 对应的 children，如果我们可以控制这个属性，是否可以进而导致XSS？答案是否定的。当 children
的类型是字符串时，React将对DOM元素使用innerText来设置children，因此不会出现XSS；若可以将其控制为Object（这通常很难），但由于它的隐藏属性
$$typeof 的值，它在高版本的React中的类型是 Symbol（ Symbol
是ES6中引入的一种能表示一种唯一值的类型，Symbol('123') == Symbol('123') 的结果是 false
），我们也无法让React渲染这个对象。所以对于一个基于React框架（Vue和Angular同样）编写的前端项目，即使没有对XSS字符串进行特殊过滤，一般也可以认为是安全的。但世界上总有喜欢剑走偏锋的开发者，在某些React开发的项目内，仍然可以挖掘到不少XSS。

##  **常规XSS**

一些开发者未系统地学习React框架的思想，导致他们可能会使用各类DOM API来绕过React对DOM的管理。这些API包括 document.write
、document.appendChild
等。可以直接全文搜索这些API。以下列举的代码均来源于GitHub公开搜索。如下图，该项目尽管使用了React，但同时还在使用DOM API。此处
innerHTML 如果可控（该项目中不可控），就可以造成一个XSS。挖掘这种类型的漏洞等同于挖掘传统的DOM XSS。  
![1637054388_619377b48e244e42a429e.png!small?1637054389450](https://image.3001.net/images/20211116/1637054388_619377b48e244e42a429e.png!small?1637054389450)

##  **滥用Ref**

[ **Ref**](https://zh-hans.reactjs.org/docs/refs-and-the-dom.html)是React提供的一种高级功能，允许开发者直接操作React组件渲染出来的DOM。React设计它的本意是实现动画、或是和某些基于DOM的第三方库配合使用（常见的如Prism等代码高亮库）、或是对
video 等媒体标签进行控制，但一个API被设计出来是很难不被滥用的。下图展示了其中的一种滥用。这种滥用的挖掘和利用和常规的挖掘DOM
XSS相同。只要值可控（该项目中不可控）也可以造成XSS。  
![1637054449_619377f1218941c2f8cee.png!small?1637054449701](https://image.3001.net/images/20211116/1637054449_619377f1218941c2f8cee.png!small?1637054449701)

由于React有几个版本对Ref做了相当多的改动，因此在实际审计时看到的ref用法可能和图中的不同，对挖掘DOM XSS无影响。

##  **滥用dangerouslySetInnerHTML**

某些时候，前端开发者需要直接往该标签内写入HTML。React希望开发者避免使用这种方式，特意给该API起了个又臭又长的名字，要求传入的对象长成{__html:
'HTML'}
的形式，还特意标注了个“dangerously”。虽然他们为了防止滥用做出了很多努力，但似乎没有起到什么成效，dangerouslySetInnerHtml的滥用仍然非常常见。如图，一看就是用户可控的XSS点。![1637054489_61937819af7a87c009988.png!small?1637054490389](https://image.3001.net/images/20211116/1637054489_61937819af7a87c009988.png!small?1637054490389)直接全局搜索
dangerouslySetInnerHtml ，可以找到一个React项目的大多数XSS。

##  **动态组件传参/动态创建组件**

我们看一下下列代码

    
    
    const a = JSON.parse(location.hash.substr(1)) // hash = #{dangerouslySetInnerHTML: {__html: '<script>alert(1)</script>'}}return <div {...a} />

它和以下的ES5代码功能基本等价。

    
    
    var a = JSON.parse(location.hash.substr(1))var b = {}for (var key in a) { // 此处存在原型链污染，仅为示例  b[key] = a[key]}return React.createElement({  "type": "div",  "props": b})

这种将用户输入不限制地传入属性参数的做法显然会导致XSS，一旦createElement的参数完全可控，实现完全用户可控的动态组件创建，也可以直接导致XSS。值得一提的是，react-dom会通过[某些方法](https://github.com/facebook/react/blob/c88fb49d37fd01024e0a254a37b7810d107bdd1d/packages/react-dom/src/client/ReactDOMComponent.js#L395)来防止动态创建的script标签内的JS代码执行，但是这个安全检查绕过难度不高，可以直接用onerror等属性替代。

##  **特殊DOM标签的特殊属性**

考虑以下代码：

    
    
    const id = location.hash.substr(1)const a = <a href={id} />const b = <iframe src={id} />

当遇到某些特殊DOM标签的特殊属性可控时，可以直接造成XSS。由于开发者们一般情况下不会把onError
等事件让用户可控，即使可控React也不接受字符串为参数，（报错：Uncaught Error: Expected onError listener to
be a function, instead got a value of string type.）所以能考虑的只有类似 frame 、iframe 、a
、meta 、object 等较为特殊的标签。`script`标签的src和内容不可控无法造成XSS。

##  **SSR时的可疑输入**

SSR是Server Side
Render的缩写，即服务器端渲染。由于前端框架只工作在前端，导致百度等搜索引擎无法对网站内容进行抓取，页面首屏加载速度也同样会有大幅度的降低。SSR技术可以解决这些问题。只要开发者编写的JS代码对DOMAPI没有依赖，这些代码就可以直接在Nodejs上运行，所以基于React的前端项目只需要将react-dom 置换为 react-dom/server
即可直接复用前端代码，在后端渲染页面并直接输出HTML。在这种开发模式下，前端与后端服务器共用一套代码，在SSR的配合下DOMXSS可以转化为存储型、反射型等其他类型的XSS。在后端渲染完成之后，前端需要基于后端的渲染结果继续运行，所以后端在输出HTML代码的同时也要将当前状态返回给前端。这会涉及到对象的序列化与反序列化，会出现意料之外的安全问题。如图为Nextjs，现代最常见的SSR框架的实现。它会把所有的状态写入到scriptid="__NEXT_DATA__"
内，前端代码会读取这个标签内的内容作出处理。

![1637054646_619378b6c8971ff3598b7.png!small?1637054648256](https://image.3001.net/images/20211116/1637054646_619378b6c8971ff3598b7.png!small?1637054648256)

很多项目的SSR可能是迭代产生的新需求，因为Nextjs需要对项目结构进行相当大的改动，所以它们SSR部分有可能是自行开发的。Redux（一个状态容器，通常与React配合使用）的官方网站提供了一个SSR的例子：https://redux.js.org/usage/server-rendering

    
    
    function renderFullPage(html, preloadedState) {return `<!doctype html><html><head><title>Redux Universal Example</title></head><body><div id="root">${html}</div><script>// WARNING: See the following for security issues around embedding JSON in HTML:// https://redux.js.org/usage/server-rendering#security-considerationswindow.__PRELOADED_STATE__ = ${JSON.stringify(preloadedState).replace(/</g,'\\u003c')}</script><script src="/static/bundle.js"></script></body></html>`}

注意preloadState这个变量，它的值可以包含各种UGC内容，也有很多开发者会将react-router（和React配合使用的一个前端路由）的状态和Redux同步。如果当前页面存在消息、微博等交互性功能，preloadState很有可能部分可控。正是因为这种原因，上述Redux的官方网站给出的代码加上了一层XSS过滤。而如果开发者阅读的文档不是Redux官方文档，而是一些更新较为迟缓的资料，则可能由于这些文档编写者没有安全意识而受到攻击。如下图的文档内的示例代码就缺少了XSS过滤。

![1637054699_619378ebd74daf51751dc.png!small?1637054700735](https://image.3001.net/images/20211116/1637054699_619378ebd74daf51751dc.png!small?1637054700735)

##  **原型链污染**

### SSR

SSR时的前端和后端的代码绝大多数是共用的，因此可以通过审计前端代码的方式来对SSR服务进行攻击。如果前端打包时存在Sourcemap泄漏，就可以更直观地看到具体的依赖库，之后直接搜CVE或者npm
audit。此处的原型链污染想要RCE难度较大，一般的SSR框架，除了express（Nodejs下的WebServer框架）以外，不怎么依赖别的Nodejs平台相关的库和API。对于原型链污染来说，部署最广泛的可攻击目标是模板引擎，但SSR一般不使用这些库，导致攻击面相对较小。

### XSS

> const a = <div {...props} />

考虑这种使用了ES6的Object spread语法来复制一个新对象的代码，原型链污染在这种场合下无法触发XSS。原因如下：

  1. 包括Babel和TypeScript的实现在内，按照标准，Object spread不会将原型链上的属性复制到新对象上。
  2. React自身在遍历Object的每个属性的时候，会使用`hasOwnProperty`检查其是否是原型链属性。

但同样是ES6语法，Destructuring就不一样了，如下代码

> const {id, username, password} = props

等同于

    
    
    var _props = props,id = _props.id,username = _props.username,password = _props.password;

以上代码显然可以被原型链污染攻击。这种写法在现代前端代码中极为常见，我们以0CTF 2021
Final的useCTF()题为例。这一题的官方解答的攻击目标是 reapop 这个库。以下是相关代码：

    
    
    const {id, title, message, dismissible, showDismissButton, buttons, allowHTML, image} = notification// ...return (<div><div style={metaStyles} className={classnames.notificationMeta}>{title &&(allowHTML ? (<h4style={titleStyles}className={classnames.notificationTitle}dangerouslySetInnerHTML={{__html: title}}/>) : (<h4 style={titleStyles} className={classnames.notificationTitle}>{title}</h4>))}

代码存在dangerouslySetInnerHTML，可以把这种危险参数作为原型链污染的目的地。按此处的逻辑，只需要Object.prototype.allowHTML为true，页面里就会直接把Object.prototype.title属性原样输出。而来自俄罗斯的More
Smoked Leet Chicken战队给出了更精妙的解法。这个题目的UI框架 chakra-ui
给部分组件提供了一个特殊的属性[as](https://chakra-ui.com/docs/layout/box#as-prop)。该属性的效果大致如下：

    
    
    const a = <Box as="button" />const b = <Box />return <div>{a}{b}</div>

在DOM内会输出为：

    
    
    <div><button></button><div></div></div>

往下阅读`as`的实现，代码在此处：https://github.com/emotion-js/emotion/blob/23f43ab9f24d44219b0b007a00f4ac681fe8712e/packages/styled/src/base.js#L134

    
    
    const Styled: PrivateStyledComponent<Props> = withEmotionCache((props, cache, ref) => {const finalTag = (shouldUseAs && props.as) || baseTagfor (let key in props) {if (shouldUseAs && key === 'as') continueif (finalShouldForwardProp(key)) {newProps[key] = props[key]}}newProps.className = classNamenewProps.ref = refconst ele = React.createElement(finalTag, newProps)

这段代码有以下问题：

  * 没有检查`props.as`是否属于props对象（对于UI框架一般也没有检查的必要）
  * `finalTag = props.as`，即原型链污染可控
  * 在复制`props `到`newProps `时未检查属性是否属于props对象

因此通过原型链污染可以完整控制一个React组件。参考本文“动态创建组件”一节，可以很轻松地构造出

`<iframe src="javascript:alert(1)"> `

并。as属性在几乎所有UI框架中都存在，这使得一个原型链污染漏洞可以在几乎所有UI框架中造成XSS。（这题无法直接给Object设置一个dangerouslySetInnerHTML属性，这会使其他代码无法运行）as属性有点类似各种CMS的反序列化链，虽然不是漏洞，但这种feature会被原型链污染漏洞滥用。

##  **React Native?**

因为React Native不使用浏览器渲染数据，所以不太可能出现XSS漏洞。挖掘RCE漏洞更好的方式是寻找 eval / new Function
等动态代码执行相关代码，或是寻找能调用某些Java / ObjectiveC API的地方。

##  **后利用窃取数据**

XSS不只是弹窗，后续利用也值得关注。获取用户数据是XSS漏洞的一大危害，而在React框架中获取数据需要一些技巧。

最轻松的获取数据的方法是从DOM或者是localStorage等数据展示/持久化存储的地方获取数据，但有些数据（例如Token）一般不会被渲染在页面内，需要从React内部获取这些数据。

在从React内部获取数据之前，可以考虑通过Hook相关API的方式来获取数据。对 fetch API和 XMLHttpRequest API进行hook
（https://github.com/wendux/Ajax-hook
），或者是对数据附近的JavaScript/BOM/DOMAPI进行Hook，都是比较好实现又不依赖于React的通用解决方案。

如果实在难以获得数据，必须从React内部获得，则需要对React的相关概念进行学习。一个React项目的数据一般会存储在这些地方：Prop、State、Context，或是ReduxStore。从外部很难获取到React内部的值。

可以从React与外部交互的接口入手。React会在渲染出的DOM元素内增加一个属性：![1637054890_619379aaeb64966daa294.png!small?1637054891490](https://image.3001.net/images/20211116/1637054890_619379aaeb64966daa294.png!small?1637054891490)在引入了Fiber的React（16.8+），会多出
__reactFiber$xxxx
属性，该属性对应的就是这个DOM在React内部对应的FiberNode，可以直接使用child属性获得子节点。节点层级可以从React Dev
Tool内查看。通过读取每个FiberNode的 memoizedProps 和 memoizedState
，即可直接获取需要的Prop和State。在高版本使用React Hooks的项目中，FiberNode的 memorizedState
是一个链表，该链表内的节点次序可以参考该组件源码内 useState 的调用顺序。旧版React，引入的属性是
__reactInternalInstance 。State也是一个Object而非链表，可以方便地看到每个state的名字。

Context等属性可以在该属性内的 stateNode
属性找到，对于Redux只需要找到需要的数据在哪个React节点内被调用，读取其props/state也可以间接获取内部数据。获取这些数据最主要的麻烦是如何寻找到对应的ReactDOM节点，这需要配合Dev
Tool和源码慢慢挖掘。

##  **自查React项目的安全问题**

  1. 排查所有用到了 dangerouslySetInnerHtml 的组件，并充分论证此处使用该API的必要性。尽量改写为使用JSX的方式。
  2. 排查所有的 useRef、refs 等涉及到Ref API使用的组件，并尽量规避其的使用。
  3. 排查所有的DOM API调用（关键词包括 appendChildinner/HTML 等），将代码尽量改写为不依赖DOM的形式。
  4. 排查SSR的数据同步部分，对用户输入进行过滤。
  5. 使用 npm audit 排查是否有某些第三方依赖存在漏洞。
  6. 自查原型链污染漏洞。

##  **扩展阅读**

[ **codeql挖掘React应用的XSS实践**](https://hexo.imagemlt.xyz/post/javascript-codeql-learning/index.html)

## 作者

ashx——腾讯安全科恩实验室安全研究员、Katzebin战队副队长、TCTF出题人之一；主要研究Web安全，在各类的Web应用中发掘不少高危漏洞；作为A*0*E与Katzebin成员参与多场CTF竞赛。

