from pathlib import Path
import pandas as pd
from gtts import gTTS
from pydub import AudioSegment

saving_root_dir = Path("tts_output")
saving_root_dir.mkdir(exist_ok=True)


def merge_audio_files():
    audio_files = saving_root_dir.glob("*.mp3")
    audio_files = sorted(audio_files, key=lambda x: x.name)

    audio_segments = [AudioSegment.from_mp3(str(audio_file)) for audio_file in audio_files]
    final_audio = sum(audio_segments)

    saving_path = saving_root_dir / "final.mp3"
    final_audio.export(saving_path, format="mp3")
    print(f"🎉 final generated : {saving_path}")



def generate_tts(
        df: pd.DataFrame,
        prefix: str = "",
        overwrite: bool = False,
        pause_duration_ms: int = 800,
):
    print("\n")
    # df = df[:3]

    # -------------------------------

    lang_map = {
        "French": "fr",
        "Italian": "it",
    }

    saving_dir = saving_root_dir / prefix
    saving_dir.mkdir(exist_ok=True, parents=True)

    pause = AudioSegment.silent(duration=pause_duration_ms)

    # -------------------------------

    all_files = []

    for i, row in df.iterrows():
        idx = row['#']
        # assert i == idx, f"index mismatch : {i} != {idx}"

        row_name = row['French'].replace(' ', '_').replace('/', '_')

        saving_path = saving_dir / f"{row_name}.mp3"

        all_files.append(saving_path)

        if saving_path.exists() and (not overwrite):
            print(f"❌ already exists : {saving_path}")
            continue

        # -------------------------------

        audio_segments = []

        for lang in lang_map.keys():
            text = row[lang].replace("_", "")
            text = text.replace("le chat ", "le tchat ")  # temp fix
            lang_code = lang_map[lang]

            temp_file = saving_dir / f"tmp_{lang}.mp3"
            gTTS(text=text, lang=lang_code).save(str(temp_file))

            segment = AudioSegment.from_mp3(str(temp_file))
            audio_segments.append(segment + pause)

        # concatenate fra + it
        combined = sum(audio_segments)
        combined.export(str(saving_path), format="mp3")

        print(f"✅ generated [{idx}/{len(df)}] : {saving_path}")


    # -------------------------------
    # clean up
    for lang in lang_map.keys():
        temp_file = saving_dir / f"tmp_{lang}.mp3"
        if temp_file.exists():
            print(f"❌ removing : {temp_file}")
            temp_file.unlink()

    # -------------------------------
    # concatenate all
    name_saved = set([p.stem for p in saving_dir.glob("*.mp3")])
    name_required = set([p.stem for p in all_files])
    print(f"missing   : {name_required - name_saved}")
    print(f"not needed: {name_saved - name_required}")

    final_audio = AudioSegment.empty()
    for file in all_files:
        final_audio += pause + AudioSegment.from_mp3(file)
    final_audio += pause

    saving_path = saving_root_dir / f"{prefix}__{len(all_files)}_rows.mp3"
    # if not saving_path.exists() and overwrite:
    final_audio.export(saving_path, format="mp3")
    print(f"🎉 final generated : {saving_path}")
