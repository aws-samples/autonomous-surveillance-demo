# Setup a robot

## Setup Raspberry Pi

- Model: Raspberry Pi 4 Model B (4GB)
- OS: Raspbian Buster

### Install Greengrass Core

Follow instructions: <https://docs.aws.amazon.com/greengrass/latest/developerguide/install-ggc.html#ggc-package-manager>.

Prepare `hash-setup.tar.gz` you downloaded in the [cloud setup process](../cloud/README.md).

```bash
# Replace `<RasPi-IP>` with IP address of your Raspberry Pi.
scp hash-setup.tar.gz pi@<RasPi-IP>:.
ssh pi@<RasPi-IP>

sudo adduser --system ggc_user
sudo addgroup --system ggc_group

sudo mkdir -p /greengrass
sudo tar -xzvf hash-setup.tar.gz -C /greengrass

cd /greengrass/certs/
sudo wget -O root.ca.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem
```

```bash
cd
mkdir greengrass-dependency-checker-GGCv1.10.x
cd greengrass-dependency-checker-GGCv1.10.x
wget https://github.com/aws-samples/aws-greengrass-samples/raw/master/greengrass-dependency-checker-GGCv1.10.x.zip
unzip greengrass-dependency-checker-GGCv1.10.x.zip
cd greengrass-dependency-checker-GGCv1.10.x
sudo ./check_ggc_dependencies | more
```

```bash
wget -O aws-iot-greengrass-keyring.deb https://d1onfpft10uf5o.cloudfront.net/greengrass-apt/downloads/aws-iot-greengrass-keyring.deb
sudo dpkg -i aws-iot-greengrass-keyring.deb
echo "deb https://dnw9lb6lzp2d8.cloudfront.net stable main" | sudo tee /etc/apt/sources.list.d/greengrass.list
sudo apt update
sudo apt install aws-iot-greengrass-core
sudo systemctl enable greengrass.service --now
```

Create robot on AWS RoboMaker console.

- Architecture: armhf
- Greengrass Group: autonomous-surveillance-NN

Submit the robot into fleet `autonomous-surveillance`.

### Install ROS

Follow instructions: <http://wiki.ros.org/ROSberryPi/Installing%20ROS%20Melodic%20on%20the%20Raspberry%20Pi>.

```bash
sudo sh -c 'echo "deb  http://packages.ros.org/ros/ubuntu  $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
sudo apt-get update

sudo apt-get install -y python-rosdep python-rosinstall-generator python-wstool python-rosinstall build-essential cmake
sudo rosdep init
rosdep update

mkdir ~/ros_catkin_ws
cd ~/ros_catkin_ws

rosinstall_generator ros_comm --rosdistro melodic --deps --wet-only --tar > melodic-desktop-wet.rosinstall
wstool init -j8 src melodic-desktop-wet.rosinstall

rosdep install -y --from-paths src --ignore-src --rosdistro melodic -r --os=debian:buster
sudo ./src/catkin/bin/catkin_make_isolated --install -DCMAKE_BUILD_TYPE=Release --install-space /opt/ros/melodic -j2
echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
```

### Install turtlebot packages

Install dependencies and apply patch.

```bash
sudo apt install libeigen3-dev python-sip-dev libogre-1.9-dev

mkdir -p ~/ros_catkin_ws/external_src
cd ~/ros_catkin_ws/external_src
wget http://sourceforge.net/projects/assimp/files/assimp-3.1/assimp-3.1.1_no_test_models.zip/download -O assimp-3.1.1_no_test_models.zip
unzip assimp-3.1.1_no_test_models.zip
cd assimp-3.1.1
cmake .
make
sudo make install
```

Add turtlebot packages into workspace.

```bash
cd ~/ros_catkin_ws

rosinstall_generator turtlebot3 turtlebot3_msgs --rosdistro melodic --deps --wet-only --tar > melodic-turtlebot3-wet.rosinstall
wstool merge -t src melodic-turtlebot3-wet.rosinstall
wstool update -t src

rosdep install -y --from-paths src --ignore-src --rosdistro melodic -r --os=debian:buster
sudo ./src/catkin/bin/catkin_make_isolated --install --force-cmake -DCMAKE_BUILD_TYPE=Release --install-space /opt/ros/melodic -j2
```

### Install navigation packages

```bash
cd ~/ros_catkin_ws

rosinstall_generator navigation --rosdistro melodic --deps --wet-only --tar > melodic-navigation-wet.rosinstall
wstool merge -t src melodic-navigation-wet.rosinstall
wstool update -t src

rosdep install -y --from-paths src --ignore-src --rosdistro melodic -r --os=debian:buster
sudo ./src/catkin/bin/catkin_make_isolated --install --force-cmake -DCMAKE_BUILD_TYPE=Release --install-space /opt/ros/melodic -j2
```

### Test roslaunch

```bash
roscore &
roslaunch turtlebot3_bringup turtlebot3_core.launch
```

