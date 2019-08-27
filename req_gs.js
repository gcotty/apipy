//--------------------------------------------------------------------------
// API Post request with WSSE header
//--------------------------------------------------------------------------
// These functions are written to be executed via Google Apps Script and as
// such contain classes specific to that implementation
//--------------------------------------------------------------------------

function getReport(my_url, myReportJSON) {
   var reportDesc = myReportJSON;
   var response_json = sendHttpPost(my_url, JSON.stringify(reportDesc));  
   
  // Get report ID
  var i = 0;
  var get_report_response = "report_not_ready";
  reportDesc = {"reportID" : response_json.reportID };

  while(get_report_response == "report_not_ready" && i<50) {
    response = sendHttpPost(reportDesc, "Report.Get");
    get_report_response = response.error;

    Utilities.sleep(10000);
    i = i+1;
  }
  
  return response;

}

function sendHttpPost(post_url, report_json) {

   var url = post_url;
   var headers = generateWSSEHeader();
    
   var options =
   {
     "method" : "post",
     "payload" : report_json,
     "headers" : headers,
     "muteHttpExceptions" : true
   };

   var report_response = UrlFetchApp.fetch(post_url, options);   
   Logger.log(report_response.getContentText());

   var response_json = JSON.parse(report_response);

   return response_json;

}

// Header follows a vendor provided format
function generateWSSEHeader(user, secret) {
  var userId = user;
  var userSecret = secret;
  
  var nonce = Utilities.getUuid();
  var b64_nonce = Utilities.base64Encode(nonce);
  var created = Utilities.formatDate(new Date(), "GMT", "yyyy-MM-dd'T'HH:mm:ss'Z'");
  
  var digest_input = nonce + created + userSecret
  var digest_output = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_1, digest_input, Utilities.Charset.US_ASCII);
  var b64_digest = Utilities.base64Encode(digest_output);
  
  var header_str = "UsernameToken Username=\"" + userId + "\", PasswordDigest=\"" 
                                               + b64_digest + "\", Nonce=\"" 
                                               + b64_nonce + "\", Created=\"" 
                                               + created + "\"";
  
  var final_header =
  {
    "X-WSSE" : header_str
  };
  
  return final_header;
  
}

// Parsing JSON data into Google Sheet cells...
// Need to fix for example provided
function parseJSON(sheetName, data, startRow, startCol) {
  var cell;
  var dataIndex;
  var countsIndex;
    
  var data_sheet = SpreadsheetApp.getActive().getSheetByName(sheetName);
  Logger.log(JSON.stringify(data));
  
  for(dataIndex = 0; dataIndex < 24; dataIndex++) {
    for(countsIndex = 0; countsIndex < 4; countsIndex++) {
      cell = data_sheet.getRange(startRow+dataIndex, startCol+countsIndex);
      cell.setValue(data.report.data[dataIndex].counts[countsIndex]);
    }
  }
}
