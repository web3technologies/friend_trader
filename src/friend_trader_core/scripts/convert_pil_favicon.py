from PIL import Image, ImageFilter, ImageEnhance
import sys


def jpg_to_favicon(jpg_file, output_file='favicon.ico', size=(16,16)):
    with Image.open(jpg_file) as img:
        img = img.resize((64, 64), Image.BICUBIC)
        img = img.resize(size, Image.BICUBIC)
        
        # Increase sharpness (optional)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        img.save(output_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py input.jpg [output.ico]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if len(sys.argv) == 3:
        output_file = sys.argv[2]
    else:
        output_file = 'favicon.ico'
    
    jpg_to_favicon(input_file, output_file)
    print(f"Converted {input_file} to {output_file}")
