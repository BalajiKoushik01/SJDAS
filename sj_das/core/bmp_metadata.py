"""BMP Metadata Handler for Loom Export.

Embeds and extracts custom metadata in BMP files for jacquard loom compatibility.
Stores loom specifications (hooks, reed, khali, weave mappings) directly in BMP.
"""

import json
import logging
import struct
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class BMPMetadata:
    """
    Professional BMP metadata handler for textile loom export.

    Embeds custom metadata in BMP file comment section for loom specifications.
    Compatible with standard BMP readers while preserving machine data.
    """

    # Metadata marker for identification
    MARKER = b"SJ-DAS-LOOM"
    VERSION = "1.0"

    @staticmethod
    def embed(image_path: str, metadata: dict[str, Any]) -> bool:
        """
        Embed metadata into BMP file.

        Args:
            image_path: Path to BMP file
            metadata: Dictionary of loom specifications

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read original BMP
            with open(image_path, 'rb') as f:
                bmp_data = bytearray(f.read())

            # Verify it's a BMP
            if bmp_data[0:2] != b'BM':
                logger.error(f"Not a valid BMP file: {image_path}")
                return False

            # Add version to metadata
            metadata['_version'] = BMPMetadata.VERSION

            # Serialize metadata to JSON
            metadata_json = json.dumps(metadata, indent=2)
            metadata_bytes = metadata_json.encode('utf-8')

            # Create metadata chunk: MARKER + length + data
            metadata_chunk = (
                BMPMetadata.MARKER +
                struct.pack('<I', len(metadata_bytes)) +
                metadata_bytes
            )

            # Append to end of BMP (after pixel data)
            # BMPs can have trailing data that renderers ignore
            bmp_data.extend(metadata_chunk)

            # Write modified BMP
            with open(image_path, 'wb') as f:
                f.write(bmp_data)

            logger.info(
                f"Embedded {len(metadata_bytes)} bytes of metadata in {Path(image_path).name}")
            return True

        except Exception as e:
            logger.error(f"Failed to embed metadata: {e}", exc_info=True)
            return False

    @staticmethod
    def extract(image_path: str) -> dict[str, Any] | None:
        """
        Extract metadata from BMP file.

        Args:
            image_path: Path to BMP file

        Returns:
            Metadata dictionary or None if not found
        """
        try:
            with open(image_path, 'rb') as f:
                bmp_data = f.read()

            # Find metadata marker
            marker_pos = bmp_data.find(BMPMetadata.MARKER)
            if marker_pos == -1:
                logger.debug(f"No metadata found in {Path(image_path).name}")
                return None

            # Read metadata length
            length_pos = marker_pos + len(BMPMetadata.MARKER)
            length = struct.unpack('<I',
                                   bmp_data[length_pos:length_pos + 4])[0]

            # Read metadata JSON
            data_pos = length_pos + 4
            metadata_bytes = bmp_data[data_pos:data_pos + length]
            metadata_json = metadata_bytes.decode('utf-8')

            # Parse JSON
            metadata = json.loads(metadata_json)

            logger.info(f"Extracted metadata from {Path(image_path).name}")
            return metadata

        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}", exc_info=True)
            return None

    @staticmethod
    def create_metadata(
        hooks: int,
        picks: int,
        reed: int,
        component: str,
        khali: int = 1,
        locking: int = 0,
        weave_map: dict | None = None,
        yarn_colors: list | None = None,
        **kwargs
    ) -> dict[str, Any]:
        """
        Create standard metadata dictionary.

        Args:
            hooks: Total warp threads (width)
            picks: Total weft shots (height)
            reed: Thread density
            component: Component type (Body/Border/Pallu/Full)
            khali: Pattern repeats
            locking: Overlap pixels
            weave_map: Color to weave pattern mapping
            yarn_colors: List of RGB color values
            **kwargs: Additional custom fields

        Returns:
            Metadata dictionary
        """
        from datetime import datetime

        metadata = {
            "X-Hooks": hooks,
            "X-Picks": picks,
            "X-Reed": reed,
            "X-Component": component,
            "X-Khali": khali,
            "X-Locking": locking,
            "X-DateCreated": datetime.now().isoformat(),
        }

        if weave_map:
            metadata["X-WeaveMap"] = weave_map

        if yarn_colors:
            metadata["X-YarnColors"] = yarn_colors

        # Add any additional fields
        metadata.update(kwargs)

        return metadata

    @staticmethod
    def validate_metadata(metadata: dict[str, Any]) -> bool:
        """
        Validate metadata has required fields.

        Args:
            metadata: Metadata to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["X-Hooks", "X-Picks", "X-Reed", "X-Component"]

        for field in required_fields:
            if field not in metadata:
                logger.error(f"Missing required field: {field}")
                return False

        # Validate ranges
        if not (100 <= metadata["X-Hooks"] <= 4800):
            logger.error("Hooks must be between 100 and 4800")
            return False

        if not (50 <= metadata["X-Reed"] <= 150):
            logger.error("Reed must be between 50 and 150")
            return False

        if metadata["X-Component"] not in ["Body", "Border", "Pallu", "Full"]:
            logger.error("Component must be Body/Border/Pallu/Full")
            return False

        return True
