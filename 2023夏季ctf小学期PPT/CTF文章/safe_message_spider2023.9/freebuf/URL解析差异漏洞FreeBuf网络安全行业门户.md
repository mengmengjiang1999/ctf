# Shiro权限绕过漏洞

## 环境

  * Shiro 1.5.1

  * Spring Boot 2.2.2.RELEASE

> 使用高版本Spring boot进行复现时复现失败，猜测是由于修改了Spring MVC的路径匹配策略导致导致的，希望有大佬解惑

`MyRealm.java`

    
    
    public class MyRealm extends AuthorizingRealm {
        @Override
        protected AuthorizationInfo doGetAuthorizationInfo(PrincipalCollection principals) {
            return null;
        }
        @Override
        protected AuthenticationInfo doGetAuthenticationInfo(AuthenticationToken token) throws AuthenticationException {
            String username = (String) token.getPrincipal();
            if (!"admin".equals(username)) {
                throw new UnknownAccountException("账户不存在!");
            }
            return new SimpleAuthenticationInfo(username, "123456", getName());
        }
    }
    

`ShiroConfig.java`

    
    
    @Configuration
    public class ShiroConfig {
        @Bean
        MyRealm myRealm() {
            return new MyRealm();
        }
        @Bean
        SecurityManager securityManager() {
            DefaultWebSecurityManager manager = new DefaultWebSecurityManager();
            manager.setRealm(myRealm());
            return manager;
        }
        @Bean
        ShiroFilterFactoryBean shiroFilterFactoryBean() {
            ShiroFilterFactoryBean bean = new ShiroFilterFactoryBean();
            bean.setSecurityManager(securityManager());
            bean.setLoginUrl("/login");
            bean.setSuccessUrl("/index");
            bean.setUnauthorizedUrl("/unauthorizedurl");
            Map<String, String> map = new LinkedHashMap();
            map.put("/login", "anon");
            map.put("/index", "anon");
            map.put("/admin", "authc");
            bean.setFilterChainDefinitionMap(map);
            return bean;
        }
    }
    

`Controller.java`

    
    
    @RestController
    public class Controller {
        @RequestMapping("/login")
        public String login(String username, String password) {
            Subject subject = SecurityUtils.getSubject();
            try {
                subject.login(new UsernamePasswordToken(username, password));
                return "登录成功";
            } catch (AuthenticationException e) {
                e.printStackTrace();
                return "登录失败";
            }
        }
        @RequestMapping("/admin")
        public String admin() {
            return "admin";
        }
        @RequestMapping("/index")
        public String index() {
            return "index";
        }
    }
    

## 复现

  * 访问`anon`权限页面  
