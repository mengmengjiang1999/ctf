# 深入理解win32（九）

阅读量 **120740**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-18 10:00:22

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01e94717568627114f.jpg)

## 前言

在上一节中我们对资源表进行了解析，在这一节里面我们来了解通用控件。

## 准备工作

首先新建一个资源脚本

![](https://p0.ssl.qhimg.com/t0104a6c54b3bad1944.png)

创建一个dialog

![](https://p1.ssl.qhimg.com/t01bc650acee85aa714.png)

在父窗口里新建两个窗口

![](https://p1.ssl.qhimg.com/t01b9770b649a64e580.png)

添加一些按钮，修改字体后如下图所示

![](https://p3.ssl.qhimg.com/t0116ce361d2d4a189f.png)

然后添加Dialog的相关函数

![](https://p1.ssl.qhimg.com/t01939c96a57d0356c8.png)

![](https://p5.ssl.qhimg.com/t0101544699abef2385.png)

然后大体的框架就已经搭建了出来

![](https://p2.ssl.qhimg.com/t0196a59a1c07ec8a86.png)

## 标准控件和通用控件

对于windows标准的控件总是可用的

    
    
    Static
    Group Box
    Button
    Check Box
    Radio Button
    Edit
    ComboBox
    ListBox
    

因为如果把所有的控件在编译的时候全部加进exe就会使exe变得十分大，所以windows把通用控件放在了`Comctrl32.dll`里面

新建一个列表控件作为进程的显示窗口

![](https://p5.ssl.qhimg.com/t012c2257af66bf7e4a.png)

再新建一个列表控件作为模块的显示窗口

![](https://p5.ssl.qhimg.com/t01cbb34ad97a655e0d.png)

这里再把样式改为报告

![](https://p5.ssl.qhimg.com/t01b94d33a0a6578728.png)

因为通用控件在dll里，所以还需要包含头文件

    
    
    #include <commctrl.h>            
    #pragma comment(lib,"comctl32.lib")
    

![](https://p0.ssl.qhimg.com/t017efe2552eba028a3.png)

另外我们需要给windows指定我们需要使用哪一个通用控件，就需要通过INITCOMMONCONTROLSEX进行初始化

###  INITCOMMONCONTROLSEX

    
    
    typedef struct tagINITCOMMONCONTROLSEX {
        DWORD dwSize;
        DWORD dwICC;
    } INITCOMMONCONTROLSEX, *LPINITCOMMONCONTROLSEX;
    

第一个参数为`INITCOMMONCONTROLSEX`的大小，第二个参数就是使用哪一个通用控件

![](https://p2.ssl.qhimg.com/t01046c6df0c0b215fb.png)

例如这里我应该使用的是`ICC_LISTVIEW_CLASSES`这个控件，但是每次找的话都会很麻烦，这里windows给我们提供了一个包含常用的通用控件的类型，即`ICC_WIN95_CLASSES`

    
    
    INITCOMMONCONTROLSEX icex;            
    icex.dwSize = sizeof(INITCOMMONCONTROLSEX);            
    icex.dwICC = ICC_WIN95_CLASSES;            
    InitCommonControlsEx(&icex);
    

即可使用通用控件生成界面

![](https://p5.ssl.qhimg.com/t012d493773658f5a60.png)

这里再设置列，添加如下代码

    
    
    void InitProcessListView(HWND hDlg)
    {
        LV_COLUMN lv;                                
        HWND hListProcess;                                
    
        //初始化                                
        memset(&lv,0,sizeof(LV_COLUMN));                                
        //获取IDC_LIST_PROCESS句柄                                
        hListProcess = GetDlgItem(hDlg,IDC_LIST_PROCESS);                                
        //设置整行选中                                
        SendMessage(hListProcess,LVM_SETEXTENDEDLISTVIEWSTYLE,LVS_EX_FULLROWSELECT,LVS_EX_FULLROWSELECT);                                
    
        //第一列                                
        lv.mask = LVCF_TEXT | LVCF_WIDTH | LVCF_SUBITEM;                                
        lv.pszText = TEXT("进程");                //列标题                
        lv.cx = 200;                                //列宽
        lv.iSubItem = 0;                                
        //ListView_InsertColumn(hListProcess, 0, &lv);                                
        SendMessage(hListProcess,LVM_INSERTCOLUMN,0,(DWORD)&lv);                                
        //第二列                                
        lv.pszText = TEXT("PID");                                
        lv.cx = 100;                                
        lv.iSubItem = 1;                                
        //ListView_InsertColumn(hListProcess, 1, &lv);                                
        SendMessage(hListProcess,LVM_INSERTCOLUMN,1,(DWORD)&lv);                                
        //第三列                                
        lv.pszText = TEXT("镜像基址");                                
        lv.cx = 100;                                
        lv.iSubItem = 2;                                
        ListView_InsertColumn(hListProcess, 2, &lv);                                
        //第四列                                
        lv.pszText = TEXT("镜像大小");                                
        lv.cx = 100;                                
        lv.iSubItem = 3;                                
        ListView_InsertColumn(hListProcess, 3, &lv);                                
    
    }
    
        case WM_INITDIALOG:
            {
                //设置ProcerssListView的风格
                InitProcessListView(hDlg);
    
                break;
            }
    

![](https://p2.ssl.qhimg.com/t011f7b8a4bfaff46f8.png)

这里如果要显示数据的话应该用遍历进程的方法，但是这里还没有涉及到，就自己写代码添加进程进去显示

    
    
    VOID EnumProcess(HWND hListProcess)
    {
        LV_ITEM vitem;                        
    
        //初始化                        
        memset(&vitem,0,sizeof(LV_ITEM));                        
        vitem.mask = LVIF_TEXT;                        
    
        vitem.pszText = "csrss.exe";                        
        vitem.iItem = 0;                        
        vitem.iSubItem = 0;                        
        //ListView_InsertItem(hListProcess, &vitem);                        
        SendMessage(hListProcess, LVM_INSERTITEM,0,(DWORD)&vitem);                        
    
        vitem.pszText = TEXT("448");                        
        vitem.iItem = 0;                        
        vitem.iSubItem = 1;                        
        ListView_SetItem(hListProcess, &vitem);                        
    
        vitem.pszText = TEXT("56590000");                        
        vitem.iItem = 0;                        
        vitem.iSubItem = 2;                        
        ListView_SetItem(hListProcess, &vitem);                        
    
        vitem.pszText = TEXT("000F0000");                        
        vitem.iItem = 0;                        
        vitem.iSubItem = 3;                        
        ListView_SetItem(hListProcess, &vitem);                        
    
        vitem.pszText = TEXT("winlogon.exe");                        
        vitem.iItem = 1;                        
        vitem.iSubItem = 0;                        
        //ListView_InsertItem(hListProcess, &vitem);                        
        SendMessage(hListProcess, LVM_INSERTITEM,0,(DWORD)&vitem);                        
    
        vitem.pszText = TEXT("456");                        
        vitem.iSubItem = 1;                        
        ListView_SetItem(hListProcess, &vitem);                        
    
        vitem.pszText = TEXT("10000000");                        
        vitem.iSubItem = 2;                        
        ListView_SetItem(hListProcess, &vitem);                        
    
        vitem.pszText = TEXT("000045800");                        
        vitem.iSubItem = 3;                        
        ListView_SetItem(hListProcess, &vitem);                        
    
    }
    

再编译生成即可发现已经生成

![](https://p1.ssl.qhimg.com/t01f67a396298b3c976.png)

## ListView的使用

这里提一个点，使用`ListView_InsertColumn`跟`SendMessage`的效果相同

    
    
    ListView_InsertColumn(hListProcess, 1, &lv);    
    SendMessage(hListModules,LVM_INSERTCOLUMN,1,(DWORD)&lv);
    

这里再写一个模块函数`InitProcessListView`

    
    
    VOID InitModulesListView(HWND hDlg)
    {
        LV_COLUMN lv;
        HWND hListModules;
    
        //初始化                                
        memset(&lv,0,sizeof(LV_COLUMN));                                
        //获取IDC_LIST_PROCESS句柄                                
        hListModules = GetDlgItem(hDlg,IDC_LIST_MOUDLE);                                
        //设置整行选中                                
        SendMessage(hListModules,LVM_SETEXTENDEDLISTVIEWSTYLE,LVS_EX_FULLROWSELECT,LVS_EX_FULLROWSELECT);
    
        //第一列                                
        lv.mask = LVCF_TEXT | LVCF_WIDTH | LVCF_SUBITEM;                                
        lv.pszText = TEXT("模块名称");                //列标题                
        lv.cx = 238;                                //列宽
        lv.iSubItem = 0;                                
        //ListView_InsertColumn(hListProcess, 0, &lv);                                
        SendMessage(hListModules,LVM_INSERTCOLUMN,0,(DWORD)&lv);                                
        //第二列                                
        lv.pszText = TEXT("模块位置");                                
        lv.cx = 238;                                
        lv.iSubItem = 1;                                
        //ListView_InsertColumn(hListProcess, 1, &lv);    
        SendMessage(hListModules,LVM_INSERTCOLUMN,1,(DWORD)&lv);
    
    }
    

调用函数初始化

![](https://p2.ssl.qhimg.com/t01aecdf6d8db08a9b4.png)

即可得到界面

![](https://p4.ssl.qhimg.com/t01dba397bcb4e8c610.png)

## WM_NOTIFY

该消息类型与`WM_COMMAND`类型相似，都是由子窗口向父窗口发送的消息。`WM_NOTIFY`可以包含比`WM_COMMAND`更丰富的信息，Windows通用组件中有很多消息，都是通过`WM_NOTIFY`来描述的。一般标准控件在父窗口执行使用`WM_COMMAND`，通用控件在父窗口执行使用`WM_NOTIFY`

`WM_NOTIFY`消息中的参数如下：

`wParam`:控件ID

`lParam`:指向一个结构

    
    
    typedef struct tagNMHDR {                     
            HWND hwndFrom; //发送通知消息的控制窗口句柄                    
            UINT idFrom;   //发送通知消息的控制ID值                    
            UINT code;     //通知码，如LVM_SELCHANGED                    
        } NMHDR;
    

这个结构体能满足一般的要求，但能描述的信息还是有限的，如果不能满足要求还可以使用另外更复杂的结构进行标识(注意这里windows会自动帮我们替换)

以下结构体都有一个共同的特点，第一个成员都是`NMHDR`，即`WM_NOTIFY`这个通用结构体，这里体现了C++继承的思想

    
    
        typedef struct tagNMLVCACHEHINT {            
            NMHDR   hdr;            
            int     iFrom;            
            int     iTo;            
        } NMLVCACHEHINT, *PNMLVCACHEHINT;            
    
        typedef struct tagLVDISPINFO {            
            NMHDR hdr;            
            LVITEM item;            
        } NMLVDISPINFO, FAR *LPNMLVDISPINFO;            
    
        typedef struct _NMLVFINDITEM {            
            NMHDR hdr;            
            int iStart;            
            LVFINDINFO lvfi;            
        } NMLVFINDITEM, *PNMLVFINDITEM;
    

这里首先写一个获取`InitProcessListView`这个模块进程的`PID`的函数

首先对从堆栈分配空间的缓冲区进行初始化操作

![](https://p0.ssl.qhimg.com/t0110ab95637c303f59.png)

然后选择行，这里使用`SendMessage()`赋值给`dwRowId`，然后判断`dwRowId`的值即可得到选取的行

当我选取第一行的时候`dwRowId`的值为0，选取第二行的时候`dwRowId`的值为1

![](https://p4.ssl.qhimg.com/t0148c467823a08c1cc.png)

![](https://p3.ssl.qhimg.com/t0184252296218a277f.png)

而当我没有选择有数据的行的时候，`dwRowId`的值就为-1

![](https://p4.ssl.qhimg.com/t018dbae4cd811254fc.png)

所以这里就可以写一个if语句进行条件的判断，当`dwRowId`的值为-1的时候直接弹出`Error`的弹窗

![](https://p1.ssl.qhimg.com/t0170df4051972cce45.png)

然后获取选中行的`PID`，要得到`PID`首先要确定`PID`所在的列，然后指定存储缓冲区的位置和大小，然后使用`SendMessage`和`MessageBox`实现弹窗

![](https://p4.ssl.qhimg.com/t01cb45f271f121bc6c.png)

效果如下

![](https://p2.ssl.qhimg.com/t01ce4aee5a362f8ec9.png)

![](https://p2.ssl.qhimg.com/t014227a4c3fe22d648.png)

完整代码如下

    
    
    VOID EnumMoudules(HWND hListProcess,WPARAM wParam,LPARAM lParam)
    {
        DWORD dwRowId;
        TCHAR szPid[0x20];
        LV_ITEM lv;
    
        //初始化
        memset(&lv, 0 , sizeof(LV_ITEM));
        memset(szPid, 0, 0x20);
    
        //获取选择行
        dwRowId = SendMessage(hListProcess, LVM_GETNEXTITEM, -1, LVNI_SELECTED);
        if (dwRowId == -1)
        {
            MessageBox(NULL, TEXT("Please choose process!"), TEXT("Error"), MB_OK);
    
            return;
        }
    
        //获取PID
        lv.iSubItem = 1;        //获取列
        lv.pszText = szPid;        //指定存储查询结果的缓冲区
        lv.cchTextMax = 0x20;    //指定缓冲区大小
        SendMessage(hListProcess, LVM_GETITEMTEXT, dwRowId, (DWORD)&lv);
    
        MessageBox(NULL, szPid, TEXT("PID"), MB_OK);
    }
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Drunkmars** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/265424](/post/id/265424)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [win32](/tag/win32)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhimg.com/t019bb9b9add2982923.jpg) Drunkmars

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

