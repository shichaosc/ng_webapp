var EMAIL_REG = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
var NEGATIVE_INTEGER_EXPRESS = /^-[1-9]\d*$/;
var POSITIVE_INTEGER_EXPRESS = /^\+?[1-9]\d*$/;
var DECIMAL_EXPRESS = /^[-+]?\d+\.\d*$|^[-+]?\d*\.\d+$/;
var MOBILE_EXPRESS = /^((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|(147)|(166)|(19[8,9]))\d{8}$/;
var TELE_EXPRESS = /^0\d{2,3}[- ]?\d{7,8}/;
var COUNTYR_PREFIX = /^\+?\d*$/; // 电话号前缀

function getUrlParam(paramName) {
    var reg = new RegExp("(^|&)" + paramName + "=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) {
        return unescape(r[2]);
    }
    return "";
}

function isNotCountryPrefix(number) {
    return !COUNTYR_PREFIX.test(number);
}

function getNativeUrlParam(paramName) {
    var reg = new RegExp("(^|&)" + paramName + "=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) {
        return r[2];
    }
    return "";
}

function isNotNumber(number) {
    return number === undefined || !(NEGATIVE_INTEGER_EXPRESS.test(number) || POSITIVE_INTEGER_EXPRESS.test(number) || DECIMAL_EXPRESS.test(number));
}

function isNotPhoneNumber(number) {
    return number === undefined || !(MOBILE_EXPRESS.test(number) || TELE_EXPRESS.test(number));
}

function isNotEmail(email) {
    return !EMAIL_REG.test(email);
}

function isNullStr(str) {
    return str === null || str === undefined || str.trim() === "";
}


function delCookie(name) {
    var exp = new Date();
    exp.setTime(exp.getTime() - 1);
    var cval = getCookie(name);
    document.cookie = name + "=" + cval + "; expires=" + exp.toGMTString();
}

function getCookie(offset) {
    var endstr = document.cookie.indexOf(";", offset);
    if (endstr === -1) {
        endstr = document.cookie.length;
    }
    return decodeURIComponent(document.cookie.substring(offset, endstr));
}

function  setCookie(name, value, duration) {
    var exp = new Date();
    exp.setTime(exp.getTime() + duration);
    document.cookie = name + "=" + escape(value) + ";expires=" + exp.toGMTString();
}


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