![image-20220314170505265](https://image.3001.net/images/20220314/1647268931_622f54434b344a343d3fa.png!small)  
可以正常访问

  * 访问`authc`权限页面  
![image-20220314170630490](https://image.3001.net/images/20220314/1647268932_622f5444cf045cfc8e52f.png!small)  
重定向到登录页面

  * 构造`url`绕过身份验证  
![image-20220314170801332](https://image.3001.net/images/20220314/1647268934_622f5446594824b5e4c13.png!small)  
未授权访问成功

## 分析

### Shiro验证

详细的调用流程网上很多，这里只看关键的几个地方

首先是经过`decodeAndCleanUriString`处理，将`uri`以`;`截断，`uri`变为`/xxx/..`![image-20220314173422002](https://image.3001.net/images/20220314/1647268935_622f5447e4271477a7939.png!small)

接着是在`getChain`中以`Shiro`的路由过滤规则，对`uri`的权限做验证![image-20220314174201533](https://image.3001.net/images/20220314/1647268937_622f5449761f760c00f75.png!small)

由于`/xxx/..`不会匹配上`/admin`，所以在`Shiro`的权限验证中通过

### Spring boot验证

经过`Shiro`的验证后，请求进入到`Spring boot`中进行验证，但由于传入`Spring
boot`的`uri`是初始的`uri(/xxx/..;/admin)`，而不是经过`Shiro`过滤的`uri(/xxx/..)`，使得请求被解析为对`/admin`的访问，从而绕过了`Shiro`的权限验证![image-20220314175251244](https://image.3001.net/images/20220314/1647268938_622f544aef78183995fb3.png!small)

# Tomcat URL解析漏洞

`Shiro`权限绕过漏洞的原理就是`Shiro`和`Spring
boot`对`url`解析的差异，在`Shiro`中`/xxx/..;/admin`被解析为`/xxx/..`绕过了权限验证，而在`Spring
boot`中`/xxx/..;/admin`又被解析成了对`/admin`的访问，造成了未授权访问

与之类似的还有`Tomcat URL`解析漏洞

## URL解析

`Servlet`中有以下几种`url`解析函数

  * request.getRequestURL()

  * request.getRequestURI()

  * request.getContextPath()

  * request.getServletPath()

  * request.getPathInfo()

解析效果如图：![image-20220314183504247](https://image.3001.net/images/20220314/1647268940_622f544c2df5fb67f28ac.png!small)

  * getRequestURL() 返回完整的路径

  * getRequestURI() 返回host地址之后的路径

  * getContextPath() 返回项目名

  * getServletPath() 返回项目名之后的路径  
如：![image-20220314184100560](https://image.3001.net/images/20220314/1647268940_622f544ce4bb80ac27cc0.png!small)

  * getPathInfo() 返回`servlet`后的路径  
如：![image-20220314193919624](https://image.3001.net/images/20220314/1647268941_622f544d8e54708819438.png!small)`servlet`配置信息为`@WebServlet(name
= "helloServlet", value = "/hello-servlet/*")`

### 解析测试

  * `demo_war_exploded/./././index.jsp`![image-20220314200004665](https://image.3001.net/images/20220314/1647268942_622f544ea6314d932fac2.png!small)

  * `demo_war_exploded/asdfas/../index.jsp`![image-20220314200214983](https://image.3001.net/images/20220314/1647268943_622f544fde9fe7eaaca66.png!small)

  * `;asdfas/index.jsp`![image-20220314200323495](https://image.3001.net/images/20220314/1647268945_622f54514f38b44c23e44.png!small)

可以看出，在使用这几种`url`地址访问时，最终访问的都是`index.jsp`，因此可以利用这种方法绕过权限检测

如：`http://localhost:8080/demo_war_exploded/admin/index.jsp`为敏感信息时，可以尝试这样绕过

    
    
    http://localhost:8080/demo_war_exploded/admin/./index.jsp
    http://localhost:8080/demo_war_exploded/;asd/admin/index.jsp
    http://localhost:8080/demo_war_exploded/admin/asd/../index.jsp
    

## Nginx

以`Nginx`+`Tomcat`为例，设置`admin`目录为禁止访问目录:

    
    
    location ^~ /admin {
        deny all;
        return 403;
    }
    

直接访问`admin/index.jsp`:![image-20220314214202093](https://image.3001.net/images/20220314/1647268946_622f5452de00d17a15748.png!small)

尝试利用上述方式进行绕过：

  * ![image-20220314214308586](https://image.3001.net/images/20220314/1647268948_622f545426bb8d8bd63c5.png!small)

  * ![image-20220314214502651](https://image.3001.net/images/20220314/1647268949_622f54555622d0b3e808e.png!small)

  * ![image-20220314214601960](https://image.3001.net/images/20220314/1647268950_622f5456b2ec748dc490d.png!small)

  * ![image-20220314214647836](https://image.3001.net/images/20220314/1647268952_622f54581842c25149b1e.png!small)

可以看出，在`url`中插入`;`，可以在`Nginx`解析`url`地址时将地址截断，使其绕过匹配，将请求转发到`tomcat`上绕过权限限制

