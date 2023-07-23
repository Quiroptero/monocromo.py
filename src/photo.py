import os
from pathlib import Path
from typing import Dict, List, Optional


class Photo:

    id: str
    prev_id: str
    post_id: str
    filename: str
    alt: str

    def __init__(
            self,
            id: str,
            prev_id: str,
            post_id: str,
            filename: str,
            alt: str,
            sizes: List[str],
    ):
        self.id = id
        self.prev_id = prev_id
        self.post_id=post_id
        self.filename=filename
        self.alt=alt
        self.sizes = sizes

    @classmethod
    def from_record(cls, record: Dict):
        return cls(
            id=record.get("id"),
            prev_id=record.get("prev_id"),
            post_id=record.get("post_id"),
            filename=record.get("filename"),
            alt=record.get("alt"),
            sizes=record.get("sizes"),
        )

    @property
    def href(self) -> str:
        return f"/photo/{self.id}/"

    @property
    def src_prefix(self) -> str:
        return f"images/{self.id}"

    @property
    def thumb_src(self) -> str:
        return f"{self.src_prefix}/thumb_{self.filename}"

    @property
    def largest(self) -> str:
        return f"{self.sizes[0]}_{self.filename}"

    @property
    def src(self) -> str:
        return f"/{self.src_prefix}/{self.largest}"

    @property
    def srcset(self) -> str:
        return ", ".join([f"/{self.src_prefix}/{size}_{self.filename} {size}w" for size in self.sizes])

    @property
    def older(self) -> Optional[str]:
        return f"/photo/{self.prev_id}" if self.prev_id is not None else None

    @property
    def newer(self) -> Optional[str]:
        return f"/photo/{self.post_id}" if self.post_id is not None else None

    def generate_thumbnail(self, src: Path, dst: Path):
        Path(dst, self.src_prefix).mkdir(parents=True, exist_ok=True)  # Make sure target dir exists
        # Convert command
        s = Path(src, "images", self.filename)
        d = Path(dst, self.thumb_src)
        opts_1 = "jpeg:size=100x65"
        opts_2 = "-thumbnail 100x65^ -gravity center -extent 100x65"
        c = f"convert -define {opts_1} {s} {opts_2} {d}".format(opts_1=opts_1, opts_2=opts_2, s=s, d=d)
        os.system(command=c)
        # Mogrify command
        c = f"mogrify -unsharp 0.25x0.08+8.3+0.045 {d}".format(d=d)
        os.system(command=c)

    def generate_sizes(self, src: Path, dst: Path):
        Path(dst, self.src_prefix).mkdir(parents=True, exist_ok=True)  # Make sure target dir exists
        s = Path(src, "images", self.filename)
        d = Path(dst, self.src_prefix)
        for size in self.sizes:
            target = Path(d, f"{size}_{self.filename}")
            os.system(command=f"convert -resize {size}x -quality 100 {s} {target}")
            os.system(command=f"mogrify -unsharp 0.25x0.08+8.3+0.045 {target}")
