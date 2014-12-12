<?php

# Usage: php getChanelId.php QUEUEFILE OUTPUTFILE LASTID
$queue = file($argv[1]);
$output = $argv[2];
if ($argc == 4) {
    $lastid = $argv[3];
    for ($i = 0; $i < count($queue); $i++) {
        $id = trim($queue[$i]);
        if (strcmp($id, $lastid) == 0) {
            break;
        }
    }
    $i++;
}
else {
    $i = 0;
}

$file = fopen($output, 'a');

for (; $i < count($queue); $i++) {
    $id = trim($queue[$i]);
    $user_file = file_get_contents('../gplus/users/'.$id);
    if (strpos($user_file, 'youtube') === false) {
        continue;
    }

    $pos = strpos($user_file, 'youtube.com/channel/');
    if ($pos !== false) {
        $eol = strpos($user_file, "\n", $pos);
        $pos = $pos + 20;
        $q = substr($user_file, $pos, $eol-$pos);
        if (strpos($q, "\t") !== false) {
            $pos = strpos($q, 'youtube.com/channel/');
            $pos = $pos + 20;
            $q = substr($q, $pos);
        }
        if (strpos($q, "?") !== false) {
            $pos = strpos($q, '?');
            $q = substr($q, 0, $pos);
        }
        if (strpos($q, "/") !== false) {
            $pos = strpos($q, '/');
            $q = substr($q, 0, $pos);
        }
        if (empty($q)) {
            continue;
        }
        fwrite($file, $id."\t".$q."\n");
        continue;
    }

    $pos = strpos($user_file, 'youtube.com/user/');
    if ($pos !== false) {
        $eol = strpos($user_file, "\n", $pos);
        $pos = $pos + 17;
        $q = substr($user_file, $pos, $eol-$pos);
        if (strpos($q, "\t") !== false) {
            $pos = strpos($q, 'youtube.com/user/');
            $pos = $pos + 17;
            $q = substr($q, $pos);
        }
        if (strpos($q, "?") !== false) {
            $pos = strpos($q, '?');
            $q = substr($q, 0, $pos);
        }
        if (strpos($q, "/") !== false) {
            $pos = strpos($q, '/');
            $q = substr($q, 0, $pos);
        }
        if (empty($q)) {
            continue;
        }

        $url = 'http://www.youtube.com/user/'.$q;
        $result = "";
        while (empty($result)) {
            $ch = curl_init();
            curl_setopt ($ch, CURLOPT_URL, $url);
            curl_setopt ($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt ($ch, CURLOPT_CONNECTTIMEOUT,10);
            $result = curl_exec($ch);
        }
        $pos = strpos($result, 'channelId');
        if ($pos !== false) {
            $pos = $pos + 20;
            $eol = strpos($result, '"', $pos);
            fwrite($file, $id."\t".substr($result, $pos, $eol-$pos)."\n");
        }
        else {
            echo "ERROR: $id\t$q\tchannelId not found on user page!\n";
        }
        continue;
    }

    $pos = strpos($user_file, 'youtube.com/');
    if ($pos === false) {
        continue;
    }
    $eol = strpos($user_file, "\n", $pos);
    while (strpos(substr($user_file, $pos, $eol-$pos), 'watch?v=') !== false) {
        $pos = strpos($user_file, 'youtube.com/', $pos+1);
        if ($pos === false) {
            break;
        }
        $eol = strpos($user_file, "\n", $pos);
    }
    if ($pos !== false) {
        $pos = $pos + 12;
        $q = substr($user_file, $pos, $eol-$pos);
        if (strpos($q, "\t") !== false) {
            $pos = strpos($q, 'youtube.com/');
            $pos = $pos + 12;
            $q = substr($q, $pos);
        }
        if (strpos($q, "?") !== false) {
            $pos = strpos($q, '?');
            $q = substr($q, 0, $pos);
        }
        if (strpos($q, "/") !== false) {
            $pos = strpos($q, '/');
            $q = substr($q, 0, $pos);
        }
        if (empty($q)) {
            continue;
        }

        $url = 'http://www.youtube.com/user/'.$q;
        $result = "";
        while (empty($result)) {
            $ch = curl_init();
            curl_setopt ($ch, CURLOPT_URL, $url);
            curl_setopt ($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt ($ch, CURLOPT_CONNECTTIMEOUT,10);
            $result = curl_exec($ch);
        }
        $pos = strpos($result, 'channelId');
        if ($pos !== false) {
            $pos = $pos + 20;
            $eol = strpos($result, '"', $pos);
            fwrite($file, $id."\t".substr($result, $pos, $eol-$pos)."\n");
        }
        else {
            echo "ERROR: $id\t$q\tchannelId not found on user page!\n";
        }
    }
}

fclose($file);

?>
