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

// get values from form
const formValues = getFormValues();

//set parameter for Rekognition
var rekognition = new AWS.Rekognition({
    region: formValues.region,
    accessKeyId: formValues.accessKeyId,
    secretAccessKey: formValues.secretAccessKey,
    sessionToken: formValues.sessionToken,
    endpoint: formValues.endpoint,
});

//capture the video and authenticate
function capture(){
    //add canvas attribute to show capturedimage
    var video = document.getElementById('video');
    var $canvas = $('#canvas');
    $canvas.attr('width', "190px");
    $canvas[0].getContext('2d').drawImage(video, 0, 0, $canvas.width(), $canvas.height());
    $('#download').attr('href', $canvas[0].toDataURL('image/png'));
    var dataurl = $canvas[0].toDataURL('image/png');
    var bin = atob(dataurl.split(',')[1]);
    var buffer = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) {
        buffer[i] = bin.charCodeAt(i);
      }

    //get ready to send the image to rekognition
    var params = {
        CollectionId: "<REPLACE_ME>",
        Image:{
            Bytes: buffer,
        }
    }

    //show the result of rekognition
    var alert = document.getElementById("alert");
    var safe = document.getElementById("safe");
    rekognition.searchFacesByImage(params, function(err, data){
        alert.style.display = "none";
        safe.style.display = "none";
        if(err){
            //when there are no recognized person in the picture, show "Rekognition Failed"
            console.log(err, err.stack);
            alert.innerHTML = "Rekognition Failed";
            alert.style.display = "block";
            safe.style.display = "none";
        }
        else {
            if(!data.FaceMatches.length){
                //when there is unknown person in the picture, show "Rekognition Failed"
                alert.innerHTML = "Stranger Alert!!!";
                alert.style.display = "block";
                safe.style.display = "none";
            }else{
                //when there is registered person in the picture, show his or her name and turn ! to ◎
                var faces =[];
                for(let i = 0; i < data.FaceMatches.length; i++) {
                    faces[i]= data.FaceMatches[i].Face.ExternalImageId
                }
                safe.innerHTML = faces;
                safe.style.display = "block";
                alert.style.display = "none";
                var position=document.getElementById("position");
                x= position.style.top.split("p")[0];
                y= position.style.left.split("p")[0];
                for(let i=1;i<3;i++){
                    let camera = "camera"+i;
                    let isOk = "isOk_"+i;
                    let isOkMessage = "isOk_message_"+(i);
                    eachCamera = document.querySelector(`#${camera}`);
                    let cameraTop = window.getComputedStyle(eachCamera, null).getPropertyValue('top').split("p")[0];
                    let cameraLeft = window.getComputedStyle(eachCamera, null).getPropertyValue('left').split("p")[0];
                    cameraLeft+=45;

                    if(Math.abs(x-cameraTop)<30 && Math.abs(y-cameraLeft)<30){
                        var image = document.getElementById(isOk);
                        image.style.width="20px"
                        image.src = "img/authenticated.svg";
                        var message = document.getElementById(isOkMessage);
                        message.style.opacity="0";
                    }
                }
            }
        }
    });
}

//check the odometry of the robot every 1 second and if it is close enough, start rekognition process
function shouldCapture(){
    x= position.style.top.split("p")[0];
    y= position.style.left.split("p")[0];

    for(let i=1;i<3;i++){
        let camera = "camera"+i;
        eachCamera = document.querySelector(`#${camera}`);
        let cameraTop = window.getComputedStyle(eachCamera, null).getPropertyValue('top').split("p")[0];
        let cameraLeft = window.getComputedStyle(eachCamera, null).getPropertyValue('left').split("p")[0];
        cameraLeft= Number(cameraLeft)+45;
        if(Math.abs(x-cameraTop)<30 && Math.abs(y-cameraLeft)<30){
            capture();
        }
    }
}
setInterval(shouldCapture, 1000);
