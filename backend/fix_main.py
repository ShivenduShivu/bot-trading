# Read main.py
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and remove AI endpoints section
ai_section_start = content.find('# ===== AI Strategy Builder Endpoints =====')
if ai_section_start != -1:
    # Find the end (next section or analytics)
    ai_section_end = content.find('\n\n# ===== Analytics Endpoints =====', ai_section_start)
    if ai_section_end != -1:
        ai_section = content[ai_section_start:ai_section_end]
        # Remove from current location
        content = content[:ai_section_start] + content[ai_section_end:]
        
        # Insert before analytics section
        analytics_pos = content.find('# ===== Analytics Endpoints =====')
        if analytics_pos != -1:
            content = content[:analytics_pos] + ai_section + '\n\n' + content[analytics_pos:]

# Write fixed file
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed! AI endpoints moved to correct location.")