## 一、前言

随着5G的快速建设，5G的安全问题受到越来越多的关注。本文首先借助free5gc和UERANSIM这两个5G开源项目分析了《3GPP TS
23.502》标准中定义的用户注册管理流程，并对《3GPP TS
33.501》5G系统安全结构和流程标准中定义的安全服务进行了流量、代码分析，以帮助安全研究人员增进对5G核心网安全，从而进行安全分析与测试。

本系列分为上下两个部分，上半部分主要介绍《3GPP TS
23.502》中定义的5G用户注册管理的概念，并结合模拟环境对用户注册管理进行分析。下半部分则基于模拟环境对《3GPP TS
33.501》中定义的相关安全服务进行详细分析。

本篇为该系列上半部分。

## 二、用户注册管理介绍

用户注册管理是用于 UE / 用户和网络之间进行注册和注销，在网络建立上下文的过程，一个 UE / 用户想要获取网络提供的业务必须先向网络进行注册。

注册类型包含以下四种：

> 初次注册（initial registration）
>
> 位置变更引起的网络重新注册（Mobility Registration Update）
>
> 周期性注册（Periodic Registration Update）
>
> 紧急业务引发的注册（Emergency Registration）

注册管理涉及到的应用场景如下：

> UE初次注册网络
>
> UE周期性注册网络
>
> UE位置变更引起的网络重新注册
>
> 紧急业务引发的网络注册

## 三、模拟环境介绍

