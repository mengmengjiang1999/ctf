**摘要**

安卓漏挖第一步，学会基本的Android开发技能。

 **安装和配置Android Studio**

首先安装和配置好Android
Studio，后续我们简化叫它AS，下载地址（https://developer.android.google.cn/studio/#downloads），安装和配置网上有很多资料，比如可参考（https://blog.csdn.net/m0_59440594/article/details/123107259）,不再赘述。

**![](https://image.3001.net/images/20221124/1669278894_637f2cae4402bbebec8be.png!small)**

 **用Android Studio编写第一个应用程序**

参考前辈的文章（https://www.52pojie.cn/thread-648530-1-1.html），首先创建一个项目，AS-->File-->New-->New
Project。

![](https://image.3001.net/images/20221124/1669278981_637f2d055a88c8d79fca0.png!small)

![](https://image.3001.net/images/20221124/1669279007_637f2d1f8c6a5f905bf7d.png!small)

Next，按照如下填写，这里的name将成为应用程序的名字。

![](https://image.3001.net/images/20221124/1669279058_637f2d52c600a62c22fb8.png!small)

Finish。进入到主程序，这里选择Project，然后点击HelloWorld2\app\src\main\res\layout
目录下的activity_main.xml。

![](https://image.3001.net/images/20221124/1669279147_637f2dab95de1af7a65c0.png!small)

![](https://image.3001.net/images/20221124/1669279198_637f2ddeac7463c1d0792.png!small)

把拖拉框上面的Textview，Plain Test
,Button控件拖拉到右侧屏幕上来，通过更改右侧对应的ID和text内容配置控件的属性，完成如图所示。这里拖拉了两个Textview，两个Plain
Test和一个Button控件。

![](https://image.3001.net/images/20221124/1669279243_637f2e0b4cc25efe0c4b4.png!small)

最终修改成如下图所示，点击布局按钮PS:我第一次没有点击这个，生成的apk安装后，所有的控件都在左上角，布局出现了问题，参考此文章（https://blog.csdn.net/Chamico/article/details/79218907）得知新版需要用这个按钮布局下。

![](https://image.3001.net/images/20221124/1669279291_637f2e3bd4e4e51c8975f.png!small)

![](https://image.3001.net/images/20221124/1669279348_637f2e74e9318be40e583.png!small)

点开MainActivity页面，编写相应的Android代码。import最好不要粘贴，可以按alt+enter自动生成。

    
    
    package com.example.helloworld2;
    
    import androidx.appcompat.app.AppCompatActivity;
    
    import android.os.Bundle;
    import android.view.View;
    import android.widget.Button;
    import android.widget.EditText;
    import android.widget.Toast;
    
    
    public class MainActivity extends AppCompatActivity {
        EditText Name; //定义Plain Test控件第一个输入框的名字
        EditText Pass; //定义Plain Test控件第二个输入框的名字
        @Override
        protected void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            setContentView(R.layout.activity_main);
            Name = (EditText) findViewById(R.id.editTextTextPersonName); //通过findViewById找到输入框控件对应的id并给它起一个名字
            Pass = (EditText) findViewById(R.id.editTextTextPersonName2);//通过findViewById找到输入框控件对应的id并给它起一个名字
            Button Login = (Button) findViewById(R.id.button);//通过findViewById找到按钮控件对应的id并给它起一个名字
            Login.setOnClickListener(new View.OnClickListener() { //监听有没有点击按钮控件 如果点击了就会执行onClick函数
                @Override
                public void onClick(View view) {
                    check(Name.getText().toString().trim(),Pass.getText().toString().trim()); //调用check函数
                }
            });
        }
        public void check(String name,String pass) //自定义函数check 这里用来检查用户名和密码是否是hfdcxy和1234
        {
            if(name.equals("hfdcxy")&&pass.equals("1234"))
            {
                Toast.makeText(MainActivity.this,"登录成功", Toast.LENGTH_SHORT).show();//弹框
            }
            else
                Toast.makeText(MainActivity.this,"登录失败", Toast.LENGTH_SHORT).show();//弹框
        }
    }
    

点击Build，Build Apk，生成第一个Android程序。如果需要改，改完之后，点击布局按钮，ctrl+s保存后，点击Build，rebuild
project去重新编译生成apk。

生成的apk在AndroidStudioProjects\HelloWorld2\app\build\outputs\apk\debug目录下。

![](https://image.3001.net/images/20221124/1669279896_637f3098298e1fe63bcef.png!small)

把apk安装到模拟器上或者真机上，如下所示。

![](https://image.3001.net/images/20221124/1669279820_637f304c943b3bf95199f.png!small)

 **参考链接**

<https://developer.android.google.cn/studio/#downloads>

<https://blog.csdn.net/m0_59440594/article/details/123107259>

<https://www.52pojie.cn/thread-648530-1-1.html>

<https://blog.csdn.net/Chamico/article/details/79218907>

