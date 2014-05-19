r:\nsncdrparser>type D:\cdr\gzcg101.sacdr.txt|nsncdrparser search duration=0 gprsDownlinkVol="\d\d\d+" -s duration0.log
Start to parse the CDR file using patterns file:<sacdr.patterns>

Search 'duration=0 and gprsDownlinkVol=\d\d\d+',
Total 0 CDR was found
and had been saved to duration0.log

parsing/caculating time: 3.15800/0.01100
serviceCode=1010000001,1010000002,
r:\nsncdrparser>type gzcg101.sacdr.txt|nsncdrparser search duration=0 -s duration0.log
Start to parse the CDR file using patterns file:<sacdr.patterns>

Search 'duration=0',
Total 23 CDR was found
and had been saved to duration0.log

parsing/caculating time: 3.10400/0.01600

r:\nsncdrparser>grep duration duration0.log
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0
-->duration(14)    value: 0

r:\nsncdrparser>egrep -e "Downlink|Uplink" duration0.log
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 40
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
------>dataVolumeGPRSUplink(3)    value: 0
------>dataVolumeGPRSDownlink(4)    value: 0
