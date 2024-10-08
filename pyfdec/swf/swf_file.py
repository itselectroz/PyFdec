from dataclasses import dataclass
from enum import Enum

from pyfdec.extended_buffer import ExtendedBuffer
from pyfdec.record_types.geometric_types import Rect
from pyfdec.tags.ShowFrame import ShowFrame
from pyfdec.tags.DefineSceneAndFrameLabelData import DefineSceneAndFrameLabelData
from pyfdec.tags.DefineShape import DefineShape
from pyfdec.tags.DefineShape2 import DefineShape2
from pyfdec.tags.DefineShape3 import DefineShape3
from pyfdec.tags.DefineShape4 import DefineShape4
from pyfdec.tags.End import End
from pyfdec.tags.FileAttriubtes import FileAttriubtes
from pyfdec.tags.SetBackgroundColor import SetBackgroundColor
from pyfdec.tags.Tag import Tag


@dataclass
class SwfHeader:

    class CompressionLevel(Enum):
        Uncompressed = b"FWS"
        Zlib = b"CWS"
        LZMA = b"ZWS"

    compression: CompressionLevel
    version: int
    fileLength: int
    frameSize: Rect
    frameRate: float
    frameCount: int

    @classmethod
    def from_buffer(cls, buffer):
        compression = cls.CompressionLevel(buffer.read(3))
        version = buffer.read_ui8()
        fileLength = buffer.read_ui32()
        frameSize = Rect.from_buffer(buffer)
        frameRate = buffer.read_fixed8()
        frameCount = buffer.read_ui16()
        return cls(compression, version, fileLength, frameSize, frameRate, frameCount)


@dataclass
class SwfFile:

    header: SwfHeader
    fileAttributes: FileAttriubtes
    tags: list[Tag]

    @classmethod
    def from_buffer(cls, buffer: ExtendedBuffer):

        header = SwfHeader.from_buffer(buffer)
        tags: list[Tag] = []

        while True:
            tag_type_and_length = buffer.read_ui16()
            tag_type = Tag.TagTypes(tag_type_and_length >> 6)
            tag_length = tag_type_and_length & 0x3F
            if tag_length == 0x3F:
                tag_length = buffer.read_ui32()

            tag_buffer = buffer.subbuffer(tag_length)
            match tag_type:
                case Tag.TagTypes.FileAttributes:
                    fileAttributes = FileAttriubtes.from_buffer(tag_buffer)
                case Tag.TagTypes.SetBackgroundColor:
                    tags.append(SetBackgroundColor.from_buffer(tag_buffer))
                case Tag.TagTypes.DefineSceneAndFrameLabelData:
                    tags.append(DefineSceneAndFrameLabelData.from_buffer(tag_buffer))
                case Tag.TagTypes.DefineShape:
                    tags.append(DefineShape.from_buffer(tag_buffer))
                case Tag.TagTypes.DefineShape2:
                    tags.append(DefineShape2.from_buffer(tag_buffer))
                case Tag.TagTypes.DefineShape3:
                    tags.append(DefineShape3.from_buffer(tag_buffer))
                case Tag.TagTypes.DefineShape4:
                    tags.append(DefineShape4.from_buffer(tag_buffer))
                case Tag.TagTypes.ShowFrame:
                    tags.append(ShowFrame.from_buffer(tag_buffer))
                case Tag.TagTypes.End:
                    tags.append(End.from_buffer(tag_buffer))
                    break
                case _:
                    pass
                    # raise NotImplementedError(f"Unimplemented tag type: {tag_type}")

        # Implement check that fileAttributes is defined
        return cls(header, fileAttributes, tags)
