from ollama import Client

client = Client(host="http://host.docker.internal:11434")
def analyze_competitors(company, data):

    prompt = f"""
    From this data about {company}:

    {data}

    Identify main competitors and explain why.
    """

    response = client.chat(
        model="gemma:2b",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]