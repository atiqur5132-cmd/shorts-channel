"""Voiceover + word timings for a short.

  py -I tools/voice.py <short-dir>
Reads <short-dir>/brief.json "script" (list of lines), synthesizes Kokoro am_michael at 1.1x,
transcribes word timings (Parakeet) and writes assets/voice.wav + assets/transcript.json.
"""
import json
import os
import subprocess
import sys

PY = r"C:/Users/atiqu/AppData/Local/Python/pythoncore-3.14-64/python.exe"


def run(cmd, cwd):
    env = dict(os.environ, HYPERFRAMES_PYTHON=PY)
    p = subprocess.run(cmd, cwd=cwd, env=env, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        print(p.stdout[-1500:], p.stderr[-1500:])
        raise SystemExit(f"failed: {cmd}")
    return p.stdout


def main(short):
    brief = json.load(open(os.path.join(short, "brief.json"), encoding="utf-8"))
    os.makedirs(os.path.join(short, "assets"), exist_ok=True)
    open(os.path.join(short, "vo.txt"), "w", encoding="utf-8").write("\n".join(brief["script"]) + "\n")
    voice = brief.get("voice", "am_michael")
    speed = brief.get("speed", 1.1)
    run(f'npx -y hyperframes@0.8.208 tts vo.txt --voice {voice} --speed {speed} -o assets/voice.wav', short)
    out = run("npx -y hyperframes@0.8.208 transcribe assets/voice.wav --json", short)
    words = None
    for line in out.splitlines():
        i = line.find('{"type":"words"')
        if i >= 0:
            words = json.loads(line[i:])["words"]
    if not words:  # the CLI also writes assets/transcript.json itself
        data = json.load(open(os.path.join(short, "assets", "transcript.json"), encoding="utf-8"))
        words = data["words"] if isinstance(data, dict) else data
    json.dump({"words": words}, open(os.path.join(short, "assets", "transcript.json"), "w", encoding="utf-8"))
    print(f"voice ok: {len(words)} words, ends {words[-1]['end']:.2f}s")


if __name__ == "__main__":
    main(sys.argv[1])
