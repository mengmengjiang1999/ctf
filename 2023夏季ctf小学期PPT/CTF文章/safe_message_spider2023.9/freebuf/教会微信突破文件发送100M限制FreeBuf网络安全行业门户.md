* 9102年了，我想大部分人使用微信的频率应该都会高于QQ了吧。

以前在QQ传文件的时候，哪里会想到会有文件大小限制，几G、几十G的文件随意传。

而现在，用微信传文件，很尴尬，只能传100M或更小的文件。为什么做这个限制？我想可能是因为微信一开始就是手机应用。

  * * 最初手机存储空间并不像电脑那么大，所以微信可能认为手机存不下（而现在256G是标配了）。
  * * 更重要的是，手机使用流量，大文件消耗流量更多，用户肯定受不了（现在流量也不贵了，再说还有WIFI呢）。
  *   

  * 所以限制文件大小，合情合理。但是，现在微信也出了PC版本了，也有很多用户在使用PC版本微信，还在限制100M就有点说不过去了。
  *   

  * 你说怕手机收到后下载耗流量，确实有点浪费，那你服务端可以区分一下嘛，用户也可以自己确认是否下载啊。
  *   

  * 但是，微信并没有做什么，这就很影响PC上微信的使用体验了。
  *   

  * 我要用微信传大文件啊（100M以上），因为我QQ密码忘了，因为我朋友QQ密码忘了...
  *   

  * 好，既然如此，你不做...还是...你不做，那就我来做！

### 1、突破本地100M限制

