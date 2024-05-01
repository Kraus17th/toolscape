#!/bin/bash
echo "this is updater script"
echo "app, full or clean?"
read action
if [[ ( $action == app ) ]];
then
echo "There is deb source"
cat /etc/apt/sources.list
echo "Starting update ..."
apt-get update
apt-get upgrade -y
exit 0
elif [[ ( $action == full ) ]];
then
echo "There is deb source"
cat /etc/apt/sources.list
echo "Starting full update ..."
apt-get update
apt full-upgrade -y
exit 0
elif [[ ( $action == clean ) ]];
then
echo "There is deb source"
cat /etc/apt/sources.list
echo "Starting clean ..."
apt-get update
apt autoremove -y
apt autoclean -y
apt clean -y
exit 0
else
echo "Error. app, full or clean?"
exit 1
fi
