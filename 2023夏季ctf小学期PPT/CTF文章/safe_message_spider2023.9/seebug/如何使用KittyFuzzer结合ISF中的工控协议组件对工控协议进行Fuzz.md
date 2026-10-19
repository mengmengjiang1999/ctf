**作者：小黑猪（朱文哲）@银河安全实验室  
公众号：[银河安全实验室](https://mp.weixin.qq.com/s/QcGd746CkQVIxx847Zp8Jg "银河安全实验室")**

之前在[《开源工控安全研究框架ISF介绍》](https://mp.weixin.qq.com/s/Ddf0O8zXxj54zCoZJM_D9A
"《开源工控安全研究框架ISF介绍》")这篇文章中，提到了可以利用ISF中的工控协议模块对设备进行进行Fuzz测试，这篇文章将介绍如何具体的使用KittyFuzzer框架来实现。

由于文章主要描述的是如何利用Kitty框架结合ISF中的工控协议组件进行Fuzz，因此不会对Kitty框架本身进行过多的说明，如果对Kitty框架的参数及如何使用存在困惑的可以参考一下[Kitty的官方文档](https://kitty.readthedocs.io/en/latest/)

### 1\. 工具介绍

#### 1.1 kittyFuzzer

Kitty是一个用python编写的模块化及可扩展的开源fuzzing框架，其设计灵感来自OpenRCE的Sulley和Michael
Eddington的Peach Fuzzer(现在是Deja Vu Security的)。

Kitty的设计之初是用于帮助我们fuzz一些非常规的目标(例如一些复杂的非TCP/IP通讯的协议)时不用每次都重复的实现一些基础的功能。因此Kitty被设计成一个通用的抽象的框架，Kitty本身包含了我们所能想到的每个Fuzz测试过程中的公共功能，并且允许用户根据他们特定的目标轻松的进行扩展。

#### 1.2 ISF

ISF是我之前从事工业控制设备漏洞挖掘工作时积累的工控协议和POC代码等内容进行整合后的产物，后来将其中的一部分内容进行了开源，项目的地址是https://github.com/dark-lbp/isf。

[ISF](Industrial Exploitation
Framework)，是一款基于python编写的类似[Metasploit]的工控漏洞利用框架。

ISF基于开源项目[routersploit]修改而来，在routersploit基础框架上针对工控设备增加了工控协议的客户端、工控协议模块等功能。

### 2\. Fuzz Modbus协议

Modbus协议是在工业控制领域使用的非常广泛的一个基础协议，其协议格式也较为简单，没有复杂的协议状态机。下面会对如何利将Kitty框架与ISF框架中的工控协议组件相结合对Modbus-TCP协议执行fuzzing测试进行说明。

#### 2.1. 导入需要的python库

在进行Fuzzing测试之前我们需要使用Kitty框架来构造测试用例，首先我们需要导入一下基础的库。

    
    
    # 从Kitty中导入Template等一系列基础组件
    from kitty.model import Template
    from kitty.interfaces import WebInterface
    from kitty.fuzzers import ServerFuzzer
    from kitty.model import GraphModel
    # 从Kitty扩展库katnip中导入TcpTarget用于Fuzz TCP目标
    from katnip.targets.tcp import TcpTarget
    # 从Kitty扩展库katnip中导入scapy模块用于直接使用Scapy的数据结构
    from katnip.model.low_level.scapy import *
    # 从ISF中导入modbus_tcp相关的数据包结构
    from icssploit.protocols.modbus_tcp import *

#### 2.2. 定义基础参数及数据结构

在导入了需要的模块后，还需要对目标Fuzzing测试对象的IP地址，通讯端口等一些基础参数进行设置。

    
    
    # 定义目标Fuzz对象的IP地址
    TARGET_IP = '172.16.22.131'
    # 定义目标Fuzz对象的通讯端口
    TARGET_PORT = 502
    # 定义随机数种子
    RANDSEED = int(RandShort())

在Modbus-TCP Fuzzing的例子中，我们将使用Modbus-TCP协议中的ReadCoilsRequest请求进行测试，下图是一个典型的Modbus Read Coils请求数据包。

![
](https://images.seebug.org/content/images/2018/12/418c6e75-3a81-4922-8799-f56d3f7b94df.jpg-w331s)

下面的代码将介绍如何利用ScapyField将ISF框架中Modbus-TCP协议的ReadCoilsRequest数据包结构直接应用于Kitty中的例子。

    
    
    # 根据ISF中Modbus-tcp协议的数据结构构造测试数据包,下面例子中将使用RandShort对请求的地址及bit位长度进行测试。
    read_coils_request_packet = ModbusHeaderRequest(func_code=0x01)/ReadCoilsRequest(ReferenceNumber=RandShort(), BitCount=RandShort())
    
    # 使用ScapyField直接将Scapy的数据包结构应用于Kitty框架中。
    read_coils_request_template = Template(name='Read Coils Request', fields=[
        ScapyField(read_coils_request_packet,
                   name='read_coils_request_packet',  # 定义这个Field的名字，用于在报告中显示
                   fuzzable=True,  # 定义这个Field是否需要Fuzz
                   seed=RANDSEED,  # 定义用于变异的随机数
                   fuzz_count=2000  # 这个数据结构的fuzz次数
                   ),
    ])
    
    # 使用GraphModel进行Fuzz
    model = GraphModel()
    # 在使用GraphModel中注册第一个节点，由于Modbus的Read Coils请求是单次的请求/回答形式，因此这里只要注册简单的一个节点即可。
    model.connect(read_coils_request_packet)

#### 2.3. 进行Fuzz模式配置

在完成了基础的定义后，还需要对Fuzz的模式等进行如下配置。

    
    
    # 定义一个目标Target, 设置IP、端口及连接超时时间。
    modbus_target = TcpTarget(name='modbus target', host=TARGET_IP, port=TARGET_PORT, timeout=2)
    
    # 定义是需要等待Target返回响应，如果设置为True Target不返回数据包则会被识别成异常进行记录。
    modbus_target.set_expect_response(True)
    
    # 定义使用ServerFuzzer的方式进行Fuzz测试
    fuzzer = ServerFuzzer()
    # 定义fuzzer使用的交互界面为web界面
    fuzzer.set_interface(WebInterface(port=26001))
    # 在fuzzer中定义使用GraphModel
    fuzzer.set_model(model)
    # 在fuzzer中定义target为modbus_target
    fuzzer.set_target(modbus_target)
    # 定义每个测试用例发送之间的延迟
    fuzzer.set_delay_between_tests(0.1)
    # 开始执行Fuzz
    fuzzer.start()

完成上述的设置后即可使用python命令执行这个脚本对目标进行测试了，运行后将会在命令行终端看到如下图所示的输出。

![
](https://images.seebug.org/content/images/2018/12/696eb05e-7c62-48d6-bb11-ce58bbd14b5a.jpg-w331s)

此时也可以通过开启的web管理界面来查看Fuzzing测试的状态。

![
](https://images.seebug.org/content/images/2018/12/65bfb107-3c55-4693-984b-93265e244131.jpg-w331s)

上面介绍的是最基础的直接使用ISF中的数据结构来对协议进行Fuzzing的例子，如果想针对性的测试Modbus不同的功能码，那么就需要修改数据结构定义的部分，下面是Fuzzing写线圈数据包的例子。

    
    
    write_coils_request_packet = ModbusHeaderRequest(func_code=0x05)/WriteSingleCoilRequest(ReferenceNumber=RandShort(), Value=RandShort())
    
    
    # 使用ScapyField直接将Scapy的数据包结构应用于Kitty框架中
    write_coils_request_packet_template = Template(name='Write Coils Request', fields=[
        ScapyField(write_coils_request_packet,
                   name='wrire_coils_request_packet',  # 定义这个Field的名字，用于在报告中显示
                   fuzzable=True,  # 定义这个Field是否需要Fuzz
                   seed=RANDSEED,  # 定义用于变异的随机数
                   fuzz_count=2000  # 这个数据结构的fuzz次数
                   ),
    ])
    
    model.connect(write_coils_request_packet_template)

#### 2.4. 完整代码

完整Fuzzing测试用例代码如下。

    
    
    # !/usr/bin/env python2
    # coding=utf-8
    from kitty.model import Template
    from kitty.interfaces import WebInterface
    from kitty.fuzzers import ServerFuzzer
    from kitty.model import GraphModel
    from katnip.targets.tcp import TcpTarget
    from katnip.model.low_level.scapy import *
    from icssploit.protocols.modbus_tcp import *
    
    
    TARGET_IP = '172.16.22.131'
    TARGET_PORT = 502
    RANDSEED = int(RandShort())
    
    # 根据ISF中Modbus-tcp协议的数据结构构造测试数据包,下面例子中将使用RandShort对请求的地址及写入的值进行变异测试。
    write_coils_request_packet = ModbusHeaderRequest(func_code=0x05)/WriteSingleCoilRequest(ReferenceNumber=RandShort(), Value=RandShort())
    
    # 使用ScapyField直接将Scapy的数据包结构应用于Kitty框架中
    write_coils_request_packet_template = Template(name='Write Coils Request', fields=[
        ScapyField(write_coils_request_packet,
                   name='wrire_coils_request_packet',  # 定义这个Field的名字，用于在报告中显示
                   fuzzable=True,  # 定义这个Field是否需要Fuzz
                   seed=RANDSEED,  # 定义用于变异的随机数
                   fuzz_count=2000  # 这个数据结构的fuzz次数
                   ),
    ])
    
    # 使用GraphModel进行Fuzz
    model = GraphModel()
    # 在使用GraphModel中注册第一个节点。
    model.connect(write_coils_request_packet_template)
    
    # 定义一个目标Target, 设置IP、端口及连接超时时间。
    modbus_target = TcpTarget(name='modbus target', host=TARGET_IP, port=TARGET_PORT, timeout=2)
    
    # 定义是需要等待Target返回响应，如果设置为True Target不返回数据包则会被识别成异常进行记录。
    modbus_target.set_expect_response(True)
    
    # 定义使用基础的ServerFuzzer进行Fuzz测试
    fuzzer = ServerFuzzer()
    # 定义fuzzer使用的交互界面为web界面
    fuzzer.set_interface(WebInterface(port=26001))
    # 在fuzzer中定义使用GraphModel
    fuzzer.set_model(model)
    # 在fuzzer中定义target为modbus_target
    fuzzer.set_target(modbus_target)
    # 定义每个测试用例发送之间的延迟
    fuzzer.set_delay_between_tests(0.1)
    # 开始执行Fuzz
    fuzzer.start()

### 3\. Fuzz 西门子s7comm协议

西门子s7comm协议是大部分西门子S7-300/400系列PLC默认使用的通讯协议，s7comm协议与Modbus-TCP协议有所不同，s7comm协议由TPKT协议及ISO-COTP协议封装后进行传输，且发送实际控制指令前必须先经过建立COTP连接及配置s7comm通讯参数这两个步骤。下面会对如何解决这些问题，对西门子S7comm协议执行Fuzzing测试进行说明。

#### 3.1. 导入需要的python库

此处的操作和进行Modbus-TCP Fuzzing测试时基本相同，只需要额外引入S7comm的协议数据结构即可。

    
    
    from kitty.model import Template
    from kitty.interfaces import WebInterface
    from kitty.fuzzers import ServerFuzzer
    from kitty.model import GraphModel
    from katnip.targets.tcp import TcpTarget
    from katnip.model.low_level.scapy import *
    # 从ISF中导入s7comm相关的数据包结构
    from icssploit.protocols.s7comm import *

#### 3.2. 定义基础参数及数据结构

如之前所说，S7comm协议在发送具体的请求参数前，需要先建立COTP连接并进行通讯参数配置，具体的流程如下图所示。

![
](https://images.seebug.org/content/images/2018/12/89663aab-2664-4aab-b523-a61254b3d3be.jpg-w331s)

因此我们在对请求操作进行Fuzzing测试时也需要先事先建立COTP连接，完成通讯参数配置后才能发送对应的测试数据。

首先需要对目标设备的一些连接信息进行设置，TSAP相关的参数涉及到目标设备的槽位号和连接方式等信息被用于建立COTP-CR连接时使用，具体参数需要根据实际测试设备在编程时的槽位号进行调整。

    
    
    # snap7 server 配置信息
    TARGET_IP = '172.16.22.131'
    TARGET_PORT = 102
    RANDSEED = int(RandShort())
    SRC_TSAP = "0100".encode('hex')  # COTP CR请求的参数
    DST_TSAP = "0102".encode('hex')  # COTP CR请求的参数

随后我们则需要进一步构造用于建立连接的数据包结构及需要进行fuzzing测试的数据包格式， 具体的代码及说明如下。

    
    
    # 定义COTP CR建立连接数据包
    COTP_CR_PACKET = TPKT()/COTPCR()
    COTP_CR_PACKET.Parameters = [COTPOption() for i in range(3)]
    COTP_CR_PACKET.PDUType = "CR"
    COTP_CR_PACKET.Parameters[0].ParameterCode = "tpdu-size"
    COTP_CR_PACKET.Parameters[0].Parameter = "\x0a"
    COTP_CR_PACKET.Parameters[1].ParameterCode = "src-tsap"
    COTP_CR_PACKET.Parameters[2].ParameterCode = "dst-tsap"
    COTP_CR_PACKET.Parameters[1].Parameter = SRC_TSAP
    COTP_CR_PACKET.Parameters[2].Parameter = DST_TSAP
    
    # 因为是建立连接使用，因此fuzzable参数需要设置为False避免数据包被变异破坏。
    # 如果想对建立连接的过程也进行分Fuzz的话，则可以另行编写测试用例。
    COTP_CR_TEMPLATE = Template(name='cotp_cr', fields=[
        ScapyField(COTP_CR_PACKET, name='cotp_cr', fuzzable=False),
    ])
    
    # 定义通讯参数配置数据结构
    SETUP_COMM_PARAMETER_PACKET = TPKT() / COTPDT(EOT=1) / S7Header(ROSCTR="Job", Parameters=S7SetConParameter())
    
    # 因为是建立连接使用，因此fuzzable参数需要设置为False避免数据包被变异破坏。
    # 如果想对建立连接的过程也进行分Fuzz的话，则可以另行编写测试用例。
    SETUP_COMM_PARAMETER_TEMPLATE = Template(name='setup comm template', fields=[
        ScapyField(SETUP_COMM_PARAMETER_PACKET, name='setup comm', fuzzable=False),
    ])
    
    # 定义需要Fuzzing的数据包结构, 下面例子中将使用RandShort对请求的SZLId及SZLIndex值进行变异测试。
    READ_SZL_PACKET = TPKT() / COTPDT(EOT=1) / S7Header(ROSCTR="UserData", Parameters=S7ReadSZLParameterReq(),Data=S7ReadSZLDataReq(SZLId=RandShort(), SZLIndex=RandShort()))
    
    # 定义READ_SZL_TEMPLATE为可以进行变异的结构，fuzzing的次数为1000次
    READ_SZL_TEMPLATE = Template(name='read szl template', fields=[
        ScapyField(READ_SZL_PACKET, name='read szl', fuzzable=True, fuzz_count=1000),
    ])
    
    # 在完成了上述的结构定义后就可以使用GraphModel将这些数据包结构进行前后关联。
    # 使用GraphModel进行Fuzz
    model = GraphModel()
    # 在GraphModel中注册第一个节点, 首先发送COTP_CR请求。
    model.connect(COTP_CR_TEMPLATE)
    # 在GraphModel中注册第二个节点, 在发送完COTP_CR后发送SETUP_COMM_PARAMETER请求。
    model.connect(COTP_CR_TEMPLATE, SETUP_COMM_PARAMETER_TEMPLATE)
    # 在GraphModel中注册第三个节点, 在发送完SETUP_COMM_PARAMETER后发送READ_SZL请求。
    model.connect(SETUP_COMM_PARAMETER_TEMPLATE, READ_SZL_TEMPLATE)

#### 3.3. 进行Fuzz模式配置

在完成了上述的定义后，剩下的配置和Modbus基本一致，只需要修改一下Target的名称等即可。

    
    
    # define target
    s7comm_target = TcpTarget(name='s7comm target', host=TARGET_IP, port=TARGET_PORT, timeout=2)
    
    # 定义是需要等待Target返回响应，如果设置为True Target不返回数据包则会被识别成异常进行记录。
    s7comm_target.set_expect_response(True)
    
    # 定义使用基础的ServerFuzzer进行Fuzz测试
    fuzzer = ServerFuzzer()
    # 定义fuzzer使用的交互界面为web界面
    fuzzer.set_interface(WebInterface(port=26001))
    # 在fuzzer中定义使用GraphModel
    fuzzer.set_model(model)
    # 在fuzzer中定义target为s7comm_target
    fuzzer.set_target(s7comm_target)
    # 定义每个测试用例发送之间的延迟
    fuzzer.set_delay_between_tests(0.1)
    # 开始执行Fuzz
    fuzzer.start()

完成上述的设置后即可使用python命令执行这个脚本对目标进行测试了，运行后将会在命令行终端看到如下图所示的输出。

![
](https://images.seebug.org/content/images/2018/12/b5eeb53f-be60-461e-a7f9-5aae2f37b2a9.jpg-w331s)

此时也可以通过开启的web管理界面来查看Fuzzing测试的状态

![
](https://images.seebug.org/content/images/2018/12/6388223a-d3f6-4374-bbf2-80118a2b3aa8.jpg-w331s)

上面介绍的是使用Kitty结合ISF中的协议数据结构对西门子S7comm协议进行Fuzzing的例子，如果想针对性的测试S7comm的不同协议功能码依旧需要修改数据结构定义的部分。

#### 3.4. 完整代码

下面是Fuzzing Read SZL结构的完整测试用例。

    
    
    #!/usr/bin/python2
    # coding:utf-8
    from kitty.model import Template
    from kitty.interfaces import WebInterface
    from kitty.fuzzers import ServerFuzzer
    from kitty.model import GraphModel
    from katnip.targets.tcp import TcpTarget
    from katnip.model.low_level.scapy import *
    # 从ISF中导入cotp相关的数据包结构
    from icssploit.protocols.cotp import *
    # 从ISF中导入s7comm相关的数据包结构
    from icssploit.protocols.s7comm import *
    
    # snap7 server 配置信息
    TARGET_IP = '172.16.22.131'
    TARGET_PORT = 102
    RANDSEED = int(RandShort())
    SRC_TSAP = "0100".encode('hex')
    DST_TSAP = "0103".encode('hex')
    
    # 定义COTP CR建立连接数据包
    COTP_CR_PACKET = TPKT()/COTPCR()
    COTP_CR_PACKET.Parameters = [COTPOption() for i in range(3)]
    COTP_CR_PACKET.PDUType = "CR"
    COTP_CR_PACKET.Parameters[0].ParameterCode = "tpdu-size"
    COTP_CR_PACKET.Parameters[0].Parameter = "\x0a"
    COTP_CR_PACKET.Parameters[1].ParameterCode = "src-tsap"
    COTP_CR_PACKET.Parameters[2].ParameterCode = "dst-tsap"
    COTP_CR_PACKET.Parameters[1].Parameter = SRC_TSAP
    COTP_CR_PACKET.Parameters[2].Parameter = DST_TSAP
    
    # 因为是建立连接使用，因此fuzzable参数需要设置为False避免数据包被变异破坏。
    COTP_CR_TEMPLATE = Template(name='cotp cr template', fields=[
        ScapyField(COTP_CR_PACKET, name='cotp cr', fuzzable=False),
    ])
    
    # 定义通讯参数配置数据结构
    SETUP_COMM_PARAMETER_PACKET = TPKT() / COTPDT(EOT=1) / S7Header(ROSCTR="Job", Parameters=S7SetConParameter())
    
    SETUP_COMM_PARAMETER_TEMPLATE = Template(name='setup comm template', fields=[
        ScapyField(SETUP_COMM_PARAMETER_PACKET, name='setup comm', fuzzable=False),
    ])
    
    # 定义需要Fuzzing的数据包结构, 下面例子中将使用RandShort对请求的SZLId及SZLIndex值进行变异测试。
    READ_SZL_PACKET = TPKT() / COTPDT(EOT=1) / S7Header(ROSCTR="UserData", Parameters=S7ReadSZLParameterReq(),Data=S7ReadSZLDataReq(SZLId=RandShort(), SZLIndex=RandShort()))
    
    # 定义READ_SZL_TEMPLATE为可以进行变异的结构，fuzzing的次数为1000次
    READ_SZL_TEMPLATE = Template(name='read szl template', fields=[
        ScapyField(READ_SZL_PACKET, name='read szl', fuzzable=True, fuzz_count=1000),
    ])
    
    # 使用GraphModel进行Fuzz
    model = GraphModel()
    # 在使用GraphModel中注册第一个节点, 首先发送COTP_CR请求。
    model.connect(COTP_CR_TEMPLATE)
    # 在使用GraphModel中注册第二个节点, 在发送完COTP_CR后发送SETUP_COMM_PARAMETER请求。
    model.connect(COTP_CR_TEMPLATE, SETUP_COMM_PARAMETER_TEMPLATE)
    # 在使用GraphModel中注册第三个节点, 在发送完SETUP_COMM_PARAMETER后发送READ_SZL请求。
    model.connect(SETUP_COMM_PARAMETER_TEMPLATE, READ_SZL_TEMPLATE)
    
    # define target
    s7comm_target = TcpTarget(name='s7comm target', host=TARGET_IP, port=TARGET_PORT, timeout=2)
    
    # 定义是需要等待Target返回响应，如果设置为True Target不返回数据包则会被识别成异常进行记录。
    s7comm_target.set_expect_response(True)
    
    # 定义使用基础的ServerFuzzer进行Fuzz测试
    fuzzer = ServerFuzzer()
    # 定义fuzzer使用的交互界面为web界面
    fuzzer.set_interface(WebInterface(port=26001))
    # 在fuzzer中定义使用GraphModel
    fuzzer.set_model(model)
    # 在fuzzer中定义target为s7comm_target
    fuzzer.set_target(s7comm_target)
    # 定义每个测试用例发送之间的延迟
    fuzzer.set_delay_between_tests(0.1)
    # 开始执行Fuzz
    fuzzer.start()

### 4\. 小结

通过将Kitty与基于Scapy的数据包结构进行结合能够基于一些现有的协议组件(例如ISF或Scapy中原生的协议)快速的构造一个高度自定义的Fuzzing测试用例，特别是在面对复杂的协议时可以减少大量的协议数据结构编写等大量工作。

Kitty的可扩展性非常强，而且本文只涉及到了其中非常少的一部分功能，通过对Kitty进行扩展可以快速的针对特定目标构造对应的Fuzzing工具。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/772/>

