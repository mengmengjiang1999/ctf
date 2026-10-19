*****本文原创作者：manwu91，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

**去年破解了某安卓app的加密算法，在抓了将近一年后发现该app有强制更新，旧版协议已经无法使用。通过分析发现返回的数据仍是用aes加密的，但密钥却是通过原生代码还原的，拿不到密钥也就无法解密。对于原生代码的还原很难，而且笔者的汇编知识早就随着岁月流走了，看着这一堆汇编代码心里已是万念俱灰；但发现该app竟然支持包括x86在内的多种架构，于是想到一种方案：让虚拟机运行原生代码，并通过http接口提供调用服务。**

## 开发

### 移植jni代码

首先创建一个安卓工程，在src/main下创建目录jniLibs，然后将apk lib下的so文件复制进来(保留目录结构)，项目结构下图所示

![cns_proj_jnilib.png](https://image.3001.net/images/20180404/15228295859376.png!small)  

然后在项目中创建jni类，类的全限定名称与内容要跟原apk中对应的类一样，建议在jadx中直接复制过来。如下是本例中的jni类

    
    
    package com.xxx.xxx.util;
    
    public class StrToLongEnUtil {
        public static StrToLongEnUtil a;
    
        static {
            System.loadLibrary("enutil-lib");
        }
    
        public static void main(String [] args){
            System.out.println(StrToLongEnUtil.a(args[0], Integer.parseInt(args[1])));
        }
        private StrToLongEnUtil() {
        }
    
        public static long a(String str, int i) {
            return a().StrToLong(str, i);
        }
    
        public static synchronized StrToLongEnUtil a() {
            StrToLongEnUtil strToLongEnUtil;
            synchronized (StrToLongEnUtil.class) {
                if (a == null) {
                    a = new StrToLongEnUtil();
                }
                strToLongEnUtil = a;
            }
            return strToLongEnUtil;
        }
    
        public static long b(String str, int i) {
            return a().StrToLong2(str, i);
        }
    
        public static long c(String str, int i) {
            return a().StrToLong3(str, i);
        }
    
        // 以下是与so绑定的原生方法
    
        public native long StrToLong(String str, int i);
    
        public native long StrToLong2(String str, int i);
    
        public native long StrToLong3(String str, int i);
    }
    

这样就可以在这个安卓项目中调用StrToLongEnUtil中的原生方法了。

### 暴露http服务

我们已经可以在项目中运行原生代码了，但还需要将调用包装成服务供爬虫代码使用，于是google到了一个可以运行在安卓端的web服务器[AndServer](https://github.com/yanzhenjie/AndServer)。它的使用非常简单，通过builder绑定网卡与端口，并注册访问路径与处理器就可以了，例如注册`/jni`路径提供解密服务：

    
    
    server = AndServer.serverBuilder()
            .inetAddress(addr)
            .port(Integer.parseInt(port))
            .registerHandler("/", new HelloHandler())
            .registerHandler("/jni", new AppJniHandler())
            .build();
    server.startup();
    

其中AppJniHandler接收必要参数，并调用native方法，将计算结果返回，代码如下

    
    
    public class AppJniHandler extends SimpleRequestHandler{
        /**
         * /jni?mth=a&str=xxx&i=10
         * @param request
         * @return
         * @throws HttpException
         * @throws IOException
         */
        @Override
        protected View handle(HttpRequest request) throws HttpException, IOException {
            Map<String, String> params = HttpRequestParser.parseParams(request);
            String str = params.get("str");
            int i = Integer.parseInt(params.get("i"));
            long result = -1;
            switch (params.get("mth")){
                case "a":
                    result = StrToLongEnUtil.a(str, i);
                    break;
                case "b":
                    result = StrToLongEnUtil.b(str, i);
                    break;
                case "c":
                    result = StrToLongEnUtil.c(str, i);
                    break;
            }
            return new OkView(String.valueOf(result));
        }
    }
    

### 关于网卡

为了对外提供服务，需要将AndServer绑定在外部能访问的网卡上，使用如下代码可以获取所有网卡

    
    
    private List<InetAddress> getAllIP4() throws Exception {
        List<InetAddress> addresses = Lists.newArrayList();
    
        for (Enumeration<NetworkInterface> ifs = NetworkInterface.getNetworkInterfaces();
             ifs.hasMoreElements(); ) {
            for (Enumeration<InetAddress> addrs = ifs.nextElement().getInetAddresses();
                 addrs.hasMoreElements(); ) {
                InetAddress addr = addrs.nextElement();
                if (addr instanceof Inet4Address) {
                    addresses.add(addr);
                }
            }
        }
        return addresses;
    }
    `
    

通过UI在启动时设置要绑定的网卡，效果如下

![cns_select_iface.png](https://image.3001.net/images/20180404/15228296115106.png!small)  

## 部署

因为so中有支持x86架构的，所以笔者采用的是genymotion模拟器。它运行在virtualbox下，virtualbox会创建一个虚拟网络，宿主机与虚拟机间以此可以相互通信。例如笔者genymotion虚拟机分配到的局域网ip为`192.168.56.101`，让AndServer监听此网卡的8888端口，服务运行起来就可以在宿主机上访问，通过`curl
'[http://192.168.56.101:8888/jni?mth=a&str=55c854f2d9a570663ef363423d1c0072&i=2](http://192.168.56.101:8888/jni?mth=a&str=55c854f2d9a570663ef363423d1c0072&i=2)'`成功拿到结果。

![cns_app_ui.png](https://image.3001.net/images/20180404/15228296523578.png!small)  

在宿主机上安装nginx，将请求反向代理到192.168.56.101:8888即可实现外网访问。

 ***本文原创作者：manwu91，本文属FreeBuf原创奖励计划，未经许可禁止转载**

