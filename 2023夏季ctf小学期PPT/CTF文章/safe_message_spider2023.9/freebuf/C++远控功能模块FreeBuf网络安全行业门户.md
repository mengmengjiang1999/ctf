## 一、前言

在利用C++编写远控，客户端会经常用到下边的十种功能获取被控端主机信息。

## 二、功能模块

### 1、获取本地计算机的名称和IP

    
    
    #include <iostream>
    #include <WinSock2.h>
    #include <WS2tcpip.h>
    #pragma comment(lib,"ws2_32.lib")
    #include <iphlpapi.h>
    #pragma comment(lib,"Iphlpapi.lib")
    #include <Windows.h>
    
    int main()
    {
    	int wVersionRequested = MAKEWORD(2, 2);
    	WSADATA lpWSAData;
    	WSAStartup(wVersionRequested, &lpWSAData);
    	//获取主机名
    	char szHostName[128];
    	if (gethostname(szHostName, 128) == 0)
    	{
    		std::cout << "本地计算机名称是：" << szHostName << std::endl;
    	}
    	//获取内网IP地址
    	struct hostent * pHost;
    	pHost = gethostbyname(szHostName);
    	for (size_t i = 0; pHost != NULL && pHost->h_addr_list[i] != NULL; i++)
    	{
    		std::cout << "内网IP地址是：" << inet_ntoa(*(struct in_addr *)pHost->h_addr_list[i]) << std::endl;
    	}
    
    	WSACleanup();
    	system("pause");
    	return 0;
    }

