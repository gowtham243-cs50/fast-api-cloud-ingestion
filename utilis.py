
import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from llama_cloud import AsyncLlamaCloud
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llms.captioning import generate_image_caption  # unchanged
import httpx

load_dotenv()


def markdown_chunk(markdown_str: str):
    """Split a markdown string into overlapping chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    texts = text_splitter.split_text(markdown_str)
    return texts


async def load_pdf_doc(source: str):
    """
    Parse a PDF with LlamaCloud and return the full result object.
    """
    client = AsyncLlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))

    # Upload file
    file_obj = await client.files.create(
        file=source,
        purpose="parse",
    )

    # Parse with markdown + image metadata expanded
    result = await client.parsing.parse(
        file_id=file_obj.id,
        tier="agentic",
        version="latest",
        # You can customize these as needed
        input_options={},
        output_options={
            "markdown": {
                # tweak markdown/table settings here if you want
                "tables": {
                    "output_tables_as_markdown": True,
                }
            },
            # store screenshots/figures so we get URLs in images_content_metadata
            "images_to_save": ["screenshot"],  # or add "figure" if enabled
        },
        processing_options={
            # example knobs; adjust as needed
            "ignore": {
                "ignore_diagonal_text": True,
            },
        },
        expand=["markdown", "images_content_metadata"],
    )

    return result


async def download_images_from_result(result, images_dir: Path) -> list[str]:
    """
    Download all images exposed via images_content_metadata to `images_dir`
    and return the list of local file paths.
    """
    images_dir.mkdir(exist_ok=True)
    image_files: list[str] = []

    # `images_content_metadata.images` has filename + presigned_url.[web:13]
    images_meta = getattr(result.images_content_metadata, "images", [])

    async with httpx.AsyncClient() as http_client:
        for image in images_meta:
            # Some entries may not be downloadable (no URL)
            if image.presigned_url is None:
                continue

            image_path = images_dir / image.filename
            resp = await http_client.get(image.presigned_url)
            resp.raise_for_status()
            image_path.write_bytes(resp.content)
            image_files.append(str(image_path))

    return image_files


async def get_markdown_chunks(source: str):
    """
    Parse PDF with LlamaCloud, extract markdown chunks, generate captions
    for downloaded images, and return (markdown_chunks, image_captions).
    """
    result = await load_pdf_doc(source)

    # Combine markdown from all pages into one big string.[web:13]
    if result.markdown is None or result.markdown.pages is None:
        markdown_str = ""
    else:
        markdown_str = "\n\n".join(
            page.markdown for page in result.markdown.pages
        )

    markdown_chunks = markdown_chunk(markdown_str=markdown_str)

    # Download any images we asked LlamaCloud to save
    images_dir = Path("images")
    image_files = await download_images_from_result(result, images_dir)

    # Your existing image captioning
    image_captions = [generate_image_caption(image_path) for image_path in image_files]

    return markdown_chunks, image_captions


# Optional: small runner for manual testing
if __name__ == "__main__":
    async def _demo():
        pdf_path = "/home/gowtham/Downloads/Ata.pdf"
        chunks, captions = await get_markdown_chunks(pdf_path)
        print(f"Num chunks: {len(chunks)}")
        print(f"Num images: {len(captions)}")
        # peek at first chunk and caption
        if chunks:
            print("First chunk:\n", chunks[0][:500])
        if captions:
            print("First caption:\n", captions[0])

    asyncio.run(_demo())