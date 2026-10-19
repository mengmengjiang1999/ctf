## 1.介绍

最近写了个小玩意儿，主要功能为用户信息管理，例如新增 删除 添加等。但在没写过滤之前，全是xss

所以拿出来给大家进行简单分析，后续通过动态代理进行过滤。

![1635317940_6178f8b4927fc29f9b5b0.png!small](https://image.3001.net/images/20211027/1635317940_6178f8b4927fc29f9b5b0.png!small)

## 2.代码分析

这里就只分析用户添加的页面了，可以看到在未做任何过滤的情况触发XSS

![1635318333_6178fa3d3afbd359eb7c6.png!small](https://image.3001.net/images/20211027/1635318333_6178fa3d3afbd359eb7c6.png!small)![1635318350_6178fa4ee99b3f091a9f8.png!small](https://image.3001.net/images/20211027/1635318350_6178fa4ee99b3f091a9f8.png!small)

在add.jsp页面发现了Servlet

![1635318472_6178fac8ae1c09d174c75.png!small](https://image.3001.net/images/20211027/1635318472_6178fac8ae1c09d174c75.png!small)

之后跟进该Servlet，通过获取用户输入进行发送到Service，Service在发送到Dao进行处理![1635318527_6178faff9e02fa45ba010.png!small](https://image.3001.net/images/20211027/1635318527_6178faff9e02fa45ba010.png!small)![1635318628_6178fb649bf28522ac167.png!small](https://image.3001.net/images/20211027/1635318628_6178fb649bf28522ac167.png!small)

Dao层用的是JDBCtemplate实现，经过测试发现如果使用PreparedStatement连接数据库的话，PreparedStatement会过滤掉常见的XSS代码

    
    
    <script>alert(xss)</script><img src=x onerror=alert(1) />...

但是PreparedStatement过滤一般常用的确实可以，但是鸡肋一点的话，就很轻松绕过了。

    
    
    <input onmouseover=alert(1)>//鸡肋点的语句...

![1635318694_6178fba608924b8a0c10a.png!small](https://image.3001.net/images/20211027/1635318694_6178fba608924b8a0c10a.png!small)

在AddServlet可以看到，最后进行了重定向，而ListUser就是首页

resp.sendRedirect("/Students/ListUser");

跟进AddServlet之后，可以发现该Servlet执行了findALL()，该方法其实就是service层-->Dao层的查询全部用户信息。并存储到了list中。之后设置setAttribute之后进行了请求转发到list.jsp

![1635319082_6178fd2a726f07e6959ae.png!small](https://image.3001.net/images/20211027/1635319082_6178fd2a726f07e6959ae.png!small)

跟进list.jsp之后，可以发现将用户的信息使用JSTL遍历出并显示。全程毫无过滤。

![1635319234_6178fdc270c2c1841e74d.png!small](https://image.3001.net/images/20211027/1635319234_6178fdc270c2c1841e74d.png!small)

## 3.Filter动态代理过滤

这里本人简单写了一下过滤。只过滤了< >标签。后续可以根据自己需求进行改进。

写的很简单，就不多说了。

    
    
    @WebFilter("/*")
    public class MyFilter implements Filter {
        @Override
        public void init(FilterConfig filterConfig) throws ServletException {
    
        }
    
        @Override
        public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
            ServletRequest servlet = (ServletRequest)Proxy.newProxyInstance(servletRequest.getClass().getClassLoader(), servletRequest.getClass().getInterfaces(), new InvocationHandler() {
                @Override
                public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
    
                    if(method.getName().equals("getParameter")){
                        String value = (String)method.invoke(servletRequest,args);//获取输入的value
                        value = value.replaceAll(">","*");//将值替换
                        value = value.replaceAll("<","*");
                        return value;
                    }else{
                        System.out.println("没有匹配成功");
                    }
    
                    return method.invoke(servletRequest,args);
                }
            });
            filterChain.doFilter(servlet,servletResponse);
        }
    
        @Override
        public void destroy() {
    
        }
    }

之后可以发现过滤成功

![1635319548_6178fefc21929ae6af153.png!small?1635319561465](https://image.3001.net/images/20211027/1635319548_6178fefc21929ae6af153.png!small?1635319561465)

