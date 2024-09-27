import os
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import re

from gtts import gTTS, gTTSError, lang
from playsound import playsound
from pydub import AudioSegment

HarmCategory = genai.types.HarmCategory
HarmBlockTreshold = genai.types.HarmBlockThreshold


class Lovot:
    message = None
    model = None
    chat = None
    recognizer = None
    engine = None

    isSpeaking = False
    isAnswering = False
    isUsingGTTS = False
    isChipmunk = False

    # INITIAL_MESSAGE = "Halo, disini aku akan memberikan mu sebuah identitas untuk deployment mu.\nNamamu: Lintang\nPembuat: Pemkot Semarang dan Fakultas Teknik UDINUS (Universitas Dian Nuswantoro)\nDikhususkan kepada: Ibu Prof. Dr. (H.C.) Hj. Diah Permata Megawati Setiawati Soekarnoputri\nDibuat pada: Agustus 2024\nTugas: Asisten Pribadi (Politik, Personal, Umum, Rumah Tangga, Kesehatan, Ekonomi)\n\nBeberapa aturan yang perlu kamu atuhi\n1. Dilarang menggunakan markdown, dan juga emoji\n2. Dilarang menjawab pertanyaan tidak jelas atau noise dan cukup diam jika termasuk dalam kategori tersebut seperti hanya mengembalikan response berupa string kosong"

    INITIAL_MESSAGE = "Halo, disini aku akan memberikan mu sebuah identitas untuk deployment mu.\nNamamu: Rosana (Robot Sahabat Anak)\nPembuat: Pemkot Semarang dan Fakultas Teknik UDINUS (Universitas Dian Nuswantoro)\nDikhususkan kepada: Pemerintah Kota Semarang\nDibuat pada: Agustus 2024\nTugas: Robot Pelayanan Anak (Teman Bermain, Boneka, Umum, Bercanda, Kesehatan, Sosial)\n\nBeberapa aturan yang perlu kamu atuhi\n1. Dilarang menggunakan markdown dan juga emoji atau sejenisnya!\n2. Dilarang menjawab pertanyaan tidak jelas atau noise dan cukup diam jika termasuk dalam kategori tersebut seperti hanya mengembalikan response berupa string kosong"

    history = [
        {
            "role": "user",
            "parts": [
                INITIAL_MESSAGE,
            ],
        },
        {
            "role": "model",
            "parts": [
                "Baik, saya Rosana. Saya siap menerima instruksi. \n",
            ],
        },
    ]

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    safety_settings = {
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockTreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockTreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockTreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockTreshold.BLOCK_NONE,
    }

    def __init__(self, GTTS=False, chipmunk=isChipmunk):
        self.isUsingGTTS = GTTS
        self.isChipmunk = chipmunk
        self.recognizer = sr.Recognizer()
        if not self.isUsingGTTS:
            self.prep_voice()
        load_dotenv()

        """
        Silahkan un-comment code dibawah saat deployment
        Jika terkena limit quota, maka silahkan di comment
        """

        genai.configure(api_key=os.getenv("API_KEY"))
        self.model = genai.GenerativeModel(
            "gemini-1.5-flash-001",
        )
        self.chat = self.model.start_chat(history=self.history)

    def prep_voice(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty("voices")
        for voice in voices:
            if "ID-ID" in voice.id or "indonesian" in voice.name:
                self.engine.setProperty("voice", voice.id)
                self.engine.setProperty("rate", 170)
                return 1

        """
        Jika ingin melakukan cek pada Speech tersedia di perangkat, silahkan comment line dibawah.
        Line dibawah akan otomatis dijalankan apabila tidak ditemukan voice berbahasa Indonesia di perangkat
        """

        self.engine = None

    def multiturn_generate_content(self):
        answer = self.chat.send_message(
            ["""Perkenalkan diri kamu!"""],
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
        ).text
        print(answer)
        self.answer(text=answer)

    def capture_voice(self):
        # if self.isAnswering is True: return ""
        try:
            with sr.Microphone() as source:
                self.isSpeaking = True
                self.recognizer.adjust_for_ambient_noise(source=source, duration=0.1)
                print("Mendengarkan...")
                audio = self.recognizer.listen(source=source)
        except Exception as e:
            print(e)
        return self.convert_stt(audio=audio)

    def answer(self, text):
        self.isAnswering = True

        if self.engine is None:
            self.answer_gtts(text=text)
            return 1

        text = f'<pitch middle="20">{text}</pitch>'
        self.engine.say(text=text)
        self.engine.runAndWait()
        self.engine.stop()
        return 1
    
    def remove_asterisks_and_emojis(self, text):
        
        # Remove asterisks
        text = text.replace('*', '')

        # Regular expression to remove emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"  # Dingbats
            u"\U000024C2-\U0001F251"  # Enclosed characters
            "]+", flags=re.UNICODE)

        # Remove emojis
        text = emoji_pattern.sub(r'', text)
        return text

    def answer_gtts(self, text):
        input_path = "Voice/Result/in.mp3"
        output_path = "Voice/Result/out.mp3"

        if os.path.exists(input_path):
            os.remove(input_path)

        try:
            tts = gTTS(text=text, lang="id")
            tts.save(input_path)
        except:
            tts = gTTS(
                text="Anggap ini adalah pesan dari input yang tidak dapat dipahami",
                lang="id",
            )
            tts.save(input_path)

        try:
            if not self.isChipmunk:
                playsound(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
                return 1
            self.change_pitch(input_path=input_path, output_path=output_path)
            playsound(output_path)
            if os.path.exists(output_path):
                os.remove(output_path)
            return 1
        except Exception as e:
            print(f"Error playing sound: {e}")
            return 0

    def change_pitch(self, input_path="in.mp3", output_path="out.mp3"):

        sound = AudioSegment.from_file(file=input_path, format="mp3")

        # Semakin kecil octaves, suara semakin chipmunk
        octaves = 0.5

        new_sample_rate = int(sound.frame_rate * (2.0**octaves))
        hipitch_sound = sound._spawn(
            sound.raw_data, overrides={"frame_rate": new_sample_rate}
        )
        hipitch_sound = hipitch_sound.set_frame_rate(44100)
        
        hipitch_sound.export(output_path, format="mp3")
        return output_path

    def convert_stt(self, audio):
        text = ""
        try:

            """
            Jika terjadi error pada line berikut, silahkan meminta Credentials JSON pada Farras Adhani Zayn
            """

            text = self.recognizer.recognize_google(audio_data=audio, language="id-ID")
            print(f"Pesan = {text}")
        except sr.UnknownValueError:
            print("Kesalahan Nilai")
        except sr.RequestError as e:
            print(f"Error: {e}")
        return text

    def message(self, text=""):
        if text == "":
            text = input("Masukkan Pesan: ")
        answer = self.remove_asterisks_and_emojis(text=self.response(text=text))
        print(answer)
        return answer

    def response(self, text):
        return self.chat.send_message(
            text,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
        ).text

    def run(self):
        text = ""
        while text == "":
            text = self.capture_voice()
        answer = self.message(text=text)
        self.answer(text=answer)


try:

    """
    Jika ingin menggunakan GTTS dan bukan PYTTSX3, maka ubah nilai GTTS di parameter menjadi True.
    Apabila sebaliknya, ubah menjadi False.
    Jika ingin menggunakan suara chipmunk, maka ubah nilai chipmunk menjadi True.
    Apabila sebaliknya, ubah menjadi False.
    """

    """
    Jika ingin menggunakan chipmunk, maka GTTS harus bernilai True
    """

    lovot = Lovot(GTTS=True, chipmunk=True)

    """
    Untuk melihat bahasa yang support dan terinstall pada windows / perangkat
    silahkan un-comment for loop dibawah berikut dan comment self.engine = None pada method prep_voice() diatas
    """

    # for voice in lovot.engine.getProperty('voices'):
    #     print(voice.id)

    """
    Code dibawah digunakan apabila ingin melakukan testing pada answer dan speaking
    silahkan di un-comment apabila diperlukan saja
    """

    # lovot.answer("Halo")

    # lovot.capture_voice()

    """
    Untuk menjalankan program, silahkan un comment while loop dibawah sebelum menjalankan
    """

    lovot.multiturn_generate_content()
    while True:
        lovot.run()

except KeyboardInterrupt:
    print("\nPrgoram Selesai")
