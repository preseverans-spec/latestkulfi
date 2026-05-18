import os

# The specific corrupted strings we found in the file views
bad_rupee = "â‚¹"
bad_minus = "âˆ’"

def deep_clean(filepath):
    try:
        # Read as UTF-8, replacing errors to avoid crashes
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if bad_rupee in content or bad_minus in content:
            new_content = content.replace(bad_rupee, "₹").replace(bad_minus, "-")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Deep Cleaned: {filepath}")
            return True
    except Exception as e:
        print(f"Error deep cleaning {filepath}: {e}")
    return False

template_dir = r"templates/inventory"
for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            deep_clean(os.path.join(root, file))

deep_clean(r"inventory/views.py")
