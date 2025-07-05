import re
import os
from PIL import Image

# Default Values

MIN_SIZE_KB = 100
MAX_SIZE_KB = 2048
VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png')

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
     global MIN_SIZE_KB, MAX_SIZE_KB, VALID_EXTENSIONS
     MIN_SIZE_KB = config.get("MIN_SIZE_KB", MIN_SIZE_KB)
     MAX_SIZE_KB = config.get("MAX_SIZE_KB", MAX_SIZE_KB)
     VALID_EXTENSIONS = tuple(config.get("VALID_EXTENSIONS", VALID_EXTENSIONS))
     return [MIN_SIZE_KB, MAX_SIZE_KB, VALID_EXTENSIONS]

def is_valid_image_format(file_path: str) -> bool:
     return file_path.lower().endswith(VALID_EXTENSIONS)

def compress_image(file_path: str, output_path: str, quality: int = 85) -> None:
     img = Image.open(file_path)
     img = img.convert("RGB")  # Convert to RGB if not already
     img.save(output_path, format='JPEG', quality=quality, optimize=True)

def process_image(input_path: str) -> None:
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
     
     for quality in range(85, 10, -5):
          temp_path = sanitized_path.replace(".jpg", f"_temp_{quality}.jpg").replace(".jpeg", f"_temp_{quality}.jpg").replace(".png", f"_temp_{quality}.png")
          compress_image(sanitized_path, temp_path, quality)
          temp_size_kb = get_file_size_kb(temp_path)
          
          if MIN_SIZE_KB <= temp_size_kb <= MAX_SIZE_KB:
               os.rename(temp_path, sanitized_path)
               print(f"Compressed {sanitized_name} to {temp_size_kb:.2f} KB at quality {quality}.")
               return
          os.remove(temp_path)

     print(f"Error: Unable to compress {sanitized_name} to a valid size.")


if __name__ == "__main__":
     s_ = try_importing_config_file()
     print(s_)