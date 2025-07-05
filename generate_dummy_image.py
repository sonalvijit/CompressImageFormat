import os
import sys
import numpy as np
from PIL import Image
import time

# Target sizes in kilobytes (KB)
target_sizes_mb = [0.5, 1, 2, 4, 10]
target_sizes_kb = [int(x * 1024) for x in target_sizes_mb]

# Output folder
output_folder = "generated_images"
os.makedirs(output_folder, exist_ok=True)

def print_progress_bar(current, total, bar_length=40):
    progress = int(bar_length * current / total)
    bar = '█' * progress + '-' * (bar_length - progress)
    percent = (current / total) * 100
    sys.stdout.write(f"\rProgress: |{bar}| {percent:.1f}%")
    sys.stdout.flush()

def generate_white_image_with_noise(target_kb: int):
    base_size = 500  # starting width & height
    quality = 100
    attempts = 0
    max_attempts = 100  # for progress bar display only

    while True:
        attempts += 1
        print_progress_bar(min(attempts, max_attempts), max_attempts)

        # Create nearly white image with slight noise
        array = np.full((base_size, base_size, 3), 255, dtype=np.uint8)
        noise = np.random.randint(0, 3, (base_size, base_size, 3), dtype=np.uint8)  # tiny noise
        array = array - noise
        img = Image.fromarray(array, 'RGB')

        file_name = f"white_{target_kb}kb.jpg"
        path = os.path.join(output_folder, file_name)

        img.save(path, format="JPEG", quality=quality, optimize=True)
        actual_size_kb = os.path.getsize(path) / 1024

     #    sys.stdout.write(f"\rTrying: {file_name} | Size: {actual_size_kb:.2f} KB | Dim: {base_size}x{base_size} | Q: {quality}      \n")
     #    sys.stdout.flush()

        # Acceptable within ±50 KB range
        if abs(actual_size_kb - target_kb) <= 50:
          #   print(f"✅ Generated: {file_name} ({actual_size_kb:.2f} KB)\n")
            print(f"✅ Generated: {file_name} ({actual_size_kb:.2f} KB)\nTrying: {file_name} | Size: {actual_size_kb:.2f} KB | Dim: {base_size}x{base_size} | Q: {quality}")
            break

        # Adjust logic
        if actual_size_kb < target_kb:
            base_size += 200
        else:
            if quality > 20:
                quality -= 5
            else:
                base_size -= 100

        if base_size > 20000 or base_size < 100:
            print(f"❌ Could not match size for {target_kb} KB\n")
            break

# Generate all images
for index, kb in enumerate(target_sizes_kb, 1):
    print(f"\n🔧 Generating image {index}/{len(target_sizes_kb)} for ~{kb} KB")
    generate_white_image_with_noise(kb)
