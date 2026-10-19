**[之前一篇文章](http://www.freebuf.com/sectool/164385.html)详细介绍了远控被控端，本系列的最后一篇文章我向大家介绍介绍控制端的实现。相对于被控端而言，控制端主要涉及软件界面、命令发送、消息显示这三个方面。接下来我从这三方面入手向大家介绍。**  

## 控制端架构

主界面使用一个TMPSOCKET
*类型的容器存储所有的主机标识。该结构使用socket和硬盘系列号来唯一标识远程主机。每次有远程主机连接到控制端，控制端通过检查硬盘序列号是否已存在来处理重复客户端的问题。

    
    
    typedef struct tagTmpSocket 
    {  
        SOCKET ClientSocket;     //连接socket  
        char HDSerial[64];       //对应主机硬盘序列号  
    }TMPSOCKET,*LPTMPSOCKET;  
    

初始化界面如下：

![界面.png](https://image.3001.net/images/20180307/15204342985677.png!small)

当设置好ip地址和监听端口，单击“开始”按钮，MyServerThread线程启动，参数为ip地址和端口。其作用是初始化socket相关库，并且进入循环等待远程主机的连接。

    
    
    DWORD WINAPI MyServerThread()  
    {  
        CTcpTran m_tcptran ;              //初始化相关库  
        m_tcptran.InitSocketLibray(2,2);  
        SOCKET ServerSocket = m_tcptran.InitSocket(SOCKETBIND,str_ip,u_port,0);  
        if (ServerSocket == SOCKET_ERROR)  
        {          
            closesocket(ServerSocket);  
            AfxMessageBox("SOCKET_ERROR");  
            return -1;  
        }  
      
      
        ....  
      
      
        while(1)                //循环等待监听  
        {  
            ClientSocket = m_tcptran.myaccept(ServerSocket,(struct sockaddr*)&Client_addr,&addrlen) ;  
    	if(ClientSocket == SOCKET_ERROR)             //返回新创建的套接字  
    	    break;  
    	strcpy( client_ip, inet_ntoa(Client_addr.sin_addr) );    //新创建的套接字的地址结构  
    	clientLinkinfo.s = ClientSocket ;                        //全局变量clientLinkinfo  
    	clientLinkinfo.BindPort  = m_linkinfo.BindPort ;		  
    	hThread = CreateThread(0,0,ServerThread,(LPVOID)&clientLinkinfo,0,&Threadid);	//创建ServerThread线程    
        }  
    	return 0;  
    }  
    

一旦接受了远程主机的连接，则为该远程主机创建一个ServerThread线程。该线程解决了重复客户端问题。每当有远程主机链接过来，总会将该主机发送过来的计算机信息中的硬盘序列号与容器中存储的已连接的计算机硬盘序列号对比，如果存在相同的，则将已存在的从容器中删除，将新的添加进去，这样做是为了应对有主机中途掉线后重连的情况。

    
    
    DWORD WINAPI ServerThread(LPVOID lp)  
    {  
        LPLINKINFO  plast_linkinfo =(LPLINKINFO)lp ;   
        CTcpTran m_tcptran ;  
        m_tcptran.m_Socket  =  plast_linkinfo->s ;  
        SYSTEMINIT m_sendmsg ;  
        char ReceiveBuf[sizeof(m_sendmsg)] = {0};  
        int  DataLen = 0;  
        DataLen = m_tcptran.myrecv(m_tcptran.m_Socket,(char *)&m_sendmsg,sizeof(m_sendmsg),0,60,0,false) ;   //接收被控端发来的计算机信息  
        if (DataLen == 0)   
        {  
            closesocket(m_tcptran.m_Socket);  
            ExitThread(0);  
        }  
    	BOOL  BDeleteid =FALSE;  
    	UINT  InseartItem =0;	  
    	for(int j = 0; j<tmp_vector.size();j++)  
    	{  
    	    if (stricmp(m_sendmsg.HDSerial,tmp_vector[j]->HDSerial)==0)     //如果已经存在该硬盘序列号  
    	    {  
    	        for(int i=0; i<m_clientdlg->m_list.GetItemCount(); i++)  
    	        {  
    	            if(stricmp(m_sendmsg.HDSerial,tmp_vector[j]->HDSerial)==0 )    //从客户端列表中查询  
    	            {  
    	                BDeleteid = TRUE;  
    	                InseartItem = i;  
                        }  
    		}  
    		tmp_vector.erase(tmp_vector.begin()+j);			      //从容器中移除			  
    	    }  
    	}  
      
        CString tmp = _T("");  
        CString m_phyaddr = _T("");	  
        int mm = m_clientdlg->m_list.GetItemCount();
        if (BDeleteid)  
        {  
            mm = InseartItem;  
            m_clientdlg->m_list.DeleteItem(InseartItem);    //从列表中移除  
        }  
        tmp.Format("%s",client_ip);                         //显示IP	  
        m_clientdlg->m_list.InsertItem(mm,"");              //列表控件，首先插入一个空的行  
        m_clientdlg->m_list.SetItemText(mm,0,tmp);  
      
      
       ....      //在列表中显示远程主机信息  
      
        TMPSOCKET *tmp00 = new TMPSOCKET;        //创建远程主机标识  
        memset(tmp00,0,sizeof(TMPSOCKET));	  
        tmp00->ClientSocket = m_tcptran.m_Socket;	   //写入对应的socket  
        lstrcpy(tmp00->HDSerial,m_sendmsg.HDSerial);   //写入硬盘序列号  
        tmp_vector.push_back(tmp00);		                //将当前主机标识压入容器  
        return true;  
    }  
    

![微信图片_20180307234851.png](https://image.3001.net/images/20180307/15204377489996.png!small)

## 进程管理界面

界面初始化完毕，调用OnStart函数向远程主机发送CMD_PROCESS_MANAGE命令，接收远程主机发送的进程消息，将每一条指向PROCESSINFO类型的指针存入容器中。

    
    
    typedef struct tagProcessInfo  
    {  
        DWORD PID;           
        char  ProcName[64];  
        char  ProcPath[128];  
    }PROCESSINFO,*LPPROCESSINFO;  
    

然后调用InitList函数将指针容器指向的消息显示到列表上。  

    
    
    void OnStart()  
    {  
        COMMAND m_command;  
        int len = 0;
        memset((char  *)&m_command, 0,sizeof(m_command));  
        m_command.wCmd = CMD_PROCESS_MANAGE;  
        m_command.DataSize = 0;  
        CTcpTran m_tcptran ;   
        int buf = 0;   
        len = m_tcptran.mysend(m_procmanagedlg->ClientSocket,(char *)&m_command,sizeof(m_command),0,60);  
        if (len<0)
        {  
            len = m_tcptran.mysend(m_procmanagedlg->ClientSocket,(char *)&m_command,sizeof(m_command),0,60);  
        }  
        int processlen = m_tcptran.myrecv(m_procmanagedlg->ClientSocket,(char *)&buf,sizeof(int),0,60,NULL,false);  
        if (processlen>0)  
        {  
            std::vector<PROCESSINFO *> pProcInfo;  
            PROCESSINFO *tmp = new PROCESSINFO;   
            for(int i=0;i<buf;i++)  
    	{  
    	    tmp = new PROCESSINFO;  
    	    memset(tmp, 0,sizeof(PROCESSINFO));  
    	    m_tcptran.myrecv(m_procmanagedlg->ClientSocket,(char *)tmp,sizeof(PROCESSINFO),0,60,0,false);			  
    	    pProcInfo.push_back(tmp);  
    	}  
    	InitList(pProcInfo);  
        }  
    }  
    

![进程管理.jpg](https://image.3001.net/images/20180308/15204386863874.jpg!small)

同样的服务管理端界面也是这个设计思路。

## 文件管理界面

初始化界面阶段调用DriverInfoThread在左侧树状列表中显示所有盘符，当点击其中一个节点时，调用OnClickTree1展开该节点，然后调用ListDirThread在右侧远程主机文件列表中显示当前文件夹下所有文件。

![文件管理.jpg](https://image.3001.net/images/20180308/15204413126270.jpg!small)

右侧列表中添加右键单击事件，弹出文件删除选项，调用消息处理函数OnFileDel对文件进行删除。  

## 远程SHELL界面

点击“执行”按钮时，获取输入的命令行内容，调用CmdShellThread启动远程命令行线程，将命令发送至远程主机，执行完后返回执行结果。这里需要注意的时，接收目标数据时，需要将myrecv函数最后一个参数设置为true，表示接收到数据立即返回显示，如果设置为false，由于数据长度通常较长，会有明显的显示延迟，所以设置为一旦接收到数据立即返回。

    
    
    UINT CmdShellThread(LPVOID lparam)  
    {  
        CTcpTran m_tcptran;  
        COMMAND m_control;  
        memset(&m_control,0,sizeof(COMMAND));  
        m_control.wCmd = CMD_CMDSHELL;  
        CShellDlg *pDlg=(CShellDlg *)lparam;  
        if(pDlg->m_command=="")  
        {  
            ExitThread(0);//无命令,退出线程  
        }  
        if(pDlg->ClientSocket!=INVALID_SOCKET)  
        {
            int ret;
            char RecvBuf[1024]={0};    //接收缓冲
            char command[120];  
            strcpy(command,pDlg->m_command);    
            strcpy(m_control.szCurDir,command);  
            ret=m_tcptran.mysend(pDlg->ClientSocket,(char *)&m_control,sizeof(m_control),0,60);//开启CMDSHELL	  
            while(ret>0)  
            {  
                ret=m_tcptran.myrecv(pDlg->ClientSocket,RecvBuf,sizeof (RecvBuf),0,10,0,true); //接收目标数据  
                if(ret<=0||RecvBuf[0]==MY_END)  
                   break;  
                //表示接收到数据  
                CString current;  
                pDlg->m_CmdEdit.GetWindowText(current);  
                pDlg->m_CmdEdit.SetWindowText(current+RecvBuf);  
                memset(RecvBuf,0,sizeof(RecvBuf));  //缓冲清零  
                pDlg->m_CmdEdit.LineScroll(pDlg->m_CmdEdit.GetLineCount());  
            }  
        }  
        pCmdShellThread = NULL;  
        return 0;	  
    }  
    

![远程shell.jpg](https://image.3001.net/images/20180308/15204398204121.jpg!small)  

## 远程桌面

远程桌面窗口启动后获得远程主机的DIB（设备无关位图文件，这是一种文件格式，是为了保证由某个应用程序创建的位图图形可以被其它应用程序装载或显示）图像，而后进入Set_BackGround_Image函数进行显示。进入Set_BackGround_Image函数首先设置位图文件的头格式，然后调用StretchDIBits函数进行显示。  

    
    
    DWORD WINAPI Set_BackGroud_Image()  
    {  
        if (m_remotedesktopdlg->m_lpImageData==NULL) return 1;  
        HWND   hWnd=m_remotedesktopdlg->GetSafeHwnd();  
        CRect rc;  
        HWND Handle = GetDlgItem(hWnd,IDC_STATIC_PICTURE);//获取窗口主句柄 
        CWnd *hwnd = CWnd::FromHandle(Handle);    
        hwnd->GetWindowRect(&rc);//获取picture control的指针，得到区间范围rect    
        CDC *theDC = m_remotedesktopdlg->m_picStatArea.GetWindowDC ();   
        if(theDC!= NULL)  
        {  
            int left = m_remotedesktopdlg->m_nLeft; //-m_hScrollBar.GetScrollPos();  
            int top =  m_remotedesktopdlg->m_nTop;  //-m_vScrollBar.GetScrollPos();  
            BYTE *tmp = m_remotedesktopdlg->m_lpImageData;  
    	// set up a DIB   
            BITMAPINFOHEADER bmiHeader;  
            bmiHeader.biSize = sizeof(BITMAPINFOHEADER);  
            bmiHeader.biWidth = m_remotedesktopdlg->m_nBmpWidth; //1024/2;//  
            bmiHeader.biHeight =m_remotedesktopdlg->m_nBmpHeight; // 768/2;  
            bmiHeader.biPlanes = 1;  
            bmiHeader.biBitCount = 24; //24  
            bmiHeader.biCompression = BI_RGB;  
            bmiHeader.biSizeImage = 0;  
            bmiHeader.biXPelsPerMeter = 0;  
            bmiHeader.biYPelsPerMeter = 0;  
            bmiHeader.biClrUsed = 0;  
            bmiHeader.biClrImportant = 0;  
            int lines = StretchDIBits(theDC->m_hDC,  
    			rc.left,  
    			rc.top,  
    			rc.Width(),//bmiHeader.biWidth,//1024/2,//rc.Width(),//bmiHeader.biWidth/2,  
    			rc.Height(),//bmiHeader.biHeight,//768/2,//rc.Height(),///bmiHeader.biHeight/2,  
    			0,0,  
    			bmiHeader.biWidth,  
    			bmiHeader.biHeight,  
    			tmp,  
    			(LPBITMAPINFO)&bmiHeader,  
    			DIB_RGB_COLORS,  
    			SRCCOPY);  
      
    ReleaseDC(hWnd,*theDC);  
        }  
      
    	return 0;  
    }  
    

![桌面监控.jpg](https://image.3001.net/images/20180308/15204408017408.jpg!small)  

[**代码传送门**]()

 ***本文原创作者：Mr极目楚天舒，转载请注明来自FreeBuf.COM**