### Create service

Add lines below to `.bashrc`.

```bash
export ROS_HOSTNAME=$(hostname).local
export ROS_MASTER_URI=http://$ROS_HOSTNAME:11311·
export TURTLEBOT3_MODEL=burger
```

- Copy `systemd/roscore.service` to `/lib/systemd/system/roscore.service`.
- Copy `systemd/turtlebot.service` to `/lib/systemd/system/turtlebot.service`.
- Copy `systemd/bin/roscore.sh` to `/opt/ros/melodic/bin/roscore.sh`.
- Copy `systemd/bin/turtlebot.sh` to `/opt/ros/melodic/bin/turtlebot.sh`.
- Make `roscore.sh` and `turtlebot.sh` executable.

```bash
sudo chmod +x /opt/ros/melodic/bin/roscore.sh
sudo chmod +x /opt/ros/melodic/bin/turtlebot.sh
```

- Enable services

```bash
sudo systemctl daemon-reload
sudo systemctl enable roscore --now
sudo systemctl enable turtlebot --now
```

### Install KVS WebRTC SDK

Follow instructions: <https://github.com/awslabs/amazon-kinesis-video-streams-webrtc-sdk-c>.

```bash
sudo apt install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev gstreamer1.0-plugins-base-apps gstreamer1.0-plugins-bad gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-tools gstreamer1.0-omx
cd
git clone --recursive https://github.com/awslabs/amazon-kinesis-video-streams-webrtc-sdk-c.git
mkdir -p amazon-kinesis-video-streams-webrtc-sdk-c/build
cd amazon-kinesis-video-streams-webrtc-sdk-c/build
cmake ..
make
```

### Setup Policy for KVS WebRTC

Attach an IoT policy `AutonomousSurveillanceKVSPolicy` created by CDK to Greengrass Core's certificate.

Update `samples/kvsWebRTCClientMasterGstreamerSample.c` to modify resolution and audio playback configuration.

```diff
--- a/samples/kvsWebRTCClientMasterGstreamerSample.c
+++ b/samples/kvsWebRTCClientMasterGstreamerSample.c
@@ -143,7 +143,7 @@ PVOID sendGstreamerAudioVideo(PVOID args)
     switch (pSampleConfiguration->mediaType) {
         case SAMPLE_STREAMING_VIDEO_ONLY:
             pipeline = gst_parse_launch(
-                    "autovideosrc ! queue ! videoconvert ! video/x-raw,width=1280,height=720,framerate=30/1 ! x264enc bframes=0 speed-preset=veryfast key-int-max=30 bitrate=512 ! "
+                    "autovideosrc ! queue ! videoconvert ! video/x-raw,width=640,height=480,framerate=30/1 ! x264enc bframes=0 speed-preset=veryfast key-int-max=30 bitrate=512 ! "
                     "video/x-h264,stream-format=byte-stream,alignment=au,profile=baseline ! appsink sync=TRUE emit-signals=TRUE name=appsink-video",
                     &error);
             break;
@@ -247,7 +249,7 @@ PVOID receiveGstreamerAudioVideo(PVOID args)

     switch (pSampleStreamingSession->pAudioRtcRtpTransceiver->receiver.track.codec) {
         case RTC_CODEC_OPUS:
-            audioDescription = "appsrc name=appsrc-audio ! opusparse ! decodebin ! autoaudiosink";
+            audioDescription = "appsrc name=appsrc-audio ! opusparse ! decodebin ! audioconvert ! alsasink";
             break;
```

Update `samples/Common.c` to use device certificate.

