*****本文原创作者：Mr极目楚天舒，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

**前一篇文章介绍了[软件的整体架构](http://www.freebuf.com/sectool/164028.html)，接下来对被控端进行详细讲解，主要介绍被控端各个功能模块的关键技术以及开发过程中遇到的坑，希望对各位读者有借鉴作用。**

## 被控端工作流程

应用程序初始化阶段初始化工作界面、从地址文件读取反向连接的ip地址和端口作为MyClientThread线程的启动参数。MyClientThread启动后执行GetClientSystemInfo函数获取本机信息并传至控制端显示。而后进入while(1)循环等待接收控制端传来的控制命令。进入switch_case结构解析命令，执行相应函数。将执行结果发送到控制端，继续进入循环等待。  

![被控端工作流程
\(2\).jpg](https://image.3001.net/images/20180304/15201760656770.jpg!small)  

## 获取计算机信息

GetClientSystemInfo传入一个SYSTEMINIT结构的引用，对该结构的定义在common.h文件中，该结构定义如下：

    
    
    typedef struct tagSytemInit         
    {
    	char computer[32];       //计算机名
    	char user[32];           //当前用户名
    	char os[72];             //操作系统信息
    	char processor[16];      //处理器信息
    	char mem[16];            //内存
    	char version[16];        //软件版本  
    	char HDSerial[32];       //硬盘序列号
    }SYSTEMINIT;  

调用GetComputerName、GetUserName、GetVersionEx、GlobalMemoryStatus来分别获取计算机名、当前用户名、操作系统版本、内存信息。CPU的信息通过查询注册表来获取，通过打开不同的注释（3个中只能打开一个）获取CPU的不同信息，这里我们选择获取CPU的频率信息。  

    
    
    #include "stdafx.h"  
    #include "windows.h"  
    #include "GetHDSerial.h"  
      
    #define BUFSIZE 16  
      
    bool GetClientSystemInfo(SYSTEMINIT& sysinfo)  
    {  
    	TCHAR computerbuf[256];                       //获取计算机名  
    	DWORD computersize=256;  
    	memset(computerbuf,0,256);  
    	if(!GetComputerName(computerbuf,&computersize))  
    	    return false;  
    	computerbuf[computersize]=0;  
    	sysinfo.computer[0]=0;  
    	strcat(sysinfo.computer,"计算机: ");  
    	strcat(sysinfo.computer,computerbuf);  
      
    	TCHAR userbuf[256];                          //获取用户名  
    	DWORD usersize=256;  
    	memset(userbuf,0,256);  
    	if(!GetUserName(userbuf,&usersize))  
    		return false;  
    	userbuf[usersize]=0;  
    	sysinfo.user[0]=0;  
    	strcat(sysinfo.user,"用户名: ");  
    	strcat(sysinfo.user,userbuf);  
      
    	OSVERSIONINFOEX osvi;                       //获取操作系统  
    	BOOL bOsVersionInfoEx;   
    	OSVERSIONINFOEX   osviex;  
        sysinfo.os[0]=0;  
    	memset(&osviex,0,sizeof(OSVERSIONINFOEX));  
    	osviex.dwOSVersionInfoSize = sizeof(OSVERSIONINFOEX);  
      
    	if(GetVersionEx((LPOSVERSIONINFO)&osviex)==0)  
    	{  
    		OutputDebugString("GetVersionEx Error");  
    		return FALSE;  
    	}  
      
    	switch(osviex.dwPlatformId)  
    	{  
    	case VER_PLATFORM_WIN32_NT:  
    		switch(osviex.dwMajorVersion)  
    		{  
    		case 4:  
    			if(osviex.dwMinorVersion == 0)  
                   strcat(sysinfo.os,"Microsoft Windows NT 4");  
    			break;  
    		case 5:  
    			if(osviex.dwMinorVersion == 0)  
    			{  
                    strcat(sysinfo.os,"Microsoft Windows 2000 ");  
    			}  
    			else if(osviex.dwMinorVersion == 1)  
    			{  
    				strcat(sysinfo.os,"Windows XP ");  
    			}  
    			else if(osviex.dwMinorVersion == 2)  
    			{  
                   strcat(sysinfo.os,"Windows 2003 ");  
    			}  
      
    		}  
    		break;  
    	}  
      
      
      
    	char *temp;                                   //获取硬盘序列号  
    	sysinfo.HDSerial[0]=0;  
            CGetHDSerial HDSerial;                        // 创建实例     
            temp=HDSerial.GetHDSerial();                  // 得到硬盘序列号      
            strcat(sysinfo.HDSerial,temp);  
      
    	sysinfo.processor[0]=0;                       //获取CPU信息  
    	HKEY hKey;  
    	char szcpuinfo[80];  
    	DWORD dwBufLen=80;  
    	RegOpenKeyEx( HKEY_LOCAL_MACHINE, "HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0", 0,          KEY_QUERY_VALUE, &hKey );  
    	RegQueryValueEx( hKey, "VendorIdentifier", NULL, NULL,  //这里获取cpu的生产厂商标识  
    	   (LPBYTE)szcpuinfo, &dwBufLen);  
    	szcpuinfo[dwBufLen]=0;
            //strcat(sysinfo.processor,szcpuinfo);                  //打开这句注释，控制端显示cpu生产厂商  
    	memset(szcpuinfo,0,80);  
    	dwBufLen=80;  
    	RegQueryValueEx( hKey, "Identifier", NULL, NULL,        //获取CPU型号  
    	   (LPBYTE)szcpuinfo, &dwBufLen);  
    	szcpuinfo[dwBufLen]=0;  
    	//strcat(sysinfo.processor,szcpuinfo);                  //可以打开这句注释，控制端显示cpu型号         
    	DWORD f;  
    	dwBufLen=8;  
    	RegQueryValueEx( hKey, "~MHz", NULL, NULL,  
    	   (LPBYTE)&f, &dwBufLen);  
    	char hz[10];  
    	sprintf(hz," %dMHZ",f);                                 //显示cpu工作频率  
    	strcat(sysinfo.processor,hz);  
    	RegCloseKey(hKey);  
      
      
    	MEMORYSTATUS ms;                                        //获取内存容量  
    	GlobalMemoryStatus(&ms);  
    	char membuf[256];//物理内存:   
            sprintf(membuf,"%dMB",ms.dwTotalPhys/1024/1024);  
    	sysinfo.mem[0]=0;  
    	strcpy(sysinfo.mem,membuf);  
    	return true;  
    }  
    

## 获取硬盘序列号

这里专门定义了一个CGetHDSerial类来封装序列号读取相关的操作。CGetHDSerial的成员函数如下：

    
    
    Win9xReadHDSerial             // Windows9X/ME系统下读取硬盘序列号  
    GetHDSerial                   // 读取硬盘序列号函数  
    WORDToChar                    // Windows 9x/ME系统下，将字类型（WORD）的硬盘信息转换为字符类型  
    DWORDToChar                   // Windows NT/2000/XP系统下，将双字类型（DWORD）的硬盘信息转换为字符类型  
    WinNTReadSCSIHDSerial         // WindowsNT/2000/XP系统下读取SCSI硬盘序列号  
    WinNTReadIDEHDSerial          // Windows NT/2000/XP下读取IDE硬盘序列号  
    WinNTGetIDEHDInfo             // Windows NT/2000/XP下读取IDE设备信息

函数调用关系为：  

![CGetHDSerial.JPG](https://image.3001.net/images/20180306/15203486959274.jpg!small)  

## 获取服务

参数为存放SERVICEINFO指针类型的容器。SERVICE数据结构定义为：

    
    
    typedef struct tagServiceInfo
    {  
        char  ServiceName[32];                  //服务名称  
        char  ServiceDetail[128];               //描述信息  
        char  ServiceState[16];                 //服务状态  
        char  ServiceStartType[16];             //启动类型  
    }SERVICEINFO,*LPSERVICEINFO;  
    

这里用到OpenSCManager函数，该函数建立了一个到服务控制管理器的连接，并打开指定的数据库。第一个参数为计算机名，若为NULL则指向本地计算机。第二个参数指定将要打开的服务控制管理数据库的名称，这里为NULL，表示指向本地默认。第三个参数为服务访问控制管理器的权限。执行成功返回一个服务控制管理器数据库的句柄ScManager。

由返回的句柄调用EnumServicesStatus函数枚举当前系统服务  

    
    
    BOOL ListService(std::vector<SERVICEINFO *> *service_vector)  
    {  
    	SERVICEINFO *service_tmp = new SERVICEINFO ;  
    	memset(service_tmp,0,sizeof(SERVICEINFO));  
       	SC_HANDLE ScManager;  
    	ENUM_SERVICE_STATUS EnService[512];  
    	DWORD   cbBufSize=512*sizeof(ENUM_SERVICE_STATUS);  
    	DWORD lpServicesReturned;  
    	DWORD   pcbBytesNeeded;           // buffer size needed  
    	DWORD   lpResumeHandle=0;           // next entry  
    	CString str,csTemp;  
    	service_vector->clear();  
      
    	ScManager=::OpenSCManager(NULL,NULL,SC_MANAGER_ENUMERATE_SERVICE|GENERIC_READ); //建立了一个到服务控制管理器的连接，得到服务控制管理器数据库的句柄  
      
    	if(ScManager==NULL)  
    	{  
    		AfxMessageBox("Error Opening Service Mgr");  
    		return FALSE;  
    	}  
      
    	if(::EnumServicesStatus(ScManager,SERVICE_WIN32,SERVICE_STATE_ALL,EnService,cbBufSize,&pcbBytesNeeded,&lpServicesReturned,&lpResumeHandle )==0)              //枚举当前系统服务  
    	{  
    		AfxMessageBox("Error Querrying Service Mgr");  
    		return FALSE;  
    	}  
      
    	for(int i=0;i<int(lpServicesReturned);i++)  
    	{  
      
    		SERVICEINFO *service_tmp = new SERVICEINFO ;  
                    memset(service_tmp,0,sizeof(SERVICEINFO));  
    		strcpy(service_tmp->ServiceName,EnService[i].lpServiceName);  
    		strcpy(service_tmp->ServiceDetail,EnService[i].lpDisplayName);  
    		switch(EnService[i].ServiceStatus.dwCurrentState)  
    		{  
    		   case SERVICE_PAUSED:  
    			strcpy(service_tmp->ServiceState,"暂停");		  
    			break;  
      
    		   case SERVICE_RUNNING:  
    			strcpy(service_tmp->ServiceState,"已启动");            
    			break;  
      
    		   case SERVICE_STOPPED :     
    			strcpy(service_tmp->ServiceState,"停止");    
    			break;  
      
    		   case SERVICE_START_PENDING :  
    			strcpy(service_tmp->ServiceState,"正在启动");    
    		        break;  
      
    		   case SERVICE_STOP_PENDING :  
    			strcpy(service_tmp->ServiceState,"正在停止");                                                                        
    			break;  
      
    		   default:  
    			strcpy(service_tmp->ServiceState,"未知");   
    			break;  
    		}  
      
    		{  
    			SC_HANDLE ScService;					  
    			QUERY_SERVICE_CONFIG ServiceConfig;  
    			DWORD CbBufSize, pcbBytesNeeded;  
    			CbBufSize=sizeof(QUERY_SERVICE_CONFIG);		                if((ScService=::OpenService(ScManager,EnService[i].lpServiceName,SERVICE_ALL_ACCESS))==NULL)  
    			{  
    				::CloseHandle(ScManager);		  
    				"Problem in opening service";	  
    			}  
      
    			::QueryServiceConfig(ScService,&ServiceConfig,CbBufSize,&pcbBytesNeeded);  
      
    			switch(ServiceConfig.dwStartType)          //查询服务状态  
    			{  
    				case SERVICE_AUTO_START:	
                                    strcpy(service_tmp->ServiceStartType,"自动");	
                                    break;  
                               
    				case SERVICE_DEMAND_START:
                                    strcpy(service_tmp->ServiceStartType,"手动");	
                                    break;
      
    				case SERVICE_DISABLED :
                                    strcpy(service_tmp->ServiceStartType,"禁用");	
                                    break;
      
    				default:  
                                    strcpy(service_tmp->ServiceStartType,"未知");  
      
    			}		  
      
    		}  
    		service_vector->push_back(service_tmp);    //压入容器  
    	}  
    	return true;  
    }  
    

## 获取进程列表

GetProcessList参数为PROCESSINFO指针类型的容器。PROCESSINFO数据结构在common.h中定义。

    
    
    typedef struct tagProcessInfo  
    {  
        DWORD PID;                      //进程PID  
        char  ProcName[64];             //进程名称  
        char  ProcPath[128];            //进程所在路径  
    }PROCESSINFO,*LPPROCESSINFO;

首先调用CreateToolhelpSnapshot获得当前系统中所有进程的快照，返回快照句柄。第二步调用Process32First获得第一个进程快照信息info，得到进程PID和进程名称。为了得到当前进程加载模块的完整路径，需要调用OpenProcess来打开对应进程对象。然而通过几次打开失败后发现，原来在
**默认的情况下进程的一些访问权限是没有被启用的，即使你是Administrator**
，所以很重要的一步就是提升当前进程的权限（启用这些权限），所以先调用OpenProcessToken打开相关进程的访问令牌（参数自己百度），而后调用EnablePrivilege提升当前进程权限，这样就可以打开进程对象了。第三步，通过while循环获得其他进程的信息。  

    
    
    BOOL GetProcessList(std::vector<PROCESSINFO*> *pProcInfo)  
    {  
        DWORD processid[1024],needed;  
        HANDLE hProcess;  
        HMODULE hModule;  
        char path[MAX_PATH] = "";  
        char temp[256] = "";  
        CString path_convert=path;  
        pProcInfo->clear();  
        HANDLE handle = CreateToolhelp32Snapshot( TH32CS_SNAPPROCESS, 0 );   //获取系统中正在运行的进程信息，给                                                //                                                                         系统内的所有进程拍一个快照，返回进程快照句柄    
        PROCESSENTRY32 *info = new PROCESSENTRY32;  
        info->dwSize=sizeof(PROCESSENTRY32);               //在使用这个结构之前先指定结构大小  
        int i = 0;  
        PROCESSINFO *Proc = new PROCESSINFO;  
        if(Process32First(handle,info))                    //获得第一个进程的句柄  
        {  
            Proc = new PROCESSINFO;  
    	memset(Proc, 0,sizeof(PROCESSINFO));  
            Proc->PID = info->th32ProcessID;  
            HANDLE hToken;  
    	lstrcpy(Proc->ProcName,info->szExeFile);	  
    	if (OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES,&hToken))  //打开与进程相关联的访问令牌                                                                          
    	{  
    	    if (EnablePrivilege(hToken,SE_DEBUG_NAME))  
    	    {			  
    		EnumProcesses(processid, sizeof(processid), &needed);    //检索进程中的每一个进程标识符，得到进程标识符数组processid  
     		hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,false,processid[i]);   //打开进程对象，并返回进程     //                                                                                                           的句柄  
    		if (hProcess)            //打开进程检索进程加载模块的路径  
    		{  
    		    EnumProcessModules(hProcess, &hModule, sizeof(hModule), &needed);  
    		    GetModuleFileNameEx(hProcess, hModule, path, sizeof(path));        //获取当前进程已加载模块的文件的完整路径  
    		    GetShortPathName(path,path,260);  
    		    lstrcpy(Proc->ProcPath,path);					  
    		}  
    	     }		  
    	}  
    	i++;  
    	pProcInfo->push_back(Proc);  
        }  
        while(Process32Next(handle,info)!=FALSE)           //循环获得下一个进程的句柄
        {  
    	Proc = new PROCESSINFO;  
    	memset(Proc, 0,sizeof(PROCESSINFO));  
    	Proc->PID = info->th32ProcessID;  
            lstrcpy(Proc->ProcName,info->szExeFile);  
    	HANDLE hToken;  
      
    	if ( OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES,&hToken))     //获得进程访问令牌  
    	{  
    	    if (EnablePrivilege(hToken,SE_DEBUG_NAME))        //提升进程权限  
    	    {		  
    		EnumProcesses(processid, sizeof(processid), &needed);      //  
    		hProcess=OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,false,processid[i]);  
    		if (hProcess)  
    		{  
    		    EnumProcessModules(hProcess, &hModule, sizeof(hModule), &needed);  
    		    GetModuleFileNameEx(hProcess, hModule, path, sizeof(path));  
    		    GetShortPathName(path,path,260);  
    		    lstrcpy(Proc->ProcPath,path);				  
    		}  
    	    }		  
    	}		  
    	i++;  
    	pProcInfo->push_back(Proc);  
        }  
        CloseHandle(handle);  
        return true;  
    }  
    

## 屏幕监视

CGetScreenToBitmap类用来获取当前屏幕画面转化成位图信息。  

    
    
    SetArea(CRect rcArea,int nArea);        // 取图象区域                           
    void ResetVariable(void);               //释放资源  
    GetScreen(CRect rcArea, int nBits, int nArea);       //截取屏幕

![截屏\(1\).jpg](https://image.3001.net/images/20180306/15203512813504.jpg!small)  

[代码传送门](https://github.com/qiutianshu/MyServer)

 ***本文原创作者：Mr极目楚天舒，本文属FreeBuf原创奖励计划，未经许可禁止转载**

