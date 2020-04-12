# append transferred keys to authorized_keys
for f in /tmp/id_rsa_hvd-*; do cat $f >> ~/.ssh/authorized_keys; done

# show new authorized_keys
cat ~/.ssh/authorized_keys
