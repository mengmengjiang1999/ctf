![](https://image.3001.net/images/20230614/1686735741_64898b7dcf04ecfca55d5.jpg!small)  

## 关于EntropyReducer

EntropyReducer是一款针对Payload隐蔽性增强的安全工具，在该工具的帮助下，广大研究人员能够有效地降低Payload的熵，并对Payload代码使用串行链表进行混淆处理。

## 工作机制

EntropyReducer的算法由 _BUFF_ __SIZE_和 _NULL_
__BYTES_的值决定，下图显示的是当BUFF_SIZE被设置为4且NULL_BYTES被设置为2时，EntropyReducer组织和处理Payload代码的流程方式：

![](https://image.3001.net/images/20230614/1686735910_64898c269c574e86a344d.jpg!small)

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Maldev-Academy/EntropyReducer.git

接下来，将项目代码导入至Visual Studio并进行代码编译即可。

## 工具使用

EntropyReducer可以直接通过命令行来读取原始的Payload文件，并将混淆处理后的版本以相同文件名（带.ER前缀）的形式写入到输出目录中。

经过混淆处理后的最终版本Payload大小取决于BUFF_SIZE和NULL_BYTES的值，计算方式如下：

    
    
    FinalSize = ((OriginalSize + BUFF_SIZE - OriginalSize % BUFF_SIZE ) / BUFF_SIZE) * (BUFF_SIZE + NULL_BYTES + sizeof(INT))

### 在自己的项目中使用EntropyReducer

我们可以直接将[ _EntropyReducer_ _.c_](https://github.com/Maldev-Academy/EntropyReducer/blob/main/PoC/EntropyReducer.c)和[ _EntropyReducer_
_.h_](https://github.com/Maldev-Academy/EntropyReducer/blob/main/PoC/EntropyReducer.h)文件导入至自己的项目中，并调用相关的混淆/
_反混淆_函数即可。

具体使用方法请参考项目提供的 _PoC_ _/main.c_文件。

## 工具输出样例

在下面的例子中，BUFF_SIZE被设置为了3，NULL_BYTES的值被设置为了1。

原始Payload的第一个数据块如下（FC 48 83）：

![](https://image.3001.net/images/20230614/1686735968_64898c600d895f7fd080f.png!small)

相同的Payload代码块，但位于不同的偏移量：

![](https://image.3001.net/images/20230614/1686735975_64898c67be3839dbe1469.png!small)

## 工具处理效果

Megasploit生成的x64 calc Shellcode的熵为5.883：

![](https://image.3001.net/images/20230614/1686735989_64898c7538fb9d023a307.png!small)

相同的文件使用AES加密后的熵为7.110：

![](https://image.3001.net/images/20230614/1686736017_64898c91900962bb98d57.png!small)

RC4算法处理相同文件后的熵结果为7.210：

![](https://image.3001.net/images/20230614/1686736038_64898ca6169dab7e39c13.png!small)

使用EntropyReducer处理相同文件后的熵为4.093：

![](https://image.3001.net/images/20230614/1686736055_64898cb724d0e912b40cc.png!small)

## 许可证协议

本项目的开发与发布遵循[ _Apache_ _-2_ _._ _0_](https://github.com/Maldev-Academy/EntropyReducer/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **EntropyReducer** ：【[ _GitHub传送门_](https://github.com/Maldev-Academy/EntropyReducer)】

## 参考资料

> [ _https://maldevacademy.com/_](https://maldevacademy.com/)
>
> [ _https://www.geeksforgeeks.org/merge-sort-for-linked-> list/_](https://www.geeksforgeeks.org/merge-sort-for-linked-list/)
>
> [
> _https://stackoverflow.com/a/9854707/15354012_](https://stackoverflow.com/a/9854707/15354012)
>
> [ _https://qr.ae/prZ6Lx_](https://qr.ae/prZ6Lx)
>
> [ _https://github.com/Leyxargon/c-linked-> list_](https://github.com/Leyxargon/c-linked-list)

