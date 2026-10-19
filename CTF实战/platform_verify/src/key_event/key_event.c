#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <limits.h>
#include <sys/time.h>
 
#include "data_type.h"
#include "cube.h"
#include "cube_define.h"
#include "cube_record.h"

#include "user_define.h"
#include "key_event.h"
// add para lib_include
RECORD(MESSAGE,INSTANCE_INFO) * _create_instance_info();
int key_event_init(void * sub_proc, void * para)
{
	int ret;
	// add yorself's module init func here
	return 0;
}
int key_event_start(void * sub_proc, void * para)
{
	int ret;
	void * recv_msg;
	int type;
	int subtype;
	// add yorself's module exec func here
	while(1)
	{
		usleep(time_val.tv_usec);
		ret=ex_module_recvmsg(sub_proc,&recv_msg);
		if(ret<0)
			continue;
		if(recv_msg==NULL)
			continue;
		type=message_get_type(recv_msg);
		subtype=message_get_subtype(recv_msg);
		if(!memdb_find_recordtype(type,subtype))
		{
			printf("message format (%d %d) is not registered!\n",
			message_get_type(recv_msg),message_get_subtype(recv_msg));
			ex_module_sendmsg(sub_proc,recv_msg);
			continue;
		}
		if((type==TYPE(USER_DEFINE))&&(subtype==SUBTYPE(USER_DEFINE,RETURN)))
		{
			ret=proc_keyevent_return(sub_proc,recv_msg);
		}
		else if((type==TYPE(GENERAL_RETURN))&&(subtype==SUBTYPE(GENERAL_RETURN,STRING)))
		{
            ret=proc_keyevent_cmd(sub_proc,recv_msg);
		}
        else
			ex_module_sendmsg(sub_proc,recv_msg);
	}
	return 0;
}

	
int proc_keyevent_return(void * sub_proc,void * recv_msg)
{
	int ret;
	RECORD(USER_DEFINE,RETURN) * login_return;
	RECORD(MESSAGE,INSTANCE_INFO) * instance_info;
    RECORD(USER_DEFINE,CLIENT_STATE) * client_state;
    RECORD(GENERAL_RETURN,STRING) * keymanage_cmd;
	char user_name[DIGEST_SIZE];
	void * new_msg;
	
	BYTE local_uuid[DIGEST_SIZE];	
	char proc_name[DIGEST_SIZE];	

	ret=message_get_record(recv_msg,&login_return,0);
	if(ret<0)
		return ret;

    if(login_return->return_code!=SUCCEED)
        return -EINVAL;

	instance_info=Talloc0(sizeof(*instance_info));
	if(instance_info==NULL)
		return -ENOMEM;
	
    // get client state
	client_state = proc_share_data_getpointer();

    // file the instance_info struct 
	proc_share_data_getvalue("proc_name",instance_info->proc_name);
	Strncpy(instance_info->user_name,client_state->user_name,DIGEST_SIZE);
	proc_share_data_getvalue("uuid",instance_info->node_uuid);

    // create key_manage cmd
	keymanage_cmd =Talloc0(sizeof(*keymanage_cmd));
	if(keymanage_cmd==NULL)
		return -ENOMEM;
    keymanage_cmd->name = dup_str("localkeyset_gen",0);
	new_msg=message_create(TYPE_PAIR(GENERAL_RETURN,STRING),NULL);	
	if(new_msg==NULL)
		return -EINVAL;
	ret=message_add_record(new_msg,keymanage_cmd);
	if(ret<0)
		return ret;

	ret=message_add_expand_data(new_msg,TYPE_PAIR(MESSAGE,INSTANCE_INFO),instance_info);
	if(ret<0)
		return ret;
    
	ret=ex_module_sendmsg(sub_proc,new_msg);
	return ret;
}
int proc_keyevent_cmd(void * sub_proc,void * recv_msg)
{
	int ret;
    MSG_HEAD * msg_head;
	RECORD(GENERAL_RETURN,STRING) * keyevent_cmd;
	ret=message_get_record(recv_msg,&keyevent_cmd,0);
	if(ret<0)
		return ret;
    
    if(Strcmp(keyevent_cmd->name,"remotekey_send")==0)
    {
        msg_head=message_get_head(recv_msg);
        if(msg_head==NULL)
            return -EINVAL;
        if(msg_head->state & MSG_STATE_RESPONSE)
        // remote key send command return, answer user        
        {
           void * send_msg = message_create(TYPE_PAIR(GENERAL_RETURN,STRING),NULL);
           if(send_msg == NULL)
                return -EINVAL;
	       RECORD(GENERAL_RETURN,STRING) * response_cmd;
           response_cmd = Talloc0(sizeof(*response_cmd));
           if(response_cmd==NULL)
                return -ENOMEM;
            response_cmd->name=dup_str("cmd_return",0);
            response_cmd->return_value = dup_str(keyevent_cmd->name,0);
            message_add_record(send_msg,response_cmd);
            return ex_module_sendmsg(sub_proc,send_msg); 
        }
        else
        // send key process
            return proc_keyevent_sendkey(sub_proc,keyevent_cmd,recv_msg);
    }
    else if(Strcmp(keyevent_cmd->name,"pcrquote")==0)
    {
        MSG_EXPAND * msg_expand;
        RECORD(GENERAL_RETURN,UUID) * external_data;
        // judge if message get the random data, if not , it is in server side, we should not do anything
        ret=message_get_define_expand(recv_msg,&msg_expand,TYPE_PAIR(GENERAL_RETURN,UUID));
        if(msg_expand != NULL)
        {
            printf("enter the client side!\n");
            ret=message_get_define_expand(recv_msg,&msg_expand,TYPE_PAIR(MESSAGE,INSTANCE_INFO));
            if(msg_expand ==NULL)
            {
                RECORD(MESSAGE,INSTANCE_INFO) * instance_info = _create_instance_info();
                if(instance_info!=NULL)
                    message_add_expand_data(recv_msg,TYPE_PAIR(MESSAGE,INSTANCE_INFO),instance_info);
            }
        }
    }
    return ex_module_sendmsg(sub_proc,recv_msg);
}