下载最新的PC微信（当时2.6.8.65），开始分析微信对文件大小限制是如何做的，然后一一突破。在选择文件过程中就做了100M限制。![1.png](https://image.3001.net/images/20190815/1565852550_5d550386110b5.png!small)  
嗯，文件大小首先就想到了`GetFileSize`，下个断点看看。

    
        bp KERNEL32!GetFileSize
    bp KERNEL32!GetFileSizeEx
    0:000:x86> kvn
     # ChildEBP RetAddr  Args to Child              
    00 0075cf6c 7908f015 c78f272a 10977de0 00000001 KERNEL32!GetFileSizeEx
    01 0075cfec 7908ed8c 109a7218 0000001f 00000020 WeChatWin!IMVQQEngine::`default constructor closure'+0x2f735
    0:000:x86> g
    Breakpoint 2 hit
    KERNEL32!GetFileSizeEx:
    777840e0 ff25d80f7e77    jmp     dword ptr [KERNEL32!_imp__GetFileSizeEx (777e0fd8)] ds:002b:777e0fd8={KERNELBASE!GetFileSizeEx (76ce2ec0)}
    0:000:x86> kvn
     # ChildEBP RetAddr  Args to Child              
    00 0075e810 7908fd9e c78f0396 00000000 0e61c3a4 KERNEL32!GetFileSizeEx
    01 0075eb50 792e5b5c 00000306 0000000f 00000000 WeChatWin!IMVQQEngine::`default constructor closure'+0x304be
    0:000:x86> g
    Breakpoint 2 hit
    KERNEL32!GetFileSizeEx:
    777840e0 ff25d80f7e77    jmp     dword ptr [KERNEL32!_imp__GetFileSizeEx (777e0fd8)] ds:002b:777e0fd8={KERNELBASE!GetFileSizeEx (76ce2ec0)}
    0:008:x86> kvn
     # ChildEBP RetAddr  Args to Child              
    00 0378e530 79a9eba3 00000002 00000000 00000000 KERNEL32!GetFileSizeEx
    01 0378e5c4 79a9ee3d 00000002 00000000 00000000 WeChatWin!_ASSERT+0x553c3 //10aeeba3
    0:008:x86> g
    

艾玛啊，触发有点多啊，头疼。算了，换个思路。点击发送文件按钮，会弹出文件选择对话框，这是微软提供的。

  *   

  * 写过win32 gui或者mfc程序的同学应该想到了，对弹出文件选择对话框的函数下断点。
  *   

  * 不是~bp shell32!SHBrowseForFolderW这是目录选择~，也不是~bp shell32!SHFileOperationW~，而是这个：`bp comdlg32!GetOpenFileNameW`
    
        Breakpoint 5 hit
    COMDLG32!GetOpenFileNameW:
    7523e810 8bff            mov     edi,edi
    0:000:x86> kvn
     # ChildEBP RetAddr  Args to Child              
    00 0075cffc 7908eac2 0075d014 c78f0306 1097cb80 COMDLG32!GetOpenFileNameW (FPO: [1,1053,4])
    01 0075ebc0 7907e81c 000003e9 00000000 00000000 WeChatWin!IMVQQEngine::`default constructor closure'+0x2f1e2 //100deac2
    02 0075ebd8 792e586f 000003e9 00000000 00000000 WeChatWin!IMVQQEngine::`default constructor closure'+0x1ef3c
    03 0075ec38 792e556e c78f0492 00000000 0075ed54 WeChatWin!IMVQQEngine::`default constructor closure'+0x285f8f
    04 0075ec54 753e48eb 00521896 000007e7 00000000 WeChatWin!IMVQQEngine::`default constructor closure'+0x285c8e
    05 0075ec80 753c613c 792e54a0 00521896 000007e7 USER32!_InternalCallWinProc+0x2b
    06 0075ed64 753c528e 792e54a0 00000000 000007e7 USER32!UserCallWinProcCheckWow+0x3ac (FPO: [SEH])
    07 0075edd8 753c5070 000007e7 0075ee18 7968d71f USER32!DispatchMessageWorker+0x20e (FPO: [Non-Fpo])
    08 0075ede4 7968d71f 0075edfc 00000000 00d90000 USER32!DispatchMessageW+0x10 (FPO: [Non-Fpo])
    09 0075ee18 79666f9e 77779830 754207b0 00000001 WeChatWin!WCSGetInstance+0x2388f
    0a 0075f0a0 00d91918 00d90000 00a72bf2 00000000 WeChatWin!StartWachat+0x14e
    0b 0075f8bc 00d930b9 00d90000 00000000 00a72bf2 WeChat+0x1918
    0c 0075f908 77776359 00520000 77776340 0075f974 WeChat+0x30b9
    0d 0075f918 77a57a94 00520000 b5777c1c 00000000 KERNEL32!BaseThreadInitThunk+0x19 (FPO: [Non-Fpo])
    0e 0075f974 77a57a64 ffffffff 77a78e17 00000000 ntdll_779f0000!__RtlUserThreadStart+0x2f (FPO: [SEH])
    0f 0075f984 00000000 00d9312b 00520000 00000000 ntdll_779f0000!_RtlUserThreadStart+0x1b (FPO: [Non-Fpo])
    

根据返回地址`7908eac2`计算到在IDA中地址`100deac2`，用IDA翻看一下函数怎么做的。微信可以同时选择多个文件，这里循环获取到路径，限制最多10个，然后进入sub_100DEED0处理。

    
        v24 = -GetOpenFileNameW(&v44);
    if ( *filename )
        {
          while ( 1 )
          {
            memset(&String1, 0, 0x208u);
            lstrcatW(&String1, (LPCWSTR)String);
            lstrcatW(&String1, filename);           // 构造完整路径
            v46 = 0;
            *(_OWORD *)sigle_filepath = 0i64;
            sub_104822F0((int *)sigle_filepath, &String1, 0xFFFFFFFF);
            LOBYTE(v73) = 4;
            sub_10056060((unsigned int *)&filepath1, (unsigned int)sigle_filepath);
            LOBYTE(v73) = 3;
            if ( ++ii > 10 )                        // 最多10个文件
              break;
            filename += lstrlenW(filename) + 1;     // 下一个文件
            if ( !*filename )
              goto LABEL_35;
          }
    ...
    sub_104822F0((int *)&filepath__, *filepath1_, 0xFFFFFFFF);
    sub_100DEED0((int)v61, v33, filepath__.buf, filepath__.len, (int)v41, v42, v43);
    

进入函数`sub_100DEED0`之后，一下就看到获取文件大小的函数，然后是判断文件是否大于100M。

    
            v16 = f_FileUtils::fileSize_10475050(&path);
        filesize = v16.LowPart;
    if ( filesize > 0 )
        {
          if ( filesize >= 104857600 )              // 100M
          {
             //100M提示框
          }
       }
    }
    

先手工windbg修改一下指令，验证是否正确。把0x6400000改为0，jl改成jge即可。篇幅原因，不展开了。

  * 通过调试确认，100M以上文件绕过这个限制。
    
        .text:100DF347 07C                 cmp     esi, 6400000h
    .text:100DF34D 07C                 jl      loc_100DF263 //0f8c10ffffff=>0f8d10ffffff(jge)
    =>
    .text:100DF347 07C                 cmp     esi, 0
    .text:100DF34D 07C                 jge      loc_100DF263 //0f8c10ffffff=>0f8d10ffffff(jge)
    

但是还没完，依然会弹框，居然还有二次验证。调试函数`sub_100DEED0`，单步继续往下走，看看是哪里弹框。最终找到在`sub_10099D70`这个函数里还有校验。

    
        v33 = sub_104FF8F0(v7 + 337);
    sub_10099D70((_BYTE *)v7[344], (size_t *)&path, (char *)(v33 == 0));
    

同样进入`sub_10099D70`，找到校验代码。

    
        v7 = f_FileUtils::fileSize_10475050(a2);
      filesize = v7.LowPart;
    if ( filesize > 0 )
      {
        if ( filesize > 104857600 )                 // 100M
        {
            //100M提示框
        }
    }
    

windbg修改一下指令，验证是否正确。把0x6400000改为0，jle改成jge即可，调试确认绕过检查。

    
        .text:1009A34C 0AC                 cmp     esi, 6400000h
    .text:1009A352 0AC                 jle     loc_1009A25C//0f8e04ffffff    =>0f8d04ffffff(jge)
    =>
    .text:1009A34C 0AC                 cmp     esi, 0
    .text:1009A352 0AC                 jge     loc_1009A25C//0f8e04ffffff    =>0f8d04ffffff(jge)
    

过了这两处检查后，文件成功显示在输入框中。![2.png](https://image.3001.net/images/20190815/1565852566_5d550396dfce9.png!small)  
不过直接发送依然失败，显示“上传文件大小不能大于100M”，应该是服务器做了检查。![2_1.png](https://image.3001.net/images/20190815/1565852571_5d55039bc0843.png!small)  
另外，微信还支持拖动文件发送，经过前面两步的突破，此时拖入文件依然提示“发送的文件大小不能大于100M”。那继续把这个干掉吧。拖动文件首先想到的就是`DragQueryFileW`，加上断点试试。

    
        bp shell32!DragQueryFileW
    0:000:x86> kv
     # ChildEBP RetAddr  Args to Child              
    00 004fdbec 790ce89a 0f1a3978 ffffffff 00000000 SHELL32!DragQueryFileW 
    01 004fded8 7577104b 038ca6c0 0c6b0bf8 00000001 WeChatWin!IMVQQEngine::`default constructor closure'+0x6efba//1011e89a 1011e8c9
    02 004fdf18 75e0f4c4 02fa7770 00000002 00180cd0 ole32!CPrivDragDrop::PrivDragDrop+0x2eb (FPO: [Non-Fpo]) (CONV: stdcall) [com\ole32\com\rot\getif.cxx @ 658] 
    03 004fdf5c 75dd4f3d 75770d60 004fe178 0000000c RPCRT4!Invoke+0x34
    0:000:x86> kv 4
     # ChildEBP RetAddr  Args to Child              
    00 004fdbec 790ce8c9 0f1a3978 00000000 004fdcc0 SHELL32!DragQueryFileW (FPO: [Non-Fpo])
    01 004fded8 7577104b 038ca6c0 0c6b0bf8 00000001 WeChatWin!IMVQQEngine::`default constructor closure'+0x6efe9//1011e8c9
    02 004fdf18 75e0f4c4 02fa7770 00000002 00180cd0 ole32!CPrivDragDrop::PrivDragDrop+0x2eb (FPO: [Non-Fpo]) (CONV: stdcall) [com\ole32\com\rot\getif.cxx @ 658] 
    03 004fdf5c 75dd4f3d 75770d60 004fe178 0000000c RPCRT4!Invoke+0x34
    

确实拖动中会断下，但经过分析并不是关键代码，没有对文件进行处理，另外断下后，再跑起来，拖动文件失败。所以另想他法。又想到了前面没有用处的`getfilesizeex`,再来尝试一下。

    
        0:004> bp kernel32!getfilesizeex
    0:004> g
    Breakpoint 6 hit
    KERNEL32!GetFileSizeEx:
    777840e0 ff25d80f7e77    jmp     dword ptr [KERNEL32!_imp__GetFileSizeEx (777e0fd8)] ds:002b:777e0fd8={KERNELBASE!GetFileSizeEx (76ce2ec0)}
    0:000:x86> kv
     # ChildEBP RetAddr  Args to Child              
    00 004fde4c 791a9fc6 c74c6e8e 00000001 038ca6c0 KERNEL32!GetFileSizeEx
    01 004fdec8 790cea71 0c700528 7a00c9dc 004fdf18 WeChatWin!IMVQQEngine::`default constructor closure'+0x14a6e6 //101f9fc6
    02 004fded8 75770ed2 038ca6c0 0c700528 00000000 WeChatWin!IMVQQEngine::`default constructor closure'+0x6f191
    03 004fdf18 75e0f4c4 02fa7770 00000002 00180cd0 ole32!CPrivDragDrop::PrivDragDrop+0x172 (FPO: [Non-Fpo]) 
    

嘿嘿，没想到一下子找到了关键位置，`getfilesizeex`建了一功。

    
              filesize = f_FileUtils::fileSize_10475050(v52);
          if ( sub_106DEFCB(*((_DWORD *)v2 + 463)) == 2 )
          {
            if ( filesize.QuadPart > 0x1900000 )
              goto LABEL_28;
          }
          else if ( filesize.QuadPart > 104857600 )
          { 
               //100M提示
          }
    

同样的方式，把0x6400000改为0，ja改成jbe，绕过这个校验。

    
        .text:101FA196 078 81 7D C0 00 00 40 06                          cmp     dword ptr [ebp+filesize], 6400000h
    .text:101FA19D 078 0F 87 76 FE FF FF                             ja      loc_101FA019
    =>
    .text:101FA196 078 81 7D C0 00 00 00 00                          cmp     dword ptr [ebp+filesize], 0
    .text:101FA19D 078 0F 86 76 FE FF FF                             jbe      loc_101FA019
    

OK，到这里，本地100M限制就成功突破，下面继续看看如何绕过服务器限制。

### 2、突破服务器100M限制

前面提到，能够选择大于100M文件之后，点击发送依然会失败，提示“上传文件大小不能大于100M”。

  *   

  * 很明显服务器做了上传文件限制。所以如何突破这个限制呢？
  *   

  * 额，动不了服务器代码啊...
  *   

  * 能够想到的就是在文件发送前，自动分割文件为小于100M的多个文件，然后将分割的文件自动发送出去，在接收方，把收到的每个文件再自动合并。
  *   

  * 如此服务器也不会说文件大于100M了，对于用户来说，体验也是一致的。
  *   

  * 是的，我就是这么实现的。
  *   

  * 首先，找到发送文件的函数。由于之前分享过如何找到发送消息的函数，详情请看文章[微信PC端技术研究(3)-如何找到消息发送接口](a%20href=)，所以这里不详细分析如何找到发送文件的函数了。
  *   

  * 直接拿来用，就是这个函数`sub_102382E0`。
    
        .text:100CC124 DE0 83 EC 14                                      sub     esp, 14h
    .text:100CC127 DF4 8B CC                                         mov     ecx, esp        ; filepath
    .text:100CC129 DF4 89 65 A0                                      mov     [ebp-60h], esp
    .text:100CC12C DF4 57                                            push    edi             ; 
    .text:100CC12D DF8 E8 FE 5E 3B 00                                call    sub_10482030
    .text:100CC132 DF4 83 EC 14                                      sub     esp, 14h
    .text:100CC135 E08 8B CC                                         mov     ecx, esp
    .text:100CC137 E08 89 65 9C                                      mov     [ebp-64h], esp
    .text:100CC13A E08 FF 75 B4                                      push    dword ptr [ebp-4Ch]
    .text:100CC13D E0C E8 EE 5E 3B 00                                call    sub_10482030
    .text:100CC142 E08 8D 85 40 FB FF FF                             lea     eax, [ebp-4C0h] ; wxid
    .text:100CC148 E08 C6 45 FC 0F                                   mov     byte ptr [ebp-4], 0Fh
    .text:100CC14C E08 50                                            push    eax             ;
    .text:100CC14D E0C E8 AE F9 F9 FF                                call    sub_1006BB00
    .text:100CC152 E0C 8B C8                                         mov     ecx, eax
    .text:100CC154 E0C C6 45 FC 0C                                   mov     byte ptr [ebp-4], 0Ch
    .text:100CC158 E0C E8 83 C1 16 00                                call    sub_102382E0 //发送文件
    

接口大概是这个样子的。

    
        void __stdcall fakeWechatSendMsg1(int unk, wchar_t* wxid, int len1, int maxlen1, int unk1, int unk2, wchar_t* path, int len2, int maxlen2, int unk3, int unk4, int a1, int a2, int a3, int a4, int a5, int a6)
    

然后hook
sub_102382E0，拿到path文件路径后，获取文件大小，如果大于100M，则分割文件，然后重新调用sub_102382E0把分割文件发送出去。大概代码如下：

    
        bool fakeWechatSendMsgInternal(DWORD dwEcx, wchar_t* wxid, wchar_t* filepath)
    {
        int filesize = XxGetFileSize(filepath); //获取文件大小
        if (filesize > FILE_SIZE_100M) {
            return ExtendSendFile(dwEcx, wxid, filepath);
        }
        return false;
    }
    bool ExtendSendFile(DWORD dwEcx, wchar_t* wxid, WCHAR* filepath)
    {
        std::vector<std::wstring> filevec;
        if (SplitFile(filepath, filevec) && filevec.size() > 0) { //分割文件
            for (int i = 0; i < filevec.size(); i++) {
                SendFileMsg(wxid, (WCHAR*)filevec[i].c_str()); //发送分割文件
            }
            return true;
        }
        return false;
    }
    

OK，突破服务器100M限制也完成了（详细实现代码请移步SuperWeChatPC开源项目）。

  *   

  * 不过在测试中，发现bug多多（说的是微信）。
  *   

  * * 经测试自带单文件发送功能，100M，甚至99M、或者更小点的文件，发送到最后都没成功，微信bug or 网络问题？
  * * 96M左右可以成功，55M左右文件可以妙传，不稳定，这个可能网络问题，但是我怎么也是100M宽带啊。
  * * 自带多个文件同时发送，40M都无法发送成功。
  * * 有时还会提示：文件无法发送，已超过今日发送限制。
  * * 而此时选择10M以内文件依然能够发送成功。
  *   

  * 所以最后，我不得不面对现实，把文件分割成了每个10M大小的文件进行尝试，终于一个大于100M的文件发送成功了，并且非常稳定！![3.png](https://image.3001.net/images/20190815/1565852583_5d5503a7c83a2.png!small)  

### 3、总结

简单总结一下，我是如何让微信发送成功100M以上文件的。

  * 1\. 首先、突破本地100M限制，也就是选择100M文件限制，最终patch三个点绕过判断即可。
  * 2\. 然后，hook发送文件接口，把大于100M文件分割，然后自动发送小文件。
  * 3\. 最后，接收方自动合并文件（并没有做，哈哈）
  *   

  * 因为接收方并没有做自动合并的功能，所以需要自己合并一下，也很简单。
    
        //使用windows原生命令合并文件
    copy /b Test_100M.pdf._1+Test_100M.pdf._2+Test_100M.pdf._3 Test_100M.pdf
    

让这个功能更完美，还需要做：

  * 1\. 删除分割的小文件
  * 2\. 接收方自动合并文件
  * 3\. 微信修复bug，能够100M分割（@tencent @weixin)
  *   

  * 最后，想试用大文件传输功能，请下载最新的[](a%20href=)<https://github.com/anhkgg/SuperWeChatPC>。欢迎PR、star、试用。

  

