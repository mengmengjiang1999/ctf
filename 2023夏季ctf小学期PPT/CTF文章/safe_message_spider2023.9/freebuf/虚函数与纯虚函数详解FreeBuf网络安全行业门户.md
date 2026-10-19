**学到了多态了，C++的多态就是让你领悟指针之美的地方**

# 虚函数

之前我们说一个对象调用成员函数是根据作用域来调用的，这其实不够严谨。在多态这边，我们运用到了虚函数，在这里函数的调用就和指针有关了。

虚函数就是在成员函数前面加一个virtual关键字。我们来看一下代码

    
    
    #include <iostream>
    using namespace std;
    
    class A
    {
    public:
        A();
        virtual void func();
    };
    A::A(){}
    void A::func()
    {
        cout << "this is A Func" << endl;
    }
    
    class B:public A
    {
    public:
        B();
        void func();
    };
    B::B(){}
    void B::func()
    {
        cout << "this is B Func" << endl;
    }
    
    int main()
    {
        A *a = new B();
        a->func();
    }
    
    

然后我们来看输出  
![image.png](https://image.3001.net/images/20211104/1635991488_61833fc0c11fab13b50ce.png!small)  
我们之前已经了解过，如果不加virtual关键字，a输出的应该是A的函数，但是加了virtual以后调用了B的函数。

前面我们也提到过成员函数的名字遮蔽，但是没有细说，在这里详细的讲一下。和变量名遮盖比较像，我们这次专门比较一下参数对函数调用的影响。

    
    
    #include <iostream>
    using namespace std;
    
    class A
    {
    public:
        A();
        void func();
    };
    A::A(){}
    void A::func()
    {
        cout << "this is A Func" << endl;
    }
    
    class B:public A
    {
    public:
        B();
    //    void func();
    };
    B::B(){}
    //void B::func()
    //{
    //    cout << "this is B Func" << endl;
    //}
    
    int main()
    {
        B *b = new B();
        b->func();
    }
    
    

首先运行一下这个代码，运行结果  
![image.png](https://image.3001.net/images/20211104/1635992082_61834212a0ea71f3bf0c1.png!small)  
然后我们把注释的地方加上  
![image.png](https://image.3001.net/images/20211104/1635992149_61834255231821866c8cc.png!small)  
发生了名字遮蔽，现在运行的是B的成员函数。我们再做一个小小的改变，在声明定义B的func函数的时候加上参数

    
    
    #include <iostream>
    using namespace std;
    
    class A
    {
    public:
        A();
        void func();
    };
    A::A(){}
    void A::func()
    {
        cout << "this is A Func" << endl;
    }
    
    class B:public A
    {
    public:
        B();
        void func(int a);
    };
    B::B(){}
    void B::func(int a)
    {
        cout << "this is B Func" << endl;
    }
    
    int main()
    {
        B *b = new B();
        b->func();
    }
    
    

然后再次运行的时候发生了报错  
![image.png](https://image.3001.net/images/20211104/1635992334_6183430e434e9f783d62e.png!small)  
那么我们就可以推测一下，只要B中出现了和A同名的成员函数，不管函数的参数列表是怎样的，都会将A的成员函数遮盖掉。

从这里我们引出了虚函数。当我们需要对函数名进行复用的时候，就用到了虚函数。用代码来举个例子

    
    
    #include <iostream>
    using namespace std;
    
    class Animal
    {
    public:
        virtual void func();
    };
    void Animal::func()
    {
        cout << "this is an animal." << endl;
    }
    
    class Dog:public Animal
    {
    public:
        void func();
    };
    void Dog::func()
    {
        cout << "this is a dog." << endl;
    }
    
    
    int main()
    {
        Animal *dog = new Dog();
        dog->func();
        return 0;
    }
    
    

一个很简单的例子，我们创建了animal类和dog类，当两者都需要用到func这个函数的时候virtual就起了作用。它让函数不在通过作用域来调用，实现了函数名的复用

虚函数基于函数名的遮盖，那么这个函数名的遮盖有什么特点吗？我们可以写代码来实现一下

    
    
    #include <iostream>
    using namespace std;
    
    class Animal
    {
    public:
        virtual void func();
        virtual void func(int a);
    };
    void Animal::func()
    {
        cout << "this is an animal." << endl;
    }
    
    void Animal::func(int a)
    {
        cout << "this is int of Animal" << endl;
    }
    
    class Dog:public Animal
    {
    public:
        void func();
        void func(string name);  //可以尝试把string name改成int a,int b
    
    };
    void Dog::func()
    {
        cout << "this is a dog." << endl;
    }
    void Dog::func(string name)  //可以尝试把string name改成int a,int b
    {
        cout << "this is a string func of dog" <<endl;
    }
    
    
    int main()
    {
        Animal *dog = new Dog();
        dog->func();
        dog->func(5);
    //    dog->func("qwe");
    //也可以换成两个数字作为参数
    
    //前面这一句会发生报错
        return 0;
    }
    
    
    

![image.png](https://image.3001.net/images/20211104/1635993407_6183473f61b4034b774f6.png!small)

代码中我们标记了几个会发生报错的地方，报错内容都是![image.png](https://image.3001.net/images/20211104/1635994012_6183499ce27787f11baa1.png!small)  
我们得出结论，派生类中但凡出现了名字遮盖，在基类中都需要有定义。尤其应该注意参数列表。

## 纯虚函数

我们只需要在虚函数后面加个=0就可以了。`virtual type
funcname()=0`。纯虚函数只需要声明不需要定义，具体的定义交给派生类。只要有一个纯虚函数，定义的类就被称为抽象类。抽象类不能被实例化。

这个感觉就有点像Java里的接口了，抽象类不仅有了虚函数中名称复用的特点，还有了Java里面接口的功能。直接看一个代码

    
    
    #include <iostream>
    using namespace std;
    
    class Animal
    {
    public:
        virtual void eat() = 0;
        virtual void speak() = 0;
    };
    
    class Cat_Family:public Animal
    {
    public:
        void eat();
    };
    void Cat_Family::eat()
    {
        cout << "I wang to eat meat" << endl;
    }
    
    class Cat:public Cat_Family
    {
    public:
        void speak();
    };
    void Cat::speak()
    {
        cout << "miao miao miao~" << endl;
    }
    
    class Tiger:public Cat_Family
    {
    public:
        void speak();
    };
    void Tiger::speak()
    {
        cout << "aowu~" << endl;
    }
    
    int main()
    {
        Animal *cat = new Cat();
        Animal *tiger = new Tiger();
        cat->eat();
        cat->speak();
        tiger->eat();
        tiger->speak();
    
    
        return 0;
    }
    
    

我们定义了动物类、猫科类、猫类和老虎类。其中动物类有两个纯虚函数，所以是一个抽象类。然后猫科类继承了动物类，但是只实现了一个纯虚函数，另外一个纯虚函数被继承了下来，所以猫科类也是一个抽象类。然后老虎类和猫类分别实现了speak函数  
![image.png](https://image.3001.net/images/20211104/1635995208_61834e4857588e4ff9961.png!small)

# 如何实现？

我们说过虚函数是通过指针进行的调用，那么具体是如何实现的？这里用到了虚函数表。之前我们学习过虚基类，是把基类的成员变量进行共享；这里的虚函数其实是把函数名进行共享，并且用到了虚函数表。

我们先来写一下代码

    
    
    #include <iostream>
    using namespace std;
    
    class Animal
    {
    public:
        Animal(int age,int big);
        virtual void what();
        virtual void food();
    protected:
        int m_age;
        int m_big;
    };
    Animal::Animal(int age,int big):m_age(age),m_big(big){}
    void Animal::food()
    {
        cout << "I want to eat everything" << endl;
    }
    void Animal::what()
    {
        cout << "This is an Animal" <<endl;
    }
    
    class Mammals:public Animal
    {
    public:
        Mammals(int age,int big,int speed);
        virtual void what();
        virtual void eat();
    protected:
        int m_speed;
    };
    Mammals::Mammals(int age,int big,int speed):Animal(age,big),m_speed(speed){}
    void Mammals::what()
    {
        cout << "this is a Mammals" << endl;
    }
    void Mammals::eat()
    {
        cout << "I will eat Fish" << endl;
    }
    
    class Whale:public Mammals
    {
    public:
        Whale(int age,int big,int speed);
        virtual void what();
        virtual void hobby();
    };
    
    Whale::Whale(int age,int big,int speed):Mammals(age,big,speed){}
    void Whale::what()
    {
        cout << "This is a Whale" << endl;
    }
    void Whale::hobby()
    {
        cout << "I can swim" << endl;
    
    }
    
    
    int main()
    {
        Animal *a = new Animal(5,50);
        a->what();
        a = new Mammals(6,60,600);
        a->what();
        a = new Whale(7,70,700);
        a->what();
    }
    
    

一个比较简单的代码，然后我们来看一下运行结果  
![image.png](https://image.3001.net/images/20211104/1636003661_61836f4d9ee842c348d94.png!small)  
但是我们如果加上这么几句

    
    
    int main()
    {
        Animal *a = new Animal(5,50);
    
        a->what();
        a = new Mammals(6,60,600);
        a->eat();
        a->what();
        a = new Whale(7,70,700);
        a->hobby();
        a->what();
    }
    

![image.png](https://image.3001.net/images/20211104/1636003736_61836f9805c4a70ec77f8.png!small)  
这时发生了报错。当我们进行实例化的时候，会在成员变量的正上方，也就是第一个成员变量的相邻低地址处增加一个虚函数指针，这个虚函数指针会指向虚函数表。

![image.png](https://image.3001.net/images/20211104/1636004347_618371fb7fdb2e5c057c6.png!small)  
就像这样，Animal的对象的顶部有一个虚函数表指针，指向了虚函数表的首地址。而它的派生类，如果有同名遮盖的函数名，则会在原位置进行遮盖；新增的函数则会放到最下面，就像下图  
![image.png](https://image.3001.net/images/20211104/1636004674_618373421e62eb1eb8d9b.png!small)  
同理可得Whale类对象的内存结构  
![image.png](https://image.3001.net/images/20211104/1636004765_6183739d99c9b929b4134.png!small)

有了这样的内存结构，编译器进行编译的时候会很方便，遵循一个公式，假设对象的头指针为p：*
(*(p+0)+x)(参数列表)，其中x代表虚函数表距离头指针的偏移。

**到这里虚函数就结束了，不过还是要记住，对象的访问一定是遵循只能访问该访问的，前面的报错就是因为我们明明是Animal类型却想要访问其它类型的成员函数！**

