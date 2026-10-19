## **Protobuf**

Protocol Buffers 是一种序列化数据结构的协议，在通过管道或存储数据进行通信的程序开发上很有用。Protobuf 通过 .proto 文件
定义数据结构，使用代码生成器生成的代码来读写这个数据结构，即可通过各种不同语言或从各种不同数据流中对已定义好的数据统一读写。

可以看出， Protobuf 的初衷应该是打造一个统一、易用、适配性广的接口协议，类似 Json 。因此， Protobuf 的攻击面非常广。本文以应用了
Protobuf 的 Fuzz 为出发点，来进行一些探索与实验。

##  **应用**

Protobuf 的开源应用例子很多：

 **● MySql X plugin** ：MySQL 5.7 发布时自带此插件，启用后可通过 X Protocol 协议实现 Client 与
Server 通信，使用 Protobuf 接口交互。

 **● gRPC** ：Google 开发的用 Protobuf 通信的 rpc 系统，采用 ProtoBuf 作为 IDL
，生成客户端和服务端代码。用户实现服务端代码中的调用接口，并且利用客户端代码来发起请求到服务端。

 **● PowerDns** ：带有用 Protobuf 格式解析、发送 DNS 请求的功能。

 **● VLC** ：往 chromecast 上远程投影和通信时使用 Protobuf 协议。

为了对使用了 Protobuf 的应用进行模糊测试，传统的基于突变的 Fuzzing 往往不能满足需求：

 **首先** ，传统的 Fuzz 方式（例如字节变异）不太符合我们的需求，因为按字节变异的 Fuzz 往往目标涵盖了 Protobuf
自身的功能健全性测试。例如它的序列化与反序列化，而 Protobuf 本身在这方面已非常成熟；

 **其次** ，我们的主要目标是测试使用 Protobuf
的应用中对字段的处理问题。因此，应该优先考虑基于生成的模糊测试，即，如何生成合格的、符合不同应用的 Protobuf 格式的测试用例。

##  **ProtoFuzz**

针对 protobuf 协议进行模糊测试，已经有一些工作进行了一些探索。

ProtoFuzz 是 Trailofbits 公司在 2016 年开源的一款基于 Protobuf 协议格式生成的模糊测试工具。我们先使用
ProtoFuzz 进行测试。https://github.com/trailofbits/protofuzz

Protofuzz 是一个 python package ，我们可以通过源码以及 pip 包管理器的方式进行安装。

它的使用方式很直观：

![1619431861_608691b50d7f3d8f83534.png!small](https://image.3001.net/images/20210426/1619431861_608691b50d7f3d8f83534.png!small)

Protofuzz 可从字符串或者 proto 文件载入 Protobuf 格式信息，再调用 permute 就可开始生成符合Protobuf
结构体的测试用例。

##  **实战 MySQL X**

以上文提到的 MySql X plugin 为例，找到 MySql 的 Protobuf 格式文件，源码路径为mysql-server/plugin/x/protocol/protobuf：

![1619431881_608691c9d3246ecdc9983.png!small](https://image.3001.net/images/20210426/1619431881_608691c9d3246ecdc9983.png!small)

以 mysqlx_sql.proto 里 StmtExecute 这个结构体为例：

![1619431899_608691dbd4ccd7cf9de3d.png!small](https://image.3001.net/images/20210426/1619431899_608691dbd4ccd7cf9de3d.png!small)

在将mysqlx_sql.proto文件作为变量传入ProtoFuzz之前，需要注意一个小问题，这个proto文件import了另外两个proto文件：

![1619431910_608691e617f496bb59708.png!small](https://image.3001.net/images/20210426/1619431910_608691e617f496bb59708.png!small)

这里需要手工把相应内容复制过来。

接着开始尝试生成测试用例时，会遇到这样的错误：

![1619431938_60869202b98da2e4b3a19.png!small](https://image.3001.net/images/20210426/1619431938_60869202b98da2e4b3a19.png!small)

查看源码与该结构体内容后发现，StmtExecute 这个表示 sql 语句的结构中，用了mysqlx_ datatypes.proto 文件中的 Any
结构体表示sql 语句的变量，参数是动态的，因此 Any 变量的结构有递归的性质，如下：

![1619431979_6086922b6a22b6600d41d.png!small](https://image.3001.net/images/20210426/1619431979_6086922b6a22b6600d41d.png!small)

ProtoFuzz 源码 （protofuzz/protofuzz.py）中，并没有处理这种特性，于是会无限递归导致了上面的错误：

![1619431996_6086923ca6a539beada0c.png!small](https://image.3001.net/images/20210426/1619431996_6086923ca6a539beada0c.png!small)

在暂时注释掉导致无限递归的结构（ Array 与Object 中的 Any ）之后，便可开始生成测试用例了：

![1619432023_6086925718810d3241715.png!small](https://image.3001.net/images/20210426/1619432023_6086925718810d3241715.png!small)

##  **测试**

为了将测试用例发送给 MySql Server ，我们通过 mysql-connector-python ，一个 MySql
官方提供的驱动器，来把生成的测试用例发给 MySql server 。因此，需要先找到 mysql-connector-python 源码中将 sql
语句转化为 Protobuf 并发送的地方，涉及到的代码有：

●mysql-connector-python\lib\mysqlx\

protobuf__init__.py 中的Message 结构体，其中的
**set_message、from_message、serialize_to_string** 方法可方便地将 ProtoFuzz 生成地测试用例转化为该
Message结构，供 mysql-connector-python 调用：

![1619432048_60869270614d6006bb603.png!small](https://image.3001.net/images/20210426/1619432048_60869270614d6006bb603.png!small)

 **●** mysql-connector-python\lib\mysqlx

\connection.py中的 **send_sql** 函数，在这里面结合上面Message代码，加入ProtoFuzz来实现循环发送测试用例：

![1619432064_60869280f0f26c9cb1acf.png!small](https://image.3001.net/images/20210426/1619432064_60869280f0f26c9cb1acf.png!small)

● 调用 mysql-connector-python 的客户端代码：

![1619432076_6086928cabc6854a7c316.png!small](https://image.3001.net/images/20210426/1619432076_6086928cabc6854a7c316.png!small)

● 启动带X plugin的MySql 服务后，运行：

![1619432100_608692a426e1b519ccbf6.png!small](https://image.3001.net/images/20210426/1619432100_608692a426e1b519ccbf6.png!small)

##  **总结**

本文以 Fuzz Protobuf 为出发点，以 Mysql X plugin 为例子，测试了针对 Protobuf 结构的变异方法初步进行 Fuzz
。在实验过程中，可以发现已有的基于生成的 Protobuf 协议的 Fuzzer ，存在一些问题：

> ● 针对开源代码，且对于不同的 Protobuf 应用，都需要手动针对性地配置；
>
> ● 现有的ProtoFuzz对Protobuf结构处理不是很健全。

除此之外，值得一提的是，另一个针对 Protobuf 进行模糊测试的工具：libprotobuf-mutator，可与 libfuzzer
结合，实现了覆盖率导向的结构敏感模糊测试(Coverage-guide Structure-Aware Fuzzing)，值得我们进一步测试。

