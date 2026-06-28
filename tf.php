<?php

$fileId = $_GET['fileId'] ?? '';
$botApi = $_GET['botApi'] ?? '';

if (!$fileId || !$botApi) {
    exit("Missing Parameters");
}

// Get file info
$get = json_decode(file_get_contents(
    "https://api.telegram.org/bot{$botApi}/getFile?file_id=" . urlencode($fileId)
), true);

if (!$get['ok']) {
    exit("Invalid File ID");
}

$filePath = $get['result']['file_path'];

$telegramUrl = "https://api.telegram.org/file/bot{$botApi}/{$filePath}";

// Extension
$ext = pathinfo($filePath, PATHINFO_EXTENSION);
if (!$ext) $ext = "bin";

// Create folder
$dir = "downloads";
if (!is_dir($dir)) {
    mkdir($dir, 0777, true);
}

// Random file name
$fileName = uniqid("tg_", true) . "." . $ext;
$savePath = $dir . "/" . $fileName;

// Download
$data = file_get_contents($telegramUrl);

if ($data === false) {
    exit("Download Failed");
}

file_put_contents($savePath, $data);

// Return URL
$protocol = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? "https" : "http";
$url = $protocol . "://" . $_SERVER['HTTP_HOST'] .
       dirname($_SERVER['SCRIPT_NAME']) .
       "/downloads/" . $fileName;

header("Content-Type: text/plain");
echo $url;

?>