###
![1688964323_64ab8ce3ddd37832e25f5.png!small?1688964323956](https://image.3001.net/images/20230710/1688964323_64ab8ce3ddd37832e25f5.png!small?1688964323956)

### 2、获取本机子网IP地址和子网掩码

    
    
    #include <iostream>
    #include <atlstr.h>
    #include <WinSock2.h>
    #include <WS2tcpip.h>
    #pragma comment(lib,"ws2_32.lib")
    #include <iphlpapi.h>
    #pragma comment(lib,"Iphlpapi.lib")
    
    
    int main()
    {
    	CString szMark;
    	PIP_ADAPTER_INFO pAdapterInfo = NULL;
    	PIP_ADAPTER_INFO pAdapter = NULL;
    	DWORD dwRetVal = 0;
    	ULONG ulOutBufLen = sizeof(IP_ADAPTER_INFO);
    	//第一次调用GetAdaptersInfo获取ulOutBufLen大小
    	if (GetAdaptersInfo(NULL, &ulOutBufLen) == ERROR_BUFFER_OVERFLOW)
    	{
    		pAdapterInfo = (IP_ADAPTER_INFO *)malloc(ulOutBufLen);
    	}
    	if ((dwRetVal = GetAdaptersInfo(pAdapterInfo, &ulOutBufLen)) == NO_ERROR)
    	{
    		pAdapter = pAdapterInfo;
    		while (pAdapter)
    		{
    			PIP_ADDR_STRING pIPAddr;
    			pIPAddr = &pAdapter->IpAddressList;
    			while (pIPAddr)
    			{
    				std::cout << "IP：" << pIPAddr->IpAddress.String << std::endl;
    				std::cout << "Mask：" << pIPAddr->IpMask.String << std::endl;
    				std::cout << std::endl;
    				pIPAddr = pIPAddr->Next;
    			}
    			pAdapter = pAdapter->Next;
    		}
    	}
    	if (pAdapterInfo)
    	{
    		free(pAdapterInfo);
    	}
    
    	system("pause");
    	return 0;
    }

###
![1688964356_64ab8d0442800315a9edf.png!small?1688964356450](https://image.3001.net/images/20230710/1688964356_64ab8d0442800315a9edf.png!small?1688964356450)

### 3、获取本机物理网卡地址信息

    
    
    #include <iostream>
    #include <atlstr.h>
    #include <WinSock2.h>
    #include <WS2tcpip.h>
    #pragma comment(lib,"ws2_32.lib")
    #include <iphlpapi.h>
    #pragma comment(lib,"Iphlpapi.lib")
    #include <Windows.h>
    
    
    int main()
    {
    	PIP_ADAPTER_INFO pAdapterInfo = NULL;
    	PIP_ADAPTER_INFO pAdapter = NULL;
    	DWORD dwRetVal = 0;
    	pAdapterInfo = (IP_ADAPTER_INFO*)malloc(sizeof(IP_ADAPTER_INFO));
    	ULONG ulOutBufLen = sizeof(IP_ADAPTER_INFO);
    
    	if (GetAdaptersInfo(NULL, &ulOutBufLen) == ERROR_BUFFER_OVERFLOW)
    	{
    		pAdapterInfo = (IP_ADAPTER_INFO *)malloc(ulOutBufLen);
    	}
    
    	if ((dwRetVal = GetAdaptersInfo(pAdapterInfo, &ulOutBufLen)) == NO_ERROR)
    	{
    		pAdapter = pAdapterInfo;
    		while (pAdapter)
    		{
    			// pAdapter->Description中包含"PCI"的为物理网卡;pAdapter->Type是71的为无线网卡
    			if (strstr(pAdapter->Description, "PCI") > 0 || pAdapter->Type == 71)
    			{
    				printf("------------------------------\n");
    				printf("AdapterName: \t%s\n", pAdapter->AdapterName);
    				printf("AdapterDesc: \t%s\n", pAdapter->Description);
    				printf("AdapterAddr: \t");
    				for (UINT i = 0; i < pAdapter->AddressLength; i++)
    				{
    					printf("%X%c", pAdapter->Address[i],
    						i == pAdapter->AddressLength - 1 ? '\n' : '-');
    				}
    				printf("AdapterType: \t%d\n", pAdapter->Type);
    				printf("IPAddress: \t%s\n",
    					pAdapter->IpAddressList.IpAddress.String);
    				printf("IPMask: \t%s\n", pAdapter->IpAddressList.IpMask.String);
    			}
    			pAdapter = pAdapter->Next;
    		}
    	}
    	else
    	{
    		printf("Callto GetAdaptersInfo failed.\n");
    	}
    	system("pause");
    	return 0;
    }

###
![1688964387_64ab8d23050494b4385db.png!small?1688964387104](https://image.3001.net/images/20230710/1688964387_64ab8d23050494b4385db.png!small?1688964387104)

### 4、获取本机所有网卡（包括虚拟网卡）的列表和信息

    
    
    #include <iostream>
    #include <atlstr.h>
    #include <WinSock2.h>
    #include <WS2tcpip.h>
    #pragma comment(lib,"ws2_32.lib")
    #include <iphlpapi.h>
    #pragma comment(lib,"Iphlpapi.lib")
    #include <Windows.h>
    
    BOOL GetLocalAdaptersInfo()
    {
    	//IP_ADAPTER_INFO结构体
    	PIP_ADAPTER_INFO pIpAdapterInfo = NULL;
    	pIpAdapterInfo = new IP_ADAPTER_INFO;
    
    	//结构体大小
    	unsigned long ulSize = sizeof(IP_ADAPTER_INFO);
    
    	//获取适配器信息
    	int nRet = GetAdaptersInfo(pIpAdapterInfo, &ulSize);
    
    	if (ERROR_BUFFER_OVERFLOW == nRet)
    	{
    		//空间不足，删除之前分配的空间
    		delete[]pIpAdapterInfo;
    
    		//重新分配大小
    		pIpAdapterInfo = (PIP_ADAPTER_INFO) new BYTE[ulSize];
    
    		//获取适配器信息
    		nRet = GetAdaptersInfo(pIpAdapterInfo, &ulSize);
    
    		//获取失败
    		if (ERROR_SUCCESS != nRet)
    		{
    			if (pIpAdapterInfo != NULL)
    			{
    				delete[]pIpAdapterInfo;
    			}
    			return FALSE;
    		}
    	}
    
    	//MAC 地址信息
    	char szMacAddr[20];
    	//赋值指针
    	PIP_ADAPTER_INFO pIterater = pIpAdapterInfo;
    	while (pIterater)
    	{
    		std::cout << "网卡名称：" << pIterater->AdapterName << std::endl;
    
    		std::cout << "网卡描述：" << pIterater->Description << std::endl;
    
    		sprintf_s(szMacAddr, 20, "%02X-%02X-%02X-%02X-%02X-%02X",
    			pIterater->Address[0],
    			pIterater->Address[1],
    			pIterater->Address[2],
    			pIterater->Address[3],
    			pIterater->Address[4],
    			pIterater->Address[5]);
    
    		std::cout << "MAC 地址：" << szMacAddr << std::endl;
    
    		std::cout << "IP地址列表：" << std::endl << std::endl;
    
    		//指向IP地址列表
    		PIP_ADDR_STRING pIpAddr = &pIterater->IpAddressList;
    		while (pIpAddr)
    		{
    			std::cout << "IP地址：  " << pIpAddr->IpAddress.String << std::endl;
    			std::cout << "子网掩码：" << pIpAddr->IpMask.String << std::endl;
    
    			//指向网关列表
    			PIP_ADDR_STRING pGateAwayList = &pIterater->GatewayList;
    			while (pGateAwayList)
    			{
    				std::cout << "网关：    " << pGateAwayList->IpAddress.String << std::endl;
    				pGateAwayList = pGateAwayList->Next;
    			}
    			pIpAddr = pIpAddr->Next;
    		}
    		std::cout << std::endl << "--------------------------" << std::endl;
    		pIterater = pIterater->Next;
    	}
    
    	//清理
    	if (pIpAdapterInfo)
    	{
    		delete[]pIpAdapterInfo;
    	}
    
    	return TRUE;
    }
    
    int main()
    {
    	GetLocalAdaptersInfo();
    	std::cin.get();
    	system("pause");
    	return 0;
    }

###
![1688964442_64ab8d5af0e85eedb0514.png!small?1688964443159](https://image.3001.net/images/20230710/1688964442_64ab8d5af0e85eedb0514.png!small?1688964443159)

### 5、获取本地计算机的IP协议统计数据

注意：

1、在创建完MFC程序后需在C/C++->代码生成->Spectre缓解，将其缓解禁用，不然在后边生成代码会出现报错。

![1688964460_64ab8d6c19f6fd83dfa5b.jpg!small?1688964460329](https://image.3001.net/images/20230710/1688964460_64ab8d6c19f6fd83dfa5b.jpg!small?1688964460329)

2、如在生成时候出现如下报错，在配置常规中修改SDK版本即可。

![1688964471_64ab8d77cae7b25891f33.jpg!small?1688964472036](https://image.3001.net/images/20230710/1688964471_64ab8d77cae7b25891f33.jpg!small?1688964472036)

![1688964482_64ab8d820a2de369d6481.jpg!small?1688964483609](https://image.3001.net/images/20230710/1688964482_64ab8d820a2de369d6481.jpg!small?1688964483609)

在DemoDlg.cpp开头包括文件和引用库文件：

    
    
    #include <Iphlpapi.h>
    #pragma comment(lib,"IPHlpApi.lib")

列表框控件设置为上下滚动条，设置空间ID名为IDC_LIST。

![1688964494_64ab8d8e0a40115c96d39.jpg!small?1688964494787](https://image.3001.net/images/20230710/1688964494_64ab8d8e0a40115c96d39.jpg!small?1688964494787)

通过函数GetIpStatistics可以获取当前主机的IP协议的统计数据，比如已经收到了多少个数据包。该函数声明如下：

    
    
    ULONG GetIpStatistics(PMIB_IPSTATS pStats);

其中，参数pStats指向MIB_IPSTATS结构的指针，该结构接收本地计算机的IP统计信息。如果函数成功，返回值为NO_ERROR。如果函数失败，返回值是以下错误代码：·ERROR_INVALID_PARAMETER：pStats参数为空，或者GetIpStatistics无法写入pStats参数指向的内存。

结构体MIB_IPSTATS的定义如下：

    
    
    typedef struct _MIB_IPSTATS
        {
        // dwForwarding指定IPv4或IPv6的每个协议转发状态，而不是接口的转发状态
            DWORD        dwForwarding;
            DWORD  dwDefaultTTL;                   //起始于特定计算机上的数据包的默认初始生存时间
            DWORD        dwInReceives;             //接收到的数据包数
            DWORD        dwInHdrErrors;            //接收到的有头部错误的数据包数
            DWORD        dwInAddrErrors;           //收到的具有地址错误的数据包数
            DWORD        dwForwDatagrams;          //转发的数据包数
            DWORD        dwInUnknownProtos;        //接收到的具有未知协议的数据包数
            DWORD        dwInDiscards;             //丢弃的接收数据包的数目
            DWORD        dwInDelivers;             //已传递的接收数据包的数目
        // IP请求传输的传出数据包数。此数目不包括转发的数据包
            DWORD        dwOutRequests;
            DWORD        dwRoutingDiscards;        //丢弃的传出数据包的数目
            DWORD        dwOutDiscards;            //丢弃的传输数据包数
        //此计算机没有到目标IP地址的路由的数据包数，这些数据包被丢弃
            DWORD        dwOutNoRoutes;
        //允许碎片数据包的所有部分到达的时间量。如果在这段时间内所有数据块都没有到达，数据包将被丢弃
            DWORD        dwReasmTimeout;
            DWORD        dwReasmReqds;             //需要重新组装的数据包数
            DWORD        dwReasmOks;               //成功重新组合的数据包数
            DWORD        dwReasmFails;             //无法重新组合的数据包数
            DWORD        dwFragOks;                //成功分段的数据包数
        //由于IP头未指定分段而未分段的数据包数，这些数据包被丢弃
            DWORD        dwFragFails;
            DWORD        dwFragCreates;            //创建的片段数
            DWORD        dwNumIf;                  //接口的数目
            DWORD        dwNumAddr;                //与此计算机关联的IP地址数
            DWORD        dwNumRoutes;              //IP路由选项卡中的路由数
        } MIB_IPSTATS, *PMIB_IPSTATS;

双击按钮，为其添加事件响应代码：

    
    
    void CMFCApplication3Dlg::OnBnClickedButton1()
    {
    	CListBox* pListBox = (CListBox*)GetDlgItem(IDC_LIST);
    	pListBox->ResetContent();
    	MIB_IPSTATS IPStats;
    	//获得IP协议统计信息
    	if (GetIpStatistics(&IPStats) != NO_ERROR)
    	{
    		return;
    	}
    	CString strText = _T("");
    	strText.Format(_T("IP forwarding enabled or disabled:%d"),
    		IPStats.dwForwarding);
    	pListBox->AddString(strText);
    	strText.Format(_T("default time-to-live:%d"),
    		IPStats.dwDefaultTTL);
    	pListBox->AddString(strText);
    	strText.Format(_T("datagrams received:%d"),
    		IPStats.dwInReceives);
    	pListBox->AddString(strText);
    	strText.Format(_T("received header errors:%d"),
    		IPStats.dwInHdrErrors);
    	pListBox->AddString(strText);
    	strText.Format(_T("received address errors:%d"),
    		IPStats.dwInAddrErrors);
    	pListBox->AddString(strText);
    	strText.Format(_T("datagrams forwarded:%d"),
    		IPStats.dwForwDatagrams);
    	pListBox->AddString(strText);
    	strText.Format(_T("datagrams with unknown protocol:%d"),
    		IPStats.dwInUnknownProtos);
    	pListBox->AddString(strText);
    	strText.Format(_T("received datagrams discarded:%d"),
    		IPStats.dwInDiscards);
    	pListBox->AddString(strText);
    	strText.Format(_T("received datagrams delivered:%d"),
    		IPStats.dwInDelivers);
    	pListBox->AddString(strText);
    	strText.Format(_T("outgoing datagrams requested to send:%d"),
    		IPStats.dwOutRequests);
    	pListBox->AddString(strText);
    	strText.Format(_T("outgoing datagrams discarded:%d"),
    		IPStats.dwOutDiscards);
    	pListBox->AddString(strText);
    	strText.Format(_T("sent datagrams discarded:%d"),
    		IPStats.dwOutDiscards);
    	pListBox->AddString(strText);
    	strText.Format(_T("datagrams for which no route exists:%d"),
    		IPStats.dwOutNoRoutes);
    	pListBox->AddString(strText);
    	strText.Format(_T("datagrams for which all frags did not arrive:%d"),
    		IPStats.dwReasmTimeout);
    	pListBox->AddString(strText);
    	strText.Format(_T("datagrams requiring reassembly:%d"),
    		IPStats.dwReasmReqds);
    	pListBox->AddString(strText);
    	strText.Format(_T("successful reassemblies:%d"),
    		IPStats.dwReasmOks);
    	pListBox->AddString(strText);
    	strText.Format(_T("failed reassemblies:%d"),
    		IPStats.dwReasmFails);
    	pListBox->AddString(strText);
    	strText.Format(_T("successful fragmentations:%d"),
    		IPStats.dwFragOks);
    	pListBox->AddString(strText);
    	strText.Format(_T("failed fragmentations:%d"),
    		IPStats.dwFragFails);
    	pListBox->AddString(strText);
    	strText.Format(_T("datagrams fragmented:%d"),
    		IPStats.dwFragCreates);
    	pListBox->AddString(strText);
    	strText.Format(_T("number of interfaces on computer:%d"),
    		IPStats.dwNumIf);
    	pListBox->AddString(strText);
    	strText.Format(_T("number of IP address on computer:%d"),
    		IPStats.dwNumAddr);
    	pListBox->AddString(strText);
    	strText.Format(_T("number of routes in routing table:%d"),
    		IPStats.dwNumRoutes);
    	pListBox->AddString(strText);
    }

![1688964512_64ab8da0c69cf5d679c91.jpg!small?1688964513429](https://image.3001.net/images/20230710/1688964512_64ab8da0c69cf5d679c91.jpg!small?1688964513429)

# 6、获取本机的DNS地址

    
    
    #include <iostream>
    #include <atlstr.h>
    #include <WinSock2.h>
    #include <WS2tcpip.h>
    #pragma comment(lib,"ws2_32.lib")
    #include <iphlpapi.h>
    #pragma comment(lib,"Iphlpapi.lib")
    #include <Windows.h>
    
    int main()
    { 
    	DWORD nLength = 0;
    	//先获取实际大小，并存入nLength
    	if (GetNetworkParams(NULL, &nLength) != ERROR_BUFFER_OVERFLOW)
    	{
    		return -1;
    	}
    	//根据实际所需大小，分配空间
    	FIXED_INFO* pFixedInfo = (FIXED_INFO*)new BYTE[nLength];
    
    	//获得本地计算机网络参数
    	if (GetNetworkParams(pFixedInfo, &nLength) != ERROR_SUCCESS)
    	{
    		delete[] pFixedInfo;
    		return -1;
    	}
    
    	//获得本地计算机DNS服务器地址
    	char strText[500] = "本地计算机的DNS地址：\n";
    	IP_ADDR_STRING* pCurrentDnsServer = &pFixedInfo->DnsServerList;
    	while (pCurrentDnsServer != NULL)
    	{
    		char strTemp[100] = "";
    		sprintf(strTemp, "%s\n", pCurrentDnsServer->IpAddress.String);
    		strcat(strText, strTemp);
    		pCurrentDnsServer = pCurrentDnsServer->Next;
    	}
    	puts(strText);
    	delete[] pFixedInfo;
    
    	system("pause");
    	return 0;
    }
    

# 7、获取本机上的TCP统计数据

空间跟上边一样，改个对话框和Caption控件名字即可。

![1688964531_64ab8db32bccb1acaa365.jpg!small?1688964531937](https://image.3001.net/images/20230710/1688964531_64ab8db32bccb1acaa365.jpg!small?1688964531937)

该功能可以通过函数GetTcpStatistics实现，该函数声明如下：

    
    
    ULONG GetTcpStatistics(  PMIB_TCPSTATS pStats);

其中，参数pStats指向MIB_TCPSTATS结构的指针，该结构接收本地计算机的TCP统计信息。如果函数成功，返回值为NO_ERROR；如果函数失败，返回值是以下错误代码：·ERROR_INVALID_PARAMETER：pStats参数为空，或者GetTcpStatistics无法写入pStats参数指向的内存。

结构体MIB_TCPSTATS定义如下：

    
    
    typedef struct _MIB_TCPSTATS
        {
            DWORD       dwRtoAlgorithm;            //正在使用的重传超时（RTO）算法
            DWORD       dwRtoMin;                  // 以毫秒为单位的最小RTO值
            DWORD       dwRtoMax;                  // 以毫秒为单位的最大RTO值
            DWORD   dwMaxConn;// 最大连接数。若此成员为-1，则最大连接数是可变的
            //活动打开的次数。在活动打开状态下，客户端正在启动与服务器的连接
            DWORD       dwActiveOpens;
            //被动打开的次数。在被动打开中，服务器正在侦听来自客户端的连接请求
            DWORD       dwPassiveOpens;
            DWORD       dwAttemptFails;            // 连接尝试失败的次数
            DWORD       dwEstabResets;             // 已重置的已建立连接数
            DWORD       dwCurrEstab;               // 当前建立的连接数
            DWORD       dwInSegs;                  // 接收的段数
            DWORD       dwOutSegs;                 // 传输的段数。此数字不包括重新传输的段
            DWORD       dwRetransSegs;             // 重新传输的段数
            DWORD       dwInErrs;                  // 收到的错误数
            DWORD       dwOutRsts;                 // 使用重置标志集传输的段数
            //系统中当前存在的连接数。此总数包括除侦听连接之外所有状态的连接
            DWORD       dwNumConns;
        } MIB_TCPSTATS, *PMIB_TCPSTATS;

双击按钮，为其添加事件响应代码：

    
    
    void CMFCApplication3Dlg::OnBnClickedButton1()
    {
    	CListBox* pListBox = (CListBox*)GetDlgItem(IDC_LIST);
    	pListBox->ResetContent();
    
    	MIB_TCPSTATS TCPStats;
    
    	//获得TCP协议统计信息
    	if (GetTcpStatistics(&TCPStats) != NO_ERROR)
    	{
    		return;
    	}
    
    	CString strText = _T("");
    	strText.Format(_T("time-out algorithm:%d"),
    		TCPStats.dwRtoAlgorithm);
    	pListBox->AddString(strText);
    	strText.Format(_T("minimum time-out:%d"),
    		TCPStats.dwRtoMin);
    	pListBox->AddString(strText);
    	strText.Format(_T("maximum time-out:%d"),
    		TCPStats.dwRtoMax);
    	pListBox->AddString(strText);
    	strText.Format(_T("maximum connections:%d"),
    		TCPStats.dwMaxConn);
    	pListBox->AddString(strText);
    	strText.Format(_T("active opens:%d"),
    		TCPStats.dwActiveOpens);
    	pListBox->AddString(strText);
    	strText.Format(_T("passive opens:%d"),
    		TCPStats.dwPassiveOpens);
    	pListBox->AddString(strText);
    	strText.Format(_T("failed attempts:%d"),
    		TCPStats.dwAttemptFails);
    	pListBox->AddString(strText);
    	strText.Format(_T("established connections reset:%d"),
    		TCPStats.dwEstabResets);
    	pListBox->AddString(strText);
    	strText.Format(_T("established connections:%d"),
    		TCPStats.dwCurrEstab);
    	pListBox->AddString(strText);
    	strText.Format(_T("segments received:%d"),
    		TCPStats.dwInSegs);
    	pListBox->AddString(strText);
    	strText.Format(_T("segment sent:%d"),
    		TCPStats.dwOutSegs);
    	pListBox->AddString(strText);
    	strText.Format(_T("segments retransmitted:%d"),
    		TCPStats.dwRetransSegs);
    	pListBox->AddString(strText);
    	strText.Format(_T("incoming errors:%d"),
    		TCPStats.dwInErrs);
    	pListBox->AddString(strText);
    	strText.Format(_T("outgoing resets:%d"),
    		TCPStats.dwOutRsts);
    	pListBox->AddString(strText);
    	strText.Format(_T("cumulative connections:%d"),
    		TCPStats.dwNumConns);
    	pListBox->AddString(strText);
    }

![1688964553_64ab8dc9eb9944239668b.jpg!small?1688964554673](https://image.3001.net/images/20230710/1688964553_64ab8dc9eb9944239668b.jpg!small?1688964554673)

# 8、获取本机上的UDP统计数据

空间跟上边一样，改个对话框和Caption控件名字即可。

该功能可以通过函数GetTcpStatistics实现，该函数声明如下：

    
    
    ULONG GetUdpStatistics(  PMIB_UDPSTATS pStats);

其中，参数pStats指向接收本地计算机的UDP统计信息的MIB_UDPTABLE结构的指针，PMIB_UDPSTATS是MIB_UDPTABLE结构的指针类型。如果函数成功，返回值为NO_ERROR；如果函数失败，使用FormatMessage获取返回错误的消息字符串。

结构体MIB_UDPSTATS定义如下：

    
    
    typedef struct _MIB_UDPSTATS
        {
           DWORD       dwInDatagrams;             // 接收的数据包数
           DWORD       dwNoPorts;                 //由于指定的端口无效而丢弃的接收的数据包数
           //接收到的错误数据包的数目。此数字不包括dwNoPorts成员包含的值
           DWORD       dwInErrors;
           DWORD       dwOutDatagrams;            // 传输的数据包数
           DWORD       dwNumAddrs;                // UDP侦听器表中的条目数
        } MIB_UDPSTATS,*PMIB_UDPSTATS;

双击按钮，为其添加事件响应代码：

    
    
    void CMFCApplication3Dlg::OnBnClickedButton1()
    {
    	CListBox* pListBox = (CListBox*)GetDlgItem(IDC_LIST);
    	pListBox->ResetContent();
    
    	MIB_UDPSTATS UDPStats;
    
    	//获得UDP协议统计信息
    	if (GetUdpStatistics(&UDPStats) != NO_ERROR)
    	{
    		return;
    	}
    	CString strText = _T("");
    	strText.Format(_T("received datagrams:%d\t\n"),
    		UDPStats.dwInDatagrams);
    	pListBox->AddString(strText);
    	strText.Format(_T("datagrams for which no port exists:%d\t\n"),
    		UDPStats.dwNoPorts);
    	pListBox->AddString(strText);
    	strText.Format(_T("errors on received datagrams:%d\t\n"),
    		UDPStats.dwInErrors);
    	pListBox->AddString(strText);
    	strText.Format(_T("sent datagrams:%d\t\n"),
    		UDPStats.dwOutDatagrams);
    	pListBox->AddString(strText);
    	strText.Format(_T("number of entries in UDP listener table:%d\t\n"),
    		UDPStats.dwNumAddrs);
    	pListBox->AddString(strText);
    }

![1688964572_64ab8ddc7f4f6a6ef5ab2.jpg!small?1688964573428](https://image.3001.net/images/20230710/1688964572_64ab8ddc7f4f6a6ef5ab2.jpg!small?1688964573428)

# 9、获取本机上支持的网络协议信息

在DemoDlg.cpp开头包含头文件和引用库文件：

    
    
    #include <Winsock2.h>
        #pragma comment(lib,"Ws2_32.lib")

为列表框控件添加一个变量m_ctrlList，方便在将信息插入到列表框上。

![1688964584_64ab8de84b753d615d5c2.jpg!small?1688964584685](https://image.3001.net/images/20230710/1688964584_64ab8de84b753d615d5c2.jpg!small?1688964584685)

可以通过函数WSAEnumProtocols检索有关可用网络传输协议的信息。该函数声明如下：

    
    
    int WSAAPI WSAEnumProtocols(LPINT lpiProtocols,LPWSAPROTOCOL_INFOA lpProtocolBuffer,LPDWORD lpdwBufferLength);

其中，参数lpiProtocols指向协议值数组；lpProtocolBuffer指向用WSAPROTOCOL_INFOA结构填充的缓冲区的指针；lpdwBufferLength在输入时，传递给WSAEnumProtocols的lpProtocolBuffer缓冲区中的字节数。输出时，可以传递给WSAEnumProtocols以检索所有请求信息的最小缓冲区大小。如果函数没有出现错误，WSAEnumProtocols将返回要报告的协议数；否则，将返回SOCKET_ERROR的值，并且可以通过调用WSAGetLastError来检索特定的错误代码。

双击按钮，为其添加事件响应代码：

    
    
    void CMFCApplication3Dlg::OnBnClickedButton1()
    {
    
    	//初始化WinSock
    	WSADATA WSAData;
    	if (WSAStartup(MAKEWORD(2, 0), &WSAData) != 0)
    	{
    		return;
    	}
    
    	int nResult = 0;
    
    	//获得需要的缓冲区大小
    	DWORD nLength = 0;
    	nResult = WSAEnumProtocols(NULL, NULL, &nLength);
    	if (nResult != SOCKET_ERROR)
    	{
    		return;
    	}
    	if (WSAGetLastError() != WSAENOBUFS)
    	{
    		return;
    	}
    	WSAPROTOCOL_INFO* pProtocolInfo = (WSAPROTOCOL_INFO*)new BYTE[nLength];
    	//获得本地计算机协议信息
    	nResult = WSAEnumProtocols(NULL, pProtocolInfo, &nLength);
    	if (nResult == SOCKET_ERROR)
    	{
    		delete[] pProtocolInfo;
    		return;
    	}
    	for (int n = 0; n < nResult; n++)
    	{
    		m_ctrlList.AddString(pProtocolInfo[n].szProtocol);
    	}
    	delete[] pProtocolInfo;
    	//清理WinSock
    	WSACleanup();
    }
    

![1688964598_64ab8df64a27478a57c04.jpg!small?1688964599117](https://image.3001.net/images/20230710/1688964598_64ab8df64a27478a57c04.jpg!small?1688964599117)

# 10、获取本地计算机的域名

可以通过函数GetNetworkParams来获取本地计算机的域名。这个函数其实可以检索本地计算机的网络参数，包括域名、主机名等。当然如果本机没有设置域名，那么得到的域名字段内容就是一个空字符串。

该函数声明如下：

    
    
    DWORD
    WINAPI
    GetNetworkParams(
        _Out_writes_bytes_opt_(*pOutBufLen)   PFIXED_INFO pFixedInfo,
        _Inout_                         PULONG      pOutBufLen
        );

其中，参数pFixedInfo指向一个缓冲区的指针，该缓冲区包含一个固定的信息结构，该结构接收本地计算机的网络参数（如果函数成功），调用GetNetworkParams函数之前，调用方必须分配正确大小的缓冲区才会获得内容信息，如果该参数为NULL，那么pOutBufLen能获得实际所需要的缓冲区大小；参数pOutBufLen指向一个ULONG变量的指针，该变量指定固定信息结构的大小。如果此大小不足以容纳信息，GetNetworkParams将使用所需大小填充此变量，并返回错误代码ERROR_BUFFER_OVERFLOW。如果函数成功，返回值为ERROR_SUCCESS；如果函数失败，返回值是错误代码。

![1688964611_64ab8e036b13d521b671f.jpg!small?1688964612120](https://image.3001.net/images/20230710/1688964611_64ab8e036b13d521b671f.jpg!small?1688964612120)

双击按钮，为其添加事件响应代码：

    
    
    void CMFCApplication4Dlg::OnBnClickedButton1()
    {
    	//获得需要的缓冲区大小
    	DWORD nLength = 0;
    	if (GetNetworkParams(NULL, &nLength) != ERROR_BUFFER_OVERFLOW)
    	{
    		return;
    	}
    
    	FIXED_INFO* pFixedInfo = (FIXED_INFO*)new BYTE[nLength];
    
    	//获得本地计算机网络参数
    	if (GetNetworkParams(pFixedInfo, &nLength) != ERROR_SUCCESS)
    	{
    		delete[] pFixedInfo;
    		return;
    	}
    
    	//获得本地计算机域名
    	CString strText = _T("");
    	strText.Format(_T("本地计算机的域名：\n%s"), pFixedInfo->DomainName);
    	AfxMessageBox(strText);
    
    	delete[] pFixedInfo;
    }

![1688964627_64ab8e13aa5604f06f92e.jpg!small?1688964627824](https://image.3001.net/images/20230710/1688964627_64ab8e13aa5604f06f92e.jpg!small?1688964627824)

  

