### deps

    pip install dpkt scapy


### build

    python -m examples.rgmii.top


### test

    python -m examples.rgmii.host


## board support

Tested on:

* cynthion  Numato RTL8211E           rx_delay=2e-9  ("rgmii", 0) # pmod a & b
* ecpix5    Numato RTL8211E           rx_delay=2e-9  ("rgmii", 1) # pmod 3 & 4
* ecpix5    built-in KSZ9031RNXCC-TR  rx_delay=0     ("rgmii", 0)
