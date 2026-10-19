### eval()函数执行
代码注入的方法：![图片.png](https://image.3001.net/images/20210906/1630941574_61363186cb2deedd8b07d.png!small)

如上图所示，给变量a赋的值是想要执行的命令加上分号，然后给eval函数传的参数是变量a，这样就会通过eval()执行phpinfo()这个命令。

### assert()函数执行 代码注入的方法：

![图片.png](https://image.3001.net/images/20210906/1630941585_613631914cc2bb0e5ee33.png!small)

如上图所示，assert()想要执行php代码，我们需要先给变量a赋值，把我们要执行的命令用反引号括住然后传给eval函数，并把这些赋值给变量a，最后再把变量a传入assert()函数即可。

### call_user_func()函数执行 代码注入的方法：

![图片.png](https://image.3001.net/images/20210906/1630941602_613631a20d17759e0de2b.png!small)

该函数输入的第一个参数是调用的函数，第二个参数是传给调用的函数的参数。例如上图，我们通过call_user_func()调用assert()，执行phpinfo()这个命令。

### call_user_func_array()函数执行 代码注入的方法：

![图片.png](https://image.3001.net/images/20210906/1630941613_613631add5d375f73b86a.png!small)

该函数传入的第一个参数是想要调用的函数，第二个参数是传给调用的函数的参数，但是该参数需要以数组的形式出现。如上图所示，我们通过call_user_func_array()调用assert()执行phpinfo()命令。

### create_function()函数执行 代码注入的方法：

![图片.png](https://image.3001.net/images/20210906/1630941625_613631b9482b834d43c6c.png!small)

如上图所示，我们可以通过create_function(),给第一个参数传入的是所调用函数所传入的参数(或者所执行命令需要的参数)，给第二个参数传入的是所调用的函数(或者所执行的命令)。

### preg_replace()函数执行 代码注入的方法：

![图片.png](https://image.3001.net/images/20210906/1630941637_613631c54e50618a33aef.png!small)

如上图所示，当第一个参数能够通过正则匹配成功替换掉第三个参数的时候，第一参数后面跟有/e，那么就会将第二个参数当做php代码执行。

### array_map()函数执行 代码注入的方法：

![图片.png](https://image.3001.net/images/20210906/1630941648_613631d0c450fe3f88307.png!small)

第一个参数传入想要调用的函数 第二个参数传入调用函数所使用（传入）的参数，即可执行命令。

执行效果：  
![图片.png](https://image.3001.net/images/20210906/1630941661_613631dde3a994d199a21.png!small)

源代码是这样也可以：  
![图片.png](https://image.3001.net/images/20210906/1630941676_613631eca07bdb1bf7a60.png!small)

就是在代码中它不再使得第二个参数是数组，我们可以通过传参的时候，使用上面图片中的方法使得第二个参数是数组，从而达到相同的效果。

### usort()函数执行 代码注入的方法：

![图片.png](https://image.3001.net/images/20210906/1630941686_613631f6e92c71be6ad42.png!small)

usort() 使用用户自定义的比较函数对数组进行排序。要执行的命令赋值给数组的第一个值即可，如上图所示。

### uasort()函数执行 代码注入的方法：

![图片.png](https://image.3001.net/images/20210906/1630941694_613631fe9e0afdd640213.png!small)

如上图所示，uasort()的第一个参数值的类型需要为数组，我们可以将该数组的第一个值，赋值为我们想要执行的命令，uasort()的第二个参数值为所调用的函数。

例如：我们可以通过给pass赋值为phpinfo(),从而来执行phpinfo()。  
![图片.png](https://image.3001.net/images/20210906/1630941717_613632150f7a1b0227995.png!small)

### ${ } 执行代码注入的方法：

![图片.png](https://image.3001.net/images/20210906/1630941725_6136321d2db52da859fce.png!small)

我们在${ }中输入我们想要执行的命令即可。

