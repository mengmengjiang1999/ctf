## 漏洞描述

CVE-2022-31692中, 在 Spring Security受影响版本范围内, 在使用
forward/include进行转发的情况下可能导致权限绕过. 但实际测试中发现需要修改为特定配置, 漏洞的实际危害不算太高。

 **受影响版本** ：

5.7.0 <= Spring Security <= 5.7.4

5.6.0 <= Spring Security <= 5.6.8

## POC

[SpindleSec/cve-2022-31692: A project demonstrating an app that is vulnerable
to Spring Security authorization bypass CVE-2022-31692
(github.com)](https://github.com/SpindleSec/cve-2022-31692)

## 成因简析

调用过程中只在进入`/forward`的时候进行了一次鉴权,
由于在`SecurityConfig.java`中已配置`.antMatchers("/forward").permitAll()`,
故未能禁止未授权用户访问. 跳转`/admin`时未进行权限验证, 造成未授权访问。

## 复现

### 正常访问流程

首先看一下直接访问 /admin页面时的正常流程(从 **鉴权** 部分开始, 前面 run**invoke和处理其他 filter的部分就不看了)

    
    
    /* 
    this is a part of the stack when processing the invoking
    texts in the commentary show the position of the function
    the outside are the function in the target line
    */
    
    // ......
    
    chain.doFilter(request, response);
    // doFilter:122, ExceptionTranslationFilter (org.springframework.security.web.access)
      /* processing the filter "org.springframework.security.web.access.ExceptionTranslationFilter" */
    
    nextFilter.doFilter(request, response, this);
    // doFilter:346, FilterChainProxy$VirtualFilterChain (org.springframework.security.web) [13]
    
    /* 
    ATTENTION, plz
    
    now the Filter = "org.springframework.security.web.access.intercept.AuthorizationFilter"
    which means it starts dealing with the Authorization, follow it and see what happends before the denying
    */
    
    doFilterInternal(httpRequest, httpResponse, filterChain);
    // doFilter:117, OncePerRequestFilter (org.springframework.web.filter) [9]
    

在进入最后一行的`doFilterInternal`后, 来到了`doFilterInternal:68, AuthorizationFilter
(org.springframework.security.web.access.intercept)`, 关键代码如下：

    
    
    @Override
    	protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
    			throws ServletException, IOException {
    
    		AuthorizationDecision decision = this.authorizationManager.check(this::getAuthentication, request);
    		this.eventPublisher.publishAuthorizationEvent(this::getAuthentication, request, decision);
    		if (decision != null && !decision.isGranted()) {
    			throw new AccessDeniedException("Access Denied");
    		}
    		filterChain.doFilter(request, response);
    	}
    

`this::getAuthentication`

    
    
    private Authentication getAuthentication() {
    		Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
    		if (authentication == null) {
    			throw new AuthenticationCredentialsNotFoundException(
    					"An Authentication object was not found in the SecurityContext");
    		}
    		return authentication;
    	}
    

`public Authentication getAuthentication()`

    
    
    @Override
    	public Authentication getAuthentication() {
    		return this.authentication;
    	}
    

`check()`

    
    
    @Override
    	public AuthorizationDecision check(Supplier<Authentication> authentication, T object) {
    		boolean granted = isGranted(authentication.get());
    		return new AuthorityAuthorizationDecision(granted, this.authorities);
    	}
    

`isGranted()`

    
    
    private boolean isGranted(Authentication authentication) {
    		return authentication != null && authentication.isAuthenticated() && isAuthorized(authentication);
    	}
    

`isAuthorized()`

    
    
    private boolean isAuthorized(Authentication authentication) {
    		Set<String> authorities = AuthorityUtils.authorityListToSet(this.authorities);
    		for (GrantedAuthority grantedAuthority : authentication.getAuthorities()) {
    			if (authorities.contains(grantedAuthority.getAuthority())) {
    				return true;
    			}
    		}
    		return false;
    	}
    

`isAuthorized()`函数中`authorities`和`grantedAuthority`的值分别如图, 显然返回`false`

![image.png](https://image.3001.net/images/20221121/1669035606_637b7656440cf2f9895c4.png!small)

则`check()`的返回值, 如图：

![image-20221109144635803](https://image.3001.net/images/20221111/1668133290_636db1aa26fb4c73e5ad2.png!small)

然后各函数均返回, 在`doFilterInternal`中抛出权限错误。

![image-20221109145042060](https://image.3001.net/images/20221111/1668133322_636db1caa96cfa13cad1a.png!small)

如此便是一个完整的鉴权流程, 接下来看一下`/forward`中的处理。

### 攻击访问流程

直接进入鉴权流程

首先获取 filter, 进入处理

![image-20221109193307550](https://image.3001.net/images/20221111/1668133397_636db2156e7a2ceae1eed.png!small)

`doFilter`源码

    
    
    @Override
    	public final void doFilter(ServletRequest request, ServletResponse response, FilterChain filterChain)
    			throws ServletException, IOException {
    
    		if (!(request instanceof HttpServletRequest) || !(response instanceof HttpServletResponse)) {
    			throw new ServletException("OncePerRequestFilter just supports HTTP requests");
    		}
    		HttpServletRequest httpRequest = (HttpServletRequest) request;
    		HttpServletResponse httpResponse = (HttpServletResponse) response;
    
    		String alreadyFilteredAttributeName = getAlreadyFilteredAttributeName();
    		boolean hasAlreadyFilteredAttribute = request.getAttribute(alreadyFilteredAttributeName) != null;
    
    		if (skipDispatch(httpRequest) || shouldNotFilter(httpRequest)) {
    			// Proceed without invoking this filter...
    			filterChain.doFilter(request, response);
    		}
    		else if (hasAlreadyFilteredAttribute) {
    			if (DispatcherType.ERROR.equals(request.getDispatcherType())) {
    				doFilterNestedErrorDispatch(httpRequest, httpResponse, filterChain);
    				return;
    			}
    
    			// Proceed without invoking this filter...
    			filterChain.doFilter(request, response);
    		}
    		else {
    			// Do invoke this filter...
    			request.setAttribute(alreadyFilteredAttributeName, Boolean.TRUE);
    			try {
    				doFilterInternal(httpRequest, httpResponse, filterChain);
    			}
    			finally {
    				// Remove the "already filtered" request attribute for this request.
    				request.removeAttribute(alreadyFilteredAttributeName);
    			}
    		}
    	}
    

`alreadyFilteredAttributeName`会获取当前 filter的名称,
若`hasAlreadyFilteredAttribute`=`true`, 即已经调用过这条过滤器, 则不进行重复调用, 否则将其标记后进行调用

开始对`/forward`鉴权

![image-20221109150907038](https://image.3001.net/images/20221111/1668133502_636db27e2f4a37e5cf872.png!small)

对`/forward`鉴权,`check()`源码如下：

    
    
    @Override
    	public AuthorizationDecision check(Supplier<Authentication> authentication, HttpServletRequest request) {
    		if (this.logger.isTraceEnabled()) {
    			this.logger.trace(LogMessage.format("Authorizing %s", request));
    		}
    		for (RequestMatcherEntry<AuthorizationManager<RequestAuthorizationContext>> mapping : this.mappings) {
    
    			RequestMatcher matcher = mapping.getRequestMatcher();
    			MatchResult matchResult = matcher.matcher(request);
    			if (matchResult.isMatch()) {
    				AuthorizationManager<RequestAuthorizationContext> manager = mapping.getEntry();
    				if (this.logger.isTraceEnabled()) {
    					this.logger.trace(LogMessage.format("Checking authorization on %s using %s", request, manager));
    				}
    				return manager.check(authentication,
    						new RequestAuthorizationContext(request, matchResult.getVariables()));
    			}
    		}
    		this.logger.trace("Abstaining since did not find matching RequestMatcher");
    		return null;
    	}
    

由于在`SecurityConfig.java`中已配置`.antMatchers("/forward").permitAll()`,
故`check()`直接跳转到`permitAllAuthorzationManager`, 验证直接通过, 相当于无权限验证。

![image-20221109154053967](https://image.3001.net/images/20221111/1668133550_636db2ae95cde01cf857f.png!small)

`/forword`请求更新为`/admin`请求后, 在`processRequest(request,response,state)`处进入处理调用

而后跟进到调用过滤器处, 为

    
    
    filterChain.doFilter(request, response);
    // invoke:711, ApplicationDispatcher (org.apache.catalina.core)
    

跟进,
运行到处理`org.springframework.security.web.access.intercept.AuthorizationFilter`过滤器处。

![image-20221109174824401](https://image.3001.net/images/20221111/1668133710_636db34e17def3125326b.png!small)

跟进, 看看与直接访问`/admin`的区别。

![image-20221109180418267](https://image.3001.net/images/20221111/1668133866_636db3ea59091e3702946.png!small)

 **`Proceed without invoking this filter...`**

破案...

## 成因总结

`forward`方法执行跳转, 且权限为`permitAll`. 而又有`OncePerRequestFilter`的条件,
只有一次使用`org.springframework.security.web.access.intercept.AuthorizationFilter`鉴权的机会,
该机会直接被浪费. 跳转`/admin`后过滤器无法进行处理, 从而越权。

## 修复方案

禁用`OncePerRequestFilter`功能或保证访问`/forward`跳转的目标网页所需的权限小于访问`/forward`的权限。

官方的修复方案是在`AuthorizationFilter.java`中新增了一个判断, 判断是否在 **当前**`request`中使用过。

    
    
    /*
    * verify whether the filter has been set observeOncePerRequest = true and applied
    */
    if (this.observeOncePerRequest && isApplied(request)) {
        chain.doFilter(request, response);
        return;
    } 
    
    if (skipDispatch(request)) {
        chain.doFilter(request, response);
        return;
    }
    
    String alreadyFilteredAttributeName = getAlreadyFilteredAttributeName();
    request.setAttribute(alreadyFilteredAttributeName, Boolean.TRUE);
    try {
        this.authorizationManager.verify(this::getAuthentication, request);
        chain.doFilter(request, response);
    }
    finally {
        request.removeAttribute(alreadyFilteredAttributeName);
    	}
    }
    