本节简单介绍了UERANSIM+free5gc环境，用户可以通过使用arp、ifconfig、docker inspect及网桥brctl
相关命令，来收集容器IP及Mac地址相关信息，绘制的组网示意图如下：![1632885091_6153d9632a94d8d919f75.png!small?1632885078984](https://image.3001.net/images/20210929/1632885091_6153d9632a94d8d919f75.png!small?1632885078984)

如上图所示：环境基于ubuntu 20.04 VMware虚机部署，5gc网元分别部署在虚机的docker容器中。5gc各模拟网元与模拟RAN
通过虚拟网桥进行数据交换。物理机上的VMware
虚拟网卡作为DN(互联网节点)通过虚拟网桥与容器中的UPF对接。详细的搭建方法可以参考沉烽网络安全实验室的文章《free5gc+UERANSIM模拟5G网络环境搭建及基本使用》
。

## 四、5G注册管理流程分析

参考3GPP TS 23.502
V16.7.0，其协议的流程如下图所示。![1632885118_6153d97e4a9abd9516f9a.png!small?1632885106964](https://image.3001.net/images/20210929/1632885118_6153d97e4a9abd9516f9a.png!small?1632885106964)

下文将基于UERANSIM+free5gc 模拟环境的报文、项目代码、协议标准三位一体的对该注册管理流程进行分析。

### 4.1 UE发送注册请求

UE发送注册请求(Registration
Request)给RAN侧，请求消息中包含了用户的标识(SUPI或SUCI或GUTI)，还包含了本次注册的注册类型，UE的能力等。

 **协议流程的位置：**

对应流程图中step1

### 4.2 AMF选择

RAN侧收到注册请求后开始做AMF的选择(AMF
Selection)，RAN将根据GUTI或者RAT+NSSAI选择一个AMF，如果选择不到，就选择默认的AMF。

 **协议流程的位置：**

对应流程图中step2

### 4.3 RAN侧向New AMF发送注册请求

RAN向New AMF发送注册请求Registration Request(这里是根据GUTI来选择AMF的)。

 **协议流程的位置：**

对应流程图中step3

**报文捕获：**![1632885140_6153d994de6e8a637e6fd.png!small?1632885128519](https://image.3001.net/images/20210929/1632885140_6153d994de6e8a637e6fd.png!small?1632885128519)

### 4.4 New AMF会向Old AMF获取UE的上下文信息

由于核心网是不认识GUTI的，所以New AMF会向Old AMF获取UE的上下文信息(SUPI号码)。

 **协议流程的位置：**

对应流程图中step4，step5

 **代码实现：**

定位到free5gc amf项目/amf/ngap/handler.go中的HandleInitialUEMessage函数

    
    
    func HandleInitialUEMessage(ran *context.AmfRan, message *ngapType.NGAPPDU) {  
    amfSelf := context.AMF_Self()  
    ​  
    var rANUENGAPID *ngapType.RANUENGAPID  
    var nASPDU *ngapType.NASPDU  
    var userLocationInformation *ngapType.UserLocationInformation  
    var rRCEstablishmentCause *ngapType.RRCEstablishmentCause  
    var fiveGSTMSI *ngapType.FiveGSTMSI  
    // var aMFSetID *ngapType.AMFSetID  
    var uEContextRequest *ngapType.UEContextRequest  
    // var allowedNSSAI *ngapType.AllowedNSSAI  
    ​  
    var iesCriticalityDiagnostics ngapType.CriticalityDiagnosticsIEList  
    ​

请求IE包括：

> id-RAN- UE-NGAP-ID
>
> id-NAS-PDU
>
> id-UserLocationInformation
>
> id-RRCEStablishmentCause
>
> id-UEContextRequest
>
> 接着由于UERANSIM+free5gc模拟环境属于未部署UDSF场景，New AMF会向Old AMF获取UE的上下文信息，代码实现如下：
    
    
    if ranUe == nil {  
    var err error  
    ranUe, err = ran.NewRanUe(rANUENGAPID.Value)  
    if err != nil {  
    ran.Log.Errorf("NewRanUe Error: %+v", err)  
    }  
    ran.Log.Debugf("New RanUe [RanUeNgapID: %d]", ranUe.RanUeNgapId)  
    ​  
    if fiveGSTMSI != nil {  
    ranUe.Log.Debug("Receive 5G-S-TMSI")  
    ​  
    servedGuami := amfSelf.ServedGuamiList[0]  
    ​  
    // <5G-S-TMSI> := <AMF Set ID><AMF Pointer><5G-TMSI>  
    // GUAMI := <MCC><MNC><AMF Region ID><AMF Set ID><AMF Pointer>  
    // 5G-GUTI := <GUAMI><5G-TMSI>  
    tmpReginID, _, _ := ngapConvert.AmfIdToNgap(servedGuami.AmfId)  
    amfID := ngapConvert.AmfIdToModels(tmpReginID, fiveGSTMSI.AMFSetID.Value, fiveGSTMSI.AMFPointer.Value)  
    ​  
    tmsi := hex.EncodeToString(fiveGSTMSI.FiveGTMSI.Value)  
    ​  
    guti := servedGuami.PlmnId.Mcc + servedGuami.PlmnId.Mnc + amfID + tmsi  
    ​  
    // 如果自上次注册请求过程以来服务AMF已更改，则调用Namf_Communication_UEContextTransfer  
    // Described in TS 23.502 4.2.2.2.2 step 4 (without UDSF deployment)  
    if amfUe, ok := amfSelf.AmfUeFindByGuti(guti); !ok {  
    ranUe.Log.Warnf("Unknown UE [GUTI: %s]", guti)  
    } else {  
    ranUe.Log.Tracef("find AmfUe [GUTI: %s]", guti)  
    ​  
    if amfUe.CmConnect(ran.AnType) {  
    ranUe.Log.Debug("Implicit Deregistration")  
    ranUe.Log.Tracef("RanUeNgapID[%d]", amfUe.RanUe[ran.AnType].RanUeNgapId)  
    amfUe.DetachRanUe(ran.AnType)  
    }  
    // TODO: stop Implicit Deregistration timer  
    ranUe.Log.Debugf("AmfUe Attach RanUe [RanUeNgapID: %d]", ranUe.RanUeNgapId)  
    amfUe.AttachRanUe(ranUe)  
    }  
    }  
    }

### 4.5 AMF向UE来获取身份信息

如果UE的上下文信息获取失败的话，NEW AMF只能向UE来获取身份信息。NEW AMF向UE发送Identity Request。UE向NEW
AMF返回Identity Response，发送SUPI或SUCI给NEW AMF。

 **协议流程的位置：**

对应流程图中step6，step7

**报文捕获：**![1632885183_6153d9bf55978727876aa.png!small?1632885171424](https://image.3001.net/images/20210929/1632885183_6153d9bf55978727876aa.png!small?1632885171424)

 **代码实现：**

定位到free5gc amf项目/amf/ngap/handler.go中的AuthenticationProcedure函数

    
    
    func AuthenticationProcedure(ue *context.AmfUe, accessType models.AccessType) (bool, error) {  
    ue.GmmLog.Info("Authentication procedure")  
    ​  
    // 判断ue有没有SUCI或SUPI  
    if IdentityVerification(ue) {  
    ue.GmmLog.Debugln("UE has SUCI / SUPI")  
    if ue.SecurityContextIsValid() {  
    ue.GmmLog.Debugln("UE has a valid security context - skip the authentication procedure")  
    return true, nil  
    }  
    } else {  
    // 如果没有，amf向ue发送identity request消息，获取SUCI  
    gmm_message.SendIdentityRequest(ue.RanUe[accessType], nasMessage.MobileIdentity5GSTypeSuci)  
    return false, nil  
    }

### 4.6 AUSF Selection

NEW AMF基于获取的SUPI或SUCI信息来选择一个AUSF，为用户执行接入认证。

 **协议流程的位置：**

对应流程图中step8

**报文捕获：**![1632885201_6153d9d180148bd3f3149.png!small?1632885189364](https://image.3001.net/images/20210929/1632885201_6153d9d180148bd3f3149.png!small?1632885189364)

代码实现：

定位到free5gc amf项目/amf/ngap/handler.go中AuthenticationProcedure函数

    
    
    // 基于SUCI来选择AUSF网元  
    param := Nnrf_NFDiscovery.SearchNFInstancesParamOpts{}  
    resp, err := consumer.SendSearchNFInstances(amfSelf.NrfUri, models.NfType_AUSF, models.NfType_AMF, &ampparam)  
    if err != nil {  
    ue.GmmLog.Error("AMF can not select an AUSF by NRF")  
    return false, err  
    }

### 4.7 执行鉴权

开始执行鉴权流程(Authentication
Security)，AUSF向UDM发起鉴权，获取鉴权向量，完成鉴权流程。详细的5G-AKA鉴权流程分析见文章《基于UERANSIM+free5gc
5G模拟环境的5G_AKA协议解析》

 **协议流程的位置：**

对应流程图中step9

**报文捕获：**![1632885237_6153d9f5703c580512ce3.png!small?1632885224889](https://image.3001.net/images/20210929/1632885237_6153d9f5703c580512ce3.png!small?1632885224889)

### 4.8 New AMF通知Old AMF，UE在New AMF注册完成

New AMF通知Old AMF，UE在New AMF注册完成。

 **协议流程的位置：**

对应流程图中step10

 **代码实现：**

定位到free5gc amf项目/amf/gmm/handler.go中的HandleInitialRegistration函数

    
    
    if ue.ServingAmfChanged {  
    //如果AMF发生了变化，New AMF会通知Old AMF，UE在New AMF注册已完成。  
    req := models.UeRegStatusUpdateReqData{  
    TransferStatus: models.UeContextTransferStatus_TRANSFERRED,  
    }  
      
    regStatusTransferComplete, problemDetails, err := consumer.RegistrationStatusUpdate(ue, req)  
    if problemDetails != nil {  
    ue.GmmLog.Errorf("Registration Status Update Failed Problem[%+v]", problemDetails)  
    } else if err != nil {  
    ue.GmmLog.Errorf("Registration Status Update Error[%+v]", err)  
    } else {  
    if regStatusTransferComplete {  
    ue.GmmLog.Infof("Registration Status Transfer complete")  
    }  
    }  
    }

### 4.9 UDM Selection

鉴权流程结束后，AMF触发UDM选择。其中NRF向AMF返回报文

 **协议流程的位置：**

对应流程图中step13

**报文捕获：**![1632885255_6153da07099cbce729f91.png!small?1632885242634](https://image.3001.net/images/20210929/1632885255_6153da07099cbce729f91.png!small?1632885242634)

 **代码实现：**

定位到free5gc amf项目/amf/gmm/handler.go中的HandleInitialRegistration函数

    
    
    if ue.ServingAmfChanged || ue.State[models.AccessType_NON_3_GPP_ACCESS].Is(context.Registered) ||  
    !ue.ContextValid {  
    if err := communicateWithUDM(ue, anType); err != nil {  
    return err  
    }  
    }

继续定位到free5gc amf项目/amf/gmm/handler.go中的communicateWithUDM函数

    
    
    func communicateWithUDM(ue *context.AmfUe, accessType models.AccessType) error {  
    ue.GmmLog.Debugln("communicateWithUDM")  
    amfSelf := context.AMF_Self()  
    ​  
    // UDM selection described in TS 23.501 6.3.8  
    // TODO: consider udm group id, Routing ID part of SUCI, GPSI or External Group ID (e.g., by the NEF)  
    param := Nnrf_NFDiscovery.SearchNFInstancesParamOpts{  
    Supi: optional.NewString(ue.Supi),  
    }  
    //基于SUPI来选择UDM  
    resp, err := consumer.SendSearchNFInstances(amfSelf.NrfUri, models.NfType_UDM, models.NfType_AMF, &ampparam)  
    if err != nil {  
    return fmt.Errorf("AMF can not select an UDM by NRF")  
    }  
    ​  
    var uecmUri, sdmUri string  
    for _, nfProfile := range resp.NfInstances {  
    ue.UdmId = nfProfile.NfInstanceId  
    uecmUri = util.SearchNFServiceUri(nfProfile, models.ServiceName_NUDM_UECM, models.NfServiceStatus_REGISTERED)  
    sdmUri = util.SearchNFServiceUri(nfProfile, models.ServiceName_NUDM_SDM, models.NfServiceStatus_REGISTERED)  
    if uecmUri != "" && sdmUri != "" {  
    break  
    }  
    }  
    ue.NudmUECMUri = uecmUri  
    ue.NudmSDMUri = sdmUri  
    if ue.NudmUECMUri == "" || ue.NudmSDMUri == "" {  
    return fmt.Errorf("AMF can not select an UDM by NRF")  
    }

### 4.10 注册 **Nudm_UECM_registration**

AMF向UDM发起注册请求

 **协议流程的位置：**

对应流程图中step14a

**报文捕获：**![1632885271_6153da17a0809050bd255.png!small?1632885259314](https://image.3001.net/images/20210929/1632885271_6153da17a0809050bd255.png!small?1632885259314)

UDM返回201Created，注册成功。![1632885283_6153da23e378891d8108c.png!small?1632885271138](https://image.3001.net/images/20210929/1632885283_6153da23e378891d8108c.png!small?1632885271138)

 **代码实现：**

定位到free5gc amf项目/amf/gmm/handler.go中的communicateWithUDM函数

    
    
    problemDetails, err := consumer.UeCmRegistration(ue, accessType, true)  
    if problemDetails != nil {  
    ue.GmmLog.Errorf("UECM_Registration Failed Problem[%+v]", problemDetails)  
    } else if err != nil {  
    ue.GmmLog.Errorf("UECM_Registration Error[%+v]", err)  
    }

接着查看free5gc amf项目/amf/consumer/ue_context_management.go中UeCmRegistration函数。

    
    
    func UeCmRegistration(ue *amf_context.AmfUe, accessType models.AccessType, initialRegistrationInd bool) (
    	*models.ProblemDetails, error) {
    	configuration := Nudm_UEContextManagement.NewConfiguration()
    	configuration.SetBasePath(ue.NudmUECMUri)
    	client := Nudm_UEContextManagement.NewAPIClient(configuration)
    
    	amfSelf := amf_context.AMF_Self()
    
    	switch accessType {
    	case models.AccessType__3_GPP_ACCESS:
    		registrationData := models.Amf3GppAccessRegistration{
    			AmfInstanceId:          amfSelf.NfId,
    			InitialRegistrationInd: initialRegistrationInd,
    			Guami:                  &amfSelf.ServedGuamiList[0],
    			RatType:                ue.RatType,
    			// TODO: not support Homogenous Support of IMS Voice over PS Sessions this stage
    			ImsVoPs: models.ImsVoPs_HOMOGENEOUS_NON_SUPPORT,
    		}
    
    		_, httpResp, localErr := client.AMFRegistrationFor3GPPAccessApi.Registration(context.Background(),
    			ue.Supi, registrationData)
    		if localErr == nil {
                //返回注册成功
    			ue.UeCmRegistered = true
    			return nil, nil
    		} else if httpResp != nil {
    			if httpResp.Status != localErr.Error() {
    				return nil, localErr
    			}
    			problem := localErr.(openapi.GenericOpenAPIError).Model().(models.ProblemDetails)
    			return &problem, nil
    		} else {
    			return nil, openapi.ReportError("server no response")
    		}
    	case models.AccessType_NON_3_GPP_ACCESS:
            //下面是针对非3gpp场景
    		registrationData := models.AmfNon3GppAccessRegistration{
    			AmfInstanceId: amfSelf.NfId,
    			Guami:         &amfSelf.ServedGuamiList[0],
    			RatType:       ue.RatType,
    		}
    
    		_, httpResp, localErr :=
    			client.AMFRegistrationForNon3GPPAccessApi.Register(context.Background(), ue.Supi, registrationData)
    		if localErr == nil {
    			ue.UeCmRegistered = true
    			return nil, nil
    		} else if httpResp != nil {
    			if httpResp.Status != localErr.Error() {
    				return nil, localErr
    			}
    			problem := localErr.(openapi.GenericOpenAPIError).Model().(models.ProblemDetails)
    			return &problem, nil
    		} else {
    			return nil, openapi.ReportError("server no response")
    		}
    	}
    
    	return nil, nil
    }

### 4.11 获取 **Nudm_SDM_Get**

AMF向UDM获取am-data数据、smf-select-data数据和ue-context-in-smf-data数据。

 **协议流程的位置：**

对应流程图中step14b

 **报文捕获：**

获取am-data数据![1632885294_6153da2ed2c219dfb1f3b.png!small?1632885282055](https://image.3001.net/images/20210929/1632885294_6153da2ed2c219dfb1f3b.png!small?1632885282055)

返回200
OK![1632885303_6153da3742c884f9bc989.png!small?1632885290691](https://image.3001.net/images/20210929/1632885303_6153da3742c884f9bc989.png!small?1632885290691)

获取smf-select-data数据

![1632885311_6153da3f31d5b7de96099.png!small?1632885298401](https://image.3001.net/images/20210929/1632885311_6153da3f31d5b7de96099.png!small?1632885298401)

返回200
ok![1632885319_6153da474d6cb5788fb91.png!small?1632885307098](https://image.3001.net/images/20210929/1632885319_6153da474d6cb5788fb91.png!small?1632885307098)

获取ue-context-in-smf-data数据![1632885324_6153da4cd862f2ffb8d4b.png!small?1632885312330](https://image.3001.net/images/20210929/1632885324_6153da4cd862f2ffb8d4b.png!small?1632885312330)

返回200
ok![1632885331_6153da533c65789cb0e62.png!small?1632885318627](https://image.3001.net/images/20210929/1632885331_6153da533c65789cb0e62.png!small?1632885318627)

 **代码实现：**

定位到free5gc amf项目/amf/gmm/handler.go中的communicateWithUDM函数

    
    
    problemDetails, err = consumer.SDMGetAmData(ue)
    	if problemDetails != nil {
    		ue.GmmLog.Errorf("SDM_Get AmData Failed Problem[%+v]", problemDetails)
    	} else if err != nil {
    		return fmt.Errorf("SDM_Get AmData Error[%+v]", err)
    	}
    
    	problemDetails, err = consumer.SDMGetSmfSelectData(ue)
    	if problemDetails != nil {
    		ue.GmmLog.Errorf("SDM_Get SmfSelectData Failed Problem[%+v]", problemDetails)
    	} else if err != nil {
    		return fmt.Errorf("SDM_Get SmfSelectData Error[%+v]", err)
    	}
    
    	problemDetails, err = consumer.SDMGetUeContextInSmfData(ue)
    	if problemDetails != nil {
    		ue.GmmLog.Errorf("SDM_Get UeContextInSmfData Failed Problem[%+v]", problemDetails)
    	} else if err != nil {
    		return fmt.Errorf("SDM_Get UeContextInSmfData Error[%+v]", err)
    	}	

### 4.12 订阅 **Nudm_SDM_Subscribe**

AMF向UDM发送订阅请求，UDM需要保存注册的AMF信息。

 **协议流程的位置：**

对应流程图中step14c

**报文捕获：**![1632885338_6153da5a932e99a137a90.png!small?1632885325918](https://image.3001.net/images/20210929/1632885338_6153da5a932e99a137a90.png!small?1632885325918)

返回201
Created，订阅成功。![1632885343_6153da5f3844da665ce0a.png!small?1632885331098](https://image.3001.net/images/20210929/1632885343_6153da5f3844da665ce0a.png!small?1632885331098)

代码实现：

定位到free5gc amf项目/amf/gmm/handler.go中的communicateWithUDM函数

    
    
    problemDetails, err = consumer.SDMSubscribe(ue)
    	if problemDetails != nil {
    		ue.GmmLog.Errorf("SDM Subscribe Failed Problem[%+v]", problemDetails)
    	} else if err != nil {
    		ue.GmmLog.Errorf("SDM Subscribe Error[%+v]", err)
    		return fmt.Errorf("SDM Subscribe Error[%+v]", err)
    	}

接着查看free5gc amf项目/amf/consumer/subscriber_data_management.go中的SDMSubscribe函数

    
    
    func SDMSubscribe(ue *amf_context.AmfUe) (problemDetails *models.ProblemDetails, err error) {
    	configuration := Nudm_SubscriberDataManagement.NewConfiguration()
    	configuration.SetBasePath(ue.NudmSDMUri)
    	client := Nudm_SubscriberDataManagement.NewAPIClient(configuration)
    
    	amfSelf := amf_context.AMF_Self()
    	sdmSubscription := models.SdmSubscription{
    		NfInstanceId: amfSelf.NfId,
    		PlmnId:       &ue.PlmnId,
    	}
    
    	resSubscription, httpResp, localErr := client.SubscriptionCreationApi.Subscribe(
    		context.Background(), ue.Supi, sdmSubscription)
    	if localErr == nil {
            //UDM向AMF返回订阅信息
    		ue.SdmSubscriptionId = resSubscription.SubscriptionId
    		return
    	} else if httpResp != nil {
    		if httpResp.Status != localErr.Error() {
    			err = localErr
    			return
    		}
    		problem := localErr.(openapi.GenericOpenAPIError).Model().(models.ProblemDetails)
    		problemDetails = &problem
    	} else {
    		err = openapi.ReportError("server no response")
    	}
    	return
    }

最后UDM向Old AMF发送注销消息，Old AMF删除MM上下文，对应step14d，step14e

### 4.13 PCF Selection

AMF触发PCF选择( **PCF selection** )

 **协议流程的位置：**

对应流程图中step15

**报文捕获：**![1632885352_6153da680ece8c0a3a578.png!small?1632885339334](https://image.3001.net/images/20210929/1632885352_6153da680ece8c0a3a578.png!small?1632885339334)

 **代码实现：**

定位到free5gc amf项目/amf/gmm/handler.go中的HandleInitialRegistration函数

    
    
    param := Nnrf_NFDiscovery.SearchNFInstancesParamOpts{
    		Supi: optional.NewString(ue.Supi),
    	}
    	for {
    		resp, err := consumer.SendSearchNFInstances(amfSelf.NrfUri, models.NfType_PCF, models.NfType_AMF, &ampparam) 
    		if err != nil {
    			ue.GmmLog.Error("AMF can not select an PCF by NRF")
    		} else {
    			// select the first PCF, TODO: select base on other info
    			var pcfUri string
    			for _, nfProfile := range resp.NfInstances {
    				pcfUri = util.SearchNFServiceUri(nfProfile, models.ServiceName_NPCF_AM_POLICY_CONTROL,
    					models.NfServiceStatus_REGISTERED)
    				if pcfUri != "" {
    					ue.PcfId = nfProfile.NfInstanceId
    					break
    				}
    			}
    			if ue.PcfUri = pcfUri; ue.PcfUri == "" {
    				ue.GmmLog.Error("AMF can not select an PCF by NRF")
    			} else {
    				break
    			}
    		}
    		time.Sleep(500 * time.Millisecond) // 如果NF接口获取失败这里增加一段延时

  

### 4.14 获取接入和移动策略控制信息AMPolicyControlCreate

AMF 执行AM Policy Association Establishment/Modification，获取接入和移动策略控制信息

 **协议流程的位置：**

对应流程图中step16

**报文捕获：**![1632885362_6153da72de07395e76492.png!small?1632885350253](https://image.3001.net/images/20210929/1632885362_6153da72de07395e76492.png!small?1632885350253)

返回201
Created![1632885373_6153da7d961fdcec4e609.png!small?1632885360752](https://image.3001.net/images/20210929/1632885373_6153da7d961fdcec4e609.png!small?1632885360752)

 **代码实现：**

定位到free5gc amf项目/amf/consumer/am_policy.go中的AMPolicyControlCreate函数

    
    
    func AMPolicyControlCreate(ue *amf_context.AmfUe, anType models.AccessType) (*models.ProblemDetails, error) {
    	configuration := Npcf_AMPolicy.NewConfiguration()
    	configuration.SetBasePath(ue.PcfUri)
    	client := Npcf_AMPolicy.NewAPIClient(configuration)
    
    	amfSelf := amf_context.AMF_Self()
    
    	policyAssociationRequest := models.PolicyAssociationRequest{
    		NotificationUri: amfSelf.GetIPv4Uri() + "/namf-callback/v1/am-policy/",
    		Supi:            ue.Supi,
    		Pei:             ue.Pei,
    		Gpsi:            ue.Gpsi,
    		AccessType:      anType,
    		ServingPlmn: &models.NetworkId{
    			Mcc: ue.PlmnId.Mcc,
    			Mnc: ue.PlmnId.Mnc,
    		},
    		Guami: &amfSelf.ServedGuamiList[0],
    	}
    
    	if ue.AccessAndMobilitySubscriptionData != nil {
    		policyAssociationRequest.Rfsp = ue.AccessAndMobilitySubscriptionData.RfspIndex
    	}
    
    	res, httpResp, localErr := client.DefaultApi.PoliciesPost(context.Background(), policyAssociationRequest)
    	if localErr == nil {
    		locationHeader := httpResp.Header.Get("Location")
    		logger.ConsumerLog.Debugf("location header: %+v", locationHeader)
    		ue.AmPolicyUri = locationHeader
    
    		re := regexp.MustCompile("/policies/.*")
    		match := re.FindStringSubmatch(locationHeader)
    
    		ue.PolicyAssociationId = match[0][10:]
    		ue.AmPolicyAssociation = &res
    
    		if res.Triggers != nil {
    			for _, trigger := range res.Triggers {
    				if trigger == models.RequestTrigger_LOC_CH {
    					ue.RequestTriggerLocationChange = true
    				}
    				//if trigger == models.RequestTrigger_PRA_CH {
    				// TODO: Presence Reporting Area handling (TS 23.503 6.1.2.5, TS 23.501 5.6.11)
    				//}
    			}
    		}
    
    		logger.ConsumerLog.Debugf("UE AM Policy Association ID: %s", ue.PolicyAssociationId)
    		logger.ConsumerLog.Debugf("AmPolicyAssociation: %+v", ue.AmPolicyAssociation)
    	} else if httpResp != nil {
    		if httpResp.Status != localErr.Error() {
    			return nil, localErr
    		}
    		problem := localErr.(openapi.GenericOpenAPIError).Model().(models.ProblemDetails)
    		return &problem, nil
    	} else {
    		return nil, openapi.ReportError("server no response")
    	}
    	return nil, nil
    }

### 4.15 更新SM上下文消息

AMF向SMF发送通知消息，更新SM上下文消息。

 **协议流程的位置：**

对应流程图中step17

 **说明：**

当注册类型为移动性注册更新，该步骤才应用，故不涉及。

### 4.17 N2 AMF Mobility Request

对于非3gpp接入的场景，AMF向N3IWF发送通知消息，告知AMF发生了变化，N3IWF向AMF返回了响应。

 **协议流程的位置：**

对应流程图中step18，step19

 **说明：**

不支持

    
    
    // TODO (step 18 optional):
    // If the AMF has changed and the old AMF has indicated an existing NGAP UE association towards a N3IWF, the new AMF
    // creates an NGAP UE association towards the N3IWF to which the UE is connectedsend N2 AMF mobility request to N3IWF
    // if anType == models.AccessType_NON_3_GPP_ACCESS && ue.ServingAmfChanged {
    // 	TODO: send N2 AMF Mobility Request

### 4.18 Registration accept

AMF给UE发送Registration Accept消息

 **协议流程的位置：**

对应流程图中step21

**报文捕获：**![1632885388_6153da8c71adba259286e.png!small?1632885375657](https://image.3001.net/images/20210929/1632885388_6153da8c71adba259286e.png!small?1632885375657)

![1632885394_6153da925f1e7072d2729.png!small?1632885381837](https://image.3001.net/images/20210929/1632885394_6153da925f1e7072d2729.png!small?1632885381837)

### 4.19 Registration Compelte

UE给AMF发送Registration Complete消息，通知AMF注册完成。

 **协议流程的位置：**

对应流程图中step22

**报文捕获：**![1632885401_6153da9912268499349c4.png!small?1632885388462](https://image.3001.net/images/20210929/1632885401_6153da9912268499349c4.png!small?1632885388462)

![1632885408_6153daa00d06ef209907d.png!small?1632885395888](https://image.3001.net/images/20210929/1632885408_6153daa00d06ef209907d.png!small?1632885395888)

 **代码实现：**

AMF处理HandleUplinkNasTransport，定位到free5gc
amf项目/amf/ngap/handler.go中的HandleUplinkNasTransport函数

    
    
    func HandleUplinkNasTransport(ran *context.AmfRan, message *ngapType.NGAPPDU) {
    	var aMFUENGAPID *ngapType.AMFUENGAPID
    	var rANUENGAPID *ngapType.RANUENGAPID
    	var nASPDU *ngapType.NASPDU
    	var userLocationInformation *ngapType.UserLocationInformation
    
    	if ran == nil {
    		logger.NgapLog.Error("ran is nil")
    		return
    	}
    	if message == nil {
    		ran.Log.Error("NGAP Message is nil")
    		return
    	}
    
    	initiatingMessage := message.InitiatingMessage
    	if initiatingMessage == nil {
    		ran.Log.Error("Initiating Message is nil")
    		return
    	}
    
    	uplinkNasTransport := initiatingMessage.Value.UplinkNASTransport
    	if uplinkNasTransport == nil {
    		ran.Log.Error("UplinkNasTransport is nil")
    		return
    	}
    	ran.Log.Info("Handle Uplink Nas Transport")
    
    	for i := 0; i < len(uplinkNasTransport.ProtocolIEs.List); i++ {
    		ie := uplinkNasTransport.ProtocolIEs.List[i]
    		switch ie.Id.Value {
    		case ngapType.ProtocolIEIDAMFUENGAPID:
    			aMFUENGAPID = ie.Value.AMFUENGAPID
    			ran.Log.Trace("Decode IE AmfUeNgapID")
    			if aMFUENGAPID == nil {
    				ran.Log.Error("AmfUeNgapID is nil")
    				return
    			}
    		case ngapType.ProtocolIEIDRANUENGAPID:
    			rANUENGAPID = ie.Value.RANUENGAPID
    			ran.Log.Trace("Decode IE RanUeNgapID")
    			if rANUENGAPID == nil {
    				ran.Log.Error("RanUeNgapID is nil")
    				return
    			}
    		case ngapType.ProtocolIEIDNASPDU:
    			nASPDU = ie.Value.NASPDU
    			ran.Log.Trace("Decode IE NasPdu")
    			if nASPDU == nil {
    				ran.Log.Error("nASPDU is nil")
    				return
    			}
    		case ngapType.ProtocolIEIDUserLocationInformation:
    			userLocationInformation = ie.Value.UserLocationInformation
    			ran.Log.Trace("Decode IE UserLocationInformation")
    			if userLocationInformation == nil {
    				ran.Log.Error("UserLocationInformation is nil")
    				return
    			}
    		}
    	}
    
    	ranUe := ran.RanUeFindByRanUeNgapID(rANUENGAPID.Value)
    	if ranUe == nil {
    		ran.Log.Errorf("No UE Context[RanUeNgapID: %d]", rANUENGAPID.Value)
    		return
    	}
    	amfUe := ranUe.AmfUe
    	if amfUe == nil {
    		err := ranUe.Remove()
    		if err != nil {
    			ran.Log.Errorf(err.Error())
    		}
    		ran.Log.Errorf("No UE Context of RanUe with RANUENGAPID[%d] AMFUENGAPID[%d] ",
    			rANUENGAPID.Value, aMFUENGAPID.Value)
    		return
    	}
    
    	ranUe.Log.Infof("Uplink NAS Transport (RAN UE NGAP ID: %d)", ranUe.RanUeNgapId)
    
    	if userLocationInformation != nil {
    		ranUe.UpdateLocation(userLocationInformation)
    	}
    
    	nas.HandleNAS(ranUe, ngapType.ProcedureCodeUplinkNASTransport, nASPDU.Value)
    }

最后定位到free5gc amf项目/amf/gmm/handler.go中的HandleRegistrationComplete函数

    
    
    func HandleRegistrationComplete(ue *context.AmfUe, accessType models.AccessType,
    	registrationComplete *nasMessage.RegistrationComplete) error {
    	//返回注册完成
        ue.GmmLog.Info("Handle Registration Complete")
    
    	if ue.T3550 != nil {
    		ue.T3550.Stop()
    		ue.T3550 = nil // clear the timer
    	}

## 五、总结

本文借助free5gc+UERANSIM模拟5G网络环境，通过抓包和源码分析的方式介绍了用户注册管理流程的相关步骤。希望能帮助到对5G知识感兴趣的读者，不足之处请多多指正。

 **作者：中兴沉烽实验室_lwc、中兴沉烽实验室_lyc**

## 参考资料

> 沉烽网络安全实验室：《free5gc+UERANSIM模拟5G网络环境搭建及基本使用》  
> https://www.freebuf.com/articles/wireless/268397.html
>
> 沉烽网络安全实验室：《基于UERANSIM+free5gc 5G模拟环境的5G_AKA协议解析》  
> https://www.freebuf.com/articles/wireless/273792.html
>
> 张忠琳：【5G核心网】free5GC 注册请求流程源码分析  
> https://www.it610.com/article/1292406752595222528.htm
>
> 3GPP TS 23 502
>
> 3GPP TS 33.501
>
> free5gc https://github.com/free5gc/free5gc
>
> UERANSIM https://github.com/aligungr/UERANSIM

