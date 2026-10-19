*****本文原创作者：Mr极目楚天舒，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

**本人为了工作中便于管理手中大量的计算机一直在寻找一款合适的远程控制软件。鉴于网上下载的远程控制软件大多都被不同程度地植入后门，于是萌生了自己打造一款远控的想法，正好借着这个机会重新拾起快要被遗忘了的C++，也借此将源代码与大众网友分享。采用成熟的MFC框架技术来搭建远控客户端和服务端，实现了进程管理、文件管理、服务管理、远程SHELL和屏幕监视功能，层次结构清晰，为日后软件版本的迭代留下了扩展空间。**

## 编程环境

Visual Studio 2010

## 连接方式

采用反弹型连接方式，被控端主动连接控制端从而能够轻松穿透大多数防火墙。

## 工作流程

![工作流程.jpg](https://image.3001.net/images/20180303/15200918318354.jpg!small)  

## 基本传输结构

### 1、被控端上报基本计算机信息结构

被控端连接控制端，并将计算机信息上报控制端显示。

    
    
    typedef struct tagSytemInit
    {
        char computer[32];      //计算机名
        char user[32];          //用户名
        char os[72];            //操作系统
        char processor[16];     //处理器信息
        char mem[16];           //内存信息
        char version[16];       //软件版本
        char HDSerial[32];      //硬盘序列号
    
    }SYSTEMINIT,*LPSYSTEMINIT;
    

### 2、临时连接结构

该结构用来存储连接到控制端上的socket信息以及相应的硬盘序列号。在后面的使用中将此结构存储到vector中用于管理被控端。

    
    
    typedef struct tagTmpSocket
    {    
       SOCKET ClientSocket;    
       char HDSerial[64];
    
    }TMPSOCKET,*LPTMPSOCKET;
    

### 3、进程通信结构

控制端控制被控端，实现进程之间的通信。

    
    
    typedef struct tagLinkInfo 
    {    
        SOCKET  s;               
        string  strBindIp;      //被控端IP
        u_short BindPort;       //监听端口
    
    }LINKINFO,*LPLINKINFO;
    

## 基本通信类

CTcpTran是整个远控的基础通信类，用于实现socket网络通信的初始化，封装相应的API函数。使用类来封装Socket
API可以避免代码的重复，便于调试。

CTcpTran类中的4个基本成员函数如下：

    
    
    SOCKET InitSocket(int SocketType, string strBindIp,u_short BindPort,int opt);                           //初始化socket，选择连接类型
    SOCKET myaccept(SOCKET s,struct sockaddr* addr,int* addrlen);                                           //本地监听处理函数
    int mysend(SOCKET sock, const char *buf, int len, int flag,int overtime);                               //发送数据
    int myrecv(SOCKET sock, char *buf, int len, int flag , int overtime,char*EndMark,BOOL soonflag=FALSE);  //接收数据
    

### InitSocket函数  

InitSocket参数解释如下，SocketType为连接类型，当值为
SOCKET_BIND时表示绑定本地端口，服务器监听端口等待客户端来连接，当值为SOCKET_NOBIND时表示不绑定，服务端主动连接客户端。strBindIp为要绑定的IP地址，""（空）为本地任意地址，这样做的目的是当服务器有多块网卡时，不论哪个网段上的客户程序都能与服务器通信。uBindPort为要绑定的端口。

    
    
    SOCKET	CTcpTran::InitSocket( int SocketType, string strBindIp,u_short BindPort,int opt)  
    {  
    	SOCKET socketid = INVALID_SOCKET;  
    	socketid = socket(PF_INET,SOCK_STREAM,0);               //建立一个流式套接字句柄  
    	SOCKADDR_IN sockStruct;                                 //初始化一个地址结构  
    	sockStruct.sin_family = AF_INET;                        //使用TCP/IP协议  
      
    	if( strBindIp.empty() )  
    	{  
    		sockStruct.sin_addr.S_un.S_addr = INADDR_ANY;   //如果strBindIp为空，则为本地任意地址       
      
    	}else  
    	{  
    		sockStruct.sin_addr.S_un.S_addr = inet_addr(strBindIp.c_str());	        
    	}  
      
      
        sockStruct.sin_port = htons(BindPort);                      //转换为网络字节  
      
    	if( SocketType == SOCKETNOBIND )  
    	{  
    		if(connect(socketid,(LPSOCKADDR)&sockStruct,sizeof(sockStruct)) == SOCKET_ERROR)      //不绑定，直接连接，被控端选择非绑定方式连接  
    		{  
    //			AfxMessageBox("InitSocket 错误");  
    			closesocket(socketid);  
    			shutdown(socketid,2);  
    			socketid = INVALID_SOCKET;  
    		}  
      
    		m_Socket = socketid;  
      
    	}else if( SocketType == SOCKETBIND )                                                        //控制端选择绑定本地端口  
    	{  
    		if(bind(socketid,(sockaddr*)&sockStruct,sizeof(sockaddr_in)) == SOCKET_ERROR)       //绑定地址结构  
    		{  
    			closesocket(socketid);  
    			socketid = INVALID_SOCKET;  
      
    		}else  
    		{  
    			if( listen(socketid,SOMAXCONN) == SOCKET_ERROR )             //进入监听  
    			{  
    				closesocket(socketid);  
    				socketid = INVALID_SOCKET;  
    			}  
    		}  
      
    		m_Socket = socketid;  
    	}  
      
    	return socketid;                                     //返回建立的socket  
    }	

### myaccept函数

服务器接收客户端的连接请求，创建一个新的套接字和参数addr指定的客户端套接字建立连接通道。s表示处于监听状态的流套接字。addr表示新创建的套接字地址结构。addrlen表示新创建套接字的地址结构的长度。

    
    
    SOCKET	CTcpTran::myaccept(SOCKET s,struct sockaddr* addr,int* addrlen)  
    {  
    	SOCKET accpsocket  = INVALID_SOCKET;  
    	accpsocket = accept(s,addr,addrlen);  
    	return accpsocket;  
    }  
    

### mysend函数

mysend函数用来发送指定的套接字数据。sock为指定的Socket。buf为用来存放要发送的数据的缓冲区。len为待发送数据的长度。flag一般设置为0。overtime为超时时间。这里采用了select机制防止I/O操作阻塞，提高了程序运行效率。这里要注意每次执行select操作之前都要更新文件描述符，因为select操作会更改文件描述符。

    
    
    int CTcpTran::mysend(SOCKET sock, const char *buf, int len, int flag,int overtime)  
    {  
    	int		ret;  
    	int		nLeft = len;                     //待发送的字节数  
    	int		idx	 = 0;                    //发送缓冲区索引  
      
    	fd_set readfds;                               
    	struct timeval  timeout;       
    	timeout.tv_sec = 0;  
    	timeout.tv_usec = 500;   
    	DWORD s_time = GetTickCount();                    //获取系统时间（从操作系统运行开始到当前的时间），第一次计时  
    	while ( nLeft > 0 )  
    	{  
    		MSG msg;  
    		PeekMessage(&msg, NULL,  0, 0, PM_REMOVE) ;  
    		if(msg.message == WM_QUIT)  
    		{  
    			return 0;  
    		}  
      
    		FD_ZERO( &readfds );                                               //每次循环更新文件描述符  
    		FD_SET( sock , &readfds );  
      
    		int errorret   = select( 0 , NULL, &readfds, NULL , &timeout );    //时间阻塞式监控，检测套接字是否可写  
      
    		if( errorret == SOCKET_ERROR )  
    		{  
    //			AfxMessageBox("mysendEx SOCKET 错误");  
    			return SOCKET_ERROR;  
    		}  
      
    		DWORD e_time = GetTickCount( );                      //第二次计时  
    		if  ( !FD_ISSET( sock , &readfds ) )                 //检测是否可以发送，如果为否表示正在占用  
    		{  
      
    			if( e_time - s_time > overtime*1000 )        //检测时间窗口是否超时  
    			{  
    //				AfxMessageBox("mysendEx发送数据超时");  
    				return 0;  
    			}  
    			else  
    			{  
    				continue;  
    			}  
    		}  
      
    		ret = send( sock, &buf[idx], nLeft, flag );          //返回实际发送的字节数  
      
    		if ( ret <= 0 )  
    		{  
    			return ret;  
    		}  
      
    		nLeft	-= ret;                                     //剩余字节数-  
    		idx		+= ret;                             //索引值+  
      
    	}  
    	return len;                                                 //返回发送字节数  
    }

### myrecv函数

myrecv函数用来接收指定的套接字数据。sock为接收端套接字描述符。buf
用来存放接收到的数据的缓冲区。len为接收数据的缓冲区的大小。flag一般设置为0。overtime为超时时间。endmark为结束标记。soonflag为是否立即返回结果，默认为否。与mysend函数一样采用select机制防止I/O操作阻塞。

    
    
    int CTcpTran::myrecv(SOCKET sock, char *buf, int len, int flag , int overtime ,char*EndMark,BOOL soonflag)  
    {  
    	int		ret;  
    	int		nLeft = len;  
    	int		idx	 = 0;  
    	int		nCount = 0;  
    	fd_set readfds;  
    	struct timeval  timeout;  
    	timeout.tv_sec = 0;  
    	timeout.tv_usec = 500;  
    	DWORD s_time = GetTickCount();  
      
    	while ( nLeft > 0 )  
    	{  
    		//接收消息  
    		MSG msg;  
    		PeekMessage(&msg, NULL,  0, 0, PM_REMOVE) ;  
    		if(msg.message == WM_QUIT)  
    			return 0;  
      
    		FD_ZERO( &readfds );  
    		FD_SET( sock , &readfds );  
    		if( select( 0 , &readfds , NULL , NULL , &timeout ) == SOCKET_ERROR )  
    		{  
    //			AfxMessageBox("recv SOCKET 错误");  
    			return SOCKET_ERROR;  
    		}  
      
    		DWORD e_time = GetTickCount( );  
    		if  ( !FD_ISSET( sock , &readfds ) )  
    		{  
    			if( e_time - s_time > overtime*1000 )   
    			{  
    //				AfxMessageBox("recv SOCKET 超时");  
    				return SOCKET_TIMEOUT;  
    			}  
    			else  
    				continue;  
    		}  
      
    		ret = recv( sock, &buf[idx], nLeft, flag );  
    		if( soonflag == TRUE )  
    		{  
    			return ret;  
    		}  
      
    		s_time = e_time ; // 只要有数据就重新置初始时间值  
      
    		if ( ret <= 0 )  
    		{  
    			int LastError = GetLastError();  
    			if ( ( -1 == ret ) && ( WSAETIMEDOUT == LastError ) )  
    				continue;  
    			if ( ( -1 == ret ) && ( WSAEWOULDBLOCK == LastError ) )  
    			{  
    				if ( nCount < 2000 )  
    				{  
    					Sleep( 10 );  
    					nCount++;  
    					continue;  
    				}  
    			}  
    			return ret;  
    		}  
    		nCount	=	0;  
      
    		nLeft	-= ret;  
    		idx		+= ret;  
      
    		if( EndMark != NULL && idx>5)  
    		{  
    			if( strstr(buf+(idx-5),EndMark) != NULL )  
    			{  
    				break;  
    			}  
    		}  
    	}  
      
    	return idx;  
    }  
    

## 主界面

![界面.png](https://image.3001.net/images/20180304/15200930783896.png!small)  

## 功能界面

### 进程管理

![进程管理.jpg](https://image.3001.net/images/20180303/15200927503096.jpg!small)  

### 文件管理

![文件管理.jpg](https://image.3001.net/images/20180304/15200929765765.jpg!small)  

### 服务管理

![服务管理.jpg](https://image.3001.net/images/20180304/15200928411650.jpg!small)  

### 远程SHELL

![远程shell.jpg](https://image.3001.net/images/20180304/15200928711135.jpg!small)  

  

### 远程桌面

![桌面监控.jpg](https://image.3001.net/images/20180304/15200929024681.jpg!small)  

***本文原创作者：Mr极目楚天舒，本文属FreeBuf原创奖励计划，未经许可禁止转载**

