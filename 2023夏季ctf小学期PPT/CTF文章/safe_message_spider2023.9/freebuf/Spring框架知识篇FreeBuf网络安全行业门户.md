本期Java代码审计Spring框架知识篇将讲述Spring构造POC要必备的知识。

 **0X01 传统Java代码命令执行**

 **1.知识说明**

由于业务需求，程序有可能要执行系统命令的功能，但如果执行的命令用户可控，业务上有没有做好限制，就可能出现命令执行漏洞。

但Spring框架漏洞则是某组件可能存在解析执行系统命令代码的方法并根据命令执行方法（Runtime.getRuntime().exec(cmd)）构造执行系统命令的POC，如果命令执行成功，造成Spring远程命令执行漏洞。

 **2.例子**

此处以getRuntime为例,Runtime.getRuntime().exec(cmd)执行系统命令并弹出计算器。

示例代码如下:

    
    
    import java.io.IOException;
    
    public class Cmd {//在linux系统下运行计算器
    
       public static void main(String[] args){
    
           String cmd = "gnome-calculator";//gnome-calculator计算器进程名
    
           try {
    
               Process ps = Runtime.getRuntime().exec(cmd);//执行命令
    
           } catch (IOException e) {
    
               e.printStackTrace();
    
           }
    
       }
    
    }
    

系统命令的执行结果：

![结果.webp.jpg](https://image.3001.net/images/20180815/1534322249_5b73e649116e6.jpg!small)

此方法将产生一个本地的进程，并返回一个Process子类的实例（注意：Runtime.getRuntime().exec(cmd)返回的是

一个Process类的实例）该实例可用于控制进程或取得进程的相关信息。

![信息.webp.jpg](https://image.3001.net/images/20180815/1534322275_5b73e663838fe.jpg!small)

由于调用 Runtime.exec()方法所创建的子进程没有自己的终端或控制台，因此该子进程的标准IO（如stdin,stdou,stderr）都通过

Process.getOutputStream() 输入流

Process.getInputStream() 输出流

Process.getErrorStream() 错误流

等方法重定向给它的父进程了。

用户需要用这些Stream来向子进程输入数据或获取子进程的输出，使用getInputStream()去读取命令执行结果：

    
    
    import java.io.BufferedReader;
    
    import java.io.IOException;
    
    import java.io.InputStream;
    
    import java.io.InputStreamReader;
    
    public class Cmd {
    
       public static void main(String[] args){
    
           String cmd = "ifconfig";
    
           try {
    
               Process run = Runtime.getRuntime().exec(cmd);//执行
    
               InputStream is = run.getInputStream();//取得执行结果输出流
    
               InputStreamReader isr =new InputStreamReader(is);//读输出流读取
    
               BufferedReader br=new BufferedReader(isr);//缓冲器读取
    
               String line=null;
    
               while((line=br.readLine())!=null)
    
               {
    
                   System.out.println(line);
    
               }
    
           } catch (IOException e) {
    
               e.printStackTrace();
    
           }
    
       }
    
    }
    

执行结果：

![执行.webp.jpg](https://image.3001.net/images/20180815/1534322315_5b73e68b42a7e.jpg!small)

 **3.补充**

例如要执行带参数的命令等，exec有下列的方法重载：

    
    
    public Process exec(String var1) throws IOException {
    
       return this.exec((String)var1, (String[])null, (File)null);
    
    }
    
    public Process exec(String var1, String[] var2) throws IOException {
    
       return this.exec((String)var1, var2, (File)null);
    
    }
    
    public Process exec(String var1, String[] var2, File var3) throws IOException {
    
       if (var1.length() == 0) {
    
           throw new IllegalArgumentException("Empty command");
    
       } else {
    
           StringTokenizer var4 = new StringTokenizer(var1);
    
           String[] var5 = new String[var4.countTokens()];
    
           for(int var6 = 0; var4.hasMoreTokens(); ++var6) {
    
               var5[var6] = var4.nextToken();
    
           }
    
           return this.exec(var5, var2, var3);
    
       }
    
    }
    
    public Process exec(String[] var1) throws IOException {
    
       return this.exec((String[])var1, (String[])null, (File)null);
    
    }
    
    public Process exec(String[] var1, String[] var2) throws IOException {
    
       return this.exec((String[])var1, var2, (File)null);
    
    }
    
    public Process exec(String[] var1, String[] var2, File var3) throws IOException {
    
       return (new ProcessBuilder(var1)).environment(var2).directory(var3).start();
    
    }
    

**0X02 SpEL表达式**

 **1.知识说明**

在Spring框架漏洞中大多数的远程命令执行漏洞，都不是直接解析执行系统命令代码，而是解析SpEL表达式。这时要构造的就是包含执行系统命令代码的SpEL表达式。

 **2.SpEL表达式介绍**

Spring表达式语言全称Spring Expression
Language是一种表达式语言，是一种可以与一个基于Spring的应用程序中的运行时对象交互。SpEL表达式是一种简化开发的表达式，通过使用表达式来简化开发，减少一些逻辑、配置的编写。SpEL是单独模块，只依赖于core模块，不依赖于其他模块，可以单独使用。

 **3.功能特性**

SpEL支持以下的一些特性：

字符表达式

布尔和关系操作符

正则表达式

类表达式

访问properties，arrays，lists，maps等集合

方法调用

关系操作符

赋值

调用构造器

Bean对象引用

创建数组

三元操作符

变量

用户自定义函数

集合选择

 **4.SpEL基础表达式用法**

用来计算String类型的字面值：

    
    
    #{'HELLO'}
    

为了在SpEL中表达使用Java的Runtime类，可以调用T()运算符所得到类型的静态方法。

    
    
    T(java.lang.Runtime).getRuntime()
    

计算正则表达式：

    
    
    #{admin.email matches '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9._%+-]+\\.com'}
    

0X03 SpEL表达式与命令执行组合

此处以SpEL表达式与getRuntime组合为例,T(java.lang.Runtime).getRuntime().exec('gnome-calculator')SpEL表达式中包含

执行系统命令并由parseExpression解析弹出计算器

示例代码如下：

    
    
    import org.springframework.expression.ExpressionParser;
    
    import org.springframework.expression.spel.standard.SpelExpressionParser;
    
    public class Sdemo {
    
           public static void main(String[] args){
    
             ExpressionParser parser = new SpelExpressionParser();
    
             String expression = "T(java.lang.Runtime).getRuntime().exec('gnome-calculator')";//构造好的SpEL表达式
    
             String result = parser.parseExpression(expression).getValue().toString();//解析SpEL
    
           }
    
    }
    

系统命令的执行结果：

![哇.webp.jpg](https://image.3001.net/images/20180815/1534322525_5b73e75d5ab45.jpg!small)

 **0X04 小总结**

此篇讲述Spring框架构造POC必备的知识，如java命令执行函数，SpEL表达式使用、两者的配合使用构造Spring框架的POC。下期斗哥将带来Java代码审计Spring框架实例篇将以Spring框架漏洞中的某个远程命令执行漏洞的Demo。根据审计思路来分析，深入学习Spring框架的代码审计。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180815/1534322578_5b73e792dbabe.jpg!small)

