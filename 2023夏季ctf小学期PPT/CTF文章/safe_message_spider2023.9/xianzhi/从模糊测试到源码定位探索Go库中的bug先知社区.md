## 前言

go 经历了几次大的更新，自从去年 1.18 版本之后 go 更是官方发布了 fuzz
功能。已经有师傅写了[go语言原生模糊测试：源码分析和实战](https://xz.aliyun.com/t/11060)，师傅把源码都讲解的很明白。官方又出了一些新功能，比如已经原生支持生成语料库，将文件转成适合
go fuzz 的格式。

昨天跑了一下，找到了两处 bug
：第一个是官方的[webp](https://pkg.go.dev/golang.org/x/image/webp)，第二个是第三方库[iprange](https://pkg.go.dev/github.com/malfunkt/iprange#section-readme)

## webp

> 自生成语料库

在[官方文档](https://go.dev/security/fuzz/)中，提供了 file2fuzz 的方法，通过该方法来让语料库适配 go 原生
fuzz：

    
    
    $ go install golang.org/x/tools/cmd/file2fuzz@latest
    $ file2fuzz

可以转单个文件，也可以批量转文件夹：

[go-fuzz-corpus](https://github.com/dvyukov/go-fuzz-corpus)
这个语料库里涵盖非常全面。非常容易找到自己想 fuzz 的文件格式，而且这个库给的语料相当多样（原本是专门为 [go-fuzz](https://github.com/dvyukov/go-fuzz) 提供的语料库：

比如到它的一个具体文件格式的文件夹下：`❯ file2fuzz -o Fuzz*** corpus/*`，其中这个`Fuzz***`是 fuzz
函数具体名称，之后要把这个文件夹丢到 go fuzz 的工作目录：比如我的就是这样的：`mv Fuzz***
/Users/yourusername/Desktop/justfu/testdata/fuzz`，其中`testdata/fuzz`格式固定，相当于`justfu`是真正的工作目录

找个文件看下文件格式：

![](./img/4915112416479507066.png)

可以官方已经把我们需要的文件转成了 byte 格式，之后在我们的 fuzz 逻辑里边就可以自由发挥了：

    
    
    package test
    
    
    import (
        "bytes"
        // "strings"
        // "fmt"
        "golang.org/x/image/webp"
        "testing"
    )
    
    
    func FuzzReverse(f *testing.F) {
        f.Fuzz(func(a *testing.T, data []byte) {//接收参数
            _, err := webp.DecodeConfig(bytes.NewReader(data))//解析参数
            if err != nil {//没错就正常运行，有错误就直接退出
                return
            }
            if _, err := webp.Decode(bytes.NewReader(data)); err != nil {//解析参数
                return
            }
        })
    }
    
    
    ❯ go test -fuzz=Fuzz
    fuzz: elapsed: 1s, gathering baseline coverage: 0/1603 completed
    fuzz: elapsed: 4s, gathering baseline coverage: 1602/1603 completed
    fuzz: elapsed: 7s, gathering baseline coverage: 1602/1603 completed
    fuzz: elapsed: 10s, gathering baseline coverage: 1602/1603 completed

这里 fuzz 就看人品了，我试过有时候 fuzz 几个小时没有东西，有时候一个小时就直接 crash 了。我直接把让程序 hang
的文件提取出来了，写了个验证程序：

    
    
    package main
    
    //main.go
    import (
        "bytes"
        "fmt"
    
        "golang.org/x/image/webp"
    )
    
    func main() {
        data := []byte("RIFF0000WEBPVP8X\n\x00\x00\x000000000000ALPH\xf0\xffx\x00D")
        cfg, err := webp.DecodeConfig(bytes.NewReader(data))
        if err != nil {
            return
        }
        fmt.Println(cfg.Width)
        fmt.Println(cfg.Height)
        if _, err := webp.Decode(bytes.NewReader(data)); err != nil {
            return
        }
    }
    
    
    ❯ go run main.go
    3158065
    3158065
    3158064//这块是我改的源码，就是底下的 Println
    3158064
    fatal error: out of memory allocating heap arena metadata

研究了半天 webp 文件格式，发现 fuzz 出来的文件一堆 0 那块，代表了 heightMinusOne、widthMinusOne 的大小，然后
alpha 没有进行验证，直接 make 这么大的内存空间。

![](./img/6246119859837712530.png)

修复该 bug 的话：我想法是给个限制范围，通过 runtime 包把内存信息拿到，然后做判断。官方没有类似的讨论，我就去翻了翻 go 的 image
库，发现已经有师傅在2月份 PR
了：<https://github.com/golang/image/pull/14>。该师傅的想法是：加个传数据的逻辑，把直接 make
改成文件流的形式，如果 chunkdata 就是假的（损坏的文件，那就会失败。不然就正常进行。

![](./img/840497416457549341.png)

## iprange

> 语料库写死到代码中

这个是当时写扫描器的时候，用到的一个库，它能够从 nmap 格式的字符串中解析出 IPv4 地址，作者给的这个用法写的很明白：

![](./img/4455493637603065404.png)

我们稍微修改下提供的用法，就可以结合 Fuzz 把 bug 给扫出来：看下整体 fuzz 代码：

    
    
    package main//ip_test.go，必须以test结尾
    
    import (
        "github.com/malfunkt/iprange"
        "testing"
    )
    
    func FuzzReverse(f *testing.F) {
        testcases := []string{"10.0.0.1", "10.0.0.5-10", "192.168.1.*", "192.168.10.0/24"}
        for _, tc := range testcases {//直接进语料库
            f.Add(tc)
        }
        f.Fuzz(func(t *testing.T, orig string) {//接收参数
            _, err1 := iprange.ParseList(orig)//解析参数
            if err1 != nil {
                return//如果报错的话让他直接返回
            }
        })
    }

逐行扫一眼代码：

  * import 的包，需要包含项目所必须的包，还有个 testing
  * 就是一个 fuzz 代码：
    1. 将10.0.0.1..进语料库
    2. Fuzz 的参数，在这里就是一个 string ，保证 iprange.ParseList 接收到正确参数即可

直接运行，相信一下就能跑出结果：

    
    
    ❯ go test -fuzz=Fuzz
    fuzz: elapsed: 0s, gathering baseline coverage: 0/4 completed
    fuzz: elapsed: 0s, gathering baseline coverage: 4/4 completed, now fuzzing with 8 workers
    fuzz: elapsed: 3s, execs: 136078 (45344/sec), new interesting: 48 (total: 52)
    fuzz: elapsed: 6s, execs: 136078 (0/sec), new interesting: 48 (total: 52)
    fuzz: elapsed: 9s, execs: 168410 (10777/sec), new interesting: 50 (total: 54)
    fuzz: elapsed: 12s, execs: 304898 (45509/sec), new interesting: 51 (total: 55)
    fuzz: minimizing 37-byte failing input file
    fuzz: elapsed: 15s, minimizing
    fuzz: elapsed: 15s, minimizing
    --- FAIL: FuzzReverse (15.30s)
        --- FAIL: FuzzReverse (0.00s)
            testing.go:1485: panic: runtime error: index out of range [3] with length 0
                goroutine 43099 [running]:
                runtime/debug.Stack()
                    /usr/local/go/src/runtime/debug/stack.go:24 +0xbc
                testing.tRunner.func1()
                    /usr/local/go/src/testing/testing.go:1485 +0x264
                panic({0x100253da0, 0x1400672cd08})
                    /usr/local/go/src/runtime/panic.go:884 +0x204
                encoding/binary.bigEndian.Uint32(...)
                    /usr/local/go/src/encoding/binary/binary.go:157
                github.com/malfunkt/iprange.(*ipParserImpl).Parse(0x14007881200, {0x100265128?, 0x14007878640?})
                    yaccpar:351 +0x2888
                github.com/malfunkt/iprange.ipParse(...)
                    yaccpar:153
                github.com/malfunkt/iprange.ParseList({0x14007807a66?, 0x0?})
                    ip.y:93 +0xcc
                m.FuzzReverse.func1(0x1400c291718?, {0x14007807a66?, 0x0?})
                    /Users/housihan/Desktop/sensor/bigdata/waf2/m_test.go:14 +0x54
                reflect.Value.call({0x100230ba0?, 0x1002637a0?, 0x1400008ee38?}, {0x1001da54a, 0x4}, {0x140078840c0, 0x2, 0x0?})
                    /usr/local/go/src/reflect/value.go:586 +0x87c
                reflect.Value.Call({0x100230ba0?, 0x1002637a0?, 0x140000100c0?}, {0x140078840c0?, 0x100262e20?, 0x10032e670?})
                    /usr/local/go/src/reflect/value.go:370 +0x90
                testing.(*F).Fuzz.func1.1(0x14000010360?)
                    /usr/local/go/src/testing/fuzz.go:335 +0x360
                testing.tRunner(0x14007882340, 0x14007863320)
                    /usr/local/go/src/testing/testing.go:1576 +0x10c
                created by testing.(*F).Fuzz.func1
                    /usr/local/go/src/testing/fuzz.go:322 +0x4c4
    
    
        Failing input written to testdata/fuzz/FuzzReverse/f5de87321fd8b751
        To re-run:
        go test -run=FuzzReverse/f5de87321fd8b751
    FAIL
    exit status 1
    FAIL    m       16.590s

然后我们查看一下引发崩溃的字符串（也就是上边的`testdata/fuzz/FuzzReverse/f5de87321fd8b751`）：

    
    
    go test fuzz v1
    string("0.0.0.0/70")

其将掩码改成了 70，我们的 fuzz 逻辑已经把 err 给判断了，发现程序没有报错反而正常运行，之后直接引发了一个 panic。

顺着调用栈到源码里一探究竟。我在这把`/usr/local/go/src/encoding/binary/binary.go`源码改了下，查看具体变量。这块代码很不好跟，非常容易跑飞：

    
    
    func (bigEndian) Uint32(b []byte) uint32 {
        fmt.Println(b)//打印一下
        _ = b[3] // bounds check hint to compiler; see golang.org/issue/14808
        return uint32(b[3]) | uint32(b[2])<<8 | uint32(b[1])<<16 | uint32(b[0])<<24
    }
    
    
    ❯ go run main.go
    []//求他的b[3]必然直接索引越界
    panic: runtime error: index out of range [3] with length 0
    
    goroutine 1 [running]:
    encoding/binary.bigEndian.Uint32({}, {0x0, 0x0, 0x10423dda8?})
            /usr/local/go/src/encoding/binary/binary.go:159 +0x88
    github.com/malfunkt/iprange.(*ipParserImpl).Parse(0x140000c6000, {0x1041d03c8?, 0x140000bc050?})
            yaccpar:351 +0x12f8
    github.com/malfunkt/iprange.ipParse(...)
            yaccpar:153
    github.com/malfunkt/iprange.ParseList({0x10418ced9?, 0x140000021a0?})
            ip.y:93 +0xa0
    main.main()
            /Users/housihan/Desktop/sensor/bigdata/waf2/main.go:10 +0x28
    exit status 2

倒着推发现它用到了 net 的 CIDRMask 方法，去自己的`/usr/local/go/src/`看看 ones 和 bits：

    
    
    // CIDRMask returns an IPMask consisting of 'ones' 1 bits
    // followed by 0s up to a total length of 'bits' bits.
    // For a mask of this form, CIDRMask is the inverse of IPMask.Size.
    func CIDRMask(ones, bits int) IPMask {
        fmt.Println(ones)
        fmt.Println(bits)
        if bits != 8*IPv4len && bits != 8*IPv6len {
            return nil
        }
        if ones < 0 || ones > bits {//直接return nil
            return nil
        }
        l := bits / 8
        m := make(IPMask, l)
        n := uint(ones)
        for i := 0; i < l; i++ {
            if n >= 8 {
                m[i] = 0xff
                n -= 8
                continue
            }
            m[i] = ^byte(0xff >> n)
            n = 0
        }
        return m
    }
    
    ❯ go run main.go
    70
    32
    panic: runtime error: index out of range [3] with length 0

可以看到，只要是大于 32 事实上是直接返回 nil 的，所以会失败。我看了看师傅写的 test 代码，没考虑掩码大于 32 的情况，比如直接把
10.0.0.1/33 送进去就会报错：

    
    
    package main
    
    import (
        "log"
    
        "github.com/malfunkt/iprange"
    )
    
    func main() {
        list, err := iprange.ParseList("10.0.0.1/33")
        if err != nil {
            log.Printf("error: %s", err)
        }
        log.Printf("%+v", list)
    
        rng := list.Expand()
        log.Printf("%s", rng)
    }
    
    
    ❯ go run main.go
    panic: runtime error: index out of range [3] with length 0
    
    goroutine 1 [running]:
    encoding/binary.bigEndian.Uint32(...)
            /usr/local/go/src/encoding/binary/binary.go:157
    github.com/malfunkt/iprange.(*ipParserImpl).Parse(0x140001a4000, {0x102adc3c8?, 0x14000198050?})
            yaccpar:351 +0x14bc
    github.com/malfunkt/iprange.ipParse(...)
            yaccpar:153
    github.com/malfunkt/iprange.ParseList({0x102a98b79?, 0x140000021a0?})
            ip.y:93 +0xa0
    main.main()
            /Users/housihan/Desktop/sensor/bigdata/waf2/main.go:10 +0x28
    exit status 2

这个问题在18年就提出来了：<https://github.com/malfunkt/iprange/issues/1>。改起来可以先判断掩码，如果大于的话直接就报错然后
return ，或者强行限制到 32。

我给师傅 `y.go` 的 502 行加了个判断：

![](./img/7630870156624730745.png)

## 总结

go 原生的 fuzz 在快速发展，目前 github 上的讨论也十分活跃。但仍存在诸多限制，比如一个测试程序跑出 panic
会导致所有运行的测试程序一起掉。之后想重新跑还得先把造成 crash 的文件提取出来，再继续不然每次开始测试的时候因为每次都会去扫一遍 testdata
里的东西，还是会掉。

