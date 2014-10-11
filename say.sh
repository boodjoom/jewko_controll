echo  "$1" | recode UTF8..KOI8-R | ru_tts.static -s /usr/local/share/ru_tts/lexicon -l ~/robotics/TTS/new_words.txt -r 1.0 -p 0.001 | aplay -t raw -r 10000 -f S16_LE > /dev/null 2>&1
#echo  "$1" | recode UTF8..KOI8-R > /tmp/ru_tts.log 
#| recode UTF8..KOI8-R | ru_tts.static -s /usr/local/share/ru_tts/lexicon -l ~/robotics/TTS/new_words.txt -r 0.1 | play -t raw -s -b 8 -r 10000 -c 1 -v 1.0 - > /dev/null 2>&1
