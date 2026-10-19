今天来简单介绍一下逆向中常用到的另一个静态分析工具IDA，还是昨天那个打印demo（64位）：

#include  
#include  
char a[] = "https://www.vultop.com/";  
int main(int argc, char* argv[])  
{  
printf("%s", a);  
system("pause");  
return 0;  
}

因为是自己编写的代码，有符号文件，所以分析起来很方便，函数名都有：

![](https://image.3001.net/images/20230426/1682491759_6448c96f60fc0e928eb12.png!small)

在箭头这块ctrl+f，出现搜索框，直接搜索main：

![](https://image.3001.net/images/20230426/1682491760_6448c97042fefec8bc541.png!small)

在右边箭头位置按空格：

![](https://image.3001.net/images/20230426/1682491761_6448c971296de92596273.png!small)

可以看到我们的主函数代码，在这块按一下F5，就可以用到IDA中最强大方便的功能，俗称F5大法，会编译成成语言形式：

![](https://image.3001.net/images/20230426/1682491761_6448c971b68232df2be70.png!small)

对照源代码，基本流程很清晰。双击printf中的参数a：

![](https://image.3001.net/images/20230426/1682491762_6448c97246455fa436d1b.png!small)

按一下shift+f12就是字符串信息：

![](https://image.3001.net/images/20230426/1682491763_6448c97313f1704e26bef.png!small)

IDA其他页面都有名字，这里不再解释，接下来我们看一下没有符号文件的时候的IDA：

![](https://image.3001.net/images/20230426/1682491763_6448c973dc3aada311865.png!small)

![](https://image.3001.net/images/20230426/1682491764_6448c974b6cf9900fab81.png!small)

可以看到这里大部分函数名是sub_xxx,搜索main函数也是搜不到的：

![](https://image.3001.net/images/20230426/1682491765_6448c975d4494297f92c9.png!small)

这种情况我们只能从start开始找主函数，就像在OD里面找到主函数一样，当然也可以通过字符串叉查找。首先通过字符串查找一下：

![](https://image.3001.net/images/20230426/1682491766_6448c97687ddd692c061f.png!small)

双击：

![](https://image.3001.net/images/20230426/1682491767_6448c9776bd7f50e9afc7.png!small)

标记这串字符串，按ctrl+x，看看哪里引用了这段字符串：

![](https://image.3001.net/images/20230426/1682491768_6448c978702702d8e2740.png!small)

然后就到了主函数这里：

![](https://image.3001.net/images/20230426/1682491769_6448c979731616ad29cee.png!small)

F5就可以查看伪代码，接下来我们靠特征找一下，函数名搜索框搜索start：

![](https://image.3001.net/images/20230426/1682491770_6448c97a15168e8fe56ca.png!small)

![](https://image.3001.net/images/20230426/1682491770_6448c97aa2f5e4c51d435.png!small)

![](https://image.3001.net/images/20230426/1682491771_6448c97b350936f518a53.png!small)

![](https://image.3001.net/images/20230426/1682491771_6448c97be6f3a288aea12.png!small)

在这里按空格，方便查看，找下面这段代码：

![](https://image.3001.net/images/20230426/1682491772_6448c97c784d2cc1bad49.png!small)

进第二个call：

![](https://image.3001.net/images/20230426/1682491773_6448c97d81500b6a1c940.png!small)

进最后一个call，走进一个jmp，到了主函数这里：

![](https://image.3001.net/images/20230426/1682491774_6448c97e7ba9b21b5f5fb.png!small)

