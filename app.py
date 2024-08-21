import base64
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
from dotenv import load_dotenv

class Lovot:
    message = ""
    model = ""
    chat = ""

    text1_1 = """Halo, disini aku akan memberikan mu sebuah identitas untuk deployment mu.

    Namamu: Lovot
    Pembuat: Pemkot Semarang dan Fakultas Teknik UDINUS (Universitas Dian Nuswantoro)
    Dikhususkan kepada: Ibu Prof. Dr. (H.C.) Hj. Diah Permata Megawati Setiawati Soekarnoputri
    Dibuat pada: Agustus 2024
    Tugas: Asisten Pribadi (Politik, Personal, Umum, Rumah Tangga, Kesehatan, Ekonomi)

    Beberapa aturan yang perlu kamu atuhi
    1. Dilarang menggunakan markdown, dan juga emoji
    2. Dilarang menjawab pertanyaan tidak jelas atau noise dan cukup diam jika termasuk dalam kategori tersebut seperti hanya mengembalikan response berupa string kosong"""

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
        load_dotenv()
        # print(os.getenv('PROJECT_NAME'))
        vertexai.init(project=os.getenv('PROJECT_NAME'), location=os.getenv('PROJECT_LOCATION'))
        self.model = GenerativeModel(
            "gemini-1.5-flash-001",
        )
        self.chat = self.model.start_chat()
        self.multiturn_generate_content()

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
        
    def message(self, text = ""):
        if text == "": text = input("Masukkan Pesan: ")
        print(self.response(text))
        
    def response(self, text):
        return self.chat.send_message(text,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
            ).text
        
    def run(self):
        self.message()

try:
    while True:
        lovot = Lovot()
        lovot.run()
except KeyboardInterrupt:
    print("\nPrgoram Selesai")