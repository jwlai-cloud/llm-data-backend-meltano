import typing as t

from singer_sdk._singerlib.messages import (
    Message,
)

class Mapper():

    def map_record_message(self, message_dict: dict) -> t.Iterable[Message]:
        page_content = message_dict["record"]["page_content"]
        page_content = page_content.replace("Three Data Point Thursday", "").replace("Finish Slime","")
        no_unicode = page_content.encode("ascii", "ignore").decode()
        text_nl = " ".join(no_unicode.split("\n"))
        text_spaces = " ".join(text_nl.split())
        message_dict["record"]["page_content"] = text_spaces
        return message_dict

