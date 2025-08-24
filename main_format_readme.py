import pandas as pd
from pathlib import Path

from tts import generate_tts, merge_audio_files
from utils import read_file, save_file, yaml_load

readme_template_path = Path("README_template.md")
readme_path = Path("README.md")

fra_masc_path = Path("fra_masc_ita_fem.yaml")
fra_fem_path = Path("fra_fem_ita_masc.yaml")

url_text = "_Écoutez les prononciations (par exemple en ouvrant ce lien dans un nouvel onglet)_"

mp3_urls = {
    "fra_masc_1": "https://drive.google.com/file/d/1uki_oBu6Alv1QBSI3xBa8D8OAnspnB9R/view?usp=sharing",
    "fra_masc_2": "https://drive.google.com/file/d/14SVAy30CMGbAYQlMVB9LoJnHocQfFJL1/view?usp=sharing",
    "fra_fem_1": "https://drive.google.com/file/d/10oxd6eB8zY_GhDuFI9tgBzeVtIFApO_p/view?usp=sharing",
    "fra_fem_2": "https://drive.google.com/file/d/1yaov_eOg1XJklURtlzKSC6LYm54g-Qfs/view?usp=sharing",
}

# sort alphabetically
def key_without_article(s):
    articles = ["les ", "la ", "le ", "l'"]
    for article in articles:
        if s.startswith(article):
            return s[len(article):].lower()
    raise ValueError(f"Article not found in {s}")


def add_fra_it(content: str) -> str:
    for file_path, content_placeholder in zip(
            [fra_masc_path, fra_fem_path],
            ["\nCONTENT_FRA_MASC", "\nCONTENT_FRA_FEM"]
    ):
        df = pd.DataFrame(
            yaml_load(file_path=file_path),
            columns=["category", "French", "Italian", " :wink: "]
        )

        # detect duplicates
        df_lower = df.apply(lambda x: x.str.lower() if x.dtype == "object" else x)
        for column_to_check in ["French", "Italian"]:
            dup = df_lower[df_lower.duplicated([column_to_check], keep=False)]
            if not dup.empty:
                print(f"in {column_to_check}: ")
                for du in dup[column_to_check].unique():
                    print(f"\tduplicate: {du}")

        for category, suffix in zip(
                [1, 2],
                ["\n", "_SECOND_RANK\n"]
        ):

            _df = df[df["category"] == category]

            from icu import Collator, Locale  # to deal with "é"

            collator = Collator.createInstance(Locale('fr_FR'))

            _df = _df.sort_values(
                by="French",
                key=lambda col: col.map(lambda x: collator.getSortKey(key_without_article(x)))
            )


            _df = _df.drop(columns=["category"])

            _df.insert(0, "#", range(1, len(_df) + 1))

            p = content_placeholder.replace('\nCONTENT_', '').lower()
            generate_tts(_df, prefix=f"{p}_{category}")

            # Français
            _df.rename(columns={
                'French': 'Français ( :fr: )',
                'Italian': 'Italien ( :it: )'
            }, inplace=True)

            table = _df.to_markdown(
                index=False,
                colalign=["center"] * len(_df.columns)
            )

            url = mp3_urls[f"{p}_{category}"]

            url_link = f":arrow_forward: [ {url_text} ]({url}) :speaking_head: :loud_sound:"

            content = content.replace(content_placeholder + suffix, f"\n{url_link}\n\n{table}\n")

    return content


def main() -> None:
    content = read_file(file_path=readme_template_path)
    content = add_fra_it(content)
    save_file(file_path=readme_path, content=content)

    merge_audio_files()

if __name__ == '__main__':
    main()