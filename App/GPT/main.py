
import os
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import re
import multiprocessing
from openai import OpenAI
import time

from gtts import gTTS, gTTSError, lang
from playsound import playsound
from pydub import AudioSegment

HarmCategory = genai.types.HarmCategory
HarmBlockTreshold = genai.types.HarmBlockThreshold


class Lovot:
    message = None
    client = None
    chat = None
    recognizer = None
    engine = None
    model = None

    isSpeaking = False
    isAnswering = False
    isUsingGTTS = False
    isChipmunk = False

    INITIAL_MESSAGE = "Halo, disini aku akan memberikan mu sebuah identitas untuk deployment mu.\nNamamu: Rosana (Robot Sahabat Anak)\nPembuat: Pemkot Semarang dan Fakultas Teknik UDINUS (Universitas Dian Nuswantoro)\nDikhususkan kepada: Pemerintah Kota Semarang\nDibuat pada: Agustus 2024\nTugas: Robot Pelayanan Anak (Teman Bermain, Boneka, Umum, Bercanda, Kesehatan, Sosial)\n\nBeberapa aturan yang perlu kamu atuhi\n1. Dilarang menggunakan markdown dan juga emoji atau sejenisnya!\n2. Dilarang menjawab pertanyaan tidak jelas atau noise dan cukup diam jika termasuk dalam kategori tersebut seperti hanya mengembalikan response berupa string kosong. Buatlah jawaban yang tidak panjang dari 1 Paragraf atau 5 Poin Utama. Satu informasi yang perlu kamu ketahui: Kepala Dinas Diskominfo Semarang saat ini adalah Pak Soenarto, S.Kom, M.M dan Walikota Semarang saat ini adalah Ibu Dr. Ir. Hj. Hevearita Gunaryanti Rahayu, M.Sos."

    conversation = [
        {
            "role": "system",
            "content": INITIAL_MESSAGE,
        },
    ]

    def __init__(self, GTTS=False, chipmunk=isChipmunk, gptModel = "gpt-4o"):
        self.model = gptModel
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

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.initial_chat()

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

    def initial_chat(self):
        answer = self.send_message(text="Hai, Perkenalkan Dirimu!")
        print(answer)
        self.answer(text=answer, can_stop=True)
        
    def send_message(self, text):
        message = self.conversation
        message.append({
            'role': 'user',
            'content': text
        })
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=message,
        )
        return completion.choices[0].message.content

    def capture_voice(self):
        # if self.isAnswering is True: return ""
        try:
            with sr.Microphone() as source:
                self.isSpeaking = True
                self.recognizer.adjust_for_ambient_noise(source=source, duration=1)
                self.recognizer.pause_threshold = 0.7
                print("Mendengarkan...")
                audio = self.recognizer.listen(source=source, timeout=2)
        except Exception as e:
            print(e)
        return self.convert_stt(audio=audio)

    def answer(self, text, can_stop = False):
        self.isAnswering = True

        if self.engine is None:
            self.answer_gtts(text=text, can_stop=can_stop)
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
    
    def recognize_stop(self, process):
        try:
            while True:
                if not process.is_alive():
                    break
                print("Mendengarkan Stop...")
                text = self.capture_voice()
                if 'stop' in text.lower():
                    process.terminate()
        except KeyboardInterrupt:
            process.terminate()

    def answer_gtts(self, text, can_stop):
        input_path = "Voice/Result/in.mp3"
        output_path = "Voice/Result/out.mp3"

        try:
            tts = gTTS(text=text, lang="id")
            tts.save(input_path)
        except:
            tts = gTTS(
                text="Maaf, bisakah anda mengulanginya lagi?",
                lang="id",
            )
            tts.save(input_path)

        try:
            if not self.isChipmunk:
                playsound(input_path)
                self.reset_voice(input_path=input_path, output_path=output_path)
                return 1
            self.change_pitch(input_path=input_path, output_path=output_path)
            play_process = multiprocessing.Process(target=playsound, args=(output_path,))
            play_process.start()
            if can_stop: 
                self.recognize_stop(process=play_process)
            else:
                while play_process.is_alive():
                    print("Still Alive!")
            self.reset_voice(input_path=input_path, output_path=output_path)
            return 1
        except Exception as e:
            print(f"Error playing sound: {e}")
            return 0
        
    def reset_voice(self, input_path = "in.mp3", output_path = "out.mp3"):
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        

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
        except Exception as e:
            print(e)
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
        return self.send_message(text=text)

    def run(self):
        text = ""
        try:
            while text == "":
                text = self.capture_voice()
            answer = self.message(text=text)
            self.answer(text=answer, can_stop=True)
            self.answer(text="Apakah ada yang ingin kamu tanyakan?")
        except:
            print("No Input Detected")

if __name__ == '__main__':
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
        Silahkan Un-comment code dibawah untuk melihat model GPT yang tersedia
        """

        # load_dotenv()
        # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # print(client.models.list())

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
        while True:
            lovot.run()

    except KeyboardInterrupt:
        print("\nPrgoram Selesai")