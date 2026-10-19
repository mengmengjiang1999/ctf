## 一、涉及的基本原理

### 蓝牙信道

有两种通信信道：广播信道和数据信道（advertising channels and data
channels）,对应的通道如下图，其中广播信道只使用37，38，39这三个通道。数据信道共包含37个信道。

![](https://image.3001.net/images/20201117/1605603161_5fb38f5942167f0d3b70b.png!small)

### 广播通道作用

> 设备发现  
> 连接建立  
> 传输广播

### 数据通道作用

> 自适应跳频以及设备间数据传输

### 自适应跳频

在数据传输时，设备间会使用跳频算法在数据通道间跳频。常见的CC2540不具备捕获数据通道中的数据的能力，需使用昂贵的专业蓝牙设备（数万元）或Ubertooth进行捕获（几百元，但是不稳定）。

### 蓝牙地址(bdaddr)

蓝牙地址也有多种类型，有设备使用固定的蓝牙地址，也有设备使用随机的蓝牙地址。类型如下,具体的定义参考末尾的参考连接

![1605603210_5fb38f8a4f6e45035356c.png!small?1605603210612](https://image.3001.net/images/20201117/1605603210_5fb38f8a4f6e45035356c.png!small?1605603210612)

### BLE安全模式

蓝牙有两种安全模式和4个安全等级，Level 1 ~ Level 4对应的安全强度由若到强，分别为：

>  **Security Level 1** supports communication without security at all, and
> applies to any Bluetooth communication, but think of it as applying to
> unpaired communications.
>
>  **Security Level 2** supports AES-CMAC encryption (aka AES-128 via RFC
> 4493, which is FIPS-compliant) during communications when the devices are
> unpaired.
>
>  **Security Level 3** supports encryption and requires pairing.
>
>  **Security Level 4** supports all the bells and whistles, and instead of
> AES-CMAC for encryption, ECDHE (aka Elliptic Curve Diffie-Hellman aka P-256,
> which is also FIPS-compliant) is used instead.

## 二、准备抓包所需的软件和硬件

### 所需硬件

Ubertooth 一个 （配合ubertooth-btle使用）  
CSR模组 一个 (配合bluetoothctl使用，也可使用树莓派等设备替代)  
Linux PC 一台  
ESP32模组 一个 （作为ble server使用）

##### ESP32模组的长相

![1605603250_5fb38fb24ca3af63cf683.png!small?1605603256255](https://image.3001.net/images/20201117/1605603250_5fb38fb24ca3af63cf683.png!small?1605603256255)

### 所需软件

ubertooth-btle （抓取数据信道数据）  
bluetoothctl （监听广播数据）  
esp-idf （烧录ble server）  
crackle （分析加密情况） wireshark  
LightBlue （手机APP）

## 三、动手做

### 烧录BLE Server

首先从乐鑫GitHub获取esp-idf工具链和demo，具体的esp-idf下载和配置的方法可按官方教程操作。 当配置好esp-idf后，连接ESP32模组和PC。

#### 烧录不安全的demo：gatts_demo

该demo位于该路径下 **esp-idf/examples/bluetooth/bluedroid/ble/gatt_server**

烧录方法

    
    
    cd ~/esp-idf/examples/bluetooth/bluedroid/ble/gatt_server  
    make menuconfig    
    make flash  //烧录时可能需按住ESP32模组上的boot键

### 扫描附近的BLE设备``

将CSR模组插入Linux PC，也可直接使用树莓派。安装并启动bluetoothctl（可能需要sudo权限）。执行如下命令。

``

    
    
    sudo bluetoothctl
    [bluetooth]# scan on   //启动扫描，等待一会
    [bluetooth]# scan off   //关闭扫描
    [bluetooth]# devices   //查看附近的设备

找到ESP_GATTS_DEMO对应的地址并记住。``

### 开始捕获数据包

将Ubertooth插入Linux PC，安装ubertooth-btle并刷入最新的固件，操作流程参考如下链接：
<https://github.com/greatscottgadgets/ubertooth/wiki/Build-Guide>  
<https://github.com/greatscottgadgets/ubertooth/wiki/Firmware>

准备完成后，输入如下命令进行捕获

    
    
    touch /tmp/pipe
    ubertooth-btle -t aa:bb:cc:dd:ee:ff -f -c /tmp/pipe   //aa:bb:cc:dd:ee:ff为之前获取到的ESP_GATTS_DEMO对应的地址  
    启动wireshark 并获取/tmp/pipe中的数据

手机端使用LightBlue连接设备，由于蓝牙跳频，有时Ubertooth会抓不到包，或者卡住，可以反复在LightBlue中“返回-进入”来抓取ble通讯包。

### 查看明文数据

由于我们使用的是未加密的demo，可直接在wireshark中看到明文传输的数据，如下图。

![1605603759_5fb391af9b098e11a2b11.png!small?1605603760622](https://image.3001.net/images/20201117/1605603759_5fb391af9b098e11a2b11.png!small?1605603760622)

可以在图片下方看到 **deedbeef** 数据值，该数据值由gatts_demo.c中如下代码产生。

    
    
    case ESP_GATTS_READ_EVT: {
            ESP_LOGI(GATTS_TAG, "GATT_READ_EVT, conn_id %d, trans_id %d, handle %d\n", param->read.conn_id, param->read.trans_id, param->read.handle);
            esp_gatt_rsp_t rsp;
            memset(&rsp, 0, sizeof(esp_gatt_rsp_t));
            rsp.attr_value.handle = param->read.handle;
            rsp.attr_value.len = 4;
            rsp.attr_value.value[0] = 0xde;
            rsp.attr_value.value[1] = 0xed;
            rsp.attr_value.value[2] = 0xbe;
            rsp.attr_value.value[3] = 0xef;
            esp_ble_gatts_send_response(gatts_if, param->read.conn_id, param->read.trans_id,
                                        ESP_GATT_OK, &rsp);
            break;
        }

### 再来分析下安全的BLE连接

在esp-idf目录下，找到如下demo，按照之前烧录不安全demo的方式烧录该demo。  
 **examples/bluetooth/bluedroid/ble/gatt_security_server**

烧录完成后，使用Ubertooth捕获手机与ESP32模组间的通讯。捕获到的数据片段如下。

![1605603818_5fb391eaf0aacd99a52fa.png!small?1605603819760](https://image.3001.net/images/20201117/1605603818_5fb391eaf0aacd99a52fa.png!small?1605603819760)

可以看到Random、DHKey、LL_ENC_REQ等信息，说明该连接使用到密钥交换，接下来我们可以借助另一个工具判断这两个连接是否安全。

### 破解工具上场--crackle

工具下载地址 **<https://github.com/mikeryan/crackle>**  
该工具可以用来破解BLE通讯中的TK，或者配合LTK对BLE通讯进行解密。  
我们分别使用该工具读取两次通讯的PCAP文件。

### 读取不安全的BLE通讯

![1605603860_5fb392142b3ed73085191.png!small?1605603860449](https://image.3001.net/images/20201117/1605603860_5fb392142b3ed73085191.png!small?1605603860449)

可以看到该通讯PCAP中不包含加密通讯。

### 读取安全的BLE通讯

![1605603893_5fb392353aa49fd651d42.png!small?1605603893762](https://image.3001.net/images/20201117/1605603893_5fb392353aa49fd651d42.png!small?1605603893762)

能看到crackle提示找到了加密的数据包，但是由于没有LTK，无法解密数据包。在让我们回到demo的代码中，那么可以看到在example_ble_sec_gatts_demo.c中有如下代码片段。

    
    
    case ESP_GATTS_CONNECT_EVT:
                ESP_LOGI(GATTS_TABLE_TAG, "ESP_GATTS_CONNECT_EVT");
                /* start security connect with peer device when receive the connect event sent by the master */
                esp_ble_set_encryption(param->connect.remote_bda, ESP_BLE_SEC_ENCRYPT_MITM);
                break;

代码片段中用到了 **ESP_BLE_SEC_ENCRYPT_MITM** 来指明连接的安全等级。除了该安全选项，还有另外三个，分别是：

> ESP_BLE_SEC_NONE
>
> ESP_BLE_SEC_ENCRYPT
>
> ESP_BLE_SEC_ENCRYPT_NO_MITM
>
> ESP_BLE_SEC_ENCRYPT_MITM

## 四、总结

> 蓝牙提供了完善的安全机制和抗干扰机制
>
> 由于自适应跳频机制的存在，捕获数据通道中的数据较为困难
>
> 不是所有的设备都会选择安全的BLE蓝牙配对和连接模式，可能存在数据明文传输的情况

## 五、参考链接

> <https://microchipdeveloper.com/wireless:ble-link-layer-channels>  
> <https://www.rfwireless-world.com/Terminology/BLE-Advertising-channels-and-> Data-channels-list.html>  
> <https://www.novelbits.io/bluetooth-address-privacy-> ble/><https://duo.com/decipher/understanding-bluetooth-security>

