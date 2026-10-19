dirs= login_server login_user user_label file_acl key_event key_manage key_event_user key_manage_server key_manage_user key_manage_hack policy_rw
all:
	$(foreach N,$(dirs),make -C $(N) || exit "$$?";)
clean:
	rm -f ../plugin/*.so ../plugin/*.cfg
	$(foreach N,$(dirs),make clean -C $(N);)
	rm -f *~


