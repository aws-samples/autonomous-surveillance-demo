# Remote Controller

## Get Ready to use remote controller

- Fill <REPLACE_ME> in the JavaScript
- Open [remote_controller/index.html](remote_controller/index.html) in a browser
- Fill forms in the Settings section

### Fill <REPLACE_ME> in the JavaScript

`remote_controller/js/app-kvs.js` - Line 181-182

```js
const iotendpoint = '<REPLACE_ME>';  // AWS IoT Core Endpoint
const iotclientId = '<REPLACE_ME>';  // MQTT Client ID
```

`/remote_controller/js/capture.js` - Line 30

```js
var params = {
    CollectionId: "<REPLACE_ME>",  // Amazon Rekognition Collection ID
    Image:{
        Bytes: buffer,
    }
}
```

## Open index.html in a browser

Open `remote_controller/index.html` in a browser (Chrome recommended)

## Fill forms in the Setting section

After opening the index.html in a browser, click a triangle on the left of "Settings".

Type in Access Key ID, Secret Access Key and other settings.

now, it should start working

## If you want to change the map

1. Replace `remote_controller/img/map.svg` with your own map.

2. Set the destination coordinate and replace line 342-344, 355-357 in `remote_controller/js/app-kvs.js` with your own coordinate.

```js
payload["x"] = "-0.35";
payload["y"] = "-0.59";
payload["yaw"] = "2.7";
```

3. Tune line 224-225 in `remote_controller/js/app-kvs.js` so that the gray dot on the browser synchronizes with the actual robot.

```js
let x = 110 + odom["x"].toFixed(4) * 110;
let y = 10 + odom["y"].toFixed(4) * 110;
```

## If you want to use game controller

Here's how to control turtlebot3 with HORIPAD ULTIMATE wireless game controller.

#### If you are using iPad
You can see two axes, one cross button, four buttons with alphabet (X, Y, A, B), and menu button on its surface. On the side, there are four buttons, L1, L2, R1, R2.

Use right axe to control robot's movement, press L2 to start video streaming, and press R2 button to capture the video.

#### If you are using Macbook
You can see two axes, one cross button, four buttons with alphabet (X, Y, A, B), and menu button on its surface.

Use right axe to control robot's movement, press right of the cross button to start video streaming, and press menu button to capture the video.

## Links

- [Amazon Kinesis Video Streams WebRTC SDK for JavaScript](https://github.com/awslabs/amazon-kinesis-video-streams-webrtc-sdk-js)
  - Some JavaScript files are copied from the repository above and modified
- [AWS IoT SDK for JavaScript](https://github.com/aws/aws-iot-device-sdk-js)
  - `aws-iot-sdk-browser-bundle.js` is created by the package above
