***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **2018年4月，一个新的Apache
Struts远程代码执行漏洞被报告。在Struts特定配置下，访问特制的URL可以触发该漏洞。漏洞编号为CVE-2018-11776（S2-057）。本文将介绍发现漏洞的过程。**  

## 映射攻击面

许多漏洞涉及从不受信任的源（例如，用户输入）流向某个特定位置的数据，这种情况下数据会以危险的方式被利用（SQL查询，反序列化以及一些其他解释语言等等）。对于特定项目，开始着手研究此类问题的一种好方法是查看旧版本软件的已知漏洞。这可以让你深入了解所想要查找的各种源及接收点。

在本案例中，作者首先查看了RCE漏洞S2-032（CVE-2016-3081），S2-033（CVE-2016-3687）和S2-037（CVE-2016-4438）。与Struts中的许多其他RCE一样，这些RCE涉及被认为是OGNL表达式的非法输入，允许攻击者在服务器上运行任意代码。这三个漏洞特别有趣，不仅因为它们让我们对Struts的内部工作有了一些了解，而且还因为同样的问题需要三次才能修复！

所有这三个问题都是远程输入通过变量methodName作为参数传递给方法OgnlUtil::getValue()的结果。

    
    
    String methodName = proxy.getMethod();    //<--- untrusted source, but where from?
    
    LOG.debug("Executing action method = {}", methodName);
    
    String timerKey = "invokeAction: " + proxy.getActionName();
    
    try {
    
        UtilTimerStack.push(timerKey);
    
        Object methodResult;
    
        try {
    
            methodResult = ognlUtil.getValue(methodName + "()", getStack().getContext(), action); //<--- RCE

这里的proxy字段是ActionProxy类型，它是一个接口。在查看它的定义时，作者发现除了方法getMethod()（在上面的代码中用于赋值的变量methodName）之外，还有各种其他的方法，如getActionName()和getNamespace()。这些方法貌似会从URL返回信息。所以作者开始假设所有这些方法都可能返回不受信任的输入。

现在可以使用QL开始对这些不受信任的来源进行建模：

    
    
    class ActionProxyGetMethod extends Method {
    
      ActionProxyGetMethod() {
    
        getDeclaringType().getASupertype*().hasQualifiedName("com.opensymphony.xwork2", "ActionProxy") and
    
        (
    
          hasName("getMethod") or
    
          hasName("getNamespace") or
    
          hasName("getActionName")
    
        )
    
      }
    
    }
    
    predicate isActionProxySource(DataFlow::Node source) {
    
       source.asExpr().(MethodAccess).getMethod() instanceof ActionProxyGetMethod
    
    }

## 识别OGNL接收点

现在已经识别并描述了一些不受信任的来源，下一步是为接收点做同样的事情。如前所述，许多Struts
RCE涉及将远程输入解析为OGNL表达式。Struts中有许多函数最终将它们的参数作为OGNL表达式进行评估;对于在本文中开始的三个漏洞，都使用了OgnlUtil::getValue()，但是在漏洞S2-045（CVE-2017-5638）中，使用了TextParseUtil::translateVariables()。我们可以寻找用于执行OGNL表达式的函数，而不是将每一个方法描述为QL中的单独接收点。而OgnlUtil::compileAndExecute()和OgnlUtl::compileAndExecuteMethod()看起来像有希望的接收点。

作者在一个QL predicate中描述了它们，如下所示：

    
    
    predicate isOgnlSink(DataFlow::Node sink) {
    
      exists(MethodAccess ma | ma.getMethod().hasName("compileAndExecute") or ma.getMethod().hasName("compileAndExecuteMethod") |
    
        ma.getMethod().getDeclaringType().getName().matches("OgnlUtil") and
    
        sink.asExpr() = ma.getArgument(0)
    
      )
    
    }

## 第一次尝试污点跟踪

现在已经在QL中定义了源和接收点，所以可以在污点跟踪查询中使用这些定义。 这里作者使用DataFlow库来定义DataFlow配置：

    
    
    class OgnlTaintTrackingCfg extends DataFlow::Configuration {
    
      OgnlTaintTrackingCfg() {
    
        this = "mapping"
    
      }
    
      override predicate isSource(DataFlow::Node source) {
    
        isActionProxySource(source)
    
      }
    
      override predicate isSink(DataFlow::Node sink) {
    
        isOgnlSink(sink)
    
      }
    
      override predicate isAdditionalFlowStep(DataFlow::Node node1, DataFlow::Node node2) {
    
        TaintTracking::localTaintStep(node1, node2) or
    
        exists(Field f, RefType t | node1.asExpr() = f.getAnAssignedValue() and node2.asExpr() = f.getAnAccess() and
    
          node1.asExpr().getEnclosingCallable().getDeclaringType() = t and
    
          node2.asExpr().getEnclosingCallable().getDeclaringType() = t
    
        )
    
      }
    
    }
    
    from OgnlTaintTrackingCfg cfg, DataFlow::Node source, DataFlow::Node sink
    
    where cfg.hasFlow(source, sink)
    
    select source, sink

这里作者使用了之前定义的isActionProxySource和isOgnlSink predicates。

需要注意的是，作者还覆盖了一个名为isAdditionalFlowStep的predicate。这个predicate允许包含可以传播非法数据的额外步骤。例如，这允许将项目特定的信息合并到流配置中。再如，如果有通过某个网络层进行通信的组件，则可以在QL中描述那些各种网络端点的代码，允许DataFlow库跟踪非法数据。

对于此特定查询，作者添加了两个额外的流程步骤供DataFlow库使用。 第一个：

    
    
    TaintTracking::localTaintStep(node1, node2)

包含标准QL TaintTracking库来跟踪标准Java库调用，字符串操作等。第二个是一个近似值，允许通过字段访问跟踪非法数据：

    
    
    exists(Field f, RefType t | node1.asExpr() = f.getAnAssignedValue() and node2.asExpr() = f.getAnAccess() and
    
      node1.asExpr().getEnclosingCallable().getDeclaringType() = t and
    
      node2.asExpr().getEnclosingCallable().getDeclaringType() = t
    
    )

这表示如果将字段分配给某个非法值，只要表达式都由相同类型的方法调用，那么对该字段的访问也将被视为非法。查看以下案例：

    
    
    public void foo(String taint) {
    
      this.field = taint;
    
    }
    
    public void bar() {
    
      String x = this.field; //x非法，因为字段被分配给`foo`中的非法值
    
    }

如你所见，bar()中this.field的访问可能并不总是非法。例如，如果在bar()之前未调用foo()。那么不会在默认的DataFlow::Configuration中包含此流程步骤，因为我们无法保证数据始终以这种方式流动。但是，对于找到漏洞，将它们包含在DataFlow::Configuration中就很有用。

## 初始结果和查询细化

在最新版本的源代码上运行查询，并开始检查结果，S2-032，S2-033和S2-037仍然被查询标记。在查看其他结果之前，先调查为什么即使代码已修复，这些特定的结果仍然被标记。

虽然最初通过过滤输入来修复第一个漏洞，但是在S2-037之后，Struts团队决定通过调用OgnlUtil::getMalue()替换对OgnlUtil::getMalue()的调用来修复漏洞。

    
    
    methodResult = ognlUtil.callMethod(methodName + "()", getStack().getContext(), action);

方法callMethod()封装对compileAndExecuteMethod()的调用：

    
    
    public Object callMethod(final String name, final Map<String, Object> context, final Object root) throws OgnlException {
    
      return compileAndExecuteMethod(name, context, new OgnlTask<Object>() {
    
        public Object execute(Object tree) throws OgnlException {
    
          return Ognl.getValue(tree, context, root);
    
        }
    
      });
    
    }

并且compileAndExecuteMethod()在执行之前对表达式执行额外检查：

    
    
    private <T> Object compileAndExecuteMethod(String expression, Map<String, Object> context, OgnlTask<T> task) throws OgnlException {
    
      Object tree;
    
      if (enableExpressionCache) {
    
        tree = expressions.get(expression);
    
        if (tree == null) {
    
          tree = Ognl.parseExpression(expression);
    
          checkSimpleMethod(tree, context); //额外检查
    
        }

这意味着我们实际上可以从接收点中移除compileAndExecuteMethod()。

在重新运行查询后，高亮的getMethod()作为接收点的调用的结果消失了。但是，仍然有一些结果突出显示了DefaultActionInvocation.java中的代码，这些代码被认为是已经被修复的，例如对getActionName()的调用，并且这里的数据路径并不是很明显。

## 路径探索和进一步查询细化

为了研究为什么这个结果被标记，就需要看到DataFlow库用来产生这个结果的每个流程步骤。QL允许编写特殊的路径问题查询，这些查询可生成可逐节点探索的可变长度路径，DataFlow库允许编写输出此数据的查询。

LGTM本身没有路径问题查询的路径探索UI，因此需要使用另一个Semmle应用程序：QL for
Eclipse。这是一个Eclipse插件，其中包含一个可视化工具，允许完成污点跟踪中的各个步骤。用户可以免费下载并安装此Eclipse插件。它不仅可以在LGTM.com上对开源项目进行离线分析，还可以提供更强大的开发环境。下文的查询可以在semmle-security-java目录下的Semmle/SecurityQueries
Git存储库中找到。你可以按照README.md文件中的说明在Eclipse插件中运行它们。

首先，在initial.ql中运行查询。 在QL for
Eclipse中，从DefaultActionInvocation.java中选择结果后，你可以在Path
Explorer窗口中看到从源到接收点的详细路径。

![详细路径](https://image.3001.net/images/20180828/1535393505_5b843ee15e6c9.png!small)

在上图中，你可以看到，经过几个步骤后，调用getActionName()返回的值会流入对pkg.getActionConfigs()返回的对象的get()调用中的参数：

    
    
    String chainedTo = actionName + nameSeparator + resultCode

> actionName来自某个地方的`getActionName`
    
    
    ActionConfig chainedToConfig = pkg.getActionConfigs().get(chainedTo)

> //chainedTo包含`actionName`并最终出现在`get`方法中

单击下一步，就到了ValueStackShadowMap::get()方法，如下所示：

    
    
    public Object get(Object key) {
    
      Object value = super.get(key);  //<--- key gets tainted?
    
      if ((value == null) && key instanceof String) {
    
        value = valueStack.findValue((String) key);  //<--- findValue ended up evaluating `key`
    
      }
    
      return value;
    
    }

事实证明，因为pkg.getActionConfigs()返回一个Map，而ValueStackShadowMap实现了Map接口，所以理论上pkg.getActionConfigs()返回的值可能是ValueStackShadowMap的一个实例。因此，QL
DataFlow库显示了从变量chainedTo到类ValueStackShadowMap中的get()实现的潜在流程。实际上，ValueStackShadowMap类属于jasperreports插件，该类的实例仅在几个地方创建，并都不会被pkg.getActionConfigs()返回。在发现ValueStackShadowMap::get()不太可能被命中之后，作者通过在DataFlow::Configuration中添加一个过滤来删除依赖它的结果：

    
    
    override predicate isBarrier(DataFlow::Node node) {
    
      exists(Method m | (m.hasName("get") or m.hasName("containsKey")) and
    
        m.getDeclaringType().hasName("ValueStackShadowMap") and
    
        node.getEnclosingCallable() = m
    
      )
    
    }

这个predicate意思是如果非法数据流入ValueStackShadowMap的get()或containsKey()方法，那么就不要继续跟踪它。

## 新漏洞：CVE-2018-11776

只有10对源和接收点，就很容易通过手工检查发现这些是否真正存在问题。通过一些路径，作者发现有些路径是无效的，因为它们在测试用例中，所以在查询中添加了一些过滤来过滤掉这些路径。这就留下了一些非常有趣的结果。

以ServletActionRedirectResult.java中的源代码为例：

![ServletActionRedirectResult.java中的源代码](https://image.3001.net/images/20180828/1535393612_5b843f4c33cb6.png!small)

在第一步中，调用getNamespace（）的源通过变量namespace流入ActionMapping构造函数的参数：

    
    
    public void execute(ActionInvocation invocation) throws Exception {
    
      actionName = conditionalParse(actionName, invocation);
    
      if (namespace == null) {
    
        namespace = invocation.getProxy().getNamespace();  //源
    
      } else {
    
        namespace = conditionalParse(namespace, invocation);
    
      }
    
      if (method == null) {
    
        method = "";
    
      } else {
    
        method = conditionalParse(method, invocation);
    
      }
    
      String tmpLocation = actionMapper.getUriFromActionMapping(new ActionMapping(actionName, namespace, method, null)); //namespace进入ActionMapping的构造函数
    
      setLocation(tmpLocation);

继续执行这些步骤之后，可以看到getUriFromActionMapping()返回一个URL字符串，该字符串使用构造的ActionMapping中的namespace。然后通过变量tmpLocation流入setLocation()的参数，然后setLocation()在超类StrutsResultSupport中设置字段位置：

    
    
    public void setLocation(String location) {
    
        this.location = location;
    
    }

然后代码在ServletActionResult上调用execute()：

    
    
    String tmpLocation = actionMapper.getUriFromActionMapping(new ActionMapping(actionName, namespace, method, null));
    
    setLocation(tmpLocation);
    
    super.execute(invocation);

它将location字段传递给对conditionalParse()的调用：

    
    
    public void execute(ActionInvocation invocation) throws Exception {
    
        lastFinalLocation = conditionalParse(location, invocation);
    
        doExecute(lastFinalLocation, invocation);
    
    }

然后conditionalParse()将位置传递给translateVariables():

    
    
    protected String conditionalParse(String param, ActionInvocation invocation) {
    
        if (parse && param != null && invocation != null) {
    
            return TextParseUtil.translateVariables(
    
                param,
    
                invocation.getStack(),
    
                new EncodingParsedValueEvaluator());
    
        } else {
    
            return param;
    
        }
    
    }

所以当在ServletActionRedirectResult中没有设置namespace参数时，代码从ActionProxy获取namespace，然后将其作为OGNL表达式进行评估。为了测试这个，作者通过以下方法替换了showcase应用程序中的一个配置文件（例如struts-actionchaining.xml）中的struts标记：

    
    
    <struts>
    
        <package name="actionchaining" extends="struts-default">
    
            <action name="actionChain1" class="org.apache.struts2.showcase.actionchaining.ActionChain1">
    
               <result type="redirectAction">
    
                 <param name = "actionName">register2</param>
    
               </result>
    
            </action>
    
        </package>
    
    </struts>

然后在本地运行showcase应用程序，并访问了一个可以触发此漏洞的URL并执行shell命令以在计算机上打开计算器应用程序。

不仅如此，来自ActionChainResult，PostbackResult和ServletUrlRenderer的不可信来源也同样有效！PortletActionRedirectResult中的那个可能也可以，但没有被测试。四个RCE足以证明问题的严重性。

## 总结

在这篇文章中，作者展示了通过使用已知（过去的）的漏洞来帮助构建应用程序的污点模型，只需将麻烦的工作留给QL DataFlow库就可以找到新的漏洞。

鉴于S2-032，S2-033和S2-037都是在短时间内被发现和修复的，安全研究人员研究了S2-032以寻找类似问题并发现S2-033和S2-037。所以这里最大的问题是：鉴于在这里发现的漏洞（S2-057）也来自类似的问题，安全研究人员和供应商是如何错过的，而且在两年后才发现？在作者看来，这是因为S2-032，S2-033和S2-037之间的相似性在某种意义上是局部的，因为它们都出现在源代码中的相似位置（全部在Rest插件中）。S2-057和S2-032之间的相似性处于更加语义的层面。它们由受污染的源连接，而不是源代码的位置，因此任何能够成功找到这样的变体的软件或工具都需要能够在整个代码库中执行这种语义分析。

***参考来源：[lgtm](https://lgtm.com/blog/apache_struts_CVE-2018-11776)，FB小编Covfefe编译，转载请注明来自FreeBuf.COM**

