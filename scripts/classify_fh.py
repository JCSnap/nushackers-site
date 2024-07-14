import os
import re
import csv
from openai import OpenAI

client = OpenAI(
    api_key="API_KEY",
)

folder_path = "../content/post"
output_file = 'output.csv'

# hardcoded one shot prompting to make sure the categories are formatted properly
one_shot_file = "2012-04-13-friday-hacks-24.md"
one_shot_content = ""

with open(os.path.join(folder_path, one_shot_file), 'r', encoding='utf-8') as file:
    one_shot_content = file.read()

one_shot_categories = "Programming Languages, Web Development"


def is_relevant_filename(filename):
    pattern = r'\d{4}-\d{2}-\d{2}-friday-hacks-\d+\.md'
    return re.match(pattern, filename)

def categorize_content(content, retries=3):
    try:
        system = """
        You will be given some description about one or two talks.

        Categorize the following content into one or a maximum of three of these categories based on relevance: Web Development, Security, Startups, Game Development, Math, Programming Languages, Machine Learning/Artificial Intelligence, Databases, Open-source, DevOps, Crypto/Finance, Networking and Distributed Software, Parallel Computing, Multimedia Information Retrieval, Audience Participation. If neither are relevant, write NONE\n\n"""

        prompt = content + "\n\n" + "Categories:"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": one_shot_content},
                {"role": "assistant", "content": one_shot_categories},
                {"role": "user", "content": prompt},
            ],
            max_tokens=100,
            temperature=0.5,
        )
        categories = response.choices[0].message.content.strip().split(", ")
    except:
        if retries > 0:
            return categorize_content(content, retries - 1)
        else:
            return []

    return categories if categories[0] != "NONE" else []

def process_files(folder_path):
    categories_dict = {
        "Web Development": [],
        "Security": [],
        "Startups": [],
        "Game Development": [],
        "Math": [],
        "Programming Languages": [],
        "Machine Learning/Artificial Intelligence": [],
        "Databases": [],
        "Open-source": [],
        "DevOps": [],
        "Crypto/Finance": [],
        "Networking and Distributed Software": [],
        "Parallel Computing": [],
        "Multimedia Information Retrieval": [],
        "Audience Participation": [],
    }

    for filename in os.listdir(folder_path):
        if is_relevant_filename(filename):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                print(f"Processing {filename}")
                content = file.read()
                categories = categorize_content(content)
                print(f"Categories: {categories}")
                for category in categories:
                    if category in categories_dict:
                        categories_dict[category].append(filename)

    return categories_dict

def write_to_csv(categories_dict, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        headers = list(categories_dict.keys())
        writer.writerow(headers)
        max_length = max(len(files) for files in categories_dict.values())
        for i in range(max_length):
            row = [categories_dict[category][i] if i < len(categories_dict[category]) else "" for category in headers]
            writer.writerow(row)

# Main function
def main():
    categories_dict = process_files(folder_path)
    write_to_csv(categories_dict, output_file)

if __name__ == "__main__":
    main()
