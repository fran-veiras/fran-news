import os
import requests
from bs4 import BeautifulSoup
import openai
import tiktoken

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

openai.api_key = os.environ["OPENAI_API_KEY"]

client = openai.OpenAI()


def get_completion_from_messages(
    messages, model="gpt-3.5-turbo", temperature=0, max_tokens=500
):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,  # this is the degree of randomness of the model's output
        max_tokens=max_tokens,  # the maximum number of tokens the model can ouptut
    )

    content = response.choices[0].message.content.strip()

    return content


URL = "https://www.theverge.com/tech"

response = requests.get(URL)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")

popular_news = soup.find_all("li", class_="leading-120 text-franklin", limit=5)

for news in popular_news:
    title = (
        news.find("a").find("h2").text
    )  # Suponiendo que el título está en un elemento h2
    link = news.find("a")["href"]  # Suponiendo que el enlace está en un elemento a
    print(title, link)

    full_link = (
        "https://www.theverge.com" + link if not link.startswith("http") else link
    )
    post_response = requests.get(full_link)

    if post_response.status_code == 200:
        post_soup = BeautifulSoup(post_response.content, "html.parser")

        post_content = (
            post_soup.find(
                "div", class_="duet--article--article-body-component-container"
            )
            .find("div")
            .text.strip()
        )

        messages = [
            {
                "role": "system",
                "content": """Make a summary of a maximum of one paragraph in non-formal Argentine Spanish, you are an expert in technology, 300 characters max""",
            },
            {"role": "user", "content": """{}""".format(post_content)},
        ]

        response = get_completion_from_messages(messages, temperature=1)

        with open("summary.txt", "a") as file:
            file.write(title + "\n" + response + "\n\n")
    else:
        print("Error al acceder al post:", post_response.status_code)
else:
    print("Error en la petición:", response.status_code)
