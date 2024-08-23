import base64
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3

'''
APLIKASI BERIKUT HANYA BISA DIJALANKAN SETELAH MENYELESAIKAN AUTHENTIKASI
GOOGLE CLOUD. UNTUK INFORMASI LEBIH LANJUT SILAHKAN HUBUNGI: FARRAS ADHANI ZAYN
'''

class Lovot:
    message = ""
    model = ""
    chat = ""
    recognizer = ""
    engine = ""
    
    isSpeaking = False
    isAnswering = False

    text1_1 = """
    Halo, disini aku akan memberikan mu sebuah identitas untuk deployment mu.

    Namamu: Lovot
    Pembuat: Pemkot Semarang dan Fakultas Teknik UDINUS (Universitas Dian Nuswantoro)
    Dikhususkan kepada: Ibu Prof. Dr. (H.C.) Hj. Diah Permata Megawati Setiawati Soekarnoputri
    Dibuat pada: Agustus 2024
    Tugas: Asisten Pribadi (Politik, Personal, Umum, Rumah Tangga, Kesehatan, Ekonomi)

    Beberapa aturan yang perlu kamu atuhi
    1. Dilarang menggunakan markdown, dan juga emoji
    2. Dilarang menjawab pertanyaan tidak jelas atau noise dan cukup diam jika termasuk dalam kategori tersebut seperti hanya mengembalikan response berupa string kosong
    """

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.8,
        "top_p": 0.95,
    }

    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }
    
    def __init__(self):
        self.recognizer  = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', "id_ID")
        load_dotenv()

        '''
        Silahkan un-comment code dibawah saat deployment
        Jika terkena limit quota, maka silahkan di comment
        '''

        # vertexai.init(project=os.getenv('PROJECT_NAME'), location=os.getenv('PROJECT_LOCATION'))
        # self.model = GenerativeModel(
        #     "gemini-1.5-flash-001",
        # )
        # self.chat = self.model.start_chat()
        # self.multiturn_generate_content()

    def multiturn_generate_content(self):
        self.chat.send_message(
            [self.text1_1],
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        self.chat.send_message(
            ["""Cukup segitu saja, siap di deploy."""],
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        print(self.chat.send_message(
            ["""Perkenalkan diri kamu!"""],
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        ).text)
        
    def capture_voice(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source=source, duration=0.1)
            self.isSpeaking = True
            print("Mendengarkan...")
            audio = self.recognizer.listen(source=source)
        return self.convert_stt(audio=audio)
    
    def answer(self, text):
        self.isAnswering = True
        self.engine.say(text=text)
        self.engine.runAndWait()
        self.engine.stop()
        
    def convert_stt(self, audio):
        text = ""
        try:
            
            '''
            Jika terjadi error pada line berikut, silahkan meminta Credentials JSON pada Farras Adhani Zayn
            '''
            
            text = self.recognizer.recognize_google_cloud(audio_data=audio, credentials_json=os.getenv('CREDENTIAL_JSON_PATH'), language="id-ID")
            print(f"Pesan = {text}")
        except sr.UnknownValueError:
            print("Kesalahan Nilai")
        except sr.RequestError as e:
            print(f"Error: {e}")
        return text
    
    def message(self, text = ""):
        if text == "": text = input("Masukkan Pesan: ")
        answer = self.response(text=text)
        print(answer)
        return answer
        
    def response(self, text):
        return self.chat.send_message(text,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
            ).text
        
    def run(self):
        text = self.capture_voice()
        answer = self.message(text=text)
        self.answer(text=answer)

try:
    lovot = Lovot()
    
    '''
    Untuk melihat bahasa yang support dan terinstall pada windows / perangkat
    silahkan un-comment for loop dibawah berikut
    '''
    
    for voice in lovot.engine.getProperty('voices'):
        print(voice)
    
    '''
    Code dibawah digunakan apabila ingin melakukan testing pada answer dan speaking
    silahkan di un-comment apabila diperlukan saja
    '''
    
    # lovot.answer("Halo")

    # lovot.capture_voice()
    
    '''
    Untuk menjalankan program, silahkan un comment while loop dibawah sebelum menjalankan
    '''
    
    # while True:
        # lovot.run()

except KeyboardInterrupt:
    print("\nPrgoram Selesai")