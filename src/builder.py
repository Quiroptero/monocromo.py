import shutil
import logging
from tqdm import tqdm
from datetime import datetime as dt
from pathlib import Path
from typing import Dict, List

from .utils import read_file, natural_key
from .site import Site
from .photo import Photo


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Builder:

    def __init__(self, site: Site, photos: List[Photo]):
        self.execution_timestamp = dt.utcnow().strftime("%a, %d %b %Y")
        self._base_path = Path(".", "src").resolve()
        self._html_path = Path(self._base_path, "html")
        self.site = site
        self.photos = photos
        self.head = read_file(filepath=Path(self._html_path, "head.html")).format(title=self.site.title)
        self.index = read_file(filepath=Path(self._html_path, "index.html"))
        self.link = read_file(filepath=Path(self._html_path, "link.html"))
        self.newer = read_file(filepath=Path(self._html_path, "newer.html"))
        self.older = read_file(filepath=Path(self._html_path, "older.html"))
        self.post = read_file(filepath=Path(self._html_path, "post.html"))
        self.rss_item = read_file(filepath=Path(self._html_path, "rss_item.xml"))
        self.rss = read_file(filepath=Path(self._html_path, "index.xml"))

    def generate_posts(self) -> List:
        posts = []
        for photo in self.photos:
            posts.append(
                {
                    "id": photo.id,
                    "payload": self.post.format(
                        head=self.head,
                        photo_href=photo.href,
                        src=photo.src,
                        srcset=photo.srcset,
                        alt=photo.alt,
                        older=self.older.format(older=photo.older) if photo.older is not None else "",
                        newer=self.newer.format(newer=photo.newer) if photo.newer is not None else "",
                    )
                }
            )
        return posts

    def write_posts(self, dst: Path):
        logging.info("Writing posts.")
        posts = self.generate_posts()
        for post in posts:
            target_dir = Path(dst, "photo", post.get("id"))
            target_filepath = Path(target_dir, "index.html")
            target_dir.mkdir(parents=True, exist_ok=True)
            with target_filepath.open("w", encoding="utf-8") as f:
                f.write(post.get("payload"))
                f.close()

    def generate_links(self) -> str:
        links = []
        for photo in self.photos:
            links.append(
                self.link.format(
                    href=photo.href,
                    thumb_src=f"/{photo.thumb_src}",
                    alt=photo.alt,
                )
            )
        links = "\n".join(sorted(links, reverse=True, key=natural_key))  # Reverse to have the newest ids first
        return links

    def generate_index(self) -> str:
        return self.index.format(
            head=self.head,
            links=self.generate_links(),
            email=self.site.email,
        )

    def write_index(self, dst: Path):
        logging.info("Writing indexes.")
        index = self.generate_index()
        for t in ["", "photo"]:  # Write in root and photos dir
            target_dir = Path(dst, t)
            target_filepath = Path(target_dir, "index.html")
            target_dir.mkdir(parents=True, exist_ok=True)
            with target_filepath.open("w", encoding="utf-8") as f:
                f.write(index)
                f.close()

    def generate_rss_items(self):
        items = []
        max_id = max(int(photo.id) for photo in self.photos)
        max_number = max_id if max_id <= 10 else 10
        for photo in self.photos[-max_number:]:
            items.append(
                self.rss_item.format(
                    alt=photo.alt,
                    permalink=f"{self.site.url}{photo.src}",
                    url=self.site.url,
                    src=photo.src,
                )
            )
        items = "\n".join(sorted(items, reverse=True, key=natural_key))  # Reverse to have the newest ids first
        return items

    def generate_rss(self) -> str:
        return self.rss.format(
            title=self.site.title,
            url=self.site.url,
            last_build=self.execution_timestamp,
            rss_items=self.generate_rss_items(),
        )

    def write_rss(self, dst: Path):
        logging.info("Writing RSS index.")
        rss = self.generate_rss()
        target_dir = Path(dst)
        target_filepath = Path(target_dir, "index.xml")
        target_dir.mkdir(parents=True, exist_ok=True)
        with target_filepath.open("w", encoding="utf-8") as f:
            f.write(rss)
            f.close()

    def copy_css(self, dst: Path):
        logging.info("Copying style sheet.")
        if not (css_filepath := Path(dst, "style.css")).exists():
            shutil.copy(Path(self._html_path, "style.css"), css_filepath)

    def generate_images(self, src: Path, dst: Path):
        logging.info("Generating images.")
        pbar = tqdm(total=len(self.photos))
        for photo in self.photos:
            pbar.update(1)
            photo.generate_thumbnail(src=src, dst=dst)
            photo.generate_sizes(src=src, dst=dst)
        pbar.close()

    def build(self, src: Path, dst: Path):
        self.generate_images(src=src, dst=dst)
        self.write_posts(dst=dst)
        self.write_index(dst=dst)
        self.write_rss(dst=dst)
        self.copy_css(dst=dst)
