/*! PPLINGO webapp scheduler - v1.0.0 - 2017-01-14 */

function getDateOfWeek(d, x) {

    d = new Date(d);

    if (Object.prototype.toString.call(d) === "[object Date]") {
    	// it is a date
        if (isNaN(d.getTime()))
            d = new Date();
        }
        else
            d = new Date();


    var day = d.getDay();
    if(day==0)
    	day=7;
    diff = d.getDate() - day + x; // adjust when day is sunday
    return new Date(d.setDate(diff));
}

function getISODateString(d) {
	
	if(Object.prototype.toString.call(d) != "[object Date]")
		d = new Date(d);
	
	var month = '' + (d.getMonth() + 1);
    var day = '' + d.getDate();
    var year = d.getFullYear();

	if (month.length < 2) month = '0' + month;
	if (day.length < 2) day = '0' + day;

	return [year, month, day].join('-');
}

function getLocaleDateString(d) {
	if(Object.prototype.toString.call(d) != "[object Date]")
		d = new Date(d);
	
	return d.toLocaleDateString();
}

function parseDate(strDate) {
	if(strDate == null)
		return null;
	
	var matches = /(\d{4})[-\/](\d{2})[-\/](\d{2})/.exec(strDate);
    if (matches != null) 
    {
    	var year = matches[1];
    	var month = matches[2] - 1;
    	var day = matches[3];
     	return new Date(year, month, day);
    	
	}
	else
		return new Date(strDate);
	
}

function isDateString(strDate) {

	if (strDate == null || strDate == "")
		return false;
	
	var d = parseDate(strDate);
	
	if ( Object.prototype.toString.call(d) === "[object Date]" ) {
		  // it is a date
		  if ( isNaN( d.getTime() ) ) {  // d.valueOf() could also work
		    // date is not valid
			  return false;
		  }
		  //else {
		    // date is valid
			//  return true;
		  //}
		}
		else {
		  // not a date
			return false;
		}

	return true;
	
}

function isEarlier(strD1, strD2) {
	var d1 = parseDate(strD1);
	var d2 = parseDate(strD2);
	console.log("d1 is:" + d1 + "; d2 is:" + d2);
	if(d1 < d2)
		return true;
	else
		return false;
	
}

function isLater(strD1, strD2) {
	if(isEarlierOrSame(strD1, strD2))
		return false;
	else
		return true;
	
}

function isEarlierOrSame(strD1, strD2) {
	var d1 = parseDate(strD1);
	var d2 = parseDate(strD2);
	
	if(d1 <= d2)
		return true;
	else
		return false;
	
}

function isLaterOrSame(strD1, strD2) {
	if(isEarlier(strD1, strD2)) 
		return false;
	else
		return true;
}

var DateDiff = {

	    inDays: function(d1, d2) {
	        var t2 = d2.getTime();
	        var t1 = d1.getTime();

	        return parseInt((t2-t1)/(24*3600*1000));
	    },

	    inWeeks: function(d1, d2) {
	        var t2 = d2.getTime();
	        var t1 = d1.getTime();

	        return parseInt((t2-t1)/(24*3600*1000*7));
	    },

	    inMonths: function(d1, d2) {
	        var d1Y = d1.getFullYear();
	        var d2Y = d2.getFullYear();
	        var d1M = d1.getMonth();
	        var d2M = d2.getMonth();

	        return (d2M+12*d2Y)-(d1M+12*d1Y);
	    },

	    inYears: function(d1, d2) {
	        return d2.getFullYear()-d1.getFullYear();
	    }
}