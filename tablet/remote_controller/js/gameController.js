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

gamePadButton=document.getElementById("useGamePad");
let useGamePad=false;

//change color of "use gamepad" button when the button is pushed
gamePadButton.onclick = () =>{
    console.log(gamePadButton.style.backgroundColor);
    if(gamePadButton.style.backgroundColor==="rgb(235, 95, 7)"){
        gamePadButton.style.backgroundColor="#aaaaaa";
        useGamePad=false;
    }else{
        gamePadButton.style.backgroundColor="#eb5f07";
        useGamePad=true;
    }
}

//use gamepad api
var rAF = window.mozRequestAnimationFrame ||
          window.webkitRequestAnimationFrame ||
          window.requestAnimationFrame;
function update() {
    var pads = navigator.getGamepads ? navigator.getGamepads() :
                    (navigator.webkitGetGamepads ? navigator.webkitGetGamepads : []);

    pads = pads[0];
    if(pads) {
        //get buttons' value
        var but = [];
        for(var i = 0 ; i < pads.buttons.length; i++) {
            var val = pads.buttons[i];
            var pressed = val >0.7;
            if (typeof(val) == "object") {
                pressed = val.pressed;
                val     = val.value;
            }
            but[i] = val;
        }

        //get axes' value
        var axes = pads.axes;

        //PC browser or iPad browser
        if(useGamePad){
            const forwardButton=document.getElementById("button_forward");
            const backwardButton=document.getElementById("button_backward");
            const rightButton=document.getElementById("button_right");
            const leftButton=document.getElementById("button_left");
            const stopButton=document.getElementById("button_stop");
            forwardButton.style.background="url(img/controller-up.svg)";
            backwardButton.style.background="url(img/controller-back.svg)";
            rightButton.style.background="url(img/controller-right.svg)";
            leftButton.style.background="url(img/controller-left.svg)";
            stopButton.style.background="url(img/controller-stop.svg)";
            if(pads.buttons.length===8){
                //command robot to move
                if(axes[2]>0.9){
                    moveAction = "right";
                    rightButton.style.background="url(img/controller-right-clicked.svg)";
                }else if(axes[2]<-0.9){
                    moveAction = "left";
                    leftButton.style.background="url(img/controller-left-clicked.svg)";
                }else if(axes[3]>0.9){
                    moveAction = "forward";
                    forwardButton.style.background="url(img/controller-up-clicked.svg)";
                }else if(axes[3]<-0.9){
                    moveAction = "backward";
                    backwardButton.style.background="url(img/controller-back-clicked.svg)";
                }else if(moveAction==="stop"){
                    moveAction="";
                }else{
                    moveAction="stop";
                }
                if(but[6]===1){
                   //if button 6 is pushed, connect to KVS
                   connectKVS();
                }
                if(but[7]===1){
                    //if button 7 is pushed, capture the video
                    capture();
                }
            }else{
                //command robot to move
                if(axes[2]>0.9){
                    moveAction = "right";
                    rightButton.style.background="url(img/controller-right-clicked.svg)";
                }else if(axes[2]<-0.9){
                    moveAction = "left";
                    leftButton.style.background="url(img/controller-left-clicked.svg)";
                }else if(axes[5]>0.9){
                    moveAction = "forward";
                    forwardButton.style.background="url(img/controller-up-clicked.svg)";
                }else if(axes[5]<-0.9){
                    moveAction = "backward";
                    backwardButton.style.background="url(img/controller-back-clicked.svg)";
                }else if(moveAction==="stop"){
                    moveAction="";
                }else{
                    moveAction="stop";
                }
                if(axes[4]===1){
                   //connect to KVS
                   connectKVS();
                }
                if(but[0]===1){
                    //capture the video
                    capture();
                }
            }
        }

    }
    rAF(update);
}

//Start
rAF(update);