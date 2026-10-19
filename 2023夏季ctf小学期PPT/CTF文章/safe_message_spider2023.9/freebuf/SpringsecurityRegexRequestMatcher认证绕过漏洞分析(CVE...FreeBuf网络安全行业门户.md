## ****前言****

Spring Security 是 Spring 家族中的一个安全管理框架，在 Spring
Security特定版本中存在一处身份认证绕过漏洞(CVE-2022-22978)。由于RegexRequestMatcher正则表达式配置权限的特性，当在Spring
Security中使用RegexRequestMatcher且规则中包含带点号的正则表达式时，攻击者可以通过构造恶意数据包绕过身份认证。

##  ** **影响版本****

Spring Security 5.5.x < 5.5.7

Spring Security 5.6.x < 5.6.4

##  ** **环境构建****

###  ** **目录结构****

![](https://image.3001.net/images/20220609/1654754359_62a18c37c6486bc6a5c76.png!small)

 ** **cc.saferoad.controller.Demo****

    
    
    package cc.saferoad.controller;
    ​
    import org.springframework.web.bind.annotation.GetMapping;
    import org.springframework.web.bind.annotation.RestController;
    ​
    @RestController
    public class Demo {
       @GetMapping("/admin/*")
       public String Manage(){
           return "Manage page";
      }
    ​
       @GetMapping("/")
       public String User(){
           return "Hello bro";
      }
    }

 ** **cc.saferoad.config.SpringSecurityConfig****

自定义配置类。

    
    
    package cc.saferoad.config;
    ​
    import org.springframework.context.annotation.Configuration;
    import org.springframework.security.config.annotation.web.builders.HttpSecurity;
    import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
    import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
    ​
    @Configuration
    @EnableWebSecurity
    public class SpringSecurityConfig extends WebSecurityConfigurerAdapter {
    ​
       @Override
       protected void configure(HttpSecurity httpSecurity) throws Exception{
           httpSecurity.authorizeRequests().regexMatchers("/admin/.*").authenticated();
      }
    }

 ** **cc.saferoad.cve202222978.Cve202222978Application****

    
    
    package cc.saferoad.cve202222978;
    ​
    import org.springframework.boot.SpringApplication;
    import org.springframework.boot.autoconfigure.SpringBootApplication;
    ​
    @SpringBootApplication(scanBasePackages = {"cc.saferoad"})
    public class Cve202222978Application {
    ​
       public static void main(String[] args) {
           SpringApplication.run(Cve202222978Application.class, args);
      }
    ​
    }

 ** **cc.saferoad.cve202222978.RegexRequestMatcherTests****

单元测试类，用于后面具体分析流程代码。

    
    
    package cc.saferoad.cve202222978;
    ​
    import org.junit.jupiter.api.Test;
    import org.springframework.mock.web.MockHttpServletRequest;
    import org.springframework.security.web.util.matcher.RegexRequestMatcher;
    import static org.assertj.core.api.Assertions.assertThat;
    ​
    public class RegexRequestMatcherTests {
    ​
       @Test
       public void matchesWithLineFeed() {
           RegexRequestMatcher matcher = new RegexRequestMatcher(".*", null);
           MockHttpServletRequest request = new MockHttpServletRequest("GET", "/blah%0d");
           request.setServletPath("/blah\r");
           assertThat(matcher.matches(request)).isTrue();
      }
    }

 ** **pom.xml****

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
       <modelVersion>4.0.0</modelVersion>
       <parent>
           <groupId>org.springframework.boot</groupId>
           <artifactId>spring-boot-starter-parent</artifactId>
           <version>2.7.0</version>
           <relativePath/> <!-- lookup parent from repository -->
       </parent>
       <groupId>cc.saferoad</groupId>
       <artifactId>CVE-2022-22978</artifactId>
       <version>0.0.1-SNAPSHOT</version>
       <packaging>war</packaging>
       <name>CVE-2022-22978</name>
       <description>CVE-2022-22978</description>
       <properties>
           <java.version>1.8</java.version>
           <spring-security.version>5.6.3</spring-security.version>
           <!--注意指定有漏洞的版本,覆盖掉默认版本-->
       </properties>
       <dependencies>
           <dependency>
               <groupId>org.springframework.boot</groupId>
               <artifactId>spring-boot-starter-web</artifactId>
           </dependency>
    ​
           <dependency>
               <groupId>org.springframework.boot</groupId>
               <artifactId>spring-boot-starter-tomcat</artifactId>
               <scope>provided</scope>
           </dependency>
           <dependency>
               <groupId>org.springframework.boot</groupId>
               <artifactId>spring-boot-starter-test</artifactId>
               <scope>test</scope>
           </dependency>
           <dependency>
               <groupId>org.springframework.boot</groupId>
               <artifactId>spring-boot-starter-security</artifactId>
           </dependency>
       </dependencies>
    ​
       <build>
           <plugins>
               <plugin>
                   <groupId>org.springframework.boot</groupId>
                   <artifactId>spring-boot-maven-plugin</artifactId>
                   <configuration>
                       <jvmArguments>
                          -Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=8989
                       </jvmArguments>
                       <!--远程调试配置,可忽略-->
                   </configuration>
               </plugin>
           </plugins>
       </build>
    ​
    </project>

配置完成后，启动SpringBoot应用，访问[ _http://localhost:8080_](http://localhost:8080)

![](https://image.3001.net/images/20220609/1654754585_62a18d19cacee29313af0.png!small)

访问/admin/路由会提示403。

![](https://image.3001.net/images/20220609/1654754645_62a18d55e00550346a0dd.png!small)

或者使用笔者构建的环境
[_https://github.com/DeEpinGh0st/CVE-2022-22978_](https://github.com/DeEpinGh0st/CVE-2022-22978)

##  ** **漏洞复现****

正常访问/admin/下任何路由均会提示403。

![](https://image.3001.net/images/20220609/1654754935_62a18e77eaa357ddd46f5.png!small)

此时在/admin/anything路由中插入%0a或者%0d,即可绕过验证访问页面。

![](https://image.3001.net/images/20220609/1654754957_62a18e8d8e269766492b7.png!small)

##  ** **漏洞分析****

使用上文中的单元测试样例，首先进行RegexRequestMatcher实例化。

![](https://image.3001.net/images/20220609/1654755041_62a18ee173b245bd99a12.png!small)

根据构造参数初始化正则表达式及httpMethod属性，注意此处Pattern.compile参数值，对照JDK API文档看一下具体参数含义。

![](https://image.3001.net/images/20220609/1654755065_62a18ef97cd2c25c1d3f4.png!small)

其中第一个参数表示要编译的表达式，而第二个参数则是指定表达式的具体匹配模式，具体可选值有

CASE_INSENSITIVE, MULTILINE, DOTALL, UNICODE_CASE, CANON_EQ, UNIX_LINES,
LITERAL, UNICODE_CHARACTER_CLASS and COMMENTS.

在RegexRequestMatcher中由于caseInsensitive设置为了false，所以此处的值为 0 代表使用默认状态，

随后进入RegexRequestMatcher:matches中在获取到传入的路由后进行路由匹配。

![](https://image.3001.net/images/20220609/1654755086_62a18f0e9c11e45f461dd.png!small)

此处我们需要注意一个点。

![](https://image.3001.net/images/20220609/1654755112_62a18f28d3c8329bcc0cf.png!small)

在默认情况下正则表达式中，是不会匹配\r\n换行符的，所以RegexRequestMatcher在进行正则匹配时不会处理\r\n从而可以绕过需要身份认证的页面。

![](https://image.3001.net/images/20220609/1654755135_62a18f3fcf8827727c02b.png!small)

##  ** **修复****

在清楚具体绕过原理后，来看一下官方提交的修复措施。

![](https://image.3001.net/images/20220609/1654755164_62a18f5ccf4e67b9569b5.png!small)

在5.6.4的diff中官方将DEFAULT默认匹配模式改为了Pattern.DOTALL点阵模式。

![](https://image.3001.net/images/20220609/1654755186_62a18f72bbf1361f8ec2a.png!small)

在点阵模式下表达式会匹配\r\n等终止符，而在API文档中官方也进行了说明 ** **默认情况下，此表达式与行终止符不匹配。****

而后也将Pattern.DOTALL在开启大小写区分的情况下进行了组合,这样无论是否开启大小写模式均使用点阵模式进行匹配。

##  ** **参考****

 _JDK8 API_

[ _5.6.3...5.6.4 Diff_](https://github.com/spring-projects/spring-security/compare/5.6.3...5.6.4)

[ _Regexp-syntax_](https://www.runoob.com/regexp/regexp-syntax.html)

  

