
# make keys
cd ~
ssh-keygen

# cp public key into name suffixed by the hostname
cd ~/.ssh/
HOSTNAME=$(hostname)
NEWNAME=$(echo "id_rsa_${HOSTNAME}.pub")
touch "$NEWNAME"
cp id_rsa.pub > echo "$NEWNAME"

# allow access to gcloud cli
export PATH=$PATH:/snap/bin

# send to all instances
eval "gcloud compute scp $NEWNAME gcp_ghobadi_google_mit_edu@hvd-t4-vm-4:/tmp --zone us-west1-b"
eval "gcloud compute scp $NEWNAME gcp_ghobadi_google_mit_edu@hvd-t4-vm-3:/tmp --zone us-west1-b"
eval "gcloud compute scp $NEWNAME gcp_ghobadi_google_mit_edu@hvd-t4-vm-2:/tmp --zone us-west1-b"
eval "gcloud compute scp $NEWNAME gcp_ghobadi_google_mit_edu@hvd-t4-vm-1:/tmp --zone us-west1-b"