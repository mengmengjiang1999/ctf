## 写在开篇:

打算利用暑假来学下Java安全方面的内容(之前被ctf的java题打怕了),然后查询了些大佬建议，都是从Java反序列化开始学起，于是兴冲冲的去看Java反序列化，结果自然看不懂。然后又听说要先学Java反射，好吧，那就先去学java反射，结果看完一些大佬们的博客后，跟着大佬的代码能编写出来，自己去写的话却又是无从下'笔'。这时我才意识到自己连类和对象的知识点都不是搞的很清楚，于是只好从最基础的面向对象编程学起。从基础开始，慢慢深入，学了几天，也算有所感悟，特此记录(师傅们轻喷)!

### (一)从java面向对象编程开始谈起

#### 1.概念简述

**Java
是面向对象的编程语言，对象就是面向对象程序设计的核心。所谓对象就是真实世界中的实体，对象与实体是一一对应的，也就是说现实世界中每一个实体都是一个对象，它是一种具体的概念**

**面向对象的三大核心特性** ：

  * 可重用性：代码重复使用，减少代码量，提高开发效率。面向对象的三大基本特征（继承、封装和多态）都围绕这个核心。
  * 可扩展性：指新的功能可以很容易地加入到系统中来，便于软件的修改。
  * 客观理性：能够将功能与数据结合，方便管理。

**面向对象编程是将现实生活中的概念通过程序进行模拟，其中有两个最重要的概念：对象，类。**

**类(class)的概念** : ** _类是对具有相同特征或属性，具有相同行为能力的一类事物的描述或称呼_**

**对象(object)的概念** : ** _对象是这一类事物带有属性值,具有具体行为的个体或实例_**

_这里这种官方类似定义性的话就不多加介绍，具体可以参考:_

<https://blog.csdn.net/zxy144/article/details/108248542>

<https://blog.csdn.net/WXS153322/article/details/128007789>

#### 2.一些自己的思考

如果你也跟我一样看上面的概念看的头皮发麻，不妨自己总结一下:

《Java编程思想》中提到了' **万物皆为对象**
‘的概念，确实如此，衣服，鸡，篮球，人等等个体都是对象，他们都有自己的特征。类的实例化就是对象，对象有其对应的属性，方法和构造器。这里拿手机来举例，手机是一类高科技产品的实例化，在现实生活中所存在的，那么手机我们可以看成是一个对象，它有名字，有重量，有生产日期，这些我们称为它的属性，那么它的整体外壳我们看成是它的构造器，那么当我们按下电源键的时候，它会亮屏，我们把这个称之为一种方法，使它开机亮屏的方法，这种方法可以作用在我这个对象上，对对象产生影响。

那么我们不妨来试试 **定义一个类** :

    
    
    //在Java中定义一个类使用关键字class,一个合法的标识符和一对表示程序体的大括号
    
    public class phone { //声明一个phone类
    
    }
    

然后我们添加上一些属性:

    
    
    public class phone {
        public String name; //声明一个字符串类型的name属性
        public double weight; //声明一个浮点型的weight属性
    }
    

