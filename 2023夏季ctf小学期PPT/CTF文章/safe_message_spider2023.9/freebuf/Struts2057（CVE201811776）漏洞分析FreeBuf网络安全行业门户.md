***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**Struts2-057,2018/8/22刚爆发的一个struts2的远程代码执行漏洞，网上已经有很多复现的文章了，这里并不打算对漏洞做复现，只是在代码层面研究漏洞。**

官方对这次漏洞的描述是：

> 1.定义XML配置时如果namespace值未设置且上层动作配置（Action
> Configuration）中未设置或用通配符namespace时可能会导致远程代码执行。
>
> 2.url标签未设置value和action值且上层动作未设置或用通配符namespace时可能会导致远程代码执行。

Namespace用于将action分为逻辑上的不同模块，可以有效避免action重名的情况。默认的namespace为空，当所有namespace中都找不到时才会在这个namespace中寻找。

先解释第一种情况：在struts.xml配置文件中，如果没有为基础xml配置中定义的result设置namespace，且上层<action>标签中没有设置namespace或者是使用通配符namespace时，则可能存在远程代码执行漏洞。（而各个result类型中只有redirectAction、chain以及postback这三种下面有namespace这个参数。）

示例：

    
    
    <struts>
    
      <package ....>
    
        <action name="a1">
    
          <result type="redirectAction">
    
            <param name="actionName">a2.action</param>
    
          </result>
    
        </action>
    
      </package>
    
    </struts>

第二种情况：如果struts的url标签<s:url>中未设置value和action值，且关联的action标签未设置或使用通配符namespace时可能会导致远程代码执行。

示例：

    
    
     <s:url action="/hello/hello_struts2" var="hello" >
    
           <s:param name="messageStore.message">Struts2 Tags</s:param>
    
     </s:url>
    
     <a href="${hello}">你好Struts2 Tag</a>

FilterDispatcher是struts2的核心控制器，负责拦截所有的用户请求，然后FilterDispatcher通过调用ActionMapper（接口）来决定调用哪个Action。

 **出问题的第一步就在这里：** ****

Struts2默认的是调用DefaultActionMapper这一实现类中的getMapping这一方法解析request来判断调用哪个action（报错namespace、name、method）,其中ActionMapper是通过parseNameAndParameters方法来获取namespace的。

![1.png](https://image.3001.net/images/20180824/1535080258_5b7f77422057e.png!small)

![2.png](https://image.3001.net/images/20180824/1535080977_5b7f7a1107180.png!small)

可以需要说下alwaysSelectFullNamespace这个属性，当alwaysSelectFullNamespace为true时，会严格按照uri提供的namespace去寻找action，找不到就会报404，所以这种情况下就算我们可以构造任意的namespace，但由于找不对应的action，在将namespace当ognl表达式执行代码前请求就会报404的错误，攻击不能成功。好在alwaysSelectFullNamespace的缺省值为true，这时

> 1.假设请求路径的URI，例如url是：<http://localhost:8081/>项目名/path1/path2 /addUser.action
>
>
> 2.首先寻找namespace为/path1/path2的package，如果存在这个package，则在这个package中寻找名字为addUser的action，若找到则执行，否则转步骤5；如果不存在这个package则转步骤3。
>
>
> 3.寻找namespace为/path1的package，如果存在这个package，则在这个package中寻找名字为addUser的action，若找到则执行，否则转步骤5；如果不存在这个package则转步骤4。
>
>
> 4.寻找namespace为/的package，如果存在这个package，则在这个package中寻找名字为addUser的action，若找到则执行，转步骤5；如果不存在转步骤5。
>
>
> 5.如果存在缺省的命名空间，就在该package下查找名字为addUser的action，若找到则执行，否则页面提示找不到action；否则提示面提示找不到action。

这也就是前文中所描述的为什么攻击需要“上层<action>标签中没有设置namespace或者是使用通配符namespace时”这一条件，这种情况下，可以构造任意namespace而请求不会出错。（这里就是source点了）

 **出问题的第二步（也就是sink点）：** ****

仅仅构造了任意的namespace还不够，还需要一个爆发点才行。这里以edirectAction这一返回类型来进行分析，redirectAction对应的类是org.apache.struts2.result.ServletActionRedirectResult。（实际上不止这一个类有问题，chain和postback这两个返回类型都有问题）。

在所请求的Action执行完后，会调用ServletActionRedirectResult.execute()进行重定向Result的解析，通过ActionMapper.getUriFromActionMapping()重组namespace和name后，由setLocation()
将带namespace的location放入父类ServletRedirectResult中调用exectue方法，然后ServletRedirectResult又会调用父类StrutsResultSupport中的exectue方法。

![3.png](https://image.3001.net/images/20180824/1535080306_5b7f7772a97c0.png!small)

![4.png](https://image.3001.net/images/20180824/1535080284_5b7f775c9071a.png!small)![5.png](https://image.3001.net/images/20180824/1535080289_5b7f77614262e.png!small)

最后由StrutsResultSupport调用conditionalParse(location,invocation)方法，通过TextParseUtil.translateVariables()调用OgnlTextParser.evaluate()解析执行url中的OGNL表达式，导致代码执行。

![6.png](https://image.3001.net/images/20180824/1535080326_5b7f778663163.png!small)![7.png](https://image.3001.net/images/20180824/1535080330_5b7f778a003ae.png!small)

 ***本文作者路上路人路过，转载请注明来自FreeBuf.COM**

