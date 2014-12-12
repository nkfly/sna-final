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
    $gplus_id = explode("\t", trim($queue[$i-1]))[0];
    $channel_id = explode("\t", trim($queue[$i-1]))[1];
    echo "\r$gplus_id\t$channel_id";

    $skip = false;
    while (true) {
        try {
            $results = $service->channels->listChannels("contentDetails", array("id"=>$channel_id));
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

    $playlists = $items[0]->getContentDetails()->getRelatedPlaylists();
    foreach (array('uploads', 'favorites', 'likes') as $name) {
        if (isset($playlists[$name])) {
            $playlist_id = $playlists[$name];

            $skip = false;
            while (true) {
                try {
                    $results = $service->playlistItems->listPlaylistItems('contentDetails', array("playlistId"=>$playlist_id, "maxResults"=>50));
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
            $videos = $results->getItems();
            if (empty($videos)) {
                continue;
            }

            while (!empty($token = $results->getNextPageToken())) {
                while (true) {
                    try {
                        $results = $service->playlistItems->listPlaylistItems('contentDetails', array("playlistId"=>$playlist_id, "maxResults"=>50, "pageToken"=>$token));
                        break;
                    } catch(Exception $e) {
                        $msg = $e->getMessage();
                        print "\n".$e->getMessage()."\n";
                        if (strpos($msg, 'Daily') !== false || strpos($msg, 'Access') !== false) {
                            return;
                        }
                        continue;
                    }
                }
                $videos = array_merge($videos, $results->getItems());
            }

            $file = fopen('video_id/'.$gplus_id.'.'.$name, 'w');
            foreach ($videos as $video) {
                fwrite($file, $video->getContentDetails()->getVideoId()."\n");
            }
            fclose($file);
        }
    }
}

?>
