var pc = null;
var dc = null, dcInterval = null;

var start_btn = document.getElementById('start');
var stop_btn = document.getElementById('stop');
var statusField = document.getElementById('status');

function btn_show_stop() {
    start_btn.classList.add('d-none');
    stop_btn.classList.remove('d-none');
}

function btn_show_start() {
    stop_btn.classList.add('d-none');
    start_btn.classList.remove('d-none');
    statusField.innerText = 'Press start';
}

function negotiate() {
    return pc.createOffer().then(function (offer) {
        return pc.setLocalDescription(offer);
    }).then(function () {
        return new Promise(function (resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function () {
        var offer = pc.localDescription;
        console.log(offer.sdp);
        return fetch('offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function (response) {
        return response.json();
    }).then(function (answer) {
        console.log(answer.sdp);
        return pc.setRemoteDescription(answer);
    }).catch(function (e) {
        console.log(e);
        btn_show_start();
    });
}

function updateTranscriptionBox(text, isPartial) {
    const transcriptionBox = document.getElementById('transcription-box');
    let content = transcriptionBox.innerHTML;

    // Remove the previous partial text if it exists and remove the old cursor
    content = content.replace(/<span class="partial">.*?<\/span>/, '');
    content = content.replace(/<div id="transcription-cursor"><\/div>/, '');

    // Update content with the new text and add the blinking cursor
    if (isPartial) {
        content += `<span class="partial">${text}</span>`;
    } else {
        content += `${text} `;
    }

    // Add the blinking cursor at the end
    content += '<div id="transcription-cursor"></div>';
    transcriptionBox.innerHTML = content;

    // Ensure the transcription box scrolls to the bottom as new text is added
    transcriptionBox.scrollTop = transcriptionBox.scrollHeight;
}


function performRecvText(str) {
    updateTranscriptionBox(str, false);
}

function performRecvPartial(str) {
    updateTranscriptionBox(str, true);
}

function start() {
    // Clear the transcription box
    const transcriptionBox = document.getElementById('transcription-box');
    transcriptionBox.innerHTML = '';
    
    btn_show_stop();
    statusField.innerText = 'Connecting...';
    var config = {
        sdpSemantics: 'unified-plan',
        iceServers: [{urls: 'stun:stun.l.google.com:19302'}]
    };

    pc = new RTCPeerConnection(config);

    

    dc = pc.createDataChannel('result');
    dc.onclose = function () {
        clearInterval(dcInterval);
        console.log('Closed data channel');
        btn_show_start();
    };
    dc.onopen = function () {
        console.log('Opened data channel');
    };
    dc.onmessage = function (messageEvent) {
        statusField.innerText = "Listening... say something";

        if (!messageEvent.data) {
            return;
        }

        let voskResult;
        try {
            voskResult = JSON.parse(messageEvent.data);
        } catch (error) {
            console.error(`ERROR: ${error.message}`);
            return;
        }
        if ((voskResult.text?.length || 0) > 0) {
            performRecvText(voskResult.text);
        } else if ((voskResult.partial?.length || 0) > 0) {
            performRecvPartial(voskResult.partial);
        }
    };

    pc.oniceconnectionstatechange = function () {
        if (pc.iceConnectionState == 'disconnected') {
            console.log('Disconnected');
            btn_show_start();
        }
    }

    // var constraints = {
    //     audio: true,
    //     video: false,
    // };

    var audioConstraints = {
        audio: {
            sampleRate: 16000, // Optimize sample rate for speech
            channelCount: 1,   // Mono audio is sufficient for voice
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            latency: 1
        },
        video: false
    };

    navigator.mediaDevices.getUserMedia(audioConstraints).then(function (stream) {
        stream.getTracks().forEach(function (track) {
            pc.addTrack(track, stream);
        });
        return negotiate();
    }, function (err) {
        console.log('Could not acquire media: ' + err);
        btn_show_start();
    });
}

function stop() {
    // close data channel
    if (dc) {
        dc.close();
    }

    // close transceivers
    if (pc.getTransceivers) {
        pc.getTransceivers().forEach(function (transceiver) {
            if (transceiver.stop) {
                transceiver.stop();
            }
        });
    }

    // close local audio / video
    pc.getSenders().forEach(function (sender) {
        sender.track.stop();
    });

    // close peer connection
    setTimeout(function () {
        pc.close();
    }, 500);
}

start_btn.addEventListener('click', start);
stop_btn.addEventListener('click', stop);