import re
import os
from PIL import Image
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('sqlite:///images.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class UserConfig(Base):
     __tablename__ = 'user_config'
     id = Column(Integer, primary_key=True)
     min_size_kb = Column(Integer, default=100)
     max_size_kb = Column(Integer, default=2048)
     valid_extensions = Column(String, default='.jpg,.jpeg,.png')
     base_dir = Column(String, default='./')

     def __repr__(self):
          return (f"<UserConfig(min_size_kb={self.min_size_kb}, "
                  f"max_size_kb={self.max_size_kb}, "
                  f"valid_extensions='{self.valid_extensions}', "
                  f"base_dir='{self.base_dir}')>")
     
def initialize_database():
     """Initialize the database and create tables."""
     try:
          Base.metadata.create_all(engine)
          print("[+] Database initialized successfully.")
     except Exception as e:
          print(f"[!] Error initializing database: {e}")
         
def add_user_config(min_size_kb: int = 100, max_size_kb: int = 2048,
                 valid_extensions: str = '.jpg,.jpeg,.png', base_dir: str = './'):
     session = Session()
     try:
          config = UserConfig(
               min_size_kb=min_size_kb,
               max_size_kb=max_size_kb,
               valid_extensions=valid_extensions,
               base_dir=base_dir
          )
          session.add(config)
          session.commit()
          print(f"[+] UserConfig added: {config}")
     except Exception as e:
          session.rollback()
          print(f"[!] Error adding UserConfig: {e}")
     finally:
          session.close()

# Default Values

MIN_SIZE_KB = 100
MAX_SIZE_KB = 2048
VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png')
BASE_DIR: str = "./"

def save_user_config():
     pass

def try_importing_config_file():
     a = read_config()
     if a is None:
          print("No config file found, using default settings.")
          return
     return parse_config(a)

def sanitize_filename(filename: str) -> str:
     name, ext = os.path.splitext(filename)
     name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
     sanitized = f"{name}{ext.lower()}"
     return sanitized

def get_file_size_kb(file_path: str) -> float:
     return os.path.getsize(file_path) / 1024

def read_config(file_path:str="./preconfig.json"):
     import json
     try:
          with open(file_path, 'r') as file:
               config = json.load(file)
          return config
     except FileNotFoundError:
          print(f"Error: The file {file_path} does not exist.")
          return None
     except json.JSONDecodeError:
          print(f"Error: The file {file_path} is not a valid JSON.")
          return None

def parse_config(config: dict):
     global MIN_SIZE_KB, MAX_SIZE_KB, VALID_EXTENSIONS, BASE_DIR
     MIN_SIZE_KB = config.get("MIN_SIZE_KB", MIN_SIZE_KB)
     MAX_SIZE_KB = config.get("MAX_SIZE_KB", MAX_SIZE_KB)
     VALID_EXTENSIONS = tuple(config.get("VALID_EXTENSIONS", VALID_EXTENSIONS))
     BASE_DIR = config.get("BASE_DIR", BASE_DIR)
     return [MIN_SIZE_KB, MAX_SIZE_KB, VALID_EXTENSIONS, BASE_DIR]

def is_valid_image_format(file_path: str) -> bool:
     return file_path.lower().endswith(VALID_EXTENSIONS)

def compress_image(file_path: str, output_path: str, quality: int = 85) -> None:
     img = Image.open(file_path)
     img = img.convert("RGB")  # Convert to RGB if not already
     img.save(output_path, format='JPEG', quality=quality)

def process_image(input_path: str) -> None:
     input_path = os.path.join(BASE_DIR, input_path)
     if not is_valid_image_format(input_path):
          print(f"Error: The file {input_path} is not a valid image format.")
          return
     
     sanitized_name = sanitize_filename(os.path.basename(input_path))
     sanitized_path = os.path.join(os.path.dirname(input_path), sanitized_name)
     os.rename(input_path, sanitized_path)

     size_kb = get_file_size_kb(sanitized_path)
     print(f"Initial Size: {size_kb:.2f} KB")

     if MIN_SIZE_KB <= size_kb <= MAX_SIZE_KB:
          print(f"File {sanitized_name} is within the size limits.")
          return
     
     for quality in range(95, 10, -5):
          name, _ = os.path.splitext(sanitized_path)
          compressed_path = f"{name}_compressed.jpg"

          compress_image(sanitized_path, compressed_path, quality)
          compressed_size_kb = get_file_size_kb(compressed_path)
          print(f"Trying quality {quality}: {compressed_size_kb:.2f} KB")

          if MIN_SIZE_KB <= compressed_size_kb <= MAX_SIZE_KB:
               print(f"Compressed {sanitized_name} to {compressed_size_kb:.2f} KB at quality {quality}.")
               return
          os.remove(compressed_path)
     print(f"Error: Unable to compress {sanitized_name} to a valid size.")

def stimulate_terminal_interface():
     print("Input these field: \n\033[35mMIN_SIZE_KB\033[0m \n\033[35mMAX_SIZE_KB\033[0m \n\033[35mBASE_DIR\033[0m")
     while True:
          try:
               in_ = input(">>> ")
               print(in_)
               if in_.strip().lower() == 'exit' or in_.strip().lower() == 'quit':
                    print("Exiting terminal interface. Existing gracefully...")
                    break
          except KeyboardInterrupt:
               print("\nExiting terminal interface. Existing gracefully...")
               break

if __name__ == "__main__":
     # stimulate_terminal_interface()
     # s_ = try_importing_config_file()
     # print(s_)
     # process_image("example.jpg")

     initialize_database()
     a = input("Do you want to add a user config? (yes/no): ").strip().lower()
     if a == 'yes':
          min_size = int(input("Enter minimum size in KB: "))
          max_size = int(input("Enter maximum size in KB: "))
          valid_ext = input("Enter valid extensions (comma separated): ")
          base_dir = input("Enter base directory: ")
          add_user_config(min_size, max_size, valid_ext, base_dir)
     else:
          print("No user config added.")