## 前言

随着国内5G网络的快速建设，5G的安全问题受到越来越多的关注。本文在《free5gc+UERANSIM模拟5G网络环境搭建及基本使用》的模拟环境基础上，对《3GPP安全保障规范（SCAS）》（SeCurity
Assurance Specifications，简称SCAS）的系列文档《3GPP TS 33.513》以及《3GPP TS
33.515》中定义的SMF（Session Management Function）和UPF（User Plane
Function）网元安全需求进行了报文和代码分析，旨在为5G安全研究及测试人员提供参考。

## 一、概念介绍

3GPP在《3GPP安全保障规范（SCAS）》规范中为网元定义了安全需求和测试用例，《3GPP TS 33.513》和《3GPP TS
33.515》属于《3GPP安全保障规范SCAS》规范文档。两者分别规定了UPF和SMF特有的安全需求，这些特定安全要求既包括相关规范中针对UPF和SMF的安全功能要求，也包括与安全要求相关的测试用例。

### 1.1 网元介绍

 **UPF（User Plane Function）网元**

负责分组路由转发，策略实施，流量报告，Qos处理等。

 **SMF（Session Management Function）网元**

负责处理用户的业务，可以看成是 MME 承载管理部分以及 SGW 和 PGW 的控制面功能的组合。

### 1.2 安全需求对应流程

文中分析的三条安全需求对应PDU会话流程中具体步骤如下：

 **TEID的唯一性**

数据面隧道端点标识符（TEID）是由UDF分配且是不可重复的，SMF通过CreatePDR向UPF申请某个接口的TEID，对应PDU会话流程中的N4会话请求N4SessionEstablishmentRequest和响应报文N4SessionEstablishmentResponse。

 **UP安全策略的优先级**

触发PDU会话建立流程，SMF通过Nudm_SDM_Get服务从UDM检索会话管理订阅数据，SMF发送的N1N2消息中包含了
UDM的用户面安全策略，对应PDU会话流程中的Namf_Communication_N1N2MessageTransfer。

 **SMF检查UP安全策略的安全功能要求**

NG-RAN 节点通过向 AMF 发送 PATH SWITCH REQUEST 消息来启动该过程。SMF验证Path-Switch
message中UE的5G安全能力，是否与SMF自身存储的相同，若不相同，SMF应将其本地存储的UE的对应PDU会话的UP安全策略发送到目标gNB，对应PDU会话流程中的Nsmf_PDUSession_SMContextUpdate
Response。

## 二、 模拟环境介绍

本节简单介绍了UERANSIM+free5gc环境，用户可以通过使用arp、ifconfig、docker
inspect及网桥brctl相关命令，来收集容器IP及mac地址等相关信息，绘制的组网示意图如下：

