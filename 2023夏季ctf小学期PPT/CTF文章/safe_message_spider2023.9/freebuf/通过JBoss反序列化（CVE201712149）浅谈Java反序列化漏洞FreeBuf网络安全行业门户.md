***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **前段时间学校学习J2EE，用到了jboss，顺便看了下jboss的反序列化，再浅谈下反序列化漏洞。**

![Clipboard
Image.png](https://image.3001.net/images/20180313/15209154598921.png!small)  

Java序列化，简而言之就是把java对象转化为字节序列的过程。而反序列话则是再把字节序列恢复为java对象的过程，然而就在这一转一变得过程中，程序员的过滤不严格，就可以导致攻击者恶意构造的代码的实现。

举个简单的例子，jboss的反序列化漏洞出现在jboss\server\all\deploy\httpha-invoker.sar\invoker.war\WEB-INF\classes\org\jboss\invocation\http\servlet目录下的ReadOnlyAccessFilter.class文件中的doFilter中。

    
    
    public void doFilter(ServletRequest request,ServletResponse response,FilterChain chain)
      throw IOException,ServletException
    {
      HttpServletRequest httpRequest=(HttpServletRequest)request;
      Principal user=httpRequest.getUserPrincipal();
      if((user=null)&&(this.readOnlyContext!=null))
      { 
        ServletInputStream sis=request.getInputStream();
        ObjectInputStream ois=new ObjectInputStream(sis);
        MarshalledInvocation mi=null;
        try
        {
          mi=(MarshalledInvocation)ois.readObject();
        } 
        catch(ClassNotFountException e)
        {
          throw new ServletException("Failed to read MarshalledInvocation",e);
        }
        request.serAttribute("MarshalledInvocation",mi);
    
        mi.setMethodMap(this.namingMethodMap);
        Method m=mi.getMethod();
        if(m!=null){
          validateAccess(m,mi)
        }
      }
      chain.doFilter(request,response);
    }

程序获取http数据保存到了httpRequest中，序列化后保存到了ois中，然后没有进行过滤操作，直接使用了readObject（）进行了反序列化操作保存到了mi变量中，这其实就是一个典型的java反序列化漏洞。

复现jboss反序列化漏洞（CVE-2017-12149）

靶机 xp_sp3 10.10.1.34

CVE-2017-12149的主要影响范围是jbossas 5.x和6.x，下载jboss5.1.0
GA并安装（需要有java环境）。运行时如果发现只能通过localhost或者127.0.0.1进行访问，可以通过运行时增加命令 run.bat -b
0.0.0.0 ，或新建start.bat 内容run.bat -b 0.0.0.0

![Clipboard
Image.png](https://image.3001.net/images/20180313/15209049971293.png!small)  

当出现这个的时候说明已经部署好了，可以进行访问了

![Clipboard
Image.png](https://image.3001.net/images/20180313/15209050239513.png!small)  

可以访问到页面，

访问10.10.1.134:8080/invoker/readonly

![Clipboard
Image.png](https://image.3001.net/images/20180313/15209050298823.png!small)  

出现此页面则可以判断含有java反序列化漏洞

进行漏洞利用，我使用的是香草反序列化工具，网上还有很多工具，包括ysoserial，都可以进行漏洞利用

![Clipboard
Image.png](https://image.3001.net/images/20180313/1520905037794.png!small)  

![Clipboard
Image.png](https://image.3001.net/images/20180313/15209050402908.png!small)  

列出了文件目录

关于修复漏洞，建议如果不使用此组件，可以删除。或添加代码，进行监控。

 ***本文作者：哲哥哥丶，转载请注明来自FreeBuf.COM**

