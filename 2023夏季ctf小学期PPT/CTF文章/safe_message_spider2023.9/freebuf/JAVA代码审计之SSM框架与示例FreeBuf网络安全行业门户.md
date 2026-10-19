**Java SSM框架代码审计、** **SSM框架各个成之间的关系**

    
    
    https://foreti.me/2017/07/20/ssm-framework/

## 审计的触发点web.xml文件  

tomcat启动后会自动加载web.xml中的配置，首先是生成DispatcherServlet类，将我们的请求转发至我们的SpringMVC中去，交由我们SpringMVC的Controller来进行接下来的处理。生成DispatcherServlet时的初始化参数contextConfigLocation参数，Spring会根据这个参数去加载所有逗号分隔的xml文件，如果没有这个参数，Spring默认加载WEB-INF/DispatcherServlet-servlet.xml文件web.xml中的几项配置

![](https://image.3001.net/images/20200522/1590124304_5ec75f10834b7.png!small)

<!--spring 的监听器-->

![](https://image.3001.net/images/20200522/1590124423_5ec75f8767769.png!small)

<!-- spring 主配置文件的 路径 和名字 -->

![](https://image.3001.net/images/20200522/1590124378_5ec75f5aed340.png!small)

<!-- 过滤器 编码格式 -->

![](https://image.3001.net/images/20200522/1590124484_5ec75fc4e533d.png!small)

## applicationContext.xml

applicationContext.xml：是Spring的核心配置文件，例如生成Bean，配置连接池，生成sqlSessionFactory

sqlSessionFactory：SqlSessionFactory是MyBatis的关键对象,SqlSessionFactory对象的实例可以通
SqlSessionFactoryBuilder对象类获得,而SqlSessionFactoryBuilder则可以从XML配置文件或一个预先定制的Configuration的实例构建出SqlSessionFactory的实例

SqlSession：SqlSession是MyBatis的关键对象，可以用SqlSession实例来直接执行被映射的SQL语句

mybatis框架主要是围绕着SqlSessionFactory进行的，创建过程大概如下

定义一个Configuration对象，其中包含数据源、事务、mapper文件资源以及影响数据库行为属性设置settings通过配置对象，则可以创建一个SqlSessionFactoryBuilder对象

通过 SqlSessionFactoryBuilder 获得SqlSessionFactory 的实例。

SqlSessionFactory 的实例可以获得操作数据的SqlSession实例，通过这个实例对数据库进行操作。  

而在 MyBatis-Spring 中，则使用 SqlSessionFactoryBean 来创建。

##
![](https://image.3001.net/images/20200522/1590124676_5ec76084d00b6.png!small)SSM框架审计之SQL注入漏洞

打开项目到登录窗口，登录发送数据请求的URL，将/login在IDEA中使用crtl+shift+f进行搜索，找到控制器@RequestMapping(value
= "/login",method = RequestMethod.POST)

![](https://image.3001.net/images/20200522/1590124791_5ec760f733b4e.png!small)先看下是否有过滤器防止SQL注入，在web.xml中找到filter标签，crtl+左键进入到对应的过滤器类中
![](https://image.3001.net/images/20200522/1590124819_5ec761139754f.png!small)这里使用了动态代理来对request域中的数据进行过滤等操作，继续跟进  

![](https://image.3001.net/images/20200522/1590124850_5ec76132e6c4b.png!small)动态代理中对request域中的数据进行了XSS的过滤，并进行了实体化编码修改数据到request域中，并没有对SQL语句进行过滤等操作  

![](https://image.3001.net/images/20200522/1590124888_5ec761586620c.png!small)回到控制器中，跟进控制器中的login方法来到接口中，接口interface
IMemberService 定义了login方法，使用crtl+alt+b进入该接口实现类中  

![](https://image.3001.net/images/20200522/1590124916_5ec76174ef83e.png!small)该接口登录方法调用了memberDao.login方法，这里使用的是SSM框架，所以Dao层对应的方法都有相应的Map.xml中对应的SQL语句  

![](https://image.3001.net/images/20200522/1590124944_5ec76190d5d3f.png!small)Dao层接口，接口名字对应着Map文件，直接找对应的Map.xml文件即可，这里是MemberMap.xml  

![](https://image.3001.net/images/20200522/1590124972_5ec761ac01d84.png!small)这里使用了预编译没有对应的漏洞  

##
![](https://image.3001.net/images/20200522/1590125001_5ec761c99f497.png!small)**SSM框架审计之SQL注入漏洞(反向)**  

全局搜索${，因为mybatis存在注入的地方就是使用了该符号作为SQL语句拼接。  

**![](https://image.3001.net/images/20200522/1590125065_5ec76209e4f59.png!small)**找到该xml文件，文件名为GroupTopicMapper.xml，找对应的Dao文件即可，搜索GroupTopicDao，找到该文件，并且搜索之前xml语句的id值即为Dao中的方法名，找到如下  

![](https://image.3001.net/images/20200522/1590125098_5ec7622a0a763.png!small)
找到Dao文件之后需要找到对应的Service，这里使用crtl+alt+h找该方法在那里被调用过，找到如下文件  

![](https://image.3001.net/images/20200522/1590125124_5ec7624423353.png!small)仍然找改方法在那里被调用，使用crtl+alt+h，发现以下俩个crontoller调用了改方法  

![](https://image.3001.net/images/20200522/1590125146_5ec7625a790c9.png!small)这里使用crtl+alt+h查看该方法在那里调用，继续跟踪找到前端url，这里看下改方法的requestmapping中的值即可找到对应的url，只是这里并不存在SQL注入，可控的参数不会进入到语句中  

##
![](https://image.3001.net/images/20200522/1590125169_5ec7627148ee1.png!small)**SSM框架审计之xss漏洞**  

访问发布评论页面，点击提交数据，查看数据提交的uri  

![](https://image.3001.net/images/20200522/1590125229_5ec762adde4c2.png!small)之前看到web.xml中配置有过滤器，MVC执行顺序是先经过过滤器，在经过控制器，所以先去过滤器中查看是否有对应的处理  

![](https://image.3001.net/images/20200522/1590125259_5ec762cb058b8.png!small)使用了动态代理对request中的数据进行处理，跟进方法，这里获取参数值，并且对参数调用了cleanXSS进行过滤，找到cleanXSS方法  

![](https://image.3001.net/images/20200522/1590125286_5ec762e609551.png!small)cleanXSS方法中先调用dealScript和dealStyle方法对xss进行处理  

![](https://image.3001.net/images/20200522/1590125317_5ec76305105a6.png!small)这里对script标签和style标签进行了正则，并进行了实体化编码，但是只对正则匹配到了的xss进行了实体化编码，而且正则可以绕过，故存在xss漏洞  

![](https://image.3001.net/images/20200522/1590125342_5ec7631ed9add.png!small)回到cleaXSS方法中，对这俩个标签处理完之后，对事件进行了正则匹配并替换，在提交处查看处理后的结果  

![](https://image.3001.net/images/20200522/1590125368_5ec763380eb59.png!small)然后回到控制器中，crtl+shift+f搜索指定的路径即可，@respinseBody将方法返回值作为返回体中的内容  

![](https://image.3001.net/images/20200522/1590125393_5ec7635114d9e.png!small)跟进save方法，crtl+alt+b进入。这部分是对提交的内容的规范做判断  

![](https://image.3001.net/images/20200522/1590125421_5ec7636d901c8.png!small)跟进该方法  

![](https://image.3001.net/images/20200522/1590125460_5ec76394c63e2.png!small)crtl+alt+b进入方法后，这里是注解方式绑定mapper中的方法与provider中的方法绑定  

    
    
    https://blog.csdn.net/qq_39367438/article/details/83789614?depth_1-utm_source=distribute.pc_relevant.none-task&utm_source=distribute.pc_relevant.none-task  
    

@options的选项指定把获取到的主键值注入到 XXX（实体类） 的 id 属性。

![](https://image.3001.net/images/20200522/1590125520_5ec763d044b0f.png!small)方法中返回了sql语句

##
![](https://image.3001.net/images/20200522/1590125547_5ec763ebd7b93.png!small)SSRF漏洞代码审计

进入文章发布面，利用编辑器插入一个链接，保存的发送的数据的uri如下，在全局搜索该Url找到控制器

    
    
    http://localhost:8080/jeesns/article/save  
    

首先进行了拦截器进行校验用户是否进行登录，使用@valid进行数据校验

![](https://image.3001.net/images/20200522/1590125658_5ec7645ab9991.png!small)@Valid注解进行数据验证

前端发送数据包，获取uri，再idea重全局搜索/SSRF/task1

![](https://image.3001.net/images/20200522/1590125715_5ec76493ba6c5.png!small)从打开的连接获取一个
InputStream，可以从中得到 URL 请求的响应流。在调用这个方法时，会自动调用 URLConnection.connect()
方法，也就是建立连接。所以一旦调用 getInputStream() 连接就已经建立好了  

## XXE代码审计  

前端发送数据包，获取uri，再idea重全局搜索/xxe/simple  

![](https://image.3001.net/images/20200522/1590125788_5ec764dc2fd87.png!small)跟进parseXml方法，这里应该是解析xml文件的方法，这里设置了允许外部xml实体，使用Unmarshal解析了读入的xml文件，故产生漏洞  

![](https://image.3001.net/images/20200522/1590125819_5ec764fb4efb3.png!small)路径穿越漏洞  

上传个人资料，看到文件名被拼接到了url后面

![](https://image.3001.net/images/20200522/1590125854_5ec7651e84624.png!small)查看提交了url,在IDEA中全局搜索PathTraversal/profile-upload。  

![](https://image.3001.net/images/20200522/1590125884_5ec7653c6ab9c.png!small)跟进方法，在方法中直接用传来的名字和路径进行了拼接导致了目录穿越  

##
![](https://image.3001.net/images/20200522/1590125909_5ec765559de8d.png!small)逻辑漏洞Ⅰ  

需求是输入安全问题进行验证成功后，进行密码修改

![](https://image.3001.net/images/20200522/1590125991_5ec765a7cac43.png!small)提交后的数据请求包如下

![](https://image.3001.net/images/20200522/1590126015_5ec765bf31549.png!small)在idea中搜索uri，定位到相对应的代码

![](https://image.3001.net/images/20200522/1590126039_5ec765d7279fe.png!small)跟进parseSecQuestions(req)方法，这里获取了请求体中的参数，并将包含secQuestion的键值放入了userAnswer的map中，并返回赋值给了submittedAnswers的map

![](https://image.3001.net/images/20200522/1590126066_5ec765f271fb7.png!small)从感觉中判断应该是第二个If应该是返回密码修改的方法，那我就想办法看是否能绕过限制进入第二个if语句中，跟进方法

![](https://image.3001.net/images/20200522/1590126099_5ec766135f739.png!small)这里我们只要让其执行第一个If，而不去执行剩下的if语句即可，可以将请求体中的secQuestsion0\1的数字替换即可，返回true

 ***本文作者：WhyNotD，转载请注明来自FreeBuf.COM**  

##