然后我们再加上构造器:

    
    
    public class phone {
        public String name;
        public double weight;
        public phone(){ //无参构造器，当我们自己没声明时，系统会自动给我们声明，方便我们实例化这个类
        }
        public phone(String name,double weight){ //有参构造器，我们需要自己声明，方便我们在构造实例化对象时给属性赋值
            this.name=name;
            this.weight=weight;
        }
    

最后我们写入一些方法:

    
    
    public class phone {
        public String name;
        public double weight;
        public phone(){
        }
        public phone(String name,double weight){
            this.name=name;
            this.weight=weight;
        }
        public void dianyuan(){ //定义一个无返回值的方法，调用会打印"开机"
            System.*out*.println("开机");
        }
        public void setName(String name){ //定义一个形参为String类型的方法，调用后给name属性赋值
            this.name=name;
        }
        public String getName(){ //定义一个调用后返回name属性的值的方法
            return name;
        }
        public void setWeight(double weight){ //定义一个形参为double类型的方法，调用后给weight属性赋值
            this.weight=weight;
        }
        public double getWeight(){ //定义一个调用后返回weight属性的值的方法
            return weight;
        }
    }
    

到此我们就简单的构造好一个类了，现在我们需要对它进行实例化为对象。

**实例化一个类（对象的创建）** :

    
    
    public class phone_tes {
        public static void main(String[] args) {
            phone p=new phone(); //使用关键字new来实例化类，并且声明是phone类型的。
        }
    }
    

这样我们就拿到了一个'手机'，那么接下来我们就可以操作这台'手机':

    
    
    public class phone_tes {
        public static void main(String[] args) {
            phone p=new phone();
            //设置它的属性
            p.name="8848";
            p.weight=114514;
            System.out.println(p.name);
            System.out.println(p.weight);
        }
    }
    

![](./img/4707420640253366634.png)

    
    
    public class phone_tes {
        public static void main(String[] args) {
            phone p=new phone();
            //调用dianyuan这个方法
            p.dianyuan();
        }
    }
    

![](./img/8695271556620724724.png)

    
    
    public class phone_tes {
        public static void main(String[] args) {
            phone p=new phone();
            //调用之前定义的setxxxx方法和getxxxx方法给属性赋值和打印
            p.setName("8848");
            System.out.println(p.getName());
            p.setWeight(114514);
            System.out.println(p.getWeight());
        }
    }
    

![](./img/7481848360112932895.png)

补充:这里我们因为我们设置了含参的构造器，所以可以直接在实例化时就赋值:

    
    
    public class phone_tes {
        public static void main(String[] args) {
            phone p=new phone("8848",114514);
            System.*out*.println(p.name);
            System.*out*.println(p.weight);
            //如果我们没有设置含参的构造器，那么就不能直接赋值
        }
    }
    

![](./img/1267903313029309768.png)

#### 3.总结

那么在学习java反射之前的基础知识铺垫大概就是这些，当然java面向对象编程还有一些如封装，继承和实体没提到，这些都比较简单，看下上面推荐的博客就能理解。那么有了面向对象思想的基础，接下来就让我们来会一会Java反射吧!

### 二.Java中的反射机制

#### 1.概念简述

Java 的 **反射机制** 是指在运行状态中，对于任意一个类都能够知道这个类所有的属性和方法；
并且对于任意一个对象，都能够调用它的任意一个方法；这种动态获取信息以及动态调用对象方法的功能成为Java语言的反射机制。

而我们之前在上面介绍的运用new关键字去实例化类的过程就叫做 **正射**
。那么假如，我是说如果我们一开始并不知道我们要初始化的类对象是什么，那么阁下该如何应对呢?

所以总的来说，就是当我在程序运行前并不知道我们要实例什么类的时候，我们就需要运用反射，通过反射我们可以获取这个类的原型，然后为所欲为。

#### 2.反射的调用

###### 获取类(class)

常见的获取类对象class的方法有三种:

    
    
    //1.使用class.forName()方法
    
    Class p=Class.forName("test.phone"); //里面要填:类所在的包名+类名
    
    //2.使用实例化对象的getClass()方法
    
    phone p=new phone(); //实例化对象
    Class p1=p.getClass();//通过实例化对象来获取完整类的原型
    
    //一开始我觉得这个方法可能有些鸡肋，既然我都获取到实例化对象了还要反射干嘛，后面想了想觉得可以利用这个来访问一些私有属性和私有方法~~~
    
    //3.使用类的class方法
    
     Class p=phone.class;
    

###### 获取实例化对象(object)

获取实例化对象object的方法通常有两种:

    
    
    //1.通过class的newInstance()方法
    
    Class p=Class.forName("test.phone");
    Object p1=p.newInstance();
    //这里也有另一种写法,区别是要进行强制类型转化
    Class p=Class.forName("test.phone");
    phone p1=(phone)p.newInstance();
    
    //2.通过constructor的newInstance()方法
    Class p=Class.forName("test.phone");
    Constructor constructor=p.getConstructor();
    Object p1=constructor.newInstance();//这里同上一样有另一种写法，就不再赘述
    
    //运用这种方法前需要先调用它的无参构造器，然后再实例化，我一度认为这是在脱裤子放屁(到后面才发现我错了)
    

第二种写法后面经过了解后我才知道一般可以用来调用含参的构造器。因为class的newInstance()方法,需要我们类中存在无参的构造器，它通过无参的构造器来实例化，而一旦我们类中不存在无参构造器，那么第一种方法就不行了,如下图所示:

![](./img/595373451918595778.png)

所以这时候我们就需要第二种方法了:

    
    
    Class p=Class.*forName*("test.phone");
    
    Constructor constructor=p.getConstructor(String.class,double.class);
    //这个是调用了我们之前设置的含参构造器(忘记的上去看看第一部分构造的),后面传入的参数是String和double的原型类，因为我们之前构造器的参数类型就是String和double，所以我们这里用这个。
    
    Object p1=constructor.newInstance("8848",114514); 
    //这里在实例化的时候就可以直接对name属性和weight属性赋值了
    

![](./img/466495386014300124.png)

###### 获取类的构造器(constructor)

获取类的构造器constructor一般有四种方法:

    
    
    //1.获取public类型的构造器:getConstructor(class[]parameterTypes)
    Class p=Class.forName("test.phone");
    Constructor constructor=p.getConstructor();
    //这里你可以指定参数，来获取含参的构造器，之前演示过，不再赘述.
    
    //2.获取全部public类型的构造器:getConstructors()
    Class p=Class.forName("test.phone");
    Constructor[] constructor=p.getConstructors();
    //注意这里要用数组，因为全部构造器可能并不只有一个
    
    //3.获取public和private类型的构造器:getDeclaredConstructor(class[]parameterTypes)
    //当我们前面构造器类型是private的时候，运用上述两种方法是调用不到的。
    Class p=Class.forName("test.phone");
    Constructor constructor=p.getDeclaredConstructor();
    
    //4.获取全部类型的构造器:getDeclaredConstructors()
    Class p=Class.forName("test.phone");
    Constructor[] constructor=p.getDeclaredConstructors();
    //注意，这个同意要改为数组的形式
    

我这里就演示最后一个:

![](./img/8764866121810564771.png)

###### 获取类的属性(field)

常见的获取类属性field的方法有四种:

    
    
    //1.获取类的一个public类型属性:getField(String name)
    Class p=Class.forName("test.phone");
    Field f=p.getField("name");
    
    //2.获取类的一个全部类型的属性:getDeclaredField(String name)
     Class p=Class.forName("test.phone");
     Field f=p.getDeclaredField("weight");
    
    //3.获取类的全部public类型的属性:getFields()
     Class p=Class.forName("test.phone");
     Field[] f=p.getFields(); //同样要注意改成数组
    
    //4.获取类的全部类型的属性:getDeclaredFields()
    Class p=Class.forName("test.phone");
    Field[] f=p.getDeclaredFields(); //同样要注意改成数组
    

这里同样演示最后一个:

![](./img/5911867506410707830.png)

可以看到public和private类型的属性都被我们获取了，然后我们就可以对这些属性进行赋值(获取单个指定属性时)等操作。

###### 获取类的方法(method)

常用的获取类的方法有三种:

    
    
    //1.获取类的一个特定public类型的方法:getMethod(String name,class[] parameterTypes)
    Class p=Class.forName("test.phone");
    Method m=p.getMethod("setName", String.class); //要注意这里有两个参数，后面要传入的是方法形参的类型的原型,无参函数就不用填
    
    //2.获取类的一个特定无论什么类型的方法:getDeclaredMethod(String name,class[] parameterTypes)
    Class p=Class.forName("test.phone");
    Method m=p.getDeclaredMethod("setName", String.class);
    
    //3.获取类的全部public的方法:getMethods()
    Class p=Class.forName("test.phone");
    Method[] m=p.getMethods();//要注意改成数组
    
    //4.获取类的全部类型的方法:getDeclaredMethods()
     Class p=Class.forName("test.phone");
     Method[] m=p.getDeclaredMethods(); //同样要注意改成数组
    

这里就演示最后一个:

![](./img/888246995427411308.png)

反射的基本要素我们学完了，下面以之前的phone类为例子，完整的演示一遍:

###### 反射完整使用演示:

    
    
    Class p=Class.*forName*("test.phone");           //获取phone类的原型
    Constructor constructor=p.getConstructor();      //获取无参的构造器
    Object o=constructor.newInstance();             //实例化一个对象o
    Method m=p.getMethod("dianyuan");               //获取方法dianyuan
    m.invoke(o);                                    //运用Method的invoke方法来执行这个类的方法
    Method m1=p.getMethod("setName", String.class); //获取方法setName
    Method m2=p.getMethod("getName");               //获取方法getName
    m1.invoke(o,"8848");                            //执行setName方法，为Name属性赋值
    System.*out*.println(m2.invoke(o));             //调用getName的方法并打印返回值
    

![](./img/6486013026195744853.png)

不仅仅只有这些模式来反射属性和方法，但每个成分对应的反射机制就是上面介绍的那些，可以根据需求来替换，选择适合自己的方式。补充:当调用的方法，属性，构造器是私有的时候，那么我们不仅仅在获取时要用特殊的方法，在获取后的调用中还要调用setAccessible方法来修改作用域，如下:

    
    
    //假设我把setName设置为私有的方法
    
    Class p=Class.*forName*("test.phone");           //获取phone类的原型
    Constructor constructor=p.getConstructor();      //获取无参的构造器
    Object o=constructor.newInstance();             //实例化一个对象o
    Method m=p.getMethod("dianyuan");               //获取方法dianyuan
    m.invoke(o);                                    //运用Method的invoke方法来执行这个类的方法
    Method m1=p.getDeclaredMethod("setName", String.class);//运用getDeclaredMethod获取私有方法setName
     m1.setAccessible(true);                       
    //调用setAccessible方法来允许我们操作私有方法(私有属性和私有构造器同样如此)
    Method m2=p.getMethod("getName");               //获取方法getName
    m1.invoke(o,"8848");                            //执行setName方法，为Name属性赋值
    System.*out*.println(m2.invoke(o));             //调用getName的方法并打印返回值
    

未使用前:

![](./img/8185207558516570125.png)

使用后:

![](./img/8657912020182750872.png)

###### Runtime类的演示

**Runtime类中有个exec方法可以进行命令执行，下面演示一下如何通过反射来调用:**

![](./img/8565840229771260070.png)

![](./img/5391900130876820152.png)  
查阅官方的Runtime.java文档，可以看到里面有个私有的无参构造器和exec方法下进行了命令执行，那么我们的目标就很明确:

    
    
    Class p=Class.*forName*("java.lang.Runtime");
    Constructor constructor=p.getDeclaredConstructor(); //调用私有构造器
    constructor.setAccessible(true); //修改作用域
    Method m=p.getMethod("exec", String.class); //获取exec方法
    Object o=constructor.newInstance(); //实例化对象
    m.invoke(o,"calc"); //调用exec方法，执行calc命令
    

![](./img/4733151689614815884.png)

### (三)写在结尾

把java反射学完，就算是入门了java安全，可以跟进后续的Java反序列化和各类Java安全漏洞和链子，初学这段时间感觉Java确实有点抽象，不过无所谓，慢慢学吧！
~~后续也会写下反序列化的内容~~

**_参考:_**

**谈谈Java反射：从入门到实践，再到原理:**<https://juejin.cn/post/6844904025607897096>

**p牛的java安全漫谈（反射篇）** ：<https://govuln.com/docs/java-things/>

