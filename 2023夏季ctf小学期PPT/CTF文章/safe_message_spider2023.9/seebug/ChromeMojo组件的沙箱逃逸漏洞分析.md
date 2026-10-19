**作者：天玄安全实验室**  
**原文链接：<https://mp.weixin.qq.com/s/tGwCwOQ8eAwm26fHXTCy5A>**

## 漏洞说明

Issue-1062091为chrom中存在的一个UAF漏洞，此漏洞存在于chromium的Mojo框架中，利用此漏洞可以导致chrome与基于chromium的浏览器沙箱逃逸。这个漏洞是在Chrome
81.0.4041.0的提交中引入的。在几周后，这个提交中的漏洞恰好移动到了实验版本命令行标志的后面。但是，这个更改位于Chrome
82.0.4065.0版本中， **因此该漏洞在Chrome稳定版本81的所有桌面平台上都是可以利用的。**

## 环境配置

一开始打算像调试v8漏洞那样尝试用fetch拉取代码编译带有漏洞的chromium，但是发现chromium源码下载太慢且太大，故直接下载编译好的chromium，地址:vikyd.github.io
![图片](https://images.seebug.org/content/images/2022/04/06/1649226437000-1xlzjy.png-w331s)

下载时除了chromium本体以外还需要将其pdb符号也一起下载
![图片](https://images.seebug.org/content/images/2022/04/06/1649226437000-2qrfzs.png-w331s)

下载好后直接将pdb符号文件与exe执行文件解压放在一起即可
![图片](https://images.seebug.org/content/images/2022/04/06/1649226438000-3wttyz.png-w331s)

最后用windbg验证是否可以正常查找函数
![图片](https://images.seebug.org/content/images/2022/04/06/1649226438000-4qmaje.png-w331s)
注：下载以上内容都需要代理

## 漏洞分析

### POC

由于poc目录结构比较复杂，直接给出完整poc下载地址(需要代理)：bugs.chromium.org下载解压后可以得到两个html文件，其中trigger.html为我们需要的poc
![图片](https://images.seebug.org/content/images/2022/04/06/1649226438000-5gwell.png-w331s)

然后尝试触发漏洞，根据说明得知chrome默认不会启用mojo，想要启用有两种方法: 一、在命令行启动chromium时加上`--enable-blink-features=MojoJS,MojoJSTest`参数。二、利用另一个漏洞去改写当前Frame对象内部的一个变量`content::RenderFrameImpl::enabled_bindings_`让Frame拥有调用MojoJS的能力，通过以下路径可以得到该变量：

    
    
    chrome.dll base => g_frame_map => RenderFrameImpl(main frame) => RenderFrameImpl.enabled_bindings_

关于改写变量部分具体可查看SCTF202中的0x02 exploit部分，在实际利用漏洞进行攻击时肯定采用第二种方式，而此时仅需要分析利用Issue
1062091漏洞即可，所以先不去过分关心mojo开启的问题，直接采用第一种方法开启mojo。使用windbg进行调试
![图片](https://images.seebug.org/content/images/2022/04/06/1649226438000-6puokr.png-w331s)

在调试开始前由于当前工作目录的问题需要将poc代码中以下两处路径进行一些改动
![图片](https://images.seebug.org/content/images/2022/04/06/1649226438000-7twdsc.png-w331s)

然后用`.childdbg 1`开启子进程调试
![图片](https://images.seebug.org/content/images/2022/04/06/1649226439000-8lnuvj.png-w331s)

之后经过几个`ntdll!LdrpDoDebuggerBreak`后就会触发crash
![图片](https://images.seebug.org/content/images/2022/04/06/1649226439000-9liyzz.png-w331s)

## 漏洞分析

通过观察异常信息可判断此处并非漏洞触发的第一现场，使用gflags.exe开启页堆(+hpa)与堆栈跟踪(+ust)并在启动chrome时添加--no-sandbox参数进行调试分析会发现崩溃点会转移到前一句代码

![图片](https://images.seebug.org/content/images/2022/04/06/1649226439000-10oigob.png-w331s)
![图片](https://images.seebug.org/content/images/2022/04/06/1649226439000-11gzici.png-w331s)

再结合代码可以判断发生崩溃的地方是在获取render_frame_host_对象虚表
![图片](https://images.seebug.org/content/images/2022/04/06/1649226439000-12zouho.png-w331s)

使用!address查看该render_frame_host_对象内存信息会发现该内存已被释放
![图片](https://images.seebug.org/content/images/2022/04/06/1649226440000-13uefls.png-w331s)

通过观察发现render_frame_host_对象在InstalledAppProviderImpl对象在构造时被初始化
![图片](https://images.seebug.org/content/images/2022/04/06/1649226440000-14yebwp.png-w331s)
![图片](https://images.seebug.org/content/images/2022/04/06/1649226440000-15ssftz.png-w331s)

对content::InstalledAppProviderImpl::Create函数下断，当执行到以下内容时将会创建InstalledAppProviderImpl对象
![图片](https://images.seebug.org/content/images/2022/04/06/1649226440000-16beyez.png-w331s)

而render_frame_host_保存在InstalledAppProviderImpl对象0x8偏移处
![图片](https://images.seebug.org/content/images/2022/04/06/1649226441000-17faoii.png-w331s)

再结合poc可以确定InstalledAppProviderImpl对象是在sub frame调用bindInterface进行接口绑定时创建的
![图片](https://images.seebug.org/content/images/2022/04/06/1649226441000-18issza.png-w331s)

在之后的poc执行中，父帧会通过MojoInterfaceInterceptor拦截并获取子帧的句柄
![图片](https://images.seebug.org/content/images/2022/04/06/1649226441000-19akllt.png-w331s)

获取后便会调用body.removeChild删除子帧
![图片](https://images.seebug.org/content/images/2022/04/06/1649226441000-20qhocq.png-w331s)
![图片](https://images.seebug.org/content/images/2022/04/06/1649226441000-21jyfao.png-w331s)

最后会通过filterInstalledApps函数去调用已经被释放的render_frame_host_对象的虚函数
![图片](https://images.seebug.org/content/images/2022/04/06/1649226442000-22ypnop.png-w331s)

总结poc的执行顺序大致为：

  * 通过window.location.hash判断是否是子帧
  * 如果是子帧就去执行Mojo.bindInterface
  * 如果是父帧就去创建子帧并用MojoInterfaceInterceptor拦截子帧的Mojo.bindInterface到并将其句柄传递给父帧
  * 释放子帧
  * 使用filterInstalledApps去调用已经被释放但却依然还留有悬挂指针的render_frame_host_虚函数

## 漏洞利用

### 开启Mojo

上文中提到过chrome默认不能直接调用mojo，所以此处使用cve
2021-21224来配合开启mojo。通过分析可知mojoJS的开启与关闭主要由RenderFrameImpl类成员变量enabled_bindings_与IsMainFrame函数来决定
![图片](https://images.seebug.org/content/images/2022/04/06/1649226442000-23gbryf.png-w331s)

IsMainFrame函数的逻辑很简单就只是将一个类成员变量返回
![图片](https://images.seebug.org/content/images/2022/04/06/1649226442000-24vqmjw.png-w331s)

而通过调试也可知当enabled_bindings_ & 2不为0时即可满足条件
![图片](https://images.seebug.org/content/images/2022/04/06/1649226442000-25pkopj.png-w331s)

也就是说此时只需要将enabled_bindings_修改为2，再将is_main_frame_修改为1即可满足条件开启mojo。而在一个页面中可能会存在多个frame，而这些frame所对应的RenderFrameImpl对象都存储在一个全局变量g_frame_map中
![图片](https://images.seebug.org/content/images/2022/04/06/1649226443000-26nbpao.png-w331s)

要查找到全局变量g_frame_map，就需要先获取到chrome.dll的基址，利用21224构造的地址泄露函数与读写原语，泄露window对象地址，再从window对象中获取到一个位于chrome.dll模块中的地址，再用该地址减去一定的偏移来得到chrome.dll模块基址，除此以外还可以用特征码查找的方式，这种方式兼容性会更好，但在我的环境下读写原语在进行频繁的读写操作时会产生异常发生崩溃，具体原因暂时未知，所以姑且使用减去固定偏移获取基址的办法。
![图片](https://images.seebug.org/content/images/2022/04/06/1649226443000-27kkeye.png-w331s)
![图片](https://images.seebug.org/content/images/2022/04/06/1649226443000-28mekms.png-w331s)

之后由于无法直接通过g_frame_map符号在windbg中使用x来查找其地址，那就通过查找调用过该全局变量的函数来查找
![图片](https://images.seebug.org/content/images/2022/04/06/1649226443000-29egtbp.png-w331s)

之后在windbg中查找RenderFrame::ForEach并查看其汇编代码获取到g_frame_map地址为00007ffe`3d927888，用此值减去chrome基址得到偏移为0x7627888，只要使用chrome基址加0x7627888即可得到g_frame_map地址
![图片](https://images.seebug.org/content/images/2022/04/06/1649226444000-30qvmyo.png-w331s)

g_frame_map变量8-16偏移处存放着一个链式结构，当只有一个frame时
![图片](https://images.seebug.org/content/images/2022/04/06/1649226444000-31lmgai.png-w331s)

创建sub frame后
![图片](https://images.seebug.org/content/images/2022/04/06/1649226444000-32xsyrd.png-w331s)

而其对应的RenderFrameImpl对象保存在红线划出内存地址的0x28偏移处
![图片](https://images.seebug.org/content/images/2022/04/06/1649226444000-33jqdcd.png-w331s)

再通过观察content::RenderFrameImpl::DidCreateScriptContext函数来获取相关变量在对象中的偏移，enabled_bindings_偏移为0x560
![图片](https://images.seebug.org/content/images/2022/04/06/1649226445000-34eunho.png-w331s)

IsMainFrame函数中用到的have_context_变量偏移为0x88
![图片](https://images.seebug.org/content/images/2022/04/06/1649226445000-35ubdxx.png-w331s)

将g_frame_map中保存的所有RenderFrameImpl对象相应偏移修改为对应的值即可。但要注意的是在我的漏洞环境（
81.0.4044.0）中，在获取成员变量enabled_bindings_时需要将g_frame_map中拿到的RenderFrameImpl对象地址加0x68再加enabled_bindings_所在偏移，而IsMainFrame中用到的成员变量就在g_frame_map中拿到的RenderFrameImpl对象的0x88偏移处。
![图片](https://images.seebug.org/content/images/2022/04/06/1649226445000-36mrluh.png-w331s)

### 内存回收

对于uaf漏洞利用的第一步肯定是将此内存进行回收，而进行内存回收的前提就是先需要知道被释放的render_frame_host_占多大内存，通过前面的调试分析得知render_frame_host_为RenderFrameHostImpl类实例，所以可以先对RenderFrameHostImpl构造函数下断，而实例大小从构造函数是看不出来的，但可以从调用该实例构造函数的函数中看到。通过kb栈回溯查看调用RenderFrameHostImpl构造函数的函数为RenderFrameHostFactory::Create
![图片](https://images.seebug.org/content/images/2022/04/06/1649226445000-37yeyls.png-w331s)

通过查看该函数可知render_frame_host_对象大小为0xC38字节
![图片](https://images.seebug.org/content/images/2022/04/06/1649226445000-38mqrkr.png-w331s)
在知道了要回收的内存大小后就可以通过创建一系列的Blob来回收该内存

    
    
    var spray_buff = new ArrayBuffer(0xC38);
    var spray_view = new DataView(spray_buff);
    for(var i = 0; i < spray_buff.byteLength; i++)
     spray_view.setInt8(i, 0x41, true);
    //释放子帧
    for(var i = 0; i < 0xA; i++)
     spray_arr[i] = new Blob([spray_buff]);

![图片](https://images.seebug.org/content/images/2022/04/06/1649226446000-39dyyfg.png-w331s)
但此方法稳定性不足，不能保证能成功进行内存回收，更好的办法是采用已经被封装好的函数

    
    
     function getAllocationConstructor() {
            let blob_registry_ptr = 
              new blink.mojom.BlobRegistryPtr();
            Mojo.bindInterface(blink.mojom.BlobRegistry.name,
                                mojo.makeRequest(
                                  blob_registry_ptr)
                                  .handle, "process", true);
    
            function Allocation(size=280) {
              function ProgressClient(allocate) {
                function ProgressClientImpl() {
                }
                ProgressClientImpl.prototype = {
                  onProgress: async (arg0) => {
                    if (this.allocate.writePromise) {
                      this.allocate.writePromise.resolve(arg0);
                    }
                  }
                };
                this.allocate = allocate;
    
                this.ptr = new mojo.AssociatedInterfacePtrInfo();
                var progress_client_req = mojo.makeRequest(this.ptr);
                this.binding = new mojo.AssociatedBinding(
                  blink.mojom.ProgressClient, 
                  new ProgressClientImpl(), 
                  progress_client_req
                );
    
                return this;
              }
    
              this.pipe = Mojo.createDataPipe({
                elementNumBytes: size, capacityNumBytes: size});
              this.progressClient = new ProgressClient(this);
              blob_registry_ptr.registerFromStream(
                "", "", size, this.pipe.consumer, 
                this.progressClient.ptr).then((res) => {
                this.serialized_blob = res.blob;
              })
    
              this.malloc = async function(data) {
                promise = new Promise((resolve, reject) => {
                  this.writePromise = {resolve: resolve, reject: reject};
                });
                this.pipe.producer.writeData(data);
                this.pipe.producer.close();
                written = await promise;
                console.assert(written == data.byteLength);
              }
    
              this.free = async function() {
                this.serialized_blob.blob.ptr.reset();
                await sleep(1000);
              }
    
              this.read = function(offset, length) {
                this.readpipe = Mojo.createDataPipe({
                  elementNumBytes: 1, capacityNumBytes: length});
                this.serialized_blob.blob.readRange(
                  offset, length, this.readpipe.producer, null);
                return new Promise((resolve) => {
                  this.watcher = this
                  .readpipe
                  .consumer
                  .watch({readable: true}, (r) => {
                    result = new ArrayBuffer(length);
                    this.readpipe.consumer.readData(result);
                    this.watcher.cancel();
                    resolve(result);
                  });
                });
              }
    
              this.readQword = async function(offset) {
                let res = await this.read(offset, 8);
                return (new DataView(res)).getBigUint64(0, true);
              }
    
              return this;
            }
    
            async function allocate(data) {
              let allocation = 
                new Allocation(data.byteLength);
              await allocation.malloc(data);
              return allocation;
            }
            return allocate;
          }
          //.....
          let allocate = getAllocationConstructor();
            function spray(data) {
              return Promise
              .all(Array(0x8)
                .fill()
                .map(() => allocate(data)));
            }
            // 释放
            let ptr = await getFreedPtr();
            // 回收
            let sa  = await spray(spray_buff);
            // 触发漏洞

### 避免崩溃

#### 堆地址泄露

此时由于原本存放render_frame_host_对象的内存现在被blob所占用，所以当调用render_frame_host_对象虚函数GetProcess时就会去调用spray_buff中的元素值+0x48处，而spray_buff对应位置值为0x4141414141414141所以此时依然会触发崩溃
![图片](https://images.seebug.org/content/images/2022/04/06/1649226446000-40arviq.png-w331s)

所以此时需要填入相应的函数地址，保证在执行GetProcess与GetBrowserContest两个虚函数时不会发生崩溃，并在执行IsOffTheRecord时能够泄露堆地址。通过查找可以首先找到一个符合条件的函数ChromeMainDelegate::CreateContentClient，此函数会将this+8处地址返回给调用者，可以将此函数地址填入堆喷占位的数据中，在调用GetProcess与GetBrowserContext虚函数时就回去调用此函数。
![图片](https://images.seebug.org/content/images/2022/04/06/1649226446000-41fbxic.png-w331s)

再查找到ChromeMainDelegate类虚表
![图片](https://images.seebug.org/content/images/2022/04/06/1649226447000-42xnobp.png-w331s)

查看虚表得知ChromeMainDelegate::CreateContentClient函数地址存放在起虚表的0x70偏移处。
![图片](https://images.seebug.org/content/images/2022/04/06/1649226447000-43apfpk.png-w331s)

而InstalledAppProviderImpl::FilterInstalledApps在调用虚函数GetProcess时会从内存中获取一个地址将其加0x48并在此处获取一个函数去执行，所以可以将ChromeMainDelegate虚表地址+(0x70-0x48)填入堆喷数据中，当InstalledAppProviderImpl::FilterInstalledApps去调用GetProcess时就会转入ChromeMainDelegate::CreateContentClient函数
![图片](https://images.seebug.org/content/images/2022/04/06/1649226447000-44romcw.png-w331s)

在ChromeMainDelegate::CreateContentClient函数执行后会将堆喷数据地址+8偏移处的地址读出并再读出该地址0xD0偏移处的地址并调用，此处对应GetBrowserContext虚函数调用。于是可以将ChromeMainDelegate虚表地址-(0xD0-0x70)填入堆喷数据中当GetBrowserContext被调用时会再次转入ChromeMainDelegate::CreateContentClient函数
![图片](https://images.seebug.org/content/images/2022/04/06/1649226447000-45ylsma.png-w331s)

最后在调用虚函数IsOffTheRecord时需要找到一个可以泄露堆地址的函数填入相应位置，通过查找找到符合条件的虚函数content::WebContentsImpl::GetWakeLockContext，由于此函数还会将this指针填入堆地址+0x8偏移处，所以也可以为后续的this地址泄露提供方便。
![图片](https://images.seebug.org/content/images/2022/04/06/1649226448000-46kfnpp.png-w331s)
![图片](https://images.seebug.org/content/images/2022/04/06/1649226448000-47rmbip.png-w331s)

此函数会创建一块内存用作对象内存，并会将此内存地址写入this+0x10+0x650偏移处，也就是堆喷占位数据的0x660偏移处
![图片](https://images.seebug.org/content/images/2022/04/06/1649226448000-48fjliq.png-w331s)
![图片](https://images.seebug.org/content/images/2022/04/06/1649226448000-49lgbce.png-w331s)

但要注意的是content::WebContentsImpl::GetWakeLockContext函数会先去判断this+0x10+0x650偏移处是否为0，如果为0才可以进行创建堆内存并写入this+0x10+0x650的操作
![图片](https://images.seebug.org/content/images/2022/04/06/1649226448000-50mobou.png-w331s)

通过以上操作，在经过`render_frame_host_->GetProcess()->GetBrowserContext()->IsOffTheRecord()`后就可以在堆喷占位数据的0x660偏移处得到一个需要的堆地址

#### this地址泄露

由于在上一步操作中已经泄露了堆地址并且还将this指针写入了堆地址+0x8偏移处，所以可以利用前面泄露堆地址的思路将UAF漏洞再触发一次，并把之前拿到的泄露的堆地址写入堆喷占位数据的对应偏移处即可获取到this指针，由于前面的漏洞利用this指针正好指向我们可控的堆喷占位数据，拿到了this地址也就得到了当前可控数据的地址。继续将ChromeMainDelegate::CreateContentClient函数放入GetProcess与GetBrowserContext函数对应的调用位置，现在只需要再找到一个符合条件可以将this指针从堆地址中获取到的函数，通过查找找到`anonymous
namespace'::DictionaryIterator::Start`函数正好符合要求。
![图片](https://images.seebug.org/content/images/2022/04/06/1649226448000-51qpbcw.png-w331s)

结合调试再通过与泄露堆地址一样再次触发UAF漏洞便可得到this指针
![图片](https://images.seebug.org/content/images/2022/04/06/1649226449000-52vcdtz.png-w331s)
![图片](https://images.seebug.org/content/images/2022/04/06/1649226449000-53njxfa.png-w331s)

### 沙盒逃逸

沙河逃逸的思路比较简单，通过回调去执行SetCommandLineFlagsForSandboxType函数将--no-sandbox参数添加到current_process_commandline_中。首先需要找到一个可以调用回调函数的虚函数，通过查找找到content::responsiveness::MessageLoopObserver::DidProcessTask函数
![图片](https://images.seebug.org/content/images/2022/04/06/1649226449000-54xfmzz.png-w331s)

现在再找到一个可以传递多个参数的回调函数，类似如下形式的
![图片](https://images.seebug.org/content/images/2022/04/06/1649226449000-55uinhu.png-w331s)

然后将SetCommandLineFlagsForSandboxType函数地址填入被泄露了地址的buffer的相应偏移处就可以将沙箱关闭，但调用SetCommandLineFlagsForSandboxType函数还需要先得到全局变量current_process_commandline_
![图片](https://images.seebug.org/content/images/2022/04/06/1649226449000-56kugtg.png-w331s)

通过extensions::SizeConstraints::set_minimum_size函数将current_process_commandline_中保存的指针拷贝进前文中已经被泄露地址的可控地址中。
![图片](https://images.seebug.org/content/images/2022/04/06/1649226450000-57aefbo.png-w331s)

最后调用SetCommandLineFlagsForSandboxType函数，将--no-sandbox(0)标志添加进全局变量current_process_commandline_中
![图片](https://images.seebug.org/content/images/2022/04/06/1649226450000-58kftau.png-w331s)

最后生成新的渲染器过程（例如，使用iframe到其他受控原点或开启新的Tab），并再次使用渲染器漏洞利用(刷新)即可成功。
![图片](https://images.seebug.org/content/images/2022/04/06/1649226450000-59xoryr.png-w331s)

## 总结

  * 21224漏洞触发后在触发1062091前浏览器就产生崩溃——手动delete清理掉oob数组
  * 在开启mojo时修改RenderFrameImpl对象相应变量导致页面崩溃——21224中构造的读写原语在循环体中同时频繁读写会导致此问题，去掉部分不必要的读或写操作
  * 将相应成员变量值写入对应的RenderFrameImpl对象偏移后mojo依然没有开启——在 81.0.4044.0版本chromium中在写入enabled_bindings_时需要将g_frame_map中拿到的RenderFrameImpl对象地址加0x68再加enabled_bindings_所在偏移，而IsMainFrame中用到的成员变量就在g_frame_map中拿到的RenderFrameImpl对象的0x88偏移处。
  * 原POC中用到的MojoInterfaceInterceptor需要开启MojoJSTest绑定才能使用——使用其他方法传递sub frame中的句柄给main frame，例如在sub frame的onload事件中使用contentWindow获取其句柄再传递给main frame，但此方法直接在本地执行时会出现跨域的问题需要起一个服务器去访问执行。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1876/>

