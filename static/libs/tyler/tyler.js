// JavaScript Document

//=========================READ URL======================


  function findGetParameter(parameterName) {
    var result = "",
        tmp = [];
    location.search
        .substr(1)
        .split("&")
        .forEach(function (item) {
          tmp = item.split("=");
          if (tmp[0] === parameterName) result = decodeURIComponent(tmp[1]);
        });
    return result;
}

var varS1 = findGetParameter("s1");
var varS2 = findGetParameter("s2");
var varS3 = findGetParameter("s3");
var varutm_source = findGetParameter("utm_source");
var varutm_medium = findGetParameter("utm_medium");
var varutm_campaign = findGetParameter("utm_campaign");
var varutm_term = findGetParameter("utm_term");
var varutm_content = findGetParameter("utm_content");
var varrefurl = document.referrer;
var varRegisteredName = findGetParameter("RegisteredName");

document.getElementById('refurl').value=document.referrer;
$("input[id=custom_s1]").val(findGetParameter("s1"));
$("input[id=custom_s2]").val(findGetParameter("s2"));
$("input[id=custom_s3]").val(findGetParameter("s3"));
$("input[id=utm_source]").val(findGetParameter("utm_source"));
$("input[id=utm_medium]").val(findGetParameter("utm_medium"));
$("input[id=utm_campaign]").val(findGetParameter("utm_campaign"));
$("input[id=utm_term]").val(findGetParameter("utm_term"));
$("input[id=utm_content]").val(findGetParameter("utm_content"));



//debug
//document.getElementById("ref").innerHTML='refrerURL['+encodeURIComponent(document.referrer)+']s1['+findGetParameter("s1")+']s2['+findGetParameter("s2")+']s3['+findGetParameter("s3")+']utm_source['+findGetParameter("utm_source")+'] utm_medium['+findGetParameter("utm_medium")+']utm_campaign['+findGetParameter("utm_campaign")+']utm_term['+findGetParameter("utm_term")+']utm_content['+findGetParameter("utm_content");



//=================================COOKIES==================


if (findGetParameter("s1") == "" && findGetParameter("s2") == "" && findGetParameter("s3") == "" &&  findGetParameter("utm_source") == ""  && findGetParameter("utm_medium") == ""  && findGetParameter("utm_campaign") == ""  && findGetParameter("utm_term") == ""  && findGetParameter("utm_content") == "" ){
	//alert('URL attributes NOT detected');
	checkCookie();
	}
	
else {
	//alert('URL attributes detected');

setCookie("cookieS1", varS1, 30)
setCookie("cookieS2", varS2, 30)
setCookie("cookieS3", varS3, 30)
setCookie("cookieutm_source", varutm_source, 30)
setCookie("cookieutm_medium", varutm_medium, 30)
setCookie("cookieutm_campaign", varutm_campaign, 30)
setCookie("cookieutm_term", varutm_term, 30)
setCookie("cookieutm_content", varutm_content, 30)

document.getElementById("ref").innerHTML += "[custom_s1:" + varS1 + "]";
document.getElementById("ref").innerHTML += "[custom_s2:" + varS2 + "]";
document.getElementById("ref").innerHTML += "[custom_s3:" + varS3 + "]";
document.getElementById("ref").innerHTML += "[utm_source:" + varutm_source + "]";
document.getElementById("ref").innerHTML += "[utm_medium:" + varutm_medium + "]";
document.getElementById("ref").innerHTML += "[utm_campaign:" + varutm_campaign + "]";
document.getElementById("ref").innerHTML += "[utm_term:" + varutm_term + "]";
document.getElementById("ref").innerHTML += "[utm_content:" + varutm_content + "]";
}


function checkCookie() {
//alert('checking cookies');
var varS1 = getCookie("cookieS1");
var varS2 = getCookie("cookieS2");
var varS3 = getCookie("cookieS3");
var varutm_source = getCookie("cookieutm_source");
var varutm_medium = getCookie("cookieutm_medium");
var varutm_campaign = getCookie("cookieutm_campaign");
var varutm_term = getCookie("cookieutm_term");
var varutm_content = getCookie("cookieutm_content");
var varrefurl = getCookie("cookierefurl");
	
	
	
document.getElementById('custom_s1').value = varS1;
document.getElementById('custom_s2').value = varS2;
document.getElementById('custom_s3').value = varS3;
document.getElementById('utm_source').value = varutm_source;
document.getElementById('utm_medium').value = varutm_medium;
document.getElementById('utm_campaign').value = varutm_campaign;
document.getElementById('utm_term').value = varutm_term;
document.getElementById('utm_content').value = varutm_content;
document.getElementById('refurl').value = varrefurl;


//document.myform.custom_s1.value = varS1;
//document.myform.custom_s2.value = varS2;
//document.myform.custom_s3.value = varS3;
//document.myform.utm_source.value = varutm_source;
//document.myform.utm_medium.value = varutm_medium;
//document.myform.utm_campaign.value = varutm_campaign;
//document.myform.utm_term.value = varutm_term;
//document.myform.utm_content.value = varutm_content;
//document.myform.refurl.value = varrefurl;


document.getElementById("ref").innerHTML += "[custom_s1:" + varS1 + "]";
document.getElementById("ref").innerHTML += "[custom_s2:" + varS2 + "]";
document.getElementById("ref").innerHTML += "[custom_s3:" + varS3 + "]";
document.getElementById("ref").innerHTML += "[utm_source:" + varutm_source + "]";
document.getElementById("ref").innerHTML += "[utm_medium:" + varutm_medium + "]";
document.getElementById("ref").innerHTML += "[utm_campaign:" + varutm_campaign + "]";
document.getElementById("ref").innerHTML += "[utm_term:" + varutm_term + "]";
document.getElementById("ref").innerHTML += "[utm_content:" + varutm_content + "]";
}


//cookies functions below

function getCookie(cname) {
	//alert('reading cookie from browser');
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i].trim();
        if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
    }
    return "";
}

function setCookie(cname,cvalue,exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires=" + d.toGMTString();
    document.cookie = cname+"="+cvalue+"; "+expires;
    //alert("setting cookie " + cname + " to "+"[ " + cvalue +" ] "+ " for " + exdays + " days")
}

function GetUrlValue(VarSearch){
    var SearchString = window.location.search.substring(1);
    var VariableArray = SearchString.split('&');
    for(var i = 0; i < VariableArray.length; i++){
        var KeyValuePair = VariableArray[i].split('=');
        if(KeyValuePair[0] == VarSearch){
            return KeyValuePair[1];
        }
    }
}




