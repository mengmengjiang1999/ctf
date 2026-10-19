## 漏洞范围

    
    
    Confluence < 6.13.23
    6.14.0 ≤ Confluence < 7.4.11
    7.5.0 ≤ Confluence < 7.11.6
    7.12.0 ≤ Confluence < 7.12.5
    Confluence < 7.13.0

## 环境

使用vulhub进行远程调试，注意不需要更改镜像内的启动环境设置，直接更改docker-compose.yml即可

增加调试端口3789

![1669822654_638778be0e2b10d81772d.png!small?1669822654648](https://image.3001.net/images/20221130/1669822654_638778be0e2b10d81772d.png!small?1669822654648)

添加如上两行即可，然后重启，无需多余操作。

IDEA配置：

![1669822858_6387798a05181400842b2.png!small?1669822858857](https://image.3001.net/images/20221130/1669822858_6387798a05181400842b2.png!small?1669822858857)

![1669822894_638779aee58b3f8f2b157.png!small?1669822895538](https://image.3001.net/images/20221130/1669822894_638779aee58b3f8f2b157.png!small?1669822895538)

## 复现

前台RCE条件需要两个：

1. **/pages/doenterpagevariables.action** 该接口不需要登录；

2. **queryString** 和 **linkCreation** ，这两个参数可以利用来输入恶意的ongl表达式，能够成功解析，从而执行命令，需要POST请求。

![1669834201_6387a5d9d0c7eb28b7dde.png!small?1669834202663](https://image.3001.net/images/20221201/1669834201_6387a5d9d0c7eb28b7dde.png!small?1669834202663)

![1669823053_63877a4d733c09ef80100.png!small?1669823054095](https://image.3001.net/images/20221130/1669823053_63877a4d733c09ef80100.png!small?1669823054095)

![1669823107_63877a83b6964cbe1e9e2.png!small?1669823110975](https://image.3001.net/images/20221130/1669823107_63877a83b6964cbe1e9e2.png!small?1669823110975)

## 调试

对于OGNL表达式注入，我们直接来找xwork相关的jar包，反编译在java中寻找getValue()函数。

![1669823144_63877aa838adff970a2c6.png!small?1669823144898](https://image.3001.net/images/20221130/1669823144_63877aa838adff970a2c6.png!small?1669823144898)

我们找到这么多包含getValue()函数的java文件，那么我们到项目中挨个下断点。

![1669823209_63877ae9064e27c7847b7.png!small](https://image.3001.net/images/20221130/1669823209_63877ae9064e27c7847b7.png!small)

然后执行paylaod。

![1669831304_63879a882a2e8eb3a0e39.png!small?1669831305446](https://image.3001.net/images/20221201/1669831304_63879a882a2e8eb3a0e39.png!small?1669831305446)

  

可以看到断到了OgnlUtil#setProperties()下，跟据调试获得的值，可知道这里的getvalue并不是我们关注的点，我们跳到下个断点看看，跳到OgnlValueStack#findValue(String
expr）。![1669823379_63877b93006f8a940340a.png!small?1669823379752](https://image.3001.net/images/20221130/1669823379_63877b93006f8a940340a.png!small?1669823379752)

发现是webResourceManager，继续跳下个断点。

经过寻找发现，真正我们需要的地方在OgnlValueStack#findValue(String expr, Class
asType)，那么我们删除其他断点，只在这里下断点进行调试。

![1669823463_63877be743b261fa27348.png!small?1669823466947](https://image.3001.net/images/20221130/1669823463_63877be743b261fa27348.png!small?1669823466947)

查看调用栈。

![1669824414_63877f9e28acb38e9a2ce.png!small?1669824414903](https://image.3001.net/images/20221201/1669824414_63877f9e28acb38e9a2ce.png!small?1669824414903)

![1669824749_638780ed58c3ce53cc6b3.png!small?1669824750233](https://image.3001.net/images/20221201/1669824749_638780ed58c3ce53cc6b3.png!small?1669824750233)

![1669831423_63879aff4afe726915905.png!small?1669831423991](https://image.3001.net/images/20221201/1669831423_63879aff4afe726915905.png!small?1669831423991)

通过调用栈，我们可以看到模板渲染靠前，模板注入就是在这一部分产生的，那么来看看这部分

往下跟。

跟进OgnlUtil.compile()。

![1669827506_63878bb2629f0b7d497f8.png!small?1669827507305](https://image.3001.net/images/20221201/1669827506_63878bb2629f0b7d497f8.png!small?1669827507305)

可以看到这里进行了ognl的解析，将字符串解析成了ASTConst类型，往下进入Ognl.getValue。

![1669827820_63878cecb025334ed3263.png!small?1669827821908](https://image.3001.net/images/20221201/1669827820_63878cecb025334ed3263.png!small?1669827821908)

这里继续对ASTConst类型的tree进行转换成node类型，之后调用本身getValue()方法，继续跟进，如下：

![1669825181_6387829d85e38abeef185.png!small?1669825183073](https://image.3001.net/images/20221201/1669825181_6387829d85e38abeef185.png!small?1669825183073)

这里会有检测，那么看看检测了什么。

![1669825421_6387838d69d2004cb3fb9.png!small?1669825422455](https://image.3001.net/images/20221201/1669825421_6387838d69d2004cb3fb9.png!small?1669825422455)

![1669831561_63879b897e66328740f46.png!small?1669831562715](https://image.3001.net/images/20221201/1669831561_63879b897e66328740f46.png!small?1669831562715)

黑名单如上，4个hashset，分别限制了静态方法，字段，构造方法，获取classloader，限制了编译后不能出现的特定变量。

检测完之后，在AbstractUITag#evaluateParams获得下一个值。

![1669827997_63878d9d8a839b36bf7af.png!small?1669827998764](https://image.3001.net/images/20221201/1669827997_63878d9d8a839b36bf7af.png!small?1669827998764)

这里获得值接，下来又是相同的步骤。

![1669828235_63878e8b6a99632a65ce7.png!small?1669828236652](https://image.3001.net/images/20221201/1669828235_63878e8b6a99632a65ce7.png!small?1669828236652)

调用Ognl.parseExpression()函数，这里将我们的输入解析成了Ognl能理解的ASTConst类型，添加进刚才的AST中，继续进入Ognl.getValue。

![1669828507_63878f9bdf6e5b797fc5b.png!small?1669828509112](https://image.3001.net/images/20221201/1669828507_63878f9bdf6e5b797fc5b.png!small?1669828509112)

![1669829259_6387928bf052b9d133b9e.png!small?1669829261062](https://image.3001.net/images/20221201/1669829259_6387928bf052b9d133b9e.png!small?1669829261062)

这里继续对ASTConst类型的tree进行转换成node类型，然后调用自身的getValue()方法，在这里进行了计算得到9，继续往下。

![1669829521_63879391b4d3e0cfcfbc0.png!small?1669829522621](https://image.3001.net/images/20221201/1669829521_63879391b4d3e0cfcfbc0.png!small?1669829522621)

进行自定义标签添加，往下走。

![1669829631_638793ff463a876369ddf.png!small?1669829632657](https://image.3001.net/images/20221201/1669829631_638793ff463a876369ddf.png!small?1669829632657)

这里进行事件处理，继续往下。

![1669829725_6387945debb3066ee9057.png!small?1669829727093](https://image.3001.net/images/20221201/1669829725_6387945debb3066ee9057.png!small?1669829727093)

开始模板渲染。

![1669829781_63879495c8e2a5a1b673f.png!small?1669829782789](https://image.3001.net/images/20221201/1669829781_63879495c8e2a5a1b673f.png!small?1669829782789)

共35次，渲染完效果如下。

![1669830219_6387964b839aa71c331bc.png!small?1669830220979](https://image.3001.net/images/20221201/1669830219_6387964b839aa71c331bc.png!small?1669830220979)

然后在render中进行渲染。

![1669826113_638786415a8e5130624bb.png!small?1669826114695](https://image.3001.net/images/20221201/1669826113_638786415a8e5130624bb.png!small?1669826114695)

可以看到渲染次数，继续往下走，开始渲染title。

![1669826294_638786f65c3c1a13a70c6.png!small?1669826295779](https://image.3001.net/images/20221201/1669826294_638786f65c3c1a13a70c6.png!small?1669826295779)

可以和上面比较发现增加了title，35个结束之后，效果如下：

![1669826648_63878858cff15cbb5b290.png!small?1669826650344](https://image.3001.net/images/20221201/1669826648_63878858cff15cbb5b290.png!small?1669826650344)

然后note中执行9次。

![1669826811_638788fb40ef37729779a.png!small?1669826812658](https://image.3001.net/images/20221201/1669826811_638788fb40ef37729779a.png!small?1669826812658)

之后进行拦截器之类的操作。

## payload编写问题

使用\u0027而不使用'原因是会被html实体化。

![1669832450_63879f0222a5852b83d43.png!small?1669832450937](https://image.3001.net/images/20221201/1669832450_63879f0222a5852b83d43.png!small?1669832450937)

因为在OgnlParserTokenManager.getNextToken()中的
this.input_stream.readChar()会读取1个字符然后返回，当遇到“\u
”时，JavaCharStream.readChar()将其转换为字符，所以可以使用“ \u0027”来进行绕过html转义。  
然后我们的payload只需要再绕过静态方法SafeExpressionUtil.isSafeExpression的黑名单安全检查就可以了。

![1669833589_6387a3755e8c04693f9c0.png!small?1669833590328](https://image.3001.net/images/20221201/1669833589_6387a3755e8c04693f9c0.png!small?1669833590328)

![1669833768_6387a4283bd1fd2e12ae6.png!small?1669833769185](https://image.3001.net/images/20221201/1669833768_6387a4283bd1fd2e12ae6.png!small?1669833769185)

参考链接：

> https://forum.butian.net/share/961

