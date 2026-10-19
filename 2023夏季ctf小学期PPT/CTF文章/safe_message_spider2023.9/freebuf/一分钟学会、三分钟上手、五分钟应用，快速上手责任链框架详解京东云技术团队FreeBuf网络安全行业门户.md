**作者：京东物流 覃玉杰**

# 1\. pie 简介

责任链模式是开发过程中常用的一种设计模式，在 SpringMVC、Netty
等许多框架中均有实现。我们日常的开发中如果要使用责任链模式，通常需要自己来实现，但自己临时实现的责任链既不通用，也很容易产生框架与业务代码耦合不清的问题，增加
Code Review 的成本。

Netty 的代码向来以优雅著称，早年我在阅读 Netty 的源码时，萌生出将其责任链的实现应用到业务开发中的想法，之后花了点时间将 Netty
中责任链的实现代码抽取出来，形成了本项目，也就是 pie。pie 的核心代码均来自 Netty，绝大部分的 API 与 Netty 是一致的。

pie 是一个可快速上手的责任链框架，开发者只需要专注业务，开发相应的业务 Handler，即可完成业务的责任链落地。

一分钟学会、三分钟上手、五分钟应用，欢迎 star。

pie
源码地址：[https://github.com/feiniaojin/pie.git](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fgithub.com%2Ffeiniaojin%2Fpie.git)

pie 案例工程源码地址：[https://github.com/feiniaojin/pie-example.git](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fgithub.com%2Ffeiniaojin%2Fpie-example.git)

# 2\. 快速入门

### 2.1 引入 maven 依赖

pie 目前已打包发布到 maven 中央仓库，开发者可以直接通过 maven 坐标将其引入到项目中。

    
    
    <dependency>
        <groupId>com.feiniaojin.ddd.ecosystem</groupId>
        <artifactId>pie</artifactId>
        <version>1.0</version>
    </dependency>
    
    

目前最新的版本是 1.0

### 2.2 实现出参工厂

出参也就是执行结果，一般的执行过程都要求有执行结果返回。实现 OutboundFactory 接口，用于产生接口默认返回值。

例如：

    
    
    public class OutFactoryImpl implements OutboundFactory {
        @Override
        public Object newInstance() {
            Result result = new Result();
            result.setCode(0);
            result.setMsg("ok");
            return result;
        }
    }
    
    

### 2.3 实现 handler 接口完成业务逻辑

在 pie 案例工程 ( [https://github.com/feiniaojin/pie-example.git](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fgithub.com%2Ffeiniaojin%2Fpie-example.git)) 的 Example1 中，为了展示 pie 的使用方法，实现了一个虚拟的业务逻辑：CMS
类项目修改文章标题、正文，大家不要关注修改操作放到两个 handler 中是否合理，仅作为讲解案例。

三个 Handler 功能如下：

CheckParameterHandler：用于参数校验。

ArticleModifyTitleHandler：用于修改文章的标题。

ArticleModifyContentHandler：用于修改文章的正文。

CheckParameterHandler 的代码如下：

    
    
    public class CheckParameterHandler implements ChannelHandler {
    
        private Logger logger = LoggerFactory.getLogger(CheckParameterHandler.class);
    
        @Override
        public void channelProcess(ChannelHandlerContext ctx,
                                   Object in,
                                   Object out) throws Exception {
    
            logger.info("参数校验:开始执行");
    
            if (in instanceof ArticleTitleModifyCmd) {
                ArticleTitleModifyCmd cmd = (ArticleTitleModifyCmd) in;
                String articleId = cmd.getArticleId();
                Objects.requireNonNull(articleId, "articleId不能为空");
                String title = cmd.getTitle();
                Objects.requireNonNull(title, "title不能为空");
                String content = cmd.getContent();
                Objects.requireNonNull(content, "content不能为空");
            }
            logger.info("参数校验:校验通过,即将进入下一个Handler");
            ctx.fireChannelProcess(in, out);
        }
    
        @Override
        public void exceptionCaught(ChannelHandlerContext ctx,
                                    Throwable cause,
                                    Object in,
                                    Object out) throws Exception {
            logger.error("参数校验:异常处理逻辑", cause);
            Result re = (Result) out;
            re.setCode(400);
            re.setMsg("参数异常");
        }
    }
    
    

ArticleModifyTitleHandler 的代码如下：

    
    
    public class ArticleModifyTitleHandler implements ChannelHandler {
    
        private Logger logger = LoggerFactory.getLogger(ArticleModifyTitleHandler.class);
    
        @Override
        public void channelProcess(ChannelHandlerContext ctx,
                                   Object in,
                                   Object out) throws Exception {
    
            logger.info("修改标题:进入修改标题的Handler");
    
            ArticleTitleModifyCmd cmd = (ArticleTitleModifyCmd) in;
    
            String title = cmd.getTitle();
            //修改标题的业务逻辑
            logger.info("修改标题:title={}", title);
    
            logger.info("修改标题:执行完成,即将进入下一个Handler");
            ctx.fireChannelProcess(in, out);
        }
    
        @Override
        public void exceptionCaught(ChannelHandlerContext ctx,
                                    Throwable cause,
                                    Object in,
                                    Object out) throws Exception {
            logger.error("修改标题:异常处理逻辑");
            Result re = (Result) out;
            re.setCode(1501);
            re.setMsg("修改标题发生异常");
        }
    }
    
    

ArticleModifyContentHandler 的代码如下：

    
    
    public class ArticleModifyContentHandler implements ChannelHandler {
    
        private Logger logger = LoggerFactory.getLogger(ArticleModifyContentHandler.class);
    
        @Override
        public void channelProcess(ChannelHandlerContext ctx,
                                   Object in,
                                   Object out) throws Exception {
    
            logger.info("修改正文:进入修改正文的Handler");
            ArticleTitleModifyCmd cmd = (ArticleTitleModifyCmd) in;
            logger.info("修改正文,content={}", cmd.getContent());
            logger.info("修改正文:执行完成,即将进入下一个Handler");
            ctx.fireChannelProcess(in, out);
        }
    
        @Override
        public void exceptionCaught(ChannelHandlerContext ctx,
                                    Throwable cause,
                                    Object in,
                                    Object out) throws Exception {
    
            logger.error("修改标题:异常处理逻辑");
    
            Result re = (Result) out;
            re.setCode(1502);
            re.setMsg("修改正文发生异常");
        }
    }
    
    

### 2.4 通过 BootStrap 拼装并执行

    
    
    public class ArticleModifyExample1 {
    
        private final static Logger logger = LoggerFactory.getLogger(ArticleModifyExample1.class);
    
        public static void main(String[] args) {
            //构造入参
            ArticleTitleModifyCmd dto = new ArticleTitleModifyCmd();
            dto.setArticleId("articleId_001");
            dto.setTitle("articleId_001_title");
            dto.setContent("articleId_001_content");
    
            //创建引导类
            BootStrap bootStrap = new BootStrap();
    
            //拼装并执行
            Result result = (Result) bootStrap
                    .inboundParameter(dto)//入参
                    .outboundFactory(new ResultFactory())//出参工厂
                    .channel(new ArticleModifyChannel())//自定义channel
                    .addChannelHandlerAtLast("checkParameter", new CheckParameterHandler())//第一个handler
                    .addChannelHandlerAtLast("modifyTitle", new ArticleModifyTitleHandler())//第二个handler
                    .addChannelHandlerAtLast("modifyContent", new ArticleModifyContentHandler())//第三个handler
                    .process();//执行
            //result为执行结果
            logger.info("result:code={},msg={}", result.getCode(), result.getMsg());
        }
    }
    
    

### 2.5 执行结果

以下是运行 ArticleModifyExample1 的 main 方法打出的日志，可以看到我们定义的 handler 被逐个执行了。  
![1683340054_6455bb16ad7a35b3dfb99.png!small?1683340055421](https://image.3001.net/images/20230506/1683340054_6455bb16ad7a35b3dfb99.png!small?1683340055421)  

# 3\. 异常处理

### 3.1 Handler 异常处理

当某个 Handler 执行发生异常时，我们可将其异常处理逻辑实现在当前 Handler 的 exceptionCaught 方法中。

在 pie 案例工程 ( [https://github.com/feiniaojin/pie-example.git](https://www.oschina.net/action/GoToLink?url=https%3A%2F%2Fgithub.com%2Ffeiniaojin%2Fpie-example.git)) 的 example2 包中，展示了某个 Handler 抛出异常时的处理方式。

假设 ArticleModifyTitleHandler 的业务逻辑会抛出异常，实例代码如下：

    
    
    public class ArticleModifyTitleHandler implements ChannelHandler {
    
        private Logger logger = LoggerFactory.getLogger(ArticleModifyTitleHandler.class);
    
        @Override
        public void channelProcess(ChannelHandlerContext ctx,
                                   Object in,
                                   Object out) throws Exception {
    
            logger.info("修改标题:进入修改标题的Handler");
            ArticleTitleModifyCmd cmd = (ArticleTitleModifyCmd) in;
            String title = cmd.getTitle();
            //此处的异常用于模拟执行过程中出现异常的场景
            throw new RuntimeException("修改title发生异常");
        }
    
        @Override
        public void exceptionCaught(ChannelHandlerContext ctx,
                                    Throwable cause,
                                    Object in,
                                    Object out) throws Exception {
            logger.error("修改标题:异常处理逻辑");
            Result re = (Result) out;
            re.setCode(1501);
            re.setMsg("修改标题发生异常");
        }
    }
    
    

此时 ArticleModifyTitleHandler 的 channelProcess 方法一定会抛出异常， 在当前 Handler 的
exceptionCaught 方法中对异常进行了处理。

运行 ArticleModifyExample2 的 main 方法，输出如下：  
![](https://image.3001.net/images/20230506/1683339757_6455b9edbef3ae7c3d85a.png!small)

### 3.2 全局异常处理

有时候，我们不想每个 handler 都处理一遍异常，我们希望在执行链的最后统一进行处理。  
在 ArticleModifyExample3 中，我们展示了通过一个全局异常进行最后的异常处理，其实现主要分为以下几步：

### 3.2.1 业务 Handler 传递异常

如果业务 Handler 实现了 ChannelHandler 接口，那么需要手工调用 ctx.fireExceptionCaught 方法向下传递异常。  
例如 CheckParameterHandler 捕获到异常时的示例如下：

    
    
    @Override
    public class XXXHandler implements ChannelHandler {
    
        //省略其他逻辑
    
        //异常处理
        public void exceptionCaught(ChannelHandlerContext ctx,
                                    Throwable cause,
                                    Object in,
                                    Object out) throws Exception {
    
            logger.info("参数校验的异常处理逻辑:不处理直接向后传递");
            ctx.fireExceptionCaught(cause, in, out);
        }
    }
    
    

如果业务 Handler 继承了 ChannelHandlerAdapter，如果没有重写 fireExceptionCaught
方法，则默认将异常向后传递。

### 3.2.2 实现全局异常处理的 Handler

我们把业务异常处理逻辑放到最后的 Handler 中进行处理，该 Handler 继承了 ChannelHandlerAdapter，只需要重写异常处理的
exceptionCaught  
方法。  
示例代码如下：

    
    
    public class ExceptionHandler extends ChannelHandlerAdapter {
    
        private Logger logger = LoggerFactory.getLogger(ExceptionHandler.class);
    
        @Override
        public void exceptionCaught(ChannelHandlerContext ctx,
                                    Throwable cause,
                                    Object in,
                                    Object out) throws Exception {
    
            logger.error("异常处理器中的异常处理逻辑");
            Result re = (Result) out;
            re.setCode(500);
            re.setMsg("系统异常");
        }
    }
    
    

### 3.2.3 将 ExceptionHandler 加入到执行链中

直接通过 BootStrap 加入到执行链最后即可，示例代码如下：

    
    
    public class ArticleModifyExample3 {
    
        private final static Logger logger = LoggerFactory.getLogger(ArticleModifyExample3.class);
    
        public static void main(String[] args) {
            //入参
            ArticleTitleModifyCmd dto = new ArticleTitleModifyCmd();
            dto.setArticleId("articleId_001");
            dto.setTitle("articleId_001_title");
            dto.setContent("articleId_001_content");
            //创建引导类
            BootStrap bootStrap = new BootStrap();
    
            Result result = (Result) bootStrap
                    .inboundParameter(dto)//入参
                    .outboundFactory(new ResultFactory())//出参工厂
                    .channel(new ArticleModifyChannel())//自定义channel
                    .addChannelHandlerAtLast("checkParameter", new CheckParameterHandler())//第一个handler
                    .addChannelHandlerAtLast("modifyTitle", new ArticleModifyTitleHandler())//第二个handler
                    .addChannelHandlerAtLast("modifyContent", new ArticleModifyContentHandler())//第三个handler
                    .addChannelHandlerAtLast("exception", new ExceptionHandler())//异常处理handler
                    .process();//执行
            //result为执行结果
            logger.info("result:code={},msg={}", result.getCode(), result.getMsg());
        }
    }
    
    

### 3.2.4 运行 ArticleModifyExample3

运行 ArticleModifyExample3 的 main 方法，控制台输出如下，可以看到异常被传递到最后的 ExceptionHandler
中进行处理。  
![](https://image.3001.net/images/20230506/1683339758_6455b9eebac6506e3aeca.png!small)

