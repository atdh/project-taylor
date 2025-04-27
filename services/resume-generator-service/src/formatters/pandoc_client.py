import os
import subprocess
import tempfile
import logging
from typing import Optional, Literal
from pathlib import Path
import aiofiles
from common_utils.logging import get_logger

logger = get_logger(__name__)

class PandocClient:
    """Client for converting documents between formats using Pandoc"""
    
    SUPPORTED_FORMATS = Literal["docx", "pdf", "html", "markdown", "latex"]
    
    def __init__(self):
        """Initialize Pandoc client and verify installation"""
        self._verify_pandoc_installation()
        self.template_dir = os.path.join(
            os.path.dirname(__file__),
            "..",
            "templates"
        )

    def _verify_pandoc_installation(self):
        """Verify Pandoc is installed and accessible"""
        try:
            result = subprocess.run(
                ["pandoc", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError("Pandoc installation check failed")
            logger.info("Pandoc installation verified")
        except FileNotFoundError:
            raise RuntimeError(
                "Pandoc not found. Please install Pandoc: https://pandoc.org/installing.html"
            )

    async def convert_document(
        self,
        content: str,
        input_format: SUPPORTED_FORMATS,
        output_format: SUPPORTED_FORMATS,
        template_name: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> bytes:
        """
        Convert document between formats
        Args:
            content: Source document content
            input_format: Source format
            output_format: Target format
            template_name: Optional template file name
            metadata: Optional metadata for template
        Returns:
            Converted document as bytes
        """
        try:
            # Create temporary files
            async with aiofiles.tempfile.NamedTemporaryFile(
                mode='w',
                suffix=f'.{input_format}',
                delete=False
            ) as input_file:
                await input_file.write(content)
                input_path = input_file.name

            output_fd, output_path = tempfile.mkstemp(suffix=f'.{output_format}')
            os.close(output_fd)

            # Build Pandoc command
            cmd = [
                "pandoc",
                "-f", input_format,
                "-t", output_format,
                input_path,
                "-o", output_path,
                "--standalone"
            ]

            # Add template if specified
            if template_name:
                template_path = os.path.join(self.template_dir, template_name)
                if not os.path.exists(template_path):
                    raise FileNotFoundError(f"Template not found: {template_name}")
                cmd.extend(["--template", template_path])

            # Add metadata if provided
            if metadata:
                metadata_file = tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.yaml',
                    delete=False
                )
                try:
                    import yaml
                    yaml.dump(metadata, metadata_file)
                    metadata_file.close()
                    cmd.extend(["--metadata-file", metadata_file.name])
                finally:
                    os.unlink(metadata_file.name)

            # PDF-specific options
            if output_format == "pdf":
                cmd.extend([
                    "--pdf-engine=xelatex",
                    "--variable=geometry:margin=1in"
                ])

            # Execute conversion
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"Pandoc conversion failed: {result.stderr}"
                )

            # Read output file
            async with aiofiles.open(output_path, 'rb') as f:
                output_content = await f.read()

            return output_content

        except Exception as e:
            logger.error(f"Document conversion error: {e}")
            raise

        finally:
            # Cleanup temporary files
            if 'input_path' in locals():
                os.unlink(input_path)
            if 'output_path' in locals():
                os.unlink(output_path)

    async def markdown_to_docx(
        self,
        markdown_content: str,
        template_name: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> bytes:
        """
        Convert Markdown to DOCX format
        Args:
            markdown_content: Markdown formatted text
            template_name: Optional DOCX template name
            metadata: Optional metadata for template
        Returns:
            DOCX document as bytes
        """
        return await self.convert_document(
            content=markdown_content,
            input_format="markdown",
            output_format="docx",
            template_name=template_name,
            metadata=metadata
        )

    async def markdown_to_pdf(
        self,
        markdown_content: str,
        template_name: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> bytes:
        """
        Convert Markdown to PDF format
        Args:
            markdown_content: Markdown formatted text
            template_name: Optional LaTeX template name
            metadata: Optional metadata for template
        Returns:
            PDF document as bytes
        """
        return await self.convert_document(
            content=markdown_content,
            input_format="markdown",
            output_format="pdf",
            template_name=template_name,
            metadata=metadata
        )

# Singleton instance
pandoc = PandocClient()
