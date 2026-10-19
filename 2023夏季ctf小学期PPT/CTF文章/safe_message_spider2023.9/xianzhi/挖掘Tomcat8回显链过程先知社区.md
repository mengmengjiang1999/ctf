  1. 工具介绍  
介绍一个项目：<https://github.com/c0ny1/java-object-searcher>  
工具介绍：配合IDEA在Java应用运行时，对内存中的对象进行搜索。比如可以可以用挖掘request对象用于回显，辅助构造java内存webshell等场景。  
首先创建一个tomcat的web环境  
直接放到lib目录加载即可

![](./img/8617227962542022380.png)

2.过程  
之后在doget第一行断点即可，段住之后，在断点处输入以下代码，这就是这个工具提供的。  
![](./img/464979769959579720.png)  
根据网上提供的规则，直接使用即可

    
    
    //设置搜索类型包含Request关键字的对象
    List<Keyword> keys = new ArrayList<>();
    keys.add(new Keyword.Builder().setField_type("Request").build());
    //定义黑名单
    List<Blacklist> blacklists = new ArrayList<>();
    blacklists.add(new Blacklist.Builder().setField_type("java.io.File").build());
    //新建一个广度优先搜索Thread.currentThread()的搜索器
    SearchRequstByBFS searcher = new SearchRequstByBFS(Thread.currentThread(),keys);
    // 设置黑名单
    searcher.setBlacklists(blacklists);
    //打开调试模式,会生成log日志
    searcher.setIs_debug(true);
    //挖掘深度为20
    searcher.setMax_search_depth(20);
    //设置报告保存位置
    searcher.setReport_save_path("D:\\");
    searcher.searchObject();
    

执行完之后，在我本地D盘出现了这个报告文件。大家一看就清晰了吧。就是通过Thread依次获取requests

![](./img/6259287531427673642.png)  
接下来看以下代码分析，首先获取Group，在获取threads，在图中发现threads下面为一个存储Thread的List列表。所以这就有了第七行的for循环，第十行获取target。到第十二行获取this$0，而在14行就是将this$0的Obejct拿到  
拿到Object后handler实现，其实就是一直通过反射往后拿。  
最后通过processors获取到RequestInfo。但是存在于一个List集合...继续往后看

    
    
    ThreadGroup threadGroup = Thread.currentThread().getThreadGroup();
            Field ths = null;
            try {
                ths = threadGroup.getClass().getDeclaredField("threads");
                ths.setAccessible(true);
                Thread[] thread1 = (Thread[]) ths.get(threadGroup);
                for(int i=0;i<thread1.length;i++){
                    Thread threadtemp = thread1[i];
                    if(threadtemp.getName().contains("Acceptor")){
                        Field target = threadtemp.getClass().getDeclaredField("target");
                        target.setAccessible(true);
                        Field field1 = target.get(threadtemp).getClass().getDeclaredField("this$0");
                        field1.setAccessible(true);
                        Object e =  field1.get(target.get(threadtemp));
                        Field field = Class.forName("org.apache.tomcat.util.net.AbstractEndpoint").getDeclaredField("handler");
                        field.setAccessible(true);
                        Object handle = field.get(e);
                        Field global = handle.getClass().getDeclaredField("global");
                        global.setAccessible(true);
                        RequestGroupInfo requestGroupInfo = (RequestGroupInfo) global.get(handle);
                        Field process = requestGroupInfo.getClass().getDeclaredField("processors");
                        process.setAccessible(true);
                        List<RequestInfo> requestInfos = (List<RequestInfo>) process.get(requestGroupInfo);
                        Field req = Class.forName("org.apache.coyote.RequestInfo").getDeclaredField("req");
                        req.setAccessible(true);
                        for (RequestInfo requestInfo:requestInfos){
                            Request request1 = (Request) req.get(requestInfo);
                            if (req.get(requestInfo)!=null){
                                org.apache.catalina.connector.Request request2 = (org.apache.catalina.connector.Request) ((Request) (req.get(requestInfo))).getNote(1);
                                request2.getResponse().getWriter().write("YYDS");
                            }
    
                        }
    
                }}
            } catch (NoSuchFieldException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            } catch (ClassNotFoundException e) {
                e.printStackTrace();
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }
    
        }
    

这里重点就来了，RequestInfo为两个，当然这里看环境问题，有时候我调试就是一个。  
现在问题就是RequestInfo第一个的Request为Null。所以要进行判断，否则就会出错

![](./img/7465591564677747542.png)  
判断也很简单，首先我通过req.get(requestInfo)进行了获取该对象，  
并在第三行判断，不为Null则获取request对象，但是可以发现首先获取了getNote(1)  
其实问题就是org.apache.coyote#Response没有getWriter();

    
    
    for (RequestInfo requestInfo:requestInfos){
                            Request request1 = (Request) req.get(requestInfo);
                            if (req.get(requestInfo)!=null){
                                org.apache.catalina.connector.Request request2 = (org.apache.catalina.connector.Request) ((Request) (req.get(requestInfo))).getNote(1);
                                request2.getResponse().getWriter().write("YYDS");
                            }
    
                        }
    

![](./img/5827690121911290240.png)  
也就是这里我通过request进行getNote(1)，其实是为了获取里面的另一个request。  
你可以理解为有两个request，一个可以回显，一个不可用。而咱们现在这个就是不可用回显的request，但是通过这个request可以获取到可回显的...大家好好捋顺一下即可  
![](./img/2235288907868140072.png)  
![](./img/371541709492605385.png)

最后放一张回显的图吧，整体来说其实就是掌握好反射，就能写出来。  
![](./img/994102778654879672.png)

