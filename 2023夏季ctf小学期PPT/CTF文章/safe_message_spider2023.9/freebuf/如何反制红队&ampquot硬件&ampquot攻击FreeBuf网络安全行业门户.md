## 1.前言

随着红蓝对抗日益激烈，而红队的攻击点从原有的Web方法，也涉及到了很多的方向，例如硬件攻击。

而硬件攻击最显著的就是Badusb。说起这个玩意儿。想必大家都知道，网上一搜一大堆制作文章。![1635165655_6176a5d78c58e61b0ea54.png!small](https://image.3001.net/images/20211025/1635165655_6176a5d78c58e61b0ea54.png!small)

  

## 2.另一种烧录BadUsb

网上的确有大多数BadUsb的烧录方法，但都是基于arduino界面的烧录，但经过本人研究

arduino也是可以通过命令行参数进行烧录的，具体如下：

    
    
    C:\Users\Administrator\Desktop\Arduino\arduino_debug.exe --port COM端口 --upload 烧录的内容文件

文件路径的话，可以看如下图，当对内容进行保存的时候，给出了详细信息，后缀名为ino，经过笔者用命令行编译试验，路径要为：

    
    
    C:\\xxx\\sketch_apr01a\sketch_apr01a.ino

sketch_apr01a为项目文件，而在上层还要有一个sketch_apr01a名字的目录![1635165986_6176a7220d0af1c857ade.png!small](https://image.3001.net/images/20211025/1635165986_6176a7220d0af1c857ade.png!small)

## 3.代码分析流程

Windows sdk开发中，任何一个窗口都能接收消息并响应。 **同理 BadUSB或U盘插入或拔出也会有相应的消息与响应。**

 **用到的消息为：WM_DEVICECHANGE**

 **(通知应用程序对设备或计算机的硬件配置进行更改，通过WindowProc函数接收消息)**

 **函数原型如下：**

    
    
    LRESULT CALLBACK WindowProc ( HWND hWnd, 
                                  UINT message,
                                    WPARAM wParam, 
                                    LParam);

WindowProc中第三个参数wParam，指向发生的事件，该参数Dbt.h头文件找那个的值。说说我们要用到的宏吧，Dbt.h中：

    
    
    DBT_DEVICEARRIVAL //设备插入会进行响应
    DBT_DEVICEREMOVECOMPLETE //设备拔出时响应

 **代码实现消息响应**

首先来看WndProc函数。具体实现就是通过一个case来进行消息响应的

![1635166124_6176a7ac2a46a4e800b54.png!small](https://image.3001.net/images/20211025/1635166124_6176a7ac2a46a4e800b54.png!small)

添加自己的消息响应，以下代码当BadUSB插入之后，会弹窗显示设备插入。

    
    
    case WM_DEVICECHANGE://捕获设备更改时的消息
        switch (wParam){
        case DBT_DEVICEARRIVAL://捕获设备插入
          MessageBoxA(NULL, "设备插入", "test", NULL);
          break;
        case DBT_DEVICEREMOVECOMPLETE://捕获设备弹出
          MessageBoxA(NULL, "设备拔出", "test", NULL);
          break;
        }

这里当我插入BadUSB之后，成功捕获到消息并弹窗。

![1635166234_6176a81a506c703291e26.png!small](https://image.3001.net/images/20211025/1635166234_6176a81a506c703291e26.png!small)

 **核心代码实现**

**既然当BadUSB插入之后，会响应消息函数，那让消息函数执行arduino命令行并进行自动烧录。当红队后期做更改BadUSB的时候，就会执行我们烧录的代码**

 **BadUSB将要烧录的内容如下，setup函数为初始化函数。当BadUSB插入之后，打开记事本并输入
By：Met32这串字符。这里可自行更改..我这里为了演示方便就这样写的。**

    
    
    void setup() {
      // put your setup code here, to run once:
    
    Keyboard.begin();//开始键盘通信
     
    delay(1000);//延时1000毫秒，不要太短，因为每天电脑的运行速度都不一样 
     
    Keyboard.press(KEY_CAPS_LOCK); //按下大写键 这里我们最好这样写 不然大多数电脑在中文输入的情况下就会出现问题
     
    Keyboard.release(KEY_CAPS_LOCK); //释放大写键
     
    delay(500);
     
     
    Keyboard.press(KEY_LEFT_GUI);//按下徽标键 也就是win键 
     
    delay(500); 
     
    Keyboard.press('r');//按下r键 
     
    delay(500); 
     
    Keyboard.release(KEY_LEFT_GUI);//松掉win键 
     
    Keyboard.release('r');//松掉r键 
     
    delay(500); 
     
    Keyboard.println("notepad");//输入notepad 打开记事本
     
    delay(500); 
     
    Keyboard.press(KEY_RETURN); //按下回车键
     
    Keyboard.release(KEY_RETURN); //释放回车键
     
    delay(500); 
     
    Keyboard.println(" By：Met32");//输入我们想显示的信息
     
    Keyboard.press(KEY_RETURN); //按下回车键
     
    Keyboard.release(KEY_RETURN); //释放回车键
     
    delay(500);
     
    Keyboard.press(KEY_CAPS_LOCK); //按下大写键
     
    Keyboard.release(KEY_CAPS_LOCK); //释放大写键 我们再次关闭开启的大写键
     
    delay(500);
     
    Keyboard.end();//结束键盘通讯 
    
    }
    
    void loop() {
      // put your main code here, to run repeatedly:
    
    }

WndProc全部实现代码如下。

    
    
    LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
    {
      int wmId, wmEvent;
      PAINTSTRUCT ps;
      HDC hdc;
    
      switch (message)
      {
      case WM_COMMAND:
        wmId    = LOWORD(wParam);
        wmEvent = HIWORD(wParam);
        // 分析菜单选择: 
        switch (wmId)
        {
        case IDM_ABOUT:
          DialogBox(hInst, MAKEINTRESOURCE(IDD_ABOUTBOX), hWnd, About);
          break;
        case IDM_EXIT:
          DestroyWindow(hWnd);
          break;
        default:
          return DefWindowProc(hWnd, message, wParam, lParam);
        }
        break;
      case WM_PAINT:
        hdc = BeginPaint(hWnd, &ps);
        // TODO:  在此添加任意绘图代码...
        EndPaint(hWnd, &ps);
        break;
      case WM_DESTROY:
        PostQuitMessage(0);
        break;
      case WM_DEVICECHANGE:
        switch (wParam){
        //代码在这
        case DBT_DEVICEARRIVAL:
          system("C:\\Users\\Arduino\\arduino_debug.exe --port COM5 --upload C:\\Users\\Administrator\\Desktop\\sketch_apr01a\\sketch_apr02a\\sketch_apr02a.ino");
          break;
        case DBT_DEVICEREMOVECOMPLETE:
          MessageBoxA(NULL, "设备拔出", "test", NULL);
          break;
        }
        break;
      default:
        return DefWindowProc(hWnd, message, wParam, lParam);
      }
      return 0;
    }

##  **4.使用过程**

现在来看一下效果，当BadUSB插入之后，自行拷贝烧录内容到对方的BadUSB。

![1635166318_6176a86e0e2378f380c3a.png!small](https://image.3001.net/images/20211025/1635166318_6176a86e0e2378f380c3a.png!small)

之后把程序退出，BadUSB从新插入一下，成功显示，证明我们成功烧录到对方的BadUSB

![1635166382_6176a8aea2d1a411f3e18.png!small](https://image.3001.net/images/20211025/1635166382_6176a8aea2d1a411f3e18.png!small)

##  **5.结尾注意点**

**Arduino路径方面的问题不必担心，因为都是自己本机，写死即可，问题就在COM端口这，当BadUSB插入之后，我们是不确定使用的哪个端口的。因此可以通过一个循环将常用的COM端口号全部执行一遍即可。**

 **如果想更加完善一点，可以检测当BadUSB插入之后禁用键盘(禁止对方代码操作)，之后在执行我们的system命令。**

