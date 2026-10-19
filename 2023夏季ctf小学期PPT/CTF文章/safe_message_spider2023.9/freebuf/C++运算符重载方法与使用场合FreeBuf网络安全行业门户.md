## 运算符重载方法

为了重载运算符，必须定义一个函数，并告诉编译器，遇到这个运算符就调用该函数，由这个函数来完成该运算符应该完成的操作。这种函数称为运算符重载函数，也就是说，运算符重载是通过定义函数来实现的。  
重载运算符的函数一般格式如下：

函数类型 operator 运算符名称（形参列表）  
{  
对运算符的重载处理  
}

例子：

    
    
    #include<iostream>
    using namespace std;
    
    class Time
    {
    private:
    	int hour;
    	int minute;
    
    public:
    	Time()
    	{
    		hour = 0;
    		minute = 0;
    	}  //定义构造函数
    	Time(int h,int m);  //重载构造函数
    	Time add(Time &t2);
    	void display();
    };
    
    Time::Time(int h,int m)
    {
    	hour = h;
    	minute = m;
    }
    
    Time Time::add(Time &t2)
    {
    	Time t;
    	t.hour = hour + t2.hour;
    	t.minute = minute + t2.minute;
    	if(t.minute >= 60)
    	{
    		t.minute -= 60;
    		t.hour++;
    	}
    	return t;
    }
    void Time::display()
    {
    	cout << hour << " hour " << minute << " minute" << endl;
    }
    
    int main()
    {
    	Time t1(3,30),t2(2,40),t;
    	t = t1.add(t2);
    	cout << "t1+t2=";
    	t.display();
    	return 0;
    }
    

结果：  
![image.png](https://image.3001.net/images/20210602/1622626692_60b751846b103bf59ac29.png!small)  
从上例中看出，上述的方法调用方式不直观、太繁琐，很不方便。能否和整数的加法运算一样，直接用加号“+”来实现时间的相加运算呢？也就是说，只要写表达式t=t1+t2，编译系统就会自动完成t1和t2两个对象相加的运算。这就需要利用运算符重载函数。按照运算符重载函数的定义格式，对其的程序修改如下。

代码：

    
    
    #include<iostream>
    using namespace std;
    
    class Time
    {
    private:
    	int hour;
    	int minute;
    
    public:
    	Time()
    	{
    		hour = 0;
    		minute = 0;
    	}  //定义构造函数
    	Time(int h,int m);  //重载构造函数
    	Time operator+(Time &t2);  //声明重载运算符+的函数
    	void display();
    };
    
    Time::Time(int h,int m)
    {
    	hour = h;
    	minute = m;
    }
    
    Time Time::operator+(Time &t2)  //定义运算符+在重载函数
    {
    	Time t;
    	t.hour = hour + t2.hour;
    	t.minute = minute + t2.minute;
    	if(t.minute >= 60)
    	{
    		t.minute -= 60;
    		t.hour++;
    	}
    	return t;
    }
    void Time::display()
    {
    	cout << hour << " hour " << minute << " minute" << endl;
    }
    
    int main()
    {
    	Time t1(3,30),t2(2,40),t;
    	t = t1 + t2;
    	cout << "t1+t2=";
    	t.display();
    	return 0;
    }
    

结果：  
![image.png](https://image.3001.net/images/20210602/1622626707_60b751934a0b1ec10b15c.png!small)  
第一个例子是采用的普通成员函数进行调用求解的方法，这个例子采用的是运算符重载函数进行调用求解的方法，两种函数的运用需要注意以下几点：  
（1） 两种函数均为类的成员函数，运算符重载函数的调用t1+t2可以解释为t1对象调用成员函数operator+，即t1.operator+（t2）。  
（2） 两者实现的功能相同，都是实现两个时间类对象的相加。  
（3） 运算符重载函数的使用可读性好，普通函数的使用可读性较差。  
此外，还可以看出运算符被重载后，其原有的功能仍然保留，没有丧失或者改变。而通过运算符重载，扩大了C++已有运算符的作用范围，使之能用于类对象。把运算符重载和类结合起来，可以在C++程序中定义出很有实用意义而且使用方便的新的数据类型，也使C++具有更强大的功能、更好的可扩充性和适应性。

## 运算符重载函数使用场合

对于很多运算符来说，可以选择使用成员函数或者非成员函数来实现运算符重载。因此需要注意两种函数的使用场合

### 1.运算符重载函数作为成员函数

如果将运算符重载函数作为成员函数，它可以通过this指针自由地访问本类的成员变量，因此可以少写一个函数的参数。但必须要求运算表达式第一个参数（即运算符左侧的操作数）是一个类对象，而且与运算符重载函数的类型相同。

    
    
    代码：
    #include<iostream>
    using namespace std;
    
    class Complex
    {
    public:
    	Complex()
    	{
    		real = 0;
    		imag = 0;
    	}
    	Complex(double r,double i)
    	{
    		real = r;
    		imag = i;
    	}
    	Complex operator+(Complex &c2)  //重载为类成员函数
    	{
    		Complex c;
    		c.real = real + c2.real;
    		c.imag = imag + c2.imag;
    		return c;
    	}
    	Complex operator+(double b)  //重载为类成员函数
    	{
    		Complex c;
    		c.real = real + b;
    		c.imag = imag;
    		return c;
    	}
    	void display();
    
    private:
    	double real;
    	double imag;
    };
    
    void Complex::display()
    {
    	cout << "(" << real << "," << imag << "i)" << endl;
    }
    
    int main()
    {
    	Complex c1(3,4),c2(5,-10),c3,c4;
    	c3 = c1 + c2;
    	cout << "c1+c2=";
    	c3.display();
    	c4 = c1 + 10;
    	c4.display();
    	return 0;
    }
    

结果：  
![image.png](https://image.3001.net/images/20210602/1622626634_60b7514a0cd8dcf3dfeb3.png!small)

### 2.运算符重载函数作为非成员函数

如果运算符左侧的操作数属于C++标准类型（如int）或是一个其他类的对象，那么运算符重载函数不能作为成员函数，只能作为非成员函数。  
代码：

    
    
    #include<iostream>
    using namespace std;
    
    class Complex
    {
    public:
    	Complex()
    	{
    		real = 0;
    		imag = 0;
    	}
    	Complex(double r,double i)
    	{
    		real = r;
    		imag = i;
    	}
    	Complex operator+(Complex &c2)  //类成员函数
    	{
    		Complex c;
    		c.real = real + c2.real;
    		c.imag = imag + c2.imag;
    		return c;
    	}
    	Complex operator+(double b)  //类成员函数
    	{
    		Complex c;
    		c.real = real + b;
    		c.imag = imag;
    		return c;
    	}
    	friend Complex operator+(double a,Complex &c2);
    	void display();
    
    private:
    	double real;
    	double imag;
    };
    
    Complex operator+(double a,Complex &c2)  //定义作为友元函数的重载函数
    {
    	Complex c;
    	c.real = a + c2.real;
    	c.imag = c2.imag;
    	return c;
    }
    
    void Complex::display()
    {
    	cout << "(" << real << "," << imag << "i)" << endl;
    }
    
    int main()
    {
    	Complex c1(3,4),c2(5,-10),c3,c4,c5;
    	c3 = c1 + c2;
    	cout << "c1+c2=";
    	c3.display();
    	c4 = c1 + 10;
    	c4.display();
    	c5 = 20 + c1; //c5=operator+(20,c1);
    	cout << "20+c1=";
    	c5.display();
    	return 0;
    }
    

结果：  
![image.png](https://image.3001.net/images/20210602/1622626612_60b751340ec784dbaf353.png!small)

