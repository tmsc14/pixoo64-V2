from threading import Thread, Lock
from PIL import Image
from pixoo import Pixoo
from config import Config

class PixooService:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self.pixoo = Pixoo(Config.PIXOO_HOST, Config.PIXOO_SCREEN_SIZE, Config.PIXOO_DEBUG)
        self.animation_thread = None
        self.stop_animation = False
        self.animation_lock = Lock()

    def start_animation(self, target, args=()):
        with self.animation_lock:
            if self.animation_thread:
                self.stop_animation = True
                self.animation_thread.join()
                
            self.stop_animation = False
            self.animation_thread = Thread(target=target, args=args, daemon=True)
            self.animation_thread.start()

    def draw_image(self, image):
        try:
            self.pixoo.draw_image(image.convert("RGB"))
            self.pixoo.push()
        except Exception as e:
            print(f"Error updating Pixoo display: {e}")