// Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
//
// Permission is hereby granted, free of charge, to any person obtaining a copy of this
// software and associated documentation files (the "Software"), to deal in the Software
// without restriction, including without limitation the rights to use, copy, modify,
// merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
// permit persons to whom the Software is furnished to do so.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
// PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
// HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
// OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
// SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//

const awsIot = require('aws-iot-device-sdk');
let moveAction = "";

function configureLogging() {
    function log(level, messages) {
        const text = messages
            .map(message => {
                if (typeof message === 'object') {
                    return JSON.stringify(message, null, 2);
                } else {
                    return message;
                }
            })
            .join(' ');
        $('#logs').prepend($(`<div class="${level.toLowerCase()}">`).text(`[${new Date().toISOString()}] [${level}] ${text}\n`));
    }

    console._warn = console.warn;
    console.warn = function (...rest) {
        log('WARN', Array.prototype.slice.call(rest));
        console._warn.apply(this, rest);
    };

    console._log = console.log;
    console.log = function (...rest) {
        log('INFO', Array.prototype.slice.call(rest));
        console._log.apply(this, rest);
    };
}

// get random client ID
function getRandomClientId() {
    return Math.random()
        .toString(36)
        .substring(2)
        .toUpperCase();
}

// get Values from form
function getFormValues() {
    return {
        region: $('#region').val(),
        channelName: $('#channelName').val(),
        clientId: $('#clientId').val() || getRandomClientId(),
        sendVideo: $('#sendVideo').is(':checked'),
        sendAudio: $('#sendAudio').is(':checked'),
        openDataChannel: $('#openDataChannel').is(':checked'),
        widescreen: $('#widescreen').is(':checked'),
        fullscreen: $('#fullscreen').is(':checked'),
        useTrickleICE: $('#useTrickleICE').is(':checked'),
        natTraversalDisabled: $('#natTraversalDisabled').is(':checked'),
        forceTURN: $('#forceTURN').is(':checked'),
        accessKeyId: $('#accessKeyId').val(),
        endpoint: null,
        secretAccessKey: $('#secretAccessKey').val(),
        sessionToken: $('#sessionToken').val() || null,
    };
}

function toggleDataChannelElements() {
    if (getFormValues().openDataChannel) {
        $('.datachannel').removeClass('d-none');
    } else {
        $('.datachannel').addClass('d-none');
    }
}

function onStatsReport(report) {
    // TODO: Publish stats
}

window.addEventListener('unhandledrejection', function (event) {
    console.error(event.reason.toString());
    event.preventDefault();
});

configureLogging();
function connectKVS() {
    console.log("Start viewer");

    const remoteView = $('.viewer .remote-view')[0];
    const formValues = getFormValues();
    console.log(formValues);

    toggleDataChannelElements();

    startViewer(null, remoteView, formValues, onStatsReport, event => {
        return;
    });
}

$('#viewer-button').click(async () => {
    console.log("Start viewer");

    const remoteView = $('.viewer .remote-view')[0];
    const formValues = getFormValues();
    console.log(formValues);

    toggleDataChannelElements();

    startViewer(null, remoteView, formValues, onStatsReport, event => {
        return;
    });
});

$('#stop-viewer-button').click(async () => {
    stopViewer();
});

// Read/Write all of the fields to/from localStorage so that fields are not lost on refresh.
const urlParams = new URLSearchParams(window.location.search);
const fields = [
    {field: 'channelName', type: 'text'},
    {field: 'clientId', type: 'text'},
    {field: 'region', type: 'text'},
    {field: 'accessKeyId', type: 'text'},
    {field: 'secretAccessKey', type: 'text'},
    {field: 'sessionToken', type: 'text'},
    {field: 'sendVideo', type: 'checkbox'},
    {field: 'sendAudio', type: 'checkbox'},
    {field: 'widescreen', type: 'radio', name: 'resolution'},
    {field: 'fullscreen', type: 'radio', name: 'resolution'},
    {field: 'openDataChannel', type: 'checkbox'},
    {field: 'useTrickleICE', type: 'checkbox'},
    {field: 'natTraversalEnabled', type: 'radio', name: 'natTraversal'},
    {field: 'forceTURN', type: 'radio', name: 'natTraversal'},
    {field: 'natTraversalDisabled', type: 'radio', name: 'natTraversal'},
];
fields.forEach(({field, type, name}) => {
    const id = '#' + field;

    // Read field from localStorage
    try {
        const localStorageValue = localStorage.getItem(field);
        if (localStorageValue) {
            if (type === 'checkbox' || type === 'radio') {
                $(id).prop('checked', localStorageValue === 'true');
            } else {
                $(id).val(localStorageValue);
            }
            $(id).trigger('change');
        }
    } catch (e) {
        /* Don't use localStorage */
    }

    // Read field from query string
    if (urlParams.has(field)) {
        paramValue = urlParams.get(field);
        if (type === 'checkbox' || type === 'radio') {
            $(id).prop('checked', paramValue === 'true');
        } else {
            $(id).val(paramValue);
        }
    }

    // Write field to localstorage on change event
    $(id).change(function () {
        try {
            if (type === 'checkbox') {
                localStorage.setItem(field, $(id).is(':checked'));
            } else if (type === 'radio') {
                fields
                    .filter(fieldItem => fieldItem.name === name)
                    .forEach(fieldItem => {
                        localStorage.setItem(fieldItem.field, fieldItem.field === field);
                    });
            } else {
                localStorage.setItem(field, $(id).val());
            }
        } catch (e) {
            /* Don't use localStorage */
        }
    });
});

