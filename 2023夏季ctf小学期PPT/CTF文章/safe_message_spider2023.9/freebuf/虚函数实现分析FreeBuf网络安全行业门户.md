C++中的虚函数的作用主要是实现了多态的机制。C++的虚函数主要通过虚表实现，虚表中存储有虚函数的入口地址，如果能改写虚表中地址则能控制程序执行流程，下面通过实际代码看一下虚函数的底层实现。

## 1、实验环境

Windows 7 X64

Visual C++ 6.0

IDA Pro 7.0

## 2、实验步骤

### 2.1 编译源代码

使用Visual C++ 6.0编译如下代码。

    
    
    #include "stdafx.h"
    
    #include "iostream.h"
    
    
    
    
    class MyClass
    
    {
    
    public:
    
    char buf[200];
    
    virtual void test1(void)
    
    {
    
    cout<<"virtual functions test1()."<<endl;
    
    }
    
    
    
    
    virtual void test2(void)
    
    {
    
    cout<<"virtual functions test2()."<<endl;
    
    }
    
    
    
    
    virtual void test3(void)
    
    {
    
    cout<<"virtual functions test3()."<<endl;
    
    }
    
    
    
    
    // 构造函数
    
    MyClass()
    
    {
    
    printf("This is constructor.\n");
    
    
    
    
    // 打印所有虚函数的地址
    
    printf("%p\n",&MyClass::test1);
    
    printf("%p\n",&MyClass::test2);
    
    printf("%p\n\n",&MyClass::test3);
    
    }
    
    
    
    
    // 析构函数
    
    ~MyClass()
    
    {
    
    printf("This is destructor.\n");
    
    }
    
    };
    
    
    
    
    int main(int argc,char*argv[])
    
    {
    
    printf("start of main()!\n\n");
    
    
    
    
    MyClass obj1,obj2;
    
    char *p_vtable;
    
    p_vtable=obj1.buf-4;//point to virtual table
    
    int pTemp =*(int *)(p_vtable);
    
    printf("p_vtable = 0x%X\n",pTemp);//得到虚函数表的地址ؖ
    
    printf("virtual function 1 address = 0x%X\n",*(int *)pTemp);
    
    printf("virtual function 2 address = 0x%X\n",*((int *)(pTemp+4)));
    
    printf("virtual function 3 address = 0x%X\n\n",*((int *)(pTemp+8)));
    
    
    
    
    
    
    
    p_vtable=obj2.buf-4;//point to virtual table
    
    pTemp =*(int *)(p_vtable);
    
    printf("p_vtable = 0x%X\n",pTemp);
    
    printf("virtual function 1 address = 0x%X\n",*(int *)pTemp);
    
    printf("virtual function 2 address = 0x%X\n",*((int *)(pTemp+4)));
    
    printf("virtual function 3 address = 0x%X\n\n",*((int *)(pTemp+8)));
    
    
    
    
    
    
    
    printf("end of main()!\n");
    
    return0;
    
    }

运行结果如图1所示，可见对象obj1的虚表中数值和对象obj2相同。

![](https://image.3001.net/images/20220829/1661763796_630c80d4e91f7ded3cf99.png!small)图1
结果输出

如图2所示为VC++调试时查看内存变量的窗口，可见对象obj1和obj2均存在一个__vfptr变量，值为0x00426110；该变量类型为指针，如图3所示。

从图2中可以查看，对象1的buf变量的地址为0x0018fe74，对象2的buf变量的地址为0x0018fda8，两个对象的buf变量地址并不相同，互不影响。

![](https://image.3001.net/images/20220829/1661763041_630c7de184e67760acf02.png!small)图2
VC调试窗口

![](https://image.3001.net/images/20220829/1661763136_630c7e40d9553cd7fed18.png!small)

图3 查看变量__vfptr的属性

如图4所示，查看0x00426110处内存，可见有3个地址值，分别为0x0040101E、0x00401019、0x00401014。

![](https://image.3001.net/images/20220829/1661763163_630c7e5b7eb998cb1dcdf.png!small)图4
Memory窗口

### 2.2 查看反汇编结果

我们使用IDA Pro查看0x0040101E处的内容，如图5所示，该二进制函数只要一条指令，即跳转到sub_401250。

![](https://image.3001.net/images/20220829/1661763258_630c7eba506d1e395ea32.png!small)

图5 0x0040101E处内容

![](https://image.3001.net/images/20220829/1661763322_630c7efac7cdfe29b6ac0.png!small)

图6 0x00401019处内容

如图7所示，二进制函数sub_401340即为虚函数test1(void)。

![](https://image.3001.net/images/20220829/1661763382_630c7f363cbdb3431544a.png!small)

图7 sub_401340二进制函数

综上，我们可知虚函数表是类对象之间共享的，而非每个对象都保存了一份，虚函数的实现如图8所示。

![](https://image.3001.net/images/20220829/1661763467_630c7f8bac335d76abb0e.png!small)图8
虚函数的实现

## 3、参考文献

《0day安全》

