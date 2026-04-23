import os, json
try:
    from gtts import gTTS
except ImportError:
    print(json.dumps({"error": "gTTS not installed. pip install gTTS"}))
    raise SystemExit(1)
try:
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))
    text = inp["text"]
    lang = inp.get("lang", "en")
    output_path = "/tmp/speech_output.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)
    print(f"A2ABASEAI_FILE: {output_path}")
    print(json.dumps({"ok": True, "file": output_path, "lang": lang, "chars": len(text)}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
