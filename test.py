from llama_cloud import AsyncLlamaCloud
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
async def main():
    client = AsyncLlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))  # Uses LLAMA_CLOUD_API_KEY env var

    # Upload and parse a document
    file = await client.files.create(file="/home/gowtham/Downloads/Katalog_GNH+SPG_210_297_Engl.pdf", purpose="parse")
    result = await client.parsing.parse(
        file_id=file.id,
        tier="agentic",
        version="latest",
        expand=["markdown"],
    )

    # Get markdown output
    print(result.markdown.pages.markdown)

asyncio.run(main())