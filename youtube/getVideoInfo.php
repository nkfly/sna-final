<?php

# Usage: php getPlaList.php QUEUEFILE API_KEY START_FROM END_AT
$queue = file($argv[1]);
$key = $argv[2];
$start_from = (int)$argv[3];
$end_at = (int)$argv[4];

set_include_path(get_include_path().PATH_SEPARATOR.'/opt/google-api-php-client/src');
require_once realpath('/opt/google-api-php-client/autoload.php');

$client = new Google_Client();
$client->setDeveloperKey($key);
$service = new Google_Service_YouTube($client);

for ($i = $start_from; $i <= $end_at && $i <= count($queue); $i++) {
    $video_id = trim($queue[$i-1]);
    echo "\r$i\t$video_id";

    $skip = false;
    while (true) {
        try {
            $results = $service->videos->listVideos("snippet,statistics", array("id"=>$video_id));
            break;
        } catch(Exception $e) {
            $msg = $e->getMessage();
            print "\n".$e->getMessage()."\n";
            if (strpos($msg, 'Daily') !== false || strpos($msg, 'Access') !== false) {
                return;
            }
            if (strpos($msg, 'Not Found') !== false) {
                $skip = true;
                break;
            }
            continue;
        }
    }
    if ($skip === true) {
        continue;
    }

    $items = $results->getItems();
    if (empty($items)) {
        continue;
    }

    $snippet = $items[0]->getSnippet();
    $statistics = $items[0]->getStatistics();

    $file = fopen('video_info/'.$video_id, 'w');
    fwrite($file, "<title>\t".$snippet->getTitle()."\n");
    fwrite($file, "<publishedAt>\t".$snippet->getPublishedAt()."\n");
    fwrite($file, "<channelId>\t".$snippet->getChannelId()."\n");
    fwrite($file, "<categoryId>\t".$snippet->getCategoryId()."\n");
    fwrite($file, "<viewCount>\t".$statistics->getViewCount()."\n");
    fwrite($file, "<likeCount>\t".$statistics->getLikeCount()."\n");
    fwrite($file, "<dislikeCount>\t".$statistics->getDislikeCount()."\n");
    fwrite($file, "<commentCount>\t".$statistics->getCommentCount()."\n");
    fwrite($file, "<description>\t".str_replace("\r", ' ', str_replace(PHP_EOL, ' ', $snippet->getDescription()))."\n");
    fclose($file);
}

?>
