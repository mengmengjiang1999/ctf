#!/bin/sh

rm instance/crypt_hub/lib/*

cd instance/crypt_hub/cert
ls | grep -v README | xargs rm
cd -

cd instance/crypt_hub/pubkey
ls | grep -v README | xargs rm
cd -

cd instance/crypt_hub/tcmkey
ls | grep -v README | xargs rm
cd -

rm instance/node/crypt_user/lib/*

cd instance/node/crypt_user/cert
ls | grep -v README | xargs rm
cd -

cd instance/node/crypt_user/pubkey
ls | grep -v README | xargs rm
cd -

cd instance/node/crypt_user/tcmkey
ls | grep -v README | xargs rm
cd -
