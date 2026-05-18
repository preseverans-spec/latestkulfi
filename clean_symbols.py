import os

def clean_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Define the bad sequences and their fixes
        replacements = [
            (b'\xe2\x82\xb9', '₹'.encode('utf-8')), # Rupee
            (b'\xe2\x88\x92', '-'.encode('utf-8')), # Minus
            (b'\xe2\x80\x93', '-'.encode('utf-8')), # En dash
            (b'\xe2\x80\x94', '-'.encode('utf-8')), # Em dash
            (b'\xe2\x80\x98', "'".encode('utf-8')),
            (b'\xe2\x80\x99', "'".encode('utf-8')),
            (b'\xe2\x80\x9c', '"'.encode('utf-8')),
            (b'\xe2\x80\x9d', '"'.encode('utf-8')),
        ]
        
        original_content = content
        for bad, good in replacements:
            content = content.replace(bad, good)
            
        if content != original_content:
            with open(filepath, 'wb') as f:
                f.write(content)
            print(f"Cleaned symbols in: {filepath}")
            return True
    except Exception as e:
        print(f"Error cleaning {filepath}: {e}")
    return False

# Clean templates
template_dir = r"templates/inventory"
for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            clean_file(os.path.join(root, file))

# Clean views
clean_file(r"inventory/views.py")
