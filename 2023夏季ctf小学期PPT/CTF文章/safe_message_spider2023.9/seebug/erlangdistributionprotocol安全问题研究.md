**作者：lxraa  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org **

# 前言

由于目前公司部分业务使用erlang实现，中文互联网上对于erlang安全问题研究较少，为了了解erlang应用的安全问题本人结合代码和公开资料进行了一些研究。

本文为erlang安全研究项目中针对erlang distribution通信协议的研究，目的是解决erlang应用的公网暴露面问题。

文中的pcap包，文档，代码存放于`https://github.com/lxraa/erl-matter/tree/master/otp25`

# 一、环境搭建（windows）

## 1、erlang运行环境安装

[Downloads - Erlang/OTP](https://www.erlang.org/downloads)

## 2、erlang包管理安装-rebar3

    
    
    git clone https://github.com/erlang/rebar3.git
    cd rebar3
    ./bootstrap

## 3、erlang调试环境搭建（vscode）

[VSCode Debug Erlang工程配置_犀牛_2046的博客-CSDN博客_vscode调试erlang](https://blog.csdn.net/weixin_38044597/article/details/118194771)

    
    
    # vscode安装erlang插件时可能会出现以下提示
    # no such file or directory pgourlain..._build...
    # 原因是vscode erlang extension（pgourlain）不会自己编译
    # 需要手动到extension目录下，使用rebar3 compile编译，生成_build文件夹

![](https://images.seebug.org/content/images/2022/09/93b77420-45d2-4fb3-b2b9-d51b08964339.png-w331s)

# 二、erlang集群通信demo

## 1、erlang语言的特点

  * 解释型语言

  * 函数式

  * 无反射

  * 擅长并行处理

    * 维护了一套ring3的线程，因此线程调度并不依赖syscall，开销较小，可以轻易创建大量线程。
  * 自带分布式

    * 底层通过rpc调用。

    * 由于没有反射，集群通信不存在反序列化rce（反序列化的本质是绕过黑名单的method.invoke），但是仍然可能存在其他安全问题。

## 2、集群通信原理图

![](https://images.seebug.org/content/images/2022/09/01415554-e57f-46e4-bbfe-28c2a9a1ffb3.png-w331s)

1、machine1对外开放服务时，会先在4369端口开放epmd服务，这个服务可以理解为注册中心，用来保存machine1服务的(name,port)

2、machine2想调用machine1的服务时，需要先找epmd拿到machine1的(name,port)列表

3、machine2直接连接machine1的port，rpc调用

## 3、通信demo

开启一个linux虚拟机，使用windows远程调用linux节点

  * 以debug模式开启，为了方便连接，给机器指定一个hostname

    
    
    # linux
    epmd -d
    hostname localcentos2

![](https://images.seebug.org/content/images/2022/09/2bc3c0b0-ba1f-4b79-ae5b-22509d9814c5.png-w331s)

  * 使用-sname指定名称，erl会自动把process对外开放，并注册到epmd（没有epmd时，还会自动开启epmd）

    
    
    erl -sname test

![](https://images.seebug.org/content/images/2022/09/48ce491d-b296-4eb2-8f78-b7db54de9fca.png-w331s)

![](https://images.seebug.org/content/images/2022/09/3eefd930-f2e0-449c-8bd6-33f460cff4e4.jpg-w331s)

  * 设置cookie

    
    
    %%注意，erlang中单引号代表atom类型，并不是string
    
    %% atom可以理解为全局唯一标识符，类似js的Symbol
    
    auth:set_cookie('123456'). 

  * windows开启erlang shell,并配置与linux node相同的cookie

host文件互相加dns解析记录

    
    
    erlang -sname test
    >> auth:set_cookie('123456').

  * 连接节点，并查看是否连接成功

    
    
    %% 连接 记得关闭linux防火墙 systemctl stop firewalld
    net_adm:ping('test@localcentos2').
    %% 查看已连接的节点
    nodes().

![](https://images.seebug.org/content/images/2022/09/b2359a4c-2a62-4ddb-8fca-b94873f6c2a2.png-w331s)

  * 这时test@PPC2LXR和test@localcentos2连接成功

    
    
    %% 执行代码
    rpc:call('test@localcentos2','os','cmd',["touch /tmp/connect_success.txt"]).

![](https://images.seebug.org/content/images/2022/09/c54e8ed2-c66a-46c6-b535-3a217f9abeed.png-w331s)

可以看到，process是通过cookie保护的，拿到cookie相当于拥有执行任意代码权限，以下解决两个问题

1、认证是与epmd通信还是与process通信？

2、认证过程是否存在安全问题？

# 三、epmd协议分析

epmd是一台主机erlang节点的注册服务，提供了name到node的解析，可以理解为一个注册中心，用来告诉外部连接这个主机上的node信息。当有外部主机请求epmd服务时，epmd返回当前主机上所有node监听端口信息和节点的name

    
    
    erl
    1> net_adm:names("localcentos2").
    {ok,[{"test",36612}]}

注意，epmd是没有认证的，也就是说epmd会暴露该主机所有通过sname或name启动的process信息，且
**epmd对非local的操作只支持查询，代码在** otp_src/erts/epmd/src/epmd_src.c:line 799 : void
do_request(g, fd, s, buf, bsize)

    
    
    ...
    case EPMD_ALIVE2_REQ:
        //只允许local调用
        dbg_printf(g, 1, "** got ALIVE2_REQ");
        if (!s->local_peer)
        {
          dbg_printf(g, 0, "ALIVE2_REQ from non local address");
          return;
        }
    
    
      case EPMD_PORT2_REQ:
        dbg_printf(g, 1, "** got PORT2_REQ");
    
        if (buf[bsize - 1] == '\000') /* Skip null termination */
          bsize--;
    
        if (bsize <= 1)
        {
          dbg_printf(g, 0, "packet too small for request PORT2_REQ (%d)", bsize);
          return;
        }
    
        for (i = 1; i < bsize; i++)
          if (buf[i] == '\000')
          {
            dbg_printf(g, 0, "node name contains ascii 0 in PORT2_REQ");
            return;
          }
    
        {
          char *name = &buf[1]; /* Points to node name */
          int nsz;
          Node *node;
    
          nsz = verify_utf8(name, bsize, 0);
          if (nsz < 1 || 255 < nsz)
          {
            dbg_printf(g, 0, "invalid node name in PORT2_REQ");
            return;
          }
    
          wbuf[0] = EPMD_PORT2_RESP;
          for (node = g->nodes.reg; node; node = node->next)
          {
            int offset;
            if (is_same_str(node->symname, name))
            {
              wbuf[1] = 0; /* ok */
              put_int16(node->port, wbuf + 2);
              wbuf[4] = node->nodetype;
              wbuf[5] = node->protocol;
              put_int16(node->highvsn, wbuf + 6);
              put_int16(node->lowvsn, wbuf + 8);
              put_int16(length_str(node->symname), wbuf + 10);
              offset = 12;
              offset += copy_str(wbuf + offset, node->symname);
              put_int16(node->extralen, wbuf + offset);
              offset += 2;
              memcpy(wbuf + offset, node->extra, node->extralen);
              offset += node->extralen;
              if (!reply(g, fd, wbuf, offset))
              {
                dbg_tty_printf(g, 1, "** failed to send PORT2_RESP (ok) for \"%s\"", name);
                return;
              }
              dbg_tty_printf(g, 1, "** sent PORT2_RESP (ok) for \"%s\"", name);
              return;
            }
          }
          wbuf[1] = 1; /* error */
          if (!reply(g, fd, wbuf, 2))
          {
            dbg_tty_printf(g, 1, "** failed to send PORT2_RESP (error) for \"%s\"", name);
            return;
          }
          dbg_tty_printf(g, 1, "** sent PORT2_RESP (error) for \"%s\"", name);
          return;
        }
        break;
    
      case EPMD_NAMES_REQ:
        dbg_printf(g, 1, "** got NAMES_REQ");
       ...
       break;
      case EPMD_DUMP_REQ:
        dbg_printf(g, 1, "** got DUMP_REQ");
        if (!s->local_peer)
        {
          dbg_printf(g, 0, "DUMP_REQ from non local address");
          return;
        }
        // 只允许local调用
        ...
        break;
    
      case EPMD_KILL_REQ:
        if (!s->local_peer)
        {
          dbg_printf(g, 0, "KILL_REQ from non local address");
          return;
        }
        dbg_printf(g, 1, "** got KILL_REQ");
    
       // 只允许local调用
    
      case EPMD_STOP_REQ:
        dbg_printf(g, 1, "** got STOP_REQ");
        if (!s->local_peer)
        {
          dbg_printf(g, 0, "STOP_REQ from non local address");
          return;
        }
        // 只允许local调用
        break;
    
      default:
        dbg_printf(g, 0, "got garbage ");
      }

EPMD_NAMES_REQ显然是用来响应net_adm:names().，以下调试EPMD_PORT2_REQ

①修改epmd代码，在do_request前print输出tcp包的内容，并`make&&make install`，在主机A通过epmd
-d启动epmd的调试模式：

    
    
    // epmd_srv.c - print16:
    ...
    print16(s->buf,s->got);
    do_request(g, s->fd, s, s->buf + 2, s->got - 2);
    ...
    static int print16(char * s,unsigned int size){
      int i = 0;
      int count = 0;
      for(i = 0;i < size;i++){
        if(count > 16){
          count = 0;
        }
        printf("%x ",s[i]);
        count++;
      }
      printf("\n");
      return 0;
    }

②使用`erl -sname test` 在主机A重新启动一个process，得到调试信息：

    
    
    invoke do_request
    0 11 78 ffffffa8 d 4d 0 0 6 0 5 0 4 74 65 73 74 0 0 
    epmd: Mon Sep  5 15:50:22 2022: ** got ALIVE2_REQ
    epmd: Mon Sep  5 15:50:22 2022: registering 'test:1662364223', port 43021
    epmd: Mon Sep  5 15:50:22 2022: type 77 proto 0 highvsn 6 lowvsn 5
    epmd: Mon Sep  5 15:50:22 2022: ** sent ALIVE2_RESP for "test"

③从主机B发起cookie错误的连接请求：

    
    
    %% 主机A  这句并不会得到调试信息，也就是说node的auth信息并不会通知epmd
    auth:set_cookie("654321").
    %% 主机B
    erl -sname test2
    auth:set_cookie("123456").
    net_adm:ping("test@192.168.245.128").

得到debug信息，可以看到请求包并不包含认证信息，也就是说auth是直接在process之间进行的，epmd不负责认证

    
    
    invoke do_request
    0 5 7a 74 65 73 74   
    epmd: Mon Sep  5 15:55:14 2022: ** got PORT2_REQ
    epmd: Mon Sep  5 15:55:14 2022: ** sent PORT2_RESP (ok) for "test"

0 5 前两个字节为长度

7a 74 65 73 74即为z t e s t ，z是控制字符，请求name为test的process信息

# 四、erlang-distribution握手协议分析

process通信安全问题之前有人研究过：<https://github.com/gteissier/erl-matter>

先给结论：

1、erl默认生成的cookie是伪随机的，可以被爆破。

2、erl distribution protocol握手靠cookie保护，通信过程没有认证，且默认无tls，可被中间人攻击。

由于erlang otp（标准库，里面含分布式通信的代码）通信协议在变化，高版本OTP process并不能与低版本通信，erl-matter工程的测试代码在otp 25（最新版本）下没有测试成功。

以下结合[官方文档](https://www.erlang.org/doc/apps/erts/erl_dist_protocol.html)对通信细节的描述和wireshark的抓包结果复现一下握手过程

（为了方便阅读，这里提供一个我的[翻译版](\[erl-matter/\[翻译\]erlang分发协议-erl distribution
protocal（OTP 25）.pdf at master · lxraa/erl-matter ·
GitHub\]\(https://github.com/lxraa/erl-matter/blob/master/otp25/%5B%E7%BF%BB%E8%AF%91%5Derlang%E5%88%86%E5%8F%91%E5%8D%8F%E8%AE%AE-erl%20distribution%20protocal%EF%BC%88OTP%2025%EF%BC%89.pdf\))，握手在13.2 章）

实验机器：

hostname | ip | system_type | 别名  
---|---|---|---  
PPC2LXR | 192.168.245.1 | WINDOWS | machine1  
localcentos1 | 192.168.245.128 | linux | machine2  
  
python3代码：

见本章末

1、windows和linux重新开启process后执行以下命令，使用wireshark抓到握手包

    
    
    net_adm:ping('test@localcentos1').

![](https://images.seebug.org/content/images/2022/09/9768b5e9-76f5-459b-b76a-29ca23d0bd1d.jpg-w331s)

2、握手第一步，machine1向machine2发送：

字段名 | 长度 | 存储方式 | 说明  
---|---|---|---  
Length | 2bytes | 大端 | data的长度  
Tag | 1byte |  | 操作码，握手时为'N'  
Flags | 8bytes |  | 见文档  
Creation | 4bytes | 大端 |
节点A标记自己pid、ports和references的标识符，由于是个标识符，编写代码时随机生成一个4bytes长的unsigned整数即可  
NameLength | 2bytes | 大端 | name的长度  
Name | NameLength |  | machine1节点的名称  
  
![](https://images.seebug.org/content/images/2022/09/1d0f90af-807f-4161-8c8c-4fd18f406910.png-w331s)

字段名 | 长度 | 存储方式 | 说明  
---|---|---|---  
Length | 2bytes | 大端 | data的长度  
Tag | 1byte |  | 操作码，成功时值为's'  
Status | 2bytes |  | 成功时值为ok  
  
![](https://images.seebug.org/content/images/2022/09/c783cd1d-ab0e-41cd-bf3a-9a6e2b784b97.png-w331s)

3、握手第二步，machine2向machine1发送：

字段名 | 长度 | 存储方式 | 说明  
---|---|---|---  
Length | 2bytes | 大端 | data的长度  
Tag | 1byte |  | 值为'N'  
Flags | 8bytes |  | 见文档  
challenge | 4bytes | 大端 | machine2生成的32位随机数  
Creation | 4bytes | 大端 | 标识符  
NameLength | 2bytes | 大端 | name的长度  
Name | NameLength |  | machine2节点的名称  
  
![](https://images.seebug.org/content/images/2022/09/b8eb8c79-17ef-4dd2-866a-272106017a11.png-w331s)

4、握手第三步，machine1向machine2发送

字段名 | 长度 | 存储方式 | 说明  
---|---|---|---  
Length | 2bytes | 大端 | data的长度-2  
Tag | 1byte |  | 值为'r'  
Challenge | 4bytes | 大端 | machine1生成的32位随机数  
Digest | 16bytes |  | md5(cookie+machine2_challenge)  
  
![](https://images.seebug.org/content/images/2022/09/b7ca336a-d042-48cd-b902-2c3d174a385c.png-w331s)

digest代码在`otp_src/lib/kernel/src/dist_util.erl`，注意转换成python代码的写法（见本章末代码）

machine2向machine1发送

字段名 | 长度 | 存储方式 | 说明  
---|---|---|---  
Length | 2bytes | 大端 | data的长度-2  
Tag | 1byte |  | 值为'a'  
Digest | 16bytes |  | md5(cookie+machine1_challenge)，互相通信，所以需要互相校验  
  
![](https://images.seebug.org/content/images/2022/09/c0183834-2c19-4d8f-bb50-12552953c7a9.png-w331s)

最终得到完整的代码：

    
    
    class Erldp:
        def __init__(self,host:string,port:int,cookie:bytes,cmd:string):
            self.host = host
            self.port = port
            self.cookie = cookie
            self.cmd = cmd
        def setCookie(self,cookie:bytes):
            self.cookie = cookie
    
        def _connect(self):
            self.sock = socket(AF_INET,SOCK_STREAM,0)
            self.sock.settimeout(1)
            assert(self.sock)
            self.sock.connect((self.host,self.port))
    
        def rand_id(self,n=6):
            return ''.join([choice(ascii_uppercase) for c in range(n)]) + '@nowhere'
    
        # 注意，这里的challenge是str.encode(str(int.from_bytes(challenge,"big")))
        def getDigest(self,cookie:bytes,challenge:int):
            challenge = str.encode(str(challenge))
            m = md5()
            m.update(cookie)
            m.update(challenge)
            return m.digest()
        def getRandom(self):
            r = int(random() * (2**32))
            return int.to_bytes(r,4,"big")
        def isErlDp(self):
            try:
                self._connect()
            except:
                print("[!]%s:%s tcp连接失败" % (self.host,self.port))
                return False
            try:
                self._handshake_step1()
            except:
                print("[!]%s:%s不是erldp" % (self.host,self.port))
                return False
            print("[*]%s:%s是erldp" % (self.host,self.port))
            return True
    
        def _handshake_step1(self):
    
            self.name = self.rand_id()
            packet = pack('!Hc8s4sH', 1+8+4+2+len(self.name), b'N', b"\x00\x00\x00\x01\x03\xdf\x7f\xbd",b"\x63\x15\x95\x8c", len(self.name)) + str.encode(self.name)
            self.sock.sendall(packet)
            (res_packet_len,) = unpack(">H",self.sock.recv(2))
            (tag,status) = unpack("1s2s",self.sock.recv(res_packet_len))
            assert(tag == b"s")
            assert(status == b"ok")
            print("step1 end:发送node1 name成功")
    
        def _handshake_step2(self):
            (res_packet_len,) = unpack(">H",self.sock.recv(2))
            data = self.sock.recv(res_packet_len)
            tag = data[0:1]
            flags = data[1:9]
            self.node2_challenge = int.from_bytes(data[9:13],"big")
            node2_creation = data[13:17]
            node2_name_len = int.from_bytes(data[17:19],"big")
            self.node2_name = data[19:]
            assert(tag == b"N")
            print("step2 end:接收node2 name成功")
    
        def _handshake_step3(self):
            node1_digest = self.getDigest(self.cookie,self.node2_challenge)
            self.node1_challenge = self.getRandom()
            packet2 = pack("!H1s4s16s",21,b"r",self.node1_challenge,node1_digest)
            self.sock.sendall(packet2)
            (res_packet_len,) = unpack(">H",self.sock.recv(2))
            (tag,node2_digest) = unpack("1s16s",self.sock.recv(res_packet_len))
    
            assert(tag == b"a")
    
            print("step3 end:验证md5成功，握手结束")
    
    
        def handshake(self):
            self._connect()
            self._handshake_step1()
            self._handshake_step2()
            self._handshake_step3()
            print("handshake done")

基于上述代码已经可以实现otp25口令爆破和端口扫描，已经能够满足需求。

默认口令的伪随机、中间人攻击、控制指令等原理见`github.com/gteissier/erl-matter`，如果编写用于OTP25的代码需要调整代码，例如`rpc:call('test@localcentos1','os','cmd',["touch
/tmp/tttt"])` 在otp25下使用了otp23新增的29号ctrl SPAWN_REQUEST（见pcap包和文档），而erl-matter中的`send_cmd`使用了6号指令REG_SEND，在otp25无法运行。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1978/>

