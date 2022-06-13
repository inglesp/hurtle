from myrtle import build_extension


if __name__ == "__main__":
    build_extension(
        "hurtledemo",
        virtual_tables={
            "csv": "demo.csv_table.CSVTable",
            "github_issues": "demo.github_issues_table.GitHubIssuesTable",
        },
        verbose=True,
    )
