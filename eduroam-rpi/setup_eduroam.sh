#!/bin/bash
#----------------------------------------------------------
# Eduroam WiFi Configuration for Raspberry Pi - University of Galway
#----------------------------------------------------------

# Prompt for user credentials
read -p 'Username (e.g., CampusAccountID@universityofgalway.ie): ' USERNAME
read -sp 'Password: ' PASSWORD
echo ""

# Set CA certificate path (Ensure you have downloaded it)
CA_CERT="/etc/ssl/certs/galway_ca.pem"  # Update with actual path if different

# Escape special characters in password
ESCAPED_PASSWORD=$(printf '%s\n' "$PASSWORD" | sed -e 's/[\/&]/\\&/g')

# Generate wpa_supplicant.conf
#----------------------------------------------------------
sudo sh -c "printf 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
ap_scan=1
update_config=1
country=GB

network={
   ssid=\"eduroam\"
   proto=RSN
   key_mgmt=WPA-EAP
   eap=PEAP
   identity=\"%s\"
   password=\"%s\"
   ca_cert=\"/etc/ssl/certs/nuigalway_Managed_Radius_CA_Root.crt\"
   phase1=\"peaplabel=0\"
   phase2=\"auth=MSCHAPV2\"
   tls_disable_tlsv1_0=1
   tls_disable_tlsv1_1=1
}
' $USERNAME $PASSWORD > /etc/wpa_supplicant/wpa_supplicant.conf"


# Restart networking services to apply changes
sudo systemctl restart dhcpcd
sudo wpa_cli -i wlan0 reconfigure

echo "Eduroam configuration applied. Trying to connect..."
