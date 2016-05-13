# GO Bot Sense
GO Bot Sense acts as the ears and eyes of the go-bot ecosystem, collecting sensor data at locations within a park or attraction and relaying that information to the GO Bot AI.  Additionally, the GO Bot Sense allows visitors within the proximity of a GO Bot Sense node to receive information such as maps, tips, and alerts for that spacific location even when their is no Internet connectivity.  This software is deployable on Raspberry Pi hardware and supports a variety of sensors to collect data that can be used by the GO Bot AI.

Underlying our GO Bot Sense efforts are the following principles:

    * GO Bot Sense will be modular and expandable and something that can be customized for the specialized needs of different parks.
    * GO Bot Sense will be solar powered and easily deployed anywhere within the park.
    * GO Bot Sense will support a number of networking options, including
		* Shared wi-fi network
		* Ad hoc wi-fi mesh-network
		* Connected by a virtual "sneaker net" where information is relayed between GO Bot Sense nodes through interaction with rangers and visitors moving between beacons via Bluetooth LE
	* Total hardware costs should be kept under $100
	* Both the hardware and software should be open source licensed
		
This project is both a software and hardware solution.  The target platform at this time is Raspberry Pi and the target device is the Pi Zero.  Currently an initial prototype is being constructed on a Raspberry Pi 3 and provides sensors for temperature and counting people moving past the node.  More information on the hardware can be found below.

# Setup of the GO Bot Sense Raspbian Environment

These instructions assume you are starting from a fresh Raspberry Pi.

1.  Go get a fresh copy of the newest NOOBS operating system [here](http://www.raspberrypi.org/downloads "here").
2.  Format the MicroSD card and copy files from the NOOBS zip onto the MicroSD card
3.  Insert MicroSD card into Pi device and boot.  The NOOBS starter OS will boot.
4.  Select Raspbian as the OS to install and start the install process.
5.  Raspbian will install, reboot, and then boot to the Raspbian desktop.
6.  From the Raspbian desktop terminal or remotely using SSH, run the following commands to get your Raspbian environment up to date
	* sudo apt-get update
	* sudo apt-get upgrade
7.  Enable I2C support by following this guide:
    [Adafruit I2C Guide](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c "Adafruit I2C Guide")
	* sudo apt-get install python-smbus
	* sudo apt-get install i2c-tools
	* sudo raspi-config
	* sudo i2cdetect -y 1
8.  Enable your DS3231 RTC using the following guide:
    [DS3231 Guide](http://www.raspberrypi-spy.co.uk/2015/05/adding-a-ds3231-real-time-clock-to-the-raspberry-pi/ "DS3231 Guide")
	* sudo nano /etc/modules
	* sudo nano /etc/rc.local
	* sudo reboot
	* sudo i2cdetect -y 1
9.	Install the Adafruit library for the ADS1x15 Analog-to-Digital coverter
    * wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python3
	* sudo python3 -m pip install adafruit-ads1x15
10. Install python dependencies
    * sudo python3 -m pip install schedule
11. Go to your home directory.
    * cd ~
12. Clone the GitHub repository.
	* git clone https://github.com/bayeshack2016/go-bot-sense.git

# Configuration of GO Bot Sense

GO Bot Sense is configured through the "config.json" file found in the software root directory.  This file is JSON formatted and contains information about the specific node, the senses for the node, and the network sync mechanism.

# Starting GO Bot Sense

For the moment, just type "python3 node.py" to start the GO Bot Sense node.

# Hardware Configuration

The current prototype is being built with a Raspberry Pi 3 but is intended to run on a Pi Zero once they become readily available.  The Pi has had an I2C Real-Time Clock added since it needs to know the time without network connectivity.  In addition, an A2D card is connected via I2C to handle translation of analog sensor signals (initially, the only analog input is from a thermistor).  Finally, a PIR motion sensor is attached so that the node can detect nearby motion.  The whole system will be powered by a battery which is charged by a solar panel.  This aspect of the system has still not been prototyped but will be tested once a Pi Zero is available for testing.

The figure below shows the hardware wiring schematic for the prototype GO Bot Sense device.

![GO Bot Sense Hardware Schematic]("go-bot-sense-hardware.png")