![1640655929_61ca6c39462037c48b21a.png!small?1640655908202](https://image.3001.net/images/20211228/1640655929_61ca6c39462037c48b21a.png!small?1640655908202)

如上图所示：环境基于ubuntu 20.04
VMware虚机部署，5gc网元分别部署在虚机的docker容器中。5gc各模拟网元与模拟RAN通过虚拟网桥进行数据交换。物理机上的VMware虚拟网卡作为DN（互联网节点）通过虚拟网桥与容器中的UPF对接。详细的搭建方法可以参考沉烽网络安全实验室的文章《free5gc+UERANSIM模拟5G网络环境搭建及基本使用》。

## 三 、安全需求条目分析

### 3.1 UPF安全需求分析

 **3.1.1 TEID的唯一性**

 **需求描述**

当建立或者发布一个新的PDU会话时，将执行CN隧道信息的分配和释放，此功能基于运营商在SMF上的配置，并由SMF或UPF网元支持。如《3GPP TS
23.501》第5.8.2.3.1条所述，CN隧道信息是与PDU会话相对应的N3/N9隧道的核心网络地址。它包括由UPF在N3/N9隧道上使用的用于PDU会话的TEID和IP地址，CN隧道信息的分配和发布将由UPF执行。当UPF需要分配/发布CN隧道信息时，SMF应向UPF发出指示。

隧道端点标识符（TEID）：此字段在接受GTP U协议实体中明确标识隧道端点。GTP隧道的接收端本地分配发送端必须使用的TEID值。

TEID是一个逻辑节点的一个IP地址内的唯一标识符。

 **输入条件**

1.测试者截获测试UPF和SMF之间的流量。

2.测试者触发最大并发N4会话建立请求次数。

3.测试者捕获从UPF向SMF发送的N4会话建立响应，并验证为每个生成的响应创建的F-TEID是唯一的。

 **输出结果**

每个不同的N4会话建立响应中设置的F-TEID是唯一的。

 **条目分析**

捕获到SMF向UPF网元发送的PFCPSessionEstablishmentRequest请求。

![1640656589_61ca6ecd65494870393b1.jpg!small?1640656589747](https://image.3001.net/images/20211228/1640656589_61ca6ecd65494870393b1.jpg!small?1640656589747)

参照\smf\producer\pdu_session.go中的HandlePDUSessionSMContextCreate函数，其中调用了SendPFCPRules函数，定位到\smf\producer\datapath.go中的SendPFCPRules函数，在此函数中进行PfcpSessionEstablishmentRequest报文的发送。

    
    
    for ip, pfcp := range pfcpPool {
            sessionContext, exist := smContext.PFCPContext[ip]
            if !exist || sessionContext.RemoteSEID == 0 {
                pfcp_message.SendPfcpSessionEstablishmentRequest(
                    pfcp.nodeID, smContext, pfcp.pdrList, pfcp.farList, nil, pfcp.qerList)
            } else {
                pfcp_message.SendPfcpSessionModificationRequest(
                    pfcp.nodeID, smContext, pfcp.pdrList, pfcp.farList, nil, pfcp.qerList)
            }
        }

在发送PfcpSessionEstablishmentRequest报文之前，传入接口的SMContext中已经生成了GTP
Tunnel信息，定位到\smf\producer\pdu_session.go的HandlePDUSessionSMContextCreate函数。

    
    
    if smf_context.SMF_Self().ULCLSupport && smf_context.CheckUEHasPreConfig(createData.Supi) {
            logger.PduSessLog.Infof("SUPI[%s] has pre-config route", createData.Supi)
            uePreConfigPaths := smf_context.GetUEPreConfigPaths(createData.Supi, selectedUPFName)
            smContext.Tunnel.DataPathPool = uePreConfigPaths.DataPathPool
            smContext.Tunnel.PathIDGenerator = uePreConfigPaths.PathIDGenerator
            defaultPath = smContext.Tunnel.DataPathPool.GetDefaultPath()
            defaultPath.ActivateTunnelAndPDR(smContext, 255)
            smContext.BPManager = smf_context.NewBPManager(createData.Supi)
        } else {
            // UE has no pre-config path.
            // Use default route
            logger.PduSessLog.Infof("SUPI[%s] has no pre-config route", createData.Supi)
            defaultUPPath := smf_context.GetUserPlaneInformation().GetDefaultUserPlanePathByDNNAndUPF(
                upfSelectionParams, smContext.SelectedUPF)
            defaultPath = smf_context.GenerateDataPath(defaultUPPath, smContext)
            if defaultPath != nil {
                defaultPath.IsDefaultPath = true
                smContext.Tunnel.AddDataPath(defaultPath)
                defaultPath.ActivateTunnelAndPDR(smContext, 255)
            }
        }
    

函数 ActivateTunnelAndPDR中调用ActivateTunnelAndPDR函数。

    
    
    func (dataPath *DataPath) ActivateTunnelAndPDR(smContext *SMContext, precedence uint32) {
        smContext.AllocateLocalSEIDForDataPath(dataPath)
    
        firstDPNode := dataPath.FirstDPNode
        logger.PduSessLog.Traceln("In ActivateTunnelAndPDR")
        logger.PduSessLog.Traceln(dataPath.String())
        // Activate Tunnels
        for curDataPathNode := firstDPNode; curDataPathNode != nil; curDataPathNode = curDataPathNode.Next() {
            logger.PduSessLog.Traceln("Current DP Node IP: ", curDataPathNode.UPF.NodeID.ResolveNodeIdToIp().String())
            if err := curDataPathNode.ActivateUpLinkTunnel(smContext); err != nil {
                logger.CtxLog.Warnln(err)
                return
            }
            if err := curDataPathNode.ActivateDownLinkTunnel(smContext); err != nil {
                logger.CtxLog.Warnln(err)
                return
            }
        }

然后进入到\smf\context\datapath.go中的 ActivateUpLinkTunnel函数， teid是在此处由UPF生成的。

    
    
    func (node *DataPathNode) ActivateUpLinkTunnel(smContext *SMContext) error {
        var err error
        logger.CtxLog.Traceln("In ActivateUpLinkTunnel")
        node.UpLinkTunnel.SrcEndPoint = node.Prev()
        node.UpLinkTunnel.DestEndPoint = node
    
        destUPF := node.UPF
        if node.UpLinkTunnel.PDR, err = destUPF.AddPDR(); err != nil {
            logger.CtxLog.Errorln("In ActivateUpLinkTunnel UPF IP: ", node.UPF.NodeID.ResolveNodeIdToIp().String())
            logger.CtxLog.Errorln("Allocate PDR Error: ", err)
            return fmt.Errorf("Add PDR failed: %s", err)
        }
    
        if err = smContext.PutPDRtoPFCPSession(destUPF.NodeID, node.UpLinkTunnel.PDR); err != nil {
            logger.CtxLog.Errorln("Put PDR Error: ", err)
            return err
        }
    
        if teid, err := destUPF.GenerateTEID(); err != nil {
            logger.CtxLog.Errorf("Generate uplink TEID fail: %s", err)
            return err
        } else {
            node.UpLinkTunnel.TEID = teid
        }

TEID的唯一性生成逻辑见smf\context\upf.go中的GenerateTEID函数及idgenerator\id_generator.go中的NewGenerator函数和Allocate函数。

    
    
    func (upf *UPF) GenerateTEID() (uint32, error) {
        if upf.UPFStatus != AssociatedSetUpSuccess {
            err := fmt.Errorf("this upf not associate with smf")
            return 0, err
        }
    
        var id uint32
        if tmpID, err := upf.teidGenerator.Allocate(); err != nil {
            return 0, err
        } else {
            id = uint32(tmpID)
        }
    
        return id, nil
    }
    
    //free5gc/idgenerator/id_generator.go
    func (idGenerator *IDGenerator) Allocate() (id int64, err error) {
      idGenerator.lock.Lock()
      defer idGenerator.lock.Unlock()
      offsetBegin := idGenerator.offset
      for {
        if _, ok := idGenerator.usedMap[idGenerator.offset]; ok {
          idGenerator.updateOffset()
    if idGenerator.offset == offsetBegin {
            err = errors.New("No available value range to allocate id")
            return
          }
        } else {
          break
        }
      }
      idGenerator.usedMap[idGenerator.offset] = true
      id = idGenerator.offset + idGenerator.minValue
      idGenerator.updateOffset()
      return
    }
    
    func (idGenerator *IDGenerator) updateOffset() {
    	idGenerator.offset++
    	idGenerator.offset = idGenerator.offset % idGenerator.valueRange
    }
    

### 3.2 SMF安全需求分析

3.2.1 SMF检查UP安全策略的安全功能要求

 **需求描述**

SMF应验证从目标NG-eNB/gNB接收的UE的UP安全策略与SMF本地存储的UE的UP安全策略相同。如果不匹配，SMF应将其本地存储的UE的对应PDU会话的UP安全策略发送到目标gNB。如果SMF包括该UP安全策略信息，则该UP安全策略信息被传递到路径切换消息中的目标NG-eNB/gNB。SMF应记录此事件的能力，并可采取其他措施，例如发出警报。

威胁参考：如《3GPP TR 33.926》第J.2.2.4条所述，SMF需要验证从NG-eNB/gNB接收的UP安全策略是否与存储在SMF本地的相同。如果SMF未能检查，上行通信的安全性可能会降低。例如，如果从NG-eNB/gNB接收的UP安全策略指示没有安全保护，而本地策略要求相反的安全保护，并且SMF在没有验证的情况下使用接收的UP安全策略，则用户平面数据将不受保护。

 **输入条件**

1.测试者向被测SMF发送Nsmf_PDUSession_SMContextUpdate Request消息。请求消息中包含的UE
UP安全策略与在被测SMF上预先配置的策略不同。

2.测试者捕获SMF发送的Nsmf_PDUSession_SMContextUpdate Response消息。

 **输出结果**

预先配置的UE安全策略包含在捕获的响应消息中的“n2SmInfo”IE中。

HandlePathSwitchRequestTransfer会对ctx变量进行处理。

 **条目分析**

捕获到AMF向SMF网元发送的UpdateSmContext请求。

![1640656675_61ca6f23173141af6bf6f.png!small?1640656675609](https://image.3001.net/images/20211228/1640656675_61ca6f23173141af6bf6f.png!small?1640656675609)

该请求的body由Bondary分割成多个字段。

![1640656688_61ca6f309cb38d86af399.png!small?1640656689012](https://image.3001.net/images/20211228/1640656688_61ca6f309cb38d86af399.png!small?1640656689012)

字段中n2SmInfoType的值为PATH_SWITCH_REQ，该条目的处理流程包含在此类型的消息中。

![1640656700_61ca6f3ca6ba13b15f894.png!small?1640656701001](https://image.3001.net/images/20211228/1640656700_61ca6f3ca6ba13b15f894.png!small?1640656701001)

最终可以看到AMF向RAN返回的NGAP消息。

![1640656713_61ca6f4951a5152bc1ba7.png!small?1640656713743](https://image.3001.net/images/20211228/1640656713_61ca6f4951a5152bc1ba7.png!small?1640656713743)

查看smf/pdusession/routers.go中的路由，/sm-contexts/:smContextRef/modify报文由HTTPUpdateSmContext函数进行处理，报文请求方式为POST。

    
    
    {
    		"UpdateSmContext",
    		strings.ToUpper("Post"),
    		"/sm-contexts/:smContextRef/modify",
    		HTTPUpdateSmContext,
    	},

HTTPUpdateSMContext首先会按照“;”作为分隔符，对Content-Type中的字段进行分割，并获取smContextRef的值。

    
    
    //free5gc-main\NFs\smf\smf-main\pdusession\api_individual_sm_context.go
    // HTTPUpdateSmContext - Update SM Context
    func HTTPUpdateSmContext(c *gin.Context) {
    	logger.PduSessLog.Info("Recieve Update SM Context Request")
    	var request models.UpdateSmContextRequest//
    	request.JsonData = new(models.SmContextUpdateData)
    	s := strings.Split(c.GetHeader("Content-Type"), ";")
    	var err error
    	switch s[0] {
    	case "application/json":
    		err = c.ShouldBindJSON(request.JsonData)
    	case "multipart/related":
    		err = c.ShouldBindWith(&request, openapi.MultipartRelatedBinding{})
    	}
    	if err != nil {
    		log.Print(err)
    		return
    	}
    	req := http_wrapper.NewRequest(c.Request, request)
    	req.Params["smContextRef"] = c.Params.ByName("smContextRef")
    	smContextRef := req.Params["smContextRef"]//获取smContextRef的值
    	HTTPResponse := producer.HandlePDUSessionSMContextUpdate(
    		smContextRef, req.Body.(models.UpdateSmContextRequest))//
    
    	if HTTPResponse.Status < 300 {
    		c.Render(HTTPResponse.Status, openapi.MultipartRelatedRender{Data: HTTPResponse.Body})
    	} else {
    		c.JSON(HTTPResponse.Status, HTTPResponse.Body)
    	}
    }
    

HandlePDUSessionSMContextUpdate函数会首先对smContext进行判空，通过比较后，根据smContextUpdateData.N2SmInfoType
字段分别对消息进行不同的处理，当该字段值为N2SmInfoType_PATH_SWITCH_REQ时，将调用HandlePathSwitchRequestTransfe，对PathSwitch请求进行处理去。

    
    
    //free5gc-main\NFs\smf\smf-main\producer\pdu_session.go
    func HandlePDUSessionSMContextUpdate(smContextRef string, body models.UpdateSmContextRequest) *http_wrapper.Response {
    	// GSM State
    	// PDU Session Modification Reject(Cause Value == 43 || Cause Value != 43)/Complete
    	// PDU Session Release Command/Complete
    	logger.PduSessLog.Infoln("In HandlePDUSessionSMContextUpdate")
    	smContext := smf_context.GetSMContext(smContextRef)//HandlePDUSessionSMContextCreate中创建
    
    	if smContext == nil {//对smContext进行判空
    		logger.PduSessLog.Warnf("SMContext[%s] is not found", smContextRef)
    
    		httpResponse := &http_wrapper.Response{
    			Header: nil,
    			Status: http.StatusNotFound,
    			Body: models.UpdateSmContextErrorResponse{
    				JsonData: &models.SmContextUpdateError{
    					UpCnxState: models.UpCnxState_DEACTIVATED,
    					Error: &models.ProblemDetails{
    						Type:   "Resource Not Found",
    						Title:  "SMContext Ref is not found",
    						Status: http.StatusNotFound,
    					},
    				},
    			},
    		}
    		return httpResponse
    	}
    
    	smContext.SMLock.Lock()
    	defer smContext.SMLock.Unlock()
    
    	var sendPFCPDelete, sendPFCPModification bool
    	var response models.UpdateSmContextResponse
    	response.JsonData = new(models.SmContextUpdatedData)
    
    	smContextUpdateData := body.JsonData
    
    	if body.BinaryDataN1SmMessage != nil {
    		logger.PduSessLog.Traceln("Binary Data N1 SmMessage isn't nil!")
    		m := nas.NewMessage()
    		err := m.GsmMessageDecode(&body.BinaryDataN1SmMessage)
    		logger.PduSessLog.Traceln("[SMF] UpdateSmContextRequest N1SmMessage: ", m)
    		if err != nil {
    			logger.PduSessLog.Error(err)
    			httpResponse := &http_wrapper.Response{
    				Status: http.StatusForbidden,
    				Body: models.UpdateSmContextErrorResponse{
    					JsonData: &models.SmContextUpdateError{
    						Error: &Nsmf_PDUSession.N1SmError,
    					},
    				}, // Depends on the reason why N4 fail
    			}
    			return httpResponse
    		}
    ......
    	switch smContextUpdateData.N2SmInfoType {
    ......
    	case models.N2SmInfoType_PATH_SWITCH_REQ:
    		logger.PduSessLog.Traceln("Handle Path Switch Request")
    		if smContext.SMContextState != smf_context.Active {
    			// Wait till the state becomes Active again
    			// TODO: implement sleep wait in concurrent architecture
    			logger.PduSessLog.Warnf("SMContext[%s-%02d] should be Active, but actual %s",
    				smContext.Supi, smContext.PDUSessionID, smContext.SMContextState.String())
    		}
    		smContext.SMContextState = smf_context.ModificationPending
    		logger.CtxLog.Traceln("SMContextState Change State: ", smContext.SMContextState.String())
    
    		if err := smf_context.HandlePathSwitchRequestTransfer(body.BinaryDataN2SmInformation, smContext); err != nil {
    			logger.PduSessLog.Errorf("Handle PathSwitchRequestTransfer: %+v", err)
    		}
    
    		if n2Buf, err := smf_context.BuildPathSwitchRequestAcknowledgeTransfer(smContext); err != nil {
    			logger.PduSessLog.Errorf("Build Path Switch Transfer Error(%+v)", err)
    		} else {
    			response.BinaryDataN2SmInformation = n2Buf
    		}
    
    		response.JsonData.N2SmInfoType = models.N2SmInfoType_PATH_SWITCH_REQ_ACK
    		response.JsonData.N2SmInfo = &models.RefToBinaryData{
    			ContentId: "PATH_SWITCH_REQ_ACK",
    		}
    
    		smContext.PendingUPF = make(smf_context.PendingUPF)
    		for _, dataPath := range tunnel.DataPathPool {
    			if dataPath.Activated {
    				ANUPF := dataPath.FirstDPNode
    				DLPDR := ANUPF.DownLinkTunnel.PDR
    
    				pdrList = append(pdrList, DLPDR)
    				farList = append(farList, DLPDR.FAR)
    
    				if _, exist := smContext.PendingUPF[ANUPF.GetNodeIP()]; !exist {
    					smContext.PendingUPF[ANUPF.GetNodeIP()] = true
    				}
    			}
    		}
    
    		sendPFCPModification = true
    		smContext.SMContextState = smf_context.PFCPModification
    		logger.CtxLog.Traceln("SMContextState Change State: ", smContext.SMContextState.String())
    	switch smContextUpdateData.HoState {
    ......
    	}
        switch smContextUpdateData.Cause {
    ......
        }
        switch smContext.SMContextState {
    ......
    }
            return httpResponse
    }

HandlePathSwitchRequestTransfer验证 PathSwitchRequest 中的 UpSecurity设置是否与本地存储的
SMF 相同。如果rcvUpSecurity.UpIntegr != ctx.UpSecurity.UpIntegr
或者rcvUpSecurity.UpConfid !=
ctx.UpSecurity.UpConfid，该函数会将布尔值UpSecurityFromPathSwitchRequestSameAsLocalStored设置为false。

    
    
    func HandlePathSwitchRequestTransfer(b []byte, ctx *SMContext) error {
    	pathSwitchRequestTransfer := ngapType.PathSwitchRequestTransfer{}
    
    	if err := aper.UnmarshalWithParams(b, &pathSwitchRequestTransfer, "valueExt"); err != nil {
    		return err
    	}
    
    	if pathSwitchRequestTransfer.DLNGUUPTNLInformation.Present != ngapType.UPTransportLayerInformationPresentGTPTunnel {
    		return errors.New("pathSwitchRequestTransfer.DLNGUUPTNLInformation.Present")
    	}
    
    	gtpTunnel := pathSwitchRequestTransfer.DLNGUUPTNLInformation.GTPTunnel
    
    	teid := binary.BigEndian.Uint32(gtpTunnel.GTPTEID.Value)
    
    	ctx.Tunnel.ANInformation.IPAddress = gtpTunnel.TransportLayerAddress.Value.Bytes
    	ctx.Tunnel.ANInformation.TEID = teid
    
    	for _, dataPath := range ctx.Tunnel.DataPathPool {
    		if dataPath.Activated {
    			ANUPF := dataPath.FirstDPNode
    			DLPDR := ANUPF.DownLinkTunnel.PDR
    
    			DLPDR.FAR.ForwardingParameters.OuterHeaderCreation = new(pfcpType.OuterHeaderCreation)
    			dlOuterHeaderCreation := DLPDR.FAR.ForwardingParameters.OuterHeaderCreation
    			dlOuterHeaderCreation.OuterHeaderCreationDescription = pfcpType.OuterHeaderCreationGtpUUdpIpv4
    			dlOuterHeaderCreation.Teid = teid
    			dlOuterHeaderCreation.Ipv4Address = ctx.Tunnel.ANInformation.IPAddress.To4()
    			DLPDR.FAR.State = RULE_UPDATE
    		}
    	}
    
    	ctx.UpSecurityFromPathSwitchRequestSameAsLocalStored = true
    
    	// Verify whether UP security in PathSwitchRequest same as SMF locally stored or not TS 33.501 6.6.1
    	if ctx.UpSecurity != nil && pathSwitchRequestTransfer.UserPlaneSecurityInformation != nil {
    		rcvSecurityIndication := pathSwitchRequestTransfer.UserPlaneSecurityInformation.SecurityIndication
    		rcvUpSecurity := new(models.UpSecurity)
    		switch rcvSecurityIndication.IntegrityProtectionIndication.Value {
    		case ngapType.IntegrityProtectionIndicationPresentRequired:
    			rcvUpSecurity.UpIntegr = models.UpIntegrity_REQUIRED
    		case ngapType.IntegrityProtectionIndicationPresentPreferred:
    			rcvUpSecurity.UpIntegr = models.UpIntegrity_PREFERRED
    		case ngapType.IntegrityProtectionIndicationPresentNotNeeded:
    			rcvUpSecurity.UpIntegr = models.UpIntegrity_NOT_NEEDED
    		}
    		switch rcvSecurityIndication.ConfidentialityProtectionIndication.Value {
    		case ngapType.ConfidentialityProtectionIndicationPresentRequired:
    			rcvUpSecurity.UpConfid = models.UpConfidentiality_REQUIRED
    		case ngapType.ConfidentialityProtectionIndicationPresentPreferred:
    			rcvUpSecurity.UpConfid = models.UpConfidentiality_PREFERRED
    		case ngapType.ConfidentialityProtectionIndicationPresentNotNeeded:
    			rcvUpSecurity.UpConfid = models.UpConfidentiality_NOT_NEEDED
    		}
    
    		if rcvUpSecurity.UpIntegr != ctx.UpSecurity.UpIntegr ||
    			rcvUpSecurity.UpConfid != ctx.UpSecurity.UpConfid {
    			ctx.UpSecurityFromPathSwitchRequestSameAsLocalStored = false
    
    			// SMF shall support logging capabilities for this mismatch event TS 33.501 6.6.1
    			logger.PduSessLog.Warnf("Received UP security policy mismatch from SMF locally stored")
    		}
    	}
    
    	return nil
    }
    

随后将调用BuildPathSwitchRequestAcknowledgeTransfer，该函数将根据UpSecurityFromPathSwitchRequestSameAsLocalStored的标志位来设置SecurityIndication的值。如果该值和本地存储的不一致，将进行规范中的相应操作。

    
    
    // TS 38.413 9.3.4.9
    func BuildPathSwitchRequestAcknowledgeTransfer(ctx *SMContext) ([]byte, error) {
    	ANUPF := ctx.Tunnel.DataPathPool.GetDefaultPath().FirstDPNode
    	UpNode := ANUPF.UPF
    	teidOct := make([]byte, 4)
    	binary.BigEndian.PutUint32(teidOct, ANUPF.UpLinkTunnel.TEID)
    
    	pathSwitchRequestAcknowledgeTransfer := ngapType.PathSwitchRequestAcknowledgeTransfer{}
    
    	// UL NG-U UP TNL Information(optional) TS 38.413 9.3.2.2
    	pathSwitchRequestAcknowledgeTransfer.
    		ULNGUUPTNLInformation = new(ngapType.UPTransportLayerInformation)
    
    	ULNGUUPTNLInformation := pathSwitchRequestAcknowledgeTransfer.ULNGUUPTNLInformation
    	ULNGUUPTNLInformation.Present = ngapType.UPTransportLayerInformationPresentGTPTunnel
    	ULNGUUPTNLInformation.GTPTunnel = new(ngapType.GTPTunnel)
    
    	if n3IP, err := UpNode.N3Interfaces[0].IP(ctx.SelectedPDUSessionType); err != nil {
    		return nil, err
    	} else {
    		gtpTunnel := ULNGUUPTNLInformation.GTPTunnel
    		gtpTunnel.GTPTEID.Value = teidOct
    		gtpTunnel.TransportLayerAddress.Value = aper.BitString{
    			Bytes:     n3IP,
    			BitLength: uint64(len(n3IP) * 8),
    		}
    	}
    
    	// Received UP security policy mismatch from SMF locally stored TS 33.501 6.6.1
    	// Security Indication(optional) TS 38.413 9.3.1.27
    	if !ctx.UpSecurityFromPathSwitchRequestSameAsLocalStored {
    		pathSwitchRequestAcknowledgeTransfer.SecurityIndication = new(ngapType.SecurityIndication)
    		securityIndication := pathSwitchRequestAcknowledgeTransfer.SecurityIndication
    
    		upSecurity := ctx.UpSecurity
    		maximumDataRatePerUEForUserPlaneIntegrityProtectionForUpLink :=
    			ctx.MaximumDataRatePerUEForUserPlaneIntegrityProtectionForUpLink
    
    		switch upSecurity.UpIntegr {
    		case models.UpIntegrity_REQUIRED:
    			securityIndication.IntegrityProtectionIndication.Value =
    				ngapType.IntegrityProtectionIndicationPresentRequired
    		case models.UpIntegrity_PREFERRED:
    			securityIndication.IntegrityProtectionIndication.Value =
    				ngapType.IntegrityProtectionIndicationPresentPreferred
    		case models.UpIntegrity_NOT_NEEDED:
    			securityIndication.IntegrityProtectionIndication.Value =
    				ngapType.IntegrityProtectionIndicationPresentNotNeeded
    		}
    		switch upSecurity.UpConfid {
    		case models.UpConfidentiality_REQUIRED:
    			securityIndication.ConfidentialityProtectionIndication.Value =
    				ngapType.ConfidentialityProtectionIndicationPresentRequired
    		case models.UpConfidentiality_PREFERRED:
    			securityIndication.ConfidentialityProtectionIndication.Value =
    				ngapType.ConfidentialityProtectionIndicationPresentPreferred
    		case models.UpConfidentiality_NOT_NEEDED:
    			securityIndication.ConfidentialityProtectionIndication.Value =
    				ngapType.ConfidentialityProtectionIndicationPresentNotNeeded
    		}
    
    		// Present only when Integrity Indication within the Security Indication is set to "required" or "preferred"
    		integrityProtectionInd := securityIndication.IntegrityProtectionIndication.Value
    		if integrityProtectionInd == ngapType.IntegrityProtectionIndicationPresentRequired ||
    			integrityProtectionInd == ngapType.IntegrityProtectionIndicationPresentPreferred {
    			securityIndication.MaximumIntegrityProtectedDataRateUL = new(ngapType.MaximumIntegrityProtectedDataRate)
    			switch maximumDataRatePerUEForUserPlaneIntegrityProtectionForUpLink {
    			case models.MaxIntegrityProtectedDataRate_MAX_UE_RATE:
    				securityIndication.MaximumIntegrityProtectedDataRateUL.Value =
    					ngapType.MaximumIntegrityProtectedDataRatePresentMaximumUERate
    			case models.MaxIntegrityProtectedDataRate__64_KBPS:
    				securityIndication.MaximumIntegrityProtectedDataRateUL.Value =
    					ngapType.MaximumIntegrityProtectedDataRatePresentBitrate64kbs
    			}
    		}
    	}
    
    	if buf, err := aper.MarshalWithParams(pathSwitchRequestAcknowledgeTransfer, "valueExt"); err != nil {
    		return nil, err
    	} else {
    		return buf, nil
    	}
    }

3.2.2 UP安全策略的优先级

 **需求描述**

UDM的用户面安全策略优先于本地配置的用户面安全策略。

威胁参考：如《3GPP TR
33.926》第J.2.2.1条所述，UDM中的用户平面安全策略必须优先于SMF中本地配置的用户平面安全策略。如果SMF不符合要求，用户平面安全性可能会降低。例如，如果UDM的UP安全策略要求对用户平面数据进行加密和完整性保护，但在SMF的本地UP安全策略中未指示任何保护，并且本地UP安全策略具有优先权，则用户平面数据将通过空中发送，而无需任何保护。

 **输入条件**

1.测试者通过向SMF发送Nsmf_PDUSession_CreateSMContext Request消息来触发PDU会话建立过程。

2.被测SMF使用Nudm_SDM_Get服务从UDM检索会话管理订阅数据，其中会话管理订阅数据包括存储在UDM中的用户平面安全策略。

3.测试者捕获从被测SMF向AMF发送的Namf_Communication_N1N2MessageTransfer消息。

 **输出结果**

Namf_Communication_N1N2MessageTransfer消息中的N2SM消息中包含Security Indication
IE，与UDM中配置的安全策略一致。

 **条目分析**

首先定位到free5gc
smf项目smf\producer\pdu_session.go中的HandlePDUSessionSMContextCreate函数122-143行，首先使用GetSmData函数从UMD中获取DnnConfiguration，然后将获取到的DnnConfiguration.UpSecurity设到SMContext中。

    
    
    smDataParams := &Nudm_SubscriberDataManagement.GetSmDataParamOpts{
            Dnn:         optional.NewString(createData.Dnn),
            PlmnId:      optional.NewInterface(openapi.MarshToJsonString(smPlmnID)),
            SingleNssai: optional.NewInterface(openapi.MarshToJsonString(smContext.Snssai)),
        }
    
        SubscriberDataManagementClient := smf_context.SMF_Self().SubscriberDataManagementClient
    
        if sessSubData, rsp, err := SubscriberDataManagementClient.
            SessionManagementSubscriptionDataRetrievalApi.
            GetSmData(context.Background(), smContext.Supi, smDataParams); err != nil {
            logger.PduSessLog.Errorln("Get SessionManagementSubscriptionData error:", err)
        } else {
            defer func() {
                if rspCloseErr := rsp.Body.Close(); rspCloseErr != nil {
                    logger.PduSessLog.Errorf("GetSmData response body cannot close: %+v", rspCloseErr)
                }
            }()
            if len(sessSubData) > 0 {
                smContext.DnnConfiguration = sessSubData[0].DnnConfigurations[smContext.Dnn]
                // UP Security info present in session management subscription data
                if smContext.DnnConfiguration.UpSecurity != nil {
                    smContext.UpSecurity = smContext.DnnConfiguration.UpSecurity
                }
            } else {
                logger.PduSessLog.Errorln("SessionManagementSubscriptionData from UDM is nil")
            }
        }

定位到smf\pfcp\handler\handler.go中的HandlePfcpSessionEstablishmentResponse函数。

    
    
    func HandlePfcpSessionEstablishmentResponse(msg *pfcpUdp.Message) {
        rsp := msg.PfcpMessage.Body.(pfcp.PFCPSessionEstablishmentResponse)
        logger.PfcpLog.Infoln("In HandlePfcpSessionEstablishmentResponse")
    
        SEID := msg.PfcpMessage.Header.SEID
        smContext := smf_context.GetSMContextBySEID(SEID)
    
        if rsp.UPFSEID != nil {
            NodeIDtoIP := rsp.NodeID.ResolveNodeIdToIp().String()
            pfcpSessionCtx := smContext.PFCPContext[NodeIDtoIP]
            pfcpSessionCtx.RemoteSEID = rsp.UPFSEID.Seid
        }
    
        ANUPF := smContext.Tunnel.DataPathPool.GetDefaultPath().FirstDPNode
        if rsp.Cause.CauseValue == pfcpType.CauseRequestAccepted &&
            ANUPF.UPF.NodeID.ResolveNodeIdToIp().Equal(rsp.NodeID.ResolveNodeIdToIp()) {
            n1n2Request := models.N1N2MessageTransferRequest{}
    
            if smNasBuf, err := smf_context.BuildGSMPDUSessionEstablishmentAccept(smContext); err != nil {
                logger.PduSessLog.Errorf("Build GSM PDUSessionEstablishmentAccept failed: %s", err)
            } else {
                n1n2Request.BinaryDataN1Message = smNasBuf
            }
            if n2Pdu, err := smf_context.BuildPDUSessionResourceSetupRequestTransfer(smContext); err != nil {
                logger.PduSessLog.Errorf("Build PDUSessionResourceSetupRequestTransfer failed: %s", err)
            } else {
                n1n2Request.BinaryDataN2Information = n2Pdu
            }
    
            n1n2Request.JsonData = &models.N1N2MessageTransferReqData{
                PduSessionId: smContext.PDUSessionID,
                N1MessageContainer: &models.N1MessageContainer{
                    N1MessageClass:   "SM",
                    N1MessageContent: &models.RefToBinaryData{ContentId: "GSM_NAS"},
                },
                N2InfoContainer: &models.N2InfoContainer{
                    N2InformationClass: models.N2InformationClass_SM,
                    SmInfo: &models.N2SmInformation{
                        PduSessionId: smContext.PDUSessionID,
                        N2InfoContent: &models.N2InfoContent{
                            NgapIeType: models.NgapIeType_PDU_RES_SETUP_REQ,
                            NgapData: &models.RefToBinaryData{
                                ContentId: "N2SmInformation",
                            },
                        },
                        SNssai: smContext.Snssai,
                    },
                },
            }
    
            rspData, _, err := smContext.
                CommunicationClient.
                N1N2MessageCollectionDocumentApi.
                N1N2MessageTransfer(context.Background(), smContext.Supi, n1n2Request)
            smContext.SMContextState = smf_context.Active
            logger.CtxLog.Traceln("SMContextState Change State: ", smContext.SMContextState.String())
            if err != nil {
                logger.PfcpLog.Warnf("Send N1N2Transfer failed")
            }
            if rspData.Cause == models.N1N2MessageTransferCause_N1_MSG_NOT_TRANSFERRED {
                logger.PfcpLog.Warnf("%v", rspData.Cause)
            }
        }
    
        if smf_context.SMF_Self().ULCLSupport && smContext.BPManager != nil {
            if smContext.BPManager.BPStatus == smf_context.AddingPSA {
                logger.PfcpLog.Infoln("Keep Adding PSAndULCL")
                producer.AddPDUSessionAnchorAndULCL(smContext, *rsp.NodeID)
                smContext.BPManager.BPStatus = smf_context.AddingPSA
            }
        }
    }

定位到
smf\context\ngap_build.go中的BuildPDUSessionResourceSetupRequestTransfer函数，实现了在Namf_Communication_N1N2MessageTransfer消息中设定UP安全策略，具体需求参照标准《3GPP
TS 23.501》 5.10.3章节。

    
    
    // Security Indication to NG-RAN (optional) TS 38.413 9.3.1.27
        // Only over 3GPP access TS 23.501 5.10.3
        if ctx.AnType == models.AccessType__3_GPP_ACCESS && ctx.UpSecurity != nil {
            upSecurity := ctx.UpSecurity
            maximumDataRatePerUEForUserPlaneIntegrityProtectionForUpLink :=
                ctx.MaximumDataRatePerUEForUserPlaneIntegrityProtectionForUpLink
    
            ie = ngapType.PDUSessionResourceSetupRequestTransferIEs{}
            ie.Id.Value = ngapType.ProtocolIEIDSecurityIndication
            ie.Criticality.Value = ngapType.CriticalityPresentReject
    
            securityIndication := new(ngapType.SecurityIndication)
    
            switch upSecurity.UpIntegr {
            case models.UpIntegrity_REQUIRED:
                securityIndication.IntegrityProtectionIndication.Value =
                    ngapType.IntegrityProtectionIndicationPresentRequired
            case models.UpIntegrity_PREFERRED:
                securityIndication.IntegrityProtectionIndication.Value =
                    ngapType.IntegrityProtectionIndicationPresentPreferred
            case models.UpIntegrity_NOT_NEEDED:
                securityIndication.IntegrityProtectionIndication.Value =
                    ngapType.IntegrityProtectionIndicationPresentNotNeeded
            }
            switch upSecurity.UpConfid {
            case models.UpConfidentiality_REQUIRED:
                securityIndication.ConfidentialityProtectionIndication.Value =
                    ngapType.ConfidentialityProtectionIndicationPresentRequired
            case models.UpConfidentiality_PREFERRED:
                securityIndication.ConfidentialityProtectionIndication.Value =
                    ngapType.ConfidentialityProtectionIndicationPresentPreferred
            case models.UpConfidentiality_NOT_NEEDED:
                securityIndication.ConfidentialityProtectionIndication.Value =
                    ngapType.ConfidentialityProtectionIndicationPresentNotNeeded
            }
    
            // Present only when Integrity Indication within the Security Indication is set to "required" or "preferred"
            integrityProtectionInd := securityIndication.IntegrityProtectionIndication.Value
            if integrityProtectionInd == ngapType.IntegrityProtectionIndicationPresentRequired ||
                integrityProtectionInd == ngapType.IntegrityProtectionIndicationPresentPreferred {
                securityIndication.MaximumIntegrityProtectedDataRateUL = new(ngapType.MaximumIntegrityProtectedDataRate)
                switch maximumDataRatePerUEForUserPlaneIntegrityProtectionForUpLink {
                case models.MaxIntegrityProtectedDataRate_MAX_UE_RATE:
                    securityIndication.MaximumIntegrityProtectedDataRateUL.Value =
                        ngapType.MaximumIntegrityProtectedDataRatePresentMaximumUERate
                case models.MaxIntegrityProtectedDataRate__64_KBPS:
                    securityIndication.MaximumIntegrityProtectedDataRateUL.Value =
                        ngapType.MaximumIntegrityProtectedDataRatePresentBitrate64kbs
                }
            }
    
            ie.Value = ngapType.PDUSessionResourceSetupRequestTransferIEsValue{
                Present:            ngapType.PDUSessionResourceSetupRequestTransferIEsPresentSecurityIndication,
                SecurityIndication: securityIndication,
            }
            resourceSetupRequestTransfer.ProtocolIEs.List = append(resourceSetupRequestTransfer.ProtocolIEs.List, ie)
        }
    
        if buf, err := aper.MarshalWithParams(resourceSetupRequestTransfer, "valueExt"); err != nil {
            return nil, fmt.Errorf("encode resourceSetupRequestTransfer failed: %s", err)
        } else {
            return buf, nil
        }
    }
    
            // Present only when Integrity Indication within the Security Indication is set to "required" or "preferred"
            integrityProtectionInd := securityIndication.IntegrityProtectionIndication.Value
            if integrityProtectionInd == ngapType.IntegrityProtectionIndicationPresentRequired ||
                integrityProtectionInd == ngapType.IntegrityProtectionIndicationPresentPreferred {
                securityIndication.MaximumIntegrityProtectedDataRateUL = new(ngapType.MaximumIntegrityProtectedDataRate)
                switch maximumDataRatePerUEForUserPlaneIntegrityProtectionForUpLink {
                case models.MaxIntegrityProtectedDataRate_MAX_UE_RATE:
                    securityIndication.MaximumIntegrityProtectedDataRateUL.Value =
                        ngapType.MaximumIntegrityProtectedDataRatePresentMaximumUERate
                case models.MaxIntegrityProtectedDataRate__64_KBPS:
                    securityIndication.MaximumIntegrityProtectedDataRateUL.Value =
                        ngapType.MaximumIntegrityProtectedDataRatePresentBitrate64kbs
                }
            }

可以根据此处代码得出关于UP的安全策略设定是从ctx参数中取得，ctx作为BuildPDUSessionResourceSetupRequestTransfer的入参，代表PDU会话流程中的SMContext，而在创建SMContext时我们根据上面的代码分析得知upsecurity是从UDM中检索而来。

## 四、总结

本文借助free5gc+UERANSIM模拟5G网络环境，通过抓包和源码分析的方式介绍了《3GPP TS 33.513》和《3GPP TS
33.515》标准中的相关安全需求。希望能帮助到对5G知识感兴趣的读者，不足之处请多多指正。

# 转载声明

如需转载，请注明出处及作者，并给出原文链接地址。  
参考资料

  * 沉烽网络安全实验室：《free5gc+UERANSIM模拟5G网络环境搭建及基本使用》

<https://www.freebuf.com/articles/wireless/268397.html>

  * 沉烽网络安全实验室：《基于UERANSIM+free5gc 5G模拟环境的5G_AKA协议解析》

<https://www.freebuf.com/articles/wireless/273792.html>

  * 沉烽网络安全实验室：《基于free5gc+UERANSIM的5G注册管理流程及安全服务分析 上》

<https://www.freebuf.com/articles/network/290436.html>

  * 沉烽网络安全实验室：《基于free5gc+UERANSIM的5G注册管理流程及安全服务分析 下》

<https://www.freebuf.com/articles/network/305734.html>

  * 张忠琳：【5G核心网】free5GC Path Switch Request源码分析

<https://blog.csdn.net/zhonglinzhang/article/details/109809903>

  * 3GPP TS 33.515
  * 3GPP TS 33.513
  * 3GPP TS 23.501
  * 3GPP TR 33.926  

 **作者：** **中兴沉烽实验室_wcs、中兴沉烽实验室_lyc**

