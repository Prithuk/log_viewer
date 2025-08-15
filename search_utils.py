def prompt_keywords():
    keywords = []
    while True:
        raw = input("Enter keyword(s) (comma-separated), or press Enter to skip: ").strip()
        if not raw or raw.lower() == 'exit':
            break
        keywords += [k.strip() for k in raw.split(',') if k.strip()]
    return keywords