int proc_keyevent_sendkey(void * sub_proc,RECORD(GENERAL_RETURN,STRING) * keyevent_cmd,void * recv_msg)
{
	int ret;
	RECORD(MESSAGE,INSTANCE_INFO) * instance_info;
	char user_name[DIGEST_SIZE];
	void * new_msg;
    MSG_EXPAND * msg_expand;
	
	BYTE local_uuid[DIGEST_SIZE];	
	char proc_name[DIGEST_SIZE];	

    // judge if this message is already has instance_info , if it has,then send this message
    ret = message_get_define_expand(recv_msg,&msg_expand,TYPE_PAIR(MESSAGE,INSTANCE_INFO));
    if(ret<0)
        return -EINVAL;
    if(msg_expand!=NULL)
    {
	    ret=ex_module_sendmsg(sub_proc,recv_msg);
	    return ret;
    }


    RECORD(USER_DEFINE,CLIENT_STATE) * client_state;
    print_cubeaudit("enter keyevent_sendkey function!");

    instance_info = Talloc0(sizeof(*instance_info));
    if(instance_info == NULL)
        return -ENOMEM;
    // get client state
	client_state = proc_share_data_getpointer();

    // file the instance_info struct 
	proc_share_data_getvalue("proc_name",instance_info->proc_name);
	Strncpy(instance_info->user_name,client_state->user_name,DIGEST_SIZE);
	proc_share_data_getvalue("uuid",instance_info->node_uuid);

	new_msg=message_create(TYPE_PAIR(GENERAL_RETURN,STRING),NULL);	
	if(new_msg==NULL)
		return -EINVAL;
	ret=message_add_record(new_msg,keyevent_cmd);
	if(ret<0)
		return ret;

	ret=message_add_expand_data(new_msg,TYPE_PAIR(MESSAGE,INSTANCE_INFO),instance_info);
	if(ret<0)
		return ret;
    
	ret=ex_module_sendmsg(sub_proc,new_msg);
	return ret;
}

RECORD(MESSAGE,INSTANCE_INFO) * _create_instance_info()
{
	RECORD(MESSAGE,INSTANCE_INFO) * instance_info;
	BYTE local_uuid[DIGEST_SIZE];	
	char proc_name[DIGEST_SIZE];	
    RECORD(USER_DEFINE,CLIENT_STATE) * client_state;

    printf( " enter _create_instance_info\n");
    instance_info = Talloc0(sizeof(*instance_info));
    if(instance_info == NULL)
        return NULL;
    // get client state
	client_state = proc_share_data_getpointer();
    // file the instance_info struct 
    printf( " client_state addr %p\n",client_state);
	proc_share_data_getvalue("proc_name",instance_info->proc_name);
	Strncpy(instance_info->user_name,client_state->user_name,DIGEST_SIZE);
	proc_share_data_getvalue("uuid",instance_info->node_uuid);
    printf( " create instance_info finished\n");

    return instance_info;
    // file the instance_info struct 
}
