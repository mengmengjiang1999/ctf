> 0x0 成果展示
>
> 0x1 起因
>
> 0x2 准备的东西
>
> 0x3 驱动编写
>
> 0x4 Client编写
>
> 0x5 Python Web后端编写
>
> 0x6 结论
>
> 0x7 后记

## 0x0 成果展示

![](https://image.3001.net/images/20191119/1574154499_5dd3b103a404d.jpg!small)

![](https://image.3001.net/images/20191119/1574167219_5dd3e2b3561db.jpg!small)

没有做日志记录因为时间关系。

我们假设恶意C2C服务器IP是220.181.38.148(百度的某个节点),某个木马的恶意流量特征是?? ?? ?? ??(? 匹配所有)

当我们要屏蔽220.181.38.148IP的时候 在我们后台输入这个IP地址就可以屏蔽了,当然这里只是展示了屏蔽功能,也可以做成给后台报警

这是没有增加规则的:

![](https://image.3001.net/images/20191119/1574166895_5dd3e16f0481a.jpg!small)

增加了规则:

![](https://image.3001.net/images/20191119/1574166966_5dd3e1b63719b.jpg!small)

数据包同理,这里的?? 代表匹配所有数据包。因此会把所有的数据包全部drop 掉

![](https://image.3001.net/images/20191119/1574167109_5dd3e2459d05e.jpg!small)

![](https://image.3001.net/images/20191119/1574167116_5dd3e24c8c277.jpg!small)

依然ping的通百度但是无法打开页面(因为数据包都被drop了。

当然你也可以选择记录这些IP和数据去后台进行报警通知.只要木马的流量特征库足够大,

这里说一下 很多DDOS防火墙也是这个道理,通过检测数据包的特征判断是否有DDOS攻击,一些AMP攻击的流量特征是固定的.

GitHub地址:<https://github.com/huoji120/NetWatch>

## 0x1 起因

本人是新手第一次接触驱动开发的小白,事情是这样的,一个星期前突发奇想想做一个威胁流量检测系统.于是就有了今天这篇文章。

## 0x2 准备的东西

做过防火墙的同学应该熟悉在windows下普遍使用WFP或者NDIS这两种驱动框架,这两种框架各有各的优点,我自己总结为:

NDIS够底层,能拦截所有的数据包和协议,而且兼容性好,覆盖系统全面.但是NDIS因为太底层,很多功能无法实现.而且很多功能实现的方法不是很友好

WFP够方便,Filte
Engine很容易就能实现一个防火墙,简单快捷.而且可以很方便的得到发包进程的详细信息.但是不是很底层,依赖于tcpip.sys,如果某些东西自己写一个驱动去发包就无法抓取到.

NDIS防火墙安装会断网.这也是为什么诸如安全狗这类软件会断网的原因

不过考虑到我放弃了WIN2003系统,所以我选择了更加方便的WFP

WFP工作方式如图:

![](https://image.3001.net/images/20191119/1574153082_5dd3ab7a53278.png!small)

## 0x3 驱动编写

首先实现一个抓包demo:

R3部分建立pipe管道

    
    
    enum ReportType
    {
    	r_income, //进来auth
    	r_output, //出去auth
    	r_stream_income,  //TCP流交互
    	r_stream_output
    };
    enum Protocoltype
    {
    	Pro_ICMP = 1,
    	Pro_IGMP = 2,
    	Pro_TCP = 6,
    	Pro_UDP = 17,
    	Pro_RDP = 27,
    	Pro_UNKNOWN
    };
    struct Networkreport {
    	ReportType type;
    	Protocoltype Protocol;
    	DWORD IPaddr;
    	DWORD BuffDataLen;
    	char* BuffData;
    };
    std::string GetSigHex(char* data, int len)
    {
    	char buf[0xFFFF] = { 0 };
    	for (int i = 0; i < len; i++)
    	{
    		char test[8] = { 0 };
    		if (i == len - 1)
    		{
    			sprintf_s(test, "%02X", (BYTE)data[i]);
    			strcat_s(buf, test);
    		}
    		else
    		{
    			sprintf_s(test, "%02X ", (BYTE)data[i]);
    			strcat_s(buf, test);
    		}
    	}
    	return std::string(buf);
    }
    int main()
    {
    	HANDLE hPipe = CreateNamedPipe(
    		TEXT("\\\\.\\Pipe\\EzFireWall"),
    		PIPE_ACCESS_DUPLEX | FILE_FLAG_OVERLAPPED,
    		PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
    		PIPE_UNLIMITED_INSTANCES,
    		0,
    		0,
    		NMPWAIT_WAIT_FOREVER,
    		NULL);
    	if (INVALID_HANDLE_VALUE == hPipe)
    		return false;
        std::cout << "创建管道完毕,监听程序...\n";
    	const int size = 1024 * 10;
    	char buf[size];
    	DWORD rlen = 0;
    	while (true)
    	{
    		if (ConnectNamedPipe(hPipe, NULL) != NULL)
    		{
    			if (ReadFile(hPipe, buf, size, &rlen, NULL) == FALSE)
    				continue;
    			else
    			{
    				//接收信息
    				Networkreport* buffer_tmp = (Networkreport*)&ampbuf
    				SIZE_T buffer_len = sizeof(Networkreport) + buffer_tmp->BuffDataLen;
    				Networkreport* buffer = (Networkreport*)malloc(buffer_len);
    				memcpy(buffer, buffer_tmp, buffer_len);
    				char* data = (char*)malloc(buffer->BuffDataLen);
    				BYTE* tmp = (BYTE*)buffer + sizeof(Networkreport);
    				memcpy(data, tmp, buffer->BuffDataLen);
    				DWORD RemoteIP = buffer->IPaddr;
    				printf("远程IP:%u.%u.%u.%u 协议类型: %d 数据类型: %d 长度: %d \n", (RemoteIP >> 24) & 0xFF, (RemoteIP >> 16) & 0xFF, (RemoteIP >> 8) & 0xFF, RemoteIP & 0xFF, buffer->Protocol, buffer->type, buffer->BuffDataLen);
    				if (buffer->type == r_stream_income || buffer->type == r_stream_output)
    				{
    					printf("数据: %s \n", GetSigHex(data,buffer->BuffDataLen).c_str());
    				}
    				free(data);
    				free(buffer);
    			}
    		}
    
    	}
    	std::cout << "出现错误 \n";
    	system("pause");
    	return 0;
    }

在驱动entry部分连接pipe管道:

    
    
    HANDLE	g_hClient;
    
    IO_STATUS_BLOCK g_ioStatusBlock;
    
    KEVENT	g_event;
    
    VOID ReportToR3(Networkreport* m_parameter,int lent)
    
    {
    
    if (!NT_SUCCESS(ZwWriteFile(g_hClient, NULL, NULL, NULL, &g_ioStatusBlock, (void*)m_parameter, lent, NULL, NULL)))
    
    DPRINT("[DebugMessage] Error Cannot Wirte Pipe! \n"),
    
    g_hClient = 0;
    
    }  
    
    
    
            RtlInitUnicodeString(&uniName, L"\\DosDevices\\Pipe\\EzFireWall");
    	InitializeObjectAttributes(&objAttr, &uniName,OBJ_CASE_INSENSITIVE | OBJ_KERNEL_HANDLE,NULL, NULL);
    	Status = ZwCreateFile(&g_hClient,
    		GENERIC_READ | GENERIC_WRITE,
    		&objAttr, &g_ioStatusBlock,
    		NULL,
    		FILE_ATTRIBUTE_NORMAL,
    		0,
    		FILE_OPEN,
    		FILE_SYNCHRONOUS_IO_NONALERT,
    		NULL, 0);
    	if (!NT_SUCCESS(Status) || !g_hClient)
    	{
    		DPRINT("[DebugMessage] Cannot pipe Fail! 0x%08X \n", Status);
    		return Status;
    	}
    	DPRINT("[DebugMessage] Connect pipe Success!\n");
    	KeInitializeEvent(&g_event, SynchronizationEvent, TRUE);

然后WFP模板部分不单独发了,没什么好说的,重点说一下我们要挂钩的几个地方:

FWPM_LAYER_ALE_AUTH_CONNECT_V4、FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V4
分别对应链接认证阶段阶段,区别是一个是out一个是income  

FWPM_LAYER_STREAM_V4 抓取数据流,用于流量信息监测  

    
    
    	if (IsEqualGUID(layerKey, &FWPM_LAYER_ALE_AUTH_CONNECT_V4))
    	{
    		DPRINT("[DebugMessage] 挂载 FWPM_LAYER_ALE_AUTH_CONNECT_V4! \n");
    		sCallout.classifyFn = SFALEConnectClassify; //我们的回调
    		sCallout.notifyFn = SFALEConnectNotify;
    	}
    	else if (IsEqualGUID(layerKey, &FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V4))
    	{
    		DPRINT("[DebugMessage] 挂载 FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V4! \n");
    		sCallout.classifyFn = SFALERecvAcceptClassify; //我们的回调
    		sCallout.notifyFn = SFALERecvAcceptNotify;
    	}
    	else if (IsEqualGUID(layerKey, &FWPM_LAYER_STREAM_V4))
    	{
    		DPRINT("[DebugMessage] 挂载 FWPM_LAYER_STREAM_V4! \n");
    		sCallout.classifyFn = SFALERecvDataClassify; //我们的回调
    		sCallout.notifyFn = SFALERecvDataNotify;
    	}
    	Status = FwpsCalloutRegister0(DeviceObject,
    		&sCallout,
    		calloutId);  
    

其中
值得一提的是FWPM_LAYER_ALE_CONNECT_REDIRECT_V4,可以改变连接的地址,实现偷梁换柱功能.非常适合拿去干坏事.不过不在本次的讨论范围内

在SFALEConnectClassify和SFALERecvAcceptClassify回调中,负责屏蔽黑名单IP,这部分稍微抄了一下前辈的代码:

    
    
    //本地连别人的IP的连接
    void SFALEConnectClassify(
    	__in const FWPS_INCOMING_VALUES0* inFixedValues,
    	__in const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    	__inout void* layerData,
    	__in const FWPS_FILTER0* filter,
    	__in UINT64 flowContext,
    	__in FWPS_CLASSIFY_OUT0* classifyOut
    )
    {
    	if (classifyOut->rights & FWPS_RIGHT_ACTION_WRITE)
    	{
    		FWP_ACTION_TYPE Action = (CanIFilterThisRequest(inFixedValues,inMetaValues, layerData,flowContext) ? FWP_ACTION_BLOCK : FWP_ACTION_PERMIT);
    
    		PerformBasicAction(inFixedValues,
    			inMetaValues,
    			layerData,
    			filter,
    			flowContext,
    			classifyOut,
    			Action);
    	}
    }
    //接收远程IP的连接
    void SFALERecvAcceptClassify(
    	__in const FWPS_INCOMING_VALUES0* inFixedValues,
    	__in const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    	__inout void* layerData,
    	__in const FWPS_FILTER0* filter,
    	__in UINT64 flowContext,
    	__inout FWPS_CLASSIFY_OUT0* classifyOut
    )
    {
    	if (classifyOut->rights & FWPS_RIGHT_ACTION_WRITE)
    	{
    		FWP_ACTION_TYPE Action = (CanIFilterThisRequest(inFixedValues,inMetaValues, layerData, flowContext) ? FWP_ACTION_BLOCK : FWP_ACTION_PERMIT);
    
    		PerformBasicAction(inFixedValues,
    			inMetaValues,
    			layerData,
    			filter,
    			flowContext,
    			classifyOut,
    			Action);
    	}
    }
      
    

FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V4 这里是我之前代码,有个小bug,至于是什么bug大佬应该一眼看出来了:  

    
    
    void SFALERecvDataClassify(
    	__in const FWPS_INCOMING_VALUES0* inFixedValues,
    	__in const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    	__inout void* layerData,//这玩意是数据指针
    	__in const FWPS_FILTER0* filter,
    	__in UINT64 flowContext,
    	__inout FWPS_CLASSIFY_OUT0* classifyOut
    )
    {
    	if (KeGetCurrentIrql() > DISPATCH_LEVEL)
    	{
    		DPRINT("[DebugMessage] Erro in PassIve: %d \n", KeGetCurrentIrql());
    		return FALSE;
    	}
    	
    	FWPS_STREAM_CALLOUT_IO_PACKET* streamPacket = (FWPS_STREAM_CALLOUT_IO_PACKET*)layerData;
    	DWORD RemoteIP = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_REMOTE_ADDRESS].value.uint32;
    	DWORD LocalIP = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_LOCAL_ADDRESS].value.uint32;
    	if (streamPacket && streamPacket->streamData != NULL && streamPacket->streamData->dataLength != 0  && RemoteIP != LocalIP && g_StartFilter)
    	{
    		SIZE_T streamLength = streamPacket->streamData->dataLength;
    		BOOLEAN inbound = (BOOLEAN)((streamPacket->streamData->flags & FWPS_STREAM_FLAG_RECEIVE) == FWPS_STREAM_FLAG_RECEIVE);
    		BYTE* stream = ExAllocatePoolWithTag(NonPagedPool, streamLength, TAG_NAME_NOTIFY);
    		SIZE_T byte_copied = 0;
    		if (stream)
    		{
    			RtlZeroMemory(stream, streamLength);
    			FwpsCopyStreamDataToBuffer(
    				streamPacket->streamData,
    				stream,
    				streamLength,
    				&byte_copied);
    			NT_ASSERT(bytesCopied == streamLength);
    			DPRINT("[DebugMessage] inbound: %d streamBuffer: %s ", inbound, stream);
    			SIZE_T buffsize = streamLength + sizeof(Networkreport);
    			inbound = (BOOLEAN)((streamPacket->streamData->flags & FWPS_STREAM_FLAG_RECEIVE) == FWPS_STREAM_FLAG_RECEIVE);
    			Networkreport* report = (Networkreport*)ExAllocatePoolWithTag(NonPagedPool, buffsize, TAG_NAME_REPORT);
    			if (report)
    			{
    				RtlZeroMemory(report, buffsize);
    				report->type = inbound ? r_stream_income : r_stream_output;
    				report->Protocol = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_PROTOCOL].value.uint16;
    				report->IPaddr = RemoteIP;
    				report->BuffDataLen = streamLength;
    				//定位到buffer的sizeof(Networkreport)位置
    				BYTE* tmp = (BYTE*)report + sizeof(Networkreport);
    				memcpy(tmp, stream, streamLength);
    				ReportToR3(report, buffsize);
    				ExFreePool(report);
    			}
    
    			ExFreePool(stream);
    		}
    	}
    	classifyOut->actionType = FWP_ACTION_CONTINUE;
    
    }
      
    

结果:

![](https://image.3001.net/images/20191119/1574154097_5dd3af71a6936.png!small)

好的可以抓包了就可以开始进行下一步过滤了:

首先是提交过滤的程序,这里偷懒了:

    
    
    //添加数据到 到黑名单数据列表
    VOID AddBlackListData(char* data,DWORD blockip,SIZE_T len)
    {
    	if (blockip == 0x0)
    	{
    		DPRINT("[DebugMessage] BlackData :%s len: %d \n", data, len);
    		PBLACK_LIST_DATA newLink = (PBLACK_LIST_DATA)ExAllocatePoolWithTag(PagedPool, sizeof(BLACK_LIST_DATA), TAG_NAME_BLACKLISTDATA);
    		if (newLink == NULL)
    			ASSERT(false);
    		//RtlZeroMemory(newLink, sizeof(BLACK_LIST_DATA));
    		memcpy(newLink->data, data, len);
    		DPRINT("[DebugMessage] BlackData :%s \n", newLink->data);
    		InsertTailList(&gBackListDataTable.link, (PLIST_ENTRY)newLink);
    	}
    	else
    	{
    		 for (int i = 0; i < MAX_DATA_SIZE; i++)
    		 {
    			if (gBackListIPTable[i] == 0)
    			{
    				gBackListIPTable[i] = blockip;
    				DPRINT("[DebugMessage] BlackIP :0x%08X \n", gBackListIPTable[i]);
    				break;
    			}
    		 }
    	}
    }  
    

控制码:

    
    
    NTSTATUS DriverControlHandler(
    	IN PDEVICE_OBJECT DeviceObject,
    	IN PIRP Irp)
    
    {
    	PIO_STACK_LOCATION  irpSp;// Pointer to current stack location
    	NTSTATUS            ntStatus = STATUS_UNSUCCESSFUL;// Assume success
    	ULONG               inBufLength; // Input buffer length
    	ULONG               outBufLength; // Output buffer length
    	PUCHAR				inBuf, outBuf;
    	UNREFERENCED_PARAMETER(DeviceObject);
    	irpSp = IoGetCurrentIrpStackLocation(Irp);
    
    	inBufLength = irpSp->Parameters.DeviceIoControl.InputBufferLength;
    	outBufLength = irpSp->Parameters.DeviceIoControl.OutputBufferLength;
    
    	inBuf = (PUCHAR)Irp->AssociatedIrp.SystemBuffer;
    	outBuf = (PUCHAR)Irp->AssociatedIrp.SystemBuffer;
    	DPRINT("[DebugMessage] DriverControlHandler: inBufLength: %d outBufLength: %d \n", inBufLength, outBufLength);
    
    	if (!inBufLength || !outBufLength)
    	{
    		ntStatus = STATUS_INVALID_PARAMETER;
    		goto End;
    	}
    
    	switch (irpSp->Parameters.DeviceIoControl.IoControlCode)
    	{
    	case IOCTL_ADD_BLACKLIST_DATA:
    	{
    		DPRINT("[DebugMessage] Add BlackList Data! \n");
    		PPUSH_DATA push_data = (PPUSH_DATA)ExAllocatePoolWithTag(PagedPool, sizeof(PUSH_DATA), "tM2d");
    		if (push_data)
    		{
    			RtlZeroMemory(push_data, sizeof(PUSH_DATA));
    			memcpy(push_data, inBuf, inBufLength);
    			AddBlackListData(push_data->data, push_data->BlockIP, push_data->dataLen);
    			DPRINT("[DebugMessage] BlockIP: 0x%08X data: %s len: %d \n",  push_data->BlockIP, push_data->data, push_data->dataLen);
    			g_StartFilter = TRUE;
    			ntStatus = STATUS_SUCCESS;
    			ExFreePoolWithTag(push_data, "tM2d");
    		}
    		else
    		{
    			ntStatus = STATUS_INVALID_PARAMETER;
    		}
    	
    		break;
    	}
    	default:
    		break;
    	}
    
    End:
    	Irp->IoStatus.Status = ntStatus;
    	Irp->IoStatus.Information = 0;
    
    	IoCompleteRequest(Irp, IO_NO_INCREMENT);
    
    	return ntStatus;
    }  
    

黑名单IP匹配:

    
    
    //黑名单IP匹配
    BOOLEAN QueryBlackIP(DWORD ipaddr)
    {
    	KIRQL   Irql = ExAcquireSpinLockExclusive(&gBlockIpLock);
    	BOOLEAN result = FALSE;
    	for (int i = 0; i < MAX_DATA_SIZE; i++)
    	{
    		if (gBackListIPTable[i] == ipaddr)
    		{
    			result = TRUE;
    			break;
    		}
    	}
    	ExReleaseSpinLockExclusive(&gBlockIpLock, Irql);
    	return result;
    }  
    

之后在SFALEConnectClassify和SFALERecvAcceptClassify的地方进行验证:

    
    
    BOOLEAN CanIFilterThisRequest(
    	__in const FWPS_INCOMING_VALUES0* inFixedValues,
    	__in const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    	__in void* packet,
    	_In_ UINT64 flowContext
    )
    {
    	UNREFERENCED_PARAMETER(inMetaValues);
    	if (KeGetCurrentIrql() > DISPATCH_LEVEL)
    	{
    		DPRINT("[DebugMessage] Erro in PassIve: %d \n", KeGetCurrentIrql());
    		return FALSE;
    	}
    	if (g_StartFilter)
    	{
    		DWORD LocalIp = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_LOCAL_ADDRESS].value.uint32;
    		DWORD RemoteIP = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_REMOTE_ADDRESS].value.uint32;
    		if (LocalIp != RemoteIP)
    		{
    			if (QueryBlackIP(RemoteIP))
    			{
    				DPRINT("[DebugMessage] Found BlackList IP! \n");
    				return TRUE;
    			}
    		}
    
    	}
    
    	//这边可以阻止黑名单IP进入.
    	/*
    	char* ProtocolName = ProtocolIdToName(inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_PROTOCOL].value.uint16);
    	DWORD LocalIp = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_LOCAL_ADDRESS].value.uint32;
    	DWORD RemoteIP = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_REMOTE_ADDRESS].value.uint32;
    	DPRINT("[DebugMessage] Out: ProtocolName: %s Local: %u.%u.%u.%u:%d Remote:%u.%u.%u.%u:%d Protocol: %s \n",
    		(LocalIp >> 24) & 0xFF, (LocalIp >> 16) & 0xFF, (LocalIp >> 8) & 0xFF, LocalIp & 0xFF,
    		inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_LOCAL_PORT].value.uint16,
    		(RemoteIP >> 24) & 0xFF, (RemoteIP >> 16) & 0xFF, (RemoteIP >> 8) & 0xFF, RemoteIP & 0xFF,
    		inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_REMOTE_PORT].value.uint16,
    		ProtocolName);
    	ExFreePool(ProtocolName);
    	*/
    	return FALSE;
    }  
    

CanIFilterThisRequest 返回TRUE后
在SFALEConnectClassify和SFALERecvAcceptClassify中阻止链接:

    
    
    FWP_ACTION_TYPE Action = (CanIFilterThisRequest(inFixedValues,inMetaValues, layerData,flowContext) ? FWP_ACTION_BLOCK : FWP_ACTION_PERMIT);
    
    PerformBasicAction(inFixedValues,inMetaValues,layerData,filter,flowContext,classifyOut,Action);  
    

然后是数据包过滤:

    
    
    //黑名单数据匹配
    BOOLEAN QueryBlackListData(char* data, SIZE_T len)
    {
    	KIRQL   Irql = ExAcquireSpinLockExclusive(&gBlockDataLock);
    	BOOLEAN result = FALSE;
    	PLIST_ENTRY	head = &gBackListDataTable.link
    	PBLACK_LIST_DATA next = (PBLACK_LIST_DATA)gBackListDataTable.link.Blink;
    	while (head != (PLIST_ENTRY)next)
    	{
    		if(FindPattern(next->data, data, len))
    		{
    			result = TRUE;
    			break;
    		}
    	}
    	ExReleaseSpinLockExclusive(&gBlockDataLock, Irql);
    	return result;
    }  
    
    
    
    void SFALERecvDataClassify(
    	__in const FWPS_INCOMING_VALUES0* inFixedValues,
    	__in const FWPS_INCOMING_METADATA_VALUES0* inMetaValues,
    	__inout void* layerData,//这玩意是数据指针
    	__in const FWPS_FILTER0* filter,
    	__in UINT64 flowContext,
    	__inout FWPS_CLASSIFY_OUT0* classifyOut
    )
    {
    	if (KeGetCurrentIrql() > DISPATCH_LEVEL)
    	{
    		DPRINT("[DebugMessage] Erro in PassIve: %d \n", KeGetCurrentIrql());
    		return FALSE;
    	}
    	
    	FWPS_STREAM_CALLOUT_IO_PACKET* streamPacket = (FWPS_STREAM_CALLOUT_IO_PACKET*)layerData;
    	DWORD RemoteIP = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_REMOTE_ADDRESS].value.uint32;
    	DWORD LocalIP = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_LOCAL_ADDRESS].value.uint32;
    	if (streamPacket && streamPacket->streamData != NULL && streamPacket->streamData->dataLength != 0  && RemoteIP != LocalIP && g_StartFilter)
    	{
    		SIZE_T streamLength = streamPacket->streamData->dataLength;
    		BOOLEAN inbound = (BOOLEAN)((streamPacket->streamData->flags & FWPS_STREAM_FLAG_RECEIVE) == FWPS_STREAM_FLAG_RECEIVE);
    		BYTE* stream = ExAllocatePoolWithTag(NonPagedPool, streamLength, TAG_NAME_NOTIFY);
    		SIZE_T byte_copied = 0;
    		if (stream)
    		{
    			RtlZeroMemory(stream, streamLength);
    			FwpsCopyStreamDataToBuffer(
    				streamPacket->streamData,
    				stream,
    				streamLength,
    				&byte_copied);
    			NT_ASSERT(bytesCopied == streamLength);
    			if (QueryBlackListData(stream, streamLength))
    			{
    				DPRINT("[DebugMessage] Found BlackList Data! \n");
    				classifyOut->actionType = FWP_ACTION_BLOCK;
    				ExFreePool(stream);
    				return;
    			}
    			/*
    			//抓包与截包,如果你发现这里蓝屏请自己加锁,但是会极大的影响系统运行效率(网络吞吐量太大,pipe管道有20MS的延迟,而且还是单线程.伤不起
    			DPRINT("[DebugMessage] inbound: %d streamBuffer: %s ", inbound, stream);
    			SIZE_T buffsize = streamLength + sizeof(Networkreport);
    			inbound = (BOOLEAN)((streamPacket->streamData->flags & FWPS_STREAM_FLAG_RECEIVE) == FWPS_STREAM_FLAG_RECEIVE);
    			Networkreport* report = (Networkreport*)ExAllocatePoolWithTag(NonPagedPool, buffsize, TAG_NAME_REPORT);
    			if (report)
    			{
    				RtlZeroMemory(report, buffsize);
    				report->type = inbound ? r_stream_income : r_stream_output;
    				report->Protocol = inFixedValues->incomingValue[FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_PROTOCOL].value.uint16;
    				report->IPaddr = RemoteIP;
    				report->BuffDataLen = streamLength;
    				//定位到buffer的sizeof(Networkreport)位置
    				BYTE* tmp = (BYTE*)report + sizeof(Networkreport);
    				memcpy(tmp, stream, streamLength);
    				ReportToR3(report, buffsize);
    				ExFreePool(report);
    			}*/
    
    			ExFreePool(stream);
    		}
    	}
    	classifyOut->actionType = FWP_ACTION_CONTINUE;
    
    }
      
    

匹配成功后 classifyOut->actionType = FWP_ACTION_BLOCK; 则丢掉这个数据包  

匹配函数FindPattern

    
    
    BOOL FindPattern(char* pattern,void* data,SIZE_T data_len)
    {
    	const char* pat = pattern;
    	DWORD firstMatch = 0;
    	DWORD End = (DWORD)data + data_len;
    	for (DWORD pCur = (DWORD)data; pCur < End; pCur++)
    	{
    		if (!*pat)
    			return firstMatch;
    
    		if (*(PBYTE)pat == '\?' || *(BYTE*)pCur == getByte(pat))
    		{
    			if (!firstMatch)
    				firstMatch = pCur;
    
    			if (!pat[2])
    				return firstMatch;
    
    			if (*(PWORD)pat == '\?\?' || *(PBYTE)pat != '\?')
    				pat += 3;
    
    			else
    				pat += 2;    //one ?
    		}
    		else
    		{
    			pat = pattern;
    			firstMatch = 0;
    		}
    	}
    
    	return firstMatch != NULL;
    }  
    

至此.驱动部分编写完毕.

##  **0x4 Client编写**

这里有个失误,不应该使用Client作为TCP服务端,应该是Python来做服务端,无所谓了.先能用再说:

    
    
    #define IOCTL_ADD_BLACKLIST_DATA \
        CTL_CODE(FILE_DEVICE_UNKNOWN, 0x1337, METHOD_IN_DIRECT, FILE_ANY_ACCESS)
    typedef NTSTATUS(WINAPI* NtOpenFileEx)(
    	_Out_ PHANDLE            FileHandle,
    	_In_  ACCESS_MASK        DesiredAccess,
    	_In_  POBJECT_ATTRIBUTES ObjectAttributes,
    	_Out_ PIO_STATUS_BLOCK   IoStatusBlock,
    	_In_  ULONG              ShareAccess,
    	_In_  ULONG              OpenOptions
    	);
    struct Networkstruct {
    	int data_len;
    	DWORD IP;
    	char data[255];
    };
    typedef struct _PUSH_DATA {
    	DWORD BlockIP;
    	SIZE_T dataLen;
    	char data[255];
    }PUSH_DATA, * PPUSH_DATA;
    NtOpenFileEx fpNtOpenFile = (NtOpenFileEx)GetProcAddress(GetModuleHandleA("ntdll"), "NtOpenFile");
    HANDLE deviceHandle_;
    bool is_loaded()
    {
    	if (!deviceHandle_ || deviceHandle_ == INVALID_HANDLE_VALUE) {
    		//deviceHandle_ = CreateFile(L"C:\\windows\\TEMP\\cpuz147\\cpuz145_x64.sys", FILE_ALL_ACCESS, FILE_SHARE_READ, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    		IO_STATUS_BLOCK io_status;
    		NTSTATUS status;
    
    		UNICODE_STRING    device_name = UNICODE_STRING{ sizeof(DEVICE_NAME) - sizeof(WCHAR), sizeof(DEVICE_NAME), (PWSTR)DEVICE_NAME };
    		OBJECT_ATTRIBUTES obj_attr = OBJECT_ATTRIBUTES{ sizeof(OBJECT_ATTRIBUTES), nullptr, &device_name, 0, nullptr, nullptr };
    
    		status = fpNtOpenFile(
    			&deviceHandle_, GENERIC_READ | GENERIC_WRITE | SYNCHRONIZE,
    			&obj_attr, &io_status, 0, OPEN_EXISTING);
    
    		if (!NT_SUCCESS(status)) {
    			ULONG i = 10;
    			do {
    				status = fpNtOpenFile(
    					&deviceHandle_, GENERIC_READ | GENERIC_WRITE | SYNCHRONIZE,
    					&obj_attr, &io_status, 0, OPEN_EXISTING);
    				Sleep(250);
    			} while (!NT_SUCCESS(status) && i--);
    		}
    	}
    	return deviceHandle_ && deviceHandle_ != INVALID_HANDLE_VALUE;
    }
    
    int main()
    {
    	
    	if (!is_loaded())
    	{
    		printf("加载驱动失败! %d \n", GetLastError());
    		system("pause");
    		return 0;
    	}
    	WSADATA wsaData;
    	SOCKET ClientSocket;
    	int port = 5099;
    
    	if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
    	{
    		return false;
    	}
    
    	SOCKET sockSrv = socket(AF_INET, SOCK_STREAM, 0);
    
    	SOCKADDR_IN addrSrv;
    	addrSrv.sin_family = AF_INET;
    	addrSrv.sin_port = htons(port); //1024以上的端口号  
    	addrSrv.sin_addr.S_un.S_addr = htonl(INADDR_ANY);
    
    	int retVal = bind(sockSrv, (LPSOCKADDR)&addrSrv, sizeof(SOCKADDR_IN));
    	if (retVal == SOCKET_ERROR) {
    		return false;
    	}
    
    	if (listen(sockSrv, 10) == SOCKET_ERROR) {
    		return false;
    	}
    
    	SOCKADDR_IN addrClient;
    	int len = sizeof(SOCKADDR);
    	static bool first = false;
    	ClientSocket = accept(sockSrv, (SOCKADDR*)&addrClient, &len);
    	if (ClientSocket == SOCKET_ERROR) {
    		return false;
    	}
    
    	while (true)
    	{
    		char recvBuf[255];
    		memset(recvBuf, 0, sizeof(recvBuf));
    		if (recv(ClientSocket, recvBuf, sizeof(recvBuf), 0) == 0 || ClientSocket == INVALID_SOCKET)
    		{
    			first = false;
    			closesocket(ClientSocket);
    			ClientSocket = accept(sockSrv, (SOCKADDR*)&addrClient, &len);
    			continue;
    		}
    		Networkstruct* buffer = (Networkstruct*)recvBuf;
    		
    		
    		//1说明是ip 2说明是data
    		char	output;
    		DWORD	returnLen, read;
    		PUSH_DATA data = { 0 };
    		data.BlockIP = buffer->IP;
    		data.dataLen = buffer->data_len;
    		printf("buffer->data %s \n", buffer->data);
    		memcpy(data.data, buffer->data,buffer->data_len);
    		printf("buffer len: %d data: %s IP: 0x%08X\n", data.dataLen, data.data, data.BlockIP);
    		
    		if (!DeviceIoControl(deviceHandle_,
    			IOCTL_ADD_BLACKLIST_DATA,
    			(LPVOID)&data,
    			sizeof(PUSH_DATA),
    			&output,
    			sizeof(char),
    			&returnLen,
    			NULL))
    		{
    			printf("DeviceIoControl错误: %d\n", GetLastError());
    		}
    		else
    		{
    			printf("提交规则成功 \n");
    		}
    		closesocket(ClientSocket);
    		ClientSocket = accept(sockSrv, (SOCKADDR*)&addrClient, &len);
    	}
    	closesocket(sockSrv);
    	WSACleanup();
    
    
    	system("pause");
    	return 0;
    }  
    

##  **0x5 Python web后台编写**

非常简单的代码,基于Flask和Jquery与semanticUI

    
    
    from flask import Flask, request
    from flask import render_template
    from binascii import hexlify
    from socket import inet_aton, socket, AF_INET, SOCK_STREAM
    import ctypes
    import json
    
    import struct
    import sys
    app = Flask(__name__)
    ip_blacklist = [{'data': '192.168.1.1', 'text': '测试路由器地址(此规则不会生效)'}]
    data_blacklist = [{'data': '?? ?? ?? ??', 'text': '拦截全部流量(此规则不会生效)'}]
    
    HOST = 'localhost'
    PORT = 5099
    BUFSIZ = 255
    ADDR = (HOST, PORT)
    
    
    def push_backlist_data(data, data_len, block_ip, push_type):
        if push_type == 1:
            data = "huoji"
            data_len = len(data)
        c = socket(AF_INET, SOCK_STREAM)
        c.connect(ADDR)
        packet = struct.pack("IL255s",
                             data_len,
                             int(block_ip),
                             data.encode('gbk'),
                             )
        c.send(packet)
        c.close()
    
    
    def Ip2Int(ipaddr):
        int_ip = struct.unpack('!I', inet_aton(ipaddr))[0]
        print('IP:' + str(int_ip))
        return int_ip
    
    
    @app.route('/')
    def index():
        context = ip_blacklist
        context_type = {
            'table_type1': "IP地址",
            'table_type2': "备注"
        }
        return render_template('index.html', main=context, type=context_type)
    
    
    @app.route('/api', methods=["POST", "GET"])
    def api():
        if request.method == 'POST':
            data = request.form.get("data")
            page = request.form.get("page")
            push = request.form.get("push")
            push_data = request.form.get("push_data")
            if data:
                # push_backlist_data(data, len(data))
                return json.dumps({"status": "success"})
            if page:
                json_return = {"status": "Error"}
                if int(page) == 1:
                    json_return = {
                        "status": "success",
                        "page": "ip_list",
                        "table_1": "IP地址",
                        "table_2": "备注",
                        "data": ip_blacklist
                    }
                if int(page) == 2:
                    json_return = {
                        "status": "success",
                        "page": "data_list",
                        "table_1": "特征码",
                        "table_2": "备注",
                        "data": data_blacklist
                    }
                return json.dumps(json_return)
            if push and push_data:
                json_return = {"status": "Error"}
                processdata = push_data.split("@")
                if int(push) == 1:
                    ip_blacklist.append({
                        "data": processdata[0],
                        "text": processdata[1]
                    })
                else:
                    data_blacklist.append({
                        "data": processdata[0],
                        "text": processdata[1]
                    })
                blockip = 0
                if int(push) == 1:
                    blockip = Ip2Int(processdata[0])
                print("type " + push + " blockip: " + str(blockip))
                push_backlist_data(
                    processdata[0],
                    len(processdata[0]),
                    blockip,
                    int(push)
                )
                return json.dumps(json_return)
        return "API"
    
    
    if __name__ == '__main__':
        app.run(debug=True)
      
    

## 0x6 结论

在前人无数的踩坑文章下诞生的没有的东西

## 0x7 后记

当今的安全企业很多都是在蹭政策(AkA
等保测评)去卖自家的产品赚钱,但自家的产品多半是从其他地方购买的东西或者是直接从github下载改造的东西.而且安全这个行业处于一个尴尬的地位,高压政策让进来的门槛变高,人员缺少,很多人觉得搞安全
= 搞黑客,去报培训班"培训"
,加上安全中的渗透这一块入门门槛和其他编程语言相比和java差不多,而渗透的水平只在于是否花更多时间积累更多经验.这些因素导致整个安全行业水分很大.有搞安全的公司领导根本不懂安全的、有安全公司直接拿开源产品改编然后去卖给甲方的.有整个公司就一个会搞安全的其他都是蹭饭的.这个时代的人们很浮躁,已经没有多少人可以像以前的人们一样能静下心来研究技术了.而是乐于给自己打上标签然后止步于这些自己立下的标签之下.

 ***本文原创作者：huoji120，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