```diff
--- a/samples/Common.c
+++ b/samples/Common.c
@@ -574,21 +574,29 @@ STATUS createSampleConfiguration(PCHAR channelName, SIGNALING_CHANNEL_ROLE_TYPE

     CHK(NULL != (pSampleConfiguration = (PSampleConfiguration) MEMCALLOC(1, SIZEOF(SampleConfiguration))), STATUS_NOT_ENOUGH_MEMORY);

-    CHK_ERR((pAccessKey = getenv(ACCESS_KEY_ENV_VAR)) != NULL, STATUS_INVALID_OPERATION, "AWS_ACCESS_KEY_ID must be set");
-    CHK_ERR((pSecretKey = getenv(SECRET_KEY_ENV_VAR)) != NULL, STATUS_INVALID_OPERATION, "AWS_SECRET_ACCESS_KEY must be set");
-    pSessionToken = getenv(SESSION_TOKEN_ENV_VAR);
+    // CHK_ERR((pAccessKey = getenv(ACCESS_KEY_ENV_VAR)) != NULL, STATUS_INVALID_OPERATION, "AWS_ACCESS_KEY_ID must be set");
+    // CHK_ERR((pSecretKey = getenv(SECRET_KEY_ENV_VAR)) != NULL, STATUS_INVALID_OPERATION, "AWS_SECRET_ACCESS_KEY must be set");
+    // pSessionToken = getenv(SESSION_TOKEN_ENV_VAR);

     if ((pSampleConfiguration->channelInfo.pRegion = getenv(DEFAULT_REGION_ENV_VAR)) == NULL) {
         pSampleConfiguration->channelInfo.pRegion = DEFAULT_AWS_REGION;
     }

-    CHK_STATUS(lookForSslCert(&pSampleConfiguration));
-
-    CHK_STATUS(createStaticCredentialProvider(pAccessKey, 0,
-                                              pSecretKey, 0,
-                                              pSessionToken, 0,
-                                              MAX_UINT64,
-                                              &pSampleConfiguration->pCredentialProvider));
+    // CHK_STATUS(lookForSslCert(&pSampleConfiguration));
+
+    // CHK_STATUS(createStaticCredentialProvider(pAccessKey, 0,
+    //                                           pSecretKey, 0,
+    //                                           pSessionToken, 0,
+    //                                           MAX_UINT64,
+    //                                           &pSampleConfiguration->pCredentialProvider));
+    CHK_STATUS(createLwsIotCredentialProvider(
+            "cce8pmyjjo3iw.credentials.iot.ap-northeast-1.amazonaws.com",  // IoT credentials endpoint
+            "/greengrass/certs/random-hash.cert.pem",  // path to iot certificate
+            "/greengrass/certs/random-hash.private.key", // path to iot private key
+            "/greengrass/certs/root.ca.pem", // path to CA cert
+            "AutonomousSurveillanceRoleAlias", // IoT role alias
+            "autonomous-surveillance-01_Core", // iot thing name, recommended to be same as your channel name
+            &pSampleConfiguration->pCredentialProvider));

     pSampleConfiguration->audioSenderTid = INVALID_TID_VALUE;
     pSampleConfiguration->videoSenderTid = INVALID_TID_VALUE;
@@ -625,6 +633,7 @@ STATUS createSampleConfiguration(PCHAR channelName, SIGNALING_CHANNEL_ROLE_TYPE
     ATOMIC_STORE_BOOL(&pSampleConfiguration->recreateSignalingClient, FALSE);

         CVAR_FREE(pSampleConfiguration->cvar);
     }

-    freeStaticCredentialProvider(&pSampleConfiguration->pCredentialProvider);
+    freeIotCredentialProvider(&pSampleConfiguration->pCredentialProvider);
+

     MEMFREE(*ppSampleConfiguration);
     *ppSampleConfiguration = NULL;
```

Build and test stream.

```bash
cd build
make
sudo chmod o+r /greengrass/certs/random-hash.private.key

AWS_DEFAULT_REGION=<REGION> ./kvsWebrtcClientMaster autonomous-surveillance-01
```

Copy `systemd/kvs-webrtc.service` to `/lib/systemd/system/kvs-webrtc.service`.

Enable kvs-webrtc.service

```bash
sudo systemctl daemon-reload
sudo systemctl enable kvs-webrtc --now
```

## Setup Autonomous Surveillance demo ROS packages

- Update `robot_ws/src/autonomous_surverillance/settings/settings.yaml` and replace `<REPLACE_ME>` with your S3 bucket name
- Download [AmazonRootCA1.pem](https://www.amazontrust.com/repository/AmazonRootCA1.pem), private key and client certificate for your Robot into `robot_ws/src/deps/aws_iot_connector/certs` directory.
- Update `robot_ws/src/deps/aws_iot_connector/certs/config.yaml` and replace `<REPLACE_ME>` with your parameters

You can use `ws_setup.sh` in [aws-robomaker-sample-application-delivery-challenge](https://github.com/aws-samples/aws-robomaker-sample-application-delivery-challenge) to setup these files automatically.

- Transfer robot_ws directory

```bash
# Replace `<RasPi-IP>` with IP address of your Raspberry Pi.
scp -r robot/robot_ws pi@<RasPi-IP>:.

ssh pi@<RasPi-IP>
sudo -H pip install awscli AWSIoTPythonSDK boto3
echo "source ~/robot_ws/install/setup.bash" >> ~/.bashrc

roslaunch autonomous_surveillance robot_navigation.launch
```

### Setup Autonomous Surveillance demo service

- Copy `systemd/autonomous_surveillance.service` to `/lib/systemd/system/autonomous_surveillance.service`.
- Copy `systemd/bin/autonomous_surveillance.sh` to `/opt/ros/melodic/bin/autonomous_surveillance.sh`.
- Make `autonomous_surveillance.sh` executable.

```bash
sudo chmod +x /opt/ros/melodic/bin/autonomous_surveillance.sh
```

- Enable service

```bash
sudo systemctl daemon-reload
sudo systemctl enable autonomous_surveillance --now
```

## Links

- [aws-robomaker-sample-application-delivery-challenge](https://github.com/aws-samples/aws-robomaker-sample-application-delivery-challenge)
  - Some ROS source codes are copied from the repository above and modified
