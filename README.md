# Docker-V6NAT
Code for taking a Docker IPv6 prefix and NATing via a public /48

Fill in the variables at the top, and then run the script to create the IPTables rules. Make sure you setup a seperate Docker network with the default masquerading disabled, configure V4 NAT and ensure your Docker daemon has IPv6 enabled! (Will add instructions for this later).

Source: https://wiki.archiveteam.org/index.php/Running_Archive_Team_Projects_with_Docker#Enabling_IPv6
