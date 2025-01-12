import pandas as pd
from pathlib import Path

from utils import read_file, save_file, yaml_load

readme_template_path = Path("README_template.md")
readme_path = Path("README.md")

fra_masc_path = Path("fra_masc_ita_fem.yaml")
fra_fem_path = Path("fra_fem_ita_masc.yaml")
fra_masc_path_second_rank = Path("fra_masc_ita_fem_second_rank.yaml")
fra_fem_path_second_rank = Path("fra_fem_ita_masc_second_rank.yaml")


# sort alphabetically
def key_without_article(s):
    articles = ["les ", "la ", "le ", "l'"]
    for article in articles:
        if s.startswith(article):
            return s[len(article):]
    raise ValueError(f"Article not found in {s}")


def add_fra_it(content: str) -> str:
    for suffix, file_path, content_placeholder in zip(
            ["masc", "fem", "masc_2", "fem_2"],
            [fra_masc_path, fra_fem_path, fra_masc_path_second_rank, fra_fem_path_second_rank],
            ["\nCONTENT_FRA_MASC\n", "\nCONTENT_FRA_FEM\n", "\nCONTENT_FRA_MASC_SECOND_RANK\n", "\nCONTENT_FRA_FEM_SECOND_RANK\n"]
    ):
        df = pd.DataFrame(
            yaml_load(file_path=file_path),
            columns=["French", "Italian", "Notes"]
        )
        df = df.sort_values(by="French", key=lambda col: col.map(key_without_article))

        table = df.to_markdown(
            index=False,
            colalign=["center"] * len(df.columns)
        )

        content = content.replace(content_placeholder, f"\n{table}\n")

    return content


def main() -> None:
    content = read_file(file_path=readme_template_path)
    content = add_fra_it(content)
    save_file(file_path=readme_path, content=content)

if __name__ == '__main__':
    main()