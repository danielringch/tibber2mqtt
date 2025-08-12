# tibber2mqtt
Publishes Tibber live consumption data from Tibber API per MQTT.

## Introduction

If you are a customer of [Tibber](https://tibber.com/) and use a [Tibber Pulse](https://tibber.com/de/pulse), you can retrieve realtime consumption data via the Tibber API.

This program publishes realtime consumption data from Tibber to one or more MQTT brokers of your choise.

The power consumption/ production value is published via MQTT as a single int16 or int32 value in Watts, negative values indicate power production.

## Get tibber token and home id

* Go to https://developer.tibber.com/settings/access-token , log in with your Tibber credentials and you will see the access token
* After this, open https://developer.tibber.com/explorer and paste the following code into the left text box:
```
{
  viewer {
    homes {
      id
    }
  }
}
```
* Execute the query (play button above the text box) and you will see your home id in the left text box

## **Prerequisites**

- Python version 3.11 or newer with pip + venv

This program should run in any OS, but I have no capacity to test this, so feedback is appreciated. My test machines run Ubuntu and Raspbian.

## **Install**

```
git clone https://github.com/danielringch/tibber2mqtt.git
python3 -m venv <path to virtual environment>
source <path to virtual environment>/bin/activate
python3 -m pip install -r requirements.txt
```

## **Configuration**

The configuration is done via yaml file. The example file can be found in [config/sample.yaml](config/sample.yaml)

To keep sensitive content out of config files, some parameters can also be passed using environment variables. See the example config file for further explanations.

## **Usage**

```
source <path to virtual environment>/bin/activate
python3 -B tibber2mqtt/tibber2mqtt.py --config /path/to/your/config/file.yaml
```

## **Get support**

You have trouble getting started? Something does not work as expected? You have some suggestions or thoughts? Please let me know.

Feel free to open an issue here on github or contact me on reddit: [3lr1ng0](https://www.reddit.com/user/3lr1ng0).
