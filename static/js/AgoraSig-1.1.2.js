Signal_=function(e){function n(e){var n,t,i;for(i=e.length;i;i--)n=Math.floor(Math.random()*i),t=e[i-1],e[i-1]=e[n],e[n]=t}function t(e,n,t){var i=new XMLHttpRequest,o=!1,s=setTimeout(function(){o=!0,i.abort(),t("timeout","")},n);i.open("GET",e),i.onreadystatechange=function(){4===i.readyState&&(o||(clearTimeout(s),200===i.status&&t("",i.responseText)))},i.send(null)}function i(e,n,t){var i=e.split(n,t),o=0;for(var s in i)o+=n.length+i[s].length;return i.push(e.substr(o)),i}this.lbs_url1=["https://lbs-1-sig.agora.io","https://lbs-2-sig.agora.io"],this.lbs_url2=["https://lbs-3-sig.agora.io","https://lbs-4-sig.agora.io"],this.vid=e,this.appid=e;var o=this,s=function(s,a){this.onLoginSuccess="",this.onLoginFailed="",this.onLogout="",this.onInviteReceived="",this.onMessageInstantReceive="",this.state="session_state_logining",this.line="",this.uid=0,this.dbg=!1;var r=this;r.lbs_state="requesting";var l=[];n(l),r.idx=0,r.socket=null;var c=function(){if(r.dbg){var e=[];for(var n in arguments)e.push(arguments[n]);console.log.apply(null,["Agora sig dbg :"].concat(e))}},u=function(e){var n=e[0].replace(/\./g,"-")+"-sig-web.agora.io",t=e[1]+1;return"wss://"+n+":"+t+"/"};r.logout=function(){"session_state_logined"==r.state&&r.onLogout?r.call2("user_logout",{line:r.line},function(e,n){r.fire_logout(e),r.socket.close()}):"session_state_logining"==r.state&&r.fire_logout(0)},r.fire_logout=function(e){e||(e=0);try{"session_state_logined"==r.state&&r.onLogout&&r.onLogout(e)}catch(n){console.error(n)}finally{r.state="session_state_logout"}};var h=function(n,i,o){if("requesting"==r.lbs_state){var s=i[o];t(s+"/getaddr?vid="+e,5e3,function(e,t){if(e)n-1>0?h(n-1,i,(o+1)%i.length):r.fire_login_failed("lbs timeout");else{if("requesting"!=r.lbs_state)return;r.lbs_state="completed",l=JSON.parse(t).web,f(),f()}})}},f=function(){if("session_state_logining"==r.state)var n=new function(){var e=u(l[r.idx]);r.idx+=1;var t=new WebSocket(e);t.state="CONNECTING",setTimeout(function(){return t.readyState==t.CONNECTING?void t.close():void 0},6e3),t.onopen=function(e){if("session_state_logout"==r.state)t.close();else if("session_state_logining"==r.state){r.socket=n,t.state="OPEN",r.state="session_state_logined",c("on conn open"),r.go_login();for(var i in s)t.send(JSON.stringify(s[i]))}else"session_state_logined"==r.state&&t.close()},t.onclose=function(e){"OPEN"==t.state&&(o("_close",""),c("on conn close")),"CONNECTING"==t.state&&f()},t.onmessage=function(e){var n=e.data,t=JSON.parse(n);t[0];o(t[0],t[1])},t.onerror=function(e){return t.state="CLOSED",r.idx<l.length&&e.target.readyState==e.target.CLOSED?void f():(c("on conn error"),void("session_state_logined"==r.state?r.fire_logout("conn error"):"session_state_logining"==r.state&&r.fire_login_failed("conn err")))};var i={},o=function(e,n){e in i&&i[e](n)},s=[];this.on=function(e,n){i[e]=n},this.emit=function(e,n){return 0==t.readyState?void s.push([e,n]):void t.send(JSON.stringify([e,n]))},this.close=function(){t.close()}};var t=0,o=function(){setTimeout(function(){"session_state_logined"==r.state&&(t++,c("send ping",t),r.socket.emit("ping",t),o())},1e4)};r.go_login=function(){""==r.line?(r.socket.emit("login",{vid:e,account:s,uid:0,token:a,device:"websdk",ip:""}),r.socket.on("login_ret",function(e){var n=e[0],t=JSON.parse(e[1]);if(c("login ret",n,t),n||"ok"!=t.result)try{r.onLoginFailed&&r.onLoginFailed(0)}catch(i){console.error(i)}else{r.uid=t.uid,r.line=t.line,r.state="session_state_logined",o(),S();try{r.onLoginSuccess&&r.onLoginSuccess(r.uid)}catch(i){console.error(i)}finally{C()}}})):r.socket.emit("line_login",{line:r.line});var n=0,t={},l={};r.call2=function(e,i,o){n++,t[n]=[e,i,o],c("call ",[e,n,i]),r.socket.emit("call2",[e,n,i])},r.socket.on("call2-ret",function(e){var n=e[0],i=e[1],o=e[2];if(n in t){var s=t[n][2];s&&s(i,o)}});var u,h=function(e,n){return""==e},f=function(e){if(e.startsWith("msg-v2 ")){var n=i(e," ",6);if(7==n.length){var t=n[1],o=n[4],s=n[6];return[t,o,s]}}return null};r.socket.on("pong",function(e){c("recv pong")}),r.socket.on("close",function(e){r.fire_logout(0),r.socket.close()}),r.socket.on("_close",function(e){r.fire_logout(0)}),r.fire_login_failed=function(e){try{"session_state_logining"==r.state&&r.onLoginFailed&&r.onLoginFailed(0)}catch(n){console.error(n)}finally{r.state="session_state_logout"}};var v=function(e){var n=e,t=n[0],i=n[1],o=n[2];if("instant"==i)try{r.onMessageInstantReceive&&r.onMessageInstantReceive(t,0,o)}catch(s){console.error(s)}if(i.startsWith("voip_")){var a,c=JSON.parse(o),u=c.channel,h=c.peer,f=c.extra,v=c.peeruid;if("voip_invite"==i)a=new b(u,h,v,f),r.call2("voip_invite_ack",{line:r.line,channelName:u,peer:h,extra:""});else if(a=l[u+h],!a)return;if("voip_invite"==i)try{r.onInviteReceived&&r.onInviteReceived(a)}catch(s){console.error(s)}if("voip_invite_ack"==i)try{a.onInviteReceivedByPeer&&a.onInviteReceivedByPeer(f)}catch(s){console.error(s)}if("voip_invite_accept"==i)try{a.onInviteAcceptedByPeer&&a.onInviteAcceptedByPeer(f)}catch(s){console.error(s)}if("voip_invite_refuse"==i)try{a.onInviteRefusedByPeer&&a.onInviteRefusedByPeer(f)}catch(s){console.error(s)}if("voip_invite_failed"==i)try{a.onInviteFailed&&a.onInviteFailed(f)}catch(s){console.error(s)}if("voip_invite_bye"==i)try{a.onInviteEndByPeer&&a.onInviteEndByPeer(f)}catch(s){console.error(s)}if("voip_invite_msg"==i)try{a.onInviteMsg&&a.onInviteMsg(f)}catch(s){console.error(s)}}},g=function(){return Date.now()},d=0,_=0,p=0,m=0,y=0,I=!1,C=function(){I||(I=!0,r.call2("user_getmsg",{line:r.line,ver_clear:d,max:30},function(e,n){if(""==e){var t=JSON.parse(n);d=t.ver_clear,p=d;for(var i in t.msgs){var o=t.msgs[i][0],s=t.msgs[i][1];v(f(s)),d=o}(30==t.msgs.length||_>d)&&C(),m=g()}I=!1,y=g()}))},N=function(){y=g()},S=function(){setTimeout(function(){if("session_state_logout"!=r.state){if("session_state_logined"==r.state){var e=g();d>p&&e-y>1e3?C():e-y>=6e4&&C()}S()}},100)};r.socket.on("notify",function(e){c("recv notify ",e),"string"==typeof e&&(e=i(e," ",2),e=e.slice(1));var n=e[0];if("channel2"==n){var t=e[1],o=e[2];if(0!=u.m_channel_msgid&&u.m_channel_msgid+1>o)return void c("ignore channel msg",t,o,u.m_channel_msgid);u.m_channel_msgid=o;var s=f(e[3]);if(s){var a=(s[0],s[1]),r=s[2],l=JSON.parse(r);if("channel_msg"==a)try{u.onMessageChannelReceive&&u.onMessageChannelReceive(l.account,l.uid,l.msg)}catch(n){console.error(n)}if("channel_user_join"==a)try{u.onChannelUserJoined&&u.onChannelUserJoined(l.account,l.uid)}catch(n){console.error(n)}if("channel_user_leave"==a)try{u.onChannelUserLeaved&&u.onChannelUserLeaved(l.account,l.uid)}catch(n){console.error(n)}if("channel_attr_update"==a)try{u.onChannelAttrUpdated&&u.onChannelAttrUpdated(l.name,l.value,l.type)}catch(n){console.error(n)}}}if("msg"==n&&(_=e[1],C()),"recvmsg"==n){var h=JSON.parse(e[1]),g=h[0],p=h[1];g==d+1?(v(f(p)),d=g,N()):(_=g,C())}}),r.messageInstantSend=function(e,n,t){r.call2("user_sendmsg",{line:r.line,peer:e,flag:"v1:E:3600",t:"instant",content:n},function(e,n){t&&t(!h(e,n))})};var b=function(e,n,t){this.onInviteReceivedByPeer="",this.onInviteAcceptedByPeer="",this.onInviteRefusedByPeer="",this.onInviteFailed="",this.onInviteEndByPeer="",this.onInviteEndByMyself="",this.onInviteMsg="";var i=this;this.channelName=e,this.peer=n,this.extra=t,l[e+n]=i,this.channelInviteUser2=function(){t=t||"",r.call2("voip_invite",{line:r.line,channelName:e,peer:n,extra:t},function(e,n){if(h(e,n));else try{i.onInviteFailed(e)}catch(t){console.error(t)}})},this.channelInviteAccept=function(t){t=t||"",r.call2("voip_invite_accept",{line:r.line,channelName:e,peer:n,extra:t})},this.channelInviteRefuse=function(t){t=t||"",r.call2("voip_invite_refuse",{line:r.line,channelName:e,peer:n,extra:t})},this.channelInviteDTMF=function(t){r.call2("voip_invite_msg",{line:r.line,channelName:e,peer:n,extra:JSON.stringify({msgtype:"dtmf",msgdata:t})})},this.channelInviteEnd=function(t){t=t||"",r.call2("voip_invite_bye",{line:r.line,channelName:e,peer:n,extra:t});try{i.onInviteEndByMyself&&i.onInviteEndByMyself("")}catch(o){console.error(o)}}};r.channelInviteUser2=function(e,n,t){var i=new b(e,n,t);return i.channelInviteUser2(),i},r.channelJoin=function(e){return"session_state_logined"!=r.state?void c("You should log in first."):(u=new function(){this.onChannelJoined="",this.onChannelJoinFailed="",this.onChannelLeaved="",this.onChannelUserList="",this.onChannelUserJoined="",this.onChannelUserLeaved="",this.onChannelUserList="",this.onChannelAttrUpdated="",this.onMessageChannelReceive="",this.name=e,this.state="joining",this.m_channel_msgid=0,this.messageChannelSend=function(n,t){r.call2("channel_sendmsg",{line:r.line,name:e,msg:n},function(e,n){t&&t()})},this.channelLeave=function(n){r.call2("channel_leave",{line:r.line,name:e},function(e,t){if(u.state="leaved",n)n();else try{u.onChannelLeaved&&u.onChannelLeaved(0)}catch(i){console.error(i)}})},this.channelSetAttr=function(n,t,i){r.call2("channel_set_attr",{line:r.line,channel:e,name:n,value:t},function(e,n){i&&i()})},this.channelDelAttr=function(n,t){r.call2("channel_del_attr",{line:r.line,channel:e,name:n},function(e,n){t&&t()})},this.channelClearAttr=function(n){r.call2("channel_clear_attr",{line:r.line,channel:e},function(e,t){n&&n()})}},r.call2("channel_join",{line:r.line,name:e},function(e,n){if(""==e){u.state="joined";try{u.onChannelJoined&&u.onChannelJoined()}catch(t){console.error(t)}var i=JSON.parse(n);try{u.onChannelUserList&&u.onChannelUserList(i.list)}catch(t){console.error(t)}try{if(u.onChannelAttrUpdated)for(var o in i.attrs)u.onChannelAttrUpdated("update",o,i.attrs[o])}catch(t){console.error(t)}}else try{u.onChannelJoinFailed&&u.onChannelJoinFailed(e)}catch(t){console.error(t)}}),u)}}};n(o.lbs_url1),n(o.lbs_url2),h(2,o.lbs_url1,0),h(2,o.lbs_url2,0)};this.login=function(e,n){return new s(e,n)}},Signal=function(e){return new Signal_(e)};