// The page is all setup. Hide the loading spinner and show the page content.
console.log('Page loaded');

async function mainIoT() {
    const iotendpoint = '<REPLACE_ME>';
    const iotclientId = '<REPLACE_ME>';
    const subscribeTopic = "autonomous-surveillance/dt/#";
    const publishTopicRos = "autonomous-surveillance/cmd/ros";
    const publishTopicGG = "autonomous-surveillance/cmd/gg";

    const formValues = getFormValues();
    const deviceIot = awsIot.device({
        region: formValues.region,
        clientId: iotclientId,
        accessKeyId: formValues.accessKeyId,
        secretKey: formValues.secretAccessKey,
        protocol: 'wss',
        port: 443,
        host: iotendpoint
    });

    deviceIot.on('message', function (topic, payload) {
        const json = JSON.parse(payload.toString());
        console.log(json);

        const command = json["command"];
        if (command === "location") {
            odom = json["odom"];
            if (odom) {
                const position = document.getElementById("position");
                let x = 110 + odom["x"].toFixed(4) * 110;
                let y = 10 + odom["y"].toFixed(4) * 110;
                position.style.top = x + "px";
                position.style.left = y + "px";
            }
        } else if (command === "result") {
            alert(json["message"])
        } else if (command === "battery") {
            let percentage = (json["battery_state"]["percentage"] - 98) * 100 / 13;
            percentage = Math.floor(percentage);
            const battery = document.getElementById("battery");
            battery.textContent = percentage + "%";
        } else if (command === "navigation") {
            var manual = document.getElementById("manual");
            var auto = document.getElementById("auto");
            manual.className = "not_selected";
            auto.className = "selected";
        }else if (command=== "navigation"){
            var manual=document.getElementById("manual");
            var auto=document.getElementById("auto");
            manual.className="not_selected"
            auto.className="selected"
            if(json["camera"]==="camera1"){
                console.log("camera1 selected")
                var image = document.getElementById("isOk_1");
                image.style.display="block"
            }else if(json["camera"]==="camera2"){
                var image = document.getElementById("isOk_2");
                image.style.display="block"
            }
        }

    });

    deviceIot.subscribe(subscribeTopic, undefined, function (err, granted) {
        if (err) {
            console.log('subscribe error: ' + err);
        } else {
            console.log('subscribe success');
        }
    });

    //----

    setInterval(syncJob, 1000);

    function syncJob() {
        let payload = {};
        let shouldPublish = false;
        if (moveAction !== "") {
            console.log(moveAction);
            payload["command"] = "move";
            payload["action"] = moveAction;
            shouldPublish = true;
        }
        if (shouldPublish) {
            deviceIot.publish(publishTopicRos, JSON.stringify(payload));
            if (moveAction === "stop") {
                moveAction = "";
            }
            var manual = document.getElementById("manual");
            var auto = document.getElementById("auto");
            manual.className = "selected";
            auto.className = "not_selected";
        }
    }

    actions = ["forward", "backward", "left", "right", "stop"];

    $("#button_forward").click(() => {
        moveAction = "forward";
    });
    $("#button_backward").click(() => {
        moveAction = "backward";
    });
    $("#button_left").click(() => {
        moveAction = "left";
    });
    $("#button_right").click(() => {
        moveAction = "right";
    });
    $("#button_stop").click(() => {
        moveAction = "stop";
    });

    $("#button_restart_kvs").click(() => {
        const payload = {"action": "webrtc", "command": "restart"};
        deviceIot.publish(publishTopicGG, JSON.stringify(payload));
    });
    $("#button_start_kvs").click(() => {
        const payload = {"action": "webrtc", "command": "start"};
        deviceIot.publish(publishTopicGG, JSON.stringify(payload));
    });
    $("#button_stop_kvs").click(() => {
        const payload = {"action": "webrtc", "command": "stop"};
        deviceIot.publish(publishTopicGG, JSON.stringify(payload));
    });

    const setting = document.getElementById("details");
    const background = document.getElementById("background");
    $("#showsetting").click(() => {
        if (setting.style.display === "block") {
            setting.style.display = "none";
            background.style.height = "1200px"
        } else {
            setting.style.display = "block";
            background.style.height = "2200px"
        }
    });

    //for navigation delete when I get camera
    const camera1 = document.getElementById("camera1");
    const camera2 = document.getElementById("camera2");

    let payload = {};
    camera1.onclick = () => {
        payload["command"] = "navigation";
        payload["action"] = "setGoal";
        payload["x"] = "-0.35";
        payload["y"] = "-0.59";
        payload["yaw"] = "2.7";
        deviceIot.publish(publishTopicRos, JSON.stringify(payload));
        var manual = document.getElementById("manual");
        var auto = document.getElementById("auto");
        manual.className = "not_selected";
        auto.className = "selected";
    };

    camera2.onclick = () => {
        payload["command"] = "navigation";
        payload["action"] = "setGoal";
        payload["x"] = "0.08";
        payload["y"] = "0.13";
        payload["yaw"] = "1.3";
        deviceIot.publish(publishTopicRos, JSON.stringify(payload));
        var manual = document.getElementById("manual");
        var auto = document.getElementById("auto");
        manual.className = "not_selected";
        auto.className = "selected";
    };
}

// window.onload = mainIoT();
window.addEventListener('load', mainIoT);
