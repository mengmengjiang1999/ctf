**作者：哈霓@蚂蚁安全实验室  
原文链接：<https://mp.weixin.qq.com/s/WzzCFQBgg7BcVUFWT8npuQ>**

在今年的Black Hat Asia上，蚂蚁安全实验室共入选了5个议题和3个工具。本期分享的是蚂蚁天宸实验室的议题《自动化挖掘gRPC网络接口漏洞》。

# 01 简介

随着移动互联网和工业互联网的快速发展，大量开发者、厂商不得不关注网络通讯的实效性和效能问题，而gRPC框架正是基于这样的浪潮下应运而生的网络通讯框架。它是一个高可用、开源的网络库，提供了跨平台的接入能力，在网络开销、性能、安全性上相比HTTP通讯有着极大的优势。然而对于这样的基础设施，业界很少有以端到云的协议通讯视角，进行漏洞挖掘技术的文章。

![](https://images.seebug.org/content/images/2021/06/3dafb9db-aefb-4316-80aa-7a4d9b01532e.jpg-w331s)

本次蚂蚁安全实验室的曹世杰，在Black Hat Asia 2021的议题《基于gRPC协议封装的移动/ IoT应用程序的安全漏洞狩猎》中，
对这个方向进行了相关技术分享。

在本议题中，我们提出了一种方法，该方法突破了端上在RPC协议漏洞挖掘的限制，可以为使用gRPC框架的应用程序自动挖掘服务器接口漏洞。

# 02 技术挑战

业界针对gRPC框架在RPC协议下的漏洞挖掘，一直缺少相应方案进行介绍，原因是：

  1. 协议包构造问题： gRPC框架具有特定的组包逻辑，并且传输过程中使用了Protobuf进行数据序列化，在没有理解gRPC框架组包过程的情况下，很难构造一个具有攻击效果的网络数据包。

  2. 端上安全机制绕过： 在客户端应用程序中通常会内置数据签名等安全保护机制。该机制导致在不注入应用程序的情况下，构造的网络数据包极有可能会存在安全校验失败的问题。

由于这些特性，使得在RPC协议下的应用程序，漏洞挖掘变得十分困难。而本次我们在会议中提到的方案，正是解决了客户端上RPC通讯的漏洞挖掘问题。

![](https://images.seebug.org/content/images/2021/06/3d0d4a14-7a34-4194-910f-78b9f8ec6868.png-w331s)

这应该是首个基于gRPC框架的自动化漏洞挖掘的议题，基于这个框架，我们发现了若干gRPC网络服务的RCE漏洞。这套方案的理念是：从端安全技术的视角，实现对不同应用RPC请求的数据获取与重放能力，以及快速拔插的HUB能力，将不同应用接入到该方案，可将传统WEB漏洞挖掘的思路应用到移动终端。另外一方面，将RPC接口的脆弱性分析部署在云端，极大地提高了漏洞挖掘的准确率和效率。

# 03 什么是gRPC

RPC协议称为远程过程调用，此协议已应用于大量的互联网移动应用程序和IoT设备。该协议的优点是，在C/S模式通信过程中，应用程序仅需知道远程服务的名称和访问远程服务的输入参数，即可获取远程服务的资源。

gRPC是Google提供的，高度可用的RPC框架，已经大规模应用于移动App以及工业互联网领域，在Http2.0以及Protobuf的加持下，具有传输更快、并且能够在传输期间压缩网络数据的优点。

![](https://images.seebug.org/content/images/2021/06/04870782-27c4-43a7-9d78-326c14c127f1.png-w331s)

# 04 gRPC框架的组包流程

应用程序通过gRPC框架构造RPC请求的示意图如下。一个RPC请求，由不同的SDK参与构造，其中红色部分，代表网络通讯中不可或缺的数据，包含了Cookie与OperationType。OperationType可以理解为是HTTP请求的路径，告诉服务端网关当前请求对应的RPC应用服务。

而橙色部分，是应用在性能与安全层面进行的优化：1.
通过操作系统提供的API如CCCrypt或者SecurityEnclave实现数据的签名，部分注重安全的厂商会使用自研的安全SDK通过黑盒算法进行签名。2.
将部分设备的环境安全检测信息，放入RPC Header中用于后期的风险防控。3. 通过Protobuf生成Proto对象，压缩网络字节，提高网络效率。

![](https://images.seebug.org/content/images/2021/06/dca7515a-c384-4361-b366-1296b3a02c24.png-w331s)

# 05 构建测试系统

针对不同的应用程序，我们开发了大量工具链用于快速开发注入的动态库，实现了端上流量获取以及重放的能力，并且可快捷接入到RPC重放网络，提供对外调用接口。这样的好处是，在漏洞挖掘的过程中，我们将不必关注端上的实现逻辑，仅仅通过几行代码就能实现模拟登录、自动重放的能力。

![](https://images.seebug.org/content/images/2021/06/402403ca-bd7b-44e1-b527-51780f55e23f.png-w331s)

在整个工程中，我们在工具链中实现的技术包括：

  1. IDAPython调用链分析工具：主要基于IDAPython对gRPC网络接口推导应用程序网络库的函数调用关系，寻找封装gRPC的网络库API。并通过叶子节点寻找构造gRPC数据包所依赖的其他接口（如签名接口、安全检测接口），从而寻找Hook切入点，以及方便接入人员构造注入代码。

  2. 安全模块：通用的安全检测对抗模块，集成通用的安全对抗代码，用于绕过证书校验、模块检查机制。另外针对不同应用程序，通过反射调用的方法实现扩展能力：用于构造协议中的数据签名、解析Protobuf数据块。

  3. 网关注册模块：任务网关的接入模块，负责与任务网关进行设备注册、心跳报活、任务执行。

  4. 任务执行模块：执行网关注册模块下发的任务，基于gRPC框架构造通用的RPC报文，借助安全模块实现签名、数据篡改和安全环境绕过，并进行重放。并负责将重放的返回结果，通过网关注册模块返回给任务中心。

  5. 守护进程模块：保障任务执行设备在遇到Crash的情况下能够主动重启任务进程。

  6. 自动登录模块：用于对不同的应用程序实现模拟登录的能力，通过RPC请求的返回值截获Response中所获取的Cookie，从而在任务执行的过程中自动带上获取的登陆态信息。

下面我们会对其中的一些工具链技术进行介绍：

## 5.1 通过IDAPython进行网络库推导

如上图所示，通过对gRPC网络库的分析，需要梳理出一批接口，作为底层函数向上分析的关系链。以iOS为例，这里的难点在于，iOS应用程序使用了objc_msgsend，以消息通知的方式进行函数调用，所以IDA是无法直接获取关系链的。于是，为了自动推到叶子结点（也就是网络库的根函数），我们使用了下面的方法：

![](https://images.seebug.org/content/images/2021/06/fffba062-6a54-4c7d-8267-9e2db688e51e.png-w331s)

技术点：

1.基于消息的调用方式，需要对sel进行2次关系链查询。

2.引入了Symbol Execution,
需要对引用的Position调用idc.GetDisasm获取上下文并执行推导，来校验objc_msgsend的Class是不是Target
Function引用的Class，否则会出现大量的结果不准确问题。

![](https://images.seebug.org/content/images/2021/06/5bfffa96-3616-4109-8a3a-9dbb45e03e43.png-w331s)

## 5.2 重放能力的构建

为了能够运行大规模的漏洞测试任务，我们使用了真实的设备构建了任务执行平台。这个平台的优势是：

（1）基于gRPC框架，实现了与真实设备的网络通讯，使得任务下发到执行可以在1-2秒完成。

（2）每台设备的应用程序，都具备守护进程和心跳包，保障任务调度的稳定性，保障平台本身的可用性。

![](https://images.seebug.org/content/images/2021/06/406ef421-72f2-4880-8d84-dc980370149a.png-w331s)

当我们的RPC模块集成到应用程序中，就会向网关对当前设备进行注册。我们定义了一种设备注册的网络格式，用于后期对不同设备不同应用的鉴别，使不同的漏洞测试任务能够快速下发到指定的应用。注册设备的报文如下：

    
    
    // 客户端
    Client Heartbeat package :
    client = GRPCAgent.instance
    client.worker = nil;
    client.platfrom = @"iOS/Android";
    client.isHeartBeat = True;
    client.isRun = FALSE;
    client.taskLock = Object;
    
    // 服务端
    Server Side register：
    executor_info = {
                      'tenant': device_tenant,
                      'did': device_id,
                      'type': device_type,
                      'name': device_name,
                      'cluster': device_cluster,
                      'others': device_others,
                      'last_update': now,
                      'metrics': mobilegw_pb2.DeviceMetrics(),
                      'last_sync_timestamp': now,
                      'task_runner': 0,
                      'app_version': device_app_version,
                      'hook_version': device_hook_version
                  }

相比Android设备，iOS的守护进程保护，显得更加困难。在iOS
8的设备中，我们应用了Mirmir（这是Cydia提供的一个多进程运行的越狱程序，在iOS 8以后就不能使用）对程序本身进行了保护。对于iOS
9以后的越狱设备，我们通过注册守护进程，来实现对应用程序的保护监控：

  1. deamon进程通过注册消息通知的方式，监听全局消息。

  2. 应用程序在遇到不可抗力的Crash崩溃时，通知我们的deamon进程，延时2秒后重新唤起我们的应用程序。

相关代码如下：

    
    
    void run_cmd(char *cmd)
    {
        pid_t pid;
        const char *argv[] = {"sh", "-c", cmd, NULL};
        int status;
    
        status = posix_spawn(&pid, "/bin/sh", NULL, NULL, (char* const*)argv, nil);
        if (status == 0) {
            if (waitpid(pid, &status, 0) == -1) {
                perror("waitpid");
            }
        }
    }
    static void Monitor(CFNotificationCenterRef center, void *observer, CFStringRef name, const void *object, CFDictionaryRef userInfo)
    {
        sleep(2)
        run_cmd("killall -9 target process");
        run_cmd("open bundleid");
    }
    int main(int argc, char *argv[], char *envp[]) {
        CFNotificationCenterAddObserver(CFNotificationCenterGetDarwinNotifyCenter(), NULL, Monitor, CFSTR("com.sec.iosecdamond"), NULL,CFNotificationSuspensionBehaviorCoalesce);
        CFRunLoopRun(); // keep it running in backgroundcom.sec.iosecdamond
    
        return 0;
    }

左右滑动查看完整代码

## 5.3 端上安全机制绕过

在程序中我们会通过注入动态库的方式实现终端上任务执行的能力，然而部分应用程序内部有着安全保护机制，会导致任务执行模块出错甚至异常。所以，我们实现了独立的对抗逻辑，帮助我们绕过程序中的安全检测机制。下面会介绍我们碰到的部分对抗手法和一些绕过思路：

（1）堆栈环境检测：在反射调用签名函数的过程中，部分应用程序会通过调用的堆栈节点来判断调用来源是否可信，通常会使用backtrace来判断调用上游的目标函数是否满足预期。

![](https://images.seebug.org/content/images/2021/06/a8beffc3-6f73-4344-9371-1b3964358640.png-w331s)

而我们的对抗思路，并不是对trace函数进行Hook，而是通过5.1推导的网络库的叶子结点，寻找应用层的加签函数，从而构造正确的签名数据。

![](https://images.seebug.org/content/images/2021/06/e8dd2b82-9846-4e89-848c-aae100248bf4.png-w331s)

（2）部分应用对符号替换的Hook方式有针对性检测，比如通过dladdr对进程中模块的符号表进行遍历检测，来识别符号替换的Hook风险。

![](https://images.seebug.org/content/images/2021/06/dea3c3ab-cfc6-4a7a-8b79-5fc472b96b87.png-w331s)

这里的绕过方式，我们应用inlinehook对目标函数进行控制，并且，在目前Hook代码中，我们通过修改函数目标地址的一行指令来对应用程序API进行Hook。这样的优势是，对函数本身的修改降为最低，篡改痕迹更小，也更难以发现。

上述的对抗场景属于我们对个别应用发现存在的校验机制，除此也会有部分通用的端安全对抗逻辑保持默认开启，规避端上安全检测对任务执行带来的影响：

（1）通过对`libboringssl.dylib`的`SSLCreateContext`、`SSLHandshake`、`SSLSetSessionOption`、`tls_helper_create_peer_trus`t函数进行Hook，强制不进行证书校验。

（2）对`_dyld_get_image_name()`函数Hook并将我们注入的任务执行模块伪装为系统模块。

## 5.4 Protobuf数据还原

我们发现大量的应用，使用了Protobuf的格式对数据进行了编码，如果没有还原Protobuf数据的能力，我们就无法对应用Protobuf的网络接口进行漏洞测试。

由于我们没有Proto文件，所以我们需要有方法对数据进行还原。经过分析，在没有对应数据对象的情况下，是可基于字节码数据对Protobuf数据格式进行原始结构的还原。

Protobuf有自己的格式结构，需要对数据块进行解析。Protobuf数据包含了自己的数据头和数据内容。通常数据头中包含了：1. 字段数，2.
数据起始位置，3. 数据类型。

需要注意的是，部分数据类型可能会告诉你仍然是一个对象，所以需要使用递归的方式进行层层解析，直到还原出每一个字段的具体数据。

![](https://images.seebug.org/content/images/2021/06/00aff6fd-0dee-4c8e-8757-e9f8f3f64c1e.png-w331s)

# 06 流量抽样 & 漏洞测试

应用的流量是非常大的，我们对流量进行了采集和抽样，提高了漏洞挖掘的效率和检出率。

## 6.1 数据抽样

我们对不同的应用程序，在不同的场景进行数据采集，经过实验，如果我们对每一条数据都进行测试，会导致我们在漏洞挖掘的效率上大打折扣。我们希望尽可能覆盖全面，能够对每个接口进行有效的测试：

（1）随机散列算法：对于初始的大量数据，我们希望尽可能地保证每种RPC请求都能够覆盖，但又能够把大数化小，这样能够保障在有足够覆盖率的情况下，不会消耗太多数据库性能。

![](https://images.seebug.org/content/images/2021/06/d243f10c-0a3b-4832-aece-3f7286298f5f.png-w331s)

（2）分群抽样算法：经过（1）的处理，仍然会出现部分请求，存在大量相似的数据。比如上图中的接口1，仍然会存在同一个接口有2GB数据，也就是数据分析中遇到的数据倾斜问题。这时需要使用分群抽样算法，这种算法能够保证对已有数据，均匀抽取固定的数据量，最后会把大量的数据压缩到一个很小的数据集提供给后续的漏洞挖掘流程。

![](https://images.seebug.org/content/images/2021/06/e49cf7d9-5532-4635-80ed-1a4944d6984f.png-w331s)

如下面的代码，使用cluster_sample对operationType进行分群，并且把flag=True的结果进行select检出，我们可以均匀地对每个operationType的数据体抽样10条数据进行分析。

    
    
    cluster_sample(bigint <x>[, bigint <y>])
    over (partition by <col1>[, <col2>...])
    
    select tmp.operationType, tmp.request_data, tmp.response_data
        from (
            select operationType, request_data, response_data, cluster_sample(operationType, 10)  as flag
            from grpc_table
            ) tmp
        where tmp.flag = true;   

左右滑动查看完整代码

## 6.2 脆弱性分析

通过上面的方法，我们可以知道，怎么把数据从大化小，提高漏洞扫描的效率。除此之外，我们将一些接口脆弱性分析的逻辑，也内置到了云端进行处理。

![](https://images.seebug.org/content/images/2021/06/8298db4a-33af-479a-9b49-13f74b86854b.png-w331s)

  * 1.接口私有性判断：基于数据的漏洞挖掘，我们提出接口“私有性”的度量方法，可以理解为：如果一个接口具备漏洞利用的价值，数据必定与用户个人相关，这类接口定义为私有性接口。我们通过对同一个接口的不同数据进行聚合，如果数据结果的聚合数量与数据总量的比越趋近于1，则越趋向于私有性接口。

F(p) = Group ( OperationType （Count (Distinct Request/Response） / Count
(Distinct User））

Group代表一个分群，如果针对一个OperationType的分群结果，如果请求/返回的结果与测试账号个数的比趋近于1，则接口私有性越强；

  * 2.相似度分析：比较不同测试账号的返回结果的相似性。对于不同账号，我们会构造同样的参数进行验证，如果出现越接近相似的结果，则越可能出现越权漏洞相关风险。相似度的判断，涉及了对请求参数，返回结果向量化的运算，由于篇幅问题，就不深入展开，感兴趣的同学可以在网上搜索相关文章。

此外，我们也加入了其他的规则辅助分析：比如通过对接口的抽样数据，分析返回结果中是否包含了敏感参数，这些规则可以通过正则表达式进行分析。以及分析数据的有效性，如：请求的结果，如果仅仅是一些无效的内容，比如日期、一些公共的id，则不会有太大的价值。我们还会维护一个全局的白名单，产生误报后，会加入到白名单里进行过滤，防止二次误报。

# 07 使用这个方法，发现的漏洞

## 7.1 越权类漏洞

![](https://images.seebug.org/content/images/2021/06/61ab2945-c8bc-476b-9cf5-e9f555dfa5dd.png-w331s)

思路：

  * 用不同的测试账号，对于相同属性的业务参数（如policyList），去探测其他用户的敏感数据（修改汽车车牌号以及电话号码获取他人车辆违章信息）。

案例：

  * 图中的例子，在这个请求中，我们可以看到gRPC服务端，允许输入任意的车牌号和电话号码，以至于我们填入正确的数据时，可以看到其他人的车辆违章信息，并可以进行修改。导致这样漏洞的原因，是因为服务端并没有校验当前的用户登陆态，是否有对应业务数据的访问以及修改权限，从而导致了逻辑越权的安全风险。

## 7.2 SSRF漏洞

![](https://images.seebug.org/content/images/2021/06/9247b3e3-7381-475a-8490-960c1c3c0bd1.png-w331s)

思路：

  * 猜测服务端对请求中的URL参数解析的可能，尝试替换为自己的测试域名，在测试域名挂起代理服务，请求后，判断是否会收到内部应用的网络请求。

案例：

  * 从图中的调用链路来看，我们发现，从真实的攻击链路来看，其实resourceUrl经过了多个服务端传递，这也是企业面临的困难，当一个攻击payload请求到服务端后，任何一个服务器节点都可能成为被攻击的对象。

## 7.3 Fastjson漏洞

![](https://images.seebug.org/content/images/2021/06/90027c41-442b-4b15-a0a5-85a9353d4e67.png-w331s)

思路：

  * 根据请求特征，判断请求中的参数，是否可能被后端进行反序列化，用于执行恶意代码（示例中的@”type”特征），并嵌入Fastjson payload。

案例：

  * 这是一个因为日志服务导致的远程RCE漏洞。当时我们发现了一个请求中带有 “@type”的字符串，我们猜测有可能是本地的数据，被服务端进行反序列化。所以，我们在请求中植入了一个Fastjson的远程命令执行的payload。而我们从白天等到了晚上，当我们都以为可能没有成功时，我们收到了相应结果，确认执行成功。因为最终触发的安全漏洞，并不是我们攻击的服务器，而是因为这台服务器将数据以日志的方式存储之后，这些日志被另外一台服务器解析，解析的过程中使用了Fastjson反序列化，从而执行了参数中具有反序列化漏洞的字符串。

# 08 该方案的局限性

尽管我们对整个方案的设计，可以以极低的介入方式集成到整个漏洞挖掘体系中，但是该方案仍然有一定的局限性，主要包含几个方面：

  1. 复杂的逻辑漏洞挖掘，仍然是需要攻克的技术难题：我们在漏洞挖掘的过程中，发现部分请求存在上下游关联的应用场景，这导致贸然对单一的RPC请求进行测试，无法满足执行条件，从而不能触发攻击Payload。

  2. 数据覆盖度的强依赖：本方案的核心是在于给予大量的数据结合算法来进行大规模的漏洞挖掘，这对于大型互联网公司来说，可以借助日志服务通过云计算能力来提高漏洞挖掘的效率。但是从黑盒视角，通过模拟执行以及人工介入，能够获取的RPC数据在覆盖率上要低于拥有日志服务能力的应用程序。

# 09 总结

在过去的时间中，我们基于这样的方法挖掘了上百个安全漏洞。本文主要介绍了我们如何针对gRPC框架，构建漏洞挖掘平台。对于如何挖掘漏洞，在文末只是简单的涉及几种颇有成效的经验。我们认为，在有了体系化的框架之后，可以引入其他的漏洞利用方式，给予框架新的漏洞挖掘能力，用于新的应用场景。

正所谓，授人以鱼不如授人以渔，希望各位看官学习这篇文章之后，可以基于这样的思路发现更多有意思的漏洞利用方法。

![](https://images.seebug.org/content/images/2021/06/15c609f3-31b3-43b9-8e00-051c7276d860.jpg-w331s)

同时我们也意识到，移动互联网的安全问题，不能仅仅依靠移动应用程序上的安全保护机制，来保障应用的安全，需要从端到云，在基础架构层面来构建自己的护城河。这种风险对抗不是单一的防御措施，而是在服务器端构建纵深防御体系的构建。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1616/>

