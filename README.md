![Project Clearwater](https://github.com/yetanothercarbot/govhack2020/raw/master/misc/banner.png)

# by Team Sanity is Optional - GovHack 2020.

[View our video covering our project here!](https://www.youtube.com/watch?v=1ijAqY6fryI)

Our project uses IoT devices to track plastic waste. It comprises of three main parts - an AWS EC2 Instance, smart labels and readers in waterways.

# AWS EC2 Instance
The EC2 instance is running a REST api developed in python using Flask. When the scanners read a tag, the information is posted to the EC2 instance as CSV. The API then stores this information into the database, after performing conversions a time conversion from epoch to a normal representation of time. All the sensors can update their epoch clock to match the server by performing a GET request. Additionally, the API also can read information from a mobile phone application which is still in the concept stage. Another feature that could be added into this API is a request for the data which can then be used for visulizations and other types of analysis.

# Smart Labels
The requirements for the labels are relatively low. In the proof of concept, NTAG213 stickers were used. These run at 13.56MHz and 144 bytes of user memory. However, in practise, lower frequency tags would likely be better for improved range and object penetration without increasing power. Tags with less user memory could be used to reduce cost of the smart labels.

| Size (bytes) | Type     | Use             | Example       |
|--------------|----------|-----------------|---------------|
| 8            | uint64_t | GUID            | 221           |
| 8            | uint64_t | UPC             | 9300605120693 |
| 8            | uint64_t | Transaction ID  | 4311          |
| 4            | float    | Store longitude | -27.506610    |
| 4            | float    | Store latitude  | 152.947870    |
| 4            | uint32_t | Purchase time   | 1597403508    |
| 1            | uint8_t  | Material type   | 7             |

- Using only floats rather than doubles does lose some accuracy, however the tags can only be written 4 bytes at a time, making it difficult to use doubles. 
- The material type is intended for faster or easier processing at recycling plants and is not transmitted to the AWS instance.

The only fields that would be programmed when the product is bottled would be it's GUID, UPC and material type. The checkout process can be streamlined by reading the Universal Product Code (UPC) from the RFID label rather than requiring the barcode to be scanned. The point of sales system will then also write the store location, transaction ID and time of purchase to the tag before locking it, preventing any changes being made to the data.

The transaction ID is not universally unique, and the PoS does not notify the central database server of the sale. It is only used when identifying if pieces of litter were likely deposited in a similar place and time.

# Scanners
In the proof of concept, the scanners were built using an ESP8266 development board which has builtin WiFi, and a PN532 rfid module. For an actual design, we'd recommend using mobile data connections - such as the IoT plans offered by Telstra - to communicate with the central database. It only uses a handful of bytes each time. Furthermore, lower frequency tags would allow better range without increasing power draw. 

The scanners could likely be powered off a solar panel and battery combination - the microcontroller would spend most of its time in deep sleep, and only activate its mobile data connection when required to transmit data. 
