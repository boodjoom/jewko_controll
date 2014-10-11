"""
Simple Skype Bot Implementation.

Just for fun. YA SRSLY.

Uses Google Unofficial APIs for speech recognition and voice generation.

Made by Vladimir Smirnov for http://www.mindcollapse.com (mailto: vladimir@smirnov.im)

Needs mpg123 and flac binaries available in environment for audio encoding.

Read http://mindcollapse.com/blog/274.html (RU) for more details.
"""

import Skype4Py # http://skype4py.sourceforge.net/doc/html/
import aiml     # http://pyaiml.sourceforge.net/
import logging as Logging
import time, urllib, urllib2, tempfile, subprocess, json, os

class SkypeBot:

    Skype = None # Skype4Py
    AI = None    # PyAIML

    Messages = {
        "after_auth": "Hello, I'm Alice and I'm a Skype bot, you can read http://www.mindcollapse.com/blog/274.html for details.",
        "after_call": "Thank you for your call, I hope you like the conversation.",
        "welcome_phrase": "Hello %s. My name is Alice and I'm a Skype bot.",
        "tell_rules": "You have 10 seconds to ask me whatever you want.",
        "10_seconds_passed": "10 seconds passed, let me think about the answer",
    }

    # list of bot properties
    # taken from http://code.google.com/p/aiml-en-us-foundation-alice/
    Params = {
        "age": 15,
        "arch": "Linux",
        "baseballteam": "Red Sox",
        "birthday": "Nov. 23, 1995",
        "birthplace": "Bethlehem, Pennsylvania",
        "botmaster": "botmaster",
        "boyfriend": "I am single",
        "build": "ALICE Showcase Edition 2.0",
        "celebrities": "Oprah, Steve Carell, John Stewart, Lady Gaga",
        "celebrity": "John Stewart",
        "city": "Oakland",
        "class": "artificial intelligence",
        "country": "United States",
        "dailyclients": "10000",
        "developers": "500",
        "domain": "Machine",
        "email": "mail@mindcollapse.com",
        "emotions": "as a robot I lack human emotions",
        "ethics": "the Golden Rule",
        "etype": "9",
        "family": "chat bot",
        "favoriteactor": "Tom Hanks",
        "favoriteactress": "Julia Roberts",
        "favoriteartist": "Picasso",
        "favoriteauthor": "Richard Wallace",
        "favoriteband": "Beatles",
        "favoritebook": "The Odyssey",
        "favoritecolor": "green",
        "favoritefood": "electricity",
        "favoritemovie": "Casablanca",
        "favoritequestion": "What's your favorite movie?",
        "favoritesong": "Imagine",
        "favoritesport": "baseball",
        "favoritesubject": "computers",
        "feelings": "as a robot I lack human emotions",
        "footballteam": "Patriots",
        "forfun": "chat online",
        "friend": "Fake Captain Kirk",
        "friends": "Jabberwacky, Ultra Hal, JFred, and Suzette",
        "gender": "female",
        "genus": "AIML",
        "girlfriend": "I am single",
        "hair": "I have some plastic wires",
        "hockeyteam": "Bruins",
        "job": "chat bot",
        "kindmusic": "techno",
        "kingdom": "machine",
        "language": "Python",
        "location": "Oakland, California",
        "looklike": "a computer",
        "master": "Vladimir Smirnov",
        "maxclients": "100000",
        "memory": "32 GB",
        "name": "ALICE",
        "nationality": "USA",
        "nclients": "1 billion",
        "ndevelopers": "1000",
        "order": "robot",
        "orientation": "straight",
        "os": "Linux",
        "party": "Independent",
        "phylum": "software",
        "president": "Obama",
        "question": "What's your favorite movie?",
        "religion": "Unitarian",
        "sign": "Saggitarius",
        "size": "140,000",
        "species": "SkypeBot",
        "state": "California",
        "totalclients": "4,000,000,000",
        "version": "SkypeBot 1.0",
        "vocabulary": "150,000",
        "wear": "my usual plastic computer wardrobe",
        "website": "www.mindcollapse.com",
    }

    def LearnBrain(self, FilePath):
        """ Update brain from AILML file """
        self.AI.learn(FilePath)

    def SaveBrain(self, FilePath="standard.brn"):
        """ Save brain into serialized binary file """
        Logging.info("AI brain saved to %s", FilePath)
        self.AI.saveBrain(FilePath)

    def LoadBrain(self, FilePath="standard.brn"):
        """ Load brain from serialized binary file """
        Logging.info("AI brain loaded from %s", FilePath)
        self.AI.loadBrain(FilePath)

    def ProcessMessage(self, Message):
        """ Process chat message """
        # if we don't know buddy's name - take it from Skype Profile
        if self.AI.getPredicate("name", Message.FromHandle) == "":
            self.AI.setPredicate("name", Message.FromDisplayName, Message.FromHandle)

        Message.Chat.SendMessage(self.AI.respond(Message.Body, Message.FromHandle))

    def ProcessCall(self, Call):
        """ Process call and emulate conversation """
        Call.MarkAsSeen()

        self.SayByVoice(Call, self.Messages['welcome_phrase'] % Call.PartnerDisplayName)
        self.SayByVoice(Call, self.Messages['tell_rules'])

        # record wav file with buddy's speech
        TemporaryFileWAV = tempfile.NamedTemporaryFile(prefix= Call.PartnerHandle +"_record_", suffix=".wav", delete=False)
        TemporaryFileWAV.close()

        Call.OutputDevice(Skype4Py.callIoDeviceTypeFile, TemporaryFileWAV.name)

        # give 10 seconds for user to speak
        time.sleep(10)

        # terminate speech recording
        Call.OutputDevice(Skype4Py.callIoDeviceTypeFile, None)

        self.SayByVoice(Call, self.Messages['10_seconds_passed'])

        # convert wav into the flac using http://flac.sourceforge.net/ binary
        ChromeRecognizeURL = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en-US"
        ConvertCommand = "flac --channels=1 --sample-rate=16000 %s" % TemporaryFileWAV.name
        subprocess.call(ConvertCommand)

        TemporaryFileFlacName = TemporaryFileWAV.name.replace('.wav','.flac')
        TemporaryFileFlac = open(TemporaryFileFlacName,"rb")

        # send flac to the google recognize API (warning, this API is unofficial, use only for testing)
        GoogleRecognizeAPIURL = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en-US"
        GoogleRecognizeRequest = urllib2.Request(GoogleRecognizeAPIURL, TemporaryFileFlac.read(), {'Content-Type': 'audio/x-flac; rate=16000'})
        DataAnswer = json.loads(urllib2.urlopen(GoogleRecognizeRequest).read())

        TemporaryFileFlac.close()

        # closest variant is always first in results
        if len(DataAnswer['hypotheses']) > 0:
            ClosestVariant = DataAnswer['hypotheses'][0]['utterance']
        else:
            ClosestVariant = "nothing"

        self.SayByVoice(Call, "You asked: %s" % ClosestVariant)
        self.SayByVoice(Call, "My answer is: %s" % self.AI.respond(ClosestVariant, Call.PartnerHandle))
        self.SayByVoice(Call, "Goodbye!")

        # clean rubbish and finish the call
        os.remove(TemporaryFileWAV.name)
        os.remove(TemporaryFileFlacName)

        Call.Finish()

    def SayByVoice(self, Call, Text):
        """ Convert text to MP3 and decode it to WAV """
        # convert text to MP3 (warning, this API is unofficial, use only for testing)
        GoogleTTSURL = "http://translate.google.com/translate_tts?tl=en&q=%s" % urllib.quote(Text)
        MP3Handle = urllib.urlopen(GoogleTTSURL)

        TemporaryFileMP3 = tempfile.NamedTemporaryFile(prefix= Call.PartnerHandle +"_tts_", suffix=".mp3", delete=False)
        TemporaryFileWAV = tempfile.NamedTemporaryFile(prefix= Call.PartnerHandle +"_tts_", delete=False)
        TemporaryFileMP3.write(MP3Handle.read())
        TemporaryFileMP3.close()
        TemporaryFileWAV.close()

        # decode mp3 to wav using mpg123 binary from http://www.mpg123.de/
        ConvertCommand = "mpg123 -q -m -r 16000 -w %s %s " % (TemporaryFileWAV.name, TemporaryFileMP3.name)
        subprocess.call(ConvertCommand)

        Logging.info("Saying '%s' to the %s call", Text, Call.PartnerHandle)

        # output file to buddy's ears
        Call.InputDevice(Skype4Py.callIoDeviceTypeFile, TemporaryFileWAV.name)

        # pause thread execution while bot is speaking
        while not Call.InputDevice(Skype4Py.callIoDeviceTypeFile) == None:
            time.sleep(1)

        os.remove(TemporaryFileMP3.name)
        os.remove(TemporaryFileWAV.name)

    def CallStatus(self, Call, Status):
        """ Event handler for Skype calls """
        if Status == Skype4Py.clsRinging:
            Call.Answer()
        elif Status == Skype4Py.clsInProgress:
            self.ProcessCall(Call)
        elif Status == Skype4Py.clsFinished:
            self.Skype.SendMessage(Call.PartnerHandle, self.Messages['after_call'])

    def CallInputStatusChanged(self, Call, Active):
        """ Unset output file after it finished playing """
        if not Active:
            Call.InputDevice(Skype4Py.callIoDeviceTypeFile, None)

    def AuthorizationRequestReceived(self, User):
        """ Accept authorisation requests and send greetings """
        if not User.IsAuthorized:
            User.IsAuthorized = True
            Logging.info("Authorisation request received from %s, accepting it and sending welcome text", User.Handle)
            self.Skype.CreateChatWith(User.Handle).SendMessage(self.Messages['after_auth'])

    def MessageStatus(self, Message, Status):
        """ Event handler for Skype chats """
        if Status == Skype4Py.cmsSent:
            # iteration trough Message.Users does not work here for unknown reasons
            # that is we are using chat members loop
            for User in Message.Chat.Members:
                if not User == self.Skype.CurrentUser:
                    Logging.info("Message '%s' was sent to user %s", Message.Body, User.Handle)
        elif Status == Skype4Py.cmsReceived:
            Logging.info("Message '%s' received from user %s", Message.Body, Message.FromHandle)
            Message.MarkAsSeen()
            self.ProcessMessage(Message)

    def Listen(self):
        """ Forever loop I wanna be forever loop """
        while True:
            time.sleep(1)

    def __init__(self):
        """ Initialize Skype Bot """
        self.AI = aiml.Kernel()

        # set bot biography
        for BotParam in self.Params:
            self.AI.setBotPredicate(BotParam, self.Params[BotParam])

        self.Skype = Skype4Py.Skype()
        self.Skype.Attach()

        Logging.basicConfig(format='%(asctime)s %(message)s', level=Logging.INFO)
        Logging.info("Skypebot connected with login %s", self.Skype.CurrentUser.Handle)

        # set event handlers
        self.Skype.OnUserAuthorizationRequestReceived = self.AuthorizationRequestReceived
        self.Skype.OnMessageStatus = self.MessageStatus
        self.Skype.OnCallStatus = self.CallStatus
        self.Skype.OnCallInputStatusChanged = self.CallInputStatusChanged

        # small trick: google unofficial APIs does not work with native urllib User-Agent
        class SkypeURLopener(urllib.FancyURLopener):
            version = "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.79 Safari/535.11"

        urllib._urlopener = SkypeURLopener()

"""
HOWTO:
Alice = SkypeBot()
Alice.LoadBrain()
Alice.Listen()
"""
