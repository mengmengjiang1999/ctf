***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 0x1 漏洞信息

CNVD-ID：CNVD-2018-00995

CVE ID：[CVE-2018-7471 ](http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-7471)

某公司工业组态软件存在整数溢出漏洞，该漏洞是由于stgopenstorage读取失败，返回的错误代码超出int在32位系统中的范围，攻击者可利用该漏洞执行任意代码。

补丁信息：<http://www.kingview.com/news_info.php?num=1000656>

漏洞发布：<http://www.cnvd.org.cn/flaw/show/CNVD-2018-00995>

## 0x2 OpenStorage函数说明

OpenStorage加载结构化存储的文件，函数返回HRESULT类型变量。函数原型如下：

![1111.png](https://image.3001.net/images/20180507/15256705151054.png!small)  

返回的结果为长整形：当函数读取正常时，返回值为0，读取失败，返回长整型整数

函数说明参考MSDN：

<https://msdn.microsoft.com/en-us/library/windows/desktop/aa380024(v=vs.85).aspx>

## 0x3查找漏洞函数

根据补丁对比，将漏洞组件确定为Touchvewocx.ocx。经分析，该模块有五个函数有变化，其中三个进行了修改，逐一进行分析。

![2.jpg](https://image.3001.net/images/20180425/15246441477441.jpg!small)

### 3.1 0x100223C0

CViewManager::LoadDocInfor(CViewManager *this,CPicDocument *pd)

![3.jpg](https://image.3001.net/images/20180425/15246441479314.jpg!small)

放大来看，主要是增加0x10022780部分的判断程序块。

![4.jpg](https://image.3001.net/images/20180425/15246441475387.jpg!small)  

3.1.1 补丁前

    
    
    .text:100223C0 var_814         = dword ptr -814h
    .text:100223C0var_810         = dword ptr -810h    -int 32
    .text:100223C0 pwcsName        = dword ptr -80Ch
    .text:100223C0 ppstgOpen       = dword ptr -808h      
    

![无标题.png](https://image.3001.net/images/20180425/15246447247330.png!small)

var_810(v25)是一个值为负数的int32(函数调用错误是，返回一个负值，其高位为1)变量，系统为64位时，负数扩展高位补F。

3.1.2 补丁后

返回值为dword 类型，返回若不为S_OK，返回值转换为Cstring（whar_t）后，进行异常处理。  

    
    
    .text:100223C0sc              = dword ptr -810h
    .text:100223C0 lpsz            = dword ptr -80Ch
    .text:100223C0 lpStorage       = dword ptr -808h  
    

![7.jpg](https://image.3001.net/images/20180425/15246450326089.jpg!small)![8.jpg](https://image.3001.net/images/20180425/15246450322612.jpg!small)

### 3.2 0x10039530

![9.jpg](https://image.3001.net/images/20180425/15246452176221.jpg!small)

修复后：

![10.jpg](https://image.3001.net/images/20180425/15246452174844.jpg!small)

将字符串改为wchar  

### 3.3 0x10151880

![11.jpg](https://image.3001.net/images/20180425/15246453053009.jpg!small)

修补前：

![12.jpg](https://image.3001.net/images/20180425/15246453053662.jpg!small)

![13.jpg](https://image.3001.net/images/20180425/15246453642716.jpg!small)

修补后：

![14.jpg](https://image.3001.net/images/20180425/15246454036898.jpg!small)

    
    
    if ( StgIsStorageFile(lpsz) == 1 )
      {
        sc =StgCreateDocfile(lpsz, 0x30022u, 0, &lpStorage);
        if ( sc< 0 || !lpStorage )
          sc =StgCreateDocfile(lpsz, 0x30000u, 0, &lpStorage);
      }
      else
      {
        sc =StgOpenStorage(lpsz, 0, 0x10022u, 0, 0, &lpStorage);
        if ( sc< 0 || !lpStorage )
          sc =StgOpenStorage(lpsz, 0, 0x10000u, 0, 0, &lpStorage);
      }
      if ( sc )
      {
        sc = 1;
        v62 = 0;
       LOBYTE(v114) = 6;
       AFX_EXCEPTION_LINK::~AFX_EXCEPTION_LINK(&_afxExceptionLink);
       LOBYTE(v114) = 5;
       CPicDocument::~CPicDocument(&PicDoc);
       LOBYTE(v114) = 4;
       CFileException::~CFileException(&e);
       LOBYTE(v114) = 3;    
    CString (&message);
       LOBYTE(v114) = 2;
        CString (&failSz);
       LOBYTE(v114) = 1;
        CString (&pd_picName);
       LOBYTE(v114) = 0;    
    CString (&viewfilename);
    v114 = -1;   
    CString (&filename);
        v4 =v62;
      }  
    

## 0x4 脆弱ActiveX接口确定

Touchvewocx的接口如下：  

![17.jpg](https://image.3001.net/images/20180425/15246461178028.jpg!small)

函数调用路径：

![18.jpg](https://image.3001.net/images/20180425/15246461173112.jpg!small)

可以基本确定漏洞ActiveX接口为SetProjectPath  

## 0x5 结论

ActiveX组件Touchvewocx.ocx接口函数SetProjectPath（string*）调用OpenStorage(
)读取失败是，异常返回长整型（32位系统32位int，64位系统，64位int），函数给返回值分配dword型变量，在32位系统中刚好满足，64位系统中直接截断，造成异常。  

***本文原创作者：flypuma，转载请注明来自FreeBuf.COM**

