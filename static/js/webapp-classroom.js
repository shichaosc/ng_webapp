/*
 * classroom related function
 * Version 1.0.0
 * Description: the basic functions for whiteboard, class control, etc
 * Copyright: Copyright (c) 2017-2018 PPLINGO.
 */

(function($) {
	$.videoControl = function(options) {
		var opts = $.extend(true, {
			provider: 'AGORA.IO',
			signallingProvider: 'AGORA.IO',
			//determine the mode is watch only
			watchOnly: false,
			//DOM object to contain local video
			localPlayer: 'video_local',
			//DOM object to contain remote video
			remotePlayer: 'video_remote',
			openboxSettings: {
				apiKey: undefined,
				sessionId: undefined, 
				token: undefined
			},
			agoraSettings: {
				dynamicKey: undefined,
				channelId: undefined,
				appId: undefined,
				signallingKey: undefined
			},
		}, options);
		
		var client, session, signalSession, signalChannel;
        var message_queue = [];
        var statusMessageQueue = [];
        
		console.log("Init");
		
		connectVideo();
		
		connectSignal();

		function connectVideo() {
			
			if(client) {
				client.leave(function () {
					console.log("Leavel channel successfully");
			  	}, function (err) {
			    	console.log("Leave channel failed");
			    });
			}
			  	
			console.log("Init AgoraRTC client with vendor key: " + opts.agoraSettings.dynamicKey);
			client = AgoraRTC.createClient({mode: 'interop'});
			  
			// for dynamic key
			client.init(opts.agoraSettings.dynamicKey, function () {
			    console.log("AgoraRTC client initialized");
			    client.join(opts.agoraSettings.dynamicKey, opts.agoraSettings.channelId, opts.userid, function(uid) {
			        console.log("User " + uid + " join channel successfully");
			        //camera = videoSource.value;
			        //microphone = audioSource.value;
			        $(".video_remote").remove();

			        if(! opts.watchOnly) {
			            localStream = AgoraRTC.createStream({streamID: opts.userid, audio: true, video: true, screen: false});
			            localStream.setVideoProfile('360P_7');
			            localStream.init(function() {
			                console.log("getUserMedia successfully");
			                $("#" + opts.localPlayer).empty();
			                localStream.play(opts.localPlayer);

			                client.publish(localStream, function (err) {
			                    console.log("Publish local stream error: " + err);
			                });

			                client.on('stream-published', function (evt) {
			                    console.log("Publish local stream successfully");

			                    //send_signal("classControl", "open");

			                });
			         
			            }, function (err) {
			                console.log("getUserMedia failed", err);
			            });
					}
			    }, function(err) {
			        console.log("Join channel failed", err);
			    });
			}, function (err) {
			    console.log("AgoraRTC client init failed", err);
			});

			client.on('stream-added', function (evt) {
			    var stream = evt.stream;
			    console.log("New stream added: " + stream.getId());
			    console.log("Subscribe ", stream);
			    client.subscribe(stream, function (err) {
			        console.log("Subscribe stream failed", err);
			    });
			});

			client.on('stream-subscribed', function (evt) {
			    var stream = evt.stream;
			    console.log("Subscribe remote stream successfully: " + stream.getId());

			    if ($('div#video #video_'+stream.getId()).length === 0) {
			        $("div#video").append('<div id="video_'+stream.getId()+'" class="video video_remote" style="width:23vw;height:17.25vw;"></div>')
			    }
			    else {
			        $('div#video #video_'+stream.getId()).empty();
			    }
			    stream.play('video_' + stream.getId());
			    console.log('video is played in video_' + stream.getId());

			});

			client.on('stream-removed', function (evt) {
			    var stream = evt.stream;
			    stream.stop();
			    $('#video_' + stream.getId()).remove();
			    console.log("Remote stream is removed " + stream.getId());
			});

			client.on('peer-leave', function (evt) {
			    var stream = evt.stream;
			    stream.stop();
			    $('#video_' + stream.getId()).remove();
			    console.log(evt.uid + " leaved from this channel");
			    
			    //double check whether peer really left
			    //sendVideoStatusQuery(stream.getId());
			
	        });
		}
		
		function connectSignal() {
			
			if(opts.signallingProvider == "OPENTOK") {
                //opentok
            	    if (OT.checkSystemRequirements() == 1) {
                    session = OT.initSession(opts.opentokSettings.apiKey, opts.opentokSettings.sessionId);

                    //initiate chat
                    //var chatWidget = new OTSolution.TextChat.ChatWidget({
                    //    session: session,
                    //    container: '#chat'
                    //});

                    //toggleChatBox();
                    //connect the webRTC session
                    connect();
                } else {
                    // The client does not support WebRTC.
                    //alert("{% trans 'the client does not support webrtc' %}");
                }
            }
			else {
				//agora.io
                var signal = Signal(opts.agoraSettings.appId);
                signalSession = signal.login(opts.username, opts.agoraSettings.signallingKey, opts.userid);

                signalSession.dbg = false;
                signalSession.onLoginSuccess = function (uid) {
                    console.log('signalling login success ' + uid);
                    //g_uid = uid;
                    joinSignalChannel();
                };

                signalSession.onLoginFailed = function (ecode) {
                    console.log('signalling login failed ' + ecode);
                    connectSignal();
                };

                signalSession.onLogout = function (ecode) {
                    console.log('signalling logouted ' + ecode);
                    //do_leave();
                };

                signalSession.onMessageInstantReceive = function (account, uid, msg) {
                    console.log('recv inst msg from ' + account + ' : ' + msg);
                };
			}
        }
        

        function joinSignalChannel() {

            signalChannel = signalSession.channelJoin(opts.agoraSettings.channelId);

            signalChannel.onChannelJoined = function () {
                	console.log('channel.onChannelJoined'); 
                	console.log(signalChannel);
                	sendSignalStatusQuery();
                	opts.agoraSettings.postProcessing(signalSession, signalChannel);
                	
            }
            	

            signalChannel.onChannelJoinFailed = function (ecode) {
                console.log('channel.onChannelJoinFailed', ecode);
                //reconnect_signal();
            };

            signalChannel.onChannelLeaved = function (code) {
                console.log('channel.onChannelLeaved');
                alert('Unstable connection, click "ok" to reconnect.');
                joinSignalChannel();
                //console.log('重新加入频道！');
            };

            signalChannel.onChannelUserJoined = function (account, uid) {
                console.log('channel.onChannelUserJoined ' + account + ' ' + uid);
            };
            signalChannel.onChannelUserLeaved = function (account, uid) {
                console.log('channel.onChannelUserLeaved ' + account + ' ' + uid);
            };

            signalChannel.onMessageChannelReceive = function (account, uid, msg) {
                //console.log('channel.onMessageChannelReceive ' + account + ' ' + uid + ' : ' + msg);
                var message = JSON.parse(msg);
            	    if (account == opts.username && message.type == "status" && message.data.target == "signal") {
            	    	    receiveSignalStatusQuery(message.data);
            	    }
            	    else if (message.type == "status") {
            	    	    //do nothing for status query message from others
            	    }
            	    else {
            	        opts.agoraSettings.messageHandling(account, uid, msg);
            	    }
            }

        }

        function sendSignal(type, message) {

            if (opts.signallingProvider == "OPENTOK") {
                //alert("enter signalling to send " + index);
                if (session == null || session.connection == null)
                    return;

                session.signal(
                    {
                        data: message,
                        type: type
                    },
                    function (error) {
                        if (error) {
                            alert("signal error ("
                                + error.code
                                + "): " + error.message);
                        } else {
                            //alert("signal sent.");
                        }
                    }
                );
            }
            else {
                var msg = {"type": type, "data": message};
                var json_string = JSON.stringify(msg);
                message_queue.push(json_string);
                //console.log("message is queued: " + json_string);
                
                sendQueuedMessage();
            }
        };
        
        function sendQueuedMessage() {
        	    if(message_queue.length > 0) {
        	    	    try {
                    signalChannel.messageChannelSend(message_queue[0]);
                    //console.log("queued message is sent: " + message_queue[0]);
                    message_queue.shift();
                    
                    //if there is any remaining queued message, send it after 1 second
                    if(message_queue.length > 0)
        	                setTimeout(sendQueuedMessage, 100);
        	    	    }
        	    	    catch (e) {
                    console.log("message hasn't been sent, and error is " + e);
                }
        	    	    
        	    }
        	
        }
        
        function sendSignalStatusQuery() {
            if(statusMessageQueue.length > 0) {
            	    statusMessageQueue = [];
            	    alert('Unstable connection, click "ok" to reconnect with server.');
            	    connectSignal();
            	    return;
            }
            
            var date = new Date(); 
            var timestamp = date.getTime();
        	    var message = {'mode': 'request', 'target': 'signal', 'timestamp': timestamp};
            sendSignal("status", message);
            statusMessageQueue.push(message);

            setTimeout(sendSignalStatusQuery, 30000);
        }

        

        function receiveSignalStatusQuery(message) {
            if (message.target == 'signal') {
                //if response is received, it shows itself is still online
               	var i = statusMessageQueue.length;
            	    while(i--)
                {
                    if(statusMessageQueue[i].timestamp <= message.timestamp) {
                        //console.log("status query matches: " + message.timestamp + ';');
                        statusMessageQueue.splice(i,1);	 
                    }
                    else {
                    	    console.log("status query mismatches: " + message.timestamp);
                    }
                }
            }
            
        }
        
        return {
            signalChannel: signalChannel,
            signalSession: signalSession,
            sendSignal: function(type, message) { sendSignal(type, message); },
            connectVideo: function() { connectVideo(); }
    		};
	};
	
/*
  //function of opentox
        function connect() {
            if (session == null)
                return;

            session.connect(token_id, function (error) {
                if (error) {
                    //alert("error");
                    alert(error.code + error.message);
                } 
                else {
                    send_signal("classControl", "open");
                }
            });
			session.on("signal:courseware", function(event) {
				if(role=="student") {
                    var obj = jQuery.parseJSON(event.data);

					retrieveCourseware(obj.session_id, obj.type);
				}
			});
            session.on("signal:pageControl", function (event) {
                if (role == "student") {
                    //alert("Signal sent from connection " + event.from.id + ": " + event.data);
                    $("#myCourseware").carousel(parseInt(event.data, 0));
                }
            });
            session.on("signal:whiteboard_open", function (event) {
                if (role == "student") {
                    
                    
                    var node = $('#wbHost');

                    if(node.is(':hidden')){
                        // 初始化白板信息
                        InitThis();
                        node.show();
                    }
                    
                }
            });
            
            session.on("signal:whiteboard_close", function (event) {
                if (role == "student") {
                    
                    var node=$('#wbHost');
                    if(node.is(':visible')){
                        node.hide();
                    }
                }
            });
            session.on("signal:classControl", function (event) {
                if (role == "student" && event.data == "close") {
                    $('#evaluationModal').modal('show');
                }
            });
            session.on("signal:pointer", function (event) {
                //alert("Signal sent from connection " + event.from.id + ": " + event.data);
                if (event.data == "hide")
                    $("#pointer").addClass("hidden");
                else {
                	try {
                    	var obj = jQuery.parseJSON(event.data);
                		show_pointer(obj.posX, obj.posY, obj.width, obj.height);        
                    }
                    catch (e) {
                        console.log("failure - pointer");
                        console.log(e);
                    }
                }
            });

        }
        
        function disconnectOpentokSignalling() {
            session.disconnect();
        }

        function reconnectOpentokSignalling() {
            disconnectOpentokSignalling();

            session.connect(token_id, function (error) {
                if (error) {
                    alert("error");
                    alert(error.code + error.message);
                } else {
                    //alert("Connected to the session.");
                }
            });
            console.log("reconnected");
        }

  
function leave() {
	
	//client.unpublish(localStream, function (err) {
	//    console.logconsole.log("Unpublish local stream failed" + err);
	//  });
    
	client.leave(function () {
		console.log("Leavel channel successfully");
  	}, function (err) {
    	console.log("Leave channel failed");
  });
}  

             function sendSignalStatusQuery() {
                var message = {'mode': 'request', 'target': 'signal'};
                send_signal("status", message);

                //setTimeout(sendSignalStatusQuery, 10000);
            }

            function sendVideoStatusQuery(streamId) {
                var message = {'mode': 'request', 'target': 'video', 'remoteStream': streamId};
                send_signal("status", message);
                //console.log("status request signal is sent:" + message);

            }

            function receiveStatusQuery(message) {
                //console.log("status signal is received: " + message);
                if (message.mode == 'response' && message.target == 'signal') {
                    //if response is received, it shows the other party is still online
                    signal_status = true;
                }
                else if (message.mode == 'request' && message.target == 'video') {
                    var localStreamId = localStream.getId();
                    if (localStreamId == message.remoteStream) {
                        reconnect_video();
                        send_signal("status", {
                            'mode': 'response',
                            'target': 'video',
                            'localStream': localStream.getId()
                        });
                        console.log("status response signal is sent:" + message);

                    }
                }
                else if (message.mode == "request" && message.target == 'signal') {
                    send_signal("status", {'mode': 'response', 'target': 'signal'});
                }
            }


            var do_leave = function () {
                console.log('leave channel!!!');
                signal_channel.channelLeave();

            };

            var do_logout = function () {
                signal_session.logout();
            };

            function reconnect_signal() {
                //do_logout();
                $('#chat').empty();
                console.log('即将重连！');
                login_signal();
                console.log('已进行重连！');
            }

            function reconnect() {
                reconnect_video();
                if (signalling_provider == "OPENTOK")
                {
                    reconnectOpentokSignalling();
                }
                else
                {
                    reconnect_signal();
                }
            } 
 */	
	
	
}(jQuery));